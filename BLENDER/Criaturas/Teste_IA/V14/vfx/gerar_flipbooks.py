"""Gera flipbooks proprios (sem licenca de terceiros) para os VFX do Dragao das Montanhas.
Cada folha: 8x8 quadros de 128 px (1024x1024 RGBA). O quadro k = estagio de vida da particula (FlipbookMode OneShot):
nasce pequeno e quente (branco-amarelo), cresce turbulento, esfria (laranja -> vermelho) e se desfaz.
Saidas: fogo_8x8.png (cor ja embutida; ParticleEmitter.Color branco), fumaca_8x8.png (cinza neutro, recoloravel),
lava_8x8.png (respingos/pedacos incandescentes). Uso: blender -b --factory-startup -P gerar_flipbooks.py -- <pasta>"""
import sys, os, struct, zlib
import numpy as np

out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else os.path.dirname(os.path.abspath(__file__))
N, Q = 128, 8
rng = np.random.default_rng(7)
GR = rng.random((256, 256, 32)).astype(np.float32)          # grade de valores (x, y, tempo)

def ruido(x, y, z):
    """value noise 3D suave (z em [0,32) periodico)."""
    xi, yi, zi = np.floor(x).astype(int), np.floor(y).astype(int), np.floor(z).astype(int)
    fx, fy, fz = x - xi, y - yi, z - zi
    sx, sy, sz = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy), fz * fz * (3 - 2 * fz)
    def g(a, b, c): return GR[a % 256, b % 256, c % 32]
    r = 0
    for dz, wz in ((0, 1 - sz), (1, sz)):
        c00 = g(xi, yi, zi + dz) * (1 - sx) + g(xi + 1, yi, zi + dz) * sx
        c10 = g(xi, yi + 1, zi + dz) * (1 - sx) + g(xi + 1, yi + 1, zi + dz) * sx
        r = r + (c00 * (1 - sy) + c10 * sy) * wz
    return r

def fbm(x, y, z, oit=5):
    s, a, f, t = 0, 0.5, 1.0, 0
    for _ in range(oit):
        s = s + a * ruido(x * f + 31.7, y * f + 11.3, z * f); t += a; a *= 0.5; f *= 2.03
    return s / t

v, u = np.mgrid[0:N, 0:N].astype(np.float32)
u = (u + 0.5) / N * 2 - 1; v = 1 - (v + 0.5) / N * 2               # v para cima

def ss(a, b, x): x = np.clip((x - a) / (b - a), 0, 1); return x * x * (3 - 2 * x)

RAMPA = np.array([[0.0, 0, 0, 0], [0.18, 0.35, 0.03, 0.01], [0.38, 0.85, 0.18, 0.02], [0.58, 1.0, 0.48, 0.07],
                  [0.78, 1.0, 0.78, 0.30], [1.0, 1.0, 0.97, 0.82]], np.float32)
def cor_fogo(T):
    T = np.clip(T, 0, 1); r = np.interp(T, RAMPA[:, 0], RAMPA[:, 1]); g = np.interp(T, RAMPA[:, 0], RAMPA[:, 2]); b = np.interp(T, RAMPA[:, 0], RAMPA[:, 3])
    return np.stack([r, g, b], -1)

def quadro_fogo(s):
    t = s * 2.4                                                             # evolucao lenta: quadros vizinhos coerentes
    wx = fbm(u * 2.0 + 5, v * 2.0 - t * 1.2, t * 1.3, 3) - 0.5          # distorcao de dominio (turbulencia subindo)
    wy = fbm(u * 2.0 - 9, v * 2.0 - t * 1.2, t * 1.3 + 7, 3) - 0.5
    pu, pv = u + wx * (0.3 + 0.45 * s), v + wy * (0.3 + 0.45 * s)
    R = 0.62 + 0.3 * s
    d = np.sqrt(pu ** 2 + (np.where(pv > 0, pv * 0.82, pv * 1.12) + 0.04) ** 2) / R
    det = fbm(pu * 4.0, pv * 4.0 - t * 2.0, t * 1.8, 5)                   # linguas e fiapos
    dens = np.clip(1.1 - d + (det - 0.5) * (0.85 + 0.8 * s) - s * 0.3, 0, 1)
    T = dens ** 0.85 * (1.18 - 0.72 * s ** 0.9) + (det - 0.5) * 0.18
    a = ss(0.02, 0.32, dens) * (1 - s ** 2.2)
    rgb = cor_fogo(T)
    return np.concatenate([rgb, a[..., None]], -1)

