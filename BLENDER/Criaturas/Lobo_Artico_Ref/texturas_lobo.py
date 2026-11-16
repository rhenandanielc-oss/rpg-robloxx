"""Texturas procedurais proprias do Lobo Artico (sem reaproveitar o atlas dos prototipos antigos).
- tex/pelo_atlas.png  1024x1024 RGBA: 4 tufos de mechas (colunas de 256), raiz na BASE da imagem, ponta no topo.
    col 0 branco A, col 1 branco B (mais longo/fino), col 2 cinza frio (subpelo/sombra), col 3 pontas azul-gelo
    (perto da marca e dos cristais). Fios afinam e somem na ponta; subpelo opaco so na raiz (sem buracos).
- tex/marca_mascara.png  512x512 RGB: R = linhas da marca (espiral + varredura + folhas finas), G = halo borrado.
Uso: python -I texturas_lobo.py <dir_tex>"""
import sys, os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.abspath(sys.argv[1]); os.makedirs(OUT, exist_ok=True)
rnd = random.Random(11)

# ------------------------------------------------------------------ atlas de mechas
H, W, CW = 1024, 1024, 256
A = np.zeros((H, W), np.float32); VS = np.zeros((H, W), np.float32); WS = np.zeros((H, W), np.float32)
OFF = [(dx, dy, math.exp(-(dx * dx + dy * dy) / 1.1)) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

def largura(t):
    """meia-largura do tufo (px) ao longo do comprimento t (0 raiz, 1 ponta): base larga, ponta fechada"""
    return 104 * math.sin(math.pi * (0.25 + 0.75 * t)) ** 0.9 + 3

def splat(xs, ys, a, v):
    xi = np.round(xs).astype(int); yi = np.round(ys).astype(int)
    for dx, dy, w in OFF:
        x = np.clip(xi + dx, 0, W - 1); y = np.clip(yi + dy, 0, H - 1); k = a * w
        np.maximum.at(A, (y, x), k); np.add.at(VS, (y, x), v * k); np.add.at(WS, (y, x), k)

def tufo(col, n_fios, comp, v_raiz, v_ponta, fino):
    cx = col * CW + CW / 2; L = (H - 16) * comp
    # subpelo: preenchimento opaco so perto da raiz (o card nao fica vazado onde encosta na pele)
    ts = np.linspace(0, 0.42, 160)
    for t in ts:
        w = largura(t) * 0.88; xs = np.arange(cx - w, cx + w, 1.0)
        borda = np.clip((w - np.abs(xs - cx)) / 18.0, 0, 1)
        a = 0.92 * (1 - t / 0.42) ** 1.4 * borda; y = 8 + t * L
        splat(xs, np.full_like(xs, y), a.astype(np.float32), np.full_like(xs, v_raiz * 0.92, dtype=np.float32))
    mechas = [(rnd.uniform(-0.75, 0.75), rnd.uniform(0.75, 1.0)) for _ in range(6)]   # sub-mechas: fios convergem nas pontas
    for i in range(n_fios):
        s = rnd.uniform(-1, 1); s = math.copysign(abs(s) ** 0.8, s)
        ms, mf = min(mechas, key=lambda m: abs(m[0] - s) + rnd.uniform(0, 0.35))
        fim = rnd.uniform(0.62, 1.0) * (1 - 0.32 * abs(s)) * mf          # fios da borda mais curtos: ponta afilada
        onda, fase, cur = rnd.uniform(0.5, 2.2), rnd.uniform(0, 6.28), rnd.uniform(-10, 10)
        brilho = rnd.uniform(-0.07, 0.07)
        t = np.linspace(0, fim, int(fim * L / 1.6)); u = t / fim
        lw = np.array([largura(x) for x in t]) * 0.94
        conv = 0.75 * u ** 1.6                                             # 0 na raiz -> fio junta na mecha na ponta
        xs = cx + (s * (1 - conv) + ms * conv) * lw + np.sin(u * 3.1 * onda + fase) * 2.2 + cur * u ** 2
        ys = 8 + t * L
        a = (0.95 * (1 - u ** 2.6)).astype(np.float32)
        v = (v_raiz + (v_ponta - v_raiz) * np.clip(u * 1.25, 0, 1) + brilho).astype(np.float32)
        if fino: a = a * (0.75 + 0.25 * (np.sin(u * 40 + fase) > -0.6))
        splat(xs, ys, a, v)

tufo(0, 190, 0.96, 0.80, 0.98, False)
tufo(1, 150, 1.00, 0.84, 0.99, True)
tufo(2, 190, 0.92, 0.62, 0.86, False)
tufo(3, 170, 0.96, 0.78, 0.96, True)
V = np.where(WS > 1e-5, VS / np.maximum(WS, 1e-5), 0.85)
rgb = np.stack([V, V, V], -1)
frio = np.array([0.965, 0.98, 1.0], np.float32)                     # branco levemente frio (sombras cinza-azuladas)
rgb *= frio
gelo = np.array([0.80, 0.93, 1.0], np.float32)
yy = np.linspace(0, 1, H)[:, None, None]                              # col 3: azul so nas pontas
rgb[:, 3 * CW:4 * CW] *= (1 - yy * 0.9) * frio + (yy * 0.9) * gelo
img = np.concatenate([np.clip(rgb, 0, 1), np.clip(A, 0, 1)[..., None]], -1)
Image.fromarray((img[::-1] * 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, "pelo_atlas.png"))   # linha 0 = topo do PNG

# ------------------------------------------------------------------ mascara da marca (espiral ciano)
S = 512; im = Image.new("L", (S, S), 0); d = ImageDraw.Draw(im)
def traco(pts, w0, w1):
    n = len(pts)
    for i in range(n - 1):
        t = i / (n - 1); w = w0 + (w1 - w0) * t
        d.line([pts[i], pts[i + 1]], fill=255, width=max(1, int(round(w))))
        r = w / 2; d.ellipse((pts[i][0] - r, pts[i][1] - r, pts[i][0] + r, pts[i][1] + r), fill=255)
# coordenadas da imagem: x = tras do lobo (u cresce para +Y), y do PIL cresce para BAIXO
cx, cy = 300, 170
esp = []
for i in range(260):
    th = i / 259 * 4.1 * math.pi; r = 5 + 78 * (i / 259) ** 1.15
    esp.append((cx + r * math.cos(th + 2.2), cy + r * math.sin(th + 2.2) * 0.92))
traco(esp, 3.0, 7.5)
ox, oy = esp[-1]
var = []                                                              # varredura: sai da espiral, desce para a frente (peito)
for i in range(120):
    t = i / 119
    var.append((ox + (-120 * t - 60 * t * t), oy + 230 * t ** 1.1 - 40 * math.sin(math.pi * t)))
traco(var, 7.0, 1.5)
def folha(p0, ang, comp, larg):
    pts_a, pts_b = [], []
    for i in range(30):
        t = i / 29; x = comp * t; y = larg * math.sin(math.pi * t) ** 0.8
        ca, sa = math.cos(ang), math.sin(ang)
        pts_a.append((p0[0] + x * ca - y * sa, p0[1] + x * sa + y * ca)); pts_b.append((p0[0] + x * ca + y * sa, p0[1] + x * sa - y * ca))
    traco(pts_a, 2.4, 1.2); traco(pts_b, 2.4, 1.2)
    traco([p0, (p0[0] + comp * 0.85 * math.cos(ang), p0[1] + comp * 0.85 * math.sin(ang))], 1.6, 1.0)
folha(var[45], math.radians(115), 95, 18)
folha(var[75], math.radians(100), 80, 15)
folha((cx + 40, cy + 95), math.radians(85), 105, 16)
for k in range(3):                                                    # linhas finas que se perdem na pelagem (descem para tras)
    x0 = cx + 10 + k * 26; pts = [(x0 + 50 * t * t + 8 * math.sin(t * 4 + k), cy + 92 + t * 160) for t in np.linspace(0, 1, 40)]
    traco(pts, 1.8, 0.5)
R = im.filter(ImageFilter.GaussianBlur(1.1))
G = im.filter(ImageFilter.GaussianBlur(14))
g = np.asarray(G, np.float32); g = np.clip(g / max(g.max(), 1) * 1.6, 0, 1)
out = np.stack([np.asarray(R, np.float32) / 255, g, np.zeros_like(g)], -1)
Image.fromarray((out * 255).astype(np.uint8), "RGB").save(os.path.join(OUT, "marca_mascara.png"))
print("TEXTURAS_OK", OUT)
