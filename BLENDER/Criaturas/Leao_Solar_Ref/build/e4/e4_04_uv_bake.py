"""E4 passo 4: junta dentes e lingua a malha de jogo, UV nova (rosto/boca com o dobro de densidade) e bake a partir da E3b.
- corpo: Cycles selecionado->ativo da E3b (pele, interior, dentes, lingua; boca fechada): cor (sem luz), normal (tangente),
  rugosidade. O "brilho" do pelo e so cor iluminada no albedo; material fosco, sem emissao.
- boca (interior, dentes, lingua): cor por vertice da propria malha de jogo (mesmas cores da E3b), normal plana,
  rugosidade fixa; composta por cima nas ilhas da boca (o raio da HIGH ali poderia pegar a superficie oposta).
- Mestre 2048 e versao 1024 (Roblox). Um material, uma UV.
Uso: blender -b <e4_boca.blend> -P e4_04_uv_bake.py -- <E3b.blend> <saida.blend> <dir_tex> [res=2048] [extrusao=0.10]"""
import bpy, bmesh, sys, os, math, time
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]
E3B, OUT, TEX = os.path.abspath(A[0]), os.path.abspath(A[1]), os.path.abspath(A[2]); RES = int(A[3]) if len(A) > 3 else 2048
EXT = float(A[4]) if len(A) > 4 else 0.10
os.makedirs(TEX, exist_ok=True); t0 = time.time(); sc = bpy.context.scene
lo = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; NOME = lo.name   # E4 ou E4b
# ---------------------------------------------------------------- 1. juntar dentes e lingua (grupos preservados)
for o in sc.objects: o.select_set(False)
partes = [bpy.data.objects[n] for n in ("Leao_Dentes_Sup", "Leao_Dentes_Inf", "Leao_Lingua")]
for o in partes:
    for m in list(o.modifiers): o.modifiers.remove(m)
    o.select_set(True)
lo.select_set(True); bpy.context.view_layer.objects.active = lo; bpy.ops.object.join()
me = lo.data
boca = np.array([p.material_index != 0 for p in me.polygons])
mats_nome = [m.name for m in me.materials]
dentes = np.array([mats_nome[p.material_index] == "M_Leao_Dentes" for p in me.polygons])
print("JUNTO tris", sum(len(p.vertices) - 2 for p in me.polygons), "faces boca", int(boca.sum()), round(time.time() - t0, 1), "s")
# normais coerentes por casca (corpo+interior e uma casca fechada: "fora" da casca = dentro da boca, que e o lado visivel)
bmn = bmesh.new(); bmn.from_mesh(me); bmesh.ops.recalc_face_normals(bmn, faces=bmn.faces); bmn.to_mesh(me); bmn.free()
# ---------------------------------------------------------------- 2. UV
while me.uv_layers: me.uv_layers.remove(me.uv_layers[0])
me.uv_layers.new(name="UV")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from e4_uv_regioes import uv_regioes, estat
print("UV cartas", uv_regioes(lo, 55.0, 700, 10), "(verts com UV, distorcao p5, p95)", estat(lo))
bm = bmesh.new(); bm.from_mesh(me); uvl = bm.loops.layers.uv.active; bm.faces.ensure_lookup_table()
def rosto(c): return c.y < -12.9 and c.z > 10.9 and abs(c.x + 0.23) < 1.7
# ilhas por conectividade de UV
vis = set(); n_esc = 0
for f in bm.faces:
    if f.index in vis: continue
    ilha = []; pilha = [f]; vis.add(f.index)
    while pilha:
        g = pilha.pop(); ilha.append(g)
        for l in g.loops:
            for e in (l.edge,):
                for h in e.link_faces:
                    if h.index in vis: continue
                    # mesma ilha se a UV coincide nos dois vertices da aresta
                    ok = True
                    for v in e.verts:
                        a = next(x[uvl].uv for x in g.loops if x.vert == v); b = next(x[uvl].uv for x in h.loops if x.vert == v)
                        if (a - b).length > 1e-6: ok = False
                    if ok: vis.add(h.index); pilha.append(h)
    fb = sum(1 for g in ilha if g.material_index != 0) / len(ilha)
    fr = sum(1 for g in ilha if g.material_index == 0 and rosto(g.calc_center_median())) / len(ilha)
    esc = 0.7 if fb > 0.5 else 2.0 if fr > 0.5 else 1.0      # pele do rosto: dobro da densidade; boca (cor lisa): menos
    if esc != 1.0:
        cs = [l[uvl].uv.copy() for g in ilha for l in g.loops]; c = sum(cs, cs[0] * 0) / len(cs)
        for g in ilha:
            for l in g.loops: l[uvl].uv = c + (l[uvl].uv - c) * esc
        n_esc += 1
