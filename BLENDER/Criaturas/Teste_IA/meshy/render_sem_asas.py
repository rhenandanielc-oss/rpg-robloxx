"""Render do corpo SEM as asas (mascara temporaria, nao salva) para enxergar cauda/quadril/patas.
Uso: blender -b arq.blend -P render_sem_asas.py -- saida_dir Clipe1,Clipe2 [repouso]"""
import bpy, sys, os
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]; out = args[0]; clipes = args[1].split(","); os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
gi = {g.index: g.name for g in M.vertex_groups}
vg = M.vertex_groups.new(name="ASAS_TMP")
for v in M.data.vertices:
    if len(v.groups) and gi[max(v.groups, key=lambda g: g.weight).group].startswith(("wing_", "shoulder_")): vg.add([v.index], 1.0, "REPLACE")
mk = M.modifiers.new("mask_tmp", "MASK"); mk.vertex_group = "ASAS_TMP"; mk.invert_vertex_group = True
cam = bpy.data.objects["cam_rev"]; sc.camera = cam; sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 560, 400
for nome in clipes:
    if nome == "repouso":
        A.animation_data.action = None
        for pb in A.pose.bones: pb.matrix_basis.identity()
        sc.frame_set(1)
    else:
        act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
        f0, f1 = map(int, act.frame_range); sc.frame_set(f0 + (f1 - f0) // 3)
    c = Vector((-0.02, 0.25, 0.3))
    for vista, d, r in (("lado", (1, 0, 0.05), 1.9), ("topo", (0.0, 0.05, 1), 1.9), ("tras", (0.2, 1, 0.3), 1.6), ("34", (0.8, 0.6, 0.5), 1.8)):
        cam.location = c + Vector(d).normalized() * r; cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, "corpo_%s_%s.png" % (nome, vista)); bpy.ops.render.render(write_still=True)
print("SEM_ASAS_OK")
