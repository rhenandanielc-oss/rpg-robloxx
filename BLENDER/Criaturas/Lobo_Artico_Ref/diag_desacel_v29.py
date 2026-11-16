"""v29 (diagnostico, so leitura): TroteParaAndar e CorridaParaTrote quadro a quadro.
Por quadro: diferenca de pose (maior angulo entre ossos, graus; e Quadril) em relacao ao clipe de DESTINO na fase theta-g e ao de
ORIGEM na fase theta (diz quando a transicao ja virou a marcha de destino = fim da desaceleracao efetiva); por pata: extensao da perna
d/(a+b), angulo do joelho/cotovelo (graus), MCP no referencial do clipe (y,z), apoio, velocidade e aceleracao angular dos ossos da
perna (graus/quadro e graus/quadro^2: esticada brusca = pico). Mesmas metricas nas marchas ciclicas de origem e destino (controle).
Uso: blender -b <blend> -P diag_desacel_v29.py -- <json_transicoes> <saida_json> [acoes]"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marcha_v21 as M
import marchas_v28 as MV
a = sys.argv[sys.argv.index("--") + 1:]; TJ = json.load(open(a[0])); OUTJ = a[1]
ACS = a[2].split(",") if len(a) > 2 else ["TroteParaAndar", "CorridaParaTrote"]
ARM = M.ARM; P = M.P; sc = bpy.context.scene; B = ARM.data.bones
def pose(nome, fr):
    ac = bpy.data.actions[nome]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    f0 = int(math.floor(fr)); sc.frame_set(f0, subframe=fr - f0); bpy.context.view_layer.update()
    q = {pb.name: pb.rotation_quaternion.copy().normalized() for pb in P}; loc = P["Quadril"].location.copy()
    pat = {}
    for k, (sup, inf, pe, dedo) in M.PATAS.items():
        S = P[sup].head; Kn = P[inf].head; Tt = P[inf].tail; L = B[sup].length + B[inf].length
        u = (Kn - S).normalized(); w = (Tt - Kn).normalized(); jo = math.degrees(math.acos(max(-1, min(1, u.dot(w)))))
        mc = P[pe].tail
        pat[k] = {"ext": (Tt - S).length / L, "joelho": jo, "mcp_y": mc.y, "mcp_z": mc.z}
    # matriz de pose dos ossos da perna (para velocidade angular no referencial da armature)
    mp = {n: P[n].matrix.to_quaternion() for c in M.PATAS.values() for n in c}
    return q, loc, pat, mp
def ang(q1, q2):
    d = abs(q1.dot(q2)); return math.degrees(2 * math.acos(min(1.0, d)))
def serie(nome, n, faseA=None, faseB=None):
    R = []
    for f in range(n + 1):
        q, loc, pat, mp = pose(nome, f); R.append((q, loc, pat, mp))
    return R
OUT = {"acoes": {}, "controle": {}}
def cinem(R):
    """velocidade/aceleracao angular dos ossos da perna por quadro (graus/quadro), maior por pata"""
    vel = {k: [] for k in M.PATAS}; acc = {k: [] for k in M.PATAS}
    for f in range(len(R)):
        for k, c in M.PATAS.items():
            v = max(ang(R[f][3][n], R[f - 1][3][n]) for n in c[:3]) if f > 0 else 0.0; vel[k].append(round(v, 3))
    for k in M.PATAS:
        acc[k] = [0.0] + [round(abs(vel[k][f + 1] - vel[k][f]), 3) for f in range(1, len(R) - 1)] + [0.0]
    return vel, acc
for g in ("Andar", "Trote", "Corrida"):
    R = serie(g, MV.NQ[g]); vel, acc = cinem(R)
    OUT["controle"][g] = {"ext_max": {k: round(max(r[2][k]["ext"] for r in R), 4) for k in M.PATAS},
                          "joelho_min": {k: round(min(r[2][k]["joelho"] for r in R), 2) for k in M.PATAS},
                          "vel_max": {k: max(vel[k][1:]) for k in M.PATAS}, "acc_max": {k: max(acc[k][1:-1]) for k in M.PATAS},
                          "por_quadro": [{k: {"ext": round(r[2][k]["ext"], 4), "joelho": round(r[2][k]["joelho"], 2), "y": round(r[2][k]["mcp_y"], 3), "z": round(r[2][k]["mcp_z"], 3), "vel": vel[k][f]} for k in M.PATAS} for f, r in enumerate(R)]}
for ac in ACS:
    A = TJ["acoes"][ac]; nA, nB = A["origem"], A["destino"]; g = A["deslocamento_global_fase"]; n = A["quadros"]; th = A["teta_por_quadro"]
    R = serie(ac, n); vel, acc = cinem(R); pq = []; conv = None
    for f in range(n + 1):
        qB, lB, pB, _ = pose(nB, ((th[f] - g) % 1.0) * MV.NQ[nB]); qA, lA, pA, _ = pose(nA, (th[f] % 1.0) * MV.NQ[nA])
        q, loc = R[f][0], R[f][1]
        dB = max(ang(q[nm], qB[nm]) for nm in q); dA = max(ang(q[nm], qA[nm]) for nm in q)
        dBl = max(ang(q[nm], qB[nm]) for c in M.PATAS.values() for nm in c); dBc = max(ang(q[nm], qB[nm]) for nm in q if nm not in {x for c in M.PATAS.values() for x in c})
        pq.append({"q": f, "s": A["s_por_quadro"][f], "v": A["v_por_quadro"][f], "teta": th[f], "fase_dest_quadro": round(((th[f] - g) % 1.0) * MV.NQ[nB], 3),
                   "dif_destino_graus": round(dB, 3), "dif_destino_pernas": round(dBl, 3), "dif_destino_corpo": round(dBc, 3), "dif_origem_graus": round(dA, 3),
                   "dif_destino_quadril": round((loc - lB).length, 5),
                   "patas": {k: {"ext": round(R[f][2][k]["ext"], 4), "joelho": round(R[f][2][k]["joelho"], 2), "y": round(R[f][2][k]["mcp_y"], 3), "z": round(R[f][2][k]["mcp_z"], 3),
                                 "apoio": A["apoio_por_quadro"][k][f], "vel": vel[k][f], "acc": acc[k][f]} for k in M.PATAS}})
    for f in range(n, -1, -1):
        if pq[f]["dif_destino_graus"] > 0.05 or pq[f]["dif_destino_quadril"] > 1e-4: conv = f + 1; break
    OUT["acoes"][ac] = {"origem": nA, "destino": nB, "quadros": n, "convergiu_no_quadro": conv, "s1_no_quadro": next(i for i, x in enumerate(A["s_por_quadro"]) if x > 0.99999),
                        "ext_max": {k: max(p["patas"][k]["ext"] for p in pq) for k in M.PATAS}, "joelho_min": {k: min(p["patas"][k]["joelho"] for p in pq) for k in M.PATAS},
                        "vel_max": {k: max(vel[k][1:]) for k in M.PATAS}, "acc_max": {k: max(acc[k][1:-1]) for k in M.PATAS}, "por_quadro": pq}
    print("DIAG", ac, "convergiu", conv, "s1", OUT["acoes"][ac]["s1_no_quadro"], "ext", OUT["acoes"][ac]["ext_max"], "acc", OUT["acoes"][ac]["acc_max"], flush=True)
for g, c in OUT["controle"].items(): print("CTRL", g, "ext", c["ext_max"], "acc", c["acc_max"], "vel", c["vel_max"], flush=True)
json.dump(OUT, open(OUTJ, "w"), indent=1); print("DIAG_DESACEL_V29_OK", flush=True)
