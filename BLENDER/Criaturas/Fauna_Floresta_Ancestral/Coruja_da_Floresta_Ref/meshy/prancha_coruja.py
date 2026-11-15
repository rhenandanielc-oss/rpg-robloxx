"""Prancha da coruja (Meshy m1): referencia x renders (textura e argila). Uso: python prancha_coruja.py <pasta_modelo>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
P = sys.argv[1]; RAIZ = os.path.dirname(os.path.abspath(__file__))
F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t); BG = (125, 116, 111)
def f(n, h):
    im = Image.open(os.path.join(P, n)).convert("RGBA"); bb = im.getchannel("A").getbbox()
    b = Image.new("RGBA", im.size, BG + (255,)); b.alpha_composite(im); b = b.convert("RGB")
    if bb: b = b.crop((max(0, bb[0] - 25), max(0, bb[1] - 25), min(b.width, bb[2] + 25), min(b.height, bb[3] + 25)))
    return b.resize((round(b.width * h / b.height), h), Image.LANCZOS)
def r(im, h): return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
def rot(im, t):
    o = Image.new("RGB", (im.width, im.height + 26), (55, 53, 51)); o.paste(im, (0, 26)); ImageDraw.Draw(o).text((6, 5), t, fill=(240, 240, 240), font=F(15)); return o
def lin(ims, gap=8):
    o = Image.new("RGB", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), (45, 43, 42)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width + gap
    return o
ref = Image.open(os.path.join(RAIZ, "..", "..", "..", "..", "REFERENCIAS", "floresta-ancestral", "coruja-da-floresta", "coruja-da-floresta-referencia.png")).convert("RGB")
r34, rlado, rfr, rcos = ref.crop((0, 0, 690, 941)), ref.crop((840, 0, 1260, 460)), ref.crop((1330, 0, 1620, 460)), ref.crop((660, 470, 1672, 941))
L = [lin([rot(r(rcos, 300), "Referência · costas (asas abertas)"), rot(f("m1_B_costas.png", 300), "Meshy m1 · costas")]),
     lin([rot(r(rfr, 330), "Ref · frente"), rot(f("m1_B_frente.png", 330), "m1 · frente (textura)"), rot(f("m1_A_frente.png", 330), "m1 · frente (argila)")]),
     lin([rot(r(r34, 380), "Ref · 3/4 (pousada)"), rot(f("m1_B_tres_quartos.png", 380), "m1 · 3/4"), rot(f("m1_B_lado.png", 380), "m1 · perfil"),
          rot(f("m1_B_rosto.png", 380), "m1 · rosto")])]
W = max(l.width for l in L); topo = Image.new("RGB", (W, 60), (45, 43, 42)); d = ImageDraw.Draw(topo)
d.text((10, 6), "Coruja-da-Floresta — Meshy m1 (malha bruta, pose de rig com asas abertas) × referência", fill=(250, 250, 250), font=F(22))
d.text((10, 36), "EEVEE, luz neutra; argila = Workbench. Altura de trabalho 0,62 u com os tufos (PROPOSTA, não é porte oficial).", fill=(205, 205, 205), font=F(13))
o = Image.new("RGB", (W, 60 + sum(l.height + 8 for l in L)), (45, 43, 42)); o.paste(topo, (0, 0)); y = 60
for l in L: o.paste(l, (0, y)); y += l.height + 8
o.save(os.path.join(P, "m1_prancha.png")); print(o.size)
