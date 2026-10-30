"""Monta o Silverwing no esqueleto de dragao do Mesh2Motion (CC0) e reaproveita as animacoes dele.
1) copia a armadura das animacoes (mesmos nomes/hierarquia/acoes); 2) encaixa cada osso nas posicoes medidas
(encaixe.json) com roll = giro minimo da orientacao do molde (assim a volta para a pose do molde e so 'swing', sem torcer);
3) pesos (calor; fallback proxy voxel); 4) reposiciona o modelo na pose de descanso do molde e aplica como descanso
-> orientacoes de repouso identicas as do molde, entao as acoes locais servem direto; 5) translacoes escaladas;
6) salva .blend de trabalho e exporta GLB. Original e Silverwing_20k ficam intocados.
Uso: blender -b -P montar_silverwing.py -- anim.glb malha.glb encaixe.json saida_dir"""
import bpy, sys, os, json, math
from mathutils import Vector, Matrix, Quaternion
args = sys.argv[sys.argv.index("--") + 1:]
anim_glb, malha_glb, enc_json, out = args[:4]
os.makedirs(out, exist_ok=True)
sys.path.insert(0, r"C:\Users\Rhenan\.claude\skills\blender-character-rigging\scripts")
import bind_mesh

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=anim_glb)
T = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
for o in [o for o in bpy.data.objects if o.type == "MESH"]: bpy.data.objects.remove(o)
for t in (T.animation_data.nla_tracks if T.animation_data else []): t.mute = True
print("MOLDE", T.name, "bones", len(T.data.bones), "matrix_world", [list(map(lambda v: round(v, 3), r)) for r in T.matrix_world])
TW = T.matrix_world.copy()
ROT_T = {b.name: (TW.to_3x3().normalized() @ b.matrix_local.to_3x3()).normalized() for b in T.data.bones}
DIR_T = {n: (m @ Vector((0, 1, 0))).normalized() for n, m in ROT_T.items()}
HEAD_T = {b.name: TW @ b.head_local for b in T.data.bones}
TAIL_T = {b.name: TW @ b.tail_local for b in T.data.bones}
extra = [b.name for b in T.data.bones]
enc = json.load(open(enc_json))["ossos"]
print("SEM_ENCAIXE", [n for n in extra if n not in enc])

# 2) armadura nova = copia do molde, transformacao identidade
A = T.copy(); A.data = T.data.copy(); A.name = "Silverwing_Rig"; A.data.name = "Silverwing_Rig"
bpy.context.scene.collection.objects.link(A)
A.matrix_world = Matrix.Identity(4)
A.animation_data_clear()
bpy.data.objects.remove(T)
bpy.context.view_layer.objects.active = A; A.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
EB = A.data.edit_bones
for eb in EB: eb.use_connect = False
ordem = []
def visita(b):
    ordem.append(b.name)
    for c in b.children: visita(c)
for b in [b for b in A.data.bones if b.parent is None]: visita(b)
ROT_OLD = {}
for n in ordem:
    eb = EB[n]
    if n in enc:
        h, t = Vector(enc[n][0]), Vector(enc[n][1])
    else:   # osso sem medida: ponta do pai, direcao do molde, comprimento pequeno
        h = EB[n].parent.tail.copy() if EB[n].parent else Vector((0, 0, 0)); t = h + DIR_T[n] * 0.02
    if (t - h).length < 1e-4: t = h + DIR_T[n] * 0.01
    d = (t - h).normalized()
    sw = DIR_T[n].rotation_difference(d).to_matrix()     # giro minimo molde -> encaixe
    R_old = (sw @ ROT_T[n]).normalized()
    eb.head, eb.tail = h, t
    eb.align_roll(R_old @ Vector((0, 0, 1)))
    ROT_OLD[n] = R_old
bpy.ops.object.mode_set(mode="OBJECT")

# 3) malha + pesos
bpy.ops.import_scene.gltf(filepath=malha_glb)
M = [o for o in bpy.data.objects if o.type == "MESH"][0]; M.name = "Silverwing"
for b in A.data.bones: b.use_deform = b.name not in ("root", "DRV_root")
rel = bind_mesh.run(armature=A.name, meshes=[M.name], method="auto", limit=4, clean=0.01)
print("PESOS", json.dumps(rel))

