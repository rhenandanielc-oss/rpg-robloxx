"""Auditoria SO LEITURA, LOCAL, da regiao cauda x patas traseiras COM O RIG REAL (acao Teste_Piloto da v10: a da v9 +
trecho H), por LOD e por lado: E (a uniao corrigida) e D (controle). Regiao: corpo com y > 1,6, z < 4,3 e x > -0,1 (E) /
x < 0,1 (D). Por pico:
- pele: arestas (repouso > 0,01) esticadas > 1,6x / > 2x, maior razao e MAIOR AUMENTO ABSOLUTO de comprimento (stud);
  comprimidas < 0,5x;
- faces viradas (normal posada contra a de repouso levada pelo osso dominante; area > 2e-4): numero e AREA (stud^2);
- colapso: vertices que chegam a < 60% da distancia de repouso ao osso dominante (so os que estavam a > 0,15);
- cruzamentos NOVOS pele x pele (triangulos sem vertice comum que se cruzam e nao se cruzavam no repouso), na regiao;
  quantos envolvem face de TAMPA (contato interno) e a profundidade maxima (centro de uma face atras do plano da outra);
- PELO x pele (separado do erro da pele): triangulos de cartao (raiz na regiao) que passam a cruzar a pele (so LOD0/LOD1).
Uso: blender -b <rig.blend> -P auditar_cauda_v10.py -- <saida_json> [LOW,LOD1,LOD2]"""
import bpy, sys, os, json, math
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIV = a[1].split(",") if len(a) > 1 else ["LOW", "LOD1", "LOD2"]
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; OSS = {b.name for b in ARM.data.bones}
PICOS = {"repouso": 0, "inclina_E": 251, "peso_E": 295, "peso_D": 313, "tras_E_frente": 498, "tras_E_tras": 512, "tras_E_passo": 530, "tras_D_frente": 558,
         "tras_D_tras": 572, "tras_D_passo": 590, "cauda_E": 621, "cauda_D": 639, "cauda_cima": 665, "cauda_baixo": 678,
         "comb_cauda_E_passo_E": 825, "comb_cauda_cima_quadril_E_tras": 845, "comb_cauda_D_quadril_E_frente": 871}
def lado_ok(p, l): return p.y > 1.6 and p.z < 4.3 and (p.x > -0.1 if l == "E" else p.x < 0.1)
def posado(o):
    dg = bpy.context.evaluated_depsgraph_get(); e = o.evaluated_get(dg); m = e.to_mesh(); P = [v.co.copy() for v in m.vertices]; e.to_mesh_clear(); return P
def dseg(p, h, t):
    ab = t - h; u = max(0.0, min(1.0, (p - h).dot(ab) / ab.length_squared)); return (p - (h + ab * u)).length
def tri(P, f):
    return [(P[f[0]], P[f[i]], P[f[i + 1]]) for i in range(1, len(f) - 1)]
