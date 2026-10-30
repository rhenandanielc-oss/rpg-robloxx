"""Malha de JOGO (LOW) do CR_Dragao a partir do master v12: corpo retopologizado (Quadriflow, quads com simetria),
membranas sem espessura (DoubleSided no Roblox), pecas rigidas reduzidas; tudo unido com UV unica e mapas assados
do master (cor, normal, rugosidade) -> GLB pronto para o Roblox e para o AI Texturing do Meshy.
Uso: blender -b CR_Dragao_master.blend -P low_dragao.py -- <saida_dir> [res]"""
import bpy, sys, os, math
args = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(args[0]); RES = int(args[1]) if len(args) > 1 else 2048
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
col = bpy.data.collections["CR_Dragao"]; HIGH = [o for o in col.objects if o.type == "MESH"]
corpo = bpy.data.objects["CR_Dragao_Corpo"]
def ativo(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
def copia(o, nome):
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); c = bpy.data.objects.new(nome, me)
    c.matrix_world = o.matrix_world.copy(); sc.collection.objects.link(c); return c
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
partes = []
# corpo: retopologia em quads com simetria (fluxo de arestas melhor para dobrar no rig que o remesh voxel)
lc = copia(corpo, "LOW_Corpo"); ativo(lc)
vx = lc.modifiers.new("V", "REMESH"); vx.mode = "VOXEL"; vx.voxel_size = 0.0075; bpy.ops.object.modifier_apply(modifier="V")   # malha fechada p/ Quadriflow
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT"); print("LOW voxel", len(lc.data.polygons))
try:
    bpy.ops.object.quadriflow_remesh(use_mesh_symmetry=True, use_preserve_sharp=False, use_preserve_boundary=False,
                                     smooth_normals=True, mode="FACES", target_faces=7600, seed=3)
    print("LOW quadriflow", len(lc.data.polygons))
    if len(lc.data.polygons) > 12000: raise RuntimeError("quadriflow nao reduziu")
except Exception as e:
    print("LOW quadriflow falhou:", e); d = lc.modifiers.new("D", "DECIMATE"); d.ratio = 11500 / tris(lc); bpy.ops.object.modifier_apply(modifier="D")   # total <= 20k tris (limite de MeshPart do Roblox)
partes.append(lc)
# membranas: grade original sem Solidify/Subsurf (o Roblox desenha os dois lados)
for o in HIGH:
    if o.name.startswith("CR_Dragao_Membrana"):
        mods = [(m.name, m.show_viewport) for m in o.modifiers]
        for m in o.modifiers:
            if m.type in ("SOLIDIFY", "SUBSURF"): m.show_viewport = False
        dg.update(); c = copia(o, "LOW_" + o.name); partes.append(c)
        for m in o.modifiers: m.show_viewport = True
# pecas rigidas: avaliadas e reduzidas
rig = [o for o in HIGH if o is not corpo and not o.name.startswith("CR_Dragao_Membrana")]
for o in rig:
    c = copia(o, "LOW_" + o.name); n = tris(c)
    alvo = 60 if o.name.startswith(("Garra", "Espinho")) else (200 if o.name.startswith("Chifre") else 80)
    if n > alvo:
        ativo(c); d = c.modifiers.new("D", "DECIMATE"); d.ratio = alvo / n; bpy.ops.object.modifier_apply(modifier="D")
    partes.append(c)
for p in partes:
    for pl in p.data.polygons: pl.use_smooth = True
# une tudo, UV unica
bpy.ops.object.select_all(action="DESELECT")
for p in partes: p.select_set(True)
bpy.context.view_layer.objects.active = lc; bpy.ops.object.join(); low = lc; low.name = "CR_Dragao_LOW"
ativo(low); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
low.data.materials.clear()
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(55), island_margin=0.004, area_weight=0.6)
bpy.ops.uv.pack_islands(margin=0.004)
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.modifier_add(type="TRIANGULATE"); bpy.ops.object.modifier_apply(modifier=low.modifiers[-1].name)
print("LOW_TRIS", len(low.data.polygons))
# material de bake
mat = bpy.data.materials.new("M_CR_Dragao")
if mat.node_tree is None: mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]; low.data.materials.append(mat)
imgs = {}
for k, cs in (("cor", "sRGB"), ("normal", "Non-Color"), ("rugosidade", "Non-Color")):
    im = bpy.data.images.new("CR_Dragao_" + k, RES, RES, alpha=False); im.colorspace_settings.name = cs
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = im; t.name = k; imgs[k] = (im, t)
sc.render.engine = "CYCLES"; sc.cycles.samples = 8
try: sc.cycles.device = "GPU"
except Exception: pass
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.012; bk.max_ray_distance = 0.04; bk.margin = 12
for o in sc.objects: o.hide_render = False
bpy.ops.object.select_all(action="DESELECT")
for o in HIGH: o.select_set(True)
low.select_set(True); bpy.context.view_layer.objects.active = low
def assar(chave, tipo, **kw):
    for n_ in nt.nodes: n_.select = False
    imgs[chave][1].select = True; nt.nodes.active = imgs[chave][1]
    bpy.ops.object.bake(type=tipo, **kw)
    imgs[chave][0].filepath_raw = os.path.join(OUT, "CR_Dragao_%s.png" % chave); imgs[chave][0].file_format = "PNG"; imgs[chave][0].save()
    print("BAKE", chave)
bk.use_pass_direct = bk.use_pass_indirect = False; bk.use_pass_color = True
assar("cor", "DIFFUSE", pass_filter={"COLOR"})
assar("normal", "NORMAL")
assar("rugosidade", "ROUGHNESS")
# liga os mapas no material de entrega
L = nt.links
L.new(imgs["cor"][1].outputs["Color"], bsdf.inputs["Base Color"])
L.new(imgs["rugosidade"][1].outputs["Color"], bsdf.inputs["Roughness"])
nm = nt.nodes.new("ShaderNodeNormalMap"); L.new(imgs["normal"][1].outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs[0], bsdf.inputs["Normal"])
# entrega: so a LOW
for o in HIGH: o.hide_render = True; o.hide_set(True)
bpy.ops.object.select_all(action="DESELECT"); low.select_set(True); bpy.context.view_layer.objects.active = low
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "CR_Dragao_LOW.glb"), export_format="GLB", use_selection=True, export_image_format="AUTO")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Dragao_LOW.blend"))
# revisao em EEVEE: LOW texturizada
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 1280, 720
from mathutils import Vector as V
cam = sc.camera
for nome, pos, alvo, lente in (("34_frente", V((-2.4, -3.6, 1.3)), V((0, -0.15, 0.5)), 42), ("cabeca", V((-0.85, -1.75, 1.02)), V((0, -0.82, 0.77)), 62),
                               ("34_tras", V((2.9, 3.4, 2.0)), V((0, 0.1, 0.55)), 42)):
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lente
    sc.render.filepath = os.path.join(OUT, "low_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("LOW_OK")
