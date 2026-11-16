"""v29: pranchas e mosaicos de video da revisao das desaceleracoes (TroteParaAndar, CorridaParaTrote). Saida review/v29_desacel/revisao/:
- 00_referencia_resultado.png: referencia (repouso) ao lado da v29 em quatro vistas, meio de cada acao;
- 01_curvas.png: por acao, v28 (fino) x v29 (grosso): velocidade, peso s, apoios por pata, quadro de saida;
- 02_apoios.png: deslize/afundamento por pata e LOD nas fases que tocam as transicoes (sequencia completa v29, metodo v24);
- 03_pernas.png: CorridaParaTrote, angulo do joelho/jarrete e extensao da perna por quadro, TE (corrigida) e TD (controle), v28 x v29,
  com as faixas da Corrida e do Trote aprovados;
- video_Comparativo_CorridaParaTrote / video_Comparativo_TroteParaAndar: linhas v28 / v29, mesmas cameras (perfil D, traseiras E e D),
  faixa com acao, quadro, velocidade, patas no chao e marcador (janela com marchas estaveis antes e depois);
- video_Comparativo_CorridaParaTrote_LODs (traseiras E, LOD1/LOD2, v28 x v29); video_Sequencia_LOW (8 vistas), video_Sequencia_LODs;
- video_Closes_<acao> (real e cores).
Uso: python prancha_marchas_v29.py (nesta pasta)"""
import os, json
from PIL import Image, ImageDraw
D = "review/v29_desacel"; O = os.path.join(D, "revisao"); os.makedirs(O, exist_ok=True); Q = os.path.join(D, "quadros")
T9 = json.load(open("anim_v29/marchas_v29.json")); T8 = json.load(open("anim_v28/marchas_v28.json")); AU = json.load(open(os.path.join(D, "aud_marchas_v29.json")))
G8 = json.load(open(os.path.join(D, "diag_v28.json"))); G9 = json.load(open(os.path.join(D, "diag_v29.json")))
PAT = ("DE", "DD", "TE", "TD"); COR = {"DE": (60, 110, 255), "DD": (240, 50, 40), "TE": (40, 200, 70), "TD": (240, 200, 20)}
TRS = ("AndarParaTrote", "TroteParaAndar", "TroteParaCorrida", "CorridaParaTrote"); MUD = ("TroteParaAndar", "CorridaParaTrote")
JAN = {"CorridaParaTrote": (287, 380), "TroteParaAndar": (381, 534)}
REF = "../../../REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png"


