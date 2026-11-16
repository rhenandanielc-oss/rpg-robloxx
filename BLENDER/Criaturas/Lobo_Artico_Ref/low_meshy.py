"""Malha de JOGO do Lobo Artico a partir do Meshy em pose neutra (meshy_neutro.py). Sem rig (vem depois da aprovacao).
- LOW_Corpo: remesh voxel (malha fechada e densidade uniforme, boa para deformar) -> decimate <= ~19k tris; UV unica;
  bake do HIGH Meshy (cor, normal, rugosidade) + EMISSAO so na marca do ombro ESQUERDO (mascara ciano da textura
  do Meshy restrita a uma caixa achada pelas proprias amostras ciano do lado +X) -> 2048 intermediario, 1024 final.
- LOW_Cristais: cristais translucidos proprios (as "placas" do Meshy ficam como pelo gelado), presos ao dorso por raio.
- LOD1 / LOD2 do corpo. GLB + custo JSON.
Uso: blender -b meshy/CR_LoboArtico_meshy_neutro.blend -P low_meshy.py -- <saida_dir> [res] [alvo_tris]"""
import bpy, bmesh, sys, os, math, json, random
import numpy as np
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); RES = int(a[1]) if len(a) > 1 else 2048
ALVO = int(a[2]) if len(a) > 2 else 19000; FINAL = 1024; rnd = random.Random(3)
os.makedirs(os.path.join(OUT, "bake%d" % RES), exist_ok=True)
sc = bpy.context.scene
hi_ob = bpy.data.objects["CR_LoboArtico_Meshy"]; me = hi_ob.data
def ativo(o):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

# ------------------------------------------------------------------ marca: caixa no ombro esquerdo achada pelas amostras ciano
mat_hi = me.materials[0]; nt_hi = mat_hi.node_tree
_b = next(n for n in nt_hi.nodes if n.type == "BSDF_PRINCIPLED")
def _origem(sock):                                                       # textura ligada (direta ou via mix) a Base Color
    for lk in sock.links:
        n_ = lk.from_node
        if n_.type == "TEX_IMAGE": return n_.image
        for s in n_.inputs:
            r = _origem(s) if s.is_linked else None
            if r: return r
    return None
