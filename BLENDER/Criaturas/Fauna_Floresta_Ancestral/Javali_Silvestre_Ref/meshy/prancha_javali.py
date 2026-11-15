"""Prancha do javali (Meshy m1): referencia x renders (textura e argila), mesma luz neutra. Uso: python prancha_javali.py modelo"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
P = sys.argv[1]; RAIZ = os.path.dirname(os.path.abspath(__file__))
F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t); BG = (125, 116, 111)
def f(n, h):
    im = Image.open(os.path.join(P, n)).convert("RGBA"); b = Image.new("RGBA", im.size, BG + (255,)); b.alpha_composite(im)
    b = b.convert("RGB"); bb = Image.open(os.path.join(P, n)).getchannel("A").getbbox() if im.mode == "RGBA" else None
    if bb: b = b.crop((max(0, bb[0] - 30), max(0, bb[1] - 30), min(b.width, bb[2] + 30), min(b.height, bb[3] + 30)))
    return b.resize((round(b.width * h / b.height), h), Image.LANCZOS)
def rot(im, t):
    o = Image.new("RGB", (im.width, im.height + 26), (55, 53, 51)); o.paste(im, (0, 26)); ImageDraw.Draw(o).text((6, 5), t, fill=(240, 240, 240), font=F(15)); return o
def lin(ims, gap=8):
    o = Image.new("RGB", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), (45, 43, 42)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width + gap
    return o
ref = Image.open(os.path.join(RAIZ, "..", "..", "..", "..", "REFERENCIAS", "floresta-ancestral", "javali-silvestre", "javali-silvestre-referencia.png")).convert("RGB")
r_34 = ref.crop((0, 0, 1060, 941)); r_lado = ref.crop((1020, 0, 1672, 400)); r_fr = ref.crop((1180, 380, 1520, 941))
l1 = lin([rot(r_34.resize((round(r_34.width * 420 / r_34.height), 420)), "Referência · 3/4"), rot(f("m1_B_tres_quartos.png", 420), "Meshy m1 · 3/4 (textura)"), rot(f("m1_A_tres_quartos.png", 420), "m1 · argila")])
l2 = lin([rot(r_lado.resize((round(r_lado.width * 300 / r_lado.height), 300)), "Referência · perfil"), rot(f("m1_B_lado.png", 300), "m1 · perfil"),
          rot(r_fr.resize((round(r_fr.width * 300 / r_fr.height), 300)), "Ref · frente"), rot(f("m1_B_frente.png", 300), "m1 · frente")])
l3 = lin([rot(f("m1_B_rosto_34.png", 360), "m1 · rosto 3/4"), rot(f("m1_B_rosto_lado.png", 360), "m1 · rosto perfil"), rot(f("m1_B_miniatura.png", 150), "miniatura")])
W = max(l.width for l in (l1, l2, l3)); topo = Image.new("RGB", (W, 60), (45, 43, 42)); d = ImageDraw.Draw(topo)
d.text((10, 6), "Javali Silvestre — Meshy m1 (malha bruta) × referência", fill=(250, 250, 250), font=F(22))
d.text((10, 36), "EEVEE, luz neutra; argila = Workbench. Escala de trabalho: meio do dorso 0,75 u (PROPOSTA, não é porte oficial).", fill=(205, 205, 205), font=F(13))
H = 60 + l1.height + l2.height + l3.height + 24; o = Image.new("RGB", (W, H), (45, 43, 42)); y = 0
for l in (topo, l1, l2, l3): o.paste(l, (0, y)); y += l.height + (0 if l is topo else 8)
o.save(os.path.join(P, "m1_prancha.png")); print(o.size)
