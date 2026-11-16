"""v27: pranchas e mosaicos de video da correcao das pernas na virada. Saida review/v27_pernas/revisao/:
- 01_lateral.png: por virada, entrada lateral do MCP de cada pata em relacao ao repouso (+ = para DENTRO, referencial do corpo) e
  distancia minima entre as pernas do mesmo par (frente DE x DD, tras TE x TD), v26 (fino) x v27 (grosso);
- 02_antes_depois.png: v26 x v27, vistas fixas frente/tras nos quadros em que a v26 tinha a pior entrada de cada pata (VirarEsquerda);
- 03_apoios.png: deslize e afundamento por pata e LOD (auditoria mundial com rotacao, ida e volta), v27;
- video_Comparativo_v26_v27 (frente/tras/topo, ida_volta_E), video_IdaVolta_{E,D}_LOW (8 vistas), video_IdaVolta_E_LODs.
Uso: python prancha_pernas_v27.py (nesta pasta)"""
import os, json
from PIL import Image, ImageDraw
D = "review/v27_pernas"; O = os.path.join(D, "revisao"); os.makedirs(O, exist_ok=True); Q = os.path.join(D, "quadros"); Q6 = os.path.join(D, "quadros_v26")
VJ = json.load(open("anim_v27/viradas_v27.json")); AV = json.load(open(os.path.join(D, "aud_viradas_v27.json")))
P6 = json.load(open(os.path.join(D, "diag_pernas_v26_LOW.json"))); P7 = json.load(open(os.path.join(D, "diag_pernas_v27_LOW.json")))
PAT = ("DE", "DD", "TE", "TD"); COR = {"DE": (60, 110, 255), "DD": (240, 50, 40), "TE": (40, 200, 70), "TD": (240, 200, 20)}


