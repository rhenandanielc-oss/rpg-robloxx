"""Importa o GLB do Meshy da Coruja-da-Floresta, orienta (frente = -Y, pes em Z = 0, centrada em X; asas ao longo de X),
escala e renderiza vistas de revisao (argila Workbench + textura EEVEE). Adaptado de Javali_Silvestre_Ref/meshy/importar_meshy_javali.py.
Orientacao: na coruja de asas abertas o eixo horizontal mais longo e a ENVERGADURA (vira X). No eixo perpendicular, a cauda
se estende para tras na metade de baixo -> o lado com mais extensao abaixo de 45% da altura e a TRAS; a frente e o oposto.
Escala de trabalho (PROPOSTA, nao e porte oficial): altura total (com os tufos) 0,62 u (corujao grande de fantasia).
Uso: [CORUJA_INVERTER=1] blender -b --factory-startup -P importar_meshy_coruja.py -- <glb> <saida_dir> [girar_graus_z]
(m1 precisa de CORUJA_INVERTER=1: a deteccao pela cauda pegou as pontas das asas)"""
import bpy, sys, os, math, json
from mathutils import Vector as V, Matrix
import numpy as np
a = sys.argv[sys.argv.index("--") + 1:]; glb, OUT = a[0], os.path.abspath(a[1]); GIRO = float(a[2]) if len(a) > 2 else 0.0
os.makedirs(OUT, exist_ok=True); VER = "m1"; ALTURA = 0.62
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
cena = bpy.context.scene
ms = [o for o in cena.objects if o.type == "MESH"]
for o in cena.objects: o.select_set(o in ms)
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1: bpy.ops.object.join()
ob = bpy.context.object; ob.name = "CR_Coruja_Meshy"
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM"); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in [o for o in cena.objects if o.type == "EMPTY"]: bpy.data.objects.remove(o)
me = ob.data
if GIRO: me.transform(Matrix.Rotation(math.radians(GIRO), 4, "Z"))
co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
mn, mx = co.min(0), co.max(0); L = mx - mn
print("MESHY_BRUTO tris", sum(len(p.vertices) - 2 for p in me.polygons), "caixa", mn.round(3), mx.round(3))
env = 0 if L[0] > L[1] else 1; prof = 1 - env                       # envergadura = eixo horizontal mais longo
baixo = co[co[:, 2] < mn[2] + 0.45 * L[2]]; meio = float(np.median(co[:, prof]))
tras_pos = (baixo[:, prof].max() - meio) > (meio - baixo[:, prof].min())   # a cauda alonga o lado de tras
if os.environ.get("CORUJA_INVERTER"): tras_pos = not tras_pos   # m1 (14/11): as pontas das asas (baixas e para tras) enganaram a deteccao
print("ORIENTACAO envergadura eixo", env, "cauda no lado", "+" if tras_pos else "-")
# queremos: envergadura em X, frente em -Y (cauda em +Y)
if env == 0: ang = 0.0 if tras_pos else math.pi                     # profundidade ja e Y
else: ang = -math.pi / 2 if tras_pos else math.pi / 2               # profundidade em X: girar 90 graus
me.transform(Matrix.Rotation(ang, 4, "Z"))
me.vertices.foreach_get("co", co.ravel()); mn, mx = co.min(0), co.max(0)
corpo = co[np.abs(co[:, 0] - (mn[0] + mx[0]) / 2) < 0.12 * (mx[0] - mn[0])]   # faixa central (sem as asas) para centrar em Y
me.transform(Matrix.Translation(V(((mn[0] + mx[0]) / 2, float(np.median(corpo[:, 1])), mn[2])) * -1))
me.vertices.foreach_get("co", co.ravel()); mn, mx = co.min(0), co.max(0)
k = ALTURA / float(mx[2]); me.transform(Matrix.Scale(k, 4))
me.vertices.foreach_get("co", co.ravel()); mn, mx = co.min(0), co.max(0)
cen = co[np.abs(co[:, 0]) < 0.08]
med = {"escala": k, "envergadura": float(mx[0] - mn[0]), "profundidade": float(mx[1] - mn[1]), "altura": float(mx[2]),
       "bico_y": float(cen[:, 1].min()), "cauda_y": float(cen[:, 1].max()),
       "tris": sum(len(p.vertices) - 2 for p in me.polygons), "materiais": [m.name for m in me.materials]}
print("MESHY_FINAL", json.dumps(med))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Coruja_meshy_bruto.blend"))
# ---------------- renders ----------------
def camera(nome, loc, alvo, lente=50, orto=None):
    c = bpy.data.cameras.new(nome); o = bpy.data.objects.new(nome, c); cena.collection.objects.link(o); o.location = loc
    if orto: c.type = "ORTHO"; c.ortho_scale = orto
    else: c.lens = lente
    o.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); return o
E = med["envergadura"]; H = med["altura"]
zc = H * 0.55; cab = V((0, med["bico_y"] + 0.06, H * 0.80))
VIS = {"frente": (camera("Cam_Frente", (0, -5, H / 2), (0, 0, H / 2), orto=E * 1.06), (1200, int(1200 * (H * 1.15) / (E * 1.06)))),
       "costas": (camera("Cam_Costas", (0, 5, H / 2), (0, 0, H / 2), orto=E * 1.06), (1200, int(1200 * (H * 1.15) / (E * 1.06)))),
       "lado": (camera("Cam_Lado", (-5, 0, H / 2), (0, 0, H / 2), orto=max(H, med["profundidade"]) * 1.25), (800, 800)),
       "tres_quartos": (camera("Cam_34", (-1.1 * E, -1.3 * E, 0.55 * E + H * 0.4), (0, 0, zc * 0.8), 32), (1000, 760)),
       "rosto": (camera("Cam_Rosto", tuple(cab + V((-0.22, -0.42, 0.04))), tuple(cab), 60), (800, 700))}
cena.render.image_settings.file_format = "PNG"; cena.render.image_settings.color_mode = "RGBA"; cena.view_settings.view_transform = "Standard"
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
mundo = bpy.data.worlds.new("Fundo"); cena.world = mundo
def render(n, arq):
    cam, r = VIS[n]; cena.camera = cam; cena.render.resolution_x, cena.render.resolution_y = r; cena.render.resolution_percentage = 100
    cena.render.film_transparent = True; cena.render.filepath = os.path.join(OUT, arq); bpy.ops.render.render(write_still=True)
cena.render.engine = "BLENDER_WORKBENCH"; sh = cena.display.shading
sh.light = "STUDIO"; sh.color_type = "SINGLE"; sh.single_color = (0.62, 0.60, 0.58); sh.show_cavity = True; sh.cavity_type = "WORLD"
for n in ("frente", "lado", "tres_quartos"): render(n, f"{VER}_A_{n}.png")
cena.render.engine = "BLENDER_EEVEE"
mundo.use_nodes = True; bg = mundo.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (*lin("8a8580"), 1); bg.inputs["Strength"].default_value = 0.9
sd = bpy.data.lights.new("Sol", "SUN"); sd.energy = 2.0; sd.angle = math.radians(12)
so = bpy.data.objects.new("Sol", sd); cena.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
try: cena.eevee.taa_render_samples = 48
except Exception: pass
for n in VIS: render(n, f"{VER}_B_{n}.png")
json.dump(med, open(os.path.join(OUT, f"{VER}_metricas.json"), "w"), indent=1)
print("MESHY_OK")
