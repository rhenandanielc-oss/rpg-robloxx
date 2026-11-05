"""Corrige o albedo por ZONA (juba/tufo x corpo) com ganhos por canal em luz linear (multiplicador fisico do albedo),
calculados pela razao referencia/render das cores medias das regioes do perfil (mesma luz neutra). Mascara de zona
rasterizada na UV a partir de meshy/zonas_uv.npz e suavizada na borda.
Uso: python 13_ganhos_albedo.py <textura_atual.png> <metricas.json> <zonas.npz> <saida.png>"""
import sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
tex, metr, zon, out = sys.argv[1:5]
c = json.load(open(metr, encoding="utf-8"))["cores"]
lin = lambda v: (np.asarray(v, float) / 255) ** 2.2
GRUPOS = {1: ["juba topo (dourado)", "juba media (laranja)", "juba baixa/tras (cobre)", "juba peito (pontas)", "tufo"],
          0: ["flanco", "ventre", "coxa", "focinho"]}
g = {}
for zn, regs in GRUPOS.items():
    r = np.array([lin(c[k]["ref"]) / np.maximum(lin(c[k]["e2"]), 1e-4) for k in regs])
    g[zn] = np.clip(np.exp(np.log(r).mean(0)), 0.3, 3.0)        # media geometrica das razoes por canal
    if zn == 0: g[zn] = np.clip(g[zn], 0.75, 1.35)              # corpo: limite para nao estourar patas/ventre claros
print("GANHOS juba", g[1].round(3), "corpo", g[0].round(3))
im = np.asarray(Image.open(tex).convert("RGB")).astype(np.float32) / 255; H, W = im.shape[:2]
d = np.load(zon); m = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(m)
for t, z in zip(d["tri"], d["zona"]):
    if z: dr.polygon([(u * W, (1 - v) * H) for u, v in t], fill=255)
m = np.asarray(m.filter(ImageFilter.GaussianBlur(6))).astype(np.float32)[..., None] / 255
Image.fromarray((m[..., 0] * 255).astype(np.uint8)).save(out.replace(".png", "_zona.png"))
L = im ** 2.2
lum = (L * np.array([0.2126, 0.7152, 0.0722], np.float32)).sum(-1, keepdims=True)
cla = np.clip((lum - 0.30) / 0.35, 0, 1); cla = cla * cla * (3 - 2 * cla)          # 0 = tons medios/escuros, 1 = claros
g0 = 1 + (g[0] - 1) * (1 - cla)                                                     # corpo: ganho so nos medios/escuros
creme = np.array([1.0, 0.93, 0.82], np.float32)                                     # claros do corpo -> creme quente
Lc = L * g0 * (1 - cla * 0.15) * (1 - cla + cla * creme)
L = m * (L * g[1]) + (1 - m) * Lc
Image.fromarray((np.clip(L, 0, 1) ** (1 / 2.2) * 255 + 0.5).astype(np.uint8)).save(out)
json.dump({"juba": g[1].tolist(), "corpo": g[0].tolist()}, open(out.replace(".png", "_ganhos.json"), "w")); print("ALBEDO_OK", out)
