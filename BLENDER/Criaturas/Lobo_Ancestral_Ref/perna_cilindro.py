"""Perna dianteira 100% reta: o trecho entre a pata e o cotovelo vira uma COLUNA regular. Eixo VERTICAL unico (centro
medio do trecho); em volta dele, o raio em cada direcao (16 setores, interpolados em angulo) vira uma reta em z (afinamento
suave) -> some todo calombo/dobra/desvio do centro. Medido no rig11 (medir_coluna.py): centro fugia em media 0,10 e ate
0,29 (z 1,6 e 2,6), calombos de raio ate 0,19. Pontas (pata e cotovelo) com transicao macia; mechas de pelo (Pelo*) fora.
So posicao de vertice (UV/textura/pesos intactos), simetrico; punho/pata (ossos) no eixo e IK refeito.
Uso: blender -b rig11/Lobo_Ancestral_Rig.blend -P perna_cilindro.py -- <saida_dir>"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
ZA, ZB, BORDA, NS = 0.62, 2.85, 0.28, 16
n = len(me.vertices); co = np.array([v.co[:] for v in me.vertices]); co0 = co.copy()
gi = {g.index: g.name for g in LO.vertex_groups}
viz = [[] for _ in range(n)]
for e in me.edges: a, b = e.vertices; viz[a].append(b); viz[b].append(a)
VZ = [np.array(v, int) for v in viz]
def macia(m, it):
    for _ in range(it): m = 0.5 * m + 0.5 * np.array([m[VZ[i]].mean() if len(VZ[i]) else m[i] for i in range(n)])
    return m
pelo = np.array([sum(g.weight for g in v.groups if gi[g.group].startswith("Pelo")) for v in me.vertices])
rel = {}
for lado, sx in (("E", 1), ("D", -1)):
    cad = {"Antebraco" + lado, "Mao" + lado, "Braco" + lado}
    w = np.array([sum(g.weight for g in v.groups if gi[g.group] in cad) for v in me.vertices])
    base = (w > 0.5) & (pelo < 0.3) & (co0[:, 0] * sx > 0.3) & (co0[:, 1] < -2.6) & (co0[:, 2] > ZA - BORDA) & (co0[:, 2] < ZB + BORDA)
    nucleo = base & (co0[:, 2] > ZA) & (co0[:, 2] < ZB)
    P = co0[nucleo]
    cx = float((P[:, 0].min() + P[:, 0].max()) / 2); cy = float(np.median([(P[np.abs(P[:, 2] - z) < 0.1, 1].min() + P[np.abs(P[:, 2] - z) < 0.1, 1].max()) / 2
                                                                         for z in np.arange(ZA + 0.1, ZB, 0.2) if (np.abs(P[:, 2] - z) < 0.1).sum() >= 3]))
    cxs = [(P[np.abs(P[:, 2] - z) < 0.1, 0].min() + P[np.abs(P[:, 2] - z) < 0.1, 0].max()) / 2 for z in np.arange(ZA + 0.1, ZB, 0.2) if (np.abs(P[:, 2] - z) < 0.1).sum() >= 3]
    cx = float(np.median(cxs))
    ang = np.arctan2(co0[:, 1] - cy, co0[:, 0] - cx); r = np.hypot(co0[:, 0] - cx, co0[:, 1] - cy)
    # reta r(z) por setor (minimos quadrados nos vertices do nucleo); setores vazios herdam do vizinho
    sa = ((ang[nucleo] + math.pi) / (2 * math.pi) * NS) % NS
    coef = [None] * NS
    for k in range(NS):
        d = np.minimum(np.abs(sa - (k + 0.5)), NS - np.abs(sa - (k + 0.5))); s = d < 1.0
        if s.sum() >= 4: coef[k] = np.polyfit(co0[nucleo][s, 2], r[nucleo][s], 1)
    for _ in range(NS):
        for k in range(NS):
            if coef[k] is None:
                vz = [coef[(k - 1) % NS], coef[(k + 1) % NS]]; vz = [c for c in vz if c is not None]
                if vz: coef[k] = np.mean(vz, axis=0)
    C = np.array(coef)
    def r_alvo(a, z):
        u = ((a + math.pi) / (2 * math.pi) * NS - 0.5) % NS; k0 = np.floor(u).astype(int) % NS; k1 = (k0 + 1) % NS; t = u - np.floor(u)
        return (1 - t) * (C[k0, 0] * z + C[k0, 1]) + t * (C[k1, 0] * z + C[k1, 1])
    peso = macia(base.astype(float), 2) * base * suave((co0[:, 2] - (ZA - BORDA)) / BORDA) * suave(((ZB + BORDA) - co0[:, 2]) / BORDA)
    zc = np.clip(co0[:, 2], ZA, ZB)
    rn = np.maximum(r_alvo(ang, zc), 0.02)
    alvo = np.c_[cx + rn * np.cos(ang), cy + rn * np.sin(ang)]
    co[:, 0] += (alvo[:, 0] - co0[:, 0]) * peso; co[:, 1] += (alvo[:, 1] - co0[:, 1]) * peso
    rel[lado] = {"eixo_x": round(cx, 4), "eixo_y": round(cy, 4), "vertices_nucleo": int(nucleo.sum()), "vertices_movidos": int((peso > 0.01).sum())}
    print("LADO", lado, rel[lado])
me.vertices.foreach_set("co", co.ravel()); me.update()
d = np.linalg.norm(co - co0, axis=1); rel["desloc_max"] = round(float(d.max()), 3); print("DESLOC max %.3f" % d.max())
# ossos: punho no eixo; pata acompanha o deslocamento do eixo no ponto de baixo
bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); EB = arm.data.edit_bones
for s in ("E", "D"):
    p = EB["Mao" + s].head.copy(); p.x = rel[s]["eixo_x"]; p.y = rel[s]["eixo_y"]
    eb = EB["Antebraco" + s]; r_ = eb.roll; eb.tail = p; eb.roll = r_
    eb = EB["Mao" + s]; r_ = eb.roll; eb.head = p; eb.roll = r_
bpy.ops.object.mode_set(mode="OBJECT")
for s in ("E", "D"):
    b1, b2 = BD["Antebraco" + s], BD["Mao" + s]
    alvo_ = bpy.data.objects["IK_Mao" + s]; alvo_.location = b2.head_local.copy(); alvo_.rotation_mode = "QUATERNION"; alvo_.rotation_quaternion = b2.matrix_local.to_quaternion()
    bpy.data.objects["Polo_Antebraco" + s].location = b1.head_local + V((0.0, 2.5, 0.0))
bpy.context.view_layer.update()
rel["polo"] = {}
for s in ("E", "D"):
    c = arm.pose.bones["Antebraco" + s].constraints["IK"]; b0 = BD["Braco" + s]
    def erro(a_):
        c.pole_angle = a_; bpy.context.view_layer.update(); return (arm.pose.bones[b0.name].tail - b0.tail_local).length
    a_ = min((erro(math.radians(g)), math.radians(g)) for g in range(-180, 180, 3))[1]
    for passo in (1.0, 0.25, 0.05): a_ = min([a_ + math.radians(passo * q) for q in range(-4, 5)], key=erro)
    c.pole_angle = a_; rel["polo"]["Mao" + s] = [round(math.degrees(a_), 2), round(erro(a_), 5)]
dg = bpy.context.evaluated_depsgraph_get(); ev = LO.evaluated_get(dg); mm = ev.to_mesh()
ce = np.array([v.co[:] for v in mm.vertices]); ev.to_mesh_clear()
rel["desvio_repouso_ik"] = float(np.abs(ce - co).max()); print("DESVIO repouso com IK %.5f" % rel["desvio_repouso_ik"], "POLO", rel["polo"])
json.dump(rel, open(os.path.join(OUT, "perna_cilindro.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("PERNA_CILINDRO_OK")
