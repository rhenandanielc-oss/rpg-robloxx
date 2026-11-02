"""Texturas proprias dos efeitos de FOGO do Dragao das Montanhas (02/11). Geradas por codigo (nada copiado): PNG RGBA
256x256 em ../ia/vfx_fogo_tex/ (servidas pelo servidor local para o upload_image do Studio).
- brasa: risco curto de brasa incandescente (eixo vertical = direcao do movimento com Orientation VelocityParallel)
- poeira: nuvem de poeira/terra irregular (ruido fractal, borda quebrada, granulado)
- onda: arco translucido de ar quente (meia-lua com fios de turbulencia) para a frente de pressao das asas
- lingua: lingua de chama irregular (base larga, ponta fina ondulada), cor branca (a cor vem do emissor)
Uso: python gerar_texturas_fogo.py"""
import os, math
import numpy as np
from PIL import Image, ImageFilter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ia", "vfx_fogo_tex"); os.makedirs(OUT, exist_ok=True)
N = 256
rng = np.random.default_rng(11)
yy, xx = np.mgrid[0:N, 0:N] / (N - 1) * 2 - 1          # -1..1 (y para baixo)

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

# brasa: nucleo quente na cabeca (topo) e cauda que esfria (o emissor colore); risco fino
w = np.exp(-(xx / (0.07 + 0.05 * (1 - yy) / 2)) ** 2)
comp = np.clip(1 - np.abs(yy + 0.1) / 0.85, 0, 1) ** 0.7
cabeca = np.exp(-((yy + 0.55) / 0.22) ** 2) * np.exp(-(xx / 0.12) ** 2)
salvar("brasa", cor(1, 1, 1), np.clip(w * comp * (0.45 + 0.55 * (1 - yy) / 2) + cabeca, 0, 1))

# poeira: ruido com queda radial e borda irregular, granulado fino
r = np.sqrt(xx ** 2 + yy ** 2); n = ruido(6, 3); g = rng.random((N, N))
borda = np.clip((0.95 - r + (n - 0.5) * 0.45) * 3.2, 0, 1)
a = borda * np.clip((1 - r) * 3.5, 0, 1) * (0.35 + 0.65 * n) * (0.85 + 0.15 * g)
salvar("poeira", cor(1, 0.97, 0.92) * (0.8 + 0.2 * n)[..., None], a)

# onda: arco (meia-lua aberta para baixo) com fios de turbulencia ao longo do arco
ang = np.arctan2(yy + 0.6, xx); rr = np.sqrt(xx ** 2 + (yy + 0.6) ** 2)
fios = ruido(5, 6)
arco = np.exp(-((rr - 0.95) / (0.10 + 0.05 * fios)) ** 2) * np.clip(np.sin(ang), 0, 1) ** 1.5
salvar("onda", cor(1, 1, 1), np.clip(arco * (0.4 + 0.6 * fios), 0, 1))

# lingua: forma de chama (base larga embaixo, ponta fina em cima, ondulada), miolo mais denso
t = (1 - yy) / 2                                         # 0 embaixo .. 1 em cima
onda = 0.10 * np.sin(t * 9 + 1.3) * t
larg = 0.55 * (1 - t) ** 0.8 + 0.02
d = np.abs(xx - onda) / larg
n2 = ruido(5, 5)
forma = np.clip((1 - d) * 3, 0, 1) * np.clip((1 - t) * 6, 0, 1) * np.clip(t * 8, 0, 1)
forma *= (0.6 + 0.4 * n2)
miolo = np.clip((1 - d * 1.6), 0, 1) * (1 - t) ** 0.5
salvar("lingua", cor(1, 1, 1), np.clip(forma * 0.85 + miolo * 0.3, 0, 1))
