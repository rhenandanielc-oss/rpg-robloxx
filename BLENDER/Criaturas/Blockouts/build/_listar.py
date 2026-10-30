import bpy
for ob in bpy.data.objects:
    print("OBJ", ob.type, ob.name, "parent=", ob.parent.name if ob.parent else "-", "mods=", [m.type for m in ob.modifiers] if ob.type=="MESH" else "")
