"""Prancha do diagnostico v22 (flanco direito / ventre). Uso: python prancha_flanco_v22.py review/v22_flanco"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
D = os.path.abspath(sys.argv[1]); AQ = os.path.dirname(os.path.abspath(__file__)); W, H = 640, 480
try: F = ImageFont.truetype("arial.ttf", 22)
except OSError: F = ImageFont.load_default()
ref = Image.open(os.path.join(AQ, "ref", "lobo-artico-referencia.png")).convert("RGB")
def cel(p, t):
    im = ref.copy() if p is None else Image.open(os.path.join(D, p)).convert("RGB"); im.thumbnail((W, H)); c = Image.new("RGB", (W, H), (20, 20, 22)); c.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    d = ImageDraw.Draw(c); d.rectangle((0, 0, W, 32), fill=(0, 0, 0)); d.text((8, 5), t, font=F, fill=(255, 255, 255)); return c
L = [[cel(None, "REFERENCIA (repouso)"), cel("diag/agulhas_repouso_q0000.png", "v21 repouso: leque de agulhas (vermelho)"), cel("diag/agulhas_Trote_q0006.png", "v21 Trote q6: agulhas esticam = membrana")],
     [cel("diag/real_LOW_Trote_barriga_q0006.png", "v21 Trote q6 (real, de baixo)"), cel("v22/real_LOW_Trote_barriga_q0006.png", "v22 so pesos Trote q6: membrana continua"), cel("diag/pesos_LOW_repouso_barriga_q0000.png", "v21 pesos: fronteira abrupta Coluna|Coxa/Tibia D")],
     [cel("diag/real_LOW_Corrida_virilha_D_q0012.png", "v21 Corrida q12 (virilha D)"), cel("v22/real_LOW_Corrida_virilha_D_q0012.png", "v22 Corrida q12"), cel("v22/pesos_LOW_Corrida_barriga_q0012.png", "v22 pesos: transicao gradual")]]
o = Image.new("RGB", (3 * W + 8, 3 * H + 8), (40, 40, 40))
for r, l in enumerate(L):
    for c, im in enumerate(l): o.paste(im, (c * (W + 4), r * (H + 4)))
o.save(os.path.join(D, "diagnostico_flanco_v22.png")); print("PRANCHA_FLANCO_OK")
