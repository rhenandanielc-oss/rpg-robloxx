"""Exporta o Crocodilo Primordial para o Roblox: 1 malha (<= 20k tris) + esqueleto com os nomes do jogo, texturas 1024,
sem animacoes no GLB (os clipes vao pelos JSON de clipes/ + montar_kfs_json.luau, como os dragoes). Remove IK/alvos.
Ossos sem peso somem na importacao do Roblox: cada um recebe 1 vertice proximo (100%).
Depois reimporta o GLB numa cena vazia e confere ossos, nomes, tris, pesos e texturas.
Uso: blender -b CR_Crocodilo_Rig.blend -P exportar_croc.py -- <saida.glb>"""
import bpy, sys, os
SAIDA = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["CR_Croc_Rig"]; M = bpy.data.objects["CR_Croc_LOW"]
for pb in A.pose.bones:
    for c in list(pb.constraints): pb.constraints.remove(c)
    pb.matrix_basis.identity()
for o in list(sc.objects):
    if o.type == "EMPTY": bpy.data.objects.remove(o)
if A.animation_data: A.animation_data.action = None
M.name = "Crocodilo_Corpo"; A.name = "Crocodilo_Rig"
nomes = {g.index: g.name for g in M.vertex_groups}; usados = set()
for v in M.data.vertices:
    for g in v.groups:
        if g.weight > 0.001: usados.add(nomes[g.group])
for bn in A.data.bones:
    if bn.name in usados: continue
    alvo = (bn.head_local + bn.tail_local) / 2
    v = min(M.data.vertices, key=lambda v: (v.co - alvo).length)
    # Lote 1: so 2% no osso sem peso, mantendo os outros pesos (100% num vertice causava puxao local quando a Pelve gira)
    (M.vertex_groups.get(bn.name) or M.vertex_groups.new(name=bn.name)).add([v.index], 0.02, "REPLACE")
    tot = sum(g.weight for g in v.groups)
    for g in v.groups: g.weight = g.weight / tot
    print("OSSO_GARANTIDO", bn.name, "vertice", v.index, "peso 2% (outros mantidos)")
tris = sum(len(p.vertices) - 2 for p in M.data.polygons); assert tris <= 20000, tris
for im in bpy.data.images:
    if im.size[0] > 1024: im.scale(1024, 1024); print("TEX", im.name, "-> 1024")
bpy.ops.object.select_all(action="DESELECT"); A.select_set(True); M.select_set(True); bpy.context.view_layer.objects.active = A
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format="GLB", use_selection=True, export_animations=False,
                          export_image_format="AUTO", export_skins=True, export_all_influences=False)
print("EXPORT_OK", SAIDA, round(os.path.getsize(SAIDA) / 1e6, 2), "MB tris", tris, "ossos", len(A.data.bones))
# ---- conferencia por reimportacao
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SAIDA)
arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]; mal = [o for o in bpy.context.scene.objects if o.type == "MESH"]
a = arms[0]; m = mal[0]
grupos = {g.name for g in m.vertex_groups}
sem = [b.name for b in a.data.bones if b.name not in grupos]
max_inf = max(len([g for g in v.groups if g.weight > 0.001]) for v in m.data.vertices)
print("REIMPORT ossos", len(a.data.bones), "malhas", len(mal), "tris", sum(len(p.vertices) - 2 for p in m.data.polygons),
      "ossos_sem_grupo", sem, "max_influencias", max_inf, "imagens", [(i.name, tuple(i.size)) for i in bpy.data.images],
      "dims", tuple(round(d, 2) for d in m.dimensions))
