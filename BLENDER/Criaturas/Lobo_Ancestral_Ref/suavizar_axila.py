"""Integra peito/escapula/topo da pata dianteira: suavizacao de Taubin (lambda/mu, preserva volume - nao murcha o ombro)
so na juncao (axila, logo abaixo do peito/juba), com mascara macia. Tira o degrau/aba que faz sombra e parece um carocos
sem cortar o volume do ombro nem mexer na silhueta lateral. Simetria: o campo so depende de |x| e a topologia e espelhada.
So posicao de vertice. Uso: blender -b <rig.blend> -P suavizar_axila.py -- <saida_dir> [iteracoes]"""
import bpy, sys, os, json
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True); IT = int(A[1]) if len(A) > 1 else 10
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
yo = BD["BracoE"].head_local.y
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3); co0 = co.copy()
viz = [[] for _ in range(n)]
for e in me.edges: a, b = e.vertices; viz[a].append(b); viz[b].append(a)
VZ = [np.array(v, int) for v in viz]
ax = np.abs(co[:, 0])
# caixa da juncao: topo interno/frontal da pata ate a borda de baixo do peito
w = (suave((ax - 0.30) / 0.25) * suave((1.65 - ax) / 0.25) * suave((co[:, 2] - 3.0) / 0.35) * suave((4.45 - co[:, 2]) / 0.35)
     * suave((co[:, 1] - (yo - 1.35)) / 0.35) * suave((yo + 0.55 - co[:, 1]) / 0.35))
borda = np.array([len(v) < 3 for v in VZ])                          # vertices de borda aberta ficam
w[borda] = 0
def lap(c):
    return np.array([c[VZ[i]].mean(axis=0) - c[i] if len(VZ[i]) else np.zeros(3) for i in range(n)])
for _ in range(IT):
    co = co + 0.50 * w[:, None] * lap(co)
    co = co - 0.53 * w[:, None] * lap(co)
co[:, 0] = np.where(np.abs(co0[:, 0]) < 1e-6, 0.0, co[:, 0])          # linha central fica no plano
d = np.linalg.norm(co - co0, axis=1)
me.vertices.foreach_set("co", co.ravel()); me.update()
rel = {"iteracoes": IT, "vertices_na_mascara": int((w > 0.05).sum()), "desloc_max": round(float(d.max()), 3), "desloc_med_mascara": round(float(np.median(d[w > 0.5])), 4)}
print("SUAVIZAR_AXILA", rel)
json.dump(rel, open(os.path.join(OUT, "suavizar_axila.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("SUAVIZAR_AXILA_OK")
