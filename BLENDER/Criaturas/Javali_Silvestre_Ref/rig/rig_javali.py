"""Rig PILOTO do Javali Silvestre (fauna de recurso) sobre a malha de jogo low_v1 (Javali_Cabeca + Javali_Corpo, ~9,7k tris).
Estrutura e nomes iguais aos do rig do Cervo-do-Bosque (Cervo_do_Bosque_Ref/rig/rig_cervo.py + rig_pernas_r2.py), para o
gerador de clipes poder ser adaptado; poses NAO sao reaproveitadas. Os nomes sao os do jogo (o Roblox liga malha a osso pelo NOME).
Sem Mandibula (boca fechada da fauna); presas rigidas na Cabeca. Pescoco curto (2 ossos curtos, como no cervo, mas ~1/3 do tamanho).
Juntas: cascos medidos (pontos mais baixos por quadrante; o Meshy deixou a traseira D ~6 cm a frente da E -> cada pata usa o
proprio casco); alturas das juntas pela anatomia de suino (perna curta: carpo ~0,15, cotovelo ~0,27, jarrete ~0,20, soldra ~0,36).
Pesos: heat num PROXY voxel das duas malhas -> Data Transfer; cabeca rigida (cranio, focinho, presas); orelhas manuais;
pernas por SEGMENTO (licao do cervo r2: heat espalhado = perna em arco); garganta em transicao gradual (licao do cervo).
Maximo 4 influencias. Gera poses de PROVA estaticas (apoio, passada, giro, focinho baixo, reacao) com chao quadriculado.
Uso: blender -b low_v1/CR_Javali_Silvestre_LOW.blend -P rig/rig_javali.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector as V
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def ativar(o):
    for x in sc.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
for o in list(sc.objects):
    if o.type in ("CAMERA", "LIGHT") or (o.type == "MESH" and o.name not in ("Javali_Cabeca", "Javali_Corpo")):
        bpy.data.objects.remove(o)
CAB, CORPO = bpy.data.objects["Javali_Cabeca"], bpy.data.objects["Javali_Corpo"]
MALHAS = [CAB, CORPO]
def coords(o):
    a = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", a); return a.reshape(-1, 3)
co = np.vstack([coords(o) for o in MALHAS]); x, y, z = co[:, 0], co[:, 1], co[:, 2]
NARIZ_Y, Y1 = float(y.min()), float(y.max())
# ------------------------------------------------------------------ cascos (por quadrante)
cb = coords(CORPO); baixo = cb[cb[:, 2] < 0.03]
PATAS = {}
for lado, sx in (("E", 1), ("D", -1)):
    for par, sy in (("dian", -1), ("tras", 1)):
        s_ = baixo[(np.sign(baixo[:, 0]) == sx) & (np.sign(baixo[:, 1]) == sy)]
        c = s_[:, :2].mean(0); PATAS[(lado, par)] = {"casco": c, "frente_y": float(s_[:, 1].min()), "sx": sx}
        print("CASCO", lado, par, c.round(3), "frente", round(float(s_[:, 1].min()), 3))
# ------------------------------------------------------------------ cabeca: focinho, nuca, orelhas
def perfil(yy, f=0.012, xm=0.03):
    s = (np.abs(y - yy) < f) & (np.abs(x) < xm); return (float(z[s].min()), float(z[s].max()))
pn = perfil(NARIZ_Y + 0.015); NARIZ = V((0, NARIZ_Y + 0.01, (pn[0] + pn[1]) / 2))
NUCA = V((0, NARIZ_Y + 0.36, 0.52))                    # atlas: atras das orelhas, no meio da altura do cranio (sem a crista)
cc = coords(CAB)
def e_orelha(p):                                        # orelhas pequenas e eretas, laterais, atras dos olhos
    return abs(p[0]) > 0.095 and p[2] > 0.60 and NARIZ_Y + 0.22 < p[1] < NARIZ_Y + 0.38
ORE = {}
for sx, lado in ((1, "E"), (-1, "D")):
    sub = np.array([q for q in co if np.sign(q[0]) == sx and e_orelha(q)])
    tip = sub[np.argmax(np.abs(sub[:, 0]) + sub[:, 2])]
    base = V((sx * 0.085, float(sub[:, 1].mean()), 0.62))
    ORE[lado] = (base, V(tuple(tip)))
    print("ORELHA", lado, len(sub), "base", tuple(round(c, 3) for c in base), "ponta", tuple(round(float(c), 3) for c in tip))
# ------------------------------------------------------------------ proxy voxel fechado (heat)
prox = CORPO.copy(); prox.data = CORPO.data.copy(); prox.name = "tmp_Proxy"; sc.collection.objects.link(prox)
c2 = CAB.copy(); c2.data = CAB.data.copy(); sc.collection.objects.link(c2)
ativar(prox); c2.select_set(True); bpy.ops.object.join()
for g in list(prox.vertex_groups): prox.vertex_groups.remove(g)
r_ = prox.modifiers.new("R", "REMESH"); r_.mode = "VOXEL"; r_.voxel_size = float(os.environ.get("JAVALI_VOX", "0.012")); bpy.ops.object.modifier_apply(modifier=r_.name)
s_ = prox.modifiers.new("S", "SMOOTH"); s_.factor = 0.5; s_.iterations = 2; bpy.ops.object.modifier_apply(modifier=s_.name)
_bm = bmesh.new(); _bm.from_mesh(prox.data); _ilhas = 0; _vist = set()
for _v in _bm.verts:
    if _v.index in _vist: continue
    _ilhas += 1; _pilha = [_v]
    while _pilha:
        _a = _pilha.pop()
        if _a.index in _vist: continue
        _vist.add(_a.index); _pilha.extend(e.other_vert(_a) for e in _a.link_edges)
print("PROXY ilhas", _ilhas, "verts", len(_bm.verts)); _bm.free()
BVP = BVHTree.FromObject(prox, bpy.context.evaluated_depsgraph_get())
def dentro_p(p):
    n_ = 0; o_ = V(p)
    for _ in range(60):
        h = BVP.ray_cast(o_, V((0.0013, 0.0007, 1)).normalized(), 5.0)
        if h[0] is None: break
        n_ += 1; o_ = h[0] + V((0, 0, 1e-5))
    return n_ % 2 == 1
# ------------------------------------------------------------------ esqueleto
arm_d = bpy.data.armatures.new("Javali_Rig"); arm = bpy.data.objects.new("Javali_Rig", arm_d); sc.collection.objects.link(arm)
ativar(arm); bpy.ops.object.mode_set(mode="EDIT"); E = arm_d.edit_bones
def osso(nome, a, b, pai=None, conecta=True):
    o = E.new(nome); o.head = V(a); o.tail = V(b)
    if pai: o.parent = E[pai]; o.use_connect = conecta and (E[pai].tail - V(a)).length < 1e-4
    return o
yo = float(np.mean([PATAS[(l, "dian")]["casco"][1] for l in "ED"])); yq = float(np.mean([PATAS[(l, "tras")]["casco"][1] for l in "ED"]))
osso("Raiz", (0, (yq + yo) / 2, 0), (0, (yq + yo) / 2 - 0.12, 0))
# espinha a ~60% entre a barriga e o dorso (o dorso sem crista fica ~0,75; a crista e cerda, nao conta)
osso("Pelve", (0, 0.50, 0.54), (0, 0.33, 0.55), "Raiz", False)
osso("Coluna1", E["Pelve"].tail, (0, 0.13, 0.56), "Pelve")
osso("Coluna2", E["Coluna1"].tail, (0, -0.06, 0.57), "Coluna1")
osso("Coluna3", E["Coluna2"].tail, (0, -0.20, 0.56), "Coluna2")                     # cernelha (ombro alto)
osso("Pescoco", E["Coluna3"].tail, (0, NARIZ_Y + 0.44, 0.545), "Coluna3")
osso("Pescoco2", E["Pescoco"].tail, NUCA, "Pescoco")
osso("Cabeca", NUCA, NARIZ, "Pescoco2")
for lado in "ED":
    b, t = ORE[lado]; osso("Orelha" + lado, b, t, "Cabeca", False)
# cauda: medida (sai da garupa em y~0,53 z~0,52 e pende ate y~0,73 z~0,30)
osso("Cauda1", (0, 0.53, 0.515), (0, 0.63, 0.455), "Pelve", False)
osso("Cauda2", E["Cauda1"].tail, (0, Y1 - 0.01, 0.31), "Cauda1")
for lado in "ED":
    p = PATAS[(lado, "dian")]; c = p["casco"]; sx = p["sx"]
    fet = V((c[0], c[1] + 0.012, 0.06)); car = V((c[0] * 1.02, c[1] + 0.03, 0.145)); cot = V((c[0] * 1.05, c[1] + 0.07, 0.27))
    omb = V((sx * 0.125, c[1] - 0.01, 0.42)); esc = V((sx * 0.07, c[1] + 0.15, 0.62)); toe = V((c[0], p["frente_y"] + 0.008, 0.01))
    osso("Escapula" + lado, esc, omb, "Coluna3", False); osso("Braco" + lado, omb, cot, "Escapula" + lado)
    osso("Antebraco" + lado, cot, car, "Braco" + lado); osso("Canela" + lado, car, fet, "Antebraco" + lado)
    osso("Quartela" + lado, fet, toe, "Canela" + lado)
    p = PATAS[(lado, "tras")]; c = p["casco"]; sx = p["sx"]
    fet = V((c[0], c[1] + 0.03, 0.06)); jar = V((c[0], c[1] + 0.065, 0.20)); joe = V((c[0] * 1.08, c[1] - 0.07, 0.36))
    qua = V((sx * 0.10, 0.43, 0.56)); toe = V((c[0], p["frente_y"] + 0.008, 0.01))
    osso("Coxa" + lado, qua, joe, "Pelve", False); osso("Perna" + lado, joe, jar, "Coxa" + lado)
    osso("CanelaTras" + lado, jar, fet, "Perna" + lado); osso("QuartelaTras" + lado, fet, toe, "CanelaTras" + lado)
FORA = []
for b in E:
    if b.name in ("Raiz", "OrelhaE", "OrelhaD"): continue
    for ponta in ("head", "tail"):
        pp = getattr(b, ponta)
        if not ((ponta == "head" and b.use_connect) or dentro_p(pp)):
            FORA.append((b.name, ponta, round(BVP.find_nearest(pp)[3], 3)))
print("OSSOS com ponta fora do proxy", FORA)
for b in E: b.roll = 0.0
bpy.ops.object.mode_set(mode="OBJECT")
arm_d.bones["Raiz"].use_deform = False
print("OSSOS", len(arm_d.bones))
# ------------------------------------------------------------------ pesos: heat no proxy -> transferencia
SEM_HEAT = ("OrelhaE", "OrelhaD") + tuple(n_ for n_ in os.environ.get("JAVALI_SEM_HEAT", "").split(",") if n_)
for nm in SEM_HEAT: arm_d.bones[nm].use_deform = False
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
for nm in SEM_HEAT: arm_d.bones[nm].use_deform = True
def grupo(o, nm): return o.vertex_groups.get(nm) or o.vertex_groups.new(name=nm)
def zera_e_poe(o, v, pesos):
    for g in list(v.groups): o.vertex_groups[g.group].remove([v.index])
    for nm, w in pesos.items():
        if w > 1e-4: grupo(o, nm).add([v.index], w, "REPLACE")
def mistura(o, v, nm, f):
    for g in list(v.groups):
        if o.vertex_groups[g.group].name != nm: o.vertex_groups[g.group].add([v.index], g.weight * (1 - f), "REPLACE")
    atual = next((g.weight for g in v.groups if o.vertex_groups[g.group].name == nm), 0.0)
    grupo(o, nm).add([v.index], atual + f, "REPLACE")
Y_CAB_DURA = NARIZ_Y + 0.27            # a frente disso: cabeca rigida (focinho, presas, olhos)
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
    FIXOS = {}; n_cab = n_ore = 0
    for v in me.vertices:
        p = v.co
        if e_orelha(p):
            lado = "E" if p.x > 0 else "D"; f = suave((abs(p.x) - 0.095) / 0.035) * suave((p.z - 0.60) / 0.04)
            FIXOS[v.index] = {"Orelha" + lado: f, "Cabeca": 1 - f}; zera_e_poe(o, v, FIXOS[v.index]); n_ore += 1
        elif p.y < Y_CAB_DURA:
            FIXOS[v.index] = {"Cabeca": 1.0}; zera_e_poe(o, v, FIXOS[v.index]); n_cab += 1
        elif p.y < Y_CAB_DURA + 0.08 and p.z > 0.45:
            mistura(o, v, "Cabeca", suave((Y_CAB_DURA + 0.08 - p.y) / 0.08)); n_cab += 1
    print("PESOS", o.name, "cabeca rigida", n_cab, "orelhas", n_ore)
    ativar(o)
    for g in o.vertex_groups: g.lock_weight = g.name in ("Cabeca",)
    bpy.ops.object.mode_set(mode="WEIGHT_PAINT"); bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=0.5, repeat=2); bpy.ops.object.mode_set(mode="OBJECT")
    for g in o.vertex_groups: g.lock_weight = False
    bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
    for i, pesos in FIXOS.items(): zera_e_poe(o, me.vertices[i], pesos)
# ---- pernas por segmento (cervo r2): abaixo do cotovelo / da soldra cada vertice pertence ao segmento onde se projeta
B = arm_d.bones; BANDA, RAIO = 0.016, 0.07
CADEIAS = {"E_d": ("AntebracoE", "CanelaE", "QuartelaE"), "D_d": ("AntebracoD", "CanelaD", "QuartelaD"),
           "E_t": ("PernaE", "CanelaTrasE", "QuartelaTrasE"), "D_t": ("PernaD", "CanelaTrasD", "QuartelaTrasD")}
O = CORPO; me = O.data; GN = {g.index: g.name for g in O.vertex_groups}; mud = {}
for nome, ossos in CADEIAS.items():
    pts = [B[ossos[0]].head_local.copy()] + [B[o_].tail_local.copy() for o_ in ossos]
    L_ = [(pts[i + 1] - pts[i]).length for i in range(3)]; S = [0, L_[0], L_[0] + L_[1], sum(L_)]
    sx = 1 if pts[0].x > 0 else -1; z_topo = pts[0].z - (0.02 if nome.endswith("_d") else 0.05); n = 0
    for v in me.vertices:
        p = v.co
        if p.z > z_topo or (p.x * sx) < 0.02: continue
        best = None
        for i in range(3):
            a, b = pts[i], pts[i + 1]; ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)); d = (p - (a + ab * t)).length
            if best is None or d < best[0]: best = (d, i, t)
        d, i, t = best
        if d > RAIO: continue
        s = S[i] + t * L_[i]; w = []
        for k in range(3):
            ini = 1.0 if k == 0 else suave((s - (S[k] - BANDA)) / (2 * BANDA)); fim = 1.0 if k == 2 else 1 - suave((s - (S[k + 1] - BANDA)) / (2 * BANDA))
            w.append(ini * fim)
        tot = sum(w) or 1.0; w = [q / tot for q in w]; mix = suave((z_topo - p.z) / 0.05)
        antigos = {GN[g.group]: g.weight for g in v.groups}
        for g in list(v.groups): O.vertex_groups[g.group].remove([v.index])
        novos = {nm: (1 - mix) * antigos.get(nm, 0.0) for nm in antigos}
        for k, nm in enumerate(ossos): novos[nm] = novos.get(nm, 0.0) + mix * w[k]
        tot = sum(novos.values()) or 1.0
        for nm, q in sorted(novos.items(), key=lambda e: -e[1])[:4]:
            if q / tot > 1e-4: grupo(O, nm).add([v.index], q / tot, "REPLACE")
        n += 1
    mud[nome] = n
print("PERNAS por segmento", mud)
# ---- garganta: transicao gradual Cabeca -> Pescoco2 -> Pescoco abaixo da linha da nuca (nas duas malhas)
Y0, Yf = NARIZ_Y + 0.22, NARIZ_Y + 0.46; gar = {}
for o_ in MALHAS:
    GN_ = {g.index: g.name for g in o_.vertex_groups}; n_ = 0
    for v in o_.data.vertices:
        p = v.co
        if not (Y0 < p.y < Yf and p.z < 0.50 and abs(p.x) < 0.17) or e_orelha(p): continue
        gz = suave((0.50 - p.z) / 0.12); dom = {GN_[g.group]: g.weight for g in v.groups}
        if sum(w for nm, w in dom.items() if nm in ("Cabeca", "Pescoco", "Pescoco2")) < 0.6: continue
        f = suave((p.y - Y0) / (Yf - Y0)); alvo_ = {"Cabeca": (1 - f) ** 2, "Pescoco2": 2 * f * (1 - f), "Pescoco": f * f}
        novos = {nm: (1 - gz) * w for nm, w in dom.items()}
        for nm, w in alvo_.items(): novos[nm] = novos.get(nm, 0.0) + gz * w
        tot = sum(novos.values()) or 1.0
        for g in list(v.groups): o_.vertex_groups[g.group].remove([v.index])
        for nm, w in sorted(novos.items(), key=lambda e: -e[1])[:4]:
            if w / tot > 1e-4: grupo(o_, nm).add([v.index], w / tot, "REPLACE")
        n_ += 1
    gar[o_.name] = n_
print("GARGANTA", gar)
# ---- costura cabeca/corpo com os mesmos pesos
def bordas(o):
    bm_ = bmesh.new(); bm_.from_mesh(o.data); idx = [v.index for v in bm_.verts if v.is_boundary]; bm_.free(); return idx
bc = bordas(CORPO); kd = KDTree(len(bc))
for i in bc: kd.insert(CORPO.data.vertices[i].co, i)
kd.balance(); cop = 0
for i in bordas(CAB):
    vc = CAB.data.vertices[i]; _, j, d = kd.find(vc.co)
    if d is None or d > 1e-4: continue
    zera_e_poe(CAB, vc, {CORPO.vertex_groups[g.group].name: g.weight for g in CORPO.data.vertices[j].groups}); cop += 1
print("COSTURA", cop, "de", len(bordas(CAB)))
REL = {"ossos": [b.name for b in B], "deformam": sum(1 for b in B if b.use_deform), "fora_do_proxy": FORA, "malhas": {}}
for o in MALHAS:
    for g in list(o.vertex_groups):
        if not any(gg.group == g.index for v in o.data.vertices for gg in v.groups): o.vertex_groups.remove(g)
    ativar(o); arm.select_set(True); bpy.context.view_layer.objects.active = arm; bpy.ops.object.parent_set(type="ARMATURE_NAME")
    REL["malhas"][o.name] = {"tris": sum(len(p.vertices) - 2 for p in o.data.polygons), "grupos": len(o.vertex_groups),
                             "max_influencias": max(len([g for g in v.groups if g.weight > 1e-4]) for v in o.data.vertices),
                             "sem_peso": sum(1 for v in o.data.vertices if not v.groups), "materiais": [m.name for m in o.data.materials]}
usados = {g.name for o in MALHAS for g in o.vertex_groups}
REL["sem_vertice"] = [b.name for b in B if b.use_deform and b.name not in usados]
print("REL", json.dumps(REL))
# ------------------------------------------------------------------ poses de PROVA (estaticas)
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
mundo = bpy.data.worlds.new("Fundo"); sc.world = mundo; mundo.use_nodes = True
bg = mundo.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (*lin("8a8580"), 1); bg.inputs["Strength"].default_value = 0.9
sd = bpy.data.lights.new("Sol", "SUN"); sd.energy = 2.0; sd.angle = math.radians(12)
so = bpy.data.objects.new("Sol", sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
# chao quadriculado (10 cm), so para as provas
bpy.ops.mesh.primitive_plane_add(size=3.2, location=(0, 0, 0)); CHAO = bpy.context.object; CHAO.name = "tmp_Chao"
mc = bpy.data.materials.new("M_Chao"); mc.use_nodes = True; nt = mc.node_tree; ck = nt.nodes.new("ShaderNodeTexChecker")
ck.inputs["Scale"].default_value = 32; ck.inputs["Color1"].default_value = (*lin("b9b2aa"), 1); ck.inputs["Color2"].default_value = (*lin("948c84"), 1)
nt.links.new(ck.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"]); CHAO.data.materials.append(mc)
def camera(nome, loc, alvo, lente):
    c = bpy.data.cameras.new(nome); o = bpy.data.objects.new(nome, c); sc.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); c.lens = lente; return o
CAMS = {"34": camera("Cam_34", (-1.05, -1.3, 0.62), (0, -0.03, 0.34), 34), "lado": camera("Cam_Lado", (-2.1, 0.0, 0.34), (0, 0.0, 0.34), 40),
        "frente": camera("Cam_Frente", (0.0, -2.1, 0.36), (0, 0, 0.32), 40)}
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
sc.render.film_transparent = False; sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGB"
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 900, 640, 100
try: sc.eevee.taa_render_samples = 32
except Exception: pass
PB = arm.pose.bones
for b in PB: b.rotation_mode = "XYZ"
def zera():
    for b in PB: b.rotation_euler = (0, 0, 0); b.location = (0, 0, 0)
def aplica(rots):
    zera()
    for nome, gx, gy, gz in rots: PB[nome].rotation_euler = (math.radians(gx), math.radians(gy), math.radians(gz))
    bpy.context.view_layer.update()
def malha_min_z(filtro=None):
    dg = bpy.context.evaluated_depsgraph_get(); mz = 9.0; pz = 9.0
    for o in MALHAS:
        ev = o.evaluated_get(dg); m_ = ev.to_mesh()
        for v in m_.vertices:
            w_ = o.matrix_world @ v.co; mz = min(mz, w_.z)
        ev.to_mesh_clear()
    return mz
def cabeca_min_z():
    dg = bpy.context.evaluated_depsgraph_get(); ev = CAB.evaluated_get(dg); m_ = ev.to_mesh()
    r = min((CAB.matrix_world @ v.co).z for v in m_.vertices); ev.to_mesh_clear(); return r
POSES = {
    "apoio": [],
    # passada (+X gira a ponta do osso para tras): dianteira E em balanco (carpo dobrado), traseira E em balanco (jarrete dobrado),
    # dianteira D e traseira D empurrando para tras
    "passada": [("BracoE", -18, 0, 0), ("AntebracoE", -8, 0, 0), ("CanelaE", 70, 0, 0), ("QuartelaE", 25, 0, 0), ("BracoD", 12, 0, 0),
                ("CoxaE", -15, 0, 0), ("PernaE", 30, 0, 0), ("CanelaTrasE", -10, 0, 0), ("QuartelaTrasE", 20, 0, 0), ("CoxaD", 14, 0, 0), ("QuartelaTrasD", -10, 0, 0)],
    "giro": [("Coluna1", 0, 0, 7), ("Coluna2", 0, 0, 8), ("Coluna3", 0, 0, 8), ("Pescoco", 0, 0, 12), ("Pescoco2", 0, 0, 10),
             ("Cabeca", 0, 0, 8), ("OrelhaE", 0, 0, -15), ("Cauda1", 0, 0, -15)],
    "reacao": [("Coluna2", -5, 0, 0), ("Coluna3", -3, 0, 0), ("Pescoco", -8, 0, 4), ("Pescoco2", -5, 0, 0), ("Cabeca", -4, 0, 6),
               ("OrelhaE", -35, 0, 0), ("OrelhaD", -35, 0, 0), ("Cauda1", -25, 0, 0)],
}
# focinho baixo: busca o angulo do pescoco que leva o ponto mais baixo da cabeca a ~2 cm do chao (sem dobrar o tronco)
alvo_z = 0.02; lo, hi = 0.0, 90.0
for _ in range(14):
    m_ = (lo + hi) / 2; aplica([("Pescoco", m_, 0, 0), ("Pescoco2", m_ * 0.5, 0, 0), ("Cabeca", m_ * 0.25, 0, 0)])
    if cabeca_min_z() > alvo_z: lo = m_
    else: hi = m_
ANG = round(lo, 1)
POSES["focinho_baixo"] = [("Pescoco", ANG, 0, 0), ("Pescoco2", ANG * 0.5, 0, 0), ("Cabeca", ANG * 0.25, 0, 0)]
print("FOCINHO_BAIXO angulo pescoco", ANG)
MET = {}
for nome, rots in POSES.items():
    aplica(rots); MET[nome] = {"min_z_malha": round(malha_min_z(), 4), "min_z_cabeca": round(cabeca_min_z(), 4)}
    for suf, cam in CAMS.items():
        if suf == "frente" and nome not in ("apoio", "focinho_baixo", "giro"): continue
        sc.camera = cam; sc.render.filepath = os.path.join(OUT, f"prova_{nome}_{suf}.png"); bpy.ops.render.render(write_still=True)
# closes de ombro / quadril / jarrete na passada
aplica(POSES["passada"])
for nm_, loc, alvo in (("ombro", (-1.05, -0.32, 0.30), (0.05, -0.22, 0.26)), ("quadril_jarrete", (-1.05, 0.30, 0.30), (0.05, 0.36, 0.26))):
    sc.camera = camera("Cam_" + nm_, loc, alvo, 45); sc.render.filepath = os.path.join(OUT, f"prova_passada_close_{nm_}.png"); bpy.ops.render.render(write_still=True)
REL["provas"] = MET; REL["focinho_baixo_angulo_pescoco"] = ANG
print("PROVAS", json.dumps(MET))
zera(); bpy.context.view_layer.update()
bpy.data.objects.remove(CHAO)
json.dump(REL, open(os.path.join(OUT, "rig_relatorio.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Javali_Rig.blend"))
print("RIG_OK")
