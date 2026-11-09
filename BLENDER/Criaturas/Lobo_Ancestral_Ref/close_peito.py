"""Close frontal do peito/juba (camera fixa, mesma para todas as variantes), pose Repouso q0 das acoes do rig2. So leitura.
Uso: blender -b <rig.blend> -P close_peito.py -- <saida.png> <blend_das_acoes>"""
import bpy, sys, os
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; SAIDA = os.path.abspath(A[0])
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
if "Lobo_Repouso" not in bpy.data.actions:
    with bpy.data.libraries.load(os.path.abspath(A[1])) as (s, d): d.actions = ["Lobo_Repouso"]
for o in sc.objects:
    if (o.type == "MESH" and o is not LO and not o.name.startswith("Plane")) or o.type == "EMPTY": o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
if not arm.animation_data: arm.animation_data_create()
act = bpy.data.actions["Lobo_Repouso"]; arm.animation_data.action = act
try: arm.animation_data.action_slot = act.slots[0]
except Exception: pass
sc.frame_set(int(act.frame_range[0]))
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16; sc.render.resolution_x, sc.render.resolution_y = 700, 820
cam = sc.camera; camd = cam.data; camd.type = "ORTHO"; camd.ortho_scale = 5.2
cam.location = V((0, -30, 5.6)); cam.rotation_euler = (1.5707963, 0, 0)
sc.render.filepath = SAIDA; bpy.ops.render.render(write_still=True)
