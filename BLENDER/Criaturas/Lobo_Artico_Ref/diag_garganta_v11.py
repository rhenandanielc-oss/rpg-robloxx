"""Diagnostico SO LEITURA da garganta/juba (base do pescoco e peito) COM O RIG REAL, por LOD, nos picos da cabeca.
Regiao: pele da cabeca e do corpo com y < -2,6 e z < 5,6 (garganta, babador da juba, peito).
Para cada face da regiao classifica: PELE (casca principal) x LAMINA (pelo esculpido do Meshy: um raio para dentro, pela
normal invertida, bate na propria malha a menos de 0,06 -> casca fina/aba solta sobre outra superficie).
Por pico: faces viradas (numero/area, pele x lamina), cruzamentos novos (pele-pele, lamina-*, cabeca-corpo), estiramento e
os ossos dominantes / mistura de pesos das faces com problema (histograma), e pontos de 'puxada pelo membro' (vertice da
garganta com peso de Umero/Escapula > 0,1 a frente do ombro).
Uso: blender -b <rig.blend> -P diag_garganta_v11.py -- <saida_json> [LOW,LOD1,LOD2]"""
import bpy, sys, os, json
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIV = a[1].split(",") if len(a) > 1 else ["LOW", "LOD1", "LOD2"]
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; OSS = {b.name for b in ARM.data.bones}
PICOS = {"repouso": 0, "cabeca_E": 99, "cabeca_D": 119, "cabeca_cima": 149, "cabeca_baixo": 169, "combinacao": 782,
         "inclina_E": 251, "peso_E": 295, "diant_E_frente": 378, "diant_D_frente": 438, "diant_E_passo": 410}   # + axila (regressao)
def reg(p): return p.y < -2.6 and p.z < 5.6
def posado(o):
    dg = bpy.context.evaluated_depsgraph_get(); e = o.evaluated_get(dg); m = e.to_mesh(); P = [v.co.copy() for v in m.vertices]; e.to_mesh_clear(); return P
R = {"picos": PICOS, "niveis": {}}
for L in NIV:
    obs = [bpy.data.objects[L + "_Cabeca"], bpy.data.objects[L + "_Corpo"]]; sc.frame_set(0)
    pos, fac, dono, W, nomes = [], [], [], [], []
    for o in obs:
        gn = {g.index: g.name for g in o.vertex_groups}; b = len(pos); P0 = [v.co.copy() for v in o.data.vertices]; pos += P0
        W += [{gn[e.group]: e.weight for e in v.groups if gn[e.group] in OSS and e.weight > 0} for v in o.data.vertices]
        uvl = o.data.uv_layers.active.data
        for p in o.data.polygons:
            if o.name.endswith("Cabeca") and uvl[p.loop_start].uv.x >= 0.9: continue   # globos/dentes/interior da boca fora
            fac.append([b + i for i in p.vertices]); dono.append(o.name)
    P0 = list(pos); bv0 = BVHTree.FromPolygons(P0, fac)
    rf = [i for i, f in enumerate(fac) if reg(sum((P0[v] for v in f), V()) / len(f))]
    nrm0 = {}; lam = set()
    for i in rf:
        f = fac[i]; c = sum((P0[v] for v in f), V()) / len(f); n = (P0[f[1]] - P0[f[0]]).cross(P0[f[2]] - P0[f[0]]).normalized(); nrm0[i] = n
        hit = bv0.ray_cast(c - n * 0.003, -n, 0.06)
        if hit[0] is not None and hit[2] != i: lam.add(i)
    area0 = {i: sum(((P0[fac[i][k]] - P0[fac[i][0]]).cross(P0[fac[i][k + 1]] - P0[fac[i][0]])).length / 2 for k in range(1, len(fac[i]) - 1)) for i in rf}
    def cruz(P):
        bv = BVHTree.FromPolygons(P, [fac[i] for i in rf]); s = set()
        for x, y in bv.overlap(bv):
            i, j = rf[x], rf[y]
            if i < j and not set(fac[i]) & set(fac[j]): s.add((i, j))
        return s
    c0 = cruz(P0)
    puxa = sum(1 for i, w in enumerate(W) if reg(P0[i]) and P0[i].y < -3.6 and sum(x for k, x in w.items() if k.startswith(("Umero", "Escapula"))) > 0.1)
    RL = R["niveis"][L] = {"faces_regiao": len(rf), "faces_lamina": len(lam), "vertices_garganta_com_peso_de_membro_>0.1": puxa, "picos": {}}
    for nome, q in PICOS.items():
        sc.frame_set(q); P = sum((posado(o) for o in obs), [])
        vir = {"pele": [0, 0.0], "lamina": [0, 0.0]}; osso = {}
        for i in rf:
            f = fac[i]; w = {}
            for v in f:
                for k, x in W[v].items(): w[k] = w.get(k, 0) + x / len(f)
            dn = max(w, key=w.get); pb = ARM.pose.bones[dn]; Rm = (pb.matrix @ pb.bone.matrix_local.inverted()).to_3x3()
            n1 = (P[f[1]] - P[f[0]]).cross(P[f[2]] - P[f[0]]).normalized()
            if n1.dot(Rm @ nrm0[i]) < 0 and area0[i] > 2e-4:
                k = "lamina" if i in lam else "pele"; vir[k][0] += 1; vir[k][1] += area0[i]
                chave = "+".join(sorted(k_ for k_, x in w.items() if x > 0.15)); osso[chave] = osso.get(chave, 0) + 1
        cz = cruz(P) - c0 if q else set(); tipo = {}
        for i, j in cz:
            t = ("lamina" if (i in lam or j in lam) else "pele") + ("_cab-corpo" if dono[i] != dono[j] else "")
            tipo[t] = tipo.get(t, 0) + 1
        boca = {v for v, w in enumerate(W) if w.get("Mandibula", 0) > 0}  # labios/boca ficam fora do estiramento (testados a parte)
        est = [((P[a_] - P[b_]).length / max((P0[a_] - P0[b_]).length, 1e-6), (P[a_] - P[b_]).length - (P0[a_] - P0[b_]).length)
               for i in rf for a_, b_ in zip(fac[i], fac[i][1:] + fac[i][:1]) if (P0[a_] - P0[b_]).length > 0.01 and a_ not in boca and b_ not in boca]
        RL["picos"][nome] = {"quadro": q, "viradas": {k: [n, round(ar, 4)] for k, (n, ar) in vir.items()}, "viradas_por_mistura_de_ossos": dict(sorted(osso.items(), key=lambda kv: -kv[1])[:6]),
                             "cruzamentos_novos": len(cz), "cruzamentos_por_tipo": tipo, "esticadas_>2x": sum(1 for r, _ in est if r > 2), "max_razao": round(max(r for r, _ in est), 2),
                             "max_aumento_abs": round(max(d for _, d in est), 4), "comprimidas_<0.5x": sum(1 for r, _ in est if r < 0.5)}
        print("DIAGG", L, nome, json.dumps(RL["picos"][nome]), flush=True)
    print("DIAGG", L, "regiao", len(rf), "laminas", len(lam), "puxada_membro", puxa, flush=True)
    sc.frame_set(0)
json.dump(R, open(OUT, "w"), indent=1); print("DIAG_GARGANTA_OK", flush=True)
