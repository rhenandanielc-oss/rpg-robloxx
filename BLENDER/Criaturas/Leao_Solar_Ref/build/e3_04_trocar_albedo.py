"""Troca so o albedo da E2 (sem mover a malha). Uso: blender -b <e2.blend> -P 14_trocar_albedo.py -- <albedo.png> <saida.blend>"""
import bpy, sys, os
A = sys.argv[sys.argv.index("--") + 1:]; img = bpy.data.images.load(os.path.abspath(A[0])); n = 0
for m in bpy.data.objects[[o.name for o in bpy.data.objects if o.name.startswith("Leao_Solar_E")][0]].data.materials:
    for nd in m.node_tree.nodes:
        if nd.type == "TEX_IMAGE" and nd.image and nd.image.colorspace_settings.name == "sRGB": nd.image = img; n += 1
print("TROCA_OK", n); bpy.ops.wm.save_as_mainfile(filepath=A[1])
