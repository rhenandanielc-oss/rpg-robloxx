"""Gera as texturas dos cartoes do CR_UrsoSilvestre (1024x1024, sRGB, com alfa) e os mapas normais:
  T_Urso_Pelo_Cor.png / T_Urso_Pelo_Normal.png  — atlas 4 colunas (formas de mecha) x 3 linhas (tons: escuro, medio, claro)
  T_Urso_Veg_Cor.png  / T_Urso_Veg_Normal.png   — samambaia (2), folha larga, raminho, musgo, casca
Layout em UV (v = 0 embaixo) documentado em ATLAS abaixo; pelo_urso.py usa os mesmos numeros.
Uso: python texturas_urso.py <saida_dir>"""
import sys, os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.abspath(sys.argv[1]); os.makedirs(OUT, exist_ok=True)
R = 1024; SS = 2                                     # supersample
rnd = random.Random(7)
ATLAS = {"pelo": {"colunas": 4, "linhas": 3},
         "veg": {"samambaia": [(0.0, 0.0, 0.25, 1.0), (0.25, 0.0, 0.5, 1.0)], "folha": (0.5, 0.5, 0.75, 1.0),
                 "raminho": (0.75, 0.5, 1.0, 1.0), "musgo": (0.5, 0.25, 1.0, 0.5), "casca": (0.5, 0.0, 1.0, 0.25)}}

def uv_px(u0, v0, u1, v1, S):
    """retangulo UV -> caixa em pixels (PIL, y para baixo)"""
    return int(u0 * S), int((1 - v1) * S), int(u1 * S), int((1 - v0) * S)
def normal_de_altura(h, forca):
    gy, gx = np.gradient(h.astype(np.float32))
    n = np.dstack((-gx * forca, gy * forca, np.ones_like(h, dtype=np.float32)))
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8), "RGB")
def mistura(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def bez(p0, p1, p2, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])

