"""Cervo-do-Bosque (Meshy) -- malha de JOGO a partir da malha bruta do Meshy (469k tris).
Adaptado de Urso_Silvestre_Ref/v2/meshy/meshy_low.py. Fauna de recurso: orcamento menor que o das domesticaveis
(varios animais ao mesmo tempo) e boca FECHADA (linha dos labios fica na textura; sem cavidade/dentes).
1) remesh por voxel (fecha a malha) -> reducao para ALVO tris com mais densidade na cabeca e na galhada;
2) separa Cabeca (rosto + orelhas + galhada) e Corpo, cada um com textura propria;
3) UV + bake Cycles (cor, normal, rugosidade) da malha bruta para a de jogo;
4) exporta GLB, grava relatorio e renders de revisao (bruto x jogo).
Uso: blender -b CR_Cervo_meshy_bruto.blend -P meshy_low_cervo.py -- <saida_dir> [alvo=12000] [voxel=0.005] [res=1024] [wg=0.62] [wc=0.70] [wj=0.65]
  (v1 em low/ usou pesos antigos: cabeca 8,8k / corpo 3,2k; v2 rebalanceada em low_v2/)
Orcamento (alvo, resolucao) e PROPOSTA ate medir varios animais em PC e celular."""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
def arg(n, d): return type(d)(next((a.split("=")[1] for a in ARGS if a.startswith(n + "=")), d))
ALVO, VOX, R = arg("alvo", 12000), arg("voxel", 0.005), arg("res", 1024)
sc = bpy.context.scene
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
def ativar(o):
    for x in sc.objects: x.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
def mod(o, tipo, **kw):
    ativar(o); m = o.modifiers.new(tipo, tipo)
    for k, v in kw.items(): setattr(m, k, v)
    bpy.ops.object.modifier_apply(modifier=m.name)
for o in [o for o in sc.objects if o.type in ("CAMERA", "LIGHT")]: bpy.data.objects.remove(o)
HIGH = bpy.data.objects["CR_Cervo_Meshy"]
co = np.array([v.co[:] for v in HIGH.data.vertices])
NARIZ_Y = co[:, 1].min()
Y_CAB = NARIZ_Y + 0.40                 # atras das orelhas/pedicelos, antes do meio do pescoco
Z_GALHA = np.percentile(co[co[:, 1] < Y_CAB][:, 2], 50)   # acima disso, na frente: galhada e topo da cabeca
print("NARIZ_Y", round(NARIZ_Y, 3), "Y_CAB", round(Y_CAB, 3), "Z_GALHA", round(Z_GALHA, 3))

# ------------------------------------------------------------------ 1) voxel + reducao
low = HIGH.copy(); low.data = HIGH.data.copy(); low.name = low.data.name = "Cervo_Corpo"; sc.collection.objects.link(low)
low.data.materials.clear()
mod(low, "REMESH", mode="VOXEL", voxel_size=VOX, use_smooth_shade=True)
print("LOW voxel", tris(low))
mod(low, "TRIANGULATE")
vg = low.vertex_groups.new(name="densidade")      # peso baixo = mais densidade (protege da reducao)
# pesos calibrados por teste (12/11): galhada ~3,5k, cabeca ~2,5k, corpo ~6k em 12k; articulacoes reforcadas para o rig
W_GALHA, W_CAB, W_JUNTA = arg("wg", 0.62), arg("wc", 0.70), arg("wj", 0.65)
Z_TOPO = arg("ztopo", 1.56)                       # acima do topo do cranio, na frente = galhada
def regiao(p):
    if p.y < Y_CAB + 0.15 and p.z > Z_TOPO: return "galhada"
    if p.y < Y_CAB: return "cabeca"
    return "corpo"
for v in low.data.vertices:
    r = regiao(v.co)
    if r == "galhada": w = W_GALHA
    elif r == "cabeca": w = W_CAB
    else: w = W_JUNTA if (0.38 < v.co.z < 0.62 or (v.co.y < Y_CAB + 0.35 and v.co.z > 0.95)) else 1.0   # joelhos/jarretes, pescoco
    vg.add([v.index], w, "REPLACE")
ativar(low); dm = low.modifiers.new("Dec", "DECIMATE"); dm.ratio = ALVO / tris(low); dm.use_collapse_triangulate = True
dm.vertex_group = "densidade"; dm.vertex_group_factor = 3.0; bpy.ops.object.modifier_apply(modifier=dm.name)
mod(low, "TRIANGULATE")
low.vertex_groups.clear()
for p in low.data.polygons: p.use_smooth = True
print("LOW reduzido", tris(low))
REG = {"galhada": 0, "cabeca": 0, "corpo": 0}
for f in low.data.polygons: REG[regiao(f.center)] += len(f.vertices) - 2
print("REGIOES", REG)

# ------------------------------------------------------------------ 2) separa cabeca (textura propria)
def separar(o, cond, nome):
    c = o.copy(); c.data = o.data.copy(); c.name = c.data.name = nome; sc.collection.objects.link(c)
    for o_, manter in ((c, True), (o, False)):
        bm_ = bmesh.new(); bm_.from_mesh(o_.data)
        bmesh.ops.delete(bm_, geom=[f for f in bm_.faces if cond(f.calc_center_median()) != manter], context="FACES")
        bm_.to_mesh(o_.data); bm_.free()
    return c
