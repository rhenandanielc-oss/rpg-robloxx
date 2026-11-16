"""v30 (diagnostico, so leitura): quanto as PATAS DIANTEIRAS (e traseiras, controle) giram, por acao e quadro.
Por pata: flexao do carpo/jarrete (angulo Antebraco x Metacarpo, graus), flexao dos dedos (Metacarpo x Dedos), guinada da pata (direcao dos
dedos no chao em relacao a frente -Y, graus; + = para fora), torcao do Metacarpo em torno do proprio eixo em relacao ao repouso
(graus) e inclinacao lateral do Metacarpo (graus). Uso: blender -b <blend> -P diag_patas_giro_v30.py -- <saida_json> [acoes]"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marcha_v21 as M
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUTJ = a[0]
ACS = a[1].split(",") if len(a) > 1 else [x.name for x in bpy.data.actions if not x.name.startswith("Teste")]
ARM = M.ARM; P = M.P; sc = bpy.context.scene; B = ARM.data.bones
def ang(u, w): return math.degrees(math.acos(max(-1, min(1, u.normalized().dot(w.normalized())))))
def medir():
    r = {}
    for k, (sup, inf, pe, dedo) in M.PATAS.items():
        sg = 1 if k[1] == "E" else -1; mi, mp, md = P[inf].matrix, P[pe].matrix, P[dedo].matrix
        yi, yp, yd = mi.col[1].xyz, mp.col[1].xyz, md.col[1].xyz
        tor = ang(mp.col[0].xyz - yp * mp.col[0].xyz.dot(yp), (mi.col[0].xyz - yp * mi.col[0].xyz.dot(yp)))      # torcao do pe vs antebraco
        dd = (P[dedo].tail - P[pe].tail); dh = V((dd.x, dd.y, 0))
        gu = math.degrees(math.atan2(sg * dh.x, -dh.y)) if dh.length > 1e-4 else 0.0
        r[k] = {"carpo": round(ang(yi, yp), 2), "dedos": round(ang(yp, yd), 2), "guinada": round(gu, 2), "torcao": round(tor, 2),
                "incl_lateral": round(math.degrees(math.asin(max(-1, min(1, sg * yp.x)))), 2), "z": round(P[pe].tail.z, 3)}
    return r
OUT = {}
for ac in ACS:
    acn = bpy.data.actions[ac]; ARM.animation_data.action = acn
    if len(acn.slots): ARM.animation_data.action_slot = acn.slots[0]
    f0, f1 = (int(x) for x in acn.frame_range); fr = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f); bpy.context.view_layer.update(); fr.append(medir())
    res = {k: {m: [round(min(x[k][m] for x in fr), 2), round(max(x[k][m] for x in fr), 2)] for m in ("carpo", "dedos", "guinada", "torcao", "incl_lateral")} for k in M.PATAS}
    OUT[ac] = {"faixas": res, "por_quadro": fr}; print("GIRO", ac, json.dumps({k: res[k] for k in ("DE", "DD", "TE")}), flush=True)
json.dump(OUT, open(OUTJ, "w"), indent=1); print("DIAG_PATAS_GIRO_OK", flush=True)
