# QA numerico da regiao do ferrao (mesmo metodo para qualquer versao).
# Uso: blender -b <v.blend> -P 04c_qa_ferrao.py -- <saida.json>
# Estatico: triangulos, ossos, materiais, imagens, dimensoes (idle f0 e repouso), triangulos degenerados,
#   diedros vivos, autointersecao (BVH), estiramento de UV, soma de pesos.
# Ciclos: idle_loop, walk_loop, fly_loop inteiros -> por frame, estiramento maximo de aresta vs repouso,
#   autointersecao e menor razao de area de triangulo (pincamento) na regiao.
import bpy, sys, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
scn = bpy.context.scene
obj = bpy.data.objects["Wyvern"]; arm = bpy.data.objects["Wyvern_Rig"]; me = obj.data
YR = 22.3
me.calc_loop_triangles()
reg = {v.index for v in me.vertices if v.co.y >= YR}
tris = [t for t in me.loop_triangles if all(i in reg for i in t.vertices)]
edges = [e for e in me.edges if e.vertices[0] in reg and e.vertices[1] in reg]
R = {"triangulos": len(me.loop_triangles), "vertices": len(me.vertices), "ossos": len(arm.data.bones),
     "materiais": [m.name for m in me.materials], "imagens_padrao": sorted(i.name for i in bpy.data.images if i.name.startswith("Wyvern_Cor_")),
     "shape_keys": [k.name for k in me.shape_keys.key_blocks] if me.shape_keys else [], "uv_layers": [u.name for u in me.uv_layers],
     "regiao_vertices": len(reg), "regiao_triangulos": len(tris)}
def dims(cos):
    return [round(max(c[i] for c in cos) - min(c[i] for c in cos), 3) for i in range(3)]
R["dim_repouso"] = dims([obj.matrix_world @ v.co for v in me.vertices])
def usar(clipe):
    a = bpy.data.actions[clipe]; arm.animation_data.action = a; _k = bpy.data.objects["Wyvern"].data.shape_keys; _sk = [s for s in a.slots if s.target_id_type == "KEY"]
    if _sk and _k.animation_data: _k.animation_data.action = a; _k.animation_data.action_slot = _sk[0]   # shape keys do clipe (slot KEY)
    try: arm.animation_data.action_slot = a.slots[0]
    except Exception: pass
    return a
def avaliar():
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    return [obj.matrix_world @ v.co for v in ev.vertices]
def area(P, t):
    a, b, c = (P[i] for i in t.vertices); return (b - a).cross(c - a).length / 2
# a malha tem vertices duplicados nas costuras de UV (glTF): vizinhanca por POSICAO de repouso soldada
_chave = {v.index: tuple(round(c, 4) for c in v.co) for v in me.vertices}
def autointersecoes(P):
    ids = [t.vertices[:] for t in tris]; sold = [{_chave[i] for i in t} for t in ids]
    bvh = BVHTree.FromPolygons([P[i] for i in range(len(P))], ids, all_triangles=True)
    n = 0
    for a, b in bvh.overlap(bvh):
        if a < b and not sold[a] & sold[b]: n += 1
    return n
usar("idle_loop"); scn.frame_set(0); P0 = avaliar()
R["dim_idle_f0"] = dims(P0)
rest = [obj.matrix_world @ v.co for v in me.vertices]
A_rest = [area(rest, t) for t in tris]
R["tri_degenerados_<1e-4"] = sum(1 for a in A_rest if a < 1e-4)
R["tri_degenerados_y"] = sorted(round(sum(rest[i].y for i in t.vertices) / 3, 2) for t, a in zip(tris, A_rest) if a < 1e-4)
R["autointersecoes_repouso"] = autointersecoes(rest)
_ids = [t.vertices[:] for t in tris]; _s = [{_chave[i] for i in t} for t in _ids]
_b = BVHTree.FromPolygons(rest, _ids, all_triangles=True)
R["autointersecoes_repouso_y"] = sorted({round(sum(rest[i].y for i in _ids[a]) / 3, 1) for a, b in _b.overlap(_b) if a < b and not _s[a] & _s[b]})
# faces dobradas/invertidas: normal da face contra a normal lisa (soldada por posicao) dos seus vertices
_ac = {}
for t in tris:
    a, b, c = (rest[i] for i in t.vertices); n = (b - a).cross(c - a)
    for i in t.vertices: _ac[_chave[i]] = _ac.get(_chave[i], Vector()) + n
