"""Esqueleto Mesh2Motion (99 ossos) encaixado no Silverwing Drake em POSE NEUTRA (Meshy T-pose, 29/10). Medidas de
medir_drake.py (fatias) em drake/Drake_lo.glb: frente -Y, esquerda do dragao = +X (_l). Asas abertas com a membrana
pendurada num plano vertical; cauda curva para +X (o repose so endireita a cauda e deita a membrana).
Gera drake/encaixe.json."""
import json, os
def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(3)]
def esp(p): return [-p[0], p[1], p[2]]                       # espelho esquerda -> direita
P = dict(S0=[0.0, 0.02, 0.30], S1=[0.0, -0.14, 0.32], S2=[0.0, -0.28, 0.33], S3=[0.0, -0.40, 0.42],
         S4=[0.0, -0.45, 0.53], S5=[0.0, -0.48, 0.635], H1=[0.0, -0.53, 0.655], MU=[0.0, -0.575, 0.625])
O = {
    "root": [[0.0, 0.0, 0.0], [0.0, 0.2, 0.0]],
    "hips": [[0.0, 0.06, 0.29], [0.0, 0.02, 0.29]],
    "spine_0": [P["S0"], P["S1"]], "spine_1": [P["S1"], P["S2"]], "spine_2": [P["S2"], P["S3"]],
    "spine_3": [P["S3"], P["S4"]], "spine_4": [P["S4"], P["S5"]], "head": [P["S5"], P["H1"]],
    "mouth_upper": [P["H1"], P["MU"]], "mouth_upper_tip": [P["MU"], [0.0, -0.605, 0.605]],
    "mouth_lower": [[0.0, -0.52, 0.635], [0.0, -0.565, 0.607]], "mouth_lower_tip": [[0.0, -0.565, 0.607], [0.0, -0.597, 0.59]],
    "stomach": [P["S1"], [0.0, -0.13, 0.24]], "stomach_tip": [[0.0, -0.13, 0.24], [0.0, -0.12, 0.19]],
}
def cadeia(nomes, pts, ini):
    a = ini
    for n, p in zip(nomes, pts): O[n] = [a, p]; a = p
def par(base, nomes_l, pts_l, ini):
    cadeia([n % "l" if "%s" in n else n for n in nomes_l], pts_l, ini)
    cadeia([n % "r" if "%s" in n else n for n in nomes_l], [esp(p) for p in pts_l], esp(ini) if ini[0] else ini)
cadeia(["horn_base_l", "horn_l", "horn_tip_L"], [[0.03, -0.46, 0.69], [0.045, -0.445, 0.73], [0.055, -0.43, 0.76]], P["S5"])
cadeia(["horn_base_r", "horn_r", "horn_tip_R"], [[-0.03, -0.46, 0.69], [-0.045, -0.445, 0.73], [-0.055, -0.43, 0.76]], P["S5"])
par(None, ["collar_anchor_%s", "front_leg_collar_%s", "front_leg_%s", "front_ankle_%s", "front_foot_%s", "front_toes_%s", "front_toes_tip_%s"],
    [[0.035, -0.30, 0.31], [0.085, -0.31, 0.31], [0.095, -0.34, 0.20], [0.093, -0.42, 0.08], [0.11, -0.47, 0.03],
     [0.12, -0.51, 0.015], [0.125, -0.55, 0.01]], P["S2"])
par(None, ["hips_anchor_%s", "back_leg_hip_%s", "back_leg_%s", "back_ankle_%s", "back_foot_%s", "back_toes_%s", "back_toes_tip_%s"],
    [[0.04, 0.03, 0.29], [0.09, 0.02, 0.28], [0.08, -0.08, 0.22], [0.085, 0.01, 0.10], [0.105, -0.02, 0.03],
     [0.11, -0.055, 0.015], [0.115, -0.09, 0.01]], P["S0"])
cadeia(["tail_1", "tail_2", "tail_3", "tail_4", "tail_5", "tail_6", "tail_tip"],
       [[0.06, 0.13, 0.225], [0.11, 0.21, 0.196], [0.18, 0.29, 0.176], [0.26, 0.36, 0.16], [0.34, 0.43, 0.15],
        [0.44, 0.50, 0.143], [0.58, 0.60, 0.147]], [0.01, 0.06, 0.26])
A = dict(raiz=[0.10, -0.30, 0.40], cot=[0.30, -0.27, 0.52], pul=[0.60, -0.245, 0.735], noz=[0.80, -0.235, 0.69],
         pon=[0.965, -0.235, 0.63], dedos=[[0.15, -0.22, 0.31], [0.25, -0.22, 0.285], [0.69, -0.22, 0.223],
                                           [0.81, -0.22, 0.34], [0.93, -0.22, 0.455]])
for s, f in (("l", lambda p: p), ("r", esp)):
    a = {k: (f(v) if k != "dedos" else [f(d) for d in v]) for k, v in A.items()}
    w3 = lerp(a["pul"], a["noz"], 0.4); w5 = lerp(a["noz"], a["pon"], 0.5)
    cadeia(["shoulder_" + s, "wing_1_" + s, "wing_2_" + s, "wing_3_" + s, "wing_4_" + s, "wing_5_" + s, "wing_tip_" + s],
           [a["raiz"], a["cot"], a["pul"], w3, a["noz"], w5, a["pon"]], P["S1"])
    for i, (orig, fim) in enumerate(zip([a["raiz"], a["cot"], a["pul"], w3, a["noz"]], a["dedos"]), start=1):
        cadeia(["wing_feather_%d_0_%s" % (i, s), "wing_feather_%d_1_%s" % (i, s), "wing_feather_%d_tip_%s" % (i, s)],
               [lerp(orig, fim, 0.33), lerp(orig, fim, 0.66), fim], orig)
J, L = {}, []
for n, (h, t) in O.items(): J[n + ".h"] = h; J[n + ".t"] = t; L.append([n + ".h", n + ".t"])
print("ossos", len(O))
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drake"); os.makedirs(d, exist_ok=True)
json.dump({"ossos": O, "juntas": J, "ligacoes": L}, open(os.path.join(d, "encaixe.json"), "w"), indent=1)
