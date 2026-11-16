"""Importa o GLB do Meshy e o coloca no mesmo referencial do modelo proprio: 1 u = 1 stud, frente = -Y, pes em Z=0,
centro em X=0, cernelha (topo do corpo logo atras da cabeca) = CERNELHA studs. Sem alterar a malha alem de
transformacao (escala/rotacao/translacao aplicadas). Salva <saida>/CR_LoboArtico_meshy_norm.blend.
Uso: blender -b --factory-startup -P normalizar_meshy.py -- <arquivo.glb> <saida_dir> [cernelha=6.6]"""
import bpy, sys, os, math
from mathutils import Vector as V, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; GLB, OUT = a[0], os.path.abspath(a[1]); CERNELHA = float(a[2]) if len(a) > 2 else 6.6
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1: bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active; ob.name = "CR_LoboArtico_Meshy"
for o in list(bpy.context.scene.objects):                       # vazios do import
    if o.type == "EMPTY": bpy.data.objects.remove(o)
ob.parent = None
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
vs = [v.co.copy() for v in ob.data.vertices]
def bbox(pts): return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]
lo, hi = bbox(vs)
eixo = 0 if (hi[0] - lo[0]) > (hi[1] - lo[1]) else 1           # eixo horizontal mais longo = comprimento do corpo
topo = max(vs, key=lambda p: p.z)                               # ponto mais alto = orelhas -> lado da cabeca
meio = (lo[eixo] + hi[eixo]) / 2
frente_pos = topo[eixo] > meio
# rotacao em Z que leva a frente para -Y
if eixo == 0: ang = math.radians(-90) if frente_pos else math.radians(90)
else: ang = math.radians(180) if frente_pos else 0.0
ob.data.transform(Matrix.Rotation(ang, 4, "Z"))
vs = [v.co.copy() for v in ob.data.vertices]; lo, hi = bbox(vs)
comp = hi[1] - lo[1]
# cernelha: topo na fatia 32-42% do comprimento a partir do focinho (atras da cabeca/orelhas)
fatia = [p.z for p in vs if lo[1] + 0.32 * comp <= p.y <= lo[1] + 0.42 * comp]
k = CERNELHA / (max(fatia) - lo[2])
ob.data.transform(Matrix.Translation(V((-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]))))
ob.data.transform(Matrix.Scale(k, 4))
vs = [v.co.copy() for v in ob.data.vertices]; lo, hi = bbox(vs)
ob.data.transform(Matrix.Translation(V((0, -0.78 - (lo[1] + hi[1]) / 2, 0))))   # mesmo centro do modelo proprio (camaras iguais)
vs = [v.co.copy() for v in ob.data.vertices]; lo, hi = bbox(vs)
col = bpy.data.collections.new("CR_LoboArtico"); bpy.context.scene.collection.children.link(col)
for c in ob.users_collection: c.objects.unlink(ob)
col.objects.link(ob)
print("MESHY_NORM eixo", "XY"[eixo], "frente_pos", frente_pos, "escala", round(k, 3), "tris",
      sum(len(p.vertices) - 2 for p in ob.data.polygons), "bbox", [round(x, 2) for x in lo], [round(x, 2) for x in hi],
      "materiais", [m.name for m in ob.data.materials])
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_meshy_norm.blend"))
print("MESHY_NORM_OK")