# 3b) asas: o proxy voxel perde a membrana fina e ela herda pesos do corpo (vira 'espinhos' ao posar).
# Vertices mais proximos de um osso de asa que de qualquer outro recebem pesos por distancia (1/d^4, 4 maiores)
# so entre os ossos de asa daquele lado. Vertices sem peso recebem o osso mais proximo.
def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-12))); return (p - (a + ab * t)).length
SEG = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in A.data.bones if b.use_deform}
def asa(n): return n.startswith("wing_") or n.startswith("shoulder_")
VG = {g.name: g for g in M.vertex_groups}
# regioes: o vertice pertence a regiao do osso mais proximo; pesos so entre ossos dessa regiao (+ juncao com o tronco)
def regiao(n):
    if asa(n): return "asa_" + n[-1]
    if n.startswith("tail_"): return "cauda"
    if n.startswith(("front_", "collar_")): return "pd_" + n[-1]
    if n.startswith(("back_", "hips_anchor_")): return "pt_" + n[-1]
    return "tronco"
JUNCAO = {"cauda": ["hips", "spine_0"], "pd_l": ["spine_1"], "pd_r": ["spine_1"], "pt_l": ["spine_0", "hips"],
          "pt_r": ["spine_0", "hips"], "asa_l": ["spine_0"], "asa_r": ["spine_0"], "tronco": []}
from collections import Counter
# REGIOES POR DISTANCIA NA SUPERFICIE (geodesica), nao em linha reta. Na pose do Meshy as pontas das asas encostam na
# base da cauda e nas patas: pelo 'osso mais proximo' a base da cauda virava ASA (a asa arrancava um pedaco da cauda
# ao bater -> cauda 'faltando um pedaco' + lascas voando). Sementes = vertices bem colados ao osso (raio pequeno por
# regiao); cada vertice fica com a regiao da semente mais proxima ANDANDO PELA MALHA (Dijkstra nas arestas).
import heapq
# tronco 0.14: os espinhos da crista do dorso ficam ~12 cm acima da coluna; com 0.06 a ASA chegava antes pela malha e
# 339 vertices da crista giravam com a asa (lascas no dorso)
RAIO_SEM = {"asa": float(os.environ.get("RAIO_ASA", "0.018")), "cauda": 0.055, "pd": 0.035, "pt": 0.045, "tronco": 0.14}
def rcls(r): return "asa" if r.startswith("asa") else ("tronco" if r == "tronco" else r[:2] if r[:2] in ("pd", "pt") else "cauda")
NV = len(M.data.vertices); PW = [M.matrix_world @ v.co for v in M.data.vertices]
viz_g = [[] for _ in range(NV)]
for e in M.data.edges:
    a, b = e.vertices; L = (PW[a] - PW[b]).length; viz_g[a].append((b, L)); viz_g[b].append((a, L))
# copias do mesmo ponto nas costuras de UV (o glTF separa o vertice): ligacao de comprimento 0, senao cada copia caia
# numa regiao/peso diferente e a costura abria em rachaduras ao posar
from mathutils.kdtree import KDTree
_kdc = KDTree(NV)
for i, p in enumerate(PW): _kdc.insert(p, i)
_kdc.balance()
GEMEOS = [[j for _, j, _ in _kdc.find_range(p, 1e-6) if j != i] for i, p in enumerate(PW)]
for i, gs in enumerate(GEMEOS):
    for j in gs: viz_g[i].append((j, 0.0))
REGV = [None] * NV; dist_g = [float("inf")] * NV; fila = []
for i, p in enumerate(PW):
    ds = sorted(((dist_seg(p, *SEG[n]), n) for n in SEG if not n.startswith("shoulder_")), key=lambda x: x[0])
    d, n = ds[0]; r = regiao(n)
    if d <= RAIO_SEM[rcls(r)]:
        dist_g[i] = 0.0; REGV[i] = r; heapq.heappush(fila, (0.0, i))
