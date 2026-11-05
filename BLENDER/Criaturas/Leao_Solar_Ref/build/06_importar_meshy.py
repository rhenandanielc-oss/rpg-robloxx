"""Importa o GLB do Meshy (Multi-Image to 3D das 3 vistas da referencia principal) e normaliza para o padrao do projeto:
1 unidade = 1 stud, frente = -Y (focinho), pes em Z=0, centrado em X. Escala: topo da juba = 18,66 studs (mesma conversao
da referencia com cernelha 11,5). Posicao em Y: ponta do focinho no Y da referencia (x=1103 px do perfil).
Uso: blender -b --factory-startup -P 06_importar_meshy.py -- <entrada.glb> <saida.blend>"""
import bpy, sys, math
from mathutils import Vector, Matrix
A = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=A[0])
mesh = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in bpy.context.scene.objects: o.select_set(o in mesh)
bpy.context.view_layer.objects.active = mesh[0]
if len(mesh) > 1: bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in list(bpy.context.scene.objects):
    if o != ob: bpy.data.objects.remove(o)
me = ob.data
def pts(): return [v.co for v in me.vertices]
# eixo longo horizontal e sentido da cabeca (onde esta o topo da juba)
xs = [p.x for p in pts()]; ys = [p.y for p in pts()]
eixo = "x" if (max(xs) - min(xs)) > (max(ys) - min(ys)) else "y"
zmax = max(p.z for p in pts()); zmin = min(p.z for p in pts()); topo = [p for p in pts() if p.z > zmax - 0.08 * (zmax - zmin)]
c_topo = sum(topo, Vector()) / len(topo); c = sum(pts(), Vector()) / len(me.vertices)
d = (c_topo - c); d.z = 0
ang = math.atan2(d.y, d.x)                         # direcao da cabeca no plano
rot = Matrix.Rotation(-math.pi / 2 - ang, 4, "Z")  # leva a cabeca para -Y
me.transform(rot)
K = 11.5 / 360.0; TOPO = (592 - 8) * K; Y_FOCINHO = -(1103 - 620) * K
z0 = min(p.z for p in pts()); s = TOPO / (max(p.z for p in pts()) - z0)
me.transform(Matrix.Translation((0, 0, -z0))); me.transform(Matrix.Scale(s, 4))
xc = (min(p.x for p in pts()) + max(p.x for p in pts())) / 2
me.transform(Matrix.Translation((-xc, Y_FOCINHO - min(p.y for p in pts()), 0)))
me.update(); ob.name = me.name = "Leao_Meshy_v1"
bb = [Vector(b) for b in ob.bound_box]
print("MESHY_OK eixo", eixo, "escala", round(s, 4), "tris", sum(len(p.vertices) - 2 for p in me.polygons),
      "X", round(bb[0].x, 2), round(bb[6].x, 2), "Y", round(bb[0].y, 2), round(bb[6].y, 2), "Z", round(bb[0].z, 2), round(bb[6].z, 2),
      "materiais", [m.name for m in me.materials])
col = bpy.data.collections.new("CR_Leao_Solar_E2_Meshy"); bpy.context.scene.collection.children.link(col)
bpy.context.scene.collection.objects.unlink(ob); col.objects.link(ob)
bpy.ops.wm.save_as_mainfile(filepath=A[1])
