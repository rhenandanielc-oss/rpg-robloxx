"""Montaria M3 (09/11/2026): textura de jogo e GLB da sela do Urso Silvestre v2 (M1 r3 aprovada). Adaptado do s1_07_textura_glb.py do Leao Solar.
1. UV de jogo unica (projecao inteligente + empacotamento; as pedras novas da r4 nao tinham UV);
2. bake Cycles 1024x1024 dos 7 materiais procedurais (Couro de Javali, Pele de Cervo, Tendao de Cervo, Madeira Ancestral, Resina Viva, Ferro, couro das folhas): cor (DIFFUSE so cor),
   normal (tangente, OpenGL: relevo do couro/costura), rugosidade, metal (bake EMIT com a emissao = metallic de cada material);
3. material unico "M_Urso_Sela_Jogo" com as imagens (metal/rugosidade empacotados no padrao glTF: G = rugosidade, B = metal);
4. GLB so da sela + armadura do urso (pesos nos ossos com os nomes do jogo, max 4 por vertice), sem animacoes, texturas embutidas.
Nada do urso e alterado (o .blend de entrada nao e salvo). Uso: blender -b CR_Urso_v2_M1_sela.blend -P m3_textura_glb.py -- <pasta_saida>"""
import bpy, sys, os, json
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
RES = 1024; sc = bpy.context.scene
arm = bpy.data.objects["Urso_Rig"]; sela = bpy.data.objects["Urso_Silvestre_Sela"]
for pb in arm.pose.bones:                     # restricoes de IK do gerador: desligadas (pose de repouso exata no export)
    for c in pb.constraints: c.mute = True
if arm.animation_data: arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
for o in list(bpy.context.selected_objects): o.select_set(False)
bpy.context.view_layer.objects.active = sela; sela.select_set(True)
# ---------------------------------------------------------------- 1. UV de jogo
me = sela.data
uv = me.uv_layers.new(name="UV_Jogo"); me.uv_layers.active = uv
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.003, area_weight=0.0, correct_aspect=True)
# r2 (09/11): margem 0,012 com milhares de ilhas pequenas usava so ~11% da imagem e as pecas miudas (ferro, resina, cordao)
# ficavam com 1-9 px por face (a cor do vizinho vazava: listras escuras no galho). Densidade igual + margem 0,003 (~3 px).
bpy.ops.uv.select_all(action="SELECT"); bpy.ops.uv.average_islands_scale()
bpy.ops.uv.pack_islands(margin=0.003, rotate=True)
bpy.ops.object.mode_set(mode="OBJECT")
for u in [u for u in me.uv_layers if u.name != "UV_Jogo"]: me.uv_layers.remove(u)
# ---------------------------------------------------------------- 2. bake
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 16; sc.render.bake.margin = 3
def img(nome, cor=False):
    # 8 bits (formato do jogo); imagens float geradas eram gravadas VAZIAS no PNG (normal preto deixava a sela cinza)
    im = bpy.data.images.new(nome, RES, RES, alpha=False, float_buffer=False); im.colorspace_settings.name = "sRGB" if cor else "Non-Color"; return im
IM = {"cor": img("T_Urso_Sela_Cor", True), "normal": img("T_Urso_Sela_Normal"), "rug": img("T_Urso_Sela_Rug"), "metal": img("T_Urso_Sela_Metal")}
mats = list(me.materials)
def alvo(im):
    for mt in mats:
        nt = mt.node_tree; n = nt.nodes.get("_alvo_bake") or nt.nodes.new("ShaderNodeTexImage"); n.name = "_alvo_bake"; n.image = im
        for x in nt.nodes: x.select = False
        n.select = True; nt.nodes.active = n
# cor: bake EMIT com a cor de base ligada na emissao (o DIFFUSE devolve cor 0 nos metais e o ferro saia preto)
guard_c = {}
for mt in mats:
    nt_ = mt.node_tree; b_ = nt_.nodes["Principled BSDF"]; lk = b_.inputs["Base Color"].links
    guard_c[mt.name] = (tuple(b_.inputs["Emission Color"].default_value), b_.inputs["Emission Strength"].default_value)
    if lk: nt_.links.new(lk[0].from_socket, b_.inputs["Emission Color"])
    else: b_.inputs["Emission Color"].default_value = b_.inputs["Base Color"].default_value
    b_.inputs["Emission Strength"].default_value = 1.0
