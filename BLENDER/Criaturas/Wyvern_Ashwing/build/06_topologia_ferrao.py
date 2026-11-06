# E6 - ajuste LOCAL de topologia na ponta da cauda (autorizado pelo usuario em 04/11/2026), partindo do E4.
# Defeitos herdados do Ashwing confirmados em 05a/05b:
#  - fenda: a "lamina" do losango original e aberta (borda aberta no lado interno do gancho, verso visivel);
#  - aba: 8 triangulos dobrados na emenda cauda/ponta (y~22,7), verso visivel por baixo, penetra no fly 4-10.
# Passos (so vertices com y >= 22,3, a mesma regiao do E4):
#  1) solda das duplicatas de costura de UV DENTRO da regiao (dist 1e-4): a UV fica por canto, nao muda;
#  2) aba: apaga as faces dobradas da junção (verso para fora) e fecha o buraco com triangulos sobre os
#     vertices que ja existem;
#  3) fenda: fecha os lacos de borda aberta da ponta com triangulos sobre os vertices existentes;
#  4) UV das faces novas copiada dos cantos vizinhos (mesma ilha); pesos = os dos vertices (nenhum vertice novo);
#  5) normais lisas so na regiao (como no E4). Sem osso, material, textura ou subdivisao.
# Uso: blender -b Wyvern_E4.blend -P 06_topologia_ferrao.py -- <saida.blend>
import bpy, bmesh, sys, json, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
obj = bpy.data.objects["Wyvern"]; me = obj.data
YR, YJ, YP = 22.3, 23.2, 26.8          # regiao; limite da zona da junção; inicio da ponta (coords de repouso E4)
antes = {"tris": sum(len(p.vertices) - 2 for p in me.polygons), "verts": len(me.vertices)}
bm = bmesh.new(); bm.from_mesh(me)
uv = bm.loops.layers.uv.active
reg = lambda v: v.co.y >= YR
# 1) solda das duplicatas de costura na regiao
rv = [v for v in bm.verts if reg(v)]
bmesh.ops.remove_doubles(bm, verts=rv, dist=1e-4)
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
def normal_lisa(v):
    n = Vector()
    for f in v.link_faces: n += f.normal * f.calc_area()
    return n
def dobrada(f):
    m = sum((normal_lisa(v) for v in f.verts), Vector())
    return m.length > 1e-12 and f.normal.dot(m.normalized()) < 0
bm.normal_update()
# 2) aba da junção: faces dobradas com todos os vertices na zona da junção (+ faces que ficariam soltas)
aba = [f for f in bm.faces if all(reg(v) and v.co.y < YJ for v in f.verts) and dobrada(f)]
info = {"aba_faces_apagadas": len(aba)}
borda_antes = {e for e in bm.edges if e.is_boundary}
bmesh.ops.delete(bm, geom=aba, context="FACES_ONLY")
soltos = [v for v in bm.verts if reg(v) and not v.link_faces]
bmesh.ops.delete(bm, geom=soltos, context="VERTS"); info["aba_vertices_soltos_apagados"] = len(soltos)
def lacos(edges):
    edges = set(edges); out = []
    while edges:
        e = edges.pop(); laco = {e}; pilha = [e]
        while pilha:
            x = pilha.pop()
            for v in x.verts:
                for y in v.link_edges:
                    if y in edges: edges.discard(y); laco.add(y); pilha.append(y)
        out.append(laco)
    return out
def fechar(edges_laco, nome):
    vs = {v for e in edges_laco for v in e.verts}
    fechado = all(sum(1 for e in v.link_edges if e in edges_laco) == 2 for v in vs)
    r = bmesh.ops.holes_fill(bm, edges=list(edges_laco), sides=0)
    novas = r["faces"]
    if novas:
        t = bmesh.ops.triangulate(bm, faces=novas, quad_method="BEAUTY", ngon_method="BEAUTY")
        novas = t["faces"]
    return {"laco": nome, "arestas": len(edges_laco), "fechado": fechado, "faces_novas": len(novas)}, novas
novas_todas = []
# buraco deixado pela aba
borda_nova = [e for e in bm.edges if e.is_boundary and reg(e.verts[0]) and reg(e.verts[1]) and e not in borda_antes]
bj = [e for e in bm.edges if e.is_boundary and all(reg(v) and v.co.y < YJ for v in e.verts)]
info["juncao_lacos"] = []
for L in lacos(bj):
    i, nv = fechar(L, "juncao"); info["juncao_lacos"].append(i); novas_todas += nv
