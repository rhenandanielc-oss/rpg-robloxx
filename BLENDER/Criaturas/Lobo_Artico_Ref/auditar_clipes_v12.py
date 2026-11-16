"""Auditoria SO LEITURA dos clipes do lote 1 (Repouso, Andar, Teste_Transicao) COM O RIG REAL, por LOD:
- APOIOS por fase (deslocamento de apresentacao: o corpo anda a -Y na velocidade do clipe; Teste_Transicao: v * amplitude):
  pontos de contato = vertices do corpo da pata (repouso: z < 0,5 a 0,8 do pe) que estao a menos de 0,04 do mais baixo;
  apoio = Andar: pelo cronograma da marcha; demais: altura minima da pata ate 0,035 acima da do repouso; por apoio: DESLIZE horizontal maximo do centro do contato
  (vertices que tocam o chao no meio do apoio, seguidos enquanto estao a < 0,06 do chao; o centro do contato muda
  naturalmente no rolamento almofada -> dedos e nao e deslize), flutuacao/afundamento (altura minima - a do repouso), altura do balanco;
  velocidade medida = recuo medio do contato apoiado no clipe no lugar (stud/s);
- LACO (Andar, Repouso): diferenca de posicao entre o quadro 0 e o ultimo (=0) e aceleracao na emenda (q1-q0 x qN-q(N-1))
  comparada a maior aceleracao dentro do proprio clipe;
- deformacao por quadro (a cada 2): faces viradas (numero/area) e arestas > 2x na pele por regiao (garganta, axila,
  cauda/pata E, resto), fresta da costura, Mandibula/Palpebras fora da piscada, marca/cristais/pelagem (distancia a pele).
Tolerancias TECNICAS (visiveis a ~10-25 studs; nao regras): deslize <= 0,03 stud por apoio; afundamento <= 0,03 abaixo do
repouso (que ja tem a pata 0,049 abaixo do chao, herdado); flutuacao <= 0,035 no apoio.
Uso: blender -b <anim.blend> -P auditar_clipes_v12.py -- <saida_json> [LOW,LOD1,LOD2] [acoes]"""
import bpy, sys, os, json, math
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIV = a[1].split(",") if len(a) > 1 else ["LOW", "LOD1", "LOD2"]
ACOES = a[2].split(",") if len(a) > 2 else ["Repouso", "Andar", "Teste_Transicao"]
sc = bpy.context.scene; SRC = os.path.dirname(bpy.data.filepath); CJ = json.load(open(os.path.join(SRC, "clipes_v12.json"))); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
ARM = bpy.data.objects["LoboArtico_Rig"]; OSS = {b.name for b in ARM.data.bones}; FPS = CJ["fps"]
CP, CN = V(PIV["costura"]["ponto"]), V(PIV["costura"]["normal"]); V_AND = CJ["andar"]["v_studs_s"]
TT = CJ["acoes"]["Teste_Transicao"]["trechos_s"]; c_ = [sum(TT[:i]) for i in range(len(TT) + 1)]
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def amp_tr(t):
    if t < c_[1]: return 0.0
    if t < c_[2]: return suave((t - c_[1]) / TT[1])
    if t < c_[3]: return 1.0
    if t < c_[4]: return 1 - suave((t - c_[3]) / TT[3])
    return 0.0
def desloc(acao, q):
    if acao == "Andar": return -V_AND * q / FPS
    if acao == "Teste_Transicao": return -V_AND * sum(amp_tr(i / FPS) for i in range(q)) / FPS
    return 0.0
def usar(acao):
    ac = bpy.data.actions[acao]; ad = ARM.animation_data; ad.action = ac
    if getattr(ad, "action_slot", None) is None and hasattr(ac, "slots") and len(ac.slots): ad.action_slot = ac.slots[0]   # Blender 5: slot
    return ac
def fase_andar(k, q):
    """cronograma da marcha (clipes_v12.json): 'apoio' (pata no chao, inclui o rolamento sobre os dedos) / 'balanco'"""
    A_ = CJ["andar"]; u = ((q / FPS / A_["T"]) - A_["fases"][k]) % 1.0; return "apoio" if u < A_["apoio"] else "balanco"
def posado(o):
    dg = bpy.context.evaluated_depsgraph_get(); e = o.evaluated_get(dg); m = e.to_mesh(); P = [v.co.copy() for v in m.vertices]; e.to_mesh_clear(); return P
def regiao(p):
    if p.y < -2.6 and p.z < 5.6: return "garganta"
    if abs(p.x) > 0.4 and -3.7 < p.y < -1.5 and 1.6 < p.z < 4.2: return "axila"
    if p.y > 2.2 and p.z < 4.3 and p.x > -0.2: return "cauda_pata_E"
    return "resto"
