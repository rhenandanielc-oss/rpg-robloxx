import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("L")
W, H = im.size
px = im.load()
# area util do painel (sem moldura): x 10..W-24, y 8..H-62 no x4
x0, x1, y0, y1 = 14, W - 26, 24, H - 64
esc = [[px[x, y] < 70 for x in range(W)] for y in range(H)]
def col_top(x):
    for y in range(y0, y1):
        if esc[y][x]: return y
    return None
# chao = linha mais baixa com muitos pixels escuros (patas)
chao = max(y for y in range(y0, y1) if sum(esc[y][x] for x in range(x0, x1)) > 6)
# humano: colunas a partir de 560
hum = [x for x in range(560, x1) if col_top(x) is not None]
hum_top = min(col_top(x) for x in hum)
print("chao", chao, "humano x", hum[0], hum[-1], "topo", hum_top, "altura px", chao - hum_top)
leao = [x for x in range(x0, 560) if col_top(x) is not None and col_top(x) < chao - 5]
print("leao x", leao[0], leao[-1])
for x in range(leao[0], 560, 12):
    t = col_top(x)
    # espessura vertical do corpo nesta coluna (primeiro claro abaixo do topo)
    if t is None: print(x, "-"); continue
    y = t
    while y < chao and esc[y][x]: y += 1
    print(f"x={x:3d} topo={t:3d} (alt {chao - t:3d}) fundo_massa={y:3d} (alt {chao - y:3d})")

