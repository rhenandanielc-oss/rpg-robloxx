"""Pranchas do rig piloto v9 (system python + PIL). Uso: python prancha_rig_v9.py review/v9_rig
- repouso_<LOD>.png: REFERENCIA | v8 (sem rig) | rig no quadro 0 | diferenca x8 (com o pixel maximo) por vista;
- poses_<LOD>_<vista>.png: cada pico da acao tecnica com os ossos posados desenhados (1a celula = referencia);
- boca_/olhos_/costura_<LOD>.png: closes com referencia; arame_cantos.png;
- reimport_<LOD>.png: rig original x esqueleto REIMPORTADO do GLB (mesmo quadro) e diferenca x8;
- hierarquia.png: ossos com nomes (lado, frente, topo, tras) + arvore;
- video/ossos/: quadros do video com os ossos e o trecho (montados em MP4 por video_rig_v9.py)."""
import sys, os, json, glob
from PIL import Image, ImageDraw, ImageChops
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ossos_desenho_v9 import desenhar
D = os.path.abspath(sys.argv[1]); AQ = os.path.dirname(os.path.abspath(__file__))
ref = Image.open(os.path.join(AQ, "ref", "lobo-artico-referencia.png")).convert("RGB")
CORTE = {"corpo": (300, 20, 1520, 900), "boca": (330, 200, 560, 372), "olhos": (330, 110, 560, 282), "costura": (330, 150, 800, 600)}
def rot(im, t, y=0):
    dr = ImageDraw.Draw(im); dr.rectangle((0, y, 7 * len(t) + 12, y + 18), fill=(0, 0, 0)); dr.text((6, y + 3), t, fill=(255, 255, 255)); return im
def abre(p, t, s):
    if not os.path.exists(p): return rot(Image.new("RGB", s, (60, 60, 60)), t + " (sem imagem)")
    return rot(Image.open(p).convert("RGB").resize(s), t)
def refc(k, s, t="REFERENCIA (so repouso)"): return rot(ref.crop(CORTE[k]).resize(s), t)
OSSOS = {}
for js in glob.glob(os.path.join(D, "*", "ossos_*.json")): OSSOS.update(json.load(open(js)))
def com_ossos(p, nome, s, t, nomes=False):
    if not os.path.exists(p): return abre(p, t, s)
    im = Image.open(p).convert("RGB"); k = os.path.splitext(os.path.basename(p))[0]
    if k in OSSOS: desenhar(im, OSSOS[k], nomes=nomes, larg=2)
    return rot(im.resize(s), t)
TR = json.load(open(os.path.join(AQ, "rig_v9", "acao_v9.json")))["trechos"]
PICO = {0: "repouso", 25: "boca meio (15)", 43: "boca maxima (32)", 64: "piscar meio", 72: "piscar total", 99: "cabeca E 35", 119: "cabeca D 35",
        149: "cabeca cima 25", 169: "cabeca baixo 18", 201: "coluna E 12", 221: "coluna D 12", 251: "inclina E 8", 269: "inclina D 8",
        295: "peso E 0,18", 313: "peso D 0,18", 339: "peso frente 0,2", 355: "peso tras 0,2", 378: "dianteira E: ombro frente 18", 392: "dianteira E: ombro tras 15",
        410: "dianteira E: passo", 438: "dianteira D: ombro frente", 452: "dianteira D: ombro tras", 470: "dianteira D: passo", 498: "traseira E: quadril frente 18",
        512: "traseira E: quadril tras 15", 530: "traseira E: passo", 558: "traseira D: quadril frente", 572: "traseira D: quadril tras", 590: "traseira D: passo",
        621: "cauda E 35", 639: "cauda D 35", 665: "cauda cima 30", 678: "cauda baixo 10", 699: "orelhas tras 35", 712: "orelhas frente 15", 732: "orelha E giro 25",
        750: "orelha D giro 25", 782: "combinacao: cabeca 30 + baixo 15 + boca 32"}
def trecho(q):
    for n, (i, f) in TR.items():
        if i <= q <= f: return n
    return ""
