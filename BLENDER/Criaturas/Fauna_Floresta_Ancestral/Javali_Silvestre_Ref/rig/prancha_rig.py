"""Prancha das provas do rig piloto do javali. Uso: python prancha_rig.py <pasta_rig>"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
P = sys.argv[1]; F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t)
R = json.load(open(os.path.join(P, "rig_relatorio.json"), encoding="utf-8")); M = R["provas"]
def f(n, h):
    im = Image.open(os.path.join(P, n)).convert("RGB"); return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
def rot(im, t):
    o = Image.new("RGB", (im.width, im.height + 24), (55, 53, 51)); o.paste(im, (0, 24)); ImageDraw.Draw(o).text((6, 4), t, fill=(240, 240, 240), font=F(14)); return o
def lin(ims, gap=6):
    o = Image.new("RGB", (sum(i.width for i in ims) + gap * (len(ims) - 1), max(i.height for i in ims)), (45, 43, 42)); x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width + gap
    return o
def met(n): m = M[n]; return f"{n} · menor z malha {m['min_z_malha']*100:+.1f} cm · cabeça {m['min_z_cabeca']*100:.1f} cm"
H = 250
L = [lin([rot(f("prova_apoio_lado.png", H), met("apoio")), rot(f("prova_apoio_34.png", H), "apoio · 3/4"), rot(f("prova_apoio_frente.png", H), "apoio · frente")]),
     lin([rot(f("prova_passada_lado.png", H), met("passada")), rot(f("prova_passada_close_ombro.png", H), "passada · ombro/cotovelo/carpo"), rot(f("prova_passada_close_quadril_jarrete.png", H), "passada · quadril/soldra/jarrete")]),
     lin([rot(f("prova_giro_34.png", H), met("giro")), rot(f("prova_giro_frente.png", H), "giro · frente"), rot(f("prova_reacao_34.png", H), met("reacao"))]),
     lin([rot(f("prova_focinho_baixo_lado.png", H), met("focinho_baixo") + f" · pescoço {R['focinho_baixo_angulo_pescoco']}°"), rot(f("prova_focinho_baixo_34.png", H), "focinho baixo · 3/4"), rot(f("prova_focinho_baixo_frente.png", H), "focinho baixo · frente (presas × chão)")])]
W = max(l.width for l in L); topo = Image.new("RGB", (W, 58), (45, 43, 42)); d = ImageDraw.Draw(topo)
d.text((10, 5), "Javali Silvestre — rig piloto (poses de prova estáticas)", fill=(250, 250, 250), font=F(21))
mm = R["malhas"]; d.text((10, 35), f"{len(R['ossos'])} ossos ({R['deformam']} deformam) · {sum(v['tris'] for v in mm.values())} tris · máx. {max(v['max_influencias'] for v in mm.values())} influências · sem peso {sum(v['sem_peso'] for v in mm.values())} · chão quadriculado 10 cm", fill=(205, 205, 205), font=F(13))
o = Image.new("RGB", (W, 58 + sum(l.height + 6 for l in L)), (45, 43, 42)); o.paste(topo, (0, 0)); y = 58
for l in L: o.paste(l, (0, y)); y += l.height + 6
o.save(os.path.join(P, "prancha_rig.png")); print(o.size)
