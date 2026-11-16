"""v28: pranchas e mosaicos de video das trocas de marcha. Saida review/v28_marchas/revisao/:
- 01_curvas.png: por transicao, velocidade v(t) (stud/s, parametro tecnico), peso da mistura s(t), cadencia (Hz) e faixas de APOIO;
- 02_apoios.png: deslize maximo e afundamento por pata e LOD nas fases que tocam as transicoes (sequencia completa, metodo v24);
- video_Sequencia_LOW (7 vistas, camera acompanha), video_Sequencia_LODs (LOD1/LOD2), video_Closes_<acao> (real e cores).
Uso: python prancha_marchas_v28.py (nesta pasta)"""
import os, json
from PIL import Image, ImageDraw
D = "review/v28_marchas"; O = os.path.join(D, "revisao"); os.makedirs(O, exist_ok=True); Q = os.path.join(D, "quadros")
TJ = json.load(open("anim_v28/marchas_v28.json")); AU = json.load(open(os.path.join(D, "aud_marchas_v28.json")))
PAT = ("DE", "DD", "TE", "TD"); COR = {"DE": (60, 110, 255), "DD": (240, 50, 40), "TE": (40, 200, 70), "TD": (240, 200, 20)}
TRS = ("AndarParaTrote", "TroteParaAndar", "TroteParaCorrida", "CorridaParaTrote")


