"""Reimporta um GLB e mede: malhas, tris, materiais, imagens, cernelha/altura/comprimento (Z para cima). So leitura.
Uso: blender -b --factory-startup -P validar_glb.py -- <arquivo.glb>"""
import bpy, sys
from mathutils import Vector as V
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index("--") + 1])
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
vs = [o.matrix_world @ v.co for o in ms for v in o.data.vertices]
ys = [v.y for v in vs]; L = max(ys) - min(ys)
cern = max(v.z for v in vs if min(ys) + 0.30 * L < v.y < min(ys) + 0.45 * L and abs(v.x) < 0.15 * L)
for o in ms: print("MALHA", o.name, "tris", sum(len(p.vertices) - 2 for p in o.data.polygons), "mats", [m.name for m in o.data.materials], "uv", len(o.data.uv_layers))
print("IMAGENS", [(i.name, tuple(i.size)) for i in bpy.data.images])
print("MEDIDAS cernelha %.2f altura %.2f comprimento %.2f largura %.2f zmin %.3f" % (cern, max(v.z for v in vs), L, max(v.x for v in vs) - min(v.x for v in vs), min(v.z for v in vs)))
