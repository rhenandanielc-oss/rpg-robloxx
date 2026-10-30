"""Corrige cruzamentos asa-esquerda x asa-direita na raiz (linha media do dorso): varre todos os quadros de todas as acoes,
junta os vertices das faces que se cruzam e transfere o peso de shoulder_*/wing_1_*/wing_feather_1_* desses vertices
(e de 2 aneis de vizinhos, metade) para spine_0/spine_1. Repete ate zerar ou 4 passadas.
Uso: blender -b Silverwing_M2M.blend -P corrigir_cruzamentos.py"""
import bpy
ANTIGAS = {"Silverwing_Idle", "Silverwing_Walk", "Silverwing_Fly_Flap", "Silverwing_Fly_Glide", "Silverwing_Rest_Pose"}   # fontes de asa (nao exportadas)
from mathutils.bvhtree import BVHTree
sc = bpy.context.scene
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
polys = [tuple(p.vertices) for p in M.data.polygons]
viz = [set() for _ in M.data.vertices]
for e in M.data.edges:
    a, b = e.vertices; viz[a].add(b); viz[b].add(a)
RAIZ = ("shoulder_", "wing_1_", "wing_feather_1_")
acoes = sorted([a for a in bpy.data.actions if a.name.startswith("Silverwing_") and a.name not in ANTIGAS], key=lambda a: a.name)
def lado(v):
    gi = {g.index: g.name for g in M.vertex_groups}
    if not len(v.groups): return ""
    n = gi[max(v.groups, key=lambda g: g.weight).group]
    return n[-1] if n.startswith(("wing_", "shoulder_")) else ""
for passada in range(4):
    LADO = [lado(v) for v in M.data.vertices]
    il = [i for i, p in enumerate(polys) if LADO[p[0]] == "l"]; ir = [i for i, p in enumerate(polys) if LADO[p[0]] == "r"]
    S = set(); total = 0
    for act in acoes:
        A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
        f0, f1 = map(int, act.frame_range)
        for f in range(f0, f1 + 1, 2):
            sc.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh()
            P = [v.co.copy() for v in me.vertices]; M.evaluated_get(dg).to_mesh_clear()
            tl = BVHTree.FromPolygons(P, [polys[i] for i in il]); tr = BVHTree.FromPolygons(P, [polys[i] for i in ir])
            par = tl.overlap(tr); total += len(par)
            for a, b in par: S.update(polys[il[a]]); S.update(polys[ir[b]])
    print("PASSADA", passada, "cruzamentos_somados", total, "vertices", len(S))
    if not S: break
    anel1 = {j for i in S for j in viz[i]} - S; anel2 = {j for i in anel1 for j in viz[i]} - S - anel1
    gi = {g.index: g.name for g in M.vertex_groups}
    for conj, fator in ((S, 1.0), (anel1, 0.6), (anel2, 0.3)):
        for i in conj:
            v = M.data.vertices[i]; ps = {gi[g.group]: g.weight for g in v.groups if g.weight > 1e-4}
            mov = sum(w for n, w in ps.items() if n.startswith(RAIZ)) * fator
            if mov <= 0: continue
            novo = {n: (w * (1 - fator) if n.startswith(RAIZ) else w) for n, w in ps.items()}
            novo["spine_0"] = novo.get("spine_0", 0) + mov * 0.6; novo["spine_1"] = novo.get("spine_1", 0) + mov * 0.4
            top = sorted(novo.items(), key=lambda x: -x[1])[:4]; s = sum(w for _, w in top)
            for g in list(v.groups): M.vertex_groups[g.group].remove([i])
            for n, w in top: M.vertex_groups[n].add([i], w / s, "REPLACE")
A.animation_data.action = None
for pb in A.pose.bones: pb.matrix_basis.identity()
bpy.ops.wm.save_mainfile()
print("CRUZ_OK")

