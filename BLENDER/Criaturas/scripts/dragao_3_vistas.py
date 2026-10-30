# Vistas de apresentacao do Dragao das Montanhas (frente, tras, lateral, escala com humano 5,2 studs).
import bpy, math, sys, os
from mathutils import Vector
OUT = sys.argv[sys.argv.index("--") + 1]; SRC = sys.argv[sys.argv.index("--") + 2]
bpy.ops.wm.open_mainfile(filepath=SRC)
scn = bpy.context.scene
arm = bpy.data.objects["Dragao_Rig"]
arm.animation_data_create(); arm.animation_data.action = bpy.data.actions["Repouso"]; scn.frame_set(1)
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 960; scn.render.resolution_y = 600
sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 3.2; so = bpy.data.objects.new("Sol", sun); scn.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(35))
scn.world = bpy.data.worlds.new("W"); scn.world.use_nodes = True; scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.58, 0.68, 1)
bpy.ops.mesh.primitive_plane_add(size=500, location=(0, 10, 0)); ch = bpy.context.active_object
cm = bpy.data.materials.new("Chao"); cm.use_nodes = True; cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.25, 0.32, 0.2, 1); ch.data.materials.append(cm)
# humano de referencia: cilindro de 5,2 studs com "cabeca"
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=4.2, location=(14, -24, 2.1)); bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(14, -24, 4.7))
cam = bpy.data.cameras.new("Cam"); co = bpy.data.objects.new("Cam", cam); scn.collection.objects.link(co); scn.camera = co; cam.lens = 35
for nome, loc, alvo in (("v_frente", (6, -125, 26), (0, 0, 16)), ("v_tras", (-6, 140, 30), (0, 10, 14)), ("v_lateral", (120, 4, 18), (0, 10, 14)),
                         ("v_escala", (32, -52, 9), (6, -16, 12))):
    co.location = loc; co.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
print("OK")