def cel(p, txt, w, h):
    im = Image.new("RGB", (w, h), (24, 24, 28))
    if p and os.path.exists(p):
        s = Image.open(p).convert("RGB"); s.thumbnail((w, h)); im.paste(s, ((w - s.width) // 2, (h - s.height) // 2))
    elif p:
        ImageDraw.Draw(im).text((8, h // 2), "falta " + os.path.basename(p), fill=(255, 80, 80))
    dd = ImageDraw.Draw(im); dd.rectangle((0, 0, w, 16), fill=(0, 0, 0)); dd.text((4, 2), txt, fill=(255, 235, 120)); return im


def linha(d, x0, y0, w, h, ys, ymin, ymax, cor, larg):
    n = max(1, len(ys) - 1); d.line([(x0 + w * i / n, y0 + h - h * (y - ymin) / (ymax - ymin)) for i, y in enumerate(ys)], fill=cor, width=larg)


def eixo(d, x0, y0, w, h, ymin, ymax, marcas, rot):
    d.rectangle((x0, y0, x0 + w, y0 + h), outline=(90, 90, 100)); d.text((x0 + 4, y0 + 2), rot, fill=(230, 230, 230))
    for m, c in marcas:
        z = y0 + h - h * (m - ymin) / (ymax - ymin); d.line((x0, z, x0 + w, z), fill=c); d.text((x0 + w - 44, z - 12), "%.2f" % m, fill=c)


img = Image.new("RGB", (1820, 1000), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "v27: pernas na virada. Entrada lateral do MCP (+ = para DENTRO, stud) e distancia entre pernas do par. Fino = v26, grosso = v27. Limite de projeto: 0,10 no apoio", fill=(255, 235, 120))
for c, ac in enumerate(("VirarEsquerda", "VirarDireita")):
    x0 = 20 + c * 900
    eixo(d, x0, 30, 860, 300, -0.8, 0.7, [(0, (120, 120, 130)), (0.1, (255, 140, 60))], "%s: entrada lateral do MCP por pata (+ = dentro)" % ac)
    for k in PAT:
        sg = 1 if k[1] == "E" else -1
        for PJ, lg in ((P6, 1), (P7, 3)):
            r0 = PJ["repouso"]["mcp_x"][k]; linha(d, x0, 30, 860, 300, [sg * (r0 - f["mcp_x"][k]) for f in PJ["acoes"][ac]["por_quadro"]], -0.8, 0.7, COR[k], lg)
    for i, k in enumerate(PAT):
        d.text((x0 + 10 + i * 210, 336), "%s: v26 %.3f -> v27 %.3f" % (k, P6["acoes"][ac]["mcp_dentro_max_" + k], P7["acoes"][ac]["mcp_dentro_max_" + k]), fill=COR[k])
    for j, (ch, nm) in enumerate((("dist_baixo_DEDD", "frente DE x DD"), ("dist_baixo_TETD", "tras TE x TD"))):
        y0 = 370 + j * 300; r0 = P7["repouso"][ch]; an = P7["acoes"]["Andar"][ch + "_min"]
        eixo(d, x0, y0, 860, 260, 0, 1.0, [(r0, (120, 200, 120)), (an, (120, 120, 200))], "distancia minima entre partes baixas, %s (verde = repouso %.2f, azul = Andar min %.2f)" % (nm, r0, an))
        linha(d, x0, y0, 860, 260, [f[ch] for f in P6["acoes"][ac]["por_quadro"]], 0, 1.0, (230, 120, 120), 1)
        linha(d, x0, y0, 860, 260, [f[ch] for f in P7["acoes"][ac]["por_quadro"]], 0, 1.0, (255, 255, 255), 3)
        d.text((x0 + 10, y0 + 266), "min: v26 %.3f (vermelho)  ->  v27 %.3f (branco)" % (P6["acoes"][ac][ch + "_min"], P7["acoes"][ac][ch + "_min"]), fill=(230, 230, 230))
img.save(os.path.join(O, "01_lateral.png")); print("PRANCHA 01")

w, h = 440, 330; lin = []
for k in PAT:
    q = P6["acoes"]["VirarEsquerda"]["mcp_dentro_q_" + k]; t = 10 + q
    lin.append([cel(os.path.join(Q6, "LOW_ida_volta_E_%s_t%04d.png" % (v, t)), "v26 %s VirarEsquerda q%d (pior %s)" % (v, q, k), w, h) for v in ("frente", "tras")] +
               [cel(os.path.join(Q, "LOW_ida_volta_E_%s_t%04d.png" % (v, t)), "v27 %s VirarEsquerda q%d" % (v, q), w, h) for v in ("frente", "tras")])
o = Image.new("RGB", (4 * (w + 4), 4 * (h + 4)), (40, 40, 40))
for r, l in enumerate(lin):
    for c, im in enumerate(l): o.paste(im, (c * (w + 4), r * (h + 4)))
o.save(os.path.join(O, "02_antes_depois.png")); print("PRANCHA 02")

img = Image.new("RGB", (1200, 420), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "v27: deslize maximo por pata (stud) nas fases que tocam as viradas, ida e volta E e D, auditoria mundial com rotacao (limite 0,03)", fill=(255, 235, 120))
for i, L in enumerate(("LOW", "LOD1", "LOD2")):
    for j, k in enumerate(PAT):
        fs = [f for sq in AV["niveis"][L].values() for f in sq["apoios"][k] if any(x.startswith("Virar") for x in f["acoes"])]
        ds = max(f["deslize"] for f in fs); af = max(f["afundamento"] for f in fs); x0 = 20 + i * 390; y0 = 50 + j * 85
        d.text((x0, y0), "%s %s  deslize %.4f  afund %.4f" % (L, k, ds, af), fill=COR[k]); d.rectangle((x0, y0 + 18, x0 + 360, y0 + 40), outline=(90, 90, 90))
        d.rectangle((x0, y0 + 18, x0 + 360 * min(1, ds / 0.03), y0 + 40), fill=COR[k] if ds <= 0.03 else (255, 0, 0))
img.save(os.path.join(O, "03_apoios.png")); print("PRANCHA 03")


def faixa(lt, ps, i, wtot):
    im = Image.new("RGB", (wtot, 44), (10, 10, 12)); dd = ImageDraw.Draw(im); ac_, q = lt[i].split(" "); q = int(q[1:])
    no = [k for k in PAT if ac_ == "Repouso" or VJ["acoes"][ac_]["apoio_por_quadro"][k][q]]
    dd.text((8, 4), "t%03d  %s  |  rumo (mundo) = %7.2f graus  |  no chao (v27): %s" % (i, lt[i], ps[i], " ".join(no)), fill=(255, 235, 120))
    bx, bw = 8, wtot - 16; dd.rectangle((bx, 26, bx + bw, 38), outline=(80, 80, 80)); xx = bx + bw * i / (len(lt) - 1); dd.rectangle((xx - 2, 24, xx + 2, 40), fill=(255, 120, 60)); return im


def mosaico(nome, fn, ncol, nlin, w, h, lt, ps):
    dv = os.path.join(O, "video_" + nome); os.makedirs(dv, exist_ok=True); W_, H_ = ncol * (w + 4), nlin * (h + 4) + 44
    for i in range(len(lt)):
        o = Image.new("RGB", (W_, H_), (40, 40, 40)); o.paste(faixa(lt, ps, i, W_), (0, 0))
        for r, l in enumerate(fn(i)):
            for c, im in enumerate(l): o.paste(im, (c * (w + 4), 44 + r * (h + 4)))
        o.save(os.path.join(dv, "v_%04d.png" % i))
    open(os.path.join(dv, "res.txt"), "w").write("%d %d" % (W_, H_)); print("VIDEO_QUADROS", nome, len(lt))


for sq in ("ida_volta_E", "ida_volta_D"):
    J = json.load(open(os.path.join(Q, "linha_LOW_%s.json" % sq))); lt, ps = J["linha_do_tempo"], J["psi_mundo_graus"]
    mosaico("IdaVolta_%s_LOW" % sq[-1], lambda i, sq=sq: [[cel(os.path.join(Q, "LOW_%s_%s_t%04d.png" % (sq, v, i)), "v27 LOW %s (camera fixa)" % v, 480, 360) for v in ("topo", "34", "perfil_E", "perfil_D")],
                                                         [cel(os.path.join(Q, "LOW_%s_%s_t%04d.png" % (sq, v, i)), "v27 LOW %s (camera fixa)" % v, 480, 360) for v in ("frente", "tras", "patas_E", "patas_D")]], 4, 2, 480, 360, lt, ps)
    if sq == "ida_volta_E":
        mosaico("Comparativo_v26_v27", lambda i: [[cel(os.path.join(QQ, "LOW_ida_volta_E_%s_t%04d.png" % (v, i)), "%s %s" % (nm, v), 480, 360) for v in ("frente", "tras", "topo")]
                                                  for QQ, nm in ((Q6, "v26 (antes)"), (Q, "v27 (corrigida)"))], 3, 2, 480, 360, lt, ps)
J = json.load(open(os.path.join(Q, "linha_LOD1_ida_volta_E.json"))); lt, ps = J["linha_do_tempo"], J["psi_mundo_graus"]
mosaico("IdaVolta_E_LODs", lambda i: [[cel(os.path.join(Q, "%s_ida_volta_E_%s_t%04d.png" % (L, v, i)), "v27 %s %s" % (L, v), 400, 300) for v in ("topo", "frente", "patas_D")] for L in ("LOD1", "LOD2")], 3, 2, 400, 300, lt, ps)
print("PRANCHA_PERNAS_V27_OK")
