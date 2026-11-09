"""Linha central (vista frontal) de cada pata dianteira/traseira e do peitoral baixo, por altura, na malha em repouso
(ou num quadro de acao). Pata = vertices cujo osso dominante e da cadeia daquela pata; peitoral = Peito/Coluna2/JubaPeito
a frente dos ombros. Centro robusto = media dos percentis 15/85. So leitura.
Uso: blender -b <rig.blend> -P medir_patas_frontal.py -- <saida.json>"""
import bpy, sys, json
import numpy as np
OUT = sys.argv[sys.argv.index("--") + 1]
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]
gi = {g.index: g.name for g in LO.vertex_groups}
co = np.array([v.co[:] for v in LO.data.vertices]); dono = [gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else "" for v in LO.data.vertices]
y_omb = arm.data.bones["BracoE"].head_local.y
CAD = {"dianE": {"EscapulaE", "BracoE", "AntebracoE", "MaoE", "DedosE"}, "dianD": {"EscapulaD", "BracoD", "AntebracoD", "MaoD", "DedosD"},
       "trasE": {"CoxaE", "CanelaE", "MetatarsoE", "PeE"}, "trasD": {"CoxaD", "CanelaD", "MetatarsoD", "PeD"},
       "peito": {"Peito", "Coluna2", "JubaPeito"}}
r = {}
for nome, gr in CAD.items():
    sel = np.array([d in gr for d in dono])
    if nome == "peito": sel &= (co[:, 1] < y_omb + 0.8)
    linhas = []
    for z0 in np.arange(0.3, 6.0, 0.3):
        s = sel & (np.abs(co[:, 2] - z0) < 0.15)
        if s.sum() >= 12:
            p15, p85 = np.percentile(co[s, 0], [15, 85])
            linhas.append([round(float(z0), 2), round(float((p15 + p85) / 2), 3), round(float(co[s, 0].min()), 3), round(float(co[s, 0].max()), 3), int(s.sum())])
    r[nome] = linhas
ossos = {b: [round(c, 3) for c in arm.data.bones[b].head_local] for b in ("BracoE", "BracoD", "AntebracoE", "AntebracoD", "MaoE", "MaoD", "DedosE", "DedosD", "CoxaE", "CoxaD", "MetatarsoE", "MetatarsoD")}
r["ossos"] = ossos
json.dump(r, open(OUT, "w"), indent=1)
for nome in ("dianE", "dianD", "peito", "trasE", "trasD"):
    print(nome, " ".join("z%.1f:%+.2f" % (z, c) for z, c, a, b, n in r[nome]))
print("OSSOS", ossos)
