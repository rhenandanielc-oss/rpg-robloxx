"""Somente leitura: dispara um raio da camera por pixels de um render (pose da boca aberta) e informa a face atingida
(indice, vertices, pesos, posicao de repouso). Uso: blender -b CR_Crocodilo_Rig.blend -P pixel_face.py -- cam_x,cam_y,cam_z alvo_x,alvo_y,alvo_z lente graus px,py[;px,py...]"""
import bpy, sys, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]
P = V([float(c) for c in A[0].split(",")]); T = V([float(c) for c in A[1].split(",")]); LENTE = float(A[2]); ANG = float(A[3])
PX = [tuple(float(c) for c in p.split(",")) for p in A[4].split(";")]
sc = bpy.context.scene; arm = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
    pb.matrix_basis.identity()
pb = arm.pose.bones["Mandibula"]; pb.rotation_mode = "XYZ"; pb.rotation_euler = (math.radians(ANG), 0, 0)
cam = sc.camera; cam.location = P; cam.rotation_euler = (T - P).to_track_quat("-Z", "Y").to_euler(); cam.data.type = "PERSP"; cam.data.lens = LENTE
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
fr = cam.data.view_frame(scene=sc)            # cantos do quadro no espaco da camera: [sup-dir, inf-dir, inf-esq, sup-esq]
gm = lo.vertex_groups["Mandibula"].index
for px, py in PX:
    u, v = px / 1280, py / 720
    topo = fr[3].lerp(fr[0], u); base = fr[2].lerp(fr[1], u); p_cam = topo.lerp(base, v)
    d = (cam.matrix_world.to_3x3() @ p_cam).normalized()
    ok, loc, nrm, idx, ob, _ = sc.ray_cast(dg, cam.matrix_world.translation, d)
    if not ok: print("PIXEL", px, py, "nada"); continue
    pol = lo.data.polygons[idx] if ob.name == lo.name else None
    if pol is None: print("PIXEL", px, py, "objeto", ob.name); continue
    info = []
    for vi in pol.vertices:
        vv = lo.data.vertices[vi]; w = sum(g.weight for g in vv.groups if g.group == gm)
        info.append((vi, tuple(round(c, 2) for c in vv.co), round(w, 2)))
    print("PIXEL", px, py, "face", idx, "area_repouso %.4f" % pol.area, "normal_ok", round(nrm.dot(-d), 2), info)
