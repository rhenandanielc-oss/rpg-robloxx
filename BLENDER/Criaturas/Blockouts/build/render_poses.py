"""Folha de poses de animacao (evidencia): renderiza quadros-chave de varias acoes do <Esp>_final.blend em Workbench.
Uso: blender -b <Esp>_final.blend -P render_poses.py -- <Esp> Acao1:t Acao2:t ..."""
import bpy, sys, os, math
from mathutils import Vector
ESP = sys.argv[sys.argv.index("--") + 1]
pedidos = sys.argv[sys.argv.index("--") + 2:]
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
sc.display.shading.show_shadows = True
sc.render.resolution_x, sc.render.resolution_y = 640, 480
sc.render.film_transparent = False
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
obs = [o for o in bpy.data.objects if o.type == "MESH"]
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam_d.lens = 40
out = os.path.join(RAIZ, "review", ESP, "poses"); os.makedirs(out, exist_ok=True)
for ped in pedidos:
    nome, t = ped.split(":"); t = float(t)
    act = bpy.data.actions.get(nome)
    if not act:
        print("SEM", nome); continue
    arm.animation_data.action = act
    for tr in arm.animation_data.nla_tracks: tr.mute = True
    f0, f1 = act.frame_range
    sc.frame_set(int(f0 + t * (f1 - f0)))
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in obs:
        eo = o.evaluated_get(dg); me = eo.to_mesh()
        pts += [eo.matrix_world @ v.co for v in list(me.vertices)[::25]]
        eo.to_mesh_clear()
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    c = (mn + mx) / 2; r = (mx - mn).length
    d = Vector((math.sin(math.radians(55)), -math.cos(math.radians(55)), 0.45)).normalized()
    cam.location = c + d * r * 1.25
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, "%s_%02d.png" % (nome, int(t * 100)))
    bpy.ops.render.render(write_still=True)
    print("POSE", nome, t)

