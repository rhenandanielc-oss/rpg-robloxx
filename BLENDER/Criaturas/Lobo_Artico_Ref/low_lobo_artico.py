"""Malha de JOGO (LOW) do CR_LoboArtico a partir do HIGH (criar_lobo_artico.py), sem rig (rig vem depois da aprovacao).
3 MeshParts (cada uma <= 20k tris, uma SurfaceAppearance por peca no Roblox):
  LOW_Corpo    corpo + orelhas + olhos + garras unidos, UV unica, mapas assados do HIGH (cor, normal, rugosidade,
               emissao da marca) em 2048 (intermediario) -> finais 1024
  LOW_Pelagem  os MESMOS cartoes do HIGH (UV no atlas de mechas 1024 com alpha) -> AlphaMode Transparency, DoubleSided
  LOW_Cristais cristais (geometria do HIGH), material translucido sem textura
LODs: LOD1 (corpo reduzido + so os cartoes longos de silhueta) e LOD2 (corpo bem reduzido, sem cartoes).
Uso: blender -b high/CR_LoboArtico_HIGH.blend -P low_lobo_artico.py -- <saida_dir> [res_bake]"""
import bpy, sys, os, math, json, shutil
args = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(args[0]); RES = int(args[1]) if len(args) > 1 else 2048
FINAL = 1024
os.makedirs(os.path.join(OUT, "bake%d" % RES), exist_ok=True)
AQUI = os.path.dirname(os.path.abspath(__file__))
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
col = bpy.data.collections["CR_LoboArtico"]; HIGH = [o for o in col.objects if o.type == "MESH"]
corpo = bpy.data.objects["CR_LoboArtico_Corpo"]; pel = bpy.data.objects["CR_LoboArtico_Pelagem"]
CRIS = [o for o in HIGH if o.name.startswith("CR_LoboArtico_Cristal")]
PECAS = [o for o in HIGH if o.name.startswith(("CR_LoboArtico_Orelha", "CR_LoboArtico_Olho", "CR_LoboArtico_Garra"))]
def ativo(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
def copia(o, nome):
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); c = bpy.data.objects.new(nome, me)
    c.matrix_world = o.matrix_world.copy(); sc.collection.objects.link(c); return c
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
def reduzir(o, alvo):
    n = tris(o)
    if n > alvo:
        ativo(o); d = o.modifiers.new("D", "DECIMATE"); d.ratio = alvo / n; bpy.ops.object.modifier_apply(modifier="D")
def unir(objs, nome):
    bpy.ops.object.select_all(action="DESELECT")
    for p in objs: p.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); o = objs[0]; o.name = nome; o.data.name = nome
    ativo(o); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); return o
def triangular(o):
    ativo(o); bpy.ops.object.modifier_add(type="TRIANGULATE"); bpy.ops.object.modifier_apply(modifier=o.modifiers[-1].name)

def corpo_low(alvo, nome):
    lc = copia(corpo, nome); ativo(lc)
    vx = lc.modifiers.new("V", "REMESH"); vx.mode = "VOXEL"; vx.voxel_size = 0.05; bpy.ops.object.modifier_apply(modifier="V")
    reduzir(lc, alvo * 0.90)
    partes = [lc]
    for o in PECAS:
        c = copia(o, "L_" + o.name)
        reduzir(c, alvo * (0.025 if "Orelha" in o.name else 0.012 if "Olho" in o.name else 0.0035))
        partes.append(c)
    b = unir(partes, nome)
    for pl in b.data.polygons: pl.use_smooth = True
    b.data.materials.clear(); triangular(b); return b

# ------------------------------------------------------------------ LOD0
low = corpo_low(10500, "LOW_Corpo")
ativo(low); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.003, area_weight=0.7)
bpy.ops.uv.pack_islands(margin=0.003); bpy.ops.object.mode_set(mode="OBJECT")
pl_low = copia(pel, "LOW_Pelagem"); triangular(pl_low)
cr_low = unir([copia(o, "L_" + o.name) for o in CRIS], "LOW_Cristais"); triangular(cr_low)
print("LOW_TRIS corpo", tris(low), "pelagem", tris(pl_low), "cristais", tris(cr_low))

