"""Pranchas da v10 (separacao cauda x pata traseira E). Uso: python prancha_cauda_v10.py review/v10_cauda
Sempre REFERENCIA (repouso, nao prova movimento) | v9 | v10, mesma acao e amplitudes:
- diagnostico.png: classe cauda/pata, pesos e pele sem pelo no repouso (v9 x v10) + tampas da v10;
- repouso_<LOD>.png: vistas do corpo inteiro v9 | v10 | diferenca x8 (pixel maximo);
- poses_<LOD>_<modo>_<vista>.png: picos da acao (colunas) v9 / v10 (linhas); modos textura, textura_sempelo, pesos;
- tampas.png: tampas v10 (vermelho cauda, verde pata) em repouso e movimento;
- video_v9_v10/ (quadros lado a lado, montados por video_rig_v9.py)."""
import sys, os, glob, json
from PIL import Image, ImageDraw, ImageChops
D = os.path.abspath(sys.argv[1]); AQ = os.path.dirname(os.path.abspath(__file__))
ref = Image.open(os.path.join(AQ, "ref", "lobo-artico-referencia.png")).convert("RGB"); RC = ref.crop((1040, 280, 1620, 900))
NOME = {0: "repouso", 295: "peso E 0,18", 498: "quadril E frente 18", 512: "quadril E tras 15", 530: "passo traseiro E", 558: "quadril D frente (controle)",
        572: "quadril D tras (controle)", 590: "passo traseiro D (controle)", 621: "cauda E 35", 639: "cauda D 35", 665: "cauda cima 30", 678: "cauda baixo 10",
        825: "comb: cauda E 25 + passo E", 845: "comb: cauda cima 20 + quadril E tras", 871: "comb: cauda D 25 + quadril E frente"}
def rot(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 7 * len(t) + 12, 18), fill=(0, 0, 0)); d.text((6, 3), t, fill=(255, 255, 255)); return im
def abre(p, t, s):
    if not os.path.exists(p): return rot(Image.new("RGB", s, (60, 60, 60)), t + " (sem imagem)")
    return rot(Image.open(p).convert("RGB").resize(s), t)
W, H = 400, 325
def grade(linhas, nome, s=(W, H)):
    cols = max(len(l) for l in linhas); o = Image.new("RGB", (cols * (s[0] + 4), len(linhas) * (s[1] + 4)), (15, 15, 15))
    for r, l in enumerate(linhas):
        for c, im in enumerate(l): o.paste(im, (c * (s[0] + 4), r * (s[1] + 4)))
    o.save(os.path.join(D, nome))
refi = lambda: rot(RC.resize((W, H)), "REFERENCIA (repouso; nao prova movimento)")
# diagnostico
lin = []
for V in ("v9", "v10"):
    l = [refi()]
    for m, v in (("classe", "lado_E_cauda"), ("classe", "interno_E"), ("pesos", "lado_E_cauda"), ("pesos", "interno_E"), ("textura_sempelo", "interno_E")):
        l.append(abre(os.path.join(D, V, "LOW_%s_%s_q0000.png" % (m, v)), "%s %s %s repouso" % (V, m, v), (W, H)))
    lin.append(l)
lin.append([refi()] + [abre(os.path.join(D, "v10", "LOW_tampa_%s_q0000.png" % v), "v10 TAMPAS %s repouso" % v, (W, H)) for v in ("lado_E_cauda", "34_tras_E", "interno_E", "tras_cauda")])
grade(lin, "diagnostico.png")
# repouso corpo inteiro
DIF = {}
for L in ("LOW", "LOD1", "LOD2"):
    lin = []; DIF[L] = {}
    for v in ("frente", "lado_E", "lado_D", "tras", "34_E", "34_D", "34_tras"):
        a = os.path.join(D, "repouso", "v9_%s_%s_q0000.png" % (L, v)); b = os.path.join(D, "repouso", "v10_%s_%s_q0000.png" % (L, v)); l = [rot(ref.resize((W, H)), "REFERENCIA")]
        l += [abre(a, "v9 %s %s" % (L, v), (W, H)), abre(b, "v10 %s %s" % (L, v), (W, H))]
        if os.path.exists(a) and os.path.exists(b):
            df = ImageChops.difference(Image.open(a).convert("RGB"), Image.open(b).convert("RGB")); mx = max(c[1] for c in df.getextrema()); DIF[L][v] = mx
            l.append(rot(df.point(lambda x: min(255, x * 8)).resize((W, H)), "diferenca x8 (pixel max %d/255)" % mx))
        lin.append(l)
    grade(lin, "repouso_%s.png" % L)
json.dump(DIF, open(os.path.join(D, "repouso_diferenca_pixels.json"), "w"), indent=1)
# poses
for L, qs, modos, vistas in (("LOW", sorted(NOME), ("textura", "textura_sempelo"), ("lado_E_cauda", "lado_D_cauda", "tras_cauda", "34_tras_E", "interno_E", "interno_D", "baixo_cauda")),
                             ("LOW", (0, 512, 530, 665, 825), ("pesos",), ("lado_E_cauda", "interno_E", "34_tras_E")),
                             ("LOD1", (0, 512, 530, 665, 825), ("textura", "textura_sempelo"), ("lado_E_cauda", "34_tras_E", "interno_E")),
                             ("LOD2", (0, 512, 530, 665, 825), ("textura", "textura_sempelo"), ("lado_E_cauda", "34_tras_E", "interno_E")),
                             ("LOD1", (0, 530, 665), ("pesos",), ("lado_E_cauda", "interno_E")), ("LOD2", (0, 530, 665), ("pesos",), ("lado_E_cauda", "interno_E"))):
    for m in modos:
        for v in vistas:
            lin = [[refi()] + [abre(os.path.join(D, V, "%s_%s_%s_q%04d.png" % (L, m, v, q)), "%s %s q%d %s" % (V, L.replace("LOW", "LOD0"), q, NOME[q]), (W, H)) for q in qs] for V in ("v9", "v10")]
            grade(lin, "poses_%s_%s_%s.png" % (L, m, v))
grade([[abre(os.path.join(D, "v10", "LOW_tampa_%s_q%04d.png" % (v, q)), "v10 tampas %s q%d %s" % (v, q, NOME[q]), (W, H)) for q in (0, 512, 530, 665, 825)] for v in ("lado_E_cauda", "34_tras_E", "interno_E", "tras_cauda")], "tampas.png")
# video lado a lado
vo = os.path.join(D, "video_v9_v10"); os.makedirs(vo, exist_ok=True); n = 0
TR = json.load(open(os.path.join(AQ, "rig_v10", "acao_v10.json")))["trechos"]
def trecho(q): return next((k for k, (i, f) in TR.items() if i <= q <= f), "")
for p in sorted(glob.glob(os.path.join(D, "video_v10", "LOW_textura_34_tras_E_q*.png"))):
    q = int(p[-8:-4]); a = os.path.join(D, "video_v9", os.path.basename(p))
    if not os.path.exists(a): continue
    o = Image.new("RGB", (1280, 520)); o.paste(rot(Image.open(a).convert("RGB"), "v9 (cauda fundida a coxa E) q%d %s" % (q, trecho(q))), (0, 0))
    o.paste(rot(Image.open(p).convert("RGB"), "v10 (separada) q%d %s" % (q, trecho(q))), (640, 0)); o.save(os.path.join(vo, "v_%04d.png" % q)); n += 1
print("PRANCHAS_CAUDA_V10_OK", DIF, "video", n)
