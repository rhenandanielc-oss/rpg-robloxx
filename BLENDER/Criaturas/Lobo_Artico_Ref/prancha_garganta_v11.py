"""Pranchas da v11 (garganta/juba). Uso: python prancha_garganta_v11.py review/v11_garganta
Sempre REFERENCIA (repouso; nao prova movimento) | v10 | v11, mesma acao e cameras:
- repouso_<LOD>.png: vistas gerais v10 | v11 | diferenca x8;
- poses_<LOD>_<modo>_<vista>.png: picos (colunas) v10 / v11 (linhas); modos textura, textura_sempelo, pescoco (pesos+arame);
- video_v10_v11/ (quadros lado a lado; MP4 por video_rig_v9.py)."""
import sys, os, glob, json
from PIL import Image, ImageDraw, ImageChops
D = os.path.abspath(sys.argv[1]); AQ = os.path.dirname(os.path.abspath(__file__))
ref = Image.open(os.path.join(AQ, "ref", "lobo-artico-referencia.png")).convert("RGB"); RC = ref.crop((300, 120, 860, 640))
NOME = {0: "repouso", 99: "cabeca E 35", 119: "cabeca D 35", 149: "cabeca cima 25", 169: "cabeca baixo 18", 782: "comb: cabeca 30 + baixo 15 + boca 32",
        251: "inclina E 8 (axila)", 295: "peso E 0,18 (axila)", 378: "ombro E frente 18 (axila)", 438: "ombro D frente 18 (axila)"}
def rot(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 7 * len(t) + 12, 18), fill=(0, 0, 0)); d.text((6, 3), t, fill=(255, 255, 255)); return im
def abre(p, t, s):
    if not os.path.exists(p): return rot(Image.new("RGB", s, (60, 60, 60)), t + " (sem imagem)")
    return rot(Image.open(p).convert("RGB").resize(s), t)
W, H = 400, 325
def grade(lin, nome):
    o = Image.new("RGB", (max(len(l) for l in lin) * (W + 4), len(lin) * (H + 4)), (15, 15, 15))
    for r, l in enumerate(lin):
        for c, im in enumerate(l): o.paste(im, (c * (W + 4), r * (H + 4)))
    o.save(os.path.join(D, nome))
refi = lambda: rot(RC.resize((W, H)), "REFERENCIA (repouso; nao prova movimento)")
DIF = {}
for L in ("LOW", "LOD1", "LOD2"):
    lin = []; DIF[L] = {}
    for v in ("frente", "lado_E", "lado_D", "34_E", "34_D"):
        a = os.path.join(D, "repouso", "v10_%s_%s_q0000.png" % (L, v)); b = os.path.join(D, "repouso", "v11_%s_%s_q0000.png" % (L, v))
        l = [rot(ref.resize((W, H)), "REFERENCIA"), abre(a, "v10 %s %s" % (L, v), (W, H)), abre(b, "v11 %s %s" % (L, v), (W, H))]
        if os.path.exists(a) and os.path.exists(b):
            df = ImageChops.difference(Image.open(a).convert("RGB"), Image.open(b).convert("RGB")); mx = max(c[1] for c in df.getextrema()); DIF[L][v] = mx
            l.append(rot(df.point(lambda x: min(255, x * 8)).resize((W, H)), "diferenca x8 (pixel max %d/255)" % mx))
        lin.append(l)
    grade(lin, "repouso_%s.png" % L)
json.dump(DIF, open(os.path.join(D, "repouso_diferenca_pixels.json"), "w"), indent=1)
VG = ("garganta_frente", "garganta_E", "garganta_D", "garganta_baixo", "garganta_34", "garganta_34_D", "geral_jogo")
for L, qs, modos, vistas in (("LOW", (0, 99, 119, 149, 169, 782, 251, 295, 378, 438), ("textura", "textura_sempelo"), VG),
                             ("LOW", (0, 169, 782, 378), ("pescoco",), ("garganta_frente", "garganta_E", "garganta_baixo", "garganta_34")),
                             ("LOD1", (0, 99, 169, 782), ("textura",), ("garganta_E", "garganta_34", "garganta_baixo", "geral_jogo")),
                             ("LOD2", (0, 99, 169, 782), ("textura",), ("garganta_E", "garganta_34", "garganta_baixo", "geral_jogo")),
                             ("LOD1", (0, 169, 782), ("textura_sempelo", "pescoco"), ("garganta_E", "garganta_34")),
                             ("LOD2", (0, 169, 782), ("textura_sempelo", "pescoco"), ("garganta_E", "garganta_34"))):
    for m in modos:
        for v in vistas:
            lin = [[refi()] + [abre(os.path.join(D, T, "%s_%s_%s_q%04d.png" % (L, m, v, q)), "%s %s q%d %s" % (T, L.replace("LOW", "LOD0"), q, NOME[q]), (W, H)) for q in qs] for T in ("v10", "v11")]
            grade(lin, "poses_%s_%s_%s.png" % (L, m, v))
vo = os.path.join(D, "video_v10_v11"); os.makedirs(vo, exist_ok=True); n = 0
TR = json.load(open(os.path.join(AQ, "rig_v11", "acao_v10.json")))["trechos"]
def trecho(q): return next((k for k, (i, f) in TR.items() if i <= q <= f), "")
for k, p in enumerate(sorted(glob.glob(os.path.join(D, "video_v11", "LOW_textura_garganta_34_q*.png")))):
    q = int(p[-8:-4]); a = os.path.join(D, "video_v10", os.path.basename(p))
    if not os.path.exists(a): continue
    o = Image.new("RGB", (1280, 520)); o.paste(rot(Image.open(a).convert("RGB"), "v10 q%d %s" % (q, trecho(q))), (0, 0))
    o.paste(rot(Image.open(p).convert("RGB"), "v11 (garganta) q%d %s" % (q, trecho(q))), (640, 0)); o.save(os.path.join(vo, "v_%04d.png" % k)); n += 1
print("PRANCHAS_GARGANTA_V11_OK", DIF, "video", n)