def cel(p, txt, w, h):
    im = Image.new("RGB", (w, h), (24, 24, 28))
    if p and os.path.exists(p):
        s = Image.open(p).convert("RGB"); s.thumbnail((w, h)); im.paste(s, ((w - s.width) // 2, (h - s.height) // 2))
    elif p:
        ImageDraw.Draw(im).text((8, h // 2), "falta " + os.path.basename(p), fill=(255, 80, 80))
    dd = ImageDraw.Draw(im); dd.rectangle((0, 0, w, 16), fill=(0, 0, 0)); dd.text((4, 2), txt, fill=(255, 235, 120)); return im


def graf(d, x0, y0, w, h, ys, ymin, ymax, cor, rot, larg=2, n=None):
    if rot: d.rectangle((x0, y0, x0 + w, y0 + h), outline=(90, 90, 100)); d.text((x0 + 4, y0 + 2), rot, fill=(230, 230, 230))
    n = n or max(1, len(ys) - 1)
    d.line([(x0 + w * i / n, y0 + h - h * (max(ymin, min(ymax, y)) - ymin) / (ymax - ymin)) for i, y in enumerate(ys)], fill=cor, width=larg)


# 00 referencia x resultado
LT9 = json.load(open(os.path.join(Q, "linha_LOW.json")))["linha_do_tempo"]
w, h = 440, 330; lin = [[cel(REF, "referencia (repouso; nao comprova biomecanica)", w, h)] + [Image.new("RGB", (w, h), (24, 24, 28))] * 3]
for ac in MUD:
    i = next(j for j, e in enumerate(LT9) if e.startswith(ac + " ")); n = T9["acoes"][ac]["quadros"]; t = i + n // 2
    lin.append([cel(os.path.join(Q, "LOW_%s_t%04d.png" % (v, t)), "v29 %s %s q%d" % (ac, v, n // 2), w, h) for v in ("perfil_D", "34_E", "frente", "tras")])
o = Image.new("RGB", (4 * (w + 4), 3 * (h + 4)), (40, 40, 40))
for r, l in enumerate(lin):
    for c, im in enumerate(l): o.paste(im, (c * (w + 4), r * (h + 4)))
o.save(os.path.join(O, "00_referencia_resultado.png")); print("PRANCHA 00")

# 01 curvas v28 x v29
img = Image.new("RGB", (1820, 700), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "v28 (fino/cinza) x v29 (grosso/cor): velocidade (stud/s, parametro tecnico), peso s e apoios por pata. Eixo = quadros da acao (mesma escala nas duas)", fill=(255, 235, 120))
for c, ac in enumerate(MUD):
    A8, A9 = T8["acoes"][ac], T9["acoes"][ac]; x0 = 20 + c * 900; n = max(A8["quadros"], A9["quadros"]); vmax = max(A8["v_por_quadro"]) * 1.1
    graf(d, x0, 30, 860, 150, A8["v_por_quadro"], 0, vmax, (150, 150, 150), "%s: v28 %d q (%.2f s, %.1f stud) -> v29 %d q (%.2f s, %.1f stud); saida v28 %s / v29 %s" % (
        ac, A8["quadros"], A8["quadros"] / 30, A8["distancia_total"], A9["quadros"], A9["quadros"] / 30, A9["distancia_total"], A8["saida"].split(" (")[0], A9["saida"].split(" (")[0]), 1, n)
    graf(d, x0, 30, 860, 150, A9["v_por_quadro"], 0, vmax, (255, 140, 60), None, 3, n)
    graf(d, x0, 190, 860, 80, A8["s_por_quadro"], -0.05, 1.05, (150, 150, 150), "peso s (rampa %.1f s)" % A9["rampa_s"], 1, n)
    graf(d, x0, 190, 860, 80, A9["s_por_quadro"], -0.05, 1.05, (120, 200, 255), None, 3, n)
    cvi = A9.get("convergencia") or {}; cv = cvi.get("quadro_convergencia_exata"); cvv = cvi.get("quadro_convergencia_visual")
    for i, k in enumerate(PAT):
        for vv, A, cc in ((0, A8, (120, 120, 120)), (1, A9, COR[k])):
            yb = 290 + i * 60 + vv * 24; d.text((x0, yb + 4), "%s %s" % (k, "v29" if vv else "v28"), fill=cc)
            for q in range(A["quadros"] + 1):
                if A["apoio_por_quadro"][k][q]: d.rectangle((x0 + 70 + 790 * q / n, yb, x0 + 70 + 790 * (q + 1) / n, yb + 18), fill=cc)
    mk = [(A9["quadros"], "fim v29", 0), (A8["quadros"], "fim v28", 0)] + ([(cvv, "<1e-3 stud", 1), (cv, "exato", 2)] if cv else [])
    for q_, rot, lv in mk:
        xx = x0 + 70 + 790 * q_ / n; d.line((xx, 285, xx, 530), fill=(255, 255, 255)); d.text((xx - 30, 535 + 12 * lv), rot, fill=(255, 255, 255))
    ik8, ik9 = A8["erro_ik_max"], A9["erro_ik_max"]; cts = {k: len(v) for k, v in A9.get("apoios_cortados_v29", {}).items() if v}
    d.text((x0, 570), "erro IK max v28 %.3f -> v29 %.4f | por pata v29 (apoio/balanco) %s" % (ik8, ik9, {k: (v["apoio"], v["balanco"]) for k, v in A9["erro_ik_por_pata"].items()}), fill=(220, 220, 220))
    d.text((x0, 590), "apoios cortados no comprimento natural (v29): %s" % (cts or "nenhum"), fill=(220, 220, 220))
    if cv: d.text((x0, 610), "pose = Andar: <1e-3 stud no q%d, exata (<=2e-6) no q%d; saida no 1o Andar q0 depois = q%d (v28: q%d)" % (cvv, cv, cvi["quadro_saida_q0"], cvi["quadros_v28"]), fill=(220, 220, 220))
img.save(os.path.join(O, "01_curvas.png")); print("PRANCHA 01")

# 02 apoios
img = Image.new("RGB", (1200, 430), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "v29: deslize maximo por pata (stud) nas fases que tocam as transicoes (sequencia completa Andar-Trote-Corrida-Trote-Andar; limite 0,03)", fill=(255, 235, 120))
for i, L in enumerate(("LOW", "LOD1", "LOD2")):
    for j, k in enumerate(PAT):
        fs = [f for f in AU["niveis"][L]["apoios"][k] if any(x in TRS for x in f["acoes"])]
        ds = max(f["deslize"] for f in fs); af = max(f["afundamento"] for f in fs); fl = max(f["flutuacao"] for f in fs); x0 = 20 + i * 390; y0 = 50 + j * 88
        d.text((x0, y0), "%s %s  desl %.4f  afund %.4f  flut %.4f" % (L, k, ds, af, fl), fill=COR[k]); d.rectangle((x0, y0 + 18, x0 + 360, y0 + 40), outline=(90, 90, 90))
        d.rectangle((x0, y0 + 18, x0 + 360 * min(1, ds / 0.03), y0 + 40), fill=COR[k] if ds <= 0.03 else (255, 0, 0))
img.save(os.path.join(O, "02_apoios.png")); print("PRANCHA 02")

# 03 pernas (CorridaParaTrote)
img = Image.new("RGB", (1820, 760), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "CorridaParaTrote: joelho/jarrete (graus, 0 = perna reta TRAVADA) e extensao d/(a+b) por quadro. Fino = v28, grosso = v29. Faixas: minimo do joelho na Corrida (laranja) e no Trote (azul)", fill=(255, 235, 120))
for c, k in enumerate(("TE", "TD")):
    x0 = 20 + c * 900; p8 = G8["acoes"]["CorridaParaTrote"]["por_quadro"]; p9 = G9["acoes"]["CorridaParaTrote"]["por_quadro"]
    jc, jt = G9["controle"]["Corrida"]["joelho_min"][k], G9["controle"]["Trote"]["joelho_min"][k]
    d.rectangle((x0, 30, x0 + 860, 330), outline=(90, 90, 100)); d.text((x0 + 4, 32), "%s joelho/jarrete (graus) %s; min v28 %.1f -> v29 %.1f (Corrida %.1f, Trote %.1f)" % (
        k, "CORRIGIDA" if k == "TE" else "CONTROLE", G8["acoes"]["CorridaParaTrote"]["joelho_min"][k], G9["acoes"]["CorridaParaTrote"]["joelho_min"][k], jc, jt), fill=(230, 230, 230))
    for m, cc in ((jc, (255, 140, 60)), (jt, (120, 160, 255))):
        z = 330 - 300 * m / 120; d.line((x0, z, x0 + 860, z), fill=cc)
    graf(d, x0, 30, 860, 300, [p["patas"][k]["joelho"] for p in p8], 0, 120, (230, 120, 120), None, 1)
    graf(d, x0, 30, 860, 300, [p["patas"][k]["joelho"] for p in p9], 0, 120, COR[k], None, 3)
    d.rectangle((x0, 360, x0 + 860, 660), outline=(90, 90, 100)); d.text((x0 + 4, 362), "%s extensao d/(a+b); max v28 %.4f -> v29 %.4f (Corrida %.3f; 0,9995 = limite do IK)" % (
        k, G8["acoes"]["CorridaParaTrote"]["ext_max"][k], G9["acoes"]["CorridaParaTrote"]["ext_max"][k], G9["controle"]["Corrida"]["ext_max"][k]), fill=(230, 230, 230))
    graf(d, x0, 360, 860, 300, [p["patas"][k]["ext"] for p in p8], 0.5, 1.01, (230, 120, 120), None, 1)
    graf(d, x0, 360, 860, 300, [p["patas"][k]["ext"] for p in p9], 0.5, 1.01, COR[k], None, 3)
    for q in range(len(p9)):
        if p9[q]["patas"][k]["apoio"]: d.rectangle((x0 + 860 * q / (len(p9) - 1), 670, x0 + 860 * (q + 1) / (len(p9) - 1), 684), fill=COR[k])
        if p8[q]["patas"][k]["apoio"]: d.rectangle((x0 + 860 * q / (len(p8) - 1), 690, x0 + 860 * (q + 1) / (len(p8) - 1), 704), fill=(130, 130, 130))
    d.text((x0, 712), "apoios: cor = v29, cinza = v28 (quadros 0..62)", fill=(200, 200, 200))
img.save(os.path.join(O, "03_pernas.png")); print("PRANCHA 03")


def linha_info(base):
    J = json.load(open(os.path.join(Q, "linha_LOW%s.json" % ("" if base == "v29" else "_" + base)))); return J["linha_do_tempo"], J["X"]
INF = {"v29": linha_info("v29") + (T9,), "v28": linha_info("v28") + (T8,)}
def v_de(X, i):
    j0, j1 = max(0, i - 1), min(len(X) - 1, i + 1); return -(X[j1] - X[j0]) * 30 / max(1, j1 - j0)
def no_chao(TJ, ent):
    ac_, q = ent.split(" "); q = int(q[1:])
    if ac_ in TJ["acoes"]: return [k for k in PAT if TJ["acoes"][ac_]["apoio_por_quadro"][k][q]]
    return None
def faixa_txt(base, i, wtot, a=None, b=None, h=30):
    LT, X, TJ = INF[base]; im = Image.new("RGB", (wtot, h), (10, 10, 12)); dd = ImageDraw.Draw(im); nc = no_chao(TJ, LT[i])
    dd.text((8, 2), "%s  t%03d  %s  |  v = %6.2f stud/s  |  %s" % (base, i, LT[i], v_de(X, i), ("no chao: " + " ".join(nc)) if nc is not None else "marcha ciclica"), fill=(255, 235, 120))
    a = 0 if a is None else a; b = len(LT) - 1 if b is None else b; bx, bw = 8, wtot - 16; dd.rectangle((bx, 18, bx + bw, 27), outline=(80, 80, 80))
    for j in range(a + 1, b + 1):
        if LT[j].split()[0] != LT[j - 1].split()[0]: xx = bx + bw * (j - a) / (b - a); dd.line((xx, 18, xx, 27), fill=(150, 150, 150))
    xx = bx + bw * (i - a) / (b - a); dd.rectangle((xx - 2, 16, xx + 2, 29), fill=(255, 120, 60)); return im
def mosaico(nome, n, fn, ncol, nlin, w, h, faixas):
    dv = os.path.join(O, "video_" + nome); os.makedirs(dv, exist_ok=True); fh = 30 * len(faixas(0)) if faixas else 0; W_, H_ = ncol * (w + 4), nlin * (h + 4) + fh
    for i in range(n):
        o = Image.new("RGB", (W_, H_), (40, 40, 40))
        for r, f in enumerate(faixas(i) if faixas else []): o.paste(f(W_), (0, 30 * r))
        for r, l in enumerate(fn(i)):
            for c, im in enumerate(l): o.paste(im, (c * (w + 4), fh + r * (h + 4)))
        o.save(os.path.join(dv, "v_%04d.png" % i))
    open(os.path.join(dv, "res.txt"), "w").write("%d %d" % (W_, H_)); print("VIDEO_QUADROS", nome, n)
def qd(base, L, v, i): return os.path.join(Q, "%s%s_%s_t%04d.png" % ("" if base == "v29" else base + "_", L, v, i))
for ac, (a, b) in JAN.items():
    mosaico("Comparativo_" + ac, b - a + 1, lambda j, a=a: [[cel(qd(bs, "LOW", v, a + j), "%s LOW %s" % (bs, v), 480, 360) for v in ("perfil_D", "traseiras_E", "traseiras_D")] for bs in ("v28", "v29")],
            3, 2, 480, 360, lambda j, a=a, b=b: [lambda W_, j=j: faixa_txt("v28", a + j, W_, a, b), lambda W_, j=j: faixa_txt("v29", a + j, W_, a, b)])
a, b = JAN["CorridaParaTrote"]
mosaico("Comparativo_CorridaParaTrote_LODs", b - a + 1, lambda j: [[cel(qd(bs, L, "traseiras_E", a + j), "%s %s traseiras_E" % (bs, L), 480, 360) for L in ("LOD1", "LOD2")] for bs in ("v28", "v29")],
        2, 2, 480, 360, lambda j: [lambda W_, j=j: faixa_txt("v28", a + j, W_, a, b), lambda W_, j=j: faixa_txt("v29", a + j, W_, a, b)])
n9 = len(INF["v29"][0])
mosaico("Sequencia_LOW", n9, lambda i: [[cel(qd("v29", "LOW", v, i), "v29 LOW %s" % v, 480, 360) for v in ("perfil_D", "perfil_E", "frente", "tras")],
                                         [cel(qd("v29", "LOW", v, i), "v29 LOW %s" % v, 480, 360) for v in ("34_E", "patas_E", "traseiras_E", "traseiras_D")]], 4, 2, 480, 360,
        lambda i: [lambda W_, i=i: faixa_txt("v29", i, W_)])
mosaico("Sequencia_LODs", n9, lambda i: [[cel(qd("v29", L, v, i), "v29 %s %s" % (L, v), 480, 360) for v in ("perfil_D", "traseiras_E")] for L in ("LOD1", "LOD2")], 2, 2, 480, 360,
        lambda i: [lambda W_, i=i: faixa_txt("v29", i, W_)])
for ac in MUD:
    n = T9["acoes"][ac]["quadros"] + 1
    mosaico("Closes_" + ac, n, lambda q, ac=ac: [[cel(os.path.join(D, "closes", "%s_%s_%s_q%04d.png" % (m, ac, v, q)), "v29 %s %s %s q%d (no lugar)" % (ac, v, m, q), 480, 360)
                                                 for v in ("fresta_E", "garganta_E", "flanco_D_baixo")] for m in ("real", "cores")], 3, 2, 480, 360, None)
print("PRANCHA_MARCHAS_V29_OK")
