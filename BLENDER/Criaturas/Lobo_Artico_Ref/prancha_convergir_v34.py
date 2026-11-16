"""v34: pranchas e videos das PATAS CONVERGINDO (v33 x v34, mesmas cameras; copia adaptada do prancha_patas_v33). Saida review/v34_convergir/revisao/:
- 01_postura agora inclui a bitola (distancia lateral E-D no apoio) por acao;
- 03_frente_corrida: substituida por 03_tras_corrida (vista de tras, Corrida q4..q11);
- 01_postura.png: cabeca em relacao a cernelha e cauda (graus abaixo da horizontal) por acao, v31 x v32 (auditoria_real_v32);
- 01_frontal.png (no lugar de 01_angulos): curva do cotovelo na vista de frente e torcao do pe por quadro, v30 x v31;
- 00_referencia_resultado.png: referencia (repouso) + v30 em quatro vistas no meio do balanco de Andar, Trote e Corrida;
- 01_angulos.png: por marcha, carpo e dedos das dianteiras por quadro (fino = v29, grosso = v30) e faixas de apoio;
- 02_apoios.png: deslize/afundamento/flutuacao por pata e LOD na sequencia completa (v30 x v29) + folga no balanco;
- 03_frente_corrida.png: vista de frente, Corrida q7..q14, v29 x v30 (as patas que viravam de lado);
- video_Comparativo_Patas: v29 / v30, perfil E, frente, patas E e D, trechos de Andar, Trote e Corrida da sequencia, faixa com quadro;
- video_Comparativo_Patas_LODs (Corrida, LOD1/LOD2); video_Sequencia_LOW (8 vistas); video_Sequencia_LODs.
Uso: python prancha_convergir_v34.py (nesta pasta)"""
import os, json
from PIL import Image, ImageDraw
D = "review/v34_convergir"; O = os.path.join(D, "revisao"); os.makedirs(O, exist_ok=True); Q = os.path.join(D, "quadros"); Q9 = "review/v33_patas/quadros"; Q9L = Q9
G9 = json.load(open(os.path.join(D, "auditoria_v33.json"))); G0 = json.load(open(os.path.join(D, "auditoria_v34.json")))
A0 = json.load(open(os.path.join(D, "aud_marchas_v34.json"))); A9 = json.load(open("review/v33_patas/aud_marchas_v33.json"))
F0 = json.load(open(os.path.join(D, "folga_v34_lods.json"))); F9 = json.load(open("review/v33_patas/folga_v33_lods.json"))
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
    lin.append([cel(os.path.join(Q, "LOW_%s_t%04d.png" % (v, t)), "v34 %s %s" % (nm, v), w, h) for v in ("perfil_E", "frente", "patas_E", "patas_D")])
o = Image.new("RGB", (4 * (w + 4), len(lin) * (h + 4)), (40, 40, 40))
for r, l in enumerate(lin):
    for c, im in enumerate(l): o.paste(im, (c * (w + 4), r * (h + 4)))
o.save(os.path.join(O, "00_referencia_resultado.png")); print("PRANCHA 00")

# 01 postura
img = Image.new("RGB", (1500, 700), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "Postura de viagem: cabeca acima da cernelha (stud, media e faixa) e cauda (graus abaixo da horizontal), v33 (cinza) x v34 (cor). Real: cabeca no nivel do dorso ao se deslocar; cauda neutra ~45 graus", fill=(255, 235, 120))
ACS_ = ["Repouso", "Andar", "Trote", "Corrida", "Arrancada", "Frenagem", "VirarEsquerda", "VirarDireita", "AndarParaTrote", "TroteParaAndar", "TroteParaCorrida", "CorridaParaTrote"]
for j, (m, lo, hi, rot) in enumerate((("cabeca_rel_cernelha", -0.5, 1.5, "cabeca - cernelha (stud)"), ("cauda_corda_graus", 30, 90, "cauda (graus abaixo da horizontal)"))):
    y0 = 40 + j * 290; d.text((10, y0), rot, fill=(230, 230, 230)); zz = lambda v: y0 + 250 - 230 * (v - lo) / (hi - lo)
    d.line((10, zz(0 if j == 0 else 45), 1490, zz(0 if j == 0 else 45)), fill=(255, 140, 60))
    for i, ac in enumerate(ACS_):
        x = 20 + i * 122
        for dx, G, cor in ((0, G9, (150, 150, 150)), (40, G0, (120, 200, 255))):
            e = G["acoes"][ac]["estatisticas"][m]; d.rectangle((x + dx, zz(e["max"]), x + dx + 30, zz(e["min"])), fill=cor); d.line((x + dx - 3, zz(e["media"]), x + dx + 33, zz(e["media"])), fill=(255, 255, 255))
        d.text((x, y0 + 256), ac[:16], fill=(200, 200, 200))
