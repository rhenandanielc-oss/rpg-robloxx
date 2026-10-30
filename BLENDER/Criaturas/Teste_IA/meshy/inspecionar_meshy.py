"""Inspecao SOMENTE LEITURA do GLB do Meshy: malhas, triangulos, armadura, animacoes, materiais/texturas, dimensoes.
Renderiza 4 vistas de referencia (sem salvar .blend)."""
import bpy, sys, os, math
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]; glb, out = args[0], args[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()
mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
for o in bpy.data.objects:
    print("OBJ", o.name, o.type, "parent", o.parent.name if o.parent else None, "scale", tuple(round(s, 3) for s in o.scale))
    if o.type == "MESH":
        me = o.data
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        print("  MESH verts", len(me.vertices), "faces", len(me.polygons), "tris", tris, "uv", [u.name for u in me.uv_layers],
              "mats", [m.name for m in me.materials if m], "vgroups", len(o.vertex_groups), "shapekeys",
              len(me.shape_keys.key_blocks) if me.shape_keys else 0)
        for v in o.bound_box:
            w = o.matrix_world @ Vector(v); mn = Vector(map(min, mn, w)); mx = Vector(map(max, mx, w))
    if o.type == "ARMATURE":
        print("  BONES", len(o.data.bones), [b.name for b in o.data.bones][:80])
print("BBOX min", tuple(round(c, 3) for c in mn), "max", tuple(round(c, 3) for c in mx), "size", tuple(round(c, 3) for c in (mx - mn)))
print("ACTIONS", [(a.name, tuple(a.frame_range)) for a in bpy.data.actions])
for im in bpy.data.images:
    print("IMG", im.name, tuple(im.size), im.colorspace_settings.name)
for m in bpy.data.materials:
    if m.use_nodes:
        print("MAT", m.name, [n.type for n in m.node_tree.nodes])
# vistas
sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_WORKBENCH"
sc.render.resolution_x, sc.render.resolution_y = 640, 480
w = bpy.data.worlds.new("w"); w.color = (0.75, 0.77, 0.8); sc.world = w
sun = bpy.data.objects.new("sol", bpy.data.lights.new("sol", "SUN")); sc.collection.objects.link(sun); sun.rotation_euler = (0.7, 0.2, 0.6)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
c = (mn + mx) / 2; r = (mx - mn).length
for nome, d in (("frente", (0, -1, 0.25)), ("lado", (1, 0, 0.2)), ("34", (0.8, -0.8, 0.5)), ("cima", (0.01, -0.2, 1))):
    dv = Vector(d).normalized(); cam.location = c + dv * r * 1.3
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, "meshy_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("INSPECAO_OK")
