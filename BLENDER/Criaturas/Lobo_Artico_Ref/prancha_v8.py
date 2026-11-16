"""Pranchas da v8 (cantos da boca). Uso: python prancha_v8.py <review/v8_final> <review/v7_final>
- canto_<E|D>_<modo>.png: diagnostico do canto, linhas = v7 repouso/meio/maximo e v8 repouso/meio/maximo, colunas =
  REFERENCIA (so repouso) + lateral | 3/4 | baixo; modos: pesos (Mandibula), classe (tecido), textura (+ arame);
- comparar_boca_<vista>.png: fases x REFERENCIA | LOD0 v7 | LOD0 v8 | LOD1 v7 | LOD1 v8 | LOD2 v7 | LOD2 v8;
- comparar_olhos_<vista>.png: idem para os olhos (checar que nao houve regressao);
- <LOD>/grade_*.png e arame_<LOD>/grade_*.png;
- sequencia_<LOD>.gif e sequencia.png (tira dos 13 quadros, LOD0/LOD1/LOD2) da abertura continua;
- distancia.png (proposta, sem medicao no Roblox)."""
import sys, os
from PIL import Image, ImageDraw
d8, d7 = (os.path.abspath(x) for x in sys.argv[1:3]); aqui = os.path.dirname(os.path.abspath(__file__))
ref = Image.open(os.path.join(aqui, "ref", "lobo-artico-referencia.png")).convert("RGB")
CORTE = {"olhos": (330, 110, 560, 282), "boca": (330, 200, 560, 372)}
FASES = ("repouso", "meio", "maximo")
def rot(im, t):
    dr = ImageDraw.Draw(im); dr.rectangle((0, 0, 7 * len(t) + 14, 20), fill=(0, 0, 0)); dr.text((7, 4), t, fill=(255, 255, 255)); return im
def abre(p, t, s):
    if not os.path.exists(p): return rot(Image.new("RGB", s, (60, 60, 60)), t + " (sem imagem)")
    return rot(Image.open(p).convert("RGB").resize(s), t)
W, H = 400, 300
for lado in "ED":
    for modo in ("pesos", "classe", "textura"):
        o = Image.new("RGB", (4 * (W + 6), 6 * (H + 6)), (15, 15, 15))
        for r, (dd, ver, fase) in enumerate([(os.path.join(d8, "antes_v7"), "v7", f) for f in FASES] + [(os.path.join(d8, "canto_v8"), "v8", f) for f in FASES]):
            y = r * (H + 6); o.paste(rot(ref.crop(CORTE["boca"]).resize((W, H)), "REFERENCIA (so repouso)"), (0, y))
            for k, v in enumerate(("lateral", "34", "baixo")):
                o.paste(abre(os.path.join(dd, "c_%s_%s_%s_%s.png" % (lado, modo, v, fase)), "%s canto %s %s %s %s" % (ver, lado, modo, v, fase), (W, H)), ((1 + k) * (W + 6), y))
        o.save(os.path.join(d8, "canto_%s_%s.png" % (lado, modo)))
VISTAS = {"boca": ("frente", "perfil", "34", "baixo", "perfil_D", "34_D"), "olhos": ("frente", "perfil", "34", "perfil_D", "34_D")}
COLS = [(d7, "LOW", "LOD0 v7"), (d8, "LOW", "LOD0 v8"), (d7, "LOD1", "LOD1 v7"), (d8, "LOD1", "LOD1 v8"), (d7, "LOD2", "LOD2 v7"), (d8, "LOD2", "LOD2 v8")]
for g, vs in VISTAS.items():
    for v in vs:
        o = Image.new("RGB", ((1 + len(COLS)) * (W + 6), 3 * (H + 6)), (15, 15, 15))
        for r, f in enumerate(FASES):
            y = r * (H + 6); o.paste(rot(ref.crop(CORTE[g]).resize((W, H)), "REFERENCIA" + (" (so repouso)" if r else "")), (0, y))
            for k, (dd, pasta, nome) in enumerate(COLS):
                o.paste(abre(os.path.join(dd, pasta, "t_%s_%s_%s.png" % (g, f, v)), "%s %s %s" % (nome, f, v), (W, H)), ((1 + k) * (W + 6), y))
        o.save(os.path.join(d8, "comparar_%s_%s.png" % (g, v)))
for n in ("LOW", "LOD1", "LOD2"):
    for pre in ("", "arame_"):
        dd = os.path.join(d8, pre + n)
        if not os.path.isdir(dd): continue
        for g, vs in VISTAS.items():
            GW, GH = 480, 360; o = Image.new("RGB", (GW * len(vs), GH * 3))
            for r, f in enumerate(FASES):
                for c, v in enumerate(vs): o.paste(abre(os.path.join(dd, "t_%s_%s_%s.png" % (g, f, v)), "%s %s %s %s" % (n.replace("LOW", "LOD0"), g, f, v), (GW, GH)), (c * GW, r * GH))
            o.save(os.path.join(dd, "grade_%s.png" % g))
sq = os.path.join(d8, "sequencia")
if os.path.isdir(sq):
    SW, SH = 320, 240; tira = Image.new("RGB", (13 * SW, 6 * SH), (15, 15, 15))
    for r, (n, v) in enumerate([(n, v) for n in ("LOW", "LOD1", "LOD2") for v in ("34_E", "canto_D")]):
        quadros = []
        for k in range(13):
            im = abre(os.path.join(sq, n, "q_%s_%02d.png" % (v, k)), "%s %s q%02d" % (n.replace("LOW", "LOD0"), v, k), (SW, SH)); tira.paste(im, (k * SW, r * SH))
            quadros.append(Image.open(os.path.join(sq, n, "q_%s_%02d.png" % (v, k))).convert("RGB"))
        quadros[0].save(os.path.join(d8, "sequencia_%s_%s.gif" % (n.replace("LOW", "LOD0"), v)), save_all=True, append_images=quadros[1:], duration=90, loop=0)
    tira.save(os.path.join(d8, "sequencia.png"))
pd = os.path.join(d8, "distancia")
if os.path.isdir(pd):
    LIN = [(20, ("LOW",)), (35, ("LOW", "LOD1")), (80, ("LOD1", "LOD2")), (120, ("LOW", "LOD2"))]
    DW, DH = 640, 360; o = Image.new("RGB", (4 * (DW + 6), len(LIN) * (DH + 6)), (15, 15, 15))
    for r, (dist, ns) in enumerate(LIN):
        k = 0
        for n in ns:
            for fase in ("repouso", "aberta"):
                im = Image.open(os.path.join(pd, "d%03d_%s_%s.png" % (dist, n, fase))).convert("RGB")
                cx, cy = im.width // 2, int(im.height * 0.47); z = min(im.width // 2, int(im.width * 9 / dist))  # recorte centrado para ver o lobo
                im = im.crop((cx - z, cy - int(z * 0.5625), cx + z, cy + int(z * 0.5625))).resize((DW, DH), Image.NEAREST)
                o.paste(rot(im, "%d studs (proposta) %s %s - recorte ampliado sem filtro" % (dist, n.replace("LOW", "LOD0"), fase)), (k * (DW + 6), r * (DH + 6))); k += 1
    o.save(os.path.join(d8, "distancia.png"))
print("PRANCHAS_V8_OK")
