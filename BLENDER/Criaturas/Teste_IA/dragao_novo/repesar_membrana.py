"""Repesa as MEMBRANAS do CR_Dragao por hastes vizinhas: cada vertice segue so as 2 cadeias mais proximas (dedo/dedo,
dedo/braco, braco/corpo), interpolado pela distancia, e dentro de cada cadeia o osso do trecho mais proximo. Antes, o
inverso da distancia a TODOS os ossos misturava ossos que na dobra ficam longe -> a membrana estufava em cortina.
Uso: blender -b CR_Dragao_M2M.blend -P repesar_membrana.py   (salva no proprio arquivo)"""
import bpy, bmesh
from mathutils import Vector as V
from mathutils.geometry import intersect_point_line
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
for pb in A.pose.bones: pb.matrix_basis.identity()
if A.animation_data: A.animation_data.action = None
bpy.context.view_layer.update()
def cadeias(s):
    return {
        "D0": ["wing_3_" + s, "wing_4_" + s, "wing_5_" + s, "wing_tip_" + s],
        "D1": ["wing_feather_5_0_" + s, "wing_feather_5_1_" + s, "wing_feather_5_tip_" + s],
        "D2": ["wing_feather_4_0_" + s, "wing_feather_4_1_" + s, "wing_feather_4_tip_" + s],
        "D3": ["wing_feather_3_0_" + s, "wing_feather_3_1_" + s, "wing_feather_3_tip_" + s],
        "F2": ["wing_feather_2_0_" + s, "wing_feather_2_1_" + s, "wing_feather_2_tip_" + s],
        "F1": ["wing_feather_1_0_" + s, "wing_feather_1_1_" + s, "wing_feather_1_tip_" + s],
        "BR": ["shoulder_" + s, "wing_1_" + s, "wing_2_" + s],
        "CO": ["spine_1", "spine_0", "hips"]}
def seg(n): b = A.data.bones[n]; return A.matrix_world @ b.head_local, A.matrix_world @ b.tail_local
def no_osso(p, n):
    h, t = seg(n); q, f = intersect_point_line(p, h, t); f = max(0.0, min(1.0, f)); return (p - (h + (t - h) * f)).length
def na_cadeia(p, ossos):
    """(distancia, [(osso, peso)]) - divide entre 2 ossos vizinhos perto da junta"""
    ds = [(no_osso(p, n), i, n) for i, n in enumerate(ossos)]
    ds.sort(); d0, i0, n0 = ds[0]
    viz = [x for x in ds[1:] if abs(x[1] - i0) == 1]
    if viz and viz[0][0] < d0 + 0.02:
        d1, _, n1 = viz[0]; w0 = (d1 - d0 + 0.004) / (2 * 0.004 + d1 - d0)
        return d0, [(n0, w0), (n1, 1 - w0)]
    return d0, [(n0, 1.0)]
# vertices de membrana: pecas soltas largas em X (mesmo criterio da exportacao)
bm = bmesh.new(); bm.from_mesh(M.data); bm.verts.ensure_lookup_table()
vis, memb = set(), []
for v in bm.verts:
    if v.index in vis: continue
    pilha, ilha = [v], []
    while pilha:
        x = pilha.pop()
        if x.index in vis: continue
        vis.add(x.index); ilha.append(x.index)
        for e in x.link_edges: pilha.append(e.other_vert(x))
    xs = [abs(bm.verts[i].co.x) for i in ilha]
    if max(xs) - min(xs) > 0.25 and len(ilha) < 3000: memb += ilha
bm.free()
nomes = {g.index: g.name for g in M.vertex_groups}
for n in set(sum((cadeias(s)[k] for s in ("l", "r") for k in cadeias(s)), [])):
    if n not in M.vertex_groups: M.vertex_groups.new(name=n)
mudou = 0
for i in memb:
    v = M.data.vertices[i]; p = M.matrix_world @ v.co
    s = "l" if p.x > 0 else "r"
    cs = sorted((na_cadeia(p, ossos) + (k,) for k, ossos in cadeias(s).items()), key=lambda x: x[0])
    (da, pa, ka), (db, pb_, kb) = cs[0], cs[1]
    wa = (db + 0.002) / (da + db + 0.004)                     # mais perto = mais peso; so 2 cadeias
    for g in list(v.groups): M.vertex_groups[nomes[g.group]].remove([i])
    for n, w in pa: M.vertex_groups[n].add([i], wa * w, "ADD")
    for n, w in pb_: M.vertex_groups[n].add([i], (1 - wa) * w, "ADD")
    mudou += 1
print("MEMBRANA_REPESADA", mudou, "vertices")
bpy.ops.wm.save_mainfile()
