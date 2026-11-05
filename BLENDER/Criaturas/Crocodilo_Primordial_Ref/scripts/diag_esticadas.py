"""Somente leitura: arestas da cabeca que mais esticam com a mandibula aberta alem do repouso e fechada a 80%.
Uso: blender -b CR_Crocodilo_Rig.blend -P diag_esticadas.py -- [graus_abre] [frac_fecha]"""
import bpy, sys, math
import numpy as np
from mathutils import Matrix
A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ABRE = float(A[0]) if A else 10.0; FECHA = float(A[1]) if len(A) > 1 else 0.8
arm = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]; me = lo.data
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
n = len(me.vertices); r0 = np.empty(n * 3); me.vertices.foreach_get("co", r0); r0 = r0.reshape(-1, 3)
ed = np.empty(len(me.edges) * 2, dtype=int); me.edges.foreach_get("vertices", ed); ed = ed.reshape(-1, 2)
L0 = np.linalg.norm(r0[ed[:, 0]] - r0[ed[:, 1]], axis=1)
gm = lo.vertex_groups["Mandibula"]
wm = np.zeros(n)
for v in me.vertices:
    for g in v.groups:
        if g.group == gm.index: wm[v.index] = g.weight
def avalia(ang, rotulo):
    pb = arm.pose.bones["Mandibula"]; pb.rotation_mode = "XYZ"; pb.rotation_euler = (math.radians(ang), 0, 0)
    bpy.context.view_layer.update()
    ev = lo.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = ev.to_mesh()
    r1 = np.empty(n * 3); m.vertices.foreach_get("co", r1); r1 = r1.reshape(-1, 3); ev.to_mesh_clear()
    L1 = np.linalg.norm(r1[ed[:, 0]] - r1[ed[:, 1]], axis=1); ratio = L1 / np.maximum(L0, 1e-5)
    idx = np.argsort(ratio)[::-1][:25]
    print("==", rotulo, "angulo", ang)
    for i in idx:
        a, b = ed[i]
        print("  aresta %d-%d estica %.2fx  pos %s  wm %.2f/%.2f" % (a, b, ratio[i], np.round((r0[a] + r0[b]) / 2, 2), wm[a], wm[b]))
    pb.rotation_euler = (0, 0, 0)
avalia(ABRE, "ABERTA")
avalia(-FECHA * arm["ang_boca"], "FECHADA")