print("SEMENTES", sum(1 for x in REGV if x), "de", NV, Counter(rcls(x) for x in REGV if x))
while fila:
    d, i = heapq.heappop(fila)
    if d > dist_g[i]: continue
    for j, L in viz_g[i]:
        nd = d + L
        if nd < dist_g[j]: dist_g[j] = nd; REGV[j] = REGV[i]; heapq.heappush(fila, (nd, j))
for i in range(NV):                                  # sem caminho (nao deve ocorrer: malha unica) -> osso mais proximo
    if REGV[i] is None: REGV[i] = regiao(min(((dist_seg(PW[i], *SEG[n]), n) for n in SEG), key=lambda x: x[0])[1])
# ASA_X_MIN: a asa nasce em |x| ~0.11 (cabeca de wing_1); vertices de 'asa' mais para dentro (peito sob o pescoco, dorso)
# chegavam a asa pela malha e ficavam com peso de shoulder/wing_1: giravam com a asa = rachadura na frente do ombro
ASA_X_MIN = float(os.environ.get("ASA_X_MIN", "0"))
if ASA_X_MIN > 0:
    _tr = [i for i in range(NV) if REGV[i].startswith("asa") and abs(PW[i].x) < ASA_X_MIN]
    for i in _tr: REGV[i] = "tronco"
    print("ASA_X_MIN vertices_para_tronco", len(_tr))
reta = Counter()
for i, p in enumerate(PW):
    rr = regiao(min(((dist_seg(p, *SEG[n]), n) for n in SEG if not n.startswith("shoulder_")), key=lambda x: x[0])[1])
    if rcls(rr) != rcls(REGV[i]): reta[(rcls(rr), rcls(REGV[i]))] += 1
print("REGIOES_GEODESICAS", Counter(REGV), "| mudaram vs linha reta (reta->superficie):", reta.most_common(8))
cont_reg = Counter(); n_asa = n_sem = 0
for v in M.data.vertices:
    p = M.matrix_world @ v.co
    ds = sorted(((dist_seg(p, *SEG[n]), n) for n in SEG), key=lambda x: x[0])
    r = REGV[v.index]; cont_reg[r] += 1
    cand = [(d, n) for d, n in ds if regiao(n) == r or n in JUNCAO[r]][:4]
    # membrana: queda mais suave (1/d^2) para dividir a dobra entre dedos vizinhos sem vincos
    pot = 2 if r.startswith("asa") else 4
    pesos = [(n, 1.0 / max(d, 0.004) ** pot) for d, n in cand]
    n_asa += r.startswith("asa")
    s = sum(w for _, w in pesos)
    # raiz da asa sobre o dorso: o peso do 'shoulder' perto da coluna passa para spine_0 (as duas raizes se
    # encontram na linha media e se cruzavam quando os ombros giram)
    if r.startswith("asa"):
        h, t = SEG["shoulder_" + r[-1]]
        u = max(0.0, min(1.0, (p - h).dot(t - h) / max((t - h).length_squared, 1e-12)))
        f = max(0.0, min(1.0, (u - 0.25) / 0.5)); f = f * f * (3 - 2 * f)
        pesos = [(n, w * (f if n.startswith("shoulder_") else 1.0)) for n, w in pesos] + \
                [("spine_0", sum(w for n, w in pesos if n.startswith("shoulder_")) * (1 - f))]
        acc = {}
        for n, w in pesos: acc[n] = acc.get(n, 0) + w
        pesos = sorted(acc.items(), key=lambda x: -x[1])[:4]
        s = sum(w for _, w in pesos)
    for g in list(v.groups): M.vertex_groups[g.group].remove([v.index])
    for n, w in pesos:
        if n not in VG: VG[n] = M.vertex_groups.new(name=n)
        VG[n].add([v.index], w / s, "REPLACE")
print("PESOS_ASA vertices", n_asa, "sem_peso_corrigidos", n_sem)

