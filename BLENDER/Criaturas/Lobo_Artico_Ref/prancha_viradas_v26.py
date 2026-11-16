"""v26: pranchas e mosaicos de video das viradas. Saida review/v26_viradas/revisao/:
- 01_rumo.png: por virada, rumo psi(t) (graus), velocidade angular (graus/s), translacao externa T(t) (stud) e faixas de APOIO por pata;
  mapa de PEGADAS visto de cima (posicao mundial de cada apoio com a orientacao da pata) e a seta de rumo inicial/final;
- 02_apoios.png: deslize maximo por pata e LOD nas fases que tocam as viradas (auditoria MUNDIAL com rotacao, ida e volta) e afundamento;
- 03_repouso.png: referencia | Repouso v25 | Repouso v26 | ultimo quadro VirarEsquerda | ultimo quadro VirarDireita (poses locais);
- video_IdaVolta_E_LOW, video_IdaVolta_D_LOW (8 vistas fixas no mundo, incl. topo), video_IdaVolta_E_LODs, video_Closes_VirarEsquerda/Direita.
Uso: python prancha_viradas_v26.py (nesta pasta)"""
import os, json, math
from PIL import Image, ImageDraw
D = "review/v26_viradas"; O = os.path.join(D, "revisao"); os.makedirs(O, exist_ok=True)
REF = "../../../REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png"
VJ = json.load(open("anim_v26/viradas_v26.json")); AV = json.load(open(os.path.join(D, "aud_viradas_v26.json")))
PAT = ("DE", "DD", "TE", "TD"); COR = {"DE": (60, 110, 255), "DD": (240, 50, 40), "TE": (40, 200, 70), "TD": (240, 200, 20)}
def sobe(x): return math.ceil(x * 10000 - 1e-9) / 10000
def graf(d, x0, y0, w, h, ys, ymin, ymax, cor, rot):
    d.rectangle((x0, y0, x0 + w, y0 + h), outline=(90, 90, 100)); d.text((x0 + 4, y0 + 2), rot, fill=(230, 230, 230)); n = len(ys) - 1
    z = y0 + h - h * (0 - ymin) / (ymax - ymin); d.line((x0, z, x0 + w, z), fill=(70, 70, 80))
    d.line([(x0 + w * i / n, y0 + h - h * (y - ymin) / (ymax - ymin)) for i, y in enumerate(ys)], fill=cor, width=2)
img = Image.new("RGB", (1820, 1060), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "Viradas v26 (parametros tecnicos): rumo externo psi em torno de +Z (anti-horario visto de cima; frente -Y; esquerda do lobo +X), T = translacao externa (pivo fixo), apoios e pegadas", fill=(255, 235, 120))
for c, ac in enumerate(("VirarEsquerda", "VirarDireita")):
    A = VJ["acoes"][ac]; x0 = 20 + c * 900; n = A["quadros"]
    graf(d, x0, 30, 860, 150, A["psi_graus_por_quadro"], -95, 95, (255, 140, 60), "%s: psi (graus), %d quadros = %.2f s, final %.1f" % (ac, n, n / 30, A["angulo_final_graus"]))
    graf(d, x0, 190, 860, 120, A["omega_graus_s_por_quadro"], -60, 60, (120, 200, 255), "velocidade angular (graus/s)")
    graf(d, x0, 320, 860, 110, [t[0] for t in A["T_por_quadro"]], -1, 1, (200, 120, 255), "T.x (roxo) e T.y (verde), stud")
    yy = [t[1] for t in A["T_por_quadro"]]; d.line([(x0 + 860 * i / n, 320 + 110 - 110 * (y + 1) / 2) for i, y in enumerate(yy)], fill=(120, 230, 120), width=2)
    for i, k in enumerate(PAT):
        yb = 440 + i * 26; d.text((x0, yb + 5), k, fill=COR[k])
        for q in range(n + 1):
            if A["apoio_por_quadro"][k][q]: d.rectangle((x0 + 30 + 830 * q / n, yb, x0 + 30 + 830 * (q + 1) / n, yb + 20), fill=COR[k])
    # pegadas (vista de cima): x -> direita, y -> para cima na imagem (camera topo)
    cx, cy, esc = x0 + 430, 820, 45
    d.rectangle((x0, 560, x0 + 860, 1050), outline=(90, 90, 100)); d.text((x0 + 4, 562), "pegadas no mundo (vista de cima, grade 1 stud); numero = ordem do apoio; traço = orientacao da pata", fill=(230, 230, 230))
    for g in range(-9, 10):
        d.line((cx + g * esc, 575, cx + g * esc, 1045), fill=(45, 45, 52)); d.line((x0 + 5, cy + g * esc, x0 + 855, cy + g * esc), fill=(45, 45, 52))
    for k in PAT:
        for j, (wx, wy, hd) in enumerate(A["plantas_mundo"][k]):
            px, py = cx + wx * esc, cy - wy * esc; r = 7; d.ellipse((px - r, py - r, px + r, py + r), outline=COR[k], width=2); d.text((px + 8, py - 6), str(j), fill=COR[k])
            hr = math.radians(hd); fx, fy = math.sin(hr), -math.cos(hr); d.line((px, py, px + fx * 22, py - fy * 22), fill=COR[k], width=2)
    pv = VJ["pivo"]; px, py = cx + pv[0] * esc, cy - pv[1] * esc; d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=(255, 255, 255)); d.text((px + 6, py + 4), "pivo", fill=(255, 255, 255))
    for ang, cor_ in ((0, (180, 180, 180)), (A["angulo_final_graus"], (255, 140, 60))):
        hr = math.radians(ang); d.line((px, py, px + math.sin(hr) * 150, py + math.cos(hr) * 150), fill=cor_, width=3)
    d.text((x0 + 8, 1030), "seta cinza = frente inicial; laranja = frente final", fill=(200, 200, 200))
