"""Pranchas da E2: (1) conjunto - referencia | E1 r8 | E2 | silhuetas da E2, por vista, + 3/4 frente/tras e tamanho
de jogo; (2) closes - rosto perfil/frente e tufo, referencia x E2, + juba 3/4; (3) cores - medias de regioes no perfil
(mesmos pixels: as cameras estao alinhadas a referencia), referencia x E2.
Uso: python 08_prancha_e2.py <ref.png> <ref_dir> <dir_r8> <dir_e2> <saida_prefixo> <titulo>"""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
REF, RDIR, R8, E2, SAIDA, TIT = sys.argv[1:7]
ref = Image.open(REF).convert("RGB"); FUNDO = (220, 213, 207)
try: F = ImageFont.truetype("arial.ttf", 22); f = ImageFont.truetype("arial.ttf", 17)
except OSError: F = f = ImageFont.load_default()
def sobre(caminho):
    im = Image.open(caminho).convert("RGBA"); b = Image.new("RGBA", im.size, FUNDO + (255,)); b.alpha_composite(im); return b.convert("RGB")
CORTES = {"lado": (0, 0, 1217, 594), "frente": (0, 610, 608, 1293), "tras": (609, 610, 1217, 1293)}
NOMES = {"lado": "Perfil", "frente": "Frente", "tras": "Traseira"}
total = np.asarray(Image.open(os.path.join(RDIR, "mascara_total.png"))) > 127
lado_m = np.load(os.path.join(RDIR, "lado.npy"))
met = {}
# ---------------------------------------------------------------- 1. conjunto
blocos = []
for v, (x0, y0, x1, y1) in CORTES.items():
    r = ref.crop((x0, y0, x1, y1)); a = sobre(os.path.join(R8, v + ".png")); b = sobre(os.path.join(E2, v + ".png"))
    mm = np.asarray(Image.open(os.path.join(E2, v + ".png")))[..., 3] > 127
    mr = (lado_m if v == "lado" else total)[y0:y1, x0:x1]
    iou = (mm & mr).sum() / max((mm | mr).sum(), 1); met["iou_" + v] = round(float(iou), 3)
    s = np.zeros(mm.shape + (3,), np.uint8) + 40
    s[mm & mr] = (150, 150, 150); s[mr & ~mm] = (220, 60, 60); s[mm & ~mr] = (60, 110, 230)
    blocos.append((f"{NOMES[v]}: referencia | E1 r8 (reprovada) | E2 | silhuetas E2 (cinza=ambos, vermelho=so ref, azul=so E2) IoU {iou:.3f}",
                   [r, a, b, Image.fromarray(s)]))
t34 = [sobre(os.path.join(R8, "tres_quartos.png")), sobre(os.path.join(E2, "tres_quartos.png")), sobre(os.path.join(E2, "tres_quartos_tras.png"))]
jogo = sobre(os.path.join(E2, "jogo_34.png")); jogo = jogo.resize((jogo.width * 4, jogo.height * 4), Image.NEAREST)
W = 20 + sum(i.width + 20 for i in blocos[0][1]); H = 70 + sum(i[1][0].height + 50 for i in blocos) + 850 + 60
P = Image.new("RGB", (W, H), (30, 30, 34)); d = ImageDraw.Draw(P); d.text((20, 18), TIT + " - conjunto", fill=(240, 220, 160), font=F)
y = 60
for txt, ims in blocos:
    d.text((20, y), txt, fill=(230, 230, 230), font=f); y += 26; x = 20
    for im in ims: P.paste(im, (x, y)); x += im.width + 20
    y += ims[0].height + 24
d.text((20, y), "3/4: E1 r8 | E2 frente | E2 tras | E2 em tamanho de jogo (200x160 px, ampliado 4x sem suavizar)", fill=(230, 230, 230), font=f); y += 26
x = 20
for im in t34 + [jogo]:
    P.paste(im, (x, y)); x += im.width + 20
