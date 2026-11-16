"""Pranchas e quadros de video do lote 1 (Repouso, Andar). Uso: python prancha_clipes_v12.py review/v12_clipes
- repouso_v11_x_v12.png: REFERENCIA | v11 (rig, sem clipe) | Repouso quadro 0 | diferenca x8;
- apoios_andar.png: 13 quadros do ciclo (perfil E com deslocamento, patas E/D) com a fase de cada pata;
- emenda_andar.png e emenda_repouso.png: quadros dos dois lados da emenda do laco;
- repouso_sequencia.png, transicao.png;
- video_<nome>/v_NNNN.png: mosaicos para MP4 (video_rig_v9.py)."""
import sys, os, json, glob
from PIL import Image, ImageDraw, ImageChops
D = os.path.abspath(sys.argv[1]); AQ = os.path.dirname(os.path.abspath(__file__))
ref = Image.open(os.path.join(AQ, "ref", "lobo-artico-referencia.png")).convert("RGB"); CJ = json.load(open(os.path.join(AQ, "anim_v12", "clipes_v12.json")))
def rot(im, t, y=0):
    d = ImageDraw.Draw(im); d.rectangle((0, y, 7 * len(t) + 12, y + 18), fill=(0, 0, 0)); d.text((6, y + 3), t, fill=(255, 255, 255)); return im
def abre(p, t, s):
    if not os.path.exists(p): return rot(Image.new("RGB", s, (60, 60, 60)), t + " (sem imagem)")
    return rot(Image.open(p).convert("RGB").resize(s), t)
def fase(k, q):
    A = CJ["andar"]; u = ((q / 30 / A["T"]) - A["fases"][k]) % 1.0; return "apoio" if u < A["apoio"] else "balanco"
W, H = 480, 360
o = Image.new("RGB", (4 * (W + 4), 5 * (H + 4)), (15, 15, 15)); DIF = {}
for r, v in enumerate(("frente", "lado_E", "lado_D", "tras", "34_E")):
    a = os.path.join(D, "repouso", "v11_%s_q0000.png" % v); b = os.path.join(D, "repouso", "v12_Repouso_%s_q0000.png" % v); y = r * (H + 4)
    o.paste(rot(ref.resize((W, H)), "REFERENCIA (repouso; nao prova movimento)"), (0, y)); o.paste(abre(a, "v11 rig %s" % v, (W, H)), (W + 4, y)); o.paste(abre(b, "v12 Repouso quadro 0 %s" % v, (W, H)), (2 * (W + 4), y))
    if os.path.exists(a) and os.path.exists(b):
        df = ImageChops.difference(Image.open(a).convert("RGB"), Image.open(b).convert("RGB")); mx = max(c[1] for c in df.getextrema()); DIF[v] = mx
        o.paste(rot(df.point(lambda x: min(255, x * 8)).resize((W, H)), "diferenca x8 (pixel max %d/255)" % mx), (3 * (W + 4), y))
o.save(os.path.join(D, "repouso_v11_x_v12.png"))
QS = list(range(0, 37, 3)); o = Image.new("RGB", (len(QS) * (W + 4), 3 * (H + 4)), (15, 15, 15))
for c, q in enumerate(QS):
    f = " ".join("%s:%s" % (k, fase(k, q)[0].upper()) for k in ("DE", "DD", "TE", "TD"))
    for r, (pre, v) in enumerate((("LOW_Andar_desloc", "perfil_E"), ("LOW_Andar_desloc", "patas_E"), ("LOW_Andar_desloc", "patas_D"))):
        im = abre(os.path.join(D, "andar", "%s_%s_q%04d.png" % (pre, v, q)), "q%d %s" % (q, v), (W, H)); rot(im, f + " (A=apoio B=balanco)", 20); o.paste(im, (c * (W + 4), r * (H + 4)))
o.save(os.path.join(D, "apoios_andar.png"))
for nome, pasta, pre, v, qs in (("emenda_andar", "andar", "LOW_Andar_nolugar", "perfil_E", (32, 33, 34, 35, 0, 1, 2, 3)), ("emenda_repouso", "repouso_clipe", "LOW_Repouso", "perfil_E", (236, 237, 238, 239, 240, 0, 1, 2))):
    o = Image.new("RGB", (len(qs) * (W + 4), H), (15, 15, 15))
    for c, q in enumerate(qs): o.paste(abre(os.path.join(D, pasta, "%s_%s_q%04d.png" % (pre, v, q)), "%s q%d%s" % (nome, q, " (=q0)" if (q == 240) else ""), (W, H)), (c * (W + 4), 0))
    o.save(os.path.join(D, nome + ".png"))
