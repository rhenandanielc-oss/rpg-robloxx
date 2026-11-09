import bpy, sys
import numpy as np
from mathutils.kdtree import KDTree
arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
gi = {g.index: g.name for g in LO.vertex_groups}
dono = np.array([gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else "" for v in LO.data.vertices])
def coords(posed):
    if posed:
        act = bpy.data.actions["Lobo_Repouso"]; arm.animation_data_create(); arm.animation_data.action = act
        try: arm.animation_data.action_slot = act.slots[0]
        except Exception: pass
    else:
        if arm.animation_data: arm.animation_data.action = None
        for pb in arm.pose.bones: pb.rotation_quaternion = (1,0,0,0); pb.location = (0,0,0); pb.scale = (1,1,1)
    bpy.context.scene.frame_set(0); bpy.context.view_layer.update()
    ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = ev.to_mesh()
    c = np.array([v.co[:] for v in m.vertices]); ev.to_mesh_clear(); return c
for posed in (False, True):
    co = coords(posed)
    print("==== POSE" if posed else "==== REPOUSO (rest)")
    for cad, gs in (("dian", ["Braco","Antebraco","Mao","Dedos"]), ("tras", ["Canela","Metatarso","Pe"])):
        selE = np.isin(dono, [g+"E" for g in gs]); selD = np.isin(dono, [g+"D" for g in gs])
        kd = KDTree(int(selD.sum()))
        for i, p in enumerate(co[selD]): kd.insert((-p[0], p[1], p[2]), i)
        kd.balance()
        cE = co[selE]; d = np.array([kd.find(p)[2] for p in cE]); dv = np.array([np.array(kd.find(p)[0]) - p for p in cE])
        for z0 in np.arange(0.1, 4.6, 0.4):
            s = np.abs(cE[:,2]-z0) < 0.2
            if s.sum() > 5:
                print("%s z%.1f  n%4d dist_med %.3f  p90 %.3f  desloc_med(x,y,z) %+.3f %+.3f %+.3f" % (cad, z0, s.sum(), np.median(d[s]), np.percentile(d[s],90), *np.median(dv[s],axis=0)))
