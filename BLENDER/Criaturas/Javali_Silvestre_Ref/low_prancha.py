"""Prancha bruto x jogo da malha LOW do javali. Uso: python low_prancha.py <pasta_low>"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
P = sys.argv[1]; F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t); BG = (125, 116, 111)
def f(n, h):
    im = Image.open(os.path.join(P, n)).convert("RGBA"); bb = im.getchannel("A").getbbox()
    b = Image.new("RGBA", im.size, BG + (255,)); b.alpha_composite(im); b = b.convert("RGB")
    if bb: b = b.crop((max(0, bb[0] - 25), max(0, bb[1] - 25), min(b.width, bb[2] + 25), min(b.height, bb[3] + 25)))
    return b.resize((round(b.width * h / b.height), h), Image.LANCZOS)
def rot(im, t):
    o = Image.new("RGB", (im.width, im.height + 26), (55, 53, 51)); o.paste(im, (0, 26)); ImageDraw.Draw(o).text((6, 5), t, fill=(240, 240, 240), font=F(15)); return o
def lin(ims, gap=8):
    o = Image.new("RGB", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), (45, 43, 42)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width + gap
    return o
r = json.load(open(os.path.join(P, "relatorio_low.json"), encoding="utf-8"))
L = [lin([rot(f("low_bruto_tres_quartos.png", 380), "Bruto Meshy · 3/4"), rot(f("low_jogo_tres_quartos.png", 380), f"Jogo · 3/4 ({r['tris_total']} tris)"), rot(f("low_jogo_arame_tres_quartos.png", 380), "Jogo · arame")]),
     lin([rot(f("low_bruto_lado.png", 300), "Bruto · perfil"), rot(f("low_jogo_lado.png", 300), "Jogo · perfil")]),
     lin([rot(f("low_bruto_rosto_34.png", 330), "Bruto · rosto"), rot(f("low_jogo_rosto_34.png", 330), "Jogo · rosto"), rot(f("low_jogo_arame_rosto_34.png", 330), "Jogo · arame do rosto"),
          rot(f("low_bruto_miniatura.png", 150), "bruto"), rot(f("low_jogo_miniatura.png", 150), "jogo")])]
W = max(l.width for l in L); topo = Image.new("RGB", (W, 60), (45, 43, 42)); d = ImageDraw.Draw(topo)
m = r["malhas"]; d.text((10, 6), "Javali Silvestre — malha de jogo (low_v1) × bruto Meshy", fill=(250, 250, 250), font=F(22))
d.text((10, 36), f"Cabeça {m['Javali_Cabeca']['tris']} + corpo {m['Javali_Corpo']['tris']} tris; 2 materiais, texturas 1024 (cor, normal, rugosidade). Bruto: {r['bruto_tris']:,} tris. Orçamento = PROPOSTA.".replace(",", "."), fill=(205, 205, 205), font=F(13))
o = Image.new("RGB", (W, 60 + sum(l.height + 8 for l in L)), (45, 43, 42)); y = 60; o.paste(topo, (0, 0))
for l in L: o.paste(l, (0, y)); y += l.height + 8
o.save(os.path.join(P, "prancha_low.png")); print(o.size)