def cel(p, txt, w, h):
    im = Image.new("RGB", (w, h), (24, 24, 28))
    if p and os.path.exists(p):
        s = Image.open(p).convert("RGB"); s.thumbnail((w, h)); im.paste(s, ((w - s.width) // 2, (h - s.height) // 2))
    elif p:
        ImageDraw.Draw(im).text((8, h // 2), "falta " + os.path.basename(p), fill=(255, 80, 80))
    dd = ImageDraw.Draw(im); dd.rectangle((0, 0, w, 16), fill=(0, 0, 0)); dd.text((4, 2), txt, fill=(255, 235, 120)); return im


def graf(d, x0, y0, w, h, ys, ymin, ymax, cor, rot):
    d.rectangle((x0, y0, x0 + w, y0 + h), outline=(90, 90, 100)); d.text((x0 + 4, y0 + 2), rot, fill=(230, 230, 230)); n = max(1, len(ys) - 1)
    d.line([(x0 + w * i / n, y0 + h - h * (y - ymin) / (ymax - ymin)) for i, y in enumerate(ys)], fill=cor, width=2)


img = Image.new("RGB", (1820, 1180), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "Trocas de marcha v28 (parametros tecnicos): velocidade, peso da mistura s (0 = origem, 1 = destino), cadencia e apoios por pata", fill=(255, 235, 120))
for c, ac in enumerate(TRS):
    A = TJ["acoes"][ac]; x0 = 20 + (c % 2) * 900; y0 = 30 + (c // 2) * 575; n = A["quadros"]
    vmax = max(A["v_por_quadro"]) * 1.1
    graf(d, x0, y0, 860, 130, A["v_por_quadro"], 0, vmax, (255, 140, 60), "%s: v (stud/s) %.2f -> %.2f, %d quadros = %.2f s, %.1f stud" % (ac, A["v_por_quadro"][0], A["v_por_quadro"][-1], n, n / 30, A["distancia_total"]))
    graf(d, x0, y0 + 140, 860, 90, A["s_por_quadro"], -0.05, 1.05, (120, 200, 255), "peso s (rampa %.1f s a partir de %.2f s)" % (A["rampa_s"], A["t_inicio_rampa_s"]))
    graf(d, x0, y0 + 240, 860, 90, A["cadencia_hz_por_quadro"], 0, 2.4, (200, 120, 255), "cadencia (ciclos/s)")
    for i, k in enumerate(PAT):
        yb = y0 + 340 + i * 26; d.text((x0, yb + 5), k, fill=COR[k])
        for q in range(n + 1):
            if A["apoio_por_quadro"][k][q]: d.rectangle((x0 + 30 + 830 * q / n, yb, x0 + 30 + 830 * (q + 1) / n, yb + 20), fill=COR[k])
    d.text((x0, y0 + 450), "fases %s -> %s; mudanca de fase por pata %s" % (A["origem"], A["destino"], {k: round(v, 2) for k, v in A["mudanca_fase_por_pata"].items()}), fill=(200, 200, 200))
    d.text((x0, y0 + 470), "entra: %s | sai: %s | erro IK max %.3f" % (A["entrada"], A["saida"], A["erro_ik_max"]), fill=(200, 200, 200))
img.save(os.path.join(O, "01_curvas.png")); print("PRANCHA 01")

img = Image.new("RGB", (1200, 430), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "v28: deslize maximo por pata (stud) nas fases que tocam as transicoes (sequencia Andar-Trote-Corrida-Trote-Andar; limite 0,03)", fill=(255, 235, 120))
for i, L in enumerate(("LOW", "LOD1", "LOD2")):
    for j, k in enumerate(PAT):
        fs = [f for f in AU["niveis"][L]["apoios"][k] if any(x in TRS for x in f["acoes"])]
        ds = max(f["deslize"] for f in fs); af = max(f["afundamento"] for f in fs); x0 = 20 + i * 390; y0 = 50 + j * 88
        d.text((x0, y0), "%s %s  deslize %.4f  afund %.4f" % (L, k, ds, af), fill=COR[k]); d.rectangle((x0, y0 + 18, x0 + 360, y0 + 40), outline=(90, 90, 90))
        d.rectangle((x0, y0 + 18, x0 + 360 * min(1, ds / 0.03), y0 + 40), fill=COR[k] if ds <= 0.03 else (255, 0, 0))
img.save(os.path.join(O, "02_apoios.png")); print("PRANCHA 02")

J = json.load(open(os.path.join(Q, "linha_LOW.json"))); LT = J["linha_do_tempo"]; X = J["X"]
def v_de(i):
    j0, j1 = max(0, i - 1), min(len(X) - 1, i + 1); return -(X[j1] - X[j0]) * 30 / max(1, j1 - j0)
def no_chao(ent):
    ac_, q = ent.split(" "); q = int(q[1:])
    if ac_ in TJ["acoes"]: return [k for k in PAT if TJ["acoes"][ac_]["apoio_por_quadro"][k][q]]
    return None
def faixa(i, wtot):
    im = Image.new("RGB", (wtot, 44), (10, 10, 12)); dd = ImageDraw.Draw(im); nc = no_chao(LT[i])
    dd.text((8, 4), "t%03d  %s  |  v = %6.2f stud/s  |  %s" % (i, LT[i], v_de(i), ("no chao: " + " ".join(nc)) if nc is not None else "marcha ciclica"), fill=(255, 235, 120))
    bx, bw = 8, wtot - 16; dd.rectangle((bx, 26, bx + bw, 38), outline=(80, 80, 80))
    for j in range(1, len(LT)):
        if LT[j].split()[0] != LT[j - 1].split()[0]: xx = bx + bw * j / (len(LT) - 1); dd.line((xx, 26, xx, 38), fill=(150, 150, 150))
    xx = bx + bw * i / (len(LT) - 1); dd.rectangle((xx - 2, 24, xx + 2, 40), fill=(255, 120, 60)); return im
def mosaico(nome, fn, ncol, nlin, w, h, n, com_faixa=True):
    dv = os.path.join(O, "video_" + nome); os.makedirs(dv, exist_ok=True); W_, H_ = ncol * (w + 4), nlin * (h + 4) + 44
    for i in range(n):
        o = Image.new("RGB", (W_, H_), (40, 40, 40)); o.paste(faixa(i, W_) if com_faixa else Image.new("RGB", (W_, 44), (10, 10, 12)), (0, 0))
        for r, l in enumerate(fn(i)):
            for c, im in enumerate(l): o.paste(im, (c * (w + 4), 44 + r * (h + 4)))
        o.save(os.path.join(dv, "v_%04d.png" % i))
    open(os.path.join(dv, "res.txt"), "w").write("%d %d" % (W_, H_)); print("VIDEO_QUADROS", nome, n)
mosaico("Sequencia_LOW", lambda i: [[cel(os.path.join(Q, "LOW_%s_t%04d.png" % (v, i)), "LOW %s" % v, 480, 360) for v in ("perfil_D", "perfil_E", "frente", "tras")],
                                    [cel(os.path.join(Q, "LOW_%s_t%04d.png" % (v, i)), "LOW %s" % v, 480, 360) for v in ("34_E", "patas_E", "patas_D")]], 4, 2, 480, 360, len(LT))
mosaico("Sequencia_LODs", lambda i: [[cel(os.path.join(Q, "%s_%s_t%04d.png" % (L, v, i)), "%s %s" % (L, v), 480, 360) for v in ("perfil_D", "patas_D")] for L in ("LOD1", "LOD2")], 2, 2, 480, 360, len(LT))
for ac in TRS:
    n = TJ["acoes"][ac]["quadros"] + 1
    mosaico("Closes_" + ac, lambda q, ac=ac: [[cel(os.path.join(D, "closes", "%s_%s_%s_q%04d.png" % (m, ac, v, q)), "%s %s %s q%d (no lugar)" % (ac, v, m, q), 480, 360)
                                               for v in ("fresta_E", "garganta_E", "flanco_D_baixo")] for m in ("real", "cores")], 3, 2, 480, 360, n, False)
print("PRANCHA_MARCHAS_V28_OK")
