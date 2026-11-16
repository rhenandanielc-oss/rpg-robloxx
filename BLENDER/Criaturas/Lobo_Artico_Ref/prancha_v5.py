"""Pranchas REFERENCIA | v4 | v5 lado a lado (olhos e boca, mesmas cameras do teste geometrico) e vista geral v4 x v5.
Uso: python prancha_v5.py <dir_v4> <dir_v5> [rotulo_A rotulo_B]   (cada dir com rosto/t_*.png e vista_*.png; padrao v4 v5)"""
import sys, os
from PIL import Image, ImageDraw
aqui = os.path.dirname(os.path.abspath(__file__)); d4, d5 = (os.path.abspath(x) for x in sys.argv[1:3])
NA, NB = (sys.argv[3:5] if len(sys.argv) >= 5 else ("v4", "v5"))
ref = Image.open(os.path.join(aqui, "ref", "lobo-artico-referencia.png")).convert("RGB")
CORTE = {"olhos": (330, 110, 560, 282), "boca": (330, 200, 560, 372)}           # recortes da referencia 1672x941
VISTAS = {"olhos": ("frente", "perfil", "34"), "boca": ("frente", "perfil", "34", "baixo")}
W, H = 400, 300
def rot(im, txt):
    dr = ImageDraw.Draw(im); dr.rectangle((0, 0, 7 * len(txt) + 14, 20), fill=(0, 0, 0)); dr.text((7, 4), txt, fill=(255, 255, 255)); return im
def abre(p, txt):
    if not os.path.exists(p): im = Image.new("RGB", (W, H), (60, 60, 60)); return rot(im, txt + " (sem imagem)")
    return rot(Image.open(p).convert("RGB").resize((W, H)), txt)
for grupo, vistas in VISTAS.items():
    cols = 1 + 2 * len(vistas); o = Image.new("RGB", (cols * W + (cols - 1) * 6, 3 * H + 12), (15, 15, 15))
    for r, fase in enumerate(("repouso", "meio", "maximo")):
        y = r * (H + 6)
        o.paste(rot(ref.crop(CORTE[grupo]).resize((W, H)), "REFERENCIA" + (" (so repouso)" if r else "")), (0, y))
        for k, v in enumerate(vistas):
            for j, (dd, nome) in enumerate(((d4, NA), (d5, NB))):
                x = (1 + 2 * k + j) * (W + 6)
                o.paste(abre(os.path.join(dd, "rosto", "t_%s_%s_%s.png" % (grupo, fase, v)), "%s %s %s" % (nome, fase, v)), (x, y))
    o.save(os.path.join(d5, "comparar_%s_ref_%s_%s.png" % (grupo, NA, NB))); print("PRANCHA", grupo)
im4, im5 = (Image.open(os.path.join(dd, "vistas.png")).convert("RGB") for dd in (d4, d5))
o = Image.new("RGB", (im4.width + im5.width + 10, max(im4.height, im5.height)), (15, 15, 15))
o.paste(rot(im4, NA), (0, 0)); o.paste(rot(im5, NB), (im4.width + 10, 0)); o.save(os.path.join(d5, "comparar_vistas_%s_%s.png" % (NA, NB))); print("PRANCHA vistas")
