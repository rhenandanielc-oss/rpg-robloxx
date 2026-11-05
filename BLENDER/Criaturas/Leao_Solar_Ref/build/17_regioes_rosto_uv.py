"""Exporta UV por face com a regiao do rosto da E2: 2 = trufa do nariz (triangulo na frente do focinho, achado pela
ponta da malha), 3 = rosto (a frente da linha das bochechas, fora da juba), 0 = resto.
Uso: blender -b <e2.blend> -P 17_regioes_rosto_uv.py -- <zonas_uv.npz> <saida.npz>"""
import bpy, sys
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]
K = 11.5 / 360
me = bpy.data.objects["Leao_Solar_E2"].data; uv = me.uv_layers.active.data
cand = [v.co for v in me.vertices if 12.8 < v.co.z < 15.2 and abs(v.co.x) < 0.35]
T = min(cand, key=lambda c: c.y); print("PONTA_NARIZ", tuple(round(c, 3) for c in T))
zj = np.load(A[0])["zona"]; reg = []; tri = []; k = 0
for p in me.polygons:
    c, n = p.center, p.normal
    base = T.z - 0.50; alt = (c.z - base) / 0.85
    nariz = (c - T).length < 1.1 and n.y < 0.2                 # vizinhanca da ponta; a trufa e escolhida pela cor no 18
    l = list(p.loop_indices)
    for i in range(1, len(l) - 1):
        r = 2 if nariz else (3 if (c.y < -(1030 - 620) * K and 11.3 < c.z < 16.6 and zj[k] == 0) else 0)
        tri.append([uv[l[0]].uv[:], uv[l[i]].uv[:], uv[l[i + 1]].uv[:]]); reg.append(r); k += 1
reg = np.array(reg, np.uint8); np.savez_compressed(A[1], tri=np.array(tri, np.float32), regiao=reg)
print("REGIOES_OK nariz", int((reg == 2).sum()), "rosto", int((reg == 3).sum()))
