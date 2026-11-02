"""Close-ups da BOCA aberta (revisao de rugido, 02/11): clipe e fracoes pedidas, 3 vistas (lado, 3/4 de frente,
frente-baixo) com a camera mirando o osso head. Uso: blender -b rig.blend -P render_boca.py -- <saida> "Clipe:0.6;..." """
import bpy, sys, os, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
SPEC = [(x.split(":")[0], [float(f) for f in x.split(":")[1].split(",")]) for x in a[1].split(";") if x]
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
for m in M.modifiers: m.show_viewport = True
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 640, 480
cam = sc.camera or bpy.data.objects.get("cam_rev")
w = sc.world or bpy.data.worlds.new("w"); sc.world = w
for nome, fr in SPEC:
    act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range)
    for x in fr:
        f = int(round(f0 + x * (f1 - f0))); sc.frame_set(f)
        pb = A.pose.bones["head"]; Mh = A.matrix_world @ pb.matrix
        c = Mh.translation; eixo = (Mh.to_3x3() @ V((0, 1, 0))).normalized()     # head: base -> focinho
        alvo = c + eixo * 0.12
        lado = V((0, 0, 1)).cross(eixo).normalized()
        for vn, pos in (("lado", alvo + lado * 0.55 + V((0, 0, 0.05))), ("frente", alvo + eixo * 0.55 + lado * 0.2 + V((0, 0, 0.08))),
                        ("baixo", alvo + eixo * 0.45 - V((0, 0, 0.22)) + lado * 0.12)):
            cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = 50
            sc.render.filepath = os.path.join(OUT, "%s_%03d_%s.png" % (nome, f, vn)); bpy.ops.render.render(write_still=True)
print("BOCA_OK", OUT)
