# Pranchas das revisoes: python prancha_r1.py <A|B|ROSTO> <pasta> [versao=r1]
# Frente e lado: referencia e render na MESMA escala (400 px/u), chao e ombro na mesma linha.
# A referencia so recebe escala uniforme (1,6x na frente, 2x no perfil), nunca esticada.
# Tres quartos: render escalado para a mesma altura do animal da referencia, base alinhada.
import sys, os
from PIL import Image, ImageDraw, ImageFont

PASS = sys.argv[1]; PASTA = sys.argv[2]; V = sys.argv[3] if len(sys.argv) > 3 else "r1"
RAIZ = os.path.dirname(os.path.abspath(__file__))
REF = Image.open(os.path.join(RAIZ, "..", "..", "..", "REFERENCIAS", "floresta-ancestral", "cervo-do-bosque",
                              "cervo-do-bosque-referencia.png")).convert("RGB")
BG = (125, 116, 111)
F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t)
PPM, TOPO = 400, 2.15
CHAO_Y = TOPO * PPM; OMBRO_Y = CHAO_Y - 1.2 * PPM

def carrega(n):
    im = Image.open(os.path.join(PASTA, f"{V}_{PASS}_{n}.png")).convert("RGBA")
    base = Image.new("RGBA", im.size, BG + (255,)); base.alpha_composite(im); return base.convert("RGB"), im
def recorte_pad(img, caixa):
    x0, y0, x1, y1 = caixa
    out = Image.new("RGB", (round(x1 - x0), round(y1 - y0)), BG)
    out.paste(img.crop((max(0, round(x0)), max(0, round(y0)), round(x1), round(y1))), (max(0, -round(x0)), max(0, -round(y0))))
    return out
def regua(img, x0=None, sentido=-1):
    d = ImageDraw.Draw(img); w, h = img.size; k = 0
    while CHAO_Y - k * 0.25 * PPM > 0:
        y = CHAO_Y - k * 0.25 * PPM
        d.line([(0, y), (w, y)], fill=(235, 215, 60) if k == 0 else (45, 45, 45), width=1)
        if k: d.text((3, y - 14), f"{k * 0.25:.2f}", fill=(25, 25, 25), font=F(12))
        k += 1
    d.line([(0, OMBRO_Y), (w, OMBRO_Y)], fill=(240, 140, 30), width=2)
    if x0 is not None:
        k = 0
        while 0 <= x0 + sentido * k * 0.25 * PPM <= w:
            x = x0 + sentido * k * 0.25 * PPM
            d.line([(x, 0), (x, h)], fill=(60, 130, 220) if k == 0 else (70, 70, 70), width=1); k += 1
    return img
def rotulo(img, txt):
    out = Image.new("RGB", (img.width, img.height + 26), (55, 53, 51)); out.paste(img, (0, 26))
    ImageDraw.Draw(out).text((6, 5), txt, fill=(240, 240, 240), font=F(15)); return out
def lado_a_lado(*imgs, gap=8, fundo=(55, 53, 51)):
    W = sum(i.width for i in imgs) + gap * (len(imgs) - 1); H = max(i.height for i in imgs)
    out = Image.new("RGB", (W, H), fundo); x = 0
    for i in imgs: out.paste(i, (x, 0)); x += i.width + gap
    return out
def empilha(*imgs, gap=10, fundo=(45, 43, 42)):
    W = max(i.width for i in imgs); H = sum(i.height for i in imgs) + gap * (len(imgs) - 1)
    out = Image.new("RGB", (W, H), fundo); y = 0
    for i in imgs: out.paste(i, (0, y)); y += i.height + gap
    return out
def bbox_ref(img, bg=None, lim=38):
    px = img.load(); w, h = img.size; bg = bg or px[5, 5]
    xs, ys = [], []
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            p = px[x, y]
            if abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > lim: xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)

