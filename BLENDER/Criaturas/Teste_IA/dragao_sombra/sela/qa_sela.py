"""QA de encaixe da sela no corpo, em varias poses (malhas avaliadas com o esqueleto).
v2: cada vertice da sela e medido contra o MESMO ponto da pele que fica embaixo dele no repouso (triangulo + baricentricas
guardados no repouso), entao asa dobrada por cima nao confunde a medida. Folga com sinal: < 0 = dentro do corpo.
Relata por pose e por peca (material): % de vertices dentro (abaixo de -0,5 mm) e a folga da face INTERNA (_interno).
Uso: blender -b rig/SB_Dragao_M2M_v11_sela.blend -P sela/qa_sela.py -- [poses]"""
import bpy, sys
from mathutils.bvhtree import BVHTree
from mathutils.geometry import area_tri
a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
POSES = (a[0] if a else "Rest_Pose:0,Parado:0.3,Andar:0.25,Andar:0.75,Voo:0.3,Voo:0.7,Fly_Glide:0.5,Decolagem:0.5,Pouso:0.6").split(",")
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; C = bpy.data.objects["Silverwing"]; S = bpy.data.objects["Silverwing_Sela"]
if not A.animation_data: A.animation_data_create()
gi = S.vertex_groups.get("_interno")
interno = {v.index for v in S.data.vertices for g in v.groups if gi and g.group == gi.index and g.weight > 0.5}
ga = {g.index for g in C.vertex_groups if g.name.startswith("wing_") and not g.name.startswith("wing_1")}   # membrana/dedos
ASA = {v.index for v in C.data.vertices if sum(g.weight for g in v.groups if g.group in ga) > 0.5}
mats = [m.name.replace("M_Sela_", "") for m in S.data.materials]
peca = {vi: mats[p.material_index] for p in S.data.polygons for vi in p.vertices}
def pose(nome, fr):
    act = bpy.data.actions.get("Silverwing_" + nome)
    if act:
        A.animation_data.action = act
        if hasattr(A.animation_data, "action_slot") and act.slots: A.animation_data.action_slot = act.slots[0]
        f0, f1 = act.frame_range; sc.frame_set(int(f0 + (f1 - f0) * float(fr)))
    else:
        A.animation_data.action = None
        for b in A.pose.bones: b.matrix_basis.identity()
        sc.frame_set(1)
    dg = bpy.context.evaluated_depsgraph_get()
    ce = C.evaluated_get(dg); me = ce.to_mesh(); mw = C.matrix_world
    vb = [mw @ v.co for v in me.vertices]; me.calc_loop_triangles()
    tris = [tuple(t.vertices) for t in me.loop_triangles if not any(i in ASA for i in t.vertices)]
    ce.to_mesh_clear()
    se = S.evaluated_get(dg); ms = se.to_mesh(); vs = [S.matrix_world @ v.co for v in ms.vertices]; se.to_mesh_clear()
    return vb, tris, vs
# ancoras no repouso, so na ILHA PRINCIPAL do corpo (a mesma de onde a sela tira os pesos)
vb, tris, vs = pose("Rest_Pose", 0)
viz = {}
for t in tris:
    for x in t:
        for y in t:
            if x != y: viz.setdefault(x, set()).add(y)
vis, maior = set(), set()
for s0 in viz:
    if s0 in vis: continue
    comp, pilha = set(), [s0]
    while pilha:
        x = pilha.pop()
        if x in vis: continue
        vis.add(x); comp.add(x); pilha.extend(viz[x] - vis)
    if len(comp) > len(maior): maior = comp
tris = [t for t in tris if t[0] in maior]
bvh = BVHTree.FromPolygons(vb, tris)
anc = []
for p in vs:
    q, n, fi, d = bvh.find_nearest(p); t = tris[fi]; a3, b3, c3 = vb[t[0]], vb[t[1]], vb[t[2]]
    tot = area_tri(a3, b3, c3) or 1e-12
    anc.append((t, (area_tri(q, b3, c3) / tot, area_tri(a3, q, c3) / tot, area_tri(a3, b3, q) / tot)))
for item in POSES:
    nome, fr = item.split(":")
    vb, _, vs = pose(nome, fr)
    por = {}; gaps = []
    for i, p in enumerate(vs):
        t, bc = anc[i]; a3, b3, c3 = vb[t[0]], vb[t[1]], vb[t[2]]
        q = a3 * bc[0] + b3 * bc[1] + c3 * bc[2]; n = (b3 - a3).cross(c3 - a3).normalized()
        sd = (p - q).dot(n)
        k = peca.get(i, "?"); c_ = por.setdefault(k, [0, 0]); c_[1] += 1
        if sd < -0.0005: c_[0] += 1
        if i in interno: gaps.append(sd)
    gaps.sort()
    g = ("interna med %.1f mm p10 %.1f mm p90 %.1f mm" % (gaps[len(gaps) // 2] * 1000, gaps[len(gaps) // 10] * 1000, gaps[int(len(gaps) * 0.9)] * 1000)) if gaps else "sem _interno"
    print("QA %-14s %s | dentro: %s" % (item, g, ", ".join("%s %.1f%%" % (k, 100 * c_[0] / c_[1]) for k, c_ in sorted(por.items()))))
print("QA_OK  (1 mm aqui = 0,0175 stud; 3 mm = ~0,05 stud)")
