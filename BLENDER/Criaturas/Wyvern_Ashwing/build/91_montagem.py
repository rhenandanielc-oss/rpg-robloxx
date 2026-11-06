import bpy, sys, os
import numpy as np
d = sys.argv[sys.argv.index("--") + 1]; saida = sys.argv[sys.argv.index("--") + 2]
nomes = sys.argv[sys.argv.index("--") + 3].split(",")
cols = int(sys.argv[sys.argv.index("--") + 4]) if len(sys.argv) > sys.argv.index("--") + 4 else 3   # colunas (opcional)
ims = []
for n in nomes:
    im = bpy.data.images.load(os.path.join(d, n + ".png"))
    w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
    ims.append(a)
h, w = ims[0].shape[:2]
rows = (len(ims) + cols - 1) // cols
big = np.ones((rows * h, cols * w, 4), dtype=np.float32)
for i, a in enumerate(ims):
    r, c = divmod(i, cols)
    big[(rows - 1 - r) * h:(rows - r) * h, c * w:(c + 1) * w] = a
out = bpy.data.images.new("M", cols * w, rows * h)
out.pixels = big.ravel()
out.filepath_raw = saida; out.file_format = "PNG"; out.save()
