import json, sys
M = [(n, json.load(open(f))) for n, f in zip(sys.argv[1::2], sys.argv[2::2])]
for p in M[0][1]:
    print("%-21s" % p + " || ".join("%s pata %s | corpo %3d/%.2f | vol %6.2f" % (n, ("%.2f/%.2f" % (m[p]['zona']['pata_espessura_p5'], m[p]['zona']['pata_espessura_min'])) if m[p]['zona'].get('pata_espessura_p5') else "  -  ",
          m[p]['corpo']['arestas_esticadas_>1.5x_e_>0.05'], m[p]['corpo']['alongamento_abs_max'], m[p]['volume_perdido_studs3']) for n, m in M))
