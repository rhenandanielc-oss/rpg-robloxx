"""Exporta a Wyvern (E6 + sela S1 aprovada) para o Roblox: GLB com a malha do corpo, a sela e o rig de 61 ossos.
- Fonte: Wyvern_E7_clipes_L6.blend (malha = E6). Sela: export/sela/Wyvern_Sela_Jogo.blend (objeto Wyvern_Sela, material
  de jogo 1024 ja assado). Nada dos .blend de origem e salvo.
- Ossos-chave recebem os nomes que os sistemas compartilhados do jogo procuram (montaria/assento, entradas, cavaleiro):
  o Roblox liga malha e osso PELO NOME, por isso a troca acontece aqui e nunca no Studio. Os clipes JSON usam o mesmo
  MAPA (22_exportar_clipes_wyvern.py).
- Sem shape keys (as correctivas fold_* valem 0 no repouso; morph em malha com pele nao serve no jogo), sem animacoes
  (clipes pela ponte JSON), texturas <= 1024, cada malha <= 20k tris.
- Nao mexe no Studio: a importacao 3D e o passo manual do usuario.
Uso: blender -b Wyvern_E7_clipes_L6.blend -P build/21_exportar_wyvern.py -- <saida.glb>"""
import bpy, sys, os
SAIDA = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
AQUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPA = {"pelvis": "Quadril", "spine_02": "Coluna2", "head": "Cabeca", "jaw": "Mandibula", "neck_02": "Pescoco2",
        "neck_04": "Pescoco4", "tail_03": "Cauda3", "tail_10": "tail_tip", "breath_socket": "mouth_upper_tip",
        "shoulder_L": "shoulder_l", "shoulder_R": "shoulder_r", "toe_L": "toes_tip_l", "toe_R": "toes_tip_r"}
A = bpy.data.objects["Wyvern_Rig"]; corpo = bpy.data.objects["Wyvern"]
if A.animation_data:
    A.animation_data.action = None
    for t in list(A.animation_data.nla_tracks): A.animation_data.nla_tracks.remove(t)
for pb in A.pose.bones: pb.matrix_basis.identity()
if corpo.data.shape_keys:
    corpo.shape_key_clear()                                    # basis fica (correctivas = 0 no repouso)
corpo.name = "Wyvern_Corpo"
# sela aprovada (ja com UV/material de jogo 1024), pesos nos mesmos ossos
with bpy.data.libraries.load(os.path.join(AQUI, "export", "sela", "Wyvern_Sela_Jogo.blend")) as (src, dst):
    dst.objects = ["Wyvern_Sela"]
sela = dst.objects[0]; bpy.context.scene.collection.objects.link(sela)
if sela.parent: bpy.context.scene.collection.objects.link(sela.parent) if sela.parent.name not in bpy.context.scene.collection.objects else None
bpy.context.view_layer.update(); mw = sela.matrix_world.copy()            # posicao aprovada no mundo (repouso)
sela.parent = A; sela.matrix_world = mw
print("SELA_MUNDO", tuple(round(x, 3) for x in mw.translation))
for md in list(sela.modifiers):
    if md.type == "ARMATURE": md.object = A
if not any(md.type == "ARMATURE" for md in sela.modifiers):
    sela.modifiers.new("Armature", "ARMATURE").object = A
malhas = (corpo, sela)
u = set()
for o in malhas:
    nm = {g.index: g.name for g in o.vertex_groups}
    for v in o.data.vertices:
        for g in v.groups:
            if g.weight > 0.001: u.add(nm[g.group])
faltam = [b.name for b in A.data.bones if b.name not in u and b.name != "root"]
assert not faltam, "ossos sem peso: %s" % faltam              # ossos sem peso somem na importacao
for velho, novo in MAPA.items():
    A.data.bones[velho].name = novo
    for o in malhas:
        g = o.vertex_groups.get(velho)
        if g: g.name = novo
for o in malhas:
    n = sum(len(p.vertices) - 2 for p in o.data.polygons); print("EXPORT", o.name, "tris", n)
    assert n <= 20000, o.name + " passa de 20k tris"
for im in bpy.data.images:
    if im.size[0] > 1024:
        if not im.packed_file and im.filepath: im.pack()
        im.scale(1024, 1024); print("TEX", im.name, "-> 1024")
for o in list(bpy.data.objects):
    if o.library and o.type == "ARMATURE" or (o.name.startswith("Wyvern_Rig.") ):
        bpy.data.objects.remove(o)
bpy.ops.object.select_all(action="DESELECT")
for o in (A,) + malhas: o.select_set(True)
bpy.context.view_layer.objects.active = A
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format="GLB", use_selection=True, export_animations=False,
                          export_morph=False, export_image_format="AUTO", export_skins=True)
print("EXPORT_OK", round(os.path.getsize(SAIDA) / 1e6, 2), "MB")
