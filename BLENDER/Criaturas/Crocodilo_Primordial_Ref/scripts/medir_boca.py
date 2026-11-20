"""Referencial e capacidade da BOCA do Crocodilo Primordial (20/11, encaixe real da presa). Le a malha do rig (vertices com
peso de Mandibula = arcada inferior; Cabeca = superior), gira a arcada inferior em torno da dobradica (eixo X) para cada
abertura alfa (0 = fechada; ABRE_MAX do anim_crocodilo = 12 graus alem da boca do Meshy) e mede, por profundidade d (ao
longo da boca, a partir da dobradica): folga entre as pontas dos dentes, folga interna (gengiva/palato, terco central) e
largura das arcadas. Saida: boca_medidas.json (unidades = studs, a malha e 1:1 com o Studio).
Uso: blender -b CR_Crocodilo_Rig_Olhos.blend --python scripts/medir_boca.py"""
import bpy, json, math
from mathutils import Matrix
arm = bpy.data.objects["CR_Croc_Rig"]; me = bpy.data.objects["CR_Croc_LOW"]
H = arm.matrix_world @ arm.data.bones["Mandibula"].head_local
CABF = (arm.matrix_world @ arm.data.bones["Cabeca"].tail_local) - (arm.matrix_world @ arm.data.bones["Cabeca"].head_local)
ANG = arm["ang_boca"]; ABRE_MAX = 12.0
low, up = [], []
for v in me.data.vertices:
    w = {me.vertex_groups[g.group].name: g.weight for g in v.groups}
    p = me.matrix_world @ v.co
    if p.y > H.y + 0.5: continue
    if w.get("Mandibula", 0) > 0.6: low.append(p)
    elif w.get("Cabeca", 0) > 0.6: up.append(p)
def rot(p, fecha):   # fecha > 0: a ponta da mandibula sobe (medido: +10 graus sobe a ponta 1,0)
    return H + (Matrix.Rotation(math.radians(-fecha), 4, "X") @ (p - H).to_4d()).to_3d()
res = {"dobradica": list(H), "eixo_cabeca": list(CABF.normalized()), "ang_meshy": ANG, "alfa_max": ANG + ABRE_MAX,
       "ponta_d": round(H.y - min(p.y for p in up), 3), "tabela": []}
for a in range(0, int(ANG + ABRE_MAX) + 1, 2):
    L = [rot(p, ANG - a) for p in low]
    for k in range(0, 12):
        d = 0.5 * k; y0 = H.y - d
        sl = [p for p in L if abs(p.y - y0) < 0.25]; su = [p for p in up if abs(p.y - y0) < 0.25]
        if len(sl) < 4 or len(su) < 4: continue
        wL = max(p.x for p in sl) - min(p.x for p in sl); wU = max(p.x for p in su) - min(p.x for p in su)
        inL = [p for p in sl if abs(p.x) < 0.30 * wL]; inU = [p for p in su if abs(p.x) < 0.30 * wU]
        zLt, zUb = max(p.z for p in sl), min(p.z for p in su)
        zLi = max(p.z for p in inL) if inL else zLt; zUi = min(p.z for p in inU) if inU else zUb
        res["tabela"].append({"alfa": a, "d": d, "folga_dentes": round(zUb - zLt, 3), "folga_interna": round(zUi - zLi, 3),
                              "meio_z": round((zUi + zLi) / 2 - H.z, 3), "larg": round(min(wL, wU), 3)})
open(bpy.path.abspath("//boca_medidas.json"), "w").write(json.dumps(res, indent=1))
print("MED_OK", len(res["tabela"]))
