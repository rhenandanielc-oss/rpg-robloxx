"""Pranchas da v7 (LODs do rosto). Uso: python prancha_lod_v7.py <review/v7_final>
- <LOD>/grade_boca.png, grade_olhos.png (e arame_<LOD>/): fases x vistas de cada LOD;
- comparar_<grupo>_<vista>.png: fases (linhas) x REFERENCIA | LOD0 | LOD1 v6 (antes) | LOD1 v7 | LOD2 v6 (antes) | LOD2 v7;
- comparar_arame_<grupo>.png: arame no repouso e no maximo, LOD0 | LOD1 | LOD2 (vista 3/4 e frente);
- protecao.png: mapa do grupo Protecao_LOD no LOD0 (vermelho = protegido);
- distancia.png: distancias PROPOSTAS (sem medicao no Roblox)."""
import sys, os
from PIL import Image, ImageDraw
d = os.path.abspath(sys.argv[1]); aqui = os.path.dirname(os.path.abspath(__file__))
ref = Image.open(os.path.join(aqui, "ref", "lobo-artico-referencia.png")).convert("RGB")
CORTE = {"olhos": (330, 110, 560, 282), "boca": (330, 200, 560, 372)}
VISTAS = {"boca": ("frente", "perfil", "34", "baixo"), "olhos": ("frente", "perfil", "34")}
FASES = ("repouso", "meio", "maximo")
def rot(im, t):
    dr = ImageDraw.Draw(im); dr.rectangle((0, 0, 7 * len(t) + 14, 20), fill=(0, 0, 0)); dr.text((7, 4), t, fill=(255, 255, 255)); return im
def abre(p, t, s):
    if not os.path.exists(p): return rot(Image.new("RGB", s, (60, 60, 60)), t + " (sem imagem)")
    return rot(Image.open(p).convert("RGB").resize(s), t)
def grade(dd):
    for g, vs in VISTAS.items():
        W, H = 600, 450; o = Image.new("RGB", (W * len(vs), H * 3))
        for r, f in enumerate(FASES):
            for c, v in enumerate(vs): o.paste(abre(os.path.join(dd, "t_%s_%s_%s.png" % (g, f, v)), "%s %s %s" % (g, f, v), (W, H)), (c * W, r * H))
        o.save(os.path.join(dd, "grade_%s.png" % g))
for n in ("LOW", "LOD1", "LOD2"):
    for pre in ("", "arame_"):
        if os.path.isdir(os.path.join(d, pre + n)): grade(os.path.join(d, pre + n))
COLS = [("LOW", "LOD0 v7"), ("v6_LOD1", "LOD1 v6 (antes)"), ("LOD1", "LOD1 v7"), ("v6_LOD2", "LOD2 v6 (antes)"), ("LOD2", "LOD2 v7")]
W, H = 400, 300
for g, vs in VISTAS.items():
    for v in vs:
        o = Image.new("RGB", ((1 + len(COLS)) * (W + 6), 3 * (H + 6)), (15, 15, 15))
        for r, f in enumerate(FASES):
            y = r * (H + 6); o.paste(rot(ref.crop(CORTE[g]).resize((W, H)), "REFERENCIA" + (" (so repouso)" if r else "")), (0, y))
            for k, (pasta, nome) in enumerate(COLS):
                o.paste(abre(os.path.join(d, pasta, "t_%s_%s_%s.png" % (g, f, v)), "%s %s %s" % (nome, f, v), (W, H)), ((1 + k) * (W + 6), y))
        o.save(os.path.join(d, "comparar_%s_%s.png" % (g, v)))
for g, vs in (("boca", ("34", "frente")), ("olhos", ("34", "frente"))):
    linhas = [(f, v) for v in vs for f in ("repouso", "maximo")]
    o = Image.new("RGB", (3 * (W + 6), len(linhas) * (H + 6)), (15, 15, 15))
    for r, (f, v) in enumerate(linhas):
        for k, n in enumerate(("LOW", "LOD1", "LOD2")):
            o.paste(abre(os.path.join(d, "arame_" + n, "t_%s_%s_%s.png" % (g, f, v)), "arame %s %s %s" % (n.replace("LOW", "LOD0"), f, v), (W, H)), (k * (W + 6), r * (H + 6)))
    o.save(os.path.join(d, "comparar_arame_%s.png" % g))
pp = os.path.join(d, "protecao")
if os.path.isdir(pp):
    ims = [("boca", "frente"), ("boca", "perfil"), ("boca", "baixo"), ("olhos", "frente"), ("olhos", "perfil"), ("olhos", "34")]
    o = Image.new("RGB", (3 * (W + 6), 2 * (H + 6)), (15, 15, 15))
    for i, (g, v) in enumerate(ims):
        o.paste(abre(os.path.join(pp, "t_%s_repouso_%s.png" % (g, v)), "Protecao_LOD (vermelho = protegido) %s %s" % (g, v), (W, H)), ((i % 3) * (W + 6), (i // 3) * (H + 6)))
    o.save(os.path.join(d, "protecao.png"))
pd = os.path.join(d, "distancia")
if os.path.isdir(pd):
    LIN = [(20, ("LOW",), "20 studs: LOD0"), (35, ("LOW", "LOD1"), "35 studs: troca LOD0 -> LOD1 (proposta)"),
           (80, ("LOD1", "LOD2"), "80 studs: troca LOD1 -> LOD2 (proposta)"), (120, ("LOW", "LOD2"), "120 studs: LOD0 x LOD2")]
    DW, DH = 640, 360; o = Image.new("RGB", (4 * (DW + 6), len(LIN) * (DH + 6)), (15, 15, 15))
    for r, (dist, ns, t) in enumerate(LIN):
        k = 0
        for n in ns:
            for fase in ("repouso", "aberta"):
                o.paste(abre(os.path.join(pd, "d%03d_%s_%s.png" % (dist, n, fase)), "%s | %s %s" % (t, n.replace("LOW", "LOD0"), fase), (DW, DH)), (k * (DW + 6), r * (DH + 6))); k += 1
    o.save(os.path.join(d, "distancia.png"))
print("PRANCHAS_OK")
