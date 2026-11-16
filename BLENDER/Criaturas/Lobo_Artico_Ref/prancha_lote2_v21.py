"""Pranchas e quadros de video do lote 2 (L2a: Trote, Corrida). Uso: python prancha_lote2_v21.py review/v21_lote2
- video_corpo_<acao>: REFERENCIA + perfil E/D, frente, tras, 3/4 com deslocamento sobre a grade (3 ciclos);
- video_nolugar_<acao>: perfil E, 3/4, patas E/D no lugar (contrato do jogo), 3 ciclos;
- video_closes_<modo>_<acao>: fresta E/baixo, garganta E/baixo, flanco D/baixo (camera parada), 3 ciclos;
- video_lods: LOD1/LOD2 perfil E e 3/4;
- apoios_<acao>.png: todos os quadros do ciclo (perfil E com deslocamento + patas) com a fase de cada pata (A/B);
- closes_comparacao_<modo>.png: Andar (aprovado) x Trote x Corrida nos quadros de pior deformacao da auditoria.
Depois: video_rig_v9.py em cada pasta video_* (normal 30 qps e lento 0,5x)."""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
D = os.path.abspath(sys.argv[1]); AQ = os.path.dirname(os.path.abspath(__file__))
CJ = json.load(open(os.path.join(AQ, "anim_v21", "clipes_v21.json"))); MAR = CJ["marchas"]
ref = Image.open(os.path.join(AQ, "ref", "lobo-artico-referencia.png")).convert("RGB")
try: F = ImageFont.truetype("arial.ttf", 20); FG = ImageFont.truetype("arial.ttf", 30)
except OSError: F = FG = ImageFont.load_default()
def rot(im, t, y=0, f=F):
    d = ImageDraw.Draw(im); w = int(d.textlength(t, font=f)) + 14; d.rectangle((0, y, w, y + f.size + 8), fill=(0, 0, 0)); d.text((7, y + 3), t, font=f, fill=(255, 255, 255)); return im
def abre(p, t, s):
    if not os.path.exists(p): return rot(Image.new("RGB", s, (60, 60, 60)), t + " (sem imagem)")
    return rot(Image.open(p).convert("RGB").resize(s), t)
def fase(ac, k, q):
    G = MAR[ac]; u = ((q / 30 / G["T"]) - G["fases"][k]) % 1.0; return "A" if u < G["apoio"] else "B"
def nq(ac): return int(round(MAR[ac]["T"] * 30))
def video(nome, celulas, qs, cols, s):
    vd = os.path.join(D, "video_" + nome); os.makedirs(vd, exist_ok=True); lin = (len(celulas) + cols - 1) // cols
    for i, q in enumerate(qs):
        o = Image.new("RGB", (cols * s[0], lin * s[1]), (15, 15, 15))
        for j, (p, t) in enumerate(celulas):
            im = rot(ref.resize(s), "REFERENCIA (repouso)") if p is None else abre(p % q if "%" in p else p, t + "  q%d" % q, s)
            o.paste(im, ((j % cols) * s[0], (j // cols) * s[1]))
        o.save(os.path.join(vd, "v_%04d.png" % i))
    return len(qs)
n = {}
for ac in ("Trote", "Corrida"):
    N = nq(ac); G = MAR[ac]; tag = "%s: ciclo %.3f s, passada %.2f, v %.2f studs/s (parametros tecnicos)" % (ac, G["T"], G["D"], G["v_studs_s"])
    n["corpo_" + ac] = video("corpo_" + ac, [(None, "")] + [(os.path.join(D, "corpo", "LOW_%s_desloc_%s_q%%04d.png" % (ac, v)), "%s %s" % (ac, v)) for v in ("perfil_E", "perfil_D", "frente", "tras", "34_E")], range(0, 3 * N), 3, (640, 480))
    n["nolugar_" + ac] = video("nolugar_" + ac, [(os.path.join(D, "corpo", "LOW_%s_nolugar_%s_q%%04d.png" % (ac, v)), "%s NO LUGAR %s" % (ac, v)) for v in ("perfil_E", "34_E", "patas_E", "patas_D")], [q % N for q in range(3 * N)], 2, (640, 480))
    for modo in ("cores", "real"):
        n["closes_%s_%s" % (modo, ac)] = video("closes_%s_%s" % (modo, ac), [(os.path.join(D, "closes", "%s_%s_%s_q%%04d.png" % (modo, ac, v)), "%s %s %s" % (ac, v, modo)) for v in ("fresta_E", "fresta_baixo", "garganta_E", "garganta_baixo", "flanco_D", "flanco_D_baixo")], [q % N for q in range(3 * N)], 3, (640, 480))
    W, H = 400, 300; o = Image.new("RGB", (N * (W + 4), 3 * (H + 4) + 50), (15, 15, 15)); rot(o, tag, 8, FG)
    for c, q in enumerate(range(N)):
        f = " ".join("%s:%s" % (k, fase(ac, k, q)) for k in ("DE", "DD", "TE", "TD"))
        for r, (p, v) in enumerate(((os.path.join(D, "corpo", "LOW_%s_desloc_perfil_E_q%04d.png" % (ac, q)), "perfil_E"), (os.path.join(D, "corpo", "LOW_%s_nolugar_patas_E_q%04d.png" % (ac, q)), "patas_E"), (os.path.join(D, "corpo", "LOW_%s_nolugar_patas_D_q%04d.png" % (ac, q)), "patas_D"))):
            im = abre(p, "q%d %s" % (q, v), (W, H)); rot(im, f + "  (A=apoio B=balanco)", 30); o.paste(im, (c * (W + 4), 50 + r * (H + 4)))
    o.save(os.path.join(D, "apoios_%s.png" % ac))
n["lods"] = video("lods", [(os.path.join(D, "lods", "%s_%s_desloc_%s_q%%04d.png" % (L, ac, v)), "%s %s %s" % (L, ac, v)) for ac in ("Trote", "Corrida") for L in ("LOD1", "LOD2") for v in ("perfil_E", "34_E")][:8], range(0, 28), 4, (480, 360))
AU = json.load(open(os.path.join(D, "aud_clipes_v21.json")))["niveis"]["LOW"]
def pior(ac, rg): return (AU.get(ac, {}).get("deformacao_por_regiao", {}).get(rg, {}) or {}).get("quadro_pior")
for modo in ("cores", "real"):
    lin = []
    for v, rg in (("fresta_E", "cauda_pata_E"), ("fresta_baixo", "cauda_pata_E"), ("garganta_E", "garganta"), ("garganta_baixo", "garganta"), ("flanco_D", "flanco_D"), ("flanco_D_baixo", "flanco_D")):
        cel = []
        for ac in ("Andar", "Trote", "Corrida"):
            q = pior(ac, rg) or 0; q = q % nq(ac) if ac != "Andar" else q % 36
            cel.append(abre(os.path.join(D, "closes", "%s_%s_%s_q%04d.png" % (modo, ac, v, q)), "%s %s q%d (pior quadro: %s)" % (ac, v, q, rg), (640, 480)))
        lin.append(cel)
    o = Image.new("RGB", (3 * 644, len(lin) * 484), (15, 15, 15))
    for r, l in enumerate(lin):
        for c, im in enumerate(l): o.paste(im, (c * 644, r * 484))
    o.save(os.path.join(D, "closes_comparacao_%s.png" % modo))
print("PRANCHAS_V21_OK", n)
