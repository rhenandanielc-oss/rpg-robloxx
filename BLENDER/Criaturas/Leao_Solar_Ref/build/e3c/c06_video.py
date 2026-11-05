"""E3b: video curto da abertura e fechamento da boca (0 -> 32 -> 0 graus, 24 qps, ~3 s), luz neutra das pranchas.
A lingua acompanha a mandibula e enrola a ponta de leve (osso Lingua, movimento discreto).
Uso: blender -b <e3b.blend> -P c06_video.py -- <saida.mp4> <vista: 34|frente|perfil> [res]"""
import bpy, sys, os, math
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); VISTA = A[1]; RES = int(A[2]) if len(A) > 2 else 640
sc = bpy.context.scene; sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = False
sc.view_settings.view_transform = "Standard"
w = bpy.data.worlds.new("Neutro"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.2; sol.angle = math.radians(40)
so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
CX = -0.22
VIS = {"34": ((CX, -14.3, 12.4), -40, 6, 8.0, 50), "frente": ((CX, -14.8, 12.3), 0, 3, 6.5, 50), "perfil": ((CX, -14.0, 12.3), -90, 0, 8.0, 50)}
alvo, az, el, dist, lens = VIS[VISTA]; alvo = Vector(alvo); cam_d.lens = lens
cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)),
                              math.sin(math.radians(el)))) * dist
cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
arm = bpy.data.objects["Leao_Rig_Teste_Boca"]; pb = arm.pose.bones["Mandibula"]; pb.rotation_mode = "XYZ"
pl = arm.pose.bones["Lingua"]; pl.rotation_mode = "XYZ"
def queixo_z(a):
    pb.rotation_euler = (math.radians(a), 0, 0); bpy.context.view_layer.update(); return (arm.matrix_world @ pb.tail).z
SINAL = 1 if queixo_z(10) < queixo_z(0) else -1
CHAVES = [(1, 0), (8, 0), (32, 32), (42, 32), (66, 0), (76, 0)]       # (quadro, graus): pausa, abre, segura, fecha, pausa
for f, g in CHAVES:
    pb.rotation_euler = (math.radians(SINAL * g), 0, 0); pb.keyframe_insert("rotation_euler", frame=f)
    pl.rotation_euler = (math.radians(-SINAL * 0.18 * g), 0, 0); pl.keyframe_insert("rotation_euler", frame=f)
sc.frame_start, sc.frame_end = 1, 76; sc.render.fps = 24
sc.render.resolution_x = sc.render.resolution_y = RES
im = sc.render.image_settings
try: im.media_type = "VIDEO"
except Exception: pass
im.file_format = "FFMPEG"; sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"
sc.render.ffmpeg.constant_rate_factor = "HIGH"
sc.render.filepath = OUT
bpy.ops.render.render(animation=True)
print("VIDEO_OK", OUT)
