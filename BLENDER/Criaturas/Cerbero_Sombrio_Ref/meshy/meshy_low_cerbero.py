"""Cerbero Sombrio (Meshy m1) -- malha de JOGO a partir da malha bruta (1,38M tris, 1 material 4K).
Adaptado de Coruja_da_Floresta_Ref/meshy/meshy_low_coruja.py. Bocas FECHADAS nesta etapa (interior da boca vem depois).
Passos: chao em z=0 -> remesh voxel (fecha tufos de pelo e placas) -> reducao com pesos por regiao (3 cabecas e patas mais densas)
-> separa Cabecas (textura propria) e Corpo -> UV + bake Cycles (cor, normal, rugosidade) da bruta -> GLB, relatorio e renders.
Uso: blender -b -t 4 modelo/CR_Cerbero_meshy_bruto.blend -P meshy_low_cerbero.py -- <saida_dir> [alvo=18000] [voxel=0.005] [res=1024]
Escala de trabalho = a do Meshy (cernelha ~1,1 u). Orcamento e PROPOSTA ate medir varios animais em PC e celular."""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector as V
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
def arg(n, d): return type(d)(next((a.split("=")[1] for a in ARGS if a.startswith(n + "=")), d))
ALVO, VOX, R = arg("alvo", 18000), arg("voxel", 0.005), arg("res", 1024)
sc = bpy.context.scene
sc.render.threads_mode = "FIXED"; sc.render.threads = 4          # PC compartilhado com o usuario
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
def ativar(o):
    for x in sc.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
def mod(o, tipo, **kw):
    ativar(o); m = o.modifiers.new(tipo, tipo)
    for k, v in kw.items(): setattr(m, k, v)
    bpy.ops.object.modifier_apply(modifier=m.name)
for o in [o for o in sc.objects if o.type in ("CAMERA", "LIGHT")]: bpy.data.objects.remove(o)
HIGH = bpy.data.objects["Mesh_0"]; HIGH.name = "CR_Cerbero_Meshy"
co = np.array([v.co[:] for v in HIGH.data.vertices])
HIGH.data.transform(__import__("mathutils").Matrix.Translation((0, 0, -co[:, 2].min())))   # patas no chao (z=0)
co = np.array([v.co[:] for v in HIGH.data.vertices])
# regioes (sondadas em 17/11): frente em -Y; cabecas a frente da cernelha e acima do peito
Y_CAB, Z_CAB, Z_PATA = arg("ycab", -0.42), arg("zcab", 0.95), 0.14
def regiao(p):
    if p.y < Y_CAB and p.z > Z_CAB: return "cabecas"
    if p.z < Z_PATA: return "patas"
    return "corpo"

# ------------------------------------------------------------------ 1) voxel + reducao
low = HIGH.copy(); low.data = HIGH.data.copy(); low.name = low.data.name = "Cerbero_Corpo"; sc.collection.objects.link(low)
low.data.materials.clear()
mod(low, "REMESH", mode="VOXEL", voxel_size=VOX, use_smooth_shade=True)
print("LOW voxel", tris(low), flush=True)
bm = bmesh.new(); bm.from_mesh(low.data); vist = set(); ilhas = []
for v0 in bm.verts:
    if v0.index in vist: continue
    il = []; pilha = [v0]
    while pilha:
        x = pilha.pop()
        if x.index in vist: continue
        vist.add(x.index); il.append(x); pilha.extend(e.other_vert(x) for e in x.link_edges)
    ilhas.append(il)
ilhas.sort(key=len, reverse=True)
soltas = [v for il in ilhas[1:] if len(il) < 0.01 * len(bm.verts) for v in il]
print("ILHAS", len(ilhas), "verts soltos", len(soltas), flush=True)
bmesh.ops.delete(bm, geom=soltas, context="VERTS"); bm.to_mesh(low.data); bm.free()
mod(low, "TRIANGULATE")
vg = low.vertex_groups.new(name="densidade")      # peso baixo = mais densidade (protege da reducao)
W_CAB, W_PATA = arg("wc", 0.45), arg("wp", 0.75)
for v in low.data.vertices:
    r = regiao(v.co)
    vg.add([v.index], W_CAB if r == "cabecas" else W_PATA if r == "patas" else 1.0, "REPLACE")
