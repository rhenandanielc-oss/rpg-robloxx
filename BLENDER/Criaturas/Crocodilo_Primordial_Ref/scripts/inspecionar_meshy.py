"""Somente leitura: ilhas, bordas abertas, faixa da boca e renders da boca do CR_Crocodilo_Meshy.blend.
Uso: blender -b CR_Crocodilo_Meshy.blend -P inspecionar_meshy.py -- <saida_dir>"""
import bpy, bmesh, sys, os
from mathutils import Vector as V
OUT = sys.argv[sys.argv.index("--") + 1:][0]
sc = bpy.context.scene; ob = bpy.data.objects["CR_Croc_Meshy"]
bm = bmesh.new(); bm.from_mesh(ob.data)
abertas = sum(1 for e in bm.edges if e.is_boundary); nao_man = sum(1 for e in bm.edges if not e.is_manifold)
bm.verts.ensure_lookup_table(); vis = set(); ilhas = []
for v in bm.verts:
    if v.index in vis: continue
    pilha = [v]; vis.add(v.index); n = 0
    while pilha:
        a = pilha.pop(); n += 1
        for e in a.link_edges:
            b = e.other_vert(a)
            if b.index not in vis: vis.add(b.index); pilha.append(b)
    ilhas.append(n)
ilhas.sort(reverse=True)
print("INSPECAO verts", len(bm.verts), "ilhas", len(ilhas), "maiores", ilhas[:6], "bordas_abertas", abertas, "nao_manifold", nao_man)
cab = [v.co for v in bm.verts if v.co.y < -10]
print("CABECA z min/max", round(min(p.z for p in cab), 2), round(max(p.z for p in cab), 2), "y min", round(min(p.y for p in cab), 2))
cam = sc.camera; cd = cam.data; cd.type = "PERSP"
for nome, p, a, lente in (("boca_frente", V((0.0, -22.5, 3.3)), V((0, -12.0, 3.0)), 55), ("boca_34", V((5.5, -19.5, 4.6)), V((0, -12.0, 3.0)), 45),
                          ("boca_baixo", V((2.5, -18.0, 0.6)), V((0, -12.0, 3.0)), 45)):
    cam.location = p; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
    sc.render.filepath = os.path.join(OUT, "m1_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("INSPECAO_OK")
