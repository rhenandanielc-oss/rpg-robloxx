"""Assimetria de COR do peito na vista frontal ortografica (orto_alinhamento: 1000 px, escala 9,5, centro z 4,3):
pixels claros (creme) e escuros (marrom/cinza) na caixa do peito, centroide em x (studs) e fracao em cada lado.
Uso: python cor_peito.py <frente.png> [z_min z_max meia_largura]"""
import sys
import numpy as np
from PIL import Image
im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(float) / 255; H, W, _ = im.shape; ESC, ZC = 9.5, 4.3
z0, z1, hw = (float(a) for a in sys.argv[2:5]) if len(sys.argv) > 4 else (2.8, 5.6, 2.2)
xs = ((np.arange(W) + 0.5) / W - 0.5) * ESC; zs = ((1 - (np.arange(H) + 0.5) / H) - 0.5) * ESC + ZC
X, Z = np.meshgrid(xs, zs)
caixa = (Z > z0) & (Z < z1) & (np.abs(X) < hw)
lum = im.mean(axis=2); bg = im[5, 5]; fundo = (np.abs(im - bg) < 0.03).all(axis=2)
linha = np.abs(np.arange(W) - W / 2) < 4; caixa &= ~linha[None, :]
claro = caixa & (lum > 0.42) & ~fundo; escuro = caixa & (lum < 0.24) & ~fundo
for nome, m in (("claro", claro), ("escuro", escuro)):
    if m.sum(): print("%s: centroide x %+.3f studs | fracao em +X %.2f | pixels %d" % (nome, X[m].mean(), (X[m] > 0).mean(), m.sum()))