CAB = separar(low, lambda p: p.y < Y_CAB, "Cervo_Cabeca")

# ------------------------------------------------------------------ 3) UV + bake (cor, normal, rugosidade)
def uv_proj(o, margem=0.003):
    ativar(o); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=margem, area_weight=0.0)
    bpy.ops.uv.pack_islands(margin=margem); bpy.ops.object.mode_set(mode="OBJECT")
sc.render.engine = "CYCLES"; sc.cycles.samples = 4; sc.cycles.device = "CPU"
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.012; bk.max_ray_distance = 0.05; bk.margin = 8
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
assar(CAB, "T_Cervo_Cabeca"); assar(low, "T_Cervo_Corpo")
print("BAKE_OK cabeca", tris(CAB), "corpo", tris(low))

# ------------------------------------------------------------------ 4) exporta + relatorio
JOGO = [CAB, low]
HIGH.hide_render = True; HIGH.hide_set(True)
for o in sc.objects: o.select_set(o in JOGO)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "CR_Cervo_do_Bosque_LOW.glb"), use_selection=True, export_format="GLB",
                          export_yup=True, export_apply=True, export_image_format="AUTO", export_materials="EXPORT")
pts = np.array([(o.matrix_world @ v.co)[:] for o in JOGO for v in o.data.vertices])
rel = {"regioes": REG, "pesos": [W_GALHA, W_CAB, W_JUNTA], "alvo": ALVO, "voxel": VOX, "textura": R, "malhas": {o.name: {"tris": tris(o), "material": o.data.materials[0].name} for o in JOGO},
       "tris_total": sum(tris(o) for o in JOGO), "bruto_tris": tris(HIGH),
       "medidas": {"comprimento": float(np.ptp(pts[:, 1])), "largura": float(np.ptp(pts[:, 0])), "altura": float(pts[:, 2].max()),
                   "casco_min_z": float(pts[:, 2].min())}}
json.dump(rel, open(os.path.join(OUT, "relatorio_low.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("REL", json.dumps(rel))

# ------------------------------------------------------------------ 5) renders de revisao (bruto x jogo, mesma luz das revisoes)
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
def camera(nome, loc, alvo, lente):
    c = bpy.data.cameras.new(nome); o = bpy.data.objects.new(nome, c); sc.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); c.lens = lente; return o
cz_ = float(np.median(co[co[:, 1] < NARIZ_Y + 0.20][:, 2])); alvo_r = V((0, NARIZ_Y + 0.15, cz_ - 0.02))
CAMS = {"tres_quartos": (camera("Cam_34", (-1.35, -2.05, 0.72), (0, -0.2, 1.02), 28), (700, 1024)),
        "lado": (camera("Cam_Lado", (-3.2, -0.05, 1.0), (0, -0.05, 1.0), 40), (900, 1000)),
        "rosto_34": (camera("Cam_R34", tuple(alvo_r + V((-0.62, -0.74, 0.06))), tuple(alvo_r), 60), (900, 700))}
mundo = bpy.data.worlds.new("Fundo"); sc.world = mundo; mundo.use_nodes = True
bg = mundo.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (*lin("8a8580"), 1); bg.inputs["Strength"].default_value = 0.9
sd = bpy.data.lights.new("Sol", "SUN"); sd.energy = 2.0; sd.angle = math.radians(12)
so = bpy.data.objects.new("Sol", sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
sc.view_settings.view_transform = "Standard"; sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_mode = "RGBA"
sc.render.film_transparent = True; sc.render.resolution_percentage = 100
def render(cam, res, arq):
    sc.camera = cam; sc.render.resolution_x, sc.render.resolution_y = res; sc.render.filepath = os.path.join(OUT, arq)
    bpy.ops.render.render(write_still=True)
sc.render.engine = "BLENDER_EEVEE"
try: sc.eevee.taa_render_samples = 48
except Exception: pass
for versao, mostrar in (("bruto", [HIGH]), ("jogo", JOGO)):
    for o in [HIGH] + JOGO: o.hide_render = o not in mostrar
    for n, (cam, res) in CAMS.items(): render(cam, res, f"low_{versao}_{n}.png")
    render(CAMS["tres_quartos"][0], (120, 176), f"low_{versao}_miniatura.png")
# arame da malha de jogo (Workbench)
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "TEXTURE"
M_FIO = bpy.data.materials.new("M_Fio"); M_FIO.diffuse_color = (0.02, 0.02, 0.02, 1); fios = []
for o in JOGO:
    f = o.copy(); f.data = o.data.copy(); f.name = o.name + "_FIO"; sc.collection.objects.link(f)
    w = f.modifiers.new("Fio", "WIREFRAME"); w.thickness = 0.0015; w.use_replace = True; w.use_even_offset = False
    f.data.materials.clear(); f.data.materials.append(M_FIO); fios.append(f)
for n in ("tres_quartos", "rosto_34"): render(CAMS[n][0], CAMS[n][1], f"low_jogo_arame_{n}.png")
for f in fios: bpy.data.objects.remove(f, do_unlink=True)
bpy.data.materials.remove(M_FIO)
for o in JOGO: o.hide_render = False
sc.render.engine = "BLENDER_EEVEE"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cervo_do_Bosque_LOW.blend"))
print("CERVO_LOW_OK")
