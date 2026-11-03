"""Monta pranchas de revisao: referencia ao lado do render na camera aproximada, e as 4 vistas.
Uso: python prancha.py <dir_rodada>"""
import sys, os
from PIL import Image, ImageDraw
d = os.path.abspath(sys.argv[1]); aqui = os.path.dirname(os.path.abspath(__file__))
ref = Image.open(os.path.join(aqui, "ref", "urso-silvestre-referencia.png")).convert("RGB")
def rot(im, txt):
    dr = ImageDraw.Draw(im); dr.rectangle((0, 0, 8 * len(txt) + 16, 26), fill=(0, 0, 0)); dr.text((8, 7), txt, fill=(255, 255, 255)); return im
def lado_a_lado(a, b, ta, tb, nome, H=620):
    a = a.resize((int(a.width * H / a.height), H)); b = b.resize((int(b.width * H / b.height), H))
    o = Image.new("RGB", (a.width + b.width + 10, H), (20, 20, 20)); o.paste(rot(a, ta), (0, 0)); o.paste(rot(b, tb), (a.width + 10, 0))
    o.save(os.path.join(d, nome)); return nome
def abre(n): p = os.path.join(d, n + ".png"); return Image.open(p).convert("RGB") if os.path.exists(p) else None
if abre("pose_ref"): lado_a_lado(ref, abre("pose_ref"), "REFERENCIA", "MODELO (pose de teste)", "comparar_ref.png")
cab = ref.crop((1000, 0, 1672, 470))
if abre("pose_cab"): lado_a_lado(cab, abre("pose_cab"), "REFERENCIA (cabeca)", "MODELO (cabeca, pose de teste)", "comparar_cabeca.png", 560)
vs = [abre(n) for n in ("vista_frente", "vista_lado", "vista_tras", "vista_34")]
if all(vs):
    W, H = 960, 540; o = Image.new("RGB", (W * 2, H * 2))
    for i, (im, t) in enumerate(zip(vs, ("FRENTE", "LADO (direito)", "TRAS", "3/4"))):
        o.paste(rot(im.resize((W, H)), t), ((i % 2) * W, (i // 2) * H))
    o.save(os.path.join(d, "vistas.png"))
print("PRANCHA_OK", d)
