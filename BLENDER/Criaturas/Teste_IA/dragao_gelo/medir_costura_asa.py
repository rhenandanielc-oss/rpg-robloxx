"""Mede se a asa SE SOLTA do corpo (usuario 02/11: "a asa deve se juntar ao corpo, nao ficar separada").
Costura = vertices de asa/ombro que em repouso estao a menos de LIM do tronco (superficie das faces do tronco). Em cada
quadro dos clipes pedidos mede a distancia de cada vertice da costura ate a superficie do tronco deformado.
Uso: blender -b rig.blend -P medir_costura_asa.py -- Clipe1,Clipe2 [LIM]"""
import bpy, sys
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]; nomes = a[0].split(","); LIM = float(a[1]) if len(a) > 1 else 0.012
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
for m in M.modifiers: m.show_viewport = True
gi = {g.index: g.name for g in M.vertex_groups}
def dom(v): return gi[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else ""
def asa(n): return n.startswith(("wing_", "shoulder_"))
DOM = [dom(v) for v in M.data.vertices]
EH_ASA = [asa(n) for n in DOM]
POL_TRONCO = [p.index for p in M.data.polygons if sum(1 for i in p.vertices if not EH_ASA[i]) == len(p.vertices)]
def estado():
    dg = bpy.context.evaluated_depsgraph_get(); ev = M.evaluated_get(dg); me = ev.to_mesh()
    co = [v.co.copy() for v in me.vertices]
    polys = [tuple(me.polygons[i].vertices) for i in POL_TRONCO]
    ev.to_mesh_clear()
    return co, BVHTree.FromPolygons(co, polys)
A.animation_data.action = None
for b in A.pose.bones: b.matrix_basis.identity()
sc.frame_set(1)
co0, bvh0 = estado()
costura = [i for i, e in enumerate(EH_ASA) if e and bvh0.find_nearest(co0[i])[3] is not None and bvh0.find_nearest(co0[i])[3] < LIM]
lado = {i: ("E" if co0[i].x > 0 else "D") for i in costura}
print("COSTURA", len(costura), "vertices (E %d / D %d)" % (sum(1 for i in costura if lado[i] == "E"), sum(1 for i in costura if lado[i] == "D")))
for nome in nomes:
    act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); pior, piorF, soltos = 0, f0, 0
    for f in range(f0, f1 + 1, 2):
        sc.frame_set(f); co, bvh = estado()
        ds = [bvh.find_nearest(co[i])[3] or 0 for i in costura]
        mx = max(ds); n = sum(1 for d in ds if d > 0.02)
        if mx > pior: pior, piorF = mx, f
        soltos = max(soltos, n)
    print("COST", nome, "maior afastamento %.2f studs (quadro %d) | vertices da costura a mais de 0,35 stud: ate %d de %d" % (pior * 17.5, piorF, soltos, len(costura)))