R = {"tolerancias": {"deslize_stud": 0.03, "afundamento_stud": 0.03, "flutuacao_stud": 0.035}, "niveis": {}}
for L in NIV:
    H, C = bpy.data.objects[L + "_Cabeca"], bpy.data.objects[L + "_Corpo"]; me = C.data; sc.frame_set(0)
    usar("Andar"); sc.frame_set(0)
    for o in (H, C): o.data.update()
    P0c = [v.co.copy() for v in me.vertices]; P0h = [v.co.copy() for v in H.data.vertices]
    gn = {g.index: g.name for g in C.vertex_groups}; Wc = [{gn[e.group]: e.weight for e in v.groups if gn[e.group] in OSS} for v in me.vertices]
    patas = {}
    for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"]):
        patas[k] = [v.index for v in me.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8]
    zr = {k: min(P0c[i].z for i in ids) for k, ids in patas.items()}
    F = [list(p.vertices) for p in me.polygons]; A = [p.area for p in me.polygons]; N0 = [p.normal.copy() for p in me.polygons]
    REGF = [regiao(sum((P0c[i] for i in f), V()) / len(f)) for f in F]
    ares = [(e.vertices[0], e.vertices[1]) for e in me.edges if (P0c[e.vertices[0]] - P0c[e.vertices[1]]).length > 0.01]
    kd = KDTree(len(me.vertices))
    for v in me.vertices: kd.insert(v.co, v.index)
    kd.balance(); pares = [(v.index, kd.find(v.co)[1]) for v in H.data.vertices if abs((v.co - CP).dot(CN)) < 0.2 and kd.find(v.co)[2] < 1e-4]
    bv0 = BVHTree.FromPolygons(P0c, F); MARCA = bpy.data.objects["LOW_Marca"]; d0m = [bv0.find_nearest(v.co)[3] for v in MARCA.data.vertices] if L != "LOD2" else []
    RL = R["niveis"][L] = {}
    for acao in ACOES:
        ac = usar(acao); n = int(ac.frame_range[1]); r = RL[acao] = {"quadros": n}
        trilha = {k: [] for k in patas}; PPd = {}; defo = {}; fresta = 0.0; marca = 0.0; boca = 0.0; palp = 0.0; PP = {}
        for q in range(0, n + 1):
            sc.frame_set(q); Pc = posado(C); dy = desloc(acao, q); PP[q] = Pc
            for k, ids in patas.items():
                zm = min(Pc[i].z for i in ids); ct = [Pc[i] for i in ids if Pc[i].z < zm + 0.04]; c0 = sum(ct, V()) / len(ct)
                trilha[k].append((q, zm - zr[k], V((c0.x, c0.y + dy, 0)), c0.y)); PPd.setdefault(q, dy)
            pbm = ARM.pose.bones["Mandibula"]; boca = max(boca, math.degrees(pbm.rotation_quaternion.angle))
            if acao != "Repouso" or not (5.2 * FPS <= q <= 5.6 * FPS):
                palp = max(palp, max(math.degrees(ARM.pose.bones[nm].rotation_quaternion.angle) for nm in ("Palpebra_Sup_E", "Palpebra_Sup_D")))
            if q % 2 == 0:
                Ph = posado(H); fresta = max(fresta, max(((Ph[i] - Pc[j]).length for i, j in pares), default=0.0))
                for fi, f in enumerate(F):
                    if A[fi] < 2e-4: continue
                    w = {}
                    for vi in f:
                        for kk, x in Wc[vi].items(): w[kk] = w.get(kk, 0) + x
                    pb = ARM.pose.bones[max(w, key=w.get)]; Rm = (pb.matrix @ pb.bone.matrix_local.inverted()).to_3x3()
                    n1 = (Pc[f[1]] - Pc[f[0]]).cross(Pc[f[2]] - Pc[f[0]]).normalized()
                    if n1.dot(Rm @ N0[fi]) < 0:
                        d = defo.setdefault(REGF[fi], {"viradas_max": 0, "area_max": 0.0, "_q": {}}); d["_q"].setdefault(q, [0, 0.0]); d["_q"][q][0] += 1; d["_q"][q][1] += A[fi]
                est = {}
                for i, j in ares:
                    if (Pc[i] - Pc[j]).length > 2 * (P0c[i] - P0c[j]).length:
                        rg = regiao(P0c[i]); est[rg] = est.get(rg, 0) + 1
                for rg, c in est.items(): defo.setdefault(rg, {"viradas_max": 0, "area_max": 0.0, "_q": {}}); defo[rg]["esticadas_>2x_max"] = max(defo[rg].get("esticadas_>2x_max", 0), c)
                if d0m:
                    bv = BVHTree.FromPolygons(Pc, F); Pm = posado(MARCA); marca = max(marca, max(abs(bv.find_nearest(p)[3] - d0) for p, d0 in zip(Pm, d0m)))
        for rg, d in defo.items():
            if d["_q"]: qm = max(d["_q"], key=lambda q: d["_q"][q][1]); d["viradas_max"] = max(v[0] for v in d["_q"].values()); d["area_max"] = round(d["_q"][qm][1], 4); d["quadro_pior"] = qm
            del d["_q"]
        apoios = {}
        for k, tr in trilha.items():
            segs, cur = [], []
            for q, h, p, yl in tr:
                no_chao = (fase_andar(k, q) == "apoio") if acao == "Andar" else h < 0.012    # Andar: cronograma; demais: altura
                if no_chao: cur.append((q, h, p, yl))
                elif cur: segs.append(cur); cur = []
            if acao == "Andar" and len(segs) > 1 and segs[0][0][0] == 0 and segs[-1][-1][0] == n:  # apoio que cruza a emenda do laco
                segs[0] = [(q_ + n, h_, p_ + V((0, -V_AND * n / FPS, 0)), y_) for q_, h_, p_, y_ in segs[-1][:-1]] + segs[0]; segs = segs[:-1]
            if cur: segs.append(cur)
            def desl_pontos(sg):                                        # vertices que tocam o chao no MEIO do apoio, seguidos
                qm = sg[len(sg) // 2][0] % n if acao == "Andar" else sg[len(sg) // 2][0]
                zm = min(PP[qm][i].z for i in patas[k]); pts = [i for i in patas[k] if PP[qm][i].z < zm + 0.03]; mx = 0.0
                ref = {i: PP[qm][i] + V((0, PPd[qm], 0)) for i in pts}
                for q_, _, _, _ in sg:
                    qq = q_ % n if acao == "Andar" else q_; dd = PPd[qq] - (V_AND * n / FPS if (acao == "Andar" and q_ >= n) else 0.0)
                    for i in pts:
                        p_ = PP[qq][i]
                        if p_.z < zm + 0.06: mx = max(mx, ((p_ + V((0, dd, 0))) - ref[i]).to_2d().length)
                return mx
            des = [desl_pontos(s) for s in segs if len(s) >= 3]
            alt = [min(h for _, h, _, _ in s) for s in segs]; maxh = max(h for _, h, _, _ in tr)
            vel = [((s[-1][3] - s[0][3]) / ((s[-1][0] - s[0][0]) / FPS)) for s in segs if len(s) >= 4 and s[-1][0] > s[0][0]]
            apoios[k] = {"apoios": len(segs), "deslize_max": round(max(des, default=0.0), 4), "deslize_medio": round(sum(des) / len(des), 4) if des else 0.0,
                         "afundamento_max": round(-min(min(alt, default=0.0), 0.0), 4), "flutuacao_max_no_apoio": round(max(max(alt, default=0.0), 0.0), 4),
                         "altura_balanco_max": round(maxh, 3), "velocidade_medida_no_lugar": round(sum(vel) / len(vel), 3) if vel else 0.0}
        r["apoios"] = apoios; r["deformacao_por_regiao"] = defo; r["costura_fresta_max"] = round(fresta, 6); r["marca_dist_delta_max"] = round(marca, 4)
        r["mandibula_giro_max_graus"] = round(boca, 3); r["palpebra_giro_max_fora_da_piscada_graus"] = round(palp, 3)
        if acao in ("Andar", "Repouso"):
            Pn, Pn1, P1 = PP[n], PP[n - 1], PP[1]
            ac2 = [max(((PP[q + 1][i] - PP[q][i]) - (PP[q][i] - PP[q - 1][i])).length for i in range(0, len(P1), 7)) for q in range(1, n)]
            r["laco"] = {"pose_q0_x_qN": round(max((a_ - b_).length for a_, b_ in zip(PP[0], Pn)), 6),
                         "aceleracao_na_emenda": round(max(((p1 - p0) - (pn - pn1)).length for p0, p1, pn, pn1 in zip(PP[0], P1, Pn, Pn1)), 5),
                         "aceleracao_max_dentro_do_clipe": round(max(ac2), 5), "passo_medio_por_quadro": round(sum((p1 - p0).length for p0, p1 in zip(PP[0], P1)) / len(P1), 5)}
        print("AUDCL", L, acao, json.dumps(r), flush=True)
json.dump(R, open(OUT, "w"), indent=1); print("AUD_CLIPES_OK", flush=True)
