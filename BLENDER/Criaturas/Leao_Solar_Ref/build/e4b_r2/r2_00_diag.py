"""E4b r2 diagnostico: nas poses de pata dianteira, lista as arestas mais esticadas/comprimidas com os pesos dos vertices
e a distancia ate a superficie do lado oposto (mecha fundida?). Uso: blender -b E4b.blend -P r2_00_diag.py -- <juntas.json>"""
import bpy, sys, json, math, os
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; J = json.load(open(A[0]))
exec(open(__file__.replace("r2_00_diag.py", "r2_poses_lib.py")).read())
ob, arm = OB, ARM; me = ob.data
G = {g.index: g.name for g in ob.vertex_groups}
def pesos(i): return sorted(((round(g.weight, 2), G[g.group]) for g in me.vertices[i].groups), reverse=True)[:4]
for nome in os.environ.get("R2_POSES", "cotovelo_dobra,punho_dobra,ombro_avanco").split(","):
    zerar(); POSE[nome](); P = posado()
    L1 = np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1); r = L1 / np.maximum(L0, 1e-6)
    print("==", nome)
    for k in (np.argsort(-(L1 - L0))[:10] if os.environ.get("R2_ABS") else np.argsort(-np.abs(np.log(np.maximum(r, 1e-6))))[:12]):
        a, b = E[k]; print(" r=%.2f L0=%.3f L1=%.3f" % (r[k], L0[k], L1[k]), np.round(CO0[a], 2), pesos(a), "|", np.round(CO0[b], 2), pesos(b))