def quadro_fumaca(s):
    t = s * 4.0
    wx = fbm(u * 1.8 + 2, v * 1.8 - t, t * 1.5, 3) - 0.5; wy = fbm(u * 1.8 - 4, v * 1.8 - t, t * 1.5 + 3, 3) - 0.5
    pu, pv = u + wx * 0.6, v + wy * 0.6
    R = 0.45 + 0.45 * s
    d = np.sqrt(pu ** 2 + pv ** 2) / R
    det = fbm(pu * 3.2, pv * 3.2 - t, t * 2.0, 5)
    dens = np.clip(1.05 - d + (det - 0.5) * 1.1, 0, 1)
    sh = 0.55 + 0.45 * np.clip(det + pv * 0.25, 0, 1)                      # sombreado leve (luz de cima)
    a = ss(0.0, 0.5, dens) * (0.85 - 0.6 * s) * ss(0.0, 0.12, s + 0.02)
    rgb = np.stack([sh, sh, sh], -1)
    return np.concatenate([rgb, a[..., None]], -1)

def quadro_lava(s):
    t = s * 3.0
    pu, pv = u + (fbm(u * 3 + 1, v * 3, t, 3) - 0.5) * 0.4, v + (fbm(u * 3 - 6, v * 3, t + 4, 3) - 0.5) * 0.4
    d = np.sqrt(pu ** 2 + pv ** 2) / (0.55 - 0.15 * s)
    det = fbm(pu * 6, pv * 6, 5 + t, 4)
    dens = np.clip(1.2 - d + (det - 0.5) * 0.8, 0, 1)
    crosta = ss(0.45, 0.75, det + s * 0.5)                                 # esfria: crosta escura cresce
    T = (1 - crosta * 0.85) * dens * (1 - 0.5 * s) + 0.08
    rgb = cor_fogo(T) * (1 - crosta[..., None] * 0.8) + crosta[..., None] * np.array([0.09, 0.06, 0.05], np.float32)
    a = ss(0.05, 0.25, dens)
    return np.concatenate([rgb, a[..., None]], -1)

def png(caminho, img):
    h, w, _ = img.shape
    dados = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
    cru = b"".join(b"\x00" + dados[y].tobytes() for y in range(h))
    def ch(t, d): c = t + d; return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    open(caminho, "wb").write(b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + ch(b"IDAT", zlib.compress(cru, 9)) + ch(b"IEND", b""))

def folha(nome, f):
    F = np.zeros((N * Q, N * Q, 4), np.float32)
    for k in range(Q * Q):
        q = f(k / (Q * Q - 1)); r, c = divmod(k, Q)
        F[r * N:(r + 1) * N, c * N:(c + 1) * N] = q
    png(os.path.join(out, nome), F)
    # previa sobre fundo escuro (so para revisao)
    P = F[..., :3] * F[..., 3:] + np.array([0.08, 0.09, 0.11]) * (1 - F[..., 3:])
    png(os.path.join(out, "previa_" + nome), np.concatenate([P, np.ones_like(F[..., :1])], -1))
    print("FOLHA_OK", nome)

os.makedirs(out, exist_ok=True)
folha("fogo_8x8.png", quadro_fogo)
folha("fumaca_8x8.png", quadro_fumaca)
folha("lava_8x8.png", quadro_lava)
