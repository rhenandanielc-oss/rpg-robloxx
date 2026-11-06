"""Lote 5: resumo das medicoes (review/L5/RESUMO_L5.txt): demonstracao dos dois lados, continuidade e reutilizacao com a
sela definitiva. Folga = menor distancia com sinal (negativa = entra). Uso: python resumo_l5.py <review/L5>"""
import sys, os, json, glob
L = sys.argv[1]; out = []
AP = {"LeftHand", "RightHand", "LeftFoot", "RightFoot"}
def mn(med, chave, filtro):
    return min(((v, n, m.get("q", m.get("i"))) for m in med if chave in m for n, v in m[chave].items() if filtro(n)), default=None)
def linha(nome, med):
    c = mn(med, "folga_croc", lambda n: n not in AP); a = mn(med, "folga_croc", lambda n: n in AP); s = mn(med, "folga_sela", lambda n: True)
    q = [m["quadril_no_osso"] for m in med if "quadril_no_osso" in m]
    der = max((sum((x - y) ** 2 for x, y in zip(p, q[0])) ** 0.5 for p in q), default=None)
    r = "%-22s corpo x pele %s | apoio x pele %s | cavaleiro x sela %s" % (nome, "%.3f (%s q%s)" % c if c else "-", "%.3f (%s q%s)" % a if a else "-", "%.3f (%s q%s)" % s if s else "-")
    if der is not None: r += " | deriva %.4f" % der
    return r
d = json.load(open(os.path.join(L, "qa_demo_L5.json")))
out.append("== SELA: " + json.dumps(d["sela"], ensure_ascii=False))
out.append("== DEMONSTRACAO (manequim R15 aproximado, sela definitiva PROPOSTA)")
for k in ("Sentado", "Montar", "Desmontar", "MontarDireita", "DesmontarDireita"):
    med = d["quadros"][k]; out.append(linha(k, med) + " | vel. quadril max %.2f studs/s" % max(m["vel_quadril"] for m in med))
out.append("== CONTINUIDADE e REUTILIZACAO")
for f in sorted(glob.glob(os.path.join(L, "seq", "medidas_*.json")) + glob.glob(os.path.join(L, "qa3", "medidas_*.json"))):
    med = json.load(open(f)); tag = os.path.basename(f).replace("medidas_", "").replace(".json", "")
    if "seq" in tag:
        out.append(linha(tag, [m for m in med if "folga_croc" in m]))
        sal = max((sum((x - y) ** 2 for x, y in zip(b["quadril"], a["quadril"])) ** 0.5 for a, b in zip(med, med[1:]) if "quadril" in a and "quadril" in b), default=0)
        out.append("%-22s maior passo do quadril entre quadros seguidos: %.3f stud" % ("", sal))
    else:
        for nome in dict.fromkeys(m["clipe"] for m in med): out.append(linha(nome, [m for m in med if m["clipe"] == nome]))
qs = os.path.join(L, "qa_sela_clipes.txt")
if os.path.exists(qs): out.append("== SELA x PELE nos clipes (quadro a quadro)"); out += [l.rstrip() for l in open(qs) if l.startswith("QA_SELA ")]
open(os.path.join(L, "RESUMO_L5.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n"); print("\n".join(out))
