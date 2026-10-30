"""Zera asa-dentro-do-corpo: varre todos os quadros, junta vertices de asa (fora da raiz) do lado de dentro da pele
(prof. > 0.004) e passa metade do peso de wing_2/wing_feather_2/3 desses vertices (e do 1o anel, 1/4) para wing_1 do
mesmo lado (o braco fica por fora). Repete ate zerar (max 5 passadas).
Uso: blender -b Silverwing_M2M.blend -P corrigir_penetracao.py"""
import bpy
ANTIGAS = {"Silverwing_Idle", "Silverwing_Walk", "Silverwing_Fly_Flap", "Silverwing_Fly_Glide", "Silverwing_Rest_Pose"}   # fontes de asa (nao exportadas)
from mathutils.bvhtree import BVHTree
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
polys = [tuple(p.vertices) for p in M.data.polygons]
viz = [set() for _ in M.data.vertices]
for e in M.data.edges:
    a, b = e.vertices; viz[a].add(b); viz[b].add(a)
acoes = sorted([a for a in bpy.data.actions if a.name.startswith("Silverwing_") and a.name not in ANTIGAS], key=lambda a: a.name)
MOV = ("wing_2_", "wing_feather_2_", "wing_feather_3_")
for passada in range(5):
    gi = {g.index: g.name for g in M.vertex_groups}
    D = [gi[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "-" for v in M.data.vertices]
    asa = [d.startswith(("wing_", "shoulder_")) for d in D]
    raiz = [d.startswith(("shoulder_", "wing_1_", "wing_feather_1_")) for d in D]
    ic = [k for k, p in enumerate(polys) if not asa[p[0]]]
    S = set(); tot = 0
    for act in acoes:
        A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
        f0, f1 = map(int, act.frame_range)
        for f in range(f0, f1 + 1):
            sc.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh()
            P = [v.co.copy() for v in me.vertices]; M.evaluated_get(dg).to_mesh_clear()
            tc = BVHTree.FromPolygons(P, [polys[k] for k in ic])
            for i in range(len(P)):
                if not asa[i] or raiz[i]: continue
                loc, nrm, fi, d = tc.find_nearest(P[i], 0.05)
                if loc is not None and -(P[i] - loc).dot(nrm) > 0.004: S.add(i); tot += 1
    print("PASSADA", passada, "ocorrencias", tot, "vertices", len(S))
    if not S: break
    anel = {j for i in S for j in viz[i]} - S
    for conj, fator in ((S, 0.5), (anel, 0.25)):
        for i in conj:
            v = M.data.vertices[i]; ps = {gi[g.group]: g.weight for g in v.groups if g.weight > 1e-4}
            lado = D[i][-1]
            mov = sum(w for n, w in ps.items() if n.startswith(MOV)) * fator
            if mov <= 0: continue
            novo = {n: (w * (1 - fator) if n.startswith(MOV) else w) for n, w in ps.items()}
            novo["wing_1_" + lado] = novo.get("wing_1_" + lado, 0) + mov
            top = sorted(novo.items(), key=lambda x: -x[1])[:4]; s = sum(w for _, w in top)
            for g in list(v.groups): M.vertex_groups[g.group].remove([i])
            for n, w in top: M.vertex_groups[n].add([i], w / s, "REPLACE")
A.animation_data.action = None
for pb in A.pose.bones: pb.matrix_basis.identity()
bpy.ops.wm.save_mainfile()
print("PEN_OK")

