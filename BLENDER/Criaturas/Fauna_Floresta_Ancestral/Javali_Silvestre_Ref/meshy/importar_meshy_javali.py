"""Importa o GLB do Meshy do javali, orienta (frente = -Y, cascos em Z = 0, centrado em X), escala e renderiza
as mesmas vistas das revisoes r1-r3 (para prancha_r1.py com versao "m1").
Escala de trabalho (PROPOSTA, nao e porte oficial): meio do dorso (sem a crista) a 0,75 u; o cervo usa 1,15 u.
Uso: blender -b --factory-startup -P importar_meshy_javali.py -- <glb> <saida_dir> [girar_graus_z]"""
import bpy, sys, os, math, json
from mathutils import Vector as V, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; glb, OUT = a[0], os.path.abspath(a[1]); GIRO = float(a[2]) if len(a) > 2 else 0.0
os.makedirs(OUT, exist_ok=True)
VER = "m1"   # javali
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
cena = bpy.context.scene
ms = [o for o in cena.objects if o.type == "MESH"]
for o in cena.objects: o.select_set(o in ms)
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1: bpy.ops.object.join()
ob = bpy.context.object; ob.name = "CR_Javali_Meshy"
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM"); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in [o for o in cena.objects if o.type == "EMPTY"]: bpy.data.objects.remove(o)
me = ob.data
if GIRO: me.transform(Matrix.Rotation(math.radians(GIRO), 4, "Z"))
import numpy as np
co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
mn, mx = co.min(0), co.max(0)
print("MESHY_BRUTO tris", sum(len(p.vertices) - 2 for p in me.polygons), "caixa", mn.round(3), mx.round(3))
L = mx - mn; eixo = 0 if L[0] > L[1] else 1
# frente = ponta com o focinho/presas: a ponta mais BAIXA e estreita no ultimo 8% (a garupa e alta e larga; a cauda e fina mas alta)
q = L[eixo] * 0.08
def larg(lado):
    s_ = co[co[:, eixo] < mn[eixo] + q] if lado < 0 else co[co[:, eixo] > mx[eixo] - q]
    return float(s_[:, 2].max() - s_[:, 2].min()) * float(s_[:, 1 - eixo].max() - s_[:, 1 - eixo].min())
frente = -1 if larg(-1) > larg(1) else 1                              # o focinho com as presas e mais volumoso que a ponta da cauda
print("FRENTE areas", round(larg(-1), 4), round(larg(1), 4), "frente", frente)
ang = {(1, -1): 0.0, (1, 1): math.pi, (0, -1): -math.pi / 2, (0, 1): math.pi / 2}[(eixo, frente)]
me.transform(Matrix.Rotation(ang, 4, "Z"))
me.vertices.foreach_get("co", co.ravel()); mn, mx = co.min(0), co.max(0)
me.transform(Matrix.Translation(V(((mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2])) * -1))
me.vertices.foreach_get("co", co.ravel()); mn, mx = co.min(0), co.max(0)
comp = mx[1] - mn[1]
faixa = (co[:, 1] > mn[1] + comp * 0.50) & (co[:, 1] < mn[1] + comp * 0.70) & (np.abs(co[:, 0]) < 0.25 * (mx[0] - mn[0]))
dorso = float(np.percentile(co[faixa][:, 2], 92))                     # sem a ponta das cerdas da crista
k = 0.75 / dorso; me.transform(Matrix.Scale(k, 4))
me.vertices.foreach_get("co", co.ravel()); mn, mx = co.min(0), co.max(0)
nariz_y = float(mn[1])
med = {"escala": k, "comprimento": float(mx[1] - mn[1]), "largura": float(mx[0] - mn[0]), "altura": float(mx[2]),
       "tris": sum(len(p.vertices) - 2 for p in me.polygons), "nariz_y": nariz_y,
       "materiais": [m.name for m in me.materials]}
print("MESHY_FINAL", json.dumps(med))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Javali_meshy_bruto.blend"))

