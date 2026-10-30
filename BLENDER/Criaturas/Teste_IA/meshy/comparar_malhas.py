"""Compara de perto a membrana da asa e o quadril: GLB original (1M) x Silverwing_20k, mesma camera.
Tambem conta ilhas soltas e bordas abertas da malha atual do rig (.blend). Uso: blender -b -P comparar_malhas.py -- orig.glb red.glb rig.blend saida"""
import bpy, sys, os, bmesh
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]; orig, red, rig, out = a; os.makedirs(out, exist_ok=True)
def render(glb, pref):
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
    sc = bpy.context.scene; sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 560, 420
    w = bpy.data.worlds.new("w"); w.color = (0.6, 0.62, 0.66); sc.world = w
    sun = bpy.data.objects.new("s", bpy.data.lights.new("s", "SUN")); sc.collection.objects.link(sun); sun.rotation_euler = (0.8, 0.2, 0.7)
    cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam
    o = [x for x in bpy.data.objects if x.type == "MESH"][0]
    zmin = min((o.matrix_world @ v.co).z for v in o.data.vertices) if len(o.data.vertices) < 100000 else None
    for nome, c, d in (("asa", Vector((0.5, 0.1, 0.55)), Vector((0.3, -1, 0.5))), ("quadril", Vector((0.05, 0.15, 0.25)), Vector((1, 0.4, 0.2)))):
        if zmin is None: c = c + Vector((0, 0, -0.0))
        cam.location = c + d.normalized() * 0.75; cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, "%s_%s.png" % (pref, nome)); bpy.ops.render.render(write_still=True)
render(orig, "orig"); render(red, "red20k")
bpy.ops.wm.open_mainfile(filepath=rig)
M = bpy.data.objects["Silverwing"]; bm = bmesh.new(); bm.from_mesh(M.data); bm.verts.ensure_lookup_table()
gi = {g.index: g.name for g in M.vertex_groups}
def dom(v): return gi[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "-"
vis = set(); ilhas = []
for v in bm.verts:
    if v.index in vis: continue
    pilha = [v]; vis.add(v.index); comp = []
    while pilha:
        x = pilha.pop(); comp.append(x.index)
        for e in x.link_edges:
            y = e.other_vert(x)
            if y.index not in vis: vis.add(y.index); pilha.append(y)
    ilhas.append(comp)
ilhas.sort(key=len, reverse=True)
from collections import Counter
print("ILHAS", len(ilhas), "tamanhos", [len(i) for i in ilhas[:12]], "pequenas(<60)", sum(1 for i in ilhas if len(i) < 60), "verts nelas", sum(len(i) for i in ilhas if len(i) < 60))
print("ILHAS_PEQ_OSSOS", Counter(dom(M.data.vertices[i[0]]) for i in ilhas if len(i) < 60).most_common(10))
borda = [e for e in bm.edges if e.is_boundary]
print("BORDAS_ABERTAS", len(borda), Counter(dom(M.data.vertices[e.verts[0].index]) for e in borda).most_common(12))
print("COMPARAR_OK")
