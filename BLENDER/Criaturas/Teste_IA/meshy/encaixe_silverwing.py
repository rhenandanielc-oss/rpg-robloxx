"""Posicoes do esqueleto Mesh2Motion (rig-dragon, 99 ossos) encaixado no Silverwing_20k (unidades do GLB, frente -Y,
esquerda do dragao = +X = sufixo _l). Medido em vistas ortograficas com grade + fatias horizontais (fatias.py).
Gera encaixe.json: {"ossos": {nome: [cabeca, cauda]}, "juntas": {...}, "ligacoes": [...]} para vistas_grade.py e o montador."""
import json, os

def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(3)]

P = dict(
    S0=[-0.02, 0.05, 0.34], S1=[-0.06, -0.12, 0.40], S2=[-0.09, -0.22, 0.46], S3=[-0.10, -0.245, 0.56],
    S4=[-0.105, -0.255, 0.64], S5=[-0.11, -0.28, 0.71], H1=[-0.115, -0.33, 0.71], MU=[-0.12, -0.37, 0.695],
)
O = {
    "root": [[-0.04, 0.04, 0.0], [-0.04, 0.25, 0.0]],
    "hips": [[-0.02, 0.14, 0.31], [-0.02, 0.10, 0.31]],
    "spine_0": [P["S0"], P["S1"]], "spine_1": [P["S1"], P["S2"]], "spine_2": [P["S2"], P["S3"]],
    "spine_3": [P["S3"], P["S4"]], "spine_4": [P["S4"], P["S5"]], "head": [P["S5"], P["H1"]],
    "mouth_upper": [P["H1"], P["MU"]], "mouth_upper_tip": [P["MU"], [-0.125, -0.415, 0.67]],
    "mouth_lower": [[-0.115, -0.32, 0.69], [-0.12, -0.36, 0.67]], "mouth_lower_tip": [[-0.12, -0.36, 0.67], [-0.125, -0.40, 0.655]],
    "stomach": [P["S1"], [-0.06, -0.10, 0.30]], "stomach_tip": [[-0.06, -0.10, 0.30], [-0.06, -0.08, 0.22]],
}
def cadeia(nomes, pts, pai_cauda):
    a = pai_cauda
    for n, p in zip(nomes, pts):
        O[n] = [a, p]; a = p
cadeia(["horn_base_l", "horn_l", "horn_tip_L"], [[-0.075, -0.27, 0.76], [-0.06, -0.24, 0.81], [-0.045, -0.21, 0.85]], P["S5"])
cadeia(["horn_base_r", "horn_r", "horn_tip_R"], [[-0.145, -0.27, 0.76], [-0.16, -0.24, 0.81], [-0.175, -0.21, 0.85]], P["S5"])
# patas dianteiras (pe esq. do dragao em x~-0.01, dir. em x~-0.25)
cadeia(["collar_anchor_l", "front_leg_collar_l", "front_leg_l", "front_ankle_l", "front_foot_l", "front_toes_l", "front_toes_tip_l"],
       [[-0.04, -0.20, 0.36], [0.02, -0.19, 0.37], [0.03, -0.14, 0.24], [0.0, -0.235, 0.12], [-0.01, -0.31, 0.03],
        [-0.013, -0.37, 0.015], [-0.015, -0.44, 0.01]], P["S2"])
cadeia(["collar_anchor_r", "front_leg_collar_r", "front_leg_r", "front_ankle_r", "front_foot_r", "front_toes_r", "front_toes_tip_r"],
       [[-0.14, -0.20, 0.36], [-0.20, -0.19, 0.37], [-0.20, -0.13, 0.24], [-0.215, -0.21, 0.12], [-0.245, -0.26, 0.03],
        [-0.25, -0.31, 0.015], [-0.26, -0.37, 0.01]], P["S2"])
# patas traseiras
cadeia(["hips_anchor_l", "back_leg_hip_l", "back_leg_l", "back_ankle_l", "back_foot_l", "back_toes_l", "back_toes_tip_l"],
       [[0.06, 0.08, 0.32], [0.13, 0.10, 0.30], [0.16, 0.05, 0.20], [0.15, 0.14, 0.10], [0.165, 0.10, 0.03],
        [0.167, 0.05, 0.015], [0.17, 0.0, 0.01]], P["S0"])
cadeia(["hips_anchor_r", "back_leg_hip_r", "back_leg_r", "back_ankle_r", "back_foot_r", "back_toes_r", "back_toes_tip_r"],
       [[-0.08, 0.10, 0.32], [-0.10, 0.14, 0.30], [-0.07, 0.10, 0.20], [-0.01, 0.215, 0.12], [-0.03, 0.19, 0.03],
        [-0.05, 0.15, 0.015], [-0.06, 0.11, 0.01]], P["S0"])
# cauda (curva para +X no chao)
cadeia(["tail_1", "tail_2", "tail_3", "tail_4", "tail_5", "tail_6", "tail_tip"],
       [[0.12, 0.27, 0.19], [0.27, 0.29, 0.12], [0.43, 0.26, 0.085], [0.59, 0.20, 0.07], [0.74, 0.16, 0.07],
        [0.85, 0.13, 0.09], [0.90, 0.15, 0.17]], [0.0, 0.20, 0.28])
# asas: ombro -> cotovelo -> pulso -> (40%) -> junta do dedo-guia -> meio -> ponta; 5 dedos de membrana
ASAS = {
    "l": dict(raiz=[0.06, -0.10, 0.50], cot=[0.21, -0.05, 0.58], pul=[0.40, 0.04, 0.84], noz=[0.58, -0.05, 1.06],
              pon=[0.93, 0.19, 0.91], dedos=[[0.28, 0.05, 0.34], [0.45, 0.10, 0.38], [0.66, 0.16, 0.28], [0.79, 0.20, 0.39],
                                              [0.955, 0.21, 0.61]]),
    "r": dict(raiz=[-0.17, -0.10, 0.50], cot=[-0.30, 0.05, 0.58], pul=[-0.38, 0.10, 0.82], noz=[-0.61, 0.11, 1.06],
              pon=[-0.93, 0.42, 0.91], dedos=[[-0.28, 0.14, 0.32], [-0.45, 0.22, 0.38], [-0.68, 0.32, 0.27], [-0.79, 0.40, 0.39],
                                               [-0.955, 0.43, 0.60]]),
}
for s, a in ASAS.items():
    w3 = lerp(a["pul"], a["noz"], 0.4); w5 = lerp(a["noz"], a["pon"], 0.5)
    cadeia(["shoulder_" + s, "wing_1_" + s, "wing_2_" + s, "wing_3_" + s, "wing_4_" + s, "wing_5_" + s, "wing_tip_" + s],
           [a["raiz"], a["cot"], a["pul"], w3, a["noz"], w5, a["pon"]], P["S1"])
    for i, (orig, fim) in enumerate(zip([a["raiz"], a["cot"], a["pul"], w3, a["noz"]], a["dedos"]), start=1):
        cadeia(["wing_feather_%d_0_%s" % (i, s), "wing_feather_%d_1_%s" % (i, s), "wing_feather_%d_tip_%s" % (i, s)],
               [lerp(orig, fim, 0.33), lerp(orig, fim, 0.66), fim], orig)
J, L = {}, []
for n, (h, t) in O.items():
    J[n + ".h"] = h; J[n + ".t"] = t; L.append([n + ".h", n + ".t"])
print("ossos", len(O))
json.dump({"ossos": O, "juntas": J, "ligacoes": L}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "encaixe", "encaixe.json"), "w"), indent=1)
