"""Patas no chao da malha (com o modificador Armature avaliado): centro e ponta de cada aglomerado z<0,3. So leitura.
Uso: blender -b <rig.blend> -P medir_patas.py"""
import bpy
import numpy as np
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; dg = bpy.context.evaluated_depsgraph_get(); me = LO.evaluated_get(dg).data
co = np.array([LO.matrix_world @ v.co for v in me.vertices]); x, y, z = co.T
s = (z < 0.30) & (y < 3.6); ym = (y[s].min() + y[s].max()) / 2
for lado, sx in (("E", 1), ("D", -1)):
    for par, c in (("dian", y < ym), ("tras", y >= ym)):
        q = s & (x * sx > 0.15) & c
        print("PATA %s %s centro x=%.2f y=%.2f  ponta y=%.2f  zmin=%.3f n=%d" % (lado, par, x[q].mean(), y[q].mean(), y[q].min(), z[q].min(), q.sum()))
print("ZMIN", round(float(z.min()), 3))
