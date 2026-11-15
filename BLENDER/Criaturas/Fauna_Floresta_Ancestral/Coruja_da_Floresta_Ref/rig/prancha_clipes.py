"""Pranchas e GIFs de revisao dos clipes do javali a partir dos quadros de render_javali.py (sem ffmpeg: GIF pelo Pillow).
Para cada rotulo: GIF da vista lateral fixa e da 3/4 fixa (velocidade real, 30 qps, ou /passo) e prancha com quadros-chave
rotulados (nome do clipe, quadro, tempo, apoios). Uso: python prancha_clipes.py <dir_render> <rotulo> [quadros,chave,...]"""
import sys, os, json, glob
from PIL import Image, ImageDraw, ImageFont
D, ROT = sys.argv[1], sys.argv[2]; F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t)
med = json.load(open(os.path.join(D, ROT, "medidas.json")))
SEG = med["segmentos"]
def clipe_de(q):
    for nome, ini, n in SEG:
        if ini <= q < ini + n: return nome, q - ini
    return SEG[-1][0], q - SEG[-1][1]
def rotula(im, q, extra=""):
    nome, ql = clipe_de(q); o = im.convert("RGB"); d = ImageDraw.Draw(o)
    d.rectangle((0, 0, o.width, 24), fill=(40, 38, 36)); d.text((6, 4), f"{nome}  q{ql:03d}  t={ql / 30:.2f}s   (cadeia q{q:03d}) {extra}", fill=(245, 245, 245), font=F(14))
    return o
for vista in ("lado_fixo", "34_fixo", "frente_fixo"):
    arqs = sorted(glob.glob(os.path.join(D, ROT, vista, "q*.png")))
    if not arqs: continue
    qs = [int(os.path.basename(a)[1:4]) for a in arqs]; passo = (qs[1] - qs[0]) if len(qs) > 1 else 1
    ims = [rotula(Image.open(a), q).resize((Image.open(a).width * 3 // 4, (Image.open(a).height + 0) * 3 // 4)) for a, q in zip(arqs, qs)]
    ims[0].save(os.path.join(D, ROT, f"{ROT}_{vista}.gif"), save_all=True, append_images=ims[1:], duration=int(1000 * passo / 30), loop=0)
chave = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
arqs = sorted(glob.glob(os.path.join(D, ROT, "lado_fixo", "q*.png"))); qs = [int(os.path.basename(a)[1:4]) for a in arqs]
if not chave: chave = [qs[int(i * (len(qs) - 1) / 7)] for i in range(8)]
pain = []
for q in chave:
    a = os.path.join(D, ROT, "lado_fixo", "q%03d.png" % q)
    if os.path.exists(a): im = rotula(Image.open(a), q); pain.append(im.resize((im.width // 2, im.height // 2)))
cols = 2; W = pain[0].width; H = pain[0].height; topo = 64
o = Image.new("RGB", (W * cols + 6, topo + (H + 4) * ((len(pain) + cols - 1) // cols)), (45, 43, 42)); d = ImageDraw.Draw(o)
d.text((8, 6), f"Coruja-da-Floresta — lote {os.environ.get('JAVALI_LOTE', 'A')} — {ROT}  ({med['cadeia']})", fill=(250, 250, 250), font=F(18))
txt = (f"avanço {med['avanco_total_u']} u em {med['duracao_s']} s ({med['velocidade_media']} u/s)"
       + (f" · {med['avanco_por_ciclo_u']} u/ciclo" if "avanco_por_ciclo_u" in med else "")
       + f" · deriva máx. casco apoiado {med['deriva_max_casco_apoiado'] * 100:.1f} cm · pele z mín {med['pele_z_min'] * 100:.1f} cm · estica máx {med['estica_max']}x")
d.text((8, 36), txt, fill=(210, 210, 210), font=F(12))
for i, im in enumerate(pain): o.paste(im, ((i % cols) * (W + 6), topo + (i // cols) * (H + 4)))
o.save(os.path.join(D, ROT, f"{ROT}_prancha.png")); print("PRANCHA", ROT, o.size)
