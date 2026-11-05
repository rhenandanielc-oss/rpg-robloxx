"""Corrige o albedo da textura do Meshy (nao a exposicao do render): saturacao e valor por zona tonal, com o peso
da juba dado pela saturacao original do texel (pelo do corpo e menos saturado). Parametros ajustados contra as
cores medias das regioes do perfil da referencia, sob a luz neutra do 07_render_eevee (meshy/correcao_cor.json).
Uso: python 09_corrigir_albedo.py <entrada.png> <params.json> <saida.png>"""
import sys, json
import numpy as np
from PIL import Image
src, prm, out = sys.argv[1:4]; p = json.load(open(prm))
c = np.asarray(Image.open(src).convert("RGB")).astype(np.float32) / 255
mx = c.max(-1); mn = c.min(-1); V = mx; S = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
h = np.where((mx - mn)[..., None] > 1e-6, (c - mn[..., None]) / np.maximum(mx - mn, 1e-6)[..., None], 1)
w = np.clip((S - 0.50) / 0.18, 0, 1)
V2 = np.minimum(1, (V ** p["gama"]) * p["val"] * (1 + p["corpo"] * (1 - w)))
V2 = V2 * (1 - 0.18 * w * np.maximum(0, 0.62 - V2))
S2 = np.minimum(1, S * (p["sat"] + p["sat_juba"] * w))
c2 = V2[..., None] * (1 - S2[..., None] * (1 - h))
Image.fromarray((np.clip(c2, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out); print("ALBEDO_OK", out)
