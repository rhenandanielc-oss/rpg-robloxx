"""Exporta o Dragao Glacial rigado para o Roblox (derivado de dragao_novo/exportar_cr.py): corpo, asas (membranas) e
detalhes (chifres, espinhos, garras, dentes, olhos, boca) como malhas separadas, cada MeshPart <= 20k tris; esqueleto
do Silverwing com os nomes do jogo (o Roblox liga malha e osso PELO NOME); texturas <= 1024; sem animacoes no GLB (os
clipes vao pela ponte JSON). NAO mexe no Studio: a importacao 3D e o passo manual do usuario.
Uso: blender -b GL_Dragao_M2M.blend -P exportar_glacial.py -- <saida.glb>"""
import bpy, bmesh, sys, os
SAIDA = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
A = bpy.data.objects["Silverwing_Rig"]; corpo = bpy.data.objects["Silverwing"]
if A.animation_data:
    A.animation_data.action = None
    for t in list(A.animation_data.nla_tracks): A.animation_data.nla_tracks.remove(t)
for pb in A.pose.bones: pb.matrix_basis.identity()
def ilhas(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); vis, out = set(), []
    for v in bm.verts:
        if v.index in vis: continue
        pilha, ilha = [v], []
        while pilha:
            x = pilha.pop()
            if x.index in vis: continue
            vis.add(x.index); ilha.append(x.index)
            for e in x.link_edges: pilha.append(e.other_vert(x))
        out.append(ilha)
    xs = {i: abs(bm.verts[i].co.x) for i in range(len(bm.verts))}; bm.free(); return out, xs
def separar(o, idx, nome):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    for v in bm.verts: v.select = v.index in idx
    bm.select_flush(True); bm.to_mesh(o.data); bm.free()
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.separate(type="SELECTED"); bpy.ops.object.mode_set(mode="OBJECT")
    novo = [x for x in bpy.context.selected_objects if x is not o][0]; novo.name = nome; return novo
grupos, xs = ilhas(corpo)
grupos.sort(key=len, reverse=True)
memb = [i for g in grupos[1:] if max(xs[i] for i in g) - min(xs[i] for i in g) > 0.25 and len(g) < 3000 for i in g]
asas = separar(corpo, set(memb), "Silverwing_Asas")
grupos, xs = ilhas(corpo); grupos.sort(key=len, reverse=True)
detalhes = separar(corpo, set(i for g in grupos[1:] for i in g), "Silverwing_Detalhes")
corpo.name = "Silverwing_Corpo"
MAPA = {"head": "Cabeca", "hips": "Quadril", "spine_1": "Coluna2", "mouth_lower": "Mandibula", "spine_4": "Pescoco4",
        "spine_2": "Pescoco2", "tail_3": "Cauda3", "wing_2_l": "AsaE_2", "wing_2_r": "AsaD_2"}
bpy.ops.object.select_all(action="DESELECT"); A.select_set(True); bpy.context.view_layer.objects.active = A
bpy.ops.object.mode_set(mode="EDIT")
for s in ("l", "r"): A.data.edit_bones["horn_base_" + s].parent = A.data.edit_bones["head"]
bpy.ops.object.mode_set(mode="OBJECT")
malhas = (corpo, asas, detalhes)
def usados():
    u = set()
    for o in malhas:
        nomes = {g.index: g.name for g in o.vertex_groups}
        for v in o.data.vertices:
            for g in v.groups:
                if g.weight > 0.001: u.add(nomes[g.group])
    return u
u = usados()
for bn in A.data.bones:                                       # ossos sem peso somem na importacao
    if bn.name in u or bn.name in ("root", "DRV_root"): continue
    alvo = A.matrix_world @ ((bn.head_local + bn.tail_local) / 2)
    o, v = min(((o, v) for o in malhas for v in o.data.vertices), key=lambda ov: ((ov[0].matrix_world @ ov[1].co) - alvo).length)
    for g in o.vertex_groups: g.remove([v.index])
    (o.vertex_groups.get(bn.name) or o.vertex_groups.new(name=bn.name)).add([v.index], 1.0, "REPLACE")
    print("OSSO_GARANTIDO", bn.name, "->", o.name)
for velho, novo in MAPA.items():
    A.data.bones[velho].name = novo
    for o in malhas:
        g = o.vertex_groups.get(velho)
        if g: g.name = novo
for o in malhas:
    n = sum(len(p.vertices) - 2 for p in o.data.polygons); print("EXPORT", o.name, "tris", n)
    assert n <= 20000, o.name + " passa de 20k tris"
for im in bpy.data.images:
    if im.size[0] > 1024: im.scale(1024, 1024); print("TEX", im.name, "-> 1024")
bpy.ops.object.select_all(action="DESELECT")
for o in (A,) + malhas: o.select_set(True)
bpy.context.view_layer.objects.active = A
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format="GLB", use_selection=True, export_animations=False,
                          export_image_format="AUTO", export_skins=True)
print("EXPORT_OK", round(os.path.getsize(SAIDA) / 1e6, 1), "MB")
