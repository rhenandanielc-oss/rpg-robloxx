"""Folha quadro a quadro do Bote nas 6 vistas. Uso: python e5_47_folha_bote.py [r3|r4]  (r4: r3 x r4 agachamento mais fundo, review/e5/bote_r4/)
(sem argumento: v1 x r2 em review/e5/bote_r2/; r3: r2 x r3 (impulso das traseiras, 45 studs) em review/e5/bote_r3/, com close da traseira)"""
import sys
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("arial.ttf", 24); f = ImageFont.truetype("arial.ttf", 17)
ETAPAS = [("agacha", 14), ("decola", 19), ("decola+1", 20), ("recolhe", 22), ("alcance no voo", 26), ("pre-pouso", 32), ("pouso", 35), ("absorve", 40)]
VISTAS = ["perfil", "frente", "34", "qa_livre", "close", "close_wire"]; VER = [("v1", "r2_Bote_v1"), ("r2", "r2_Bote")]; w, h = 360, 203; B = "review/e5/bote_r2/"
QV = None
if len(sys.argv) > 1 and sys.argv[1] == "r3":
    ETAPAS = ["agacha", "impulso", "traseiras decolam", "traseiras esticadas", "recolhe no voo", "pre-pouso", "pouso", "absorve"]
    QV = {"r2": [14, 18, 22, 23, 27, 32, 35, 40], "r3": [14, 20, 23, 26, 36, 47, 52, 62]}; ETAPAS = list(zip(ETAPAS, QV["r3"]))
    VISTAS = ["perfil", "34", "qa_livre", "close_tras", "close_tras_wire", "close"]; VER = [("r2", "r3_Bote_r2"), ("r3", "r3_Bote")]; B = "review/e5/bote_r3/"
if len(sys.argv) > 1 and sys.argv[1] == "r4":   # mesmos tempos nas duas versoes; muda so a profundidade do agachamento
    ETAPAS = [("agacha", 10), ("mais baixo", 16), ("impulso", 20), ("traseiras decolam", 23), ("traseiras esticadas", 26), ("recolhe no voo", 36), ("pouso", 52), ("absorve", 62)]
    QV = {"r3": [q for _, q in ETAPAS], "r4": [q for _, q in ETAPAS]}
    VISTAS = ["perfil", "frente", "34", "qa_livre", "close_tras", "close"]; VER = [("r3", "r4_Bote_r3"), ("r4", "r4_Bote")]; B = "review/e5/bote_r4/"
P = Image.new("RGB", (130 + len(ETAPAS) * w, 70 + len(VISTAS) * 2 * (h + 6)), (30, 30, 34)); d = ImageDraw.Draw(P)
d.text((12, 12), (("Bote - r3 (vermelho) x r4 agachamento 2,9 studs (azul)" if B.endswith("r4/") else "Bote - r2 15 studs (vermelho) x r3 45 studs com impulso das traseiras (azul)") if QV else "Bote - v1 (vermelho) x r2 (azul): dianteiras na decolagem, voo e pouso") + "; Blender, nada testado no Roblox", fill=(240, 220, 160), font=F)
for i, (e, q) in enumerate(ETAPAS): d.text((130 + i * w + 6, 44), e if QV else "%s q%d" % (e, q), fill=(235, 235, 235), font=f)
for j, (v, (rot, pasta)) in enumerate([(v, x) for v in VISTAS for x in VER]):
    y = 70 + j * (h + 6); d.text((8, y + 8), v[:12], fill=(235, 235, 235), font=f); d.text((8, y + 32), rot, fill=(230, 110, 100) if rot == VER[0][0] else (110, 170, 240), font=f)
    for i, (e, q) in enumerate(ETAPAS):
        q = QV[rot][i] if QV else q
        P.paste(Image.open(B + "%s/%s_%04d.png" % (pasta, v, q)).convert("RGB").resize((w, h)), (130 + i * w, y)); d.text((130 + i * w + 6, y + h - 22), "q%d" % q, fill=(255, 255, 0), font=f)
P.save(B + ("_folha_Bote_%s_%s.png" % (VER[0][0], VER[1][0]) if QV else "_folha_Bote_v1_r2.png")); print("FOLHA", P.size)
