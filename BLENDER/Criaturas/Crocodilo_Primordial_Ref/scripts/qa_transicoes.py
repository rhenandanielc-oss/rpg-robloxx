"""Continuidade transicao <-> laco: maior angulo (graus) entre ossos do primeiro/ultimo quadro da transicao e o quadro
mais parecido do clipe de origem/destino (indica o quadro de entrada no laco e quanto crossfade o jogo precisa).
Uso: python qa_transicoes.py <dir_clipes> [emendas_transicoes.json]"""
import sys, json, math, os
d = sys.argv[1]
def carrega(n): return json.load(open(os.path.join(d, "Crocodilo_%s.json" % n)))
def pose(c, q): return {o: s[q * 7:q * 7 + 4] for o, s in c["ossos"].items() if o != "Raiz"}
def dif(p1, p2): return max(math.degrees(2 * math.acos(min(1.0, abs(sum(a * b for a, b in zip(p1[o], p2[o])))))) for o in p1)
def melhor(p, c):
    return min((dif(p, pose(c, q)), q) for q in range(c["quadros"]))
PARES = [("Repouso", "RepousoParaAndar", "Andar"), ("Andar", "AndarParaRepouso", "Repouso"), ("Andar", "AndarParaCorrida", "Corrida"),
         ("Corrida", "CorridaParaAndar", "Andar"), ("Repouso", "Arrancada", "Corrida"), ("Corrida", "Frenagem", "Repouso"),
         ("Andar", "EntradaAgua", "Nado"), ("Nado", "SaidaAgua", "Andar"),
         ("Repouso", "ReacaoGolpe", "Repouso"), ("Repouso", "Comer", "Repouso"), ("Repouso", "Deitar", "DescansoDeitado"),   # Lote 3
         ("DescansoDeitado", "Levantar", "Repouso"), ("Repouso", "Observar", "Repouso"), ("Repouso", "Alerta", "Repouso"), ("Repouso", "Morte", None),
         ("Repouso", "Montar", "Repouso"), ("Repouso", "Desmontar", "Repouso")]   # Lote 4 (montado = Repouso reutilizado)
emendas = {}
for orig, tr, dest in PARES:
    t = carrega(tr); a = melhor(pose(t, 0), carrega(orig))
    b = melhor(pose(t, t["quadros"] - 1), carrega(dest)) if dest else (0.0, -1)
    print("TRANS %-18s inicio x %-8s %.1f graus (q%d) | fim x %-8s %.1f graus (q%d)" % (tr, orig, a[0], a[1], dest, b[0], b[1]))
    emendas[tr] = {"vem_de": orig, "quadro_origem_mais_parecido": a[1], "dif_inicio_graus": round(a[0], 1), "vai_para": dest or "(fica no ultimo quadro)",
                   "entrar_no_quadro": b[1], "dif_fim_graus": round(b[0], 1)}
if len(sys.argv) > 2:                                              # mescla no emendas_transicoes.json (mantem o que ja existe)
    ant = json.load(open(sys.argv[2], encoding="utf-8")); ant.update(emendas)
    json.dump(ant, open(sys.argv[2], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
