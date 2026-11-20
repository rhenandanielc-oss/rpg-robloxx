"""20/11 - Montaria "igual ao Blender": exporta o cavaleiro de TESTE aprovado no Lote 5 (manequim R15 aproximado, acoes
DEMO_Cav_Montar/Desmontar/MontarDireita/DesmontarDireita/Sentado de CR_Crocodilo_Montaria_L5.blend) para o Roblox.
Por quadro (15 qps): centro da caixa LowerTorso e a rotacao (delta em relacao ao repouso, eixos do mundo) de cada parte
R15, convertidos para o espaco LOCAL DO PIVO do crocodilo no Roblox.
Eixos: Blender frente -Y, esquerda +X, Z para cima -> Roblox frente -Z, direita +X, Y para cima: (x, y, z) -> (-x, z, y).
Origem: o osso Raiz (repouso) do Blender = Raiz no Roblox, medido em 20/11: pivo + (0, -2.868, -4.2035).
Uso: blender -b CR_Crocodilo_Montaria_L5.blend -P exportar_cavaleiro.py -- <saida.json>"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix as Mx
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manequim_r15 as mq
A = sys.argv[sys.argv.index("--") + 1:]; OUT = A[0]
sc = bpy.context.scene
ra = bpy.data.objects[mq.NOME + "_Rig"]; croc = bpy.data.objects["CR_Croc_Rig"]
MAP = Mx(((-1, 0, 0), (0, 0, 1), (0, 1, 0)))                       # Blender -> Roblox (det +1)
RAIZ_B = croc.matrix_world @ croc.data.bones["Raiz"].head_local
RAIZ_R = V((0.0, -2.868, -4.2035))
def pos_r(p): return MAP @ (V(p) - RAIZ_B) + RAIZ_R
def rot_r(R3): return MAP @ R3 @ MAP.transposed()
ACOES = {"Montar": ("DEMO_Cav_Montar", "Croc_Montar"), "Desmontar": ("DEMO_Cav_Desmontar", "Croc_Desmontar"),
         "MontarDireita": ("DEMO_Cav_MontarDireita", "Croc_MontarDireita"), "DesmontarDireita": ("DEMO_Cav_DesmontarDireita", "Croc_DesmontarDireita"),
         "Sentado": ("DEMO_Cav_Sentado", None)}
PASSO = 2                                                            # 30 qps do Blender -> 15 qps
res = {"fps": 30 / PASSO, "partes": list(mq.PARTES.keys()), "acoes": {}, "origem": "CR_Crocodilo_Montaria_L5.blend (Lote 5 aprovado)"}
LTC = V(mq.PARTES["LowerTorso"][4])
for nome, (acao, acaoCroc) in ACOES.items():
    act = bpy.data.actions[acao]
    if not ra.animation_data: ra.animation_data_create()
    ra.animation_data.action = act
    if act.slots: ra.animation_data.action_slot = act.slots[0]
    if acaoCroc and acaoCroc in bpy.data.actions:                       # o crocodilo no mesmo quadro (so por consistencia)
        if not croc.animation_data: croc.animation_data_create()
        ca = bpy.data.actions[acaoCroc]; croc.animation_data.action = ca
        if ca.slots: croc.animation_data.action_slot = ca.slots[0]
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    quadros = []
    for f in range(f0, f1 + 1, PASSO):
        sc.frame_set(f); bpy.context.view_layer.update()
        q = {}; cen = {}
        for nm in mq.PARTES:
            pb = ra.pose.bones[nm]; bo = ra.data.bones[nm]
            W = ra.matrix_world @ pb.matrix; Wr = ra.matrix_world @ bo.matrix_local
            Rd = (W.to_3x3().normalized() @ Wr.to_3x3().normalized().inverted())
            qq = rot_r(Rd).to_quaternion()
            q[nm] = [round(qq.x, 4), round(qq.y, 4), round(qq.z, 4), round(qq.w, 4)]
            cc = W @ (Wr.inverted() @ (ra.matrix_world @ V(mq.PARTES[nm][4])))      # centro da caixa (conferencia)
            cen[nm] = [round(v, 3) for v in pos_r(cc)]
            if nm == "LowerTorso":
                lt = pos_r(cc)
        quadros.append({"lt": [round(lt.x, 3), round(lt.y, 3), round(lt.z, 3)], "r": q, "c": cen})
    res["acoes"][nome] = {"quadros": quadros, "dur": (f1 - f0) / 30.0}
    print("ACAO", nome, len(quadros), "quadros, dur", (f1 - f0) / 30.0, "LT ini", quadros[0]["lt"], "fim", quadros[-1]["lt"], flush=True)
json.dump(res, open(OUT, "w"), separators=(",", ":"))
print("CAVALEIRO_OK", OUT)
