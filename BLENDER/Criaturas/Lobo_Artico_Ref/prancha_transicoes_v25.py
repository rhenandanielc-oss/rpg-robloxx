"""v25: pranchas e mosaicos de video do bloco Arrancada + Frenagem. Saida review/v25_transicoes/revisao/:
- 01_curvas.png: v(t) e X(t) (stud/s, stud) da Arrancada e da Frenagem + faixas de APOIO por pata (cronograma do gerador) no mesmo
  eixo de tempo; e a sequencia completa (Repouso | Arrancada | Corrida x3 | Frenagem | Repouso) com as emendas marcadas;
- 02_apoios.png: deslize maximo por pata e LOD nas fases de apoio que tocam Arrancada/Frenagem (sequencia continua) e afundamento,
  linha 0,03 (valores arredondados para cima na 4a casa);
- 03_repouso.png: referencia | Repouso v24 | Repouso v25 | ultimo quadro da Frenagem (= Repouso q0), corpo inteiro;
- video_Sequencia_LOW, video_Sequencia_LODs, video_Closes_Arrancada, video_Closes_Frenagem: mosaicos para MP4 (normal e 0,5x).
Uso: python prancha_transicoes_v25.py (nesta pasta)"""
import os, json, math
from PIL import Image, ImageDraw
D = "review/v25_transicoes"; O = os.path.join(D, "revisao"); os.makedirs(O, exist_ok=True)
REF = "../../../REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png"
TJ = json.load(open("anim_v25/transicoes_v25.json")); AS = json.load(open(os.path.join(D, "aud_seq_v25.json")))
PAT = ("DE", "DD", "TE", "TD"); COR = {"DE": (60, 110, 255), "DD": (240, 50, 40), "TE": (40, 200, 70), "TD": (240, 200, 20)}; FPS = 30
def sobe(x): return math.ceil(x * 10000 - 1e-9) / 10000
def grafico(d, x0, y0, w, h, ts, ys, ymax, cor, rot):
    d.rectangle((x0, y0, x0 + w, y0 + h), outline=(90, 90, 100)); d.text((x0 + 4, y0 + 2), rot, fill=(230, 230, 230))
    pts = [(x0 + w * t / ts[-1], y0 + h - h * y / ymax) for t, y in zip(ts, ys)]
    d.line(pts, fill=cor, width=2)
# 1. curvas
img = Image.new("RGB", (1800, 1000), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "Curvas tecnicas v25 (parametros, nao regra de jogo): velocidade v (stud/s), deslocamento |X| (stud) e faixas de APOIO por pata; tempo em quadros (30 qps)", fill=(255, 235, 120))
for c, ac in enumerate(("Arrancada", "Frenagem")):
    A = TJ["acoes"][ac]; n = A["quadros"]; ts = list(range(n + 1)); x0 = 20 + c * 890
    grafico(d, x0, 40, 860, 230, ts, A["v_por_quadro"], 22, (255, 140, 60), "%s: v (0..22 stud/s); %d quadros = %.2f s" % (ac, n, n / FPS))
    grafico(d, x0, 290, 860, 200, ts, [-x for x in A["X_por_quadro"]], max(1e-6, -A["X_por_quadro"][-1]) * 1.05, (120, 200, 255), "%s: |X| (0..%.1f stud)" % (ac, -A["X_por_quadro"][-1]))
    for i, k in enumerate(PAT):
        yb = 510 + i * 34; d.text((x0, yb + 6), k, fill=COR[k])
        for q in range(n + 1):
            if A["apoio_por_quadro"][k][q]: d.rectangle((x0 + 30 + 830 * q / n, yb, x0 + 30 + 830 * (q + 1) / n, yb + 26), fill=COR[k])
    d.text((x0, 650), "apoio = pata no chao (cronograma do gerador); intervalos em quadros: " + "; ".join("%s %s" % (k, ",".join("%.1f-%.1f" % tuple(s) for s in A["apoios_quadros_continuos"][k])) for k in PAT)[:150], fill=(200, 200, 200))
