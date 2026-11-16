"""Diagnostico SO LEITURA da uniao cauda x pata traseira (LOD0/LOD1/LOD2 do corpo), sem cartoes de pelo.
Classifica cada ponto do corte pela distancia GEODESICA (pela pele) a sementes certas da cauda e de cada pata (a distancia
aos eixos dos ossos erra: os ossos da cauda ficam no fundo do volume; s = d_pata - d_cauda so e usada na faixa) e corta
a malha em fatias horizontais: em cada altura encadeia os segmentos do corte em contornos FECHADOS e diz se a cauda e a
pata estao no MESMO contorno (fusao topologica: a pele passa de uma para a outra) ou em contornos separados (so contato).
Mede tambem a menor distancia entre as superficies dos dois lados (contato visual) por altura.
Uso: blender -b <rig.blend> -P diag_cauda_v10.py -- <saida_json> [LOW,LOD1,LOD2]"""
import bpy, sys, os, json, math
from mathutils import Vector as V
from mathutils.kdtree import KDTree
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIV = a[1].split(",") if len(a) > 1 else ["LOW", "LOD1", "LOD2"]
ARM = bpy.data.objects["LoboArtico_Rig"]; B = ARM.data.bones
def dseg(p, h, t):
    ab = t - h; u = max(0.0, min(1.0, (p - h).dot(ab) / ab.length_squared)); return (p - (h + ab * u)).length
CAUDA = [(B[n].head_local, B[n].tail_local) for n in ("Cauda1", "Cauda2", "Cauda3", "Cauda4")]
def PATA(l): return [(B[n + "_" + l].head_local, B[n + "_" + l].tail_local) for n in ("Coxa", "Tibia", "Metatarso", "DedosPe")]
PE, PD = PATA("E"), PATA("D")
def s_de(p):
    dt = min(dseg(p, h, t) for h, t in CAUDA); dl = min(dseg(p, h, t) for h, t in (PE if p.x > 0 else PD)); return dl - dt
def caixa(p): return 2.0 < p.y < 5.2 and p.z < 3.8 and abs(p.x) < 1.9
import heapq
def geodesica(me, P):
    """classe por distancia GEODESICA (pela pele, z < 3,95) a sementes certas: G_E/G_D = d_cauda - d_pata (<0 cauda)"""
    viz = [[] for _ in P]
    for e in me.edges:
        a_, b_ = e.vertices; l = (P[a_] - P[b_]).length; viz[a_].append((b_, l)); viz[b_].append((a_, l))
    ok = [p.y > 2.0 and p.z < 3.95 for p in P]
    def dj(sem):
        d = {i: 0.0 for i, p in enumerate(P) if ok[i] and sem(p)}; h = [(0.0, i) for i in d]; heapq.heapify(h)
        while h:
            dv, i = heapq.heappop(h)
            if dv > d.get(i, 9e9): continue
            for j, l in viz[i]:
                if ok[j] and dv + l < d.get(j, 9e9): d[j] = dv + l; heapq.heappush(h, (dv + l, j))
        return d
    dt = dj(lambda p: p.y > 4.1 or (p.z < 0.95 and abs(p.x) < 0.7 and p.y > 3.2))
    out = {}
    for l, sx in (("E", 1), ("D", -1)):
        dl_ = dj(lambda p: p.x * sx > 1.3 or (p.z < 0.95 and p.x * sx > 0.7 and p.y < 3.0))
        out[l] = [dt.get(i, 9.0) - dl_.get(i, 9.0) for i in range(len(P))]
    return out
R = {}
for L in NIV:
    o = bpy.data.objects[L + "_Corpo"]; me = o.data; P = [v.co.copy() for v in me.vertices]; S = [s_de(p) if caixa(p) else None for p in P]; GG = geodesica(me, P)
    r = R[L] = {"fatias": {}}
    for zz in [round(0.5 + 0.2 * k, 2) for k in range(17)]:
        segs = []                                                       # (ponto_a, ponto_b) do corte por face
        for f in me.polygons:
            vs = list(f.vertices); cr = []
            for i in range(len(vs)):
                p, q = P[vs[i]], P[vs[(i + 1) % len(vs)]]
                if (p.z - zz) * (q.z - zz) < 0:
                    t = (zz - p.z) / (q.z - p.z); cr.append((tuple(sorted((vs[i], vs[(i + 1) % len(vs)]))), p + (q - p) * t, (vs[i], vs[(i + 1) % len(vs)], t)))
            if len(cr) == 2 and caixa(cr[0][1]): segs.append(cr)
        viz = {}                                                        # contornos = componentes pelas arestas cortadas
        for (ea, pa, _), (eb, pb, _) in segs: viz.setdefault(ea, set()).add(eb); viz.setdefault(eb, set()).add(ea)
        pos = {e: p for sg in segs for e, p, _ in sg}; gi_ = {e: x for sg in segs for e, _, x in sg}; vis, laces = set(), []
        for e in viz:
            if e in vis: continue
            pilha, comp = [e], []
            while pilha:
                x = pilha.pop()
                if x in vis: continue
                vis.add(x); comp.append(x); pilha += list(viz[x] - vis)
            laces.append(comp)
        info = []
        for comp in laces:
            pts = [pos[e] for e in comp]; c0 = sum(pts, V()) / len(pts); gl = GG["E" if c0.x > 0 else "D"]
            ss = [-(gl[gi_[e][0]] * (1 - gi_[e][2]) + gl[gi_[e][1]] * gi_[e][2]) for e in comp]   # >0 cauda (geodesica)
            nt, nl = sum(1 for x in ss if x > 0.15), sum(1 for x in ss if x < -0.15)
            c = sum(pts, V()) / len(pts)
            if len(pts) < 6: continue
            info.append({"pontos": len(pts), "centro": [round(c.x, 2), round(c.y, 2)], "cauda": nt, "pata": nl, "lado": "E" if c.x > 0 else "D"})
        fus = [i for i in info if i["cauda"] >= 4 and i["pata"] >= 4]
        tp = [pos[e] for comp in laces for e in comp if s_de(pos[e]) > 0.15 and pos[e].x > -0.2]; lp = [pos[e] for comp in laces for e in comp if s_de(pos[e]) < -0.15]
        dmin = None
        if tp and lp:
            kd = KDTree(len(lp))
            for i, p in enumerate(lp): kd.insert(p, i)
            kd.balance(); dmin = round(min(kd.find(p)[2] for p in tp), 3)
        r["fatias"][zz] = {"contornos": info, "fundido_com": [i["lado"] for i in fus], "dist_min_cauda_pata": dmin}
        print("DIAG", L, zz, "contornos", len(info), "fusao", [i["lado"] for i in fus], "dist", dmin, flush=True)
    vb = [i for i, p in enumerate(P) if S[i] is not None]
    r["vertices_regiao"] = len(vb); r["faixa_ponte_abs_s<0.15"] = sum(1 for i in vb if abs(S[i]) < 0.15)
json.dump(R, open(OUT, "w"), indent=1); print("DIAG_CAUDA_OK", flush=True)
