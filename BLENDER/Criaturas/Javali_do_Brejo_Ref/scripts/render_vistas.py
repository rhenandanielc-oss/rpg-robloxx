"""Vistas fixas de comparacao (frente, perfil, 3/4, miniatura) em pose de descanso do rig, mesmas cameras para base e variante.
modo 'argila' = material cinza unico (forma/proporcao, antes do acabamento); 'textura' = materiais do arquivo.
Uso: blender -b <arquivo.blend> -P scripts/render_vistas.py -- <pasta_saida> <prefixo> <argila|textura>"""
import bpy, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); PRE = A[1]; MODO = A[2]
os.makedirs(OUT, exist_ok=True); sc = bpy.context.scene
arm = next(o for o in sc.objects if o.type == "ARMATURE"); MALHAS = [o for o in sc.objects if o.type == "MESH" and o.parent == arm]
for o in sc.objects:
    if o.type in ("CAMERA", "LIGHT"): bpy.data.objects.remove(o)
    elif o.type == "MESH" and o not in MALHAS: o.hide_render = True
arm.data.pose_position = "REST"; bpy.context.view_layer.update()
if MODO == "argila":
    m = bpy.data.materials.new("Argila"); b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.55, 0.53, 0.50, 1); b.inputs["Roughness"].default_value = 0.85
    for o in MALHAS: o.data.materials[0] = m
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False
try: sc.eevee.taa_render_samples = 32
except Exception: pass
w = bpy.data.worlds.new("C"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.50, 0.46, 0.44, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.9; sc.world = w
for nome, en, rot in (("Sol", 3.0, (50, 0, -40)), ("Contra", 1.2, (60, 0, 150))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo)
    lo.rotation_euler = [math.radians(x) for x in rot]
cd = bpy.data.cameras.new("Q"); cam = bpy.data.objects.new("Q", cd); sc.collection.objects.link(cam); sc.camera = cam
# frente = -Y. Enquadramento fixo (cabe o focinho mais longo da variante).
VISTAS = {"frente": ((0, -4.0, 0.44), (0, 0, 0.42), "ORTHO", 1.15, (700, 700)),
          "perfil": ((4.0, -0.02, 0.42), (0, -0.02, 0.42), "ORTHO", 1.85, (1000, 600)),
          "34": ((2.05, -2.15, 1.25), (0, -0.05, 0.38), "PERSP", 50, (900, 700)),
          "miniatura": ((2.05, -2.15, 1.25), (0, -0.05, 0.38), "PERSP", 50, (96, 75)),
          "rosto_perfil": ((3.0, -0.52, 0.55), (0, -0.52, 0.55), "ORTHO", 0.72, (620, 520)),
          "rosto_34": ((1.10, -1.75, 0.78), (0, -0.55, 0.48), "PERSP", 85, (620, 520)),
          "baixo_34": ((1.6, -1.2, 0.12), (0, 0.0, 0.30), "PERSP", 40, (900, 520))}         # ventre e patas (lama)
for vista, (loc, alvo, tipo, val, res) in VISTAS.items():
    cam.location = loc; cam.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); cd.type = tipo
    if tipo == "ORTHO": cd.ortho_scale = val
    else: cd.lens = val
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.render.filepath = os.path.join(OUT, f"{PRE}_{MODO}_{vista}.png"); bpy.ops.render.render(write_still=True)
print("VISTAS_OK", PRE, MODO)
