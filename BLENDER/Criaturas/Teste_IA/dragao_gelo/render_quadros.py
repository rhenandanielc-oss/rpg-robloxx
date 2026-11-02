"""Renders de certificacao (02/11): quadros escolhidos de clipes do GL_Dragao_M2M.blend, com piso cinza em z=0 para
ver apoio/penetracao, e (modo video) TODOS os quadros de um clipe para montar MP4 (meshy/video_mp4.py).
Uso: blender -b rig.blend -P render_quadros.py -- <saida_dir> "Clipe:0,0.5;Clipe2:0.3" [vista=tres_q|lado|frente|baixo|cima]
     [piso=1] [video=0] [res=960x540]"""
import bpy, sys, os, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
SPEC = [(x.split(":")[0], [float(f) for f in x.split(":")[1].split(",")] if ":" in x else [0.0]) for x in a[1].split(";") if x]
VISTA = a[2] if len(a) > 2 else "tres_q"; PISO = (a[3] if len(a) > 3 else "1") == "1"
VIDEO = (a[4] if len(a) > 4 else "0") == "1"; RES = [int(v) for v in (a[5] if len(a) > 5 else "960x540").split("x")]
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
for m in M.modifiers: m.show_viewport = True
for o in sc.objects:
    if o.type == "LIGHT": o.hide_render = True
w = bpy.data.worlds.new("Ceu_Cert"); sc.world = w
if w.node_tree is None: w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.62, 0.72, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.35
for nome, en, cor, rot in (("Sol", 4.0, (1.0, 0.97, 0.94), (math.radians(50), 0, math.radians(30))),
                           ("Contra", 3.0, (0.85, 0.92, 1.0), (math.radians(115), 0, math.radians(200))),
                           ("Preench", 1.2, (0.88, 0.94, 1.0), (math.radians(60), 0, math.radians(-120)))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.color = cor; lo = bpy.data.objects.new(nome, l)
    sc.collection.objects.link(lo); lo.rotation_euler = rot
if PISO:
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0)); pl = bpy.context.active_object
    mt = bpy.data.materials.new("Piso"); mt.use_nodes = True
    mt.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.32, 0.34, 0.33, 1); pl.data.materials.append(mt)
    # grade: linhas a cada 0,1 (1,75 stud) para ver deslizamento
    for k in range(-30, 31):
        for eixo in (0, 1):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(k * 0.1 if eixo == 0 else 0, k * 0.1 if eixo == 1 else 0, 0.0005))
            c = bpy.context.active_object; c.scale = (0.002, 6, 0.0004) if eixo == 0 else (6, 0.002, 0.0004)
            c.data.materials.append(bpy.data.materials.get("Linha") or bpy.data.materials.new("Linha"))
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = RES
sc.view_settings.view_transform = "AgX"
cam = sc.camera
VISTAS = {"tres_q": (V((1.9, -2.9, 1.15)), V((0, -0.25, 0.40)), 38), "lado": (V((-3.4, -0.25, 0.55)), V((0, -0.25, 0.40)), 38),
          "frente": (V((0.0, -3.4, 0.70)), V((0, -0.25, 0.45)), 38), "baixo": (V((1.6, -2.6, 0.12)), V((0, -0.25, 0.30)), 34),
          "cima": (V((1.2, 1.6, 3.2)), V((0, -0.2, 0.35)), 34), "tras": (V((-1.4, 3.2, 1.2)), V((0, -0.2, 0.40)), 38)}
pos, alvo, lente = VISTAS[VISTA]
cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lente
for nome, fr in SPEC:
    act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range)
    quadros = list(range(f0, f1 + 1)) if VIDEO else [int(round(f0 + x * (f1 - f0))) for x in fr]
    for i, f in enumerate(quadros):
        sc.frame_set(f)
        sc.render.filepath = os.path.join(OUT, ("f_%04d" % i) if VIDEO else "%s_%s_%03d" % (nome, VISTA, f)) + ".png"
        bpy.ops.render.render(write_still=True)
print("RENDER_OK", OUT)
