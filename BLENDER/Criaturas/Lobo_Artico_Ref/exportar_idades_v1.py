"""Malhas por idade do Lobo Artico (19/11/2026; proposta visual APROVADA pelo usuario: "Aprovar e seguir" sobre idades_v1).
Para UMA idade: aplica as proporcoes como REPOUSO (mesmos 37 ossos e nomes, orientacoes intactas: so comprimento/espessura),
poe as patas no chao, escala os cristais, tinge a cor da pelagem (PNG multiplicado) e exporta um GLB SEM animacoes
(os clipes do jogo ja estao na biblioteca do place). Tamanho normalizado (Adulto = 1): o tamanho da idade e o Model:ScaleTo
do Idade_Servidor.
Diferenca para o prototipo: o Anciao NAO baixa a cabeca no repouso (girar o repouso mudaria a convencao dos clipes); a
cabeca mais baixa fica para uma camada de pose no jogo, se o usuario pedir.
Uso: blender -b anim_v42b/CR_LoboArtico_Anim.blend -P exportar_idades_v1.py -- <Idade> <dir_saida>"""
import bpy, bmesh, sys, os, json
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; IDADE = a[0]; OUT = os.path.abspath(a[1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; P = ARM.pose.bones
NOMES = ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"]
PERNAS = ("Umero", "Antebraco", "Coxa", "Tibia")
def idade(cab, cab_y, orelha, perna, pata, cauda, corpo_y, pesc_xz=1.0, pesc_y=1.0, corpo_xz=1.0):
    s = {"Cabeca": (cab, cab_y, cab), "Orelha_E": (orelha,) * 3, "Orelha_D": (orelha,) * 3,
         "Cauda1": (1, cauda, 1), "Cauda2": (1, cauda, 1), "Cauda3": (1, cauda, 1), "Cauda4": (1, cauda, 1),
         "Coluna1": (corpo_xz, corpo_y, corpo_xz), "Coluna2": (corpo_xz, corpo_y, corpo_xz), "Coluna3": (corpo_xz, corpo_y, corpo_xz),
         "Pescoco1": (pesc_xz, pesc_y, pesc_xz), "Pescoco2": (pesc_xz, pesc_y, pesc_xz)}
    # r2 (QA 19/11): a perna INTEIRA encolhe na mesma proporcao (umero/antebraco/metacarpo/dedos; coxa/tibia/metatarso/dedos
    # do pe) -> triangulos semelhantes: o apoio dos clipes do Adulto continua no chao. A pata grande e so em LARGURA.
    for l in ("E", "D"):
        for n in PERNAS + ("Metacarpo", "Metatarso"): s[n + "_" + l] = (1, perna, 1)
        s["Dedos_" + l] = (pata, perna, pata); s["DedosPe_" + l] = (pata, perna, pata)
    return s
IDADES = {  # mesma tabela aprovada (idades_v1.py / prancha idades_v1d)
    # r3 (QA 19/11): pernas com o comprimento do Adulto em todas as idades (os clipes de deitar/sentar baixam o corpo uma
    # distancia fixa: perna curta afundava o filhote -0,78 e perna longa deixava o jovem flutuando +0,25). A idade aparece na
    # cabeca, corpo curto/gordinho ou magro, patas largas, cauda, pescoco, pelagem e cristais.
    "Filhote":   (idade(1.22, 0.90, 1.30, 1.0, 1.32, 0.60, 0.92, pesc_y=0.80, corpo_xz=1.06), (0.46, 0.42, 0.39), 0.0),
    "Jovem":     (idade(1.12, 1.00, 1.16, 1.0, 1.14, 0.84, 0.95, pesc_y=0.95, corpo_xz=0.92), (0.70, 0.69, 0.68), 0.45),
    "PreAdulto": (idade(1.05, 1.01, 1.05, 1.0, 1.04, 0.95, 0.98, corpo_xz=0.97), (0.88, 0.88, 0.88), 0.75),
    "Adulto":    (idade(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0), (1.0, 1.0, 1.0), 1.0),
    "Anciao":    (idade(1.0, 1.0, 0.97, 1.0, 1.0, 1.0, 1.0, pesc_xz=1.10), (1.0, 0.95, 0.86), 1.35),
}
ESC, TINTA, CRI = IDADES[IDADE]
for ac in list(bpy.data.actions): bpy.data.actions.remove(ac)            # GLB sem animacoes
if ARM.animation_data: ARM.animation_data.action = None
for o in sc.objects:
    if o.type == "MESH" and o.name not in NOMES and o.parent == ARM: o.hide_render = True
if IDADE == "Filhote": NOMES.remove("LOW_Marca"); bpy.data.objects["LOW_Marca"].hide_render = True   # filhote sem a marca acesa (prototipo aprovado)
obs = [bpy.data.objects[n] for n in NOMES]
for pb in P: pb.matrix_basis.identity()
bpy.context.view_layer.update()
corpo = bpy.data.objects["LOW_Corpo"]
def chao_min():
    dg = bpy.context.evaluated_depsgraph_get(); ev = corpo.evaluated_get(dg); me = ev.to_mesh()
    z = min((ev.matrix_world @ v.co).z for v in me.vertices); ev.to_mesh_clear(); return z
Z0 = chao_min()
# 1) cristais (antes de tudo, no repouso): escala de cada cristal em torno da propria base
cri = bpy.data.objects["LOW_Cristais"]
if CRI != 1.0:
    me = cri.data; bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); vistos = set()
    for v in bm.verts:
        if v.index in vistos: continue
        pilha, ilha = [v], []
        while pilha:
            x = pilha.pop()
            if x.index in vistos: continue
            vistos.add(x.index); ilha.append(x)
            for e in x.link_edges: pilha.append(e.other_vert(x))
        base = sum((x.co for x in ilha), V()) / len(ilha); base.z = min(x.co.z for x in ilha)
        for x in ilha: x.co = base + (x.co - base) * max(CRI, 0.01)
    bm.to_mesh(me); bm.free(); me.update()
# 2) proporcoes na pose (sem heranca de escala) -> malha deformada vira a malha de repouso -> pose vira repouso
for bo in ARM.data.bones: bo.inherit_scale = "NONE"
for pb in P: pb.scale = ESC.get(pb.name, (1, 1, 1))
bpy.context.view_layer.update()
dz = Z0 - chao_min()                                                     # patas de volta ao chao
dg = bpy.context.evaluated_depsgraph_get()
for o in obs:
    ev = o.evaluated_get(dg); nova = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
    for v in nova.vertices: v.co.z += dz            # espaco do objeto = espaco do rig (filhos sem transformacao propria)
    velha = o.data; o.data = nova; nova.name = velha.name
bpy.context.view_layer.objects.active = ARM
for x in sc.objects: x.select_set(False)
ARM.select_set(True); bpy.ops.object.mode_set(mode="POSE"); bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode="EDIT")
for eb in ARM.data.edit_bones: eb.head.z += dz; eb.tail.z += dz
bpy.ops.object.mode_set(mode="OBJECT")
for bo in ARM.data.bones: bo.inherit_scale = "FULL"
bpy.context.view_layer.update()
# conferencias: patas no chao e ossos no lugar da malha
z1 = chao_min()
# 3) tinta: PNGs de cor ja multiplicados por tingir_idades_v1.py (o Python do Blender nao tem PIL)
def tingir(img):
    if TINTA == (1.0, 1.0, 1.0): return
    src = bpy.path.abspath(img.filepath); dst = os.path.join(OUT, "%s_%s.png" % (os.path.splitext(os.path.basename(src))[0], IDADE))
    assert os.path.exists(dst), "rode tingir_idades_v1.py antes: " + dst
    img.filepath = dst; img.reload()
