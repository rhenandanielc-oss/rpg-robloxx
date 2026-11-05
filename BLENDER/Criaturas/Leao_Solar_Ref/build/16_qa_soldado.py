"""QA da E2 com as costuras de UV soldadas (copia em memoria; nao salva): partes reais, bordas abertas, auto-cruzamento nao medido.
Uso: blender -b <e2.blend> -P 16_qa_soldado.py"""
import bpy, bmesh
me = bpy.data.objects["Leao_Solar_E2"].data
bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
abertas = sum(1 for e in bm.edges if e.is_boundary); bm.verts.ensure_lookup_table()
vis = set(); partes = []
for v in bm.verts:
    if v.index in vis: continue
    p = [v]; vis.add(v.index); n = 0
    while p:
        a = p.pop(); n += 1
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in vis: vis.add(b.index); p.append(b)
    partes.append(n)
print("QA_SOLDADO verts", len(bm.verts), "partes", len(partes), "maiores", sorted(partes)[-4:], "bordas_abertas", abertas,
      "pecas_pequenas(<50 verts)", sum(1 for x in partes if x < 50))
