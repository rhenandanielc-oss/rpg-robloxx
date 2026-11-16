"""Pranchas de revisao do Lobo Artico: referencia ao lado do render (enquadramento comparavel) e as vistas.
Uso: python prancha.py <dir_rodada>"""
import sys, os
from PIL import Image, ImageDraw
d = os.path.abspath(sys.argv[1]); aqui = os.path.dirname(os.path.abspath(__file__))
ref = Image.open(os.path.join(aqui, "ref", "lobo-artico-referencia.png")).convert("RGB")
def rot(im, txt):
    dr = ImageDraw.Draw(im); dr.rectangle((0, 0, 7 * len(txt) + 16, 24), fill=(0, 0, 0)); dr.text((8, 6), txt, fill=(255, 255, 255)); return im
def abre(n):
    p = os.path.join(d, "vista_%s.png" % n); return Image.open(p).convert("RGB") if os.path.exists(p) else None
def lado_a_lado(a, b, ta, tb, nome, H=620):
    a = a.resize((int(a.width * H / a.height), H)); b = b.resize((int(b.width * H / b.height), H))
    o = Image.new("RGB", (a.width + b.width + 10, H), (20, 20, 20)); o.paste(rot(a, ta), (0, 0)); o.paste(rot(b, tb), (a.width + 10, 0))
    o.save(os.path.join(d, nome)); print("PRANCHA", nome)
# recortes da referencia para os detalhes (coordenadas da imagem 1672x941)
RECORTES = {"rosto": (250, 20, 760, 430), "ombro": (560, 160, 1000, 560), "cristais": (600, 120, 960, 400)}
if abre("pose_ref"): lado_a_lado(ref, abre("pose_ref"), "REFERENCIA", "MODELO (camera aproximada, luz neutra)", "comparar_ref.png")
for k, cx in RECORTES.items():
    if abre(k): lado_a_lado(ref.crop(cx), abre(k), "REFERENCIA (%s)" % k, "MODELO (%s)" % k, "comparar_%s.png" % k, 520)
vs = [(abre(n), t) for n, t in (("frente", "FRENTE"), ("lado", "LADO ESQUERDO (visivel na ref)"), ("tras", "TRAS"),
                                ("34", "3/4 (frente-direita, lado oculto)"), ("lado_d", "LADO DIREITO (oculto: proposta)"))]
vs = [(im, t) for im, t in vs if im]
if vs:
    W, H = 800, 450; cols = 2; rows = (len(vs) + 1) // 2; o = Image.new("RGB", (W * cols, H * rows), (20, 20, 20))
    for i, (im, t) in enumerate(vs): o.paste(rot(im.resize((W, H)), t), ((i % cols) * W, (i // cols) * H))
    o.save(os.path.join(d, "vistas.png")); print("PRANCHA vistas.png")
