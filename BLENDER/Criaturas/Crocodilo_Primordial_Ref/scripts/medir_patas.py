"""Somente leitura: centro da secao de cada pata por faixa de altura (para cotovelo/joelho do rig).
Uso: blender -b CR_Crocodilo_LOW.blend -P medir_patas.py"""
import bpy, numpy as np
lo = bpy.data.objects["CR_Croc_LOW"]; me = lo.data
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
x, y, z = co.T
for nome, sx, cond in (("dianE", 1, y < -4), ("tras_E", 1, y >= -4), ("dianD", -1, y < -4), ("trasD", -1, y >= -4)):
    pe = co[(z < 0.35) & (x * sx > 1.5) & cond].mean(axis=0)
    print("PATA", nome, "pe", np.round(pe, 2))
    for z0 in np.arange(0.2, 3.4, 0.3):
        s = (np.abs(z - z0) < 0.15) & (x * sx > 1.8) & (np.abs(y - pe[1]) < 2.0)
        if s.sum() > 5:
            print("   z %.1f centro x %.2f y %.2f  larg_x %.2f larg_y %.2f n %d" % (z0, x[s].mean(), y[s].mean(), np.ptp(x[s]), np.ptp(y[s]), s.sum()))
