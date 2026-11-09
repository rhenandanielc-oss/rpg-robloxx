"""Mede, trecho a trecho (a cada 0,1 de altura), quanto a perna dianteira foge de uma coluna reta: centro (x, y) e raio
em 16 direcoes em volta do eixo, por altura; desvio do centro em relacao a reta e "calombos" do raio (diferenca para a
reta ajustada em cada direcao). So leitura. Uso: blender -b <rig.blend> -P medir_coluna.py -- <saida.json>"""
import bpy, sys, json, math
import numpy as np
OUT = sys.argv[sys.argv.index("--") + 1]
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; me = LO.data
gi = {g.index: g.name for g in LO.vertex_groups}
co = np.array([v.co[:] for v in me.vertices])
cad = {"AntebracoE", "MaoE"}
w = np.array([sum(g.weight for g in v.groups if gi[g.group] in cad) for v in me.vertices])
pelo = np.array([sum(g.weight for g in v.groups if gi[g.group].startswith("Pelo")) for v in me.vertices])
sel = (w > 0.5) & (pelo < 0.3) & (co[:, 0] > 0.3) & (co[:, 1] < -2.6) & (co[:, 2] > 0.55) & (co[:, 2] < 3.0)
P = co[sel]
zs = np.arange(0.6, 2.96, 0.1)
cen = []
for z0 in zs:
    s = np.abs(P[:, 2] - z0) < 0.08
    q = P[s] if s.sum() >= 4 else P[np.argsort(np.abs(P[:, 2] - z0))[:6]]
    cen.append(((q[:, 0].min() + q[:, 0].max()) / 2, (q[:, 1].min() + q[:, 1].max()) / 2))
cen = np.array(cen)
fx = np.polyfit(zs, cen[:, 0], 1); fy = np.polyfit(zs, cen[:, 1], 1)
dc = np.hypot(cen[:, 0] - np.polyval(fx, zs), cen[:, 1] - np.polyval(fy, zs))
# raio por direcao em volta do eixo reto
ax = np.polyval(fx, P[:, 2]); ay = np.polyval(fy, P[:, 2])
ang = np.arctan2(P[:, 1] - ay, P[:, 0] - ax); r = np.hypot(P[:, 0] - ax, P[:, 1] - ay)
NS = 16; setor = ((ang + math.pi) / (2 * math.pi) * NS).astype(int) % NS
calombo = []
for k in range(NS):
    s = setor == k
    if s.sum() < 5: continue
    c = np.polyfit(P[s, 2], r[s], 1); calombo.append(np.abs(r[s] - np.polyval(c, P[s, 2])))
cal = np.concatenate(calombo)
res = {"vertices": int(sel.sum()), "centro_desvio_max": round(float(dc.max()), 4), "centro_desvio_medio": round(float(dc.mean()), 4),
       "inclinacao_x_graus": round(math.degrees(math.atan(fx[0])), 2), "inclinacao_y_graus": round(math.degrees(math.atan(fy[0])), 2),
       "calombo_raio_p90": round(float(np.percentile(cal, 90)), 4), "calombo_raio_max": round(float(cal.max()), 4),
       "por_altura": [[round(float(z), 1), round(float(d), 3)] for z, d in zip(zs, dc)]}
print("COLUNA", json.dumps({k: v for k, v in res.items() if k != "por_altura"}))
print("DESVIO_CENTRO_POR_ALTURA", " ".join("z%.1f:%.3f" % (z, d) for z, d in res["por_altura"]))
json.dump(res, open(OUT, "w"), indent=1)
