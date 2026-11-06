"""Lote 5b: sela definitiva para o Roblox. Faz UV novo em atlas unico, assa os materiais procedurais (5) em 4 mapas
1024 (cor, normal tangente, rugosidade, metal) num material so (M_Sela_Atlas, 1 SurfaceAppearance no jogo), exporta GLB
com o esqueleto do crocodilo (mesmos 28 nomes de osso, sem mudar o rig) + a malha da sela, sem animacao.
No jogo a sela vai DENTRO do modelo do crocodilo e usa os ossos dele (o Roblox liga a pele pelo nome do osso); ossos
sem peso na sela somem na importacao do GLB da sela, o que nao importa.
Depois reimporta o GLB numa cena vazia e confere: ossos, tris, grupos, influencias, imagens, medidas e a deformacao numa
pose de teste (diferenca de vertices original x reimportado).
Uso: blender -b CR_Crocodilo_Sela.blend -P exportar_sela.py -- <saida.glb> <pasta_tex> [tamanho]"""
import bpy, sys, os, math, json
from mathutils import Vector as V, Quaternion as Q
A = sys.argv[sys.argv.index("--") + 1:]; SAIDA = os.path.abspath(A[0]); TEX = os.path.abspath(A[1]); TAM = int(A[2]) if len(A) > 2 else 1024
os.makedirs(os.path.dirname(SAIDA), exist_ok=True); os.makedirs(TEX, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["CR_Croc_Rig"]; sela = bpy.data.objects["CR_Croc_Sela"]
for pb in arm.pose.bones:
    for c in list(pb.constraints): pb.constraints.remove(c)
    pb.rotation_mode = "QUATERNION"; pb.matrix_basis.identity()
if arm.animation_data: arm.animation_data.action = None
bpy.context.view_layer.update()
me = sela.data
# ------------------------------------------------------------------ UV em atlas (ilhas pela quebra de angulo; margem ~4 px)
for o in bpy.context.selected_objects: o.select_set(False)
sela.select_set(True); bpy.context.view_layer.objects.active = sela
uv = me.uv_layers.new(name="Atlas"); me.uv_layers.active = uv
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(55), island_margin=0.004, scale_to_bounds=False)
bpy.ops.uv.pack_islands(rotate=True, margin=4.0 / TAM)
bpy.ops.object.mode_set(mode="OBJECT")
# ------------------------------------------------------------------ assar
sc.render.engine = "CYCLES"; sc.cycles.samples = 8; sc.cycles.device = "CPU"
bk = sc.render.bake; bk.margin = 8; bk.use_selected_to_active = False; bk.target = "IMAGE_TEXTURES"
imgs = {}
def nova(nome, cor_dado):
    im = bpy.data.images.new("CR_Sela_%s_%d" % (nome, TAM), TAM, TAM, alpha=False)
    im.colorspace_settings.name = "Non-Color" if cor_dado else "sRGB"; imgs[nome] = im; return im
def alvo(im):
    for mt in me.materials:
        nt = mt.node_tree; n = nt.nodes.get("ALVO_BAKE") or nt.nodes.new("ShaderNodeTexImage"); n.name = "ALVO_BAKE"
        n.image = im; nt.nodes.active = n; n.select = True
def assa(tipo, nome, cor_dado, **kw):
    im = nova(nome, cor_dado); alvo(im)
    bpy.ops.object.bake(type=tipo, use_clear=True, **kw)
    im.filepath_raw = os.path.join(TEX, im.name + ".png"); im.file_format = "PNG"; im.save()
    print("BAKE", nome, im.filepath_raw, flush=True)
# cor pela EMISSAO (o passe difuso do Cycles da preto em material metalico): cor base ligada na emissao so para assar
tmp = []
for mt in me.materials:
    nt_ = mt.node_tree; b_ = nt_.nodes["Principled BSDF"]; lk = b_.inputs["Base Color"].links
    em_ = (tuple(b_.inputs["Emission Color"].default_value), b_.inputs["Emission Strength"].default_value)
    if lk: tmp.append((mt, nt_.links.new(lk[0].from_socket, b_.inputs["Emission Color"]), em_))
    else: b_.inputs["Emission Color"].default_value = b_.inputs["Base Color"].default_value; tmp.append((mt, None, em_))
    b_.inputs["Emission Strength"].default_value = 1.0
assa("EMIT", "cor", False)
for mt, l_, em_ in tmp:
    b_ = mt.node_tree.nodes["Principled BSDF"]
    if l_: mt.node_tree.links.remove(l_)
    b_.inputs["Emission Color"].default_value = em_[0]; b_.inputs["Emission Strength"].default_value = em_[1]
assa("NORMAL", "normal", True, normal_space="TANGENT")
assa("ROUGHNESS", "rugosidade", True)
guarda = {}
for mt in me.materials:                                     # metal: emissao = valor metalico do material
    b = mt.node_tree.nodes["Principled BSDF"]; m_ = b.inputs["Metallic"].default_value
    guarda[mt.name] = (tuple(b.inputs["Emission Color"].default_value), b.inputs["Emission Strength"].default_value)
    b.inputs["Emission Color"].default_value = (m_, m_, m_, 1); b.inputs["Emission Strength"].default_value = 1.0
