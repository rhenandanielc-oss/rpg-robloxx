"""Lote 4: resumo das medicoes do cavaleiro de teste (review/L4/RESUMO_L4.txt). Folga = menor distancia com sinal da
caixa do manequim ate a pele (negativa = entra). 'apoio' = maos/pes que tocam a pele de proposito; 'corpo' = demais partes.
Uso: python resumo_l4.py <review/L4>"""
import sys, os, json, glob
L = sys.argv[1]; out = []
APOIO = {"LeftHand", "RightHand", "LeftFoot", "RightFoot"}
def resumo(med, nome):
    fc = [(v, n, m.get("t", m.get("i"))) for m in med if "folga_croc" in m for n, v in m["folga_croc"].items()]
    corpo = min((x for x in fc if x[1] not in APOIO), default=None); apoio = min((x for x in fc if x[1] in APOIO), default=None)
    fs = min(((v, n, m.get("t", m.get("i"))) for m in med if "folga_sela" in m for n, v in m["folga_sela"].items()), default=None)
    q = [m["quadril_no_osso"] for m in med if "quadril_no_osso" in m]
    der = max((sum((a - b) ** 2 for a, b in zip(x, q[0])) ** 0.5 for x in q), default=None)
    ruins = len({m.get("t", m.get("i")) for m in med if "folga_croc" in m and min(m["folga_croc"].values()) < -0.15})
    linha = "%-24s corpo %s | apoio %s | sela %s" % (nome, "%.3f (%s)" % corpo[:2] if corpo else "-", "%.3f (%s)" % apoio[:2] if apoio else "-", "%.3f (%s)" % fs[:2] if fs else "-")
    if der is not None: linha += " | deriva quadril/osso %.4f" % der
    linha += " | quadros < -0,15: %d de %d" % (ruins, len(med))
    agua = [m["agua"] for m in med if "agua" in m]
    if agua:
        linha += "\n%-24s agua: quadril %.2f..%.2f | base do tronco %.2f..%.2f | pescoco %.2f..%.2f | pe min %.2f" % ("", min(a["quadril_sobre_agua"] for a in agua), max(a["quadril_sobre_agua"] for a in agua),
                 min(a["base_tronco_sobre_agua"] for a in agua), max(a["base_tronco_sobre_agua"] for a in agua), min(a["pescoco_sobre_agua"] for a in agua), max(a["pescoco_sobre_agua"] for a in agua), min(a["pe_min_sobre_agua"] for a in agua))
    out.append(linha)
d = json.load(open(os.path.join(L, "qa_demo_L4.json")))
out.append("== DEMONSTRACAO (manequim animado por alvos/IK, assado em FK)")
for k in ("Sentado", "Montar", "Desmontar"):
    resumo(d["quadros"][k], k); med = d["quadros"][k]
    out.append("%-24s quadril: vel max %.2f studs/s (sem salto) | sola min z %.3f" % ("", max(m["vel_quadril"] for m in med), min(m["sola_min_z"] for m in med)))
out.append("== CONTINUIDADE e REUTILIZACAO (cavaleiro sentado preso ao osso Coluna1)")
for f in sorted(glob.glob(os.path.join(L, "seq", "medidas_*.json")) + glob.glob(os.path.join(L, "qa3", "medidas_*.json"))):
    med = json.load(open(f))
    for nome in dict.fromkeys(m["clipe"] for m in med):
        resumo([m for m in med if m["clipe"] == nome], ("seq:" if "seq" in f else "") + nome)
    if "seq" in f:
        sal = max((sum((a - b) ** 2 for a, b in zip(m1["quadril"], m0["quadril"])) ** 0.5 for m0, m1 in zip(med, med[1:]) if "quadril" in m0 and "quadril" in m1), default=0)
        out.append("%-24s maior passo do quadril entre quadros seguidos (seq inteira, passo 1): %.3f studs" % ("", sal))
for f in sorted(glob.glob(os.path.join(L, "agua", "medidas_*_cavaleiro.json"))):
    med = json.load(open(f)); c = [m[-1] for m in med]
    out.append("agua %-19s quadril %.2f..%.2f | base do tronco %.2f..%.2f | pescoco %.2f..%.2f | pe min %.2f | malha x terreno max %.3f" % (
        os.path.basename(f).split("_")[1], min(x["quadril"] for x in c), max(x["quadril"] for x in c), min(x["tronco_base"] for x in c), max(x["tronco_base"] for x in c),
        min(x["pescoco"] for x in c), max(x["pescoco"] for x in c), min(x["pe_min"] for x in c), max(m[4] for m in med)))
for f in sorted(glob.glob(os.path.join(L, "encaixe", "encaixe*.json"))):
    e = json.load(open(f)); out.append("encaixe %s: %s" % (os.path.basename(f), json.dumps(e, ensure_ascii=False)))
open(os.path.join(L, "RESUMO_L4.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n"); print("\n".join(out))
