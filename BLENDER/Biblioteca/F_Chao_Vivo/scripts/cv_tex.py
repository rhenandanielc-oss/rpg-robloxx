import bpy, math, random
import numpy as np

TEXDIR = r"C:\Users\Rhenan\Downloads\RPG_Roblox_GitHub_Pacote_Inicial\BLENDER\Biblioteca\Texturas"

def blank(w, h):
    return np.zeros((h, w, 4), np.float32)

def _inside(px, py, pts):
    n = len(pts)
    res = np.zeros(px.shape, bool)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        cond = ((yi > py) != (yj > py)) & (px < (xj - xi) * (py - yi) / (yj - yi + 1e-12) + xi)
        res ^= cond
        j = i
    return res

def fill_poly(img, pts, color, alpha=1.0):
    h, w = img.shape[:2]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0 = max(0, int(math.floor(min(xs))) - 1)
    x1 = min(w, int(math.ceil(max(xs))) + 2)
    y0 = max(0, int(math.floor(min(ys))) - 1)
    y1 = min(h, int(math.ceil(max(ys))) + 2)
    if x1 <= x0 or y1 <= y0:
        return
    gy, gx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    cov = np.zeros(gx.shape, np.float32)
    offs = (0.17, 0.5, 0.83)
    for ox in offs:
        for oy in offs:
            cov += _inside(gx + ox, gy + oy, pts)
    cov /= 9.0
    cov *= alpha
    if callable(color):
        rgb = color(gx, gy)
    else:
        rgb = np.array(color[:3], np.float32)[None, None, :]
    reg = img[y0:y1, x0:x1]
    a = cov[..., None]
    da = reg[..., 3:4]
    oa = a + da * (1 - a)
    reg[..., :3] = (rgb * a + reg[..., :3] * da * (1 - a)) / np.maximum(oa, 1e-6)
    reg[..., 3:4] = oa

def leaf_pts(cx, cy, L, W, ang, n=14, power=0.7, bulge=0.5):
    pts = []
    for i in range(n + 1):
        t = i / n
        wd = W / 2 * (math.sin(math.pi * (t ** (0.6 + bulge * 0.4))) ** power)
        pts.append((t * L, wd))
    for i in range(n, -1, -1):
        t = i / n
        wd = W / 2 * (math.sin(math.pi * (t ** (0.6 + bulge * 0.4))) ** power)
        pts.append((t * L, -wd))
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]

def circle_pts(cx, cy, r, n=28):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]

def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))

def grad_v(c0, c1, y0, y1):
    def f(gx, gy):
        t = np.clip((gy - y0) / (y1 - y0 + 1e-6), 0, 1)[..., None]
        return np.array(c0, np.float32) * (1 - t) + np.array(c1, np.float32) * t
    return f

