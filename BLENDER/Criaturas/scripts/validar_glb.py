# Reimporta o GLB exportado num Blender vazio e confere o que o importador do Roblox recebera.
import bpy, sys
SRC = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
print("ARMATURES", len(arms), "OSSOS", sum(len(a.data.bones) for a in arms))
for m in meshes:
    tris = sum(len(p.vertices) - 2 for p in m.data.polygons)
    infl = max((len([g for g in v.groups if g.weight > 0]) for v in m.data.vertices), default=0)
    dims = m.dimensions
    print("MESH", m.name, "TRIS", tris, "MAX_INFLUENCIAS", infl, "GRUPOS", len(m.vertex_groups), "DIM %.1f x %.1f x %.1f" % (dims.x, dims.y, dims.z))
print("ACOES", len(bpy.data.actions), sorted(a.name for a in bpy.data.actions))
print("IMAGENS", [(i.name, i.size[0], i.size[1]) for i in bpy.data.images])
print("MATERIAIS", [m.name for m in bpy.data.materials])
