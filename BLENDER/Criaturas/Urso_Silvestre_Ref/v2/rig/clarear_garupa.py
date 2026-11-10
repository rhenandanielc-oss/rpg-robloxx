"""Clareia, na textura de cor do corpo, a face de baixo da garupa/base da cauda (mascara de mascara_garupa.py), com
borda suave. Origem SEMPRE o backup T_Urso_Corpo_Cor_antes_clarear.png (rodar de novo nao acumula).
Uso: python clarear_garupa.py <mascara.json> <ganho> [<saida_mascara.png>]"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np
LOW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "low")
src = Image.open(os.path.join(LOW, "T_Urso_Corpo_Cor_antes_clarear.png")).convert("RGB"); W, H = src.size
d = json.load(open(sys.argv[1])); g = float(sys.argv[2])
m = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(m)
for t in d["tris"]:
    dr.polygon([(u * W, (1 - v) * H) for u, v in t[:3]], fill=255)
m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(4))     # cobre a margem da costura e suaviza
if len(sys.argv) > 3: m.save(sys.argv[3])
a = np.asarray(src).astype(np.float32) / 255; k = (np.asarray(m).astype(np.float32) / 255)[..., None]
quente = np.array([1.0, 1.0, 1.0], np.float32)                                    # mesmo matiz (so brilho)
out = a * (1 + (g - 1) * k * quente)
lum = out.mean(axis=2, keepdims=True); out = out + (lum - out) * 0.2 * k            # tira um pouco da saturacao (evita mancha alaranjada)
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(LOW, "T_Urso_Corpo_Cor.png"))
area = float((np.asarray(m) > 127).mean()); print("CLAREAR_OK ganho", g, "area_mascara %.4f" % area,
      "brilho_regiao antes %.3f depois %.3f" % (a[k[..., 0] > 0.5].mean(), np.clip(out, 0, 1)[k[..., 0] > 0.5].mean()))