alvo(IM["cor"]); bpy.ops.object.bake(type="EMIT"); print("BAKE cor ok", flush=True)
for mt in mats:
    nt_ = mt.node_tree; b_ = nt_.nodes["Principled BSDF"]
    for l_ in list(b_.inputs["Emission Color"].links): nt_.links.remove(l_)
    b_.inputs["Emission Color"].default_value = guard_c[mt.name][0]; b_.inputs["Emission Strength"].default_value = guard_c[mt.name][1]
alvo(IM["normal"]); sc.render.bake.normal_space = "TANGENT"; bpy.ops.object.bake(type="NORMAL"); print("BAKE normal ok", flush=True)
alvo(IM["rug"]); bpy.ops.object.bake(type="ROUGHNESS"); print("BAKE rugosidade ok", flush=True)
# metal: emissao = metallic do material (o bake EMIT le a emissao); depois restaura
guard = {}
for mt in mats:
    b = mt.node_tree.nodes["Principled BSDF"]; m_ = b.inputs["Metallic"].default_value
    guard[mt.name] = (tuple(b.inputs["Emission Color"].default_value), b.inputs["Emission Strength"].default_value)
    b.inputs["Emission Color"].default_value = (m_, m_, m_, 1); b.inputs["Emission Strength"].default_value = 1.0
alvo(IM["metal"]); bpy.ops.object.bake(type="EMIT"); print("BAKE metal ok", flush=True)
for mt in mats:
    b = mt.node_tree.nodes["Principled BSDF"]; b.inputs["Emission Color"].default_value = guard[mt.name][0]; b.inputs["Emission Strength"].default_value = guard[mt.name][1]
# empacota metal/rugosidade (glTF: G = rugosidade, B = metal) e salva os PNG
def px(im): return np.array(im.pixels[:], dtype=np.float32).reshape(RES, RES, 4)
mr = np.ones((RES, RES, 4), np.float32); mr[..., 1] = px(IM["rug"])[..., 0]; mr[..., 2] = px(IM["metal"])[..., 0]; mr[..., 0] = 1.0
IM["mr"] = bpy.data.images.new("T_Urso_Sela_MetalRug", RES, RES, alpha=False); IM["mr"].colorspace_settings.name = "Non-Color"; IM["mr"].pixels = mr.ravel()
arquivos = {}
for k, im in IM.items():
    caminho = os.path.join(OUT, im.name + ".png"); im.filepath_raw = caminho; im.file_format = "PNG"; im.save(); arquivos[k] = caminho
# ---------------------------------------------------------------- 3. material unico de jogo
mj = bpy.data.materials.new("M_Urso_Sela_Jogo"); mj.use_nodes = True; nt = mj.node_tree; b = nt.nodes["Principled BSDF"]
def tex(k, cs):
    n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(arquivos[k]); n.image.colorspace_settings.name = cs; return n
tc = tex("cor", "sRGB"); nt.links.new(tc.outputs["Color"], b.inputs["Base Color"])
tm = tex("mr", "Non-Color"); sp = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(tm.outputs["Color"], sp.inputs["Color"])
nt.links.new(sp.outputs["Green"], b.inputs["Roughness"]); nt.links.new(sp.outputs["Blue"], b.inputs["Metallic"])
tn = tex("normal", "Non-Color"); nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(tn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
me.materials.clear(); me.materials.append(mj)
for p in me.polygons: p.material_index = 0
# pesos: no maximo 4 influencias, normalizados
bpy.ops.object.vertex_group_limit_total(limit=4); bpy.ops.object.vertex_group_normalize_all(lock_active=False)
# ---------------------------------------------------------------- 4. GLB (sela + armadura do urso, sem animacao)
for o in list(bpy.context.selected_objects): o.select_set(False)
sela.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = sela
glb = os.path.join(OUT, "Urso_Silvestre_Sela.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_animations=False, export_skins=True, export_yup=True,
                          export_apply=False, export_image_format="AUTO", export_tangents=True)
info = {"tris": sum(len(p.vertices) - 2 for p in me.polygons), "vertices": len(me.vertices), "texturas": {k: os.path.basename(v) for k, v in arquivos.items()},
        "resolucao": RES, "glb": os.path.basename(glb), "glb_bytes": os.path.getsize(glb), "grupos": len(sela.vertex_groups)}
json.dump(info, open(os.path.join(OUT, "sela_jogo_info.json"), "w"), indent=1); print("SELA_JOGO", json.dumps(info))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Urso_Silvestre_Sela_Jogo.blend")); print("SELA_JOGO_OK")
