"""Prancha E3b: E2 v11 (aprovada) | E3 anterior | E3b (correcao). Rosto fechado com a referencia, aberto 10/20/32 em 3/4,
closes a 32 graus (frente, perfil, 3/4, interna, baixo), quadros intermediarios, tamanho de jogo e membros.
Uso: python c08_prancha.py <ref.png> <saida.png>"""
import sys
from PIL import Image, ImageDraw, ImageFont
REF, SAIDA = sys.argv[1:3]
ref = Image.open(REF).convert("RGB"); FUNDO = (220, 213, 207)
F = ImageFont.truetype("arial.ttf", 24); f = ImageFont.truetype("arial.ttf", 17)
def sob(p, t=None):
    im = Image.open(p).convert("RGBA"); b = Image.new("RGBA", im.size, FUNDO + (255,)); b.alpha_composite(im); b = b.convert("RGB")
    return b.resize(t, Image.LANCZOS) if t else b
def prancha(titulo, linhas, saida):
    larg = max(sum(im.width for _, im in l) + 16 * (len(l) + 1) for _, l in linhas)
    alt = 60 + sum(max(im.height for _, im in l) + 54 for _, l in linhas)
    P = Image.new("RGB", (larg, alt), (30, 30, 34)); d = ImageDraw.Draw(P); d.text((16, 16), titulo, fill=(240, 220, 160), font=F); y = 56
    for txt, l in linhas:
        d.text((16, y), txt, fill=(235, 235, 235), font=f); x = 16
        for rot, im in l:
            d.text((x, y + 24), rot, fill=(200, 200, 200), font=f); P.paste(im, (x, y + 46)); x += im.width + 16
        y += max(im.height for _, im in l) + 54
    P.save(saida); return P
V11, E3G, E3BG, E3A, E3B = "review/e2_v11", "review/e3/geral", "review/e3c/geral", "review/e3c/e3_antiga", "review/e3c/final"
T = (330, 330)
rl = ref.crop((0, 0, 1217, 594)).crop((830, 20, 1217, 420)).resize((330, 341)); rf = ref.crop((0, 610, 608, 1293)).crop((130, 0, 480, 360)).resize((330, 339))
L = []
L.append(("1. Boca FECHADA (deve igualar a v11 aprovada) - perfil: referencia | E2 v11 | E3 anterior | E3b", [("referencia", rl)] +
          [(n, sob(f"{d}/close_rosto_lado.png", (262, 340))) for n, d in (("E2 v11", V11), ("E3 anterior", E3G), ("E3b", E3BG))] +
          [("ref. frente", rf)] + [(n + " frente", sob(f"{d}/close_rosto_frente.png", (310, 340))) for n, d in (("v11", V11), ("E3", E3G), ("E3b", E3BG))]))
for g in (10, 20, 32):
    L.append((f"2. Aberta {g} graus - E3 anterior (3/4, frente, interna) | E3b (3/4, frente, interna). A v11 nao tem mandibula articulada.",
              [(f"E3 {v}", sob(f"{E3A}/boca_{g:02d}_{v}.png", T)) for v in ("34", "frente", "interna")] +
              [(f"E3b {v}", sob(f"{E3B}/boca_{g:02d}_{v}.png", T)) for v in ("34", "frente", "interna")]))
L.append(("3. Closes a 32 graus - E3b: perfil | 3/4 lado oposto | de baixo  ||  E3 anterior: perfil | de baixo",
          [("E3b perfil", sob(f"{E3B}/boca_32_perfil.png", T)), ("E3b 3/4 (X-)", sob(f"{E3B}/boca_32_34e.png", T)), ("E3b baixo", sob(f"{E3B}/boca_32_baixo.png", T)),
           ("E3 perfil", sob(f"{E3A}/boca_32_perfil.png", T)), ("E3 baixo", sob(f"{E3A}/boca_32_baixo.png", T))]))
L.append(("4. Quadros intermediarios E3b (3/4): 0 | 5 | 10 | 15 | 20 | 26 | 32 graus", [(f"{g} graus", sob(f"{E3B}/boca_{g:02d}_34.png", (250, 250))) for g in (0, 5, 10, 15, 20, 26, 32)]))
L.append(("4b. Quadros intermediarios E3b (frente)", [(f"{g} graus", sob(f"{E3B}/boca_{g:02d}_frente.png", (250, 250))) for g in (0, 5, 10, 15, 20, 26, 32)]))
L.append(("5. Tamanho de jogo (render de 360 px do corpo inteiro): E3 anterior 0/20/32 | E3b 0/20/32",
          [(f"E3 {g}", sob(f"{E3A}/boca_{g:02d}_jogo.png").resize((300, 300), Image.NEAREST)) for g in (0, 20, 32)] +
          [(f"E3b {g}", sob(f"{E3B}/boca_{g:02d}_jogo.png").resize((300, 300), Image.NEAREST)) for g in (0, 20, 32)]))
c = (100, 380, 508, 683); c2 = (200, 250, 1050, 594)
L.append(("6. Membros (frente): referencia | E2 v11 | E3 anterior | E3b (so dianteiros, matiz do pelo vizinho)",
          [("referencia", ref.crop((0, 610, 608, 1293)).crop(c))] + [(n, sob(f"{d}/frente.png").crop(c)) for n, d in (("E2 v11", V11), ("E3 anterior", E3G), ("E3b", E3BG))]))
L.append(("6b. Membros e flancos (perfil): referencia | E2 v11 | E3 anterior (linha clara na coxa) | E3b",
          [("referencia", ref.crop((0, 0, 1217, 594)).crop(c2).resize((425, 172)))] +
          [(n, sob(f"{d}/lado.png").crop(c2).resize((425, 172))) for n, d in (("E2 v11", V11), ("E3 anterior", E3G), ("E3b", E3BG))]))
P = prancha("Leao Solar E3b - correcao da boca e juncao da mandibula (Blender, luz neutra; nada testado no Roblox)", L, SAIDA)
print("PRANCHA_OK", P.size)
