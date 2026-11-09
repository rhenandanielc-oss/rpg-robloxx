"""Revisao do rig: ossos como tubos coloridos por cima da malha semitransparente (raio-X) + malha opaca, em vistas
ortograficas (lado/frente/cima) e 3/4. So leitura (nao salva).
Uso: blender -b rig/Lobo_Ancestral_Rig.blend -P render_rig.py -- <saida_dir> [opaco]"""
import bpy, bmesh, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for o in sc.objects:
    if o.type == "MESH" and o not in (LO,) and not o.name.startswith("Plane"): o.hide_render = True
m = bpy.data.meshes.new("Ossos"); b = bmesh.new()
for pb in arm.pose.bones:
    h, t = arm.matrix_world @ pb.head, arm.matrix_world @ pb.tail
    d = t - h; L = d.length
    if L < 1e-4: continue
    r_ = bmesh.ops.create_cone(b, cap_ends=True, segments=6, radius1=0.07, radius2=0.025, depth=L)
    q = d.to_track_quat("Z", "Y")
    for v in r_["verts"]: v.co = h + q @ (v.co + V((0, 0, L / 2)))
    r2 = bmesh.ops.create_uvsphere(b, u_segments=8, v_segments=4, radius=0.09)
    for v in r2["verts"]: v.co += h
b.to_mesh(m); b.free(); ob = bpy.data.objects.new("Ossos", m); sc.collection.objects.link(ob)
mat = bpy.data.materials.new("Osso")
if mat.node_tree is None: mat.use_nodes = True
bs = mat.node_tree.nodes["Principled BSDF"]; bs.inputs["Base Color"].default_value = (1, 0.2, 0.05, 1)
bs.inputs["Emission Color"].default_value = (1, 0.25, 0.05, 1); bs.inputs["Emission Strength"].default_value = 2.0
m.materials.append(mat)
opaco = "opaco" in A
if not opaco:
    for ms in LO.data.materials:
        nt = ms.node_tree; p = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"); p.inputs["Alpha"].default_value = 0.30
        try: ms.surface_render_method = "BLENDED"
        except Exception: ms.blend_method = "BLEND"
sc.render.resolution_x, sc.render.resolution_y = 1100, 900
cam = sc.camera; camd = cam.data
for nome, pos, alvo, orto in (("lado", V((30, -1.5, 4.2)), V((0, -1.5, 4.2)), 15.5), ("frente", V((0, -30, 4.2)), V((0, 0, 4.2)), 10),
                              ("cima", V((0, -1.0, 30)), V((0, -1.0, 0)), 15.5), ("tres_quartos", V((14, -14, 9)), V((0, -1, 3.8)), None)):
    camd.type = "ORTHO" if orto else "PERSP"
    if orto: camd.ortho_scale = orto
    else: camd.lens = 45
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(OUT, "rig_%s%s.png" % (nome, "_opaco" if opaco else "")); bpy.ops.render.render(write_still=True)
print("RENDER_RIG_OK")
