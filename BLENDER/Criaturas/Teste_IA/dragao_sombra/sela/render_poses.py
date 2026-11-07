"""Renders rapidos de poses de qualquer rig de dragao (Silverwing_Rig), sem sela: vistas 3/4 e frente.
Uso: POSES=Parado:0.3,Andar:0.5 blender -b <rig.blend> -P sela/render_poses.py -- <saida_dir> <prefixo>"""
import bpy, os, sys
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT, PRE = os.path.abspath(a[0]), a[1]; os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
for o in sc.objects:
    if o.name.startswith("chao_revisao"): o.hide_render = True
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 800, 600
cam = bpy.data.objects.new("CamPoses", bpy.data.cameras.new("CamPoses")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 40
if not [o for o in sc.objects if o.type == "LIGHT"]:
    l = bpy.data.objects.new("SolP", bpy.data.lights.new("SolP", "SUN")); l.data.energy = 3.2; sc.collection.objects.link(l); l.rotation_euler = (0.7, 0.2, 0.8)
bpy.ops.mesh.primitive_plane_add(size=40); ch = bpy.context.object
mt = bpy.data.materials.new("chaoP"); mt.use_nodes = True; mt.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.31, 0.29, 1); ch.data.materials.append(mt)
if not A.animation_data: A.animation_data_create()
for item in os.environ.get("POSES", "Parado:0.3").split(","):
    nome, fr = item.split(":"); act = bpy.data.actions["Silverwing_" + nome]
    A.animation_data.action = act
    if act.slots: A.animation_data.action_slot = act.slots[0]
    f0, f1 = act.frame_range; sc.frame_set(int(f0 + (f1 - f0) * float(fr)))
    alvo = A.matrix_world @ A.pose.bones["spine_1"].head + V((0, 0, 0.02))
    for vn, d in (("34", V((1.6, -1.6, 0.9))), ("frente", V((0.3, -2.4, 0.5)))):
        cam.location = alvo + d; cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "%s_%s_%s.png" % (PRE, nome, vn)); bpy.ops.render.render(write_still=True)
print("POSES_OK")
