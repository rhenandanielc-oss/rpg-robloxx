"""Rig PILOTO de AVE da Coruja-da-Floresta sobre a malha de jogo low_v1 (Coruja_Cabeca + Coruja_Corpo, 9k tris, asas abertas).
31 ossos (nomes do jogo; o Roblox liga malha a osso pelo NOME). Sem mandibula (bico fechado da fauna).
  tronco: Raiz, Pelve, Coluna1, Coluna2, Pescoco, Pescoco2, Cabeca, TufoE/D (tufos)
  asa (E/D): OmbroAsa (escapula), BracoAsa (umero), AntebracoAsa (ulna, secundarias), MaoAsa (pulso/carpo), Primarias
  cauda: Cauda, CaudaLequeE/D (abre o leque)      pernas (E/D): Coxa, Tibia, Tarso, Dedos
Juntas medidas na malha (bordo de ataque da asa, pes, tufos, bico, cauda). Asas sao laminas finas (o heat/proxy voxel nao e
confiavel nelas): PESOS GEOMETRICOS -> asa pela posicao ao longo da envergadura (1D, faixas suaves nas juntas); tronco por
distancia aos ossos (gaussiana); cabeca rigida; tufos manuais; cauda pelo lado (leque); pernas por segmento. Max 4 influencias.
Poses de PROVA estaticas: repouso (T), asas fechadas (pousada), asas no alto e embaixo da batida, cabeca virada, cauda em leque.
Uso: blender -b low_v1/CR_Coruja_da_Floresta_LOW.blend -P rig/rig_coruja.py -- <saida_dir>
r3 (14/11, cabeca descolava ao virar): CORUJA_R3=1 ... -- rig/r3  (pivos do pescoco no eixo da cabeca + faixa de torcao)"""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.kdtree import KDTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def ativar(o):
    for x in sc.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
for im in bpy.data.images:
    if im.filepath and "low_voxel" in im.filepath: im.filepath = im.filepath.replace("low_voxel", "low_v1"); im.reload()
for o in list(sc.objects):
    if o.type in ("CAMERA", "LIGHT") or (o.type == "MESH" and o.name not in ("Coruja_Cabeca", "Coruja_Corpo")): bpy.data.objects.remove(o)
CAB, CORPO = bpy.data.objects["Coruja_Cabeca"], bpy.data.objects["Coruja_Corpo"]; MALHAS = [CAB, CORPO]
# ------------------------------------------------------------------ esqueleto (posicoes medidas na low_v1, 14/11)
ASA = [(0.06, -0.050, 0.420), (0.155, -0.065, 0.425), (0.30, -0.055, 0.460), (0.46, 0.000, 0.488), (0.56, 0.022, 0.512), (0.745, 0.100, 0.465)]
#        ombro (raiz escapula)   ombro (cabeca do umero)  cotovelo            pulso               base das primarias   ponta
OSSOS_ASA = ["OmbroAsa", "BracoAsa", "AntebracoAsa", "MaoAsa", "Primarias"]
arm_d = bpy.data.armatures.new("Coruja_Rig"); arm = bpy.data.objects.new("Coruja_Rig", arm_d); sc.collection.objects.link(arm)
ativar(arm); bpy.ops.object.mode_set(mode="EDIT"); E = arm_d.edit_bones
def osso(nome, a, b, pai=None, conecta=True):
    o = E.new(nome); o.head = V(a); o.tail = V(b)
    if pai: o.parent = E[pai]; o.use_connect = conecta and (E[pai].tail - V(a)).length < 1e-4
    return o
osso("Raiz", (0, -0.05, 0), (0, -0.17, 0))
osso("Pelve", (0, 0.06, 0.24), (0, 0.0, 0.32), "Raiz", False)
osso("Coluna1", E["Pelve"].tail, (0, -0.04, 0.39), "Pelve"); osso("Coluna2", E["Coluna1"].tail, (0, -0.07, 0.435), "Coluna1")
R3 = bool(os.environ.get("CORUJA_R3"))
if not R3:
    osso("Pescoco", E["Coluna2"].tail, (0, -0.09, 0.47), "Coluna2"); osso("Pescoco2", E["Pescoco"].tail, (0, -0.11, 0.50), "Pescoco")
    osso("Cabeca", E["Pescoco2"].tail, (0, -0.25, 0.49), "Pescoco2")
