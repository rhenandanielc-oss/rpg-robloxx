"""E2 v2: a partir da E2 v1 (Meshy normalizado), troca o albedo pela textura corrigida e desloca 0,32 stud para a
frente (melhor encaixe do perfil: +10 px). Uso: blender -b <e2_v1.blend> -P 10_e2_v2.py -- <albedo.png> <saida.blend>"""
import bpy, sys
from mathutils import Matrix
A = sys.argv[sys.argv.index("--") + 1:]
ob = bpy.data.objects["Leao_Meshy_v1"]; ob.data.transform(Matrix.Translation((0, -10 * 11.5 / 360.0, 0))); ob.data.update()
import os; img = bpy.data.images.load(os.path.abspath(A[0])); n = 0
for m in ob.data.materials:
    for nd in m.node_tree.nodes:
        if nd.type == "TEX_IMAGE" and nd.image and nd.image.colorspace_settings.name == "sRGB":
            nd.image = img; n += 1
ob.name = "Leao_Solar_E2"; print("V2_OK texturas trocadas:", n)
pe = {}
for v in ob.data.vertices:
    q = ("D" if v.co.y < -3 else "T") + ("E" if v.co.x > 0 else "R")
    pe[q] = min(pe.get(q, 9), v.co.z)
print("PES_MIN_Z", {k: round(z, 3) for k, z in pe.items()})
bpy.ops.wm.save_as_mainfile(filepath=A[1])
