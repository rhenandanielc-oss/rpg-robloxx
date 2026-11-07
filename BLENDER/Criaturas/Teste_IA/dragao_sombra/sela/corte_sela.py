"""Cortes transversais (planos y = constante) do corpo e da sela no repouso, exportados em JSON (desenho: sela/desenhar_cortes.py, Python do sistema): mostra se a sela assenta
no dorso. Corpo: cinza (ilha principal) e laranja (outras ilhas: asa, espinhos); sela: couro marrom, metal azul, madeira.
Uso: blender -b rig/SB_Dragao_M2M_v11_sela.blend -P sela/corte_sela.py -- <saida.json> [y1,y2,...]"""
import bpy, bmesh, sys, os
from mathutils import Vector as V
import json
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0])
A = bpy.data.objects["Silverwing_Rig"]; C = bpy.data.objects["Silverwing"]; S = bpy.data.objects["Silverwing_Sela"]
for b in A.pose.bones: b.matrix_basis.identity()
if A.animation_data: A.animation_data.action = None
bpy.context.view_layer.update()
y0 = (A.matrix_world @ A.data.bones["spine_1"].head_local).y
YS = [float(x) for x in a[1].split(",")] if len(a) > 1 else [y0 - 0.085, y0 - 0.045, y0, y0 + 0.045, y0 + 0.085]
def secoes(o, y, ilhas=False):
    dg = bpy.context.evaluated_depsgraph_get(); oe = o.evaluated_get(dg); me = oe.to_mesh()
    bm = bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); oe.to_mesh_clear()
    comp = {}
    if ilhas:
        bm.verts.ensure_lookup_table(); vis = set(); maior = set()
        for v in bm.verts:
            if v.index in vis: continue
            c, p = set(), [v]
            while p:
                x = p.pop()
                if x.index in vis: continue
                vis.add(x.index); c.add(x.index); p += [e.other_vert(x) for e in x.link_edges]
            if len(c) > len(maior): maior = c
    segs = []
    for f in bm.faces:
        pts = []
        vs = f.verts
        for i in range(len(vs)):
            p, q = vs[i].co, vs[(i + 1) % len(vs)].co
            if (p.y - y) * (q.y - y) < 0:
                t = (y - p.y) / (q.y - p.y); pts.append(p.lerp(q, t))
        if len(pts) == 2:
            tag = (0 if all(v.index in maior for v in vs) else 1) if ilhas else f.material_index
            segs.append((pts[0], pts[1], tag))
    bm.free(); return segs
cs = [m.name for m in S.data.materials]
dados = {"y0": y0, "mats": cs, "cortes": []}
for y in YS:
    corpo = secoes(C, y, True); sela = secoes(S, y)
    dados["cortes"].append({"y": y, "corpo": [[p.x, p.z, q.x, q.z, t] for p, q, t in corpo], "sela": [[p.x, p.z, q.x, q.z, t] for p, q, t in sela]})
json.dump(dados, open(OUT, "w")); print("CORTE_OK", OUT)
