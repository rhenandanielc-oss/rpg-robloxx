"""E5: renders ortograficos da cabeca (frente, lado, cima) com grade de coordenadas (para achar orelhas/olhos).
Uso: blender -b E4b_r2.blend -P e5_06_cabeca_grade.py -- <saida_dir>"""
import bpy, sys, os, math
from mathutils import Vector
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True); sc = bpy.context.scene
for o in bpy.data.objects:
    if o.type == "ARMATURE": o.data.pose_position = "REST"
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.5, 0.5, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.4; so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False
cd = bpy.data.cameras.new("C"); cd.type = "ORTHO"; cd.ortho_scale = 8; cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
# grade: linhas finas a cada 0,5 (grossas a cada 1)
mg = bpy.data.materials.new("_g"); mg.use_nodes = True; e = mg.node_tree.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value = (0, 1, 1, 1)
mg.node_tree.links.new(e.outputs[0], mg.node_tree.nodes["Material Output"].inputs[0])
def grade(plano, c, nome):
    import bmesh
    bm = bmesh.new(); r = 4.0
    for k in range(-8, 9):
        t = k * 0.5; w_ = 0.012 if k % 2 else 0.03
        for a, b in (((t, -r), (t, r)), ((-r, t), (r, t))):
            p0 = [0, 0, 0]; p1 = [0, 0, 0]
            i, j, f = plano; p0[i], p0[j], p0[f] = c[i] + a[0], c[j] + a[1], c[f]; p1[i], p1[j], p1[f] = c[i] + b[0], c[j] + b[1], c[f]
            v0 = Vector(p0); v1 = Vector(p1); d = (v1 - v0).normalized(); nrm = [0, 0, 0]; nrm[f] = 1; side = d.cross(Vector(nrm)) * w_
            vs = [bm.verts.new(v0 - side), bm.verts.new(v1 - side), bm.verts.new(v1 + side), bm.verts.new(v0 + side)]; bm.faces.new(vs)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); ob = bpy.data.objects.new(nome, me); sc.collection.objects.link(ob); me.materials.append(mg); return ob
C = Vector((0, -13.2, 14.2))
for nome, pos, plano, frente in (("frente", Vector((0, -30, 14.2)), (0, 2, 1), -17.5), ("lado", Vector((30, -13.2, 14.2)), (1, 2, 0), 3.5), ("cima", Vector((0, -13.2, 40)), (0, 1, 2), 17.5)):
    c = list(C); c[plano[2]] = frente; g = grade(plano, c, "_g" + nome)
    cam.location = pos; cam.rotation_euler = (C - pos).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = sc.render.resolution_y = 800; sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
    g.hide_render = True
print("OK")
