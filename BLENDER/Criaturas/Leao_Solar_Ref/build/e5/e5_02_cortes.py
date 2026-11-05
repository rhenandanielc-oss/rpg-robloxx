"""E5 inspecao: cortes horizontais (z fixo) da regiao peito/patas dianteiras, malha de jogo e malha densa, em JSON (desenho: e5_02b_desenha.py).
Uso: blender -b <arquivo.blend> -P e5_02_cortes.py -- <saida.json> <nome_obj_prefixo> [z1,z2,...]"""
import bpy, bmesh, sys
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; OUT, PREF = A[0], A[1]; EIXO = int(A[3]) if len(A) > 3 else 2; ZS = [float(z) for z in (A[2].split(",") if len(A) > 2 else "3.5,4.2,4.8,5.4,6.0,6.8".split(","))]
ob = max([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(PREF)], key=lambda o: len(o.data.vertices)); print("OBJ", ob.name, len(ob.data.vertices))
me = ob.data; co = np.array([v.co for v in me.vertices]); E = np.array([e.vertices[:] for e in me.edges])
RES = {}
for z in ZS:
    # interseccao das faces com o plano z: segmentos
    segs = []
    for p in me.polygons:
        vs = list(p.vertices); pz = co[vs, EIXO]
        if pz.min() > z or pz.max() < z: continue
        pts = []
        for i in range(len(vs)):
            a, b = co[vs[i]], co[vs[(i + 1) % len(vs)]]
            if (a[EIXO] - z) * (b[EIXO] - z) < 0: t = (z - a[EIXO]) / (b[EIXO] - a[EIXO]); pts.append(a + t * (b - a))
        if len(pts) >= 2: segs.append((pts[0], pts[1]))
    k_ = [i for i in range(3) if i != EIXO]; RES[str(z)] = [[a[k_].tolist(), b[k_].tolist()] for a, b in segs if a[1] < -3 and b[1] < -3]
import json; json.dump({"obj": ob.name, "eixo": EIXO, "cortes": RES}, open(OUT, "w")); print("CORTES_OK")
