"""Medicoes por clipe (todos os quadros) para base (JAVALI_PFX=Javali) e variante (JavaliBrejo); a comparacao fica em comparar_clipes.py.
Por clipe: pose de cada osso por quadro (para provar que a curva nao mudou), pele/cabeca minimas, pares de triangulos
cabeca x corpo e auto-intersecao do corpo (sem vizinhos e sem a faixa da costura), estiramento maximo por regiao.
Uso: JAVALI_PFX=JavaliBrejo blender -b <arquivo.blend> -P scripts/medir_clipes.py -- <pasta_saida> <Clipe1,Clipe2,...>"""
import bpy, sys, os, json
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); LISTA = A[1].split(",")
PFX = os.environ.get("JAVALI_PFX", "JavaliBrejo"); os.makedirs(OUT, exist_ok=True); sc = bpy.context.scene
arm = bpy.data.objects[PFX + "_Rig"]; corpo = bpy.data.objects[PFX + "_Corpo"]; cab = bpy.data.objects[PFX + "_Cabeca"]
arm.animation_data_create(); arm.matrix_world.identity()
def malha(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); mm = ev.to_mesh()
    c = np.empty(len(mm.vertices) * 3); mm.vertices.foreach_get("co", c); ev.to_mesh_clear(); return c.reshape(-1, 3)
POL = {o.name: [tuple(p.vertices) for p in o.data.polygons] for o in (corpo, cab)}
ED = {o.name: np.array([tuple(e.vertices) for e in o.data.edges]) for o in (corpo, cab)}
arm.animation_data.action = None; arm.data.pose_position = "REST"; bpy.context.view_layer.update()
REST = {o.name: malha(o) for o in (corpo, cab)}; arm.data.pose_position = "POSE"
L0 = {n: np.linalg.norm(REST[n][ED[n][:, 0]] - REST[n][ED[n][:, 1]], axis=1) for n in ED}
kd = KDTree(len(REST[corpo.name]))
for i, p in enumerate(REST[corpo.name]): kd.insert(p, i)
kd.balance(); cost_h = {j for j, p in enumerate(REST[cab.name]) if kd.find(p)[2] < 1e-5}
cost_c = {kd.find(REST[cab.name][j])[1] for j in cost_h}
def anel(pol, ini):
    s = set(ini)
    for _ in range(2): s |= {v for p in pol if s & set(p) for v in p}
    return {i for i, p in enumerate(pol) if s & set(p)}
viz_c, viz_h = anel(POL[corpo.name], cost_c), anel(POL[cab.name], cost_h)
def grupo_dom(o):
    nomes = {vg.index: vg.name for vg in o.vertex_groups}; g = []
    for v in o.data.vertices:
        e = max(v.groups, key=lambda e: e.weight, default=None); g.append(nomes.get(e.group, "") if e else "")
    return np.array(g)
GD = {o.name: grupo_dom(o) for o in (corpo, cab)}
REG = {"ombro": ("EscapulaE", "EscapulaD", "BracoE", "BracoD"), "quadril": ("CoxaE", "CoxaD", "Pelve"),
       "jarrete": ("PernaE", "PernaD", "CanelaTrasE", "CanelaTrasD"), "pescoco": ("Pescoco", "Pescoco2"), "cabeca_presas": ("Cabeca",)}
MASK = {}
for reg, ossos in REG.items():
    for n in ED:
        ed = ED[n]; MASK[(reg, n)] = (np.isin(GD[n][ed[:, 0]], ossos) | np.isin(GD[n][ed[:, 1]], ossos)) & (L0[n] > 0.003)
R = {"arquivo": bpy.data.filepath, "prefixo": PFX, "clipes": {}}
OSSOS = [pb.name for pb in arm.pose.bones]
for nome in LISTA:
    act = bpy.data.actions[PFX + "_" + nome]; arm.animation_data.action = act
    if arm.animation_data.action_slot is None and len(act.slots): arm.animation_data.action_slot = act.slots[0]
    F0 = int(act.frame_range[0]); NQ = int(act.frame_range[1] - act.frame_range[0]) + 1
    m = {"quadros": NQ, "pele_z_min_cm": 99.0, "cabeca_z_min_cm": 99.0, "cabeca_x_corpo_max": 0, "corpo_auto_soma": 0, "corpo_auto_max": 0,
         "estira_max": {r: 0.0 for r in REG}, "pose": []}
    for q in range(NQ):
        sc.frame_set(F0 + q); bpy.context.view_layer.update()
        m["pose"].append([round(c, 5) for b in OSSOS for c in arm.pose.bones[b].matrix_basis.to_quaternion()])
        C = {o.name: malha(o) for o in (corpo, cab)}
        m["pele_z_min_cm"] = min(m["pele_z_min_cm"], round(100 * float(min(C[corpo.name][:, 2].min(), C[cab.name][:, 2].min())), 2))
        m["cabeca_z_min_cm"] = min(m["cabeca_z_min_cm"], round(100 * float(C[cab.name][:, 2].min()), 2))
        bc = BVHTree.FromPolygons([V(p) for p in C[corpo.name]], POL[corpo.name]); bh = BVHTree.FromPolygons([V(p) for p in C[cab.name]], POL[cab.name])
        hc = sum(1 for i, j in bc.overlap(bh) if i not in viz_c and j not in viz_h)
        au = sum(1 for i, j in bc.overlap(bc) if i < j and not (set(POL[corpo.name][i]) & set(POL[corpo.name][j])))
        m["cabeca_x_corpo_max"] = max(m["cabeca_x_corpo_max"], hc); m["corpo_auto_soma"] += au; m["corpo_auto_max"] = max(m["corpo_auto_max"], au)
        for reg in REG:
            for n in ED:
                mk = MASK[(reg, n)]
                if mk.any():
                    r = np.linalg.norm(C[n][ED[n][mk, 0]] - C[n][ED[n][mk, 1]], axis=1) / L0[n][mk]
                    m["estira_max"][reg] = max(m["estira_max"][reg], round(float(r.max()), 2))
    m["corpo_auto_media"] = round(m.pop("corpo_auto_soma") / NQ, 1)
    R["clipes"][nome] = m; print("CLIPE", PFX, nome, {k: v for k, v in m.items() if k != "pose"})
json.dump(R, open(os.path.join(OUT, f"medidas_clipes_{PFX}.json"), "w", encoding="utf-8"))
print("FIM", PFX)
