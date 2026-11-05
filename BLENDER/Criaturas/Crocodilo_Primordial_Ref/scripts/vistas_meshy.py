"""Vistas de revisao enquadradas no Meshy normalizado (32 studs; cabeca em y ~ -16). Nao salva.
Uso: blender -b <blend> -P vistas_meshy.py -- <saida_dir> <prefixo>"""
import bpy, sys, os
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT, PRE = os.path.abspath(A[0]), A[1]; os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; cam = sc.camera; cd = cam.data
VISTAS = {"ref": (V((27.0, -21.0, 6.0)), V((0.8, -1.2, 2.7)), 33, None), "lado": (V((40, 0, 3)), V((0, 0, 3)), 0, 34),
          "cabeca": (V((8.0, -21.0, 6.5)), V((0, -12.5, 3.4)), 40, None), "boca": (V((4.5, -21.5, 4.4)), V((0, -13.0, 3.2)), 45, None),
          "queixo": (V((5.0, -18.5, 0.2)), V((0, -12.5, 2.3)), 40, None), "ventre": (V((11, -4, -0.6)), V((0, -2, 1.6)), 30, None),
          "topo": (V((0, 0, 40)), V((0, 0.01, 0)), 0, 34)}
for nome in (A[2].split(",") if len(A) > 2 else VISTAS):
    p, a, lente, orto = VISTAS[nome]
    cam.location = p; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y").to_euler()
    if orto: cd.type = "ORTHO"; cd.ortho_scale = orto
    else: cd.type = "PERSP"; cd.lens = lente
    sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (PRE, nome)); bpy.ops.render.render(write_still=True)
print("VISTAS_OK")
