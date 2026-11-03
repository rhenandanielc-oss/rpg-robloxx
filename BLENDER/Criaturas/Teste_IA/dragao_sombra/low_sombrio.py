"""Malha de JOGO (LOW) do DRAGAO SOMBRIO (copia do low_glacial.py com os nomes SB_ e o fundo dos mapas escuro).
--- texto de origem ---
Malha de JOGO (LOW) do Dragao Glacial r4 (derivado de dragao_novo/low_dragao.py).
Diferencas do CR: o corpo NAO passa por remesh (o voxel fecharia a fenda da boca e perderia o grupo SB_Mandibula):
reducao por Decimate com simetria em X, que preserva a fenda e interpola os pesos. Cada peca rigida ganha um grupo
TAG_* (cabeca / mandibula) para o rig saber a que osso pertence depois do join; a pele interna da boca mantem
SB_Mandibula. Membranas sem espessura (DoubleSided no Roblox). UV unica e bake HIGH->LOW (cor, normal, rugosidade).
Uso: blender -b SB_Dragao_master.blend -P low_sombrio.py -- <saida_dir> [res]"""
import bpy, sys, os, math
args = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(args[0]); RES = int(args[1]) if len(args) > 1 else 2048     # r8: assa em 2048 (o export reduz para 1024)
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
col = bpy.data.collections["SB_Dragao"]; HIGH = [o for o in col.objects if o.type == "MESH"]
corpo = bpy.data.objects["SB_Dragao_Corpo"]
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
d = lc.modifiers.new("D", "DECIMATE"); d.ratio = 18500 / tris(lc)   # (03/11) +3k tris: linha da mandibula/labios sem micro-pontas (Corpo continua < 20k); d.use_symmetry = True; d.symmetry_axis = "X"
d.vertex_group = "DECIMAR"; d.vertex_group_factor = 2.0
bpy.ops.object.modifier_apply(modifier="D"); lc.vertex_groups.remove(lc.vertex_groups["DECIMAR"])
print("LOW corpo tris", tris(lc), "cabeca", sum(1 for p in lc.data.polygons if (lc.matrix_world @ p.center).y < -0.66), "SB_Mandibula", "SB_Mandibula" in lc.vertex_groups)
partes.append(lc)
for o in HIGH:
    if o.name.startswith("SB_Dragao_Membrana"):
        for m in o.modifiers:
            if m.type in ("SOLIDIFY", "SUBSURF"): m.show_viewport = False
        dg.update(); partes.append(copia(o, "LOW_" + o.name))
        for m in o.modifiers: m.show_viewport = True
CABECA = ("Chifre", "Olho", "Espinho_Bochecha", "Espinho_Sobrancelha", "Dente_Sup", "SB_Dragao_Boca_Sup")
MAND = ("Dente_Inf", "SB_Dragao_Boca_Inf")
for o in HIGH:
    if o is corpo or o.name.startswith("SB_Dragao_Membrana"): continue
    c = copia(o, "LOW_" + o.name); n = tris(c)
    alvo = (48 if o.name.startswith("Dente") else 120 if o.name.startswith("Garra") else 70 if o.name.startswith("Espinho") else 150 if o.name.startswith("Chifre")
            else 400 if o.name.startswith("SB_Dragao_Boca") else 160)       # r8: garras/chifres/dentes/olhos com mais faces
    if n > alvo:
        ativo(c); dm = c.modifiers.new("D", "DECIMATE"); dm.ratio = alvo / n; bpy.ops.object.modifier_apply(modifier="D")
    tag = "TAG_cabeca" if o.name.startswith(CABECA) else "TAG_mandibula" if o.name.startswith(MAND) else None
    if tag:
        g = c.vertex_groups.get(tag) or c.vertex_groups.new(name=tag); g.add([v.index for v in c.data.vertices], 1.0, "REPLACE")
    if o.name.startswith("SB_Dragao_Boca_Parede"):   # (03/11) parede interna: cor pintada direto (o bake pega dentes/ceu vizinhos)
        g = c.vertex_groups.get("UV_PAREDE") or c.vertex_groups.new(name="UV_PAREDE"); g.add([v.index for v in c.data.vertices], 1.0, "REPLACE")
    if o.name.startswith(("Dente", "Olho")):   # (03/11) marca dentes/olhos: ganham mais area na UV (senao o bake fica escuro)
        g = c.vertex_groups.get("UV_GRANDE") or c.vertex_groups.new(name="UV_GRANDE"); g.add([v.index for v in c.data.vertices], 1.0, "REPLACE")
    partes.append(c)
