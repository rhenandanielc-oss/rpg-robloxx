"""Abre Silverwing_M2M.blend, garante <=4 influencias normalizadas (sem DRV_root/root), renderiza descanso e quadros de
cada acao (vista 3/4 e lateral), salva o .blend. Uso: blender -b arq.blend -P revisar_silverwing.py -- saida_dir [quadros_por_acao]"""
import bpy, sys, os, math
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]; out = args[0]; nq = int(args[1]) if len(args) > 1 else 4
os.makedirs(out, exist_ok=True)
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
proib = {"root", "DRV_root"}
for b in A.data.bones: b.use_deform = b.name not in proib
gi = {g.index: g.name for g in M.vertex_groups}
mx_ant = 0
for v in M.data.vertices:
    gs = [(g.group, g.weight) for g in v.groups if g.weight > 1e-4 and gi[g.group] not in proib]
    mx_ant = max(mx_ant, len(gs))
    gs.sort(key=lambda x: -x[1]); manter = gs[:4]; s = sum(w for _, w in manter)
    for g in list(v.groups):
        M.vertex_groups[g.group].remove([v.index]) if g.group not in [i for i, _ in manter] else None
    for i, w in manter: M.vertex_groups[i].add([v.index], w / s if s > 0 else 0, "REPLACE")
mx = max((len([g for g in v.groups if g.weight > 1e-4]) for v in M.data.vertices), default=0)
sem = sum(1 for v in M.data.vertices if not any(g.weight > 1e-4 for g in v.groups))
print("INFLUENCIAS antes", mx_ant, "depois", mx, "sem_peso", sem)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 640, 420
w = bpy.data.worlds.new("w"); w.color = (0.55, 0.6, 0.66); sc.world = w
if "sol" not in bpy.data.objects:
    sun = bpy.data.objects.new("sol", bpy.data.lights.new("sol", "SUN")); sc.collection.objects.link(sun)
    sun.rotation_euler = (0.8, 0.2, 0.7); sun.data.energy = 3
    bpy.ops.mesh.primitive_plane_add(size=20); chao = bpy.context.object; chao.name = "chao_revisao"
    mc = bpy.data.materials.new("chao"); mc.diffuse_color = (0.3, 0.32, 0.3, 1); chao.data.materials.append(mc)
cam = bpy.data.objects.get("cam_rev") or bpy.data.objects.new("cam_rev", bpy.data.cameras.new("cam_rev"))
if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
sc.camera = cam
def centro():
    dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh()
    ps = [M.matrix_world @ v.co for v in me.vertices]
    mn = Vector([min(p[i] for p in ps) for i in range(3)]); mxv = Vector([max(p[i] for p in ps) for i in range(3)])
    M.evaluated_get(dg).to_mesh_clear(); return (mn + mxv) / 2, (mxv - mn).length, mn.z
def foto(nome):
    c, r, zmin = centro()
    for vista, d in (("34", (0.9, -1.0, 0.55)), ("lado", (1, 0.0, 0.12))):
        cam.location = c + Vector(d).normalized() * r * 1.45
        cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, "%s_%s.png" % (nome, vista)); bpy.ops.render.render(write_still=True)
    return zmin
A.animation_data_create(); A.animation_data.action = None
for pb in A.pose.bones: pb.matrix_basis.identity()
sc.frame_set(1); print("ZMIN descanso", round(foto("descanso"), 3))
for act in [a for a in bpy.data.actions if a.name.startswith("Silverwing_")]:
    A.animation_data.action = act
    if len(act.slots): A.animation_data.action_slot = act.slots[0]
    f0, f1 = act.frame_range
    for i in range(nq):
        f = int(round(f0 + (f1 - f0) * i / max(1, nq)))
        sc.frame_set(f); z = foto("%s_%02d" % (act.name.replace("Silverwing_", ""), i))
        print("QUADRO", act.name, f, "zmin", round(z, 3))
A.animation_data.action = None
for pb in A.pose.bones: pb.matrix_basis.identity()
bpy.ops.wm.save_mainfile()
print("REVISAR_OK")
