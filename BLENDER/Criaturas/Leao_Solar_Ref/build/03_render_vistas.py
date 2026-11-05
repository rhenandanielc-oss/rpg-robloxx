"""Renders ortograficos alinhados pixel a pixel com os recortes da referencia principal (perfil, frente, traseira)
+ 3/4 em perspectiva. Workbench, luz de estudio neutra, cor por atributo, fundo transparente (alfa = silhueta).
Uso: blender -b <arquivo.blend> -P 03_render_vistas.py -- <saida_dir> [nomes,a,ocultar]"""
import bpy, sys, os, math
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
OCULTAR = A[1].split(",") if len(A) > 1 else []
for o in bpy.data.objects:
    if any(t in o.name for t in OCULTAR if t): o.hide_render = True
sc = bpy.context.scene
K = 11.5 / 360.0; TOPO = (592 - 8) * K; KF = TOPO / (1240 - 623); KB = TOPO / (1238 - 624)
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "STUDIO"; sh.color_type = "VERTEX"; sh.show_cavity = True; sh.cavity_type = "WORLD"
sh.show_shadows = False; sh.show_specular_highlight = False
sc.render.film_transparent = True
sc.view_settings.view_transform = "Standard"
cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
def ortho(nome, loc, rot, escala, w, h):
    cam_d.type = "ORTHO"; cam_d.ortho_scale = escala
    cam.location = loc; cam.rotation_euler = [math.radians(a) for a in rot]
    sc.render.resolution_x, sc.render.resolution_y = w, h; sc.render.resolution_percentage = 100
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
# perfil: recorte x 0-1217, y 0-594 da referencia; cabeca a direita => camera em -X olhando +X
ortho("lado", (-80, -(608.5 - 620) * K, (592 - 297) * K), (90, 0, -90), 1217 * K, 1217, 594)
# frente: recorte x 0-608, y 610-1293 => camera em -Y
ortho("frente", ((304 - 335) * KF, -80, (1240 - 951.5) * KF), (90, 0, 0), 683 * KF, 608, 683)
# traseira: recorte x 609-1217, y 610-1293 => camera em +Y (direita da imagem = -X)
ortho("tras", (-(913 - 875) * KB, 80, (1238 - 951.5) * KB), (90, 0, 180), 683 * KB, 608, 683)
# 3/4 frontal-direita, perspectiva
cam_d.type = "PERSP"; cam_d.lens = 50
alvo = Vector((0, -1.5, 8.5)); az, el, dist = math.radians(-35), math.radians(12), 62
cam.location = alvo + Vector((math.sin(az) * math.cos(el) * dist * -1, -math.cos(az) * math.cos(el) * dist, math.sin(el) * dist))
cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.resolution_x, sc.render.resolution_y = 1000, 800
sc.render.filepath = os.path.join(OUT, "tres_quartos.png"); bpy.ops.render.render(write_still=True)
print("RENDER_OK", OUT)
