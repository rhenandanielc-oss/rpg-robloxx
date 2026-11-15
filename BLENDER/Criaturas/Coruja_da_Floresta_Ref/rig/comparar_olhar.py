"""Antes (lote A r1) x depois (r2, rig r3) do giro de cabeca da coruja: GIFs empilhados (mesma camera fixa, mesma velocidade, 30 qps)
e pranchas das capturas fixas (frente, perfil, 3/4 de tras, close da juncao) com a referencia ao lado.
Uso: python comparar_olhar.py <dir_render_antes> <dir_render_depois> <dir_capturas> <saida> <referencia.png>"""
import sys, os, glob
from PIL import Image, ImageDraw, ImageFont
RA, RD, CAP, OUT, REF = sys.argv[1:6]; os.makedirs(OUT, exist_ok=True)
F = lambda t: ImageFont.truetype("C:/Windows/Fonts/arial.ttf", t)
def rot(im, t, cor):
    d = ImageDraw.Draw(im); d.rectangle((0, 0, im.width, 22), fill=cor); d.text((6, 3), t, fill=(255, 255, 255), font=F(14)); return im
for ac in ("OlharE", "OlharD"):
    for vista in ("lado_fixo", "34_fixo", "frente_fixo"):
        A = sorted(glob.glob(os.path.join(RA, ac, vista, "q*.png"))); D = sorted(glob.glob(os.path.join(RD, ac, vista, "q*.png")))
        if not A or not D: continue
        fr = []
        for i in range(max(len(A), len(D))):
            a = rot(Image.open(A[min(i, len(A) - 1)]).convert("RGB"), f"ANTES (r1)  {ac}  quadro da cadeia {i:03d}  t={i / 30:.2f}s", (110, 40, 35))
            b = rot(Image.open(D[min(i, len(D) - 1)]).convert("RGB"), f"DEPOIS (r2, rig r3)  {ac}  quadro {i:03d}  t={i / 30:.2f}s", (35, 90, 45))
            o = Image.new("RGB", (a.width, a.height * 2 + 4), (30, 30, 30)); o.paste(a, (0, 0)); o.paste(b, (0, a.height + 4))
            fr.append(o.resize((o.width * 3 // 4, o.height * 3 // 4)))
        fr[0].save(os.path.join(OUT, f"antes_depois_{ac}_{vista}.gif"), save_all=True, append_images=fr[1:], duration=33, loop=0); print("GIF", ac, vista, len(fr))
ref = Image.open(REF).convert("RGB"); r34 = ref.crop((0, 0, 690, 941)).resize((round(690 * 220 / 941), 220))
for ac in ("OlharE", "OlharD"):
    qs = [0, 5, 20, 58, 71]; vs = ["frente", "perfil", "34tras", "close"]; W = 220
    o = Image.new("RGB", (r34.width + 8 + W * 5, 40 + (W + 20) * 8), (40, 40, 40)); d = ImageDraw.Draw(o)
    d.text((8, 8), f"Coruja — {ac}: antes (r1) × depois (r2, rig r3) · quadros início / meio do giro / extremo / retorno / fim", fill=(250, 250, 250), font=F(17))
    o.paste(r34, (0, 40)); d.text((4, 40 + r34.height + 4), "referência", fill=(220, 220, 220), font=F(13))
    y = 40
    for v in vs:
        for ver, cor in (("antes", (255, 130, 120)), ("depois", (140, 240, 140))):
            for i, q in enumerate(qs):
                p_ = os.path.join(CAP, ver, f"{ac}_q{q:03d}_{v}.png")
                if os.path.exists(p_): o.paste(Image.open(p_).convert("RGB").resize((W, W)), (r34.width + 8 + i * W, y + 20))
                d.text((r34.width + 12 + i * W, y + 3), f"{ver.upper()} q{q} · {v}", fill=cor, font=F(13))
            y += W + 20
    o.save(os.path.join(OUT, f"prancha_{ac}_antes_depois.png")); print("PRANCHA", ac, o.size)
outros = [("InclinarCabeca", [0, 20, 40]), ("AjeitarPenas", [0, 20, 40]), ("Repouso", [0, 20, 40])]
W = 200; o = Image.new("RGB", (W * 6 + 10, 40 + (W + 20) * 6), (40, 40, 40)); d = ImageDraw.Draw(o); d.text((8, 8), "Outros clipes de cabeça: antes × depois (frente e close)", fill=(250, 250, 250), font=F(17)); y = 40
for ac, qs in outros:
    for v in ("frente", "close"):
        x = 0
        for ver in ("antes", "depois"):
            for q in qs:
                p_ = os.path.join(CAP, ver + "_outros", f"{ac}_q{q:03d}_{v}.png")
                if os.path.exists(p_): o.paste(Image.open(p_).convert("RGB").resize((W, W)), (x, y + 20))
                d.text((x + 4, y + 3), f"{ver.upper()} {ac} q{q} {v}", fill=(255, 130, 120) if ver == "antes" else (140, 240, 140), font=F(11)); x += W
            x += 10
        y += W + 20
o.save(os.path.join(OUT, "prancha_outros_antes_depois.png")); print("PRANCHA outros")
