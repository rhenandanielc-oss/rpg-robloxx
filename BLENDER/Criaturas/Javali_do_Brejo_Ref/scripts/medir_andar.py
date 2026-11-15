"""Medicoes do Andar que o render_andar.py nao cobre, para base (JAVALI_PFX=Javali) e variante (JavaliBrejo), no MESMO clipe:
ordem/fase dos apoios (4 tempos), apoio %, onde o deslocamento e aplicado, emenda do laco, penetracoes (cabeca x corpo e
auto-intersecao do corpo, filtrando triangulos vizinhos e a costura), chao, estiramento por regiao nas poses extremas
e closes (ombro, quadril/jarrete, pescoco/presas) nessas poses.
Uso: JAVALI_PFX=JavaliBrejo blender -b <arquivo.blend> -P scripts/medir_andar.py -- <pasta_saida> [render=1]"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); RENDER = (A[1] if len(A) > 1 else "1") == "1"
PFX = os.environ.get("JAVALI_PFX", "JavaliBrejo"); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; FPS = 30
arm = bpy.data.objects[PFX + "_Rig"]; corpo = bpy.data.objects[PFX + "_Corpo"]; cab = bpy.data.objects[PFX + "_Cabeca"]
act = bpy.data.actions[PFX + "_Andar"]; arm.animation_data_create(); arm.animation_data.action = act
arm.data.pose_position = "POSE"; arm.matrix_world.identity()
F0 = int(act.frame_range[0]); NQ = int(act.frame_range[1] - act.frame_range[0]) + 1
R = {"arquivo": bpy.data.filepath, "prefixo": PFX, "acao": act.name, "quadros": NQ, "duracao_s": round(NQ / FPS, 3),
     "propriedades": {k: (act[k] if not hasattr(act[k], "to_list") else act[k].to_list()) for k in act.keys() if k not in ("apoio_json",) and not k.startswith("_")}}
# ---- apoios: fase de pouso por pata no 1o ciclo
APO = json.loads(act["apoio_json"]); T_CIC = 27                                   # 0,9 s a 30 qps (manifesto do lote A)
fases = {}
for k, s in APO.items():
    s = np.array(s); pousos = [i for i in range(1, len(s)) if s[i] and not s[i - 1]]
    fases[k] = {"pousos_q": pousos[:4], "fase_no_ciclo": round((pousos[0] % T_CIC) / T_CIC, 3) if pousos else None, "apoio_%": round(100 * s.mean(), 1)}
ordem = sorted((v["fase_no_ciclo"], k) for k, v in fases.items() if v["fase_no_ciclo"] is not None)
R["apoios"] = {"ciclo_quadros": T_CIC, "por_pata": fases, "ordem_de_pouso": [k for _, k in ordem],
               "intervalos_entre_pousos_q": [round(((ordem[(i + 1) % 4][0] - ordem[i][0]) % 1) * T_CIC, 1) for i in range(4)]}
# ---- onde esta o deslocamento: curvas de location da Raiz/Pelve na acao
loc = {}
def curvas(a):
    try: return list(a.fcurves)
    except AttributeError:
        cs = []
        for l in a.layers:
            for st in l.strips:
                for cb in st.channelbags: cs += list(cb.fcurves)
        return cs
for fc in curvas(act):
    if fc.data_path.endswith(".location") and ('"Raiz"' in fc.data_path or '"Pelve"' in fc.data_path):
        vals = [fc.evaluate(F0 + q) for q in range(NQ)]
        loc[f"{fc.data_path.split(chr(34))[1]}[{fc.array_index}]"] = [round(min(vals), 4), round(max(vals), 4)]
R["deslocamento"] = {"curvas_location_raiz_pelve_min_max_u": loc,
                     "velocidade_PROPOSTA_na_acao": act.get("velocidade_PROPOSTA"),
                     "leitura": "acao NO LUGAR: a Raiz so oscila (cm); o avanco e do controlador (no render, arm.matrix_world integra velocidade_PROPOSTA; no jogo, o movimento do modelo)"}
# ---- pose por quadro, emenda do laco
def pose(q):
    sc.frame_set(F0 + q); bpy.context.view_layer.update()
    return {pb.name: pb.matrix_basis.to_quaternion() for pb in arm.pose.bones}
def ang(a, b): return max(math.degrees(a[n].rotation_difference(b[n]).angle) for n in a)
P = [pose(q) for q in range(NQ)]
passos = [ang(P[q], P[q + 1]) for q in range(NQ - 1)]
R["emenda_laco"] = {"giro_ultimo_para_primeiro_graus": round(ang(P[-1], P[0]), 2), "giro_por_quadro_mediana": round(float(np.median(passos)), 2),
                    "giro_por_quadro_max": round(max(passos), 2), "q0_igual_ao_q_ciclo": round(ang(P[0], P[T_CIC]), 3)}
# ---- malhas avaliadas
def malha(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); mm = ev.to_mesh()
    c = np.empty(len(mm.vertices) * 3); mm.vertices.foreach_get("co", c); ev.to_mesh_clear(); return c.reshape(-1, 3)
POL = {o.name: [tuple(p.vertices) for p in o.data.polygons] for o in (corpo, cab)}
ED = {o.name: np.array([tuple(e.vertices) for e in o.data.edges]) for o in (corpo, cab)}
arm.data.pose_position = "REST"; bpy.context.view_layer.update()
REST = {o.name: malha(o) for o in (corpo, cab)}; arm.data.pose_position = "POSE"
L0 = {n: np.linalg.norm(REST[n][ED[n][:, 0]] - REST[n][ED[n][:, 1]], axis=1) for n in ED}
kd = KDTree(len(REST[corpo.name]))
for i, p in enumerate(REST[corpo.name]): kd.insert(p, i)
kd.balance(); costura_cab = set()
for j, p in enumerate(REST[cab.name]):
    if kd.find(p)[2] < 1e-5: costura_cab.add(j)
viz_corpo = set()                                   # tris do corpo a ate 2 aneis da costura (cabeca encosta por construcao)
seam_c = {kd.find(REST[cab.name][j])[1] for j in costura_cab}
anel = set(seam_c)
for _ in range(2):
    anel |= {v for p in POL[corpo.name] if anel & set(p) for v in p}
viz_corpo = {i for i, p in enumerate(POL[corpo.name]) if anel & set(p)}
anel_h = set(costura_cab)
for _ in range(2):
    anel_h |= {v for p in POL[cab.name] if anel_h & set(p) for v in p}
viz_cab = {i for i, p in enumerate(POL[cab.name]) if anel_h & set(p)}
def grupo_dom(o):
    g = np.full(len(o.data.vertices), -1); w = np.zeros(len(o.data.vertices))
    for v in o.data.vertices:
        for e in v.groups:
            if e.weight > w[v.index]: w[v.index] = e.weight; g[v.index] = e.group
    nomes = {vg.index: vg.name for vg in o.vertex_groups}; return np.array([nomes.get(i, "") for i in g])
GD = {o.name: grupo_dom(o) for o in (corpo, cab)}
REG = {"ombro": ("EscapulaE", "EscapulaD", "BracoE", "BracoD"), "quadril": ("CoxaE", "CoxaD", "Pelve"),
       "jarrete": ("PernaE", "PernaD", "CanelaTrasE", "CanelaTrasD"), "pescoco": ("Pescoco", "Pescoco2"), "cabeca_presas": ("Cabeca",)}
def estira(C):
    out = {}
    for reg, ossos in REG.items():
        rs = []
        for n in (corpo.name, cab.name):
            ed = ED[n]; m = np.isin(GD[n][ed[:, 0]], ossos) | np.isin(GD[n][ed[:, 1]], ossos)
            m &= L0[n] > 0.003
            if m.any(): rs.append(np.linalg.norm(C[n][ed[m, 0]] - C[n][ed[m, 1]], axis=1) / L0[n][m])
        if rs: r = np.concatenate(rs); out[reg] = {"max": round(float(r.max()), 2), "p99": round(float(np.percentile(r, 99)), 2), "min": round(float(r.min()), 2)}
    return out
def overlaps(C):
    bc = BVHTree.FromPolygons([V(p) for p in C[corpo.name]], POL[corpo.name]); bh = BVHTree.FromPolygons([V(p) for p in C[cab.name]], POL[cab.name])
    hc = [(i, j) for i, j in bc.overlap(bh) if i not in viz_corpo and j not in viz_cab]
    auto = [(i, j) for i, j in bc.overlap(bc) if i < j and not (set(POL[corpo.name][i]) & set(POL[corpo.name][j]))]
    return hc, auto
pen = {"cabeca_x_corpo": [], "corpo_auto": [], "chao_pele_z_min_cm": 99.0, "cabeca_z_min_cm": 99.0}
reg_auto = {}
NQ3 = min(NQ, 3 * T_CIC)
for q in range(NQ3):
    sc.frame_set(F0 + q); bpy.context.view_layer.update(); C = {o.name: malha(o) for o in (corpo, cab)}
    hc, auto = overlaps(C); pen["cabeca_x_corpo"].append(len(hc)); pen["corpo_auto"].append(len(auto))
    for i, j in auto:
        for t in (i, j):
            z = float(np.mean(C[corpo.name][list(POL[corpo.name][t]), 2])); chave = "pernas(z<0,30)" if z < 0.30 else ("dorso(z>0,62)" if z > 0.62 else "tronco")
            reg_auto[chave] = reg_auto.get(chave, 0) + 1
    pen["chao_pele_z_min_cm"] = min(pen["chao_pele_z_min_cm"], round(100 * float(min(C[corpo.name][:, 2].min(), C[cab.name][:, 2].min())), 2))
    pen["cabeca_z_min_cm"] = min(pen["cabeca_z_min_cm"], round(100 * float(C[cab.name][:, 2].min()), 2))
R["penetracoes_3_ciclos"] = {"pares_tri_cabeca_x_corpo_max_por_quadro": max(pen["cabeca_x_corpo"]), "pares_tri_cabeca_x_corpo_media": round(float(np.mean(pen["cabeca_x_corpo"])), 1),
                             "pares_tri_corpo_auto_max_por_quadro": max(pen["corpo_auto"]), "pares_tri_corpo_auto_media": round(float(np.mean(pen["corpo_auto"])), 1),
                             "tris_em_auto_intersecao_por_regiao_soma": reg_auto,
                             "pele_z_min_cm": pen["chao_pele_z_min_cm"], "cabeca_z_min_cm": pen["cabeca_z_min_cm"],
                             "nota": "pares de triangulos que se cruzam; exclui vizinhos que dividem vertice e a faixa de 2 aneis da costura cabeca/corpo"}
# ---- poses extremas (1o ciclo): dianteira E mais a frente / mais atras (frente = -Y)
yE = []
for q in range(T_CIC):
    sc.frame_set(F0 + q); bpy.context.view_layer.update()
    yE.append((arm.pose.bones["QuartelaE"].head - arm.pose.bones["Raiz"].head).y)
EXT = {"dianteiraE_a_frente": int(np.argmin(yE)), "dianteiraE_atras": int(np.argmax(yE))}
R["poses_extremas"] = {}
for nome, q in EXT.items():
    sc.frame_set(F0 + q); bpy.context.view_layer.update(); C = {o.name: malha(o) for o in (corpo, cab)}
    hc, auto = overlaps(C)
    R["poses_extremas"][nome] = {"quadro": q, "estiramento_por_regiao": estira(C), "pares_cabeca_x_corpo": len(hc), "pares_corpo_auto": len(auto)}
json.dump(R, open(os.path.join(OUT, f"medidas_extra_{PFX}.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("EXTRA", PFX, json.dumps({k: v for k, v in R.items() if k not in ("propriedades",)}, ensure_ascii=False)[:3000])
# ---- closes nas poses extremas
if RENDER:
    for o in sc.objects:
        if o.type in ("CAMERA", "LIGHT"): bpy.data.objects.remove(o)
    sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("C"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.50, 0.46, 0.44, 1); sc.world = w
    l = bpy.data.lights.new("S", "SUN"); l.energy = 3.0; lo = bpy.data.objects.new("S", l); sc.collection.objects.link(lo); lo.rotation_euler = (math.radians(50), 0, math.radians(-40))
    bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0)); ch = bpy.context.active_object
    mp = bpy.data.materials.new("Chao"); mp.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.45, 0.43, 0.40, 1); ch.data.materials.append(mp)
    cd = bpy.data.cameras.new("Q"); cam = bpy.data.objects.new("Q", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 70
    sc.render.resolution_x, sc.render.resolution_y = 520, 440
    CLOSE = {"ombro": ((1.55, -0.05, 0.30), "BracoE", "tail"), "quadril_jarrete": ((1.55, 0.05, 0.30), "PernaE", "head"),   # membro inteiro, ate o casco
             "pescoco_presas": ((0.95, -1.05, 0.55), "Cabeca", "head")}
    for nome, q in EXT.items():
        sc.frame_set(F0 + q); bpy.context.view_layer.update()
        for reg, (loc_, osso, pt) in CLOSE.items():
            alvo = getattr(arm.pose.bones[osso], pt)
            if reg == "pescoco_presas": alvo = (arm.pose.bones["Cabeca"].head + arm.pose.bones["Cabeca"].tail) * 0.5
            alvo = V((alvo.x, alvo.y, loc_[2])) if reg != "pescoco_presas" else alvo
            cam.location = alvo + V(loc_) - V((0, 0, alvo.z)) + V((0, 0, loc_[2]))
            cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = os.path.join(OUT, "extremos", f"{PFX}_{nome}_{reg}.png"); bpy.ops.render.render(write_still=True)
    print("CLOSES_OK", PFX)