assa("EMIT", "metal", True)
for mt in me.materials:
    b = mt.node_tree.nodes["Principled BSDF"]; b.inputs["Emission Color"].default_value = guarda[mt.name][0]; b.inputs["Emission Strength"].default_value = guarda[mt.name][1]
# ------------------------------------------------------------------ material unico com os mapas
mt = bpy.data.materials.new("M_Sela_Atlas"); mt.use_nodes = True; nt = mt.node_tree; b = nt.nodes["Principled BSDF"]
def tex(nome):
    n = nt.nodes.new("ShaderNodeTexImage"); n.image = imgs[nome]; return n
nt.links.new(tex("cor").outputs["Color"], b.inputs["Base Color"])
nt.links.new(tex("rugosidade").outputs["Color"], b.inputs["Roughness"]); nt.links.new(tex("metal").outputs["Color"], b.inputs["Metallic"])
nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(tex("normal").outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
me.materials.clear(); me.materials.append(mt)
for p in me.polygons: p.material_index = 0
for l in [l for l in me.uv_layers if l.name != "Atlas"]: me.uv_layers.remove(l)
me.uv_layers["Atlas"].name = "UVMap"
for md in list(sela.modifiers):
    if md.type != "ARMATURE": sela.modifiers.remove(md)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath), "CR_Crocodilo_Sela_Atlas.blend"), copy=True)   # para revisao
# ------------------------------------------------------------------ pose de teste (antes de exportar)
POSE = {"Pelve": (V((1, 0, 0)), 8.0), "Coluna1": (V((0, 0, 1)), 12.0), "Coluna2": (V((0, 1, 0)), -7.0), "BracoE": (V((1, 0, 0)), 20.0)}
def pose(a):
    for nm_, (eixo, g) in POSE.items():
        pb = a.pose.bones[nm_]; pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = Q(eixo, math.radians(g))
    bpy.context.view_layer.update()
def verts(o):
    dg = bpy.context.evaluated_depsgraph_get(); e = o.evaluated_get(dg); m = e.to_mesh(); r = [tuple(o.matrix_world @ v.co) for v in m.vertices]; e.to_mesh_clear(); return r
repouso = verts(sela); pose(arm); antes = verts(sela)
for pb in arm.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()
# ------------------------------------------------------------------ exportar (so esqueleto + sela)
sela.name = "Crocodilo_Sela"; arm.name = "Crocodilo_Rig"
for o in sc.objects: o.select_set(False)
arm.select_set(True); sela.select_set(True); bpy.context.view_layer.objects.active = arm
tris = sum(len(p.vertices) - 2 for p in me.polygons)
bpy.ops.export_scene.gltf(filepath=SAIDA, export_format="GLB", use_selection=True, export_animations=False,
                          export_image_format="AUTO", export_skins=True, export_all_influences=False)
print("EXPORT_OK", SAIDA, round(os.path.getsize(SAIDA) / 1e6, 2), "MB tris", tris, flush=True)
# ------------------------------------------------------------------ conferencia por reimportacao
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SAIDA)
a = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]; mal = [o for o in bpy.context.scene.objects if o.type == "MESH"]
print("MALHAS_REIMPORT", [(o.name, len(o.data.vertices), o.parent.name if o.parent else None) for o in mal])
m = next(o for o in mal if o.name.startswith("Crocodilo_Sela"))
grupos = {g.name for g in m.vertex_groups}; nomes_g = {g.index: g.name for g in m.vertex_groups}
max_inf = max(len([g for g in v.groups if g.weight > 0.001]) for v in m.data.vertices)
com_peso = sorted({nomes_g[g.group] for v in m.data.vertices for g in v.groups if g.weight > 0.001})
# o glTF divide vertices nas costuras do UV: casa cada vertice reimportado com o original pela posicao de repouso
from mathutils.kdtree import KDTree
kd = KDTree(len(repouso))
for i, p in enumerate(repouso): kd.insert(p, i)
kd.balance(); rep_m = verts(m); par = [kd.find(p) for p in rep_m]; casa = max(d for _, _, d in par)
pose(a); depois = verts(m)
dif = max((V(depois[k]) - V(antes[i])).length for k, (_, i, _) in enumerate(par))
res = {"ossos": len(a.data.bones), "malhas": len(mal), "tris": sum(len(p.vertices) - 2 for p in m.data.polygons), "vertices": len(m.data.vertices),
       "vertices_original": len(antes), "max_influencias": max_inf, "ossos_com_peso": com_peso,
       "materiais": [s.material.name for s in m.material_slots], "imagens": [(i.name, tuple(i.size)) for i in bpy.data.images],
       "dims": [round(d, 3) for d in m.dimensions], "casamento_repouso_max": casa, "pose_teste_dif_max": dif}
print("REIMPORT", json.dumps(res, ensure_ascii=False))
json.dump(res, open(os.path.splitext(SAIDA)[0] + "_conferencia.json", "w"), indent=1, ensure_ascii=False)
