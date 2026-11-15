"""Compara curvas de acoes de mesmo nome em dois .blend (valor de cada curva em cada quadro), por osso.
Uso: blender -b --factory-startup -P scripts/comparar_acoes.py -- <a.blend> <b.blend> <Clipe1,...> [prefixo_a=Javali_] [prefixo_b=Javali_]"""
import bpy, sys, json, math, os
A = sys.argv[sys.argv.index("--") + 1:]; FA, FB, L = os.path.abspath(A[0]), os.path.abspath(A[1]), A[2].split(","); PA = A[3] if len(A) > 3 else "Javali_"; PB = A[4] if len(A) > 4 else "Javali_"
def carrega(f, pfx):
    with bpy.data.libraries.load(f, link=False) as (s, d): d.actions = [pfx + n for n in L]
    return d.actions
def curvas(a):
    cs = {}
    for l in a.layers:
        for st in l.strips:
            for cb in st.channelbags:
                for c in cb.fcurves: cs[(c.data_path, c.array_index)] = c
    return cs
aa, bb = carrega(FA, PA), carrega(FB, PB); R = {}
for n, a, b in zip(L, aa, bb):
    ca, cb = curvas(a), curvas(b); f0, f1 = int(a.frame_range[0]), int(a.frame_range[1]); dif = {}
    for k in ca:
        if k not in cb: dif[str(k)] = "faltando"; continue
        m = max(abs(ca[k].evaluate(f) - cb[k].evaluate(f)) for f in range(f0, f1 + 1))
        osso = k[0].split('"')[1] if '"' in k[0] else k[0]
        dif[osso] = max(dif.get(osso, 0.0), m)
    R[n] = {"quadros": [f0, f1, int(b.frame_range[1])], "max_dif_geral": round(max(v for v in dif.values() if isinstance(v, float)), 5),
            "ossos_diferentes(>1e-4)": {o: round(v, 4) for o, v in dif.items() if isinstance(v, float) and v > 1e-4}}
print("COMPARA", json.dumps(R, ensure_ascii=False))