tex_cor = _origem(_b.inputs["Base Color"])
print("MARCA textura de cor:", tex_cor.name, tuple(tex_cor.size), flush=True)
W_, H_ = tex_cor.size; px = np.empty(W_ * H_ * 4, np.float32); tex_cor.pixels.foreach_get(px); px = px.reshape(H_, W_, 4)
nl = len(me.loops); uv = np.empty(nl * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
vi = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", vi)
co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
cx = np.clip((uv[:, 0] % 1) * W_, 0, W_ - 1).astype(int); cy = np.clip((uv[:, 1] % 1) * H_, 0, H_ - 1).astype(int)
rgb = px[cy, cx, :3]; mx_, mn_ = rgb.max(1), rgb.min(1); sat = (mx_ - mn_) / np.maximum(mx_, 1e-3)
ciano = (sat > 0.28) & (rgb[:, 1] > rgb[:, 0] + 0.10) & (rgb[:, 2] > rgb[:, 0] + 0.10)
lo, hi = co.min(0), co.max(0); L = hi[1] - lo[1]
p = co[vi[ciano]]
esq = p[(p[:, 0] > 0.35) & (p[:, 1] > lo[1] + 0.22 * L) & (p[:, 1] < lo[1] + 0.60 * L) & (p[:, 2] > 2.5)]
cmin, cmax = np.percentile(esq, 3, axis=0) - 0.12, np.percentile(esq, 97, axis=0) + 0.12
print("MARCA amostras", len(esq), "caixa", np.round(cmin, 2), np.round(cmax, 2), flush=True)
# no de emissao no material do HIGH (so para o bake EMIT)
L_ = nt_hi.links; bsdf_hi = next(n for n in nt_hi.nodes if n.type == "BSDF_PRINCIPLED")
tn = next(n for n in nt_hi.nodes if n.type == "TEX_IMAGE" and n.image == tex_cor)
def no(t, **kw):
    x = nt_hi.nodes.new(t)
    for k, v in kw.items(): setattr(x, k, v)
    return x
hsv = no("ShaderNodeSeparateColor", mode="HSV"); L_.new(tn.outputs["Color"], hsv.inputs[0])
def faixa(ent, a0, a1, b0, b1):
    m1 = no("ShaderNodeMapRange"); m1.inputs[1].default_value = a0; m1.inputs[2].default_value = a1; L_.new(ent, m1.inputs[0])
    m2 = no("ShaderNodeMapRange"); m2.inputs[1].default_value = b1; m2.inputs[2].default_value = b0; L_.new(ent, m2.inputs[0])
    x = no("ShaderNodeMath", operation="MULTIPLY"); L_.new(m1.outputs[0], x.inputs[0]); L_.new(m2.outputs[0], x.inputs[1]); return x.outputs[0]
mh = faixa(hsv.outputs[0], 0.44, 0.47, 0.56, 0.60)                      # matiz ciano
ms = no("ShaderNodeMapRange"); ms.inputs[1].default_value = 0.22; ms.inputs[2].default_value = 0.36; L_.new(hsv.outputs[1], ms.inputs[0])
tc = no("ShaderNodeTexCoord"); sp = no("ShaderNodeSeparateXYZ"); L_.new(tc.outputs["Object"], sp.inputs[0])
caixa = None
for i, eixo in enumerate("XYZ"):
    f = faixa(sp.outputs[eixo], cmin[i] - 0.1, cmin[i] + 0.05, cmax[i] - 0.05, cmax[i] + 0.1)
    if caixa is None: caixa = f
    else:
        x = no("ShaderNodeMath", operation="MULTIPLY"); L_.new(caixa, x.inputs[0]); L_.new(f, x.inputs[1]); caixa = x.outputs[0]
m_ = no("ShaderNodeMath", operation="MULTIPLY"); L_.new(mh, m_.inputs[0]); L_.new(ms.outputs[0], m_.inputs[1])
m2_ = no("ShaderNodeMath", operation="MULTIPLY"); L_.new(m_.outputs[0], m2_.inputs[0]); L_.new(caixa, m2_.inputs[1])
bsdf_hi.inputs["Emission Color"].default_value = (0.30, 0.92, 1.0, 1)
L_.new(m2_.outputs[0], bsdf_hi.inputs["Emission Strength"])

# ------------------------------------------------------------------ cristais (aparencia; nao definem elemento)
def cristal(base, direc, alt, raio, nome, lados=6):
    m = bpy.data.meshes.new(nome); b = bmesh.new(); aneis = []
    for zf, rf in ((-0.30 * alt, 0.80), (0.0, 1.0), (0.55 * alt, 0.95), (0.78 * alt, 0.55)):
        anel = []
        for i in range(lados):
            an = 2 * math.pi * i / lados + 0.3; j = 1 + rnd.uniform(-0.10, 0.10)
            anel.append(b.verts.new((math.cos(an) * raio * rf * j, math.sin(an) * raio * rf * j * 0.78, zf)))
        aneis.append(anel)
    topo = b.verts.new((raio * 0.12, 0, alt))
    for k in range(3):
        for i in range(lados):
            b.faces.new((aneis[k][i], aneis[k][(i + 1) % lados], aneis[k + 1][(i + 1) % lados], aneis[k + 1][i]))
    for i in range(lados): b.faces.new((aneis[3][i], aneis[3][(i + 1) % lados], topo))
    b.faces.new(aneis[0][::-1]); b.to_mesh(m); b.free()
    o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    o.location = base; o.rotation_euler = direc.normalized().to_track_quat("Z", "Y").to_euler()
    return o
CRIS = []
# referencia: 4-5 cristais logo atras da crista da juba, no alto da cernelha, inclinados para tras; 1 pequeno a direita [PROPOSTA]
for (f, dx, alt, r, inc, lat) in ((0.33, 0.14, 0.80, 0.24, 0.60, 0.25), (0.365, 0.26, 0.66, 0.21, 0.68, 0.40),
                                  (0.40, 0.10, 0.55, 0.18, 0.75, 0.20), (0.43, 0.24, 0.42, 0.15, 0.82, 0.45),
                                  (0.30, 0.34, 0.48, 0.16, 0.50, 0.50), (0.385, -0.14, 0.42, 0.15, 0.70, -0.30)):
    y = lo[1] + f * L
    ok, hit, nrm, _ = hi_ob.ray_cast(V((dx, y, 12.0)), V((0, 0, -1)))
    base = (hit + V((0, 0, -0.06))) if ok else V((dx, y, 6.3))
    CRIS.append(cristal(base, V((lat, inc, 1.0)), alt, r, "Cristal"))
mc = bpy.data.materials.new("M_LoboArtico_Cristal")
if mc.node_tree is None: mc.use_nodes = True
b3 = mc.node_tree.nodes["Principled BSDF"]; b3.inputs["Base Color"].default_value = (0.55, 0.86, 1.0, 1)
b3.inputs["Alpha"].default_value = 0.62; b3.inputs["Roughness"].default_value = 0.06
b3.inputs["Emission Color"].default_value = (0.45, 0.85, 1.0, 1); b3.inputs["Emission Strength"].default_value = 0.35
if "Coat Weight" in b3.inputs: b3.inputs["Coat Weight"].default_value = 0.6
mc.surface_render_method = "BLENDED"; mc.use_backface_culling = False
for o in CRIS: o.data.materials.append(mc)
bpy.ops.object.select_all(action="DESELECT")
for o in CRIS: o.select_set(True)
bpy.context.view_layer.objects.active = CRIS[0]; bpy.ops.object.join(); cr = CRIS[0]; cr.name = cr.data.name = "LOW_Cristais"
ativo(cr); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for pl in cr.data.polygons: pl.use_smooth = False

# ------------------------------------------------------------------ LOW do corpo
dg = bpy.context.evaluated_depsgraph_get()
low = bpy.data.objects.new("LOW_Corpo", bpy.data.meshes.new_from_object(hi_ob.evaluated_get(dg))); low.data.name = "LOW_Corpo"
sc.collection.objects.link(low); ativo(low)
low.data.materials.clear()
vx = low.modifiers.new("V", "REMESH"); vx.mode = "VOXEL"; vx.voxel_size = 0.035; bpy.ops.object.modifier_apply(modifier="V")
print("LOW voxel faces", len(low.data.polygons), flush=True)
d = low.modifiers.new("D", "DECIMATE"); d.ratio = ALVO / max(tris(low), 1); bpy.ops.object.modifier_apply(modifier="D")
bpy.ops.object.modifier_add(type="TRIANGULATE"); bpy.ops.object.modifier_apply(modifier=low.modifiers[-1].name)
for pl in low.data.polygons: pl.use_smooth = True
# limpeza: a decimacao deixa gravatas/furos pequenos (nao-manifold) que deformam mal no rig
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.002); bpy.ops.mesh.dissolve_degenerate(threshold=0.0005)
bpy.ops.mesh.delete_loose()
for _ in range(2):
    bpy.ops.mesh.select_all(action="DESELECT"); bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=False,
                                                                                  use_multi_face=True, use_non_contiguous=True, use_verts=True)
    bpy.ops.mesh.delete(type="VERT")                                   # remove o nucleo defeituoso...
    bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.fill_holes(sides=12)   # ...e fecha os furos resultantes
bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.quads_convert_to_tris()
bpy.ops.object.mode_set(mode="OBJECT")
import bmesh as _bm
_b = _bm.new(); _b.from_mesh(low.data)
print("LOW limpeza: nao_manifold", sum(1 for e in _b.edges if not e.is_manifold), "faces", len(_b.faces), flush=True); _b.free()
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.003, area_weight=0.7)
bpy.ops.uv.pack_islands(margin=0.003); bpy.ops.object.mode_set(mode="OBJECT")
print("LOW_TRIS corpo", tris(low), "cristais", tris(cr), flush=True)

# ------------------------------------------------------------------ bake HIGH -> LOW
mat = bpy.data.materials.new("M_LoboArtico_Corpo_LOW")
if mat.node_tree is None: mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]; low.data.materials.append(mat)
MAPAS = (("cor", "sRGB"), ("normal", "Non-Color"), ("rugosidade", "Non-Color"), ("emissao", "sRGB"))
imgs = {}
for k, cs in MAPAS:
    im = bpy.data.images.new("LoboArtico_" + k, RES, RES, alpha=False); im.colorspace_settings.name = cs
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = im; imgs[k] = (im, t)
sc.render.engine = "CYCLES"; sc.cycles.samples = 8
try:
    pr = bpy.context.preferences.addons["cycles"].preferences; pr.compute_device_type = "CUDA"; pr.get_devices(); sc.cycles.device = "GPU"