else:
    # r3 (14/11): o pescoco girava em eixos 4-8 cm ATRAS do centro da cabeca (y -0,147 medido) -> no OlharE a cabeca se deslocava
    # 10,4 cm e parecia descolar. Agora os pivos ficam no eixo vertical do pescoco/cabeca (medido por fatias: y -0,12 a -0,147).
    osso("Pescoco", (0, -0.125, 0.415), (0, -0.140, 0.455), "Coluna2", False); osso("Pescoco2", E["Pescoco"].tail, (0, -0.147, 0.495), "Pescoco")
    osso("Cabeca", E["Pescoco2"].tail, (0, -0.255, 0.49), "Pescoco2")
for l, sx in (("E", 1), ("D", -1)):
    osso("Tufo" + l, (sx * 0.095, -0.12, 0.565), (sx * 0.129, -0.12, 0.619), "Cabeca", False)
    pts = [V((sx * p[0], p[1], p[2])) for p in ASA]
    osso("OmbroAsa" + l, pts[0], pts[1], "Coluna2", False)
    for i, nm in enumerate(OSSOS_ASA[1:], 1): osso(nm + l, pts[i], pts[i + 1], OSSOS_ASA[i - 1] + l)
    osso("Coxa" + l, (sx * 0.060, 0.000, 0.26), (sx * 0.062, -0.030, 0.150), "Pelve", False)
    osso("Tibia" + l, E["Coxa" + l].tail, (sx * 0.064, -0.020, 0.090), "Coxa" + l)
    osso("Tarso" + l, E["Tibia" + l].tail, (sx * 0.064, -0.060, 0.022), "Tibia" + l)
    osso("Dedos" + l, E["Tarso" + l].tail, (sx * 0.064, -0.185, 0.012), "Tarso" + l)
osso("Cauda", (0, 0.06, 0.24), (0, 0.14, 0.15), "Pelve", False)
for l, sx in (("E", 1), ("D", -1)): osso("CaudaLeque" + l, (sx * 0.015, 0.12, 0.17), (sx * 0.055, 0.232, 0.03), "Cauda", False)
for b in E: b.roll = 0.0
bpy.ops.object.mode_set(mode="OBJECT"); arm_d.bones["Raiz"].use_deform = False
B = arm_d.bones; print("OSSOS", len(B))
# ------------------------------------------------------------------ pesos geometricos
def seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9))); return (p - (a + ab * t)).length, t
HL = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in B}
TRONCO = {"Pelve": 0.07, "Coluna1": 0.07, "Coluna2": 0.07, "Pescoco": 0.045, "Pescoco2": 0.045}
if os.environ.get("CORUJA_R3"): TRONCO = {"Pelve": 0.07, "Coluna1": 0.07, "Coluna2": 0.08}   # r3: pescoco so pela faixa propria
def pesos_tronco(p):
    w = {nm: math.exp(-(seg(p, *HL[nm])[0] / s) ** 2) for nm, s in TRONCO.items()}; return w
XA = [p[0] for p in ASA]                                         # juntas da asa ao longo de |x|
BANDAS = [0.03, 0.035, 0.03, 0.025]                               # meia-largura da dobra em cada junta (ombro, cotovelo, pulso, primarias)
def pesos_asa(ax, l):
    w = {}
    for i, nm in enumerate(OSSOS_ASA):
        ini = 1.0 if i == 0 else suave((ax - (XA[i] - BANDAS[i - 1])) / (2 * BANDAS[i - 1]))
        fim = 1.0 if i == len(OSSOS_ASA) - 1 else 1 - suave((ax - (XA[i + 1] - BANDAS[i])) / (2 * BANDAS[i]))
        if ini * fim > 1e-4: w[nm + l] = ini * fim
    return w
def pesos_perna(p, l):
    cad = ["Coxa" + l, "Tibia" + l, "Tarso" + l, "Dedos" + l]; best = min(cad, key=lambda nm: seg(p, *HL[nm])[0])
    d, t = seg(p, *HL[best]); w = {best: 1.0}; i = cad.index(best)
    if t < 0.25 and i > 0: f = 0.5 * (1 - t / 0.25); w = {best: 1 - f, cad[i - 1]: f}     # dobra suave perto da junta de cima
    elif t > 0.75 and i < 3: f = 0.5 * (t - 0.75) / 0.25; w = {best: 1 - f, cad[i + 1]: f}
    return w
