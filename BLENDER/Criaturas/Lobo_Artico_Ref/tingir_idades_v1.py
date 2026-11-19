"""Cores por idade (proposta aprovada 19/11): multiplica a cor da pelagem (Corpo, Cabeca, atlas da Pelagem; so RGB).
Saida em idades_v1/export/<arquivo>_<Idade>.png, usada por exportar_idades_v1.py. Uso: python tingir_idades_v1.py"""
import os
from PIL import Image
SRC = "anim_v42b"; OUT = "idades_v1/export"; os.makedirs(OUT, exist_ok=True)
TINTAS = {"Filhote": (0.46, 0.42, 0.39), "Jovem": (0.70, 0.69, 0.68), "PreAdulto": (0.88, 0.88, 0.88), "Anciao": (1.0, 0.95, 0.86)}   # r2: mais claras (no GLB a tinta pesava mais que no prototipo aprovado)
for arq in ("LoboArtico_Corpo_cor.png", "LoboArtico_Cabeca_cor.png", "LoboArtico_pelo_atlas.png"):
    im = Image.open(os.path.join(SRC, arq)); modo = im.mode; im = im.convert("RGBA"); r, g, b, a = im.split()
    for idade, t in TINTAS.items():
        rr, gg, bb = (c.point(lambda x, k=k: int(x * k)) for c, k in zip((r, g, b), t))
        Image.merge("RGBA", (rr, gg, bb, a)).convert(modo if modo in ("RGB", "RGBA") else "RGBA").save(os.path.join(OUT, "%s_%s.png" % (os.path.splitext(arq)[0], idade)))
    print(arq, modo, im.size)
print("TINGIR_OK")
