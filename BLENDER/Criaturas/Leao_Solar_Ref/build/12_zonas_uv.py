"""Exporta, por face, a UV e a zona (1 = juba/tufo, 0 = corpo) da E2. Zona: centro da face dentro da silhueta da juba
ou do tufo no perfil E dentro da frente (mascaras da referencia, mesma conversao px->stud).
Uso: blender -b <e2.blend> -P 12_zonas_uv.py -- <ref_dir> <saida.npz>"""
import bpy, sys, os
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]
ms = {n: np.load(os.path.join(A[0], n + ".npy")) for n in ("juba_lado", "tufo_lado", "frente")}
K = 11.5 / 360; KF = (592 - 8) * K / (1240 - 623)
ob = bpy.data.objects["Leao_Solar_E2"]; me = ob.data; uv = me.uv_layers.active.data
cen = np.array([p.center for p in me.polygons])
xs = np.clip(np.round(620 - cen[:, 1] / K).astype(int), 0, 1216); ys = np.clip(np.round(592 - cen[:, 2] / K).astype(int), 0, 1292)
xf = np.clip(np.round(335 + cen[:, 0] / KF).astype(int), 0, 1216); yf = np.clip(np.round(1240 - cen[:, 2] / KF).astype(int), 0, 1292)
z = ((ms["juba_lado"][ys, xs] | ms["tufo_lado"][ys, xs]) & ms["frente"][yf, xf]).astype(np.uint8)
tri = [];  zz = []
for p, zi in zip(me.polygons, z):
    l = list(p.loop_indices)
    for i in range(1, len(l) - 1):
        tri.append([uv[l[0]].uv[:], uv[l[i]].uv[:], uv[l[i + 1]].uv[:]]); zz.append(zi)
np.savez_compressed(A[1], tri=np.array(tri, np.float32), zona=np.array(zz, np.uint8)); print("ZONAS_OK", len(tri), int(np.sum(zz)))
