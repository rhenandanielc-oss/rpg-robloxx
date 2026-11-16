"""Uivo Boreal - camada de efeito do corpo do Lobo Artico (16/11/2026; REFERENCIAS_PODERES_E_EFEITOS.md v5.2 §5.1/§5.3).
Gera, sobre o modelo aprovado (anim_v41/CR_LoboArtico_Anim.blend, pose de REPOUSO do rig):
  * LINHAS azul-gelo: fitas finas e continuas que seguem o corpo POR CIMA do pelo (costas, flancos, pescoco ate a nuca,
    pernas e cauda; rosto limpo). Divididas em 6 regioes (Linhas_1 pescoco ... Linhas_6 cauda) para o brilho
    percorrer da cabeca para a cauda. Pele (Armature) copiada da LOW_Corpo por proximidade -> seguem a animacao.
  * ESPINHOS de gelo: fileira na linha do dorso, da nuca a garupa, maiores no pescoco e menores para a cauda,
    inclinados para tras, facetados (faces claras/escuras), com uma ponta secundaria menor na base. Cada espinho e um
    objeto RIGIDO (sem pele) com a origem na base; no Roblox o cliente prende cada um ao osso mais proximo e faz
    crescer (0,6 s) / recolher (0,8 s).
Saidas: boreal/CR_LoboArtico_Boreal.blend, boreal/export/CR_LoboArtico_BorealFX.glb (rig + linhas + espinhos),
boreal/export/boreal_fx.json (espinhos: osso, base, eixo, altura; linhas: regioes e tris).
Uso: blender -b anim_v41/CR_LoboArtico_Anim.blend -P boreal/boreal_fx.py -- [r1]"""
import bpy, bmesh, sys, os, math, json
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
VER = ARGS[0] if ARGS else "r1"
AQUI = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.join(AQUI, "export"); os.makedirs(EXP, exist_ok=True)

rig = bpy.data.objects["LoboArtico_Rig"]
rig.data.pose_position = "REST"
bpy.context.view_layer.update()
corpo = bpy.data.objects["LOW_Corpo"]
pelo = bpy.data.objects["LOW_Pelagem"]

