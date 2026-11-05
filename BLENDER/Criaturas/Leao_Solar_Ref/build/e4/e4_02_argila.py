"""Render de argila (material cinza unico) para comparar forma HIGH x LOW: 3/4, perfil, frente, close da juba e do rosto.
Uso: blender -b <arquivo.blend> -P e4_02_argila.py -- <prefixo_saida> [objeto_prefixo]"""
import bpy, sys, math
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]; OUT = A[0]; PRE = A[1] if len(A) > 1 else "Leao_Solar_E"
sc = bpy.context.scene; sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = True; sc.view_settings.view_transform = "Standard"
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.5, 0.5, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 3.0; sol.angle = math.radians(20)
so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(35))
m = bpy.data.materials.new("Argila"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.75, 0.72, 0.68, 1); b.inputs["Roughness"].default_value = 0.7
for o in bpy.data.objects:
    if o.type == "MESH":
        o.hide_render = not o.name.startswith(PRE)
        for i in range(len(o.data.materials)): o.data.materials[i] = m
        if not o.data.materials: o.data.materials.append(m)
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
def vista(nome, alvo, az, el, dist, lens=50, res=700):
    alvo = Vector(alvo); cd.lens = lens
    cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = sc.render.resolution_y = res; sc.render.filepath = OUT + "_" + nome + ".png"; bpy.ops.render.render(write_still=True)
vista("34", (0, -1, 9), -40, 12, 62)
vista("perfil", (0, 0, 8.5), -90, 0, 62)
vista("juba", (0, -10.5, 13.5), -35, 10, 22)
vista("rosto", (-0.2, -14.2, 13.0), -20, 5, 11)
vista("tufo", (0, 13.5, 4.5), -60, 10, 12)
vista("patas", (0, -7, 1.5), -30, 5, 14)
print("ARGILA_OK")