for mn in ("M_LoboArtico_Corpo_LOW", "M_LoboArtico_Cabeca_LOW", "M_LoboArtico_Pelagem_LOW"):
    nt = bpy.data.materials[mn].node_tree; lk = nt.nodes["Principled BSDF"].inputs["Base Color"].links
    if lk and lk[0].from_node.bl_idname == "ShaderNodeTexImage": tingir(lk[0].from_node.image)
# 4) export (mesmos parametros do exportar_clipes_v41, sem animacoes)
ops = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
def kw(**d): return {k: v for k, v in d.items() if k in ops}
OSS = [b.name for b in ARM.data.bones]; usados = set()
for o in obs:
    gn = {g.index: g.name for g in o.vertex_groups}
    for v in o.data.vertices:
        for e in v.groups:
            if e.weight > 0.001 and gn[e.group] in OSS: usados.add(gn[e.group])
alvo = corpo; garant = []
for bn in ARM.data.bones:                       # osso sem peso some no Import 3D: triangulo minimo nele
    if bn.name in usados: continue
    me = alvo.data; bm = bmesh.new(); bm.from_mesh(me); vs = [bm.verts.new(bn.head_local) for _ in range(3)]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
    g = alvo.vertex_groups.get(bn.name) or alvo.vertex_groups.new(name=bn.name); ids = list(range(len(me.vertices) - 3, len(me.vertices)))
    for og in alvo.vertex_groups:
        if og is not g: og.remove(ids)
    g.add(ids, 1.0, "REPLACE"); garant.append(bn.name)
tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs}; assert all(t <= 20000 for t in tris.values()), tris
for x in sc.objects: x.select_set(False)
for o in [ARM] + obs: o.hide_viewport = False; o.hide_select = False; o.hide_set(False); o.select_set(True)
bpy.context.view_layer.objects.active = ARM
arq = os.path.join(OUT, "CR_LoboArtico_%s.glb" % IDADE)
bpy.ops.export_scene.gltf(filepath=arq, **kw(export_format="GLB", use_selection=True, export_yup=True, export_image_format="AUTO", export_materials="EXPORT",
                                             export_skins=True, export_all_influences=False, export_influence_nb=4, export_def_bones=False,
                                             export_animations=False, export_reset_pose_bones=True, export_morph=False))
rest = {b.name: [list(b.head_local), list(b.tail_local)] for b in ARM.data.bones}
rel = {"idade": IDADE, "arquivo": os.path.basename(arq), "MB": round(os.path.getsize(arq) / 1e6, 2), "tris": tris, "dz": round(dz, 4),
       "chao_antes": round(Z0, 4), "chao_depois": round(z1, 4), "ossos_garantidos": garant, "repouso": rest}
json.dump(rel, open(os.path.join(OUT, "idade_%s.json" % IDADE), "w"), indent=0)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_%s.blend" % IDADE), copy=True)
print("IDADE_EXPORT", IDADE, rel["MB"], "MB dz", rel["dz"], "chao", rel["chao_antes"], "->", rel["chao_depois"], flush=True)
