"""Prancha dos closes nas poses extremas (medir_andar.py): linhas base/variante por pose; colunas ombro, quadril-jarrete, pescoco-presas.
Uso: python scripts/prancha_extremos.py andar"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
D = sys.argv[1]; E = os.path.join(D, "extremos"); F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t)
mb, mv = [json.load(open(os.path.join(D, f"medidas_extra_{p}.json"), encoding="utf-8")) for p in ("Javali", "JavaliBrejo")]
REG = (("ombro", "ombro"), ("quadril_jarrete", "jarrete"), ("pescoco_presas", "pescoco"))
lin = []
for pose, tit in (("dianteiraE_a_frente", "dianteira E toda à frente"), ("dianteiraE_atras", "dianteira E toda atrás")):
    for pfx, m, nome in (("Javali", mb, "base"), ("JavaliBrejo", mv, "brejo v4")):
        ims = []
        for reg, chave in REG:
            im = Image.open(os.path.join(E, f"{pfx}_{pose}_{reg}.png")).convert("RGB").resize((390, 330))
            er = m["poses_extremas"][pose]["estiramento_por_regiao"]; e2 = er[chave]
            extra = f" · jarrete {er['jarrete']['max']}x" if reg == "quadril_jarrete" else ""
            extra = f" · quadril {er['quadril']['max']}x" + extra if reg == "quadril_jarrete" else (f" · cabeça {er['cabeca_presas']['max']}x" if reg == "pescoco_presas" else "")
            o = Image.new("RGB", (390, 356), (55, 53, 51)); o.paste(im, (0, 26))
            ImageDraw.Draw(o).text((6, 5), f"{nome} · q{m['poses_extremas'][pose]['quadro']} {tit} · {chave} {e2['max']}x{extra}", fill=(240, 240, 240), font=F(11))
            ims.append(o)
        row = Image.new("RGB", (390 * 3 + 12, 356), (45, 43, 42))
        for i, im in enumerate(ims): row.paste(im, (i * 396, 0))
        lin.append(row)
H = 70; out = Image.new("RGB", (lin[0].width, H + sum(r.height + 6 for r in lin)), (40, 38, 36)); d = ImageDraw.Draw(out)
d.text((8, 6), "Andar · poses extremas · base × Javali-do-Brejo v4 (estiramento máx. de aresta vs. descanso, por região)", fill=(250, 250, 250), font=F(17))
pv, pb = mv["penetracoes_3_ciclos"], mb["penetracoes_3_ciclos"]
d.text((8, 36), f"cabeça×corpo: {pb['pares_tri_cabeca_x_corpo_max_por_quadro']} / {pv['pares_tri_cabeca_x_corpo_max_por_quadro']} pares · auto-interseção do corpo (média/quadro): base {pb['pares_tri_corpo_auto_media']} · brejo {pv['pares_tri_corpo_auto_media']} · cabeça mín. base {pb['cabeca_z_min_cm']} cm · brejo {pv['cabeca_z_min_cm']} cm", fill=(210, 210, 210), font=F(12))
y = H
for r in lin: out.paste(r, (0, y)); y += r.height + 6
out.save(os.path.join(D, "extremos_prancha.png")); print("PRANCHA", out.size)