# REPOSE com pesos MUITO suaves (so para esta mudanca de pose): com os pesos finais (transicoes curtas) o giro grande
# das asas (erguidas -> abertas) dobrava a pele em placas/lascas na raiz da asa e no dorso, que ficavam gravadas no
# descanso. Os pesos finais sao recalculados do zero na pose nova (repesar_silverwing.py).
_gi = {g.index: g.name for g in M.vertex_groups}
_W = [{_gi[x.group]: x.weight for x in v.groups if x.weight > 1e-4} for v in M.data.vertices]
_viz = [[] for _ in M.data.vertices]
# suaviza SO dentro da mesma regiao (e na juncao asa-tronco, onde nasce a dobra): misturar asa com pata/cauda
# deformava tudo junto
# (misturar asa com tronco espalhava peso de asa nos espinhos do dorso: eles giravam com a asa = lascas)
def _pode(ra, rb): return ra == rb
# COSTURA_RAIZ (raio): perto da dobradica da asa (cabeca de wing_1), longe da linha media do dorso, asa e tronco se
# misturam no repose; a fronteira 1/0 ali gravava uma rachadura/placa no ombro do descanso
COSTURA_RAIZ = float(os.environ.get("COSTURA_RAIZ", "0"))
_dob = [A.data.bones["wing_1_" + s].head_local.copy() for s in ("l", "r")] if COSTURA_RAIZ > 0 else []
def _junto_raiz(i):
    co = M.data.vertices[i].co
    return abs(co.x) > 0.05 and any((co - d).length < COSTURA_RAIZ for d in _dob)
_n_cost = 0
for e in M.data.edges:
    a_, b_ = e.vertices
    if _pode(REGV[a_], REGV[b_]) or (COSTURA_RAIZ > 0 and {REGV[a_][:3], REGV[b_][:3]} <= {"asa", "tro", "pd_"}
                                     and _junto_raiz(a_) and _junto_raiz(b_)):
        _viz[a_].append(b_); _viz[b_].append(a_); _n_cost += REGV[a_] != REGV[b_]
for i, gs in enumerate(GEMEOS): _viz[i].extend(gs)      # copias da costura de UV suavizam juntas
print("COSTURA_RAIZ arestas_entre_regioes", _n_cost)
for _it in range(25):                                   # Laplaciano dos pesos (media com os vizinhos)
    _N = []
    for i, w in enumerate(_W):
        acc = dict(w)
        for j in _viz[i]:
            for n, x in _W[j].items(): acc[n] = acc.get(n, 0) + x
        s = sum(acc.values()) or 1; _N.append({n: x / s for n, x in acc.items() if x / s > 0.002})
    _W = _N
for v, w in zip(M.data.vertices, _W):
    top = sorted(w.items(), key=lambda t: -t[1])[:4]; s = sum(x for _, x in top) or 1
    for x in list(v.groups): M.vertex_groups[x.group].remove([v.index])
    for n, x in top: M.vertex_groups[n].add([v.index], x / s, "REPLACE")
print("PESOS_REPOSE suavizados")
# ALTA (opcional, 5o argumento): o original de 1M acompanha o repose pela malha leve (Surface Deform) e e exportado
# JA NA POSE NOVA; dele se refaz a malha leve (remesh + bake), sem as placas do repose por skin linear.
HI = None
if len(args) > 4:
    antes_hi = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=args[4])
    HI = [o for o in bpy.data.objects if o not in antes_hi and o.type == "MESH"][0]; HI.name = "HI_original"
    _zs = min(v.co.z for v in HI.data.vertices); _xs = [v.co.x for v in HI.data.vertices]; _ys = [v.co.y for v in HI.data.vertices]
    HI.data.transform(Matrix.Translation((-(min(_xs) + max(_xs)) / 2, -(min(_ys) + max(_ys)) / 2, -_zs)))   # = remesh_bake
    # pesos da leve -> alta por interpolacao na face mais proxima; a alta segue o MESMO esqueleto (Surface Deform
    # explodia em pontas onde a leve e fina)
    for g in M.vertex_groups: HI.vertex_groups.new(name=g.name)
    dt = HI.modifiers.new("pesos", "DATA_TRANSFER"); dt.object = M; dt.use_vert_data = True
    dt.data_types_verts = {"VGROUP_WEIGHTS"}; dt.vert_mapping = "POLYINTERP_NEAREST"
    dt.layers_vgroup_select_src = "ALL"; dt.layers_vgroup_select_dst = "NAME"
    with bpy.context.temp_override(object=HI, active_object=HI, selected_objects=[HI], selected_editable_objects=[HI]):
        bpy.ops.object.modifier_apply(modifier=dt.name)
    am = HI.modifiers.new("Armature", "ARMATURE"); am.object = A
    print("HI ligado", len(HI.data.vertices), "verts, grupos", len(HI.vertex_groups))
