"""QA dos JSON de clipes x GLB exportado: nomes dos ossos, quaternions unitarios, fechamento do laco e saltos entre quadros.
Uso: python qa_clipes_json.py <dir_clipes> <glb>"""
import sys, json, glob, math, struct, os
d, glb = sys.argv[1], sys.argv[2]
b = open(glb, "rb").read(); n = struct.unpack("<I", b[12:16])[0]; j = json.loads(b[20:20 + n])
nos = j["nodes"]; juntas = {nos[i]["name"] for i in j["skins"][0]["joints"]}
def ang(q1, q2):
    dp = abs(sum(a * b_ for a, b_ in zip(q1, q2))); return math.degrees(2 * math.acos(min(1.0, dp)))
for f in sorted(glob.glob(os.path.join(d, "Crocodilo_*.json"))):
    c = json.load(open(f)); ossos = c["ossos"]; nq = c["quadros"]
    faltam = juntas - set(ossos); sobram = set(ossos) - juntas
    norma = max(abs(math.sqrt(sum(v * v for v in s[k * 7:k * 7 + 4])) - 1) for s in ossos.values() for k in range(nq))
    salto = {}; laco = {}
    for o in ("Raiz", "Pelve", "Cabeca", "Mandibula", "Cauda8", "MaoE", "PeD"):
        s = ossos[o]; qs = [s[k * 7:k * 7 + 4] for k in range(nq)]; ts = [s[k * 7 + 4:k * 7 + 7] for k in range(nq)]
        passos = [ang(qs[k], qs[k + 1]) for k in range(nq - 1)]
        salto[o] = round(max(passos), 2)
        if c["loop"]: laco[o] = round(ang(qs[-1], qs[0]) - max(passos), 2)      # <= 0: o retorno nao e maior que um passo normal
    print("QA", os.path.basename(f), "quadros", nq, "loop", c["loop"], "ossos", len(ossos), "faltam", sorted(faltam), "sobram", sorted(sobram),
          "erro_norma %.6f" % norma, "maior_passo_graus", salto, "laco(retorno-maior_passo)", laco)
