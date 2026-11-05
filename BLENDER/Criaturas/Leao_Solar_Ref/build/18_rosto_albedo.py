"""Ajuste local do albedo do rosto da E2: trufa do nariz marrom-escura (como a referencia) e rosto menos alaranjado
(saturacao -15%, leve aquecimento dos claros). Mascaras rasterizadas na UV (17_regioes_rosto_uv) e suavizadas.
Uso: python 18_rosto_albedo.py <textura.png> <regioes.npz> <saida.png>"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
tex, reg, out = sys.argv[1:4]
im = np.asarray(Image.open(tex).convert("RGB")).astype(np.float32) / 255; H, W = im.shape[:2]
d = np.load(reg)
def mascara(cod, raio):
    m = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(m)
    for t, r in zip(d["tri"], d["regiao"]):
        if r == cod: dr.polygon([(u * W, (1 - v) * H) for u, v in t], fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(raio))).astype(np.float32)[..., None] / 255
mn, mr = mascara(2, 0), mascara(3, 8)
mx_, mn_ = im.max(-1), im.min(-1); S = (mx_ - mn_) / np.maximum(mx_, 1e-4)
hue = np.where(mx_ == im[..., 0], ((im[..., 1] - im[..., 2]) / np.maximum(mx_ - mn_, 1e-4)) % 6, 3) * 60   # so o setor do vermelho
rosa = ((hue < 14) | (hue > 330)) & (S > 0.18) & (S < 0.75)                                               # trufa rosada, nao o pelo laranja
mn = (mn * rosa[..., None]).astype(np.float32)
mn = np.asarray(Image.fromarray((mn[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32)[..., None] / 255
cinza = im.mean(-1, keepdims=True)
rosto = cinza + (im - cinza) * 0.85
rosto = rosto * np.array([1.0, 0.99, 0.95], np.float32)
im = im * (1 - mr) + rosto * mr
lum = im.mean(-1, keepdims=True)
nariz = np.array([0.30, 0.19, 0.16], np.float32) * (0.75 + 0.5 * lum)                 # marrom-escuro, mantendo relevo
im = im * (1 - mn) + nariz * mn
Image.fromarray((np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out); print("ROSTO_OK", out)