LT = AS["linha_do_tempo"]; X = AS["X"]; vs = [0.0] + [(X[i - 1] - X[i]) * FPS for i in range(1, len(X))]
grafico(d, 20, 700, 1750, 200, list(range(len(X))), vs, 22, (255, 140, 60), "Sequencia continua: v por quadro (stud/s); linhas = emendas (Repouso | Arrancada | Corrida x3 | Frenagem | Repouso)")
for i in range(1, len(LT)):
    if LT[i].split()[0] != LT[i - 1].split()[0]: xx = 20 + 1750 * i / (len(LT) - 1); d.line((xx, 700, xx, 900), fill=(200, 200, 200)); d.text((xx + 3, 905), LT[i], fill=(200, 200, 200))
img.save(os.path.join(O, "01_curvas.png")); print("PRANCHA 01")
# 2. apoios
img = Image.new("RGB", (1500, 470), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "Deslize maximo (stud) nas fases de apoio que tocam Arrancada/Frenagem, sequencia continua, pontos fixos (metodo v24); linha = 0,03; afund = afundamento max", fill=(255, 235, 120))
for c, L in enumerate(("LOW", "LOD1", "LOD2")):
    x0 = 10 + c * 495; d.rectangle((x0, 30, x0 + 485, 460), outline=(90, 90, 100)); d.text((x0 + 6, 34), L, fill=(255, 255, 255)); base = 420; esc = 330 / 0.04
    d.line((x0 + 5, base - 0.03 * esc, x0 + 480, base - 0.03 * esc), fill=(255, 120, 120))
    for i, k in enumerate(PAT):
        fs = [f for f in AS["niveis"][L]["apoios"][k] if any(a in f["acoes"] for a in ("Arrancada", "Frenagem"))]; m = max(f["deslize"] for f in fs); af = max(f["afundamento"] for f in fs)
        bx = x0 + 30 + i * 115; d.rectangle((bx, base - m * esc, bx + 60, base), fill=COR[k]); d.text((bx, base + 6), "%s %.4f" % (k, sobe(m)), fill=(230, 230, 230)); d.text((bx, base + 20), "afund %.4f" % af, fill=(180, 180, 180))
