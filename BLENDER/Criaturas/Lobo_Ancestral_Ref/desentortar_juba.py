"""Correcao localizada da leitura frontal da juba/peito do Lobo Ancestral (malha de jogo do rig2, em repouso): a juba
tem o centro deslocado em sentidos opostos por altura (alto para -X, baixo do peito para +X) -> "cisalhamento" que se le
como mechas descendo em diagonal. Aplica so na regiao JUBA/PEITO (mascara macia, so a frente dos ombros) um campo de
deslocamento LATERAL suave dx(z) = -centro(z), com centro robusto (media dos percentis 15 e 85) e curva suavizada.
Sem projecao, sem bake: UV, textura, topologia, pesos e esqueleto intactos (a textura acompanha a superficie).
Cabeca/rosto e corpo nao mudam. v1 (espelhamento + bake) foi descartada: dobrava a malha e manchava a textura.
Uso: blender -b rig2/Lobo_Ancestral_Rig.blend -P desentortar_juba.py -- <saida_dir> [ganho=1.0]"""
import bpy, sys, os, json
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
GANHO = float(A[1]) if len(A) > 1 else 1.0
GIRO = float(A[2]) if len(A) > 2 else 0.0                  # graus: giro local da juba no plano frontal (direcao das mechas)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
gi = {g.index: g.name for g in LO.vertex_groups}
def dono(v): return gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else ""
JUB = {"JubaE", "JubaD", "JubaPeito", "Pescoco1", "Pescoco2", "Peito"}
y_omb = arm.data.bones["BracoE"].head_local.y
reg = np.array([1.0 if (dono(v) in JUB and v.co.y < y_omb + 0.5 and v.co.z > 3.4) else 0.0 for v in me.vertices])
viz = [[] for _ in range(n)]
for e in me.edges: a, b = e.vertices; viz[a].append(b); viz[b].append(a)
m = reg.copy()
for _ in range(8):
    m = np.array([0.5 * m[i] + 0.5 * (m[viz[i]].mean() if viz[i] else m[i]) for i in range(n)])
m = np.clip(m * 1.5, 0, 1)
if GIRO:                                                     # giro em torno do eixo Y que passa pelo centro do peito, so na mascara
    sel = reg > 0; zc_ = float(np.median(co[sel, 2])); a = np.radians(GIRO) * m * (1 - suave((co[:, 2] - 6.2) / 1.0))   # so o peito (a juba alta atras da cabeca nao gira)
    x0, z0 = co[:, 0].copy(), co[:, 2] - zc_
    co[:, 0] = x0 * np.cos(a) + z0 * np.sin(a); co[:, 2] = zc_ - x0 * np.sin(a) + z0 * np.cos(a)
    print("GIRO %.1f graus em torno de z %.2f" % (GIRO, zc_))
# 1o o giro (direcao das mechas), depois o centro por altura e medido e recentrado (posicao)
# centro robusto por altura (so a regiao)
zs = np.arange(3.2, 7.8, 0.2); cz = []
for z0 in zs:
    s = (reg > 0) & (np.abs(co[:, 2] - z0) < 0.25)
    if s.sum() > 25:
        p15, p85 = np.percentile(co[s, 0], [15, 85]); cz.append((z0, (p15 + p85) / 2))
cz = np.array(cz)
curva = np.polyval(np.polyfit(cz[:, 0], cz[:, 1], 3), zs)
curva = np.convolve(np.pad(curva, 2, mode="edge"), np.ones(5) / 5, mode="valid")
print("CENTRO_JUBA antes", [(round(float(a), 1), round(float(b), 2)) for a, b in cz[::2]])
dx = -GANHO * np.interp(co[:, 2], zs, curva) * m
co[:, 0] += dx
me.vertices.foreach_set("co", co.ravel()); me.update()
print("DESLOCAMENTO verts com |dx|>0,01:", int((np.abs(dx) > 0.01).sum()), "max %.3f" % np.abs(dx).max())
cz2 = []
for z0 in zs[::2]:
    s = (reg > 0) & (np.abs(co[:, 2] - z0) < 0.25)
    if s.sum() > 25:
        p15, p85 = np.percentile(co[s, 0], [15, 85]); cz2.append((round(float(z0), 1), round(float((p15 + p85) / 2), 2)))
print("CENTRO_JUBA depois", cz2)
json.dump({"ganho": GANHO, "centro_antes": cz.tolist(), "centro_depois": cz2, "dx_max": float(np.abs(dx).max()),
           "verts_movidos": int((np.abs(dx) > 0.01).sum())}, open(os.path.join(OUT, "desentortar_juba.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend"))
print("DESENTORTAR_OK")
