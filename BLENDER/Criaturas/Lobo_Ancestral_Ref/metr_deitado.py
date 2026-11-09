"""Medidas do Deitado (so leitura): barriga (Coluna1/Coluna2 sem pelo) mais baixa, pelve, esterno, topo das costas por
regiao (cernelha y<-2, meio, garupa) e corcunda. Uso: blender -b <Anim.blend> -P metr_deitado.py -- <rotulo>"""
import bpy, sys
import numpy as np
R = sys.argv[sys.argv.index("--") + 1]
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; PB = arm.pose.bones
for pb in PB:
    for c in pb.constraints: c.mute = True
gi = {g.index: g.name for g in LO.vertex_groups}
D = np.array([gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else "" for v in LO.data.vertices])
pelo = np.array([sum(g.weight for g in v.groups if gi[g.group].startswith(("Pelo", "Cauda"))) for v in LO.data.vertices])
act = bpy.data.actions["Lobo_Deitado"]; arm.animation_data_create(); arm.animation_data.action = act
try: arm.animation_data.action_slot = act.slots[0]
except Exception: pass
sc.frame_set(int(act.frame_range[0])); bpy.context.view_layer.update()
ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = ev.to_mesh(); co = np.array([v.co[:] for v in m.vertices]); ev.to_mesh_clear()
def zmin(gs):
    i = np.isin(D, gs) & (pelo < 0.05)
    if not i.any(): i = np.isin(D, gs)
    return co[i, 2].min()
sm = np.abs(co[:, 0]) < 0.7
def topo(y0, y1): f = sm & (co[:, 1] > y0) & (co[:, 1] < y1); return co[f, 2].max()
print("DEIT %-28s barriga %.2f pelve %.2f esterno %.2f | topo cernelha %.2f meio %.2f garupa %.2f | pitch? Pelve osso %.2f Peito %.2f" % (
    R, zmin(["Coluna1", "Coluna2"]), zmin(["Pelve"]), zmin(["Peito"]), topo(-4.4, -2.0), topo(-2.0, 0.0), topo(0.0, 2.0), PB["Pelve"].head.z, PB["Peito"].head.z))
