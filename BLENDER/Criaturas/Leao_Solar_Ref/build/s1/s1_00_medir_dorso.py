"""S1 (sela): mede o dorso do Leao Solar na pose de repouso (so leitura): perfil da coluna (topo da pele em x=0), largura
do dorso, onde a juba termina no dorso, altura da barriga e posicao dos ossos (coluna, escapulas, cotovelos, quadril).
Uso: blender -b Leao_Solar_Ref_E5_clipes_r6.blend -P s1_00_medir_dorso.py -- <saida.json>"""
import bpy, sys, json
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]
arm = bpy.data.objects["Leao_Solar_Rig"]; ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]
arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); m = ob.evaluated_get(dg).to_mesh(); W = ob.matrix_world
P = np.array([W @ v.co for v in m.vertices]); fs = [tuple(p.vertices) for p in m.polygons]; mats = [p.material_index for p in m.polygons]
GI = {g.index: g.name for g in ob.vertex_groups}
dom = []
for v in ob.data.vertices:
    w = sorted(((g.weight, GI[g.group]) for g in v.groups), reverse=True); dom.append(w[0][1] if w else "")
juba = np.array([d.startswith("Juba") for d in dom])
bvh = BVHTree.FromPolygons([V(p) for p in P], fs)
# pele sem juba: faces cujos vertices nao sao dominados pela juba
fs_pele = [f for f in fs if not any(juba[i] for i in f)]
bvh_p = BVHTree.FromPolygons([V(p) for p in P], fs_pele)
out = {"materiais": [s.material.name if s.material else None for s in ob.material_slots], "perfil": [], "ossos": {}}
for y in np.arange(-12.0, 9.01, 0.5):
    top = bvh.ray_cast(V((0, y, 30)), V((0, 0, -1))); topp = bvh_p.ray_cast(V((0, y, 30)), V((0, 0, -1)))
    bot = bvh_p.ray_cast(V((0, y, -5)), V((0, 0, 1)))
    larg = None
    if topp[0]:
        zz = topp[0].z - 1.0; r = bvh_p.ray_cast(V((9, y, zz)), V((-1, 0, 0))); l = bvh_p.ray_cast(V((-9, y, zz)), V((1, 0, 0)))
        larg = [round(r[0].x, 2) if r[0] else None, round(l[0].x, 2) if l[0] else None]
    out["perfil"].append(dict(y=round(float(y), 2), topo_com_juba=round(top[0].z, 2) if top[0] else None, topo_pele=round(topp[0].z, 2) if topp[0] else None,
                              barriga=round(bot[0].z, 2) if bot[0] else None, largura_1abaixo=larg))
# onde a juba cobre o dorso: para cada y, a juba esta acima da pele em x=0?
jy = P[juba]; out["juba_y_max_no_dorso"] = round(float(jy[(np.abs(jy[:, 0]) < 1.5) & (jy[:, 2] > 8)][:, 1].max()), 2)
out["juba_y_max_lados"] = round(float(jy[(np.abs(jy[:, 0]) > 1.5) & (jy[:, 2] > 6)][:, 1].max()), 2)
for b in arm.data.bones:
    if any(b.name.startswith(k) for k in ("Raiz", "Quadril", "Coluna", "Peito", "Pescoco", "Escapula", "Umero", "Antebraco", "Coxa")):
        out["ossos"][b.name] = dict(cabeca=[round(x, 2) for x in b.head_local], cauda=[round(x, 2) for x in b.tail_local], pai=b.parent.name if b.parent else None)
out["vertices"] = len(P); out["tris"] = sum(len(f) - 2 for f in fs)
json.dump(out, open(A[0], "w"), indent=1); print("MEDIDO", out["juba_y_max_no_dorso"], out["juba_y_max_lados"], out["tris"])
