"""Texturas proprias dos efeitos de GELO (Dragao Glacial, 02/11). Geradas por codigo (nada copiado): PNG RGBA 256x256
em ../ia/vfx_gelo_tex/ (servidas pelo servidor local para o upload_image do Studio).
- lasca: fragmento/lanca de gelo facetado (eixo vertical = direcao do movimento com Orientation VelocityParallel)
- rastro: risco de velocidade fino e brilhante (eixo vertical)
- nevoa: nevoa fria macia (ruido fractal, bordas suaves)
- jato: fios turbulentos esticados (miolo do sopro)
- brilho: cintilacao de cristal em estrela de 4 pontas
- floco: floco de neve hexagonal pequeno
- geada: geada no chao (veios radiais ramificados + cristais), para Decal num disco que cresce
Uso: python gerar_texturas_gelo.py"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ia", "vfx_gelo_tex"); os.makedirs(OUT, exist_ok=True)
N = 256
rng = np.random.default_rng(7)
yy, xx = np.mgrid[0:N, 0:N] / (N - 1) * 2 - 1          # -1..1

def salvar(nome, rgb, a):
    a = np.clip(a, 0, 1); rgb = np.clip(rgb, 0, 1)
    img = np.dstack([rgb[..., 0], rgb[..., 1], rgb[..., 2], a]) * 255
    Image.fromarray(img.astype(np.uint8), "RGBA").save(os.path.join(OUT, nome + ".png")); print("ok", nome)
def cor(r, g, b): return np.dstack([np.full((N, N), r), np.full((N, N), g), np.full((N, N), b)])
def ruido(oct=5, base=4):
    t = np.zeros((N, N))
    for o in range(oct):
        f = base * 2 ** o; g = rng.random((f + 1, f + 1))
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((N, N), Image.BICUBIC)
        t += np.asarray(im) / 255 / 2 ** o
    return (t - t.min()) / (t.max() - t.min())

# lasca: losango alongado (ponta em cima), facetas por normal falsa, aresta clara, miolo azulado
d = np.abs(xx) / (0.30 * (1 - np.clip(yy, -1, 1) * 0.15)) + np.abs(yy) / 0.95
forma = np.clip((1 - d) * 6, 0, 1)
faceta = np.where(xx > 0, 0.75, 1.0) * (0.75 + 0.25 * (1 - np.abs(yy)))
aresta = np.clip(1 - np.abs(1 - d) * 12, 0, 1) * forma
rgb = cor(0.70, 0.86, 1.0) * faceta[..., None] + aresta[..., None] * 0.5
salvar("lasca", rgb, forma * (0.55 + 0.45 * aresta) + forma * 0.25)

# rastro: linha fina vertical com cauda (mais forte em cima)
w = np.exp(-(xx / 0.06) ** 2) * np.clip(1 - np.abs(yy), 0, 1) ** 0.6 * (0.55 + 0.45 * (1 - yy) / 2)
salvar("rastro", cor(0.9, 0.97, 1.0), w)

# nevoa: ruido fractal com queda radial suave
r = np.sqrt(xx ** 2 + yy ** 2); n = ruido(6, 3)
a = np.clip(1 - r, 0, 1) ** 1.6 * (0.35 + 0.65 * n)
salvar("nevoa", cor(0.94, 0.97, 1.0), a)

# jato: fios esticados na vertical (ruido anisotropico)
g = rng.random((9, 48)); fios = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((N, N), Image.BICUBIC)) / 255
fios = (fios - fios.min()) / (fios.max() - fios.min())
a = np.clip(1 - np.abs(xx) * 1.1, 0, 1) ** 1.2 * np.clip(1 - np.abs(yy), 0, 1) ** 0.8 * (0.25 + 0.75 * fios ** 1.5)
salvar("jato", cor(0.92, 0.97, 1.0) * (0.85 + 0.15 * fios)[..., None], a)

# brilho: estrela de 4 pontas fina + nucleo
s = np.exp(-(xx / 0.03) ** 2) * np.exp(-np.abs(yy) * 2.2) + np.exp(-(yy / 0.03) ** 2) * np.exp(-np.abs(xx) * 2.2)
s += np.exp(-(r / 0.12) ** 2)
salvar("brilho", cor(0.95, 0.99, 1.0), np.clip(s, 0, 1))

# floco: 6 bracos com ramos
im = Image.new("L", (N, N), 0); dr = ImageDraw.Draw(im); c = N / 2
for k in range(6):
    a0 = k * math.pi / 3; L = N * 0.42
    x1, y1 = c + math.cos(a0) * L, c + math.sin(a0) * L
    dr.line([(c, c), (x1, y1)], fill=255, width=7)
    for f in (0.45, 0.7):
        bx, by = c + math.cos(a0) * L * f, c + math.sin(a0) * L * f
        for sgn in (-1, 1):
            a1 = a0 + sgn * math.pi / 4; l2 = L * 0.28 * (1.2 - f)
            dr.line([(bx, by), (bx + math.cos(a1) * l2, by + math.sin(a1) * l2)], fill=255, width=5)
im = im.filter(ImageFilter.GaussianBlur(1.5))
salvar("floco", cor(0.92, 0.98, 1.0), np.asarray(im) / 255)

# geada: veios radiais ramificados (random walk) + cristais finos, base translucida com borda irregular
G = 512; im = Image.new("L", (G, G), 0); dr = ImageDraw.Draw(im); c = G / 2
def veio(x, y, ang, comp, larg, prof):
    for _ in range(int(comp)):
        ang += rng.normal(0, 0.18); nx, ny = x + math.cos(ang) * 4, y + math.sin(ang) * 4
        if math.hypot(nx - c, ny - c) > G * 0.49: return
        dr.line([(x, y), (nx, ny)], fill=255, width=max(1, int(larg)))
        x, y = nx, ny; larg *= 0.985
        if prof < 3 and rng.random() < 0.06: veio(x, y, ang + rng.choice([-1, 1]) * rng.uniform(0.4, 0.9), comp * 0.45, larg * 0.7, prof + 1)
for k in range(26): veio(c, c, k / 26 * 2 * math.pi + rng.normal(0, 0.08), 70, 4, 0)
for _ in range(900):
    x, y = rng.uniform(0, G), rng.uniform(0, G)
    if math.hypot(x - c, y - c) < G * 0.47:
        a1 = rng.uniform(0, math.pi); l = rng.uniform(2, 7)
        dr.line([(x - math.cos(a1) * l, y - math.sin(a1) * l), (x + math.cos(a1) * l, y + math.sin(a1) * l)], fill=170, width=1)
veios = np.asarray(im.filter(ImageFilter.GaussianBlur(0.8))) / 255
gy, gx = np.mgrid[0:G, 0:G] / (G - 1) * 2 - 1; rr = np.sqrt(gx ** 2 + gy ** 2)
nb = np.asarray(Image.fromarray((ruido(5, 4) * 255).astype(np.uint8)).resize((G, G), Image.BICUBIC)) / 255
borda = np.clip((0.97 - rr + (nb - 0.5) * 0.18) * 9, 0, 1)
a = np.clip(0.30 + 0.25 * nb + 0.75 * veios, 0, 1) * borda
rgb = np.dstack([0.78 + 0.22 * veios, 0.90 + 0.10 * veios, np.ones((G, G))])
img = np.dstack([rgb, a]) * 255
Image.fromarray(img.astype(np.uint8), "RGBA").save(os.path.join(OUT, "geada.png")); print("ok geada")
# versoes horizontais (Beam/Trail desenham a textura ao longo do comprimento)
for n_ in ("jato", "rastro"): Image.open(os.path.join(OUT, n_ + ".png")).rotate(90, expand=True).save(os.path.join(OUT, n_ + "_h.png")); print("ok", n_ + "_h")
