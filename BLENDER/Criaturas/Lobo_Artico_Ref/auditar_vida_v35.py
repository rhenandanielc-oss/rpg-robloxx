"""Auditoria do bloco 1 do lote de vida (Deitar, Deitado, LevantarDeitado), por LOD, na malha deformada:
- DESLIZE: em cada janela PLANTADA de cada pata (vida_v35.json), pontos fixos = vertices da pata (selecao da v24: z < 0,5 e a 0,8 do pe
  no repouso) que estao a <= 0,03 do mais baixo no MEIO da janela; deslize = maior deslocamento horizontal desses pontos na janela,
  contados enquanto < 0,06 do chao (mesmo criterio da v24). Clipes no lugar (sem deslocamento de apresentacao).
- CHAO: por quadro, ponto mais baixo por regiao (ossos dominantes) - o mais negativo = compressao/atravessar.
- EMENDAS: maior diferenca de vertice entre Repouso q0 x Deitar q0, Deitar fim x Deitado q0, Deitado fim x Deitado q0 (laco),
  Deitado q0 x LevantarDeitado q0, LevantarDeitado fim x Repouso q0; e aceleracao na emenda x maior aceleracao dentro dos clipes.
Uso: blender -b anim_v35/CR_LoboArtico_Anim.blend -P auditar_vida_v35.py -- <saida_json> [LOW,LOD1,LOD2]"""
import bpy, sys, os, json, math
a = sys.argv[sys.argv.index("--") + 1:]; OUTJ = a[0]; LODS = a[1].split(",") if len(a) > 1 else ["LOW"]
SRC = os.path.dirname(bpy.data.filepath); sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]
VJ = json.load(open(os.path.join(SRC, "vida_v35.json"))); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
GR = {"pelve/ventre": ("Quadril", "Coluna1"), "barriga": ("Coluna2",), "esterno/peito": ("Coluna3", "Escapula_E", "Escapula_D", "Pescoco1"),
      "cotovelo+antebraco": ("Umero_E", "Umero_D", "Antebraco_E", "Antebraco_D"), "patas_D": ("Metacarpo_E", "Metacarpo_D", "Dedos_E", "Dedos_D"),
      "jarrete+canela": ("Tibia_E", "Tibia_D", "Metatarso_E", "Metatarso_D"), "patas_T": ("DedosPe_E", "DedosPe_D"), "queixo/cabeca": ("Cabeca", "Mandibula", "Pescoco2"),
      "cauda": ("Cauda1", "Cauda2", "Cauda3", "Cauda4")}
def usar(ac):
    acn = bpy.data.actions[ac]; ARM.animation_data.action = acn
    if len(acn.slots): ARM.animation_data.action_slot = acn.slots[0]
