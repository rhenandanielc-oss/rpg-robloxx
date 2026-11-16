"""Auditoria SO LEITURA do rig piloto v9 COM O RIG REAL (malhas avaliadas pelo modificador Armature na acao
'Teste_Piloto'; nada e girado por script), por LOD e por quadro-pico de cada trecho:
- repouso: desvio maximo das malhas no quadro 0 frente as posicoes da v8 (tem de ser 0);
- pele (cabeca so pele UV x<0,9; corpo inteiro): arestas visiveis (> 0,01 no repouso) esticadas > 1,6x / > 2x e
  comprimidas < 0,5x; faces viradas (normal posada contra a normal de repouso levada pelo osso dominante; area > 2e-4);
  colapso (vertice que chega a < 60% da distancia de repouso ao seu osso dominante, so os que estavam a > 0,15);
- costura: distancia maxima entre os pares coincidentes cabeca/corpo posados;
- chao: z minimo de cada pata (contra o repouso) e deslize horizontal das patas plantadas nos trechos do tronco;
- cristais: variacao relativa maxima das arestas (forma rigida) e distancia da base a pele;
- marca: distancia maxima a pele posada (descolamento) ; pelagem: distancia raiz -> pele (p99 e maxima);
- boca maxima: desvio rig x teste v8 (giro por peso) e cantos (arestas visiveis > 0,06 abertas, > 2x / > 3x, zona 0,35);
- palpebras fechadas: amostras da iris descobertas (raio para fora do globo sem bater na pele);
- so LOD0: cruzamentos NOVOS da pele (pares de triangulos sem vertice comum que se cruzam e nao se cruzavam no repouso).
Uso: blender -b rig_v9/CR_LoboArtico_Rig.blend -P auditar_rig_v9.py -- <saida_dir> [LOW,LOD1,LOD2]"""
import bpy, bmesh, sys, os, json, math
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
NIVEIS = a[1].split(",") if len(a) > 1 else ["LOW", "LOD1", "LOD2"]
SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); AC = json.load(open(os.path.join(SRC, "acao_v10.json" if os.path.exists(os.path.join(SRC, "acao_v10.json")) else "acao_v9.json")))
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; ARM.animation_data.action = bpy.data.actions["Teste_Piloto"]
CP, CN = V(PIV["costura"]["ponto"]), V(PIV["costura"]["normal"]); PV = V(PIV["mandibula"]["pivo_sugerido"]); IRIS_C, IRIS_R = V((0.96, 0.54)), 0.036
KS = {k: V(PIV["canto_v8"][k]["canto_K"]) for k in ("E", "D")}
PICOS = {"repouso": 0, "boca_meio": 25, "boca_max": 43, "piscar_meio": 64, "piscar_total": 72, "cabeca_E": 99, "cabeca_D": 119, "cabeca_cima": 149,
         "cabeca_baixo": 169, "coluna_E": 201, "coluna_D": 221, "inclina_E": 251, "inclina_D": 269, "peso_E": 295, "peso_D": 313, "peso_frente": 339,
         "peso_tras": 355}
for i, (nm, t0) in enumerate((("diant_E", 366), ("diant_D", 426), ("tras_E", 486), ("tras_D", 546))):
    PICOS.update({nm + "_frente": t0 + 12, nm + "_tras": t0 + 26, nm + "_passo": t0 + 44, nm + "_dedos-": t0 + 42, nm + "_dedos+": t0 + 45})
PICOS.update({"cauda_E": 621, "cauda_D": 639, "cauda_cima": 665, "cauda_baixo": 678, "orelhas_tras": 699, "orelhas_frente": 712, "orelha_E_giro": 732,
              "orelha_D_giro": 750, "combinacao": 782})
if AC["quadros"][1] > 806:                                               # acao v10: trecho H (cauda + pata traseira E)
    PICOS.update({"comb_cauda_E_passo_E": 825, "comb_cauda_cima_quadril_E_tras": 845, "comb_cauda_D_quadril_E_frente": 871})
CONJ = {"LOW": ("LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem"), "LOD1": ("LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem"), "LOD2": ("LOD2_Cabeca", "LOD2_Corpo", None)}
MARCA, CRIST = bpy.data.objects["LOW_Marca"], bpy.data.objects["LOW_Cristais"]
OSSOS = {b.name for b in ARM.data.bones}
def posado(o):
    dg = bpy.context.evaluated_depsgraph_get(); e = o.evaluated_get(dg); m = e.to_mesh(); P = [v.co.copy() for v in m.vertices]; e.to_mesh_clear(); return P
