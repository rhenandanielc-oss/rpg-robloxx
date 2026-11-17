"""Pranchas e video da revisao das garras v43 r5 (17/11/2026). Uso: python prancha_garra_r5.py (nesta pasta).
Saidas em review/v43r5/revisao/: comp_GarraE.jpg / comp_GarraD.jpg (referencia | r4 na pior fase | r5 sincronizada;
corpo inteiro, close lateral e de frente das patas, alvo de ensaio), bases_GarraE.jpg / bases_GarraD.jpg (r5 em Repouso,
Andar, Trote e Corrida), video_garras_r4_x_r5.mp4 (dois lados, quatro bases, velocidade real e metade)."""
import os, json, wave
from PIL import Image, ImageDraw, ImageFont
O = "review/v43r5"; R = os.path.join(O, "revisao"); os.makedirs(R, exist_ok=True)
REF = "../../../REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png"
try: FT = ImageFont.truetype("arial.ttf", 20); FG = ImageFont.truetype("arial.ttf", 30)
except Exception: FT = FG = ImageFont.load_default()
QA = json.load(open(os.path.join(R, "qa_garra_r5.json")))
w, h = 240, 165
Q = [0, 3, 5, 7, 9, 11, 13, 15]
COMP = {"GarraE": ("R4_GarraE__Andar3", "GarraE_Andar__Andar32"), "GarraD": ("R4_GarraD__Andar21", "GarraD_Andar__Andar14")}
for g, (r4, r5) in COMP.items():
    linhas = [(r4, "perfil_E", "r4 pior fase"), (r5, "perfil_E", "r5 sincronizada"), (r4, "pata", "r4 pata"), (r5, "pata", "r5 pata"),   # frente sem o alvo (tampava as patas)
              (r4, "frente_pata", "r4 frente"), (r5, "frente_pata", "r5 frente")]
    H0 = 190; img = Image.new("RGB", (150 + len(Q) * (w + 3), H0 + len(linhas) * (h + 3)), (36, 36, 40)); d = ImageDraw.Draw(img)
    rt = Image.open(REF).convert("RGB"); rt.thumbnail((290, H0 - 30)); img.paste(rt, (6, 26))
    d.text((6, 4), "%s sobre Andar - referencia | r4 (pior fase de inicio) x r5 (sincronizada no descolamento) - CONTATO q7 (vermelho) - alvo de ensaio em vermelho" % g, fill=(255, 235, 120), font=FT)
    for r, (pref, v, rot) in enumerate(linhas):
        y = H0 + r * (h + 3); d.text((4, y + h // 2 - 10), rot, fill=(255, 140, 120) if rot.startswith("r4") else (140, 255, 160), font=FT)
        for c, q in enumerate(Q):
            f = os.path.join(O, "comp", "%s__%s__q%02d.png" % (pref, v, q))
            if not os.path.exists(f): continue
            s = Image.open(f).convert("RGB"); s.thumbnail((w, h)); x = 150 + c * (w + 3); img.paste(s, (x, y))
            d.text((x + 3, y + 2), "q%d %.2fs" % (q, q / 30), fill=(255, 60, 60) if q == 7 else (255, 255, 255), font=FT)
    img.save(os.path.join(R, "comp_%s.jpg" % g), quality=88)
BASES = {"GarraE": [("GarraE__Repouso0", "Repouso"), ("GarraE_Andar__Andar32", "Andar"), ("GarraE_Trote__Trote8", "Trote"), ("GarraE_Corrida__Corrida10", "Corrida")],
         "GarraD": [("GarraD__Repouso0", "Repouso"), ("GarraD_Andar__Andar14", "Andar"), ("GarraD_Trote__Trote17", "Trote"), ("GarraD_Corrida__Corrida9", "Corrida")]}
QB = [0, 3, 7, 10, 13, 15]
for g, itens in BASES.items():
    linhas = [(p, v, b) for p, b in itens for v in ("perfil_E", "pata")]
    img = Image.new("RGB", (190 + len(QB) * (w + 3), 26 + len(linhas) * (h + 3)), (36, 36, 40)); d = ImageDraw.Draw(img)
    d.text((6, 4), "%s r5 - Repouso / Andar / Trote / Corrida (sincronizadas) - CONTATO q7" % g, fill=(255, 235, 120), font=FT)
    for r, (p, v, b) in enumerate(linhas):
        y = 26 + r * (h + 3); d.text((4, y + h // 2 - 10), "%s %s" % (b, "corpo" if v == "perfil_E" else "pata"), fill=(255, 235, 120), font=FT)
        for c, q in enumerate(QB):
            f = os.path.join(O, "bases", "%s__%s__q%02d.png" % (p, v, q))
            if not os.path.exists(f): continue
            s = Image.open(f).convert("RGB"); s.thumbnail((w, h)); x = 190 + c * (w + 3); img.paste(s, (x, y))
            d.text((x + 3, y + 2), "q%d" % q, fill=(255, 60, 60) if q == 7 else (255, 255, 255), font=FT)
    img.save(os.path.join(R, "bases_%s.jpg" % g), quality=88)
# video
S = os.path.join(O, "seq"); V = os.path.join(R, "video_quadros"); os.makedirs(V, exist_ok=True)
for f in os.listdir(V): os.remove(os.path.join(V, f))
n = 0
CHAVE = {"Repouso": ("GarraX|Repouso", "R4_GarraX|Repouso"), "Andar": ("GarraX_Andar|Andar", "R4_GarraX|Andar"),
         "Trote": ("GarraX_Trote|Trote", "R4_GarraX|Trote"), "Corrida": ("GarraX_Corrida|Corrida", "R4_GarraX_Corrida|Corrida")}
for vez, nome_vel in ((1, "velocidade real"), (2, "metade da velocidade")):
    for lado in ("E", "D"):
        for b in ("Repouso", "Andar", "Trote", "Corrida"):
            k5, k4 = [x.replace("GarraX", "Garra" + lado) for x in CHAVE[b]]
            q5 = QA.get(k5, {}); q4 = QA.get(k4, {})
            f5 = q5.get("fases", {}).get(str(q5.get("pior_fase")), {}); f4 = q4.get("fases", {}).get(str(q4.get("pior_fase")), {})
            info4 = "r4: afunda %.2f, salto fim %.2f, arrasto %.2f" % (f4.get("afund", 0), f4.get("salto_fim_extra", 0), f4.get("arrasto_extra", 0)) if f4 else ""
            info5 = "r5: afunda %.2f, salto fim %.2f, arrasto %.2f" % (f5.get("afund", 0), f5.get("salto_fim_extra", 0), f5.get("arrasto_extra", 0)) if f5 else ""
            for q in range(16):
                c = Image.new("RGB", (1920, 1080), (14, 15, 18)); d = ImageDraw.Draw(c)
                d.text((24, 12), "Garra%s sobre %s - %s - q%d%s" % (lado, b, nome_vel, q, "  CONTATO" if q == 7 else ""), fill=(255, 235, 140), font=FG)
                for (tag, v, x, y, ww, hh, rot) in (("r4_%s_%s" % (lado, b), "perfil_E", 20, 60, 930, 500, "r4 (pior fase de inicio)  " + info4),
                                                     ("r5_%s_%s" % (lado, b), "perfil_E", 970, 60, 930, 500, "r5 (sincronizada)  " + info5),
                                                     ("r5_%s_%s" % (lado, b), "pata", 495, 570, 930, 500, "r5 close das patas")):
                    f = os.path.join(S, "%s__%s__%04d.png" % (tag, v, q))
                    if os.path.exists(f):
                        s = Image.open(f).convert("RGB").resize((ww, hh)); c.paste(s, (x, y)); d.text((x + 8, y + 6), rot, fill=(255, 255, 255), font=FT)
                for _ in range(vez): n += 1; c.save(os.path.join(V, "q%05d.jpg" % n), quality=90)
ww = wave.open(os.path.join(R, "silencio.wav"), "wb"); ww.setnchannels(2); ww.setsampwidth(2); ww.setframerate(48000); ww.writeframes(b"\0" * 4 * int(48000 * n / 30 + 4800)); ww.close()
print("PRANCHA_GARRA_R5_OK quadros_video", n)
