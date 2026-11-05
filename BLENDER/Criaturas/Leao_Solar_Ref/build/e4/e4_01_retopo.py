"""E4 passo 1: superficie nova do corpo (boca fechada) a partir da E3_t2 (mesma malha da E3b antes da boca).
1) remesh por voxel (reconstroi uma casca fechada: some com as fendas e os pontos nao-manifold da juba);
2) reducao ate a meta por um de dois caminhos: Quadriflow (quads regulares) ou Decimate com peso por regiao
   (rosto/boca, patas e tufo guardam mais detalhe). Mede a distancia HIGH->LOW.
Uso: blender -b Leao_Solar_Ref_E3_t2.blend -P e4_01_retopo.py -- <saida.blend> <voxel> <metodo quadriflow|decimate> <tris>"""
import bpy, bmesh, sys, time
import numpy as np
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]; OUT, VOX, MET, TRIS = A[0], float(A[1]), A[2], int(A[3]); TRIS1 = int(A[4]) if len(A) > 4 else 60000
t0 = time.time(); sc = bpy.context.scene
hi = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E")][0]
lo = hi.copy(); lo.data = hi.data.copy(); lo.name = "Leao_Solar_E4"; sc.collection.objects.link(lo)
for o in sc.objects: o.select_set(False)
bpy.context.view_layer.objects.active = lo; lo.select_set(True)
rm = lo.modifiers.new("Voxel", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = VOX; rm.adaptivity = 0.0; rm.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=rm.name)
print("VOXEL", VOX, "faces", len(lo.data.polygons), round(time.time() - t0, 1), "s", flush=True)
# so a maior casca (descarta ilhas soltas minusculas do voxel)
bm = bmesh.new(); bm.from_mesh(lo.data); bm.verts.ensure_lookup_table()
vis = set(); ilhas = []
for v in bm.verts:
    if v in vis: continue
    pilha = [v]; vis.add(v); comp = []
    while pilha:
        x = pilha.pop(); comp.append(x)
        for e in x.link_edges:
            y = e.other_vert(x)
            if y not in vis: vis.add(y); pilha.append(y)
    ilhas.append(comp)
ilhas.sort(key=len, reverse=True)
print("ILHAS", len(ilhas), [len(i) for i in ilhas[:6]])
fora = [v for i in ilhas[1:] for v in i if len(i) < 200]
bmesh.ops.delete(bm, geom=fora, context="VERTS"); bm.to_mesh(lo.data); bm.free()
co = np.array([v.co for v in lo.data.vertices])
if MET == "quadriflow":
    pre = lo.modifiers.new("Pre", "DECIMATE"); pre.ratio = min(1.0, 200000 / max(len(lo.data.polygons), 1)); bpy.ops.object.modifier_apply(modifier=pre.name)
    r = bpy.ops.object.quadriflow_remesh(target_faces=TRIS // 2, use_preserve_sharp=False, use_preserve_boundary=False, use_mesh_symmetry=False, smooth_normals=False, seed=0)
    print("QUADRIFLOW", r)
else:
    # 1a passada: reducao uniforme ate TRIS1 (densidade que o rosto precisa); 2a: rosto/boca protegidos (grupo com
    # inversao = preservado) e o resto reduzido ate a meta. (Peso graduado no Decimate age quase como liga/desliga.)
    def s(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
    def reduzir(alvo, grupo=None):
        for _ in range(4):
            tri = sum(len(p.vertices) - 2 for p in lo.data.polygons)
            if tri <= alvo * 1.01: return
            dc = lo.modifiers.new("Reduz", "DECIMATE"); dc.ratio = alvo / tri; dc.use_collapse_triangulate = True
            if grupo: dc.vertex_group = grupo; dc.invert_vertex_group = True; dc.vertex_group_factor = 1.0
            bpy.ops.object.modifier_apply(modifier=dc.name)
    reduzir(TRIS1)
    co = np.array([v.co for v in lo.data.vertices]); x, y, z = co[:, 0], co[:, 1], co[:, 2]
    rosto = (y < -12.9) & (z > 10.9) & (np.abs(x + 0.23) < 1.7)
    g = lo.vertex_groups.new(name="detalhe"); g.add([int(i) for i in np.nonzero(rosto)[0]], 1.0, "REPLACE")
    reduzir(TRIS, "detalhe")
tri = sum(len(p.vertices) - 2 for p in lo.data.polygons)
for p in lo.data.polygons: p.use_smooth = True
def regiao(c):
    if c.y < -12.8 and c.z > 10.9 and abs(c.x + 0.23) < 1.7: return "rosto"
    if c.y > 9.0: return "cauda/tufo"
    if c.z < 1.5: return "patas"
    return "juba/corpo"
cont = {}
for p_ in lo.data.polygons: k = regiao(p_.center); cont[k] = cont.get(k, 0) + len(p_.vertices) - 2
print("TRIS por regiao", cont)
# distancia HIGH -> LOW (amostras dos vertices da HIGH)
lo.data.calc_loop_triangles()
bv = BVHTree.FromPolygons([v.co for v in lo.data.vertices], [list(t.vertices) for t in lo.data.loop_triangles])
hv = hi.data.vertices; idx = np.random.default_rng(0).choice(len(hv), 20000, replace=False)
d = np.array([bv.find_nearest(hv[int(i)].co)[3] for i in idx])
print("LOW", MET, "tris", tri, "verts", len(lo.data.vertices), "dist HIGH->LOW media/p95/max", round(d.mean(), 4), round(np.percentile(d, 95), 4), round(d.max(), 4), round(time.time() - t0, 1), "s")
bpy.data.objects.remove(hi, do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("RETOPO_OK")
