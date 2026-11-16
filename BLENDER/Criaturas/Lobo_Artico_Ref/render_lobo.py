"""Renders de revisao do Lobo Artico sob iluminacao NEUTRA (estudio cinza, luz branca), sem cenario.
Vistas: pose_ref (camera aproximada da referencia), frente, lado (esquerdo, visivel na ref), lado_d (direito,
area oculta), tras, 34, rosto, ombro (marca), cristais.
Uso: blender -b <arquivo.blend> -P render_lobo.py -- <dir_saida> [vista1,vista2,...] [amostras]"""
import bpy, sys, os, math
from mathutils import Vector as V
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
SO = ARGS[1].split(",") if len(ARGS) > 1 and ARGS[1] != "todas" else None
AMOSTRAS = int(ARGS[2]) if len(ARGS) > 2 else 48
sc = bpy.context.scene
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA") or o.name.startswith("Chao"): bpy.data.objects.remove(o)
w = bpy.data.worlds.new("Estudio"); sc.world = w
if w.node_tree is None: w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.42, 0.43, 0.45, 1); bg.inputs[1].default_value = 0.55
for nome, en, rot in (("Chave", 3.2, (50, 0, 35)), ("Contra", 2.2, (120, 0, 205)), ("Preench", 0.9, (65, 0, -120))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.color = (1, 1, 1); l.angle = math.radians(6)
    lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = [math.radians(a) for a in rot]
bpy.ops.mesh.primitive_plane_add(size=80); chao = bpy.context.object; chao.name = "Chao"
mch = bpy.data.materials.new("Chao_Neutro")
if mch.node_tree is None: mch.use_nodes = True
pb = mch.node_tree.nodes["Principled BSDF"]; pb.inputs["Base Color"].default_value = (0.30, 0.30, 0.31, 1); pb.inputs["Roughness"].default_value = 0.9
chao.data.materials.append(mch)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = AMOSTRAS
for k, v in (("use_raytracing", True), ("use_shadows", True)):
    if hasattr(sc.eevee, k): setattr(sc.eevee, k, v)
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Base Contrast"
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
camd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", camd); sc.collection.objects.link(cam); sc.camera = cam
VISTAS = [("pose_ref", V((17.5, -11.0, 4.6)), V((0, -1.0, 3.9)), 45),
          ("frente", V((0, -24.0, 4.6)), V((0, 0, 3.9)), 50), ("lado", V((24.0, -0.9, 4.0)), V((0, -0.9, 3.9)), 50),
          ("lado_d", V((-24.0, -0.9, 4.0)), V((0, -0.9, 3.9)), 50), ("tras", V((0, 24.0, 4.6)), V((0, 0, 3.9)), 50),
          ("34", V((-15.0, -16.0, 8.5)), V((0, -0.6, 3.8)), 50),
          ("rosto", V((3.6, -13.0, 7.3)), V((0.0, -6.0, 6.5)), 60), ("ombro", V((7.8, -4.6, 5.6)), V((0.5, -3.1, 5.0)), 55),
          ("cristais", V((4.8, -5.4, 9.2)), V((0.2, -2.5, 6.4)), 55)]
for nome, pos, alvo, lente in VISTAS:
    if SO and nome not in SO: continue
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
    sc.render.filepath = os.path.join(OUT, "vista_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("RENDER_OK", OUT)
