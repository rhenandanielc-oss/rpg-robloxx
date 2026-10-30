import sys, os
from PIL import Image, ImageDraw
R = sys.argv[1]; es = sys.argv[2].split(","); out = sys.argv[3]
rows = []
for e in es:
    ims = [Image.open(os.path.join(R, "ref", e + "_silhueta_x4.png")).convert("RGB")] if os.path.exists(os.path.join(R, "ref", e + "_silhueta_x4.png")) else []
    for v in ("clay_front", "clay_side", "clay_threequarter"):
        b = Image.open(os.path.join(R, "review", e, "clay", v + ".png")).convert("RGB")
        g = b.convert("L").point(lambda x: 255 if x > 12 else 0).getbbox() or (0, 0, b.width, b.height)
        ims.append(b.crop((max(0, g[0] - 10), max(0, g[1] - 10), min(b.width, g[2] + 10), min(b.height, g[3] + 10))))
    rows.append((e, ims))
Hh = 210
s = Image.new("RGB", (4 * 330, len(rows) * (Hh + 18)), (30, 30, 30)); d = ImageDraw.Draw(s)
for i, (e, ims) in enumerate(rows):
    y = i * (Hh + 18); d.text((4, y + 2), e, fill=(255, 255, 0))
    for j, im in enumerate(ims):
        sc = min(Hh / im.height, 320 / im.width); im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))))
        s.paste(im, (j * 330 + 5, y + 16))
s.save(out); print(s.size)