# ------------------------------------------------------------------ bake HIGH -> LOW_Corpo
mat = bpy.data.materials.new("M_LoboArtico_Corpo_LOW")
if mat.node_tree is None: mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]; low.data.materials.append(mat)
MAPAS = (("cor", "sRGB"), ("normal", "Non-Color"), ("rugosidade", "Non-Color"), ("emissao", "sRGB"))
imgs = {}
for k, cs in MAPAS:
    im = bpy.data.images.new("LoboArtico_" + k, RES, RES, alpha=False); im.colorspace_settings.name = cs
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = im; t.name = k; imgs[k] = (im, t)
sc.render.engine = "CYCLES"; sc.cycles.samples = 16
try:
    bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
    bpy.context.preferences.addons["cycles"].preferences.get_devices(); sc.cycles.device = "GPU"
except Exception as e: print("LOW sem GPU:", e)
for o in sc.objects: o.hide_render = False
pel.hide_render = True; pl_low.hide_render = True                    # cartoes nao entram no AO/bake do corpo
for o in CRIS: o.hide_render = True
cr_low.hide_render = True
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.06; bk.max_ray_distance = 0.25; bk.margin = 8
bpy.ops.object.select_all(action="DESELECT")
for o in [corpo] + PECAS: o.select_set(True)
low.select_set(True); bpy.context.view_layer.objects.active = low
def assar(chave, tipo, **kw):
    for n_ in nt.nodes: n_.select = False
    imgs[chave][1].select = True; nt.nodes.active = imgs[chave][1]
    bpy.ops.object.bake(type=tipo, **kw)
    im = imgs[chave][0]; im.filepath_raw = os.path.join(OUT, "bake%d" % RES, "LoboArtico_%s_%d.png" % (chave, RES)); im.file_format = "PNG"; im.save()
    print("BAKE", chave, flush=True)
bk.use_pass_direct = bk.use_pass_indirect = False; bk.use_pass_color = True
assar("cor", "DIFFUSE", pass_filter={"COLOR"})
assar("normal", "NORMAL")
assar("rugosidade", "ROUGHNESS")
assar("emissao", "EMIT")
# finais 1024 (limite do Roblox para este projeto)
for k, _ in MAPAS:
    im = imgs[k][0]; im.scale(FINAL, FINAL)
    im.filepath_raw = os.path.join(OUT, "LoboArtico_%s.png" % k); im.file_format = "PNG"; im.save()
L = nt.links
L.new(imgs["cor"][1].outputs["Color"], bsdf.inputs["Base Color"])
L.new(imgs["rugosidade"][1].outputs["Color"], bsdf.inputs["Roughness"])
nm = nt.nodes.new("ShaderNodeNormalMap"); L.new(imgs["normal"][1].outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs[0], bsdf.inputs["Normal"])
L.new(imgs["emissao"][1].outputs["Color"], bsdf.inputs["Emission Color"]); bsdf.inputs["Emission Strength"].default_value = 1.0
if "Sheen Weight" in bsdf.inputs: bsdf.inputs["Sheen Weight"].default_value = 0.0
pl_low.hide_render = False; cr_low.hide_render = False                # volta a aparecer nos renders de revisao

# pelagem: atlas 1024 com alpha (sem AO: o Roblox nao tem o no de oclusao)
shutil.copy(os.path.join(AQUI, "tex", "pelo_atlas.png"), os.path.join(OUT, "LoboArtico_pelo_atlas.png"))
mp = bpy.data.materials.new("M_LoboArtico_Pelagem_LOW")
if mp.node_tree is None: mp.use_nodes = True
b2 = mp.node_tree.nodes["Principled BSDF"]; ta = mp.node_tree.nodes.new("ShaderNodeTexImage")
ta.image = bpy.data.images.load(os.path.join(OUT, "LoboArtico_pelo_atlas.png"))
mp.node_tree.links.new(ta.outputs["Color"], b2.inputs["Base Color"]); mp.node_tree.links.new(ta.outputs["Alpha"], b2.inputs["Alpha"])
b2.inputs["Roughness"].default_value = 0.75; mp.surface_render_method = "DITHERED"; mp.use_backface_culling = False
pl_low.data.materials.clear(); pl_low.data.materials.append(mp)
mc = bpy.data.materials.new("M_LoboArtico_Cristal_LOW")
if mc.node_tree is None: mc.use_nodes = True
b3 = mc.node_tree.nodes["Principled BSDF"]; b3.inputs["Base Color"].default_value = (0.55, 0.85, 1.0, 1)
b3.inputs["Alpha"].default_value = 0.62; b3.inputs["Roughness"].default_value = 0.08
b3.inputs["Emission Color"].default_value = (0.45, 0.85, 1.0, 1); b3.inputs["Emission Strength"].default_value = 0.35
mc.surface_render_method = "BLENDED"; mc.use_backface_culling = False
cr_low.data.materials.clear(); cr_low.data.materials.append(mc)

