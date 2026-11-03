"""Folha de revisao da CABECA nos rugidos (03/11): para cada clipe, quadros em fases escolhidas, camera 3/4 frontal fixa
mirando a regiao media da cabeca no clipe (mostra giro, inclinacao, trancos e abertura da boca).
Uso: blender -b arq.blend -P render_cabeca_rugidos.py -- saida_dir clipe1,clipe2 [fases separadas por virgula]"""
import bpy, sys, os
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]; out = args[0]; quais = args[1].split(",")
FASES = [float(x) for x in args[2].split(",")] if len(args) > 2 else [0.0, 0.25, 0.4, 0.55, 0.7, 0.85]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 420, 340
cam = bpy.data.objects.get("cam_rev")
if cam is None:
    cam = bpy.data.objects.new("cam_rev", bpy.data.cameras.new("cam_rev")); sc.collection.objects.link(cam)
sc.camera = cam
def cabeca(): return A.matrix_world @ A.pose.bones["head"].head
for nome in quais:
    act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range)
    ps = []
    for k in range(9):
        sc.frame_set(int(f0 + (f1 - f0) * k / 8)); ps.append(cabeca().copy())
    c = sum(ps, Vector()) / len(ps) + Vector((0, -0.04, -0.03))
    cam.location = c + Vector((0.75, -0.95, 0.25)).normalized() * 0.95
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    for i, fa in enumerate(FASES):
        sc.frame_set(int(round(f0 + (f1 - f0) * fa)))
        sc.render.filepath = os.path.join(out, "%s_%d.png" % (nome, i)); bpy.ops.render.render(write_still=True)
A.animation_data.action = None
print("RENDER_OK")