if PASS == "ROSTO":
    # referencia: rosto da vista 3/4 (alta resolucao) e da vista lateral (ampliada 4x, so escala uniforme)
    def fundo(n):
        im = Image.open(os.path.join(PASTA, f"{V}_B_rosto_{n}.png")).convert("RGBA")
        b = Image.new("RGBA", im.size, BG + (255,)); b.alpha_composite(im); return b.convert("RGB")
    r34 = REF.crop((520, 150, 800, 368)).resize((900, 700), Image.LANCZOS)
    rlado = REF.crop((1305, 95, 1395, 165)).resize((900, 700), Image.LANCZOS)
    l1 = lado_a_lado(rotulo(r34, "3/4 · referência"), rotulo(fundo("34"), f"3/4 · {V} B"))
    l2 = lado_a_lado(rotulo(rlado, "Perfil · referência (ampliada)"), rotulo(fundo("lado"), f"Perfil · {V} B"))
    topo = Image.new("RGB", (l1.width, 64), (45, 43, 42)); d = ImageDraw.Draw(topo)
    d.text((10, 6), f"Cervo-do-Bosque — revisão {V} · rosto: boca, olhos" + (" e nariz" if V not in ("r1", "r2") else ""), fill=(250, 250, 250), font=F(22))
    if V.startswith("m"):
        d.text((10, 38), "Malha bruta do Meshy: olhos, nariz com narinas, boca e orelhas vêm esculpidos e pintados na própria malha/textura. EEVEE, luz neutra.", fill=(205, 205, 205), font=F(13))
    else: d.text((10, 38), "Olho: globo com íris castanho-escura, pupila horizontal, córnea brilhante, pálpebras escuras, aro claro e glândula pré-orbital pintada. "
           "Boca: linha dos lábios com lábio escuro pintado." + (" Nariz: rinário úmido embutido no focinho, narinas em vírgula e sulco." if V not in ("r1", "r2") else "") + " EEVEE, luz neutra.", fill=(205, 205, 205), font=F(13))
    saida = os.path.join(PASTA, f"{V}_prancha_rosto.png"); empilha(topo, l1, l2).save(saida); print(saida); sys.exit()
nome_pass = {"A": "silhueta (material neutro, Workbench)", "B": "estudo de pelagem (EEVEE, luz neutra)"}[PASS]
if V.startswith("m"): nome_pass += " — malha bruta do Meshy"
# --- frente: ref 0,004 u/px -> x1,6 ---
rf = recorte_pad(REF, (1056, 977.5 - TOPO * 250, 1296, 977.5 + 0.10 * 250)).resize((384, 900), Image.LANCZOS)
bf, _ = carrega("frente")
rf = regua(rf, 192, 1); regua(rf, 192, -1); bf = regua(bf, 192, 1); regua(bf, 192, -1)
# --- lado: ref 0,005 u/px -> x2; focinho 0,1 u da borda direita nos dois ---
rl = recorte_pad(REF, (996, 422.5 - TOPO * 200, 1396, 422.5 + 0.10 * 200)).resize((800, 900), Image.LANCZOS)
bl, _ = carrega("lado")
rl = regua(rl, 760, -1); bl = regua(bl, 760, -1)
# --- tres quartos ---
r3 = REF.crop((120, 0, 830, 1024))
x0, y0, x1, y1 = bbox_ref(r3)
b3c, b3a = carrega("tres_quartos")
bb = b3a.getchannel("A").getbbox()
esc = (y1 - y0) / (bb[3] - bb[1])
corte = b3a.crop(bb); corte = corte.resize((round(corte.width * esc), round(corte.height * esc)), Image.LANCZOS)
b3 = Image.new("RGBA", r3.size, BG + (255,))
b3.alpha_composite(corte, (round((x0 + x1) / 2 - corte.width / 2), round(y1 - corte.height)))
b3 = b3.convert("RGB")
for im in (r3, b3):
    d = ImageDraw.Draw(im); d.line([(0, y1), (im.width, y1)], fill=(235, 215, 60)); d.line([(0, y0), (im.width, y0)], fill=(60, 130, 220))

linha1 = lado_a_lado(rotulo(rf, "Frente · referência"), rotulo(bf, f"{V} {PASS}"), rotulo(rl, "Perfil · referência"),
                     rotulo(bl, f"{V} {PASS}"), rotulo(r3.resize((621, 900)), "3/4 · referência"),
                     rotulo(b3.resize((621, 900)), f"{V} {PASS}"), gap=6)

