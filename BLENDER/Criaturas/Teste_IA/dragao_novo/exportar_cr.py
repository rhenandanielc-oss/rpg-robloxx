"""Exporta o CR_Dragao para o Roblox: corpo, asas (membranas) e detalhes (olhos/boca) como malhas separadas
(cada MeshPart <= 20k tris), esqueleto do Silverwing, texturas reduzidas a 1024 (limite do Roblox). Sem animacoes no
GLB: os clipes vao pela ponte JSON (exportar_clipes_json.py + montar_kfs_json.luau).
Uso: blender -b CR_Dragao_M2M.blend -P exportar_cr.py -- <saida.glb>"""
import bpy, bmesh, sys, os
SAIDA = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
A = bpy.data.objects["Silverwing_Rig"]; corpo = bpy.data.objects["Silverwing"]; det = bpy.data.objects["Silverwing_Detalhes"]
if A.animation_data:
    A.animation_data.action = None
    for t in list(A.animation_data.nla_tracks): A.animation_data.nla_tracks.remove(t)
for pb in A.pose.bones: pb.matrix_basis.identity()
# membranas -> malha propria (pecas soltas largas em X)
bpy.ops.object.select_all(action="DESELECT"); corpo.select_set(True); bpy.context.view_layer.objects.active = corpo
bm = bmesh.new(); bm.from_mesh(corpo.data); bm.verts.ensure_lookup_table()
vis, memb = set(), []
for v in bm.verts:
    if v.index in vis: continue
    pilha, ilha = [v], []
    while pilha:
        x = pilha.pop()
        if x.index in vis: continue
        vis.add(x.index); ilha.append(x)
        for e in x.link_edges: pilha.append(e.other_vert(x))
    xs = [abs(x.co.x) for x in ilha]
    if max(xs) - min(xs) > 0.25 and len(ilha) < 3000: memb += ilha
for v in bm.verts: v.select = False
for v in memb: v.select = True
bm.select_flush(True); bm.to_mesh(corpo.data); bm.free()
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.separate(type="SELECTED"); bpy.ops.object.mode_set(mode="OBJECT")
asas = [o for o in bpy.context.selected_objects if o is not corpo][0]; asas.name = "Silverwing_Asas"
corpo.name = "Silverwing_Corpo"
for o in (corpo, asas, det):
    print("EXPORT", o.name, "tris", sum(len(p.vertices) - 2 for p in o.data.polygons))
    assert sum(len(p.vertices) - 2 for p in o.data.polygons) <= 20000, o.name + " passa de 20k tris"
# texturas 1024
for im in bpy.data.images:
    if im.size[0] > 1024: im.scale(1024, 1024); print("TEX", im.name, "-> 1024")
bpy.ops.object.select_all(action="DESELECT")
for o in (A, corpo, asas, det): o.select_set(True)
bpy.context.view_layer.objects.active = A
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format="GLB", use_selection=True, export_animations=False,
                          export_image_format="AUTO", export_skins=True)
print("EXPORT_OK", round(os.path.getsize(SAIDA) / 1e6, 1), "MB")