ativar(low); dm = low.modifiers.new("Dec", "DECIMATE"); dm.ratio = ALVO / tris(low); dm.use_collapse_triangulate = True
dm.vertex_group = "densidade"; dm.vertex_group_factor = arg("fator", 3.0); bpy.ops.object.modifier_apply(modifier=dm.name)
mod(low, "TRIANGULATE"); low.vertex_groups.clear()
for p in low.data.polygons: p.use_smooth = True
REG = {"cabecas": 0, "patas": 0, "corpo": 0}
for f in low.data.polygons: REG[regiao(f.center)] += len(f.vertices) - 2
print("LOW reduzido", tris(low), "REGIOES", REG, flush=True)

# ------------------------------------------------------------------ 2) separa as tres cabecas (textura propria)
def separar(o, cond, nome):
    c = o.copy(); c.data = o.data.copy(); c.name = c.data.name = nome; sc.collection.objects.link(c)
    for o_, manter in ((c, True), (o, False)):
        bm_ = bmesh.new(); bm_.from_mesh(o_.data)
        bmesh.ops.delete(bm_, geom=[f for f in bm_.faces if cond(f.calc_center_median()) != manter], context="FACES")
        bm_.to_mesh(o_.data); bm_.free()
    return c
CAB = separar(low, lambda p: regiao(p) == "cabecas", "Cerbero_Cabecas")

# ------------------------------------------------------------------ 3) UV + bake (cor, normal, rugosidade)
def uv_proj(o, margem=0.003):
    ativar(o); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=margem, area_weight=0.0)
    bpy.ops.uv.pack_islands(margin=margem); bpy.ops.object.mode_set(mode="OBJECT")
sc.render.engine = "CYCLES"; sc.cycles.samples = 4; sc.cycles.device = "CPU"
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.008; bk.max_ray_distance = 0.03; bk.margin = 8
def preencher_falhas(img):
    px = np.array(img.pixels[:], dtype=np.float32).reshape(R, R, 4)
    for _ in range(12):
        falha = (px[..., 0] + px[..., 1] + px[..., 2]) < 1e-4
        if not falha.any(): break
        viz = np.zeros_like(px[..., :3]); cont = np.zeros((R, R, 1), np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.roll(px, (dy, dx), axis=(0, 1)); ok = ((sh[..., 0] + sh[..., 1] + sh[..., 2]) >= 1e-4)[..., None]
            viz += sh[..., :3] * ok; cont += ok
        preenche = falha & (cont[..., 0] > 0)
        px[preenche, :3] = (viz / np.maximum(cont, 1))[preenche]
    img.pixels[:] = px.ravel()
def assar(o, prefixo):
    uv_proj(o)
    imgs = {k: bpy.data.images.new(f"{prefixo}_{k}", R, R) for k in ("Cor", "Normal", "Rugosidade")}
    imgs["Normal"].colorspace_settings.name = "Non-Color"; imgs["Rugosidade"].colorspace_settings.name = "Non-Color"
    mat = bpy.data.materials.new("M_" + prefixo[2:]); mat.use_nodes = True; nt = mat.node_tree
    for img in imgs.values():
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = img; tx.name = img.name
    o.data.materials.clear(); o.data.materials.append(mat)
    for o_ in sc.objects: o_.select_set(False)
    HIGH.select_set(True); o.select_set(True); bpy.context.view_layer.objects.active = o
    nt.nodes.active = nt.nodes[imgs["Cor"].name]; bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"})
    nt.nodes.active = nt.nodes[imgs["Normal"].name]; bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")
    nt.nodes.active = nt.nodes[imgs["Rugosidade"].name]; bpy.ops.object.bake(type="ROUGHNESS")
    preencher_falhas(imgs["Cor"])
    for img in imgs.values():
        img.filepath_raw = os.path.join(OUT, img.name + ".png"); img.file_format = "PNG"; img.save()
    b_ = nt.nodes["Principled BSDF"]; nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(nt.nodes[imgs["Cor"].name].outputs["Color"], b_.inputs["Base Color"])
    nt.links.new(nt.nodes[imgs["Normal"].name].outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs[0], b_.inputs["Normal"])
    nt.links.new(nt.nodes[imgs["Rugosidade"].name].outputs["Color"], b_.inputs["Roughness"])
assar(CAB, "T_Cerbero_Cabecas"); assar(low, "T_Cerbero_Corpo")
print("BAKE_OK cabecas", tris(CAB), "corpo", tris(low), flush=True)

# ------------------------------------------------------------------ 4) exporta + relatorio
JOGO = [CAB, low]
HIGH.hide_render = True
for o in sc.objects: o.select_set(o in JOGO)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "CR_Cerbero_Sombrio_LOW.glb"), use_selection=True, export_format="GLB",
                          export_yup=True, export_apply=True, export_image_format="AUTO", export_materials="EXPORT")
