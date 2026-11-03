"""Monta folhas com as tiras de quadros por clipe. Uso: python tiras.py <dir_render> <saida.png> [clipes]"""
import sys, os, glob
from PIL import Image, ImageDraw
d, saida = sys.argv[1], sys.argv[2]; quais = sys.argv[3].split(",") if len(sys.argv) > 3 else None
nomes = sorted({os.path.basename(p).rsplit("_", 1)[0] for p in glob.glob(os.path.join(d, "tira", "*.png"))})
if quais: nomes = [n for n in quais if n in nomes]
W, H = 280, 190; cols = max(len(glob.glob(os.path.join(d, "tira", nomes[0] + "_*.png"))), 1)
o = Image.new("RGB", (120 + W * cols, H * len(nomes)), (20, 20, 20)); dr = ImageDraw.Draw(o)
for j, n in enumerate(nomes):
    dr.text((6, j * H + H // 2), n, fill=(255, 255, 255))
    for i, p in enumerate(sorted(glob.glob(os.path.join(d, "tira", n + "_*.png")))):
        o.paste(Image.open(p).convert("RGB").resize((W, H)), (120 + i * W, j * H))
o.save(saida); print("TIRAS", saida, o.size)
