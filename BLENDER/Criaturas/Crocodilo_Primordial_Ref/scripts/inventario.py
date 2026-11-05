"""Somente leitura: actions, quadros, ossos e NLA de um .blend. Uso: blender -b <blend> -P inventario.py"""
import bpy
print("INV arquivo", bpy.data.filepath)
for a in bpy.data.actions:
    print("INV action", a.name, "quadros", tuple(int(x) for x in a.frame_range), "loop", a.get("loop"), "fcurves", sum(len(cb.fcurves) for l in a.layers for s in l.strips for cb in s.channelbags) if hasattr(a, "layers") else "")
for o in bpy.data.objects:
    if o.type == "ARMATURE":
        print("INV rig", o.name, "ossos", len(o.data.bones), "nla", [t.name for t in o.animation_data.nla_tracks] if o.animation_data else [])
    if o.type == "MESH": print("INV malha", o.name, "tris", sum(len(p.vertices) - 2 for p in o.data.polygons))
