"""Uivo Boreal r7 (16/11/2026) - as LINHAS passam a ser PARTE DO CORPO (pedido do usuario: "que facam parte do corpo do lobo,
nao flutuem ao redor; o poder do uivo implemente ao corpo estes efeitos").
Em vez de fitas soltas, as linhas sao ASSADAS na UV da LOW_Corpo como mascara de emissao: no Roblox a SurfaceAppearance
do corpo ganha esta mascara e o Uivo so liga/pulsa EmissiveStrength (0 em repouso = nenhuma linha).
Fonte das linhas: as fitas do r6 (boreal_fx.py), projetadas na pele por bake EMIT selected-to-active (Cycles).
Saidas: boreal/tex/LoboArtico_Corpo_linhas_raw.png (2048, so as linhas),
        boreal/tex/LoboArtico_Corpo_emissao_boreal.png (1024 = linhas engrossadas e suavizadas + brilhos antigos do corpo)
Uso: blender -b boreal/CR_LoboArtico_Boreal_r6.blend -P boreal/assar_linhas_corpo.py"""
import bpy, os
AQUI = os.path.dirname(os.path.abspath(__file__)); TEX = os.path.join(AQUI, "tex"); os.makedirs(TEX, exist_ok=True)
sc = bpy.context.scene
rig = bpy.data.objects["LoboArtico_Rig"]; rig.data.pose_position = "REST"
corpo = bpy.data.objects["LOW_Corpo"]
fitas = [o for o in bpy.data.objects if o.name.startswith("Linhas_")]

# fitas: emissao branca pura
me_ = bpy.data.materials.new("Bake_Linha"); me_.use_nodes = True
nt = me_.node_tree; nt.nodes.clear()
em = nt.nodes.new("ShaderNodeEmission"); em.inputs[1].default_value = 1.0
out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], out.inputs[0])
for o in fitas:
    o.data.materials.clear(); o.data.materials.append(me_)

# alvo: imagem preta na UV da LOW_Corpo (no material do corpo, no ativa, sem ligar em nada)
img = bpy.data.images.new("Corpo_linhas_raw", 2048, 2048, alpha=False)
img.generated_color = (0, 0, 0, 1)
mat = corpo.data.materials[0]
no_img = mat.node_tree.nodes.new("ShaderNodeTexImage"); no_img.image = img
for n in mat.node_tree.nodes: n.select = False
no_img.select = True; mat.node_tree.nodes.active = no_img

sc.render.engine = "CYCLES"; sc.cycles.samples = 4
try: sc.cycles.device = "GPU"
except Exception: pass
bk = sc.render.bake
bk.use_selected_to_active = True; bk.cage_extrusion = 0.75; bk.max_ray_distance = 1.2; bk.margin = 4
bpy.ops.object.select_all(action="DESELECT")
for o in fitas: o.select_set(True)
corpo.select_set(True); bpy.context.view_layer.objects.active = corpo
bpy.ops.object.bake(type="EMIT")
img.filepath_raw = os.path.join(TEX, "LoboArtico_Corpo_linhas_raw.png"); img.file_format = "PNG"; img.save()
print("BAKE_OK", img.filepath_raw)
