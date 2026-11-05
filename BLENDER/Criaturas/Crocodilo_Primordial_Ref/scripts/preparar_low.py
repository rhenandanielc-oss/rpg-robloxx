"""Malha de jogo (LOW) do Crocodilo Primordial a partir do Meshy normalizado (CR_Crocodilo_Meshy_v2.blend, 32 studs).
1) correcao de cor na HIGH por mascara de geometria (ventre/flanco baixo creme -> ocre terroso da referencia; faixa
   rosada sob a mandibula -> pele); dentes, garras e boca ficam fora da mascara.
2) LOW: solda as costuras de UV ANTES de reduzir (licao do Silverwing), Decimate ate ~TRIS, UV nova (Smart UV).
3) bake Cycles HIGH -> LOW: cor (sem luz), normal (tangente) e rugosidade. Salva 2048 (mestre) e 1024 (Roblox).
Uso: blender -b CR_Crocodilo_Meshy_v2.blend -P preparar_low.py -- <saida_dir> [tris=19000] [res=2048]"""
import bpy, bmesh, sys, os, math, time
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(A[0]); TRIS = int(A[1]) if len(A) > 1 else 19000; RES = int(A[2]) if len(A) > 2 else 2048
os.makedirs(os.path.join(OUT, "tex"), exist_ok=True)
sc = bpy.context.scene; hi = bpy.data.objects["CR_Croc_Meshy"]; me = hi.data
t0 = time.time()
def suave(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)

# ------------------------------------------------------------------ 1) mascara na HIGH (normais lidas uma vez, numpy)
n = len(me.vertices)
co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
nr = np.empty(n * 3); me.vertex_normals.foreach_get("vector", nr); nr = nr.reshape(-1, 3)
x, y, z, nz = co[:, 0], co[:, 1], co[:, 2], nr[:, 2]
# base da cabeca por fatia de y (para achar a parte de baixo da mandibula)
bins = np.floor(y / 0.25).astype(int); zmin = {}
for b in np.unique(bins[y < -9.5]):
    sel = (bins == b) & (np.abs(x) < 1.6)
    if sel.any(): zmin[b] = z[sel].min()
base_cab = np.array([zmin.get(b, -9) for b in bins])
cab = y < -10.0
ventre = suave((-0.12 - nz) / 0.35) * (~cab)
flanco = suave((0.35 - nz) / 0.4) * suave((2.4 - z) / 0.6) * (~cab) * 0.65
mand_ext = cab & (z < base_cab + 0.75) & (nz < 0.25)
mand = suave((0.25 - nz) / 0.5) * mand_ext * 0.8
R = np.maximum(np.maximum(ventre, flanco), mand) * suave((z - 0.55) / 0.3)       # sem pes/garras
G = (cab & (z < base_cab + 0.45) & (nz < -0.3)).astype(float)                    # faixa rosada sob a mandibula
print("MASCARA ventre/flanco/mandibula: verts com peso >0,5:", int((R > 0.5).sum()), " faixa rosada:", int(G.sum()), "de", n)
att = me.color_attributes.new("mascara", "FLOAT_COLOR", "POINT")
cols = np.zeros((n, 4)); cols[:, 0] = R; cols[:, 1] = G; cols[:, 3] = 1
att.data.foreach_set("color", cols.ravel())

mat = me.materials[0]; nt = mat.node_tree; L = nt.links
bsdf = next(nd for nd in nt.nodes if nd.type == "BSDF_PRINCIPLED")
lk = bsdf.inputs["Base Color"].links[0]; tex_out = lk.from_socket
def nn(t, **kw):
    x_ = nt.nodes.new(t)
    for k, v in kw.items(): setattr(x_, k, v)
    return x_
def mr(ent, a, b, c=0.0, d=1.0):
    m = nn("ShaderNodeMapRange"); m.inputs[1].default_value = a; m.inputs[2].default_value = b
    m.inputs[3].default_value = c; m.inputs[4].default_value = d; L.new(ent, m.inputs[0]); return m.outputs[0]
def op(o, a, b=None, v=None):
    m = nn("ShaderNodeMath", operation=o); L.new(a, m.inputs[0])
    if b is not None: L.new(b, m.inputs[1])
    if v is not None: m.inputs[1].default_value = v
    return m.outputs[0]
def mix(f, a, b, tipo="MIX"):
    m = nn("ShaderNodeMix", data_type="RGBA", blend_type=tipo); L.new(f, m.inputs["Factor"])
    for i, c in ((6, a), (7, b)):
        if isinstance(c, tuple): m.inputs[i].default_value = c
        else: L.new(c, m.inputs[i])
    return m.outputs[2]
