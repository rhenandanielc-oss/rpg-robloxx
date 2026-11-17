"""Rig do Cerbero Sombrio (malha de jogo low_v3d do Meshy). Adaptado de Urso_Silvestre_Ref/v2/rig/rig_urso.py.
Esqueleto: Raiz (chao, nao deforma), Pelve, Coluna1-3, 3 cadeias de cabeca (Pescoco{K}1, Pescoco{K}2, Cabeca{K}, Mandibula{K};
K = C centro, E esquerda, D direita), 4 membros digitigrados (Escapula/Braco/Antebraco/Mao/Dedos; Coxa/Canela/Pe/DedosPe) e Cauda1-3.
Nomes ja sao os do jogo (o Roblox liga malha a osso pelo NOME; nao renomear no Studio).
Escala: a malha de trabalho do Meshy (cernelha ~1,1 u) e multiplicada por ESC (PROPOSTA: 12,7 -> ~14 studs de ombro; oficial 12-16).
Pesos: heat num PROXY fechado (voxel) transferido para a pele; cranio x mandibula pela linha dos labios de cada cabeca (a mesma da
boca, medida na v3d); cranio/mandibula de uma cabeca nao vazam para as outras; barriga entre as patas na coluna; sola -> pata;
pecas da boca rigidas pelos atributos "mand"/"cabeca". Maximo de 4 influencias por vertice (Roblox).
Uso: blender -b -t 4 ../low_v3d/CR_Cerbero_Sombrio_LOW.blend -P rig_cerbero.py -- <saida_dir> [esc=12.7]"""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.kdtree import KDTree
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
def arg(n, d): return type(d)(next((a.split("=")[1] for a in ARGS if a.startswith(n + "=")), d))
ESC = arg("esc", 12.7)
sc = bpy.context.scene
sc.render.threads_mode = "FIXED"; sc.render.threads = 4
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def ativar(o):
    for x in sc.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
for o in list(sc.objects):                                   # malha bruta (fonte do bake), cameras e luz nao vao para o rig
    if o.name.startswith("CR_Cerbero_Meshy") or o.type in ("CAMERA", "LIGHT"): bpy.data.objects.remove(o)
CABM, CORPO, BOCA = (bpy.data.objects[n] for n in ("Cerbero_Cabecas", "Cerbero_Corpo", "Cerbero_Bocas"))
for o in (CABM, CORPO, BOCA):                                # escala de jogo aplicada na malha
    o.data.transform(Matrix.Scale(ESC, 4)); o.matrix_world = Matrix()

# ------------------------------------------------------------------ cabecas (referencial da v3d: T, f e linha dos labios)
REL = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "relatorio_low.json"), encoding="utf-8"))
CABS = {"C": ((-0.0103, -0.951, 1.3438), (0.1072, -0.9942)), "E": ((-0.4798, -0.8523, 1.1428), (-0.5549, -0.8319)),
        "D": ((0.5103, -0.7272, 1.1808), (0.8968, -0.4424))}          # CENTRO da v3d (low_v3d.log)
ORDEM = ["C", "E", "D"]
class Cab:
    def __init__(s_, k):
        t, f = CABS[k]; s_.k = k; s_.T = V(t) * ESC; s_.f = V((f[0], f[1], 0)).normalized(); s_.s = s_.f.cross(V((0, 0, 1))).normalized()
        s_.z = V((0, 0, 1)); lab = REL["labios"][k]
        s_.LAB = [(a * ESC, h * ESC) for a, h in lab["linha"]]; s_.L = lab["L"] * ESC; s_.HW = lab["meia_largura"] * ESC
        s_.CANTO, s_.FRENTE = s_.LAB[0][0], s_.LAB[-1][0]
    def P(s_, a, l, h): return s_.T + s_.f * a + s_.s * l + s_.z * h
    def loc(s_, p): r = V(p) - s_.T; return r.dot(s_.f), r.dot(s_.s), r.dot(s_.z)
    def lip(s_, a):
        L = s_.LAB
        if a <= L[0][0]: return L[0][1]
        for (a0, h0), (a1, h1) in zip(L, L[1:]):
            if a0 <= a <= a1: return lerp(h0, h1, (a - a0) / (a1 - a0))
        return L[-1][1]
