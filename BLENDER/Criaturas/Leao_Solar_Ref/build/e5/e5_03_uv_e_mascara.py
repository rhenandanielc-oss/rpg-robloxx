"""E5 inspecao: ocupacao da UV (espaco livre no atlas) e regiao 'juba pintada na pata' (mascara de cor dentro do cilindro da pata).
Uso: blender -b E4b_r2.blend -P e5_03_uv_e_mascara.py -- <juntas.json> <saida_dir>"""
import bpy, sys, os, json, math
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; J = json.load(open(A[0])); OUT = A[1]; os.makedirs(OUT, exist_ok=True)
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; me = ob.data
uv = np.array([d.uv for d in me.uv_layers.active.data]); R = 512; occ = np.zeros((R, R), bool)
for p in me.polygons:
    li = list(p.loop_indices); P = uv[li] * R
    for k in range(1, len(li) - 1):
        tri = P[[0, k, k + 1]]; x0, y0 = np.floor(tri.min(0)).astype(int); x1, y1 = np.ceil(tri.max(0)).astype(int)
        xs, ys = np.meshgrid(np.arange(max(x0, 0), min(x1 + 1, R)), np.arange(max(y0, 0), min(y1 + 1, R)))
        if xs.size == 0: continue
        q = np.stack([xs.ravel() + 0.5, ys.ravel() + 0.5], 1); a, b, c = tri
        d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(d) < 1e-12: continue
        l1 = ((b[1] - c[1]) * (q[:, 0] - c[0]) + (c[0] - b[0]) * (q[:, 1] - c[1])) / d; l2 = ((c[1] - a[1]) * (q[:, 0] - c[0]) + (a[0] - c[0]) * (q[:, 1] - c[1])) / d
        m = (l1 >= -0.01) & (l2 >= -0.01) & (l1 + l2 <= 1.01); occ[q[m, 1].astype(int), q[m, 0].astype(int)] = True
print("UV_OCUPACAO %.1f%%" % (100 * occ.mean()))
# maiores retangulos livres (aproximacao por blocos de 16 px)
B = 16; livre = []
for by in range(0, R, B):
    for bx in range(0, R, B):
        if not occ[by:by + B, bx:bx + B].any(): livre.append((bx, by))
print("BLOCOS_LIVRES_16px", len(livre), "de", (R // B) ** 2)
from PIL import Image
Image.fromarray((~occ[::-1] * 255).astype(np.uint8)).save(os.path.join(OUT, "uv_livre.png"))
json.dump({"ocupacao": float(occ.mean()), "blocos_livres": livre, "R": R, "B": B}, open(os.path.join(OUT, "uv_livre.json"), "w"))
