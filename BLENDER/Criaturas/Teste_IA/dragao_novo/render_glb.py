"""Renderiza um GLB do dragao (com as texturas dele) nas vistas de revisao, com a mesma luz do master.
Uso: blender -b --factory-startup -P render_glb.py -- <arquivo.glb> <saida_dir> <prefixo>"""
import bpy, sys, os, math
from mathutils import Vector as V
glb, out, pre = sys.argv[sys.argv.index("--") + 1:][:3]; os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=glb)
# o Meshy devolve o modelo normalizado (outra escala/posicao): volta ao tamanho do master (envergadura 4,4 u, pes em z=0)
malhas = [o for o in sc.objects if o.type == "MESH"]
pts = [o.matrix_world @ V(c) for o in malhas for c in o.bound_box]
mn = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
k = 4.40 / (mx.x - mn.x)
raizes = [o for o in sc.objects if o.parent is None]
for o in raizes:
    o.matrix_world = __import__("mathutils").Matrix.Translation(V((-(mn.x + mx.x) / 2 * k, -(mn.y + mx.y) / 2 * k + 0.30, -mn.z * k))) @ \
                     __import__("mathutils").Matrix.Scale(k, 4) @ o.matrix_world
print("ESCALA", round(k, 4))
for o in sc.objects:
    if o.type == "MESH":
        for m in o.data.materials:
            if m: m.use_backface_culling = False
w = bpy.data.worlds.new("Ceu"); sc.world = w
if w.node_tree is None: w.use_nodes = True
bg = w.node_tree.nodes["Background"]; ceu = w.node_tree.nodes.new("ShaderNodeTexSky")
for t in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA", "HOSEK_WILKIE"):
    try: ceu.sky_type = t; break
    except Exception: pass
if hasattr(ceu, "sun_elevation"): ceu.sun_elevation = math.radians(30)
w.node_tree.links.new(ceu.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.10
for nome, en, cor, rot in (("Sol", 4.0, (1.0, 0.92, 0.80), (math.radians(50), 0, math.radians(30))),
                           ("Contra", 3.0, (1.0, 0.85, 0.70), (math.radians(115), 0, math.radians(200))),
                           ("Preench", 1.2, (1.0, 0.86, 0.72), (math.radians(60), 0, math.radians(-120)))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.color = cor; lo = bpy.data.objects.new(nome, l)
    sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=40); chao = bpy.context.object
mc = bpy.data.materials.new("Chao")
if mc.node_tree is None: mc.use_nodes = True
mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.26, 0.21, 0.16, 1); chao.data.materials.append(mc)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 64
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
camd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", camd); sc.collection.objects.link(cam); sc.camera = cam
for nome, pos, alvo, lente in (("conceito", V((-1.6, -2.3, 0.62)), V((0, -0.2, 0.62)), 35), ("cabeca", V((-0.85, -1.75, 1.02)), V((0, -0.82, 0.77)), 62),
                               ("34_tras", V((2.9, 3.4, 2.0)), V((0, 0.1, 0.55)), 42), ("lado", V((-5.6, 0.25, 0.75)), V((0, 0.25, 0.5)), 42)):
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
    sc.render.filepath = os.path.join(out, "%s_%s.png" % (pre, nome)); bpy.ops.render.render(write_still=True)
print("RENDER_GLB_OK")