def bvh_de(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    for o in objs:
        me = o.evaluated_get(dg).to_mesh()
        tmp = bmesh.new(); tmp.from_mesh(me); tmp.transform(o.matrix_world)
        me2 = bpy.data.meshes.new("tmp"); tmp.to_mesh(me2); tmp.free()
        bm.from_mesh(me2); bpy.data.meshes.remove(me2)
        o.evaluated_get(dg).to_mesh_clear()
    t = BVHTree.FromBMesh(bm); bm.free()
    return t
BVH_PELE = bvh_de([corpo])
BVH_PELO = bvh_de([corpo, pelo])
BVH_TOPO = bvh_de([corpo, bpy.data.objects["LOW_Cabeca"]])

def osso(n):
    b = rig.data.bones[n]
    return rig.matrix_world @ b.head_local, rig.matrix_world @ b.tail_local

def cadeia(nomes, ate_cauda=True):
    pts = []
    for n in nomes:
        h, t = osso(n); pts.append(h)
    if ate_cauda: pts.append(osso(nomes[-1])[1])
    return pts

def reamostrar(pts, passo):
    out = [pts[0]]; acum = 0.0
    seg = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    for a, b in seg:
        L = (b - a).length; d = passo - acum
        while d <= L:
            out.append(a.lerp(b, d / L)); d += passo
        acum = L - (d - passo)
    if (out[-1] - pts[-1]).length > passo * 0.3: out.append(pts[-1])
    return out

def suavizar(pts, n=3, it=4):
    p = [v.copy() for v in pts]
    for _ in range(it):
        q = [v.copy() for v in p]
        for i in range(1, len(p) - 1):
            a, b = max(0, i - n), min(len(p), i + n + 1)
            m = V((0, 0, 0))
            for k in range(a, b): m += p[k]
            q[i] = m / (b - a)
        p = q
    return p

def superficie(P, d, bvh, folga):
    """ponto na superficie EXTERNA na direcao d a partir de P (lanca de fora para dentro)"""
    o = P + d * 4.0
    hit, nrm, idx, dist = bvh.ray_cast(o, -d, 4.0)
    if hit is None: return None, None
    return hit + d * folga, nrm

def base_local(T):
    up = V((0, 0, 1)); U = (up - T * up.dot(T)).normalized(); S = T.cross(U).normalized()
    return U, S

PESO_PELO = lambda P: 0.15
def linha_corpo(eixo_pts, theta, passo=0.12, folga=0.05, pelo_tambem=True):
    """linha que corre ao longo do eixo (centro do corpo em cada fatia) no angulo theta (0 = dorso, + = esquerda)"""
    amostras = reamostrar(eixo_pts, passo)
    res = []
    for i, P in enumerate(amostras):
        T = (amostras[min(i + 1, len(amostras) - 1)] - amostras[max(i - 1, 0)]).normalized()
        U, S = base_local(T)
        # centro da fatia: entre o topo e o fundo na vertical local
        top, _ = superficie(P, U, BVH_PELE, 0); bot, _ = superficie(P, -U, BVH_PELE, 0)
        C = (top + bot) / 2 if (top and bot) else P
        d = (U * math.cos(theta) + S * math.sin(theta)).normalized()
        q, _ = superficie(C, d, BVH_PELO if pelo_tambem else BVH_PELE, folga)
        q2, _ = superficie(C, d, BVH_PELE, folga + 0.10)
        if q is None and q2 is None: continue
        # raio: mediana entre pele+0,15 e casca do pelo (o pelo e ruidoso)
        # r2: o pelo (cartoes longos) empurrava a linha para fora do corpo -> pele + folga, com um pouco do pelo
        # so no pescoco (juba); e nunca mais que 0,22 acima da pele
        if q2 is None: continue
        rp = (q2 - C).length
        # r3: no pescoco (juba) e na cauda a linha fica NA superficie do pelo, senao some
        w = PESO_PELO(P)
        r = rp if q is None else (1 - w) * rp + w * min((q - C).length, rp + (0.55 if w > 0.5 else 0.22))
        res.append(C + d * r)
    return suavizar(res, 3, 5)

def linha_perna(nomes, lado, passo=0.10):
    """linha pelo lado de fora da perna (lado: +1 esquerda/E = +X no Blender, -1 direita)"""
    pts = reamostrar(cadeia(nomes, ate_cauda=False), passo)
    res = []
    for i, P in enumerate(pts):
        T = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        fora = V((lado, 0, 0)); fora = (fora - T * fora.dot(T)).normalized()
        frente = V((0, -1, 0)); frente = (frente - T * frente.dot(T)).normalized()
        d = (fora * 0.85 + frente * 0.35).normalized()
        q2, _ = superficie(P, d, BVH_PELE, 0.07)          # r2: perna so na pele (pelo curto; o rabo e a coxa atrapalhavam)
        if q2 is not None and (q2 - P).length < 1.6: res.append(q2)
    return suavizar(res, 2, 4)

# ---- eixo do corpo: nuca -> coluna -> quadril; cauda separada ------------------------------------------------------
eixo_corpo = cadeia(["Pescoco2", "Pescoco1", "Coluna3", "Coluna2", "Coluna1", "Quadril"], ate_cauda=False)
# ordem: o rig vai da cauda para a cabeca? garantir nuca -> garupa (y crescente: frente do lobo e -Y)
eixo_corpo = sorted(eixo_corpo, key=lambda v: v.y)
nuca = osso("Cabeca")[0]
eixo_corpo = [nuca] + eixo_corpo
eixo_cauda = cadeia(["Cauda1", "Cauda2", "Cauda3", "Cauda4"])

LARG = 0.075            # ~1,1% da altura do corpo (6,7)
linhas = {}             # regiao -> lista de polilinhas
def regiao_de(y):
    # 1 pescoco | 2 ombros | 3 costas | 4 garupa | 5 pernas (atribuidas a parte) | 6 cauda
    if y < -2.4: return 1
    if y < -0.6: return 2
    if y < 1.4: return 3
    return 4

polis = []
PESO_PELO = lambda P: 0.9 if P.y < -2.6 else (0.9 - (P.y + 2.6) * 0.75 if P.y < -1.6 else 0.15)
for th, ini in ((0.0, -4.3), (math.radians(42), -4.4), (math.radians(-42), -4.4), (math.radians(88), -3.4), (math.radians(-88), -3.4)):
    pl = linha_corpo(eixo_corpo, th)
    pl = [p for p in pl if p.y >= ini and p.y <= 3.4]
    polis.append(("corpo", pl))
PESO_PELO = lambda P: 0.7
polis.append(("cauda", linha_corpo(eixo_cauda + [eixo_cauda[-1]], 0.0, passo=0.10, folga=0.04)))
PESO_PELO = lambda P: 0.15
for nomes, lado in ((["Umero_E", "Antebraco_E", "Metacarpo_E", "Dedos_E"], 1), (["Umero_D", "Antebraco_D", "Metacarpo_D", "Dedos_D"], -1),
                    (["Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E"], 1), (["Coxa_D", "Tibia_D", "Metatarso_D", "DedosPe_D"], -1)):
    polis.append(("perna", linha_perna(nomes, lado)))

def fita(pl, largura, bvh_normal=BVH_PELO):
    """fita voltada para fora (normal da superficie mais proxima), com pontas afinando"""
    vs, fs = [], []
    n = len(pl)
    for i, p in enumerate(pl):
        T = (pl[min(i + 1, n - 1)] - pl[max(i - 1, 0)]).normalized()
        loc, nrm, idx, dist = BVH_PELE.find_nearest(p)
        N = (p - loc).normalized() if loc is not None and (p - loc).length > 1e-4 else V((0, 0, 1))
        W = T.cross(N).normalized()
        afina = min(1.0, i / 4.0, (n - 1 - i) / 4.0)
        w = largura * (0.35 + 0.65 * afina) / 2
        vs += [p + W * w, p - W * w]
        if i: k = 2 * i; fs.append((k - 2, k - 1, k + 1, k))
    return vs, fs

def objeto_de(nome, partes):
    me = bpy.data.meshes.new(nome); bm = bmesh.new()
    for vs, fs in partes:
        base = len(bm.verts); vv = [bm.verts.new(v) for v in vs]
        for f in fs:
            try: bm.faces.new([vv[j] for j in f])
            except ValueError: pass
    bm.normal_update(); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(ob)
    return ob

grupos = {k: [] for k in range(1, 7)}
for tipo, pl in polis:
    if len(pl) < 3: continue
    if tipo == "cauda": grupos[6].append(fita(pl, LARG * 0.9)); continue
    if tipo == "perna":
        g = 2 if pl[0].y < 0 else 4; grupos[g].append(fita(pl, LARG * 0.8)); continue
    # corpo: corta a polilinha por regiao (com 1 ponto de sobreposicao para nao abrir fresta)
    atual, seg = None, []
    for p in pl:
        r = regiao_de(p.y)
        if atual is not None and r != atual:
            seg.append(p); grupos[atual].append(fita(seg, LARG)); seg = [seg[-2], p] if len(seg) > 1 else [p]
        atual = r; seg.append(p)
    if len(seg) > 2: grupos[atual].append(fita(seg, LARG))

MAT_L = bpy.data.materials.new("M_Boreal_Linhas")
if MAT_L.node_tree is None: MAT_L.use_nodes = True
pb = MAT_L.node_tree.nodes["Principled BSDF"]
pb.inputs["Base Color"].default_value = (0.25, 0.62, 1.0, 1); pb.inputs["Emission Color"].default_value = (0.30, 0.68, 1.0, 1)
pb.inputs["Emission Strength"].default_value = 1.2

objs_linhas = []
for g, partes in grupos.items():
    if not partes: continue
    ob = objeto_de("Linhas_%d" % g, partes); ob.data.materials.append(MAT_L)
    objs_linhas.append(ob)

# pele: copia pesos da LOW_Corpo por proximidade e Armature do rig
for ob in objs_linhas:
    for vg in corpo.vertex_groups: ob.vertex_groups.new(name=vg.name)
    dt = ob.modifiers.new("Pesos", "DATA_TRANSFER"); dt.object = corpo
    dt.use_vert_data = True; dt.data_types_verts = {"VGROUP_WEIGHTS"}; dt.vert_mapping = "POLYINTERP_NEAREST"
    dt.layers_vgroup_select_src = "ALL"; dt.layers_vgroup_select_dst = "NAME"
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=dt.name)
    ob.parent = rig
    am = ob.modifiers.new("Armature", "ARMATURE"); am.object = rig

