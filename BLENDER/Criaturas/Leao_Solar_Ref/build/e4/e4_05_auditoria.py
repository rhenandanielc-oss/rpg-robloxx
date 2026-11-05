"""E4: auditoria da malha de jogo (le, nao salva): contagens por peca (material/grupo), bordas abertas, arestas >2 faces,
vertices nao-manifold, faces degeneradas, normais inconsistentes, cascas (ilhas de geometria), autointersecoes
(pares de triangulos que se cruzam sem compartilhar vertice), vertices com UV, influencias de osso, texturas.
Uso: blender -b Leao_Solar_Ref_E4.blend -P e4_05_auditoria.py -- <saida.json>"""
import bpy, bmesh, sys, json
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; me = ob.data
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
r = {}
r["tris"] = sum(len(f.verts) - 2 for f in bm.faces); r["verts"] = len(bm.verts); r["faces"] = len(bm.faces)
uv = me.uv_layers.active.data
r["verts_com_uv"] = len({(l.vertex_index, round(uv[l.index].uv[0], 5), round(uv[l.index].uv[1], 5)) for l in me.loops})
borda = [e for e in bm.edges if e.is_boundary]
r["bordas_abertas"] = len(borda); r["arestas_mais_2_faces"] = sum(1 for e in bm.edges if len(e.link_faces) > 2)
r["verts_nao_manifold"] = sum(1 for v in bm.verts if not v.is_manifold)
r["faces_degeneradas"] = sum(1 for f in bm.faces if f.calc_area() < 1e-7)
r["arestas_comprimento_zero"] = sum(1 for e in bm.edges if e.calc_length() < 1e-6)
inc = 0; MATS_INC = []
for e in bm.edges:
    if len(e.link_faces) == 2:
        a, b = e.link_faces; va, vb = e.verts
        def ordem(f):
            vs = list(f.verts); i = vs.index(va); return vs[(i + 1) % len(vs)] == vb
        if ordem(a) == ordem(b):
            inc += 1; MATS_INC.append(tuple(round(c, 2) for c in e.verts[0].co))
r["arestas_normais_inconsistentes"] = inc; r["normais_inc_ex"] = MATS_INC[:15]
# cascas
vis = set(); cascas = []; casca_de = {}
for f in bm.faces:
    if f.index in vis: continue
    pilha = [f]; vis.add(f.index); n = 0; k = len(cascas)
    while pilha:
        g = pilha.pop(); n += 1; casca_de[g.index] = k
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in vis: vis.add(h.index); pilha.append(h)
    cascas.append(n)
# localizacao das normais inconsistentes

r["cascas"] = len(cascas); r["cascas_faces"] = sorted(cascas, reverse=True)[:40]
# pecas pelos grupos/cores: dentes = vertices so com grupo e cor clara; simples: por cascas pequenas
me.calc_loop_triangles(); T = me.loop_triangles
bvh = BVHTree.FromPolygons([v.co for v in me.vertices], [list(t.vertices) for t in T])
pares = bvh.overlap(bvh); n_ai = 0; ex = []; CAT = {}
for a, b in pares:
    if a >= b: continue
    if set(T[a].vertices) & set(T[b].vertices): continue
    n_ai += 1
    ca, cb = casca_de[T[a].polygon_index], casca_de[T[b].polygon_index]
    cat = ("corpo_x_corpo" if ca == cb == 0 else "mesma_peca" if ca == cb else "corpo_x_peca" if 0 in (ca, cb) else "peca_x_peca")
    CAT[cat] = CAT.get(cat, 0) + 1
    if cat == "corpo_x_corpo" and len(ex) < 12: ex.append([round(c, 2) for c in T[a].center])
r["autointersecoes_pares"] = n_ai; r["autointersecoes_por_tipo"] = CAT; r["autointersecoes_ex"] = ex
gi = {g.index: g.name for g in ob.vertex_groups}
infl = [sum(1 for g in v.groups if g.weight > 1e-4) for v in me.vertices]
r["grupos"] = list(gi.values()); r["influencias_max_por_vertice"] = max(infl) if infl else 0
r["materiais"] = [m.name for m in me.materials]
r["texturas"] = sorted({n.image.filepath for m in me.materials for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image})
# bordas abertas por posicao
r["bordas_ex"] = [[round(c, 2) for c in ((e.verts[0].co + e.verts[1].co) / 2)] for e in borda[:20]]
json.dump(r, open(A[0], "w"), indent=1); print("AUDIT_E4", json.dumps({k: v for k, v in r.items() if k not in ("cascas_faces", "autointersecoes_ex", "bordas_ex", "texturas")}))
print("cascas", r["cascas_faces"][:30]); print("autointersecoes ex", ex); print("bordas ex", r["bordas_ex"])
