"""v23: pranchas de revisao da retopologia da prega coxa D x ventre (renders de renders_v23.sh; cameras iguais v21/v22/v23).
Saida review/v23_flanco/revisao/:
- 01_repouso_corpo.png: referencia + corpo inteiro em repouso (perfil D/E, tres-quartos, traseira, de baixo) v21 | v22 | v23;
- 02_repouso_<vista>.png: closes de repouso (real com cartoes, sem cartoes, arame, pesos) v21 | v22 | v23;
- 03_poses_<modo>.png: Trote q6, Corrida q6/q8/q10/q12, Andar q14 (real, sempelo, wire, pesos, dobras) v21 | v22 | v23;
- 04_lods.png: LOD1/LOD2 v21 | v23 (repouso, Trote q6, Corrida q12; sem cartoes e arame);
- 05_uv_ilhas.png: ilhas novas no atlas (cor e normal) por LOD;
- video_<acao>/v_NNNN.png: mosaico v21 | v22 | v23 (barriga, virilha D, tres-quartos; real com cartoes) para MP4.
Uso: python prancha_flanco_v23.py (nesta pasta)"""
import os, json
from PIL import Image, ImageDraw
D = "review/v23_flanco"; O = os.path.join(D, "revisao"); os.makedirs(O, exist_ok=True)
REF = "../../../REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png"
VS = ("v21", "v22", "v23"); ROT = {"v21": "v21 (antes)", "v22": "v22 (so pesos)", "v23": "v23 (retopo + pesos)"}
W, H = 480, 360
def cel(p, txt, w=W, h=H):
    im = Image.new("RGB", (w, h), (24, 24, 28))
    if p and os.path.exists(p):
        s = Image.open(p).convert("RGB"); s.thumbnail((w, h)); im.paste(s, ((w - s.width) // 2, (h - s.height) // 2))
    elif p: ImageDraw.Draw(im).text((10, h // 2), "falta: " + os.path.basename(p), fill=(255, 80, 80))
    d = ImageDraw.Draw(im); d.rectangle((0, 0, w, 18), fill=(0, 0, 0)); d.text((5, 3), txt, fill=(255, 235, 120)); return im
def grade(linhas, nome, w=W, h=H):
    nc = max(len(l) for l in linhas); o = Image.new("RGB", (nc * (w + 4), len(linhas) * (h + 4)), (40, 40, 40))
    for r, l in enumerate(linhas):
        for c, im in enumerate(l): o.paste(im, (c * (w + 4), r * (h + 4)))
    o.save(os.path.join(O, nome)); print("PRANCHA", nome, o.size)
CORPO = ("c_perfil_D", "c_perfil_E", "c_34_D", "c_tras", "c_baixo")
grade([[cel(REF, "REFERENCIA (repouso; nao prova movimento)")] + [cel(None, "")] * 4] +
      [[cel("%s/repouso/%s/real_LOW_repouso_%s_q0000.png" % (D, v, c), "%s repouso %s" % (ROT[v], c)) for c in CORPO] for v in VS], "01_repouso_corpo.png")
for vi in ("barriga", "flanco_D_baixo", "virilha_D"):
    grade([[cel("%s/repouso/%s/%s_LOW_repouso_%s_q0000.png" % (D, v, m, vi), "%s repouso %s %s" % (ROT[v], vi, m)) for v in VS] for m in ("real", "sempelo", "wire", "pesos")],
          "02_repouso_%s.png" % vi)
POSES = (("Trote", 6, "barriga"), ("Corrida", 6, "virilha_D"), ("Corrida", 8, "virilha_D"), ("Corrida", 10, "barriga"), ("Corrida", 12, "virilha_D"), ("Andar", 14, "barriga"))
for m in ("real", "sempelo", "wire", "pesos", "dobras"):
    VV = ("v21", "v23") if m == "dobras" else VS
    linhas = []
    for ac, q, vi in POSES:
        linhas.append([cel("%s/poses/%s/%s_LOW_%s_%s_q%04d.png" % (D, v, m, ac, vi, q), "%s %s q%d %s %s" % (ROT[v], ac, q, vi, m)) for v in VV] +
                      [cel("%s/poses/%s/%s_LOW_%s_flanco_D_baixo_q%04d.png" % (D, v, m, ac, q), "%s %s q%d flanco_D_baixo" % (ROT[v], ac, q)) for v in VV])
    grade(linhas, "03_poses_%s.png" % m, 400, 300)
lin = []
for L in ("LOD1", "LOD2"):
    for ac, q, vi in (("repouso", 0, "barriga"), ("Trote", 6, "barriga"), ("Corrida", 12, "virilha_D")):
        lin.append([cel("%s/lods/%s/%s_%s_%s_%s_q%04d.png" % (D, v, m, L, ac, vi, q), "%s %s %s q%d %s %s" % (L, ROT[v], ac, q, vi, m)) for v in ("v21", "v23") for m in ("sempelo", "wire")])
    lin.append([cel("%s/lods/%s/real_%s_repouso_%s_q0000.png" % (D, v, L, c), "%s %s repouso %s" % (L, ROT[v], c)) for v in ("v21", "v23") for c in ("c_perfil_D", "c_34_D")])
grade(lin, "04_lods.png", 400, 300)
# ilhas UV novas
r = json.load(open("anim_v23/retopo_flanco_v23.json")); ims = []
for L in ("LOW", "LOD1", "LOD2"):
    x, y, w, h = r[L]["uv"]["retangulo_atlas_px"]
    for k in ("cor", "normal"):
        a = Image.open("anim_v23/LoboArtico_Corpo_%s.png" % k).transpose(Image.FLIP_TOP_BOTTOM).crop((x - 6, 1024 - (y + h) - 6, x + w + 6, 1024 - y + 6)).resize((300, 220), Image.NEAREST)
        ims.append(cel(None, "")); ims[-1].paste(a, (0, 18)); ImageDraw.Draw(ims[-1]).text((5, 3), "%s ilha nova %s (%dx%d px)" % (L, k, w, h), fill=(255, 235, 120))
grade([ims[0:2], ims[2:4], ims[4:6]], "05_uv_ilhas.png", 300, 240)
# video: mosaico 3 x 3 (colunas v21 | v22 | v23; linhas barriga, virilha_D, c_34_D)
for ac, n in (("Trote", 18), ("Corrida", 14), ("Andar", 36)):
    dv = os.path.join(O, "video_%s" % ac); os.makedirs(dv, exist_ok=True)
    for q in range(n):
        linhas = [[cel("%s/video/%s/real_LOW_%s_%s_q%04d.png" % (D, v, ac, vi, q), "%s %s q%d %s" % (ROT[v], ac, q, vi), 640, 360) for v in VS] for vi in ("barriga", "virilha_D", "c_34_D")]
        o = Image.new("RGB", (3 * 640 + 8, 3 * 360 + 8), (40, 40, 40))
        for rr, l in enumerate(linhas):
            for c, im in enumerate(l): o.paste(im, (c * 644, rr * 364))
        o.save(os.path.join(dv, "v_%04d.png" % q))
    print("VIDEO_QUADROS", ac, n)
print("PRANCHA_V23_OK")
