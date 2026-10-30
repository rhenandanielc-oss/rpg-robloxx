import sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
print("size", im.size)
crops = {"painel_completo": (724, 526, 1448, 1086), "conceito_principal": (726, 528, 1262, 926), "silhueta_lateral": (1266, 814, 1444, 928), "rosto": (1266, 528, 1444, 676), "juba": (1266, 678, 1444, 812)}
for k, b in crops.items():
    c = im.crop(b); c.save(f"{out}/{k}.png")
    big = c.resize((c.width * 4, c.height * 4), Image.LANCZOS) if k in ("silhueta_lateral",) else None
    if big: big.save(f"{out}/{k}_x4.png")
    print(k, c.size)
