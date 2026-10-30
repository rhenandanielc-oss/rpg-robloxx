import sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("L")
# janela so do leao (x4): sem moldura, sem o humano (x >= 560); chao na linha 391
box = (22, 30, 558, 392)
c = im.crop(box)
W, H = c.size
m = Image.new("RGBA", (W, H), (0, 0, 0, 0))
p, q = c.load(), m.load()
for y in range(H):
    for x in range(W):
        if p[x, y] < 70: q[x, y] = (0, 0, 0, 255)
# limpar restos de borda: manter so componentes ligados ao chao/corpo (remove linhas finas no topo)
top = None
for y in range(H):
    n = sum(1 for x in range(W) if q[x, y][3])
    if n > 0 and n < W * 0.9:
        top = y; break
for y in range(0, top or 0):
    for x in range(W): q[x, y] = (0, 0, 0, 0)
m.save(out)
xs = [x for x in range(W) for y in range(H) if q[x, y][3]]
ys = [y for y in range(H) for x in range(W) if q[x, y][3]]
print("matte", W, H, "x", min(xs), max(xs), "y", min(ys), max(ys), "top_row", top)
print("subject_frac", round((H - min(ys)) / H, 3))
