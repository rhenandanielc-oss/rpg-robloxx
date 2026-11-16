"""Reimporta cada GLB do piloto v9 numa cena LIMPA e valida pelo ESQUELETO REIMPORTADO (nao pelo rig original):
nomes/hierarquia dos ossos (contra rig_v9.json), malhas, tris, grupos = ossos, influencias por vertice e soma dos pesos,
materiais, imagens e tamanho, escala (cernelha e z minimo), acoes presentes (nome, quadros, ossos animados) e a
DEFORMACAO: toca a acao reimportada e compara, quadro a quadro de amostra, as posicoes das malhas com a referencia
gravada do rig original por exportar_rig_v9.py (vertices casados pela posicao de repouso).
Salva a cena reimportada em <dir_glb>/reimport_<LOD>.blend (para renders com o esqueleto reimportado).
Uso: blender -b --factory-startup -P reimportar_rig_v9.py -- <dir_glb> <dir_referencia> <rig_v9.json>"""
import bpy, sys, os, json, shutil
import numpy as np
from mathutils.kdtree import KDTree
a = sys.argv[sys.argv.index("--") + 1:]; DG, REF, RJ = (os.path.abspath(x) for x in a[:3])
RIG = json.load(open(RJ)); EXP = json.load(open(os.path.join(DG, "export_rig_v9.json"))); QA = EXP["quadros_amostra"]
PAI = {o["nome"]: o["pai"] for o in RIG["ossos"]}
OUTR = {}
for L in ("LOW", "LOD1", "LOD2"):
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30
    ops = bpy.ops.import_scene.gltf.get_rna_type().properties.keys()
    kw = {"bone_heuristic": "BLENDER"} if "bone_heuristic" in ops else {}
    bpy.ops.import_scene.gltf(filepath=os.path.join(DG, EXP["lods"][L]["arquivo"]), **kw)
    arms = [o for o in sc.objects if o.type == "ARMATURE"]; A = arms[0]
    mal = [o for o in sc.objects if o.type == "MESH" and o.vertex_groups]
    ossos = {b.name: (b.parent.name if b.parent else None) for b in A.data.bones}
    r = {"armatures": len(arms), "ossos": len(ossos), "nomes_faltando": sorted(set(PAI) - set(ossos)), "nomes_extras": sorted(set(ossos) - set(PAI)),
         "hierarquia_diferente": sorted(n for n in ossos if n in PAI and ossos[n] != PAI[n]), "malhas": {}, "imagens": {}}
    for m in mal:
        me = m.data; gn = {g.index: g.name for g in m.vertex_groups}
        inf = [len([e for e in v.groups if e.weight > 1e-4]) for v in me.vertices]; soma = [sum(e.weight for e in v.groups) for v in me.vertices]
        r["malhas"][m.name] = {"tris": sum(len(p.vertices) - 2 for p in me.polygons), "vertices": len(me.vertices), "grupos": len(m.vertex_groups),
                               "grupos_nao_osso": sorted(set(gn.values()) - set(ossos)), "max_influencias": max(inf), "sem_influencia": inf.count(0),
                               "soma_pesos_min_max": [round(min(soma), 4), round(max(soma), 4)], "armature": any(md.type == "ARMATURE" and md.object == A for md in m.modifiers),
                               "materiais": [mt.name for mt in me.materials if mt],
                               "imagens": sorted({n.image.name for mt in me.materials if mt and mt.node_tree for n in mt.node_tree.nodes if n.type == "TEX_IMAGE" and n.image})}
    for im in bpy.data.images:
        if im.size[0]: r["imagens"][im.name] = list(im.size)
    pts = [m.matrix_world @ v.co for m in mal for v in m.data.vertices]
    cz = [p.z for m in mal if "Corpo" in m.name for p in [m.matrix_world @ v.co for v in m.data.vertices] if -3.6 < p.y < -2.6 and abs(p.x) < 0.3]
    r["escala"] = {"z_min": round(min(p.z for p in pts), 3), "cernelha_z": round(max(cz), 3) if cz else None, "malhas_importadas": [m.name for m in mal],
                   "comprimento_y": [round(min(p.y for p in pts), 3), round(max(p.y for p in pts), 3)]}
    acs = list(bpy.data.actions); r["acoes"] = {}
    for ac in acs:
        nomes = set()
        try:
            for lay in ac.layers:
                for st in lay.strips:
                    for cb in st.channelbags:
                        for fc in cb.fcurves:
                            if fc.data_path.startswith('pose.bones["'): nomes.add(fc.data_path.split('"')[1])
        except AttributeError:
            for fc in ac.fcurves:
                if fc.data_path.startswith('pose.bones["'): nomes.add(fc.data_path.split('"')[1])
        r["acoes"][ac.name] = {"quadros": [round(ac.frame_range[0], 2), round(ac.frame_range[1], 2)], "ossos_animados": len(nomes)}
    ac = next((x for x in acs if "Teste_Piloto" in x.name), None)
    if ac:
        A.animation_data_create(); A.animation_data.action = ac
        if A.animation_data.action_slot is None and len(ac.slots): A.animation_data.action_slot = ac.slots[0]
    ref = np.load(os.path.join(REF, "ref_%s.npz" % L)); casam = {}
    for m in mal:
        if m.name not in ref.files: continue
        R0 = ref[m.name][0]; kd = KDTree(len(R0))
        for i, p in enumerate(R0): kd.insert(p.tolist(), i)
        kd.balance(); cand, dmax, fora = [], 0.0, 0                     # vertices coincidentes: todos os candidatos (o GLB divide por UV)
        for v in m.data.vertices:
            p = m.matrix_world @ v.co; c = [j for _, j, _ in kd.find_range(p, 1e-4)]
            if not c: fora += 1; c = [-1]                                   # vertice extra (triangulo-guarda de osso sem peso)
            else: dmax = max(dmax, kd.find(p)[2])
            cand.append(c)
        casam[m.name] = (cand, dmax, fora)
    def desvio(q):
        sc.frame_set(q); dg = bpy.context.evaluated_depsgraph_get(); out = {}
        for m in mal:
            if m.name not in casam: continue
            e = m.evaluated_get(dg); me = e.to_mesh(); P = np.array([(m.matrix_world @ v.co)[:] for v in me.vertices]); e.to_mesh_clear()
            k = QA.index(q) + 1; Rk = ref[m.name][k]
            out[m.name] = max((min(float(np.abs(P[i] - Rk[j]).max()) for j in c) for i, c in enumerate(casam[m.name][0]) if c[0] >= 0), default=0.0)
        return out
    dv = {q: desvio(q) for q in QA} if ac else {}
    r["deformacao_vs_rig_original"] = {"casamento_repouso_dist_max": {n: round(d, 6) for n, (_, d, _) in casam.items()},
                                        "vertices_extras_sem_par": {n: f for n, (_, _, f) in casam.items()},
                                        "desvio_max_por_malha": {n: round(max(d[n] for d in dv.values()), 5) for n in casam} if dv else None,
                                        "quadro_pior": max(dv, key=lambda q: max(dv[q].values())) if dv else None, "quadros_comparados": len(dv)}
    if A.name != "LoboArtico_Rig": A.name = "LoboArtico_Rig"
    shutil.copy(os.path.join(os.path.dirname(RJ), "rig_pivos.json"), os.path.join(DG, "rig_pivos.json"))
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DG, "reimport_%s.blend" % L))
    OUTR[L] = r; print("REIMPORT", L, json.dumps(r), flush=True)
json.dump(OUTR, open(os.path.join(DG, "reimport_rig_v9.json"), "w"), indent=1); print("REIMPORT_RIG_OK", flush=True)
