"""Reimporta o GLB exportado numa cena vazia, aplica quadros dos JSON de clipes (matrix_basis por osso) e renderiza:
confere que GLB + JSON reproduzem a pose (nomes, hierarquia, pesos, materiais e deformacao).
Uso: blender -b --factory-startup -P glb_json_pose.py -- <glb> <dir_clipes> <saida_dir> clipe:quadro[,clipe:quadro...]"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Quaternion, Matrix
A = sys.argv[sys.argv.index("--") + 1:]; GLB, CL, OUT = A[0], A[1], os.path.abspath(A[2]); PEDIDOS = A[3].split(",")
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=GLB)
arm = next(o for o in sc.objects if o.type == "ARMATURE"); malha = next(o for o in sc.objects if o.type == "MESH" and o.find_armature())
for o in sc.objects:
    if o.type == "MESH" and o is not malha: o.hide_render = True
print("GLB_REIMPORT ossos", len(arm.data.bones), "raiz", [b.name for b in arm.data.bones if not b.parent], "materiais", [m.name for m in malha.data.materials],
      "grupos", len(malha.vertex_groups), "modificador", [m.type for m in malha.modifiers])
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.43, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 1.3
l = bpy.data.lights.new("S", "SUN"); l.energy = 3.5; lo_ = bpy.data.objects.new("S", l); sc.collection.objects.link(lo_); lo_.rotation_euler = (0.8, 0, 2.4)
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 800, 450; sc.view_settings.view_transform = "AgX"
for ped in PEDIDOS:
    nome, q = ped.split(":"); q = int(q)
    d = json.load(open(os.path.join(CL, "Crocodilo_%s.json" % nome)))
    for pb in arm.pose.bones:
        s = d["ossos"].get(pb.name)
        if s is None: continue
        x, y, z, ww, tx, ty, tz = s[q * 7:q * 7 + 7]
        pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = Quaternion((ww, x, y, z)); pb.location = (tx, ty, tz)
    bpy.context.view_layer.update()
    for cn, p, a, lente in (("cabeca", V((8.0, -21.0, 5.5)), V((0, -12.5, 3.4)), 38), ("corpo", V((24, -22, 8)), V((0, -3, 2.4)), 32)):
        cam.location = p; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
        sc.render.filepath = os.path.join(OUT, "glb_%s_q%d_%s.png" % (nome, q, cn)); bpy.ops.render.render(write_still=True)
print("GLB_POSE_OK")