img.save(os.path.join(O, "02_apoios.png")); print("PRANCHA 02")
# 3. repouso
def cel(p, txt, w, h):
    im = Image.new("RGB", (w, h), (24, 24, 28))
    if p and os.path.exists(p): s = Image.open(p).convert("RGB"); s.thumbnail((w, h)); im.paste(s, ((w - s.width) // 2, (h - s.height) // 2))
    elif p: ImageDraw.Draw(im).text((8, h // 2), "falta " + os.path.basename(p), fill=(255, 80, 80))
    dd = ImageDraw.Draw(im); dd.rectangle((0, 0, w, 16), fill=(0, 0, 0)); dd.text((4, 2), txt, fill=(255, 235, 120)); return im
VS = ("c_perfil_D", "c_perfil_E", "c_34_D", "c_tras"); w, h = 420, 315
lin = [[cel(REF, "REFERENCIA (repouso)", w, h)] + [cel(None, "", w, h)] * 3]
lin.append([cel("%s/repouso/v24/real_LOW_repouso_%s_q0000.png" % (D, v), "Repouso v24 %s" % v, w, h) for v in VS])
lin.append([cel("%s/repouso/v25/real_LOW_repouso_%s_q0000.png" % (D, v), "Repouso v25 %s" % v, w, h) for v in VS])
lin.append([cel("%s/repouso/v25_fim_frenagem/real_LOW_frenagem_fim_%s_q0048.png" % (D, v), "Frenagem ultimo quadro (= Repouso q0) %s" % v, w, h) for v in VS])
o = Image.new("RGB", (4 * (w + 4), 4 * (h + 4)), (40, 40, 40))
for r, l in enumerate(lin):
    for c, im in enumerate(l): o.paste(im, (c * (w + 4), r * (h + 4)))
o.save(os.path.join(O, "03_repouso.png")); print("PRANCHA 03")
# 4. videos
def faixa(i, wtot):
    im = Image.new("RGB", (wtot, 44), (10, 10, 12)); dd = ImageDraw.Draw(im); ac_, q = LT[i].split(" "); q = int(q[1:])
    no = [k for k in PAT if ((ac_ == "Repouso") or (ac_ in ("Arrancada", "Frenagem") and TJ["acoes"][ac_]["apoio_por_quadro"][k][q]) or
          (ac_ == "Corrida" and ((q / 30 / 0.466667) - {"TE": 0, "TD": 0.08, "DD": 0.30, "DE": 0.40}[k]) % 1.0 < 0.28))]
    dd.text((8, 4), "t%03d  %s  |  v = %5.2f stud/s  |  |X| = %6.2f stud  |  no chao: %s" % (i, LT[i], vs[i], -X[i], " ".join(no) or "-"), fill=(255, 235, 120))
    bx = 8; bw = wtot - 16
    dd.rectangle((bx, 26, bx + bw, 38), outline=(80, 80, 80))
    for j in range(1, len(LT)):
        if LT[j].split()[0] != LT[j - 1].split()[0]: xx = bx + bw * j / (len(LT) - 1); dd.line((xx, 26, xx, 38), fill=(150, 150, 150))
    xx = bx + bw * i / (len(LT) - 1); dd.rectangle((xx - 2, 24, xx + 2, 40), fill=(255, 120, 60)); return im
Q = os.path.join(D, "quadros")
def mosaico(nome, linhas_fn, ncol, nlin, w, h, n):
    dv = os.path.join(O, "video_" + nome); os.makedirs(dv, exist_ok=True); W_, H_ = ncol * (w + 4), nlin * (h + 4) + 44
    for i in range(n):
        o = Image.new("RGB", (W_, H_), (40, 40, 40)); o.paste(faixa(i, W_) if nome.startswith("Sequencia") else Image.new("RGB", (W_, 44), (10, 10, 12)), (0, 0))
        for r, l in enumerate(linhas_fn(i)):
            for c, im in enumerate(l): o.paste(im, (c * (w + 4), 44 + r * (h + 4)))
        o.save(os.path.join(dv, "v_%04d.png" % i))
    open(os.path.join(dv, "res.txt"), "w").write("%d %d" % (W_, H_)); print("VIDEO_QUADROS", nome, n)
NT = len(LT)
mosaico("Sequencia_LOW", lambda i: [[cel(os.path.join(Q, "LOW_%s_t%04d.png" % (v, i)), "LOW %s" % v, 480, 360) for v in ("perfil_D", "perfil_E", "frente", "tras")],
                                    [cel(os.path.join(Q, "LOW_%s_t%04d.png" % (v, i)), "LOW %s" % v, 480, 360) for v in ("34_E", "patas_E", "patas_D", "fixa_D")]], 4, 2, 480, 360, NT)
mosaico("Sequencia_LODs", lambda i: [[cel(os.path.join(Q, "%s_%s_t%04d.png" % (L, v, i)), "%s %s" % (L, v), 400, 300) for v in ("perfil_D", "patas_E", "patas_D")] for L in ("LOD1", "LOD2")], 3, 2, 400, 300, NT)
for ac, n in (("Arrancada", TJ["acoes"]["Arrancada"]["quadros"] + 1), ("Frenagem", TJ["acoes"]["Frenagem"]["quadros"] + 1)):
    mosaico("Closes_" + ac, lambda q, ac=ac: [[cel(os.path.join(D, "closes", "%s_%s_%s_q%04d.png" % (m, ac, v, q)), "%s %s %s q%d" % (ac, v, m, q), 480, 360) for v in ("fresta_E", "garganta_E", "flanco_D_baixo")] for m in ("real", "cores")], 3, 2, 480, 360, n)
print("PRANCHA_TRANSICOES_V25_OK")