W, H = 400, 300
# 1) repouso v8 x rig
VC = ("frente", "lado_E", "lado_D", "tras", "34_E", "34_D", "34_tras"); VF = ("canto_E", "canto_D", "boca_34", "boca_baixo", "olhos", "olho_E", "olho_D", "costura_E", "costura_D", "costura_baixo")
DIF = {}
for L in ("LOW", "LOD1", "LOD2"):
    vs = VC + VF; o = Image.new("RGB", (4 * (W + 6), len(vs) * (H + 6)), (15, 15, 15)); DIF[L] = {}
    for r, v in enumerate(vs):
        y = r * (H + 6); k = "corpo" if v in VC else ("olhos" if v.startswith("olho") else ("costura" if v.startswith("costura") else "boca"))
        o.paste(refc(k, (W, H)), (0, y))
        a = os.path.join(D, "repouso", "v8_%s_%s_q0000.png" % (L, v)); b = os.path.join(D, "repouso", "rig_%s_%s_q0000.png" % (L, v))
        o.paste(abre(a, "v8 %s %s (sem rig)" % (L, v), (W, H)), (W + 6, y)); o.paste(abre(b, "rig v9 %s %s quadro 0" % (L, v), (W, H)), (2 * (W + 6), y))
        if os.path.exists(a) and os.path.exists(b):
            df = ImageChops.difference(Image.open(a).convert("RGB"), Image.open(b).convert("RGB")); mx = max(c[1] for c in df.getextrema())
            DIF[L][v] = mx; o.paste(rot(df.point(lambda x: min(255, x * 8)).resize((W, H)), "diferenca x8 (pixel max %d/255)" % mx), (3 * (W + 6), y))
    o.save(os.path.join(D, "repouso_%s.png" % L))
