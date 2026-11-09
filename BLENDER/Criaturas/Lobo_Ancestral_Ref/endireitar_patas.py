"""Endireita (vista frontal) a malha das 4 patas e do volume do ombro/peitoral do Lobo Ancestral em repouso: a linha
central de cada pata (osso dominante da cadeia; centro robusto por altura) e levada ate a linha dos OSSOS daquela pata
(simetrica, +-1,3), com um campo de deslocamento LATERAL suave por altura e mascara macia (transicao para o corpo).
O peitoral entre/acima das patas e recentrado em x = 0 do mesmo jeito. Sem projecao/bake: UV, textura, topologia, pesos,
esqueleto e apoios intactos. Entrada preservada. Uso: blender -b rig3/Lobo_Ancestral_Rig.blend -P endireitar_patas.py -- <saida_dir>"""
import bpy, sys, os, json
import numpy as np
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
gi = {g.index: g.name for g in LO.vertex_groups}
dono = [gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else "" for v in me.vertices]
viz = [[] for _ in range(n)]
for e in me.edges: a, b = e.vertices; viz[a].append(b); viz[b].append(a)
def macia(ind, it):
    m = ind.astype(float)
    for _ in range(it): m = np.array([0.5 * m[i] + 0.5 * (m[viz[i]].mean() if viz[i] else m[i]) for i in range(n)])
    return m
y_omb = BD["BracoE"].head_local.y
CAD = {"dianE": (["EscapulaE", "BracoE", "AntebracoE", "MaoE", "DedosE"], ["DedosE", "MaoE", "AntebracoE", "BracoE", "EscapulaE"]),
       "dianD": (["EscapulaD", "BracoD", "AntebracoD", "MaoD", "DedosD"], ["DedosD", "MaoD", "AntebracoD", "BracoD", "EscapulaD"]),
       "trasE": (["CoxaE", "CanelaE", "MetatarsoE", "PeE"], ["PeE", "MetatarsoE", "CanelaE", "CoxaE"]),
       "trasD": (["CoxaD", "CanelaD", "MetatarsoD", "PeD"], ["PeD", "MetatarsoD", "CanelaD", "CoxaD"])}
dx_total = np.zeros(n); rel = {}
zs = np.arange(0.2, 6.2, 0.2)
def centro_curva(sel):
    pts = []
    for z0 in zs:
        s = sel & (np.abs(co[:, 2] - z0) < 0.15)
        if s.sum() >= 10:
            p15, p85 = np.percentile(co[s, 0], [15, 85]); pts.append((z0, (p15 + p85) / 2))
    pts = np.array(pts)
    c = np.interp(zs, pts[:, 0], pts[:, 1])
    return np.convolve(np.pad(c, 3, mode="edge"), np.ones(7) / 7, mode="valid"), pts
for nome, (grupos, juntas) in CAD.items():
    sel = np.array([d in grupos for d in dono])
    c, pts = centro_curva(sel)
    jz = [(BD[j].head_local.z, BD[j].head_local.x) for j in juntas]
    jz.sort(); alvo = np.interp(zs, [a for a, b in jz], [b for a, b in jz])
    corr = alvo - c
    m = np.clip(macia(sel, 5) * 1.4, 0, 1)
    if nome.startswith("dian"): m *= np.clip((y_omb + 1.6 - co[:, 1]) / 0.8, 0, 1)        # nao alcanca o flanco
    else: m *= np.clip((co[:, 1] - (BD["CoxaE"].head_local.y - 1.8)) / 0.8, 0, 1)
    dx = np.interp(co[:, 2], zs, corr) * m
    dx_total += dx
    rel[nome] = {"centro_antes": [[round(float(a), 2), round(float(b), 3)] for a, b in pts], "correcao_max": round(float(np.abs(corr).max()), 3)}
    print(nome, "correcao por altura", " ".join("z%.1f:%+.2f" % (z, k) for z, k in zip(zs[::2], corr[::2])))
co[:, 0] += dx_total
# peitoral entre/acima das patas (frente dos ombros): recentra em x = 0
selp = np.array([d in ("Peito", "Coluna2", "JubaPeito", "Pescoco1") for d in dono]) & (co[:, 1] < y_omb + 0.8) & (co[:, 2] < 5.6)
cp, ptsp = centro_curva(selp)
mp = np.clip(macia(selp, 5) * 1.4, 0, 1) * np.clip((y_omb + 1.2 - co[:, 1]) / 0.8, 0, 1) * np.clip((5.9 - co[:, 2]) / 0.6, 0, 1)
dxp = -np.interp(co[:, 2], zs, cp) * mp
co[:, 0] += dxp
print("peitoral correcao", " ".join("z%.1f:%+.2f" % (z, -k) for z, k in zip(zs[::2], cp[::2]) if 2.6 < z < 5.8))
me.vertices.foreach_set("co", co.ravel()); me.update()
print("MOVIDOS", int((np.abs(dx_total + dxp) > 0.005).sum()), "max %.3f" % np.abs(dx_total + dxp).max())
# conferencia: patas no chao intactas
z0 = co[:, 2] < 0.3; print("PES z<0,3: deslocamento max %.4f" % np.abs((dx_total + dxp)[z0]).max())
json.dump(rel, open(os.path.join(OUT, "endireitar_patas.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend"))
print("ENDIREITAR_PATAS_OK")
