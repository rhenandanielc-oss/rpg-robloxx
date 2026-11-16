"""Pranchas da correcao do pelo da cauda preso na perna E (v14). Uso: python prancha_pelo_cauda_v14.py review/v14_pelo_cauda
- pelo_cauda_andar.png: REFERENCIA | antes (v13) | depois (v14), Andar LOW, vistas cauda_E / tras / 34_tras, quadros com a
  traseira E no fim do apoio e no balanco (0, 12, 24, 30);
- pelo_cauda_lod1.png, repouso_v13_x_v14.png (diferenca x8);
- video_pelo_cauda/v_NNNN.png: mosaico antes|depois do ciclo (video_rig_v9.py)."""
import sys, os
from PIL import Image, ImageDraw, ImageChops
D = os.path.abspath(sys.argv[1]); AQ = os.path.dirname(os.path.abspath(__file__)); W, H = 640, 480
ref = Image.open(os.path.join(AQ, "ref", "lobo-artico-referencia.png")).convert("RGB").resize((W, H))
def rot(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 7 * len(t) + 12, 18), fill=(0, 0, 0)); d.text((6, 3), t, fill=(255, 255, 255)); return im
def abre(v, n, t): return rot(Image.open(os.path.join(D, v, n)).convert("RGB").resize((W, H)), t)
def grade(L, s):
    o = Image.new("RGB", (max(len(l) for l in L) * (W + 4), len(L) * (H + 4)), (15, 15, 15))
    for r, l in enumerate(L):
        for c, im in enumerate(l): o.paste(im, (c * (W + 4), r * (H + 4)))
    o.save(os.path.join(D, s))
grade([[rot(ref.copy(), "REFERENCIA (repouso)"), abre("v13", "LOW_Andar_desloc_%s_q%04d.png" % (v, q), "ANTES v13 Andar q%d %s" % (q, v)), abre("v14", "LOW_Andar_desloc_%s_q%04d.png" % (v, q), "DEPOIS v14 Andar q%d %s" % (q, v))]
       for v in ("cauda_E", "tras", "34_tras") for q in (12, 24, 30)], "pelo_cauda_andar.png")
grade([[abre("v13", "LOD1_Andar_desloc_%s_q%04d.png" % (v, q), "ANTES v13 LOD1 q%d %s" % (q, v)), abre("v14", "LOD1_Andar_desloc_%s_q%04d.png" % (v, q), "DEPOIS v14 LOD1 q%d %s" % (q, v))]
       for v in ("cauda_E", "tras") for q in (20, 30)], "pelo_cauda_lod1.png")
L = []; DIF = {}
for v in ("perfil_E", "tras", "cauda_E"):
    n = "LOW_Repouso_%s_q0000.png" % v; a, b = (Image.open(os.path.join(D, x, n)).convert("RGB") for x in ("v13", "v14"))
    df = ImageChops.difference(a, b); DIF[v] = max(c[1] for c in df.getextrema())
    L.append([rot(ref.copy(), "REFERENCIA"), abre("v13", n, "ANTES v13 Repouso %s" % v), abre("v14", n, "DEPOIS v14 Repouso %s" % v), rot(df.point(lambda x: min(255, x * 8)).resize((W, H)), "diferenca x8 (max %d/255)" % DIF[v])])
grade(L, "repouso_v13_x_v14.png")
vd = os.path.join(D, "video_pelo_cauda"); os.makedirs(vd, exist_ok=True)
for q in range(36):
    o = Image.new("RGB", (2 * W, 2 * H), (15, 15, 15))
    for r, v in enumerate(("cauda_E", "34_tras")):
        for c, x in enumerate(("v13", "v14")): o.paste(abre(x, "LOW_Andar_desloc_%s_q%04d.png" % (v, q), "%s %s %s q%d" % ("ANTES" if x == "v13" else "DEPOIS", x, v, q)), (c * W, r * H))
    o.save(os.path.join(vd, "v_%04d.png" % q))
print("PRANCHAS_PELO_V14_OK", DIF)
