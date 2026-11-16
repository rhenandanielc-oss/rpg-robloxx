"""v24: mede os APOIOS nos GLB REIMPORTADOS (cena limpa, acoes executadas pelo esqueleto importado), com o MESMO metodo do
auditar_clipes_v21 / diag_apoios_v24: cronograma da marcha (clipes_v21.json da pasta do blend), apoio que cruza a emenda = uma
fase, deslocamento de apresentacao continuo -v*q/FPS, pontos = vertices da pata (mesma selecao: z < 0,5 a 0,8 do pe, pela
posicao de repouso) que tocam o chao (<= 0,03 do mais baixo) no MEIO do apoio, fixos na fase, contados enquanto < 0,06 do chao;
afundamento = - (altura minima da pata na fase - altura minima da pata no repouso). O glTF duplica vertices nas costuras de
UV (coincidentes, mesmo movimento): nao muda o resultado. Compara com o diag da fonte (diag_apoios_v24.json).
Uso: blender -b --factory-startup -P apoios_reimport_v24.py -- <dir_glb> <dir_blend_fonte> <diag_fonte.json> <saida_json>"""
import bpy, sys, os, json, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; DG, SRC, DF, OUT = (os.path.abspath(x) for x in a[:4])
CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); MAR = CJ["marchas"]; FPS = CJ["fps"]; PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
EXP = json.load(open(os.path.join(DG, os.environ.get("EXP_JSON", "export_clipes_v21.json")))); FON = json.load(open(DF))   # v25: EXP_JSON=export_clipes_v25.json
R = {"metodo": __doc__.split("Uso:")[0], "unidade": "stud", "tolerancia": 0.03, "niveis": {}}
for L in ("LOW", "LOD1", "LOD2"):
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = FPS
    ops = bpy.ops.import_scene.gltf.get_rna_type().properties.keys()
    bpy.ops.import_scene.gltf(filepath=os.path.join(DG, EXP["lods"][L]["arquivo"]), **({"bone_heuristic": "BLENDER"} if "bone_heuristic" in ops else {}))
    A = [o for o in sc.objects if o.type == "ARMATURE"][0]; C = bpy.data.objects[L + "_Corpo"]; Mw = C.matrix_world.copy()
    if A.animation_data is None: A.animation_data_create()
    P0 = [Mw @ v.co for v in C.data.vertices]
    patas = {k: [i for i, p in enumerate(P0) if p.z < 0.5 and math.hypot(p.x - xy[0], p.y - xy[1]) < 0.8] for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"])}
    zr = {k: min(P0[i].z for i in ids) for k, ids in patas.items()}
    RL = R["niveis"][L] = {}
    for acao in ("Andar", "Trote", "Corrida"):
        ac = next(x for x in bpy.data.actions if x.name == acao or x.name.startswith(acao)); A.animation_data.action = ac
        if len(ac.slots): A.animation_data.action_slot = ac.slots[0]
        n = int(round(ac.frame_range[1] - ac.frame_range[0])); f0 = int(round(ac.frame_range[0])); v = MAR[acao]["v_studs_s"]; G = MAR[acao]
        PP = {}
        for q in range(n):
            sc.frame_set(f0 + q); dg = bpy.context.evaluated_depsgraph_get(); e = C.evaluated_get(dg); m = e.to_mesh(); PP[q] = [Mw @ x.co for x in m.vertices]; e.to_mesh_clear()
        def fase(k, q): u = ((q / FPS / G["T"]) - G["fases"][k]) % 1.0; return u < G["apoio"]
        RA = RL[acao] = {"quadros": n, "patas": {}}
        for k, ids in patas.items():
            segs, cur = [], []
            for q in range(n):
                if fase(k, q): cur.append(q)
                elif cur: segs.append(cur); cur = []
            if cur: segs.append(cur)
            if len(segs) > 1 and segs[0][0] == 0 and segs[-1][-1] == n - 1: segs = [[q - n for q in segs[-1]] + segs[0]] + segs[1:-1]
            fs = []
            for sg in segs:
                qm = sg[len(sg) // 2]; P = PP[qm % n]; zm = min(P[i].z for i in ids); pts = [i for i in ids if P[i].z < zm + 0.03]
                ref = {i: P[i] + V((0, -v * qm / FPS, 0)) for i in pts}; mx = 0.0
                for qq in sg:
                    for i in pts:
                        p_ = PP[qq % n][i]
                        if p_.z < zm + 0.06: mx = max(mx, ((p_ + V((0, -v * qq / FPS, 0))) - ref[i]).to_2d().length)
                afu = -min(0.0, min(min(PP[qq % n][i].z for i in ids) for qq in sg) - zr[k])
                fs.append({"inicio": sg[0], "fim": sg[-1], "deslize": round(mx, 5), "afundamento": round(afu, 4)})
            fonte = max(f["deslize"] for f in FON["niveis"][L][acao]["patas"][k])
            RA["patas"][k] = {"fases": fs, "deslize_max": max(f["deslize"] for f in fs), "afundamento_max": max(f["afundamento"] for f in fs), "deslize_max_fonte": fonte,
                              "diferenca_fonte_reimport": round(abs(max(f["deslize"] for f in fs) - fonte), 5)}
            print("REIMP_APOIO", L, acao, k, json.dumps({x: RA["patas"][k][x] for x in ("deslize_max", "afundamento_max", "deslize_max_fonte", "diferenca_fonte_reimport")}), flush=True)
json.dump(R, open(OUT, "w"), indent=1); print("APOIOS_REIMPORT_V24_OK", flush=True)
