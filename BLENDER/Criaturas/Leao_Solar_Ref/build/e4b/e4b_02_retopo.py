"""E4b passo 2: superficie de jogo preparada para deformar (boca fechada; a boca vem depois, com o e4_03).
1) remesh por voxel 0,04 (casca nova, como na E4);
2) reducao em 3 passadas: uniforme ate T1; rosto protegido ate T2; rosto + ZONAS DE ARTICULACAO (esferas nas juntas de
   juntas.json: ombros, cotovelos, punhos, quadris, joelhos, jarretes, base da cauda, base do pescoco) protegidos ate a meta;
3) LACOS de articulacao: em cotovelos, punhos, joelhos, jarretes e base da cauda, 3 aneis de arestas perpendiculares a
   bissetriz dos dois ossos (cortes planos so dentro do cilindro da pata), triangulados.
Uso: blender -b Leao_Solar_Ref_E3_t2.blend -P e4b_02_retopo.py -- <juntas.json> <saida.blend> <meta_tris> [T1=60000] [T2=36000] [nome]"""
import bpy, bmesh, sys, json, time
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]
J = json.load(open(A[0])); OUT = A[1]; TRIS = int(A[2]); T1 = int(A[3]) if len(A) > 3 else 60000; T2 = int(A[4]) if len(A) > 4 else 36000
NOME = A[5] if len(A) > 5 else "Leao_Solar_E4b"
t0 = time.time(); sc = bpy.context.scene
hi = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E")][0]
lo = hi.copy(); lo.data = hi.data.copy(); lo.name = NOME; sc.collection.objects.link(lo)
for o in sc.objects: o.select_set(False)
bpy.context.view_layer.objects.active = lo; lo.select_set(True)
rm = lo.modifiers.new("Voxel", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.04; rm.adaptivity = 0.0
bpy.ops.object.modifier_apply(modifier=rm.name)
bm = bmesh.new(); bm.from_mesh(lo.data); bm.verts.ensure_lookup_table(); vis = set(); ilhas = []
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
bmesh.ops.delete(bm, geom=[v for i in ilhas[1:] for v in i], context="VERTS"); bm.to_mesh(lo.data); bm.free()
print("VOXEL faces", len(lo.data.polygons), "ilhas descartadas", len(ilhas) - 1)
def ntri(): return sum(len(p.vertices) - 2 for p in lo.data.polygons)
def reduzir(alvo, grupo=None):
    for _ in range(4):
        tri = ntri()
        if tri <= alvo * 1.01: return
        dc = lo.modifiers.new("Reduz", "DECIMATE"); dc.ratio = alvo / tri; dc.use_collapse_triangulate = True
        if grupo: dc.vertex_group = grupo; dc.invert_vertex_group = True; dc.vertex_group_factor = 1.0
        bpy.ops.object.modifier_apply(modifier=dc.name)
def V(p): return np.array(p, float)
ZONAS = []                                                    # (centro, raio)
for perna in ("DD", "DE"):
    for n, r in (("ombro", 1.3), ("cotovelo", 1.1), ("punho", 0.8)): ZONAS.append((V(J[perna][n]), r))
for perna in ("TD", "TE"):
    for n, r in (("quadril", 1.3), ("joelho", 1.1), ("jarrete", 0.9)): ZONAS.append((V(J[perna][n]), r))
ZONAS.append((V(J["cauda"][0]), 1.0)); ZONAS.append((V(J["cauda"][1]), 0.8)); ZONAS.append((V(J["pescoco"][1]), 1.2))
def grupo_mascara(nome, mascara):
    if nome in lo.vertex_groups: lo.vertex_groups.remove(lo.vertex_groups[nome])
    g = lo.vertex_groups.new(name=nome); g.add([int(i) for i in np.nonzero(mascara)[0]], 1.0, "REPLACE")
def mascaras():
    co = np.array([v.co for v in lo.data.vertices]); x, y, z = co[:, 0], co[:, 1], co[:, 2]
    rosto = (y < -12.9) & (z > 10.9) & (np.abs(x + 0.23) < 1.7)
    junta = np.zeros(len(co), bool)
    for c, r in ZONAS: junta |= np.linalg.norm(co - c, axis=1) < r
    return rosto, junta
reduzir(T1)
rosto, junta = mascaras(); grupo_mascara("detalhe", rosto); reduzir(T2, "detalhe")
rosto, junta = mascaras(); grupo_mascara("detalhe", rosto | junta); reduzir(TRIS, "detalhe")
print("REDUCAO tris", ntri(), round(time.time() - t0, 1), "s")
# ---------------------------------------------------------------- lacos de articulacao (aneis por corte plano)
def unit(v): v = np.asarray(v, float); return v / max(np.linalg.norm(v), 1e-9)
LACOS = []
for perna, cad in (("DD", ("ombro", "cotovelo", "punho", "pata")), ("DE", ("ombro", "cotovelo", "punho", "pata")),
                   ("TD", ("quadril", "joelho", "jarrete", "pata")), ("TE", ("quadril", "joelho", "jarrete", "pata"))):
    for i in (1, 2):
        a, j, b = V(J[perna][cad[i - 1]]), V(J[perna][cad[i]]), V(J[perna][cad[i + 1]])
        eixo = unit(unit(j - a) + unit(b - j))               # normal do plano = bissetriz da junta
        raio = 1.15 if i == 1 else 0.85
        LACOS.append((perna + "_" + cad[i], j, eixo, raio))
ca = [V(p) for p in J["cauda"]]
LACOS.append(("cauda_base", ca[1], unit(ca[2] - ca[0]), 0.75))
bm = bmesh.new(); bm.from_mesh(lo.data); antes = len(bm.faces); rel = {}
for nome, j, eixo, raio in LACOS:
    for off in (-0.28, 0.0, 0.28):
        co_ = j + eixo * off
        bm.faces.ensure_lookup_table()
        reg = []
        for f in bm.faces:
            c = np.array(f.calc_center_median()); d = c - co_; ax = d @ eixo
            if abs(ax) < 0.25 and np.linalg.norm(d - ax * eixo) < raio: reg.append(f)
        if not reg: continue
        geom = list({v for f in reg for v in f.verts}) + list({e for f in reg for e in f.edges}) + reg
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=Vector(co_), plane_no=Vector(eixo), dist=0.02)
    rel[nome] = None