def pesos(o):
    nm = {g.index: g.name for g in o.vertex_groups}
    return [{nm[e.group]: e.weight for e in v.groups if nm[e.group] in OSSOS and e.weight > 0} for v in o.data.vertices]
def dominante(w): return max(w.items(), key=lambda kv: kv[1])[0] if w else "Raiz"
def mat_osso(n):
    pb = ARM.pose.bones[n]; return pb.matrix @ pb.bone.matrix_local.inverted()
def seg(n):
    pb = ARM.pose.bones[n]; return pb.head.copy(), pb.tail.copy()
def dseg(p, a_, b_):
    ab = b_ - a_; t = max(0.0, min(1.0, (p - a_).dot(ab) / max(ab.length_squared, 1e-9))); return (p - (a_ + ab * t)).length
def ilhas(me):
    pai = list(range(len(me.vertices)))
    def r(i):
        while pai[i] != i: pai[i] = pai[pai[i]]; i = pai[i]
        return i
    for e in me.edges:
        x, y = r(e.vertices[0]), r(e.vertices[1])
        if x != y: pai[x] = y
    g = {}
    for i in range(len(me.vertices)): g.setdefault(r(i), []).append(i)
    return list(g.values())
def info_pele(o, cabeca):
    bm = bmesh.new(); bm.from_mesh(o.data); uv = bm.loops.layers.uv.active; bm.faces.ensure_lookup_table()
    pele_f = [f.index for f in bm.faces if not cabeca or f.loops[0][uv].uv.x < 0.90]; ps = set(pele_f)
    arestas = [(e.verts[0].index, e.verts[1].index) for e in bm.edges if e.link_faces and all(f.index in ps for f in e.link_faces) and e.calc_length() > 0.01]
    canto = [(e.verts[0].index, e.verts[1].index) for e in bm.edges if e.link_faces and min((e.verts[0].co - k).length for k in KS.values()) < 0.35
             and any(f.loops[0][uv].uv.x < 0.90 or 0.955 < f.loops[0][uv].uv.x < 0.97 for f in e.link_faces)] if cabeca else []
    iris = [f.index for f in bm.faces if all((l[uv].uv - IRIS_C).length < IRIS_R * 1.05 for l in f.loops)] if cabeca else []
    globo = {f.index for f in bm.faces if cabeca and f.loops[0][uv].uv.x > 0.90 and (sum((l[uv].uv for l in f.loops), V((0, 0))) / len(f.loops) - IRIS_C).length < 0.10}
    faces = [[v.index for v in f.verts] for f in bm.faces]; areas = [f.calc_area() for f in bm.faces]; nrm = [f.normal.copy() for f in bm.faces]
    bm.free(); return dict(pele_f=pele_f, arestas=arestas, canto=canto, iris=iris, globo=globo, faces=faces, areas=areas, nrm=nrm)
def normal_face(P, f):
    if len(f) == 3: return (P[f[1]] - P[f[0]]).cross(P[f[2]] - P[f[0]]).normalized()
    return (P[f[2]] - P[f[0]]).cross(P[f[3]] - P[f[1]]).normalized()
def v8_boca(o, gb):
    """teste geometrico da v8 (giro por peso nos grupos v8_), para comparar com o rig"""
    gi = {g.name: g.index for g in o.vertex_groups}.get("v8_Mandibula"); P = [v.co.copy() for v in o.data.vertices]
    for i, v in enumerate(o.data.vertices):
        w = next((e.weight for e in v.groups if e.group == gi), 0.0)
        if w > 0: P[i] = PV + Matrix.Rotation(math.radians(gb) * w, 3, V((1, 0, 0))) @ (P[i] - PV)
    return P
def canto_stats(P0, P1, ares):
    out = {}
    for lado, k in KS.items():
        rs = []
        for i, j in ares:
            if (P0[i] - k).length > 0.35 or (P0[i].x > 0) != (lado == "E"): continue
            l0, l1 = (P0[i] - P0[j]).length, (P1[i] - P1[j]).length
            if l1 > 0.06: rs.append(l1 / max(l0, 1e-6))
        rs.sort(); out[lado] = {"visiveis_>2x": sum(r > 2 for r in rs), "visiveis_>3x": sum(r > 3 for r in rs), "p95": round(rs[int(len(rs) * 0.95)] if rs else 0, 2)}
    return out
