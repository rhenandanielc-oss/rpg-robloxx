"""QA da malha da E2: tris, partes soltas, bordas abertas/nao-manifold, texturas, medidas (cernelha, juba, comprimento).
Uso: blender -b <arquivo.blend> -P 11_qa_malha.py"""
import bpy, bmesh
ob = bpy.data.objects["Leao_Solar_E2"]; me = ob.data
bm = bmesh.new(); bm.from_mesh(me)
abertas = sum(1 for e in bm.edges if e.is_boundary); nao_man = sum(1 for e in bm.edges if not e.is_manifold)
bm.verts.ensure_lookup_table(); vis = set(); partes = []
for v in bm.verts:
    if v.index in vis: continue
    pilha = [v]; vis.add(v.index); n = 0
    while pilha:
        a = pilha.pop(); n += 1
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in vis: vis.add(b.index); pilha.append(b)
    partes.append(n)
K = 11.5 / 360
def faixa(y0, y1): return [v.co for v in me.vertices if y0 < v.co.y < y1 and abs(v.co.x) < 0.4]
dorso = {x: round(max(p.z for p in faixa(-(x - 620) * K - 0.2, -(x - 620) * K + 0.2)), 2) for x in (480, 540, 600, 640)}
co = [v.co for v in me.vertices]
print("QA tris", sum(len(p.vertices) - 2 for p in me.polygons), "verts", len(me.vertices), "partes", len(partes),
      "maiores", sorted(partes)[-3:], "bordas_abertas", abertas, "nao_manifold", nao_man)
print("QA dorso_z_por_x_px", dorso, "topo", round(max(p.z for p in co), 2), "Y", round(min(p.y for p in co), 2), round(max(p.y for p in co), 2),
      "X", round(min(p.x for p in co), 2), round(max(p.x for p in co), 2))
print("QA materiais", [m.name for m in me.materials], "imagens", [(i.name, tuple(i.size)) for i in bpy.data.images if i.size[0]])
