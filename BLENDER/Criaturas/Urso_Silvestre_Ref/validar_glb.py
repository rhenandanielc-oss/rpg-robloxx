"""Reimporta um GLB numa cena vazia e confere malhas, triangulos (<= 20k por malha), materiais, imagens, UV e caixa.
Uso: blender -b --factory-startup -P validar_glb.py -- <arquivo.glb>"""
import bpy, sys
from mathutils import Vector as V
glb = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]; ok = True
for o in ms:
    t = sum(len(p.vertices) - 2 for p in o.data.polygons)
    imgs = sorted({n.image.name for m in o.data.materials if m and m.node_tree for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image})
    ok &= t <= 20000 and len(o.data.uv_layers) > 0 and len(o.data.materials) == 1
    print("GLB_MALHA %-16s tris=%6d uv=%d mats=%s imagens=%s" % (o.name, t, len(o.data.uv_layers), [m.name for m in o.data.materials], imgs))
pts = [o.matrix_world @ V(c) for o in ms for c in o.bound_box]
mn = V((min(p[i] for p in pts) for i in range(3))); mx = V((max(p[i] for p in pts) for i in range(3)))
print("GLB_CAIXA min", tuple(round(c, 2) for c in mn), "max", tuple(round(c, 2) for c in mx))
print("GLB_IMAGENS", sorted((i.name, i.size[0], i.size[1]) for i in bpy.data.images if i.size[0]))
print("GLB_VALIDO" if ok else "GLB_FALHOU")