def pesos_pescoco_r3(p):
    """r3 (v8, escolhida por captura 14/11): a CABECA inteira e rigida acima de z 0,445 (rosto, bico, olhos e a lateral do rosto),
    e a torcao fica numa faixa curta (z 0,40-0,455) logo abaixo da borda do disco facial: Coluna2 -> Pescoco -> Pescoco2 -> Cabeca.
    Testadas e descartadas: faixa de 14 cm (z 0,40-0,54) e faixas altas -> um 'cachecol' de penas torcidas cobria o rosto,
    mesmo com o giro reduzido para 100-120 graus (a lateral do rosto ficava dentro da faixa)."""
    z0, z1 = [float(x) for x in os.environ.get("CORUJA_R3_BANDA", "0.40,0.455").split(",")]
    h = max(0.0, min(1.0, (p.z - z0) / (z1 - z0))); w = {}
    for (a0, a1, n0, n1) in ((0.0, 0.30, "Coluna2", "Pescoco"), (0.30, 0.65, "Pescoco", "Pescoco2"), (0.65, 1.0, "Pescoco2", "Cabeca")):
        if a0 <= h <= a1: f = suave((h - a0) / (a1 - a0)); w = {n0: 1 - f, n1: f}; break
    yr = float(os.environ.get("CORUJA_R3_ROSTO_Y", "-0.13"))
    rosto = suave((yr - p.y) / 0.035) * suave((p.z - 0.415) / 0.03)
    zr = float(os.environ.get("CORUJA_R3_CABECA_Z", "0.445"))           # acima disto a cabeca toda e rigida (inclui a lateral do rosto)
    rosto = max(rosto, suave((p.z - zr) / 0.02))
    if rosto > 0: w = {k: v * (1 - rosto) for k, v in w.items()}; w["Cabeca"] = w.get("Cabeca", 0) + rosto
    return w
def pesos(p, malha_cab):
    ax = abs(p.x); l = "E" if p.x > 0 else "D"
    if R3 and (malha_cab or (p.z > 0.40 and ax < 0.13 and p.y < 0.0)):
        if ax > 0.085 and p.z > 0.55: f = suave((p.z - 0.555) / 0.04); return {"Tufo" + l: f, "Cabeca": 1 - f}
        return pesos_pescoco_r3(p)
    # cabeca: rigida (rosto, bico, olhos); tufos; garganta mistura com o pescoco
    if malha_cab or (p.z > 0.47 and p.y < -0.02 and ax < 0.15):
        if ax > 0.085 and p.z > 0.55: f = suave((p.z - 0.555) / 0.04); return {"Tufo" + l: f, "Cabeca": 1 - f}
        g = suave((p.z - 0.43) / 0.06)                             # base da cabeca / garganta
        if g < 1: w = pesos_tronco(p); s = sum(w.values()) or 1; w = {k: v / s * (1 - g) for k, v in w.items()}; w["Cabeca"] = g; return w
        return {"Cabeca": 1.0}
    # asa: fora do corpo
    if ax > 0.09 and p.z > 0.19 and p.y < 0.17:
        f = suave((ax - 0.10) / 0.07)
        wa = pesos_asa(ax, l)
        if f >= 1: return wa
        wt = pesos_tronco(p); s = sum(wt.values()) or 1
        w = {k: v / s * (1 - f) for k, v in wt.items()}
        for k, v in wa.items(): w[k] = w.get(k, 0) + v * f
        return w
    # cauda (atras e abaixo da pelve)
    if p.y > 0.09 and p.z < 0.26 and (ax < 0.11 or (p.y > 0.12 and ax < 0.17)):   # (r2: laterais da cauda sao mais largas)
        lado = suave((ax - 0.01) / 0.04); prof = suave((p.y - 0.11) / 0.06)
        w = {"Cauda": 1 - lado * prof, "CaudaLeque" + l: lado * prof}
        base = 1 - suave((p.y - 0.07) / 0.05)                      # junto da pelve
        if base > 0: w = {k: v * (1 - base) for k, v in w.items()}; w["Pelve"] = base
        return w
    # pernas e pes
    if p.z < 0.17 and ax < 0.14:
        if p.z < 0.035: return {"Dedos" + l: 1.0}                    # (r2: ponto do pe no chao com peso do Tarso afundava ao flexionar)
        w = pesos_perna(p, l); cima = suave((p.z - 0.13) / 0.04)
        if cima > 0: w = {k: v * (1 - cima) for k, v in w.items()}; w["Pelve"] = w.get("Pelve", 0) + cima
        return w
    return pesos_tronco(p)
