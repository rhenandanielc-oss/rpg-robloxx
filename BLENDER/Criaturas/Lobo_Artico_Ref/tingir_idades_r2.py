"""Pelagem mais clara para Filhote e Jovem NO ROBLOX (19/11/2026). No Studio elas saem mais escuras que no Blender (sem a
curva AgX do render). Gera PNGs para upload (idades_v1/roblox_r2/) - as malhas nao mudam, so a textura de cor.
Uso: python tingir_idades_r2.py"""
import os
from PIL import Image
SRC = "anim_v42b"; OUT = "idades_v1/roblox_r2"; os.makedirs(OUT, exist_ok=True)
TINTAS = {"Filhote": (0.55, 0.50, 0.46), "Jovem": (0.78, 0.77, 0.76)}   # r1 (GLB): 0,46/0,42/0,39 e 0,70 (escuro demais no Roblox); r2a 0,64/0,85 (claro demais: filhote quase branco)
for arq in ("LoboArtico_Corpo_cor.png", "LoboArtico_Cabeca_cor.png", "LoboArtico_pelo_atlas.png"):
    im = Image.open(os.path.join(SRC, arq)); modo = im.mode; im = im.convert("RGBA"); r, g, b, a = im.split()
    for idade, t in TINTAS.items():
        rr, gg, bb = (c.point(lambda x, k=k: int(x * k)) for c, k in zip((r, g, b), t))
        Image.merge("RGBA", (rr, gg, bb, a)).convert(modo if modo in ("RGB", "RGBA") else "RGBA").save(os.path.join(OUT, "%s_%s.png" % (os.path.splitext(arq)[0], idade)))
print("TINGIR_R2_OK", sorted(os.listdir(OUT)))
