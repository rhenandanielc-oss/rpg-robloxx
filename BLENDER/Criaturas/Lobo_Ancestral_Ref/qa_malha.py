"""QA da malha LOW do Lobo (so leitura): tris, bordas abertas (buracos), arestas nao-manifold, dobras bruscas (angulo
diedro > 120 graus entre faces vizinhas) no total e na regiao peito/ombro/topo das patas, erro de simetria (vertice x
espelho mais proximo) e vertices sem peso. Uso: blender -b <rig.blend> -P qa_malha.py -- <saida.json>"""
import bpy, bmesh, sys, json, math
import numpy as np
from mathutils.kdtree import KDTree
OUT = sys.argv[sys.argv.index("--") + 1]
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; me = LO.data; BD = bpy.data.objects["Lobo_Ancestral_Rig"].data.bones
yo = BD["BracoE"].head_local.y
bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
def na_regiao(p): return 0.2 < abs(p.x) < 1.8 and 2.6 < p.z < 4.7 and yo - 1.5 < p.y < yo + 0.9
borda = [e for e in bm.edges if e.is_boundary]; nman = [e for e in bm.edges if not e.is_manifold and not e.is_boundary]
dobras = [];
for e in bm.edges:
    if len(e.link_faces) == 2:
        a = math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal, 0))
        if a > 120: dobras.append(e)
reg_d = [e for e in dobras if na_regiao((e.verts[0].co + e.verts[1].co) / 2)]
reg_b = [e for e in borda if na_regiao((e.verts[0].co + e.verts[1].co) / 2)]
co = np.array([v.co[:] for v in me.vertices]); kd = KDTree(len(co))
for i, p in enumerate(co): kd.insert(p, i)
kd.balance()
sim = max(kd.find((-p[0], p[1], p[2]))[2] for p in co)
r = {"tris": sum(len(p.vertices) - 2 for p in me.polygons), "bordas_abertas": len(borda), "bordas_abertas_regiao": len(reg_b),
     "nao_manifold": len(nman), "dobras_120": len(dobras), "dobras_120_regiao": len(reg_d), "erro_simetria_max": round(float(sim), 5),
     "sem_peso": sum(1 for v in me.vertices if not v.groups)}
print("QA_MALHA", r); json.dump(r, open(OUT, "w"), indent=1)
