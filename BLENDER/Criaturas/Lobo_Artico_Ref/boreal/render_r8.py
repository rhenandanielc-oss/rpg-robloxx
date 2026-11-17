"""Render de revisao dos efeitos de gelo (r8+): fundo escuro como a referencia PREPARO/VOO/POUSO, perfil E e 3/4.
Uso: blender -b boreal/CR_LoboArtico_Boreal_r8.blend -P boreal/render_r8.py -- <dir> <Acao:quadro,...> [mascara=<png>]"""
import bpy, sys, os, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
POSES = [x.split(":") for x in a[1].split(",")]; MASC = next((o[8:] for o in a[2:] if o.startswith("mascara=")), None)
sc = bpy.context.scene; rig = bpy.data.objects["LoboArtico_Rig"]; rig.data.pose_position = "POSE"
for o in sc.objects:
    if o.type == "MESH" and o.name.startswith(("LOD1", "LOD2")): o.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
if MASC:                                                        # linhas assadas: emissao do corpo = mascara x ciano; esconde as fitas
    for o in sc.objects:
        if o.name.startswith("Linhas_"): o.hide_render = True
    mat = bpy.data.objects["LOW_Corpo"].data.materials[0]; nt = mat.node_tree
    pb = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"); img = bpy.data.images.load(os.path.abspath(MASC)); img.colorspace_settings.name = "Non-Color"
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 1.0
    mix.inputs[7].default_value = (0.0, 0.55, 1.0, 1); nt.links.new(tx.outputs["Color"], mix.inputs[6]); nt.links.new(mix.outputs[2], pb.inputs["Emission Color"])
    pb.inputs["Emission Strength"].default_value = 9.0
sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE_NEXT"
sc.render.resolution_x, sc.render.resolution_y = 1100, 760
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.013, 0.016, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.002)); ch = bpy.context.object
mc = bpy.data.materials.new("Chao"); mc.use_nodes = True; mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1); ch.data.materials.append(mc)
for nome, loc, en, sz in (("Chave", (9, -6, 12), 2600, 8), ("Recorte", (-8, 8, 9), 1400, 6), ("Prench", (10, 4, 3), 500, 8)):
    ld = bpy.data.lights.new(nome, "AREA"); ld.energy = en; ld.size = sz; lo = bpy.data.objects.new(nome, ld); sc.collection.objects.link(lo)
    lo.location = loc; lo.rotation_euler = (V((0, 0, 3)) - V(loc)).to_track_quat("-Z", "Y").to_euler()
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 60
C0 = V((0, 0.2, 3.4)); VIS = {"perfil_E": C0 + V((23, 0, 1.0)), "34_E": C0 + V((15, -15, 5.5))}
try:
    sc.view_settings.view_transform = "AgX"
except Exception: pass
for acn, q in POSES:
    ac = bpy.data.actions[acn]; rig.animation_data.action = ac
    if len(ac.slots): rig.animation_data.action_slot = ac.slots[0]
    sc.frame_set(int(q))
    for v, pos in VIS.items():
        cam.location = pos; cam.rotation_euler = (C0 - pos).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "%s_q%s_%s.png" % (acn, q, v)); bpy.ops.render.render(write_still=True)
print("RENDER_R8_OK", flush=True)
