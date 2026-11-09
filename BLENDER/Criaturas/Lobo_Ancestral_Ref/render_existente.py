"""Renderiza um .blend existente (so leitura: nao salva) com as cameras da revisao do Lobo Ancestral_Ref.
Uso: blender -b <arquivo.blend> -P render_existente.py -- <saida_dir>"""
import bpy, sys, os, math
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
objs = [o for o in sc.objects if o.type == "MESH" and o.visible_get()]
for o in objs: print("OBJ", o.name, len(o.data.polygons), tuple(round(c, 2) for c in o.dimensions))
zs = [(o.matrix_world @ V(b)).z for o in objs for b in o.bound_box]; ys = [(o.matrix_world @ V(b)).y for o in objs for b in o.bound_box]
print("BBOX z", min(zs), max(zs), "y", min(ys), max(ys))
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 24
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
camd = bpy.data.cameras.new("CamRev"); cam = bpy.data.objects.new("CamRev", camd); sc.collection.objects.link(cam); sc.camera = cam
if not any(o.type == "LIGHT" for o in sc.objects):
    l = bpy.data.lights.new("Sol", "SUN"); l.energy = 3; lo = bpy.data.objects.new("Sol", l); sc.collection.objects.link(lo)
    lo.rotation_euler = (math.radians(55), 0, math.radians(-40))
for nome, pos, alvo, lente in [("lado", V((26, 0, 4.6)), V((0, 0, 4.6)), 50), ("cabeca", V((3.8, -9.6, 8.6)), V((0, -4.4, 7.8)), 60),
                               ("referencia", V((13.5, -15.0, 4.2)), V((0, 0.2, 4.6)), 50)]:
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
    sc.render.filepath = os.path.join(OUT, "vista_%s.png" % nome); bpy.ops.render.render(write_still=True)
