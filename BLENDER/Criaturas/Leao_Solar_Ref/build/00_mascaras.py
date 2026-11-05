"""Mascaras das 3 vistas da referencia principal (fundo cinza claro uniforme). Uso: python -I 00_mascaras.py <ref.png> <saida_dir>"""
import sys, os
from PIL import Image, ImageFilter
import numpy as np
ref, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
im = np.asarray(Image.open(ref).convert("RGB")).astype(float)
bg = np.median(np.concatenate([im[:8].reshape(-1,3), im[-8:].reshape(-1,3)]), axis=0)
d = np.sqrt(((im - bg) ** 2).sum(-1))
m = (d > 28)
Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5)).save(os.path.join(out, "mascara_total.png"))
m = np.asarray(Image.open(os.path.join(out, "mascara_total.png"))) > 127
print("fundo", bg)
H, W = m.shape
# separar perfil (topo) das vistas de baixo pela linha vazia
rows = m.sum(1); 
for y in range(560, 700):
    if rows[y] == 0: print("linha vazia", y); break
def caixa(sub, x0, y0, nome):
    ys, xs = np.nonzero(sub); print(nome, "x", xs.min()+x0, xs.max()+x0, "y", ys.min()+y0, ys.max()+y0)
    Image.fromarray((sub*255).astype(np.uint8)).save(os.path.join(out, nome + ".png"))
    return xs.min()+x0, xs.max()+x0, ys.min()+y0, ys.max()+y0
caixa(m[:610], 0, 0, "perfil")
caixa(m[610:, :610], 0, 610, "frente")
caixa(m[610:, 610:], 610, 610, "traseira")