R = {"picos": PICOS, "niveis": {}}
for L in NIV:
    C = bpy.data.objects[L + "_Corpo"]; me = C.data; gn = {g.index: g.name for g in C.vertex_groups}
    W = [{gn[e.group]: e.weight for e in v.groups if gn[e.group] in OSS and e.weight > 0} for v in me.vertices]
    dom = [max(w.items(), key=lambda kv: kv[1])[0] if w else "Raiz" for w in W]
    F = [list(p.vertices) for p in me.polygons]; A = [p.area for p in me.polygons]; N = [p.normal.copy() for p in me.polygons]
    FUR = bpy.data.objects.get(L + "_Pelagem"); la_ = me.attributes.get("lado_tampa")
    TAMPA = [bool(la_ and la_.data[i].value) for i in range(len(F))]; LADO_V = True
    sc.frame_set(0); P0 = posado(C); PF0 = posado(FUR) if FUR else None
    reg = {l: {i for i, p in enumerate(P0) if lado_ok(p, l)} for l in "ED"}
    ares = {l: [(e.vertices[0], e.vertices[1]) for e in me.edges if e.vertices[0] in reg[l] and e.vertices[1] in reg[l] and (P0[e.vertices[0]] - P0[e.vertices[1]]).length > 0.01] for l in "ED"}
    facs = {l: [i for i, f in enumerate(F) if all(v in reg[l] for v in f)] for l in "ED"}
    d0 = [dseg(p, ARM.data.bones[d].head_local, ARM.data.bones[d].tail_local) for p, d in zip(P0, dom)]
    def cruz(P, fl):
        tris = [(fi, t) for fi in fl for t in tri(P, F[fi])]; pos = []; fac = []; dono = []
        for fi, t in tris:
            b = len(pos); pos += list(t); fac.append([b, b + 1, b + 2]); dono.append(fi)
        bv = BVHTree.FromPolygons(pos, fac); s = set()
        for i, j in bv.overlap(bv):
            fi, fj = dono[i], dono[j]
            if fi < fj and not set(F[fi]) & set(F[fj]): s.add((fi, fj))
        return s
    def fur_cruz(PF, P, l):
        if not FUR: return None
        fm = FUR.data; ff = [list(p.vertices) for p in fm.polygons if all(lado_ok(PF0[v], l) for v in p.vertices)]
        tf = [t for f in ff for t in tri(PF, f)]; ts = [t for fi in facs[l] for t in tri(P, F[fi])]
        if not tf or not ts: return 0
        bf = BVHTree.FromPolygons([p for t in tf for p in t], [[3 * i, 3 * i + 1, 3 * i + 2] for i in range(len(tf))])
        bs = BVHTree.FromPolygons([p for t in ts for p in t], [[3 * i, 3 * i + 1, 3 * i + 2] for i in range(len(ts))])
        return len({i for i, j in bf.overlap(bs)})
    c0 = {l: cruz(P0, facs[l]) for l in "ED"}; fc0 = {l: fur_cruz(PF0, P0, l) for l in "ED"}
    RL = R["niveis"][L] = {}
    for nome, q in PICOS.items():
        sc.frame_set(q); P = posado(C); PF = posado(FUR) if FUR else None; r = RL[nome] = {"quadro": q}
        for l in "ED":
            rr = [((P[i] - P[j]).length / (P0[i] - P0[j]).length, (P[i] - P[j]).length - (P0[i] - P0[j]).length) for i, j in ares[l]]
            vir, av = 0, 0.0
            for fi in facs[l]:
                if A[fi] < 2e-4: continue
                w = {}
                for vi in F[fi]:
                    for k, x in W[vi].items(): w[k] = w.get(k, 0) + x
                pb = ARM.pose.bones[max(w.items(), key=lambda kv: kv[1])[0]]; Rm = (pb.matrix @ pb.bone.matrix_local.inverted()).to_3x3()
                f = F[fi]; n1 = (P[f[1]] - P[f[0]]).cross(P[f[2]] - P[f[0]]).normalized()
                if n1.dot(Rm @ N[fi]) < 0: vir += 1; av += A[fi]
            col = 0
            for i in reg[l]:
                if d0[i] < 0.15: continue
                pb = ARM.pose.bones[dom[i]]
                if dseg(P[i], pb.head, pb.tail) < 0.6 * d0[i]: col += 1
            cz = cruz(P, facs[l]) - c0[l] if q else set()
            ntam = sum(1 for i, j in cz if TAMPA[i] or TAMPA[j])                 # com face de tampa (zona de contato interna)
            prof = 0.0                                                     # profundidade: vertice de um lado dentro do outro
            if cz and LADO_V:
                for i, j in list(cz)[:400]:
                    for fa, fb in ((i, j), (j, i)):
                        pa = sum((P[v] for v in F[fa]), V()) / len(F[fa]); nb = (P[F[fb][1]] - P[F[fb][0]]).cross(P[F[fb][2]] - P[F[fb][0]]).normalized()
                        prof = max(prof, -min(0.0, (pa - P[F[fb][0]]).dot(nb)))
            fz = (fur_cruz(PF, P, l) - fc0[l]) if (FUR and q) else None
            r[l] = {"esticadas_>1.6x": sum(1 for x, _ in rr if x > 1.6), "esticadas_>2x": sum(1 for x, _ in rr if x > 2), "max_razao": round(max(x for x, _ in rr), 2),
                    "max_aumento_abs": round(max(d for _, d in rr), 4), "comprimidas_<0.5x": sum(1 for x, _ in rr if x < 0.5),
                    "faces_viradas": vir, "area_viradas": round(av, 4), "colapso": col, "cruzamentos_pele_novos": len(cz), "cruzamentos_com_tampa": ntam,
                    "profundidade_cruzamento_max": round(prof, 3), "pelo_x_pele_novos": fz}
        print("AUDC", L, nome, json.dumps(r), flush=True)
    sc.frame_set(0)
json.dump(R, open(OUT, "w"), indent=1); print("AUD_CAUDA_OK", flush=True)
