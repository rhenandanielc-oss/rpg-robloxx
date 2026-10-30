"""Matte limpo da silhueta oficial: escuro contra o fundo -> maior componente ligado (tira o humano e restos),
corta abaixo da linha do chao, recorta com margem e chao na ultima linha. Imprime o perfil por colunas.
Uso: python matte.py <Especie> [--chao LINHA_x4] [--limiar DELTA] [--xmax COL] [--xmin COL]"""
import sys, os, argparse
from collections import deque
from PIL import Image

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = argparse.ArgumentParser()
p.add_argument("especie")
p.add_argument("--chao", type=int, default=0, help="linha (na imagem x4) abaixo da qual tudo e cortado")
p.add_argument("--limiar", type=int, default=35)
p.add_argument("--xmin", type=int, default=0)
p.add_argument("--xmax", type=int, default=0, help="ignora colunas >= xmax (ex.: humano encostado)")
p.add_argument("--passo", type=int, default=12)
p.add_argument("--margem", type=float, default=0.05)
a = p.parse_args()
im = Image.open(os.path.join(R, "ref", a.especie + "_silhueta_x4.png")).convert("L")
W, H = im.size
px = im.load()
# limiar de Otsu no interior (as bordas dos paineis tem moldura escura)
mx, my = int(W * a.margem), int(H * a.margem)
hist = [0] * 256
for y in range(my, H - my):
    for x in range(mx, W - mx):
        hist[px[x, y]] += 1
tot = sum(hist); sm = sum(i * h for i, h in enumerate(hist)); sb = wb = 0; melhor = (0, 0)
for t in range(256):
    wb += hist[t]
    if wb == 0 or wb == tot: continue
    sb += t * hist[t]
    mb, mf = sb / wb, (sm - sb) / (tot - wb)
    v = wb * (tot - wb) * (mb - mf) ** 2
    if v > melhor[0]: melhor = (v, t)
fundo = melhor[1]
lim = fundo - (a.limiar - 35)          # --limiar 35 = Otsu puro; maior = mais rigoroso
chao = a.chao or (H - my)
xmax = a.xmax or (W - mx)
xmin = max(a.xmin, mx)
esc = [[(xmin <= x < xmax) and my <= y < chao and px[x, y] < lim for x in range(W)] for y in range(H)]
lab = [[0] * W for _ in range(H)]
comps = []
for y in range(H):
    for x in range(W):
        if esc[y][x] and not lab[y][x]:
            idx = len(comps) + 1; pts = []; dq = deque([(x, y)]); lab[y][x] = idx
            while dq:
                u, v = dq.popleft(); pts.append((u, v))
                for du, dv in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nu, nv = u + du, v + dv
                    if 0 <= nu < W and 0 <= nv < H and esc[nv][nu] and not lab[nv][nu]:
                        lab[nv][nu] = idx; dq.append((nu, nv))
            comps.append(pts)
comps.sort(key=len, reverse=True)
c = comps[0]
xs = [u for u, v in c]; ys = [v for u, v in c]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
mg = 8
out = Image.new("RGBA", (x1 - x0 + 1 + 2 * mg, y1 - y0 + 1 + mg), (0, 0, 0, 0))
o = out.load()
for u, v in c:
    o[u - x0 + mg, v - y0 + mg] = (0, 0, 0, 255)
dest = os.path.join(R, "ref", a.especie + "_matte.png")
out.save(dest)
Wm, Hm = out.size
print("fundo %d limiar %d | componentes %d (maiores %s)" % (fundo, lim, len(comps), [len(k) for k in comps[:4]]))
print("MATTE %s  %dx%d  eixo(col centro)=%d  chao(linha)=%d  sujeito %dx%d px" % (dest, Wm, Hm, Wm // 2, Hm, x1 - x0 + 1, y1 - y0 + 1))
q = out.load()
for x in range(0, Wm, a.passo):
    runs, y = [], 0
    while y < Hm:
        if q[x, y][3]:
            s = y
            while y < Hm and q[x, y][3]: y += 1
            runs.append("%d->%d" % (Hm - s, Hm - y))
        else:
            y += 1
    print("x=%3d %s" % (x, " ".join(runs)))