img.save(os.path.join(O, "01_rumo.png")); print("PRANCHA 01")
img = Image.new("RGB", (1500, 470), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "Deslize maximo (stud) nas fases de apoio que tocam as viradas - auditoria MUNDIAL com rotacao, sequencias ida e volta E e D; linha = 0,03", fill=(255, 235, 120))
for c, L in enumerate(("LOW", "LOD1", "LOD2")):
    x0 = 10 + c * 495; d.rectangle((x0, 30, x0 + 485, 460), outline=(90, 90, 100)); d.text((x0 + 6, 34), L, fill=(255, 255, 255)); base = 420; esc = 330 / 0.04
    d.line((x0 + 5, base - 0.03 * esc, x0 + 480, base - 0.03 * esc), fill=(255, 120, 120))
    for i, k in enumerate(PAT):
        fs = [f for sq in AV["niveis"][L].values() for f in sq["apoios"][k] if any(a.startswith("Virar") for a in f["acoes"])]
        m = max(f["deslize"] for f in fs); af = max(f["afundamento"] for f in fs); bx = x0 + 30 + i * 115
        d.rectangle((bx, base - m * esc, bx + 60, base), fill=COR[k]); d.text((bx, base + 6), "%s %.4f" % (k, sobe(m)), fill=(230, 230, 230)); d.text((bx, base + 20), "afund %.4f" % af, fill=(180, 180, 180))