CB = {k: Cab(k) for k in ORDEM}

# ------------------------------------------------------------------ pele unida (pesos consistentes nas costuras)
ativar(CABM); CORPO.select_set(True); bpy.ops.object.join(); PELE = bpy.context.object; PELE.name = "tmp_Pele"
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.remove_doubles(threshold=1e-4 * ESC)
bpy.ops.object.mode_set(mode="OBJECT")
for g in list(PELE.vertex_groups): PELE.vertex_groups.remove(g)
me = PELE.data; n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
x, y, z = co[:, 0], co[:, 1], co[:, 2]; Y0, Y1 = y.min(), y.max()
print("PELE verts", n, "y", round(Y0, 2), round(Y1, 2), "zmax", round(z.max(), 2))

# ------------------------------------------------------------------ marcos (fracoes da altura de cernelha H)
H = 1.10 * ESC
def pe_de(sx, dian):
    s = (z < 0.055 * ESC) & (x * sx > 0.05 * ESC) & ((y < 0.15 * ESC) if dian else (y >= 0.15 * ESC)); return V(co[s].mean(axis=0))
def fatia(pe, zz, sx, raio=0.13, faixa=0.035):
    s = (np.abs(z - zz) < faixa * ESC) & (np.abs(x - pe.x) < raio * ESC) & (np.abs(y - pe.y) < 0.2 * ESC) & (x * sx > 0.08 * ESC)
    return V(co[s].mean(axis=0)) if s.sum() > 8 else V((pe.x, pe.y, zz))
def centro(yy, faixa=0.05, ztopo=None):
    s = (np.abs(y - yy) < faixa * ESC) & (np.abs(x + 0.045 * ESC) < 0.12 * ESC)
    if ztopo is not None: s &= z < ztopo
    return V((-0.045 * ESC, yy, (z[s].min() + z[s].max()) / 2)) if s.any() else V((-0.045 * ESC, yy, 0.8 * ESC))
PES = {(l, d): pe_de(sx, d) for l, sx in (("E", -1), ("D", 1)) for d in (True, False)}   # lado E = -x (como as cabecas)
y_omb = (PES[("E", True)].y + PES[("D", True)].y) / 2 + 0.11 * ESC        # ombro ~ atras da pata dianteira
y_quad = (PES[("E", False)].y + PES[("D", False)].y) / 2 - 0.10 * ESC     # quadril ~ a frente da pata traseira
y_meio = (y_omb + y_quad) / 2
print("PES", {k: tuple(round(c, 2) for c in v) for k, v in PES.items()}, "y_omb", round(y_omb, 2), "y_quad", round(y_quad, 2))

# ------------------------------------------------------------------ esqueleto
arm_d = bpy.data.armatures.new("Cerbero_Rig"); arm = bpy.data.objects.new("Cerbero_Rig", arm_d); sc.collection.objects.link(arm)
ativar(arm); bpy.ops.object.mode_set(mode="EDIT"); E = arm_d.edit_bones
def osso(nome, a, b, pai=None, conecta=True):
    o = E.new(nome); o.head = a; o.tail = b
    if pai: o.parent = E[pai]; o.use_connect = conecta and (E[pai].tail - V(a)).length < 1e-4
    return o
