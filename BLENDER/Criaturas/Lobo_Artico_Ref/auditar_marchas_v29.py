"""v29 = copia do auditar_marchas_v28 (modulo/JSON v29; duplicado do fim de cada transicao comparado ao quadro de SAIDA do destino).
v28: auditoria da SEQUENCIA COMPLETA de troca de marchas (linha do tempo de marchas_v29.linha: Andar x2 | AndarParaTrote |
Trote x3 | TroteParaCorrida | Corrida x3 | CorridaParaTrote | Trote x2 | TroteParaAndar | Andar x2), com o MESMO metodo de pontos
fixos da v24/v25 (copia do auditar_sequencia_v25 com a linha do tempo, o deslocamento e os apoios do modulo marchas_v29):
- deslocamento X acumulado por quadro: marchas -v/30; transicoes = CURVA gravada (marchas_v29.json, X_por_quadro);
- apoio por quadro: marchas = cronograma da marcha; transicoes = cronograma do gerador; uma fase atravessa as emendas;
- pontos = vertices da pata que tocam o chao (<= 0,03 do mais baixo) no MEIO do apoio, FIXOS na fase, contados enquanto < 0,06;
  deslize = maior deslocamento horizontal (com X) em relacao ao meio; afundamento/flutuacao = altura minima - repouso;
- emendas: 2a diferenca na emenda x maior dentro dos clipes vizinhos; quadros duplicados: origem q0 x transicao q0 e transicao
  q_fim x destino q0.
Uso: blender -b <anim.blend> -P auditar_marchas_v29.py -- <saida_json> [LOW,LOD1,LOD2] [--glb <dir_export> <dir_fonte>]"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector as V
import marchas_v29 as MV
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIV = a[1].split(",") if len(a) > 1 and not a[1].startswith("--") else ["LOW", "LOD1", "LOD2"]
GLB = a[a.index("--glb") + 1] if "--glb" in a else None; SRC = os.path.abspath(a[a.index("--glb") + 2]) if GLB else os.path.dirname(bpy.data.filepath)
CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); TJ = json.load(open(os.path.join(SRC, "marchas_v29.json"))); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
G = MV.marchas(CJ); FPS = 30; LT = MV.linha(TJ); Xc = MV.deslocamento(LT, G, TJ)
def apoio(acao, k, q): return MV.apoio(G, TJ, acao, k, q)
NOMES = ("Andar", "Trote", "Corrida") + tuple(MV.TRANS)
R = {"metodo": __doc__.split("Uso:")[0], "unidade": "stud", "tolerancia_deslize": 0.03, "linha_do_tempo": ["%s q%d" % e for e in LT], "X": [round(x, 4) for x in Xc], "niveis": {}}
for L in NIV:
    if GLB:
        bpy.ops.wm.read_factory_settings(use_empty=True); bpy.context.scene.render.fps = FPS     # 30 qps ANTES de importar (cena nova abre em 24)
        ops = bpy.ops.import_scene.gltf.get_rna_type().properties.keys()
        EXP = json.load(open(os.path.join(GLB, "export_clipes_v29.json")))
        bpy.ops.import_scene.gltf(filepath=os.path.join(GLB, EXP["lods"][L]["arquivo"]), **({"bone_heuristic": "BLENDER"} if "bone_heuristic" in ops else {}))
        A = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
        if A.animation_data is None: A.animation_data_create()
        ACS = {n: next(x for x in bpy.data.actions if x.name == n or x.name.startswith(n + "|")) for n in NOMES}
    else:
        A = bpy.data.objects["LoboArtico_Rig"]; ACS = {n: bpy.data.actions[n] for n in NOMES}
    sc = bpy.context.scene; C = bpy.data.objects[L + "_Corpo"]; Mw = C.matrix_world.copy(); P0 = [Mw @ v.co for v in C.data.vertices]
    patas = {k: [i for i, p in enumerate(P0) if p.z < 0.5 and math.hypot(p.x - xy[0], p.y - xy[1]) < 0.8] for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"])}
    zr = {k: min(P0[i].z for i in ids) for k, ids in patas.items()}
    cache = {}
    def pose(acao, q):
        if (acao, q) in cache: return cache[(acao, q)]
        acn = ACS[acao]; A.animation_data.action = acn
        if len(acn.slots): A.animation_data.action_slot = acn.slots[0]
        sc.frame_set(int(round(acn.frame_range[0])) + q); dg = bpy.context.evaluated_depsgraph_get(); e = C.evaluated_get(dg); m = e.to_mesh()
        Pq = [Mw @ v.co for v in m.vertices]; e.to_mesh_clear(); cache[(acao, q)] = Pq; return Pq
    PP = [pose(*e) for e in LT]
    RL = R["niveis"][L] = {"apoios": {}, "emendas": {}, "duplicados": {}}
    for k, ids in patas.items():
        segs, cur = [], []
        for i, (ac_, q) in enumerate(LT):
            if apoio(ac_, k, q): cur.append(i)
            elif cur: segs.append(cur); cur = []
        if cur: segs.append(cur)
        fs = []
        for sg in segs:
            im = sg[len(sg) // 2]; zm = min(PP[im][i].z for i in ids); pts = [i for i in ids if PP[im][i].z < zm + 0.03]
            ref = {i: PP[im][i] + V((0, Xc[im], 0)) for i in pts}; mx = 0.0; qp = None
            for j in sg:
                for i in pts:
                    p_ = PP[j][i]
                    if p_.z < zm + 0.06:
                        d = ((p_ + V((0, Xc[j], 0))) - ref[i]).to_2d().length
                        if d > mx: mx, qp = d, j
            alt = min(min(PP[j][i].z for i in ids) - zr[k] for j in sg)
            fs.append({"inicio": "%s q%d" % LT[sg[0]], "fim": "%s q%d" % LT[sg[-1]], "indices": [sg[0], sg[-1]], "quadros": len(sg),
                       "acoes": sorted({LT[j][0] for j in sg}), "deslize": round(mx, 5), "quadro_pior": "%s q%d" % LT[qp] if qp is not None else None,
                       "afundamento": round(-min(alt, 0.0), 4), "flutuacao": round(max(alt, 0.0), 4), "pontos": len(pts)})
        RL["apoios"][k] = fs
        pior = max((f for f in fs if any(x in f["acoes"] for x in MV.TRANS)), key=lambda f: f["deslize"])
        print("SEQ", L, k, "fases", len(fs), "pior(transicoes)", pior["deslize"], pior["inicio"], "->", pior["fim"], "afund", max(f["afundamento"] for f in fs), flush=True)
    # emendas: 2a diferenca na emenda x maior dentro dos clipes vizinhos (amostra de vertices, com X)
    amo = list(range(0, len(P0), 7))
    def W(j, i): return PP[j][i] + V((0, Xc[j], 0))
    def ac2(j): return max(((W(j + 1, i) - W(j, i)) - (W(j, i) - W(j - 1, i))).length for i in amo)
    for j in range(1, len(LT) - 1):
        if LT[j][0] != LT[j - 1][0]:
            nm = "%s->%s" % (LT[j - 1][0], LT[j][0]); viz = [ac2(i) for i in range(max(1, j - 12), min(len(LT) - 1, j + 12)) if i not in (j - 1, j)]
            RL["emendas"][nm] = {"indice": j, "aceleracao_na_emenda": round(max(ac2(j - 1), ac2(j)), 5), "aceleracao_max_vizinha": round(max(viz), 5),
                                 "velocidade_X_antes": round((Xc[j - 1] - Xc[j - 2]) * FPS, 3), "velocidade_X_depois": round((Xc[j + 1] - Xc[j]) * FPS, 3)}
    def dif(a_, b_): return max((p - q_).length for p, q_ in zip(a_, b_))
    for tn, (o_, d_) in MV.TRANS.items():
        RL["duplicados"]["%s q0 x %s q0" % (o_, tn)] = round(dif(pose(o_, 0), pose(tn, 0)), 6)
        qs_ = TJ["acoes"][tn].get("saida_quadro_destino", 0); RL["duplicados"]["%s fim x %s q%d" % (tn, d_, qs_)] = round(dif(pose(tn, TJ["acoes"][tn]["quadros"]), pose(d_, qs_)), 6)
    print("SEQ", L, "emendas", json.dumps(RL["emendas"]), "duplicados", json.dumps(RL["duplicados"]), flush=True)
json.dump(R, open(OUT, "w"), indent=1); print("AUD_MARCHAS_V29_OK", flush=True)
