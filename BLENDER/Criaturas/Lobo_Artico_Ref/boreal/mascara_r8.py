"""Mascara de emissao r8 (Python do sistema, com PIL): linhas assadas (assar_linhas_r8.py) afinadas + brilhos antigos do corpo.
r8d: o bake abre a fita em leque na pele (largura vem da projecao, nao da fita) -> afina por erosao 5 px como o r7b.
Uso: python boreal/mascara_r8.py"""
import os, numpy as np
from PIL import Image, ImageFilter
AQUI = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(AQUI, "tex")
raw = Image.open(os.path.join(T, "LoboArtico_Corpo_linhas_raw_r8.png")).convert("L")
lin = np.asarray(raw.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(0.7)).resize((1024, 1024), Image.LANCZOS)).astype(float) / 255
antigo = np.asarray(Image.open(os.path.join(AQUI, "..", "anim_v41", "LoboArtico_Corpo_emissao.png")).convert("L")).astype(float) / 255
import json
from PIL import ImageDraw
SJ = json.load(open(os.path.join(AQUI, "export", "uv_simbolo_r8.json")))
S4 = 4096; esp = Image.new("L", (S4, S4), 0); de = ImageDraw.Draw(esp)
for lado in SJ["lados"].values():                                   # r8l: espiral direto na UV (redonda e nitida na perna)
    pts = [(u * S4, (1 - v) * S4) for u, v in lado["espiral_uv"]]
    for p, q in zip(pts, pts[1:]):
        if abs(p[0] - q[0]) + abs(p[1] - q[1]) < 40: de.line([p, q], fill=255, width=7)
esp = np.asarray(esp.filter(ImageFilter.GaussianBlur(2.0)).resize((1024, 1024), Image.LANCZOS)).astype(float) / 255
lin = np.maximum(lin, np.clip(esp * 1.5, 0, 1) / 1.4)
m = np.clip(np.maximum(np.clip(lin * 1.4, 0, 1), antigo), 0, 1)
Image.fromarray((m * 255).astype(np.uint8)).convert("RGB").save(os.path.join(T, "LoboArtico_Corpo_emissao_gelo_r8.png")); print("MASCARA_R8_OK", round(float((lin > 0.3).mean()), 4))
