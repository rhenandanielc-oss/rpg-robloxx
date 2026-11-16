"""Quadros dos videos de revisao do pelo da cauda (v14): ANTES (v13) | DEPOIS (v14) lado a lado, 960x720 cada, rotulos
grandes. Um video por vista e modo (cores / real), 3 ciclos do Andar (108 quadros), e uma prancha de 4 quadros por modo.
Uso: python video_pelo_cauda_v14.py review/v14_pelo_cauda/revisao [antes depois] (padrao v13 v14; depois: video_rig_v9.py em cada pasta video_*)"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
D = os.path.abspath(sys.argv[1]); W, H = 960, 720; A_, B_ = (sys.argv[2], sys.argv[3]) if len(sys.argv) > 3 else ("v13", "v14")
try: F = ImageFont.truetype("arial.ttf", 34); F2 = ImageFont.truetype("arial.ttf", 22)
except OSError: F = F2 = ImageFont.load_default()
LEG = {"cores": "laranja = osso da CAUDA   azul = PERNA traseira E   (laranja nao pode ir junto com o azul)", "real": "render normal (EEVEE), camera parada, clipe no lugar"}
def celula(v, modo, vista, q):
    im = Image.open(os.path.join(D, v, "%s_%s_q%04d.png" % (modo, vista, q))).convert("RGB"); d = ImageDraw.Draw(im)
    t = ("ANTES (%s)" % v if v == A_ else "DEPOIS (%s)" % v) + "   quadro %d" % q
    d.rectangle((0, 0, W, 50), fill=(0, 0, 0) if v == A_ else (0, 70, 20)); d.text((14, 7), t, font=F, fill=(255, 255, 255))
    return im
def quadro(modo, vista, q):
    o = Image.new("RGB", (2 * W + 8, H + 40), (40, 40, 40))
    o.paste(celula(A_, modo, vista, q), (0, 0)); o.paste(celula(B_, modo, vista, q), (W + 8, 0))
    ImageDraw.Draw(o).text((14, H + 8), "Andar - %s - %s" % (vista, LEG[modo]), font=F2, fill=(230, 230, 230)); return o
n = 0
for modo in ("cores", "real"):
    for vista in ("fresta_E", "fresta_tras", "fresta_baixo"):
        vd = os.path.join(D, "video_%s_%s_%s" % (B_, modo, vista)); os.makedirs(vd, exist_ok=True)
        for i in range(108): quadro(modo, vista, i % 36).save(os.path.join(vd, "v_%04d.png" % i)); n += 1
    pr = [quadro(modo, "fresta_E", q) for q in (6, 18, 24, 30)]
    o = Image.new("RGB", (pr[0].width, len(pr) * pr[0].height), (0, 0, 0))
    for k, im in enumerate(pr): o.paste(im, (0, k * im.height))
    o.resize((o.width // 2, o.height // 2)).save(os.path.join(D, "prancha_%s_%s_fresta_E.png" % (B_, modo)))
print("VIDEO_PELO_QUADROS_OK", n)
