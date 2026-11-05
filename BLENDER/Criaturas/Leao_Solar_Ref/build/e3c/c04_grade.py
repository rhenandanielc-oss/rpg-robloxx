"""Grade de revisao: linhas = poses, colunas = vistas. Uso: python c04_grade.py <dir> <graus,...> <vistas,...> <saida> [lado]"""
import sys, os
from PIL import Image, ImageDraw
d, gs, vs, out = sys.argv[1], sys.argv[2].split(","), sys.argv[3].split(","), sys.argv[4]; T = int(sys.argv[5]) if len(sys.argv) > 5 else 300
G = Image.new("RGB", (len(vs) * T, len(gs) * T + 20), (28, 28, 32)); dr = ImageDraw.Draw(G)
for i, g in enumerate(gs):
    for j, v in enumerate(vs):
        f = os.path.join(d, "boca_%02d_%s.png" % (int(g), v))
        if not os.path.exists(f): continue
        im = Image.open(f).convert("RGBA"); bg = Image.new("RGBA", im.size, (214, 210, 204, 255)); bg.alpha_composite(im)
        G.paste(bg.convert("RGB").resize((T, T)), (j * T, 20 + i * T)); dr.text((j * T + 4, 22 + i * T), "%s %s" % (g, v), fill=(0, 0, 0))
G.save(out)
