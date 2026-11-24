"""Referencia para conferir no Studio: posicao da CABECA (= Bone do Roblox), relativa a cabeca do osso Raiz em repouso, de ossos-chave em poses conhecidas,
no espaco do Blender (frente -Y, Z para cima) e ja convertida para o eixo do glTF/Roblox (x, z, -y).
Uso: blender -b rig/clipes_L3r7/CR_Cerbero_Anim.blend -P studio/referencia_poses.py -- <saida.json>"""
import bpy, sys, json
A = sys.argv[sys.argv.index("--") + 1:]
arm = bpy.data.objects["Cerbero_Rig"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
OSSOS = ["CabecaC", "MandibulaC", "CabecaE", "CabecaD", "PescocoC2", "Coluna2", "Cauda3", "MaoE", "MaoD", "PeE", "PeD"]
CASOS = [("Repouso", 0), ("Corrida", 5), ("MordidaE", 12), ("FuriaRugidoR4", 30), ("InvestidaSobre", 34), ("Deitar", 40)]
res = {}
for nome, q in CASOS:
    act = bpy.data.actions["Cerbero_" + nome]; arm.animation_data.action = act; arm.animation_data.action_slot = act.slots[0]
    bpy.context.scene.frame_set(int(act.frame_range[0]) + q); bpy.context.view_layer.update()
    r0 = arm.matrix_world @ arm.data.bones["Raiz"].head_local          # Raiz em REPOUSO (referencia fixa)
    d = {}
    for b in OSSOS:
        p = arm.matrix_world @ arm.pose.bones[b].head - r0          # CABECA do osso = posicao do Bone no Roblox
        d[b] = [round(p.x, 3), round(p.z, 3), round(-p.y, 3)]           # eixo Roblox (glTF): x, z, -y
    res["%s:%d" % (nome, q)] = d
json.dump(res, open(A[0], "w"), indent=1)
print("REF_OK", len(res))
