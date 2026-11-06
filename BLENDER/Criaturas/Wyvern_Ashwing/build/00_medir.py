# Wyvern (base Ashwing Drake Lite) - medidas de referencia antes da adaptacao. Somente leitura.
# Uso: blender -b --factory-startup -P 00_medir.py -- <glb>
import bpy, sys, json
from mathutils import Vector
src = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
mesh = [o for o in bpy.data.objects if o.type == "MESH" and o.name != "Icosphere"][0]
scn = bpy.context.scene
r = {}
# canais animados por acao: quais ossos tem location/scale
for a in bpy.data.actions:
    tipos = {}
    for fc in getattr(a, "fcurves", []) or []:
        tipos.setdefault(fc.data_path.split(".")[-1], set()).add(fc.data_path.split('"')[1] if '"' in fc.data_path else "?")
    if not tipos:
        for layer in a.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    for fc in cb.fcurves:
                        tipos.setdefault(fc.data_path.split(".")[-1], set()).add(fc.data_path.split('"')[1] if '"' in fc.data_path else "?")
    r[a.name] = {k: sorted(v) if k != "rotation_quaternion" else len(v) for k, v in tipos.items()}
# altura do dorso no idle: topo do corpo acima da articulacao do ombro (sem asas)
a = bpy.data.actions["idle_loop"]
arm.animation_data.action = a
try: arm.animation_data.action_slot = a.slots[0]
except Exception: pass
scn.frame_set(0)
dg = bpy.context.evaluated_depsgraph_get(); ev = mesh.evaluated_get(dg)
omb = arm.matrix_world @ arm.pose.bones["shoulder_L"].head
pel = arm.matrix_world @ arm.pose.bones["pelvis"].head
# grupos de asa: vertices com peso dominante em ossos de asa ficam fora
asa = {i for i, g in enumerate(mesh.vertex_groups) if any(k in g.name for k in ("upperarm", "forearm", "hand", "finger", "strut", "thumb"))}
topo = 0; topo_pel = 0
for v in mesh.data.vertices:
    gs = sorted(v.groups, key=lambda g: -g.weight)
    if gs and gs[0].group in asa: continue
    w = mesh.matrix_world @ ev.data.vertices[v.index].co
    if abs(w.y - omb.y) < 0.35 and abs(w.x) < 0.6: topo = max(topo, w.z)
    if abs(w.y - pel.y) < 0.3 and abs(w.x) < 0.6: topo_pel = max(topo_pel, w.z)
r["idle"] = {"ombro_artic_z": round(omb.z, 3), "dorso_ombro_z": round(topo, 3), "dorso_quadril_z": round(topo_pel, 3)}
# envergadura com asas abertas: maior largura no fly_loop
best = 0
for nome in ("fly_loop", "takeoff"):
    a = bpy.data.actions[nome]; arm.animation_data.action = a
    try: arm.animation_data.action_slot = a.slots[0]
    except Exception: pass
    for f in range(int(a.frame_range[0]), int(a.frame_range[1]) + 1, 2):
        scn.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = mesh.evaluated_get(dg)
        xs = [(mesh.matrix_world @ v.co).x for v in ev.data.vertices]
        best = max(best, max(xs) - min(xs))
r["envergadura_max_anim"] = round(best, 3)
# envergadura no repouso do rig (asas estendidas)
arm.animation_data.action = None
for pb in arm.pose.bones: pb.matrix_basis.identity()
scn.frame_set(0); dg = bpy.context.evaluated_depsgraph_get(); ev = mesh.evaluated_get(dg)
xs = [(mesh.matrix_world @ v.co).x for v in ev.data.vertices]; ys = [(mesh.matrix_world @ v.co).y for v in ev.data.vertices]
r["repouso"] = {"envergadura": round(max(xs) - min(xs), 3), "comprimento": round(max(ys) - min(ys), 3), "y_min": round(min(ys), 3), "y_max": round(max(ys), 3)}
r["cauda_y"] = {b: round((arm.matrix_world @ arm.data.bones[b].head_local).y, 3) for b in ("pelvis", "tail_01", "tail_05", "tail_10")}
print("MEDJSON" + json.dumps(r) + "MEDFIM")