img.save(os.path.join(O, "02_apoios.png")); print("PRANCHA 02")
def cel(p, txt, w, h):
    im = Image.new("RGB", (w, h), (24, 24, 28))
    if p and os.path.exists(p): s = Image.open(p).convert("RGB"); s.thumbnail((w, h)); im.paste(s, ((w - s.width) // 2, (h - s.height) // 2))
    elif p: ImageDraw.Draw(im).text((8, h // 2), "falta " + os.path.basename(p), fill=(255, 80, 80))
    dd = ImageDraw.Draw(im); dd.rectangle((0, 0, w, 16), fill=(0, 0, 0)); dd.text((4, 2), txt, fill=(255, 235, 120)); return im
VS = ("c_perfil_D", "c_perfil_E", "c_34_D", "c_tras"); w, h = 400, 300
lin = [[cel(REF, "REFERENCIA (repouso)", w, h)] + [cel(None, "", w, h)] * 3,
       [cel("%s/repouso/v25/real_LOW_repouso_%s_q0000.png" % (D, v), "Repouso v25 %s" % v, w, h) for v in VS],
       [cel("%s/repouso/v26/real_LOW_repouso_%s_q0000.png" % (D, v), "Repouso v26 %s" % v, w, h) for v in VS],
       [cel("%s/repouso/v26_fim/real_LOW_VE_fim_%s_q0092.png" % (D, v), "VirarEsquerda ultimo quadro (local) %s" % v, w, h) for v in VS],
       [cel("%s/repouso/v26_fim/real_LOW_VD_fim_%s_q0092.png" % (D, v), "VirarDireita ultimo quadro (local) %s" % v, w, h) for v in VS]]
o = Image.new("RGB", (4 * (w + 4), 5 * (h + 4)), (40, 40, 40))
for r, l in enumerate(lin):
    for c, im in enumerate(l): o.paste(im, (c * (w + 4), r * (h + 4)))
o.save(os.path.join(O, "03_repouso.png")); print("PRANCHA 03")
Q = os.path.join(D, "quadros")
def faixa(lt, ps, i, wtot):
    im = Image.new("RGB", (wtot, 44), (10, 10, 12)); dd = ImageDraw.Draw(im); ac_, q = lt[i].split(" "); q = int(q[1:])
    no = [k for k in PAT if ac_ == "Repouso" or VJ["acoes"][ac_]["apoio_por_quadro"][k][q]]
    dd.text((8, 4), "t%03d  %s  |  rumo (mundo) = %7.2f graus  |  no chao: %s" % (i, lt[i], ps[i], " ".join(no)), fill=(255, 235, 120))
    bx, bw = 8, wtot - 16; dd.rectangle((bx, 26, bx + bw, 38), outline=(80, 80, 80))
    for j in range(1, len(lt)):
        if lt[j].split()[0] != lt[j - 1].split()[0]: xx = bx + bw * j / (len(lt) - 1); dd.line((xx, 26, xx, 38), fill=(150, 150, 150))
    xx = bx + bw * i / (len(lt) - 1); dd.rectangle((xx - 2, 24, xx + 2, 40), fill=(255, 120, 60)); return im
def mosaico(nome, fn, ncol, nlin, w, h, n, lt=None, ps=None):
    dv = os.path.join(O, "video_" + nome); os.makedirs(dv, exist_ok=True); W_, H_ = ncol * (w + 4), nlin * (h + 4) + 44
    for i in range(n):
        o = Image.new("RGB", (W_, H_), (40, 40, 40)); o.paste(faixa(lt, ps, i, W_) if lt else Image.new("RGB", (W_, 44), (10, 10, 12)), (0, 0))
        for r, l in enumerate(fn(i)):
            for c, im in enumerate(l): o.paste(im, (c * (w + 4), 44 + r * (h + 4)))
        o.save(os.path.join(dv, "v_%04d.png" % i))
    open(os.path.join(dv, "res.txt"), "w").write("%d %d" % (W_, H_)); print("VIDEO_QUADROS", nome, n)
for sq in ("ida_volta_E", "ida_volta_D"):
    J = json.load(open(os.path.join(Q, "linha_LOW_%s.json" % sq))); lt, ps = J["linha_do_tempo"], J["psi_mundo_graus"]
    mosaico("IdaVolta_%s_LOW" % sq[-1], lambda i, sq=sq: [[cel(os.path.join(Q, "LOW_%s_%s_t%04d.png" % (sq, v, i)), "LOW %s (camera fixa)" % v, 480, 360) for v in ("topo", "34", "perfil_E", "perfil_D")],
                                                         [cel(os.path.join(Q, "LOW_%s_%s_t%04d.png" % (sq, v, i)), "LOW %s (camera fixa)" % v, 480, 360) for v in ("frente", "tras", "patas_E", "patas_D")]], 4, 2, 480, 360, len(lt), lt, ps)
J = json.load(open(os.path.join(Q, "linha_LOD1_ida_volta_E.json"))); lt, ps = J["linha_do_tempo"], J["psi_mundo_graus"]
mosaico("IdaVolta_E_LODs", lambda i: [[cel(os.path.join(Q, "%s_ida_volta_E_%s_t%04d.png" % (L, v, i)), "%s %s" % (L, v), 400, 300) for v in ("topo", "perfil_D", "patas_D")] for L in ("LOD1", "LOD2")], 3, 2, 400, 300, len(lt), lt, ps)
for ac in ("VirarEsquerda", "VirarDireita"):
    n = VJ["acoes"][ac]["quadros"] + 1
    mosaico("Closes_" + ac, lambda q, ac=ac: [[cel(os.path.join(D, "closes", "%s_%s_%s_q%04d.png" % (m, ac, v, q)), "%s %s %s q%d (no lugar)" % (ac, v, m, q), 480, 360) for v in ("fresta_E", "garganta_E", "flanco_D_baixo")] for m in ("real", "cores")], 3, 2, 480, 360, n)
print("PRANCHA_VIRADAS_V26_OK")
