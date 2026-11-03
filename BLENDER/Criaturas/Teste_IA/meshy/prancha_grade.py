"""Monta uma prancha (grade) de PNGs com o Blender (sem PIL): linhas = clipes, colunas = quadros <nome>_<i>.png.
Uso: blender -b --factory-startup -P prancha_grade.py -- pasta clipe1,clipe2 n_colunas saida.png"""
import bpy, sys, os
import numpy as np
a = sys.argv[sys.argv.index("--") + 1:]; pasta, nomes, ncol, saida = a[0], a[1].split(","), int(a[2]), a[3]
linhas = []
for n in nomes:
    cols = []
    for i in range(ncol):
        im = bpy.data.images.load(os.path.join(pasta, "%s_%d.png" % (n, i)))
        w, h = im.size; px = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        px[:2, :, :3] = 0.15; px[:, :2, :3] = 0.15                       # fio separador
        cols.append(px); bpy.data.images.remove(im)
    linhas.append(np.concatenate(cols, axis=1))
grade = np.concatenate(linhas[::-1], axis=0)                             # pixels do Blender comecam embaixo
H, W = grade.shape[:2]
out = bpy.data.images.new("prancha", W, H, alpha=True); out.pixels = grade.ravel()
out.filepath_raw = saida; out.file_format = "PNG"; out.save()
print("PRANCHA_OK", W, H)
