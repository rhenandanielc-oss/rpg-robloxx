"""Malha de jogo (LOW) do Lobo Ancestral a partir da HIGH do Meshy em pose neutra: solda costuras -> decimacao (alvo de
tris) -> UV nova (Smart UV) -> bake Cycles HIGH->LOW de cor (difusa) e normal -> 1024 px -> GLB.
Uma MeshPart <= 20k tris (limite do Roblox); textura 1024 (celular). A HIGH nao e alterada.
Uso: blender -b <endireitado.blend> -P low_lobo.py -- <saida_dir> [alvo_tris=18000] [bake_px=2048]"""
import bpy, bmesh, sys, os, math, time
A = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
ALVO = int(A[1]) if len(A) > 1 else 18000; PX = int(A[2]) if len(A) > 2 else 2048
sc = bpy.context.scene; t0 = time.time()
HI = bpy.data.objects["Lobo_Meshy"]
LO = HI.copy(); LO.data = HI.data.copy(); LO.name = LO.data.name = "Lobo_Ancestral_LOW"; sc.collection.objects.link(LO)
for o in sc.objects: o.select_set(False)
bpy.context.view_layer.objects.active = LO; LO.select_set(True)
bm = bmesh.new(); bm.from_mesh(LO.data)
n0 = len(bm.verts); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
print("SOLDA", n0, "->", len(bm.verts)); bm.to_mesh(LO.data); bm.free()
tris0 = sum(len(p.vertices) - 2 for p in LO.data.polygons)
dec = LO.modifiers.new("Dec", "DECIMATE"); dec.decimate_type = "COLLAPSE"; dec.ratio = ALVO / tris0; dec.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier=dec.name)
me = LO.data
bm = bmesh.new(); bm.from_mesh(me)                              # limpeza: faces degeneradas e soltas minusculas
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=0.0002)
bmesh.ops.triangulate(bm, faces=bm.faces)
bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth = True
tris = len(me.polygons); print("LOW_TRIS", tris, "(de", tris0, ")", round(time.time() - t0), "s")
# UV nova
while me.uv_layers: me.uv_layers.remove(me.uv_layers[0])
me.uv_layers.new(name="UVMap")
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.003, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
bpy.ops.object.mode_set(mode="OBJECT")
# mais texels no rosto: ilhas da cabeca (frente do pescoco para a frente, acima do peito) crescem K_ROSTO antes do pack
K_ROSTO = 2.2
ys_ = [v.co.y for v in me.vertices]; y_cab = min(ys_) + 0.17 * (max(ys_) - min(ys_)); z_cab = 0.70 * max(v.co.z for v in me.vertices)
bm = bmesh.new(); bm.from_mesh(me); uvl = bm.loops.layers.uv.active; bm.faces.ensure_lookup_table()
vist, n_cab = set(), 0
for f0 in bm.faces:
    if f0.index in vist: continue
    ilha, pilha = [], [f0]; vist.add(f0.index)
    while pilha:                                                  # ilha UV = faces ligadas por arestas com UV continua
        f = pilha.pop(); ilha.append(f)
        for lp in f.loops:
            e = lp.edge
            for f2 in e.link_faces:
                if f2.index in vist: continue
                l2 = [l for l in f2.loops if l.edge is e][0]
                a1, b1 = lp[uvl].uv, lp.link_loop_next[uvl].uv; a2, b2 = l2.link_loop_next[uvl].uv, l2[uvl].uv
                if (a1 - a2).length < 1e-5 and (b1 - b2).length < 1e-5: vist.add(f2.index); pilha.append(f2)
    c3 = sum((f.calc_center_median() for f in ilha), bmesh.types.BMVert.__mro__[0] and __import__("mathutils").Vector()) / len(ilha)
    if c3.y < y_cab and c3.z > z_cab:
        n_cab += 1; luv = [l[uvl] for f in ilha for l in f.loops]
        cu = sum((l.uv for l in luv), __import__("mathutils").Vector((0, 0))) / len(luv)
        for l in luv: l.uv = cu + (l.uv - cu) * K_ROSTO
bm.to_mesh(me); bm.free(); print("UV_ILHAS_CABECA", n_cab, "x", K_ROSTO)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.pack_islands(margin=0.003, rotate=True, scale=True)
bpy.ops.object.mode_set(mode="OBJECT")
bm = bmesh.new(); bm.from_mesh(me)
print("BORDAS_ABERTAS", sum(1 for e in bm.edges if e.is_boundary), "NAO_MANIFOLD", sum(1 for e in bm.edges if not e.is_manifold), "de", len(bm.edges))
bm.free()
# material e imagens de bake
while me.materials: me.materials.pop()
mat = bpy.data.materials.new("M_Lobo_Ancestral")
if mat.node_tree is None: mat.use_nodes = True
nt = mat.node_tree; bs = nt.nodes["Principled BSDF"]; me.materials.append(mat)
def imagem(nome, cor):
    im = bpy.data.images.new(nome, PX, PX, alpha=False, float_buffer=False)
    if not cor: im.colorspace_settings.name = "Non-Color"
    return im
I_COR, I_NOR = imagem("T_Lobo_Cor", True), imagem("T_Lobo_Normal", False)
tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = I_COR
texn = nt.nodes.new("ShaderNodeTexImage"); texn.image = I_NOR
nm = nt.nodes.new("ShaderNodeNormalMap")
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 4
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.04; bk.max_ray_distance = 0.25; bk.margin = 8
for o in sc.objects: o.select_set(False)
HI.select_set(True); LO.select_set(True); bpy.context.view_layer.objects.active = LO
for im, tipo in ((I_COR, "DIFFUSE"), (I_NOR, "NORMAL")):
    for nd in nt.nodes: nd.select = False
    alvo = tex if im is I_COR else texn; alvo.select = True; nt.nodes.active = alvo
    if tipo == "DIFFUSE":
        bk.use_pass_direct = False; bk.use_pass_indirect = False; bk.use_pass_color = True
    t1 = time.time(); bpy.ops.object.bake(type=tipo); print("BAKE", tipo, round(time.time() - t1), "s")
    im.filepath_raw = os.path.join(OUT, im.name + "_%d.png" % PX); im.file_format = "PNG"; im.save()
# versoes 1024 para o jogo
for im in (I_COR, I_NOR):
    if PX != 1024: im.scale(1024, 1024)
    im.filepath_raw = os.path.join(OUT, im.name + ".png"); im.save()
nt.links.new(tex.outputs["Color"], bs.inputs["Base Color"])
nt.links.new(texn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], bs.inputs["Normal"])
bs.inputs["Roughness"].default_value = 0.82
if "Specular IOR Level" in bs.inputs: bs.inputs["Specular IOR Level"].default_value = 0.3
HI.hide_render = True; HI.hide_set(True)
sc.render.engine = "BLENDER_EEVEE"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_LOW.blend"))
for o in sc.objects: o.select_set(False)
LO.select_set(True); bpy.context.view_layer.objects.active = LO
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "Lobo_Ancestral_LOW.glb"), use_selection=True, export_format="GLB",
                          export_image_format="AUTO", export_yup=True, export_apply=True)
print("LOW_OK tris", tris, "materiais", len(me.materials), "uv", len(me.uv_layers), "tempo", round(time.time() - t0), "s")
