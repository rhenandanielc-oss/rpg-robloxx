"""Somente leitura: ilhas (componentes conexos) da LOW riggada na cabeca, com tamanho, centro e peso medio da Mandibula.
Uso: blender -b CR_Crocodilo_Rig.blend -P ilhas_cabeca.py"""
import bpy, bmesh
lo = bpy.data.objects["CR_Croc_LOW"]; me = lo.data; gi = lo.vertex_groups["Mandibula"].index
w = {}
for v in me.vertices:
    w[v.index] = sum(g.weight for g in v.groups if g.group == gi)
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); vis = set(); ilhas = []
for v in bm.verts:
    if v.index in vis: continue
    pil = [v]; vis.add(v.index); comp = []
    while pil:
        a = pil.pop(); comp.append(a)
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in vis: vis.add(b.index); pil.append(b)
    ilhas.append(comp)
ilhas.sort(key=len)
print("ILHAS total", len(ilhas), "tamanhos", [len(c) for c in ilhas][-6:])
for c in ilhas:
    if len(c) > 200: continue
    cen = sum((v.co for v in c), c[0].co * 0) / len(c)
    print("ILHA n=%d centro (%.2f, %.2f, %.2f) wm %.2f" % (len(c), cen.x, cen.y, cen.z, sum(w[v.index] for v in c) / len(c)))
# vizinhanca mista: arestas com pesos muito diferentes a frente da juncao
yj = bpy.data.objects["CR_Croc_Rig"].get("y_juncao", -12.75)
mist = [(e, abs(w[e.verts[0].index] - w[e.verts[1].index])) for e in bm.edges if max(e.verts[0].co.y, e.verts[1].co.y) < yj and abs(w[e.verts[0].index] - w[e.verts[1].index]) > 0.5]
print("ARESTAS com salto de peso > 0,5 a frente da juncao:", len(mist))
for e, d in mist[:20]:
    m = (e.verts[0].co + e.verts[1].co) / 2; print("   (%.2f, %.2f, %.2f) salto %.2f" % (m.x, m.y, m.z, d))