_inv = []
for t in tris:
    a, b, c = (rest[i] for i in t.vertices); n = (b - a).cross(c - a)
    m = sum((_ac[_chave[i]] for i in t.vertices), Vector())
    if n.length > 1e-9 and m.length > 1e-9 and n.normalized().dot(m.normalized()) < 0: _inv.append(round(sum(rest[i].y for i in t.vertices) / 3, 2))
R["faces_dobradas"] = len(_inv); R["faces_dobradas_y"] = sorted(_inv)
# diedros vivos na regiao (arestas com 2 faces e angulo > 60)
import bmesh
bm = bmesh.new(); bm.from_mesh(me)
viv = [round(math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal, 0)), 1) for e in bm.edges
       if len(e.link_faces) == 2 and all(v.co.y >= YR for v in e.verts)]
R["diedros_>60"] = sum(1 for a in viv if a > 60); R["diedros_>90"] = sum(1 for a in viv if a > 90); R["diedro_medio"] = round(sum(viv) / len(viv), 2)
# bordas abertas reais = bordas que nao coincidem com outra borda na mesma posicao (costura de UV nao conta)
bord = [e for e in bm.edges if len(e.link_faces) < 2 and all(v.co.y >= YR for v in e.verts)]
ch = lambda e: frozenset(_chave[v.index] for v in e.verts)
from collections import Counter
cnt = Counter(ch(e) for e in bord)
R["bordas_costura_uv"] = len(bord); R["bordas_abertas_reais"] = sum(1 for e in bord if cnt[ch(e)] < 2)
# UV: razao area3D/areaUV normalizada pela mediana da cauda antes da regiao
uvl = me.uv_layers.active.data
def rz(t, P):
    q = [Vector((*uvl[l].uv, 0)) for l in t.loops]; au = (q[1] - q[0]).cross(q[2] - q[0]).length / 2
    return area(P, t) / max(au, 1e-12)
ref_t = [t for t in me.loop_triangles if all(19.0 < rest[i].y < 22.3 for i in t.vertices)]
ref = sorted(rz(t, rest) for t in ref_t)[len(ref_t) // 2]
u = sorted(rz(t, rest) / ref for t in tris)
R["uv_estiramento_regiao_p05_p50_p95"] = [round(u[int(len(u) * q)], 2) for q in (0.05, 0.5, 0.95)]
R["peso_soma_min_max"] = [round(min(sum(g.weight for g in me.vertices[i].groups) for i in reg), 3), round(max(sum(g.weight for g in me.vertices[i].groups) for i in reg), 3)]
# ciclos
L_rest = {e.index: (rest[e.vertices[0]] - rest[e.vertices[1]]).length for e in edges}
cic = {}
for clipe in ("idle_loop", "walk_loop", "fly_loop"):
    a = usar(clipe); f0, f1 = int(a.frame_range[0]), int(a.frame_range[1])
    est_max = 0; comp_min = 9; ar_min = 9; inter = 0; fr_pior = f0
    for f in range(f0, f1 + 1):
        scn.frame_set(f); P = avaliar()
        for e in edges:
            r = (P[e.vertices[0]] - P[e.vertices[1]]).length / max(L_rest[e.index], 1e-6)
            if r > est_max: est_max = r; fr_pior = f
            comp_min = min(comp_min, r)
        for t, a0 in zip(tris, A_rest):
            if a0 > 1e-4: ar_min = min(ar_min, area(P, t) / a0)
        if f % 2 == 0: inter = max(inter, autointersecoes(P))
    cic[clipe] = {"frames": [f0, f1], "aresta_estiramento_max": round(est_max, 3), "frame_pior": fr_pior,
                  "aresta_compressao_min": round(comp_min, 3), "area_tri_min_vs_repouso": round(ar_min, 3), "autointersecoes_max": inter}
R["ciclos"] = cic
json.dump(R, open(OUT, "w"), indent=1, ensure_ascii=False)
print("OK")
