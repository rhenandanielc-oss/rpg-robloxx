"""Mostra o peso total dos ossos de pelo (vermelho = mecha solta ao vento, cinza = presa ao corpo), lateral/frente/3/4/cima.
So leitura. Uso: blender -b <rig.blend> -P ver_pelo.py -- <saida_prefixo>"""
import bpy, sys, os
from mathutils import Vector as V
PRE = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
sc = bpy.context.scene; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data
for o in sc.objects:
    if (o.type == "MESH" and o is not LO and not o.name.startswith("Plane")) or o.type == "EMPTY": o.hide_render = True
if arm.animation_data: arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    for c in pb.constraints: c.mute = True
pel = {g.index for g in LO.vertex_groups if g.name.startswith("Pelo")}
at = me.color_attributes.get("ver_pelo") or me.color_attributes.new("ver_pelo", "FLOAT_COLOR", "POINT")
for v in me.vertices:
    w = min(1.0, sum(g.weight for g in v.groups if g.group in pel) / 0.6)
    at.data[v.index].color = (0.55 + 0.45 * w, 0.55 * (1 - w), 0.55 * (1 - w), 1)
m = bpy.data.materials.new("ver_pelo"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
a = nt.nodes.new("ShaderNodeVertexColor"); a.layer_name = "ver_pelo"; nt.links.new(a.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.9
LO.data.materials[0] = m
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 12; sc.render.resolution_x, sc.render.resolution_y = 800, 520
cam = sc.camera; cam.data.type = "PERSP"; cam.data.lens = 40
alvo = V((0, -1.2, 4.0))
for vn, pos in (("lado", V((24, -1.2, 4.5))), ("frente", V((0, -24, 5.0))), ("tres_quartos", V((15, -16, 9.0))), ("cima", V((0.01, -1.2, 26)))):
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = "%s_%s.png" % (PRE, vn); bpy.ops.render.render(write_still=True)
