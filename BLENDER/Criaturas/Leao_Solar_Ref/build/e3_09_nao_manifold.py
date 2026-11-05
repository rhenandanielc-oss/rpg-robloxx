"""Localiza arestas nao-manifold (>2 faces) e vertices nao-manifold por regiao/material (le, nao salva).
Uso: blender -b <arquivo.blend> -P e3_09_nao_manifold.py"""
import bpy, bmesh
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E")][0]
bm = bmesh.new(); bm.from_mesh(ob.data)
def reg(c, mats):
    if 1 in mats: return "boca(interior/comissuras)"
    if c.y < -12.6 and 10.8 < c.z < 16.8 and abs(c.x) < 2.2: return "rosto"
    return "juba/corpo"
ae, vv = {}, {}
for e in bm.edges:
    if len(e.link_faces) > 2:
        r = reg((e.verts[0].co + e.verts[1].co) / 2, {f.material_index for f in e.link_faces}); ae[r] = ae.get(r, 0) + 1
for v in bm.verts:
    if not v.is_manifold and not v.is_boundary:
        r = reg(v.co, {f.material_index for f in v.link_faces}); vv[r] = vv.get(r, 0) + 1
print("NM arestas", ae, "verts", vv)
