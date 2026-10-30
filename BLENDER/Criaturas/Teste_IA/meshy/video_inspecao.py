"""Inspecao para o video de demonstracao: acoes, faixas, fps, objetos, eixo de frente."""
import bpy, json
sc = bpy.context.scene
A = bpy.data.objects["Silverwing_Rig"]
out = {"fps": sc.render.fps, "objs": [(o.name, o.type, tuple(round(v, 3) for v in o.dimensions), o.parent.name if o.parent else None) for o in bpy.data.objects],
       "rig_loc": tuple(A.location), "rig_rot": tuple(A.rotation_euler), "rig_scale": tuple(A.scale),
       "acoes": {a.name: tuple(a.frame_range) for a in bpy.data.actions if a.name.startswith("Silverwing_")},
       "ossos_raiz": [b.name for b in A.data.bones if not b.parent],
       "mundo": bpy.data.worlds[0].name if bpy.data.worlds else None, "materiais": [m.name for m in bpy.data.materials]}
# deslocamento do osso raiz/quadril ao longo de clipes de locomocao (clipes no lugar ou com avanco?)
for nome in ("Andar", "Correr", "Voo", "Decolagem", "Pouso"):
    act = bpy.data.actions.get("Silverwing_" + nome)
    if not act: continue
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); pos = []
    for f in (f0, (f0 + f1) // 2, f1):
        sc.frame_set(f); pb = A.pose.bones[0]; pos.append(tuple(round(v, 3) for v in (A.matrix_world @ pb.head)))
    out["mov_" + nome] = [A.pose.bones[0].name, pos]
print("INSP_JSON" + json.dumps(out))