def dilate_rgb(img, iters=8):
    # espalha RGB dos pixels opacos para os transparentes (evita franja escura)
    a = img[..., 3]
    rgb = img[..., :3].copy()
    known = a > 0.02
    for _ in range(iters):
        acc = np.zeros_like(rgb)
        cnt = np.zeros(a.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k = np.roll(known, (dy, dx), (0, 1))
            r = np.roll(rgb, (dy, dx), (0, 1))
            acc += r * k[..., None]
            cnt += k
        newk = (~known) & (cnt > 0)
        rgb[newk] = acc[newk] / cnt[newk][..., None]
        known = known | newk
    img[..., :3] = rgb

def save_png(img, name):
    h, w = img.shape[:2]
    dilate_rgb(img)
    im = bpy.data.images.get(name)
    if im:
        bpy.data.images.remove(im)
    im = bpy.data.images.new(name, w, h, alpha=True)
    im.pixels = img.ravel().tolist()
    im.alpha_mode = 'STRAIGHT'
    path = TEXDIR + "\\" + name + ".png"
    im.filepath_raw = path
    im.file_format = 'PNG'
    im.save()
    return im

# ---------------- atlas de flores e cogumelos (1024x512) ----------------
def make_flores():
    rnd = random.Random(11)
    img = blank(1024, 512)
    def cell(i, j):
        return i * 256, 256 + j * 0  # (ox, oy) linha de cima = flores (oy=256), embaixo = cogumelos (oy=0)
    # linha de cima (flores): oy=256
    # 0 margarida branca
    ox, oy = 0, 256
    cx, cy = ox + 128, oy + 128
    for k in range(14):
        a = k / 14 * 2 * math.pi
        col = lerp((0.93, 0.93, 0.9), (1.0, 1.0, 1.0), rnd.random())
        fill_poly(img, leaf_pts(cx + math.cos(a) * 12, cy + math.sin(a) * 12, 100, 28, a, power=0.8), col)
    fill_poly(img, circle_pts(cx, cy, 24), (0.95, 0.75, 0.12))
    fill_poly(img, circle_pts(cx, cy, 14), (0.85, 0.55, 0.05))
    # 1 botao-de-ouro amarelo
    ox = 256
    cx, cy = ox + 128, oy + 128
    for k in range(5):
        a = k / 5 * 2 * math.pi + 0.3
        fill_poly(img, leaf_pts(cx + math.cos(a) * 6, cy + math.sin(a) * 6, 98, 78, a, power=0.55), (0.98, 0.82, 0.1))
        fill_poly(img, leaf_pts(cx + math.cos(a) * 6, cy + math.sin(a) * 6, 70, 40, a, power=0.55), (1.0, 0.9, 0.3))
    fill_poly(img, circle_pts(cx, cy, 12), (0.8, 0.55, 0.05))
    # 2 flor roxa (estrela)
    ox = 512
    cx, cy = ox + 128, oy + 128
    for k in range(6):
        a = k / 6 * 2 * math.pi
        fill_poly(img, leaf_pts(cx, cy, 104, 46, a, power=0.7), lerp((0.45, 0.25, 0.75), (0.6, 0.4, 0.9), rnd.random()))
        fill_poly(img, leaf_pts(cx, cy, 60, 14, a, power=0.7), (0.3, 0.12, 0.5))
    fill_poly(img, circle_pts(cx, cy, 14), (0.98, 0.92, 0.5))
    # 3 papoula vermelha
    ox = 768
    cx, cy = ox + 128, oy + 128
    for k in range(4):
        a = k / 4 * 2 * math.pi + 0.5
        fill_poly(img, leaf_pts(cx + math.cos(a) * 4, cy + math.sin(a) * 4, 98, 100, a, power=0.5), lerp((0.8, 0.1, 0.08), (0.95, 0.2, 0.12), rnd.random()))
        fill_poly(img, leaf_pts(cx, cy, 55, 38, a, power=0.5), (0.6, 0.05, 0.05))
    fill_poly(img, circle_pts(cx, cy, 20), (0.12, 0.08, 0.1))
    # linha de baixo: cogumelos (chapeu planar, topo visto de cima)
    caps = [((0.46, 0.29, 0.17), (0.7, 0.55, 0.38), False),   # marrom
            ((0.82, 0.3, 0.14), (0.98, 0.95, 0.9), True),      # laranja com pintas brancas
            ((0.78, 0.66, 0.46), (0.55, 0.42, 0.25), True)]   # bege com pintas escuras
    for i, (base, spot, spots) in enumerate(caps):
        ox = i * 256
        oy2 = 0
        cx, cy = ox + 128, oy2 + 128
        def rad(gx, gy, cx=cx, cy=cy, base=base):
            r = np.sqrt((gx - cx) ** 2 + (gy - cy) ** 2) / 128.0
            t = np.clip(r, 0, 1)[..., None]
            return np.array(base, np.float32) * (1.15 - 0.45 * t)
        fill_poly(img, circle_pts(cx, cy, 126, 48), rad)
        for s in range(14 if spots else 6):
            a = rnd.random() * 2 * math.pi
            d = rnd.random() * 90
            fill_poly(img, circle_pts(cx + math.cos(a) * d, cy + math.sin(a) * d, rnd.uniform(5, 12)), spot, 0.9 if spots else 0.35)
    # celula 3 baixo: caule creme (esquerda) e verde de folha (direita)
    ox = 768
    fill_poly(img, [(ox + 4, 4), (ox + 124, 4), (ox + 124, 252), (ox + 4, 252)], grad_v((0.86, 0.8, 0.66), (0.95, 0.92, 0.82), 0, 252))
    fill_poly(img, [(ox + 132, 4), (ox + 252, 4), (ox + 252, 252), (ox + 132, 252)], grad_v((0.13, 0.32, 0.1), (0.3, 0.5, 0.18), 0, 252))
    return save_png(img, "ChaoVivo_Flores")

# ---------------- atlas de solo (1024x1024) ----------------
def make_solo():
    rnd = random.Random(23)
    img = blank(1024, 1024)
    # Q1 (0..512,0..512): tufo de capim alto (base embaixo ao centro)
    ox, oy = 0, 0
    greens = [(0.16, 0.34, 0.08), (0.22, 0.45, 0.1), (0.3, 0.55, 0.14), (0.38, 0.55, 0.2), (0.45, 0.5, 0.2)]
    for k in range(26):
        bx = ox + 256 + rnd.uniform(-80, 80)
        hgt = rnd.uniform(300, 480)
        lean = rnd.uniform(-90, 90)
        wb = rnd.uniform(12, 22)
        n = 12
        left, right = [], []
        for i in range(n + 1):
            t = i / n
            x = bx + lean * t * t
            y = oy + 6 + hgt * t
            wd = wb * (1 - t) ** 0.9 + 0.8
            left.append((x - wd, y))
            right.append((x + wd, y))
        col = greens[rnd.randrange(len(greens))]
        top = lerp(col, (0.6, 0.65, 0.3), 0.35)
        fill_poly(img, left + right[::-1], grad_v(col, top, oy, oy + 500))
    for k in range(5):
        bx = ox + 256 + rnd.uniform(-70, 70)
        hgt = rnd.uniform(330, 440)
        lean = rnd.uniform(-60, 60)
        fill_poly(img, [(bx - 1.5, oy + 6), (bx + 1.5, oy + 6), (bx + lean + 1.5, oy + hgt), (bx + lean - 1.5, oy + hgt)], (0.4, 0.45, 0.2))
        fill_poly(img, leaf_pts(bx + lean, oy + hgt, 46, 14, math.pi / 2 + lean * 0.002, power=0.8), (0.72, 0.6, 0.3))
    # Q2 (512..1024, 0..512): trevo
    ox, oy = 512, 0
    placed = []
    for k in range(70):
        a = rnd.random() * 2 * math.pi
        d = math.sqrt(rnd.random()) * 225
        x, y = ox + 256 + math.cos(a) * d, oy + 256 + math.sin(a) * d
        if any((x - px) ** 2 + (y - py) ** 2 < 34 ** 2 for px, py in placed):
            continue
        placed.append((x, y))
        rot = rnd.random() * 2 * math.pi
        col = lerp((0.15, 0.4, 0.1), (0.3, 0.58, 0.2), rnd.random())
        for q in range(3):
            aa = rot + q * 2 * math.pi / 3
            fill_poly(img, circle_pts(x + math.cos(aa) * 13, y + math.sin(aa) * 13, 13, 16), col)
            fill_poly(img, leaf_pts(x + math.cos(aa) * 3, y + math.sin(aa) * 3, 18, 3, aa, power=1.0), lerp(col, (0.85, 0.95, 0.8), 0.45), 0.7)
    for k in range(9):
        a = rnd.random() * 2 * math.pi
        d = math.sqrt(rnd.random()) * 200
        x, y = ox + 256 + math.cos(a) * d, oy + 256 + math.sin(a) * d
        fill_poly(img, circle_pts(x, y, 11, 14), (0.97, 0.96, 0.92))
        fill_poly(img, circle_pts(x, y, 4, 8), (0.95, 0.85, 0.4))
    # Q3 (0..512, 512..1024): serapilheira (folhas caidas)
    ox, oy = 0, 512
    pal = [(0.42, 0.26, 0.12), (0.55, 0.36, 0.14), (0.62, 0.45, 0.16), (0.36, 0.3, 0.12), (0.47, 0.19, 0.1), (0.5, 0.48, 0.18), (0.28, 0.22, 0.1)]
    for k in range(95):
        a = rnd.random() * 2 * math.pi
        d = math.sqrt(rnd.random()) * 230
        x, y = ox + 256 + math.cos(a) * d, oy + 256 + math.sin(a) * d
        L = rnd.uniform(46, 90)
        W = L * rnd.uniform(0.38, 0.55)
        ang = rnd.random() * 2 * math.pi
        col = pal[rnd.randrange(len(pal))]
        col = lerp(col, (col[0] * 0.8, col[1] * 0.8, col[2] * 0.8), rnd.random() * 0.5)
        fill_poly(img, leaf_pts(x, y, L, W, ang), col)
        fill_poly(img, leaf_pts(x + math.cos(ang) * 2, y + math.sin(ang) * 2, L * 0.95, 2.2, ang, power=1.0), lerp(col, (0.2, 0.12, 0.05), 0.5), 0.8)
    for k in range(10):
        a = rnd.random() * 2 * math.pi
        d = math.sqrt(rnd.random()) * 215
        x, y = ox + 256 + math.cos(a) * d, oy + 256 + math.sin(a) * d
        ang = rnd.random() * 2 * math.pi
        fill_poly(img, leaf_pts(x, y, rnd.uniform(60, 110), 5, ang, power=1.0), (0.3, 0.2, 0.1))
    # Q4 (512..1024, 512..1024): musgo
    ox, oy = 512, 512
    N = 64
    base = np.random.RandomState(5).rand(N // 4 + 1, N // 4 + 1)
    # ruido suave por interpolacao bilinear
    def noise2(w, h, freq, seed):
        r = np.random.RandomState(seed).rand(freq + 2, freq + 2).astype(np.float32)
        ys = np.linspace(0, freq, h, dtype=np.float32)
        xs = np.linspace(0, freq, w, dtype=np.float32)
        yi = ys.astype(int)
        xi = xs.astype(int)
        yf = (ys - yi)[:, None]
        xf = (xs - xi)[None, :]
        a = r[yi][:, xi]
        b = r[yi][:, xi + 1]
        c = r[yi + 1][:, xi]
        d = r[yi + 1][:, xi + 1]
        return a * (1 - xf) * (1 - yf) + b * xf * (1 - yf) + c * (1 - xf) * yf + d * xf * yf
    n1 = noise2(512, 512, 6, 1) * 0.6 + noise2(512, 512, 18, 2) * 0.3 + noise2(512, 512, 50, 3) * 0.1
    yy, xx = np.mgrid[0:512, 0:512].astype(np.float32)
    rr = np.sqrt((xx - 256) ** 2 + (yy - 256) ** 2) / 250.0
    mask = np.clip((0.82 - rr + (n1 - 0.5) * 0.9) * 5.0, 0, 1)
    col = np.zeros((512, 512, 3), np.float32)
    t = noise2(512, 512, 30, 4)[..., None]
    col[:] = np.array((0.14, 0.33, 0.1), np.float32) * (1 - t) + np.array((0.32, 0.52, 0.18), np.float32) * t
    fine = noise2(512, 512, 120, 7)[..., None]
    col *= (0.8 + 0.4 * fine)
    img[oy:oy + 512, ox:ox + 512, :3] = np.clip(col, 0, 1)
    img[oy:oy + 512, ox:ox + 512, 3] = mask
    return save_png(img, "ChaoVivo_Solo")
