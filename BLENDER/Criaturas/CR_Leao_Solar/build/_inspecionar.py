import bpy
from mathutils import Vector
dg = bpy.context.evaluated_depsgraph_get()
for ob in sorted(bpy.data.collections["LOW"].all_objects, key=lambda o: o.name):
    eo = ob.evaluated_get(dg)
    try:
        me = eo.to_mesh()
    except Exception:
        print(ob.name, "sem malha"); continue
    ws = [eo.matrix_world @ v.co for v in me.vertices]
    if not ws: print(ob.name, "vazia"); continue
    mn = Vector((min(w.x for w in ws), min(w.y for w in ws), min(w.z for w in ws)))
    mx = Vector((max(w.x for w in ws), max(w.y for w in ws), max(w.z for w in ws)))
    print("%-34s x %6.2f..%6.2f  y %6.2f..%6.2f  z %6.2f..%6.2f  rot %s" % (ob.name, mn.x, mx.x, mn.y, mx.y, mn.z, mx.z, tuple(round(r, 2) for r in ob.rotation_euler)))
    eo.to_mesh_clear()
