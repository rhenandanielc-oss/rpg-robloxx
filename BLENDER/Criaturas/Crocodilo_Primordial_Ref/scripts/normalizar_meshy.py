"""Importa o GLB do Meshy, orienta (frente = -Y, cauda +Y, pes em z=0, centrado em X), aplica a escala oficial
(comprimento alvo 29,5 studs; ombro <= 7) e monta a mesma cena neutra do CR_Crocodilo_Ref. Nao altera o GLB.
Uso: blender -b --factory-startup -P normalizar_meshy.py -- <glb> <saida.blend> [comprimento]"""
import bpy, sys, math
from mathutils import Vector as V, Matrix
A = sys.argv[sys.argv.index("--") + 1:]
GLB, SAIDA = A[0], A[1]; COMP = float(A[2]) if len(A) > 2 else 29.5
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=GLB)
obs = [o for o in sc.objects if o.type == "MESH"]
for o in sc.objects: o.select_set(o in obs)
bpy.context.view_layer.objects.active = obs[0]
if len(obs) > 1: bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active; ob.name = "CR_Croc_Meshy"
ob.parent = None; ob.matrix_world = ob.matrix_world.copy()
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(sc.objects):
    if o.type == "EMPTY": bpy.data.objects.remove(o)
me = ob.data
def pts(): return [v.co for v in me.vertices]
P = pts(); mn = V([min(p[i] for p in P) for i in range(3)]); mx = V([max(p[i] for p in P) for i in range(3)])
d = mx - mn; print("BRUTO dims", tuple(round(x, 3) for x in d))
# eixo do comprimento = maior eixo horizontal (X ou Y); alto = Z apos o import glTF
eixo = 0 if d.x >= d.y else 1
if eixo == 0: me.transform(Matrix.Rotation(math.radians(90), 4, "Z"))   # comprimento passa para Y
P = pts(); ys = [p.y for p in P]; y0, y1 = min(ys), max(ys); L = y1 - y0
def area_fatia(a, b):
    sel = [p for p in P if a <= p.y <= b]
    if not sel: return 0
    return (max(p.x for p in sel) - min(p.x for p in sel)) * (max(p.z for p in sel) - min(p.z for p in sel))
# ponta da cauda e fina; a cabeca e larga e alta
a_ini, a_fim = area_fatia(y0, y0 + 0.08 * L), area_fatia(y1 - 0.08 * L, y1)
print("FATIAS area inicio", round(a_ini, 4), "fim", round(a_fim, 4))
if a_ini < a_fim: me.transform(Matrix.Rotation(math.radians(180), 4, "Z"))    # cabeca fica em -Y
P = pts(); mn = V([min(p[i] for p in P) for i in range(3)]); mx = V([max(p[i] for p in P) for i in range(3)])
k = COMP / (mx.y - mn.y)
me.transform(Matrix.Translation(V((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))))
me.transform(Matrix.Scale(k, 4)); me.update()
P = pts(); mn = V([min(p[i] for p in P) for i in range(3)]); mx = V([max(p[i] for p in P) for i in range(3)])
def topo_em(y, faixa=0.6):
    sel = [p.z for p in P if abs(p.y - y) < faixa and abs(p.x) < 1.2]
    return max(sel) if sel else float("nan")
perfil = [(round(y, 1), round(topo_em(y), 2)) for y in [mn.y + (mx.y - mn.y) * f for f in (0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.7, 0.85)]]
print("MEDIDAS comprimento %.2f largura %.2f altura_max %.2f" % (mx.y - mn.y, mx.x - mn.x, mx.z))
print("PERFIL_TOPO (y, z)", perfil)
tris = sum(len(p.vertices) - 2 for p in me.polygons)
print("TRIS", tris, "materiais", [m.name for m in me.materials],
      "imagens", [(i.name, tuple(i.size)) for i in bpy.data.images])
# cena neutra (mesma do CR_Crocodilo_Ref)
w = bpy.data.worlds.new("Neutro"); sc.world = w
if w.node_tree is None: w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.43, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.3
for nome, en, rot in (("Chave", 3.6, (math.radians(45), 0, math.radians(140))), ("Preench", 1.0, (math.radians(60), 0, math.radians(-60))),
                      ("Contra", 1.6, (math.radians(120), 0, math.radians(10)))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.angle = math.radians(8); lo = bpy.data.objects.new(nome, l)
    sc.collection.objects.link(lo); lo.rotation_euler = rot
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 48
for kk, v in (("use_raytracing", True), ("use_shadows", True)):
    if hasattr(sc.eevee, kk): setattr(sc.eevee, kk, v)
sc.view_settings.view_transform = "AgX"; sc.render.resolution_x, sc.render.resolution_y = 1672, 941
camd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", camd); sc.collection.objects.link(cam); sc.camera = cam
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=SAIDA)
print("NORMALIZADO_OK", SAIDA)
