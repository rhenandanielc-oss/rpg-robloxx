# Prancha de revisao: referencia x blockout, vistas frente / lado / tres quartos.
# Uso: python prancha.py <passagem> <pasta_blockout>
# Regua: linhas a cada 0,25 u (Blender) a partir do chao; linha laranja = ombro (1,2 u).
# A referencia e normalizada pela altura do ombro (1,2 u), medida na propria vista.
import sys, os, json
from PIL import Image, ImageDraw, ImageFont

PASS = int(sys.argv[1]); PASTA = sys.argv[2]
RAIZ = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(RAIZ, "..", "..", "..", "REFERENCIAS", "floresta-ancestral", "cervo-do-bosque",
                   "cervo-do-bosque-referencia.png")
met = json.load(open(os.path.join(PASTA, f"p{PASS}_metricas.json"), encoding="utf-8"))
ref = Image.open(REF).convert("RGB")
F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t)
OMBRO = 1.2

def regua(img, chao_y, ppm, x0=None, sentido=-1, rotulo=True):
    d = ImageDraw.Draw(img); w, h = img.size
    k = 0
    while True:
        y = chao_y - k * 0.25 * ppm
        if y < 0: break
        d.line([(0, y), (w, y)], fill=(235, 215, 60) if k == 0 else (40, 40, 40), width=1)
        if rotulo and k: d.text((3, y - 13), f"{k*0.25:.2f}", fill=(20, 20, 20), font=F(11))
        k += 1
    yo = chao_y - OMBRO * ppm
    d.line([(0, yo), (w, yo)], fill=(240, 140, 30), width=2)
    if x0 is not None:  # linhas verticais a cada 0,25 u a partir do focinho/centro
        k = 0
        while 0 <= x0 + sentido * k * 0.25 * ppm <= w:
            x = x0 + sentido * k * 0.25 * ppm
            d.line([(x, 0), (x, h)], fill=(70, 70, 70) if k else (60, 130, 220), width=1)
            k += 1
    return img

def par(ref_img, ren_img, titulo, altura=620):
    a = ref_img.resize((int(ref_img.width * altura / ref_img.height), altura))
    b = ren_img.resize((int(ren_img.width * altura / ren_img.height), altura))
    out = Image.new("RGB", (a.width + b.width + 30, altura + 34), (60, 58, 56))
    out.paste(a, (10, 30)); out.paste(b, (a.width + 20, 30))
    d = ImageDraw.Draw(out)
    d.text((10, 6), f"{titulo} — referência", fill=(240, 240, 240), font=F(16))
    d.text((a.width + 20, 6), f"blockout p{PASS}", fill=(240, 240, 240), font=F(16))
    return out

# frente: recorte 1060..1300 x 440..1000; chao y=537,5; 0,004 u/px; centro x=116
rf = regua(ref.crop((1060, 440, 1300, 1000)), 537.5, 250, x0=116, sentido=1)
regua(rf, 537.5, 250, x0=116, sentido=-1, rotulo=False)
bf = Image.open(os.path.join(PASTA, f"p{PASS}_frente.png")).convert("RGB")
ppm = 840 / 2.3; regua(bf, 420 + 1.07 * ppm, ppm, x0=180, sentido=1); regua(bf, 420 + 1.07 * ppm, ppm, x0=180, sentido=-1, rotulo=False)
# lado: recorte 1000..1400 x 0..440; chao y=422,5; 0,005 u/px; focinho x=376
rl = regua(ref.crop((1000, 0, 1400, 440)), 422.5, 200, x0=376, sentido=-1)
bl = Image.open(os.path.join(PASTA, f"p{PASS}_lado.png")).convert("RGB")
ppm = 792 / 2.3; nariz_x = 360 + (-met["nariz_y"] - 0.12) * ppm
regua(bl, 396 + 1.07 * ppm, ppm, x0=nariz_x, sentido=-1)
# tres quartos: sem regua (perspectiva)
r3 = ref.crop((120, 0, 830, 1024))
b3 = Image.open(os.path.join(PASTA, f"p{PASS}_tres_quartos.png")).convert("RGB")

pares = [par(rf, bf, "Frente"), par(rl, bl, "Lado"), par(r3, b3, "Três quartos")]
W = sum(p.width for p in pares) + 10 * (len(pares) + 1)
H = max(p.height for p in pares) + 70
prancha = Image.new("RGB", (W, H), (45, 43, 42))
x = 10
for p in pares:
    prancha.paste(p, (x, 60)); x += p.width + 10
d = ImageDraw.Draw(prancha)
nome = {1: "Passagem 1 — silhueta, volumes e apoios (material neutro)",
        2: "Passagem 2 — traços de identidade + cores provisórias"}[PASS]
d.text((10, 8), f"Cervo-do-Bosque — blockout {nome}", fill=(250, 250, 250), font=F(22))
d.text((10, 36), "Régua: linhas a cada 0,25 u do Blender (amarela = chão, laranja = ombro 1,2 u, azul = focinho/centro). "
       "Referência normalizada pela altura do ombro em cada vista; escala em studs é PROPOSTA.",
       fill=(200, 200, 200), font=F(13))
saida = os.path.join(PASTA, f"prancha_p{PASS}.png")
prancha.save(saida); print(saida, prancha.size)