P.save(SAIDA + "_conjunto.png")
# ---------------------------------------------------------------- 2. closes
pares = [("Rosto perfil", ref.crop((950, 40, 1120, 260)).resize((510, 660), Image.LANCZOS), sobre(os.path.join(E2, "close_rosto_lado.png"))),
         ("Rosto frente", ref.crop((241, 650, 451, 880)).resize((630, 690), Image.LANCZOS), sobre(os.path.join(E2, "close_rosto_frente.png"))),
         ("Tufo da cauda", ref.crop((30, 335, 290, 545)).resize((520, 420), Image.LANCZOS), sobre(os.path.join(E2, "close_tufo.png")))]
jub = sobre(os.path.join(E2, "close_juba_34.png")); jref = ref.crop((800, 0, 1110, 320)).resize((870, 900), Image.LANCZOS)
W2 = 20 + max(a.width + b.width + 60 for _, a, b in pares) + jub.width + jref.width + 60
H2 = 70 + sum(max(a.height, b.height) + 50 for _, a, b in pares)
Q = Image.new("RGB", (max(W2, 2400), max(H2, 1000)), (30, 30, 34)); d = ImageDraw.Draw(Q); d.text((20, 18), TIT + " - closes (referencia | E2)", fill=(240, 220, 160), font=F)
y = 60
for nome, a, b in pares:
    d.text((20, y), nome, fill=(230, 230, 230), font=f); Q.paste(a, (20, y + 26)); Q.paste(b, (40 + a.width, y + 26)); y += max(a.height, b.height) + 50
xj = 60 + max(a.width + b.width for _, a, b in pares) + 20
d.text((xj, 60), "Juba: referencia (perfil) | E2 (3/4 de perto)", fill=(230, 230, 230), font=f)
Q.paste(jref, (xj, 86)); Q.paste(jub, (xj + jref.width + 20, 86))
Q.save(SAIDA + "_closes.png")
# ---------------------------------------------------------------- 3. cores (perfil, mesma luz neutra nas vistas da E2)
REG = {"juba topo (dourado)": (900, 40, 960, 80), "juba media (laranja)": (840, 200, 900, 260), "juba baixa/tras (cobre)": (700, 330, 760, 400),
       "juba peito (pontas)": (880, 400, 940, 450), "flanco": (560, 270, 640, 330), "ventre": (600, 360, 660, 385),
       "coxa": (450, 330, 500, 380), "focinho": (1068, 176, 1090, 192), "tufo": (100, 450, 160, 500)}
e2l = np.asarray(Image.open(os.path.join(E2, "lado.png")).convert("RGBA")).astype(float); rr = np.asarray(ref).astype(float)
C = Image.new("RGB", (900, 70 + 60 * len(REG)), (30, 30, 34)); d = ImageDraw.Draw(C)
d.text((20, 18), TIT + " - cores medias no perfil: referencia | E2 (EEVEE, luz neutra)", fill=(240, 220, 160), font=f)
cores = {}
for i, (nome, (x0, y0, x1, y1)) in enumerate(REG.items()):
    m = lado_m[y0:y1, x0:x1]; cr = rr[y0:y1, x0:x1][m].mean(0) if m.any() else np.zeros(3)
    blk = e2l[y0:y1, x0:x1]; mm = blk[..., 3] > 127; ce = blk[mm][:, :3].mean(0) if mm.any() else np.zeros(3)
    cores[nome] = {"ref": [int(c) for c in cr], "e2": [int(c) for c in ce]}
    yy = 60 + 60 * i; d.text((20, yy + 15), nome, fill=(230, 230, 230), font=f)
    d.rectangle((300, yy, 400, yy + 50), fill=tuple(int(c) for c in cr)); d.rectangle((410, yy, 510, yy + 50), fill=tuple(int(c) for c in ce))
    d.text((530, yy + 15), f"ref {tuple(int(c) for c in cr)}   E2 {tuple(int(c) for c in ce)}", fill=(230, 230, 230), font=f)
C.save(SAIDA + "_cores.png")
met["cores"] = cores
json.dump(met, open(SAIDA + "_metricas.json", "w"), indent=1, ensure_ascii=False)
print("PRANCHAS", SAIDA, {k: v for k, v in met.items() if k.startswith("iou")})