# ------------------------------------------------------------------ LODs (mesmo UV/texturas)
def lod_corpo(alvo, nome):
    c = low.copy(); c.data = low.data.copy(); c.name = nome; sc.collection.objects.link(c)
    ativo(c); d = c.modifiers.new("D", "DECIMATE"); d.ratio = alvo / tris(c); bpy.ops.object.modifier_apply(modifier="D"); return c
lod1 = lod_corpo(4500, "LOD1_Corpo"); lod2 = lod_corpo(1800, "LOD2_Corpo")
import bmesh
p1 = pl_low.copy(); p1.data = pl_low.data.copy(); p1.name = "LOD1_Pelagem"; sc.collection.objects.link(p1)
bm = bmesh.new(); bm.from_mesh(p1.data); bm.faces.ensure_lookup_table()
vistos, apagar = set(), []                                             # cada cartao = componente ligado de faces
for f in bm.faces:
    if f.index in vistos: continue
    pilha, comp = [f], []
    while pilha:
        g = pilha.pop()
        if g.index in vistos: continue
        vistos.add(g.index); comp.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in vistos: pilha.append(h)
    comprimento = max((v.co - w.co).length for g in comp for v in g.verts for w in comp[0].verts)
    if comprimento < 0.95: apagar.extend(comp)                         # LOD1: so as mechas longas da silhueta
bmesh.ops.delete(bm, geom=apagar, context="FACES"); bm.to_mesh(p1.data); bm.free()
p1.hide_render = True
for o in (lod1, lod2): o.hide_render = True

# ------------------------------------------------------------------ export e registro
def exportar(objs, nome):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, nome), export_format="GLB", use_selection=True, export_image_format="AUTO",
                              export_yup=True, export_apply=True)
exportar([low, pl_low, cr_low], "CR_LoboArtico_LOW.glb")
exportar([lod1, p1, cr_low], "CR_LoboArtico_LOD1.glb")
exportar([lod2, cr_low], "CR_LoboArtico_LOD2.glb")
reg = {"LOD0": {"LOW_Corpo": tris(low), "LOW_Pelagem": tris(pl_low), "LOW_Cristais": tris(cr_low)},
       "LOD1": {"LOD1_Corpo": tris(lod1), "LOD1_Pelagem": tris(p1), "LOW_Cristais": tris(cr_low)},
       "LOD2": {"LOD2_Corpo": tris(lod2), "LOW_Cristais": tris(cr_low)},
       "texturas_finais": {k: "LoboArtico_%s.png (%dx%d)" % (k, FINAL, FINAL) for k, _ in MAPAS},
       "atlas_pelagem": "LoboArtico_pelo_atlas.png (1024x1024 RGBA)", "bake_intermediario": RES}
for k in ("LOD0", "LOD1", "LOD2"): reg[k]["total"] = sum(reg[k].values())
json.dump(reg, open(os.path.join(OUT, "custo_lobo_artico.json"), "w"), indent=1)
print("LOW_REGISTRO", json.dumps(reg))
# entrega: o .blend LOW guarda so as malhas de jogo
for o in list(sc.objects):
    if o.type == "MESH" and not o.name.startswith(("LOW_", "LOD1_", "LOD2_")): bpy.data.objects.remove(o)
for o in (lod1, lod2, p1): o.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_LOW.blend"))
print("LOW_OK")