bm.to_mesh(me); bm.free(); print("UV ilhas do rosto/boca ampliadas 2x:", n_esc)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.pack_islands(rotate=True, margin=0.003)
bpy.ops.object.mode_set(mode="OBJECT")
# ---------------------------------------------------------------- 3. material unico de jogo
lm = bpy.data.materials.new("M_" + NOME.replace("Leao_Solar", "Leao_Solar")); lm.use_nodes = True; nt = lm.node_tree; lb = nt.nodes["Principled BSDF"]
lb.inputs["Specular IOR Level"].default_value = 0.25; lb.inputs["Metallic"].default_value = 0.0
lm.use_backface_culling = True                              # como no Roblox (sem verso das faces): revela face invertida
IM = {}
for nome, cs in (("cor", "sRGB"), ("normal", "Non-Color"), ("rugosidade", "Non-Color")):
    im = bpy.data.images.new(NOME + "_%s" % nome, RES, RES, alpha=False, float_buffer=(nome == "normal")); im.colorspace_settings.name = cs; IM[nome] = im
    nd = nt.nodes.new("ShaderNodeTexImage"); nd.image = im; nd.name = nome
nm = nt.nodes.new("ShaderNodeNormalMap"); L = nt.links
L.new(nt.nodes["cor"].outputs["Color"], lb.inputs["Base Color"]); L.new(nt.nodes["rugosidade"].outputs["Color"], lb.inputs["Roughness"])
L.new(nt.nodes["normal"].outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs[0], lb.inputs["Normal"])
me.materials.clear(); me.materials.append(lm)
for p in me.polygons: p.material_index = 0
# ---------------------------------------------------------------- 4. HIGH da E3b (boca fechada = repouso)
with bpy.data.libraries.load(E3B, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n in ("Leao_Solar_E3", "Leao_Dentes_Sup", "Leao_Dentes_Inf", "Leao_Lingua")]
his = []
for o in dst.objects:
    sc.collection.objects.link(o); his.append(o)
    for m in list(o.modifiers): o.modifiers.remove(m)          # repouso: sem armature
print("HIGH", [(o.name, len(o.data.polygons)) for o in his])
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
bk = sc.render.bake; bk.margin = 8
def ativar(nome):
    for nd in nt.nodes: nd.select = False
    nt.nodes[nome].select = True; nt.nodes.active = nt.nodes[nome]
def assar(nome, tipo, sel_ativo, **kw):
    ativar(nome); bk.use_selected_to_active = sel_ativo
    if sel_ativo: bk.cage_extrusion = EXT; bk.max_ray_distance = 3 * EXT
    t = time.time(); bpy.ops.object.bake(type=tipo, **kw); print("BAKE", nome, tipo, round(time.time() - t, 1), "s", flush=True)
