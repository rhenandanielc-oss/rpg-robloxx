"""Referencia para conferir no Studio: posicao (relativa a cabeca do osso Raiz) de ossos-chave em poses conhecidas,
no espaco do Blender (frente -Y, Z para cima) e ja convertida para o eixo do glTF/Roblox (x, z, -y).
Uso: blender -b CR_Crocodilo_Anim.blend -P studio/referencia_poses.py -- <saida.json>"""
import bpy, sys, json
A = sys.argv[sys.argv.index("--") + 1:]
arm = bpy.data.objects["CR_Croc_Rig"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
OSSOS = ["Cabeca", "Mandibula", "Pescoco2", "Coluna2", "Cauda4", "Cauda8", "MaoE", "MaoD", "PeE", "PeD"]
CASOS = [("Repouso", 0), ("DescansoDeitado", 0), ("Corrida", 4), ("BoteAquatico", 16), ("RolarDaMorte", 9), ("DeitadoBocaAberta", 0)]
res = {}
for nome, q in CASOS:
    act = bpy.data.actions["Croc_" + nome]; arm.animation_data.action = act; arm.animation_data.action_slot = act.slots[0]
    bpy.context.scene.frame_set(int(act.frame_range[0]) + q); bpy.context.view_layer.update()
    r0 = arm.matrix_world @ arm.data.bones["Raiz"].head_local          # Raiz em REPOUSO (referencia fixa)
    d = {}
    for b in OSSOS:
        p = arm.matrix_world @ arm.pose.bones[b].tail - r0
        d[b] = [round(p.x, 3), round(p.z, 3), round(-p.y, 3)]           # eixo Roblox (glTF): x, z, -y
    res["%s:%d" % (nome, q)] = d
json.dump(res, open(A[0], "w"), indent=1)
print("REF_OK", len(res))
