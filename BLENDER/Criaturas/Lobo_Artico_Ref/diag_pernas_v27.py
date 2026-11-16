"""v27 (diagnostico): pernas que entram para DENTRO na virada. Por quadro, no referencial do corpo (armature, clipe no lugar):
- x lateral do MCP (ponta do metacarpo/metatarso) de cada pata e desvio para DENTRO em relacao ao repouso (+ = mais perto do meio);
- distancia minima entre as partes baixas das pernas do mesmo par (DE x DD, TE x TD: vertices dominados por antebraco/tibia,
  metacarpo/metatarso e dedos) e entre a parte baixa de uma perna e a parte de cima da outra;
- vertices da perna que passam do plano do meio (x = 0).
Uso: blender -b <anim.blend> -P diag_pernas_v27.py -- <saida_json> [acoes] [LOD]"""
import bpy, sys, os, json, math
from mathutils import Vector as V
from mathutils.kdtree import KDTree
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); ACS = a[1].split(",") if len(a) > 1 else ["Andar", "VirarEsquerda", "VirarDireita"]; L = a[2] if len(a) > 2 else "LOW"
ARM = bpy.data.objects["LoboArtico_Rig"]; P = ARM.pose.bones; sc = bpy.context.scene
PATAS = {"DE": ("Umero_E", "Antebraco_E", "Metacarpo_E", "Dedos_E"), "DD": ("Umero_D", "Antebraco_D", "Metacarpo_D", "Dedos_D"),
         "TE": ("Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E"), "TD": ("Coxa_D", "Tibia_D", "Metatarso_D", "DedosPe_D")}
C = bpy.data.objects[L + "_Corpo"]; me = C.data; gn = {g.index: g.name for g in C.vertex_groups}
dom = {}
for v in me.vertices:
    if v.groups: dom[v.index] = max(((gn[g.group], g.weight) for g in v.groups), key=lambda t: t[1])
BAIXO = {k: [i for i, (n, w) in dom.items() if n in c[1:] and w > 0.5] for k, c in PATAS.items()}
CIMA = {k: [i for i, (n, w) in dom.items() if n == c[0] and w > 0.5] for k, c in PATAS.items()}
PAR = (("DE", "DD"), ("TE", "TD"))
def usar(n):
    ac = bpy.data.actions[n]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    return int(ac.frame_range[0]), int(ac.frame_range[1])
def posado(q):
    sc.frame_set(q); dg = bpy.context.evaluated_depsgraph_get(); e = C.evaluated_get(dg); m = e.to_mesh(); r = [v.co.copy() for v in m.vertices]; e.to_mesh_clear(); return r
def medir(Pq):
    r = {"mcp_x": {k: round(P[c[2]].tail.x, 4) for k, c in PATAS.items()}}
    for e_, d_ in PAR:
        kd = KDTree(len(BAIXO[d_])); [kd.insert(Pq[i], j) for j, i in enumerate(BAIXO[d_])]; kd.balance()
        r["dist_baixo_" + e_ + d_] = round(min(kd.find(Pq[i])[2] for i in BAIXO[e_]), 4)
        for x_, y_ in ((e_, d_), (d_, e_)):
            kc = KDTree(len(CIMA[y_])); [kc.insert(Pq[i], j) for j, i in enumerate(CIMA[y_])]; kc.balance()
            r["dist_baixo%s_cima%s" % (x_, y_)] = round(min(kc.find(Pq[i])[2] for i in BAIXO[x_]), 4)
    r["meio"] = {k: sum(1 for i in BAIXO[k] + CIMA[k] if (Pq[i].x < 0) == (k[1] == "E")) for k in PATAS}
    r["x_mais_dentro"] = {k: round(min(Pq[i].x for i in BAIXO[k]) if k[1] == "E" else max(Pq[i].x for i in BAIXO[k]), 4) for k in PATAS}
    return r
usar("Repouso"); R0 = medir(posado(0)); R = {"lod": L, "repouso": R0, "acoes": {}}
for n in ACS:
    f0, f1 = usar(n); fr = [medir(posado(q)) for q in range(f0, f1 + 1)]
    res = {"quadros": len(fr), "por_quadro": fr}
    for k in PATAS:
        sg = 1 if k[1] == "E" else -1; dent = [sg * (R0["mcp_x"][k] - f["mcp_x"][k]) for f in fr]
        res["mcp_dentro_max_" + k] = round(max(dent), 4); res["mcp_dentro_q_" + k] = dent.index(max(dent))
        res["x_mais_dentro_" + k] = (min if sg > 0 else max)(f["x_mais_dentro"][k] for f in fr)
        res["meio_max_" + k] = max(f["meio"][k] for f in fr)
    for ch in [c for c in fr[0] if c.startswith("dist")]:
        vals = [f[ch] for f in fr]; res[ch + "_min"] = min(vals); res[ch + "_q"] = vals.index(min(vals))
    R["acoes"][n] = res
    print("PERNAS", n, json.dumps({c: v for c, v in res.items() if c != "por_quadro"}), flush=True)
print("REPOUSO", json.dumps(R0), flush=True)
json.dump(R, open(OUT, "w"), indent=1); print("DIAG_PERNAS_OK", flush=True)