sc.frame_set(0); bpy.context.view_layer.update()
R = {"acao": AC["trechos"], "picos": PICOS, "niveis": {}}
for L in NIVEIS:
    nh, nc, nf = CONJ[L]; H, C = bpy.data.objects[nh], bpy.data.objects[nc]
    obs = [H, C] + ([bpy.data.objects[nf]] if nf else []) + ([MARCA] if L != "LOD2" else []) + [CRIST]
    REP = {o.name: [v.co.copy() for v in o.data.vertices] for o in obs}; WS = {o.name: pesos(o) for o in (H, C)}
    IH, IC = info_pele(H, True), info_pele(C, False)
    kd = KDTree(len(C.data.vertices))
    for v in C.data.vertices: kd.insert(v.co, v.index)
    kd.balance(); pares = [(v.index, kd.find(v.co)[1]) for v in H.data.vertices if abs((v.co - CP).dot(CN)) < 0.2 and kd.find(v.co)[2] < 1e-4]
    patas = {}
    for k, xy in zip(("diant_E", "diant_D", "tras_E", "tras_D"), PIV["pose_neutra"]["patas_xy_depois"]):
        patas[k] = [v.index for v in C.data.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8]
    def base_pele(P_h, P_c):
        pos = P_h + P_c; n = len(P_h); fac = [IH["faces"][i] for i in IH["pele_f"]] + [[n + j for j in f] for f in IC["faces"]]
        return BVHTree.FromPolygons(pos, fac)
    cris = ilhas(CRIST.data); cr_ares = [(e.vertices[0], e.vertices[1]) for e in CRIST.data.edges]
    fur = bpy.data.objects[nf] if nf else None; fur_raiz = []
    bv0 = base_pele(REP[nh], REP[nc])
    if fur:
        for il in ilhas(fur.data): fur_raiz.append(min(il, key=lambda i: bv0.find_nearest(REP[fur.name][i])[3]))
    cr_raiz = [min(il, key=lambda i: bv0.find_nearest(REP[CRIST.name][i])[3]) for il in cris]
    d0_marca = [bv0.find_nearest(p)[3] for p in REP[MARCA.name]] if L != "LOD2" else []
    d0_cr = [bv0.find_nearest(REP[CRIST.name][i])[3] for i in cr_raiz]
    d0_fur = [bv0.find_nearest(REP[fur.name][i])[3] for i in fur_raiz] if fur else []
    rest_dist = {}
    for o, Wo in ((H, WS[nh]), (C, WS[nc])):
        rest_dist[o.name] = [dseg(p, ARM.data.bones[dominante(w)].head_local, ARM.data.bones[dominante(w)].tail_local) for p, w in zip(REP[o.name], Wo)]
    def cruz_set(PH, PC):
        pos = PH + PC; n = len(PH); fac = [IH["faces"][i] for i in IH["pele_f"]] + [[n + j for j in f] for f in IC["faces"]]
        t = BVHTree.FromPolygons(pos, fac); s = set()
        for i, j in t.overlap(t):
            if i < j and not set(fac[i]) & set(fac[j]): s.add((i, j))
        return s, fac, pos
    if L == "LOW": sc.frame_set(0); cruz0, FAC_J, _ = cruz_set(posado(H), posado(C))   # repouso avaliado (mesma aritmetica)
    RL = R["niveis"][L] = {"pares_costura": len(pares), "quadros": {}}
    pe_min0 = {k: min(REP[nc][i].z for i in ids) for k, ids in patas.items()}; pe_c0 = {k: sum((REP[nc][i] for i in ids), V()) / len(ids) for k, ids in patas.items()}
    for nome, q in PICOS.items():
        sc.frame_set(q); bpy.context.view_layer.update()
        PP = {o.name: posado(o) for o in obs}; r = RL["quadros"][nome] = {"quadro": q}
        if q == 0: r["desvio_repouso_max"] = round(max((p - p0).length for o in obs for p, p0 in zip(PP[o.name], REP[o.name])), 6)
        for o, I, Wo in ((H, IH, WS[nh]), (C, IC, WS[nc])):
            P0, P1 = REP[o.name], PP[o.name]; rr = [(P1[i] - P1[j]).length / (P0[i] - P0[j]).length for i, j in I["arestas"]]
            vir, area_vir = 0, 0.0
            for fi in I["pele_f"]:
                f = I["faces"][fi]
                if I["areas"][fi] < 2e-4: continue
                w = {}
                for vi in f:
                    for k, x in Wo[vi].items(): w[k] = w.get(k, 0) + x
                Rm = mat_osso(dominante(w)).to_3x3(); n1 = normal_face(P1, f)
                if n1.dot(Rm @ I["nrm"][fi]) < 0: vir += 1; area_vir += I["areas"][fi]
            col = 0; col_onde = {}
            for i, (p, w) in enumerate(zip(P1, Wo)):
                d0 = rest_dist[o.name][i]
                if d0 < 0.15: continue
                dn = dominante(w); h_, t_ = seg(dn)
                if dseg(p, h_, t_) < 0.6 * d0: col += 1; col_onde[dn] = col_onde.get(dn, 0) + 1
            r[o.name] = {"esticadas_>1.6x": sum(x > 1.6 for x in rr), "esticadas_>2x": sum(x > 2 for x in rr), "max_razao": round(max(rr), 2),
                         "comprimidas_<0.5x": sum(x < 0.5 for x in rr), "faces_viradas": vir, "area_viradas": round(area_vir, 4),
                         "colapso_vertices": col, "colapso_por_osso": dict(sorted(col_onde.items(), key=lambda kv: -kv[1])[:4])}
        r["costura_fresta_max"] = round(max((PP[nh][i] - PP[nc][j]).length for i, j in pares), 6)
        r["patas_zmin_delta"] = {k: round(min(PP[nc][i].z for i in ids) - pe_min0[k], 4) for k, ids in patas.items()}
        r["patas_deslize"] = {k: round(((sum((PP[nc][i] for i in ids), V()) / len(ids)) - pe_c0[k]).to_2d().length, 4) for k, ids in patas.items()}
        bv = base_pele(PP[nh], PP[nc])
        P = PP[CRIST.name]; r["cristais_variacao_aresta_max"] = round(max(abs((P[i] - P[j]).length / max((REP[CRIST.name][i] - REP[CRIST.name][j]).length, 1e-6) - 1) for i, j in cr_ares), 4)
        r["cristais_base_dist_delta_max"] = round(max(abs(bv.find_nearest(P[i])[3] - d0) for i, d0 in zip(cr_raiz, d0_cr)), 4)
        if L != "LOD2": r["marca_dist_pele_max"] = round(max(bv.find_nearest(p)[3] for p in PP[MARCA.name]), 4); r["marca_dist_pele_max_repouso"] = round(max(d0_marca), 4)
        if fur:
            ds = sorted(abs(bv.find_nearest(PP[fur.name][i])[3] - d0) for i, d0 in zip(fur_raiz, d0_fur))
            r["pelagem_raiz_delta_p99"] = round(ds[int(len(ds) * 0.99)], 4); r["pelagem_raiz_delta_max"] = round(ds[-1], 4)
        if nome == "boca_max":
            P8 = v8_boca(H, 32.0); dv = [(p - p8).length for p, p8 in zip(PP[nh], P8)]
            r["boca_rig_x_v8"] = {"desvio_max": round(max(dv), 4), "desvio_medio_vertices_que_mexem": round(sum(d for d in dv if d > 1e-5) / max(1, sum(d > 1e-5 for d in dv)), 4)}
            r["cantos_rig"] = canto_stats(REP[nh], PP[nh], IH["canto"]); r["cantos_teste_v8"] = canto_stats(REP[nh], P8, IH["canto"])
        if nome in ("piscar_total", "piscar_meio"):
            P = PP[nh]; bvh = BVHTree.FromPolygons(P, IH["faces"]); desc = tot = 0; cs = [V(o_["centro_globo"]) for o_ in PIV["olhos"].values()]
            for fi in IH["iris"]:
                f = IH["faces"][fi]; qv = sum((P[i] for i in f), V()) / len(f); S = min(cs, key=lambda s: (s - qv).length); d = (qv - S).normalized(); tot += 1
                o_ = qv + d * 0.004; hit = bvh.ray_cast(o_, d, 0.6)
                while hit[0] is not None and hit[2] in IH["globo"]: o_ = hit[0] + d * 0.002; hit = bvh.ray_cast(o_, d, 0.6)
                desc += hit[0] is None
            r["iris"] = {"amostras": tot, "descobertas": desc}
        if L == "LOW" and q != 0:
            s, fac, pos = cruz_set(PP[nh], PP[nc]); novos = s - cruz0; onde = {}
            nH = len(PP[nh])
            for i, j in novos:
                vi = fac[i][0]; w = WS[nh][vi] if vi < nH else WS[nc][vi - nH]; dn = dominante(w); onde[dn] = onde.get(dn, 0) + 1
            r["cruzamentos_novos"] = len(novos); r["cruzamentos_novos_por_osso"] = dict(sorted(onde.items(), key=lambda kv: -kv[1])[:5])
        print("AUD", L, nome, json.dumps({k: v for k, v in r.items() if k not in (nh, nc)}), "|", json.dumps({o: r[o] for o in (nh, nc)}), flush=True)
    sc.frame_set(0)
json.dump(R, open(os.path.join(OUT, "auditoria_rig.json"), "w"), indent=1); print("AUD_RIG_OK", flush=True)