ZC = 0.80 * ESC                                                         # altura da coluna (meio do tronco, abaixo das placas)
osso("Raiz", V((-0.045 * ESC, y_meio, 0)), V((-0.045 * ESC, y_meio - 0.15 * ESC, 0)))
cp = lambda yy, dz=0.0: V((-0.045 * ESC, yy, ZC + dz))
osso("Pelve", cp(y_quad + 0.10 * ESC, 0.02 * ESC), cp(y_quad - 0.06 * ESC), "Raiz", False)
osso("Coluna1", E["Pelve"].tail, cp(y_meio), "Pelve")
osso("Coluna2", E["Coluna1"].tail, cp(y_omb + 0.08 * ESC, 0.04 * ESC), "Coluna1")
osso("Coluna3", E["Coluna2"].tail, cp(y_omb - 0.12 * ESC, 0.10 * ESC), "Coluna2")       # cintura escapular (raiz dos 3 pescocos)
RAIZ_P = {"C": V((-0.03, -0.46, 1.02)), "E": V((-0.17, -0.47, 0.98)), "D": V((0.10, -0.47, 0.98))}
for k, c in CB.items():
    piv = c.P(-0.85 * c.L - 0.02 * ESC, 0, 0.02 * ESC)                  # atlas: atras do cranio, na altura dos olhos
    r0 = RAIZ_P[k] * ESC; mid = (r0 + piv) / 2 + V((0, 0, 0.03 * ESC)) - c.f * 0.02 * ESC
    osso("Pescoco%s1" % k, r0, mid, "Coluna3", False); osso("Pescoco%s2" % k, mid, piv, "Pescoco%s1" % k)
    osso("Cabeca" + k, piv, c.P(-0.05 * c.L, 0, 0.0), "Pescoco%s2" % k)
    osso("Mandibula" + k, c.P(c.CANTO - 0.08 * c.L, 0, c.lip(c.CANTO) + 0.02 * c.L),
         c.P(c.FRENTE - 0.05 * c.L, 0, c.lip(c.FRENTE) - 0.20 * c.L), "Cabeca" + k, False)
# cauda: centroide de fatias atras da garupa
def cauda_pt(yy):
    s = (np.abs(y - yy) < 0.04 * ESC) & (z > 0.45 * ESC) & (np.abs(x + 0.04 * ESC) < 0.2 * ESC)
    return V(co[s].mean(axis=0)) if s.sum() > 5 else V((-0.04 * ESC, yy, 0.75 * ESC))
cy = [0.62, 0.72, 0.82, 0.92]
osso("Cauda1", cauda_pt(cy[0] * ESC), cauda_pt(cy[1] * ESC), "Pelve", False)
osso("Cauda2", E["Cauda1"].tail, cauda_pt(cy[2] * ESC), "Cauda1"); osso("Cauda3", E["Cauda2"].tail, cauda_pt(cy[3] * ESC), "Cauda2")
PATA = {}
for lado, sx in (("E", -1), ("D", 1)):
    pe = PES[(lado, True)]                                              # dianteira digitigrada
    omb = fatia(pe, 0.74 * ESC, sx); cot = fatia(pe, 0.46 * ESC, sx) + V((0, 0.03 * ESC, 0)); pun = fatia(pe, 0.16 * ESC, sx)
    mao = V((pe.x, pe.y - 0.01 * ESC, 0.045 * ESC)); ponta = V((pe.x, pe.y - 0.09 * ESC, 0.025 * ESC))
    esc = V((omb.x * 0.55 - 0.02 * ESC, omb.y + 0.08 * ESC, 1.0 * ESC))
    osso("Escapula" + lado, esc, omb, "Coluna3", False)
    osso("Braco" + lado, omb, cot, "Escapula" + lado); osso("Antebraco" + lado, cot, pun, "Braco" + lado)
    osso("Mao" + lado, pun, mao, "Antebraco" + lado); osso("Dedos" + lado, mao, ponta, "Mao" + lado)
    pe = PES[(lado, False)]                                             # traseira: joelho a frente, jarrete atras
    qua = V((pe.x * 0.9, y_quad + 0.02 * ESC, 0.76 * ESC)); joe = fatia(pe, 0.45 * ESC, sx) + V((0, -0.03 * ESC, 0))
    jar = fatia(pe, 0.18 * ESC, sx) + V((0, 0.03 * ESC, 0)); pep = V((pe.x, pe.y + 0.01 * ESC, 0.045 * ESC))
    ponta = V((pe.x, pe.y - 0.08 * ESC, 0.025 * ESC))
    osso("Coxa" + lado, qua, joe, "Pelve", False); osso("Canela" + lado, joe, jar, "Coxa" + lado)
    osso("Pe" + lado, jar, pep, "Canela" + lado); osso("DedosPe" + lado, pep, ponta, "Pe" + lado)
