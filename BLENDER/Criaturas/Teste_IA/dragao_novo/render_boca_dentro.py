"""Revisao do INTERIOR da boca (02/11): pose fixa (clipe+fracao) e 4 cameras fixas no espaco da cabeca: de frente para
dentro, 3/4 baixo, lado e canto (cantos da boca). Uso: blender -b rig.blend -P render_boca_dentro.py -- <saida> Clipe:frac [rotulo]"""
import bpy, sys, os
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
clipe, fr = a[1].split(":"); fr = float(fr); rot = a[2] if len(a) > 2 else "x"
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
for o in sc.objects:
    if o.type == "MESH":
        for m in o.modifiers: m.show_viewport = True
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 640, 480
cam = sc.camera
act = bpy.data.actions["Silverwing_" + clipe]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
f0, f1 = map(int, act.frame_range); sc.frame_set(int(round(f0 + fr * (f1 - f0))))
def P(n, tail=False):
    pb = A.pose.bones[n]; return A.matrix_world @ (pb.tail if tail else pb.head)
dobra = P("mouth_lower")                                         # articulacao da mandibula
tipU, tipL = P("mouth_upper_tip"), P("mouth_lower_tip")
boca = (tipU + tipL) / 2; fw = (boca - dobra).normalized()       # eixo da abertura (articulacao -> ponta)
up = (tipU - tipL).normalized(); sd = fw.cross(up).normalized()
for vn, pos, alvo in (("dentro", boca + fw * 0.22, dobra), ("baixo", boca + fw * 0.18 - up * 0.10 + sd * 0.07, dobra + fw * 0.05),
                      ("lado", dobra + fw * 0.1 + sd * 0.32, dobra + fw * 0.1), ("canto", dobra + sd * 0.15 + fw * 0.05, dobra + fw * 0.03)):
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = 35; cam.data.clip_start = 0.005
    sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (rot, vn)); bpy.ops.render.render(write_still=True)
print("DENTRO_OK", OUT)
