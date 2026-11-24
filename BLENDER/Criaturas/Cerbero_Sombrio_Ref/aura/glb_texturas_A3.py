"""GLB "portador" das 4 texturas da aura A3 para o Roblox (20/11): o Import 3D do Studio sobe as texturas para a conta e
cria SurfaceAppearances com os IDs, que o plugin consegue LER (o Asset Manager nao expoe os IDs ao plugin). 4 quadrados, um
por textura (cor base = a imagem). Depois de ler os IDs, os quadrados sao apagados do place; o Cerbero nao e reimportado.
Uso: blender -b -t 2 --factory-startup -P glb_texturas_A3.py -- <pasta_roblox_A3> <saida.glb>"""
import bpy, sys, os
A = sys.argv[sys.argv.index("--") + 1:]
PASTA, SAIDA = os.path.abspath(A[0]), os.path.abspath(A[1])
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
NOMES = ["T_Cerbero_Corpo_Cor_Fogo", "T_Cerbero_Corpo_EmissivaMascara", "T_Cerbero_Cabecas_Cor_Fogo", "T_Cerbero_Cabecas_EmissivaMascara"]
REV = A[2] if len(A) > 2 else ""
for i, n in enumerate(NOMES):
    bpy.ops.mesh.primitive_plane_add(size=2, location=(i * 3, 0, 0)); o = bpy.context.object; o.name = n + REV
    m = bpy.data.materials.new(n); nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(PASTA, n + ".png"))
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"]); o.data.materials.append(m)
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format="GLB", export_image_format="AUTO", use_selection=False)
print("GLB_OK", SAIDA, os.path.getsize(SAIDA))
