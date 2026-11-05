"""Render somente leitura de um .blend existente (nao salva nada). Uso: blender -b arq.blend -P render_existente.py -- saida_prefixo"""
import bpy, sys, math
from mathutils import Vector
OUT = sys.argv[sys.argv.index("--") + 1]
sc = bpy.context.scene
obs = [o for o in sc.objects if o.type == "MESH" and o.visible_get()]
dg = bpy.context.evaluated_depsgraph_get()
mn = Vector((1e9,)*3); mx = Vector((-1e9,)*3)
for o in obs:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c); mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
print("BBOX", tuple(round(v,2) for v in mn), tuple(round(v,2) for v in mx))
ctr = (mn + mx) / 2; L = (mx - mn).length
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
for nome, d in (("lado", Vector((-1, 0, 0.05))), ("34", Vector((-0.75, -0.75, 0.30)))):
    cam.location = ctr + d.normalized() * L * 1.25; cam.rotation_euler = (ctr - cam.location).to_track_quat("-Z", "Y").to_euler()
    cd.lens = 50; sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.render.engine = "BLENDER_EEVEE"; sc.render.filepath = OUT + "_" + nome + ".png"
    if sc.world is None: sc.world = bpy.data.worlds.new("W")
    l = bpy.data.lights.new("S", "SUN"); l.energy = 3; lo = bpy.data.objects.new("S", l); sc.collection.objects.link(lo); lo.rotation_euler = (0.8, 0, 0.6)
    bpy.ops.render.render(write_still=True)
