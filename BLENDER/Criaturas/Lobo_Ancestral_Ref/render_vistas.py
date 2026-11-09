"""Renderiza as 6 vistas de revisao de um .blend ja montado (Lobo_Meshy + luzes/camera do normalizar_meshy). Nao salva.
Uso: blender -b <arquivo.blend> -P render_vistas.py -- <saida_dir> [objeto]"""
import bpy, sys, os
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; cam = sc.camera; camd = cam.data
ob = bpy.data.objects[A[1] if len(A) > 1 else "Lobo_Meshy"]
vs = [ob.matrix_world @ v.co for v in ob.data.vertices]
yf = min(v.y for v in vs); zc = max(v.z for v in vs)
VISTAS = [("referencia", V((13.5, -15.0, 4.2)), V((0, 0.2, 4.6)), 50), ("lado", V((26, 0.0, 4.6)), V((0, 0, 4.6)), 50),
          ("frente", V((0, -26, 5.2)), V((0, 0, 4.8)), 50), ("tras", V((0, 26, 5.2)), V((0, 0, 4.6)), 50),
          ("tres_quartos", V((15, -15, 9.0)), V((0, 0, 4.4)), 50),
          ("cabeca", V((3.8, yf - 4.6, zc - 0.3)), V((0, yf + 1.0, zc - 1.4)), 60)]
for nome, pos, alvo, lente in VISTAS:
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
    sc.render.filepath = os.path.join(OUT, "vista_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("VISTAS_OK")
