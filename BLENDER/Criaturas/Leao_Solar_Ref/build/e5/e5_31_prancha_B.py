"""Prancha da Fase B: folhas de quadros (corpo e rosto) de cada clipe e tabela de QA. Uso: python e5_31_prancha_B.py <saida.png>"""
import sys, glob
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("arial.ttf", 26); f = ImageFont.truetype("arial.ttf", 18); fm = ImageFont.truetype("consola.ttf", 15)
ORDEM = ["Alerta_Ameaca", "Intimidacao", "Rosnado", "Rugido", "Aproximacao_Furtiva", "Bote", "Patada_D", "Patada_E", "Mordida", "Esquiva_E", "Esquiva_D", "Fadiga_Recuperacao"]
blocos = []
for n in ORDEM:
    for tag in ("corpo", "rosto"):
        g = glob.glob("review/e5/faseB/_folha_%s_%s.png" % (n, tag))
        if g: blocos.append(("%s (%s)" % (n, tag), Image.open(g[0]).convert("RGB")))
linhas = ["%-20s %5s %6s %5s %7s %7s %8s %6s" % ("clipe", "q", "dur_s", "tipo", "desl", "ik_max", "esc_max", "zmin")]
for l in open("review/e5/_tabela_B.txt", encoding="utf-8"):
    c = [x.strip() for x in l.strip().strip("|").split("|")]
    linhas.append("%-20s %5s %6s %5s %7s %7s %8s %6s" % tuple(c[:8]))
im = Image.new("RGB", (900, 24 * len(linhas) + 12), (24, 24, 28)); d = ImageDraw.Draw(im)
for i, l in enumerate(linhas): d.text((8, 6 + 24 * i), l, fill=(225, 225, 225), font=fm)
blocos.append(("QA (Blender): esc = escorregamento p90 das almofadas apoiadas por quadro; zmin = menor altura da malha", im))
W = max(i.width for _, i in blocos) + 32; H = 60 + sum(i.height + 40 for _, i in blocos)
P = Image.new("RGB", (W, H), (30, 30, 34)); d = ImageDraw.Draw(P)
d.text((16, 16), "Leao Solar E5 - Fase B (atitude agressiva e ataques; so movimento, sem efeitos) - Blender; nada testado no Roblox", fill=(240, 220, 160), font=F); y = 60
for t, i in blocos:
    d.text((16, y), t, fill=(235, 235, 235), font=f); P.paste(i, (16, y + 26)); y += i.height + 40
P.save(sys.argv[1]); print("PRANCHA_B", P.size)
