"""Sobreposicao frontal (Python do sistema + PIL): malha base a 55% sobre fundo neutro, contornos de CORPO (amarelo),
JUBA/PEITO (ciano) e CABECA (magenta), linha central (vermelho) e eixos anatomicos (cranio branco, esterno verde,
coluna laranja, ombros/pelve azul). Uso: python sobrepor_frontal.py <pasta_analise> <titulo>"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
d = sys.argv[1]; tit = sys.argv[2] if len(sys.argv) > 2 else d
J = json.load(open(os.path.join(d, "analise.json"))); E = J["eixos_px"]; W, H = J["W"], J["H"]
base = Image.open(os.path.join(d, "base.png")).convert("RGBA")
fundo = Image.new("RGBA", (W, H), (70, 80, 70, 255)); fundo.alpha_composite(base)
out = Image.blend(Image.new("RGBA", (W, H), (70, 80, 70, 255)), fundo, 0.55)
def contorno(k, cor):
    m = Image.open(os.path.join(d, "mascara_%d.png" % k)).split()[-1].point(lambda a: 255 if a > 60 else 0)
    borda = m.filter(ImageFilter.MaxFilter(5)); borda = ImageChops.subtract(borda, m)
    camada = Image.new("RGBA", (W, H), cor); out.paste(camada, (0, 0), borda)
contorno(0, (255, 220, 40, 255)); contorno(1, (40, 230, 255, 255)); contorno(2, (255, 60, 220, 255))
dr = ImageDraw.Draw(out)
dr.line([(W / 2, 0), (W / 2, H)], fill=(255, 40, 40, 255), width=2)
dr.line(E["cranio"], fill=(255, 255, 255, 255), width=4); dr.line(E["orelhas"], fill=(255, 255, 255, 255), width=2)
if len(E["esterno"]) > 1: dr.line(E["esterno"], fill=(60, 255, 90, 255), width=4)
dr.line(E["coluna"], fill=(255, 150, 40, 255), width=3)
dr.line(E["pelve"], fill=(70, 140, 255, 255), width=3); dr.line(E["ombros"], fill=(70, 140, 255, 255), width=3)
try: f = ImageFont.truetype("arial.ttf", 20)
except Exception: f = ImageFont.load_default()
M = J["medidas"]
dr.text((10, 10), tit, fill=(255, 255, 255, 255), font=f)
dr.text((10, 36), "cranio inclin. %+.1f graus | nariz x %+.2f | orelhas meio x %+.2f dz %+.2f" % (M["cranio_inclinacao_graus"], M["nariz_x"], M["orelhas_meio_x"], M["orelhas_dz"]), fill=(255, 255, 255, 255), font=f)
dr.text((10, H - 120), "amarelo corpo | ciano juba/peito | magenta cabeca | vermelho linha central", fill=(255, 255, 255, 255), font=f)
dr.text((10, H - 94), "branco eixo do cranio | verde esterno | laranja coluna | azul ombros/pelve", fill=(255, 255, 255, 255), font=f)
j = [x for x in M["juba"] if 4.0 <= x["z"] <= 6.4]
if j:
    dr.text((10, H - 64), "juba z4-6.4: meio medio %+.2f, media %+.2f, fracao em +X %.0f%%" % (sum(x["meio"] for x in j) / len(j), sum(x["media"] for x in j) / len(j), 100 * sum(x["frac_dir_pos"] for x in j) / len(j)), fill=(255, 255, 255, 255), font=f)
dr.text((10, H - 38), "esterno x: " + " ".join("%+.2f" % x for x in M["esterno_x"]), fill=(255, 255, 255, 255), font=f)
out.convert("RGB").save(os.path.join(d, "Sobreposicao_frontal.png")); print(os.path.join(d, "Sobreposicao_frontal.png"))
