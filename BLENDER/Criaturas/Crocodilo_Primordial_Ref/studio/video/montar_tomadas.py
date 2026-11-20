"""Captura em tempo real (capturar.py) -> video por tomadas: separa as tomadas pelas telas pretas, grava cada uma em
tempo real a 30 qps (q00000.jpg...) com 0,3 s de preto entre elas e, no fim, repete as tomadas pedidas em camera lenta.
Uso: python montar_tomadas.py PASTA_CAP DURACAO_S PASTA_SAIDA "3,8" [fator_lento]"""
import sys, os, glob, shutil
from PIL import Image, ImageStat
cap, dur, saida = sys.argv[1], float(sys.argv[2]), sys.argv[3]
lentas = [int(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 and sys.argv[4] else []
fator = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
fs = sorted(glob.glob(os.path.join(cap, "f*.jpg"))); n = len(fs); dtq = dur / n
preto = lambda f: ImageStat.Stat(Image.open(f).convert("L").resize((64, 36))).mean[0] < 8
segs, cur = [], []
for i, f in enumerate(fs):
    if preto(f):
        if cur: segs.append(cur); cur = []
    else: cur.append(i)
if cur: segs.append(cur)
segs = [s for s in segs if len(s) * dtq > 1.0]          # ignora piscadas curtas
os.makedirs(saida, exist_ok=True)
for f in glob.glob(os.path.join(saida, "q*.jpg")): os.remove(f)
k = 0; tam = Image.open(fs[0]).size
def grava(src=None):
    global k
    dst = os.path.join(saida, "q%05d.jpg" % k)
    if src: shutil.copy(src, dst)
    else: Image.new("RGB", tam).save(dst)
    k += 1
def tomada(seg, vel=1.0):
    t0, t1 = seg[0] * dtq, seg[-1] * dtq; j = 0
    t0 = max(t0, t1 - 8.5)                                # tomada longa (espera de preparo): so os ultimos 8,5 s
    while t0 + j * vel / 30 <= t1:
        grava(fs[min(n - 1, round((t0 + j * vel / 30) / dtq))]); j += 1
    for _ in range(9): grava()
for s in segs: tomada(s)
for i in lentas:
    if i < len(segs): tomada(segs[i], fator)
print("tomadas", len(segs), [round(len(s) * dtq, 1) for s in segs], "quadros", k)
