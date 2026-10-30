"""Folha de avaliacao de uma especie: silhueta oficial, gate (diff), frente, lateral, 3/4, tamanho de jogo, medidas."""
import sys, os, json
from PIL import Image, ImageDraw

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
esp = sys.argv[1]
rev = os.path.join(R, "review", esp)
clay = os.path.join(rev, "clay")


def abre(p):
    return Image.open(p).convert("RGB") if os.path.exists(p) else None


gate = {}
gj = os.path.join(rev, "gate", "gate_az270.json")
for nome in os.listdir(os.path.join(rev, "gate")) if os.path.isdir(os.path.join(rev, "gate")) else []:
    if nome.startswith("gate_") and nome.endswith(".json"):
        gate = json.load(open(os.path.join(rev, "gate", nome)))
        diff = os.path.join(rev, "gate", nome.replace("gate_", "diff_").replace(".json", ".png"))
        break
else:
    diff = ""
md = {}
mj = os.path.join(rev, "medidas_neutra.json")
if os.path.exists(mj):
    md = json.load(open(mj, encoding="utf-8"))

iou = gate.get("iou")
paineis = [
    ("Silhueta oficial (painel de referencia)", abre(os.path.join(R, "ref", esp + "_silhueta_x4.png"))),
    ("Gate na pose da referencia  IoU %s  (cinza=ambos, vermelho=so ref, azul=so modelo)" % (("%.3f" % iou) if iou else "-"), abre(diff) if diff else None),
    ("Tamanho de jogo 128 px", abre(os.path.join(clay, "clay_gameplay_128px.png"))),
    ("Frente", abre(os.path.join(clay, "clay_front.png"))),
    ("Lateral", abre(os.path.join(clay, "clay_side.png"))),
    ("3/4", abre(os.path.join(clay, "clay_threequarter.png"))),
]
T, CW = 470, 700
folha = Image.new("RGB", (3 * CW, 2 * (T + 44) + 70), (32, 32, 36))
d = ImageDraw.Draw(folha)
for i, (t, im) in enumerate(paineis):
    x, y = (i % 3) * CW, (i // 3) * (T + 44)
    d.text((x + 10, y + 10), t, fill=(235, 235, 235))
    if im is None:
        d.text((x + 10, y + 200), "(sem imagem)", fill=(160, 160, 160))
        continue
    s = min(T / im.height, (CW - 20) / im.width)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))))
    folha.paste(im, (x + (CW - im.width) // 2, y + 34))
txt = "%s  |  medidas (studs): %s" % (esp, ", ".join("%s=%s" % (k, v) for k, v in md.items()))
d.text((10, 2 * (T + 44) + 12), txt[:330], fill=(255, 220, 120))
if gate:
    d.text((10, 2 * (T + 44) + 34), "faixas (modelo - ref, fracao da altura): %s" % gate.get("band_width_diff"), fill=(200, 200, 200))
out = os.path.join(R, "review", "Folha_%s.png" % esp)
folha.save(out)
print("FOLHA", out)