for p in partes:
    for pl in p.data.polygons: pl.use_smooth = True
bpy.ops.object.select_all(action="DESELECT")
for p in partes: p.select_set(True)
bpy.context.view_layer.objects.active = lc; bpy.ops.object.join(); low = lc; low.name = "SB_Dragao_LOW"
ativo(low); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
low.data.materials.clear()
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(72), island_margin=0.003, area_weight=0.6)   # r8: menos ilhas minusculas
# (03/11, inspecao da boca) dentes com poucos texels saiam PRETOS no jogo (o bake pegava o labio escuro vizinho):
# as ilhas de UV dos dentes e olhos sao ampliadas x5 antes do empacotamento (que preserva a proporcao entre ilhas)
import bmesh as _bm
bpy.ops.object.mode_set(mode="OBJECT")
_b = _bm.new(); _b.from_mesh(low.data); _uv = _b.loops.layers.uv.active; _dl = _b.verts.layers.deform.active
_gi = low.vertex_groups["UV_GRANDE"].index if "UV_GRANDE" in low.vertex_groups else None
_fs = [f for f in _b.faces if _gi is not None and all(_gi in v[_dl] for v in f.verts)] if _dl else []
_vis = set()
for f in _fs:
    if f.index in _vis: continue
    ilha, st = [], [f]
    while st:
        x = st.pop()
        if x.index in _vis: continue
        _vis.add(x.index); ilha.append(x)
        st += [y for e in x.edges for y in e.link_faces if y.index not in _vis and _gi in y.verts[0][_dl]]
    cs = [l[_uv].uv.copy() for x in ilha for l in x.loops]; c = sum(cs, cs[0] * 0) / len(cs)
    for x in ilha:
        for l in x.loops: l[_uv].uv = c + (l[_uv].uv - c) * 5.0
_b.to_mesh(low.data); _b.free()
print("LOW ilhas UV ampliadas (dentes/olhos):", len(_fs), "faces")
if "UV_GRANDE" in low.vertex_groups: low.vertex_groups.remove(low.vertex_groups["UV_GRANDE"])
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.pack_islands(margin=0.004)
bpy.ops.object.mode_set(mode="OBJECT")
_gp = low.vertex_groups["UV_PAREDE"].index if "UV_PAREDE" in low.vertex_groups else None
TRI_PAREDE = []
if _gp is not None:
    _b = _bm.new(); _b.from_mesh(low.data); _uv = _b.loops.layers.uv.active; _dl = _b.verts.layers.deform.active
    for f in _b.faces:
        if all(_gp in v[_dl] for v in f.verts):
            uvs = [l[_uv].uv.copy() for l in f.loops]
            for k in range(1, len(uvs) - 1): TRI_PAREDE.append((uvs[0], uvs[k], uvs[k + 1]))
    _b.free(); low.vertex_groups.remove(low.vertex_groups["UV_PAREDE"])
