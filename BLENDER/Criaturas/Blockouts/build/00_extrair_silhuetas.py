import sys, os
from PIL import Image, ImageDraw
P = r"C:\Users\Rhenan\Downloads\RPG_Referencias_Visuais_GitHub\REFERENCES\03_CREATURES"
OUT = sys.argv[1]
BOX = {
 "Lobo_Ancestral": ("01-lobos-urso-leao.png", (546, 292, 714, 388)),
 "Lobo_Artico": ("01-lobos-urso-leao.png", (1270, 292, 1442, 388)),
 "Urso_Silvestre": ("01-lobos-urso-leao.png", (546, 818, 714, 926)),
 "Leao_Solar": ("01-lobos-urso-leao.png", (1266, 814, 1444, 928)),
 "Dragao_das_Montanhas": ("02-dragoes-wyvern.png", (435, 395, 561, 505)),
 "Dragao_Glacial": ("02-dragoes-wyvern.png", (1148, 395, 1274, 505)),
 "Dragao_Sombrio": ("02-dragoes-wyvern.png", (419, 912, 561, 1036)),
 "Wyvern": ("02-dragoes-wyvern.png", (1133, 912, 1268, 1036)),
 "Basilisco": ("03-basilisco-crocodilo-escorpiao-lagarto.png", (425, 396, 531, 497)),
 "Crocodilo_Primordial": ("03-basilisco-crocodilo-escorpiao-lagarto.png", (1147, 396, 1254, 497)),
 "Escorpiao_Colossal": ("03-basilisco-crocodilo-escorpiao-lagarto.png", (424, 915, 531, 1031)),
 "Lagarto_Cristalino": ("03-basilisco-crocodilo-escorpiao-lagarto.png", (1147, 915, 1255, 1031)),
 "Bufalo_Colossal": ("04-bufalo-serpente-marinha-leviata-cerbero.png", (406, 395, 529, 497)),
 "Serpente_Marinha": ("04-bufalo-serpente-marinha-leviata-cerbero.png", (1115, 395, 1251, 497)),
 "Cerbero_Sombrio": ("04-bufalo-serpente-marinha-leviata-cerbero.png", (1126, 911, 1251, 1030)),
}
os.makedirs(OUT, exist_ok=True)
tiles = []
for k, (f, b) in BOX.items():
    im = Image.open(os.path.join(P, f)).convert("RGB").crop(b)
    big = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
    big.save(os.path.join(OUT, k + "_silhueta_x4.png"))
    t = big.resize((300, int(300 * big.height / big.width)))
    tiles.append((k, t))
W = 5 * 310; H = 3 * 300
s = Image.new("RGB", (W, H), (20, 20, 20)); d = ImageDraw.Draw(s)
for i, (k, t) in enumerate(tiles):
    x, y = (i % 5) * 310, (i // 5) * 300
    s.paste(t, (x, y + 20)); d.text((x + 4, y + 4), k, fill=(255, 255, 0))
s.save(os.path.join(OUT, "_contato_silhuetas.png")); print("ok", len(tiles))
