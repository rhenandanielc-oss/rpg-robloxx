"""Rig do Cervo-do-Bosque (fauna de recurso) sobre a malha de jogo v2 (low_v2: Cervo_Cabeca + Cervo_Corpo, 12k tris).
Adaptado do rig ungulado do Bufalo (Bufalo_Colossal_Ref/build/44_rig.py), escala ~1/8. Nomes ja sao os do jogo
(o Roblox liga malha a osso pelo NOME). Sem Mandibula: a boca da fauna e fechada (sem cavidade).
Marcos medidos na malha: cascos (pontos mais baixos por quadrante), colunas das patas em fatias, linha da espinha
pelo perfil, nuca/focinho/orelhas na cabeca. Alturas das juntas pela anatomia de cervideo (blockout r1).
Pesos: Raiz nao deforma; heat num PROXY voxel das duas malhas -> Data Transfer; cabeca e galhada rigidas (Cabeca);
orelhas -> Orelha E/D; abaixo do boleto -> Quartela. Maximo 4 influencias, normalizado.
Gera tambem poses de teste (renders) para conferir a deformacao.
Uso: blender -b low_v2/CR_Cervo_do_Bosque_LOW.blend -P rig/rig_cervo.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, Euler
from mathutils.kdtree import KDTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def ativar(o):
    for x in sc.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
for o in list(sc.objects):
    if o.type in ("CAMERA", "LIGHT") or (o.type == "MESH" and o.name not in ("Cervo_Cabeca", "Cervo_Corpo")):
        bpy.data.objects.remove(o)
CAB, CORPO = bpy.data.objects["Cervo_Cabeca"], bpy.data.objects["Cervo_Corpo"]
MALHAS = [CAB, CORPO]
def coords(o):
    a = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", a); return a.reshape(-1, 3)
co = np.vstack([coords(o) for o in MALHAS]); x, y, z = co[:, 0], co[:, 1], co[:, 2]
NARIZ_Y, Y1 = y.min(), y.max()
# ------------------------------------------------------------------ cascos e colunas das patas
cb = coords(CORPO); baixo = cb[cb[:, 2] < 0.035]
cen = np.array([[0.08, -0.36], [-0.08, -0.36], [0.12, 0.45], [-0.12, 0.55]])
for _ in range(25):                                  # k-means com 4 cascos (o Meshy deixa as traseiras desalinhadas)
    k = ((baixo[:, None, :2] - cen[None]) ** 2).sum(-1).argmin(1)
    cen = np.array([baixo[k == i, :2].mean(0) for i in range(4)])
PATAS = {}
for i, (lado, par) in enumerate((("E", "dian"), ("D", "dian"), ("E", "tras"), ("D", "tras"))):
    s_ = baixo[k == i]; c = s_[:, :2].mean(0); frente = s_[:, 1].min(); sx = 1 if lado == "E" else -1
    pts = []; cur = c.copy()
    for zz in np.arange(0.06, 0.62, 0.04):          # segue a coluna da pata para cima
        m = (np.abs(cb[:, 2] - zz) < 0.02) & (np.hypot(cb[:, 0] - cur[0], cb[:, 1] - cur[1]) < 0.09)
        if m.sum() > 6: cur = cb[m][:, :2].mean(0); pts.append((zz, cur.copy()))
    PATAS[(lado, par)] = {"casco": c, "col": pts, "frente_y": float(frente), "sx": sx}
    print("PATA", lado, par, "casco", c.round(3), "frente", round(float(frente), 3), "pontos coluna", len(pts))
def col_em(p, zz):
    pts = p["col"]
    if not pts: return V((p["casco"][0], p["casco"][1], zz))
    best = min(pts, key=lambda t: abs(t[0] - zz)); return V((best[1][0], best[1][1], zz))
def fatia_y(yy, f=0.02, xm=0.04, zmin=0.5, zmax=1.6):
    s = (np.abs(y - yy) < f) & (np.abs(x) < xm) & (z > zmin) & (z < zmax)
    return (z[s].min(), z[s].max()) if s.any() else (0.8, 1.1)
def espinha(yy, frac=0.38):
    a, b = fatia_y(yy); return V((0, yy, b - frac * (b - a)))
yo = float(np.mean([PATAS[(l, "dian")]["casco"][1] for l in "ED"])); yq = float(np.mean([PATAS[(l, "tras")]["casco"][1] for l in "ED"]))
# cabeca: nuca e focinho pelo perfil central (|x| < 0,025 evita pedicelos/galhada)
def perfil(yy):
    s = (np.abs(y - yy) < 0.012) & (np.abs(x) < 0.025) & (z > 1.0)
    return (z[s].min(), z[s].max()) if s.any() else None
pn = perfil(NARIZ_Y + 0.02); NARIZ = V((0, NARIZ_Y + 0.01, (pn[0] + pn[1]) / 2))
pc = perfil(NARIZ_Y + 0.23); NUCA = V((0, NARIZ_Y + 0.23, pc[1] - 0.09))       # junta atlas: abaixo do topo do cranio
print("CABECA nariz", tuple(round(c, 3) for c in NARIZ), "nuca", tuple(round(c, 3) for c in NUCA), "perfil nuca", [round(c, 3) for c in pc])
# orelhas: ponta = vertice mais lateral atras dos olhos, abaixo da galhada
cc = coords(CAB)
ORE = {}
def e_orelha(p):                                      # orelha: lateral, abaixo da galhada, atras dos olhos
    return abs(p[0]) > 0.105 and 1.42 < p[2] < 1.64 and NARIZ_Y + 0.20 < p[1] < NARIZ_Y + 0.40
def e_galhada(p):
    # acima de 1,62 so existe galhada (o dorso/pescoco nao passam de ~1,53); ramos de tras invadem a malha do corpo
    return p[2] > 1.62 or (p[2] > 1.54 and 0.025 < abs(p[0]) < 0.105 and NARIZ_Y + 0.15 < p[1] < NARIZ_Y + 0.33)
for sx, lado in ((1, "E"), (-1, "D")):
    sub = np.array([q for q in cc if np.sign(q[0]) == sx and e_orelha(q)])
    pont = sub[(sub[:, 2] < 1.60) & (sub[:, 1] > NARIZ_Y + 0.24) & (sub[:, 1] < NARIZ_Y + 0.36)]   # ponta da orelha, nao da galhada
    tip = pont[np.argmax(np.abs(pont[:, 0]))]; raiz = sub[np.abs(sub[:, 0]) < 0.125]
    base = V(tuple(raiz.mean(0))); base.x = sx * 0.095
    ORE[lado] = (base, V(tuple(tip)))
    print("ORELHA", lado, len(sub), "base", tuple(round(c, 3) for c in base), "ponta", tuple(round(float(c), 3) for c in tip))
# ------------------------------------------------------------------ proxy voxel fechado das duas malhas (heat e checagem dos ossos)
prox = CORPO.copy(); prox.data = CORPO.data.copy(); prox.name = "tmp_Proxy"; sc.collection.objects.link(prox)
c2 = CAB.copy(); c2.data = CAB.data.copy(); sc.collection.objects.link(c2)
ativar(prox); c2.select_set(True); bpy.ops.object.join()
for g in list(prox.vertex_groups): prox.vertex_groups.remove(g)
r_ = prox.modifiers.new("R", "REMESH"); r_.mode = "VOXEL"; r_.voxel_size = 0.012; bpy.ops.object.modifier_apply(modifier=r_.name)
s_ = prox.modifiers.new("S", "SMOOTH"); s_.factor = 0.5; s_.iterations = 2; bpy.ops.object.modifier_apply(modifier=s_.name)
from mathutils.bvhtree import BVHTree
BVP = BVHTree.FromObject(prox, bpy.context.evaluated_depsgraph_get())
def dentro_p(p):
    n_ = 0; o_ = V(p)
    for _ in range(60):
        h = BVP.ray_cast(o_, V((0.0013, 0.0007, 1)).normalized(), 5.0)
        if h[0] is None: break
        n_ += 1; o_ = h[0] + V((0, 0, 1e-5))
    return n_ % 2 == 1
# ------------------------------------------------------------------ esqueleto (nomes do jogo)
arm_d = bpy.data.armatures.new("Cervo_Rig"); arm = bpy.data.objects.new("Cervo_Rig", arm_d); sc.collection.objects.link(arm)
ativar(arm); bpy.ops.object.mode_set(mode="EDIT"); E = arm_d.edit_bones
def osso(nome, a, b, pai=None, conecta=True):
    o = E.new(nome); o.head = V(a); o.tail = V(b)
    if pai: o.parent = E[pai]; o.use_connect = conecta and (E[pai].tail - V(a)).length < 1e-4
    return o
osso("Raiz", (0, (yq + yo) / 2, 0), (0, (yq + yo) / 2 - 0.19, 0))
def dorso(yy, abaixo=0.12):           # topo da garupa/lombo (janela larga) menos uma profundidade fixa
    s_ = (np.abs(y - yy) < 0.05) & (np.abs(x) < 0.08) & (z > 0.6) & (z < 1.4)
    return V((0, yy, (z[s_].max() if s_.any() else 1.1) - abaixo))
osso("Pelve", dorso(yq + 0.16), dorso(yq - 0.06), "Raiz", False)
osso("Coluna1", E["Pelve"].tail, dorso(yq - 0.30, 0.13), "Pelve")
osso("Coluna2", E["Coluna1"].tail, espinha(yo + 0.20, 0.40), "Coluna1")
osso("Coluna3", E["Coluna2"].tail, espinha(yo + 0.02, 0.45), "Coluna2")                    # cernelha
base_pesc = E["Coluna3"].tail.copy()
meio = base_pesc.lerp(NUCA, 0.5) + V((0, -0.03, 0.02))
osso("Pescoco", base_pesc, meio, "Coluna3")
osso("Pescoco2", meio, NUCA, "Pescoco")
osso("Cabeca", NUCA, NARIZ, "Pescoco2")
for lado in "ED":
    b, t = ORE[lado]; osso("Orelha" + lado, b, t, "Cabeca", False)
# cauda: tufo curto pendente atras da garupa (medido: y Y1-0,06..Y1, z ~0,98 -> 0,77)
mc = (y > Y1 - 0.07) & (np.abs(x) < 0.06) & (z > 0.6)
ct, cbx = z[mc].max(), z[mc].min()
osso("Cauda1", V((0, Y1 - 0.06, ct - 0.03)), V((0, Y1 - 0.035, (ct + cbx) / 2)), "Pelve", False)
osso("Cauda2", E["Cauda1"].tail, V((0, Y1 - 0.02, cbx + 0.025)), "Cauda1")
for lado in "ED":
    p = PATAS[(lado, "dian")]; c = p["casco"]; sx = p["sx"]
    fet = V((c[0], c[1] + 0.01, 0.105)); car = col_em(p, 0.32) + V((0, 0.005, 0)); cot = col_em(p, 0.60) + V((0, 0.035, 0.03))
    cot.z = 0.63; omb = V((cot.x * 0.95, cot.y - 0.08, 0.84)); esc = V((sx * 0.07, cot.y + 0.10, 1.13))
    toe = V((c[0], p["frente_y"] + 0.012, 0.012))
    osso("Escapula" + lado, esc, omb, "Coluna3", False); osso("Braco" + lado, omb, cot, "Escapula" + lado)
    osso("Antebraco" + lado, cot, car, "Braco" + lado); osso("Canela" + lado, car, fet, "Antebraco" + lado)
    osso("Quartela" + lado, fet, toe, "Canela" + lado)
    p = PATAS[(lado, "tras")]; c = p["casco"]; sx = p["sx"]
    def borda(zz, lado_y):              # fatia da pata traseira: borda de tras (jarrete) ou da frente (joelho)
        m = (np.abs(cb[:, 2] - zz) < 0.02) & (np.sign(cb[:, 0]) == sx) & (np.abs(cb[:, 0]) > 0.04) & (cb[:, 1] > c[1] - 0.35)
        q = cb[m]; return q, (q[:, 1].max() if lado_y > 0 else q[:, 1].min())
    qj, yj = borda(0.40, 1); qk, yk = borda(0.64, -1)
    fet = V((c[0], c[1] + 0.012, 0.105)); jar = V((float(qj[:, 0].mean()), yj - 0.035, 0.38))
    joe = V((float(qk[:, 0].mean()), yk + 0.06, 0.64)); qua = V((sx * 0.085, joe.y + 0.13, 0.96))
    print("TRASEIRA", lado, "jarrete", tuple(round(c_, 3) for c_ in jar), "joelho", tuple(round(c_, 3) for c_ in joe))
    toe = V((c[0], p["frente_y"] + 0.012, 0.012))
    osso("Coxa" + lado, qua, joe, "Pelve", False); osso("Perna" + lado, joe, jar, "Coxa" + lado)
    osso("CanelaTras" + lado, jar, fet, "Perna" + lado); osso("QuartelaTras" + lado, fet, toe, "CanelaTras" + lado)
# diagnostico: pontas de osso fora do proxy (pontas de pata e cauda fora sao normais e nao impedem o heat)
PUXADOS = []
for b in E:
    if b.name in ("Raiz", "OrelhaE", "OrelhaD"): continue
    if b.use_connect: b.head = b.parent.tail
    for ponta in ("head", "tail"):
        pp = getattr(b, ponta)
        if (ponta == "head" and b.use_connect) or dentro_p(pp): continue
        loc, nrm, _, d = BVP.find_nearest(pp); PUXADOS.append((b.name, ponta, round(d, 3)))   # so diagnostico (mover encurta ossos)
for b in E:
    if b.use_connect: b.head = b.parent.tail
print("OSSOS com ponta fora do proxy", PUXADOS)
for b in E: b.roll = 0.0
bpy.ops.object.mode_set(mode="OBJECT")
arm_d.bones["Raiz"].use_deform = False
print("OSSOS", len(arm_d.bones), [b.name for b in arm_d.bones])
# ------------------------------------------------------------------ pesos: heat num proxy voxel das duas malhas -> transferencia
for nm in ("OrelhaE", "OrelhaD"): arm_d.bones[nm].use_deform = False      # orelha e mais fina que o voxel: peso manual
ativar(prox); arm.select_set(True); bpy.context.view_layer.objects.active = arm
try: bpy.ops.object.parent_set(type="ARMATURE_AUTO")
except Exception as e: print("HEAT erro:", e)
print("HEAT proxy verts", len(prox.data.vertices), "sem peso", sum(1 for v in prox.data.vertices if not v.groups))
for o in MALHAS:
    for g in list(o.vertex_groups): o.vertex_groups.remove(g)
    for g in prox.vertex_groups: o.vertex_groups.new(name=g.name)
    ativar(o); dt = o.modifiers.new("DT", "DATA_TRANSFER"); dt.object = prox; dt.use_vert_data = True
    dt.data_types_verts = {"VGROUP_WEIGHTS"}; dt.vert_mapping = "POLYINTERP_NEAREST"; dt.layers_vgroup_select_src = "ALL"; dt.layers_vgroup_select_dst = "NAME"
    bpy.ops.object.modifier_apply(modifier=dt.name)
bpy.data.objects.remove(prox)
for nm in ("OrelhaE", "OrelhaD"): arm_d.bones[nm].use_deform = True
def grupo(o, nm): return o.vertex_groups.get(nm) or o.vertex_groups.new(name=nm)
def zera_e_poe(o, v, pesos):
    for g in list(v.groups): o.vertex_groups[g.group].remove([v.index])
    for nm, w in pesos.items():
        if w > 1e-4: grupo(o, nm).add([v.index], w, "REPLACE")
def mistura(o, v, nm, f):     # puxa o vertice para o osso nm com fator f, mantendo o resto proporcional
    for g in list(v.groups):
        if o.vertex_groups[g.group].name != nm: o.vertex_groups[g.group].add([v.index], g.weight * (1 - f), "REPLACE")
    atual = next((g.weight for g in v.groups if o.vertex_groups[g.group].name == nm), 0.0)
    grupo(o, nm).add([v.index], atual + f, "REPLACE")
Y_CAB_DURA = NARIZ_Y + 0.24          # a frente disso: cabeca rigida (cranio, focinho, galhada)
# o voxel fundiu a ponta da orelha E com um ramo da galhada: perto da galhada a orelha fica presa a Cabeca (a ponte estica ao girar).
# Tentativa de apagar a ponte (12/11) descartada: a faixa z 1,62-1,64 e ambigua e o corte apagava borda de orelha e costura.
_gal = [q for q in coords(CAB) if q[2] > 1.645 and q[1] < NARIZ_Y + 0.55]      # galhada inequivoca (a faixa 1,62-1,64 e ambigua)
KD_GAL = KDTree(len(_gal))
for i_, q in enumerate(_gal): KD_GAL.insert(V(tuple(q)), i_)
KD_GAL.balance()
Z_TOPO = 1.56
for o in MALHAS:
    me = o.data
    vaz = [v for v in me.vertices if not v.groups]
    if vaz:
        kd = KDTree(len(me.vertices) - len(vaz))
        for v in me.vertices:
            if v.groups: kd.insert(v.co, v.index)
        kd.balance()
        for v in vaz:
            _, j, _ = kd.find(v.co)
            for g in me.vertices[j].groups: o.vertex_groups[g.group].add([v.index], g.weight, "REPLACE")
    n_cab = n_ore = 0
    FIXOS = {}                       # pesos rigidos reaplicados depois da suavizacao
    for v in me.vertices:
        p = v.co
        galhada = e_galhada(p)
        orelha = None
        if e_orelha(p):
            lado = "E" if p.x > 0 else "D"
            _, _, dg_ = KD_GAL.find(p)
            orelha = (lado, suave((abs(p.x) - 0.10) / 0.05) * suave((dg_ - 0.004) / 0.045))
        if orelha:
            lado, f = orelha; FIXOS[v.index] = {"Orelha" + lado: f, "Cabeca": 1 - f}; zera_e_poe(o, v, FIXOS[v.index]); n_ore += 1
        elif galhada or p.y < Y_CAB_DURA:
            FIXOS[v.index] = {"Cabeca": 1.0}; zera_e_poe(o, v, FIXOS[v.index]); n_cab += 1
        elif p.y < Y_CAB_DURA + 0.08 and p.z > 1.05:
            mistura(o, v, "Cabeca", suave((Y_CAB_DURA + 0.08 - p.y) / 0.08)); n_cab += 1
    # abaixo do boleto: pele segue a quartela da pata
    for (lado, par), pt in PATAS.items():
        nmq = ("Quartela" if par == "dian" else "QuartelaTras") + lado; c = pt["casco"]
        for v in me.vertices:
            q = v.co
            if q.z > 0.15 or math.hypot(q.x - c[0], q.y - c[1]) > 0.09: continue
            mistura(o, v, nmq, suave((0.15 - q.z) / 0.06))
    print("PESOS", o.name, "cabeca rigida", n_cab, "orelhas", n_ore)
    ativar(o)
    for g in o.vertex_groups: g.lock_weight = g.name in ("Cabeca",)
    bpy.ops.object.mode_set(mode="WEIGHT_PAINT"); bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=0.5, repeat=2); bpy.ops.object.mode_set(mode="OBJECT")
    for g in o.vertex_groups: g.lock_weight = False
    bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
    for i, pesos in FIXOS.items(): zera_e_poe(o, me.vertices[i], pesos)     # galhada/cranio rigidos, orelhas exatas
    for g in list(o.vertex_groups):
        if not any(gg.group == g.index for v in me.vertices for gg in v.groups): o.vertex_groups.remove(g)
    ativar(o); arm.select_set(True); bpy.context.view_layer.objects.active = arm; bpy.ops.object.parent_set(type="ARMATURE_NAME")
    infl = max(len([g for g in v.groups if g.weight > 1e-4]) for v in me.vertices); semp = sum(1 for v in me.vertices if not v.groups)
    print("PESOS", o.name, "grupos", len(o.vertex_groups), "max infl", infl, "sem peso", semp)
# costura cabeca/corpo: vertices de borda na mesma posicao recebem os MESMOS pesos (senao a costura abre ao dobrar)
def bordas(o):
    bm_ = bmesh.new(); bm_.from_mesh(o.data); idx = [v.index for v in bm_.verts if v.is_boundary]; bm_.free(); return idx
bc = bordas(CORPO); kd = KDTree(len(bc))
for i in bc: kd.insert(CORPO.data.vertices[i].co, i)
kd.balance(); copiados = 0
for i in bordas(CAB):
    vc = CAB.data.vertices[i]; _, j, d = kd.find(vc.co)
    if d is None or d > 1e-4: continue
    pesos = {CORPO.vertex_groups[g.group].name: g.weight for g in CORPO.data.vertices[j].groups}
    zera_e_poe(CAB, vc, pesos); copiados += 1
print("COSTURA vertices igualados", copiados, "de", len(bordas(CAB)))
# ossos sem nenhum vertice (somem na importacao do Roblox)
usados = {g.name for o in MALHAS for g in o.vertex_groups}
sem_v = [b.name for b in arm_d.bones if b.use_deform and b.name not in usados]
print("OSSOS sem vertice:", sem_v)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cervo_Rig.blend"))
json.dump({"ossos": [b.name for b in arm_d.bones], "sem_vertice": sem_v, "nariz": list(NARIZ), "nuca": list(NUCA)},
          open(os.path.join(OUT, "rig_relatorio.json"), "w"), indent=1)

# ------------------------------------------------------------------ poses de teste (so para conferir deformacao)
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
mundo = bpy.data.worlds.new("Fundo"); sc.world = mundo; mundo.use_nodes = True
bg = mundo.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (*lin("8a8580"), 1); bg.inputs["Strength"].default_value = 0.9
sd = bpy.data.lights.new("Sol", "SUN"); sd.energy = 2.0; sd.angle = math.radians(12)
so = bpy.data.objects.new("Sol", sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
def camera(nome, loc, alvo, lente):
    c = bpy.data.cameras.new(nome); o = bpy.data.objects.new(nome, c); sc.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); c.lens = lente; return o
CAM = camera("Cam_34", (-1.45, -1.75, 1.0), (0, -0.08, 0.9), 30)
CAM_L = camera("Cam_Lado", (-2.5, -0.08, 0.95), (0, -0.08, 0.9), 34)
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
sc.render.film_transparent = True; sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 900, 900, 100
try: sc.eevee.taa_render_samples = 32
except Exception: pass
PB = arm.pose.bones
for b in PB: b.rotation_mode = "XYZ"
def zera():
    for b in PB: b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0)
def rot(nome, gx=0, gy=0, gz=0):
    PB[nome].rotation_euler = (math.radians(gx), math.radians(gy), math.radians(gz))
POSES = {
    "repouso": [],
    "pastar": [("Pescoco", 55, 0, 0), ("Pescoco2", 30, 0, 0), ("Cabeca", 10, 0, 0), ("Coluna3", 5, 0, 0)],
    "olhar_lado": [("Pescoco", 0, 0, 25), ("Pescoco2", 0, 0, 25), ("Cabeca", 0, 0, 15), ("OrelhaE", 0, 0, -30), ("OrelhaD", 0, 0, 30)],
    "passada": [("BracoE", -25, 0, 0), ("AntebracoE", 60, 0, 0), ("CanelaE", -40, 0, 0), ("CoxaD", 20, 0, 0), ("PernaD", -35, 0, 0),
                ("CanelaTrasD", 45, 0, 0), ("BracoD", 15, 0, 0), ("CoxaE", -15, 0, 0), ("Cauda1", 30, 0, 0)],
    "alerta": [("Pescoco", -15, 0, 0), ("Cabeca", -10, 0, 0), ("OrelhaE", 30, 0, 0), ("OrelhaD", 30, 0, 0), ("Cauda1", -40, 0, 0)],
}
for nome, rots in POSES.items():
    zera()
    for r in rots: rot(*r)
    bpy.context.view_layer.update()
    for cam, suf in ((CAM, "34"), (CAM_L, "lado")):
        sc.camera = cam; sc.render.filepath = os.path.join(OUT, f"pose_{nome}_{suf}.png"); bpy.ops.render.render(write_still=True)
zera(); bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cervo_Rig.blend"))
print("RIG_OK")
