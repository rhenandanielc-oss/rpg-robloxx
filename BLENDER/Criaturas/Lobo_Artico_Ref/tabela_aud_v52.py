"""v52 (= tabela_aud_v51 com versoes v51/v52/v52_reimport; le aud_v51_* de review/v51_partida): tabela antes/depois por pata, LOD e TRECHO da sequencia auditada (Repouso*15 -> PartidaCurva -> AndarCurva ->
CurvaParaAndar -> ParadaAndar -> RepousoFim), a partir dos JSON do auditar_curvas_v46.py (mesmo metodo para v50, v51 e a
reimportacao). Cada fase de apoio e atribuida ao(s) trecho(s) que ela cobre (fase que atravessa uma emenda aparece nos dois).
Uso: python tabela_aud_v51.py <dir_review>  -> imprime e grava tabela_v51.md"""
import json, os, sys
R = sys.argv[1]; BASE = os.path.dirname(os.path.abspath(__file__))
VJ = json.load(open(os.path.join(BASE, "anim_v52", "curvas_v46b.json")))["acoes"]
VJ.update(json.load(open(os.path.join(BASE, "anim_v52", "partida_v48.json")))["acoes"])
VJ.update(json.load(open(os.path.join(BASE, "anim_v52", "partida_v51.json")))["acoes"])
def trechos(lado):
    seq = [("repouso", 15), ("partida", VJ["PartidaCurva" + lado]["quadros"]), ("laco", VJ["AndarCurva" + lado]["quadros"]),
           ("saida", VJ["CurvaParaAndar" + lado]["quadros"]), ("parada", VJ["ParadaAndar"]["quadros"]), ("repouso_fim", 20)]
    out, q = [], 0
    for n, k in seq: out.append((n, q, q + k - 1)); q += k
    return out
TOL = 0.03; PATAS = ("DE", "DD", "TE", "TD"); TRE = ("partida", "laco", "saida", "parada")
linhas = ["| versão | LOD | lado | trecho | " + " | ".join(PATAS) + " | fases > 0,03 (pata: quadros) |", "|---|---|---|---|" + "---|" * 4 + "---|"]
resumo = {}
for ver in ("v51", "v52", "v52_reimport"):
    for L in ("LOW", "LOD1", "LOD2"):
        p = os.path.join(R if ver != "v51" else os.path.join(R, "..", "v51_partida"), "aud_%s_%s.json" % (ver, L))
        if not os.path.exists(p): continue
        d = json.load(open(p))
        for cn, lado in (("partida_curva_E", "Esquerda"), ("partida_curva_D", "Direita")):
            T = trechos(lado); c = d["cenarios"][cn]
            for tr in TRE:
                a, b = next((x[1], x[2]) for x in T if x[0] == tr)
                vals, viol = [], []
                for k in PATAS:
                    fs = [f for f in c["patas"][k]["fases"] if f["q"][0] <= b and f["q"][1] >= a]
                    m = max([f["deslize"] for f in fs] or [0.0]); vals.append(m)
                    viol += ["%s: %d-%d (%.4f)" % (k, f["q"][0], f["q"][1], f["deslize"]) for f in fs if f["deslize"] > TOL]
                    resumo.setdefault((ver, tr, k), []).append(m)
                linhas.append("| %s | %s | %s | %s | %s | %s |" % (ver, L, lado[0], tr, " | ".join(("**%.4f**" if v > TOL else "%.4f") % v for v in vals), "; ".join(viol) or "—"))
            g = c["folga_lateral_min_MCP"]; ac = c["aceleracao_q2"]
            linhas.append("| %s | %s | %s | geral | folga diant %.3f / tras %.3f | acel max %.3f | rumo %.0f | desloc %s | |" % (ver, L, lado[0], g["diant"], g["tras"], ac["max"], c["rumo_final_graus"], c["deslocamento_final"]))
txt = "\n".join(linhas)
txt += "\n\nMáximo por versão/trecho/pata (3 LODs, E e D):\n\n| versão | trecho | " + " | ".join(PATAS) + " |\n|---|---|" + "---|" * 4 + "\n"
for ver in ("v51", "v52", "v52_reimport"):
    for tr in TRE:
        if (ver, tr, "DE") in resumo:
            txt += "| %s | %s | %s |\n" % (ver, tr, " | ".join(("**%.4f**" if max(resumo[(ver, tr, k)]) > TOL else "%.4f") % max(resumo[(ver, tr, k)]) for k in PATAS))
open(os.path.join(R, "tabela_v52.md"), "w", encoding="utf-8").write(txt + "\n"); print(txt)
