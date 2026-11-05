"""Exporta, por triangulo da malha, o centro 3D, a normal e a UV (para operacoes de textura guiadas pela geometria).
Uso: blender -b <arquivo.blend> -P e3_02_exportar_tris.py -- <objeto> <saida.npz>"""
import bpy, sys
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]
ob = bpy.data.objects[A[0]]; me = ob.data; me.calc_loop_triangles(); uv = me.uv_layers.active.data
n = len(me.loop_triangles)
cen = np.zeros((n, 3), np.float32); nor = np.zeros((n, 3), np.float32); tri = np.zeros((n, 3, 2), np.float32)
pos = np.zeros((n, 3, 3), np.float32)
for i, t in enumerate(me.loop_triangles):
    cen[i] = t.center; nor[i] = t.normal
    for j, l in enumerate(t.loops): tri[i, j] = uv[l].uv
    for j, vi in enumerate(t.vertices): pos[i, j] = me.vertices[vi].co
np.savez_compressed(A[1], centro=cen, normal=nor, tri=tri, pos=pos); print("TRIS_OK", n)
