"""Close-ups laterais/frontais da cabeca (HIGH e LOW) para estudar boca, labios e olhos. So leitura.
Uso: blender -b <blend> -P close_cabeca.py -- <saida_dir> <objeto> [objeto2...]"""
import bpy, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; cam = sc.camera; camd = cam.data
sc.render.resolution_x, sc.render.resolution_y = 1000, 800
for nome in A[1:]:
    for o in sc.objects:
        if o.type == "MESH" and not o.name.startswith("Plane"): o.hide_render = (o.name != nome)
    ob = bpy.data.objects[nome]; vs = [ob.matrix_world @ v.co for v in ob.data.vertices]
    yf = min(v.y for v in vs); nar = min(vs, key=lambda v: v.y)
    alvo = V((0, yf + 0.9, nar.z - 0.1))
    for vista, pos, lente in (("lado", alvo + V((6, 0, 0)), 70), ("frente", alvo + V((0, -6, 0.3)), 70), ("baixo34", alvo + V((3.5, -3.5, -1.2)), 70)):
        cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
        sc.render.filepath = os.path.join(OUT, "close_%s_%s.png" % (nome, vista)); bpy.ops.render.render(write_still=True)
    print("NARIZ", nome, tuple(round(c, 2) for c in nar))
