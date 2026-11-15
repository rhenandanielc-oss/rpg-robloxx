"""Prancha base x variante (frente, perfil, 3/4, miniatura) a partir de render_vistas.py.
Uso: python scripts/prancha_comparar.py <pasta_vistas> <prefixo_variante> <argila|textura> <saida.png> [ref.png]"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
D, VAR, MODO, SAIDA = sys.argv[1:5]; REF = sys.argv[5] if len(sys.argv) > 5 else None
F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t)
def rot(im, t):
    o = Image.new("RGB", (im.width, im.height + 26), (55, 53, 51)); o.paste(im, (0, 26)); ImageDraw.Draw(o).text((6, 5), t, fill=(240, 240, 240), font=F(15)); return o
def lin(ims, gap=8):
    o = Image.new("RGB", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), (45, 43, 42)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width + gap
    return o
def col(ims, gap=8):
    o = Image.new("RGB", (max(i.width for i in ims), sum(i.height for i in ims) + gap * (len(ims) - 1)), (45, 43, 42)); y = 0
    for i in ims: o.paste(i, (0, y)); y += i.height + gap
    return o
def v(pre, vista, h):
    im = Image.open(os.path.join(D, f"{pre}_{MODO}_{vista}.png")).convert("RGB")
    if vista == "miniatura": return im.resize((im.width * 2, im.height * 2), Image.NEAREST)   # 96 px ampliado 2x, sem suavizar
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
nome = {"base": "Javali Silvestre (base)", VAR: "Javali-do-Brejo (" + VAR.split("_")[-1] + ")"}
linhas = []
for vista, h, t in (("perfil", 300, "perfil"), ("34", 330, "três quartos"), ("frente", 300, "frente")):
    linhas.append(lin([rot(v("base", vista, h), f"{nome['base']} · {t}"), rot(v(VAR, vista, h), f"{nome[VAR]} · {t}")]))
linhas.append(lin([rot(v("base", "rosto_perfil", 250), "base · rosto perfil"), rot(v(VAR, "rosto_perfil", 250), "brejo · rosto perfil"),
                   rot(v("base", "rosto_34", 250), "base · rosto 3/4"), rot(v(VAR, "rosto_34", 250), "brejo · rosto 3/4")], 6))
linhas.append(lin([rot(v("base", "baixo_34", 250), "base · de baixo (ventre e patas)"), rot(v(VAR, "baixo_34", 250), "brejo · de baixo (ventre e patas)")]))
mini = lin([rot(v("base", "miniatura", 0), "base · miniatura 96 px"), rot(v(VAR, "miniatura", 0), "brejo · miniatura 96 px")])
if REF:
    r = Image.open(REF).convert("RGB"); r = r.resize((round(r.width * 150 / r.height), 150), Image.LANCZOS)
    mini = lin([mini, rot(r, "referência anatômica da base (Javali Silvestre)")])
corpo = col(linhas + [mini])
topo = Image.new("RGB", (corpo.width, 62), (40, 38, 36)); d = ImageDraw.Draw(topo)
tit = {"argila": "ANTES do acabamento (argila: só forma e proporção)", "textura": "DEPOIS do acabamento (texturas assadas)"}[MODO]
d.text((8, 6), f"Javali Silvestre × Javali-do-Brejo — {tit}", fill=(250, 250, 250), font=F(19))
d.text((8, 36), "Sem ficha própria em REFERENCIAS/pantano-nebuloso/javali-do-brejo/ → direção PROVISÓRIA para revisão. Pose de descanso do rig, mesmas câmeras.", fill=(210, 210, 210), font=F(13))
col([topo, corpo], 0).save(SAIDA); print("PRANCHA", SAIDA)
