"""Renders de referencia do modelo original (textura, luz de estudio, fundo cinza claro) para anexar no ChatGPT."""
import bpy, sys, os
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]; out = a[1]; os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=a[0])
o = [x for x in bpy.data.objects if x.type == "MESH"][0]
ps = [o.matrix_world @ v.co for v in list(o.data.vertices)[::9]]
mn = Vector([min(p[i] for p in ps) for i in range(3)]); mx = Vector([max(p[i] for p in ps) for i in range(3)]); c = (mn + mx) / 2; r = (mx - mn).length
sc = bpy.context.scene; sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 1400, 1050
sc.view_settings.view_transform = "Standard"
w = bpy.data.worlds.new("w"); w.color = (0.78, 0.79, 0.8); sc.world = w
for rot, e in (((0.9, 0.1, 0.8), 3.0), ((1.1, 0.0, -2.2), 1.2), ((0.3, 0.0, 3.4), 1.0)):
    l = bpy.data.objects.new("l", bpy.data.lights.new("l", "SUN")); sc.collection.objects.link(l); l.rotation_euler = rot; l.data.energy = e
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 50
for nome, d in (("34_frente", (0.7, -1, 0.35)), ("frente", (0, -1, 0.15)), ("lado", (1, 0, 0.1)), ("costas_34", (-0.7, 1, 0.4)), ("cabeca", None)):
    if d is None:
        cc = c + Vector((0, (mn.y - c.y) * 0.75, (mx.z - c.z) * 0.55)); cam.location = cc + Vector((0.6, -1, 0.25)).normalized() * r * 0.4
    else:
        cc = c; cam.location = c + Vector(d).normalized() * r * 1.25
    cam.rotation_euler = (cc - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, "silverwing_ref_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("REF_OK")