# ---- espinhos ----------------------------------------------------------------------------------------------------------
dorso = linha_corpo(eixo_corpo, 0.0, passo=0.08, folga=0.0)
def ponto_dorso(y):
    # r4: raio de cima sobre a pele (o dorso amostrado nao cobria a nuca e dois espinhos caiam no mesmo ponto);
    # +0,12 de pelo, igual ao resto do dorso
    # r5: o pescoco de cima e coberto pela LOW_Cabeca (a LOW_Corpo nao tem topo ali): inclui a cabeca no alvo
    hit, nrm, idx, dist = BVH_TOPO.ray_cast(V((0, y, 12)), V((0, 0, -1)), 20)
    if hit is None: return min(dorso, key=lambda p: abs(p.y - y))
    return hit + V((0, 0, 0.22 if y < -2.4 else 0.12))
CRIST_Y = (-3.30, -1.55)          # zona dos cristais permanentes (LOW_Cristais): nao colocar espinho em cima
# r6: na nuca os espinhos viravam chifre entre as orelhas; os cristais permanentes ja sao o ponto mais alto do
# pescoco -> a fileira comeca logo atras deles e diminui ate a garupa
POS_Y = [-1.35, -0.82, -0.28, 0.27, 0.82, 1.37, 1.92, 2.47]
H0, H1 = 0.95, 0.36

