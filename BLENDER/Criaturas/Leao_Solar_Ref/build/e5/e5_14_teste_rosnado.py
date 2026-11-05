"""E5 Fase B: teste visual do rosnado (labios sobem, mandibula entreabre, focinho/palpebra). Uso: blender -b <rig.blend> -P e5_14_teste_rosnado.py -- <saida_dir>"""
import bpy, sys, os, math
from mathutils import Vector, Quaternion
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True); sc = bpy.context.scene
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]; PB = arm.pose.bones; BD = arm.data.bones
for pb in PB: pb.rotation_mode = "QUATERNION"
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.4; so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
def vista(nome, alvo, az, el, dist):
    alvo = Vector(alvo); cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = sc.render.resolution_y = 380; sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
def rot_local(nome, q): r = BD[nome].matrix_local.to_3x3(); return (r.inverted() @ q.to_matrix() @ r).to_quaternion()
def pose(labio, mand, palp=0.0):
    for pb in PB: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    for k in ("D", "E"):
        PB["Labio_" + k].location = BD["Labio_" + k].matrix_local.to_3x3().inverted() @ Vector((0, 0.04 * labio / 0.3, labio))
        PB["Palpebra_" + k].rotation_quaternion = rot_local("Palpebra_" + k, Quaternion((1, 0, 0), math.radians(palp)))
    z0 = (arm.matrix_world @ PB["Mandibula"].tail).z
    PB["Mandibula"].rotation_quaternion = rot_local("Mandibula", Quaternion((1, 0, 0), math.radians(mand)))
    bpy.context.view_layer.update()
    if (arm.matrix_world @ PB["Mandibula"].tail).z > z0 and mand: PB["Mandibula"].rotation_quaternion = rot_local("Mandibula", Quaternion((1, 0, 0), math.radians(-mand))); bpy.context.view_layer.update()
for nome, lab, mand, palp in (("0_neutro", 0, 0, 0), ("1_lab015", 0.15, 0, -10), ("2_lab030", 0.30, 4, -15), ("3_lab030_m12", 0.30, 12, -18), ("4_lab040_m20", 0.40, 20, -18)):
    pose(lab, mand, palp); vista(nome + "_frente", (-0.2, -14.6, 12.8), 0, 4, 5.5); vista(nome + "_34", (-0.2, -14.4, 12.8), -40, 8, 6)
print("OK")