ca = nn("ShaderNodeVertexColor"); ca.layer_name = "mascara"; sm = nn("ShaderNodeSeparateColor"); L.new(ca.outputs["Color"], sm.inputs[0])
hsv = nn("ShaderNodeSeparateColor", mode="HSV"); L.new(tex_out, hsv.inputs[0])
rgb = nn("ShaderNodeSeparateColor"); L.new(tex_out, rgb.inputs[0])
creme = op("MULTIPLY", mr(hsv.outputs[1], 0.40, 0.12), mr(hsv.outputs[2], 0.25, 0.55))     # pouco saturado e claro
tint = nn("ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); tint.inputs["Factor"].default_value = 1.0
L.new(tex_out, tint.inputs[6]); tint.inputs[7].default_value = (0.86, 0.58, 0.28, 1)                  # ocre terroso
c1 = mix(op("MULTIPLY", creme, sm.outputs[0]), tex_out, tint.outputs[2])
rosa = mr(op("SUBTRACT", rgb.outputs[0], rgb.outputs[1]), 0.03, 0.12)
lum = nn("ShaderNodeRGBToBW"); L.new(tex_out, lum.inputs[0])
alvo = nn("ShaderNodeCombineColor"); L.new(op("MULTIPLY", lum.outputs[0], v=1.05), alvo.inputs[0])
L.new(op("MULTIPLY", lum.outputs[0], v=0.80), alvo.inputs[1]); L.new(op("MULTIPLY", lum.outputs[0], v=0.48), alvo.inputs[2])
c2 = mix(op("MULTIPLY", rosa, sm.outputs[1]), c1, alvo.outputs[0])
hs = nn("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = 1.15; hs.inputs["Value"].default_value = 0.93
L.new(c2, hs.inputs["Color"])                                        # paleta geral mais saturada e escura (referencia)
L.remove(lk); L.new(hs.outputs[0], bsdf.inputs["Base Color"])
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)             # HIGH corrigida (v2; o v1 nao e tocado)
print("HIGH_CORRIGIDA salva", round(time.time() - t0, 1), "s")

# ------------------------------------------------------------------ 2) LOW
lo = hi.copy(); lo.data = hi.data.copy(); lo.name = "CR_Croc_LOW"; sc.collection.objects.link(lo)
bm = bmesh.new(); bm.from_mesh(lo.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.003)
bm.to_mesh(lo.data); bm.free()
for a in list(lo.data.color_attributes): lo.data.color_attributes.remove(a)
tri0 = sum(len(p.vertices) - 2 for p in lo.data.polygons)
dc = lo.modifiers.new("Reduz", "DECIMATE"); dc.ratio = TRIS / tri0; dc.use_collapse_triangulate = True
for o in sc.objects: o.select_set(False)
bpy.context.view_layer.objects.active = lo; lo.select_set(True)
bpy.ops.object.modifier_apply(modifier=dc.name)
while lo.data.uv_layers: lo.data.uv_layers.remove(lo.data.uv_layers[0])
lo.data.uv_layers.new(name="UV")
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003, scale_to_bounds=True)
bpy.ops.object.mode_set(mode="OBJECT")
for p in lo.data.polygons: p.use_smooth = True
tri1 = sum(len(p.vertices) - 2 for p in lo.data.polygons)
print("LOW tris", tri1, "(de", tri0, ") verts", len(lo.data.vertices), round(time.time() - t0, 1), "s")

# material da LOW: imagens de bake
lm = bpy.data.materials.new("M_Croc_LOW"); lm.use_nodes = True
lo.data.materials.clear(); lo.data.materials.append(lm)
lnt = lm.node_tree; lb = lnt.nodes["Principled BSDF"]
IMGS = {}
for nome, cs in (("cor", "sRGB"), ("normal", "Non-Color"), ("rugosidade", "Non-Color")):
    im = bpy.data.images.new("CR_Croc_%s" % nome, RES, RES, alpha=False, float_buffer=(nome == "normal"))
    im.colorspace_settings.name = cs; IMGS[nome] = im
    nd = lnt.nodes.new("ShaderNodeTexImage"); nd.image = im; nd.name = nome
nm = lnt.nodes.new("ShaderNodeNormalMap")
lnt.links.new(lnt.nodes["cor"].outputs["Color"], lb.inputs["Base Color"])
lnt.links.new(lnt.nodes["rugosidade"].outputs["Color"], lb.inputs["Roughness"])
lnt.links.new(lnt.nodes["normal"].outputs["Color"], nm.inputs["Color"]); lnt.links.new(nm.outputs[0], lb.inputs["Normal"])

# ------------------------------------------------------------------ 3) bake HIGH -> LOW
sc.render.engine = "CYCLES"; sc.cycles.samples = 4
try:
    pr = bpy.context.preferences.addons["cycles"].preferences
    for t in ("OPTIX", "CUDA", "HIP", "ONEAPI"):
        try:
            pr.compute_device_type = t; pr.get_devices()
            if any(d.type == t for d in pr.devices):
                for d in pr.devices: d.use = True
                sc.cycles.device = "GPU"; print("BAKE GPU", t); break
        except Exception: pass
except Exception: pass
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.06; bk.max_ray_distance = 0.4; bk.margin = 8
for o in sc.objects: o.select_set(False)
hi.select_set(True); lo.select_set(True); bpy.context.view_layer.objects.active = lo
def bake(nome, tipo, **kw):
    for nd in lnt.nodes: nd.select = False
    lnt.nodes[nome].select = True; lnt.nodes.active = lnt.nodes[nome]
    t = time.time(); bpy.ops.object.bake(type=tipo, **kw); print("BAKE", nome, round(time.time() - t, 1), "s", flush=True)
    im = IMGS[nome]
    im.filepath_raw = os.path.join(OUT, "tex", "CR_Croc_%s_%d.png" % (nome, RES)); im.file_format = "PNG"; im.save()
bake("cor", "DIFFUSE", pass_filter={"COLOR"})
bake("normal", "NORMAL", normal_space="TANGENT")
bake("rugosidade", "ROUGHNESS")
for nome, im in IMGS.items():                                       # versao Roblox 1024
    c = im.copy(); c.scale(1024, 1024); c.filepath_raw = os.path.join(OUT, "tex", "CR_Croc_%s_1024.png" % nome); c.file_format = "PNG"; c.save()
    bpy.data.images.remove(c)
# arquivo LOW proprio (sem a HIGH)
bpy.data.objects.remove(hi, do_unlink=True)
for im in IMGS.values(): im.filepath = im.filepath_raw; im.source = "FILE"
sc.render.engine = "BLENDER_EEVEE"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Crocodilo_LOW.blend"))
print("LOW_OK", round(time.time() - t0, 1), "s")
