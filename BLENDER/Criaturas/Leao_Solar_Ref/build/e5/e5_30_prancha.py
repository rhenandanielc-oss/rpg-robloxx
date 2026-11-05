"""Prancha E5: referencia | E3b (aprovada) | E5 (malha E4b, rig de producao) em repouso; folhas de quadros de cada clipe da
Fase A (perfil e 3/4); poses de deformacao do rig final; tabela de QA. Uso: python e5_30_prancha.py <ref.png> <saida.png>"""
import sys, json, glob, os
from PIL import Image, ImageDraw, ImageFont
REF, SAIDA = sys.argv[1:3]; ref = Image.open(REF).convert("RGB")
F = ImageFont.truetype("arial.ttf", 26); f = ImageFont.truetype("arial.ttf", 18); fm = ImageFont.truetype("consola.ttf", 15)
def sob(p, t=None):
    im = Image.open(p).convert("RGBA"); b = Image.new("RGBA", im.size, (220, 213, 207, 255)); b.alpha_composite(im); b = b.convert("RGB")
    return b.resize(t, Image.LANCZOS) if t else b
def alt(im, h): return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
blocos = []
blocos.append(("repouso: referencia | E3b aprovada | E5 (quadro 1 do Repouso_Vigilante, chao e sombra)",
               [alt(ref.crop((0, 0, 1217, 594)), 300), alt(sob("review/e3c/geral/lado.png"), 300), alt(Image.open("review/e5/faseA/Repouso_Vigilante/perfil_0001.png").convert("RGB"), 300)]))
D = {}
for j in glob.glob("review/e5/faseA/clipes_*.json"): D.update(json.load(open(j)))
ORDEM = ["Repouso_Vigilante", "Repouso_Relaxado", "Observar_Farejar", "Andar", "Trote", "Corrida", "Repouso_para_Andar", "Andar_para_Repouso",
         "Andar_para_Trote", "Trote_para_Andar", "Trote_para_Corrida", "Corrida_para_Trote", "Arrancada", "Frenagem", "Virar_E", "Virar_D"]
for n in ORDEM:
    blocos.append((n, [Image.open("review/e5/faseA/_folha_%s.png" % n).convert("RGB")]))
blocos.append(("rig final: dobra de cotovelo, punho, passo dianteiro, pescoco virado, boca 32 graus (repouso | posado | arame)", [Image.open("review/e5/_poses_rig.png").convert("RGB")]))
linhas = ["%-19s %4s %6s %5s %8s %7s %8s %9s %s" % ("clipe", "q", "dur_s", "loop", "v st/s", "desl", "ik_max", "esc_max", "zmin")]
for n in ORDEM:
    d = D[n]; linhas.append("%-19s %4d %6.2f %5s %8.1f %7.1f %8.3f %9.3f %.2f" % (n, d["quadros"], d["duracao_s"], "sim" if d["loop"] else "nao", d["velocidade_studs_s"],
                            d["deslocamento_raiz"][1], d["erro_ik_max"], max(d["escorregamento_apoio_p90"].values()), d["altura_min_malha"]))
im = Image.new("RGB", (1100, 24 * len(linhas) + 12), (24, 24, 28)); dr = ImageDraw.Draw(im)
for i, l in enumerate(linhas): dr.text((8, 6 + 24 * i), l, fill=(225, 225, 225), font=fm)
blocos.append(("QA (Blender): esc = escorregamento p90 das almofadas apoiadas por quadro; zmin = menor altura da malha (o repouso ja tem -0,01)", [im]))
W = max(sum(i.width for i in l) + 16 * (len(l) + 1) for _, l in blocos); H = 60 + sum(max(i.height for i in l) + 40 for _, l in blocos)
P = Image.new("RGB", (W, H), (30, 30, 34)); d = ImageDraw.Draw(P)
d.text((16, 16), "Leao Solar E5 - rig de producao e clipes da Fase A (Blender; nada testado no Roblox)", fill=(240, 220, 160), font=F); y = 60
for t, l in blocos:
    d.text((16, y), t, fill=(235, 235, 235), font=f); x = 16
    for i in l: P.paste(i, (x, y + 26)); x += i.width + 16
    y += max(i.height for i in l) + 40
P.save(SAIDA); print("PRANCHA", P.size)
