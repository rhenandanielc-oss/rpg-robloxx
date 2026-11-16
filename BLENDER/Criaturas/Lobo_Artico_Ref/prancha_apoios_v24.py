"""v24: pranchas e mosaicos de video da correcao dos apoios (v23 x v24, mesmas cameras). Saida review/v24_apoios/revisao/:
- 01_deslize_barras.png: deslize maximo por acao x LOD x pata, v23 x v24, linha da tolerancia 0,03 (valores com 4 casas, sem
  arredondar para baixo: o valor impresso e truncado para cima na 4a casa);
- 02_trajetorias.png: deslocamento horizontal do pior ponto de cada fase de apoio ao longo da fase (stud x quadro; quadros < 0 =
  ciclo anterior, apoio que cruza a emenda), v23 tracejado x v24 cheio;
- video_<acao>_LOW/ e video_<acao>_LODs/: mosaicos v23 | v24 (vistas de vistas_apoios_v24.py) para MP4.
Uso: python prancha_apoios_v24.py (nesta pasta)"""
import os, json, math
from PIL import Image, ImageDraw
D = "review/v24_apoios"; O = os.path.join(D, "revisao"); os.makedirs(O, exist_ok=True)
REF = "../../../REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png"
D23 = json.load(open(os.path.join(D, "diag_apoios_v23.json"))); D24 = json.load(open(os.path.join(D, "diag_apoios_v24.json")))
ACS = ("Andar", "Trote", "Corrida"); LODS = ("LOW", "LOD1", "LOD2"); PAT = ("DE", "DD", "TE", "TD")
COR = {"DE": (60, 110, 255), "DD": (240, 50, 40), "TE": (40, 200, 70), "TD": (240, 200, 20)}
def sobe(x): return math.ceil(x * 10000 - 1e-9) / 10000
# 1. barras
W, H = 520, 300; img = Image.new("RGB", (3 * W, 3 * H + 40), (28, 28, 32)); d = ImageDraw.Draw(img)
d.text((8, 8), "Deslize maximo por fase de apoio (stud), v23 (claro) x v24 (forte); linha = 0,03; metodo do auditar_clipes_v21 (cronograma, emenda = 1 fase)", fill=(255, 235, 120))
for r, ac in enumerate(ACS):
    for c, L in enumerate(LODS):
        x0, y0 = c * W, 40 + r * H; d.rectangle((x0 + 4, y0 + 4, x0 + W - 4, y0 + H - 4), outline=(80, 80, 90)); d.text((x0 + 10, y0 + 8), "%s %s" % (ac, L), fill=(255, 255, 255))
        esc = (H - 70) / 0.05; base = y0 + H - 30; lim = base - 0.03 * esc
        d.line((x0 + 10, lim, x0 + W - 10, lim), fill=(255, 120, 120)); d.text((x0 + W - 60, lim - 14), "0,03", fill=(255, 120, 120))
        for i, k in enumerate(PAT):
            a = max(f["deslize"] for f in D23["niveis"][L][ac]["patas"][k]); b = max(f["deslize"] for f in D24["niveis"][L][ac]["patas"][k])
            bx = x0 + 30 + i * 120; cl = COR[k]; fraco = tuple(int(0.45 * x + 0.55 * 60) for x in cl)
            d.rectangle((bx, base - min(a, 0.05) * esc, bx + 40, base), fill=fraco); d.rectangle((bx + 44, base - min(b, 0.05) * esc, bx + 84, base), fill=cl)
            d.text((bx, base + 4), "%s %.4f>%.4f" % (k, sobe(a), sobe(b)), fill=(230, 230, 230) if b <= 0.03 else (255, 90, 90))
