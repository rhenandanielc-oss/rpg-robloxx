"""v38 = copia do prancha_vida_v37 so para o LevantarSentado (review/v38_cauda).
v37 = copia do prancha_vida_v36 para Sentar, Sentado, LevantarSentado (review/v37_sentado).
v36 = copia do prancha_vida_v35 (Deitar, Descanso, Adormecer, Dormindo, Despertar, LevantarDeitado; review/v36_descanso).
v35: Lote de vida, bloco 1 (v35): pranchas e mosaicos de video de Deitar, Deitado e LevantarDeitado. Saida review/v35_vida/revisao/:
- 01_fases_<acao>.png: 8 quadros espacados (perfil E, 3/4) com o marcador da fase;
- 02_contato.png: ponto mais baixo por regiao (pior quadro) e deslize por pata/janela plantada, por LOD; emendas;
- video_<acao>_LOW (perfil E, frente, tras, 3/4) e video_<acao>_LODs (LOD1/LOD2 perfil D e 3/4).
Uso: python prancha_vida_v35.py (nesta pasta)"""
import os, json
from PIL import Image, ImageDraw
D = "review/v38_cauda"; O = os.path.join(D, "revisao"); os.makedirs(O, exist_ok=True); Q = os.path.join(D, "quadros")
VJ = json.load(open("anim_v38/vida_v38.json")); AU = json.load(open(os.path.join(D, "aud_vida_v38.json")))
N = {ac: A["quadros"] for ac, A in VJ["acoes"].items() if ac == "LevantarSentado"}
def fase(ac, q):
    t = q / 30.0; m = VJ["acoes"][ac].get("marcadores_s", {})
    if not m: return "laco"
    nome = "inicio"
    for k, v in sorted(m.items(), key=lambda kv: kv[1]):
        if t <= v + 1e-6: return "rumo a " + k
    return "fim"
def cel(p, txt, w, h):
    im = Image.new("RGB", (w, h), (24, 24, 28))
    if os.path.exists(p):
        s = Image.open(p).convert("RGB"); s.thumbnail((w, h)); im.paste(s, ((w - s.width) // 2, (h - s.height) // 2))
    else: ImageDraw.Draw(im).text((6, h // 2), "falta " + os.path.basename(p), fill=(255, 80, 80))
    d = ImageDraw.Draw(im); d.rectangle((0, 0, w, 15), fill=(0, 0, 0)); d.text((3, 2), txt, fill=(255, 235, 120)); return im
for ac, n in N.items():
    qs = [round(j * n / 7) for j in range(8)]; w, h = 300, 225
    img = Image.new("RGB", (8 * (w + 3), 2 * (h + 3) + 24), (40, 40, 40)); d = ImageDraw.Draw(img); d.text((6, 6), "%s (v38): 8 quadros, %d quadros = %.2f s" % (ac, n, n / 30), fill=(255, 235, 120))
    for c, q in enumerate(qs):
        for r, v in enumerate(("perfil_E", "34_E")):
            img.paste(cel(os.path.join(Q, "LOW_%s_%s_q%04d.png" % (ac, v, q)), "q%d %.2fs %s | %s" % (q, q / 30, v, fase(ac, q)), w, h), (c * (w + 3), 24 + r * (h + 3)))
    img.save(os.path.join(O, "01_fases_%s.png" % ac))
img = Image.new("RGB", (1500, 900), (26, 26, 30)); d = ImageDraw.Draw(img)
d.text((10, 6), "v38: ponto mais baixo por regiao (stud; 0 = chao; negativo = comprime/atravessa) no PIOR quadro, deslize por pata nas janelas plantadas (limite 0,03), emendas", fill=(255, 235, 120))
y = 30
for L in ("LOW", "LOD1", "LOD2"):
    for ac in N:
        A = AU[L]["acoes"][ac]; d.text((10, y), "%s %s: deslize max %.4f" % (L, ac, A["deslize_max"]), fill=(120, 220, 120) if A["deslize_max"] <= 0.03 else (255, 80, 80))
        d.text((300, y), "  ".join("%s %.2f(q%d)" % (k, v[0], v[1]) for k, v in A["chao_min_por_regiao"].items()), fill=(210, 210, 210)); y += 18
    y += 6
d.text((10, y + 4), "emendas LOW: " + "  ".join("%s %s" % (k, v) for k, v in AU["LOW"]["emendas"].items()), fill=(210, 210, 210))
img.save(os.path.join(O, "02_contato.png")); print("PRANCHAS")
def mosaico(nome, n, fn, ncol, nlin, w, h, ac):
    dv = os.path.join(O, "video_" + nome); os.makedirs(dv, exist_ok=True); W_, H_ = ncol * (w + 4), nlin * (h + 4) + 30
    for q in range(n + 1):
        o = Image.new("RGB", (W_, H_), (40, 40, 40)); dd = ImageDraw.Draw(o); dd.text((8, 8), "%s  q%03d  %.2f s  |  %s" % (ac, q, q / 30, fase(ac, q)), fill=(255, 235, 120))
        for r, l in enumerate(fn(q)):
            for c, im in enumerate(l): o.paste(im, (c * (w + 4), 30 + r * (h + 4)))
        o.save(os.path.join(dv, "v_%04d.png" % q))
    open(os.path.join(dv, "res.txt"), "w").write("%d %d" % (W_, H_)); print("VIDEO_QUADROS", nome, n + 1)
for ac, n in N.items():
    mosaico(ac + "_LOW", n, lambda q, ac=ac: [[cel(os.path.join(Q, "LOW_%s_%s_q%04d.png" % (ac, v, q)), "LOW " + v, 480, 360) for v in ("perfil_E", "frente")],
                                              [cel(os.path.join(Q, "LOW_%s_%s_q%04d.png" % (ac, v, q)), "LOW " + v, 480, 360) for v in ("tras", "34_E")]], 2, 2, 480, 360, ac)
    mosaico(ac + "_LODs", n, lambda q, ac=ac: [[cel(os.path.join(Q, "%s_%s_%s_q%04d.png" % (L, ac, v, q)), "%s %s" % (L, v), 480, 360) for v in ("perfil_D", "34_E")] for L in ("LOD1", "LOD2")], 2, 2, 480, 360, ac)
print("PRANCHA_VIDA_V38_OK")
