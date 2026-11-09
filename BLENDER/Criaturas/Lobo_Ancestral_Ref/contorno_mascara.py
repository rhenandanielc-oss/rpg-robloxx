"""Contorno real da perna dianteira (mascara de mascara_perna.py) linha a linha: bordas, centro e largura por altura e
o desvio de cada borda em relacao a uma reta (curvatura/dobras). Uso: python contorno_mascara.py <prefixo> [<prefixo>...]"""
import sys
import numpy as np
from PIL import Image
ESC = 6.4 / 900
for pre in sys.argv[1:]:
    for v, lim in (("frente", 450), ("lado", 900)):
        im = np.array(Image.open("%s_%s.png" % (pre, v)).convert("RGB")).astype(int); H = im.shape[0]
        b = (im[:, :, 0] > 150) & (im[:, :, 1] > 150) & (im[:, :, 2] > 150)
        zs, e, d = [], [], []
        for y in range(H):
            z = 3.0 + (0.5 - y / H) * 6.4
            if not (0.7 <= z <= 2.8): continue
            cols = np.nonzero(b[y, :lim])[0]
            if len(cols) == 0: continue
            segs = np.split(cols, np.nonzero(np.diff(cols) > 2)[0] + 1); s = max(segs, key=len)
            zs.append(z); e.append(s[0]); d.append(s[-1])
        zs, e, d = map(np.array, (zs, e, d))
        res = []
        for nome, borda in (("borda1", e), ("borda2", d), ("centro", (e + d) / 2)):
            c = np.polyfit(zs, borda, 1); dev = (borda - np.polyval(c, zs)) * ESC
            res.append("%s desvio da reta max %.3f p90 %.3f" % (nome, np.abs(dev).max(), np.percentile(np.abs(dev), 90)))
        larg = (d - e) * ESC
        print("%s %-6s | %s | largura %.2f..%.2f" % (pre.split("/")[-1], v, " | ".join(res), larg.min(), larg.max()))
