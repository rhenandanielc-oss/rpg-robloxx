"""Pranchas da correcao das manchas (v13). Uso: python prancha_manchas_v13.py review/v13_manchas
- manchas_andar.png: REFERENCIA | v12 (antes) | v13 (depois), close cauda/pata E no Andar, com e sem pelo, quadros 0/3/30;
- manchas_lods.png: LOD1 e LOD2 antes/depois;
- repouso_v12_x_v13.png: silhueta do Repouso q0 antes/depois + diferenca x8;
- video_manchas/v_NNNN.png: mosaico antes|depois do ciclo para MP4 (video_rig_v9.py)."""
import sys, os
from PIL import Image, ImageDraw, ImageChops
D = os.path.abspath(sys.argv[1]); AQ = os.path.dirname(os.path.abspath(__file__)); W, H = 640, 480
ref = Image.open(os.path.join(AQ, "ref", "lobo-artico-referencia.png")).convert("RGB").resize((W, H))
def rot(im, t):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, 7 * len(t) + 12, 18), fill=(0, 0, 0)); d.text((6, 3), t, fill=(255, 255, 255)); return im
def abre(v, nome, t): return rot(Image.open(os.path.join(D, v, nome)).convert("RGB").resize((W, H)), t)
def grade(linhas, saida):
    o = Image.new("RGB", (max(len(l) for l in linhas) * (W + 4), len(linhas) * (H + 4)), (15, 15, 15))
    for r, l in enumerate(linhas):
        for c, im in enumerate(l): o.paste(im, (c * (W + 4), r * (H + 4)))
    o.save(os.path.join(D, saida))
L = []
for q in (0, 3, 30):
    for pre, t in (("LOW_Andar_desloc_cauda_E", "com pelo"), ("LOW_Andar_desloc_sempelo_cauda_E", "sem pelo")):
        n = "%s_q%04d.png" % (pre, q)
        L.append([rot(ref.copy(), "REFERENCIA (repouso)"), abre("v12", n, "ANTES v12 Andar q%d %s" % (q, t)), abre("v13", n, "DEPOIS v13 Andar q%d %s" % (q, t))])
grade(L, "manchas_andar.png")
grade([[abre("v12", "%s_Andar_desloc_cauda_E_q%04d.png" % (lo, q), "ANTES v12 %s q%d" % (lo, q)), abre("v13", "%s_Andar_desloc_cauda_E_q%04d.png" % (lo, q), "DEPOIS v13 %s q%d" % (lo, q))]
       for lo in ("LOD1", "LOD2") for q in (0, 30)], "manchas_lods.png")
L = []; DIF = {}
for v in ("perfil_E", "perfil_D", "tras", "34_E", "cauda_E"):
    n = "LOW_Repouso_%s_q0000.png" % v; a = Image.open(os.path.join(D, "v12", n)).convert("RGB"); b = Image.open(os.path.join(D, "v13", n)).convert("RGB")
    df = ImageChops.difference(a, b); DIF[v] = max(c[1] for c in df.getextrema())
    L.append([rot(ref.copy(), "REFERENCIA"), abre("v12", n, "ANTES v12 Repouso %s" % v), abre("v13", n, "DEPOIS v13 Repouso %s" % v), rot(df.point(lambda x: min(255, x * 8)).resize((W, H)), "diferenca x8 (max %d/255)" % DIF[v])])
grade(L, "repouso_v12_x_v13.png")
vd = os.path.join(D, "video_manchas"); os.makedirs(vd, exist_ok=True)
for q in range(36):
    o = Image.new("RGB", (2 * W, 2 * H), (15, 15, 15))
    for r, pre in enumerate(("LOW_Andar_desloc_cauda_E", "LOW_Andar_desloc_sempelo_cauda_E")):
        for c, v in enumerate(("v12", "v13")):
            o.paste(abre(v, "%s_q%04d.png" % (pre, q), "%s %s q%d" % ("ANTES" if v == "v12" else "DEPOIS", v + (" sem pelo" if r else ""), q)), (c * W, r * H))
    o.save(os.path.join(vd, "v_%04d.png" % q))
print("PRANCHAS_MANCHAS_V13_OK", DIF)
