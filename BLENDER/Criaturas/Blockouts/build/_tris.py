import bpy
m = max(((sum(len(p.vertices) - 2 for p in o.data.polygons)), o.name) for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("REF_"))
print("MAIOR_OBJETO", m)
print("OBJETOS_MALHA", sum(1 for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith("REF_")))
