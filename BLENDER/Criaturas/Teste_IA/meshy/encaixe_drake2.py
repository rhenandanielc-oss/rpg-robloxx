"""Esqueleto Mesh2Motion (99 ossos) no Silverwing Drake v2 (Meshy 29/10 19:41): asas DEITADAS (plano ~3 graus), cauda
reta, 4 patas no chao. Medidas de fatias.py / medir em drake2/Drake2_lo.glb (frente -Y, esquerda = +X = _l).
Torso y[-0.65,-0.22]; pes dianteiros y-0.60, traseiros y-0.28; asa: bordo de ataque y~-0.55 z~0.40, pulso x0.555.
Gera drake2/encaixe.json."""
import json, os
def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(3)]
def esp(p): return [-p[0], p[1], p[2]]
P = dict(S0=[0.0, -0.26, 0.30], S1=[0.0, -0.40, 0.31], S2=[0.0, -0.54, 0.33], S3=[0.0, -0.595, 0.43],
         S4=[0.0, -0.62, 0.53], S5=[0.0, -0.625, 0.615], H1=[0.0, -0.66, 0.615], MU=[0.0, -0.71, 0.59])
O = {
    "root": [[0.0, -0.40, 0.0], [0.0, -0.20, 0.0]],
    "hips": [[0.0, -0.22, 0.30], [0.0, -0.26, 0.30]],
    "spine_0": [P["S0"], P["S1"]], "spine_1": [P["S1"], P["S2"]], "spine_2": [P["S2"], P["S3"]],
    "spine_3": [P["S3"], P["S4"]], "spine_4": [P["S4"], P["S5"]], "head": [P["S5"], P["H1"]],
    "mouth_upper": [P["H1"], P["MU"]], "mouth_upper_tip": [P["MU"], [0.0, -0.745, 0.575]],
    "mouth_lower": [[0.0, -0.65, 0.585], [0.0, -0.70, 0.565]], "mouth_lower_tip": [[0.0, -0.70, 0.565], [0.0, -0.735, 0.555]],
    "stomach": [P["S1"], [0.0, -0.40, 0.23]], "stomach_tip": [[0.0, -0.40, 0.23], [0.0, -0.40, 0.205]],
}
def cadeia(nomes, pts, ini):
    a = ini
    for n, p in zip(nomes, pts): O[n] = [a, p]; a = p
def par(nomes, pts, ini):
    cadeia([n % "l" for n in nomes], pts, ini)
    cadeia([n % "r" for n in nomes], [esp(p) for p in pts], ini)
cadeia(["horn_base_l", "horn_l", "horn_tip_L"], [[0.03, -0.60, 0.65], [0.045, -0.565, 0.675], [0.057, -0.53, 0.70]], P["S5"])
cadeia(["horn_base_r", "horn_r", "horn_tip_R"], [[-0.03, -0.60, 0.65], [-0.045, -0.565, 0.675], [-0.057, -0.53, 0.70]], P["S5"])
par(["collar_anchor_%s", "front_leg_collar_%s", "front_leg_%s", "front_ankle_%s", "front_foot_%s", "front_toes_%s", "front_toes_tip_%s"],
    [[0.03, -0.53, 0.32], [0.075, -0.52, 0.31], [0.077, -0.50, 0.20], [0.072, -0.55, 0.09], [0.08, -0.585, 0.025],
     [0.083, -0.62, 0.012], [0.085, -0.65, 0.008]], P["S2"])
par(["hips_anchor_%s", "back_leg_hip_%s", "back_leg_%s", "back_ankle_%s", "back_foot_%s", "back_toes_%s", "back_toes_tip_%s"],
    [[0.03, -0.25, 0.30], [0.065, -0.25, 0.29], [0.06, -0.30, 0.19], [0.066, -0.235, 0.09], [0.08, -0.265, 0.025],
     [0.083, -0.295, 0.012], [0.085, -0.325, 0.008]], P["S0"])
cadeia(["tail_1", "tail_2", "tail_3", "tail_4", "tail_5", "tail_6", "tail_tip"],
       [[0.0, -0.08, 0.296], [0.0, 0.06, 0.29], [0.0, 0.20, 0.284], [0.0, 0.34, 0.27], [0.0, 0.48, 0.261],
        [0.0, 0.62, 0.258], [0.0, 0.75, 0.255]], [0.0, -0.20, 0.30])
A = dict(raiz=[0.11, -0.50, 0.37], cot=[0.33, -0.49, 0.40], pul=[0.555, -0.575, 0.41], noz=[0.75, -0.52, 0.405],
         pon=[0.945, -0.45, 0.40], dedos=[[0.14, -0.26, 0.37], [0.31, -0.19, 0.40], [0.545, -0.12, 0.43],
                                          [0.755, -0.12, 0.43], [0.92, -0.28, 0.42]])
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
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drake2"); os.makedirs(d, exist_ok=True)
json.dump({"ossos": O, "juntas": J, "ligacoes": L}, open(os.path.join(d, "encaixe.json"), "w"), indent=1)
