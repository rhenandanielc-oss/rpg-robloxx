"""Diagnostico de apoio (so leitura): num Clipe:quadro, para cada pata mostra os ossos (punho/jarrete, bola, ponta dos
dedos) e a malha mais baixa por SUBREGIAO - dedos/almofada (Dedos/Pe), metacarpo/metatarso (Mao/Metatarso), antebraco/
canela - com o osso dominante e a altura relativa ao osso. Assim se ve se a penetracao vem da inclinacao do pe, da
flexao do punho, dos pesos ou do alvo de IK. Uso: blender -b <Anim.blend> -P diag_apoios.py -- Clipe:quadro[,...]"""
import bpy, sys
import numpy as np
LISTA = sys.argv[sys.argv.index("--") + 1].split(",")
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; PB = arm.pose.bones
for pb in PB:
    for c in pb.constraints: c.mute = True
gi = {g.index: g.name for g in LO.vertex_groups}
D = np.array([gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else "" for v in LO.data.vertices])
SUB = {"dian": [("dedos", "Dedos"), ("metacarpo", "Mao"), ("antebraco", "Antebraco")],
       "tras": [("dedos", "Pe"), ("metatarso", "Metatarso"), ("canela", "Canela")]}
for item in LISTA:
    nome, q = item.split(":"); act = bpy.data.actions["Lobo_" + nome]
    arm.animation_data_create(); arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    sc.frame_set(int(act.frame_range[0]) + int(q)); bpy.context.view_layer.update()
    ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = ev.to_mesh(); co = np.array([v.co[:] for v in m.vertices]); ev.to_mesh_clear()
    print("=== ", item)
    for tipo, s in (("dian", "E"), ("tras", "E")):
        if tipo == "dian": juntas = [("cotovelo", "Antebraco"), ("punho", "Mao"), ("bola", "Dedos")]
        else: juntas = [("joelho", "Canela"), ("jarrete", "Metatarso"), ("bola", "Pe")]
        txt = " ".join("%s z%.2f y%.2f" % (n, PB[b + s].head.z, PB[b + s].head.y) for n, b in juntas)
        ponta = PB[("Dedos" if tipo == "dian" else "Pe") + s].tail
        mb = PB[("Mao" if tipo == "dian" else "Metatarso") + s]; d = (mb.tail - mb.head).normalized()
        import math
        print("  %s%s ossos: %s ponta-dedos z%.2f | inclinacao do metacarpo/metatarso %.0f graus do chao" % (tipo, s, txt, ponta.z, math.degrees(math.asin(max(-1, min(1, -d.z))))))
        for sub, g in SUB[tipo]:
            idx = np.nonzero(D == g + s)[0]
            if not len(idx): continue
            z = co[idx, 2]; j = idx[np.argmin(z)]
            print("     %-10s min z %.3f  p10 %.3f  (vertice %d em y %.2f)" % (sub, z.min(), np.percentile(z, 10), j, co[j, 1]))
    for nm, gs in (("esterno", ("Peito", "Coluna2")), ("pelve", ("Pelve", "Coluna1")), ("queixo", ("Cabeca", "Mandibula")), ("cauda", tuple("Cauda%d" % i for i in range(1, 8)))):
        idx = np.nonzero(np.isin(D, gs))[0]; z = co[idx, 2]
        print("  %-8s min z %.3f p5 %.3f" % (nm, z.min(), np.percentile(z, 5)))
