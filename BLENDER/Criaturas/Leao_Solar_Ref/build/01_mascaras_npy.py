"""Mascaras numpy para o build do Blender: perfil (corpo inteiro e so juba), frente e traseira simetrizadas.
Coordenadas = pixels da referencia principal. Uso: python 01_mascaras_npy.py <ref_dir>"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
d = sys.argv[1]
m = np.asarray(Image.open(os.path.join(d, "mascara_total.png"))) > 127
H, W = m.shape
lado = m.copy(); lado[594:] = False
# regiao da juba no perfil (limite inferior inventado pela anatomia: corta patas, barriga e rosto)
poli = [(640, 236), (620, 0), (1066, 0), (1062, 92), (1030, 104), (1016, 150), (1028, 196), (1048, 240), (1120, 246),
        (1120, 452), (962, 452), (912, 505), (822, 512), (742, 492), (690, 448), (650, 380), (628, 300)]
reg = Image.new("L", (W, H), 0); ImageDraw.Draw(reg).polygon(poli, fill=255)
juba = lado & (np.asarray(reg) > 0)
tufo = lado.copy(); tufo[:, 222:] = False
def sim(mask, cx):
    out = mask.copy()
    for y in range(H):
        row = mask[y]; xs = np.arange(W); xm = (2 * cx - xs)
        ok = (xm >= 0) & (xm < W); r2 = np.zeros(W, bool); r2[ok] = row[xm[ok]]
        out[y] = row | r2
    return out
frente = m.copy(); frente[:610] = False; frente[:, 610:] = False; frente = sim(frente, 335)
tras = m.copy(); tras[:610] = False; tras[:, :610] = False; tras = sim(tras, 875)
for nome, a in dict(lado=lado, juba_lado=juba, tufo_lado=tufo, frente=frente, tras=tras).items():
    np.save(os.path.join(d, nome + ".npy"), a)
    Image.fromarray((a * 255).astype(np.uint8)).save(os.path.join(d, "m_" + nome + ".png"))
print("ok", juba.sum(), tufo.sum())
