"""Prancha E4: referencia | E2 v11 | E3b | E4 (malha de jogo) sob a mesma luz; closes; boca 0/10/20/32 (E3b x E4);
tamanho de jogo; deformacao provisoria; atlas. Tambem grava as diferencas de pixels. Uso: python e4_07_prancha.py <ref.png> <saida.png>"""
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
REF, SAIDA = sys.argv[1:3]; ref = Image.open(REF).convert("RGB"); FUNDO = (220, 213, 207)
F = ImageFont.truetype("arial.ttf", 24); f = ImageFont.truetype("arial.ttf", 17)
def sob(p, t=None):
    im = Image.open(p).convert("RGBA"); b = Image.new("RGBA", im.size, FUNDO + (255,)); b.alpha_composite(im); b = b.convert("RGB")
    return b.resize(t, Image.LANCZOS) if t else b
def alt(im, h): return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
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
V11, E3B, E4 = "review/e2_v11", "review/e3c/geral", "review/e4/geral"
CORTES = {"lado": (0, 0, 1217, 594), "frente": (0, 610, 608, 1293), "tras": (609, 610, 1217, 1293)}
L = []
for n, c in CORTES.items():
    h = 300 if n == "lado" else 330
    L.append((f"{n}: referencia | E2 v11 | E3b | E4 (jogo)", [("referencia", alt(ref.crop(c), h))] + [(k, alt(sob(f"{d}/{n}.png"), h)) for k, d in (("E2 v11", V11), ("E3b", E3B), ("E4", E4))]))
for n in ("tres_quartos", "tres_quartos_tras"):
    L.append((f"{n}: E2 v11 | E3b | E4", [(k, alt(sob(f"{d}/{n}.png"), 330)) for k, d in (("E2 v11", V11), ("E3b", E3B), ("E4", E4))]))
for n in ("close_rosto_frente", "close_rosto_lado", "close_juba_34", "close_tufo"):
    L.append((f"close {n[6:]}: E2 v11 | E3b | E4", [(k, alt(sob(f"{d}/{n}.png"), 360)) for k, d in (("E2 v11", V11), ("E3b", E3B), ("E4", E4))]))
c = (100, 380, 508, 683)
L.append(("patas (frente): referencia | E2 v11 | E3b | E4", [("referencia", ref.crop((0, 610, 608, 1293)).crop(c))] + [(k, sob(f"{d}/frente.png").crop(c)) for k, d in (("E2 v11", V11), ("E3b", E3B), ("E4", E4))]))
for g in (0, 10, 20, 32):
    vs = ("34", "frente", "perfil") + (("interna",) if g else ())
    L.append((f"boca {g} graus: E3b | E4", [(f"E3b {v}", sob(f"review/e3c/final/boca_{g:02d}_{v}.png", (250, 250))) for v in vs] +
              [(f"E4 {v}", sob(f"review/e4/boca/boca_{g:02d}_{v}.png", (250, 250))) for v in vs]))
L.append(("tamanho de jogo (render 3/4 pequeno, ampliado 2x sem filtro): E2 v11 | E3b | E4 | E4 boca 20 e 32",
          [(k, sob(f"{d}/jogo_34.png").resize((sob(f"{d}/jogo_34.png").width * 2, sob(f"{d}/jogo_34.png").height * 2), Image.NEAREST)) for k, d in (("E2 v11", V11), ("E3b", E3B), ("E4", E4))] +
          [(f"E4 boca {g}", sob(f"review/e4/boca/boca_{g:02d}_jogo.png").crop((90, 90, 270, 270)).resize((360, 360), Image.NEAREST)) for g in (20, 32)]))
ns = ["repouso", "pescoco_baixo_virado", "passo_dianteiro", "passo_traseiro", "coluna_curvada", "cauda"]
L.append(("deformacao com rig PROVISORIO e pesos automaticos (3/4)", [(n, sob(f"review/e4/deform/{n}_34.png", (300, 300))) for n in ns]))
L.append(("deformacao (perfil)", [(n, sob(f"review/e4/deform/{n}_perfil.png", (300, 300))) for n in ns]))
L.append(("atlas 2048 (cor | normal | rugosidade)", [(n, Image.open(f"e4/tex/Leao_Solar_E4_{n}_2048.png").convert("RGB").resize((400, 400))) for n in ("cor", "normal", "rugosidade")]))
P = prancha("Leao Solar E4 - malha de jogo (17.798 tris, 1 material, 2048/1024) - Blender, luz neutra; nada testado no Roblox", L, SAIDA)
met = {}
for n in ("lado", "frente", "tras", "tres_quartos", "tres_quartos_tras", "close_rosto_frente", "close_rosto_lado", "close_juba_34", "close_tufo", "jogo_34"):
    a = np.asarray(sob(f"{V11}/{n}.png")).astype(float); b = np.asarray(sob(f"{E3B}/{n}.png")).astype(float); e = np.asarray(sob(f"{E4}/{n}.png")).astype(float)
    m = {}
    for k, (x, y) in {"E4_vs_E3b": (e, b), "E4_vs_v11": (e, a), "E3b_vs_v11": (b, a)}.items():
        d = np.abs(x - y).mean(-1); m[k] = {"media": round(float(d.mean()), 2), "pct>12": round(float((d > 12).mean() * 100), 2)}
    met[n] = m
json.dump(met, open(SAIDA.replace(".png", "_diferencas.json"), "w"), indent=1); print("PRANCHA_E4", P.size); print(json.dumps(met))