# ---------------- renders (mesmas janelas das revisoes) ----------------
def camera(nome, loc, rot=None, orto=None, alvo=None, lente=50):
    c = bpy.data.cameras.new(nome); o = bpy.data.objects.new(nome, c); cena.collection.objects.link(o)
    o.location = loc
    if orto: c.type = "ORTHO"; c.ortho_scale = orto
    else: c.lens = lente
    if rot: o.rotation_euler = [math.radians(x) for x in rot]
    if alvo: o.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler()
    return o
PPM, JAN = 600, (-0.05, 1.20)          # janela menor: javali baixo (dorso ~0,75 u)
cz = sum(JAN) / 2; hz = JAN[1] - JAN[0]
VIS = {"frente": (camera("Cam_Frente", (0, -6, cz), rot=(90, 0, 0), orto=hz), (384, int(hz * PPM))),
       "lado": (camera("Cam_Lado", (-6, nariz_y + 0.72, cz), rot=(90, 0, -90), orto=1.70), (1100, int(1100 * hz / 1.70))),
       "tres_quartos": (camera("Cam_TresQuartos", (-1.25, -1.7, 0.75), alvo=(0, -0.08, 0.42), lente=32), (900, 760))}
# rosto: alvo no ponto medio entre olho e focinho (estimado pela ponta da frente)
cab = co[co[:, 1] < nariz_y + 0.20]; zc_ = float(np.median(cab[:, 2]))
alvo_r = V((0, nariz_y + 0.12, zc_))
VIS["rosto_34"] = (camera("Cam_Rosto_34", tuple(alvo_r + V((-0.75, -0.95, 0.12))), alvo=tuple(alvo_r + V((0, 0.08, 0))), lente=60), (900, 700))
VIS["rosto_lado"] = (camera("Cam_Rosto_Lado", tuple(alvo_r + V((-1.40, -0.02, 0.02))), alvo=tuple(alvo_r + V((0, -0.02, 0))), lente=60), (900, 700))
cena.render.image_settings.file_format = "PNG"; cena.render.image_settings.color_mode = "RGBA"
cena.view_settings.view_transform = "Standard"
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
mundo = bpy.data.worlds.new("Fundo"); cena.world = mundo
def render(n, arq, res=None):
    cam, r = VIS[n]; r = res or r
    cena.camera = cam; cena.render.resolution_x, cena.render.resolution_y = r; cena.render.resolution_percentage = 100
    cena.render.film_transparent = True; cena.render.filepath = os.path.join(OUT, arq)
    bpy.ops.render.render(write_still=True)
# A: argila neutra (Workbench)
cena.render.engine = "BLENDER_WORKBENCH"; sh = cena.display.shading
sh.light = "STUDIO"; sh.color_type = "SINGLE"; sh.single_color = (0.62, 0.60, 0.58); sh.show_cavity = True; sh.cavity_type = "WORLD"
for n in ("frente", "lado", "tres_quartos"): render(n, f"{VER}_A_{n}.png")
render("tres_quartos", f"{VER}_A_miniatura.png", (180, 152))
# B: textura do Meshy, luz neutra (EEVEE) - mesma luz das revisoes
cena.render.engine = "BLENDER_EEVEE"
mundo.use_nodes = True; bg = mundo.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (*lin("8a8580"), 1); bg.inputs["Strength"].default_value = 0.9
sd = bpy.data.lights.new("Sol", "SUN"); sd.energy = 2.0; sd.angle = math.radians(12)
so = bpy.data.objects.new("Sol", sd); cena.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
try: cena.eevee.taa_render_samples = 48
except Exception: pass
for n in ("frente", "lado", "tres_quartos", "rosto_34", "rosto_lado"): render(n, f"{VER}_B_{n}.png")
render("tres_quartos", f"{VER}_B_miniatura.png", (180, 152))
json.dump(med, open(os.path.join(OUT, f"{VER}_metricas.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Javali_meshy_bruto.blend"))
print("MESHY_OK")
