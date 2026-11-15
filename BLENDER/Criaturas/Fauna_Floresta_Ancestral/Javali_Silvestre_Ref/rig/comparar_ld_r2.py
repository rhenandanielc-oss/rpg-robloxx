"""Antes (lote D r1) x depois (r2) do javali: GIFs empilhados na MESMA escala e velocidade (cameras fixas iguais), grafico de
giro maximo por quadro e de velocidade/distancia por fase, e prancha com a referencia ao lado de quadros-chave.
Uso: python comparar_ld_r2.py <dir_render_antes_depois> <dir_saida> <json_r1> <json_r2> <referencia.png>"""
import sys, os, json, glob, math
from PIL import Image, ImageDraw, ImageFont
import numpy as np
RD, OUT, J1, J2, REF = sys.argv[1:6]; os.makedirs(OUT, exist_ok=True)
F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t)
def med(rot): return json.load(open(os.path.join(RD, rot, "medidas.json")))
def clipe_de(m, q):
    for nome, ini, n in m["segmentos"]:
        if ini <= q < ini + n: return nome, q - ini
    return m["segmentos"][-1][0], q - m["segmentos"][-1][1]
def quadros(rot, vista): return sorted(glob.glob(os.path.join(RD, rot, vista, "q*.png")))
def rotula(im, txt, cor):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, im.width, 22), fill=cor); d.text((6, 3), txt, fill=(255, 255, 255), font=F(14)); return im
# ---------------------------------------------------------------- GIFs empilhados
for cadeia in ("investida", "reacao", "derrota"):
    ma, md = med("antes_" + cadeia), med("depois_" + cadeia)
    for vista in ("lado_fixo", "34_fixo"):
        A, D = quadros("antes_" + cadeia, vista), quadros("depois_" + cadeia, vista)
        if not A or not D: continue
        n = max(len(A), len(D)); fr = []
        for i in range(n):
            a = Image.open(A[min(i, len(A) - 1)]).convert("RGB"); b = Image.open(D[min(i, len(D) - 1)]).convert("RGB")
            na, qa = clipe_de(ma, min(i, len(A) - 1)); nb, qb = clipe_de(md, min(i, len(D) - 1))
            rotula(a, f"ANTES (r1)  {na} q{qa:03d}   t={i / 30:.2f}s" + ("  [fim]" if i >= len(A) else ""), (110, 40, 35))
            rotula(b, f"DEPOIS (r2)  {nb} q{qb:03d}   t={i / 30:.2f}s" + ("  [fim]" if i >= len(D) else ""), (35, 90, 45))
            o = Image.new("RGB", (a.width, a.height * 2 + 4), (30, 30, 30)); o.paste(a, (0, 0)); o.paste(b, (0, a.height + 4))
            fr.append(o.resize((o.width * 2 // 3, o.height * 2 // 3)))
        fr[0].save(os.path.join(OUT, f"antes_depois_{cadeia}_{vista}.gif"), save_all=True, append_images=fr[1:], duration=33, loop=0)
        print("GIF", cadeia, vista, len(fr))
# ---------------------------------------------------------------- graficos
def giros(path):
    d = json.load(open(path)); n = d["quadros"]; mx = np.zeros(n - 1); quem = [""] * (n - 1)
    for b, v in d["ossos"].items():
        Q = np.array(v).reshape(n, 7)[:, :4]
        a = np.degrees(2 * np.arccos(np.clip(np.abs((Q[:-1] * Q[1:]).sum(1)), 0, 1)))
        for i in range(n - 1):
            if a[i] > mx[i]: mx[i] = a[i]; quem[i] = b
    return mx, quem, d
def grafico(titulo, series, ymax, arq, ylab):
    W, H, M = 900, 300, 50; o = Image.new("RGB", (W, H), (250, 250, 248)); d = ImageDraw.Draw(o)
    d.text((M, 6), titulo, fill=(20, 20, 20), font=F(15)); n = max(len(s[1]) for s in series)
    d.line((M, H - 30, W - 10, H - 30), fill=(0, 0, 0)); d.line((M, 30, M, H - 30), fill=(0, 0, 0))
    for y in range(0, int(ymax) + 1, max(1, int(ymax / 5))):
        yy = H - 30 - (H - 60) * y / ymax; d.line((M - 4, yy, W - 10, yy), fill=(225, 225, 225)); d.text((6, yy - 7), str(y), fill=(60, 60, 60), font=F(11))
    for i in range(0, n, 10): d.text((M + (W - M - 10) * i / n - 6, H - 26), f"q{i}", fill=(60, 60, 60), font=F(10))
    d.text((W - 200, H - 14), ylab, fill=(60, 60, 60), font=F(11))
    for k_, (nome, vals, cor) in enumerate(series):
        pts = [(M + (W - M - 10) * i / n, H - 30 - (H - 60) * min(v, ymax) / ymax) for i, v in enumerate(vals)]
        d.line(pts, fill=cor, width=2); d.text((W - 260, 30 + 16 * k_), nome, fill=cor, font=F(13))
    o.save(arq)
REL = {}
for clipe in ("Ameaca", "Investida", "RecuperacaoInvestida", "ReacaoImpacto", "Derrota"):
    g1, w1, d1 = giros(os.path.join(J1, f"Javali_{clipe}.json")); g2, w2, d2 = giros(os.path.join(J2, f"Javali_{clipe}.json"))
    grafico(f"{clipe}: maior giro de osso entre quadros (graus)", [("antes r1 (max %.1f %s q%d)" % (g1.max(), w1[g1.argmax()], g1.argmax()), list(g1), (170, 50, 40)),
            ("depois r2 (max %.1f %s q%d)" % (g2.max(), w2[g2.argmax()], g2.argmax()), list(g2), (40, 120, 60))], 50, os.path.join(OUT, f"giro_{clipe}.png"), "quadro (30 qps)")
    REL[clipe] = {"giro_max_r1": [round(float(g1.max()), 1), w1[g1.argmax()], int(g1.argmax())], "giro_max_r2": [round(float(g2.max()), 1), w2[g2.argmax()], int(g2.argmax())],
                  "giro_por_quadro_r1": [round(float(x), 1) for x in g1], "giro_por_quadro_r2": [round(float(x), 1) for x in g2],
                  "duracao_r1": round(d1["quadros"] / 30, 3), "duracao_r2": round(d2["quadros"] / 30, 3)}
    if d1.get("v_perfil") and max(d1["v_perfil"]) > 0:
        v1, v2 = d1["v_perfil"], d2["v_perfil"]
        grafico(f"{clipe}: velocidade (u/s) gravada", [("antes r1", v1, (170, 50, 40)), ("depois r2", v2, (40, 120, 60))], 3.0, os.path.join(OUT, f"vel_{clipe}.png"), "quadro (30 qps)")
        def fases(v):
            s = np.concatenate([[0], np.cumsum([(v[i] + v[i + 1]) / 2 / 30 for i in range(len(v) - 1)])]); vmax = max(v)
            i_fr = next((i for i, x in enumerate(v) if x < 0.98 * vmax), 0); i_par = next((i for i, x in enumerate(v) if x < 0.02), len(v) - 1)
            return {"ate_comecar_a_frear_u": round(float(s[i_fr]), 3), "q_inicio_freada": i_fr, "freando_u": round(float(s[i_par] - s[i_fr]), 3),
                    "q_parado": i_par, "assentando_u": round(float(s[-1] - s[i_par]), 3), "total_u": round(float(s[-1]), 3),
                    "s_parado": round(i_par / 30, 3), "s_assentando": round((len(v) - 1 - i_par) / 30, 3)}
        REL[clipe]["fases_r1"] = fases(v1); REL[clipe]["fases_r2"] = fases(v2)
json.dump(REL, open(os.path.join(OUT, "comparacao_r1_r2.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for c in REL: print(c, {k: v for k, v in REL[c].items() if not k.startswith("giro_por")})
# ---------------------------------------------------------------- prancha com a referencia
ref = Image.open(REF).convert("RGB"); r34 = ref.crop((0, 0, 1060, 941)); rlado = ref.crop((1020, 0, 1672, 400))
def q_de(rot, nome, ql):
    m = med(rot)
    for n_, ini, n in m["segmentos"]:
        if n_ == nome: return ini + min(ql, n - 1)
def foto(rot, vista, q, txt, cor, h=230):
    im = Image.open(os.path.join(RD, rot, vista, "q%03d.png" % q)).convert("RGB"); im = im.resize((round(im.width * h / im.height), h))
    return rotula(im, txt, cor)
CHAVES = [("investida", "Ameaca", 54, 54, "Ameaca: fim (focinho baixo, peso nos ombros)"),
          ("investida", "Ameaca", 26, 24, "Ameaca: raspada"),
          ("investida", "RecuperacaoInvestida", 18, 12, "Recuperacao: ombros recebem o peso"),
          ("reacao", "ReacaoImpacto", 7, 7, "ReacaoImpacto: empurrao"),
          ("derrota", "Derrota", 58, 57, "Derrota: flanco bate no chao")]
lin = []
for cad, nome, qa, qd, txt in CHAVES:
    a = foto("antes_" + cad, "lado_fixo", q_de("antes_" + cad, nome, qa), f"ANTES r1 · {txt}", (110, 40, 35))
    b = foto("depois_" + cad, "lado_fixo", q_de("depois_" + cad, nome, qd), f"DEPOIS r2 · {txt}", (35, 90, 45))
    rr = rlado.resize((round(rlado.width * 230 / rlado.height), 230)); rotula(rr, "Referência · perfil", (60, 60, 60))
    o = Image.new("RGB", (rr.width + a.width + b.width + 12, 230), (40, 40, 40)); o.paste(rr, (0, 0)); o.paste(a, (rr.width + 6, 0)); o.paste(b, (rr.width + a.width + 12, 0)); lin.append(o)
W = max(l.width for l in lin); P = Image.new("RGB", (W, 40 + sum(l.height + 6 for l in lin)), (40, 40, 40)); d = ImageDraw.Draw(P)
d.text((10, 10), "Javali Silvestre — lote D r1 × r2 (perfil, câmera fixa igual) ao lado da referência", fill=(250, 250, 250), font=F(18)); y = 40
for l in lin: P.paste(l, (0, y)); y += l.height + 6
P.save(os.path.join(OUT, "prancha_referencia_r1_r2.png")); print("PRANCHA", P.size)
