"""Linha media (x medio por fatia de y) e pontos-chave do lobo normalizado. So leitura.
Uso: blender -b <normalizado.blend> -P analisar_eixo.py"""
import bpy
import numpy as np
ob = bpy.data.objects["Lobo_Meshy"]; n = len(ob.data.vertices)
co = np.empty(n * 3, dtype=np.float32); ob.data.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
x, y, z = co[:, 0], co[:, 1], co[:, 2]
print("BBOX", co.min(0).round(2), co.max(0).round(2))
for y0 in np.arange(y.min(), y.max(), 0.5):
    m = (y >= y0) & (y < y0 + 0.5)
    if m.sum() < 50: continue
    for lo, hi in ((0.0, 2.5), (2.5, 5.0), (5.0, 9.0)):
        mm = m & (z >= lo) & (z < hi)
        if mm.sum() > 50: print("FATIA y=%.1f z%.0f-%.0f n=%6d x=[%.2f %.2f] xm=%.2f" % (y0, lo, hi, mm.sum(), x[mm].min(), x[mm].max(), x[mm].mean()))
cab = z > 6.6
i = np.argmax(z); print("TOPO", co[i].round(2))
for nome, idx in (("min_y_cab", np.argmin(np.where(cab, y, 1e9))), ("max_x_cab", np.argmax(np.where(cab, x, -1e9))),
                  ("min_x_cab", np.argmin(np.where(cab, x, 1e9)))):
    print(nome, co[idx].round(2))
cauda = y > 2.5
print("cauda_x_medio_por_y", [(round(float(a), 1), round(float(x[(y >= a) & (y < a + 0.5) & (z > 1.0)].mean()), 2)) for a in np.arange(2.5, y.max(), 0.5) if ((y >= a) & (y < a + 0.5)).sum() > 50])