# 4) pose do molde: cada osso com a orientacao do molde, posicao levada pelo pai (FK)
bpy.context.view_layer.objects.active = A; A.select_set(True)
bpy.ops.object.mode_set(mode="POSE")
OLD = {b.name: b.matrix_local.copy() for b in A.data.bones}
NEW = {}
# 'mao' da asa (dedo-guia apos o pulso + 5 dedos de membrana) mantem o leque do Silverwing: e carregada rigida
# pelo pai. Forcar o 'pente' paralelo do molde rasga a membrana. As acoes desses ossos sao conjugadas depois.
def mao(n): return n.startswith("wing_feather_") or n.split("_")[0] == "wing" and n.split("_")[1] in ("3", "4", "5", "tip")
# giro unico por lado que leva o plano da mao do Silverwing (dedo-guia + leque) ao plano da asa aberta do molde
def quadro(pulso, ponta, dedos):
    u = (ponta - pulso).normalized(); v = (sum(dedos, Vector()) / len(dedos) - pulso)
    v = (v - u * v.dot(u)).normalized(); return Matrix((u, v, u.cross(v))).transposed()
RMAO = {}
# ASA_INTEIRA (modelo em T-pose do Meshy, membrana num plano vertical): a asa toda gira como UM bloco a partir da raiz
# (ombro) ate o plano da asa aberta do molde; sem torcer o pulso nem os dedos separadamente.
ASA_INTEIRA = os.environ.get("ASA_INTEIRA") == "1"
CORPO_FIXO = os.environ.get("CORPO_FIXO") == "1"
for s in ("l", "r"):
    def H(n): return HEAD_T[n]
    raiz = "shoulder_" + s if ASA_INTEIRA else "wing_3_" + s
    q_o = quadro(OLD[raiz].translation if not ASA_INTEIRA else A.data.bones["wing_1_" + s].head_local, A.data.bones["wing_tip_" + s].tail_local,
                 [A.data.bones["wing_feather_%d_tip_%s" % (i, s)].tail_local for i in (3, 4, 5)])
    q_t = quadro(H(raiz) if not ASA_INTEIRA else H("wing_1_" + s), TAIL_T["wing_tip_" + s], [TAIL_T["wing_feather_%d_tip_%s" % (i, s)] for i in (3, 4, 5)])
    RMAO[s] = q_t @ q_o.inverted()
    print("GIRO_ASA", s, round(math.degrees(RMAO[s].to_quaternion().angle), 1))
if ASA_INTEIRA:
    _mao_antiga = mao
    # o ombro (shoulder_) nasce no CENTRO da coluna: girar a partir dele arrastava a raiz da asa num arco grande e
    # rasgava o dorso. O ombro fica parado; o bloco gira a partir de wing_1 (raiz real da asa).
    def mao(n): return _mao_antiga(n) or n.startswith(("wing_1_", "wing_2_"))
for n in ordem:
    b = A.data.bones[n]
    if b.parent is None: h = OLD[n].translation.copy(); carga = None
    else:
        p = b.parent.name
        carga = NEW[p] @ OLD[p].inverted()
        h = carga @ OLD[n].translation
    if mao(n) and carga is not None:
        NEW[n] = Matrix.Translation(h) @ (RMAO[n[-1]] @ OLD[n].to_3x3()).to_4x4()
    elif CORPO_FIXO and not n.startswith("tail"):
        # modelo ja em pose neutra: tronco, pescoco, cabeca e patas FICAM como estao (o repose para as orientacoes do
        # molde dobrava pescoco/ombros e gerava as placas/lascas). So asas (bloco) e cauda (endireitar) mudam.
        NEW[n] = (carga @ OLD[n]) if carga is not None else OLD[n].copy()
    else:
        NEW[n] = Matrix.Translation(h) @ ROT_T[n].to_4x4()
    A.pose.bones[n].matrix = NEW[n]
    bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode="OBJECT")
