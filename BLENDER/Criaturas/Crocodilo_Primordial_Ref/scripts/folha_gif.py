"""Folha (N quadros em grade) e GIF continuo (3 ciclos) a partir de render_clipes_v2.py.
Uso: python folha_gif.py <dir> <clipe> <camera> [ms_por_quadro] [ciclos] [lento]"""
import sys, glob, os
from PIL import Image, ImageDraw, ImageFont
d, cl, cam = sys.argv[1:4]; ms = int(sys.argv[4]) if len(sys.argv) > 4 else 100; ciclos = int(sys.argv[5]) if len(sys.argv) > 5 else 3
fs = sorted(glob.glob(os.path.join(d, "%s_%s_*.png" % (cl, cam))))
fr = [Image.open(f).convert("RGB") for f in fs]
seq = fr * ciclos
seq[0].save(os.path.join(d, "%s_%s.gif" % (cl, cam)), save_all=True, append_images=seq[1:], duration=ms, loop=0)
if len(sys.argv) > 6: seq0 = fr; seq0[0].save(os.path.join(d, "%s_%s_lento.gif" % (cl, cam)), save_all=True, append_images=seq0[1:], duration=ms * 3, loop=0)
f = ImageFont.truetype("arial.ttf", 16); W, H = 400, 225; n = min(len(fr), 12); passo = max(1, len(fr) // n)
sel = fr[::passo][:n]; g = Image.new("RGB", (4 * W, ((len(sel) + 3) // 4) * H), (30, 30, 32)); dr = ImageDraw.Draw(g)
for i, im in enumerate(sel):
    x, y = (i % 4) * W, (i // 4) * H; g.paste(im.resize((W, H)), (x, y)); dr.text((x + 5, y + 3), "%s %s q%d" % (cl, cam, i * passo), fill=(255, 220, 120), font=f)
g.save(os.path.join(d, "FOLHA_%s_%s.png" % (cl, cam))); print("FOLHA", cl, cam, len(fr), "quadros")
