"""Renderiza um GLB antigo do urso (somente leitura) em 4 vistas para avaliar reaproveitamento.
Uso: blender -b --factory-startup -P render_glb_antigo.py -- <glb> <saida_dir>"""
import bpy, sys, os, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; glb, out = a[0], os.path.abspath(a[1]); os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=glb)
ms = [o for o in sc.objects if o.type == "MESH"]
mn = V((min(min((o.matrix_world @ V(c))[i] for c in o.bound_box) for o in ms) for i in range(3)))
mx = V((max(max((o.matrix_world @ V(c))[i] for c in o.bound_box) for o in ms) for i in range(3)))
print("BBOX", tuple(round(x, 2) for x in mn), tuple(round(x, 2) for x in mx), "tris", sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in ms))
for o in ms: print("MALHA", o.name, len(o.data.polygons), [m.name for m in o.data.materials])
c = (mn + mx) / 2; R = (mx - mn).length
for nome, en, rot in (("Sol", 3.5, (0.8, 0, 0.6)), ("Pre", 1.5, (1.0, 0, -2.2))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.5, 0.5, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 800, 600; sc.view_settings.view_transform = "AgX"
cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
for nome, d in (("lado", (1, 0, 0.1)), ("frente", (0, -1, 0.1)), ("34", (0.7, -0.7, 0.3)), ("tras", (0, 1, 0.2))):
    for eixo in ("Y", "Z"):
        pass
    cam.location = c + V(d).normalized() * R * 1.25; cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, "v5_%s.png" % nome); bpy.ops.render.render(write_still=True)
