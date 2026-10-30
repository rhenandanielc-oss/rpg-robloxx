"""Corpo sem pelagem (argila), lateral e 3/4 traseiro, para inspecionar a forma. Uso: blender -b <blend> -P render_corpo.py -- <pasta>"""
import bpy, sys, os, math
from mathutils import Vector
out = sys.argv[sys.argv.index("--") + 1]; os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "SINGLE"
sc.display.shading.single_color = (0.6, 0.58, 0.55); sc.render.resolution_x, sc.render.resolution_y = 900, 650
for o in list(bpy.data.objects):
    if o.type in ("LIGHT", "CAMERA") or o.name.startswith("REF_") or "Pelagem" in o.name: bpy.data.objects.remove(o, do_unlink=True)
cd = bpy.data.cameras.new("c"); cd.lens = 50; cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
def mira(alvo, pos, nome):
    cam.location = pos; cam.rotation_euler = (Vector(alvo) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, nome + ".png"); bpy.ops.render.render(write_still=True)
mira((0, 1.6, 4.0), (9, 1.6, 4.2), "corpo_lateral_tras")
mira((0, 1.8, 4.2), (6, 7.5, 6.0), "corpo_34_tras")
mira((0, -0.5, 4.5), (14, -0.5, 4.6), "corpo_lateral")
print("OK_CORPO")
