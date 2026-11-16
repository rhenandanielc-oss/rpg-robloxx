"""r7: monta a mascara final e uma cena de revisao com as linhas NO CORPO (sem as fitas).
1) mascara 1024 = linhas assadas (2048 -> engrossa 1 px -> reduz) somadas aos brilhos antigos da LoboArtico_Corpo_emissao.png
2) blend de revisao: LOW_Corpo com emissao = mascara x azul-gelo; fitas removidas; espinhos mantidos (estado "no pico").
Uso: blender -b boreal/CR_LoboArtico_Boreal_r6.blend -P boreal/preparar_emissao_r7.py"""
import os
import numpy as np
try:
    import bpy
except ImportError:
    bpy = None
AQUI = os.path.dirname(os.path.abspath(__file__)); TEX = os.path.join(AQUI, "tex")
# mascara: o Python do Blender nao tem PIL -> roda fora: python boreal/preparar_emissao_r7.py --mascara
import sys
if "--mascara" in sys.argv:
    from PIL import Image, ImageFilter
    raw = Image.open(os.path.join(TEX, "LoboArtico_Corpo_linhas_raw.png")).convert("L")
    # r7b: as faixas sairam largas demais (o bake projeta a fita em leque na pele) -> afina por erosao e nao engrossa
    raw = raw.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(0.7)).resize((1024, 1024), Image.LANCZOS)
    lin = np.asarray(raw).astype(float) / 255
    antigo = np.asarray(Image.open(os.path.join(AQUI, "..", "anim_v41", "LoboArtico_Corpo_emissao.png")).convert("L")).astype(float) / 255
    mask = np.clip(np.maximum(np.clip(lin * 1.25, 0, 1), antigo), 0, 1)
    arq = os.path.join(TEX, "LoboArtico_Corpo_emissao_boreal.png")
    Image.fromarray((mask * 255).astype(np.uint8)).convert("RGB").save(arq)
    print("MASCARA_OK", arq)
    sys.exit(0)
arq = os.path.join(TEX, "LoboArtico_Corpo_emissao_boreal.png")


for o in [o for o in bpy.data.objects if o.name.startswith("Linhas_")]: bpy.data.objects.remove(o)
corpo = bpy.data.objects["LOW_Corpo"]
mat = corpo.data.materials[0]; nt = mat.node_tree
pb = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
img = bpy.data.images.load(arq); img.colorspace_settings.name = "Non-Color"
tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img
uv = next((n for n in nt.nodes if n.type == "UVMAP"), None)
mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
mix.inputs["Factor"].default_value = 1.0
mix.inputs[7].default_value = (0.35, 0.72, 1.0, 1)
nt.links.new(tx.outputs["Color"], mix.inputs[6])
nt.links.new(mix.outputs[2], pb.inputs["Emission Color"])
pb.inputs["Emission Strength"].default_value = 1.6
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, "CR_LoboArtico_Boreal_r7_revisao.blend"))
print("REVISAO_OK")
