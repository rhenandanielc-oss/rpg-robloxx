"""E3 passo 1 (copia da E2 v11; a v11 nao e alterada): solda as costuras de UV (a UV continua nos loops), fecha os lacos
pequenos de bordas abertas por fusao no centro (fendas/agulhas do remesh do Meshy, perimetro < 0,8 stud), remove faces
duplicadas e degeneradas e refaz as normais. Lacos maiores ficam e sao listados.
Uso: blender -b Leao_Solar_Ref_E2_v11.blend -P e3_01_topologia.py -- <saida.blend>"""
import bpy, bmesh, sys
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]
ob = bpy.data.objects["Leao_Solar_E2"]; me = ob.data
bm = bmesh.new(); bm.from_mesh(me)
v0 = len(bm.verts); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
def lacos_abertos():
    bm.edges.ensure_lookup_table(); vistos = set(); out = []
    for e in bm.edges:
        if not e.is_boundary or e.index in vistos: continue
        pilha = [e]; vistos.add(e.index); laco = []
        while pilha:
            a = pilha.pop(); laco.append(a)
            for v in a.verts:
                for b in v.link_edges:
                    if b.is_boundary and b.index not in vistos: vistos.add(b.index); pilha.append(b)
        out.append(laco)
    return out
fechados = 0; ficaram = []
for it in range(3):
    for laco in lacos_abertos():
        if not all(e.is_valid for e in laco): continue
        per = sum(e.calc_length() for e in laco)
        vs = list({v for e in laco for v in e.verts})
        if per < 0.8 and len(vs) <= 12:
            c = sum((v.co for v in vs), Vector()) / len(vs)
            bmesh.ops.pointmerge(bm, verts=vs, merge_co=c); fechados += 1
        elif it == 2: ficaram.append((len(laco), round(per, 3)))
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-5)
# faces duplicadas (mesmo conjunto de vertices)
vistas = {}; dup = []
for f in bm.faces:
    k = frozenset(v.index for v in f.verts)
    if k in vistas: dup.append(f)
    else: vistas[k] = f
bmesh.ops.delete(bm, geom=dup, context="FACES_ONLY")
soltos = [v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm, geom=soltos, context="VERTS")
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me); me.update(); bm.free()
ob.name = "Leao_Solar_E3"; me.name = "Leao_Solar_E3"
print("TOPO_OK verts", v0, "->", len(me.vertices), "lacos_fechados", fechados, "duplicadas", len(dup), "ficaram", ficaram[:10])
bpy.ops.wm.save_as_mainfile(filepath=A[0])