# --- linha 2 ---
def mini(nome_arq):
    im = Image.open(os.path.join(PASTA, nome_arq)).convert("RGBA")
    base = Image.new("RGBA", im.size, BG + (255,)); base.alpha_composite(im); return base.convert("RGB")
ref_mini = REF.crop((120, 0, 830, 1024)).resize((122, 176), Image.LANCZOS)
m_r1 = mini(f"{V}_{PASS}_miniatura.png")
def amplia(im, k=3): return im.resize((im.width * k, im.height * k), Image.NEAREST)
bloco_mini = lado_a_lado(rotulo(lado_a_lado(ref_mini, m_r1), "Miniatura real (176 px)"),
                         rotulo(lado_a_lado(amplia(ref_mini), amplia(m_r1)), "Miniatura ampliada 3x (pixels)"))
itens = [bloco_mini]
if PASS == "A":
    if os.path.exists(os.path.join(PASTA, f"{V}_A_apoios.png")):
      ap = Image.open(os.path.join(PASTA, f"{V}_A_apoios.png")).convert("RGB")
      itens.append(rotulo(ap.resize((round(ap.width * 554 / ap.height), 554)), "Apoios: 4 cascos no plano (Z mín = 0,000; sem interpenetração)"))
else:
    # recortes comparaveis (mesma janela, perfil alinhado): cabeca+peito e dorso+flanco
    def janela(img, y_atras, y_frente, z_lo, z_hi):  # distancias atras do focinho (u)
        return img.crop((round(760 - y_atras * PPM), round(CHAO_Y - z_hi * PPM), round(760 - y_frente * PPM), round(CHAO_Y - z_lo * PPM)))
    rl0 = recorte_pad(REF, (996, 422.5 - TOPO * 200, 1396, 422.5 + 0.10 * 200)).resize((800, 900), Image.LANCZOS)
    bl0, _ = carrega("lado")
    cab = [janela(i, 0.62, -0.08, 0.80, 1.72) for i in (rl0, bl0)]
    flc = [janela(i, 1.55, 0.50, 0.62, 1.30) for i in (rl0, bl0)]
    cab = [c.resize((round(c.width * 554 / c.height), 554), Image.LANCZOS) for c in cab]
    flc = [c.resize((round(c.width * 300 / c.height), 300), Image.LANCZOS) for c in flc]
    itens.append(rotulo(lado_a_lado(*cab), f"Recorte cabeça + peito (ref | {V} B)"))
    itens.append(rotulo(empilha(*flc, gap=6), f"Recorte dorso + flanco (ref em cima | {V} B)"))
    if os.path.exists(os.path.join(PASTA, f"{V}_B_arame.png")):
        ar = Image.open(os.path.join(PASTA, f"{V}_B_arame.png")).convert("RGBA")
        arb = Image.new("RGBA", ar.size, BG + (255,)); arb.alpha_composite(ar)
        itens.append(rotulo(arb.convert("RGB").resize((round(ar.width * 554 / ar.height), 554)), "Arame (malha final)"))
linha2 = lado_a_lado(*itens, gap=10)

topo = Image.new("RGB", (max(linha1.width, linha2.width), 64), (45, 43, 42)); d = ImageDraw.Draw(topo)
d.text((10, 6), f"Cervo-do-Bosque — revisão {V} · passagem {PASS}: {nome_pass}", fill=(250, 250, 250), font=F(22))
d.text((10, 38), "Frente/perfil: mesma escala (400 px/u), referência só com escala uniforme. Linhas a cada 0,25 u; amarela = chão; "
       "laranja = ombro 1,2 u (PROPOSTA); azul = centro/focinho. 3/4: mesma altura total do animal, base alinhada.",
       fill=(205, 205, 205), font=F(13))
saida = os.path.join(PASTA, f"{V}_prancha_{PASS}.png")
empilha(topo, linha1, linha2).save(saida); print(saida)
