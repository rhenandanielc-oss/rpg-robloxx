"""Pranchas de simetria: cabeca frente | espelhada | sobreposicao 50% (onde ha 'fantasma' ha assimetria) e vistas do corpo.
Uso: python prancha_simetria_v5.py <dir_simetria>"""
import sys, os
from PIL import Image, ImageDraw, ImageOps, ImageChops
d = os.path.abspath(sys.argv[1])
def rot(im, t):
    dr = ImageDraw.Draw(im); dr.rectangle((0, 0, 7 * len(t) + 14, 20), fill=(0, 0, 0)); dr.text((7, 4), t, fill=(255, 255, 255)); return im
def ab(n, s): return Image.open(os.path.join(d, "o_%s.png" % n)).convert("RGB").resize(s)
for nome in ("cabeca_frente", "corpo_frente", "cabeca_topo"):
    a = ab(nome, (600, 600) if "frente" in nome else (480, 600)); e = ImageOps.mirror(a); w, h = a.size
    m = Image.blend(a, e, 0.5); dif = ImageOps.autocontrast(ImageChops.difference(a, e).convert("L")).convert("RGB")
    o = Image.new("RGB", (4 * w + 18, h), (15, 15, 15))
    for k, (im, t) in enumerate(((a, "original"), (e, "espelhada (E<->D)"), (m, "sobreposicao 50%"), (dif, "diferenca (claro = assimetrico)"))):
        o.paste(rot(im, t), (k * (w + 6), 0))
    o.save(os.path.join(d, "simetria_%s.png" % nome))
S = (450, 450); L = (600, 400); T = (315, 450)
o = Image.new("RGB", (2 * S[0] + 2 * T[0] + 18, S[1] + L[1] + 6), (15, 15, 15))
for k, (n, s) in enumerate((("corpo_frente", S), ("corpo_tras", S), ("corpo_topo", T), ("corpo_baixo", T))):
    o.paste(rot(ab(n, s), n), (sum([S[0], S[0], T[0]][:k]) + 6 * k, 0))
for k, n in enumerate(("corpo_lado_E", "corpo_lado_D")): o.paste(rot(ab(n, L), n), (k * (L[0] + 6), S[1] + 6))
o.save(os.path.join(d, "simetria_corpo_vistas.png")); print("OK")
