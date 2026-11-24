"""Previa das texturas assadas para o Roblox (cor + mascara de emissao) no modelo, imitando a SurfaceAppearance:
emissao = cor x mascara x forca x tinta (no Roblox a emissao e multiplicada pelo albedo). Sem chamas, sem shader da A3.
Uso: blender -b -t 2 CR_Cerbero_Fogo_A3.blend -P previa_textura_roblox.py -- <pasta_texturas> <saida.png> [forca] [dia|noite]"""
import bpy, sys, os, math
A = sys.argv[sys.argv.index("--") + 1:]
PASTA, SAIDA = os.path.abspath(A[0]), os.path.abspath(A[1]); FORCA = float(A[2]) if len(A) > 2 else 3.0
NOITE = len(A) > 3 and A[3] == "noite"
sc = bpy.context.scene; sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 8
sc.render.resolution_x, sc.render.resolution_y = 720, 500; sc.render.threads_mode = "FIXED"; sc.render.threads = 2
for o in bpy.data.objects:
    if o.name.startswith("ChamaA3") or o.name == "Fogo_Faixas": o.hide_render = True
for n in ("Corpo", "Cabecas"):
    o = bpy.data.objects["Cerbero_" + n]
    m = bpy.data.materials.new("Prev_" + n); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    c = nt.nodes.new("ShaderNodeTexImage"); c.image = bpy.data.images.load(os.path.join(PASTA, "T_Cerbero_%s_Cor_Fogo.png" % n))
    k = nt.nodes.new("ShaderNodeTexImage"); k.image = bpy.data.images.load(os.path.join(PASTA, "T_Cerbero_%s_EmissivaMascara.png" % n))
    k.image.colorspace_settings.name = "Non-Color"
    nt.links.new(c.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.8
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs["Factor"].default_value = 1
    nt.links.new(c.outputs["Color"], mx.inputs["A"]); mx.inputs["B"].default_value = (1.0, 0.43, 0.12, 1)
    nt.links.new(mx.outputs["Result"], b.inputs["Emission Color"])
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = FORCA * 4
    nt.links.new(k.outputs["Color"], mul.inputs[0]); nt.links.new(mul.outputs[0], b.inputs["Emission Strength"])
    o.data.materials.clear(); o.data.materials.append(m)
w = sc.world or bpy.data.worlds.new("W"); sc.world = w
bg = w.node_tree.nodes.get("Background")
if bg: bg.inputs["Color"].default_value = (0.02, 0.02, 0.035, 1) if NOITE else (0.35, 0.45, 0.6, 1); bg.inputs["Strength"].default_value = 1.0
cam = bpy.data.objects.new("CamPrev", bpy.data.cameras.new("CamPrev")); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (-26, -30, 16); alvo = bpy.data.objects.new("AlvoPrev", None); sc.collection.objects.link(alvo); alvo.location = (0, -2, 9)
t = cam.constraints.new("TRACK_TO"); t.target = alvo; t.track_axis = "TRACK_NEGATIVE_Z"; t.up_axis = "UP_Y"; cam.data.lens = 40
sc.render.filepath = SAIDA; bpy.ops.render.render(write_still=True); print("PREV_OK", SAIDA)
