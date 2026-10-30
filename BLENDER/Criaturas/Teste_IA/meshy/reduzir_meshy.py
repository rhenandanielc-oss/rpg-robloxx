"""Gera COPIA leve do Silverwing (original intocado): decimacao para ~alvo triangulos, cabeca virada para -Y
(= +Z no glTF, frente do Mesh2Motion), pes no chao, texturas reduzidas. Renderiza frente/lado para conferencia."""
import bpy, sys, os
from mathutils import Vector, Matrix
import math
args = sys.argv[sys.argv.index("--") + 1:]; glb, saida, alvo = args[0], args[1], int(args[2])
pasta = os.path.dirname(saida)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
o = [x for x in bpy.data.objects if x.type == "MESH"][0]
bpy.context.view_layer.objects.active = o; o.select_set(True)
n0 = len(o.data.polygons)
m = o.modifiers.new("dec", "DECIMATE"); m.ratio = alvo / n0; m.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier="dec")
# o Meshy ja exporta a cabeca para -Y (envergadura no eixo X): sem rotacao
zs = min((v.co.z for v in o.data.vertices)); xs = [v.co.x for v in o.data.vertices]; ys = [v.co.y for v in o.data.vertices]
o.data.transform(Matrix.Translation((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -zs)))
for im in bpy.data.images:
    if im.size[0] > 2048: im.scale(2048, 2048)
print("TRIS", n0, "->", sum(len(p.vertices) - 2 for p in o.data.polygons))
bpy.ops.export_scene.gltf(filepath=saida, export_format="GLB", use_selection=True, export_image_format="JPEG")
print("TAM_MB", round(os.path.getsize(saida) / 1e6, 2))
sc = bpy.context.scene; sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 560, 420
w = bpy.data.worlds.new("w"); w.color = (0.75, 0.77, 0.8); sc.world = w
sun = bpy.data.objects.new("sol", bpy.data.lights.new("sol", "SUN")); sc.collection.objects.link(sun); sun.rotation_euler = (0.7, 0.2, 0.6)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
c = Vector((0, 0, 0.5))
for nome, d in (("frente", (0, -1, 0.15)), ("lado", (1, 0, 0.15))):
    cam.location = c + Vector(d).normalized() * 2.6; cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(pasta, "reduzido_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("REDUZIR_OK")
