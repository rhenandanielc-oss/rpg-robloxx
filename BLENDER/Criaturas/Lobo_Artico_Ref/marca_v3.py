"""Mascara da marca v3 (desenho da referencia): espiral de ~2,3 voltas (aneis sem se tocar), haste curva descendo para a frente
(peito) com folhas de gelo lanceoladas alternadas, e uma gavinha curta subindo para tras (rumo aos cristais).
Saida: tex/marca_mascara_v3.png 512x512 RGB (R = linhas/folhas, G = halo borrado). Sem tracos retos verticais.
Uso: python marca_v3.py <dir_tex>"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.abspath(sys.argv[1]); S = 512
im = Image.new("L", (S, S), 0); d = ImageDraw.Draw(im)
def traco(pts, w0, w1, val=255):
    n = len(pts)
    for i in range(n - 1):
        w = w0 + (w1 - w0) * i / (n - 1); d.line([pts[i], pts[i + 1]], fill=val, width=max(1, int(round(w))))
        r = w / 2; d.ellipse((pts[i][0] - r, pts[i][1] - r, pts[i][0] + r, pts[i][1] + r), fill=val)
def bez(p0, p1, p2, p3, n=80):
    return [tuple((1 - t) ** 3 * np.array(p0) + 3 * (1 - t) ** 2 * t * np.array(p1) + 3 * (1 - t) * t * t * np.array(p2) + t ** 3 * np.array(p3))
            for t in np.linspace(0, 1, n)]
# coordenadas do PIL: x cresce para TRAS do lobo, y cresce para BAIXO
cx, cy = 318, 196
esp = []
for i in range(300):
    t = i / 299; th = t * 2.3 * 2 * math.pi + 1.2; r = 5 + 80 * t ** 1.15
    esp.append((cx + r * math.cos(th), cy + r * math.sin(th) * 0.95))
traco(esp, 3.5, 9.0)
ox, oy = esp[-1]
haste = bez((ox, oy), (ox - 40, oy + 90), (190, 340), (92, 470))
traco(haste, 8.5, 2.5)
gav = bez((cx + 60, cy - 60), (cx + 110, cy - 110), (cx + 150, cy - 140), (cx + 175, cy - 105), 50)   # gavinha que sobe
traco(gav, 5.0, 2.0)
def folha(base, ang, comp, larg):
    ca, sa = math.cos(ang), math.sin(ang); a, b = [], []
    for i in range(24):
        t = i / 23; x = comp * t; y = larg * math.sin(math.pi * t ** 0.85) * (1 - 0.25 * t)
        a.append((base[0] + x * ca - y * sa, base[1] + x * sa + y * ca)); b.append((base[0] + x * ca + y * sa, base[1] + x * sa - y * ca))
    d.polygon(a + b[::-1], fill=150); traco(a, 2.2, 1.0); traco(b, 2.2, 1.0)
    traco([base, (base[0] + comp * 0.9 * ca, base[1] + comp * 0.9 * sa)], 1.6, 0.8)
for k, t in enumerate(np.linspace(0.12, 0.85, 7)):                 # folhas alternadas ao longo da haste
    i = int(t * (len(haste) - 1)); p = haste[i]; q = haste[min(i + 1, len(haste) - 1)]
    tang = math.atan2(q[1] - p[1], q[0] - p[0]); lado = 1 if k % 2 == 0 else -1
    folha(p, tang + lado * math.radians(58), 62 - 5 * k, 13 - 0.8 * k)
for k, t in enumerate((0.35, 0.7)):                                 # duas folhinhas na gavinha
    i = int(t * (len(gav) - 1)); p = gav[i]; folha(p, math.radians(-40 - 50 * k), 34, 8)
R = im.filter(ImageFilter.GaussianBlur(0.9)); G = im.filter(ImageFilter.GaussianBlur(13))
g = np.asarray(G, np.float32); g = np.clip(g / max(g.max(), 1) * 1.7, 0, 1)
Image.fromarray((np.stack([np.asarray(R, np.float32) / 255, g, np.zeros_like(g)], -1) * 255).astype(np.uint8), "RGB").save(os.path.join(OUT, "marca_mascara_v3.png"))
print("MARCA_V3_OK")
