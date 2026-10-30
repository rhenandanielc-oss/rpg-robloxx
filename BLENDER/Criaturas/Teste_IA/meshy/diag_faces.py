"""Diagnostico 'como o Roblox ve' (faces de um lado so): normais invertidas por regiao, faces degeneradas/finas,
lascas (faces com cantos de ossos muito diferentes que esticam), e render Workbench COM backface culling.
Uso: blender -b arq.blend -P diag_faces.py -- saida_dir [Clipe:quadro ...]"""
import bpy, sys, os, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import Counter
args = sys.argv[sys.argv.index("--") + 1:]; out = args[0]; quadros = [a.split(":") for a in args[1:]]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]; me = M.data
gi = {g.index: g.name for g in M.vertex_groups}
def dom(v): return gi[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "-"
def reg(n):
    if n.startswith(("wing_", "shoulder_")): return "asa"
    if n.startswith("tail"): return "cauda"
    if n.startswith(("front_", "back_", "collar", "hips_anchor")): return "pata"
    return "corpo"
D = [dom(v) for v in me.vertices]
# 1) normais: para cada face, raio a partir do centro ao longo da normal; se a primeira coisa atingida 'de dentro'
#    mostra que a face aponta para dentro do volume (paridade de cruzamentos), conta como invertida
bvh = BVHTree.FromObject(M, bpy.context.evaluated_depsgraph_get()) if False else None
verts = [v.co.copy() for v in me.vertices]; polys = [tuple(p.vertices) for p in me.polygons]
bvh = BVHTree.FromPolygons(verts, polys)
inv = Counter(); tot = Counter()
for p in me.polygons:
    c = p.center + p.normal * 1e-4; d = p.normal.copy()
    n_hits = 0; o = c
    for _ in range(12):
        h = bvh.ray_cast(o, d, 5.0)
        if h[0] is None: break
        n_hits += 1; o = h[0] + d * 1e-4
    r = reg(D[p.vertices[0]]); tot[r] += 1
    if n_hits % 2 == 1: inv[r] += 1
print("NORMAIS_PARA_DENTRO (paridade impar)", {k: "%d/%d" % (inv[k], tot[k]) for k in tot})
# 2) faces finas/degeneradas no repouso
fin = Counter()
for p in me.polygons:
    if p.area < 1e-8: fin["degenerada"] += 1
    else:
        ls = [(verts[p.vertices[i]] - verts[p.vertices[(i + 1) % len(p.vertices)]]).length for i in range(len(p.vertices))]
        if max(ls) / max(min(ls), 1e-9) > 25: fin[reg(D[p.vertices[0]])] += 1
print("FACES_FINAS_REPOUSO", dict(fin))
# 3) normais vizinhas opostas (costura com orientacao trocada)
bm = bmesh.new(); bm.from_mesh(me)
opostas = Counter()
for e in bm.edges:
    if len(e.link_faces) == 2:
        f1, f2 = e.link_faces
        # aresta percorrida no mesmo sentido pelas duas faces = orientacao inconsistente
        def sentido(f):
            vs = [v.index for v in f.verts]; a, b = e.verts[0].index, e.verts[1].index; i = vs.index(a)
            return vs[(i + 1) % len(vs)] == b
        if sentido(f1) == sentido(f2): opostas[reg(D[e.verts[0].index])] += 1
    if len(e.link_faces) > 2: opostas["nao_manifold"] += 1
print("ARESTAS_ORIENTACAO_INCONSISTENTE", dict(opostas)); bm.free()
# 4) renders com backface culling (o que o Roblox mostra)
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading
sh.light = "STUDIO"; sh.color_type = "TEXTURE"; sh.show_backface_culling = True
sc.render.resolution_x, sc.render.resolution_y = 560, 420
cam = bpy.data.objects.get("cam_rev") or bpy.data.objects.new("cam_rev", bpy.data.cameras.new("cam_rev"))
if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
sc.camera = cam
for o in bpy.data.objects:
    if o.name.startswith("chao"): o.hide_render = True
for nome, q in (quadros or [("repouso", "1")]):
    if nome == "repouso":
        A.animation_data.action = None
        for pb in A.pose.bones: pb.matrix_basis.identity()
    else:
        act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    sc.frame_set(int(q))
    for vista, c, d, r in (("cauda_topo", Vector((0, 0.45, 0.35)), (0, 0.15, 1), 1.1), ("cauda_lado", Vector((0, 0.45, 0.35)), (1, 0, 0.1), 1.1),
                           ("dorso", Vector((-0.02, -0.1, 0.45)), (0.4, 0.8, 0.6), 0.7), ("asa_baixo", Vector((0.2, -0.1, 0.4)), (0.3, -0.2, -1), 1.3),
                           ("frente", Vector((-0.02, -0.2, 0.35)), (0.3, -1, 0.3), 1.2), ("tras", Vector((-0.02, 0.1, 0.35)), (0.2, 1, 0.4), 1.4)):
        cam.location = c + Vector(d).normalized() * r; cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, "cull_%s_%s.png" % (nome, vista)); bpy.ops.render.render(write_still=True)
print("DIAG_FACES_OK")
