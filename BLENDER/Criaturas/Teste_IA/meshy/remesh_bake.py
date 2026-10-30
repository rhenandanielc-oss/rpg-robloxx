"""Malha leve LIMPA a partir do original (1M, intocado): remesh por voxel (fecha a casca, funde espinhos/escamas finas
que viravam 'lascas' achatadas na reducao), decimacao para <= alvo triangulos (limite do Roblox), UV nova e BAKE do
original -> cor (2048) + normal tangente (2048): o relevo dos espinhos/escamas fica no normal map, sem geometria fina.
Uso: blender -b -P remesh_bake.py -- orig.glb saida.glb voxel alvo [previa_dir]"""
import bpy, sys, os, bmesh, math
from mathutils import Vector, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; glb, saida, voxel, alvo = a[0], a[1], float(a[2]), int(a[3])
previa = a[4] if len(a) > 4 and a[4] != "sem_centrar" else None
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
hi = [o for o in bpy.data.objects if o.type == "MESH"][0]; hi.name = "HI"
mat_hi = hi.data.materials[0]
# pes no chao / centrado (mesma referencia da v2)
if "sem_centrar" not in a:                         # alta ja reposta vem nas coordenadas do rig: nao mexer
    zs = min(v.co.z for v in hi.data.vertices); xs = [v.co.x for v in hi.data.vertices]; ys = [v.co.y for v in hi.data.vertices]
    hi.data.transform(Matrix.Translation((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -zs)))
bm = bmesh.new(); bm.from_mesh(hi.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-5); bm.to_mesh(hi.data); bm.free()
# LO: copia -> voxel remesh -> decimate
lo = hi.copy(); lo.data = hi.data.copy(); lo.name = "Silverwing_LO"; bpy.context.scene.collection.objects.link(lo)
lo.data.materials.clear()
bpy.context.view_layer.objects.active = lo
for o in bpy.data.objects: o.select_set(o == lo)
lo.data.remesh_voxel_size = voxel; lo.data.use_remesh_fix_poles = True
bpy.ops.object.voxel_remesh()
print("REMESH verts", len(lo.data.vertices), "tris", sum(len(p.vertices) - 2 for p in lo.data.polygons))
m = lo.modifiers.new("dec", "DECIMATE"); m.ratio = min(1.0, alvo / max(1, sum(len(p.vertices) - 2 for p in lo.data.polygons)))
m.use_collapse_triangulate = True; bpy.ops.object.modifier_apply(modifier="dec")
bm = bmesh.new(); bm.from_mesh(lo.data)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-6); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(lo.data); bm.free()
for p in lo.data.polygons: p.use_smooth = True
from collections import deque
bm = bmesh.new(); bm.from_mesh(lo.data); bm.verts.ensure_lookup_table()
vis = [False] * len(bm.verts); ilhas = []
for v in bm.verts:
    if vis[v.index]: continue
    q = deque([v]); vis[v.index] = True; c = 0
    while q:
        x = q.popleft(); c += 1
        for e in x.link_edges:
            y = e.other_vert(x)
            if not vis[y.index]: vis[y.index] = True; q.append(y)
    ilhas.append(c)
print("LO verts", len(bm.verts), "tris", sum(len(f.verts) - 2 for f in bm.faces), "ilhas", sorted(ilhas, reverse=True)[:8],
      "bordas", sum(1 for e in bm.edges if e.is_boundary), "nao_manifold", sum(1 for e in bm.edges if len(e.link_faces) > 2)); bm.free()
# UV
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004)
bpy.ops.uv.pack_islands(margin=0.004)
bpy.ops.object.mode_set(mode="OBJECT")
# material com imagens de bake
RES = 2048
img_c = bpy.data.images.new("SW_Cor", RES, RES); img_n = bpy.data.images.new("SW_Normal", RES, RES); img_n.colorspace_settings.name = "Non-Color"
mat = bpy.data.materials.new("Silverwing_Mat"); lo.data.materials.append(mat)
nt = mat.node_tree; bsdf = nt.nodes.get("Principled BSDF")
tc = nt.nodes.new("ShaderNodeTexImage"); tc.image = img_c
tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = img_n
nm = nt.nodes.new("ShaderNodeNormalMap")
nt.links.new(tc.outputs["Color"], bsdf.inputs["Base Color"]); nt.links.new(tn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Roughness"].default_value = 0.65
# bake (selected -> active), Cycles CPU
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 4
bk = sc.render.bake; bk.use_selected_to_active = True; bk.use_cage = False; bk.cage_extrusion = voxel * 3; bk.max_ray_distance = voxel * 8; bk.margin = 8
for o in bpy.data.objects: o.select_set(o in (hi, lo))
bpy.context.view_layer.objects.active = lo
nt.nodes.active = tc
bk.use_pass_direct = False; bk.use_pass_indirect = False; bk.use_pass_color = True
bpy.ops.object.bake(type="DIFFUSE"); print("BAKE_COR_OK")
nt.nodes.active = tn
bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT"); print("BAKE_NORMAL_OK")
pasta = os.path.dirname(saida)
for im in (img_c, img_n):
    im.filepath_raw = os.path.join(pasta, im.name + ".png"); im.file_format = "PNG"; im.save()
bpy.data.objects.remove(hi)
for o in bpy.data.objects: o.select_set(o == lo)
bpy.ops.export_scene.gltf(filepath=saida, export_format="GLB", use_selection=True, export_image_format="JPEG")
print("GLB", saida, round(os.path.getsize(saida) / 1e6, 2), "MB")
if previa:
    os.makedirs(previa, exist_ok=True)
    sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 640, 480
    w = bpy.data.worlds.new("w"); w.color = (0.6, 0.62, 0.66); sc.world = w
    sun = bpy.data.objects.new("s", bpy.data.lights.new("s", "SUN")); sc.collection.objects.link(sun); sun.rotation_euler = (0.8, 0.2, 0.7); sun.data.energy = 3
    mat.use_backface_culling = True
    cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
    for nome, c, d, r in (("geral", Vector((0, 0, 0.5)), (0.9, -1, 0.6), 2.4), ("dorso", Vector((0, 0, 0.45)), (0.3, 0.6, 1), 1.0),
                          ("quadril", Vector((0.05, 0.25, 0.25)), (1, 0.3, 0.1), 0.8), ("cauda", Vector((0.2, 0.5, 0.3)), (0.2, 0.3, 1), 1.0)):
        cam.location = c + Vector(d).normalized() * r; cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(previa, "rb_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("REMESH_BAKE_OK")