print("LOW parede interna triangulos UV", len(TRI_PAREDE))
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.modifier_add(type="TRIANGULATE"); bpy.ops.object.modifier_apply(modifier=low.modifiers[-1].name)
print("LOW_TRIS", len(low.data.polygons), "grupos", [g.name for g in low.vertex_groups])
mat = bpy.data.materials.new("M_SB_Dragao")
if mat.node_tree is None: mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]; low.data.materials.append(mat)
imgs = {}
for k, cs in (("cor", "sRGB"), ("normal", "Non-Color"), ("rugosidade", "Non-Color")):
    im = bpy.data.images.new("SB_Dragao_" + k, RES, RES, alpha=False); im.colorspace_settings.name = cs
    # fundo = cor media da pele / normal neutra: pixel que o bake nao alcanca (triangulo menor que 1 px) nao vira preto
    im.generated_color = {"cor": (0.020, 0.012, 0.030, 1),   # SOMBRIO: fundo = preto-violeta
                          "normal": (0.5, 0.5, 1.0, 1), "rugosidade": (0.62, 0.62, 0.62, 1)}[k]
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
    imgs[chave][0].filepath_raw = os.path.join(OUT, "SB_Dragao_%s.png" % chave); imgs[chave][0].file_format = "PNG"; imgs[chave][0].save()
    print("BAKE", chave)
bk.use_pass_direct = bk.use_pass_indirect = False; bk.use_pass_color = True
assar("cor", "DIFFUSE", pass_filter={"COLOR"})
assar("normal", "NORMAL")
assar("rugosidade", "ROUGHNESS")
# (03/11) parede interna da boca: pinta as ilhas dela (com 2 px de folga) em vermelho escuro de cavidade, normal neutra
import numpy as _np
def _pintar(im, cor):
    W_, H_ = im.size; a_ = _np.array(im.pixels[:], dtype=_np.float32).reshape(H_, W_, 4); n_ = 0
    for t in TRI_PAREDE:
        xs = [p.x * W_ for p in t]; ys = [p.y * H_ for p in t]
        x0, x1 = max(0, int(min(xs)) - 2), min(W_ - 1, int(max(xs)) + 2); y0, y1 = max(0, int(min(ys)) - 2), min(H_ - 1, int(max(ys)) + 2)
        (ax, ay), (bx, by), (cx, cy) = [(p.x * W_, p.y * H_) for p in t]
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(d) < 1e-9: continue
        for yy in range(y0, y1 + 1):
            for xx in range(x0, x1 + 1):
                px_, py_ = xx + 0.5, yy + 0.5
                l1 = ((by - cy) * (px_ - cx) + (cx - bx) * (py_ - cy)) / d; l2 = ((cy - ay) * (px_ - cx) + (ax - cx) * (py_ - cy)) / d
                m_ = 2.5 / max(1.0, (abs(d) ** 0.5))
                if l1 >= -m_ and l2 >= -m_ and 1 - l1 - l2 >= -m_: a_[yy, xx, :3] = cor; n_ += 1
    im.pixels.foreach_set(a_.ravel()); im.save(); return n_
if TRI_PAREDE:
    print("LOW parede pixels", _pintar(imgs["cor"][0], (0.26, 0.05, 0.09)), _pintar(imgs["normal"][0], (0.5, 0.5, 1.0)), _pintar(imgs["rugosidade"][0], (0.35, 0.35, 0.35)))
L = nt.links
L.new(imgs["cor"][1].outputs["Color"], bsdf.inputs["Base Color"])
L.new(imgs["rugosidade"][1].outputs["Color"], bsdf.inputs["Roughness"])
nm = nt.nodes.new("ShaderNodeNormalMap"); L.new(imgs["normal"][1].outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs[0], bsdf.inputs["Normal"])
for im, _ in imgs.values(): im.pack()
for o in HIGH: o.hide_render = True; o.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "SB_Dragao_LOW.blend"))
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 1280, 720
from mathutils import Vector as V
cam = sc.camera
for nome, pos, alvo, lente in (("34_frente", V((-2.4, -3.6, 1.3)), V((0, -0.15, 0.5)), 42), ("cabeca", V((-0.85, -1.78, 1.38)), V((0, -0.85, 1.13)), 62),
                               ("lado", V((-6.4, 0.55, 0.85)), V((0, 0.55, 0.6)), 42)):
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lente
    sc.render.filepath = os.path.join(OUT, "low_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("LOW_OK")