pts = np.array([(o.matrix_world @ v.co)[:] for o in JOGO for v in o.data.vertices])
rel = {"regioes": REG, "pesos": [W_CAB, W_PATA], "alvo": ALVO, "voxel": VOX, "textura": R,
       "malhas": {o.name: {"tris": tris(o), "material": o.data.materials[0].name} for o in JOGO},
       "tris_total": sum(tris(o) for o in JOGO), "bruto_tris": tris(HIGH),
       "medidas": {"comprimento": float(np.ptp(pts[:, 1])), "largura": float(np.ptp(pts[:, 0])), "altura": float(pts[:, 2].max()),
                   "pata_min_z": float(pts[:, 2].min())}}
json.dump(rel, open(os.path.join(OUT, "relatorio_low.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("REL", json.dumps(rel), flush=True)

# ------------------------------------------------------------------ 5) renders de revisao (bruto x jogo)
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
def camera(nome, loc, alvo, lente):
    c = bpy.data.cameras.new(nome); o = bpy.data.objects.new(nome, c); sc.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); c.lens = lente; return o
CAMS = {"tres_quartos": (camera("Cam_34", (-2.6, -3.0, 1.9), (0, 0, 0.72), 58), (1000, 760)),
        "frente": (camera("Cam_Frente", (0, -4.2, 1.1), (0, 0, 0.78), 58), (900, 760)),
        "perfil": (camera("Cam_Perfil", (4.4, 0, 0.9), (0, 0, 0.75), 58), (1000, 700)),
        "costas": (camera("Cam_Costas", (1.2, 3.8, 1.7), (0, 0, 0.7), 55), (1000, 700)),
        "cabecas_34": (camera("Cam_Cab", (-1.0, -2.1, 1.75), (0, -0.62, 1.22), 55), (900, 700))}
mundo = bpy.data.worlds.new("Fundo"); sc.world = mundo; mundo.use_nodes = True
bg = mundo.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (*lin("8a8580"), 1); bg.inputs["Strength"].default_value = 1.1
sd = bpy.data.lights.new("Sol", "SUN"); sd.energy = 3.0; sd.angle = math.radians(12)
so = bpy.data.objects.new("Sol", sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
sc.view_settings.view_transform = "Standard"; sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
sc.render.film_transparent = True; sc.render.resolution_percentage = 100
def render(cam, res, arq):
    sc.camera = cam; sc.render.resolution_x, sc.render.resolution_y = res; sc.render.filepath = os.path.join(OUT, arq)
    bpy.ops.render.render(write_still=True)
sc.render.engine = "BLENDER_EEVEE"
try: sc.eevee.taa_render_samples = 32
except Exception: pass
for versao, mostrar in (("bruto", [HIGH]), ("jogo", JOGO)):
    for o in [HIGH] + JOGO: o.hide_render = o not in mostrar
    for n, (cam, res) in CAMS.items(): render(cam, res, f"low_{versao}_{n}.png")
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "TEXTURE"
M_FIO = bpy.data.materials.new("M_Fio"); M_FIO.diffuse_color = (0.85, 0.85, 0.85, 1); fios = []
for o in JOGO:
    f = o.copy(); f.data = o.data.copy(); f.name = o.name + "_FIO"; sc.collection.objects.link(f)
    w = f.modifiers.new("Fio", "WIREFRAME"); w.thickness = 0.002; w.use_replace = True; w.use_even_offset = False
    f.data.materials.clear(); f.data.materials.append(M_FIO); fios.append(f)
for n in ("tres_quartos", "cabecas_34"): render(CAMS[n][0], CAMS[n][1], f"low_jogo_arame_{n}.png")
for f in fios: bpy.data.objects.remove(f, do_unlink=True)
bpy.data.materials.remove(M_FIO)
for o in JOGO: o.hide_render = False
HIGH.hide_set(True)
sc.render.engine = "BLENDER_EEVEE"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cerbero_Sombrio_LOW.blend"))
print("CERBERO_LOW_OK", flush=True)
