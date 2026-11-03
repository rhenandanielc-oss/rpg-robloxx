"""Exporta o Urso Silvestre v2 com rig para o Roblox: 4 MeshParts skinned (<= 20k tris), esqueleto com nomes do jogo,
texturas <= 1024, SEM animacoes (os clipes vem na etapa seguinte). Ossos sem peso somem na importacao do Roblox:
cada osso sem peso recebe um triangulo degenerado (invisivel) na sua cabeca, com 100% de peso.
Depois reimporta o GLB numa cena vazia e confere ossos, nomes, malhas, tris, grupos, influencias e texturas.
Uso: blender -b CR_Urso_v2_Rig.blend -P exportar_urso.py -- <saida.glb>"""
import bpy, bmesh, sys, os
SAIDA = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Urso_Rig"]
MALHAS = [bpy.data.objects[n] for n in ("Urso_Cabeca", "Urso_Corpo_Frente", "Urso_Corpo_Tras", "Urso_Boca")]
for pb in A.pose.bones:
    for c in list(pb.constraints): pb.constraints.remove(c)
    pb.matrix_basis.identity()
if A.animation_data: A.animation_data.action = None
usados = set()
for o in MALHAS:
    nomes = {g.index: g.name for g in o.vertex_groups}
    for v in o.data.vertices:
        for g in v.groups:
            if g.weight > 0.001: usados.add(nomes[g.group])
alvo = bpy.data.objects["Urso_Corpo_Tras"]
for bn in A.data.bones:
    if bn.name in usados: continue
    me = alvo.data; bm = bmesh.new(); bm.from_mesh(me)
    p = bn.head_local; vs = [bm.verts.new(p) for _ in range(3)]; bm.faces.new(vs)
    bm.to_mesh(me); bm.free()
    g = alvo.vertex_groups.get(bn.name) or alvo.vertex_groups.new(name=bn.name)
    ids = list(range(len(me.vertices) - 3, len(me.vertices)))
    for og in alvo.vertex_groups:
        if og is not g: og.remove(ids)
    g.add(ids, 1.0, "REPLACE"); print("OSSO_GARANTIDO", bn.name, "(triangulo degenerado)")
for o in MALHAS:
    t = sum(len(p.vertices) - 2 for p in o.data.polygons); assert t <= 20000, (o.name, t)
for im in list(bpy.data.images):
    if im.name.startswith("Image_"): bpy.data.images.remove(im); continue      # texturas 4K da malha bruta (fonte do bake), sem uso
    if im.size[0] > 1024: im.scale(1024, 1024); print("TEX", im.name, "-> 1024")
bpy.ops.object.select_all(action="DESELECT")
for o in [A] + MALHAS: o.select_set(True)
bpy.context.view_layer.objects.active = A
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format="GLB", use_selection=True, export_animations=False, export_yup=True,
                          export_image_format="AUTO", export_skins=True, export_all_influences=False, export_materials="EXPORT")
print("EXPORT_OK", SAIDA, round(os.path.getsize(SAIDA) / 1e6, 2), "MB ossos", len(A.data.bones))
# ---- conferencia por reimportacao
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=SAIDA)
arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]; mal = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.vertex_groups]   # sem a Icosphere que o importador cria para exibir ossos
a = arms[0]; ossos = [b.name for b in a.data.bones]
grupos = set()
for m in mal: grupos |= {g.name for g in m.vertex_groups}
sem = [b for b in ossos if b not in grupos]
print("REIMPORT ossos", len(ossos), "sem_grupo", sem)
for m in mal:
    mi = max(len([g for g in v.groups if g.weight > 0.001]) for v in m.data.vertices)
    imgs = sorted({n.image.name + " %dx%d" % tuple(n.image.size) for mt in m.data.materials if mt and mt.node_tree for n in mt.node_tree.nodes if n.type == "TEX_IMAGE" and n.image})
    print("REIMPORT malha %-18s tris %6d grupos %2d max_influencias %d modificador_armature %s imagens %s" % (
        m.name, sum(len(p.vertices) - 2 for p in m.data.polygons), len(m.vertex_groups), mi,
        any(md.type == "ARMATURE" for md in m.modifiers), imgs))
pts = [m.matrix_world @ v.co for m in mal for v in m.data.vertices]
print("REIMPORT caixa z %.2f..%.2f y %.2f..%.2f" % (min(p.z for p in pts), max(p.z for p in pts), min(p.y for p in pts), max(p.y for p in pts)))
print("VALIDO" if not sem and all(sum(len(p.vertices) - 2 for p in m.data.polygons) <= 20000 for m in mal) else "FALHOU")
