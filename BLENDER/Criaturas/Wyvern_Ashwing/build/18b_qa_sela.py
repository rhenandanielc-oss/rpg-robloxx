# QA da sela da Wyvern (somente leitura): em TODAS as actions (passo 2,4 quadros; Ride*/Mount/Dismount a cada 1,6) mede
#   - sela dentro da pele: distancia com sinal dos vertices da sela a pele do corpo (negativa = dentro; voto de 6 raios)
#   - pele dentro da sela: vertices da pele perto da sela que ficam dentro do volume das pecas (voto de 6 raios)
#   - cavaleiro da demonstracao (trajetorias de 17_demo_cavaleiro.py) x sela: pontos das caixas dentro da sela e a folga
#     entre o fundo do tronco do cavaleiro e o topo do assento (sentado = encostado, ~0)
# Uso: blender -b Wyvern_S1_sela.blend -P 18b_qa_sela.py -- <saida.json> <trajetorias_cavaleiro.json>
import bpy, sys, json, math
from collections import Counter
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
argv = sys.argv[sys.argv.index("--") + 1:]
OUT, TRAJ = argv[0], argv[1]
scn = bpy.context.scene; FPS = scn.render.fps
arm = bpy.data.objects["Wyvern_Rig"]; pele = bpy.data.objects["Wyvern"]; sela = bpy.data.objects["Wyvern_Sela"]; key = pele.data.shape_keys
GR = {g.index: g.name for g in pele.vertex_groups}
DOM = [GR[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "?" for v in pele.data.vertices]
ASA = lambda o: any(k in o for k in ("shoulder", "upperarm", "forearm", "hand", "finger", "strut", "thumb"))
pele.data.calc_loop_triangles(); TRI = [tuple(t.vertices) for t in pele.data.loop_triangles]
TRI_C = [t for t in TRI if not ASA(Counter(DOM[i] for i in t).most_common(1)[0][0])]
DIR6 = [V((1, 0, 0)), V((-1, 0, 0)), V((0, 1, 0)), V((0, -1, 0)), V((0, 0, 1)), V((0, 0, -1))]
def dentro(bvh, p):
    v = 0
    for d in DIR6:
        loc, n, _, _ = bvh.ray_cast(p, d)
        if loc is not None and n.dot(d) > 0: v += 1
    return v >= 4
def usar(nome):
    a = bpy.data.actions[nome]
    for ob, tipo in ((arm, "OBJECT"), (key, "KEY")):
        if ob.animation_data is None: ob.animation_data_create()
        ob.animation_data.action = a; ob.animation_data.action_slot = [s for s in a.slots if s.target_id_type == tipo][0]
    return a
def malhas():
    dg = bpy.context.evaluated_depsgraph_get()
    ep = pele.evaluated_get(dg).data; Pp = [pele.matrix_world @ v.co for v in ep.vertices]
    es = sela.evaluated_get(dg); ms = es.to_mesh(); Ps = [es.matrix_world @ v.co for v in ms.vertices]
    ms.calc_loop_triangles(); Ts = [tuple(t.vertices) for t in ms.loop_triangles]; es.to_mesh_clear()
    return Pp, Ps, Ts
PL = sela.get("pecas"); PECA = [PL[x] for x in [a_.value for a_ in sela.data.attributes["peca"].data]]
traj = json.load(open(TRAJ))
POR_CLIPE = {}
for nome_seq, d in traj.items():
    POR_CLIPE.setdefault(d["clipe"], []).append((nome_seq, {round(t, 3): P for t, P in d["quadros"]}))
R = {}
pior_geral = {"sela_dentro_pele": (9e9, None), "pele_dentro_sela": (0, None), "cav_dentro_sela": (0, None)}
for a in bpy.data.actions:
    if a.name.startswith("DEMO"): continue
    usar(a.name); f1 = a.frame_range[1]; passo = 1.6 if a.name in POR_CLIPE else 2.4
    fs = [k * passo for k in range(int(f1 / passo + 1e-6) + 1)]
    sd_min = (9e9, None, None); pd_n = 0; pd_max = 0.0; cav = {"dentro_max": 0.0, "folga_assento": []}
    for f in fs:
        scn.frame_set(int(f), subframe=f - int(f)); Pp, Ps, Ts = malhas()
        bp = BVHTree.FromPolygons(Pp, TRI_C, all_triangles=True); bs = BVHTree.FromPolygons(Ps, Ts, all_triangles=True)
        for i in range(0, len(Ps), 2):                                  # sela x pele
            loc, n, _, dd = bp.find_nearest(Ps[i])
            if loc is None: continue
            if dd < 0.6:
                sd = -dd if dentro(bp, Ps[i]) else dd
                if sd < sd_min[0]: sd_min = (round(sd, 3), round(f, 1), PECA[i])
        cx = sum((p for p in Ps), V()) / len(Ps); r_ = max((p - cx).length for p in Ps)
        for p in Pp:                                                    # pele x sela
            if (p - cx).length > r_: continue
            loc, n, _, dd = bs.find_nearest(p)
            if loc is not None and dd < 0.5 and dentro(bs, p):
                pd_n += 1; pd_max = max(pd_max, dd)
        t = round(f / FPS, 3)
        for nome_seq, qd in POR_CLIPE.get(a.name, []):                  # cavaleiro x sela
            Pc = qd.get(t)
            if Pc is None: continue
            for parte, Mm in Pc.items():
                Mm = Matrix(Mm)
                for i in (-1, 0, 1):
                    for j in (-1, 0, 1):
                        for k in (-1, 0, 1):
                            q = Mm @ V((i * 0.4, j * 0.4, k * 0.4))
                            loc, n, _, dd = bs.find_nearest(q)
                            if loc is not None and dd < 0.6 and dentro(bs, q): cav["dentro_max"] = max(cav["dentro_max"], round(dd, 3))
            if "TroncoInf" in Pc:
                base = Matrix(Pc["TroncoInf"]) @ V((0, 0, -0.2))
                hit = bs.ray_cast(base, V((0, 0, -1)))
                if hit[0] is not None and (base - hit[0]).length < 1.5: cav["folga_assento"].append(round((base - hit[0]).length, 3))
    R[a.name] = {"quadros": len(fs), "sela_dentro_pele_min": sd_min, "pele_dentro_sela_vertices_max": pd_n, "pele_dentro_sela_prof_max": round(pd_max, 3)}
    if a.name in POR_CLIPE:
        fa = cav["folga_assento"]
        R[a.name]["cavaleiro_dentro_sela_max"] = cav["dentro_max"]
        R[a.name]["cavaleiro_fundo_tronco_sobre_assento"] = [min(fa), max(fa)] if fa else None
    print("QA", a.name, json.dumps(R[a.name]), flush=True)
json.dump(R, open(OUT, "w"), indent=1); print("OK")
