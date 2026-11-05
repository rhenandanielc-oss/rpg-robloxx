"""Folhas quadro a quadro da Patada (antes x depois): preparo, maior elevacao, pre-contato, contato, seguimento, recuperacao.
Uso: python e5_45_folha_patada.py [r3]   (sem argumento: v1 x r2 em review/e5/patada_r2/; com r3: r2 x r3, saida em review/e5/patada_r3/)"""
import sys
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("arial.ttf", 24); f = ImageFont.truetype("arial.ttf", 17)
ETAPAS = ["preparo", "maior elevacao", "pre-contato", "contato", "seguimento", "recuperacao"]
QUADROS = {"antes": [8, 21, 23, 25, 27, 34], "depois": [8, 24, 26, 28, 30, 38]}   # v1: golpe em 0,30-1,18 s; r2/r3: 0,32-1,36 s, contato 0,90 s
VISTAS = ["perfil", "frente", "34", "qa_livre", "close", "close_wire"]; w, h = 400, 225; B = "review/e5/patada_r2/"
R3 = len(sys.argv) > 1 and sys.argv[1] == "r3"
VER = [("antes", "v1", B), ("depois", "r2", B)] if not R3 else [("depois", "r2 (pesos antigos)", B), ("r3", "r3", "review/e5/patada_r3/")]
QUADROS["r3"] = QUADROS["depois"]
for lado in "DE":
    linhas = [(v, ver) for v in VISTAS for ver in VER]
    P = Image.new("RGB", (150 + 6 * w, 70 + len(linhas) * (h + 6)), (30, 30, 34)); d = ImageDraw.Draw(P)
    d.text((12, 12), "Patada_%s - %s (vermelho) x %s (azul); Blender, nada testado no Roblox" % (lado, VER[0][1], VER[1][1]), fill=(240, 220, 160), font=F)
    for i, e in enumerate(ETAPAS): d.text((150 + i * w + 6, 44), e, fill=(235, 235, 235), font=f)
    for j, (v, ver) in enumerate(linhas):
        y = 70 + j * (h + 6); d.text((8, y + 8), v, fill=(235, 235, 235), font=f)
        d.text((8, y + 32), ver[1][:12], fill=(230, 110, 100) if ver is VER[0] else (110, 170, 240), font=f)
        for i, q in enumerate(QUADROS[ver[0]]):
            im = Image.open(ver[2] + "%s_Patada_%s/%s_%04d.png" % (ver[0], lado, v, q)).convert("RGB").resize((w, h)); P.paste(im, (150 + i * w, y))
            d.text((150 + i * w + 6, y + h - 22), "q%d" % q, fill=(255, 255, 255), font=f)
    P.save(VER[1][2] + ("_folha_Patada_%s_r2_r3.png" if R3 else "_folha_Patada_%s_antes_depois.png") % lado); print("FOLHA", lado, P.size)
    if R3:   # subida e armada em close com wireframe (onde estava a contorcao do print): q12..q26
        Q = list(range(12, 27, 2)); P2 = Image.new("RGB", (150 + len(Q) * w, 70 + 2 * (h + 6)), (30, 30, 34)); d2 = ImageDraw.Draw(P2)
        d2.text((12, 12), "Patada_%s - close com wireframe na subida/armada: r2 (pesos antigos) x r3" % lado, fill=(240, 220, 160), font=F)
        for j, (pre, rot, pasta) in enumerate(VER):
            y = 70 + j * (h + 6); d2.text((8, y + 8), rot[:14], fill=(235, 235, 235), font=f)
            for i, q in enumerate(Q):
                P2.paste(Image.open(pasta + "%s_Patada_%s/close_wire_%04d.png" % (pre, lado, q)).convert("RGB").resize((w, h)), (150 + i * w, y)); d2.text((150 + i * w + 6, y + h - 22), "q%d" % q, fill=(255, 255, 0), font=f)
        P2.save(VER[1][2] + "_close_subida_Patada_%s_r2_r3.png" % lado)
