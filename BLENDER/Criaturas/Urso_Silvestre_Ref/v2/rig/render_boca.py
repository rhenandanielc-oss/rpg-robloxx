"""Close da boca/cabeca (frente 3/4 e lado) nos quadros indicados - conferencia de esticamento.
Uso: blender -b CR_Urso_v2_Anim.blend -P render_boca.py -- <saida_dir> Clipe:q[,Clipe:q...]"""
import bpy, sys, os
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["Urso_Rig"]
for o in [o for o in sc.objects if o.type == "EMPTY"]: o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
for o in [o for o in sc.objects if o.type in ("LIGHT", "CAMERA")]: bpy.data.objects.remove(o)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.5, 0.5, 1)
for nome, en, rot in (("K", 3.0, (0.9, 0, -2.4)), ("R", 1.5, (1.2, 0, 0.6))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16; sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 520, 420
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
if not arm.animation_data: arm.animation_data_create()
for item in A[1].split(","):
    nome, q = item.split(":"); q = int(q)
    arm.animation_data.action = bpy.data.actions["Urso_" + nome]; sc.frame_set(q + 1)
    pb = arm.pose.bones["Cabeca"]; h = arm.matrix_world @ pb.head; t = arm.matrix_world @ pb.tail
    alvo = h + (t - h) * 0.6 + V((0, 0, -0.35))
    for vista, off in (("frente", V((-2.6, -5.2, -0.6))), ("lado", V((-6.0, -0.4, 0.2)))):
        cam.location = alvo + off; cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "%s_%03d_%s.png" % (nome, q, vista)); bpy.ops.render.render(write_still=True)
print("BOCA_OK")