for o in MALHAS:
    for g in list(o.vertex_groups): o.vertex_groups.remove(g)
    for b in B:
        if b.use_deform: o.vertex_groups.new(name=b.name)
    for v in o.data.vertices:
        w = pesos(v.co, o is CAB); w = dict(sorted(w.items(), key=lambda e: -e[1])[:4]); s = sum(w.values()) or 1.0
        for nm, x in w.items():
            if x / s > 1e-4: o.vertex_groups[nm].add([v.index], x / s, "REPLACE")
    ativar(o)
    for g in o.vertex_groups: g.lock_weight = g.name == "Cabeca"
    bpy.ops.object.mode_set(mode="WEIGHT_PAINT"); bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=0.4, repeat=2); bpy.ops.object.mode_set(mode="OBJECT")
    for g in o.vertex_groups: g.lock_weight = False
    bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4); bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
# costura cabeca/corpo: mesmos pesos
def bordas(o):
    bm_ = bmesh.new(); bm_.from_mesh(o.data); idx = [v.index for v in bm_.verts if v.is_boundary]; bm_.free(); return idx
bc = bordas(CORPO); kd = KDTree(len(bc))
for i in bc: kd.insert(CORPO.data.vertices[i].co, i)
kd.balance(); cop = 0
for i in bordas(CAB):
    vc = CAB.data.vertices[i]; _, j, d = kd.find(vc.co)
    if d is None or d > 1e-4: continue
    for g in list(vc.groups): CAB.vertex_groups[g.group].remove([vc.index])
    for g in CORPO.data.vertices[j].groups: CAB.vertex_groups[CORPO.vertex_groups[g.group].name].add([vc.index], g.weight, "REPLACE")
    cop += 1
REL = {"ossos": [b.name for b in B], "deformam": sum(1 for b in B if b.use_deform), "costura": [cop, len(bordas(CAB))], "malhas": {}}
for o in MALHAS:
    for g in list(o.vertex_groups):
        if not any(gg.group == g.index for v in o.data.vertices for gg in v.groups): o.vertex_groups.remove(g)
    ativar(o); arm.select_set(True); bpy.context.view_layer.objects.active = arm; bpy.ops.object.parent_set(type="ARMATURE_NAME")
    REL["malhas"][o.name] = {"tris": sum(len(p.vertices) - 2 for p in o.data.polygons), "grupos": len(o.vertex_groups),
                             "max_influencias": max(len([g for g in v.groups if g.weight > 1e-4]) for v in o.data.vertices),
                             "sem_peso": sum(1 for v in o.data.vertices if not v.groups)}
usados = {g.name for o in MALHAS for g in o.vertex_groups}; REL["sem_vertice"] = [b.name for b in B if b.use_deform and b.name not in usados]
print("REL", json.dumps(REL))
# ------------------------------------------------------------------ poses de PROVA
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
mundo = bpy.data.worlds.new("Fundo"); sc.world = mundo; mundo.use_nodes = True
bg = mundo.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (*lin("8a8580"), 1); bg.inputs["Strength"].default_value = 0.9
sd = bpy.data.lights.new("Sol", "SUN"); sd.energy = 2.0; sd.angle = math.radians(12)
so = bpy.data.objects.new("Sol", sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0)); CHAO = bpy.context.object
mc = bpy.data.materials.new("M_Chao"); mc.use_nodes = True; nt = mc.node_tree; ck = nt.nodes.new("ShaderNodeTexChecker")
ck.inputs["Scale"].default_value = 20; ck.inputs["Color1"].default_value = (*lin("b9b2aa"), 1); ck.inputs["Color2"].default_value = (*lin("948c84"), 1)
nt.links.new(ck.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"]); CHAO.data.materials.append(mc)
def camera(nome, loc, alvo, lente):
    c = bpy.data.cameras.new(nome); o = bpy.data.objects.new(nome, c); sc.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); c.lens = lente; return o
