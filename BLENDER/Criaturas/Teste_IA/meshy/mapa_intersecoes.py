"""Conta intersecoes de faces entre partes (asa x corpo, pata x corpo) por acao/quadro, ignorando faces vizinhas
(compartilham vertice ou estao a <= 2 aneis). Imprime total, ossos dominantes e centro. Opcional: renderiza mapa.
Uso: blender -b Silverwing_M2M.blend -P mapa_intersecoes.py -- [saida_dir] [acao:quadro ...]  (sem pedidos = todas)"""
import bpy, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import Counter
ANTIGAS = {"Silverwing_Idle", "Silverwing_Walk", "Silverwing_Fly_Flap", "Silverwing_Fly_Glide", "Silverwing_Rest_Pose"}
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = args[0] if args else None; pedidos = [a.split(":") for a in args[1:]]
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
gi = {g.index: g.name for g in M.vertex_groups}
def dom(v): return gi[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "-"
DOM = [dom(v) for v in M.data.vertices]
def parte(n):
    if n.startswith(("wing_", "shoulder_")): return "asa_" + n[-1]
    if n.startswith(("front_", "collar_")): return "pd_" + n[-1]
    if n.startswith(("back_", "hips_anchor")): return "pt_" + n[-1]
    if n.startswith("tail"): return "cauda"
    return "corpo"
polys = [tuple(p.vertices) for p in M.data.polygons]
PF = [Counter(parte(DOM[v]) for v in p).most_common(1)[0][0] for p in polys]
viz = [set() for _ in M.data.vertices]
for e in M.data.edges:
    a, b = e.vertices; viz[a].add(b); viz[b].add(a)
perto = []                                   # vertices a ate 3 aneis de cada face (para ignorar contato de costura)
for p in polys:
    s = set(p)
    for _ in range(3): s |= {n for v in s for n in viz[v]}
    perto.append(s)
if pedidos:
    quadros = [(bpy.data.actions.get("Silverwing_" + a), int(q)) for a, q in pedidos]
else:
    quadros = []
    for act in bpy.data.actions:
        if not act.name.startswith("Silverwing_") or act.name in ANTIGAS: continue
        f0, f1 = map(int, act.frame_range); quadros += [(act, f) for f in range(f0, f1 + 1, 4)]
tot = Counter(); por_acao = Counter()
for act, f in quadros:
    A.animation_data.action = act
    if act is None:                                  # repouso
        for pb in A.pose.bones: pb.matrix_basis.identity()
    elif len(act.slots): A.animation_data.action_slot = act.slots[0]
    sc.frame_set(f)
    ev = M.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh()
    P = [v.co.copy() for v in me.vertices]; ev.to_mesh_clear()
    t = BVHTree.FromPolygons(P, polys)
    pares = [(a, b) for a, b in t.overlap(t) if a < b and PF[a] != PF[b] and not (set(polys[b]) & perto[a])]
    c = Counter(tuple(sorted((PF[a], PF[b]))) for a, b in pares)
    for k, n in c.items(): tot[k] += n
    nome = act.name if act else "repouso"
    por_acao[nome] += len(pares)
    if pedidos:
        cent = [sum((P[v] for v in polys[a]), Vector()) / len(polys[a]) for a, b in pares]
        cm = sum(cent, Vector()) / len(cent) if cent else Vector()
        print("INTER", nome, f, len(pares), c.most_common(5), "centro", tuple(round(x, 3) for x in cm))
print("INTER_TOTAL", sum(tot.values()), tot.most_common(12))
print("INTER_ACOES", por_acao.most_common())
A.animation_data.action = None
print("INTER_OK")