# diagnostico: arestas esticadas (>2.5x) -> ossos dominantes envolvidos
from collections import Counter
dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh()
gi = {g.index: g.name for g in M.vertex_groups}
def dom(v): return gi[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "-"
cont = Counter(); n_est = 0
for e in M.data.edges:
    a, b = e.vertices; l0 = (M.data.vertices[a].co - M.data.vertices[b].co).length
    l1 = (me.vertices[a].co - me.vertices[b].co).length
    if l0 > 1e-6 and l1 / l0 > 2.5:
        n_est += 1; cont[(dom(M.data.vertices[a]), dom(M.data.vertices[b]))] += 1
M.evaluated_get(dg).to_mesh_clear()
print("ESTICADAS", n_est, cont.most_common(15))
# pontes do Meshy (asa/cauda/patas fundidas entre si). v1 APAGAVA essas faces -> buraco na base da cauda (no Roblox,
# que so desenha um lado das faces, aparecia como cauda 'faltando um pedaco'). v2: RASGA sem apagar: cada face fica
# com a regiao da maioria dos seus vertices, as arestas entre faces de membros diferentes (asa x cauda x patas) sao
# separadas, e cada copia de vertice passa a seguir SO os ossos da regiao das suas faces. Nenhuma face some.
import bmesh
reg = list(REGV)                                    # regioes geodesicas (nao o osso dominante)
bm = bmesh.new(); bm.from_mesh(M.data); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
def membro(r): return r[:3] if r != "tronco" else "tronco"          # asa_l/asa_r, cau(da), pd_, pt_
freg = {}
for f in bm.faces:
    freg[f.index] = Counter(reg[v.index] for v in f.verts).most_common(1)[0][0]
# membro x tronco: a juncao legitima e so perto da articulacao (ombro/quadril/raiz da asa). Contato longe dela (pata
# dianteira colada na barriga, ponta da asa encostada no flanco na pose do Meshy) tambem e ponte -> rasga.
def raiz_membro(r):
    s = r[-1]
    if r.startswith("pd"): return SEG["front_leg_collar_" + s][0], 0.12
    if r.startswith("pt"): return SEG["back_leg_hip_" + s][0], 0.12
    if r.startswith("asa"): return SEG["shoulder_" + s][1], 0.14
    return None, 0
def ponte(e):
    fa, fb = e.link_faces; ra, rb = freg[fa.index], freg[fb.index]
    if ra == rb: return False
    if "tronco" not in (ra, rb): return True
    r, f = (ra, fa) if rb == "tronco" else (rb, fb)
    if r == "cauda": return False
    c, lim = raiz_membro(r)
    return min(((M.matrix_world @ v.co) - c).length for v in e.verts) > lim
corte = [e for e in bm.edges if len(e.link_faces) == 2 and ponte(e)]
if os.environ.get("SEM_PONTES") == "1": corte = []      # modelo em pose neutra: nada encosta; rasgar so abre fendas
nv0 = len(bm.verts)
bmesh.ops.split_edges(bm, edges=corte)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
nova_reg = {}
for v in bm.verts:
    c = Counter(freg[f.index] for f in v.link_faces)
    if c: nova_reg[v.index] = c.most_common(1)[0][0]
bm.to_mesh(M.data); bm.free(); M.data.update()
gi = {g.index: g.name for g in M.vertex_groups}; VG = {g.name: g for g in M.vertex_groups}
trocados = 0
for v in M.data.vertices:
    r = nova_reg.get(v.index); atual = regiao(dom(v)) if len(v.groups) else None
    if r is None or r == atual: continue
    p = M.matrix_world @ v.co
    cand = sorted(((dist_seg(p, *SEG[n]), n) for n in SEG if regiao(n) == r or n in JUNCAO[r]), key=lambda x: x[0])[:4]
    pesos = [(n, 1.0 / max(d, 0.004) ** 3) for d, n in cand]; s = sum(w for _, w in pesos)
    for g in list(v.groups): M.vertex_groups[g.group].remove([v.index])
    for n, w in pesos:
        if n not in VG: VG[n] = M.vertex_groups.new(name=n)
        VG[n].add([v.index], w / s, "REPLACE")
    trocados += 1
print("PONTES_RASGADAS arestas", len(corte), "vertices", nv0, "->", len(M.data.vertices), "repesados", trocados)
gi = {g.index: g.name for g in M.vertex_groups}
# correcao: vertices em arestas esticadas recebem a media dos pesos dos vizinhos (varias rodadas, ate 4 ossos)
viz = [[] for _ in M.data.vertices]
for e in M.data.edges:
    a, b = e.vertices; viz[a].append(b); viz[b].append(a)
def pesos_de(v): return {gi[g.group]: g.weight for g in v.groups if g.weight > 1e-4}
for rodada in range(8):
    dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh()
    marc = set()
    for e in M.data.edges:
        a, b = e.vertices; l0 = (M.data.vertices[a].co - M.data.vertices[b].co).length
        if l0 > 1e-6 and (me.vertices[a].co - me.vertices[b].co).length / l0 > 2.0: marc.update((a, b))
    M.evaluated_get(dg).to_mesh_clear()
    print("RODADA", rodada, "vertices_esticados", len(marc))
    if not marc: break
    W = {i: pesos_de(M.data.vertices[i]) for i in set(marc) | {j for i in marc for j in viz[i]}}
    novos = {}
    for i in marc:
        acc = {}
        for j in viz[i] + [i]:
            for n, w in W[j].items(): acc[n] = acc.get(n, 0) + w
        top = sorted(acc.items(), key=lambda x: -x[1])[:4]; s = sum(w for _, w in top)
        novos[i] = [(n, w / s) for n, w in top]
    for i, ps in novos.items():
        v = M.data.vertices[i]
        for g in list(v.groups): M.vertex_groups[g.group].remove([i])
        for n, w in ps:
            g = M.vertex_groups.get(n) or M.vertex_groups.new(name=n); g.add([i], w, "REPLACE")
    gi = {g.index: g.name for g in M.vertex_groups}
# aplica a pose na malha e como descanso
bpy.context.view_layer.objects.active = M
mod = [m for m in M.modifiers if m.type == "ARMATURE"][0]
# a mudanca de pose (asas erguidas do Meshy -> asas abertas do molde) e GRAVADA no descanso: com skin linear ela deixa
# vincos/placas (lascas) na raiz das asas e no dorso, que aparecem ate parado. Corrective Smooth depois do Armature
# alisa so o ERRO da deformacao (compara com a forma original), preservando o relevo.
cs = M.modifiers.new("corretivo", "CORRECTIVE_SMOOTH")
cs.rest_source = "ORCO"; cs.smooth_type = "LENGTH_WEIGHTED"; cs.factor = 1.0; cs.iterations = 25; cs.use_pin_boundary = True
# aplica a PILHA de uma vez (avaliada): aplicando o Armature antes, o ORCO do Corrective Smooth ja seria a forma dobrada
dg = bpy.context.evaluated_depsgraph_get()
if HI is not None:                                    # alta na pose nova (antes de mexer na malha leve)
    me_hi = HI.evaluated_get(dg).to_mesh(); cos_hi = [v.co.copy() for v in me_hi.vertices]; HI.evaluated_get(dg).to_mesh_clear()
    HI.modifiers.clear()
    for v, c in zip(HI.data.vertices, cos_hi): v.co = c
    HI.data.update(); print("HI reposta")
me_ev = M.evaluated_get(dg).to_mesh()
assert len(me_ev.vertices) == len(M.data.vertices)
cos = [v.co.copy() for v in me_ev.vertices]; M.evaluated_get(dg).to_mesh_clear()
mx_desl = 0.0
for v, c in zip(M.data.vertices, cos): v.co = c
M.modifiers.remove(cs); M.modifiers.remove(mod); M.data.update()
print("REPOUSO_COM_CORRETIVO aplicado")
bpy.context.view_layer.objects.active = A
bpy.ops.object.mode_set(mode="POSE"); bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode="OBJECT")
mod = M.modifiers.new("Armature", "ARMATURE"); mod.object = A
# chao: menor z da malha = 0
zmin = min((M.matrix_world @ v.co).z for v in M.data.vertices)
desl = Matrix.Translation((0, 0, -zmin))
M.data.transform(desl)
if HI is not None:
    HI.data.transform(desl)
    for o in bpy.data.objects: o.select_set(o == HI)
    bpy.context.view_layer.objects.active = HI
    hi_out = os.path.join(out, "HI_reposto.glb")
    bpy.ops.export_scene.gltf(filepath=hi_out, export_format="GLB", use_selection=True, export_image_format="JPEG")
    print("HI_EXPORTADO", hi_out, round(os.path.getsize(hi_out) / 1e6, 1), "MB")
    bpy.data.objects.remove(HI); HI = None
    bpy.context.view_layer.objects.active = A
    for o in bpy.data.objects: o.select_set(o == A)
