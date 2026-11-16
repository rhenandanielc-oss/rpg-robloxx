"""(v38 = copia da v37: export_clipes_v38.json -> reimport_clipes_v38.json; 21 acoes.)
(v37 = copia da v36: export_clipes_v38.json -> reimport_clipes_v38.json; 21 acoes.)
(v36 = copia da v35: export_clipes_v38.json -> reimport_clipes_v38.json; 18 acoes.)
(v35 = copia da v29: export_clipes_v38.json -> reimport_clipes_v38.json; 15 acoes.)
(v28 = copia da v27: export_clipes_v38.json -> reimport_clipes_v38.json; 12 acoes.)
(v27 = copia da v26 lendo viradas_v27.json / export_clipes_v38.json; resto igual.)
(v26 = copia do reimportar_clipes_v25: export_clipes_v38.json -> reimport_clipes_v38.json; 8 acoes; viradas nao sao lacos.)
(v25 = copia do reimportar_clipes_v21: le export_clipes_v25.json, grava reimport_clipes_v25.json; 6 acoes; para Arrancada e Frenagem
(nao sao lacos) o campo laco_ultimo_menos_primeiro_max e so informativo.)
(v21: le export_clipes_v21.json e grava reimport_clipes_v21.json; acoes Repouso, Andar, Trote, Corrida.)
Reimporta cada GLB do lote 1 numa cena LIMPA e valida pelo ESQUELETO REIMPORTADO: acoes presentes (so Repouso e
Andar), quadros/duracao, canais por osso, laco (ultimo quadro = primeiro), ossos/hierarquia (contra rig_v11.json),
malhas, influencias, soma dos pesos, materiais/imagens, escala; e a DEFORMACAO de cada acao comparada, quadro a quadro de
amostra, com a referencia do rig original (vertices casados pela posicao de repouso; coincidentes = todos os candidatos).
Uso: blender -b --factory-startup -P reimportar_clipes_v12.py -- <dir_glb> <dir_referencia> <rig_v11.json>"""
import bpy, sys, os, json
import numpy as np
from mathutils.kdtree import KDTree
a = sys.argv[sys.argv.index("--") + 1:]; DG, REF, RJ = (os.path.abspath(x) for x in a[:3])
RIG = json.load(open(RJ)); EXP = json.load(open(os.path.join(DG, "export_clipes_v38.json"))); QA = EXP["amostras"]
PAI = {o["nome"]: o["pai"] for o in RIG["ossos"]}; OUTR = {}
for L in ("LOW", "LOD1", "LOD2"):
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30
    ops = bpy.ops.import_scene.gltf.get_rna_type().properties.keys()
    bpy.ops.import_scene.gltf(filepath=os.path.join(DG, EXP["lods"][L]["arquivo"]), **({"bone_heuristic": "BLENDER"} if "bone_heuristic" in ops else {}))
    A = [o for o in sc.objects if o.type == "ARMATURE"][0]; mal = [o for o in sc.objects if o.type == "MESH" and o.vertex_groups]
    ossos = {b.name: (b.parent.name if b.parent else None) for b in A.data.bones}
    r = {"ossos": len(ossos), "nomes_faltando": sorted(set(PAI) - set(ossos)), "hierarquia_diferente": sorted(n for n in ossos if n in PAI and ossos[n] != PAI[n]), "malhas": {}, "acoes": {}}
    for m in mal:
        inf = [len([e for e in v.groups if e.weight > 1e-4]) for v in m.data.vertices]; soma = [sum(e.weight for e in v.groups) for v in m.data.vertices]
        r["malhas"][m.name] = {"tris": sum(len(p.vertices) - 2 for p in m.data.polygons), "max_influencias": max(inf), "sem_influencia": inf.count(0),
                               "soma_pesos": [round(min(soma), 4), round(max(soma), 4)], "materiais": [mt.name for mt in m.data.materials if mt]}
    r["imagens"] = sorted("%s %dx%d" % (im.name, *im.size) for im in bpy.data.images if im.size[0])
    pts = [m.matrix_world @ v.co for m in mal for v in m.data.vertices]; r["escala"] = {"z_min": round(min(p.z for p in pts), 3), "z_max": round(max(p.z for p in pts), 3)}
    ref = np.load(os.path.join(REF, "ref_%s.npz" % L)); cand = {}
    for m in mal:
        k0 = next((k for k in ref.files if k.endswith("|" + m.name)), None)
        if not k0: continue
        R0 = ref[k0][0]; kd = KDTree(len(R0))
        for i, p in enumerate(R0): kd.insert(p.tolist(), i)
        kd.balance(); cand[m.name] = [[j for _, j, _ in kd.find_range(m.matrix_world @ v.co, 1e-4)] or [-1] for v in m.data.vertices]
    for ac in bpy.data.actions:
        canais = {}
        for lay in ac.layers:
            for st in lay.strips:
                for cb in st.channelbags:
                    for fc in cb.fcurves:
                        if fc.data_path.startswith('pose.bones["'):
                            b = fc.data_path.split('"')[1]; canais.setdefault(b, set()).add(fc.data_path.split(".")[-1])
                            ini, fim = fc.keyframe_points[0].co[1], fc.keyframe_points[-1].co[1]
                            canais.setdefault("_laco_max", 0.0); canais["_laco_max"] = max(canais["_laco_max"], abs(fim - ini))
        A.animation_data_create(); A.animation_data.action = ac
        if A.animation_data.action_slot is None and len(ac.slots): A.animation_data.action_slot = ac.slots[0]
        nome = ac.name.split("|")[-1]; dv = 0.0
        for k, q in enumerate(QA.get(nome, [])):
            sc.frame_set(q); dg = bpy.context.evaluated_depsgraph_get()
            for m in mal:
                key = "%s|%s" % (nome, m.name)
                if key not in ref.files: continue
                e = m.evaluated_get(dg); me = e.to_mesh(); P = np.array([(m.matrix_world @ v.co)[:] for v in me.vertices]); e.to_mesh_clear(); Rk = ref[key][k + 1]
                dv = max(dv, max((min(float(np.abs(P[i] - Rk[j]).max()) for j in c) for i, c in enumerate(cand[m.name]) if c[0] >= 0), default=0.0))
        r["acoes"][ac.name] = {"quadros": [round(ac.frame_range[0], 2), round(ac.frame_range[1], 2)], "ossos_animados": len([b for b in canais if not b.startswith("_")]),
                               "canais_por_osso": sorted({"+".join(sorted(v)) for b, v in canais.items() if not b.startswith("_")}),
                               "laco_ultimo_menos_primeiro_max": round(canais.get("_laco_max", 0.0), 6), "desvio_max_vs_rig_original": round(dv, 5),
                               "quadros_comparados": len(QA.get(nome, []))}
    OUTR[L] = r; print("REIMPORT", L, json.dumps(r), flush=True)
json.dump(OUTR, open(os.path.join(DG, "reimport_clipes_v38.json"), "w"), indent=1); print("REIMPORT_CLIPES_OK", flush=True)
