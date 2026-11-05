"""Material de pelo da E2: mantem albedo/normal do Meshy, deixa o pelo fosco (rugosidade = 0,35 + 0,75 x mapa,
~0,8) e reduz o especular (0,25) para nao parecer plastico/metal; metal = 0. Opcional: troca o albedo.
Uso: blender -b <e2.blend> -P 15_material_pelo.py -- <saida.blend> [albedo.png]"""
import bpy, sys, os
A = sys.argv[sys.argv.index("--") + 1:]
for m in bpy.data.objects["Leao_Solar_E2"].data.materials:
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    for l in list(b.inputs["Metallic"].links): nt.links.remove(l)
    b.inputs["Metallic"].default_value = 0.0; b.inputs["Specular IOR Level"].default_value = 0.25
    r = b.inputs["Roughness"]; src = r.links[0].from_socket if r.links else None
    if src is not None and src.node.type != "MATH":
        mt = nt.nodes.new("ShaderNodeMath"); mt.operation = "MULTIPLY_ADD"; mt.inputs[1].default_value = 0.75; mt.inputs[2].default_value = 0.35
        mt.use_clamp = True; nt.links.new(src, mt.inputs[0]); nt.links.new(mt.outputs[0], r)
    if len(A) > 1:
        img = bpy.data.images.load(os.path.abspath(A[1]))
        for nd in nt.nodes:
            if nd.type == "TEX_IMAGE" and nd.image and nd.image.colorspace_settings.name == "sRGB": nd.image = img
print("MATERIAL_OK"); bpy.ops.wm.save_as_mainfile(filepath=A[0])