bpy.ops.object.mode_set(mode="EDIT")
for eb in A.data.edit_bones: eb.head.z -= zmin; eb.tail.z -= zmin
bpy.ops.object.mode_set(mode="OBJECT")
# conferencia: orientacao de repouso == molde
err = max(math.degrees((A.data.bones[n].matrix_local.to_3x3().to_quaternion()).rotation_difference(ROT_T[n].to_quaternion()).angle)
          for n in ordem if not mao(n))
# conjugacao para a mao: mesma rotacao (eixo no mundo, em repouso) expressa no referencial do osso do Silverwing
CONJ = {n: (ROT_T[n].inverted() @ A.data.bones[n].matrix_local.to_3x3()).to_quaternion() for n in ordem if mao(n)}
print("ERRO_ORIENTACAO_MAX_GRAUS", round(err, 4), "zmin", round(zmin, 4))

# 5) acoes: copias com translacoes escaladas
def comp(nomes, H):
    return sum((H[nomes[i + 1]] - H[nomes[i]]).length for i in range(len(nomes) - 1))
cad = ["spine_0", "spine_1", "spine_2", "spine_3", "spine_4", "head"]
HA = {b.name: b.head_local.copy() for b in A.data.bones}
k = comp(cad, HA) / comp(cad, HEAD_T)
print("ESCALA_TRANSLACAO", round(k, 4))
acoes = [a for a in bpy.data.actions]
A.animation_data_create()
for act in acoes:
    nova = act.copy(); nova.name = "Silverwing_" + act.name.replace(" ", "_")
    maxloc = 0
    for lay in nova.layers:
        for st in lay.strips:
            for cb in st.channelbags:
                quat = {}
                for fc in cb.fcurves:
                    if fc.data_path.endswith(".rotation_quaternion"):
                        osso = fc.data_path.split('"')[1]
                        if osso in CONJ: quat.setdefault(osso, {})[fc.array_index] = fc
                for osso, fcs in quat.items():
                    if len(fcs) != 4 or len({len(f.keyframe_points) for f in fcs.values()}) != 1:
                        print("AVISO_QUAT", nova.name, osso); continue
                    C = CONJ[osso]; Ci = C.inverted()
                    for i in range(len(fcs[0].keyframe_points)):
                        q = Quaternion([fcs[c].keyframe_points[i].co[1] for c in range(4)])
                        q2 = Ci @ q @ C
                        for c in range(4):
                            kp = fcs[c].keyframe_points[i]; kp.co[1] = q2[c]; kp.interpolation = "LINEAR"
                for fc in cb.fcurves:
                    if fc.data_path.endswith(".location"):
                        for kp in fc.keyframe_points:
                            maxloc = max(maxloc, abs(kp.co[1]))
                            kp.co[1] *= k; kp.handle_left[1] *= k; kp.handle_right[1] *= k
    nova.use_fake_user = True
    print("ACAO", nova.name, tuple(nova.frame_range), "maxloc_molde", round(maxloc, 4))
for act in acoes: bpy.data.actions.remove(act)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "Silverwing_M2M.blend"))
print("MONTAR_OK")