CAMS = {"frente": camera("Cam_F", (0, -2.6, 0.55), (0, 0, 0.45), 38), "34": camera("Cam_34", (-1.5, -1.6, 1.0), (0, 0, 0.34), 38),
        "lado": camera("Cam_L", (-2.3, 0, 0.40), (0, 0, 0.32), 40), "cima": camera("Cam_C", (0.0, 0.9, 2.3), (0, 0, 0.30), 38)}
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 900, 640, 100
try: sc.eevee.taa_render_samples = 32
except Exception: pass
PB = arm.pose.bones
for b in PB: b.rotation_mode = "QUATERNION"
def rot_mundo(nome, eixos):
    r = B[nome].matrix_local.to_3x3(); q = Matrix.Identity(3)
    for eixo, ang in eixos: q = Matrix.Rotation(math.radians(ang), 3, eixo) @ q
    return (r.inverted() @ q @ r).to_quaternion()
X_, Y_, Z_ = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
def asa(l, braco, ante, mao, prim, ombro=()):
    """rotacoes da asa E; a D espelha (Y e Z trocam de sinal)"""
    s = 1 if l == "E" else -1; m = lambda e: [(ax, ang * (s if ax != X_ else 1)) for ax, ang in e]
    return [("OmbroAsa" + l, m(ombro)), ("BracoAsa" + l, m(braco)), ("AntebracoAsa" + l, m(ante)), ("MaoAsa" + l, m(mao)), ("Primarias" + l, m(prim))]
DOBRA = dict(ombro=[(Z_, 10)], braco=[(Z_, 75), (Y_, 60)], ante=[(Z_, -155)], mao=[(Z_, 150)], prim=[(Z_, -8)])
ALTO = dict(ombro=[(Y_, -20)], braco=[(Y_, -45), (Z_, 10)], ante=[(Y_, -10)], mao=[(Y_, 5)], prim=[])
BAIXO = dict(ombro=[(Y_, 10)], braco=[(Y_, 45), (Z_, -5)], ante=[(Y_, 15)], mao=[(Y_, 10)], prim=[(Y_, 5)])
def pose_asas(d): return asa("E", **d) + asa("D", **d)
# asa FECHADA: resolvida por alvos em rig/dobra_asas.py (rotacoes locais gravadas em rig/dobra_asas.json; refazer se os pesos mudarem)
_J = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dobra_asas.json")
FECHADA = [("__quat__", nm, q) for nm, q in json.load(open(_J))["ossos"].items()] if os.path.exists(_J) else pose_asas(DOBRA)
NO_AR = [("__raiz__", (0, 0, 0.30))]                                # poses de voo: corpo no ar (nao e prova de contato com o chao)
POSES = {"repouso_T": [],
         "asas_fechadas": FECHADA,
         "batida_alto": NO_AR + pose_asas(ALTO),
         "batida_baixo": NO_AR + pose_asas(BAIXO),
         "cabeca_virada": FECHADA + [("Pescoco", [(Z_, 40)]), ("Pescoco2", [(Z_, 45)]), ("Cabeca", [(Z_, 35)])],
         "cauda_leque": FECHADA + [("CaudaLequeE", [(Y_, -25)]), ("CaudaLequeD", [(Y_, 25)]), ("Cauda", [(X_, 18)])]}
def aplica(lista):
    for b in PB: b.rotation_quaternion = (1, 0, 0, 0); b.location = (0, 0, 0)
    for item in lista:
        if item[0] == "__quat__": PB[item[1]].rotation_quaternion = item[2]
        elif item[0] == "__raiz__": PB["Raiz"].location = B["Raiz"].matrix_local.to_3x3().inverted() @ V(item[1])
        else: PB[item[0]].rotation_quaternion = rot_mundo(item[0], item[1])
    bpy.context.view_layer.update()
def min_z():
    dg = bpy.context.evaluated_depsgraph_get(); m_ = 9
    for o in MALHAS:
        ev = o.evaluated_get(dg); me_ = ev.to_mesh(); m_ = min(m_, min(v.co.z for v in me_.vertices)); ev.to_mesh_clear()
    return m_
MET = {}
for nome, lista in POSES.items():
    aplica(lista); MET[nome] = round(min_z() * 100, 2)
    for suf, cam in CAMS.items():
        sc.camera = cam; sc.render.filepath = os.path.join(OUT, f"prova_{nome}_{suf}.png"); bpy.ops.render.render(write_still=True)
REL["provas_min_z_cm"] = MET; print("PROVAS", MET)
aplica([]); bpy.data.objects.remove(CHAO)
json.dump(REL, open(os.path.join(OUT, "rig_relatorio.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Coruja_Rig.blend")); print("RIG_OK")