MAT_E = bpy.data.materials.new("M_Boreal_Espinho")
if MAT_E.node_tree is None: MAT_E.use_nodes = True
pe = MAT_E.node_tree.nodes["Principled BSDF"]
pe.inputs["Base Color"].default_value = (0.70, 0.88, 1.0, 1); pe.inputs["Roughness"].default_value = 0.12
pe.inputs["Transmission Weight"].default_value = 0.35; pe.inputs["Emission Color"].default_value = (0.45, 0.78, 1.0, 1)
pe.inputs["Emission Strength"].default_value = 0.6

def cristal(bm, base, eixo, altura, raio, lados, giro, inclina_lado=V((0, 0, 0))):
    eixo = eixo.normalized()
    a = eixo.orthogonal().normalized(); b = eixo.cross(a)
    anel = []
    for k in range(lados):
        ang = giro + 2 * math.pi * k / lados
        rr = raio * (0.85 + 0.3 * ((k * 37) % 7) / 7)            # irregular (faces de tamanhos diferentes)
        anel.append(bm.verts.new(base + (a * math.cos(ang) + b * math.sin(ang)) * rr))
    meio = [bm.verts.new(base + eixo * altura * 0.55 + (v.co - base) * 0.62 + inclina_lado * altura * 0.1) for v in anel]
    ponta = bm.verts.new(base + eixo * altura + inclina_lado * altura * 0.15)
    for k in range(lados):
        k2 = (k + 1) % lados
        bm.faces.new((anel[k], anel[k2], meio[k2], meio[k]))
        bm.faces.new((meio[k], meio[k2], ponta))
    bm.faces.new(list(reversed(anel)))

espinhos = []
for i, y in enumerate(POS_Y):
    t = i / (len(POS_Y) - 1)
    h = H0 + (H1 - H0) * (t ** 0.8)
    p = ponto_dorso(y)
    loc, nrm, idx, dist = BVH_PELE.find_nearest(p)
    Nn = (p - loc).normalized() if (p - loc).length > 1e-4 else V((0, 0, 1))
    eixo = (Nn + V((0, 0.62, 0))).normalized()                    # inclinado para tras (~32 graus)
    base = p - eixo * 0.22 * h                                     # base enterrada no pelo
    me = bpy.data.meshes.new("Espinho_%02d" % (i + 1)); bm = bmesh.new()
    cristal(bm, V((0, 0, 0)), eixo, h, max(0.085, 0.20 * h), 6, 0.4 * i)
    lado = 1 if i % 2 == 0 else -1
    eixo2 = (eixo + V((0.55 * lado, 0.15, -0.1))).normalized()
    cristal(bm, eixo * 0.08 * h + V((0.07 * lado, 0.05, 0)), eixo2, 0.36 * h, max(0.045, 0.085 * h), 5, 1.1 * i)
    bm.normal_update(); bm.to_mesh(me); bm.free()
    for f in me.polygons: f.use_smooth = False
    ob = bpy.data.objects.new(me.name, me); bpy.context.scene.collection.objects.link(ob)
    ob.location = base; ob.data.materials.append(MAT_E)
    # osso mais proximo da base (para prender no Roblox)
    melhor, dm = None, 1e9
    for b in rig.data.bones:
        if b.name.startswith(("Coluna", "Pescoco", "Quadril", "Cabeca")):
            h0, t0 = osso(b.name)
            # distancia ao segmento
            ab = t0 - h0; u = max(0, min(1, (base - h0).dot(ab) / ab.length_squared)); d = (h0 + ab * u - base).length
            if d < dm: dm, melhor = d, b.name
    espinhos.append({"nome": ob.name, "osso": melhor, "base": list(base), "eixo": list(eixo), "altura": round(h, 3)})
    ob.parent = rig; ob.parent_type = "BONE"; ob.parent_bone = melhor
    ob.matrix_world = Matrix.Translation(base)

# ---- relatorio, arquivo e exportacao -----------------------------------------------------------------------------------
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
rel = {"versao": VER, "espinhos": espinhos, "linhas": {o.name: tris(o) for o in objs_linhas},
       "espinhos_tris": sum(tris(bpy.data.objects[e["nome"]]) for e in espinhos),
       "obs": "Blender: frente -Y, esquerda +X, cima +Z; base em coordenadas do mundo em REPOUSO (origem = pivo do modelo)"}
json.dump(rel, open(os.path.join(EXP, "boreal_fx_%s.json" % VER), "w"), indent=1)
print("LINHAS", rel["linhas"], "ESPINHOS_TRIS", rel["espinhos_tris"])
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, "CR_LoboArtico_Boreal_%s.blend" % VER))
print("BOREAL_OK")