o = Image.new("RGB", (7 * (W + 4), 2 * (H + 4)), (15, 15, 15))
for c, q in enumerate(range(0, 241, 40)):
    for r, v in enumerate(("perfil_E", "34_E")): o.paste(abre(os.path.join(D, "repouso_clipe", "LOW_Repouso_%s_q%04d.png" % (v, q)), "Repouso q%d %s" % (q, v), (W, H)), (c * (W + 4), r * (H + 4)))
o.save(os.path.join(D, "repouso_sequencia.png"))
o = Image.new("RGB", (9 * (W + 4), 2 * (H + 4)), (15, 15, 15))
for c, q in enumerate(range(0, 265, 33)):
    for r, v in enumerate(("perfil_E", "34_E")): o.paste(abre(os.path.join(D, "transicao", "LOW_Teste_Transicao_desloc_%s_q%04d.png" % (v, q)), "TESTE transicao q%d %s" % (q, v), (W, H)), (c * (W + 4), r * (H + 4)))
o.save(os.path.join(D, "transicao.png"))
def video(nome, celulas, qs, cols, s=(480, 360)):
    vd = os.path.join(D, "video_" + nome); os.makedirs(vd, exist_ok=True); lin = (len(celulas) + cols - 1) // cols
    for i, q in enumerate(qs):
        o = Image.new("RGB", (cols * s[0], lin * s[1]), (15, 15, 15))
        for j, (p, t) in enumerate(celulas):
            if p is None: im = rot(ref.resize(s), "REFERENCIA (repouso)")
            else: im = abre(p % q if "%" in p else p, t + " q%d" % q, s)
            o.paste(im, ((j % cols) * s[0], (j // cols) * s[1]))
        o.save(os.path.join(vd, "v_%04d.png" % i))
    return len(qs)
A = os.path.join(D, "andar", "LOW_Andar_desloc_%s_q%%04d.png")
n = {}
n["andar"] = video("andar", [(None, "")] + [(A % v, "Andar LOD0 com deslocamento %s" % v) for v in ("perfil_E", "perfil_D", "frente", "tras", "34_E")], range(0, 108), 3)
n["andar_closes"] = video("andar_closes", [(A % "patas_E", "patas E"), (A % "patas_D", "patas D"), (A % "cauda_E", "cauda/pata E"),
                                           (os.path.join(D, "andar", "LOW_Andar_desloc_sempelo_patas_E_q%04d.png"), "patas E sem pelo"),
                                           (os.path.join(D, "andar", "LOW_Andar_desloc_sempelo_cauda_E_q%04d.png"), "cauda E sem pelo")], [q % 36 if False else q for q in range(0, 36)], 3)
n["andar_nolugar"] = video("andar_nolugar", [(os.path.join(D, "andar", "LOW_Andar_nolugar_%s_q%%04d.png" % v), "Andar NO LUGAR (contrato do jogo) %s" % v) for v in ("perfil_E", "34_E")] +
                           [(os.path.join(D, "andar", "LOW_Andar_garganta_q%04d.png"), "garganta")], [q % 36 for q in range(0, 108)], 3)
n["repouso"] = video("repouso", [(None, "")] + [(os.path.join(D, "repouso_clipe", "LOW_Repouso_%s_q%%04d.png" % v), "Repouso LOD0 %s" % v) for v in ("perfil_E", "34_E", "frente")], range(0, 240), 2)
n["lods"] = video("lods", [(os.path.join(D, "lods", "%s_Andar_desloc_%s_q%%04d.png" % (L, v)), "%s Andar %s" % (L, v)) for L in ("LOD1", "LOD2") for v in ("perfil_E", "34_E")], range(0, 72), 2)
n["transicao"] = video("transicao", [(os.path.join(D, "transicao", "LOW_Teste_Transicao_desloc_%s_q%%04d.png" % v), "TESTE tecnico Repouso->Andar->Repouso %s" % v) for v in ("perfil_E", "34_E")], range(0, 265), 2)
print("PRANCHAS_CLIPES_V12_OK", DIF, n)
