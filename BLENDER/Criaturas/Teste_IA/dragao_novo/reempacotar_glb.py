"""Troca a base color do GLB do Meshy pela versao corrigida e exporta o GLB final (texturas embutidas).
Tambem relata os mapas ligados ao material (para conferir emissao/normal). Uso:
blender -b --factory-startup -P reempacotar_glb.py -- <entrada.glb> <base_color_nova.png> <saida.glb>"""
import bpy, sys, os
ent, cor, sai = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ent)
nova = bpy.data.images.load(cor); nova.pack()
for m in bpy.data.materials:
    if not m.node_tree: continue
    b = m.node_tree.nodes.get("Principled BSDF")
    for l in m.node_tree.links:
        if l.to_node == b and l.from_node.type == "TEX_IMAGE":
            print("MAPA", m.name, l.to_socket.name, l.from_node.image.name if l.from_node.image else None)
            if l.to_socket.name == "Base Color": l.from_node.image = nova
    if b:
        # o mapa de emissao do Meshy clareava o ventre (tom menta); o SurfaceAppearance do Roblox nao usa emissao
        for l in list(m.node_tree.links):
            if l.to_node == b and l.to_socket.name == "Emission Color": m.node_tree.links.remove(l)
        b.inputs["Emission Strength"].default_value = 0.0; print("EMISSAO removida", m.name)
os.makedirs(os.path.dirname(os.path.abspath(sai)), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=sai, export_format="GLB", export_image_format="AUTO")
print("REEMPACOTADO", round(os.path.getsize(sai) / 1e6, 1), "MB")
