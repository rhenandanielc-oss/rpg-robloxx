"""Pranchas e quadros de video da revisao v43 r4 x r3 (17/11/2026). Uso: python prancha_ataque_r4.py (nesta pasta).
Saidas em review/v43r4/revisao/: comp_<golpe>.jpg (referencia + r3 x r4, corpo inteiro e closes), bases_<golpe>.jpg
(r4 sobre Repouso/Andar/Trote/Corrida em fases diferentes) e as pastas de quadros 1920x1080 dos videos (normal + lenta)."""
import os, re, wave
from PIL import Image, ImageDraw, ImageFont
O = "review/v43r4"; R = os.path.join(O, "revisao"); os.makedirs(R, exist_ok=True)
REF = "../../../REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png"
try: FT = ImageFont.truetype("arial.ttf", 20); FG = ImageFont.truetype("arial.ttf", 30)
except Exception: FT = FG = ImageFont.load_default()
CONT = {"Mordida1": 6, "Mordida2": 6, "GarraE": 7, "GarraD": 7}
Q = [0, 3, 4, 5, 6, 7, 9, 12]
w, h = 240, 165
def ref_thumb(hh):
    im = Image.open(REF).convert("RGB"); im.thumbnail((int(hh * 1.8), hh)); return im
for g in CONT:
    vistas = ["perfil_E", "cabeca", "frente"] if g.startswith("Mordida") else ["perfil_E", "pata"]
    linhas = [(ver, v) for v in vistas for ver in ("R3_" + g, g)]
    H0 = 190
    img = Image.new("RGB", (130 + len(Q) * (w + 3), H0 + len(linhas) * (h + 3)), (36, 36, 40)); d = ImageDraw.Draw(img)
    rt = ref_thumb(H0 - 30); img.paste(rt, (6, 26))
    d.text((6, 4), "%s - referencia | r3 (antes) x r4 (correcao) sobre Andar - 30 q/s - CONTATO q%d (vermelho)" % (g, CONT[g]), fill=(255, 235, 120), font=FT)
    for r, (ac, v) in enumerate(linhas):
        y = H0 + r * (h + 3); d.text((4, y + h // 2 - 10), ("r3 " if ac.startswith("R3_") else "r4 ") + v, fill=(255, 140, 120) if ac.startswith("R3_") else (140, 255, 160), font=FT)
        for c, q in enumerate(Q):
            f = os.path.join(O, "comp", "%s__Andar6__%s__q%02d.png" % (ac, v, q))
            if not os.path.exists(f): continue
            s = Image.open(f).convert("RGB"); s.thumbnail((w, h)); x = 130 + c * (w + 3); img.paste(s, (x, y))
            d.text((x + 3, y + 2), "q%d %.2fs" % (q, q / 30), fill=(255, 60, 60) if q == CONT[g] else (255, 255, 255), font=FT)
    img.save(os.path.join(R, "comp_%s.jpg" % g), quality=88)
BASES = ["Repouso0", "Andar0", "Andar18", "Trote9", "Corrida7"]; QB = [0, 4, 6, 7, 10]   # Corrida = variante _Corrida
for g in CONT:
    img = Image.new("RGB", (130 + len(QB) * (w + 3), 26 + len(BASES) * (h + 3)), (36, 36, 40)); d = ImageDraw.Draw(img)
    d.text((6, 4), "%s r4 sobre a locomocao em fases diferentes (perfil) - CONTATO q%d" % (g, CONT[g]), fill=(255, 235, 120), font=FT)
    for r, b in enumerate(BASES):
        y = 26 + r * (h + 3); d.text((4, y + h // 2 - 10), b, fill=(255, 235, 120), font=FT)
        for c, q in enumerate(QB):
            f = os.path.join(O, "bases", "%s__%s__perfil_E__q%02d.png" % (g + ("_Corrida" if b.startswith("Corrida") else ""), b, q))
            if not os.path.exists(f): continue
            s = Image.open(f).convert("RGB"); s.thumbnail((w, h)); x = 130 + c * (w + 3); img.paste(s, (x, y))
            d.text((x + 3, y + 2), "q%d" % q, fill=(255, 60, 60) if q == CONT[g] else (255, 255, 255), font=FT)
    img.save(os.path.join(R, "bases_%s.jpg" % g), quality=88)
# ---- quadros dos videos: r3 | r4 lado a lado (perfil em cima, close embaixo), depois r4 em Trote e Corrida
S = os.path.join(O, "seq"); V = os.path.join(R, "video_quadros"); os.makedirs(V, exist_ok=True)
for f in os.listdir(V): os.remove(os.path.join(V, f))
SEQ = ["Mordida1", "GarraE", "Mordida2", "GarraD"]
n = 0
def quadro(paineis, titulo):
    global n
    c = Image.new("RGB", (1920, 1080), (14, 15, 18)); d = ImageDraw.Draw(c); d.text((24, 14), titulo, fill=(255, 235, 140), font=FG)
    for (im, x, y, ww, hh, rot) in paineis:
        if im is None: continue
        s = Image.open(im).convert("RGB").resize((ww, hh)); c.paste(s, (x, y)); d.text((x + 8, y + 6), rot, fill=(255, 255, 255), font=FT)
    for _ in range(VEZ): n += 1; c.save(os.path.join(V, "q%05d.jpg" % n), quality=90)
for VEZ, nome in ((1, "velocidade real"), (2, "metade da velocidade")):
    for i in range(60):
        g = SEQ[i // 15]; q = i % 15; lab = "%s q%d%s" % (g, q, "  CONTATO" if q == CONT[g] else "")
        P = lambda tag, v: os.path.join(S, "%s__%s__%04d.png" % (tag, v, i))
        quadro([(P("r3_andar", "perfil_E"), 20, 70, 930, 500, "r3 (antes) - " + lab), (P("r4_andar", "perfil_E"), 970, 70, 930, 500, "r4 (correcao) - " + lab),
                (P("r3_andar", "cabeca"), 20, 575, 930, 495, "r3 close"), (P("r4_andar", "cabeca"), 970, 575, 930, 495, "r4 close")],
               "Ataque basico: sequencia Mordida1 > GarraE > Mordida2 > GarraD sobre ANDAR - %s" % nome)
    for i in range(60):
        g = SEQ[i // 15]; q = i % 15; lab = "%s q%d%s" % (g, q, "  CONTATO" if q == CONT[g] else "")
        P = lambda tag, v: os.path.join(S, "%s__%s__%04d.png" % (tag, v, i))
        quadro([(P("r4_corrida", "perfil_E"), 20, 70, 930, 500, "r4 Corrida (variante _Corrida) - " + lab), (P("r4_corrida", "pata"), 970, 70, 930, 500, "r4 Corrida close patas"),
                (P("r4_trote", "perfil_E"), 495, 575, 930, 495, "r4 Trote - " + lab)],
               "Ataque basico r4 sobre TROTE e CORRIDA - %s" % nome)
ww = wave.open(os.path.join(R, "silencio.wav"), "wb"); ww.setnchannels(2); ww.setsampwidth(2); ww.setframerate(48000); ww.writeframes(b"\0" * 4 * int(48000 * n / 30 + 4800)); ww.close()
print("PRANCHA_R4_OK quadros_video", n)
