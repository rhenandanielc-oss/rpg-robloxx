"""Perfil da linha das costas (so leitura): altura maxima da malha sem pelo solto (|x| < 0,6) por fatia de y, do pescoco a
cauda, num Clipe:quadro; "corcunda" = quanto a cernelha/ombros sobem acima da reta entre a nuca e o quadril.
Uso: blender -b <Anim.blend> -P perfil_costas.py -- Clipe:quadro[,...]"""
import bpy, sys
import numpy as np
LISTA = sys.argv[sys.argv.index("--") + 1].split(",")
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; PB = arm.pose.bones
for pb in PB:
    for c in pb.constraints: c.mute = True
gi = {g.index: g.name for g in LO.vertex_groups}
pelo = np.array([sum(g.weight for g in v.groups if gi[g.group].startswith(("Pelo", "Juba", "Cauda"))) for v in LO.data.vertices])
for item in LISTA:
    nome, q = item.split(":"); act = bpy.data.actions["Lobo_" + nome]
    arm.animation_data_create(); arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    sc.frame_set(int(act.frame_range[0]) + int(q)); bpy.context.view_layer.update()
    ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = ev.to_mesh(); co = np.array([v.co[:] for v in m.vertices]); ev.to_mesh_clear()
    s = (np.abs(co[:, 0]) < 0.6) & (pelo < 0.3)
    nuca = PB["Pescoco2"].head; quad = PB["Pelve"].head
    ys = np.arange(nuca.y, quad.y + 0.01, 0.5); topo = []
    for y in ys:
        f = s & (np.abs(co[:, 1] - y) < 0.25)
        topo.append(co[f, 2].max() if f.any() else np.nan)
    topo = np.array(topo); t0, t1 = topo[0], topo[-1]
    reta = t0 + (t1 - t0) * (ys - ys[0]) / (ys[-1] - ys[0])
    acima = topo - reta
    print("COSTAS %-12s corcunda max %.2f em y %.1f | ombro(Escapula) z %.2f  peito z %.2f  pelve z %.2f  nuca z %.2f | pitch raiz?" % (
        item, np.nanmax(acima), ys[np.nanargmax(acima)], PB["EscapulaE"].head.z, PB["Peito"].head.z, PB["Pelve"].head.z, nuca.z))
    print("   perfil", " ".join("y%.1f:%.2f" % (y, t) for y, t in zip(ys, topo)))
