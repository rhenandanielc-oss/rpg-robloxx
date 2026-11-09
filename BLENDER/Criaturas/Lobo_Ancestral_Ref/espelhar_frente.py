"""Frente do Lobo Ancestral (pata dianteira E, ombro E e metade E do peitoral) refeita como ESPELHO da metade D.
Medido no rig5 (assim.py): ossos das duas patas simetricos, mas a MALHA da pata E (+X) difere do espelho da D em
0,25-0,50 por altura (pata torcida, punho/dedos virados para dentro) - a linha central por percentis (endireitar_patas)
nao enxergava isso. Aqui: ajuste nao rigido da regiao +X sobre a superficie espelhada da -X (ponto mais proximo com
normal concordante, campo de deslocamento suavizado na malha, passos parciais, mascara macia com transicao na linha
central e no flanco). So posicao de vertice: UV, textura, topologia, pesos, esqueleto e apoios intactos.
Uso: blender -b rig5/Lobo_Ancestral_Rig.blend -P espelhar_frente.py -- <saida_dir> [com_traseiras]"""
import bpy, sys, os, json
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3); co0 = co.copy()
gi = {g.index: g.name for g in LO.vertex_groups}
dono = np.array([gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else "" for v in me.vertices])
viz = [[] for _ in range(n)]
for e in me.edges: a, b = e.vertices; viz[a].append(b); viz[b].append(a)
VZ = [np.array(v, int) for v in viz]
def media_viz(f):
    return np.array([f[VZ[i]].mean(axis=0) if len(VZ[i]) else f[i] for i in range(n)])
def macia(m, it):
    m = m.astype(float)
    for _ in range(it): m = 0.5 * m + 0.5 * media_viz(m)
    return m
y_omb = BD["BracoE"].head_local.y; y_cox = BD["CoxaE"].head_local.y
CAB = np.isin(dono, ["Cabeca", "Mandibula", "OrelhaE", "OrelhaD"])
# ---------------------------------------------------------------- mascara da metade +X que sera refeita
frente = (co[:, 1] < y_omb + 1.8) & (co[:, 2] < 6.3) & ~CAB
m = frente.astype(float) * suave((y_omb + 1.8 - co[:, 1]) / 1.0) * suave((6.3 - co[:, 2]) / 0.7)
if "com_traseiras" in A:
    tras = np.isin(dono, ["CoxaE", "CanelaE", "MetatarsoE", "PeE"]) & (co[:, 2] < 3.4)
    m = np.maximum(m, tras * suave((3.4 - co[:, 2]) / 0.8))
m *= suave((co[:, 0] - 0.04) / 0.30)                       # transicao na linha central (x = 0 nao se move)
w = np.clip(macia(m, 3), 0, 1) * (co[:, 0] > 0)
mov = w > 0.01
print("vertices na mascara:", int(mov.sum()), "| w>0,9:", int((w > 0.9).sum()))
# ---------------------------------------------------------------- alvo: superficie espelhada da metade -X
me.calc_loop_triangles()
tri = np.array([t.vertices[:] for t in me.loop_triangles])
lado_d = co0[tri].mean(axis=1)[:, 0] < 0.02
esp = co0 * np.array([-1, 1, 1])
bvh = BVHTree.FromPolygons([V(p) for p in esp], [list(t[::-1]) for t in tri[lado_d]])   # ordem invertida: normal para fora
def normais(c):
    nn = np.zeros_like(c); a, b, cc = c[tri[:, 0]], c[tri[:, 1]], c[tri[:, 2]]; fn = np.cross(b - a, cc - a)
    for k in range(3): np.add.at(nn, tri[:, k], fn)
    return nn / np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-9)
def alvo(c):
    nv = normais(c); d = np.zeros_like(c); ok = np.zeros(n, bool); idx = np.nonzero(mov)[0]
    for i in idx:
        p = V(c[i]); nvi = V(nv[i]); loc, fn, fi, dist = bvh.find_nearest(p, 1.2)
        if loc is not None and fn.dot(nvi) > 0.3: d[i] = np.array(loc) - c[i]; ok[i] = True; continue
        melhor = None
        for s in (1, -1):                                  # ao longo da normal do vertice, nos dois sentidos
            h = bvh.ray_cast(p, nvi * s, 1.0)
            if h[0] is not None and h[1].dot(nvi) > 0.3 and (melhor is None or h[3] < melhor[1]): melhor = (h[0], h[3])
        if melhor: d[i] = np.array(melhor[0]) - c[i]; ok[i] = True
    return d, ok
hist = []
PASSOS = [(0.5, 8)] * 14 + [(0.7, 4)] * 6 + [(1.0, 1)] * 4
for k, (passo, it) in enumerate(PASSOS):
    d, ok = alvo(co)
    peso = ok * w; D = d * peso[:, None]; P = peso.copy()
    for _ in range(it): D = 0.5 * D + 0.5 * media_viz(D); P = 0.5 * P + 0.5 * media_viz(P)   # media ponderada pela validade
    D = D / np.maximum(P, 1e-3)[:, None] * np.clip(P / 0.25, 0, 1)[:, None]
    co = co + passo * w[:, None] * D
    r = np.linalg.norm(d[ok & (w > 0.9)], axis=1)
    hist.append([k, round(float(np.median(r)), 4), round(float(np.percentile(r, 95)), 4), int((~ok & mov).sum())])
    print("passo %2d  resid. med %.4f  p95 %.4f  sem alvo %d" % tuple(hist[-1]))
# apoios: base das patas no chao como antes
z0 = co0[:, 2] < 0.05; co[z0, 2] = co0[z0, 2]
co[:, 2] = np.where(co[:, 2] < co0[:, 2].min(), co0[:, 2].min(), co[:, 2])
desl = np.linalg.norm(co - co0, axis=1)
me.vertices.foreach_set("co", co.ravel()); me.update()
rel = {"vertices_movidos": int((desl > 0.005).sum()), "deslocamento_max": round(float(desl.max()), 3),
       "deslocamento_med_regiao": round(float(np.median(desl[w > 0.9])), 3), "historico": hist}
print("MOVIDOS", rel["vertices_movidos"], "max %.3f" % desl.max(), "mediana(w>0,9) %.3f" % rel["deslocamento_med_regiao"])
json.dump(rel, open(os.path.join(OUT, "espelhar_frente.json"), "w"), indent=1); np.save(os.path.join(OUT, "mascara_espelho.npy"), w)   # usada por espelhar_textura.py
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("ESPELHAR_FRENTE_OK")