json.dump(DIF, open(os.path.join(D, "repouso_diferenca_pixels.json"), "w"), indent=1)
# 2) poses
def grade(arqs, nome, cols=6, s=(400, 300), refk="corpo"):
    n = len(arqs) + 1; lin = (n + cols - 1) // cols; o = Image.new("RGB", (cols * (s[0] + 4), lin * (s[1] + 4)), (15, 15, 15))
    o.paste(refc(refk, s, "REFERENCIA (repouso; nao prova movimento)"), (0, 0))
    for i, (p, t) in enumerate(arqs, 1):
        o.paste(com_ossos(p, None, s, t), ((i % cols) * (s[0] + 4), (i // cols) * (s[1] + 4)))
    o.save(os.path.join(D, nome))
for L, vs in (("LOW", ("34_E", "lado_E", "frente")), ("LOD1", ("34_E",)), ("LOD2", ("34_E",))):
    for v in vs:
        arqs = sorted(glob.glob(os.path.join(D, "poses", "%s_%s_q*.png" % (L, v))))
        grade([(p, "%s q%d %s" % (L.replace("LOW", "LOD0"), int(p[-8:-4]), PICO.get(int(p[-8:-4]), trecho(int(p[-8:-4]))))) for p in arqs], "poses_%s_%s.png" % (L, v))
for v in ("patas", "34_tras"):
    arqs = sorted(glob.glob(os.path.join(D, "poses", "LOW_%s_q*.png" % v)))
    grade([(p, "LOD0 q%d %s" % (int(p[-8:-4]), PICO.get(int(p[-8:-4]), trecho(int(p[-8:-4]))))) for p in arqs], "poses_LOW_%s.png" % v, cols=5)
# 3) closes
for L in ("LOW", "LOD1", "LOD2"):
    for g, qs, vs, k in (("boca", (0, 25, 43, 782), ("canto_E", "canto_D", "boca_34", "boca_baixo"), "boca"), ("olhos", (0, 64, 72), ("olhos", "olho_E", "olho_D"), "olhos"),
                         ("costura", (0, 99, 119, 149, 169, 782), ("costura_E", "costura_D", "costura_baixo"), "costura")):
        o = Image.new("RGB", ((1 + len(vs)) * (W + 6), len(qs) * (H + 6)), (15, 15, 15))
        for r, q in enumerate(qs):
            y = r * (H + 6); o.paste(refc(k, (W, H)), (0, y))
            for c, v in enumerate(vs):
                o.paste(abre(os.path.join(D, "closes", "%s_%s_q%04d.png" % (L, v, q)), "%s %s q%d %s" % (L.replace("LOW", "LOD0"), v, q, PICO.get(q, "")), (W, H)), ((1 + c) * (W + 6), y))
        o.save(os.path.join(D, "%s_%s.png" % (g, L)))
o = Image.new("RGB", (3 * (W + 6), 2 * (H + 6)), (15, 15, 15))
for c, q in enumerate((0, 43, 782)):
    for r, v in enumerate(("canto_E", "canto_D")):
        o.paste(abre(os.path.join(D, "closes", "arame_LOW_%s_q%04d.png" % (v, q)), "LOD0 arame %s q%d %s" % (v, q, PICO[q]), (W, H)), (c * (W + 6), r * (H + 6)))
o.save(os.path.join(D, "arame_cantos.png"))
# 4) reimportado x original
QR = (0, 43, 72, 99, 169, 201, 295, 410, 530, 621, 699, 782); RD = {}
for L in ("LOW", "LOD1", "LOD2"):
    o = Image.new("RGB", (3 * (W + 6), len(QR) * (H + 6)), (15, 15, 15)); RD[L] = {}
    for r, q in enumerate(QR):
        a = os.path.join(D, "poses", "%s_34_E_q%04d.png" % (L, q)); b = os.path.join(D, "reimport", "reimp_%s_34_E_q%04d.png" % (L, q)); y = r * (H + 6)
        o.paste(com_ossos(a, None, (W, H), "rig original %s q%d %s" % (L.replace("LOW", "LOD0"), q, PICO.get(q, ""))), (0, y))
        o.paste(com_ossos(b, None, (W, H), "GLB reimportado %s q%d (esqueleto importado)" % (L.replace("LOW", "LOD0"), q)), (W + 6, y))
        if os.path.exists(a) and os.path.exists(b):
            df = ImageChops.difference(Image.open(a).convert("RGB"), Image.open(b).convert("RGB")); mx = max(c[1] for c in df.getextrema()); RD[L][q] = mx
            o.paste(rot(df.point(lambda x: min(255, x * 8)).resize((W, H)), "diferenca x8 (pixel max %d/255; materiais do GLB)" % mx), (2 * (W + 6), y))
    o.save(os.path.join(D, "reimport_%s.png" % L))
json.dump(RD, open(os.path.join(D, "reimport_diferenca_pixels.json"), "w"), indent=1)
# 5) hierarquia
rig = json.load(open(os.path.join(AQ, "rig_v9", "rig_v9.json")))["ossos"]; filhos = {}
for b in rig: filhos.setdefault(b["pai"], []).append(b["nome"])
linhas = []
def arv(n, k):
    linhas.append("  " * k + n)
    for f in filhos.get(n, []): arv(f, k + 1)
for raiz in filhos[None]: arv(raiz, 0)
txt = Image.new("RGB", (420, 14 * len(linhas) + 30), (250, 250, 250)); dr = ImageDraw.Draw(txt); dr.text((8, 6), "Hierarquia (37 ossos; X local = lateral)", fill=(0, 0, 0))
for i, l in enumerate(linhas): dr.text((8, 24 + 14 * i), l, fill=(0, 0, 0))
hs = [Image.open(p).convert("RGB") for p in sorted(glob.glob(os.path.join(D, "hierarquia", "ossos", "*.png")))]
o = Image.new("RGB", (2 * 700 + txt.width, max(2 * 500, txt.height)), (15, 15, 15))
for i, im in enumerate(hs[:4]): o.paste(im.resize((700, 500)), ((i % 2) * 700, (i // 2) * 500))
o.paste(txt, (1400, 0)); o.save(os.path.join(D, "hierarquia.png"))
# 6) quadros do video com ossos e trecho
vd = os.path.join(D, "video"); os.makedirs(os.path.join(vd, "ossos"), exist_ok=True)
for p in sorted(glob.glob(os.path.join(vd, "LOW_34_E_q*.png"))):
    q = int(p[-8:-4]); im = Image.open(p).convert("RGB"); k = os.path.splitext(os.path.basename(p))[0]
    if k in OSSOS: desenhar(im, OSSOS[k], nomes=False, larg=2)
    rot(im, "rig real LOD0 - quadro %d/806 - %s" % (q, trecho(q))).save(os.path.join(vd, "ossos", "v_%04d.png" % q))
print("PRANCHAS_RIG_V9_OK", DIF, RD)
