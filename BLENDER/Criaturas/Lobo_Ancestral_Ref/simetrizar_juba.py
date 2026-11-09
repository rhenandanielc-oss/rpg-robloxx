"""Correcao localizada da leitura frontal do peito/juba do Lobo Ancestral (malha de jogo do rig2, em repouso):
a metade -X da JUBA/PEITO (mechas que descem para o centro) e espelhada sobre a metade +X, com transicao suave na linha
central e nas bordas da regiao. Geometria (vertices +X projetados na superficie espelhada), COR e NORMAL da textura (bake
do lado espelhado so dentro da mascara, em espaco UV) e PESOS (copiados do lado oposto trocando E<->D). Cabeca/rosto,
corpo, patas, UV, topologia e esqueleto nao mudam. Entrada preservada (rig2/).
Uso: blender -b rig2/Lobo_Ancestral_Rig.blend -P simetrizar_juba.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, kdtree
from mathutils.bvhtree import BVHTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
def suave(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
n = len(me.vertices); co0 = [v.co.copy() for v in me.vertices]
gi = {g.index: g.name for g in LO.vertex_groups}
def dono(v): return gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else ""
JUB = {"JubaE", "JubaD", "JubaPeito", "Pescoco1", "Pescoco2", "Peito"}
y_omb = arm.data.bones["BracoE"].head_local.y
reg = np.array([1.0 if (dono(v) in JUB and v.co.y < y_omb + 0.5 and v.co.z > 3.4) else 0.0 for v in me.vertices])
viz = [[] for _ in range(n)]
for e in me.edges: a, b = e.vertices; viz[a].append(b); viz[b].append(a)
m = reg.copy()
for _ in range(6):                                            # borda macia da regiao
    m = np.array([0.5 * m[i] + 0.5 * (m[viz[i]].mean() if viz[i] else m[i]) for i in range(n)])
m = np.clip(m * 1.6, 0, 1)
w = np.array([m[i] * suave(co0[i].x / 0.30) if co0[i].x > 0 else 0.0 for i in range(n)])
print("REGIAO verts", int(reg.sum()), "afetados (w>0,02)", int((w > 0.02).sum()), "w max", round(float(w.max()), 3))
# fonte: faces do lado -X na regiao (coordenadas originais)
fonte = [p for p in me.polygons if all(co0[i].x < 0.12 for i in p.vertices) and max(m[i] for i in p.vertices) > 0.01]
verts_f = sorted({i for p in fonte for i in p.vertices}); mapa = {i: k for k, i in enumerate(verts_f)}
bvh = BVHTree.FromPolygons([co0[i] for i in verts_f], [[mapa[i] for i in p.vertices] for p in fonte])
kd = kdtree.KDTree(len(verts_f))
for i in verts_f: kd.insert(co0[i], i)
kd.balance()
def esp(p): return V((-p.x, p.y, p.z))
TROCA = {}
for nm in gi.values():
    if nm.endswith("E") and nm[:-1] + "D" in gi.values(): TROCA[nm] = nm[:-1] + "D"; TROCA[nm[:-1] + "D"] = nm
idx_g = {g.name: g.index for g in LO.vertex_groups}
pesos0 = [{gi[q.group]: q.weight for q in v.groups} for v in me.vertices]
mov = 0; desl = []
for i in range(n):
    if w[i] <= 0.02: continue
    loc, nrm, fi, dist = bvh.find_nearest(esp(co0[i]))
    if loc is None: continue
    alvo = esp(loc); novo = co0[i].lerp(alvo, w[i]); desl.append((novo - co0[i]).length); me.vertices[i].co = novo; mov += 1
    _, j, _ = kd.find(esp(co0[i]))
    src = {TROCA.get(k, k): wt for k, wt in pesos0[j].items()}
    nomes = set(pesos0[i]) | set(src)
    mist = {k: (1 - w[i]) * pesos0[i].get(k, 0.0) + w[i] * src.get(k, 0.0) for k in nomes}
    tot = sum(mist.values()) or 1.0
    for k in list(pesos0[i]):
        if mist.get(k, 0.0) <= 1e-4: LO.vertex_groups[k].remove([i])
    for k, wt in mist.items():
        if wt > 1e-4: LO.vertex_groups[k].add([i], wt / tot, "REPLACE")
me.update()
print("GEOMETRIA vertices movidos", mov, "deslocamento medio %.3f max %.3f" % (np.mean(desl), np.max(desl)))
# limite de 4 influencias
bpy.ops.object.select_all(action="DESELECT"); LO.select_set(True); bpy.context.view_layer.objects.active = LO
bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)

# ------------------------------------------------------------------ textura: bake do lado espelhado so dentro da mascara
mat = me.materials[0]; nt = mat.node_tree
tex_cor = next(nd for nd in nt.nodes if nd.type == "TEX_IMAGE" and nd.image and nd.image.name.startswith("T_Lobo_Cor"))
tex_nor = next(nd for nd in nt.nodes if nd.type == "TEX_IMAGE" and nd.image and nd.image.name.startswith("T_Lobo_Normal"))
IMC, IMN = tex_cor.image, tex_nor.image; R = IMC.size[0]
# espelho: copia da malha ORIGINAL (antes da edicao) refletida em X, normais invertidas, mesmo material/UV
em_me = me.copy()
for v, c in zip(em_me.vertices, co0): v.co = c
bm = bmesh.new(); bm.from_mesh(em_me); bmesh.ops.transform(bm, matrix=Matrix.Diagonal((-1, 1, 1, 1)), verts=bm.verts)
bmesh.ops.reverse_faces(bm, faces=bm.faces); bm.to_mesh(em_me); bm.free()
ESP = bpy.data.objects.new("Espelho_Juba", em_me); sc.collection.objects.link(ESP)
m_esp = bpy.data.materials.new("M_Espelho"); m_esp.use_nodes = True; ne = m_esp.node_tree; ne.nodes.clear()
o_e = ne.nodes.new("ShaderNodeOutputMaterial"); emis = ne.nodes.new("ShaderNodeEmission"); ti = ne.nodes.new("ShaderNodeTexImage")
ne.links.new(ti.outputs["Color"], emis.inputs["Color"]); ne.links.new(emis.outputs[0], o_e.inputs[0])
em_me.materials.clear(); em_me.materials.append(m_esp)
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 1
bk = sc.render.bake; bk.margin = 4
def alvo_img(nome, cor):
    im = bpy.data.images.new(nome, R, R, alpha=False)
    if not cor: im.colorspace_settings.name = "Non-Color"
    return im
nd_alvo = nt.nodes.new("ShaderNodeTexImage")
def bake_espelho(img_fonte, nome, cor):
    ti.image = img_fonte; im = alvo_img(nome, cor); nd_alvo.image = im
    for q in nt.nodes: q.select = False
    nd_alvo.select = True; nt.nodes.active = nd_alvo
    bk.use_selected_to_active = True; bk.cage_extrusion = 0.06; bk.max_ray_distance = 0.3
    bpy.ops.object.select_all(action="DESELECT"); ESP.select_set(True); LO.select_set(True); bpy.context.view_layer.objects.active = LO
    bpy.ops.object.bake(type="EMIT"); return im
E_COR = bake_espelho(IMC, "Espelho_Cor", True); E_NOR = bake_espelho(IMN, "Espelho_Nor", False)
# mascara em UV: atributo de cor = w, bake EMIT na propria malha com material temporario
ca = me.color_attributes.new("MascJuba", "FLOAT_COLOR", "POINT")
for i in range(n): ca.data[i].color = (w[i], w[i], w[i], 1)
m_tmp = bpy.data.materials.new("M_Masc"); m_tmp.use_nodes = True; nm_ = m_tmp.node_tree; nm_.nodes.clear()
o2 = nm_.nodes.new("ShaderNodeOutputMaterial"); e2 = nm_.nodes.new("ShaderNodeEmission"); vc = nm_.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "MascJuba"
nm_.links.new(vc.outputs["Color"], e2.inputs["Color"]); nm_.links.new(e2.outputs[0], o2.inputs[0])
IMM = alvo_img("Mascara_Juba", False); t2 = nm_.nodes.new("ShaderNodeTexImage"); t2.image = IMM; t2.select = True; nm_.nodes.active = t2
me.materials[0] = m_tmp
bk.use_selected_to_active = False
bpy.ops.object.select_all(action="DESELECT"); LO.select_set(True); bpy.context.view_layer.objects.active = LO
bpy.ops.object.bake(type="EMIT")
me.materials[0] = mat; me.color_attributes.remove(me.color_attributes["MascJuba"])
def arr(im): a = np.empty(R * R * 4, np.float32); im.pixels.foreach_get(a); return a.reshape(R, R, 4)
cor, nor, ec, en, mk = arr(IMC), arr(IMN), arr(E_COR), arr(E_NOR), arr(IMM)[:, :, :1]
en[:, :, 0] = 1.0 - en[:, :, 0]                               # tangente espelhada: inverte o vermelho da normal
cor_n = cor * (1 - mk) + ec * mk; nor_n = nor * (1 - mk) + en * mk; cor_n[:, :, 3] = 1; nor_n[:, :, 3] = 1
print("TEXTURA texels mascara > 0,5:", int((mk[:, :, 0] > 0.5).sum()), "de", R * R)
NC, NN = bpy.data.images.new("T_Lobo_Cor_v3", R, R), bpy.data.images.new("T_Lobo_Normal_v3", R, R); NN.colorspace_settings.name = "Non-Color"
NC.pixels.foreach_set(cor_n.ravel()); NN.pixels.foreach_set(nor_n.ravel())
for im, nome in ((NC, "T_Lobo_Cor.png"), (NN, "T_Lobo_Normal.png"), (IMM, "mascara_juba.png")):
    im.filepath_raw = os.path.join(OUT, nome); im.file_format = "PNG"; im.save()
tex_cor.image, tex_nor.image = NC, NN
nt.nodes.remove(nd_alvo); bpy.data.objects.remove(ESP)
for im in (NC, NN): im.pack()
sc.render.engine = "BLENDER_EEVEE"
json.dump({"verts_regiao": int(reg.sum()), "verts_movidos": mov, "desloc_medio": float(np.mean(desl)), "desloc_max": float(np.max(desl))},
          open(os.path.join(OUT, "simetrizar_juba.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend"))
print("SIMETRIZAR_OK")