# 3) fenda da ponta: na verdade sao ABAS soltas (triangulos presos por aresta nao-manifold, com borda aberta),
#    herdadas do losango do Ashwing. Remove so essas abas (iterando) e fecha os lacos que sobrarem.
info["ponta_abas_apagadas"] = 0
for it in range(12):
    nm = lambda e: len(e.link_faces) > 2
    abas = [f for f in bm.faces if all(v.co.y > YP for v in f.verts)
            and ((any(nm(e) for e in f.edges) and any(e.is_boundary for e in f.edges))
                 or all(e.is_boundary for e in f.edges))]          # + triangulo isolado preso so por um vertice
    if not abas: break
    bmesh.ops.delete(bm, geom=abas, context="FACES_ONLY"); info["ponta_abas_apagadas"] += len(abas)
    soltos = [v for v in bm.verts if v.co.y > YP and not v.link_faces]
    bmesh.ops.delete(bm, geom=soltos, context="VERTS")
info["nao_manifold_restantes_regiao"] = sum(1 for e in bm.edges if len(e.link_faces) > 2 and all(reg(v) for v in e.verts))
bp = [e for e in bm.edges if e.is_boundary and all(v.co.y > YP for v in e.verts)]
info["ponta_lacos"] = []
for L in lacos(bp):
    i, nv = fechar(L, "ponta"); info["ponta_lacos"].append(i); novas_todas += nv
bm.normal_update()
# orientacao das faces novas igual a das vizinhas (normal contra a normal lisa local)
for f in novas_todas:
    if f.is_valid and dobrada(f): f.normal_flip()
bm.normal_update()
# 4) UV das faces novas: para cada canto, a UV do mesmo vertice numa face vizinha que compartilha aresta
for f in novas_todas:
    if not f.is_valid: continue
    for l in f.loops:
        cand = None
        for e in (l.edge, l.link_loop_prev.edge):
            for g in e.link_faces:
                if g is f or g in novas_todas: continue
                for l2 in g.loops:
                    if l2.vert is l.vert: cand = l2[uv].uv.copy(); break
                if cand: break
            if cand: break
        if cand is None:
            for l2 in l.vert.link_loops:
                if l2.face not in novas_todas: cand = l2[uv].uv.copy(); break
        if cand is not None: l[uv].uv = cand
# limpeza: arestas soltas (sobra de FACES_ONLY) e vertices soltos, so na regiao
bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces and all(reg(v) for v in e.verts)], context="EDGES")
bmesh.ops.delete(bm, geom=[v for v in bm.verts if reg(v) and not v.link_faces], context="VERTS")
info["bordas_restantes_regiao"] =sum(1 for e in bm.edges if e.is_boundary and all(reg(v) for v in e.verts))
bm.to_mesh(me); bm.free(); me.update()
# 4b) pesos da junção: a camada da cauda (tail_08) sobrepoe a da ponta (tail_09) no dorso em y~22,4-23,3 e os
#     pesos originais sao desencontrados entre as camadas (22,62 -> 94% tail_09; 22,83 -> 94% tail_08) -> no fly as
#     camadas deslizam e se cruzam. Rampa unica tail_08->tail_09 por y (as duas camadas andam juntas).
g08 = obj.vertex_groups["tail_08"]; g09 = obj.vertex_groups["tail_09"]
JA, JB = 22.3, 23.1
n_peso = 0
for v in me.vertices:
    if not (JA <= v.co.y <= JB): continue
    gs = {g.group for g in v.groups if g.weight > 1e-4}
    if not gs <= {g08.index, g09.index}: continue
    x = (v.co.y - JA) / (JB - JA); w = x * x * (3 - 2 * x)
    g08.add([v.index], 1 - w, "REPLACE"); g09.add([v.index], w, "REPLACE"); n_peso += 1
info["juncao_vertices_peso_rampa"] = n_peso
# 5) normais: cantos fora da regiao preservados; regiao lisa por vertice (agora soldada), entrada suave em YR
cn = [Vector(c.vector) for c in me.corner_normals]
def sstep(x):
    x = min(1.0, max(0.0, x)); return x * x * x * (x * (6 * x - 15) + 10)
acum = {}
for p in me.polygons:
    for v in p.vertices:
        if me.vertices[v].co.y >= YR: acum[v] = acum.get(v, Vector()) + p.normal * p.area
for l in me.loops:
    v = l.vertex_index
    if v in acum and acum[v].length > 1e-9:
        cn[l.index] = cn[l.index].lerp(acum[v].normalized(), sstep((me.vertices[v].co.y - YR) / 0.6)).normalized()
me.normals_split_custom_set([c[:] for c in cn])
me.update()
info["antes"] = antes; info["depois"] = {"tris": sum(len(p.vertices) - 2 for p in me.polygons), "verts": len(me.vertices)}
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("RJSON" + json.dumps(info) + "RFIM")
