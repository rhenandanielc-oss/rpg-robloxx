"""Malha leve v2 a partir do ORIGINAL (intocado): solda as costuras de UV ANTES de reduzir (na v1 a decimacao moveu
cada lado da costura sozinho -> 771 pedacos e buracos), normais para fora, decimacao para ~alvo triangulos, sem faces
degeneradas, pes no chao. Relata ilhas, bordas abertas e normais. Uso: blender -b -P reduzir_meshy_v2.py -- orig.glb saida.glb alvo"""
import bpy, sys, os, bmesh
from collections import deque
a = sys.argv[sys.argv.index("--") + 1:]; glb, saida, alvo = a[0], a[1], int(a[2])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
o = [x for x in bpy.data.objects if x.type == "MESH"][0]
bpy.context.view_layer.objects.active = o; o.select_set(True)
def relatorio(tag):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    vis = [False] * len(bm.verts); ilhas = 0; tam = []
    for v in bm.verts:
        if vis[v.index]: continue
        ilhas += 1; q = deque([v]); vis[v.index] = True; c = 0
        while q:
            x = q.popleft(); c += 1
            for e in x.link_edges:
                y = e.other_vert(x)
                if not vis[y.index]: vis[y.index] = True; q.append(y)
        tam.append(c)
    tam.sort(reverse=True)
    print(tag, "verts", len(bm.verts), "tris", sum(len(f.verts) - 2 for f in bm.faces), "ilhas", ilhas, "maiores", tam[:6],
          "bordas", sum(1 for e in bm.edges if e.is_boundary), "nao_manifold", sum(1 for e in bm.edges if len(e.link_faces) > 2))
    bm.free()
bm = bmesh.new(); bm.from_mesh(o.data)
r = bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-5)
bm.to_mesh(o.data); bm.free(); o.data.update()
relatorio("SOLDADO_1M")
# remove fragmentos minusculos (poeira solta do gerador, < 40 vertices)
bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
vis = [False] * len(bm.verts); lixo = []
for v in bm.verts:
    if vis[v.index]: continue
    q = deque([v]); vis[v.index] = True; comp = []
    while q:
        x = q.popleft(); comp.append(x)
        for e in x.link_edges:
            y = e.other_vert(x)
            if not vis[y.index]: vis[y.index] = True; q.append(y)
    if len(comp) < 40: lixo += comp
bmesh.ops.delete(bm, geom=lixo, context="VERTS"); print("FRAGMENTOS_REMOVIDOS verts", len(lixo))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(o.data); bm.free(); o.data.update()
n0 = len(o.data.polygons)
m = o.modifiers.new("dec", "DECIMATE"); m.ratio = alvo / n0; m.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier="dec")
bm = bmesh.new(); bm.from_mesh(o.data)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(o.data); bm.free(); o.data.update()
zs = min(v.co.z for v in o.data.vertices); xs = [v.co.x for v in o.data.vertices]; ys = [v.co.y for v in o.data.vertices]
from mathutils import Matrix
o.data.transform(Matrix.Translation((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -zs)))
relatorio("REDUZIDO")
for im in bpy.data.images:
    if im.size[0] > 2048: im.scale(2048, 2048)
bpy.ops.export_scene.gltf(filepath=saida, export_format="GLB", use_selection=True, export_image_format="JPEG")
print("TAM_MB", round(os.path.getsize(saida) / 1e6, 2)); print("REDUZIR_V2_OK")
