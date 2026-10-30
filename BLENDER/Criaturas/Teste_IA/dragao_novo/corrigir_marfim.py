"""Corrige na base_color do Meshy (variante texto) o tom esverdeado/cinza do ventre e dos chifres para MARFIM quente,
sem tocar no vermelho das escamas nem no laranja das membranas: pixels de baixa saturacao ou matiz verde/ciano
recebem matiz ~36 graus e saturacao de marfim, mantendo o brilho (o desenho das placas e preservado).
Uso: python corrigir_marfim.py <base_color.png> <saida.png>"""
import sys
import numpy as np
from PIL import Image
ent, sai = sys.argv[1], sys.argv[2]
im = Image.open(ent).convert("RGB"); hsv = np.asarray(im.convert("HSV")).astype(np.float32)
h, s, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
verde = (h > 42) & (h < 215)                        # amarelo-esverdeado/ciano
neutro = (s < 0.34) & (v > 0.38)                    # creme palido / cinza claro (o vermelho das escamas tem s > 0.5)
m = (verde | neutro) & (v > 0.12)
# transicao suave na borda da mascara (evita contorno duro entre placa e escama)
from PIL import ImageFilter
mask = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
w = np.asarray(mask).astype(np.float32) / 255
h2 = np.where(w > 0, 34.0, h); s2 = s * (1 - w) + (0.40 + 0.12 * (1 - v)) * w
v2 = v * (1 - w) + np.clip(v * 1.04, 0, 1) * w
out = np.stack([h2 * 255 / 360, np.clip(s2, 0, 1) * 255, np.clip(v2, 0, 1) * 255], -1).astype(np.uint8)
Image.fromarray(out, "HSV").convert("RGB").save(sai)
print("pixels corrigidos: %.1f%%" % (100 * m.mean()))
