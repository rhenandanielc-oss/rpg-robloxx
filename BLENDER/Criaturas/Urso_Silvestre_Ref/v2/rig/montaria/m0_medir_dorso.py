"""Montaria M0 (09/11): mede o dorso do Urso Silvestre v2 na pose de repouso (so leitura): perfil do topo da pele no
meio, largura um pouco abaixo do topo, barriga, e o topo nas laterais. Uso:
blender -b CR_Urso_v2_Anim.blend -P m0_medir_dorso.py -- <saida.json>"""
import bpy, sys, json
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]
arm = bpy.data.objects["Urso_Rig"]
if arm.animation_data: arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); vs, fs = [], []
for nm in ("Urso_Corpo_Frente", "Urso_Corpo_Tras", "Urso_Cabeca"):
    o = bpy.data.objects[nm]; m = o.evaluated_get(dg).to_mesh(); W = o.matrix_world; k = len(vs)
    vs += [W @ v.co for v in m.vertices]; fs += [tuple(i + k for i in p.vertices) for p in m.polygons]
bvh = BVHTree.FromPolygons(vs, fs); P = np.array([tuple(v) for v in vs])
out = {"bbox_min": P.min(0).round(2).tolist(), "bbox_max": P.max(0).round(2).tolist(), "perfil": []}
for y in np.arange(-6.0, 7.01, 0.5):
    row = {"y": round(float(y), 2)}
    for x in (-2.0, -1.0, 0.0, 1.0, 2.0):
        h = bvh.ray_cast(V((x, y, 30)), V((0, 0, -1))); row["topo_x%+.0f" % x] = round(h[0].z, 2) if h[0] else None
    b = bvh.ray_cast(V((0, y, -5)), V((0, 0, 1))); row["barriga"] = round(b[0].z, 2) if b[0] else None
    if row["topo_x+0"]:
        zz = row["topo_x+0"] - 1.0; r = bvh.ray_cast(V((9, y, zz)), V((-1, 0, 0))); l = bvh.ray_cast(V((-9, y, zz)), V((1, 0, 0)))
        row["lados_1abaixo"] = [round(r[0].x, 2) if r[0] else None, round(l[0].x, 2) if l[0] else None]
        zz = row["topo_x+0"] - 2.5; r = bvh.ray_cast(V((9, y, zz)), V((-1, 0, 0))); l = bvh.ray_cast(V((-9, y, zz)), V((1, 0, 0)))
        row["lados_2.5abaixo"] = [round(r[0].x, 2) if r[0] else None, round(l[0].x, 2) if l[0] else None]
    out["perfil"].append(row)
json.dump(out, open(A[0], "w"), indent=1); print("MEDIDO", out["bbox_min"], out["bbox_max"])
