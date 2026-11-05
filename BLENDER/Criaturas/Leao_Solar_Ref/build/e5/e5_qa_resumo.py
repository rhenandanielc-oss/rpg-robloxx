"""resume as linhas CLIPE do gerador (stdin)"""
import sys, json
for l in sys.stdin:
    if l.startswith("CLIPE "):
        n, j = l[6:].split(" ", 1); d = json.loads(j)
        print("%-19s q%3d v%5.1f desl%6.1f ik%.3f esc %s zmin %.2f@%s %s" % (n, d["quadros"], d["velocidade_studs_s"], d["deslocamento_raiz"][1], d["erro_ik_max"],
              {k: round(v, 3) for k, v in d["escorregamento_apoio_p90"].items()}, d["altura_min_malha"], d["altura_min_onde"], d["emenda_loop_graus"] if d["loop"] else ""))
    elif "Error" in l or "Trace" in l or "line " in l: print(l.strip()[:300])
