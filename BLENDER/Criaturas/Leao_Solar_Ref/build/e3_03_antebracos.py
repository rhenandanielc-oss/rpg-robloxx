"""E3 passo 2: uniformiza as manchas escuras dos membros sem achatar o pelo, por TEXEL.
1. Rasteriza na UV a posicao 3D de cada texel dos membros (mapa de posicao, interpolacao baricentrica).
2. Baixa frequencia em 3D: luminancia dos texels agregada numa grade de 0,15 stud e suavizada (~0,45 stud).
3. Alvo: percentil 80 da luminancia do MESMO membro numa janela de altura de +-1,5 stud (a mancha cobre a faixa toda).
4. Razao = alvo x 0,92 / baixa frequencia (so clareia, ate 3x em luz linear), suavizada em 3D e aplicada texel a texel:
   a variacao fina do pelo fica. Regiao: membros abaixo do ventre (Z < 7,5), fora da juba (saturacao alta).
Uso: python e3_03_antebracos.py <textura.png> <tris.npz com pos> <saida.png>"""
import sys
import numpy as np
from PIL import Image
tex, trisf, out = sys.argv[1:4]
im = np.asarray(Image.open(tex).convert("RGB")).astype(np.float32) / 255; H, W = im.shape[:2]; L = im ** 2.2
d = np.load(trisf); cen, tri, pos = d["centro"], d["tri"], d["pos"]
sel = np.nonzero((cen[:, 2] < 7.4) & (np.abs(cen[:, 0]) > 0.5) & (cen[:, 2] > 0.1))[0]
P = np.zeros((H, W, 3), np.float32); M = np.zeros((H, W), bool)
for i in sel:                                                    # mapa de posicao 3D por texel
    uv = tri[i] * np.array([W, -H]) + np.array([0, H])
    x0, y0 = np.floor(uv.min(0)).astype(int); x1, y1 = np.ceil(uv.max(0)).astype(int)
    x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, W - 1), min(y1, H - 1)
    if x1 < x0 or y1 < y0: continue
    X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
    (ax, ay), (bx, by), (cx, cy) = uv; den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(den) < 1e-9: continue
    l1 = ((by - cy) * (X - cx) + (cx - bx) * (Y - cy)) / den; l2 = ((cy - ay) * (X - cx) + (ax - cx) * (Y - cy)) / den; l3 = 1 - l1 - l2
    dentro = (l1 >= -0.01) & (l2 >= -0.01) & (l3 >= -0.01)
    if not dentro.any(): continue
    p = l1[..., None] * pos[i, 0] + l2[..., None] * pos[i, 1] + l3[..., None] * pos[i, 2]
    yy, xx = np.nonzero(dentro); P[y0 + yy, x0 + xx] = p[yy, xx]; M[y0 + yy, x0 + xx] = True
ty, tx = np.nonzero(M); pt = P[ty, tx]; lt = L[ty, tx] @ np.array([0.2126, 0.7152, 0.0722], np.float32)
srgb = im[ty, tx]; S = (srgb.max(1) - srgb.min(1)) / np.maximum(srgb.max(1), 1e-4)
def suave(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
peso = suave((7.5 - pt[:, 2]) / 0.8) * suave((0.84 - S) / 0.06)
g = 0.15; o = pt.min(0) - 4 * g; idx = ((pt - o) / g).astype(int); n = idx.max(0) + 6; ii = tuple(idx.T)
def blur(a, r):
    for ax in range(3):
        c = np.cumsum(np.pad(a, [(r + 1, r) if i == ax else (0, 0) for i in range(3)]), axis=ax)
        hi = [slice(None)] * 3; lo = [slice(None)] * 3; hi[ax] = slice(2 * r + 1, None); lo[ax] = slice(0, -2 * r - 1)
        a = c[tuple(hi)] - c[tuple(lo)]
    return a
soma = np.zeros(n, np.float32); cont = np.zeros(n, np.float32)
np.add.at(soma, ii, lt * peso); np.add.at(cont, ii, peso)
baixa = (blur(soma, 3) / np.maximum(blur(cont, 3), 1e-4))[ii]
membro = (pt[:, 0] > 0).astype(int) * 2 + (pt[:, 1] < -4.5).astype(int); faixa = np.clip((pt[:, 2] / 0.5).astype(int), 0, 40)
alvo = np.zeros(len(pt), np.float32)
for m_ in range(4):
    for z_ in range(41):
        janela = (membro == m_) & (np.abs(faixa - z_) <= 3) & (peso > 0.5); aqui = (membro == m_) & (faixa == z_)
        if janela.sum() >= 200 and aqui.any(): alvo[aqui] = np.percentile(lt[janela], 80)
r = np.where(alvo > 0, np.clip(0.92 * alvo / np.maximum(baixa, 1e-4), 1.0, 3.0), 1.0)
rs = np.zeros(n, np.float32); np.add.at(rs, ii, (r - 1) * peso); r = 1 + (blur(rs, 2) / np.maximum(blur(cont, 2), 1e-4))[ii] * (peso > 0.02)
print("texels dos membros", len(pt), "clareados >5%", int((r > 1.05).sum()), "razao p50/p95/max", np.percentile(r, [50, 95]).round(3), round(float(r.max()), 3))
L2 = L.copy(); L2[ty, tx] = L[ty, tx] * r[:, None]
Image.fromarray((np.clip(L2, 0, 1) ** (1 / 2.2) * 255 + 0.5).astype(np.uint8)).save(out)
C = np.zeros((H, W), np.uint8); C[ty, tx] = (np.clip((r - 1) / 2, 0, 1) * 255).astype(np.uint8)
Image.fromarray(C).save(out.replace(".png", "_correcao.png")); print("ANTEBRACOS_OK", out)
