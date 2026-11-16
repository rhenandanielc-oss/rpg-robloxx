import bpy, mathutils
for o in bpy.data.objects:
    info = f"{o.name:28s} {o.type:9s} parent={o.parent.name if o.parent else '-'}"
    if o.type == 'MESH':
        me = o.data
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        bb = [o.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
        mn = [min(v[i] for v in bb) for i in range(3)]; mx = [max(v[i] for v in bb) for i in range(3)]
        mods = ",".join(m.type for m in o.modifiers)
        info += f" tris={tris} vg={len(o.vertex_groups)} mods={mods} min=({mn[0]:.2f},{mn[1]:.2f},{mn[2]:.2f}) max=({mx[0]:.2f},{mx[1]:.2f},{mx[2]:.2f}) mats={[m.name for m in me.materials if m]}"
    if o.type == 'ARMATURE':
        info += f" bones={len(o.data.bones)}"
    print(info)
print("acoes", len(bpy.data.actions))