for b in E: b.roll = 0.0
bpy.ops.object.mode_set(mode="OBJECT")
print("OSSOS", len(arm_d.bones), [b.name for b in arm_d.bones], flush=True)

# ------------------------------------------------------------------ pesos: heat num PROXY fechado -> transferencia para a pele
prox = PELE.copy(); prox.data = PELE.data.copy(); prox.name = "tmp_Proxy"; sc.collection.objects.link(prox)
arm.data.bones["Raiz"].use_deform = False
ativar(prox); rmp = prox.modifiers.new("R", "REMESH"); rmp.mode = "VOXEL"; rmp.voxel_size = arg("voxproxy", 0.012) * ESC
bpy.ops.object.modifier_apply(modifier=rmp.name)
smp = prox.modifiers.new("S", "SMOOTH"); smp.factor = 0.5; smp.iterations = 3; bpy.ops.object.modifier_apply(modifier=smp.name)
ativar(prox); arm.select_set(True); bpy.context.view_layer.objects.active = arm
try: bpy.ops.object.parent_set(type="ARMATURE_AUTO")
except Exception as e: print("HEAT proxy erro:", e)
sem_p = sum(1 for v in prox.data.vertices if not v.groups); print("PESOS heat no proxy: verts", len(prox.data.vertices), "sem peso", sem_p, flush=True)
if sem_p > len(prox.data.vertices) * 0.02:
    for g in list(prox.vertex_groups): prox.vertex_groups.remove(g)
    segs = [(b.name, b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones if b.name != "Raiz"]
    gs = {nm: prox.vertex_groups.new(name=nm) for nm, _, _ in segs}
    def dseg(p, a_, b_):
        ab = b_ - a_; t_ = max(0.0, min(1.0, (p - a_).dot(ab) / max(ab.length_squared, 1e-9))); return (p - (a_ + ab * t_)).length
    for v in prox.data.vertices:
        ds = sorted((dseg(v.co, a_, b_), nm) for nm, a_, b_ in segs)[:4]; ws = [1.0 / max(d, 0.05) ** 4 for d, _ in ds]; tot = sum(ws)
        for (d, nm), w_ in zip(ds, ws): gs[nm].add([v.index], w_ / tot, "REPLACE")
    print("PESOS reserva: distancia aos ossos")
for g in prox.vertex_groups: PELE.vertex_groups.new(name=g.name)
ativar(PELE); dt = PELE.modifiers.new("DT", "DATA_TRANSFER"); dt.object = prox; dt.use_vert_data = True
dt.data_types_verts = {"VGROUP_WEIGHTS"}; dt.vert_mapping = "POLYINTERP_NEAREST"; dt.layers_vgroup_select_src = "ALL"; dt.layers_vgroup_select_dst = "NAME"
bpy.ops.object.modifier_apply(modifier=dt.name)
bpy.data.objects.remove(prox)
ativar(PELE); arm.select_set(True); bpy.context.view_layer.objects.active = arm; bpy.ops.object.parent_set(type="ARMATURE_NAME")
vazios = [v.index for v in me.vertices if not v.groups or max(g.weight for g in v.groups) < 1e-3]
sv = set(vazios); cheios = [v.index for v in me.vertices if v.index not in sv]
kd = KDTree(len(cheios))
for i in cheios: kd.insert(me.vertices[i].co, i)
kd.balance()
for i in vazios:
    _, j, _ = kd.find(me.vertices[i].co)
    for g in me.vertices[j].groups: PELE.vertex_groups[g.group].add([i], g.weight, "REPLACE")
print("PESOS na pele: verts sem peso", len(vazios), "-> herdados do vizinho", flush=True)
G = {g.name: g for g in PELE.vertex_groups}
def grupo(nome): return G.setdefault(nome, PELE.vertex_groups.get(nome) or PELE.vertex_groups.new(name=nome))
def wget(i, g): return next((gg.weight for gg in me.vertices[i].groups if gg.group == g.index), 0.0)
adj = {}
for e in me.edges:
    a_, b_ = e.vertices; adj.setdefault(a_, []).append(b_); adj.setdefault(b_, []).append(a_)

# cabeca de cada vertice: a mais proxima pelo segmento cranio (piv -> focinho)
def dseg(p, a_, b_):
    ab = b_ - a_; t_ = max(0.0, min(1.0, (p - a_).dot(ab) / max(ab.length_squared, 1e-9))); return (p - (a_ + ab * t_)).length
SEG = {k: (arm.data.bones["Cabeca" + k].head_local.copy(), arm.data.bones["Cabeca" + k].tail_local.copy()) for k in ORDEM}
def cab_de(p): return min(ORDEM, key=lambda k: dseg(p, *SEG[k]))
# 1) cranio/mandibula de outra cabeca nao vazam (o heat espalhava na juba)
CRAN = {k: ("Cabeca" + k, "Mandibula" + k) for k in ORDEM}
viz_cab = 0
for v in me.vertices:
    k = cab_de(v.co)
    for g in list(v.groups):
        nm = PELE.vertex_groups[g.group].name
        if any(nm in CRAN[j] for j in ORDEM if j != k) and g.weight > 0:
            PELE.vertex_groups[g.group].remove([v.index]); viz_cab += 1
print("PESOS cranio de outra cabeca removidos", viz_cab, flush=True)
# 2) cranio x mandibula pela linha dos labios (metodo do urso, em fracoes do focinho L)
def w_mand(c, p, nz=0.0):
    a, l, h = c.loc(p)
    if abs(l) > c.HW * 1.9: return 0.0
    YJ = c.CANTO - 0.45 * c.L                                            # fim da mandibula atras da comissura
    if a < YJ: return 0.0
    if a > c.CANTO:
        # r2: a fenda e muito fina, os dois labios ficam a +-0,0003 da linha. A normal decide o lado: face de cima do labio
        # inferior (normal para cima) = mandibula; face de baixo do labio superior (normal para baixo) = cranio.
        return suave(((c.lip(a) - h) + 0.03 * c.L * nz) / (0.02 * c.L) + 0.5)
    return suave((c.lip(c.CANTO) - 0.03 * c.L - h) / (0.30 * c.L)) * suave((a - YJ) / (c.CANTO - YJ))
# r2: pontes que a fenda nao cortou na frente da boca (a tira esticava ate 196x ao abrir): faces da zona dos labios com
# vertices dos dois lados (cranio x mandibula) sao retiradas. Atras da comissura (+0,15 L) nada muda.
bmp = bmesh.new(); bmp.from_mesh(me); bmp.verts.ensure_lookup_table(); bmp.normal_update()
def lado_v(v_):
    k_ = cab_de(v_.co); c_ = CB[k_]; a_, l_, h_ = c_.loc(v_.co)
    if a_ < c_.CANTO + 0.15 * c_.L or abs(l_) > 0.8 * c_.HW or abs(h_ - c_.lip(a_)) > 0.06 * c_.L: return None
    return (k_, w_mand(c_, v_.co, v_.normal.z) >= 0.5)
LADO = {v_.index: lado_v(v_) for v_ in bmp.verts}
pontes = [f_ for f_ in bmp.faces if all(LADO[v_.index] is not None for v_ in f_.verts)
          and len({LADO[v_.index] for v_ in f_.verts}) > 1 and len({LADO[v_.index][0] for v_ in f_.verts}) == 1]
print("PONTES retiradas na frente das bocas", len(pontes), sorted({LADO[f_.verts[0].index][0] for f_ in pontes}), flush=True)
bmesh.ops.delete(bmp, geom=pontes, context="FACES"); bmp.to_mesh(me); bmp.free(); me.update()
adj = {}                                                              # vizinhanca refeita (indices mudaram)
for e in me.edges:
    a_, b_ = e.vertices; adj.setdefault(a_, []).append(b_); adj.setdefault(b_, []).append(a_)
for v in me.vertices:
    k = cab_de(v.co); c = CB[k]; a, l, h = c.loc(v.co)
    if a < c.CANTO - 1.0 * c.L or dseg(v.co, *SEG[k]) > 0.9 * c.L: continue
    gC, gM = grupo("Cabeca" + k), grupo("Mandibula" + k); wm = w_mand(c, v.co, v.normal.z)
    if a > c.CANTO - 0.25 * c.L:                                         # focinho e rosto: so cranio/mandibula
        for g in list(v.groups): PELE.vertex_groups[g.group].remove([v.index])
        gC.add([v.index], 1.0 - wm, "REPLACE")
        if wm > 1e-3: gM.add([v.index], wm, "REPLACE")
    elif wm > 1e-3:
        gM.add([v.index], wm, "REPLACE")
# 3) barriga e peito por baixo, entre as patas: peso das pernas passa para a coluna
PERNA = ("Braco", "Antebraco", "Coxa", "Canela")
def coluna_de(yy): return "Pelve" if yy > y_quad - 0.08 * ESC else ("Coluna1" if yy > y_meio else ("Coluna2" if yy > y_omb else "Coluna3"))
for v in me.vertices:
    p = v.co
    if not (y_omb - 0.12 * ESC < p.y < y_quad + 0.12 * ESC and p.z < 0.62 * ESC): continue
    k_ = suave((0.13 * ESC - abs(p.x + 0.045 * ESC)) / (0.06 * ESC)) * suave((0.62 * ESC - p.z) / (0.08 * ESC))
    if k_ < 1e-3: continue
    mov = 0.0
    for g in list(v.groups):
        nm = PELE.vertex_groups[g.group].name
        if nm.startswith(PERNA):
            tira = g.weight * k_; mov += tira; PELE.vertex_groups[g.group].add([v.index], g.weight - tira, "REPLACE")
    if mov > 0:
        gc_ = grupo(coluna_de(p.y)); gc_.add([v.index], wget(v.index, gc_) + mov, "REPLACE")
# 4) suavizacao geral preservando cranio x mandibula
ativar(PELE)
for g in PELE.vertex_groups: g.lock_weight = g.name.startswith(("Cabeca", "Mandibula"))
bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=0.6, repeat=4, expand=0.0)
bpy.ops.object.mode_set(mode="OBJECT")
for g in PELE.vertex_groups: g.lock_weight = False
# 5) sola segue a pata (Mao/Pe) em degrade a partir do punho/jarrete
pata_mov = 0
for lado in ("E", "D"):
    for pata, perna_, alc in (("Mao", "Antebraco", 0.05), ("Pe", "Canela", 0.08)):
        gP, gL = grupo(pata + lado), grupo(perna_ + lado); j = arm.data.bones[pata + lado].head_local
        for v in me.vertices:
            p = v.co
            if p.z > j.z + alc * ESC or math.hypot(p.x - j.x, p.y - j.y) > 0.16 * ESC: continue
            wl = wget(v.index, gL)
            if wl <= 1e-4: continue
            f = suave((j.z + alc * ESC - p.z) / (0.07 * ESC))
            if f <= 1e-3: continue
            gL.add([v.index], wl * (1 - f), "REPLACE"); gP.add([v.index], wget(v.index, gP) + wl * f, "REPLACE"); pata_mov += 1
