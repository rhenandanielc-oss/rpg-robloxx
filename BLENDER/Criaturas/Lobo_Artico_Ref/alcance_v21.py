"""Lote 2: ALCANCE de cada pata no chao (dz = 0), para escolher a passada pela geometria do rig em vez de presumir: para
cada pata e cada abaixamento do Quadril (dz_q), o intervalo de dy (frente = -y) em que o IK fecha (erro < 0,002) com a perna
a no maximo EXT_MAX do comprimento (sem esticar travada). Uso: blender -b anim_v20/CR_LoboArtico_Anim.blend -P alcance_v21.py -- <json>"""
import bpy, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector as V
import marcha_v21 as M
OUT = sys.argv[sys.argv.index("--") + 1:][0]; EXT_MAX = 0.97
M.ARM.animation_data.action = None; R = {"ext_max": EXT_MAX}
for dzq in (0.0, -0.3, -0.6):
    for k in M.PATAS:
        ok = []
        for i in range(-60, 61):
            dy = i * 0.1; M.aplicar_corpo({}, V((0, 0, dzq)))
            pes = {kk: (0.0, 0.0, 0.0, 0.0) for kk in M.PATAS}; pes[k] = (dy, 0.0, 0.0, 0.0)
            err, ext = M.aplicar_patas(pes)
            if err < 0.002 and ext[k] <= EXT_MAX: ok.append(dy)
        R.setdefault("dz_quadril_%.1f" % dzq, {})[k] = {"frente_max": round(-min(ok), 2) if ok else None, "tras_max": round(max(ok), 2) if ok else None}
    print("ALC", dzq, json.dumps(R["dz_quadril_%.1f" % dzq]), flush=True)
pb = {k: (M.B[c[0]].head_local, M.MCP0[k]) for k, c in M.PATAS.items()}
R["ombro_quadril_y"] = {k: round(v[0].y, 3) for k, v in pb.items()}; R["pata_repouso_y"] = {k: round(v[1].y, 3) for k, v in pb.items()}
R["comprimento_perna"] = {k: round(M.B[c[0]].length + M.B[c[1]].length, 3) for k, c in M.PATAS.items()}
json.dump(R, open(OUT, "w"), indent=1); print("ALCANCE_OK", R["ombro_quadril_y"], R["pata_repouso_y"], R["comprimento_perna"], flush=True)
