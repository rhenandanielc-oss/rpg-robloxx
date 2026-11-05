"""E5 inspecao: renders da regiao peito/antebraco com faces de arestas longas (mechas) destacadas. Uso: blender -b E4b_r2.blend -P e5_00_ver_mecha.py -- <saida_dir>"""
import bpy, sys, os, math, bmesh
import numpy as np
from mathutils import Vector
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True); sc = bpy.context.scene
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; me = ob.data
for o in bpy.data.objects:
    if o.type == "ARMATURE": o.data.pose_position = "REST"
co = np.array([v.co for v in me.vertices]); E = np.array([e.vertices[:] for e in me.edges]); L = np.linalg.norm(co[E[:, 0]] - co[E[:, 1]], axis=1)
Lmax = np.zeros(len(co)); np.maximum.at(Lmax, E[:, 0], L); np.maximum.at(Lmax, E[:, 1], L)
# faces destacadas: alguma aresta > 0,8 na regiao do peito baixo / antebraco
reg = (co[:, 1] > -10.5) & (co[:, 1] < -5.0) & (co[:, 2] > 1.5) & (co[:, 2] < 6.5)
sel_f = [p.index for p in me.polygons if all(reg[v] for v in p.vertices) and max(Lmax[v] for v in p.vertices) > 0.8 and
         max(np.linalg.norm(co[p.vertices[i]] - co[p.vertices[(i + 1) % len(p.vertices)]]) for i in range(len(p.vertices))) > 0.8]
print("FACES_LONGAS", len(sel_f))
for side in (1, -1):
    fs = [f for f in sel_f if np.mean(co[list(me.polygons[f].vertices), 0]) * side > 0]
    c = co[np.unique(np.concatenate([list(me.polygons[f].vertices) for f in fs]))]
    print("LADO", side, len(fs), "faces; caixa", np.round(c.min(0), 2), np.round(c.max(0), 2))
# copia destacada em vermelho, levemente inflada
bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
dele = [f for f in bm.faces if f.index not in set(sel_f)]; bmesh.ops.delete(bm, geom=dele, context="FACES")
md = bpy.data.meshes.new("_dest"); bm.to_mesh(md); bm.free(); dest = bpy.data.objects.new("_dest", md); sc.collection.objects.link(dest)
mr = bpy.data.materials.new("_verm"); mr.use_nodes = True; nt = mr.node_tree; em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (1, 0.05, 0.6, 1)
nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs[0]); md.materials.append(mr)
dm = dest.modifiers.new("d", "DISPLACE"); dm.strength = 0.01
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.2; so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
arame = ob.copy(); arame.data = me; sc.collection.objects.link(arame); arame.modifiers.clear(); wm = arame.modifiers.new("W", "WIREFRAME"); wm.thickness = 0.01
ma = bpy.data.materials.new("_ar"); ma.use_nodes = True; e2 = ma.node_tree.nodes.new("ShaderNodeEmission"); e2.inputs[0].default_value = (0.03, 0.03, 0.05, 1)
ma.node_tree.links.new(e2.outputs[0], ma.node_tree.nodes["Material Output"].inputs[0])
for s in arame.material_slots: s.link = "OBJECT"; s.material = ma
def vista(nome, alvo, az, el, dist, arame_on):
    alvo = Vector(alvo); arame.hide_render = not arame_on
    cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = sc.render.resolution_y = 640; sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
A = (2.0, -7.5, 4.0)
for nome, az, el in (("lado_D", -90, 5), ("tras_D", -150, 10), ("frente_D", -10, 5), ("dentro_D", 90, 5), ("baixo_D", -120, -35)):
    vista(nome, A, az, el, 9, True)
vista("lado_E", (-2.0, -7.5, 4.0), 90, 5, 9, True); vista("frente_tex", (0, -8, 5), 0, 5, 16, False)
