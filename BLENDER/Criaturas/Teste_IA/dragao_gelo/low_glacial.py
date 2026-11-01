"""Malha de JOGO (LOW) do Dragao Glacial r4 (derivado de dragao_novo/low_dragao.py).
Diferencas do CR: o corpo NAO passa por remesh (o voxel fecharia a fenda da boca e perderia o grupo GL_Mandibula):
reducao por Decimate com simetria em X, que preserva a fenda e interpola os pesos. Cada peca rigida ganha um grupo
TAG_* (cabeca / mandibula) para o rig saber a que osso pertence depois do join; a pele interna da boca mantem
GL_Mandibula. Membranas sem espessura (DoubleSided no Roblox). UV unica e bake HIGH->LOW (cor, normal, rugosidade).
Uso: blender -b GL_Dragao_master.blend -P low_glacial.py -- <saida_dir> [res]"""
import bpy, sys, os, math
args = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(args[0]); RES = int(args[1]) if len(args) > 1 else 2048     # r8: assa em 2048 (o export reduz para 1024)
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
col = bpy.data.collections["GL_Dragao"]; HIGH = [o for o in col.objects if o.type == "MESH"]
corpo = bpy.data.objects["GL_Dragao_Corpo"]
def ativo(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
def copia(o, nome):
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    c = bpy.data.objects.new(nome, me); c.matrix_world = o.matrix_world.copy(); sc.collection.objects.link(c)
    for g in o.vertex_groups:
        if g.name not in c.vertex_groups: c.vertex_groups.new(name=g.name)
    return c
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
partes = []
lc = copia(corpo, "LOW_Corpo"); ativo(lc)
# r8: a CABECA (rosto, boca, olhos) fica mais densa que o resto: o peso do grupo DECIMAR controla quanto cada parte
# reduz (1 = reduz muito, ~0 = preserva). Antes o rosto ficava facetado e o bake deixava triangulos pretos
gd = lc.vertex_groups.new(name="DECIMAR")
for v in lc.data.vertices:
    y = (lc.matrix_world @ v.co).y
    gd.add([v.index], 0.08 + 0.92 * max(0.0, min(1.0, (y + 0.66) / 0.10)), "REPLACE")
d = lc.modifiers.new("D", "DECIMATE"); d.ratio = 15500 / tris(lc); d.use_symmetry = True; d.symmetry_axis = "X"
d.vertex_group = "DECIMAR"; d.vertex_group_factor = 2.0
bpy.ops.object.modifier_apply(modifier="D"); lc.vertex_groups.remove(lc.vertex_groups["DECIMAR"])
print("LOW corpo tris", tris(lc), "cabeca", sum(1 for p in lc.data.polygons if (lc.matrix_world @ p.center).y < -0.66), "GL_Mandibula", "GL_Mandibula" in lc.vertex_groups)
partes.append(lc)
for o in HIGH:
    if o.name.startswith("GL_Dragao_Membrana"):
        for m in o.modifiers:
            if m.type in ("SOLIDIFY", "SUBSURF"): m.show_viewport = False
        dg.update(); partes.append(copia(o, "LOW_" + o.name))
        for m in o.modifiers: m.show_viewport = True
CABECA = ("Chifre", "Olho", "Espinho_Bochecha", "Espinho_Sobrancelha", "Dente_Sup", "GL_Dragao_Boca_Sup")
MAND = ("Dente_Inf", "GL_Dragao_Boca_Inf")
for o in HIGH:
    if o is corpo or o.name.startswith("GL_Dragao_Membrana"): continue
    c = copia(o, "LOW_" + o.name); n = tris(c)
    alvo = (48 if o.name.startswith("Dente") else 120 if o.name.startswith("Garra") else 70 if o.name.startswith("Espinho") else 150 if o.name.startswith("Chifre")
            else 400 if o.name.startswith("GL_Dragao_Boca") else 160)       # r8: garras/chifres/dentes/olhos com mais faces
    if n > alvo:
        ativo(c); dm = c.modifiers.new("D", "DECIMATE"); dm.ratio = alvo / n; bpy.ops.object.modifier_apply(modifier="D")
    tag = "TAG_cabeca" if o.name.startswith(CABECA) else "TAG_mandibula" if o.name.startswith(MAND) else None
    if tag:
        g = c.vertex_groups.get(tag) or c.vertex_groups.new(name=tag); g.add([v.index for v in c.data.vertices], 1.0, "REPLACE")
    partes.append(c)
for p in partes:
    for pl in p.data.polygons: pl.use_smooth = True
bpy.ops.object.select_all(action="DESELECT")
for p in partes: p.select_set(True)
bpy.context.view_layer.objects.active = lc; bpy.ops.object.join(); low = lc; low.name = "GL_Dragao_LOW"
ativo(low); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
low.data.materials.clear()
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(72), island_margin=0.003, area_weight=0.6)   # r8: menos ilhas minusculas
bpy.ops.uv.pack_islands(margin=0.004)
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.modifier_add(type="TRIANGULATE"); bpy.ops.object.modifier_apply(modifier=low.modifiers[-1].name)
print("LOW_TRIS", len(low.data.polygons), "grupos", [g.name for g in low.vertex_groups])
mat = bpy.data.materials.new("M_GL_Dragao")
if mat.node_tree is None: mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]; low.data.materials.append(mat)
imgs = {}
for k, cs in (("cor", "sRGB"), ("normal", "Non-Color"), ("rugosidade", "Non-Color")):
    im = bpy.data.images.new("GL_Dragao_" + k, RES, RES, alpha=False); im.colorspace_settings.name = cs
    # fundo = cor media da pele / normal neutra: pixel que o bake nao alcanca (triangulo menor que 1 px) nao vira preto
    im.generated_color = {"cor": (0.42, 0.56, 0.76, 1), "normal": (0.5, 0.5, 1.0, 1), "rugosidade": (0.62, 0.62, 0.62, 1)}[k]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = im; t.name = k; imgs[k] = (im, t)
