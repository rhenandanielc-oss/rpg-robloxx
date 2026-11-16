"""v30: pranchas e videos das patas dianteiras (v29 x v30, mesmas cameras). Saida review/v30_patas/revisao/:
- 00_referencia_resultado.png: referencia (repouso) + v30 em quatro vistas no meio do balanco de Andar, Trote e Corrida;
- 01_angulos.png: por marcha, carpo e dedos das dianteiras por quadro (fino = v29, grosso = v30) e faixas de apoio;
- 02_apoios.png: deslize/afundamento/flutuacao por pata e LOD na sequencia completa (v30 x v29) + folga no balanco;
- 03_frente_corrida.png: vista de frente, Corrida q7..q14, v29 x v30 (as patas que viravam de lado);
- video_Comparativo_Patas: v29 / v30, perfil E, frente, patas E e D, trechos de Andar, Trote e Corrida da sequencia, faixa com quadro;
- video_Comparativo_Patas_LODs (Corrida, LOD1/LOD2); video_Sequencia_LOW (8 vistas); video_Sequencia_LODs.
Uso: python prancha_patas_v30.py (nesta pasta)"""
import os, json
from PIL import Image, ImageDraw
D = "review/v30_patas"; O = os.path.join(D, "revisao"); os.makedirs(O, exist_ok=True); Q = os.path.join(D, "quadros"); Q9 = "review/v29_desacel/quadros"; Q9L = os.path.join(D, "quadros_v29")
G9 = json.load(open(os.path.join(D, "giro_v29.json"))); G0 = json.load(open(os.path.join(D, "giro_v30.json")))
A0 = json.load(open(os.path.join(D, "aud_marchas_v30.json"))); A9 = json.load(open("review/v29_desacel/aud_marchas_v29.json"))
F0 = json.load(open(os.path.join(D, "folga_v30_lods.json"))); F9 = json.load(open(os.path.join(D, "folga_v29_lods.json")))
PAT = ("DE", "DD", "TE", "TD"); COR = {"DE": (60, 110, 255), "DD": (240, 50, 40), "TE": (40, 200, 70), "TD": (240, 200, 20)}
REF = "../../../REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png"
LT = json.load(open(os.path.join(Q, "linha_LOW.json")))["linha_do_tempo"]
JAN = [(0, 71, "Andar"), (142, 195, "Trote"), (259, 300, "Corrida")]


