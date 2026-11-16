"""v24: DIAGNOSTICO (so leitura) do deslize dos apoios, com o MESMO metodo do auditar_clipes_v21.py (contrato de aceite):
- apoio = cronograma da marcha (clipes_v21.json); o apoio que cruza a emenda e UMA fase (quadros do ciclo anterior = q - n,
  com o deslocamento de apresentacao do ciclo anterior); deslocamento de apresentacao: o corpo anda a -Y a v = D/T;
- pontos medidos = vertices da pata que tocam o chao (ate 0,03 acima do mais baixo) no MEIO do apoio, FIXOS para a fase
  inteira; cada ponto conta enquanto esta a < 0,06 do chao do meio do apoio; deslize = maior deslocamento horizontal
  (stud) de um ponto em relacao a ele mesmo no meio do apoio.
Decomposicao do pior ponto de cada fase (pior quadro):
- OSSO: o mesmo ponto se seguisse RIGIDO o osso dominante (Metacarpo/Metatarso ou Dedos) -> deslize vindo do clipe (trajetoria,
  rolamento, IK gravado em FK);
- PELE = real - OSSO: vindo dos pesos/malha (LBS de varios ossos, reducao dos LODs);
- PIVO: deslize do ponto de giro do rolamento C (70% do osso dos dedos no repouso, rigido no metacarpo/metatarso: o clipe
  gira o metacarpo em torno de C) e da ponta dos dedos (osso), stud; com IK exato e trajetoria certa, C fica parado;
- ALTURA do pior ponto no pior quadro (acima do chao do meio do apoio): distingue arrasto plantado (altura ~0) de ponto
  que esta saindo do chao no rolamento (altura perto de 0,06).
Tambem: centro da area de contato (media dos pontos a < 0,04 do mais baixo a cada quadro, metodo do relatorio v12) e a sua
variacao, so informativa (o centro anda naturalmente no rolamento almofada -> dedos).
Uso: blender -b <anim.blend> -P diag_apoios_v24.py -- <saida_json> [LOW,LOD1,LOD2] [Andar,Trote,Corrida]"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIV = a[1].split(",") if len(a) > 1 else ["LOW", "LOD1", "LOD2"]
ACOES = a[2].split(",") if len(a) > 2 else ["Andar", "Trote", "Corrida"]
sc = bpy.context.scene; SRC = os.path.dirname(bpy.data.filepath); CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); MAR = CJ["marchas"]
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); FPS = CJ["fps"]; ARM = bpy.data.objects["LoboArtico_Rig"]; OSS = {b.name for b in ARM.data.bones}
CAD = {"DE": ("Metacarpo_E", "Dedos_E"), "DD": ("Metacarpo_D", "Dedos_D"), "TE": ("Metatarso_E", "DedosPe_E"), "TD": ("Metatarso_D", "DedosPe_D")}
def usar(n):
    ac = bpy.data.actions[n]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    return ac
def fase(acao, k, q): A_ = MAR[acao]; u = ((q / FPS / A_["T"]) - A_["fases"][k]) % 1.0; return u < A_["apoio"]
def posado(o):
    dg = bpy.context.evaluated_depsgraph_get(); e = o.evaluated_get(dg); m = e.to_mesh(); P = [v.co.copy() for v in m.vertices]; e.to_mesh_clear(); return P
R = {"metodo": __doc__.split("Uso:")[0], "unidade": "stud", "tolerancia": 0.03, "niveis": {}}
for L in NIV:
    C = bpy.data.objects[L + "_Corpo"]; me = C.data; usar("Andar"); sc.frame_set(0)
    P0 = [v.co.copy() for v in me.vertices]; gn = {g.index: g.name for g in C.vertex_groups}
    W = [{gn[e.group]: e.weight for e in v.groups if gn[e.group] in OSS} for v in me.vertices]
    patas = {k: [v.index for v in me.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8]
             for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"])}
    # repouso (sem acao) para a posicao de repouso dos vertices em relacao aos ossos
    ARM.animation_data.action = None
    for pb in ARM.pose.bones: pb.matrix_basis.identity()
    bpy.context.view_layer.update(); PR = [v.co.copy() for v in me.vertices]
    dom = {i: max(W[i], key=W[i].get) for ids in patas.values() for i in ids}
    RL = R["niveis"][L] = {}
    for acao in ACOES:
        ac = usar(acao); n = int(ac.frame_range[1]); v = MAR[acao]["v_studs_s"]; G = MAR[acao]
        PP, RG, PIVQ = {}, {}, {}
        for q in range(n + 1):
            sc.frame_set(q); PP[q] = posado(C); dy = -v * q / FPS
            Mb = {nm: ARM.pose.bones[nm].matrix @ ARM.data.bones[nm].matrix_local.inverted() for nm in OSS}
            RG[q] = {i: Mb[dom[i]] @ PR[i] for ids in patas.values() for i in ids}
            PIVQ[q] = {}
            for k, (pe, dd) in CAD.items():
                b = ARM.pose.bones[dd]; br = ARM.data.bones[dd]; c_r = br.head_local + 0.7 * (br.tail_local - br.head_local)
                PIVQ[q][k] = (Mb[pe] @ c_r, b.tail.copy())      # C e rigido no METACARPO/METATARSO (o rolamento gira o metacarpo em torno de C)
        def off(qq): return -v * qq / FPS          # deslocamento de apresentacao continuo (qq < 0 = ciclo anterior), igual ao auditar_clipes_v21
        RA = RL[acao] = {"quadros": n, "v_studs_s": v, "ciclo_s": round(n / FPS, 4), "apoio_fracao": G["apoio"], "patas": {}}
        for k, ids in patas.items():
            qs = [q for q in range(n) if fase(acao, k, q)]                    # q = n e igual a q = 0 (laco)
            segs, cur = [], []
            for q in range(n):
                if q in qs: cur.append(q)
                elif cur: segs.append(cur); cur = []
            if cur: segs.append(cur)
            if len(segs) > 1 and segs[0][0] == 0 and segs[-1][-1] == n - 1: segs = [[q - n for q in segs[-1]] + segs[0]] + segs[1:-1]   # apoio que cruza a emenda = UMA fase
            fases = []
            for sg in segs:
                qm = sg[len(sg) // 2]; qmm = qm % n
                def X(qq, i, src): P_ = (PP if src == "real" else RG)[qq % n][i]; return P_ + V((0, off(qq), 0))
                zm = min(PP[qmm][i].z for i in ids); pts = [i for i in ids if PP[qmm][i].z < zm + 0.03]
                ref = {i: X(qm, i, "real") for i in pts}; refr = {i: X(qm, i, "rigido") for i in pts}
                pior = (0.0, None, None); traj = []
                for qq in sg:
                    for i in pts:
                        p_ = PP[qq % n][i]
                        if p_.z < zm + 0.06:
                            d = (X(qq, i, "real") - ref[i]).to_2d().length
                            if d > pior[0]: pior = (d, qq, i)
                q_, i_ = pior[1], pior[2]
                if i_ is None: continue
                for qq in sg: p_ = X(qq, i_, "real"); traj.append([qq, round(p_.x, 4), round(p_.y, 4), round(PP[qq % n][i_].z - zm, 4)])
                d_osso = (X(q_, i_, "rigido") - refr[i_]).to_2d().length
                d_pele = ((X(q_, i_, "real") - X(q_, i_, "rigido")) - (ref[i_] - refr[i_])).to_2d().length
                pv = [(PIVQ[qq % n][k][0] + V((0, off(qq), 0))) for qq in sg]; pt = [(PIVQ[qq % n][k][1] + V((0, off(qq), 0))) for qq in sg]
                pv_m = pv[len(sg) // 2]; pt_m = pt[len(sg) // 2]
                # centro da area de contato (informativo)
                cts = []
                for qq in sg:
                    z2 = min(PP[qq % n][i].z for i in ids); ct = [PP[qq % n][i] for i in ids if PP[qq % n][i].z < z2 + 0.04]
                    cts.append((sum(ct, V()) / len(ct)) + V((0, off(qq), 0)))
                cmid = cts[len(sg) // 2]
                fases.append({"inicio": sg[0], "fim": sg[-1], "cruza_emenda": sg[0] < 0, "pontos": len(pts), "deslize": round(pior[0], 5), "quadro_pior": q_,
                              "vertice_pior": i_, "osso_dominante": dom[i_], "pesos_pior": {kk: round(x, 3) for kk, x in sorted(W[i_].items(), key=lambda t: -t[1]) if x > 0.01},
                              "componente_osso": round(d_osso, 5), "componente_pele": round(d_pele, 5), "altura_pior_no_quadro": round(PP[q_ % n][i_].z - zm, 4),
                              "pivo_rolamento_deslize": round(max((p - pv_m).to_2d().length for p in pv), 5), "ponta_dedos_deslize": round(max((p - pt_m).to_2d().length for p in pt), 5),
                              "centro_contato_variacao": round(max((c - cmid).to_2d().length for c in cts), 4), "afundamento_min_z": round(min(min(PP[qq % n][i].z for i in ids) for qq in sg), 4),
                              "trajetoria_pior_ponto": traj})
            RA["patas"][k] = fases
            pf = max(fases, key=lambda f: f["deslize"])
            print("APOIO", L, acao, k, pf["inicio"], pf["fim"], "desl", pf["deslize"], "osso", pf["componente_osso"], "pele", pf["componente_pele"], "h", pf["altura_pior_no_quadro"],
                  "pivo", pf["pivo_rolamento_deslize"], "ponta", pf["ponta_dedos_deslize"], "q", pf["quadro_pior"], pf["osso_dominante"], flush=True)
json.dump(R, open(OUT, "w"), indent=1); print("DIAG_APOIOS_V24_OK", flush=True)
