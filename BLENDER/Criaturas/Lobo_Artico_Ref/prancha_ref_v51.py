"""v51: prancha de comparacao com as referencias. Linha 1: lobo real (Wikimedia Commons, "Close opnamen wolf", Enting Films /
Sound and Vision, CC BY-SA 3.0 NL) 0:23,5-0:27,5, parado -> vira ~90 graus e sai andando, 2 q/s. Linhas 2 e 3: v50 e v51 (tres-quartos)
nos mesmos instantes a partir do inicio da partida. Linha 4: imagem de referencia do lobo artico (postura/anatomia) + v51 de perfil
parado e no meio da virada. Uso: python prancha_ref_v51.py <dir_quadros> <dir_review_v51>"""
import sys, os, glob
from PIL import Image, ImageDraw
Q, R = sys.argv[1], sys.argv[2]
BASE = os.path.dirname(os.path.abspath(__file__)); REF = os.path.join(BASE, "..", "..", "..", "REFERENCIAS", "tundra-congelada", "lobo-artico", "lobo-artico-referencia.png")
W, H = 300, 190
def q(pre, vista, t):                                     # t = s desde o inicio da partida; sequencia: 15 q de Repouso, render 1 q sim 1 nao
    i = int(round((15 + 30 * t) / 2)); return os.path.join(Q, vista, "%s_LOW_partida_curva_E_%s_t%04d.png" % (pre, vista, i))
def cel(p, rot):
    im = Image.open(p).convert("RGB"); im.thumbnail((W, H)); c = Image.new("RGB", (W, H), (30, 30, 30)); c.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    ImageDraw.Draw(c).text((4, H - 14), rot, fill=(255, 230, 120)); return c
reais = sorted(glob.glob(os.path.join(R, "ref", "real_a_*.jpg")))
ts = [0.5 * i for i in range(len(reais))]
linhas = [("LOBO REAL 0:23,5-0:27,5 (Commons, CC BY-SA 3.0 NL)", [cel(p, "real +%.1f s" % t) for p, t in zip(reais, ts)]),
          ("v50 tres-quartos (mesmos instantes desde a partida)", [cel(q("ANTES", "c34", t), "v50 +%.1f s" % t) for t in ts]),
          ("v51 tres-quartos", [cel(q("V46B", "c34", t), "v51 +%.1f s" % t) for t in ts]),
          ("REFERENCIA (postura) x v51 de perfil: parado, +0,6 s, +1,2 s, +2,0 s", [cel(REF, "referencia")] + [cel(q("V46B", "perfil_E", t), "v51 perfil +%.1f s" % t) for t in (0.0, 0.6, 1.2, 2.0)])]
TOP = 22; out = Image.new("RGB", (W * len(ts), len(linhas) * (H + TOP)), (12, 12, 12)); dr = ImageDraw.Draw(out)
for r, (tit, cs) in enumerate(linhas):
    y = r * (H + TOP); dr.text((6, y + 5), tit, fill=(255, 255, 255))
    for c_, im in enumerate(cs): out.paste(im, (c_ * W, y + TOP))
o = os.path.join(R, "prancha_ref_v51.jpg"); out.save(o, quality=88); print("PRANCHA", o, out.size)
