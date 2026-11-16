"""v31 (diagnostico, so leitura): a perna vista de FRENTE. Por pata e quadro (referencial do clipe, X lateral, sinal + = para FORA):
- cotovelo_fora: distancia lateral do cotovelo/joelho a reta ombro-punho (stud; curva da perna na vista de frente);
- punho_x, mcp_x, dedo_x: deslocamento lateral do punho/MCP/ponta dos dedos em relacao ao ombro/quadril (stud);
- plano_graus: inclinacao do plano da dobra (ombro, cotovelo, punho) em relacao ao plano sagital (0 = perna dobra para frente/tras);
- torcao_pe: giro do Metacarpo em torno do proprio eixo em relacao ao Antebraco (graus).
Uso: blender -b <blend> -P diag_perna_frontal_v31.py -- <saida_json> [acoes]"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marcha_v21 as M
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUTJ = a[0]
ACS = a[1].split(",") if len(a) > 1 else [x.name for x in bpy.data.actions if not x.name.startswith("Teste")]
ARM = M.ARM; P = M.P; sc = bpy.context.scene
def medir():
    r = {}
    for k, (sup, inf, pe, dedo) in M.PATAS.items():
        sg = 1 if k[1] == "E" else -1; S = P[sup].head; K = P[inf].head; W = P[inf].tail; Mc = P[pe].tail; T = P[dedo].tail
        u = (W - S); t = (K - S).dot(u) / max(1e-9, u.length_squared); Q = S + u * t; off = (K - Q)
        n = (K - S).cross(W - S); pl = math.degrees(math.asin(min(1.0, abs(n.normalized().x)))) if n.length > 1e-6 else 0.0
        xi = P[inf].matrix.col[0].xyz; yp = P[pe].matrix.col[1].xyz; xp = P[pe].matrix.col[0].xyz
        a_ = (xi - yp * xi.dot(yp)).normalized(); b_ = (xp - yp * xp.dot(yp)).normalized(); tor = math.degrees(math.acos(max(-1, min(1, a_.dot(b_)))))
        r[k] = {"cotovelo_fora": round(sg * off.x, 4), "punho_x": round(sg * (W.x - S.x), 4), "mcp_x": round(sg * (Mc.x - S.x), 4), "dedo_x": round(sg * (T.x - S.x), 4),
                "plano_graus": round(90 - pl, 2), "torcao_pe": round(tor, 2)}
    return r
OUT = {}
for ac in ACS:
    acn = bpy.data.actions[ac]; ARM.animation_data.action = acn
    if len(acn.slots): ARM.animation_data.action_slot = acn.slots[0]
    f0, f1 = (int(x) for x in acn.frame_range); fr = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f); bpy.context.view_layer.update(); fr.append(medir())
    fx = {k: {m: [round(min(x[k][m] for x in fr), 3), round(max(x[k][m] for x in fr), 3)] for m in fr[0][k]} for k in M.PATAS}
    OUT[ac] = {"faixas": fx, "por_quadro": fr}; print("FRONTAL", ac, json.dumps({k: fx[k] for k in ("DE", "DD", "TE")}), flush=True)
json.dump(OUT, open(OUTJ, "w"), indent=1); print("DIAG_PERNA_FRONTAL_OK", flush=True)
