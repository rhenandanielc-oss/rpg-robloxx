"""Auditoria SO LEITURA do rosto por LOD (LOW/LOD1/LOD2) no .blend (com grupos; nao vale para o GLB, que nao leva grupos).
Por LOD: tris; fresta da costura cabeca-corpo (distancia de cada vertice da borda de um lado a polilinha do outro; so
bordas junto ao anel real da costura do LOD0, nao outras bordas do corpo que cruzem o plano) e pesos
na costura; vertices por grupo (>0,01 / >0,5); arestas abertas do corte da boca; nao-manifold / enrolamento invertido;
pose geometrica (os pesos girados como um rig faria, igual a teste_rosto_v5.py):
- palpebras fechadas: fracao de amostras da iris (faces com UV da iris) que ficam DESCOBERTAS (raio para fora do globo
  sem bater na pele) -> 'iris vazando';
- boca no maximo (32 graus): maior esticamento de aresta so de PELE (as duas faces de pele; o saco bucal estica por projeto);
- Mandibula na PELE do focinho de cima (acima da linha da boca + 0,06, a frente do canto; sem dentes): tem de ser ~0.
Uso: blender -b <arquivo.blend> -P auditar_lod_v7.py -- <saida_dir>"""
import bpy, bmesh, sys, os, json, math
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_point_line
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
CP, CN = V(PIV["costura"]["ponto"]), V(PIV["costura"]["normal"]); BA, BB = PIV["mandibula"]["linha_boca"]; CANTO = PIV["mandibula"]["canto_y"]
PV = V(PIV["mandibula"]["pivo_sugerido"]); IRIS_C, IRIS_R = V((0.96, 0.54)), 0.036
def tris(me): return sum(len(p.vertices) - 2 for p in me.polygons)
def na_costura(p): return abs((p - CP).dot(CN)) < 0.03
from mathutils.kdtree import KDTree
_b = bmesh.new(); _b.from_mesh(bpy.data.objects["LOW_Cabeca"].data)               # anel real da costura (LOD0)
_cs = [v.co.copy() for v in _b.verts if v.is_boundary and na_costura(v.co)]; _b.free()
KD_COST = KDTree(len(_cs))
for _i, _p in enumerate(_cs): KD_COST.insert(_p, _i)
KD_COST.balance()
def na_costura_real(p): return na_costura(p) and KD_COST.find(p)[2] < 0.15      # perto do plano E do anel do pescoco
def borda_costura(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    es = [(e.verts[0].co.copy(), e.verts[1].co.copy(), e.verts[0].index, e.verts[1].index) for e in bm.edges if e.is_boundary and na_costura_real((e.verts[0].co + e.verts[1].co) / 2)]
    bm.free(); return es
def dist_poli(p, es):
    best = 9.0
    for a, b, _, _ in es:
        q, t = intersect_point_line(p, a, b); t = max(0.0, min(1.0, t)); best = min(best, (p - (a + (b - a) * t)).length)
    return best
def pose(o, fo, gb):
    me = o.data; gi = {g.name: g.index for g in o.vertex_groups}; P = [v.co.copy() for v in me.vertices]
    W = [{e.group: e.weight for e in v.groups} for v in me.vertices]
    for lado, ol in PIV["olhos"].items():
        S, ax = V(ol["centro_globo"]), V(ol["eixo"])
        for nome, ang in (("Palpebra_Sup_" + lado, ol["fechar_sup_graus"]), ("Palpebra_Inf_" + lado, ol["fechar_inf_graus"])):
            g = gi.get(nome)
            for i in range(len(P)):
                w = W[i].get(g, 0.0)
                if w > 0: P[i] = S + Matrix.Rotation(math.radians(ang * w * fo), 3, ax) @ (P[i] - S)
    g = gi.get("Mandibula")
    for i in range(len(P)):
        w = W[i].get(g, 0.0)
        if w > 0: P[i] = PV + Matrix.Rotation(math.radians(gb) * w, 3, V((1, 0, 0))) @ (P[i] - PV)
    return P
R = {}
for L in ("LOW", "LOD1", "LOD2"):
    h, c = bpy.data.objects[L + "_Cabeca"], bpy.data.objects[L + "_Corpo"]; r = R[L] = {"tris_cabeca": tris(h.data), "tris_corpo": tris(c.data),
        "materiais": [m.name for m in h.data.materials] + [m.name for m in c.data.materials]}
    eh, ec = borda_costura(h), borda_costura(c)
    vh = {i: a for a, b, i, j in eh} | {j: b for a, b, i, j in eh}; vc = {i: a for a, b, i, j in ec} | {j: b for a, b, i, j in ec}
    dh = [dist_poli(p, ec) for p in vh.values()]; dc = [dist_poli(p, eh) for p in vc.values()]
    gnome = {g.index: g.name for g in h.vertex_groups}
    pesos_cost = max((e.weight for i in vh for e in h.data.vertices[i].groups if gnome[e.group] != "Protecao_LOD"), default=0.0)
    r["costura"] = {"arestas_cabeca": len(eh), "arestas_corpo": len(ec), "fresta_max": round(max(dh + dc), 5),
                    "vertices_com_fresta_>0.001": sum(d > 0.001 for d in dh + dc), "peso_max_rosto_na_costura": round(pesos_cost, 4)}
    cont = {}
    for v in h.data.vertices:
        for e in v.groups:
            k = cont.setdefault(h.vertex_groups[e.group].name, [0, 0]); k[0] += e.weight > 0.01; k[1] += e.weight > 0.5
    r["grupos_>0.01_>0.5"] = cont
    bm = bmesh.new(); bm.from_mesh(h.data); uv = bm.loops.layers.uv.active
    r["corte_boca_arestas_abertas"] = sum(1 for e in bm.edges if e.is_boundary and not na_costura((e.verts[0].co + e.verts[1].co) / 2)
                                          and (e.verts[0].co.y < CANTO + 0.05) and abs(e.verts[0].co.z - (BA + BB * e.verts[0].co.y)) < 0.2)
    r["nao_manifold"] = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    def inv(e):
        f1, f2 = e.link_faces; a, b = e.verts
        def ordem(f):
            vs = list(f.verts); i = vs.index(a); return vs[(i + 1) % len(vs)] == b
        return ordem(f1) == ordem(f2)
    r["enrolamento_invertido"] = sum(1 for e in bm.edges if len(e.link_faces) == 2 and inv(e))
    pele_f = [f.index for f in bm.faces if f.loops[0][uv].uv.x < 0.90]
    iris_f = [f.index for f in bm.faces if (f.loops[0][uv].uv - IRIS_C).length < IRIS_R and all((l[uv].uv - IRIS_C).length < IRIS_R * 1.05 for l in f.loops)]
    globo_f = set(f.index for f in bm.faces if (sum((l[uv].uv for l in f.loops), V((0, 0))) / len(f.loops) - IRIS_C).length < 0.10 and f.loops[0][uv].uv.x > 0.90)
    arestas_pele = [(e.verts[0].index, e.verts[1].index) for e in bm.edges if e.link_faces and all(f.loops[0][uv].uv.x < 0.90 for f in e.link_faces)
                    and e.verts[0].co.y < CANTO + 0.3 and abs(e.verts[0].co.z - (BA + BB * e.verts[0].co.y)) < 0.45]
    v_pele = {v.index for f in bm.faces if f.loops[0][uv].uv.x < 0.90 for v in f.verts}
    faces = [[v.index for v in f.verts] for f in bm.faces]; bm.free()
    # palpebras fechadas: iris coberta?
    P = pose(h, 1.0, 0.0); bvh = BVHTree.FromPolygons(P, faces); descob = tot = 0
    centros = {k: V(o["centro_globo"]) for k, o in PIV["olhos"].items()}
    for fi in iris_f:
        q = sum((P[i] for i in faces[fi]), V()) / len(faces[fi]); S = min(centros.values(), key=lambda s: (s - q).length)
        d = (q - S).normalized(); tot += 1; o_ = q + d * 0.004; hit = bvh.ray_cast(o_, d, 0.6)
        while hit[0] is not None and hit[2] in globo_f:                 # ignora o proprio globo
            o_ = hit[0] + d * 0.002; hit = bvh.ray_cast(o_, d, 0.6)
        if hit[0] is None: descob += 1
    r["palpebras_fechadas"] = {"amostras_iris": tot, "descobertas": descob}
    P0 = [v.co.copy() for v in h.data.vertices]; P1 = pose(h, 0.0, 32.0)
    est = sorted(((P1[a] - P1[b]).length / max((P0[a] - P0[b]).length, 1e-6), (P1[a] - P1[b]).length, (P0[a] + P0[b]) / 2) for a, b in arestas_pele)
    vis = [x for x in est if x[1] > 0.06]                               # so arestas que ficam visiveis (> 0,06 stud abertas)
    r["boca_max_esticamento_pele"] = {"max_visivel": round(max((s for s, _, _ in vis), default=0), 3),
                                      "onde_max_visivel": [round(x, 3) for x in max(vis, key=lambda x: x[0])[2]] if vis else None,
                                      "visiveis_>2x": sum(1 for s, _, _ in vis if s > 2.0), "visiveis_>3x": sum(1 for s, _, _ in vis if s > 3.0),
                                      "maior_aresta_aberta": round(max(l for _, l, _ in est), 3)}
    gi = {g.name: g.index for g in h.vertex_groups}.get("Mandibula")
    cima = [e.weight for v in h.data.vertices if v.index in v_pele and v.co.y < CANTO - 0.1 and v.co.z > BA + BB * v.co.y + 0.06 for e in v.groups if e.group == gi]
    r["mandibula_no_focinho_de_cima"] = {"vertices_com_peso": sum(w > 0.01 for w in cima), "max": round(max(cima, default=0.0), 4)}
    print("AUD", L, json.dumps(r), flush=True)
json.dump(R, open(os.path.join(OUT, "auditoria_lod.json"), "w"), indent=1); print("AUD_OK", flush=True)
