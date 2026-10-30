"""Faces que VIRAM na pose (normal da pose contra a normal de repouso girada pelo osso dominante da face): sao as lascas
e rachaduras escuras. Imprime contagem por acao/quadro e pelos pares de ossos (dominante da face x outro osso forte).
Uso: blender -b Silverwing_M2M.blend -P faces_viradas.py -- [acao:quadro ...]  (sem pedidos = todas, passo 4)"""
import bpy, sys
from mathutils import Vector
from collections import Counter
ANTIGAS = {"Silverwing_Idle", "Silverwing_Walk", "Silverwing_Fly_Flap", "Silverwing_Fly_Glide", "Silverwing_Rest_Pose"}
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
gi = {g.index: g.name for g in M.vertex_groups}
polys = [tuple(p.vertices) for p in M.data.polygons]
N0 = [p.normal.copy() for p in M.data.polygons]
def dom_face(p):
    acc = Counter()
    for v in p:
        for g in M.data.vertices[v].groups: acc[gi[g.group]] += g.weight
    return acc.most_common(2)
DF = [dom_face(p) for p in polys]
if args:
    quadros = [(bpy.data.actions["Silverwing_" + a.split(":")[0]], int(a.split(":")[1])) for a in args]
else:
    quadros = []
    for act in bpy.data.actions:
        if not act.name.startswith("Silverwing_") or act.name in ANTIGAS: continue
        f0, f1 = map(int, act.frame_range); quadros += [(act, f) for f in range(f0, f1 + 1, 4)]
tot = Counter(); por = Counter(); vira_vert = Counter()
for act, f in quadros:
    A.animation_data.action = act
    if len(act.slots): A.animation_data.action_slot = act.slots[0]
    sc.frame_set(f)
    ev = M.evaluated_get(bpy.context.evaluated_depsgraph_get()); me = ev.to_mesh()
    N1 = [p.normal.copy() for p in me.polygons]; ev.to_mesh_clear()
    n = 0
    for i, d in enumerate(DF):
        b = A.pose.bones[d[0][0]]
        R = (b.matrix @ b.bone.matrix_local.inverted()).to_3x3()
        if (R @ N0[i]).normalized().dot(N1[i]) < 0.0:
            n += 1; tot[(d[0][0], d[1][0] if len(d) > 1 else "-")] += 1
            for v in polys[i]: vira_vert[v] += 1
    por[act.name + ":" + str(f) if args else act.name] += n
print("VIRADAS_POR", por.most_common())
print("VIRADAS_OSSOS", tot.most_common(15))
print("VIRADAS_VERTICES", len(vira_vert))
A.animation_data.action = None
print("VIRADAS_OK")
