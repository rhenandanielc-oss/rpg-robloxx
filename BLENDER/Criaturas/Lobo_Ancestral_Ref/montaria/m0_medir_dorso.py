"""Montaria M0 (10/11/2026): mede o dorso do Lobo Ancestral (rig18) no repouso (so leitura): topo da pele no meio e nas
laterais, barriga, largura 1 e 2,5 abaixo do topo, e onde estao ombros/quadril/cernelha. Uso:
blender -b rig18/Lobo_Ancestral_Rig.blend -P montaria/m0_medir_dorso.py -- <saida.json>"""
import bpy, sys, json
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]
arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
if arm.animation_data: arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); m = LO.evaluated_get(dg).to_mesh(); W = LO.matrix_world
vs = [W @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]
bvh = BVHTree.FromPolygons(vs, fs); P = np.array([tuple(v) for v in vs])
out = {"bbox_min": P.min(0).round(2).tolist(), "bbox_max": P.max(0).round(2).tolist(), "perfil": [],
       "ossos": {b.name: [round(c, 2) for c in (arm.matrix_world @ b.head_local)] for b in arm.data.bones if b.name in
                 ("Pelve", "Coluna1", "Coluna2", "Peito", "Pescoco1", "EscapulaE", "BracoE", "CoxaE", "Cabeca")}}
for y in np.arange(-7.0, 5.01, 0.5):
    row = {"y": round(float(y), 2)}
    for x in (-1.5, -0.75, 0.0, 0.75, 1.5):
        h = bvh.ray_cast(V((x, y, 30)), V((0, 0, -1))); row["topo_x%+.2f" % x] = round(h[0].z, 2) if h[0] else None
    b = bvh.ray_cast(V((0, y, -5)), V((0, 0, 1))); row["barriga"] = round(b[0].z, 2) if b[0] else None
    if row["topo_x+0.00"]:
        for dz in (0.5, 1.0, 2.0):
            zz = row["topo_x+0.00"] - dz; r = bvh.ray_cast(V((9, y, zz)), V((-1, 0, 0))); l = bvh.ray_cast(V((-9, y, zz)), V((1, 0, 0)))
            row["lados_%.1fabaixo" % dz] = [round(r[0].x, 2) if r[0] else None, round(l[0].x, 2) if l[0] else None]
    out["perfil"].append(row)
json.dump(out, open(A[0], "w"), indent=1); print("MEDIDO", out["bbox_min"], out["bbox_max"])
