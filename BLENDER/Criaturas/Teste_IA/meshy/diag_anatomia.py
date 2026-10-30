"""Diagnostico anatomico do Silverwing_M2M.blend (somente leitura): por acao/quadro
- posicao dos 4 pes (ponta dos dedos) relativa ao quadril/peito: espalhamento frente-tras e lateral, altura sobre o chao;
- comprimento das pernas (quadril->pe) vs repouso (perna encolhida/agrupada);
- cauda: angulo entre segmentos consecutivos (quebras), distancia base da cauda <-> quadril;
- repouso: comparacao com a malha original (pes do Meshy medidos pelas fatias).
Uso: blender -b arq.blend -P diag_anatomia.py"""
import bpy, math
from mathutils import Vector
sc = bpy.context.scene
A = bpy.data.objects["Silverwing_Rig"]
PES = {"PD_E": "front_toes_l", "PD_D": "front_toes_r", "PT_E": "back_toes_l", "PT_D": "back_toes_r"}
RAIZ = {"PD_E": "front_leg_collar_l", "PD_D": "front_leg_collar_r", "PT_E": "back_leg_hip_l", "PT_D": "back_leg_hip_r"}
CAUDA = ["tail_1", "tail_2", "tail_3", "tail_4", "tail_5", "tail_6", "tail_tip"]
def W(n): return A.matrix_world @ A.pose.bones[n].head
def Wt(n): return A.matrix_world @ A.pose.bones[n].tail
def medir():
    pes = {k: W(v) for k, v in PES.items()}
    pernas = {k: (pes[k] - W(RAIZ[k])).length for k in PES}
    fr = (pes["PD_E"] + pes["PD_D"]) / 2; tr = (pes["PT_E"] + pes["PT_D"]) / 2
    frente = (W("head") - W("hips")); frente.z = 0; frente.normalize()
    espalha_ft = (fr - tr).dot(frente)
    lat_f = (pes["PD_E"] - pes["PD_D"]).length; lat_t = (pes["PT_E"] - pes["PT_D"]).length
    alt = {k: round(p.z, 3) for k, p in pes.items()}
    angs = []
    for i in range(len(CAUDA) - 1):
        a = (Wt(CAUDA[i]) - W(CAUDA[i])).normalized(); b = (Wt(CAUDA[i + 1]) - W(CAUDA[i + 1])).normalized()
        angs.append(round(math.degrees(a.angle(b)), 1))
    base = (W("tail_1") - W("hips")).length
    a0 = (Wt("tail_1") - W("tail_1")).normalized(); sp = (W("hips") - W("spine_1")).normalized()
    return dict(ft=round(espalha_ft, 3), lat_f=round(lat_f, 3), lat_t=round(lat_t, 3), alt=alt,
                pernas={k: round(v, 3) for k, v in pernas.items()}, cauda_angs=angs, base=round(base, 3),
                cauda_vs_coluna=round(math.degrees(a0.angle(sp)), 1), quadril_z=round(W("hips").z, 3))
A.animation_data.action = None
for pb in A.pose.bones: pb.matrix_basis.identity()
sc.frame_set(1); R = medir(); print("REPOUSO", R)
comp_corpo = (W("head") - W("hips")).length
print("CORPO quadril->cabeca", round(comp_corpo, 3))
for act in sorted([a for a in bpy.data.actions if a.name.startswith("Silverwing_")], key=lambda a: a.name):
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range)
    for f in sorted({f0, (f0 + f1) // 4, (f0 + f1) // 2, 3 * (f0 + f1) // 4}):
        sc.frame_set(f); m = medir()
        print("Q", act.name.replace("Silverwing_", ""), f, "espalhaFT", m["ft"], "(rep", R["ft"], ") latF", m["lat_f"], "latT", m["lat_t"],
              "altPes", m["alt"], "pernas", m["pernas"], "quadZ", m["quadril_z"], "caudaAngs", m["cauda_angs"],
              "caudaVsColuna", m["cauda_vs_coluna"], "base", m["base"])
print("DIAG_OK")