for o in sc.objects: o.select_set(False)
for o in his: o.select_set(True)
lo.select_set(True); bpy.context.view_layer.objects.active = lo
assar("cor", "DIFFUSE", True, pass_filter={"COLOR"})
assar("normal", "NORMAL", True, normal_space="TANGENT")
assar("rugosidade", "ROUGHNESS", True)
BASE = {k: np.array(IM[k].pixels[:], np.float32).reshape(RES, RES, 4) for k in IM}
# ---------------------------------------------------------------- 5. boca: cor da propria malha (emissao da cor por vertice)
for o in his: bpy.data.objects.remove(o, do_unlink=True)
dup = lo.copy(); dup.data = lo.data.copy(); dup.name = "_boca_bake"; sc.collection.objects.link(dup)
bm = bmesh.new(); bm.from_mesh(dup.data); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not boca[f.index]], context="FACES"); bm.to_mesh(dup.data); bm.free()
mb = bpy.data.materials.new("_bake_boca"); mb.use_nodes = True; nb = mb.node_tree
em = nb.nodes.new("ShaderNodeEmission"); va = nb.nodes.new("ShaderNodeVertexColor"); va.layer_name = "CorBoca"
nb.links.new(va.outputs["Color"], em.inputs["Color"]); nb.links.new(em.outputs[0], nb.nodes["Material Output"].inputs[0])
im2 = bpy.data.images.new("_boca", RES, RES, alpha=True); im2.pixels[:] = np.zeros(RES * RES * 4, np.float32)
t2 = nb.nodes.new("ShaderNodeTexImage"); t2.image = im2; nb.nodes.active = t2
dup.data.materials.clear(); dup.data.materials.append(mb)
for o in sc.objects: o.select_set(False)
dup.select_set(True); bpy.context.view_layer.objects.active = dup
bk.use_selected_to_active = False; bk.margin = 3; bpy.ops.object.bake(type="EMIT")
B2 = np.array(im2.pixels[:], np.float32).reshape(RES, RES, 4)
def raster(obj):
    """mascara dos texels cobertos pelos triangulos do objeto (UV), com 2 texels de folga"""
    m_ = obj.data; m_.calc_loop_triangles(); uv = m_.uv_layers.active.data; M_ = np.zeros((RES, RES), bool)
    for t in m_.loop_triangles:
        P = np.array([uv[l].uv for l in t.loops]) * RES
        x0, y0 = np.floor(P.min(0)).astype(int) - 2; x1, y1 = np.ceil(P.max(0)).astype(int) + 2
        x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, RES - 1), min(y1, RES - 1)
        X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, ay), (bx, by), (cx, cy) = P; den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12: continue
        l1 = ((by - cy) * (X - cx) + (cx - bx) * (Y - cy)) / den; l2 = ((cy - ay) * (X - cx) + (ax - cx) * (Y - cy)) / den; l3 = 1 - l1 - l2
        tol = 2.5 / max(np.abs(den) ** 0.5, 1e-6)
        dentro_ = (l1 >= -tol) & (l2 >= -tol) & (l3 >= -tol); yy, xx = np.nonzero(dentro_); M_[y0 + yy, x0 + xx] = True
    return M_
mask = raster(dup)
print("BOCA texels", int(mask.sum()))
BASE["cor"][mask, :3] = B2[mask, :3]
BASE["normal"][mask, :3] = (0.5, 0.5, 1.0)
# rugosidade: mucosa 0,55; dentes 0,35 (dentes = texels claros)
lumb = B2[..., :3].mean(-1)
BASE["rugosidade"][mask, :3] = np.where((lumb[mask] > 0.6)[:, None], 0.35, 0.55)
bpy.data.objects.remove(dup, do_unlink=True)
for k, im in IM.items():
    im.pixels[:] = BASE[k].ravel()
    im.filepath_raw = os.path.join(TEX, NOME + "_%s_%d.png" % (k, RES)); im.file_format = "PNG"; im.save()
    c = im.copy(); c.scale(1024, 1024); c.filepath_raw = os.path.join(TEX, NOME + "_%s_1024.png" % k); c.file_format = "PNG"; c.save()
    bpy.data.images.remove(c); im.filepath = im.filepath_raw; im.source = "FILE"
sc.render.engine = "BLENDER_EEVEE"
for p in me.polygons: p.use_smooth = True
print("BAKE_OK", round(time.time() - t0, 1), "s")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