def cel(p, txt, w, h):
    im = Image.new("RGB", (w, h), (24, 24, 28))
    if p and os.path.exists(p):
        s = Image.open(p).convert("RGB"); s.thumbnail((w, h)); im.paste(s, ((w - s.width) // 2, (h - s.height) // 2))
    elif p:
        ImageDraw.Draw(im).text((8, h // 2), "falta " + os.path.basename(p), fill=(255, 80, 80))
    dd = ImageDraw.Draw(im); dd.rectangle((0, 0, w, 16), fill=(0, 0, 0)); dd.text((4, 2), txt, fill=(255, 235, 120)); return im


def graf(d, x0, y0, w, h, ys, ymin, ymax, cor, larg):
    n = max(1, len(ys) - 1); d.line([(x0 + w * i / n, y0 + h - h * (max(ymin, min(ymax, y)) - ymin) / (ymax - ymin)) for i, y in enumerate(ys)], fill=cor, width=larg)


# 00 referencia x resultado
w, h = 400, 300; lin = [[cel(REF, "referencia (repouso; nao comprova biomecanica)", w, h)] + [Image.new("RGB", (w, h), (24, 24, 28))] * 3]
for t, nm in ((1, "Andar q1"), (154, "Trote q12"), (271, "Corrida q12")):
    lin.append([cel(os.path.join(Q, "LOW_%s_t%04d.png" % (v, t)), "v30 %s %s" % (nm, v), w, h) for v in ("perfil_E", "frente", "patas_E", "patas_D")])
o = Image.new("RGB", (4 * (w + 4), len(lin) * (h + 4)), (40, 40, 40))
for r, l in enumerate(lin):
    for c, im in enumerate(l): o.paste(im, (c * (w + 4), r * (h + 4)))
o.save(os.path.join(O, "00_referencia_resultado.png")); print("PRANCHA 00")

# 01 angulos
img = Image.new("RGB", (1860, 1000), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "Patas dianteiras: angulo do carpo (cima) e dos dedos (baixo) por quadro, graus (0 = reto). Fino = v29, grosso = v30. Barras = pata no chao (so o balanco muda)", fill=(255, 235, 120))
for c, ac in enumerate(("Andar", "Trote", "Corrida")):
    x0 = 20 + c * 615
    for j, (m, top) in enumerate((("carpo", 160), ("dedos", 100))):
        y0 = 30 + j * 420; d.rectangle((x0, y0, x0 + 590, y0 + 340), outline=(90, 90, 100))
        mx9 = {k: G9[ac]["faixas"][k][m][1] for k in ("DE", "DD")}; mx0 = {k: G0[ac]["faixas"][k][m][1] for k in ("DE", "DD")}
        d.text((x0 + 4, y0 + 2), "%s %s max: DE %.0f -> %.0f, DD %.0f -> %.0f" % (ac, m, mx9["DE"], mx0["DE"], mx9["DD"], mx0["DD"]), fill=(230, 230, 230))
        for k in ("DE", "DD"):
            graf(d, x0, y0 + 20, 590, 320, [f[k][m] for f in G9[ac]["por_quadro"]], 0, top, tuple(int(v * 0.55) for v in COR[k]), 1)
            graf(d, x0, y0 + 20, 590, 320, [f[k][m] for f in G0[ac]["por_quadro"]], 0, top, COR[k], 3)
img.save(os.path.join(O, "01_angulos.png")); print("PRANCHA 01")

# 02 apoios e folga
img = Image.new("RGB", (1240, 640), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "v30: pior deslize por pata e LOD em TODAS as fases da sequencia completa (limite 0,03), v29 -> v30; e menor folga da pata DIANTEIRA no ar (malha)", fill=(255, 235, 120))
for i, L in enumerate(("LOW", "LOD1", "LOD2")):
    for j, k in enumerate(PAT):
        f0 = A0["niveis"][L]["apoios"][k]; f9 = A9["niveis"][L]["apoios"][k]
        ds0 = max(f["deslize"] for f in f0); ds9 = max(f["deslize"] for f in f9); af = max(f["afundamento"] for f in f0); fl = max(f["flutuacao"] for f in f0)
        x0 = 20 + i * 405; y0 = 40 + j * 80
        d.text((x0, y0), "%s %s desl %.4f -> %.4f  afund %.4f flut %.4f" % (L, k, ds9, ds0, af, fl), fill=COR[k]); d.rectangle((x0, y0 + 18, x0 + 370, y0 + 38), outline=(90, 90, 90))
        d.rectangle((x0, y0 + 18, x0 + 370 * min(1, ds0 / 0.03), y0 + 38), fill=COR[k] if ds0 <= 0.03 else (255, 0, 0))
y = 380; d.text((20, y), "folga minima no ar (stud; chao = sola no repouso), v29 -> v30, patas dianteiras:", fill=(230, 230, 230))
for i, L in enumerate(("LOW", "LOD1", "LOD2")):
    for j, ac in enumerate(("Andar", "Trote", "Corrida", "Arrancada", "Frenagem", "VirarEsquerda", "VirarDireita")):
        t = "%s %s: DE %.3f -> %.3f | DD %.3f -> %.3f" % (L, ac, F9[L][ac]["DE"][0], F0[L][ac]["DE"][0], F9[L][ac]["DD"][0], F0[L][ac]["DD"][0])
        d.text((20 + i * 405, y + 22 + j * 30), t, fill=(200, 200, 200))
img.save(os.path.join(O, "02_apoios.png")); print("PRANCHA 02")

# 03 frente corrida
rows = []
for tag, QQ in (("v29", Q9), ("v30", Q)):
    row = Image.new("RGB", (8 * 240, 258), (30, 30, 30)); d = ImageDraw.Draw(row)
    for c, t in enumerate(range(266, 274)):
        p = os.path.join(QQ, "LOW_frente_t%04d.png" % t)
        if os.path.exists(p):
            im = Image.open(p).convert("RGB"); W_, H_ = im.size; im = im.crop((int(W_ * 0.19), int(H_ * 0.5), int(W_ * 0.81), H_)); im.thumbnail((240, 240)); row.paste(im, (c * 240, 18))
        d.text((c * 240 + 4, 2), "%s Corrida q%d frente" % (tag, t - 259), fill=(255, 235, 120))
    rows.append(row)
o = Image.new("RGB", (1920, 516)); [o.paste(r, (0, i * 258)) for i, r in enumerate(rows)]; o.save(os.path.join(O, "03_frente_corrida.png")); print("PRANCHA 03")


def faixa(i, wtot, rot=""):
    im = Image.new("RGB", (wtot, 30), (10, 10, 12)); dd = ImageDraw.Draw(im); dd.text((8, 8), "t%03d  %s  %s" % (i, LT[i], rot), fill=(255, 235, 120)); return im
def mosaico(nome, idxs, fn, ncol, nlin, w, h):
    dv = os.path.join(O, "video_" + nome); os.makedirs(dv, exist_ok=True); W_, H_ = ncol * (w + 4), nlin * (h + 4) + 30
    for j, i in enumerate(idxs):
        o = Image.new("RGB", (W_, H_), (40, 40, 40)); o.paste(faixa(i, W_), (0, 0))
        for r, l in enumerate(fn(i)):
            for c, im in enumerate(l): o.paste(im, (c * (w + 4), 30 + r * (h + 4)))
        o.save(os.path.join(dv, "v_%04d.png" % j))
    open(os.path.join(dv, "res.txt"), "w").write("%d %d" % (W_, H_)); print("VIDEO_QUADROS", nome, len(idxs))
IDX = [i for a, b, _ in JAN for i in range(a, b + 1)]
mosaico("Comparativo_Patas", IDX, lambda i: [[cel(os.path.join(QQ, "LOW_%s_t%04d.png" % (v, i)), "%s LOW %s" % (tag, v), 400, 300) for v in ("perfil_E", "frente", "patas_E", "patas_D")]
                                             for tag, QQ in (("v29", Q9), ("v30", Q))], 4, 2, 400, 300)
mosaico("Comparativo_Patas_LODs", list(range(259, 301)), lambda i: [[cel(os.path.join(QQ, "%s_%s_t%04d.png" % (L, v, i)), "%s %s %s" % (tag, L, v), 400, 300) for L in ("LOD1", "LOD2") for v in ("frente", "patas_E")]
                                                                     for tag, QQ in (("v29", Q9L), ("v30", Q))], 4, 2, 400, 300)
mosaico("Sequencia_LOW", list(range(len(LT))), lambda i: [[cel(os.path.join(Q, "LOW_%s_t%04d.png" % (v, i)), "v30 LOW %s" % v, 400, 300) for v in ("perfil_D", "perfil_E", "frente", "tras")],
                                                          [cel(os.path.join(Q, "LOW_%s_t%04d.png" % (v, i)), "v30 LOW %s" % v, 400, 300) for v in ("34_E", "patas_E", "patas_D", "traseiras_E")]], 4, 2, 400, 300)
mosaico("Sequencia_LODs", list(range(len(LT))), lambda i: [[cel(os.path.join(Q, "%s_%s_t%04d.png" % (L, v, i)), "v30 %s %s" % (L, v), 400, 300) for v in ("perfil_E", "frente", "patas_E")] for L in ("LOD1", "LOD2")], 3, 2, 400, 300)
print("PRANCHA_PATAS_V30_OK")
