"""Close de cabeca (textura/material) + uma pose de animacao em EEVEE, luz de estudio neutra (aprox. Roblox Studio).
Uso: blender -b <Esp>_final.blend -P render_closeup.py -- <Esp> <Acao:t>"""
import bpy, sys, os, math
from mathutils import Vector
ESP = sys.argv[sys.argv.index("--") + 1]
pose = sys.argv[sys.argv.index("--") + 2]
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(RAIZ, "review", ESP, "v2"); os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try: sc.render.engine = eng; break
    except TypeError: pass
sc.render.resolution_x, sc.render.resolution_y = 800, 600
w = bpy.data.worlds.new("W"); sc.world = w
bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND"); bg.inputs[0].default_value = (0.55, 0.6, 0.68, 1); bg.inputs[1].default_value = 0.9
sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 3.2; so = bpy.data.objects.new("Sol", sun); sc.collection.objects.link(so)
so.rotation_euler = (math.radians(50), 0, math.radians(30))
bpy.ops.mesh.primitive_plane_add(size=400); chao = bpy.context.active_object
m = bpy.data.materials.new("Chao"); b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"); b.inputs["Base Color"].default_value = (0.25, 0.27, 0.22, 1)
chao.data.materials.append(m)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
def mira(alvo, d, lente):
    cam_d.lens = lente; cam.location = alvo + d
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
# 3) tres angulos com textura
dg = bpy.context.evaluated_depsgraph_get()
pts = [o.matrix_world @ v.co for o in bpy.data.objects if o.type == "MESH" and o.parent == arm for v in list(o.data.vertices)[::40]]
mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
c = (mn + mx) / 2; r = (mx - mn).length
for nomev, d in (("frente", Vector((0, -1, 0.18))), ("lateral", Vector((1, 0, 0.12))), ("tres_quartos", Vector((0.75, -0.9, 0.45)))):
    mira(c, d.normalized() * r * 1.05, 40)
    sc.render.filepath = os.path.join(out, "%s.png" % nomev); bpy.ops.render.render(write_still=True)
# 1) close da cabeca (pose de descanso)
cab = next((b for b in arm.data.bones if b.name.startswith("Cabeca")), None)
if cab:
    h = arm.matrix_world @ ((cab.head_local + cab.tail_local) / 2)
    L = (cab.tail_local - cab.head_local).length
    mira(h, Vector((L * 1.6, -L * 2.2, L * 0.8)), 50)
    sc.render.filepath = os.path.join(out, "close_cabeca.png"); bpy.ops.render.render(write_still=True)
# 2) pose de animacao
nome, t = pose.split(":")
act = bpy.data.actions.get(nome)
if act:
    arm.animation_data.action = act
    f0, f1 = act.frame_range; sc.frame_set(int(f0 + float(t) * (f1 - f0)))
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in bpy.data.objects:
        if o.type == "MESH" and o.parent == arm:
            eo = o.evaluated_get(dg); me = eo.to_mesh(); pts += [eo.matrix_world @ v.co for v in list(me.vertices)[::40]]; eo.to_mesh_clear()
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))); mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    c = (mn + mx) / 2; r = (mx - mn).length
    mira(c, Vector((0.75, -0.95, 0.45)).normalized() * r * 1.1, 40)
    sc.render.filepath = os.path.join(out, "pose_%s.png" % nome); bpy.ops.render.render(write_still=True)
    arm.animation_data.action = None
    for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
print("RENDER_OK", ESP)
