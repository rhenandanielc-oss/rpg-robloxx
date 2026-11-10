"""Montaria M7 (10/11/2026): GLB DEFINITIVO da sela do urso, com o MESMO esqueleto do urso no Roblox.
Causa do problema do M4: a sela so tinha peso em 13 dos 31 ossos. O Roblox descarta/trata diferente os ossos sem peso
no import (a sela chegou com 18 ossos e o Raiz girado 180 graus), e a pele nao podia usar os ossos do urso pelo nome.
Correcao = a mesma do exportar_urso.py do proprio urso: cada osso sem peso recebe um triangulo degenerado (invisivel) na
cabeca do osso, com 100% de peso. Assim os 31 ossos chegam iguais aos do urso, e no Studio a sela pode ficar DENTRO do
modelo do urso sem ossos proprios (a pele usa os ossos do urso pelo nome), sem script de copia.
Parte do .blend da M3 (textura de jogo ja assada; nada e re-assado). Mesmas opcoes de export do exportar_urso.py.
Uso: blender -b export/sela/Urso_Silvestre_Sela_Jogo.blend -P m7_sela_definitiva.py -- <saida.glb>"""
import bpy, bmesh, sys, os
SAIDA = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
A = bpy.data.objects["Urso_Rig"]; S = bpy.data.objects["Urso_Silvestre_Sela"]
for pb in A.pose.bones:
    for c in pb.constraints: c.mute = True
    pb.matrix_basis.identity()
if A.animation_data: A.animation_data.action = None
bpy.context.view_layer.update()
nomes = {g.index: g.name for g in S.vertex_groups}; usados = set()
for v in S.data.vertices:
    for g in v.groups:
        if g.weight > 0.001: usados.add(nomes[g.group])
Minv = S.matrix_world.inverted(); garantidos = []
for bn in A.data.bones:
    if bn.name in usados: continue
    me = S.data; bm = bmesh.new(); bm.from_mesh(me)
    p = Minv @ (A.matrix_world @ bn.head_local); vs = [bm.verts.new(p) for _ in range(3)]; bm.faces.new(vs)
    bm.to_mesh(me); bm.free()
    g = S.vertex_groups.get(bn.name) or S.vertex_groups.new(name=bn.name)
    ids = list(range(len(me.vertices) - 3, len(me.vertices)))
    for og in S.vertex_groups:
        if og is not g: og.remove(ids)
    g.add(ids, 1.0, "REPLACE"); garantidos.append(bn.name)
print("OSSOS_GARANTIDOS", len(garantidos), garantidos)
# r2 (10/11): com UMA malha so, o Import 3D pendura os ossos na propria MeshPart e eles chegam girados 180 graus em
# relacao ao urso (que tem 4 malhas: o importador cria uma RootPart e os ossos ficam nela). Uma 2a malha minima
# ("ancora": 1 triangulo degenerado, peso 100% no Raiz) faz a sela chegar com a MESMA estrutura do urso.
if os.environ.get("SELA_ANCORA", "1") == "1":
    ma = bpy.data.meshes.new("Urso_Sela_Ancora"); p = A.matrix_world @ A.data.bones["Raiz"].head_local
    ma.from_pydata([tuple(p), tuple(p), tuple(p)], [], [(0, 1, 2)]); ma.update()
    an = bpy.data.objects.new("Urso_Sela_Ancora", ma); bpy.context.scene.collection.objects.link(an)
    an.data.materials.append(S.data.materials[0])
    an.vertex_groups.new(name="Raiz").add([0, 1, 2], 1.0, "REPLACE")
    an.parent = A; an.matrix_parent_inverse = A.matrix_world.inverted(); an.modifiers.new("Armature", "ARMATURE").object = A
    print("ANCORA criada")
bpy.ops.object.select_all(action="DESELECT")
for o in [A, S] + [o for o in bpy.data.objects if o.name == "Urso_Sela_Ancora"]: o.select_set(True)
bpy.context.view_layer.objects.active = A
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format="GLB", use_selection=True, export_animations=False, export_yup=True,
                          export_image_format="AUTO", export_skins=True, export_all_influences=False, export_materials="EXPORT",
                          export_tangents=True)
print("EXPORT_OK", SAIDA, round(os.path.getsize(SAIDA) / 1e6, 2), "MB")