sc.render.engine = "CYCLES"; sc.cycles.samples = 8
try: sc.cycles.device = "GPU"
except Exception: pass
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.012; bk.max_ray_distance = 0.05; bk.use_clear = False   # mantem o fundo (cor media) onde o bake nao alcanca; bk.margin = 8
for o in sc.objects: o.hide_render = False
bpy.ops.object.select_all(action="DESELECT")
for o in HIGH: o.select_set(True)
low.select_set(True); bpy.context.view_layer.objects.active = low
def assar(chave, tipo, **kw):
    for n_ in nt.nodes: n_.select = False
    imgs[chave][1].select = True; nt.nodes.active = imgs[chave][1]
    bpy.ops.object.bake(type=tipo, **kw)
    imgs[chave][0].filepath_raw = os.path.join(OUT, "GL_Dragao_%s.png" % chave); imgs[chave][0].file_format = "PNG"; imgs[chave][0].save()
    print("BAKE", chave)
bk.use_pass_direct = bk.use_pass_indirect = False; bk.use_pass_color = True
assar("cor", "DIFFUSE", pass_filter={"COLOR"})
assar("normal", "NORMAL")
assar("rugosidade", "ROUGHNESS")
L = nt.links
L.new(imgs["cor"][1].outputs["Color"], bsdf.inputs["Base Color"])
L.new(imgs["rugosidade"][1].outputs["Color"], bsdf.inputs["Roughness"])
nm = nt.nodes.new("ShaderNodeNormalMap"); L.new(imgs["normal"][1].outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs[0], bsdf.inputs["Normal"])
for im, _ in imgs.values(): im.pack()
for o in HIGH: o.hide_render = True; o.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "GL_Dragao_LOW.blend"))
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 1280, 720
from mathutils import Vector as V
cam = sc.camera
for nome, pos, alvo, lente in (("34_frente", V((-2.4, -3.6, 1.3)), V((0, -0.15, 0.5)), 42), ("cabeca", V((-0.85, -1.78, 1.38)), V((0, -0.85, 1.13)), 62),
                               ("lado", V((-6.4, 0.55, 0.85)), V((0, 0.55, 0.6)), 42)):
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lente
    sc.render.filepath = os.path.join(OUT, "low_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("LOW_OK")
