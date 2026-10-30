import sys
from PIL import Image
from collections import deque
m = Image.open(sys.argv[1]).convert("RGBA"); W, H = m.size; q = m.load()
lab = [[0] * W for _ in range(H)]; comps = []
for y in range(H):
    for x in range(W):
        if q[x, y][3] and not lab[y][x]:
            idx = len(comps) + 1; pts = []; dq = deque([(x, y)]); lab[y][x] = idx
            while dq:
                a, b = dq.popleft(); pts.append((a, b))
                for da, db in ((1,0),(-1,0),(0,1),(0,-1)):
                    na, nb = a + da, b + db
                    if 0 <= na < W and 0 <= nb < H and q[na, nb][3] and not lab[nb][na]:
                        lab[nb][na] = idx; dq.append((na, nb))
            comps.append(pts)
comps.sort(key=len, reverse=True)
print("componentes", len(comps), "maiores", [len(c) for c in comps[:5]])
out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); o = out.load()
for a, b in comps[0]: o[a, b] = (0, 0, 0, 255)
xs = [a for a, b in comps[0]]; ys = [b for a, b in comps[0]]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
# recorta com margem igual dos lados (sujeito centrado) e chao na ultima linha
mg = 8; out = out.crop((x0 - mg, y0 - mg, x1 + mg + 1, y1 + 1))
out.save(sys.argv[1])
print("lion px: largura", x1 - x0 + 1, "altura", y1 - y0 + 1, "-> imagem", out.size, "subject_frac", round((y1 - y0 + 1) / out.size[1], 3))
