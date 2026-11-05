"""Somente leitura: lacos de borda aberta e faces-lasca (muito finas) da LOW riggada, com posicao e peso da Mandibula.
Uso: blender -b CR_Crocodilo_Rig.blend -P diag_bordas.py"""
import bpy, bmesh
lo = bpy.data.objects["CR_Croc_LOW"]; me = lo.data; gi = lo.vertex_groups["Mandibula"].index
w = {v.index: sum(g.weight for g in v.groups if g.group == gi) for v in me.vertices}
bm = bmesh.new(); bm.from_mesh(me); bm.edges.ensure_lookup_table()
bd = {e.index for e in bm.edges if e.is_boundary}; vis = set(); lacos = []
for e0 in list(bd):
    if e0 in vis: continue
    pil = [bm.edges[e0]]; comp = []
    while pil:
        e = pil.pop()
        if e.index in vis: continue
        vis.add(e.index); comp.append(e)
        for v in e.verts:
            for e2 in v.link_edges:
                if e2.index in bd and e2.index not in vis: pil.append(e2)
    lacos.append(comp)
print("BORDAS arestas", len(bd), "lacos", len(lacos))
for c in sorted(lacos, key=len, reverse=True):
    vs = {v for e in c for v in e.verts}; cen = sum((v.co for v in vs), list(vs)[0].co * 0) / len(vs)
    fechado = all(sum(1 for e2 in v.link_edges if e2.index in bd) == 2 for v in vs)
    print("LACO arestas %d fechado %s centro (%.2f, %.2f, %.2f) wm %.2f" % (len(c), fechado, cen.x, cen.y, cen.z, sum(w[v.index] for v in vs) / len(vs)))
lascas = []
for f in bm.faces:
    c = f.calc_center_median()
    if c.y > -10.0: continue
    a = f.calc_area(); per = f.calc_perimeter()
    if a > 0 and per * per / a > 80: lascas.append((per * per / a, c))
print("LASCAS faces finas na cabeca", len(lascas))
for r, c in sorted(lascas, reverse=True)[:15]: print("   razao %.0f em (%.2f, %.2f, %.2f)" % (r, c.x, c.y, c.z))