img.save(os.path.join(O, "01_deslize_barras.png")); print("PRANCHA 01")
# 2. trajetorias do pior ponto (pior fase de cada pata)
img = Image.new("RGB", (3 * W, 3 * H + 40), (28, 28, 32)); d = ImageDraw.Draw(img)
d.text((8, 8), "Deslocamento horizontal do pior ponto na pior fase de apoio x quadro (stud); v23 tracejado, v24 cheio; linha = 0,03", fill=(255, 235, 120))
for r, ac in enumerate(ACS):
    for c, L in enumerate(LODS):
        x0, y0 = c * W, 40 + r * H; d.rectangle((x0 + 4, y0 + 4, x0 + W - 4, y0 + H - 4), outline=(80, 80, 90)); d.text((x0 + 10, y0 + 8), "%s %s" % (ac, L), fill=(255, 255, 255))
        fs_all = [f for DD in (D23, D24) for k in PAT for f in DD["niveis"][L][ac]["patas"][k]]; qmin = min(f["inicio"] for f in fs_all); qmax = max(f["fim"] for f in fs_all)
        ex = (W - 50) / max(1, qmax - qmin); ey = (H - 60) / 0.045; base = y0 + H - 25
        d.line((x0 + 30, base - 0.03 * ey, x0 + W - 15, base - 0.03 * ey), fill=(255, 120, 120))
        for DD, tr in ((D23, True), (D24, False)):
            for k in PAT:
                f = max(DD["niveis"][L][ac]["patas"][k], key=lambda f: f["deslize"]); t = f["trajetoria_pior_ponto"]; qm = t[len(t) // 2]
                pts = [(x0 + 30 + (q - qmin) * ex, base - min(0.045, math.hypot(x - qm[1], y - qm[2])) * ey) for q, x, y, h in t if h < 0.06]
                for j in range(len(pts) - 1):
                    if tr and j % 2: continue
                    d.line((pts[j], pts[j + 1]), fill=COR[k], width=1 if tr else 3)
        d.text((x0 + 30, base + 4), "q %d .. %d" % (qmin, qmax), fill=(200, 200, 200))
img.save(os.path.join(O, "02_trajetorias.png")); print("PRANCHA 02")
# 3. mosaicos de video
def cel(p, txt, w, h):
    im = Image.new("RGB", (w, h), (24, 24, 28))
    if p and os.path.exists(p): s = Image.open(p).convert("RGB"); s.thumbnail((w, h)); im.paste(s, ((w - s.width) // 2, (h - s.height) // 2))
    dd = ImageDraw.Draw(im); dd.rectangle((0, 0, w, 16), fill=(0, 0, 0)); dd.text((4, 2), txt, fill=(255, 235, 120)); return im
NQ = {"Andar": 2 * 36, "Trote": 3 * 18, "Corrida": 3 * 14}; Q = os.path.join(D, "quadros")
for ac, nq in NQ.items():
    dv = os.path.join(O, "video_%s_LOW" % ac); os.makedirs(dv, exist_ok=True); w, h = 480, 360
    LIN = [("perfil_D", "perfil_E"), ("frente", "tras"), ("34_E", "patas_E"), ("patas_D", None)]
    for q in range(nq + 1):
        o = Image.new("RGB", (4 * (w + 4), 4 * (h + 4)), (40, 40, 40))
        for r, par in enumerate(LIN):
            for j, vi in enumerate(par):
                for c, v in enumerate(("v23", "v24")):
                    im = cel(os.path.join(Q, v, "LOW_%s_%s_q%04d.png" % (ac, vi, q)), "%s %s %s q%d" % ({"v23": "v23 (antes)", "v24": "v24 (apoios)"}[v], ac, vi, q), w, h) if vi else \
                         (cel(REF, "REFERENCIA (repouso; nao prova contato)", w, h) if c == 0 else cel(None, "DE azul, DD vermelho, TE verde, TD amarelo; grade 0,5/1 stud", w, h))
                    o.paste(im, ((2 * j + c) * (w + 4), r * (h + 4)))
        o.save(os.path.join(dv, "v_%04d.png" % q))
    open(os.path.join(dv, "res.txt"), "w").write("%d %d" % (4 * (w + 4), 4 * (h + 4)))
    dv = os.path.join(O, "video_%s_LODs" % ac); os.makedirs(dv, exist_ok=True); w, h = 400, 300
    for q in range(nq + 1):
        o = Image.new("RGB", (6 * (w + 4), 2 * (h + 4)), (40, 40, 40))
        for r, L in enumerate(("LOD1", "LOD2")):
            for j, vi in enumerate(("perfil_D", "patas_E", "patas_D")):
                for c, v in enumerate(("v23", "v24")):
                    o.paste(cel(os.path.join(Q, v, "%s_%s_%s_q%04d.png" % (L, ac, vi, q)), "%s %s %s %s q%d" % (L, v, ac, vi, q), w, h), ((2 * j + c) * (w + 4), r * (h + 4)))
        o.save(os.path.join(dv, "v_%04d.png" % q))
    open(os.path.join(dv, "res.txt"), "w").write("%d %d" % (6 * (w + 4), 2 * (h + 4)))
    print("VIDEO_QUADROS", ac)
print("PRANCHA_APOIOS_V24_OK")
