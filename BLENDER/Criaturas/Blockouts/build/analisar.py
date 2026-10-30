"""Le o diff do world_gate e mostra, por faixa (linha amostrada), as extremidades da referencia e do modelo,
mais as colunas onde falta (so ref) ou sobra (so modelo) massa. Uso: python analisar.py <Especie> [n_linhas]"""
import sys, os, glob
from PIL import Image

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esp = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
f = glob.glob(os.path.join(R, "review", esp, "gate", "diff_*.png"))[0]
d = Image.open(f).convert("RGB"); W, H = d.size; p = d.load()


def tipo(x, y):
    r, g, b = p[x, y]
    if r > 200 and b < 100: return "r"
    if b > 200 and r < 100: return "m"
    if abs(r - 150) < 12 and abs(g - 150) < 12: return "g"
    return "."


ys = [y for y in range(H) if any(tipo(x, y) in "rg" for x in range(W))]
y0, y1 = min(ys), max(ys)
for k in range(n):
    yy = int(y0 + (k + 0.5) * (y1 - y0) / n)
    lin = [tipo(x, yy) for x in range(W)]
    ref = [x for x in range(W) if lin[x] in "rg"]
    mod = [x for x in range(W) if lin[x] in "mg"]
    def trechos(c):
        out, x = [], 0
        while x < W:
            if lin[x] == c:
                s = x
                while x < W and lin[x] == c: x += 1
                if x - s >= 3: out.append("%d-%d" % (s, x - 1))
            else:
                x += 1
        return " ".join(out)
    print("faixa %d (h=%3d px): ref %s | modelo %s | falta[%s] sobra[%s]" % (
        k, H - yy, ("%d..%d" % (min(ref), max(ref))) if ref else "-", ("%d..%d" % (min(mod), max(mod))) if mod else "-",
        trechos("r"), trechos("m")))
