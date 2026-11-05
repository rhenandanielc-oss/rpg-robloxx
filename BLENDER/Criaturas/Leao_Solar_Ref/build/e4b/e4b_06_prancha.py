"""Prancha E4b: referencia | E3b | E4 | E4b na pose neutra (mesma luz) e closes; poses extremas por articulacao
(E4 x E4b com o MESMO rig de teste: textura e arame, antes/depois); tabela das medicoes. Uso: python e4b_06_prancha.py <ref.png> <saida.png>"""
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
REF, SAIDA = sys.argv[1:3]; ref = Image.open(REF).convert("RGB"); FUNDO = (220, 213, 207)
F = ImageFont.truetype("arial.ttf", 24); f = ImageFont.truetype("arial.ttf", 17); fm = ImageFont.truetype("consola.ttf", 15)
def sob(p, t=None):
    im = Image.open(p).convert("RGBA"); b = Image.new("RGBA", im.size, FUNDO + (255,)); b.alpha_composite(im); b = b.convert("RGB")
    return b.resize(t, Image.LANCZOS) if t else b
def alt(im, h): return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
def texto(linhas, w=1500):
    im = Image.new("RGB", (w, 22 * len(linhas) + 10), (24, 24, 28)); d = ImageDraw.Draw(im)
    for i, l in enumerate(linhas): d.text((8, 6 + 22 * i), l, fill=(225, 225, 225), font=fm)
    return im
def prancha(titulo, linhas, saida):
    larg = max(sum(im.width for _, im in l) + 16 * (len(l) + 1) for _, l in linhas)
    H = 60 + sum(max(im.height for _, im in l) + 54 for _, l in linhas)
    P = Image.new("RGB", (larg, H), (30, 30, 34)); d = ImageDraw.Draw(P); d.text((16, 16), titulo, fill=(240, 220, 160), font=F); y = 56
    for txt, l in linhas:
        d.text((16, y), txt, fill=(235, 235, 235), font=f); x = 16
        for rot, im in l:
            d.text((x, y + 24), rot, fill=(200, 200, 200), font=f); P.paste(im, (x, y + 46)); x += im.width + 16
        y += max(im.height for _, im in l) + 54
    P.save(saida); return P
V = (("E3b", "review/e3c/geral"), ("E4", "review/e4/geral"), ("E4b", "review/e4b/geral"))
CORTES = {"lado": (0, 0, 1217, 594), "frente": (0, 610, 608, 1293), "tras": (609, 610, 1217, 1293)}
L = []
for n, c in CORTES.items():
    h = 290 if n == "lado" else 330
    L.append((f"{n} (neutra): referencia | E3b | E4 | E4b", [("referencia", alt(ref.crop(c), h))] + [(k, alt(sob(f"{d}/{n}.png"), h)) for k, d in V]))
L.append(("3/4 frente e tras: E3b | E4 | E4b", [(k + " 3/4", alt(sob(f"{d}/tres_quartos.png"), 300)) for k, d in V] + [(k + " tras", alt(sob(f"{d}/tres_quartos_tras.png"), 300)) for k, d in V]))
for n in ("close_rosto_frente", "close_rosto_lado", "close_juba_34", "close_tufo"):
    L.append((f"close {n[6:]}: E3b | E4 | E4b", [(k, alt(sob(f"{d}/{n}.png"), 330)) for k, d in V]))
c = (100, 380, 508, 683)
L.append(("patas (frente): referencia | E3b | E4 | E4b", [("referencia", ref.crop((0, 610, 608, 1293)).crop(c))] + [(k, sob(f"{d}/frente.png").crop(c)) for k, d in V]))
PO = ["ombro_avanco", "cotovelo_dobra", "punho_dobra", "passo_dianteiro", "quadril_recuo", "joelho_dobra", "jarrete_dobra", "passo_traseiro",
      "pescoco_baixo_virado", "coluna_curva", "cauda_curva", "boca_32"]
M4 = json.load(open("review/e4b/poses_e4/poses.json")); M4b = json.load(open("review/e4b/poses_e4b/poses.json"))
for p in PO:
    def lin(m): z = m[p]["zona"]; return "aresta min %.2f max %.2f | espessura p5 %.2f" % (z["razao_min"], z["razao_max"], z["espessura_p5"])
    L.append((f"{p}: E4 (repouso arame | posado textura | posado arame)  ||  E4b (idem)   -   E4: {lin(M4)}   E4b: {lin(M4b)}",
              [("E4 repouso", sob(f"review/e4b/poses_e4/{p}_0_arame.png", (270, 270))), ("E4 posado", sob(f"review/e4b/poses_e4/{p}_1_tex.png", (270, 270))),
               ("E4 arame", sob(f"review/e4b/poses_e4/{p}_1_arame.png", (270, 270))),
               ("E4b repouso", sob(f"review/e4b/poses_e4b/{p}_0_arame.png", (270, 270))), ("E4b posado", sob(f"review/e4b/poses_e4b/{p}_1_tex.png", (270, 270))),
               ("E4b arame", sob(f"review/e4b/poses_e4b/{p}_1_arame.png", (270, 270)))]))
cab = "%-22s | %-34s | %-34s" % ("pose (mesmo rig)", "E4: aresta min/max, espessura p5", "E4b: aresta min/max, espessura p5")
rows = [cab, "-" * len(cab)]
for p in PO:
    a, b = M4[p]["zona"], M4b[p]["zona"]
    rows.append("%-22s | %6.2f %6.2f %6.2f                | %6.2f %6.2f %6.2f" % (p, a["razao_min"], a["razao_max"], a["espessura_p5"], b["razao_min"], b["razao_max"], b["espessura_p5"]))
L.append(("medicoes na zona de cada articulacao (aresta = comprimento posado/repouso; espessura = distancia ate os ossos, posado/repouso)", [("tabela", texto(rows))]))
P = prancha("Leao Solar E4b - malha preparada para deformar (17.602 tris) - Blender, rig de TESTE; nada testado no Roblox", L, SAIDA)
print("PRANCHA_E4B", P.size)
