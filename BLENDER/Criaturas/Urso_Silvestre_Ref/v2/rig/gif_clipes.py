"""Monta GIFs dos clipes (quadros de render_clipes.py ... video): velocidade normal (30 qps) e lenta (1/3), lado a lado
num mesmo GIF por clipe, com o nome. Uso: python gif_clipes.py <dir_render> <saida_dir>"""
import sys, os, glob
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
for pasta in sorted(glob.glob(os.path.join(d, "video", "*"))):
    nome = os.path.basename(pasta); qs = [Image.open(p).convert("RGB") for p in sorted(glob.glob(os.path.join(pasta, "*.png")))]
    if not qs: continue
    W, H = qs[0].size; n = len(qs); quadros = []
    # GIF unico: a cada passo de 1/30 s o lado esquerdo avanca 1 quadro e o direito 1/3 de quadro (lento)
    for k in range(n * 3):
        o = Image.new("RGB", (W * 2, H), (20, 20, 20)); o.paste(qs[k % n], (0, 0)); o.paste(qs[(k // 3) % n], (W, 0))
        dr = ImageDraw.Draw(o); dr.rectangle((0, 0, W * 2, 18), fill=(0, 0, 0))
        dr.text((6, 3), "%s - velocidade normal" % nome, fill=(255, 255, 255)); dr.text((W + 6, 3), "%s - lento (1/3)" % nome, fill=(255, 255, 255))
        quadros.append(o.quantize(colors=128))
    quadros[0].save(os.path.join(out, "Urso_%s.gif" % nome), save_all=True, append_images=quadros[1:], duration=33, loop=0, optimize=True)
    print("GIF", nome, n, "quadros")