y0 = 600; d.text((10, y0 - 20), "bitola no apoio (stud, dianteira / traseira): v33 -> v34", fill=(230, 230, 230))
for i, ac in enumerate(ACS_):
    b9 = G9["acoes"][ac]["bitola_no_apoio"]; b0 = G0["acoes"][ac]["bitola_no_apoio"]
    d.text((20 + (i % 4) * 370, y0 + (i // 4) * 18), "%s: %s/%s -> %s/%s" % (ac, b9["dianteira"], b9["traseira"], b0["dianteira"], b0["traseira"]), fill=(200, 200, 200))
img.save(os.path.join(O, "01_postura.png")); print("PRANCHA 01")

# 02 apoios e folga
img = Image.new("RGB", (1240, 640), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "v34: pior deslize por pata e LOD em TODAS as fases da sequencia completa (limite 0,03), v33 -> v34; e menor folga da pata DIANTEIRA no ar (malha)", fill=(255, 235, 120))
for i, L in enumerate(("LOW", "LOD1", "LOD2")):
    for j, k in enumerate(PAT):
        f0 = A0["niveis"][L]["apoios"][k]; f9 = A9["niveis"][L]["apoios"][k]
        ds0 = max(f["deslize"] for f in f0); ds9 = max(f["deslize"] for f in f9); af = max(f["afundamento"] for f in f0); fl = max(f["flutuacao"] for f in f0)
        x0 = 20 + i * 405; y0 = 40 + j * 80
        d.text((x0, y0), "%s %s desl %.4f -> %.4f  afund %.4f flut %.4f" % (L, k, ds9, ds0, af, fl), fill=COR[k]); d.rectangle((x0, y0 + 18, x0 + 370, y0 + 38), outline=(90, 90, 90))
        d.rectangle((x0, y0 + 18, x0 + 370 * min(1, ds0 / 0.03), y0 + 38), fill=COR[k] if ds0 <= 0.03 else (255, 0, 0))
y = 380; d.text((20, y), "folga minima no ar (stud; chao = sola no repouso), v33 -> v34, patas dianteiras:", fill=(230, 230, 230))
for i, L in enumerate(("LOW", "LOD1", "LOD2")):
    for j, ac in enumerate(("Andar", "Trote", "Corrida", "Arrancada", "Frenagem", "VirarEsquerda", "VirarDireita")):
        t = "%s %s: DE %.3f -> %.3f | DD %.3f -> %.3f" % (L, ac, F9[L][ac]["DE"][0], F0[L][ac]["DE"][0], F9[L][ac]["DD"][0], F0[L][ac]["DD"][0])
        d.text((20 + i * 405, y + 22 + j * 30), t, fill=(200, 200, 200))
img.save(os.path.join(O, "02_apoios.png")); print("PRANCHA 02")

# 03 frente corrida
rows = []
for tag, QQ in (("v33", Q9), ("v34", Q)):
    row = Image.new("RGB", (8 * 240, 258), (30, 30, 30)); d = ImageDraw.Draw(row)
    for c, t in enumerate(range(263, 271)):
        p = os.path.join(QQ, "LOW_tras_t%04d.png" % t)
        if os.path.exists(p):
            im = Image.open(p).convert("RGB"); W_, H_ = im.size; im = im.crop((int(W_ * 0.19), int(H_ * 0.5), int(W_ * 0.81), H_)); im.thumbnail((240, 240)); row.paste(im, (c * 240, 18))
        d.text((c * 240 + 4, 2), "%s Corrida q%d tras" % (tag, t - 259), fill=(255, 235, 120))
    rows.append(row)
o = Image.new("RGB", (1920, 516)); [o.paste(r, (0, i * 258)) for i, r in enumerate(rows)]; o.save(os.path.join(O, "03_tras_corrida.png")); print("PRANCHA 03")


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
mosaico("Comparativo_Patas", IDX, lambda i: [[cel(os.path.join(QQ, "LOW_%s_t%04d.png" % (v, i)), "%s LOW %s" % (tag, v), 400, 300) for v in ("frente", "tras", "34_E", "patas_D")]
                                             for tag, QQ in (("v33", Q9), ("v34", Q))], 4, 2, 400, 300)
mosaico("Comparativo_Patas_LODs", list(range(259, 301)), lambda i: [[cel(os.path.join(QQ, "%s_%s_t%04d.png" % (L, v, i)), "%s %s %s" % (tag, L, v), 400, 300) for L in ("LOD1", "LOD2") for v in ("frente", "perfil_E")]
                                                                     for tag, QQ in (("v33", Q9L), ("v34", Q))], 4, 2, 400, 300)
mosaico("Sequencia_LOW", list(range(len(LT))), lambda i: [[cel(os.path.join(Q, "LOW_%s_t%04d.png" % (v, i)), "v34 LOW %s" % v, 400, 300) for v in ("perfil_D", "perfil_E", "frente", "tras")],
                                                          [cel(os.path.join(Q, "LOW_%s_t%04d.png" % (v, i)), "v34 LOW %s" % v, 400, 300) for v in ("34_E", "patas_E", "patas_D", "traseiras_E")]], 4, 2, 400, 300)
mosaico("Sequencia_LODs", list(range(len(LT))), lambda i: [[cel(os.path.join(Q, "%s_%s_t%04d.png" % (L, v, i)), "v34 %s %s" % (L, v), 400, 300) for v in ("perfil_E", "frente", "patas_E")] for L in ("LOD1", "LOD2")], 3, 2, 400, 300)
print("PRANCHA_CONVERGIR_V34_OK")
