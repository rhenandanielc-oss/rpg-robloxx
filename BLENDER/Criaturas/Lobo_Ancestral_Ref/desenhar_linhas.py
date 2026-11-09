"""Desenha sobre <img> as linhas de ossos salvas em <img>.json por lado_perna.py. Uso: python desenhar_linhas.py <img>"""
import sys, json
from PIL import Image, ImageDraw
im = Image.open(sys.argv[1]).convert("RGB"); d = ImageDraw.Draw(im)
for pts in json.load(open(sys.argv[1] + ".json")).values():
    pts = [tuple(p) for p in pts]; d.line(pts, fill=(255, 60, 60), width=4)
    for x, y in pts: d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(255, 255, 0), width=2)
im.save(sys.argv[1])