# ================================================================== PELO
S = R * SS; cor = Image.new("RGBA", (S, S), (0, 0, 0, 0)); alt = Image.new("L", (S, S), 0)
dc, da = ImageDraw.Draw(cor), ImageDraw.Draw(alt)
TONS = [(40, 24, 13), (80, 48, 25), (116, 76, 40)]          # escuro, medio, claro (sRGB)
PONTA = [(78, 52, 30), (128, 86, 46), (168, 118, 62)]
NC, NL = 4, 3
for lin in range(NL):
    for colu in range(NC):
        x0, y0, x1, y1 = uv_px(colu / NC, lin / NL, (colu + 1) / NC, (lin + 1) / NL, S)
        w, h = x1 - x0, y1 - y0
        n_pontas = (1, 2, 3, 1)[colu]
        pontas = [(x0 + w * (0.5 + (k - (n_pontas - 1) / 2) * 0.24 + rnd.uniform(-0.04, 0.04)), y0 + h * rnd.uniform(0.03, 0.10))
                  for k in range(n_pontas)]
        curva = (0.0, 0.0, 0.0, 0.18)[colu]
        # massa da mecha: silhueta solida (raiz larga -> pontas), as fibras vao por cima
        contorno = [(x0 + w * 0.10, y1)]
        for k, pt in enumerate(sorted(pontas)):
            contorno.append((pt[0] - w * 0.10 + w * curva * 0.5, pt[1] + h * 0.30)); contorno.append((pt[0], pt[1] + h * 0.04))
            contorno.append((pt[0] + w * 0.09 + w * curva * 0.5, pt[1] + h * 0.30))
            if k < len(pontas) - 1:
                contorno.append(((pt[0] + sorted(pontas)[k + 1][0]) / 2 + w * curva * 0.4, pt[1] + h * 0.42))
        contorno.append((x0 + w * 0.90, y1))
        corpo_c = mistura(TONS[lin], (0, 0, 0), 0.25)
        dc.polygon(contorno, fill=corpo_c + (255,)); da.polygon(contorno, fill=110)
        for _ in range(260):
            xr = x0 + w * rnd.uniform(0.10, 0.90); yr = y1 - h * rnd.uniform(0.0, 0.05)
            pt = rnd.choice(pontas); comp = rnd.uniform(0.55, 1.0)
            fim = (lerp_x := xr + (pt[0] - xr) * comp + rnd.uniform(-0.03, 0.03) * w, yr + (pt[1] - yr) * comp)
            meio = ((xr + fim[0]) / 2 + w * (curva + rnd.uniform(-0.06, 0.06)), (yr + fim[1]) / 2)
            base_c = mistura(TONS[lin], (0, 0, 0), rnd.uniform(0.0, 0.35)) if rnd.random() < 0.6 else mistura(TONS[lin], PONTA[lin], rnd.uniform(0.0, 0.3))
            larg0 = rnd.uniform(2.0, 5.0) * SS; N = 14
            for i in range(N):
                t0, t1 = i / N, (i + 1) / N
                a, b = bez((xr, yr), meio, fim, t0), bez((xr, yr), meio, fim, t1)
                tt = (t0 + t1) / 2
                c = mistura(mistura(base_c, (0, 0, 0), 0.45 * (1 - tt) ** 3), PONTA[lin], 0.55 * tt ** 2)
                lw = max(1, int(larg0 * (1 - tt) ** 0.8))
                dc.line([a, b], fill=c + (255,), width=lw)
                da.line([a, b], fill=int(120 + 120 * (1 - abs(0.5 - (i % 3) / 2))), width=max(1, lw // 2))
cor = cor.resize((R, R), Image.LANCZOS); alt = alt.resize((R, R), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
arr = np.array(cor).astype(np.float32); th = R / NL
for lin in range(NL):
    y_raiz = R - lin * th                                     # linha de baixo do tile (raiz)
    for x in range(R):
        alc = th * (0.10 + 0.07 * math.sin(x * 0.21) * math.sin(x * 0.047) + 0.03 * rnd.random())
        y0_ = int(y_raiz - alc); y1_ = int(y_raiz)
        if y1_ > y0_:
            rampa_ = np.linspace(1.0, 0.0, y1_ - y0_) ** 1.5
            arr[y0_:y1_, x, 3] *= rampa_[: arr[y0_:y1_, x, 3].shape[0]]
cor = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
cor.save(os.path.join(OUT, "T_Urso_Pelo_Cor.png")); normal_de_altura(np.array(alt) / 255.0, 6.0).save(os.path.join(OUT, "T_Urso_Pelo_Normal.png"))

# ================================================================== VEGETACAO
cor = Image.new("RGBA", (S, S), (0, 0, 0, 0)); alt = Image.new("L", (S, S), 0)
dc, da = ImageDraw.Draw(cor), ImageDraw.Draw(alt)
VERDE_E, VERDE, VERDE_C = (42, 78, 22), (78, 128, 34), (150, 178, 60)
def folheto(cx, cy, ang, comp, larg, cor_, serrilha=0):
    """folha ovada pontuda: poligono com borda opcional serrilhada"""
    pts = []
    for i in range(41):
        t = i / 40; lado = 1 if i <= 20 else -1; tt = t * 2 if i <= 20 else (1 - t) * 2
        r = larg * math.sin(math.pi * tt) ** 0.8 * (1 - 0.35 * tt)
        if serrilha: r *= 1 - 0.18 * (0.5 + 0.5 * math.sin(tt * math.pi * serrilha))
        px = tt * comp; py = lado * r
        pts.append((cx + px * math.cos(ang) - py * math.sin(ang), cy + px * math.sin(ang) + py * math.cos(ang)))
    dc.polygon(pts, fill=cor_ + (255,)); da.polygon(pts, fill=150)
    dc.line([(cx, cy), (cx + comp * 0.95 * math.cos(ang), cy + comp * 0.95 * math.sin(ang))], fill=mistura(cor_, VERDE_C, 0.4) + (255,), width=max(1, int(larg * 0.12)))
    da.line([(cx, cy), (cx + comp * math.cos(ang), cy + comp * math.sin(ang))], fill=210, width=max(1, int(larg * 0.12)))
# samambaias: raque da base (baixo) a ponta (cima), pinas em pares que diminuem para a ponta
for k, (u0, v0, u1, v1) in enumerate(ATLAS["veg"]["samambaia"]):
    x0, y0, x1, y1 = uv_px(u0, v0, u1, v1, S); w, h = x1 - x0, y1 - y0
    base, topo = (x0 + w * 0.5, y1 - h * 0.01), (x0 + w * (0.5 + (0.08 if k else -0.06)), y0 + h * 0.02)
    meio = (x0 + w * (0.5 + (-0.06 if k else 0.07)), (y0 + y1) / 2)
    raque = [bez(base, meio, topo, i / 60) for i in range(61)]
    for i in range(60):
        dc.line([raque[i], raque[i + 1]], fill=(70, 92, 30, 255), width=int(5 * SS * (1 - i / 70)))
    NP = 26
    for j in range(2, NP + 1):
        t = j / NP * 0.97; i = int(t * 60); p = raque[i]; q = raque[min(60, i + 1)]
        ang_r = math.atan2(q[1] - p[1], q[0] - p[0])
        comp = w * 0.46 * math.sin(math.pi * min(1.0, 0.25 + t * 0.95)) ** 0.7 * (1 - 0.55 * t)
        for lado in (1, -1):
            a = ang_r + lado * math.radians(62 - 15 * t)
            c = mistura(VERDE if rnd.random() < 0.6 else VERDE_E, VERDE_C, rnd.uniform(0.0, 0.35) + 0.2 * t)
            # pina: eixo + pinulas
            fim = (p[0] + comp * math.cos(a), p[1] + comp * math.sin(a))
            dc.line([p, fim], fill=c + (255,), width=max(1, int(2 * SS)))
            NPin = max(4, int(comp / (5.5 * SS)))
            for m in range(NPin):
                tm = (m + 0.5) / NPin; pm = (p[0] + (fim[0] - p[0]) * tm, p[1] + (fim[1] - p[1]) * tm)
                cpin = comp * 0.26 * (1 - 0.7 * tm)
                for lado2 in (1, -1):
                    folheto(pm[0], pm[1], a + lado2 * math.radians(70), cpin, cpin * 0.45, mistura(c, VERDE_E, rnd.uniform(0, 0.3)))
# folha larga
x0, y0, x1, y1 = uv_px(*ATLAS["veg"]["folha"], S); w, h = x1 - x0, y1 - y0
folheto(x0 + w * 0.5, y1 - h * 0.04, -math.pi / 2, h * 0.92, w * 0.36, VERDE)
for i in range(1, 9):                                                        # nervuras
    t = i / 9; cx, cy = x0 + w * 0.5, y1 - h * 0.04 - h * 0.92 * t
    for lado in (1, -1):
        dc.line([(cx, cy), (cx + lado * w * 0.28 * math.sin(math.pi * t) , cy - h * 0.06)], fill=mistura(VERDE, VERDE_C, 0.5) + (255,), width=SS * 2)
        da.line([(cx, cy), (cx + lado * w * 0.28 * math.sin(math.pi * t), cy - h * 0.06)], fill=200, width=SS * 2)
# raminho com 3 folhas
x0, y0, x1, y1 = uv_px(*ATLAS["veg"]["raminho"], S); w, h = x1 - x0, y1 - y0
dc.line([(x0 + w * 0.5, y1), (x0 + w * 0.5, y0 + h * 0.35)], fill=(70, 60, 30, 255), width=4 * SS)
for (fx, fy, a) in ((0.5, 0.40, -90), (0.5, 0.62, -35), (0.5, 0.62, -145), (0.5, 0.82, -50), (0.5, 0.82, -130)):
    folheto(x0 + w * fx, y0 + h * fy, math.radians(a), h * 0.36, w * 0.17, mistura(VERDE, VERDE_C, rnd.uniform(0, 0.3)))
# musgo: 4 tufos redondos irregulares (franja em toda a volta)
x0, y0, x1, y1 = uv_px(*ATLAS["veg"]["musgo"], S); w, h = x1 - x0, y1 - y0
for k in range(4):
    cx, cy = x0 + w * (k + 0.5) / 4, y0 + h * 0.5; rx, ry = w / 8 * 0.92, h * 0.46
    for _ in range(1700):
        ang = rnd.uniform(0, 6.283); rr = rnd.random() ** 0.6 * (0.80 + 0.2 * math.sin(ang * 5 + k))
        x, y = cx + math.cos(ang) * rx * rr, cy + math.sin(ang) * ry * rr
        r = rnd.uniform(2.0, 5.5) * SS * (1.1 - 0.5 * rr)
        c = mistura(mistura((92, 112, 30), (40, 58, 16), rnd.random() * 0.8 * (0.4 + rr)), (150, 160, 56), rnd.random() * 0.25 * (1 - rr))
        dc.ellipse((x - r, y - r, x + r, y + r), fill=c + (255,)); da.ellipse((x - r, y - r, x + r, y + r), fill=int(rnd.randint(90, 230) * (1 - 0.5 * rr)))
# casca: fissuras verticais + liquen
x0, y0, x1, y1 = uv_px(*ATLAS["veg"]["casca"], S); w, h = x1 - x0, y1 - y0
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
rng = np.random.default_rng(3)
def ruido(fx, fy, oct=4):
    acc = np.zeros((h, w), np.float32); amp = 1.0
    for o in range(oct):
        g = rng.standard_normal((int(fy * 2 ** o) + 2, int(fx * 2 ** o) + 2)).astype(np.float32)
        im = Image.fromarray(g).resize((w, h), Image.BICUBIC); acc += np.array(im) * amp; amp *= 0.5
    return (acc - acc.min()) / (acc.max() - acc.min())
warp = ruido(4, 2, 3); placas = ruido(10, 2, 3); liq = ruido(8, 4, 3); fino = ruido(40, 6, 2)
fase = xx / w * 60 + warp * 6.0                                  # muitas fibras finas                                   # fibras verticais longas e onduladas
crista = 0.5 + 0.5 * np.sin(2 * np.pi * fase)
quebra = (np.sin(2 * np.pi * (yy / h * 3 + warp * 1.5)) > 0.93) & (crista < 0.55)   # quebras horizontais raras
fiss = np.clip((crista - 0.10) * 4.0, 0, 1) * (1 - quebra * 0.8) * (0.75 + 0.25 * fino)   # fissura = linha escura fina
base = np.array((112, 94, 72), np.float32) * (0.72 + 0.40 * placas[..., None]) * (0.85 + 0.25 * crista[..., None])
escuro = np.array((30, 23, 17), np.float32)
rgb = escuro + (base - escuro) * fiss[..., None]
lm = np.clip((liq - 0.66) * 5, 0, 1)[..., None] * np.clip(fiss, 0, 1)[..., None]
rgb = rgb * (1 - lm) + np.array((104, 124, 52), np.float32) * lm
cas = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB").convert("RGBA"); cor.paste(cas, (x0, y0))
alt.paste(Image.fromarray((np.clip(fiss * 0.8 + crista * 0.2, 0, 1) * 255).astype(np.uint8), "L"), (x0, y0))
cor = cor.resize((R, R), Image.LANCZOS); alt = alt.resize((R, R), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
# sangra a cor para dentro do alfa zero (evita borda preta no mipmap)
arr = np.array(cor); rgbb = Image.fromarray(arr[..., :3]).filter(ImageFilter.MaxFilter(5)); a = arr[..., 3:4] / 255.0
arr[..., :3] = (arr[..., :3] * a + np.array(rgbb) * (1 - a)).astype(np.uint8)
Image.fromarray(arr, "RGBA").save(os.path.join(OUT, "T_Urso_Veg_Cor.png"))
normal_de_altura(np.array(alt) / 255.0, 5.0).save(os.path.join(OUT, "T_Urso_Veg_Normal.png"))
print("TEXTURAS_OK", OUT)
