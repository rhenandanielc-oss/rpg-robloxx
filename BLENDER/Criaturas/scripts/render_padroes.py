# Renderiza cada forma de dragao com cada um dos 3 padroes (troca so a textura de cor).
import bpy, math, sys, os, glob
from mathutils import Vector
OUT = sys.argv[sys.argv.index("--") + 1]; B = sys.argv[sys.argv.index("--") + 2]
for nome in ("Dragao_das_Montanhas", "Dragao_Glacial", "Dragao_Sombrio"):
    bpy.ops.wm.open_mainfile(filepath=os.path.join(B, nome + ".blend"))
    scn = bpy.context.scene
    arm = bpy.data.objects["Dragao_Rig"]; arm.animation_data_create(); arm.animation_data.action = bpy.data.actions["Rugido"]; scn.frame_set(50)
    scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 640; scn.render.resolution_y = 400
    sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 3.2; so = bpy.data.objects.new("Sol", sun); scn.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(35))
    scn.world = bpy.data.worlds.new("W"); scn.world.use_nodes = True; scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.58, 0.68, 1)
    cam = bpy.data.cameras.new("Cam"); co = bpy.data.objects.new("Cam", cam); scn.collection.objects.link(co); scn.camera = co; cam.lens = 35
    co.location = (62, -82, 38); co.rotation_euler = (Vector((0, -6, 19)) - co.location).to_track_quat("-Z", "Y").to_euler()
    mat = bpy.data.materials["Basalto"]
    tex = [n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and "_Cor_" in n.image.name][0]
    for png in sorted(glob.glob(os.path.join(B, nome + "_Cor_*.png"))):
        tex.image = bpy.data.images.load(png)
        pad = os.path.basename(png).split("_Cor_")[1][:-4]
        scn.render.filepath = os.path.join(OUT, "pad_%s_%s.png" % (nome, pad)); bpy.ops.render.render(write_still=True)
print("OK")
