"""Desenha os ossos projetados (JSON de vistas_rig_v9.py) sobre um render, por cadeia e com o nome opcional.
Uso como modulo: desenhar(img_PIL, ossos_da_imagem, nomes=True) ; ou: python ossos_desenho_v9.py <dir> (desenha todos)."""
import sys, os, json, glob
from PIL import Image, ImageDraw
COR = {"Raiz": (255, 255, 255), "Quadril": (255, 220, 0), "Coluna": (255, 200, 0), "Pescoco": (255, 150, 0), "Cabeca": (255, 90, 0),
       "Mandibula": (255, 0, 0), "Palpebra": (255, 0, 200), "Orelha": (200, 100, 255), "Cauda": (0, 220, 255),
       "_E": (0, 230, 90), "_D": (60, 140, 255)}
def cor(n):
    for k in ("Mandibula", "Palpebra", "Orelha", "Cauda", "Raiz", "Quadril", "Coluna", "Pescoco", "Cabeca"):
        if n.startswith(k): return COR[k]
    return COR["_E"] if n.endswith("_E") else COR["_D"]
def desenhar(im, ossos, nomes=True, larg=3, pular=()):
    d = ImageDraw.Draw(im)
    for n, (h, t, _) in ossos.items():
        if n in pular or h[2] <= 0: continue
        c = cor(n); d.line([tuple(h[:2]), tuple(t[:2])], fill=(0, 0, 0), width=larg + 2); d.line([tuple(h[:2]), tuple(t[:2])], fill=c, width=larg)
        r = larg + 1; d.ellipse([h[0] - r, h[1] - r, h[0] + r, h[1] + r], fill=c, outline=(0, 0, 0))
        if nomes:
            mx, my = (h[0] + t[0]) / 2, (h[1] + t[1]) / 2; d.text((mx + 4, my - 5), n, fill=(0, 0, 0)); d.text((mx + 3, my - 6), n, fill=c)
    return im
if __name__ == "__main__":
    dd = sys.argv[1]; os.makedirs(os.path.join(dd, "ossos"), exist_ok=True)
    for js in glob.glob(os.path.join(dd, "ossos_*.json")):
        for nome, ossos in json.load(open(js)).items():
            p = os.path.join(dd, nome + ".png")
            if os.path.exists(p): desenhar(Image.open(p).convert("RGB"), ossos, nomes="nomes" in sys.argv).save(os.path.join(dd, "ossos", nome + ".png"))
    print("OSSOS_DESENHADOS")
