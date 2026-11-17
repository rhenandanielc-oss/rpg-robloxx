"""Conferencia da mascara do Uivo no Blender: emissao verde-musgo = L (+ runas R mais claras, olhos E), sobre a cor do lobo.
Uso: blender -b rig18/Lobo_Ancestral_Anim_v31.blend -P habilidades/efeito_uivo/render_mascara_uivo.py -- <saida.png> [forca_runas]"""
import bpy, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); FR = float(A[1]) if len(A) > 1 else 0.0
AQUI = os.path.dirname(os.path.abspath(__file__))
sc = bpy.context.scene
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
lobo = [o for o in bpy.data.objects if o.type == "MESH" and o.find_armature() == arm and "LOW" in o.name][0]
for o in sc.objects:
    if o.type == "MESH" and o is not lobo: o.hide_render = True
    if o.type == "EMPTY": o.hide_render = True
if arm.animation_data: arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.matrix_basis.identity()
    for c in pb.constraints: c.mute = True
mat = lobo.data.materials[0]; nt = mat.node_tree
bsdf = [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"][0]
img = bpy.data.images.load(os.path.join(AQUI, "mascara_uivo_preview.png")); img.colorspace_settings.name = "Non-Color"
tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img; tx.interpolation = "Closest"
uv = nt.nodes.new("ShaderNodeUVMap")
nt.links.new(uv.outputs[0], tx.inputs[0])
sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(tx.outputs[0], sep.inputs[0])
# preview: R = max(L,E), G = max(0.8L, R), B = R  -> linhas = R*... ; aproximacao: emissao = verde * R + runas extra * B
mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "ADD"
nt.links.new(sep.outputs[0], mul.inputs[0])
mr = nt.nodes.new("ShaderNodeMath"); mr.operation = "MULTIPLY"; mr.inputs[1].default_value = FR
nt.links.new(sep.outputs[2], mr.inputs[0]); nt.links.new(mr.outputs[0], mul.inputs[1])
bsdf.inputs["Emission Color"].default_value = (0.32, 0.62, 0.22, 1)
nt.links.new(mul.outputs[0], bsdf.inputs["Emission Strength"])
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16; sc.render.resolution_x, sc.render.resolution_y = 1280, 720
w = bpy.data.worlds.new("Wm"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.62, 0.68, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
sol = bpy.data.objects.new("SolM", bpy.data.lights.new("SolM", "SUN")); sc.collection.objects.link(sol); sol.data.energy = 2.5
sol.rotation_euler = (math.radians(45), 0, math.radians(-40))
cam = bpy.data.objects.new("CamM", bpy.data.cameras.new("CamM")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 45
alvo = V((0, -0.8, 4.2)); cam.location = alvo + V((12, -9, 5)); cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
cam.location = alvo + V((-12, 4, 9)); cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = OUT.replace(".png", "_b.png"); bpy.ops.render.render(write_still=True)
cam.location = V((1.6, -11.5, 7.6)); cam.rotation_euler = (V((0, -5.6, 7.0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = OUT.replace(".png", "_rosto.png"); bpy.ops.render.render(write_still=True)
print("RENDER_OK")
