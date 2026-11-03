"""Quadros seguidos em volta dos picos de aceleracao angular (conferencia visual dos estalos), perfil das patas.
Uso: blender -b CR_Urso_v2_Anim.blend -P render_picos.py -- <saida_dir> Clipe:q0-q1[,Clipe:q0-q1...]"""
import bpy, sys, os
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["Urso_Rig"]
for o in [o for o in sc.objects if o.type == "EMPTY"]: o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
for o in [o for o in sc.objects if o.type in ("LIGHT", "CAMERA")]: bpy.data.objects.remove(o)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.42, 1)
for nome, en, rot in (("K", 3.0, (0.84, 0, -0.61)), ("R", 2.0, (2.1, 0, 2.8))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=120); mc = bpy.data.materials.new("C"); mc.use_nodes = True; bpy.context.object.data.materials.append(mc)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 8; sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 420, 330
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 45
pos, alvo = V((-17, -2.0, 3.6)), V((0, -0.5, 3.2)); cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
if not arm.animation_data: arm.animation_data_create()
for item in A[1].split(","):
    nome, faixa = item.split(":"); q0, q1 = [int(x) for x in faixa.split("-")]
    arm.animation_data.action = bpy.data.actions["Urso_" + nome]
    for q in range(q0, q1 + 1):
        sc.frame_set(q + 1)                                  # acao comeca no quadro 1 (indice 0 do JSON)
        sc.render.filepath = os.path.join(OUT, "%s_%03d.png" % (nome, q)); bpy.ops.render.render(write_still=True)
print("PICOS_OK")
