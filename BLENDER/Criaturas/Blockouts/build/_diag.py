import bpy, numpy as np
o = next(x for x in bpy.data.objects if x.name.endswith("_Corpo"))
arm = o.parent
arm.animation_data.action = bpy.data.actions["Andar"]
bpy.context.scene.frame_set(9)
me0 = o.data
ed = np.array([e.vertices[:] for e in me0.edges])
P0 = np.array([v.co for v in me0.vertices])
dg = bpy.context.evaluated_depsgraph_get(); eo = o.evaluated_get(dg); me = eo.to_mesh()
P = np.array([v.co for v in me.vertices]); eo.to_mesh_clear()
L0 = np.linalg.norm(P0[ed[:,0]]-P0[ed[:,1]],axis=1)+1e-6; L = np.linalg.norm(P[ed[:,0]]-P[ed[:,1]],axis=1)+1e-6
r = np.maximum(L/L0, L0/L)
bad = np.argsort(-r)[:40]
print("L0 min/med", L0.min(), np.median(L0))
for i in bad[:15]:
    v = ed[i][0]
    gs = sorted([(g.weight, o.vertex_groups[g.group].name) for g in me0.vertices[v].groups], reverse=True)[:3]
    print(round(r[i],2), round(L0[i],4), tuple(round(x,2) for x in P0[v]), gs)