except Exception as e: print("sem GPU:", e)
cr.hide_render = True
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.10; bk.max_ray_distance = 0.40; bk.margin = 8
bpy.ops.object.select_all(action="DESELECT"); hi_ob.select_set(True); low.select_set(True); bpy.context.view_layer.objects.active = low
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
for k, _ in MAPAS:
    im = imgs[k][0]; im.scale(FINAL, FINAL); im.filepath_raw = os.path.join(OUT, "LoboArtico_%s.png" % k); im.save()
Lk = nt.links
Lk.new(imgs["cor"][1].outputs["Color"], bsdf.inputs["Base Color"])
Lk.new(imgs["rugosidade"][1].outputs["Color"], bsdf.inputs["Roughness"])
nm = nt.nodes.new("ShaderNodeNormalMap"); Lk.new(imgs["normal"][1].outputs["Color"], nm.inputs["Color"]); Lk.new(nm.outputs[0], bsdf.inputs["Normal"])
Lk.new(imgs["emissao"][1].outputs["Color"], bsdf.inputs["Emission Color"]); bsdf.inputs["Emission Strength"].default_value = 1.0
cr.hide_render = False

# ------------------------------------------------------------------ LODs, export, registro
def lod(alvo, nome):
    c = low.copy(); c.data = low.data.copy(); c.name = c.data.name = nome; sc.collection.objects.link(c)
    ativo(c); dd = c.modifiers.new("D", "DECIMATE"); dd.ratio = alvo / tris(c); bpy.ops.object.modifier_apply(modifier="D")
    c.hide_render = True; return c
lod1, lod2 = lod(7000, "LOD1_Corpo"), lod(2500, "LOD2_Corpo")
def exportar(objs, nome):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, nome), export_format="GLB", use_selection=True, export_image_format="AUTO", export_yup=True)
exportar([low, cr], "CR_LoboArtico_LOW.glb"); exportar([lod1, cr], "CR_LoboArtico_LOD1.glb"); exportar([lod2, cr], "CR_LoboArtico_LOD2.glb")
reg = {"base": "Meshy image-to-3D (pose neutra por meshy_neutro.py)", "HIGH_tris": tris(hi_ob),
       "LOD0": {"LOW_Corpo": tris(low), "LOW_Cristais": tris(cr)}, "LOD1": {"LOD1_Corpo": tris(lod1), "LOW_Cristais": tris(cr)},
       "LOD2": {"LOD2_Corpo": tris(lod2), "LOW_Cristais": tris(cr)},
       "texturas_finais": ["LoboArtico_%s.png (%d)" % (k, FINAL) for k, _ in MAPAS], "bake_intermediario": RES,
       "marca_caixa_esquerda": [np.round(cmin, 2).tolist(), np.round(cmax, 2).tolist()]}
for k in ("LOD0", "LOD1", "LOD2"): reg[k]["total"] = sum(reg[k].values())
json.dump(reg, open(os.path.join(OUT, "custo_lobo_artico.json"), "w"), indent=1)
print("LOW_REGISTRO", json.dumps(reg), flush=True)
bpy.data.objects.remove(hi_ob)
for o in (lod1, lod2): o.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_LOW.blend"))
print("LOW_OK")
