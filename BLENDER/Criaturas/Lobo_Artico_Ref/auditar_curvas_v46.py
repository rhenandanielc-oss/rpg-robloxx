"""v46: auditoria MUNDIAL das curvas andando (translacao + rotacao externas aplicadas a malha deformada), por LOD.
Linha do tempo e mistura por peso = linha_curvas_v46.py (emula o controlador proposto). Mede, por pata e por fase de apoio:
  deslize = maior deslocamento HORIZONTAL MUNDIAL dos vertices da sola que tocam o chao no meio do apoio (enquanto < 0,06 do chao);
  afundamento / flutuacao = altura minima da pata na fase - minima no repouso (chao em z = 0 do armature).
  (o criterio local e deslize <= 0,03 stud por fase; o Andar reto aprovado e a referencia de comparacao: modo ANTES = Andar reto
  com o pivo girando, que e o que o Controle r10e faz hoje andando)
Cruzamento: menor folga lateral entre a pata esquerda e a direita do mesmo par (MCP no referencial do corpo; <0 = cruzou).
Emendas: 2a diferenca mundial de vertices amostrados (aceleracao por quadro^2) nas trocas de peso x mediana do cenario.
Uso: blender -b anim_v46/CR_LoboArtico_Anim.blend -P auditar_curvas_v46.py -- <saida_json> <LOD> [cenarios,...] [--antes]"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector as V, Matrix
import linha_curvas_v46 as LC
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); L = a[1]
CEN = a[2].split(",") if len(a) > 2 and not a[2].startswith("--") else LC.CENARIOS; ANTES = "--antes" in a; PES = "--pes" in a; SEQ = "--seq" in a
if SEQ:
    VJB = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "curvas_v46b.json")))["acoes"]; CEN = [c for c in CEN if c in LC.SEQ_B]
    _pp = os.path.join(os.path.dirname(bpy.data.filepath), "partida_v48.json")
    if os.path.exists(_pp): VJB.update(json.load(open(_pp))["acoes"])
    for _m in ("trote", "corrida"):
        _pm = os.path.join(os.path.dirname(bpy.data.filepath), "curvas_%s_v49.json" % _m)
        if os.path.exists(_pm): VJB.update(json.load(open(_pm))["acoes"])
    _MARCHAS = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "clipes_v21.json")))["marchas"]
SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
ARM = bpy.data.objects["LoboArtico_Rig"]; P = ARM.pose.bones; sc = bpy.context.scene
REST = {b.name: b.matrix_local.copy() for b in ARM.data.bones}
MCPB = {"DE": "Metacarpo_E", "DD": "Metacarpo_D", "TE": "Metatarso_E", "TD": "Metatarso_D"}
DEDB = {"DE": "Dedos_E", "DD": "Dedos_D", "TE": "DedosPe_E", "TD": "DedosPe_D"}
for pb in P: pb.rotation_mode = "QUATERNION"
CACHE = {}; DED = {}
def basis(acao, q):
    if (acao, q) not in CACHE:
        ac = bpy.data.actions[acao]; ARM.animation_data.action = ac
        if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
        sc.frame_set(int(ac.frame_range[0]) + q)
        CACHE[(acao, q)] = {pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P}
        DED[(acao, q)] = {k: (ARM.matrix_world @ P[b].tail).to_2d().to_3d() for k, b in DEDB.items()}
        ARM.animation_data.action = None
    return CACHE[(acao, q)]
for n in ["Repouso", "Andar"] + (["Trote", "Corrida"] if SEQ else []) + (list(VJB) if SEQ else ["AndarCurvaEsquerda", "AndarCurvaDireita", "AndarCurvaFechadaEsquerda", "AndarCurvaFechadaDireita"]):
    for q in range(240 if n == "Repouso" else (VJB[n]["quadros"] if SEQ and n in VJB else (int(bpy.data.actions[n].frame_range[1] - bpy.data.actions[n].frame_range[0]) if n in ("Trote", "Corrida") else LC.NQ))): basis(n, q)
ARM.animation_data.action = None
C = bpy.data.objects[L + "_Corpo"]; Mw = C.matrix_world.copy()
for pb in P: pb.matrix_basis.identity()
bpy.context.view_layer.update(); P0 = [Mw @ v.co for v in C.data.vertices]
patas = {k: [i for i, p in enumerate(P0) if p.z < 0.5 and math.hypot(p.x - xy[0], p.y - xy[1]) < 0.8] for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"])}
zr = {k: min(P0[i].z for i in ids) for k, ids in patas.items()}; amo = list(range(0, len(P0), 23))
R = {"metodo": __doc__.split("Uso:")[0], "lod": L, "modo": "ANTES (Andar reto + pivo girando)" if ANTES else ("v46b (sequencia de clipes, curva externa de cada clipe)" if SEQ else ("v46 (mistura Andar/Curva; pivo pelas patas apoiadas)" if PES else "v46 (mistura Andar/Curva; giro nominal)")), "tolerancia_deslize": 0.03, "cenarios": {}}
for cn in CEN:
    _g = next((m for m in ("Trote", "Corrida") if cn.startswith(m.lower())), None)
    LT = LC.linha_seq(cn, VJB, G=(dict(_MARCHAS[_g], nome=_g) if _g else None)) if SEQ else LC.linha(cn)
    if ANTES: LT = [dict(e, mix=[("Repouso", q_, w) if a_ == "Repouso" else ("Andar", q_, w) for a_, q_, w in e["mix"]]) for e in LT]
    elif PES and not SEQ:
        def dedos(mix):
            tot = sum(w for _, _, w in mix); return {k: sum((DED[(a_, q_)][k] * (w / tot) for a_, q_, w in mix), V((0, 0, 0))) for k in DEDB}
        LT = LC.raiz_pelos_pes(LT, dedos)
    PW, AM, MCP = [], [], []
    for e in LT:
        LC.aplicar(P, None, REST, e["mix"], basis); bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get(); ev = C.evaluated_get(dg); m = ev.to_mesh(); W = e["M"] @ Mw
        PW.append({k: [W @ m.vertices[i].co for i in ids] for k, ids in patas.items()}); AM.append([W @ m.vertices[i].co for i in amo]); ev.to_mesh_clear()
        MCP.append({k: (ARM.matrix_world @ P[b].tail).copy() for k, b in MCPB.items()})
    RS = {"quadros": len(LT), "rumo_final_graus": round(LT[-1]["psi"], 2), "deslocamento_final": [round(x, 3) for x in LT[-1]["pos"]][:2], "patas": {}}
    for k in patas:
        segs, cur = [], []
        for i, e in enumerate(LT):
            if e["apoio"][k]: cur.append(i)
            elif cur: segs.append(cur); cur = []
        if cur: segs.append(cur)
        fs = []
        for sg in segs:
            if len(sg) < 4: continue
            im = sg[len(sg) // 2]; zm = min(p.z for p in PW[im][k]); pts = [j for j, p in enumerate(PW[im][k]) if p.z < zm + 0.03]; mx = 0.0
            for i in sg:
                for j in pts:
                    p_ = PW[i][k][j]
                    if p_.z < zm + 0.06: mx = max(mx, (p_ - PW[im][k][j]).to_2d().length)
            alt = min(min(p.z for p in PW[i][k]) - zr[k] for i in sg)
            om_ = max(abs(LT[i]["omega"]) for i in sg)
            fs.append({"q": [sg[0], sg[-1]], "omega_max": round(om_, 1), "deslize": round(mx, 4), "afund": round(-min(alt, 0), 4), "flut": round(max(alt, 0), 4)})
        cur_ = [f for f in fs if f["omega_max"] > 0.5]
        RS["patas"][k] = {"fases": fs, "pior_deslize_em_curva": max((f["deslize"] for f in cur_), default=0.0),
                          "pior_deslize_reto": max((f["deslize"] for f in fs if f["omega_max"] <= 0.5), default=0.0),
                          "afund_max": max(f["afund"] for f in fs), "flut_max": max(f["flut"] for f in fs),
                          "fases_acima_0_03": sum(1 for f in fs if f["deslize"] > 0.03)}
    gap = {"diant": min(MCP[i]["DE"].x - MCP[i]["DD"].x for i in range(len(LT))), "tras": min(MCP[i]["TE"].x - MCP[i]["TD"].x for i in range(len(LT)))}
    RS["folga_lateral_min_MCP"] = {k_: round(v_, 3) for k_, v_ in gap.items()}
    acc = [max(((AM[i + 1][j] - AM[i][j]) - (AM[i][j] - AM[i - 1][j])).length for j in range(len(amo))) for i in range(1, len(LT) - 1)]
    sa = sorted(acc); RS["aceleracao_q2"] = {"mediana": round(sa[len(sa) // 2], 5), "p95": round(sa[int(len(sa) * 0.95)], 5), "max": round(sa[-1], 5),
                                          "quadro_max": acc.index(sa[-1]) + 1, "serie": [round(x, 4) for x in acc]}
    R["cenarios"][cn] = RS
    print("AUD", L, "ANTES" if ANTES else ("v46b" if SEQ else ("v46pes" if PES else "v46nominal")), cn, "rumo", RS["rumo_final_graus"], "deslize_curva", {k: RS["patas"][k]["pior_deslize_em_curva"] for k in patas},
          "reto", {k: RS["patas"][k]["pior_deslize_reto"] for k in patas}, "fases>0.03", {k: RS["patas"][k]["fases_acima_0_03"] for k in patas},
          "afund", max(RS["patas"][k]["afund_max"] for k in patas), "flut", max(RS["patas"][k]["flut_max"] for k in patas),
          "folga", RS["folga_lateral_min_MCP"], "acel", RS["aceleracao_q2"], flush=True)
json.dump(R, open(OUT, "w"), indent=1); print("AUD_CURVAS_V46_OK", flush=True)
