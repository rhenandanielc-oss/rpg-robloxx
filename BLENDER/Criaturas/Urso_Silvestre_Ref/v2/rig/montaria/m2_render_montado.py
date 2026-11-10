"""Montaria M2: video do cavaleiro de TESTE sentado (preso a Coluna2) com o urso nos clipes Repouso, Andar, Corrida e VirarE
(no lugar, como os clipes: o jogo move o modelo). So leitura. Uso:
blender -b CR_Urso_v2_M2_montaria.blend -P m2_render_montado.py -- <saida> [res=450]"""
import bpy, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); RES = int(A[1]) if len(A) > 1 else 450
os.makedirs(OUT, exist_ok=True); R = math.radians; sc = bpy.context.scene; sc.render.fps = 30
arm = bpy.data.objects["Urso_Rig"]; ra = bpy.data.objects["TESTE_Manequim_R15aprox_Rig"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
ra.animation_data.action = bpy.data.actions["DEMO_Cav_Sentado"]
arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
sc.frame_set(1); bpy.context.view_layer.update()
BL = arm.data.bones["Coluna2"].matrix_local
def osso(): return arm.matrix_world @ arm.pose.bones["Coluna2"].matrix @ BL.inverted()
REL = osso().inverted() @ ra.matrix_world
ra.animation_data.action = None                          # pose sentada fica; o rig inteiro segue o osso
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0)); ch = bpy.context.active_object
mc = bpy.data.materials.new("_chao"); mc.use_nodes = True; nt = mc.node_tree; bs = nt.nodes["Principled BSDF"]
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 100; ck.inputs["Color1"].default_value = (0.47, 0.43, 0.36, 1); ck.inputs["Color2"].default_value = (0.38, 0.35, 0.29, 1)
tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["UV"], ck.inputs["Vector"]); nt.links.new(ck.outputs["Color"], bs.inputs["Base Color"])
ch.data.materials.append(mc)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.64, 0.66, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.6; sol.angle = R(8)
so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (R(50), 0, R(35))
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 45
sc.render.resolution_x, sc.render.resolution_y = int(RES * 16 / 9) // 2 * 2, RES; sc.render.image_settings.file_format = "PNG"
az, el, dist, al = -60, 12, 34, V((0, 0, 6.8))
cam.location = al + V((-math.sin(R(az)) * math.cos(R(el)), -math.cos(R(az)) * math.cos(R(el)), math.sin(R(el)))) * dist
cam.rotation_euler = (al - cam.location).to_track_quat("-Z", "Y").to_euler()
pasta = os.path.join(OUT, "montado"); os.makedirs(pasta, exist_ok=True); n = 0
for nome, voltas in (("Repouso", 1), ("Andar", 2), ("Corrida", 5), ("VirarE", 2)):
    act = bpy.data.actions["Urso_" + nome]; arm.animation_data.action = act; f1 = int(act.frame_range[1])
    for _ in range(voltas):
        for f in range(1, f1 + 1):
            sc.frame_set(f); bpy.context.view_layer.update(); ra.matrix_world = osso() @ REL; bpy.context.view_layer.update()
            n += 1; sc.render.filepath = os.path.join(pasta, "m_%04d.png" % n); bpy.ops.render.render(write_still=True)
s2 = bpy.data.scenes.new("_v"); s2.sequence_editor_create(); s2.render.fps = 30; s2.frame_start = 1; s2.frame_end = n
st = s2.sequence_editor.strips.new_image("img", os.path.join(pasta, "m_0001.png"), channel=1, frame_start=1)
for f in range(2, n + 1): st.elements.append("m_%04d.png" % f)
s2.render.resolution_x, s2.render.resolution_y = sc.render.resolution_x, sc.render.resolution_y
im = s2.render.image_settings
try: im.media_type = "VIDEO"
except Exception: pass
im.file_format = "FFMPEG"; s2.render.ffmpeg.format = "MPEG4"; s2.render.ffmpeg.codec = "H264"; s2.render.ffmpeg.constant_rate_factor = "HIGH"
s2.render.filepath = os.path.join(OUT, "Montado_repouso_andar_corrida_virar.mp4"); bpy.ops.render.render(animation=True, scene=s2.name)
print("RENDER_MONTADO_OK", n)
