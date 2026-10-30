"""Silhueta lateral ortografica (preta sobre cinza) com o humano de 5,2 studs a frente do focinho, no arranjo do
painel oficial (03_CREATURES/01: silhueta com humano). Mesma camera para todas as versoes.
Uso: blender -b <blend> -P render_silhueta.py -- <saida.png>"""
import bpy, sys, os, math
from mathutils import Vector
out = sys.argv[sys.argv.index("--") + 1]
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "FLAT"; sc.display.shading.color_type = "SINGLE"; sc.display.shading.single_color = (0.02, 0.02, 0.02)
sc.display.shading.background_type = "VIEWPORT"
sc.render.resolution_x, sc.render.resolution_y = 1000, 600
w = bpy.data.worlds.new("W"); sc.world = w; w.color = (0.32, 0.32, 0.33)
sc.display.shading.background_type = "WORLD"
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
if arm:
    if arm.animation_data:
        for tr in arm.animation_data.nla_tracks: tr.mute = True
        arm.animation_data.action = None
    for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
for o in list(bpy.data.objects):
    if o.type in ("LIGHT", "CAMERA") or o.name.startswith("REF_"): bpy.data.objects.remove(o, do_unlink=True)
import bmesh
bm = bmesh.new()                                                 # humano 5,2 studs (cabeca + corpo + pernas)
bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=0.5); bmesh.ops.translate(bm, vec=(0, 0, 4.7), verts=bm.verts)
t = bmesh.new(); bmesh.ops.create_cube(t, size=1.0); bmesh.ops.scale(t, vec=(0.7, 1.3, 2.0), verts=t.verts); bmesh.ops.translate(t, vec=(0, 0, 3.2), verts=t.verts)
me = bpy.data.meshes.new("h"); t.to_mesh(me); bm.from_mesh(me)
t = bmesh.new(); bmesh.ops.create_cube(t, size=1.0); bmesh.ops.scale(t, vec=(0.6, 1.1, 2.2), verts=t.verts); bmesh.ops.translate(t, vec=(0, 0, 1.1), verts=t.verts)
t.to_mesh(me); bm.from_mesh(me)
hm = bpy.data.meshes.new("Humano"); bm.to_mesh(hm); ho = bpy.data.objects.new("Humano", hm); sc.collection.objects.link(ho)
from mathutils import Vector
pts = [o.matrix_world @ v.co for o in bpy.data.objects if o.type == "MESH" and o != ho for v in list(o.data.vertices)[::30]]
mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
ho.location = (0, mn.y - 2.5, 0)                                   # humano a frente do focinho
larg = max(17.0, (mx.y - mn.y + 4.0) * 1.08, mx.z * 1.9)
cd = bpy.data.cameras.new("c"); cd.type = "ORTHO"; cd.ortho_scale = larg
cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (60, (mn.y - 2.5 + mx.y) / 2, larg * 0.3); cam.rotation_euler = (math.radians(90), 0, math.radians(90))
sc.render.filepath = out; bpy.ops.render.render(write_still=True)
print("SIL_OK")
