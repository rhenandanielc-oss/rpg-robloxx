"""Lista a cadeia da asa esquerda (repouso e na pose Idle quadro 1): pai, cabeca, cauda, comprimento.
Uso: blender -b arq.blend -P diag_asa.py"""
import bpy
A = bpy.data.objects["Silverwing_Rig"]
def lista(b, nivel=0):
    print("ASA", "  " * nivel + b.name, "pai", b.parent.name if b.parent else "-", "cab", tuple(round(c, 3) for c in b.head_local),
          "cauda", tuple(round(c, 3) for c in b.tail_local), "L", round(b.length, 3))
    for c in b.children: lista(c, nivel + 1)
lista(A.data.bones["shoulder_l"])
act = bpy.data.actions["Silverwing_Idle"]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
bpy.context.scene.frame_set(int(act.frame_range[0]))
for pb in A.pose.bones:
    if pb.name.endswith("_l") and (pb.name.startswith("wing") or pb.name.startswith("shoulder")):
        print("IDLE", pb.name, "cab", tuple(round(c, 3) for c in pb.head), "cauda", tuple(round(c, 3) for c in pb.tail))
print("HIPS", tuple(round(c, 3) for c in A.data.bones["hips"].head_local), "SPINE2", tuple(round(c, 3) for c in A.data.bones["spine_2"].head_local))
