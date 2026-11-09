"""Mascara frontal/lateral ortografica so da pata dianteira (branco = vertices da cadeia Escapula/Braco/Antebraco/Mao/
Dedos, emissao, sem luz) para medir o contorno real da perna por altura. So leitura.
Uso: blender -b <rig.blend> -P mascara_perna.py -- <saida_prefixo>"""
import bpy, sys, os
from mathutils import Vector as V
PRE = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
sc = bpy.context.scene; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data
for o in sc.objects:
    if o is not LO and o.type == "MESH": o.hide_render = True
if arm.animation_data: arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    for c in pb.constraints: c.mute = True
cad = {g.index for g in LO.vertex_groups if g.name.startswith(("Escapula", "Braco", "Antebraco", "Mao", "Dedos"))}
at = me.color_attributes.get("mask_perna") or me.color_attributes.new("mask_perna", "FLOAT_COLOR", "POINT")
for v in me.vertices:
    w = 1.0 if sum(g.weight for g in v.groups if g.group in cad) > 0.5 else 0.0
    at.data[v.index].color = (w, w, w, 1)
m = bpy.data.materials.new("mask"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
a = nt.nodes.new("ShaderNodeVertexColor"); a.layer_name = "mask_perna"; e = nt.nodes.new("ShaderNodeEmission"); o = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(a.outputs["Color"], e.inputs["Color"]); nt.links.new(e.outputs["Emission"], o.inputs["Surface"])
LO.data.materials[0] = m
sc.world.use_nodes = True; bg = sc.world.node_tree.nodes.get("Background")
if bg: bg.inputs[0].default_value = (0, 0, 1, 1); bg.inputs[1].default_value = 1.0
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 4; sc.view_settings.view_transform = "Standard"
sc.render.resolution_x, sc.render.resolution_y = 900, 900
cam = sc.camera; cam.data.type = "ORTHO"; cam.data.ortho_scale = 6.4
for vn, pos, alvo in (("frente", V((0, -20, 3.0)), V((0, 0, 3.0))), ("lado", V((20, -4.0, 3.0)), V((0, -4.0, 3.0)))):
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = "%s_%s.png" % (PRE, vn); bpy.ops.render.render(write_still=True)
