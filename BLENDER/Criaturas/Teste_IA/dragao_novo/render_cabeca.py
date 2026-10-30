"""Close-ups da cabeca (lado, frente, cima, 3/4, 3/4 de tras) do CR_Dragao_master.blend.
Uso: blender -b CR_Dragao_master.blend -P render_cabeca.py -- <saida_dir>"""
import bpy, sys, os
from mathutils import Vector as V
out = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; cam = sc.camera; sc.render.resolution_x, sc.render.resolution_y = 800, 600
alvo = V((0, -0.84, 0.78))
for nome, d in (("lado", (-1, 0, 0.05)), ("frente", (0, -1, 0.12)), ("cima", (0.001, 0.05, 1)), ("34", (-0.8, -0.8, 0.35)),
                ("34_tras", (-0.8, 0.7, 0.45)), ("baixo", (-0.6, -0.6, -0.35))):
    cam.location = alvo + V(d).normalized() * 0.95; cam.data.lens = 60
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, "cab_%s.png" % nome); bpy.ops.render.render(write_still=True)
