"""Revisao (so leitura) da Arrancada e da Frenagem (v25, identicas na anim_v29): por quadro e pata, extensao d/(a+b), angulo do
joelho/jarrete (graus; perto de 0 = perna reta travada), MCP (y,z), apoio, velocidade e aceleracao angular (graus/quadro, quadro^2);
mesmas metricas no Repouso (q0..30) e na Corrida (controle). Uso: blender -b <blend> -P diag_arranca_freio_v29.py -- <json_transicoes_v25> <saida>"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marcha_v21 as M
a = sys.argv[sys.argv.index("--") + 1:]; TJ = json.load(open(a[0])); OUTJ = a[1]
ARM = M.ARM; P = M.P; sc = bpy.context.scene; B = ARM.data.bones
def pose(nome, f):
    ac = bpy.data.actions[nome]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    sc.frame_set(f); bpy.context.view_layer.update(); pat = {}
    for k, (sup, inf, pe, dedo) in M.PATAS.items():
        S = P[sup].head; Kn = P[inf].head; Tt = P[inf].tail; L = B[sup].length + B[inf].length
        u = (Kn - S).normalized(); w = (Tt - Kn).normalized()
        pat[k] = {"ext": (Tt - S).length / L, "joelho": math.degrees(math.acos(max(-1, min(1, u.dot(w))))), "y": P[pe].tail.y, "z": P[pe].tail.z}
    return pat, {n: P[n].matrix.to_quaternion() for c in M.PATAS.values() for n in c}
def ang(q1, q2): return math.degrees(2 * math.acos(min(1.0, abs(q1.dot(q2)))))
def serie(nome, n, apoio=None):
    R = [pose(nome, f) for f in range(n + 1)]; out = []
    for f in range(n + 1):
        d = {}
        for k, c in M.PATAS.items():
            v = max(ang(R[f][1][x], R[f - 1][1][x]) for x in c[:3]) if f > 0 else 0.0
            d[k] = {"ext": round(R[f][0][k]["ext"], 4), "joelho": round(R[f][0][k]["joelho"], 2), "y": round(R[f][0][k]["y"], 3), "z": round(R[f][0][k]["z"], 3), "vel": round(v, 3),
                    "apoio": bool(apoio[k][f]) if apoio else None}
        out.append(d)
    for f in range(len(out)):
        for k in M.PATAS: out[f][k]["acc"] = round(abs(out[f][k]["vel"] - out[f - 1][k]["vel"]), 3) if 1 < f else 0.0
    res = {k: {"joelho_min": min(o[k]["joelho"] for o in out), "q_joelho_min": min(range(len(out)), key=lambda f: out[f][k]["joelho"]), "ext_max": max(o[k]["ext"] for o in out),
               "vel_max": max(o[k]["vel"] for o in out), "acc_max": max(o[k]["acc"] for o in out[2:]), "q_acc_max": max(range(2, len(out)), key=lambda f: out[f][k]["acc"])} for k in M.PATAS}
    return res, out
OUT = {}
for nome, n in (("Arrancada", 75), ("Frenagem", 48), ("Corrida", 14), ("Repouso", 30)):
    ap = TJ["acoes"][nome]["apoio_por_quadro"] if nome in TJ["acoes"] else None
    r, o = serie(nome, n, ap); OUT[nome] = {"resumo": r, "por_quadro": o}; print("DIAG", nome, json.dumps(r), flush=True)
json.dump(OUT, open(OUTJ, "w"), indent=1); print("DIAG_ARRANCA_FREIO_OK", flush=True)
