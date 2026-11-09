"""Close frontal ortografico das pernas dianteiras/peito (z 0-6) para revisar a coluna de cada perna. So leitura.
Uso: blender -b <rig.blend> -P close_pernas.py -- <saida.png>"""
import bpy, sys, os
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for o in sc.objects:
    if o.type == "MESH" and o is not LO and not o.name.startswith("Plane"): o.hide_render = True
if arm.animation_data: arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    for c in pb.constraints: c.mute = True
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16; sc.render.resolution_x, sc.render.resolution_y = 900, 900
cam = sc.camera; cam.data.type = "ORTHO"; cam.data.ortho_scale = 6.4
cam.location = V((0, -20, 3.0)); cam.rotation_euler = (V((0, 0, 3.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