print("PESOS sola->pata", pata_mov, flush=True)
# 6) canto da boca e garganta: fracao mandibula/(mandibula+cranio) suavizada pelas arestas, so atras da comissura
for k, c in CB.items():
    gM, gC = grupo("Mandibula" + k), grupo("Cabeca" + k)
    reg = [v.index for v in me.vertices if cab_de(v.co) == k and c.CANTO - 0.9 * c.L < c.loc(v.co)[0] < c.CANTO + 0.15 * c.L]
    frac = {}; tot = {}
    for i in reg:
        wm, wc = wget(i, gM), wget(i, gC); s = wm + wc
        if s > 1e-4: frac[i] = wm / s; tot[i] = s
    for _ in range(30):
        frac = {i: (f_ + sum(frac[j] for j in adj.get(i, []) if j in frac)) / (1 + sum(1 for j in adj.get(i, []) if j in frac)) for i, f_ in frac.items()}
    for i, m in frac.items(): gM.add([i], tot[i] * m, "REPLACE"); gC.add([i], tot[i] * (1 - m), "REPLACE")
    # nuca: cranio x pescoco suavizados (arestas curtas esticavam ao girar a cabeca)
    GN = [grupo("Cabeca" + k), grupo("Pescoco%s2" % k), grupo("Pescoco%s1" % k)]
    zona = [v.index for v in me.vertices if cab_de(v.co) == k and -1.6 * c.L < c.loc(v.co)[0] < -0.5 * c.L]
    fr_ = {}; tt_ = {}
    for i in zona:
        ws = [wget(i, g) for g in GN]; s = sum(ws)
        if s > 1e-4: fr_[i] = [w_ / s for w_ in ws]; tt_[i] = s
    for _ in range(12):
        fr_ = {i: [(fv[c_] + sum(fr_[j][c_] for j in adj.get(i, []) if j in fr_)) / (1 + sum(1 for j in adj.get(i, []) if j in fr_)) for c_ in range(3)] for i, fv in fr_.items()}
    for i, fv in fr_.items():
        for g, x_ in zip(GN, fv): g.add([i], tt_[i] * x_, "REPLACE")
    print("PESOS boca/nuca", k, len(frac), len(fr_), flush=True)
bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
# pecas da boca: rigidas (mand = 1 -> Mandibula{K}, senao Cabeca{K})
am, ac = BOCA.data.attributes["mand"], BOCA.data.attributes["cabeca"]
for k in ORDEM:
    for nm in ("Cabeca" + k, "Mandibula" + k): BOCA.vertex_groups.new(name=nm)
for i in range(len(BOCA.data.vertices)):
    k = ORDEM[ac.data[i].value]; BOCA.vertex_groups[("Mandibula" if am.data[i].value > 0.5 else "Cabeca") + k].add([i], 1.0, "REPLACE")
ativar(BOCA); arm.select_set(True); bpy.context.view_layer.objects.active = arm; bpy.ops.object.parent_set(type="ARMATURE_NAME")
for g in list(BOCA.vertex_groups):
    if not g.name.startswith(("Cabeca", "Mandibula")): BOCA.vertex_groups.remove(g)

# ------------------------------------------------------------------ separa de novo em MeshParts (Cabecas / Corpo) pelo material
antes = set(sc.objects)
ativar(PELE); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.separate(type="MATERIAL")
bpy.ops.object.mode_set(mode="OBJECT")
partes = [o for o in sc.objects if o.type == "MESH" and (o is PELE or o not in antes)]
def mat_de(o): return o.data.materials[o.data.polygons[0].material_index].name
for o in partes:
    nome = "Cerbero_Cabecas" if mat_de(o) == "M_Cerbero_Cabecas" else "Cerbero_Corpo"; o.name = o.data.name = nome
    used = {p.material_index for p in o.data.polygons}
    for idx in sorted(range(len(o.data.materials)), reverse=True):
        if idx not in used: o.data.materials.pop(index=idx)
    usados = {o.vertex_groups[gg.group].name for v in o.data.vertices for gg in v.groups if gg.weight > 0}
    for nm in [g.name for g in o.vertex_groups if g.name not in usados]: o.vertex_groups.remove(o.vertex_groups[nm])   # por nome (indices mudam)
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
print("PARTES", [(o.name, tris(o), len(o.vertex_groups)) for o in partes + [BOCA]], flush=True)
for im in list(bpy.data.images):
    if im.name.startswith("Image_"): bpy.data.images.remove(im)
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cerbero_Rig.blend"))
print("RIG_OK", flush=True)
