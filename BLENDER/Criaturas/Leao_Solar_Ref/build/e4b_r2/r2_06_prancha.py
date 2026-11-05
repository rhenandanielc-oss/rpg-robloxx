"""Prancha E4b r2: poses das patas dianteiras e pescoco, E4b x r2 (mesma malha; muda so rig/pesos), tabela E4 | E4b | r2
e quadros dos videos. Uso: python r2_06_prancha.py <saida.png>"""
import sys, os, json, glob
from PIL import Image, ImageDraw, ImageFont
exec(open(os.path.join(os.path.dirname(__file__), "..", "e4b", "e4b_06_prancha.py"), encoding="utf-8").read().split("V = ((")[0].replace("REF, SAIDA = sys.argv[1:3]; ref = Image.open(REF).convert(\"RGB\"); ", ""))
SAIDA = sys.argv[1]
PO = ["ombro_avanco", "cotovelo_dobra", "punho_dobra", "passo_dianteiro", "pescoco_baixo_virado"]
A4, A, B = "review/e4b/poses_e4", "review/e4b_r2/poses_E4b_com_qa", "review/e4b_r2/poses_Leao_Solar_Ref_E4b_r2"
L = []
for p in PO:
    L.append((f"{p}: E4b (repouso arame | posado textura | posado arame)  ||  r2 (posado textura | posado arame)",
              [("E4b repouso", sob(f"{A}/{p}_0_arame.png", (300, 300))), ("E4b posado", sob(f"{A}/{p}_1_tex.png", (300, 300))), ("E4b arame", sob(f"{A}/{p}_1_arame.png", (300, 300))),
               ("r2 posado", sob(f"{B}/{p}_1_tex.png", (300, 300))), ("r2 arame", sob(f"{B}/{p}_1_arame.png", (300, 300)))]))
M = [(n, json.load(open(f"review/e4b_r2/med3_{f}/poses.json"))) for n, f in (("E4", "E4_rig_novo"), ("E4b", "E4b_com_qa"), ("r2", "Leao_Solar_Ref_E4b_r2"))]
def g(m, p, *k):
    x = m[p]
    for kk in k: x = x.get(kk) if isinstance(x, dict) else None
    return x
rows = ["%-21s | %-8s | %-17s | %-22s | %-24s | %-9s" % ("pose (mesmo rig)", "versao", "pata p5 / min", "pele: arestas>1,5x / abs", "corpo: arestas>1,5x / abs", "vol perd."), "-" * 118]
for p in PO + ["joelho_dobra", "jarrete_dobra", "passo_traseiro", "cauda_curva", "boca_32"]:
    for n, m in M:
        pp = g(m, p, "zona", "pata_espessura_p5"); pm = g(m, p, "zona", "pata_espessura_min"); pe = g(m, p, "pele_fora_da_juba")
        rows.append("%-21s | %-8s | %-17s | %-22s | %-24s | %9s" % (p if n == "E4" else "", n, ("%.2f / %.2f (%dv)" % (pp, pm, g(m, p, "zona", "pata_vertices"))) if pp else "-",
                    ("%d / %.2f" % (pe["arestas_esticadas_>1.5x_e_>0.05"], pe["alongamento_abs_max"])) if pe else "(sem mascara)",
                    "%d / %.2f" % (m[p]["corpo"]["arestas_esticadas_>1.5x_e_>0.05"], m[p]["corpo"]["alongamento_abs_max"]), "%.2f" % m[p]["volume_perdido_studs3"]))
L.append(("medicoes (E4 e E4b com o mesmo rig de teste da E4b; r2 = rig revisado). pata = vertices com peso >= 0,5 na cadeia, esfera 2,2; pele = fora da mascara de cor da juba; vol perd. = perda de volume do corpo na pose (positivo = afinou)", [("tabela", texto(rows, 1250))]))
q = sorted(glob.glob("review/e4b_r2/videos/_q_*.png"))
if q: L.append(("quadros dos videos r2 (lado e 3/4, chao visivel)", [(os.path.basename(f)[3:-4], alt(Image.open(f).convert("RGB"), 260)) for f in q[:6]]))
P = prancha("Leao Solar E4b r2 - correcao de cotovelo, punho e juba do peito (mesma malha 17.602 tris) - Blender, rig de TESTE; nada testado no Roblox", L, SAIDA)
print("PRANCHA_R2", P.size)
