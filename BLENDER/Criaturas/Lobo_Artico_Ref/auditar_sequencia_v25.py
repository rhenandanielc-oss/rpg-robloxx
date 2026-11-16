"""v25: auditoria da SEQUENCIA COMPLETA Repouso -> Arrancada -> Corrida x3 -> Frenagem -> Repouso (acoes de uma vez + lacos), com
o MESMO metodo de pontos fixos da v24 (diag_apoios_v24 / auditar_clipes_v21), adaptado a acoes NAO ciclicas:
- linha do tempo sem quadros duplicados: Repouso q230..q239 | Arrancada q0..q(n-1) (q n = Corrida q0) | Corrida q0..q13 x 3 |
  Frenagem q0..q(n-1) (q0 = Corrida q14 = q0; q n = Repouso q0) | Repouso q0..q10;
- deslocamento de apresentacao X acumulado por quadro: Repouso 0; Arrancada/Frenagem = CURVA gravada (transicoes_v25.json,
  X_por_quadro, nao uniforme); Corrida -v/30 por quadro (v = 20,357);
- apoio por quadro: Repouso = 4 patas; Arrancada/Frenagem = cronograma do gerador (apoio_por_quadro); Corrida = cronograma da
  marcha; um apoio = quadros consecutivos em apoio NA LINHA DO TEMPO (atravessa as emendas: uma fase so);
- pontos = vertices da pata que tocam o chao (<= 0,03 do mais baixo) no MEIO do apoio, FIXOS na fase, contados enquanto < 0,06
  do chao do meio; deslize = maior deslocamento horizontal (com X) em relacao ao meio; afundamento/flutuacao = altura minima
  da pata na fase - altura minima no repouso (como a auditoria v21);
- emendas: pose (posicoes dos vertices) e 2a diferenca (aceleracao) na emenda x maior aceleracao dentro dos clipes vizinhos;
  quadros duplicados: Repouso q0 x Arrancada q0, Arrancada q_fim x Corrida q0, Corrida q0 x Frenagem q0, Frenagem q_fim x
  Repouso q0 (diferenca max, stud).
Modo GLB (--glb <dir_export>): importa cada LOD numa cena limpa e roda pelo esqueleto importado.
Uso: blender -b <anim.blend> -P auditar_sequencia_v25.py -- <saida_json> [LOW,LOD1,LOD2]
     blender -b --factory-startup -P auditar_sequencia_v25.py -- <saida_json> LOW,LOD1,LOD2 --glb <dir_export> <dir_blend_fonte>"""
import bpy, sys, os, json, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIV = a[1].split(",") if len(a) > 1 else ["LOW", "LOD1", "LOD2"]
GLB = a[a.index("--glb") + 1] if "--glb" in a else None; SRC = os.path.abspath(a[a.index("--glb") + 2]) if GLB else os.path.dirname(bpy.data.filepath)
CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); TJ = json.load(open(os.path.join(SRC, "transicoes_v25.json"))); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
COR = CJ["marchas"]["Corrida"]; FPS = 30; VC = COR["v_studs_s"]; NA, NF = TJ["acoes"]["Arrancada"]["quadros"], TJ["acoes"]["Frenagem"]["quadros"]; NC = 14
LT = [("Repouso", q) for q in range(230, 240)] + [("Arrancada", q) for q in range(NA)] + [("Corrida", q) for _ in range(3) for q in range(NC)] + \
     [("Frenagem", q) for q in range(NF)] + [("Repouso", q) for q in range(0, 11)]
def dx(acao, q):                                   # X(q) - X(q-1) da entrada
    if acao in ("Arrancada", "Frenagem"): Xs = TJ["acoes"][acao]["X_por_quadro"]; return Xs[q] - Xs[q - 1] if q > 0 else (Xs[0] if acao == "Arrancada" else -VC / FPS)
    if acao == "Corrida": return -VC / FPS
    return 0.0
Xc = []; x = 0.0
for i, (ac_, q) in enumerate(LT):
    if i > 0: x += dx(ac_, q)
    Xc.append(x)
def apoio(acao, k, q):
    if acao == "Repouso": return True
    if acao in ("Arrancada", "Frenagem"): return TJ["acoes"][acao]["apoio_por_quadro"][k][q]
    u = ((q / FPS / COR["T"]) - COR["fases"][k]) % 1.0; return u < COR["apoio"]
R = {"metodo": __doc__.split("Uso:")[0], "unidade": "stud", "tolerancia_deslize": 0.03, "linha_do_tempo": ["%s q%d" % e for e in LT], "X": [round(x, 4) for x in Xc], "niveis": {}}
for L in NIV:
    if GLB:
        bpy.ops.wm.read_factory_settings(use_empty=True); bpy.context.scene.render.fps = FPS     # 30 qps ANTES de importar (cena nova abre em 24)
        ops = bpy.ops.import_scene.gltf.get_rna_type().properties.keys()
        EXP = json.load(open(os.path.join(GLB, os.environ.get("EXP_JSON", "export_clipes_v25.json"))))   # v26: EXP_JSON=export_clipes_v26.json
        bpy.ops.import_scene.gltf(filepath=os.path.join(GLB, EXP["lods"][L]["arquivo"]), **({"bone_heuristic": "BLENDER"} if "bone_heuristic" in ops else {}))
        A = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
        if A.animation_data is None: A.animation_data_create()
        ACS = {n: next(x for x in bpy.data.actions if x.name == n or x.name.startswith(n + "|") or x.name.startswith(n)) for n in ("Repouso", "Arrancada", "Corrida", "Frenagem")}
    else:
        A = bpy.data.objects["LoboArtico_Rig"]; ACS = {n: bpy.data.actions[n] for n in ("Repouso", "Arrancada", "Corrida", "Frenagem")}
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
        pior = max((f for f in fs if any(x in f["acoes"] for x in ("Arrancada", "Frenagem"))), key=lambda f: f["deslize"])
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
    for nm, (x1, x2) in {"Repouso q0 x Arrancada q0": (("Repouso", 0), ("Arrancada", 0)), "Arrancada fim x Corrida q0": (("Arrancada", NA), ("Corrida", 0)),
                         "Corrida q0 x Frenagem q0": (("Corrida", 0), ("Frenagem", 0)), "Frenagem fim x Repouso q0": (("Frenagem", NF), ("Repouso", 0))}.items():
        RL["duplicados"][nm] = round(dif(pose(*x1), pose(*x2)), 6)
    print("SEQ", L, "emendas", json.dumps(RL["emendas"]), "duplicados", json.dumps(RL["duplicados"]), flush=True)
json.dump(R, open(OUT, "w"), indent=1); print("AUD_SEQUENCIA_V25_OK", flush=True)