ng = [f for f in bm.faces if len(f.verts) > 3]
bmesh.ops.triangulate(bm, faces=ng, quad_method="BEAUTY", ngon_method="BEAUTY")
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
bm.to_mesh(lo.data); bm.free()
for p in lo.data.polygons: p.use_smooth = True
print("LACOS", len(LACOS), "articulacoes x 3 aneis; tris", ntri(), "(+%d)" % (ntri() - antes))
# contagem por regiao
co = np.array([v.co for v in lo.data.vertices])
def regiao(c):
    if c.y < -12.9 and c.z > 10.9 and abs(c.x + 0.23) < 1.7: return "rosto"
    for cc, r in ZONAS:
        if np.linalg.norm(np.array(c) - cc) < r: return "articulacoes"
    if c.y > 9.0 and c.z < 7: return "cauda/tufo"
    if c.z < 1.5: return "patas"
    return "juba/corpo"
cont = {}
for p_ in lo.data.polygons: k = regiao(p_.center); cont[k] = cont.get(k, 0) + len(p_.vertices) - 2
lo.data.calc_loop_triangles()
bv = BVHTree.FromPolygons([v.co for v in lo.data.vertices], [list(t.vertices) for t in lo.data.loop_triangles])
hv = hi.data.vertices; idx = np.random.default_rng(0).choice(len(hv), 20000, replace=False)
d = np.array([bv.find_nearest(hv[int(i)].co)[3] for i in idx])
print("E4B tris", ntri(), "por regiao", cont, "dist media/p95/max", round(d.mean(), 4), round(np.percentile(d, 95), 4), round(d.max(), 4))
bpy.data.objects.remove(hi, do_unlink=True)
for g in list(lo.vertex_groups): lo.vertex_groups.remove(g)
bpy.ops.wm.save_as_mainfile(filepath=OUT); print("RETOPO_E4B_OK")
