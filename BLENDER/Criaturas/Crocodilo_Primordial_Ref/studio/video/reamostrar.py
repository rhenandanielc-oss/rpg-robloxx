"""Captura em tempo real (capturar.py) -> quadros a 30 qps em tempo real (q00000.jpg...) + uma prancha por tomada
(tomadas separadas pelas telas pretas). Uso: python reamostrar.py PASTA_CAP DURACAO_S PASTA_SAIDA [quadros_por_prancha]"""
import sys, os, glob, shutil
from PIL import Image, ImageStat
cap, dur, saida = sys.argv[1], float(sys.argv[2]), sys.argv[3]; npr = int(sys.argv[4]) if len(sys.argv) > 4 else 8
fs = sorted(glob.glob(os.path.join(cap, "f*.jpg"))); n = len(fs)
preto = lambda f: ImageStat.Stat(Image.open(f).convert("L").resize((64, 36))).mean[0] < 8
i0 = next(i for i, f in enumerate(fs) if not preto(f)); i1 = max(i for i, f in enumerate(fs) if not preto(f))
i0 = max(0, i0 - 8); i1 = min(n - 1, i1 + 8)
q = os.path.join(saida, "quadros"); os.makedirs(q, exist_ok=True)
for f in glob.glob(os.path.join(q, "q*.jpg")): os.remove(f)
t0 = i0 * dur / n; t1 = i1 * dur / n; k = 0
while t0 + k / 30 <= t1:
    shutil.copy(fs[min(n - 1, round((t0 + k / 30) * n / dur))], os.path.join(q, "q%05d.jpg" % k)); k += 1
fq = sorted(glob.glob(os.path.join(q, "q*.jpg"))); segs = []; cur = []
for f in fq:
    if preto(f):
        if cur: segs.append(cur); cur = []
    else: cur.append(f)
if cur: segs.append(cur)
for i, s in enumerate(segs):
    sel = [s[int(j * (len(s) - 1) / (npr - 1))] for j in range(npr)]
    cols = 4; rows = (npr + cols - 1) // cols
    P = Image.new("RGB", (460 * cols, 257 * rows))
    for j, f in enumerate(sel): P.paste(Image.open(f).resize((460, 257)), (460 * (j % cols), 257 * (j // cols)))
    P.save(os.path.join(saida, "prancha_%d.jpg" % (i + 1)), quality=80)
print("quadros", k, round(k / 30, 1), "s; tomadas", [len(s) for s in segs])
