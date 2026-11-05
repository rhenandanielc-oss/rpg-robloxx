"""E4b: juntas do esqueleto de teste, lidas no perfil da malha densa (E3_t2) e refinadas: cada junta e dada em (y, z)
pelo contorno da pata (punho no entalhe do coxim, jarrete na saliencia do calcanhar, joelho na frente da coxa...);
o x e o centro da fatia da pata naquele (y, z). Grava juntas.json e um grafico de conferencia.
Uso: python e4b_01_juntas.py <pontos_high.npy> <saida.json> <grafico.png>"""
import sys, json
import numpy as np
co = np.load(sys.argv[1])
# (y, z) lidos nos perfis (review/e4b/_pernas_pontos.png); lado: +1 = X+, -1 = X-
YZ = {
 "DD": {"ombro": (-9.3, 8.2), "cotovelo": (-7.7, 5.2), "punho": (-8.2, 1.9), "pata": (-9.3, 0.6), "dedos": (-10.4, 0.4)},
 "DE": {"ombro": (-9.3, 8.2), "cotovelo": (-7.7, 5.2), "punho": (-8.1, 1.9), "pata": (-9.3, 0.6), "dedos": (-10.3, 0.4)},
 "TD": {"quadril": (6.2, 8.8), "joelho": (3.9, 6.0), "jarrete": (5.4, 3.6), "pata": (4.0, 0.7), "dedos": (2.7, 0.4)},
 "TE": {"quadril": (6.2, 8.8), "joelho": (7.0, 6.2), "jarrete": (9.2, 3.7), "pata": (8.3, 0.7), "dedos": (7.0, 0.4)},
}
def x_fatia(lado, y, z, r=0.35):
    sel = (co[:, 0] * lado > 0.25) & (np.abs(co[:, 1] - y) < r) & (np.abs(co[:, 2] - z) < r) & (np.abs(co[:, 0]) < 3.6)
    if sel.sum() < 6: return None
    xs = co[sel, 0]; return float((xs.min() + xs.max()) / 2)
J = {}
for perna, d in YZ.items():
    lado = 1 if perna.endswith("D") else -1; J[perna] = {}
    for n, (y, z) in d.items():
        x = x_fatia(lado, y, z)
        if x is None or n in ("ombro", "quadril"): x = lado * (1.35 if n == "ombro" else 1.25) if x is None else x
        if n in ("ombro", "quadril"): x = lado * min(abs(x), 1.5)       # dentro do corpo, nao na juba/coxa externa
        J[perna][n] = [round(x, 3), y, z]
def meio(y, z, r=0.4):
    sel = (np.abs(co[:, 1] - y) < r) & (np.abs(co[:, 2] - z) < 1.5) & (np.abs(co[:, 0]) < 1.5)
    return round(float(np.median(co[sel, 0])) if sel.sum() > 5 else 0.0, 3)
COL = [(6.6, 9.4), (3.0, 9.7), (-1.0, 9.9), (-5.0, 10.0), (-7.6, 10.4)]
J["coluna"] = [[0.0, y, z] for y, z in COL]
J["pescoco"] = [[0.0, -7.6, 10.4], [0.0, -10.3, 12.4], [-0.1, -12.0, 13.3]]
J["cabeca_fim"] = [-0.2, -14.9, 13.8]
J["mandibula"] = {"pivo": [0.0, -12.75, 12.353], "queixo": [0.0, -15.15, 11.95]}
# cauda: pontos sobre a propria cauda (fatias da malha densa ao longo da curva lida no perfil)
CAUDA_YZ = [(6.9, 9.3), (8.4, 7.7), (10.2, 5.7), (12.2, 4.7), (14.2, 4.3), (15.9, 4.1), (17.6, 3.0)]
cauda = []
for y, z in CAUDA_YZ:
    sel = (np.abs(co[:, 1] - y) < 0.3) & (np.abs(co[:, 2] - z) < 0.9) & (np.abs(co[:, 0]) < 3.0)
    x = float((co[sel, 0].min() + co[sel, 0].max()) / 2) if sel.sum() > 5 else 0.0
    cauda.append([round(x if y > 8 else 0.0, 3), y, z])
J["cauda"] = cauda
json.dump(J, open(sys.argv[2], "w"), indent=1); print(json.dumps(J))
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 3, figsize=(30, 11))
for a, (nome, sel) in zip(ax, (("X+", co[:, 0] > 0.2), ("X-", co[:, 0] < -0.2), ("meio", np.abs(co[:, 0]) < 0.8))):
    p = co[sel]; a.scatter(p[:, 1], p[:, 2], s=0.2, c="0.6")
    for perna, d in J.items():
        if perna in ("DD", "DE", "TD", "TE") and ((nome == "X+") == perna.endswith("D")) and nome != "meio":
            pts = np.array(list(d.values())); a.plot(pts[:, 1], pts[:, 2], "r-o")
    if nome == "meio":
        for k in ("coluna", "pescoco", "cauda"):
            pts = np.array(J[k]); a.plot(pts[:, 1], pts[:, 2], "b-o")
    a.set_aspect("equal"); a.invert_xaxis(); a.grid(alpha=.3); a.set_title(nome)
plt.tight_layout(); plt.savefig(sys.argv[3], dpi=45)
