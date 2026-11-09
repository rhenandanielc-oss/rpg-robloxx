"""Importa o GLB do Meshy, orienta (frente = -Y, pes em Z=0, centrado em X), escala a cernelha para ALVO studs e
renderiza as vistas de revisao (mesmas cameras da prancha). O GLB original nao e alterado.
Uso: blender -b --factory-startup -P normalizar_meshy.py -- <lobo_meshy.glb> <saida_dir> [rot_z_graus] [cernelha_alvo]"""
import bpy, sys, os, math
from mathutils import Vector as V, Matrix
A = sys.argv[sys.argv.index("--") + 1:]
GLB, OUT = os.path.abspath(A[0]), os.path.abspath(A[1]); os.makedirs(OUT, exist_ok=True)
ROT = float(A[2]) if len(A) > 2 and A[2] != "auto" else None
ALVO = float(A[3]) if len(A) > 3 else 6.6
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=GLB)
malhas = [o for o in sc.objects if o.type == "MESH"]
for o in malhas: print("MALHA", o.name, len(o.data.polygons), "mats", [m.name for m in o.data.materials])
bpy.ops.object.select_all(action="DESELECT")
for o in malhas: o.select_set(True)
bpy.context.view_layer.objects.active = malhas[0]
if len(malhas) > 1: bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active; ob.name = "Lobo_Meshy"
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(sc.objects):
    if o is not ob: bpy.data.objects.remove(o)
vs = [v.co.copy() for v in ob.data.vertices]
zmin, zmax = min(v.z for v in vs), max(v.z for v in vs)
cen = sum(vs, V()) / len(vs)
if ROT is None:                                    # eixo do tronco por PCA (no plano XY); a cabeca (mais alta) vai para -Y
    H = zmax - zmin
    tr = [v for v in vs[::7] if zmin + 0.40 * H < v.z < zmin + 0.70 * H]
    mx = sum(v.x for v in tr) / len(tr); my = sum(v.y for v in tr) / len(tr)
    sxx = sum((v.x - mx) ** 2 for v in tr); syy = sum((v.y - my) ** 2 for v in tr); sxy = sum((v.x - mx) * (v.y - my) for v in tr)
    a = 0.5 * math.atan2(2 * sxy, sxx - syy); eixo = V((math.cos(a), math.sin(a), 0))
    topo = [v for v in vs if v.z > zmax - 0.12 * H]
    ct = sum(topo, V()) / len(topo)
    if (V((ct.x - mx, ct.y - my, 0))).dot(eixo) < 0: eixo = -eixo
    ROT = -90.0 - math.degrees(math.atan2(eixo.y, eixo.x))
print("ROT_Z", round(ROT, 1))
ob.data.transform(Matrix.Rotation(math.radians(ROT), 4, "Z")); ob.data.update()
vs = [v.co for v in ob.data.vertices]
xs, ys, zs = [v.x for v in vs], [v.y for v in vs], [v.z for v in vs]
off = V(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
ob.data.transform(Matrix.Translation(-off)); ob.data.update()
vs = [v.co for v in ob.data.vertices]
ys = [v.y for v in vs]; L = max(ys) - min(ys)
# cernelha: topo do dorso na faixa das patas dianteiras (entre 30% e 45% do comprimento a partir da frente)
y0 = min(ys) + 0.30 * L; y1 = min(ys) + 0.45 * L
faixa = [v.z for v in vs if y0 < v.y < y1 and abs(v.x) < 0.15 * L]
cern = max(faixa) if faixa else max(v.z for v in vs)
k = ALVO / cern
ob.data.transform(Matrix.Scale(k, 4)); ob.data.update()
vs = [v.co for v in ob.data.vertices]
print("MEDIDAS cernelha_bruta", round(cern, 3), "escala", round(k, 3), "altura", round(max(v.z for v in vs), 2),
      "comprimento", round(max(v.y for v in vs) - min(v.y for v in vs), 2), "largura", round(max(v.x for v in vs) - min(v.x for v in vs), 2),
      "tris", sum(len(p.vertices) - 2 for p in ob.data.polygons))
# cena de revisao (mesma luz da prancha)
w = bpy.data.worlds.new("Ceu"); sc.world = w
if w.node_tree is None: w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.32, 0.40, 0.30, 1); bg.inputs[1].default_value = 0.4
for nome, en, cor_, rot in (("Sol", 2.4, (1.0, 0.86, 0.66), (math.radians(55), 0, math.radians(150))),
                            ("Chave", 1.5, (1.0, 0.95, 0.88), (math.radians(60), 0, math.radians(-50))),
                            ("Preench", 0.5, (0.85, 0.95, 0.85), (math.radians(75), 0, math.radians(60)))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.color = cor_; l.angle = math.radians(4)
    lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=80); chao = bpy.context.object
m = bpy.data.materials.new("Chao")
if m.node_tree is None: m.use_nodes = True
m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.10, 0.12, 0.06, 1); chao.data.materials.append(m)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32
sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
camd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", camd); sc.collection.objects.link(cam); sc.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Meshy_normalizado.blend"))
cab = [v.co for v in ob.data.vertices if v.co.y < min(ys) + 0.15 * L] if False else None
yf = min(v.co.y for v in ob.data.vertices); zc = max(v.co.z for v in ob.data.vertices)
VISTAS = [("referencia", V((13.5, -15.0, 4.2)), V((0, 0.2, 4.6)), 50), ("lado", V((26, 0.0, 4.6)), V((0, 0, 4.6)), 50),
          ("frente", V((0, -26, 5.2)), V((0, 0, 4.8)), 50), ("tras", V((0, 26, 5.2)), V((0, 0, 4.6)), 50),
          ("tres_quartos", V((15, -15, 9.0)), V((0, 0, 4.4)), 50),
          ("cabeca", V((3.8, yf - 4.6, zc - 0.3)), V((0, yf + 1.0, zc - 1.4)), 60)]
for nome, pos, alvo, lente in VISTAS:
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
    sc.render.filepath = os.path.join(OUT, "vista_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("NORMALIZAR_OK")
