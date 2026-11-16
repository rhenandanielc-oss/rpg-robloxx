"""Monta o video das animacoes a partir da captura por passos (capturar.py): separa os clipes pelas telas pretas,
mantem 1 quadro por passo (descarta copias identicas seguidas, pela miniatura), confere a contagem com os quadros
esperados de cada clipe e grava a sequencia final (q00000.jpg...) a 30 qps, com 0,4 s de tela preta entre clipes.
Uso: python montar_video.py PASTA_CAPTURA PASTA_SAIDA ESPERADOS_JSON"""
import sys, os, glob, shutil, hashlib, json
from PIL import Image, ImageStat
cap, saida, esp = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
fs = sorted(glob.glob(os.path.join(cap, "f*.jpg")))
def preto(f): return ImageStat.Stat(Image.open(f).convert("L").resize((64, 36))).mean[0] < 8
segs = []; atual = []; antes_preto = True
for f in fs:
    if preto(f):
        if atual: segs.append(atual); atual = []
        continue
    atual.append(f)
if atual: segs.append(atual)
def uni(seg):
    out = []; ult = None
    for f in seg:
        h = hashlib.md5(Image.open(f).resize((320, 180)).tobytes()).hexdigest()
        if h != ult: out.append(f); ult = h
    return out
os.makedirs(saida, exist_ok=True)
for f in glob.glob(os.path.join(saida, "q*.jpg")): os.remove(f)
n = 0; tam = Image.open(fs[0]).size; rel = []
def grava(img_path=None):
    global n
    if img_path: shutil.copy(img_path, os.path.join(saida, "q%05d.jpg" % n))
    else: Image.new("RGB", tam).save(os.path.join(saida, "q%05d.jpg" % n))
    n += 1
for k in range(12): grava()
for i, seg in enumerate(segs):
    nome, e = esp[i] if i < len(esp) else ("?", 0)
    # cada passo ficou o mesmo tempo na tela: amostra uniforme no tempo (o "unico" por miniatura nao serve, a
    # renderizacao varia um pouco entre duas capturas do mesmo passo)
    u = [seg[min(len(seg) - 1, int((k + 0.5) * len(seg) / e))] for k in range(e)] if e else uni(seg)
    rel.append("%-24s capturas %4d  -> %4d quadros (%.2f capturas por passo)" % (nome, len(seg), len(u), len(seg) / max(1, e)))
    for f in u: grava(f)
    for k in range(12): grava()
print("\n".join(rel)); print("segmentos", len(segs), "clipes esperados", len(esp), "quadros", n, "=", round(n / 30, 1), "s")
open(os.path.join(saida, "relatorio_montagem.txt"), "w").write("\n".join(rel) + "\n")
