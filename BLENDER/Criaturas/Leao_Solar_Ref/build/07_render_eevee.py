"""Renders EEVEE com materiais reais e luz neutra IGUAL para todas as vistas: mundo cinza uniforme + sol suave de cima.
Mesmas cameras ortograficas do 03 (alinhadas aos recortes da referencia), 3/4, closes do rosto e do tufo, e vista de
tamanho de jogo (3/4 pequeno). Uso: blender -b <arquivo.blend> -P 07_render_eevee.py -- <saida_dir>"""
import bpy, sys, os, math
from mathutils import Vector
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
K = 11.5 / 360.0; TOPO = (592 - 8) * K; KF = TOPO / (1240 - 623); KB = TOPO / (1238 - 624)
sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = True
sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"
try: sc.eevee.taa_render_samples = 64
except Exception: pass
w = bpy.data.worlds.new("Neutro"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes.get("Background"); bg.inputs[0].default_value = (0.62, 0.62, 0.62, 1); bg.inputs[1].default_value = 1.0
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.2; sol.angle = math.radians(40)
so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
def ortho(nome, loc, rot, escala, w_, h_):
    cam_d.type = "ORTHO"; cam_d.ortho_scale = escala
    cam.location = loc; cam.rotation_euler = [math.radians(a) for a in rot]
    sc.render.resolution_x, sc.render.resolution_y = w_, h_
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
def persp(nome, alvo, az, el, dist, lens, w_, h_):
    cam_d.type = "PERSP"; cam_d.lens = lens; alvo = Vector(alvo)
    cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)),
                                  math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = w_, h_
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
ortho("lado", (-80, -(608.5 - 620) * K, (592 - 297) * K), (90, 0, -90), 1217 * K, 1217, 594)
ortho("frente", ((304 - 335) * KF, -80, (1240 - 951.5) * KF), (90, 0, 0), 683 * KF, 608, 683)
ortho("tras", (-(913 - 875) * KB, 80, (1238 - 951.5) * KB), (90, 0, 180), 683 * KB, 608, 683)
persp("tres_quartos", (0, -1.5, 8.5), -35, 12, 62, 50, 1000, 800)
persp("tres_quartos_tras", (0, 1.0, 8.0), 145, 14, 64, 50, 1000, 800)
# closes: rosto (perfil e frente) no mesmo recorte da referencia; tufo
ortho("close_rosto_lado", (-80, -(1035 - 620) * K, (592 - 150) * K), (90, 0, -90), 220 * K, 510, 660)
ortho("close_rosto_frente", ((335 - 335) * KF + (346 - 335) * KF, -80, (1240 - 765) * KF), (90, 0, 0), 230 * KF, 630, 690)
ortho("close_tufo", (-80, -(160 - 620) * K, (592 - 440) * K), (90, 0, -90), 260 * K, 520, 420)
persp("close_juba_34", (0, -9.0, 13.0), -40, 10, 30, 50, 900, 900)
persp("jogo_34", (0, -1.5, 8.5), -35, 18, 62, 50, 200, 160)
print("RENDER_OK", OUT)
