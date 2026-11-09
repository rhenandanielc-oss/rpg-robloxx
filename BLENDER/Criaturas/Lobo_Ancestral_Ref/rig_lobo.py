"""Rig do Lobo Ancestral (malha de jogo low/l03, base Meshy). Articulacoes medidas na propria malha; nomes dos ossos ja
sao os do jogo (o Roblox liga malha a osso pelo nome). Pesos: heat numa copia VOXEL fechada (a LOW tem mechas finas,
boca aberta e bordas) -> Data Transfer para a LOW -> mandibula/cabeca pelos atributos da boca -> suavizacao no corpo
(juba sem placas rigidas) -> no maximo 4 influencias. IK de 2 ossos por pata (alvo no punho/jarrete, polo achado por
busca). Pose de repouso: as 4 patas apoiadas e simetricas por par (a malha herdou a passada da pintura) e gravada
como repouso (malha e esqueleto).
Uso: blender -b low/l03/Lobo_Ancestral_LOW_rig.blend -P rig_lobo.py -- <saida_dir> [sem_repose]"""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
REPOSE = "sem_repose" not in A; ESPELHAR = "espelhar" in A
sc = bpy.context.scene; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; me = LO.data
DIR_IN = os.path.dirname(bpy.data.filepath)
M = json.load(open(os.path.join(DIR_IN, "marcos_rig.json")))
NAR = V(M["nariz"]); YC = M["y_canto"]
def zb(yy): return float(np.interp(yy, M["curva_y"], M["curva_z"]))
def ativo(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
x, y, z = co[:, 0], co[:, 1], co[:, 2]
YT = y.max()
# ------------------------------------------------------------------ patas: aglomerados no chao
pe_sel = (z < 0.30) & (y < 3.6)
pes = {}
ymid = (y[pe_sel].min() + y[pe_sel].max()) / 2
for lado, sx in (("E", 1), ("D", -1)):
    for par, cond in (("dian", y < ymid), ("tras", y >= ymid)):
        s = pe_sel & (x * sx > 0.15) & cond
        pes[(lado, par)] = V(co[s].mean(axis=0)); pes[(lado, par)].z = 0.0
        pes[(lado, par, "ponta")] = V((co[s][:, 0].mean(), co[s][:, 1].min(), 0.12))
        pes[(lado, par, "calc")] = V((co[s][:, 0].mean(), co[s][:, 1].max(), 0.15))
print("PES", {k: tuple(round(c, 2) for c in v) for k, v in pes.items() if len(k) == 2})
def secao(sx, y0, z0, faixa=0.12, raio=1.3):
    s = (np.abs(z - z0) < faixa) & (x * sx > 0.05) & (np.abs(y - y0) < raio)
    return V(co[s].mean(axis=0)) if s.sum() > 4 else None
ALT = 6.6                                                     # cernelha de projeto
PATA = {}
for lado, sx in (("E", 1), ("D", -1)):
    p = pes[(lado, "dian")]; pt = pes[(lado, "dian", "ponta")]
    punho = secao(sx, p.y, 0.16 * ALT, raio=0.8) or p + V((0, 0.1, 1.0))
    cot = secao(sx, punho.y, 0.48 * ALT, raio=1.1) or punho + V((0, 0.3, 2.1))
    omb = secao(sx, cot.y, 0.66 * ALT, raio=1.2) or cot + V((0, -0.4, 1.2))
    esc = V((omb.x * 0.6, omb.y + 0.55, 0.88 * ALT))
    cot = V((cot.x, cot.y + 0.20, cot.z))                     # cotovelo atras do eixo (dobra para tras)
    base = V((p.x, p.y - 0.15, 0.22)); ponta = V((pt.x, pt.y + 0.05, 0.10))
    PATA[(lado, "dian")] = (esc, omb, cot, punho, base, ponta)
    p = pes[(lado, "tras")]; pt = pes[(lado, "tras", "ponta")]
    jarr = secao(sx, p.y + 0.4, 0.25 * ALT, raio=0.9) or p + V((0, 0.5, 1.6))
    joel = secao(sx, jarr.y - 0.5, 0.50 * ALT, raio=1.2) or jarr + V((0, -0.8, 1.6))
    joel = V((joel.x, joel.y - 0.25, joel.z))                 # joelho a frente (dobra para frente)
    quad = secao(sx, joel.y + 0.6, 0.68 * ALT, raio=1.2) or joel + V((0, 0.6, 1.2))
    quad = V((quad.x * 0.75, quad.y + 0.1, quad.z))
    base = V((p.x, p.y - 0.15, 0.22)); ponta = V((pt.x, pt.y + 0.05, 0.10))
    PATA[(lado, "tras")] = (quad, joel, jarr, base, ponta)
# raizes das patas simetricas (pelve rigida; escapulas no repouso): media do par em y/z e |x| medio
def sim(pE, pD):
    xm = (abs(pE.x) + abs(pD.x)) / 2; ym = (pE.y + pD.y) / 2; zm = (pE.z + pD.z) / 2
    return V((xm, ym, zm)), V((-xm, ym, zm))
for par, idx in (("dian", (0, 1)), ("tras", (0,))):
    E_, D_ = list(PATA[("E", par)]), list(PATA[("D", par)])
    for i in idx: E_[i], D_[i] = sim(E_[i], D_[i])
    PATA[("E", par)], PATA[("D", par)] = tuple(E_), tuple(D_)
if ESPELHAR:                                                   # 2a passada (malha ja com as patas simetricas): D = espelho da media
    def esp(v): return V((-v.x, v.y, v.z))
    for par in ("dian", "tras"):
        E_, D_ = PATA[("E", par)], PATA[("D", par)]
        med = tuple((a + esp(b)) / 2 for a, b in zip(E_, D_))
        PATA[("E", par)] = med; PATA[("D", par)] = tuple(esp(v) for v in med)
# v2 (03/11): cotovelo e joelho na RETA ombro->punho / quadril->jarrete na vista frontal (a secao media pegava o pelo
# do peito e punha o cotovelo em x 0,49 com ombro e punho em 1,28: perna em "X" e ombro/juba arrastados no repouso)
for lado, sx in (("E", 1), ("D", -1)):
    esc, omb, cot, punho, base, ponta = PATA[(lado, "dian")]
    t_ = (omb.z - cot.z) / max(1e-3, omb.z - punho.z); cot = V((omb.x + (punho.x - omb.x) * t_, cot.y + (0.30 if ESPELHAR else 0.0), cot.z))   # olecrano atras da linha (folga do IK)
    PATA[(lado, "dian")] = (esc, omb, cot, punho, base, ponta)
    quad, joel, jarr, base, ponta = PATA[(lado, "tras")]
    t_ = (quad.z - joel.z) / max(1e-3, quad.z - jarr.z); joel = V((quad.x + (jarr.x - quad.x) * t_ + 0.06 * sx, joel.y, joel.z))
    PATA[(lado, "tras")] = (quad, joel, jarr, base, ponta)
for k, v in PATA.items(): print("PATA", k, [tuple(round(c, 2) for c in q) for q in v])
# ------------------------------------------------------------------ coluna, pescoco, cabeca, cauda
def centro(y0, zmin=3.4, faixa=0.25):
    s = (np.abs(y - y0) < faixa) & (z > zmin) & (np.abs(x) < 1.5)
    if s.sum() < 10: return None
    zz = z[s]; return V((0, y0, zz.max() - 0.38 * (zz.max() - zz.min())))
y_omb = (PATA[("E", "dian")][1].y + PATA[("D", "dian")][1].y) / 2
y_quad = (PATA[("E", "tras")][0].y + PATA[("D", "tras")][0].y) / 2
ys = np.linspace(y_quad, y_omb, 4)
COL = [centro(float(a)) for a in ys]
Y_ATLAS = NAR.y + 2.05                                        # nuca (atras das orelhas)
s_cab = (y < NAR.y + 2.3) & (z > 6.0)
z_topo_cab = z[s_cab & (np.abs(x) < 0.3)].max()
ATLAS = V((0, Y_ATLAS, z_topo_cab - 0.55))
CAB_PONTA = V((0, NAR.y + 0.15, NAR.z))
PESC_BASE = COL[-1] + V((0, -0.35, 0.35))
PESC_MEIO = PESC_BASE.lerp(ATLAS, 0.5) + V((0, -0.15, 0.10))
DOB = V((0, YC + 0.45, zb(YC) + 0.05)); QUEIXO = V((0, NAR.y + 0.45, zb(NAR.y + 0.45) - 0.12))
# orelhas: pontas mais altas de cada lado
orel = {}
for lado, sx in (("E", 1), ("D", -1)):
    s = s_cab & (x * sx > 0.05); i = int(np.argmax(np.where(s, z, -9)))
    topo = V(co[i]); base = V((topo.x * 0.85, topo.y + 0.10, topo.z - 0.85))
    orel[lado] = (base, topo)
if ESPELHAR:
    bE, tE = orel["E"]; bD, tD = orel["D"]
    mb = V(((bE.x - bD.x) / 2, (bE.y + bD.y) / 2, (bE.z + bD.z) / 2)); mt = V(((tE.x - tD.x) / 2, (tE.y + tD.y) / 2, (tE.z + tD.z) / 2))
    orel = {"E": (mb, mt), "D": (V((-mb.x, mb.y, mb.z)), V((-mt.x, mt.y, mt.z)))}
print("ORELHAS", {k: [tuple(round(c, 2) for c in q) for q in v] for k, v in orel.items()})
CAUDA = []
for a in np.linspace(y_quad + 0.9, YT - 0.25, 7):
    s = (np.abs(y - a) < 0.25) & (z > 0.8) & (y > y_quad + 0.6)
    if s.sum() > 10: CAUDA.append(V((0, float(a), float((z[s].min() + z[s].max()) / 2))))
print("COLUNA", [tuple(round(c, 2) for c in q) for q in COL], "ATLAS", tuple(round(c, 2) for c in ATLAS), "CAUDA", len(CAUDA))
# ------------------------------------------------------------------ armadura
ad = bpy.data.armatures.new("Lobo_Ancestral_Rig"); arm = bpy.data.objects.new("Lobo_Ancestral_Rig", ad)
sc.collection.objects.link(arm); ativo(arm); bpy.ops.object.mode_set(mode="EDIT"); E = ad.edit_bones
def osso(nome, a, b, pai=None, conecta=False, deform=True):
    o = E.new(nome); o.head = a; o.tail = b; o.use_deform = deform
    if pai: o.parent = E[pai]; o.use_connect = conecta and (E[pai].tail - a).length < 1e-4
    return o
y_meio = (y_quad + y_omb) / 2
osso("Raiz", V((0, y_meio, 0)), V((0, y_meio - 1.0, 0)), deform=False)
osso("Pelve", COL[0] + V((0, 0.6, 0.05)), COL[0], "Raiz")
osso("Coluna1", COL[0], COL[1], "Pelve", True)
osso("Coluna2", COL[1], COL[2], "Coluna1", True)
osso("Peito", COL[2], COL[3], "Coluna2", True)
osso("Pescoco1", COL[3], PESC_MEIO, "Peito", False)
osso("Pescoco2", PESC_MEIO, ATLAS, "Pescoco1", True)
osso("Cabeca", ATLAS, CAB_PONTA, "Pescoco2", True)
osso("Mandibula", DOB, QUEIXO, "Cabeca")
for lado in ("E", "D"):
    b_, t_ = orel[lado]; osso("Orelha" + lado, b_, t_, "Cabeca")
    sx = 1 if lado == "E" else -1
    jb = PESC_MEIO + V((0.75 * sx, 0.1, -0.2)); osso("Juba" + lado, jb, jb + V((0.25 * sx, 0.35, -0.9)), "Pescoco1")
pc = COL[3] + V((0, -1.15, -0.7)); osso("JubaPeito", pc, pc + V((0, -0.1, -1.0)), "Peito")
prev = "Pelve"; cini = COL[0] + V((0, 0.6, 0.05))
pts_c = [cini] + CAUDA
for i in range(len(pts_c) - 1):
    osso("Cauda%d" % (i + 1), pts_c[i], pts_c[i + 1], prev, i > 0); prev = "Cauda%d" % (i + 1)
for lado in ("E", "D"):
    esc, omb, cot, punho, base, ponta = PATA[(lado, "dian")]
    osso("Escapula" + lado, esc, omb, "Peito"); osso("Braco" + lado, omb, cot, "Escapula" + lado, True)
    osso("Antebraco" + lado, cot, punho, "Braco" + lado, True); osso("Mao" + lado, punho, base, "Antebraco" + lado, True)
    osso("Dedos" + lado, base, ponta, "Mao" + lado, True)
    quad, joel, jarr, base, ponta = PATA[(lado, "tras")]
    osso("Coxa" + lado, quad, joel, "Pelve"); osso("Canela" + lado, joel, jarr, "Coxa" + lado, True)
    osso("Metatarso" + lado, jarr, base, "Canela" + lado, True); osso("Pe" + lado, base, ponta, "Metatarso" + lado, True)
for b in E: b.roll = 0.0
bpy.ops.object.mode_set(mode="OBJECT")
print("OSSOS", len(ad.bones))

# ------------------------------------------------------------------ pesos: heat no proxy voxel -> transferencia
PX = LO.copy(); PX.data = me.copy(); PX.name = "Proxy_Pesos"; sc.collection.objects.link(PX)
ativo(PX)
rm = PX.modifiers.new("Vox", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.08; bpy.ops.object.modifier_apply(modifier=rm.name)
bmp = bmesh.new(); bmp.from_mesh(PX.data); bmp.verts.ensure_lookup_table()   # so a peca principal (ilhas de mecha soltas)
vist = set(); ilhas = []
for v0 in bmp.verts:
    if v0.index in vist: continue
    pilha = [v0]; vist.add(v0.index); ilha = []
    while pilha:
        v = pilha.pop(); ilha.append(v)
        for e in v.link_edges:
            w_ = e.other_vert(v)
            if w_.index not in vist: vist.add(w_.index); pilha.append(w_)
    ilhas.append(ilha)
ilhas.sort(key=len, reverse=True)
bmesh.ops.delete(bmp, geom=[v for il in ilhas[1:] for v in il], context="VERTS")
print("PROXY ilhas", len(ilhas), "mantida", len(ilhas[0]))
bmp.to_mesh(PX.data); bmp.free()
sm_ = PX.modifiers.new("Liso", "SMOOTH"); sm_.iterations = 4; bpy.ops.object.modifier_apply(modifier=sm_.name)
dc = PX.modifiers.new("Dec", "DECIMATE"); dc.ratio = min(1.0, 40000 / max(1, len(PX.data.polygons))); bpy.ops.object.modifier_apply(modifier=dc.name)
for vg in list(PX.vertex_groups): PX.vertex_groups.remove(vg)
bpy.ops.object.select_all(action="DESELECT"); PX.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
sem = sum(1 for v in PX.data.vertices if not v.groups); print("PROXY verts", len(PX.data.vertices), "sem peso", sem)
for vg in list(LO.vertex_groups):
    if vg.name != "Densidade": continue
    LO.vertex_groups.remove(vg)
for b in ad.bones:
    if b.use_deform and b.name not in LO.vertex_groups: LO.vertex_groups.new(name=b.name)
ativo(LO)
dt = LO.modifiers.new("DT", "DATA_TRANSFER"); dt.object = PX; dt.use_vert_data = True; dt.data_types_verts = {"VGROUP_WEIGHTS"}
dt.vert_mapping = "POLYINTERP_NEAREST"; dt.layers_vgroup_select_src = "ALL"; dt.layers_vgroup_select_dst = "NAME"
bpy.ops.object.datalayout_transfer(modifier=dt.name); bpy.ops.object.modifier_apply(modifier=dt.name)
bpy.data.objects.remove(PX)
def gp(nome): return LO.vertex_groups[nome]
def peso(g, i):
    try: return g.weight(i)
    except RuntimeError: return 0.0
# mandibula x cabeca pelos atributos da boca (faces "mandibula" e pecas de baixo) + degrade atras do canto
MAND = set()
ma = me.attributes["mandibula"].data
for p in me.polygons:
    if ma[p.index].value: MAND.update(p.vertices)
gc, gm = gp("Cabeca"), gp("Mandibula")
def suave(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
cab_ = 0
for v in me.vertices:
    c = v.co
    if c.y > DOB.y + 0.9 or c.z < zb(min(c.y, YC)) - 1.4 or abs(c.x) > 1.4: continue
    if v.index in MAND: wm = 1.0
    elif c.y < YC - 0.05: wm = 0.0
    else:
        wm = (1 - suave((c.y - YC) / (DOB.y + 0.9 - YC))) * suave((DOB.z + 0.05 - c.z) / 0.45)
    if c.y < YC - 0.05 or v.index in MAND:                    # focinho: so Cabeca/Mandibula
        for g in list(v.groups):
            nm = LO.vertex_groups[g.group].name
            if nm not in ("Cabeca", "Mandibula"): LO.vertex_groups[g.group].remove([v.index])
        gm.add([v.index], wm, "REPLACE"); gc.add([v.index], 1.0 - wm, "REPLACE"); cab_ += 1
    else:
        tot = sum(g.weight for g in v.groups) or 1.0
        gm.add([v.index], wm * tot, "REPLACE")
print("BOCA verts mandibula", len(MAND), "focinho", cab_)
# suaviza pesos do corpo (fora do focinho) para a juba nao virar placa
ativo(LO)
nomes_g = [g.name for g in LO.vertex_groups]; G = len(nomes_g); Wt = np.zeros((G, n))
for v in me.vertices:
    for g in v.groups: Wt[g.group, v.index] = g.weight
viz = [[] for _ in range(n)]
for e in me.edges: a_, b_ = e.vertices; viz[a_].append(b_); viz[b_].append(a_)
fixo = np.array([v.co.y < YC + 0.9 and v.co.z > 5.4 and abs(v.co.x) < 1.4 for v in me.vertices])   # focinho/mandibula intocados
for _ in range(3):
    Wn = Wt.copy()
    for i in range(n):
        if fixo[i] or not viz[i]: continue
        Wn[:, i] = 0.5 * Wt[:, i] + 0.5 * Wt[:, viz[i]].mean(axis=1)
    Wt = Wn
for gi, nm in enumerate(nomes_g):
    g = LO.vertex_groups[nm]
    for i in np.nonzero(Wt[gi] > 1e-4)[0]: g.add([int(i)], float(Wt[gi, i]), "REPLACE")
print("PESOS suavizados (3x vizinhos)")
bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
if "Densidade" in LO.vertex_groups: LO.vertex_groups.remove(LO.vertex_groups["Densidade"])
sem = sum(1 for v in me.vertices if not v.groups); print("PESOS LOW sem peso", sem)
LO.parent = arm
for m_ in list(LO.modifiers): LO.modifiers.remove(m_)
am = LO.modifiers.new("Armature", "ARMATURE"); am.object = arm

# ------------------------------------------------------------------ IK por pata
def criar_ik():
    alvos = {}
    for lado, sx in (("E", 1), ("D", -1)):
        for nomes in (("Braco", "Antebraco", "Mao"), ("Coxa", "Canela", "Metatarso")):
            b0, b1, b2 = (arm.data.bones[q + lado] for q in nomes)
            alvo = bpy.data.objects.get("IK_" + nomes[2] + lado) or bpy.data.objects.new("IK_" + nomes[2] + lado, None)
            if alvo.name not in sc.collection.objects: sc.collection.objects.link(alvo)
            alvo.location = b2.head_local.copy(); alvo.empty_display_size = 0.4; alvo.rotation_mode = "QUATERNION"
            alvo.rotation_quaternion = b2.matrix_local.to_quaternion()
            polo = bpy.data.objects.get("Polo_" + nomes[1] + lado) or bpy.data.objects.new("Polo_" + nomes[1] + lado, None)
            if polo.name not in sc.collection.objects: sc.collection.objects.link(polo)
            frente = -1.0 if nomes[0] == "Coxa" else 1.0           # joelho aponta para a frente (-Y); cotovelo para tras (+Y)
            polo.location = b1.head_local + V((0.0, 2.5 * frente, 0.0))
            pb = arm.pose.bones[nomes[1] + lado]
            for c in list(pb.constraints): pb.constraints.remove(c)
            c = pb.constraints.new("IK"); c.target = alvo; c.pole_target = polo; c.chain_count = 2; c.use_tail = True
            pm = arm.pose.bones[nomes[2] + lado]
            for c2 in list(pm.constraints): pm.constraints.remove(c2)
            cr = pm.constraints.new("COPY_ROTATION"); cr.target = alvo; cr.mix_mode = "REPLACE"; cr.target_space = "WORLD"; cr.owner_space = "WORLD"
            alvos[nomes[2] + lado] = (alvo, polo, nomes)
    bpy.context.view_layer.update()
    for k, (alvo, polo, nomes) in alvos.items():
        lado = k[-1]; c = arm.pose.bones[nomes[1] + lado].constraints["IK"]; b0 = arm.data.bones[nomes[0] + lado]
        def erro(a_):
            c.pole_angle = a_; bpy.context.view_layer.update()
            return (arm.pose.bones[b0.name].tail - b0.tail_local).length
        a_ = min((erro(math.radians(g)), math.radians(g)) for g in range(-180, 180, 3))[1]
        for passo in (1.0, 0.25, 0.05):
            a_ = min([a_ + math.radians(passo * q) for q in range(-4, 5)], key=erro)
        c.pole_angle = a_; print("POLO", k, round(math.degrees(a_), 1), "erro", round(erro(a_), 4))
    return alvos
ativo(arm); arm.select_set(True)
for pb in arm.pose.bones: pb.rotation_mode = "QUATERNION"
ALVOS = criar_ik()

# ------------------------------------------------------------------ pose de repouso: 4 patas apoiadas, simetricas por par
if REPOSE:
    # almofada (base dos dedos) simetrica por par; metacarpo/metatarso com a MESMA direcao nos dois lados (quase
    # vertical, base um pouco a frente); dedos deitados para a frente; altura ajustada ate a pata tocar o chao
    DIR = {"Mao": V((0, -0.22, -1)).normalized(), "Metatarso": V((0, -0.30, -1)).normalized()}
    DEDO = V((0, -1, -0.20)).normalized()
    alvo_bola = {}
    for par in ("Mao", "Metatarso"):
        bE, bD = arm.data.bones[par + "E"], arm.data.bones[par + "D"]
        tE, tD = bE.tail_local, bD.tail_local
        ym = (tE.y + tD.y) / 2; xm = (abs(tE.x) + abs(tD.x)) / 2 * 0.92; zm = (tE.z + tD.z) / 2
        for lado, sx in (("E", 1), ("D", -1)):
            alvo_bola[par + lado] = V((xm * sx, ym, zm))
    def aplicar(ajuste_z):
        for k, bola in alvo_bola.items():
            bn = arm.data.bones[k]; alvo = ALVOS[k][0]; d = DIR[k[:-1]]
            alvo.location = bola + V((0, 0, ajuste_z.get(k, 0.0))) - d * bn.length
            R = bn.matrix_local.to_3x3().col[1].normalized().rotation_difference(d)
            alvo.rotation_quaternion = R @ bn.matrix_local.to_quaternion()
        bpy.context.view_layer.update()
        for lado in ("E", "D"):
            for nm in ("Dedos", "Pe"):
                pb = arm.pose.bones[nm + lado]; pb.rotation_quaternion = (1, 0, 0, 0); bpy.context.view_layer.update()
                mt = pb.matrix.copy(); R = mt.to_3x3().col[1].normalized().rotation_difference(DEDO)
                nova = Matrix.Translation(mt.translation) @ (R.to_matrix().to_4x4() @ mt.to_3x3().to_4x4())
                pb.matrix = nova; bpy.context.view_layer.update()
    def zmin_patas():
        dg = bpy.context.evaluated_depsgraph_get(); ev = LO.evaluated_get(dg).data
        out = {}
        for k, bola in alvo_bola.items():
            pts = [v.co.z for v in ev.vertices if (v.co.x - bola.x) ** 2 + (v.co.y - bola.y) ** 2 < 0.45 ** 2 and v.co.z < 0.9]
            out[k] = min(pts) if pts else 0.0
        return out
    ajuste = {}
    for it in range(3):
        aplicar(ajuste); zm_ = zmin_patas()
        for k, zz in zm_.items(): ajuste[k] = ajuste.get(k, 0.0) - zz
        print("REPOSE iteracao", it, {k: round(v, 3) for k, v in zm_.items()})
    aplicar(ajuste)
    for k in alvo_bola: print("REPOSE", k, "bola", tuple(round(c, 2) for c in alvo_bola[k]), "dz", round(ajuste.get(k, 0), 3))
    # grava: malha deformada vira a malha de repouso; pose vira repouso do esqueleto
    ativo(LO)
    dg = bpy.context.evaluated_depsgraph_get(); ev = LO.evaluated_get(dg)
    novos = [v.co.copy() for v in ev.data.vertices]
    for v, p in zip(me.vertices, novos): v.co = p
    me.update()
    ativo(arm); bpy.ops.object.mode_set(mode="POSE"); bpy.ops.pose.select_all(action="SELECT")
    bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode="OBJECT")
    for pb in arm.pose.bones:
        for c in pb.constraints: pb.constraints.remove(c)
    ALVOS = criar_ik()
    zmin = min(v.co.z for v in me.vertices); print("REPOSE z_min malha", round(zmin, 3))
desvio = max((arm.pose.bones[b.name].tail - b.tail_local).length for b in arm.data.bones)
print("IK desvio_repouso_max %.4f" % desvio)
arm["y_canto"], arm["dob_y"], arm["dob_z"] = YC, DOB.y, DOB.z
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend"))
if REPOSE:                                                    # malha em repouso simetrico, sem rig: entrada da 2a passada
    for o in list(sc.objects):
        if o.type in ("ARMATURE", "EMPTY"): bpy.data.objects.remove(o)
    LO.modifiers.clear(); LO.vertex_groups.clear()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DIR_IN, "Lobo_Ancestral_LOW_repouso.blend"))
    print("REPOUSO_SALVO", os.path.join(DIR_IN, "Lobo_Ancestral_LOW_repouso.blend"))
print("RIG_OK ossos", len(ad.bones), [b.name for b in ad.bones])
