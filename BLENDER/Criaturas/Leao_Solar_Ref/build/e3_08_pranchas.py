"""Pranchas da E3: geral (referencia | E2 v11 | E3), membros (v11 x E3, 4 membros), boca (fechada v11 x E3, aberta
10/20/32 graus em 3/4 e perfil, vista interna) e diferenca de pixels v11 x E3 de boca fechada.
Uso: python e3_08_pranchas.py <ref.png> <dir_v11> <dir_e3_geral> <dir_e3_boca> <saida_prefixo>"""
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
REF, V11, E3, BOCA, SAIDA = sys.argv[1:6]
ref = Image.open(REF).convert("RGB"); FUNDO = (220, 213, 207)
F = ImageFont.truetype("arial.ttf", 22); f = ImageFont.truetype("arial.ttf", 17)
def sobre(p):
    im = Image.open(p).convert("RGBA"); b = Image.new("RGBA", im.size, FUNDO + (255,)); b.alpha_composite(im); return b.convert("RGB")
def prancha(titulo, linhas, saida, escala=1.0):
    larg = max(sum(im.width for _, im in l) + 20 * (len(l) + 1) for _, l in linhas)
    alt = 60 + sum(max(im.height for _, im in l) + 56 for _, l in linhas)
    P = Image.new("RGB", (larg, alt), (30, 30, 34)); d = ImageDraw.Draw(P); d.text((20, 16), titulo, fill=(240, 220, 160), font=F); y = 56
    for txt, l in linhas:
        d.text((20, y), txt, fill=(230, 230, 230), font=f); x = 20
        for rot, im in l:
            d.text((x, y + 24), rot, fill=(200, 200, 200), font=f); P.paste(im, (x, y + 48)); x += im.width + 20
        y += max(im.height for _, im in l) + 56
    if escala != 1: P = P.resize((int(P.width * escala), int(P.height * escala)), Image.LANCZOS)
    P.save(saida)
CORTES = {"lado": (0, 0, 1217, 594), "frente": (0, 610, 608, 1293), "tras": (609, 610, 1217, 1293)}
geral = [(f"{n}: referencia | E2 v11 (aprovada) | E3", [("referencia", ref.crop(c)), ("E2 v11", sobre(f"{V11}/{n}.png")), ("E3", sobre(f"{E3}/{n}.png"))])
         for n, c in CORTES.items()]
geral += [("3/4 frente e tras: E2 v11 | E3", [("v11 3/4", sobre(f"{V11}/tres_quartos.png")), ("E3 3/4", sobre(f"{E3}/tres_quartos.png")),
                                               ("v11 3/4 tras", sobre(f"{V11}/tres_quartos_tras.png")), ("E3 3/4 tras", sobre(f"{E3}/tres_quartos_tras.png"))])]
prancha("Leao Solar E3 - geral (mesma luz neutra)", geral, SAIDA + "_geral.png", 0.75)
# membros: recortes das patas nas 4 vistas
REC = {"frente": (150, 420, 460, 683), "lado": (280, 330, 1000, 594), "tras": (740, 420, 1100, 683), "tres_quartos": (330, 450, 720, 800)}
REC["tras"] = (130, 420, 480, 683)
mem = []
for n, c in REC.items():
    a = sobre(f"{V11}/{n}.png").crop(c); b = sobre(f"{E3}/{n}.png").crop(c)
    if a.width < 500: a = a.resize((a.width * 2, a.height * 2), Image.LANCZOS); b = b.resize((b.width * 2, b.height * 2), Image.LANCZOS)
    mem.append((f"membros - {n}: E2 v11 (antes) | E3 (depois)", [("antes", a), ("depois", b)]))
prancha("Leao Solar E3 - membros: manchas escuras dos antebracos (antes | depois)", mem, SAIDA + "_membros.png", 0.8)
# boca
fe = [("Boca FECHADA (deve igualar a aprovada): v11 | E3", [("v11 perfil", sobre(f"{V11}/close_rosto_lado.png")), ("E3 perfil", sobre(f"{E3}/close_rosto_lado.png")),
                                                         ("v11 frente", sobre(f"{V11}/close_rosto_frente.png")), ("E3 frente", sobre(f"{E3}/close_rosto_frente.png"))])]
ab = [("Boca ABERTA em 3/4: 10 | 20 | 32 graus", [(f"{g} graus", sobre(f"{BOCA}/boca_{g:02d}_34.png").resize((600, 600))) for g in (10, 20, 32)]),
      ("Perfil 32 graus | vista interna 20 e 32 graus", [("perfil 32", sobre(f"{BOCA}/boca_32_perfil.png").resize((600, 600))),
                                                         ("interna 20", sobre(f"{BOCA}/boca_20_interna.png").resize((600, 600))),
                                                         ("interna 32", sobre(f"{BOCA}/boca_32_interna.png").resize((600, 600)))])]
prancha("Leao Solar E3 - boca (mandibula com pivo na articulacao; interior fechado)", fe + ab, SAIDA + "_boca.png", 0.8)
# diferenca de pixels, boca fechada, closes do rosto
met = {}
for n in ("close_rosto_lado", "close_rosto_frente", "frente", "lado"):
    a = np.asarray(sobre(f"{V11}/{n}.png")).astype(float); b = np.asarray(sobre(f"{E3}/{n}.png")).astype(float)
    dd = np.abs(a - b).mean(-1); met[n] = {"media": round(float(dd.mean()), 2), "pct_pixels_>12": round(float((dd > 12).mean() * 100), 2)}
json.dump(met, open(SAIDA + "_diferenca_v11.json", "w"), indent=1); print("PRANCHAS_E3", met)
