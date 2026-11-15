"""Prancha das provas do rig piloto da coruja. Uso: python prancha_rig.py <pasta_rig>"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
P = sys.argv[1]; F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t); R = json.load(open(os.path.join(P, "rig_relatorio.json"), encoding="utf-8"))
NOMES = [("repouso_T", "repouso (pose de rig, asas abertas)"), ("asas_fechadas", "asas fechadas (pousada) — resolvida por alvos"),
         ("batida_alto", "batida: asas no alto (no ar, +0,30 u)"), ("batida_baixo", "batida: asas embaixo (no ar)"),
         ("cabeca_virada", "cabeça virada 120° (pescoço + cabeça)"), ("cauda_leque", "cauda em leque (sobe e abre)")]
VS = [("frente", "frente"), ("34", "3/4"), ("lado", "perfil"), ("cima", "de cima/trás")]
W, H = 330, 235; linhas = []
for n, t in NOMES:
    o = Image.new("RGB", (W * 4 + 18, H + 24), (45, 43, 42)); d = ImageDraw.Draw(o)
    d.text((6, 4), f"{t} · menor z da malha {R['provas_min_z_cm'][n]:.1f} cm", fill=(240, 240, 240), font=F(14))
    for i, (v, vt) in enumerate(VS): im = Image.open(os.path.join(P, f"prova_{n}_{v}.png")).convert("RGB").resize((W, H)); o.paste(im, (i * (W + 6), 24))
    linhas.append(o)
topo = Image.new("RGB", (W * 4 + 18, 56), (45, 43, 42)); d = ImageDraw.Draw(topo)
d.text((8, 5), "Coruja-da-Floresta — rig piloto de ave (poses de prova estáticas)", fill=(250, 250, 250), font=F(21))
mm = R["malhas"]; d.text((8, 33), f"{len(R['ossos'])} ossos ({R['deformam']} deformam) · {sum(v['tris'] for v in mm.values())} tris · máx. {max(v['max_influencias'] for v in mm.values())} influências · sem peso {sum(v['sem_peso'] for v in mm.values())} · costura {R['costura'][0]}/{R['costura'][1]}", fill=(205, 205, 205), font=F(13))
out = Image.new("RGB", (topo.width, 56 + sum(l.height + 4 for l in linhas)), (45, 43, 42)); out.paste(topo, (0, 0)); y = 56
for l in linhas: out.paste(l, (0, y)); y += l.height + 4
out.save(os.path.join(P, "prancha_rig.png")); print(out.size)
