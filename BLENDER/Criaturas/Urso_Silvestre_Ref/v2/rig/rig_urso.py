"""Rig do Urso Silvestre v2 (malha de jogo do Meshy). Pele deformavel com ossos de coluna, quadril, escapulas, 4 membros
plantigrados (com dedos), pescoco, cabeca, mandibula, orelhas e cauda. Marcos medidos na propria malha (fatias de
altura por pata). Nomes ja sao os do jogo (o Roblox liga malha a osso pelo NOME; nao renomear no Studio).
Pesos: heat (Blender) na pele unida (costuras soldadas para nao abrir); mandibula pela linha dos labios medida na malha;
orelhas por distancia da base; pecas da boca pelo atributo "mand". Maximo de 4 influencias por vertice (Roblox).
Uso: blender -b ../low/CR_Urso_v2_LOW.blend -P rig_urso.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def ativar(o):
    for x in sc.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
for o in list(sc.objects):                                   # a malha bruta (fonte do bake) nao vai para o rig
    if o.name.startswith("CR_Urso_Meshy"): bpy.data.objects.remove(o)
CAB, FR, TR, BOCA = (bpy.data.objects[n] for n in ("Urso_Cabeca", "Urso_Corpo_Frente", "Urso_Corpo_Tras", "Urso_Boca"))

# ------------------------------------------------------------------ pele unida (pesos consistentes nas costuras)
ativar(CAB); FR.select_set(True); TR.select_set(True); bpy.ops.object.join(); PELE = bpy.context.object; PELE.name = "tmp_Pele"
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.remove_doubles(threshold=1e-4)
bpy.ops.object.mode_set(mode="OBJECT")
for g in list(PELE.vertex_groups): PELE.vertex_groups.remove(g)     # tira grupos auxiliares (ex.: 'densidade' da reducao)
me = PELE.data; n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
x, y, z = co[:, 0], co[:, 1], co[:, 2]; Y0, Y1 = y.min(), y.max()
print("PELE verts", n, "y", round(Y0, 2), round(Y1, 2))

# ------------------------------------------------------------------ marcos
def eixo_pata(sx, ypes):
    """centroide da coluna da pata em fatias de altura (segue o eixo real do membro)"""
    sel0 = (z < 0.45) & (x * sx > 0.8) & (np.abs(y - ypes) < 1.6)
    pe = co[sel0].mean(axis=0)
    def fatia(zz, raio=1.3):
        s = (np.abs(z - zz) < 0.18) & (np.abs(x - pe[0]) < raio) & (np.abs(y - pe[1]) < 1.7) & (x * sx > 0.6)
        return V(co[s].mean(axis=0)) if s.sum() > 10 else V((pe[0], pe[1], zz))
    return V(pe), fatia
pes = {}
for lado, sx in (("E", 1), ("D", -1)):
    for par, ys in (("dian", (y < 0)), ("tras", (y >= 0))):
        sel = (z < 0.45) & (x * sx > 0.8) & ys
        pes[(lado, par)] = co[sel].mean(axis=0)
print("PES", {k: tuple(round(float(c), 2) for c in v) for k, v in pes.items()})
def centro(yy, faixa=0.25):
    s = (np.abs(y - yy) < faixa) & (np.abs(x) < 0.8)
    return V((0, yy, (z[s].min() + z[s].max()) / 2)) if s.any() else V((0, yy, 5.5))
def topo(yy, faixa=0.25):
    s = (np.abs(y - yy) < faixa) & (np.abs(x) < 0.8); return float(z[s].max())
y_omb = (pes[("E", "dian")][1] + pes[("D", "dian")][1]) / 2
y_quad = (pes[("E", "tras")][1] + pes[("D", "tras")][1]) / 2
DOBRA = V((0, -4.70, 6.30)); CANTO = -5.13                        # mandibula (linha dos labios medida na malha)
LAB = [(-5.13, 6.263), (-5.24, 6.213), (-5.39, 6.153), (-5.55, 6.133), (-5.72, 6.150), (-5.90, 6.140), (-6.25, 6.140)]
def lab(yy):
    if yy >= LAB[0][0]: return LAB[0][1]
    for (y0, z0), (y1, z1) in zip(LAB, LAB[1:]):
        if y1 <= yy <= y0: return z0 + (z1 - z0) * (yy - y0) / (y1 - y0)
    return LAB[-1][1]
# orelhas: ponto mais alto de cada lado na regiao da cabeca
ORE = {}
for lado, sx in (("E", 1), ("D", -1)):
    s = (y < -4.0) & (y > -5.2) & (x * sx > 0.45)
    i = np.argmax(np.where(s, z, -9)); ORE[lado] = V(co[i])
print("ORELHAS", {k: tuple(round(c, 2) for c in v) for k, v in ORE.items()}, "ombro y", round(float(y_omb), 2), "quadril y", round(float(y_quad), 2))

# ------------------------------------------------------------------ esqueleto
arm_d = bpy.data.armatures.new("Urso_Rig"); arm = bpy.data.objects.new("Urso_Rig", arm_d); sc.collection.objects.link(arm)
ativar(arm); bpy.ops.object.mode_set(mode="EDIT"); E = arm_d.edit_bones
def osso(nome, a, b, pai=None, conecta=True):
    o = E.new(nome); o.head = a; o.tail = b
    if pai: o.parent = E[pai]; o.use_connect = conecta and (E[pai].tail - V(a)).length < 1e-4
    return o
y_meio = (y_quad + y_omb) / 2
osso("Raiz", V((0, y_meio, 0)), V((0, y_meio - 1.0, 0)))                          # no chao, aponta para a frente
osso("Pelve", centro(y_quad + 0.6), centro(y_quad - 0.5), "Raiz", False)
osso("Coluna1", E["Pelve"].tail, centro(y_meio), "Pelve")
osso("Coluna2", E["Coluna1"].tail, centro(y_omb + 0.6), "Coluna1")
osso("Coluna3", E["Coluna2"].tail, centro(y_omb - 0.5), "Coluna2")                 # corcova/escapulas
osso("Pescoco", E["Coluna3"].tail, V((0, -3.55, 6.75)), "Coluna3")
osso("Pescoco2", E["Pescoco"].tail, V((0, -4.45, 6.85)), "Pescoco")
osso("Cabeca", E["Pescoco2"].tail, V((0, Y0 + 0.35, 6.50)), "Pescoco2")
osso("Mandibula", DOBRA, V((0, Y0 + 0.45, lab(Y0 + 0.45) - 0.20)), "Cabeca", False)
for lado in ("E", "D"):
    b0 = ORE[lado] - V((0, 0, 0.38)); osso("Orelha" + lado, b0, ORE[lado], "Cabeca", False)
osso("Cauda1", centro(Y1 - 1.0), centro(Y1 - 0.45), "Pelve", False)
osso("Cauda2", E["Cauda1"].tail, V((0, Y1 + 0.05, centro(Y1 - 0.45).z - 0.15)), "Cauda1")
PATA = {}
for lado, sx in (("E", 1), ("D", -1)):
    for par in ("dian", "tras"):
        pe, fatia = eixo_pata(sx, pes[(lado, par)][1])
        frente_y = co[(z < 0.45) & (np.abs(x - pe.x) < 1.2) & (np.abs(y - pe.y) < 1.6)][:, 1].min()
        if par == "dian":
            omb = fatia(6.0); cot = fatia(3.6) + V((0, 0.30, 0)); pun = fatia(1.05); mao = V((pe.x, pe.y - 0.10, 0.42))
            ponta = V((pe.x, frente_y + 0.25, 0.30))
            esc = V((omb.x * 0.55, omb.y + 0.15, topo(omb.y) - 0.45))
            osso("Escapula" + lado, esc, omb, "Coluna3", False)
            osso("Braco" + lado, omb, cot, "Escapula" + lado); osso("Antebraco" + lado, cot, pun, "Braco" + lado)
            osso("Mao" + lado, pun, mao, "Antebraco" + lado); osso("Dedos" + lado, mao, ponta, "Mao" + lado)
            PATA[(lado, par)] = (omb, cot, pun, mao, ponta)
        else:
            qua = fatia(5.3); joe = fatia(3.1) + V((0, -0.30, 0)); cal = fatia(0.85) + V((0, 0.35, 0)); pep = V((pe.x, pe.y - 0.05, 0.40))
            ponta = V((pe.x, frente_y + 0.25, 0.28))
            osso("Coxa" + lado, qua, joe, "Pelve", False); osso("Canela" + lado, joe, cal, "Coxa" + lado)
            osso("Pe" + lado, cal, pep, "Canela" + lado); osso("Dedos" + ("Pe" + lado), pep, ponta, "Pe" + lado)
            PATA[(lado, par)] = (qua, joe, cal, pep, ponta)
for b in E: b.roll = 0.0
bpy.ops.object.mode_set(mode="OBJECT")
print("OSSOS", len(arm_d.bones), [b.name for b in arm_d.bones])

# ------------------------------------------------------------------ pesos: heat num PROXY fechado (voxel) -> transferencia para a pele
# (o heat falha na pele real: boca recortada e pequenas sobreposicoes do Meshy)
prox = PELE.copy(); prox.data = PELE.data.copy(); prox.name = "tmp_Proxy"; sc.collection.objects.link(prox)
arm.data.bones["Raiz"].use_deform = False                     # osso no chao, fora da malha: nao deforma (o heat falha com ele)
ativar(prox); rmp = prox.modifiers.new("R", "REMESH"); rmp.mode = "VOXEL"; rmp.voxel_size = 0.10; bpy.ops.object.modifier_apply(modifier=rmp.name)
smp = prox.modifiers.new("S", "SMOOTH"); smp.factor = 0.5; smp.iterations = 3; bpy.ops.object.modifier_apply(modifier=smp.name)
ativar(prox); arm.select_set(True); bpy.context.view_layer.objects.active = arm
try: bpy.ops.object.parent_set(type="ARMATURE_AUTO")
except Exception as e: print("HEAT proxy erro:", e)
sem_p = sum(1 for v in prox.data.vertices if not v.groups); print("PESOS heat no proxy: verts", len(prox.data.vertices), "sem peso", sem_p)
if sem_p > len(prox.data.vertices) * 0.02:
    # reserva: peso por distancia aos segmentos dos ossos (1/d^4), lados das patas separados por x
    for g in list(prox.vertex_groups): prox.vertex_groups.remove(g)
    segs = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones if b.name != "Raiz"]
    gs = {nm: prox.vertex_groups.new(name=nm) for nm, _, _ in segs}
    def dseg(p, a_, b_):
        ab = b_ - a_; t_ = max(0.0, min(1.0, (p - a_).dot(ab) / max(ab.length_squared, 1e-9))); return (p - (a_ + ab * t_)).length
    for v in prox.data.vertices:
        p = v.co; ds = []
        for nm, a_, b_ in segs:
            if nm.endswith("E") and p.x < -0.3 and not nm.startswith("Orelha"): continue
            if nm.endswith("D") and p.x > 0.3 and not nm.startswith("Orelha"): continue
            ds.append((dseg(p, a_, b_), nm))
        ds.sort(); ds = ds[:4]; ws = [1.0 / max(d, 0.05) ** 4 for d, _ in ds]; tot = sum(ws)
        for (d, nm), w_ in zip(ds, ws): gs[nm].add([v.index], w_ / tot, "REPLACE")
    print("PESOS reserva: distancia aos ossos")
for g in prox.vertex_groups: PELE.vertex_groups.new(name=g.name)
ativar(PELE); dt = PELE.modifiers.new("DT", "DATA_TRANSFER"); dt.object = prox; dt.use_vert_data = True
dt.data_types_verts = {"VGROUP_WEIGHTS"}; dt.vert_mapping = "POLYINTERP_NEAREST"; dt.layers_vgroup_select_src = "ALL"; dt.layers_vgroup_select_dst = "NAME"
bpy.ops.object.modifier_apply(modifier=dt.name)
bpy.data.objects.remove(prox)
ativar(PELE); arm.select_set(True); bpy.context.view_layer.objects.active = arm; bpy.ops.object.parent_set(type="ARMATURE_NAME")
from mathutils.kdtree import KDTree
vazios = [v.index for v in me.vertices if not v.groups or max(g.weight for g in v.groups) < 1e-3]
cheios = [v.index for v in me.vertices if v.index not in set(vazios)]
kd = KDTree(len(cheios))
for i in cheios: kd.insert(me.vertices[i].co, i)
kd.balance()
for i in vazios:                                              # herda os pesos do vizinho com peso mais proximo
    _, j, _ = kd.find(me.vertices[i].co)
    for g in me.vertices[j].groups: PELE.vertex_groups[g.group].add([i], g.weight, "REPLACE")
print("PESOS na pele: verts sem peso", len(vazios), "-> herdados do vizinho")
G = {g.name: g for g in PELE.vertex_groups}
def grupo(nome): return G.get(nome) or PELE.vertex_groups.new(name=nome)
gM, gC = grupo("Mandibula"), grupo("Cabeca")
YJ = -4.75
def w_mand(p):
    if p.y > YJ: return 0.0
    if p.y < CANTO: return suave((lab(p.y) - p.z) / 0.012 + 0.5)
    return suave((lab(CANTO) - 0.02 - p.z) / 0.25) * suave((YJ - p.y) / (YJ - CANTO))
for v in me.vertices:
    p = v.co
    if p.y < -4.3 and p.z > 5.0:                              # cabeca: cranio x mandibula pela linha dos labios
        wm = w_mand(p)
        tot_cab = sum(g.weight for g in v.groups if PELE.vertex_groups[g.group].name in ("Cabeca", "Mandibula", "OrelhaE", "OrelhaD"))
        if p.y < -4.9:                                        # a frente das orelhas: so cabeca/mandibula (o heat vaza para o pescoco)
            for g in list(v.groups): PELE.vertex_groups[g.group].remove([v.index])
            gC.add([v.index], 1.0 - wm, "REPLACE"); gM.add([v.index], wm, "REPLACE") if wm > 1e-3 else None
        elif wm > 1e-3:
            gM.add([v.index], wm, "REPLACE")
    for lado in ("E", "D"):                                   # orelhas: da base para a ponta
        b0 = ORE[lado] - V((0, 0, 0.38)); d = (p - ORE[lado]).length
        if d < 0.45 and p.z > b0.z - 0.05 and p.y < -3.95:
            w = suave((p.z - (b0.z - 0.12)) / 0.45) * suave((0.45 - d) / 0.20)      # REVISAO: degrade mais longo na base da orelha
            if w > 1e-3: grupo("Orelha" + lado).add([v.index], w, "REPLACE")
# barriga e peito por baixo, entre as patas: peso das pernas passa para a coluna (as franjas esticavam com as pernas)
PERNA = ("Braco", "Antebraco", "Coxa", "Canela")
def coluna_de(yy): return "Pelve" if yy > 3.4 else ("Coluna1" if yy > 1.0 else ("Coluna2" if yy > -1.6 else "Coluna3"))
for v in me.vertices:
    p = v.co
    if not (-3.4 < p.y < 5.0 and p.z < 4.6): continue
    k = suave((1.25 - abs(p.x)) / 0.55) * suave((4.6 - p.z) / 0.6)
    if k < 1e-3: continue
    mov = 0.0
    for g in list(v.groups):
        nm = PELE.vertex_groups[g.group].name
        if nm.startswith(PERNA):
            tira = g.weight * k; mov += tira; PELE.vertex_groups[g.group].add([v.index], g.weight - tira, "REPLACE")
    if mov > 0:
        gc_ = grupo(coluna_de(p.y)); atual = next((g.weight for g in v.groups if g.group == gc_.index), 0.0)
        gc_.add([v.index], atual + mov, "REPLACE")
ativar(PELE)
# suaviza pesos (lascas de pelo do Meshy pegavam peso de osso distante e esticavam), preservando cabeca x mandibula
travados = {"Mandibula", "Cabeca"}
for g in PELE.vertex_groups: g.lock_weight = g.name in travados
bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=0.6, repeat=4, expand=0.0)
bpy.ops.object.mode_set(mode="OBJECT")
for g in PELE.vertex_groups: g.lock_weight = False
# REVISAO 03/11: sola das patas segue a pata (Mao/Pe) em degrade a partir do punho/calcanhar. Medido: a sola tinha peso
# do antebraco/canela e andava ~0,07 durante o apoio (o punho ficava parado) e afundava ~0,08 ao pousar. Dedos/garras
# mantem os pesos proprios (articulacao preservada); acima do punho nada muda.
pata_mov = 0
for lado in ("E", "D"):
    for pata, perna_, dedos_ in (("Mao", "Antebraco", "Dedos"), ("Pe", "Canela", "DedosPe")):
        gP, gL = grupo(pata + lado), grupo(perna_ + lado); j = arm.data.bones[pata + lado].head_local
        for v in me.vertices:
            p = v.co
            alc = 0.35 if pata == "Mao" else 0.60                        # calcanhar traseiro: transicao mais longa (joelho dobra muito ao sentar)
            if p.z > j.z + alc or math.hypot(p.x - j.x, p.y - j.y) > 1.7: continue
            wl = next((g.weight for g in v.groups if g.group == gL.index), 0.0)
            if wl <= 1e-4: continue
            f = suave((j.z + alc - p.z) / (0.6 if pata == "Mao" else 0.75))
            if f <= 1e-3: continue
            wp = next((g.weight for g in v.groups if g.group == gP.index), 0.0)
            gL.add([v.index], wl * (1 - f), "REPLACE"); gP.add([v.index], wp + wl * f, "REPLACE"); pata_mov += 1
print("PESOS sola->pata: verts ajustados", pata_mov)
# REVISAO 03/11: canto da boca e garganta: fracao mandibula/(mandibula+cabeca) suavizada pelas arestas (transicao gradual),
# so atras da comissura (os labios da frente ficam separados pela fenda e nao mudam).
adj = {}
for e in me.edges:
    a_, b_ = e.vertices; adj.setdefault(a_, []).append(b_); adj.setdefault(b_, []).append(a_)
reg = [v.index for v in me.vertices if -5.45 < v.co.y < -4.00 and v.co.z < 6.75 and abs(v.co.x) < 1.10]
def wget(i, g): return next((gg.weight for gg in me.vertices[i].groups if gg.group == g.index), 0.0)
frac = {}; tot = {}
for i in reg:
    wm, wc = wget(i, gM), wget(i, gC); s = wm + wc
    if s > 1e-4: frac[i] = wm / s; tot[i] = s
for _ in range(40):
    novo = {}
    for i in frac:
        viz = [frac[j] for j in adj.get(i, []) if j in frac]
        novo[i] = (frac[i] + sum(viz)) / (1 + len(viz)) if viz else frac[i]
    frac = novo
for i, m in frac.items(): gM.add([i], tot[i] * m, "REPLACE"); gC.add([i], tot[i] * (1 - m), "REPLACE")
print("PESOS boca: verts com transicao gradual", len(frac))
# REVISAO 03/11: base das orelhas suavizada pelas arestas (arestas curtas esticavam > 3x ao girar a orelha)
for lado in ("E", "D"):
    gO = grupo("Orelha" + lado); base = ORE[lado] - V((0, 0, 0.38))
    zona = [v.index for v in me.vertices if (v.co - ORE[lado]).length < 0.75 and v.co.y < -3.95]
    wo = {i: wget(i, gO) for i in zona}
    for _ in range(12):
        wo = {i: (wo[i] + sum(wo[j] for j in adj.get(i, []) if j in wo)) / (1 + sum(1 for j in adj.get(i, []) if j in wo)) for i in wo}
    for i, w_ in wo.items():
        antes = wget(i, gO); delta = w_ - antes
        if abs(delta) < 1e-4: continue
        gO.add([i], max(0.0, w_), "REPLACE")
        if delta > 0: gC.add([i], max(0.0, wget(i, gC) - delta), "REPLACE")          # o que a orelha ganha sai da cabeca
print("PESOS orelhas suavizadas")
# REVISAO 03/11: transicao cabeca x pescoco no alto do cranio (arestas curtas esticavam > 3x ao girar a cabeca)
GN = [grupo(n_) for n_ in ("Cabeca", "Pescoco2", "Pescoco")]
zona = [v.index for v in me.vertices if -5.35 < v.co.y < -3.4 and v.co.z > 6.3]
fr_ = {}; tt_ = {}
for i in zona:
    ws = [wget(i, g) for g in GN]; s = sum(ws)
    if s > 1e-4: fr_[i] = [w_ / s for w_ in ws]; tt_[i] = s
for _ in range(15):
    novo = {}
    for i, fv in fr_.items():
        viz = [fr_[j] for j in adj.get(i, []) if j in fr_]
        novo[i] = [(fv[c] + sum(x[c] for x in viz)) / (1 + len(viz)) for c in range(3)]
    fr_ = novo
for i, fv in fr_.items():
    for g, x in zip(GN, fv): g.add([i], tt_[i] * x, "REPLACE")
print("PESOS cabeca/pescoco suavizados", len(fr_))
bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
# pecas da boca: rigidas (mand = 1 -> Mandibula, senao Cabeca)
am = BOCA.data.attributes["mand"]
for nm in ("Cabeca", "Mandibula"): BOCA.vertex_groups.new(name=nm)
for i, v in enumerate(BOCA.data.vertices):
    BOCA.vertex_groups["Mandibula" if am.data[i].value > 0.5 else "Cabeca"].add([i], 1.0, "REPLACE")
ativar(BOCA); arm.select_set(True); bpy.context.view_layer.objects.active = arm; bpy.ops.object.parent_set(type="ARMATURE_NAME")
for g in list(BOCA.vertex_groups):                              # ARMATURE_NAME cria grupos vazios para todos os ossos
    if g.name not in ("Cabeca", "Mandibula"): BOCA.vertex_groups.remove(g)

# ------------------------------------------------------------------ separa de novo em MeshParts (cabeca / corpo frente / corpo tras)
antes = set(sc.objects)
ativar(PELE); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.separate(type="MATERIAL")
bpy.ops.object.mode_set(mode="OBJECT")
partes_ = [o for o in sc.objects if o.type == "MESH" and (o is PELE or o not in antes)]
def mat_de(o): return o.data.materials[o.data.polygons[0].material_index].name
cab = next(o for o in partes_ if mat_de(o) == "M_Urso_Cabeca"); corpo = next(o for o in partes_ if mat_de(o) == "M_Urso_Corpo")
ys = sorted(p.center.y for p in corpo.data.polygons); corte = ys[len(ys) // 2]
ativar(corpo); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="DESELECT"); bpy.ops.object.mode_set(mode="OBJECT")
antes = set(sc.objects)
bmc = bmesh.new(); bmc.from_mesh(corpo.data); bmc.faces.ensure_lookup_table()
for f_ in bmc.faces: f_.select_set(f_.calc_center_median().y > corte)
bmc.select_flush_mode(); bmc.to_mesh(corpo.data); bmc.free()
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_mode(type="FACE"); bpy.ops.mesh.separate(type="SELECTED"); bpy.ops.object.mode_set(mode="OBJECT")
tras = next(o for o in sc.objects if o.type == "MESH" and o not in antes)
for o, nome in ((cab, "Urso_Cabeca"), (corpo, "Urso_Corpo_Frente"), (tras, "Urso_Corpo_Tras")):
    o.name = o.data.name = nome
    for m_ in list(o.data.materials):                         # so o material usado
        pass
    used = {p.material_index for p in o.data.polygons}
    for idx in sorted(range(len(o.data.materials)), reverse=True):
        if idx not in used: o.data.materials.pop(index=idx)
    for g in list(o.vertex_groups):                           # grupos vazios fora
        if not any(gg.group == g.index for v in o.data.vertices for gg in v.groups): o.vertex_groups.remove(g)
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
print("PARTES", [(o.name, tris(o), [m.name for m in o.data.materials]) for o in (cab, corpo, tras, BOCA)])
for im in list(bpy.data.images):
    if im.name.startswith("Image_"): bpy.data.images.remove(im)          # texturas 4K da malha bruta, sem uso no rig
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Urso_v2_Rig.blend"))
print("RIG_OK")
