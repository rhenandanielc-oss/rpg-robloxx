"""16/11/2026: quadros de revisao de um clipe (3/4 de perto, pescoco e dorso) para comparar o pelo antes/depois.
Uso: blender -b <blend> -P comportamento/render_pelo.py -- <dir_saida> <Clipe>"""
import bpy, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True); nome = A[1]
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for o in sc.objects:
    if o.type == "MESH" and o is not LO: o.hide_render = True
    if o.type == "EMPTY": o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
act = bpy.data.actions["Lobo_" + nome]; arm.animation_data_create(); arm.animation_data.action = act
if hasattr(act, "slots") and len(act.slots): arm.animation_data.action_slot = act.slots[0]
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 12; sc.render.resolution_x, sc.render.resolution_y = 640, 720
w = bpy.data.worlds.new("Wp"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.70, 0.78, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
sol = bpy.data.objects.new("SolP", bpy.data.lights.new("SolP", "SUN")); sc.collection.objects.link(sol); sol.data.energy = 3.5
sol.rotation_euler = (math.radians(40), 0, math.radians(-35))
bpy.ops.mesh.primitive_plane_add(size=60)
cam = bpy.data.objects.new("CamP", bpy.data.cameras.new("CamP")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 40
alvo = V((0, -2.2, 5.6)); cam.location = alvo + V((9.0, 3.0, 4.0)); cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
n = int(act.frame_range[1])
for q in range(1, n + 1):
    sc.frame_set(q); sc.render.filepath = os.path.join(OUT, "f%04d.png" % q); bpy.ops.render.render(write_still=True)
print("PELO_OK", nome, n)
