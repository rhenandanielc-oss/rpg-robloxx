"""QA dos JSON de clipes do Urso v2: NaN/inf, quaternions normalizados, ossos presentes, e emenda dos loops
(salto do ultimo para o primeiro quadro comparado ao maior passo entre quadros vizinhos). Uso: python qa_clipes.py <dir_clipes>"""
import sys, os, glob, json, math
d = sys.argv[1]; ok = True
for f in sorted(glob.glob(os.path.join(d, "Urso_*.json"))):
    js = json.load(open(f)); n = js["quadros"]; ossos = js["ossos"]; ruins = 0; passo_max = 0.0; emenda = 0.0
    for nome, seq in ossos.items():
        assert len(seq) == n * 7, (f, nome)
        for i in range(n):
            q = seq[i * 7:i * 7 + 4]
            if any(math.isnan(x) or math.isinf(x) for x in seq[i * 7:i * 7 + 7]) or abs(math.sqrt(sum(c * c for c in q)) - 1) > 1e-3: ruins += 1
        def ang(a, b):
            qa, qb = seq[a * 7:a * 7 + 4], seq[b * 7:b * 7 + 4]; dot = abs(sum(x * y for x, y in zip(qa, qb)))
            return 2 * math.degrees(math.acos(min(1.0, dot)))
        def des(a, b): return math.dist(seq[a * 7 + 4:a * 7 + 7], seq[b * 7 + 4:b * 7 + 7])
        for i in range(n - 1): passo_max = max(passo_max, ang(i, i + 1) + 30 * des(i, i + 1))
        if js["loop"]: emenda = max(emenda, ang(n - 1, 0) + 30 * des(n - 1, 0))
    situ = "OK" if ruins == 0 and (not js["loop"] or emenda <= passo_max * 1.25 + 0.5) else "ATENCAO"
    ok &= situ == "OK"
    print("%-26s quadros %3d ossos %d loop %-5s passo_max %.2f emenda %.2f invalidos %d %s" % (os.path.basename(f), n, len(ossos), js["loop"], passo_max, emenda, ruins, situ))
print("QA_CLIPES", "OK" if ok else "ATENCAO")
