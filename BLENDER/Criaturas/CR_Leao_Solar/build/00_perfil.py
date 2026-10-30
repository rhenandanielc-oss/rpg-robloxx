import sys
from PIL import Image
m = Image.open(sys.argv[1]).convert("RGBA"); W, H = m.size; q = m.load()
G = H  # chao = base da imagem
print("W", W, "H", H)
for x in range(0, W, 13):
    runs = []; y = 0
    while y < H:
        if q[x, y][3]:
            s = y
            while y < H and q[x, y][3]: y += 1
            runs.append((G - s, G - y))  # (alto, baixo) em px acima do chao
        else: y += 1
    print(f"x={x:3d} " + " ".join(f"[{a}->{b}]" for a, b in runs))