R = {}
for L in LODS:
    C = bpy.data.objects[L + "_Corpo"]; me = C.data; gn = {g.index: g.name for g in C.vertex_groups}
    dom = {}
    for v in me.vertices:
        if v.groups: dom[v.index] = gn.get(max(v.groups, key=lambda g: g.weight).group)
    ARM.animation_data.action = None
    for pb in ARM.pose.bones: pb.matrix_basis.identity()
    bpy.context.view_layer.update()
    patas = {k: [v.index for v in me.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8] for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"])}
    cache = {}
    def posado(ac, q):
        if (ac, q) not in cache:
            usar(ac); sc.frame_set(q); dg = bpy.context.evaluated_depsgraph_get(); e = C.evaluated_get(dg); m = e.to_mesh(); cache[(ac, q)] = [C.matrix_world @ v.co for v in m.vertices]; e.to_mesh_clear()
        return cache[(ac, q)]
    RL = {"acoes": {}, "emendas": {}}
    for ac, A in VJ["acoes"].items():
        n = A["quadros"]; chao = {}; pior_q = {}
        for q in range(n + 1):
            Pq = posado(ac, q)
            for i, z in enumerate(p.z for p in Pq):
                nm = dom.get(i)
                for reg, ossos in GR.items():
                    if nm in ossos and z < chao.get(reg, 9): chao[reg] = z; pior_q[reg] = q
        desl = {}
        for k, jans in A["plantas"].items():
            ds = []
            for j0, j1 in jans:
                if j1 - j0 < 1: continue
                mid = (j0 + j1) // 2; Pm = posado(ac, mid); zm = min(Pm[i].z for i in patas[k]); pts = [i for i in patas[k] if Pm[i].z < zm + 0.03]; mx = 0.0
                for q in range(j0, j1 + 1):
                    Pq = posado(ac, q)
                    for i in pts:
                        if Pq[i].z < zm + 0.06: mx = max(mx, math.hypot(Pq[i].x - Pm[i].x, Pq[i].y - Pm[i].y))
                ds.append({"janela": [j0, j1], "deslize": round(mx, 5), "pontos": len(pts)})
            desl[k] = ds
        RL["acoes"][ac] = {"chao_min_por_regiao": {k: [round(v, 3), pior_q[k]] for k, v in chao.items()}, "deslize": desl,
                           "deslize_max": round(max([d["deslize"] for v in desl.values() for d in v] + [0.0]), 5)}
        print("AUD", L, ac, "deslize", RL["acoes"][ac]["deslize_max"], "chao", RL["acoes"][ac]["chao_min_por_regiao"], flush=True)
    def dif(a_, b_): return max((p - q_).length for p, q_ in zip(a_, b_))
    def ac2(seq, j):
        return max(((seq[j + 1][i] - seq[j][i]) - (seq[j][i] - seq[j - 1][i])).length for i in range(0, len(seq[j]), 9))
    N = {ac: A["quadros"] for ac, A in VJ["acoes"].items()}
    pares = [("Repouso", 0, "Deitar", 0), ("Deitar", N["Deitar"], "Deitado", 0), ("Deitado", N["Deitado"], "Deitado", 0), ("Deitado", 0, "LevantarDeitado", 0), ("LevantarDeitado", N["LevantarDeitado"], "Repouso", 0)]
    for a1, q1, a2, q2 in pares: RL["emendas"]["%s q%d x %s q%d" % (a1, q1, a2, q2)] = round(dif(posado(a1, q1), posado(a2, q2)), 6)
    # aceleracao: Repouso(-2..0) | Deitar | Deitado | LevantarDeitado | Repouso(1..3)
    seqs = {"Repouso->Deitar": [posado("Repouso", 239), posado("Repouso", 240 - 0)] + [posado("Deitar", q) for q in range(1, 6)],
            "Deitar->Deitado": [posado("Deitar", q) for q in range(N["Deitar"] - 4, N["Deitar"] + 1)] + [posado("Deitado", q) for q in range(1, 4)],
            "Deitado->LevantarDeitado": [posado("Deitado", q) for q in range(N["Deitado"] - 3, N["Deitado"] + 1)] + [posado("LevantarDeitado", q) for q in range(1, 5)],
            "LevantarDeitado->Repouso": [posado("LevantarDeitado", q) for q in range(N["LevantarDeitado"] - 4, N["LevantarDeitado"] + 1)] + [posado("Repouso", q) for q in range(1, 4)]}
    def acc_max_clipe(ac):
        n = N[ac]; s = [posado(ac, q) for q in range(n + 1)]; return max(ac2(s, j) for j in range(1, n))
    vmax = {ac: acc_max_clipe(ac) for ac in N}
    for nm, sq in seqs.items():
        mid = len(sq) // 2; RL["emendas"]["acel " + nm] = [round(max(ac2(sq, j) for j in range(1, len(sq) - 1)), 5), round(max(vmax[x] for x in vmax if x in nm), 5)]
    R[L] = RL; print("AUD", L, "emendas", json.dumps(RL["emendas"]), flush=True)
json.dump(R, open(OUTJ, "w"), indent=1); print("AUD_VIDA_V35_OK", flush=True)
