"""Renders de revisao do CR_Crocodilo_Ref (nao salva o .blend). Uso:
blender -b CR_Crocodilo_Ref.blend -P render_revisao.py -- <saida_dir> <prefixo> [vistas,separadas,por,virgula]"""
import bpy, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(A[0]); PRE = A[1]; os.makedirs(OUT, exist_ok=True)
QUAIS = A[2].split(",") if len(A) > 2 else None
sc = bpy.context.scene; cam = sc.camera; cd = cam.data
ORTO = {"lado": (V((40, -0.2, 3.4)), V((0, -0.2, 3.4)), 31.0), "frente": (V((0, -40, 3.6)), V((0, 0, 3.6)), 12.0),
        "topo": (V((0, -0.3, 40)), V((0, -0.3, 0)), 31.0)}
PERSP = {"ref": (V((25.5, -19.5, 6.4)), V((0.8, -0.8, 3.1)), 33),            # camera equivalente a referencia (3/4 frente-esquerda)
         "34_tras": (V((-20, 17, 11)), V((0, 0.5, 3.6)), 32), "cabeca": (V((9.5, -18.5, 8.0)), V((0.3, -10.8, 5.0)), 40),
         "cabeca_lado": (V((9.0, -11.0, 5.2)), V((0, -11.0, 4.9)), 45), "boca_frente": (V((0.0, -20.0, 5.6)), V((0, -11.0, 4.7)), 60),
         "boca_dentro": (V((2.2, -17.5, 7.0)), V((0, -10.4, 4.3)), 40), "pata": (V((8.5, -9.5, 2.0)), V((3.6, -4.8, 0.9)), 40),
         "ventre": (V((12, -2, -1.8)), V((0, -1, 2.5)), 30)}
for nome in (QUAIS or list(ORTO) + list(PERSP)):
    if nome in ORTO:
        p, a, esc = ORTO[nome]; cd.type = "ORTHO"; cd.ortho_scale = esc
    else:
        p, a, lente = PERSP[nome]; cd.type = "PERSP"; cd.lens = lente
    cam.location = p; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y" if nome != "topo" else "Y").to_euler()
    if nome == "topo": cam.rotation_euler = (0, 0, 0)
    cd.clip_end = 500
    sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (PRE, nome)); bpy.ops.render.render(write_still=True)
print("RENDER_OK")
