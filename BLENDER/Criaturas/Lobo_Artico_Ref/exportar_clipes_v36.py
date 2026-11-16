"""(v36 = copia da v35 com 18 acoes: Deitado sai; + Descanso, Adormecer, Dormindo, Despertar; saida export_clipes_v36.json.)
(v35 = copia da v28/v29 com 15 acoes: + Deitar, Deitado (laco), LevantarDeitado - lote de vida, bloco 1; saida export_clipes_v36.json.)
(v28 = copia da v27 com 12 acoes: + AndarParaTrote, TroteParaAndar, TroteParaCorrida, CorridaParaTrote (acoes de uma vez); saida export_clipes_v36.json.)
(v27 = copia da v26 lendo viradas_v27.json / export_clipes_v36.json; resto igual.)
(v26 = copia do exportar_clipes_v25 com as 8 acoes finais (+ VirarEsquerda, VirarDireita; acoes de uma vez); saida export_clipes_v36.json.)
(v25 = copia do exportar_clipes_v21 com as 6 acoes finais: Repouso, Andar, Trote, Corrida, Arrancada, Frenagem; saida export_clipes_v25.json;
Arrancada e Frenagem sao acoes de uma vez - todos os quadros entram na referencia.)
(v21: lote 1 + L2a - Repouso, Andar, Trote, Corrida; saidas export_clipes_v21.json.)
Exporta o lote 1 por LOD: GLB com armature (37 ossos), malhas skinned (<= 20k tris, <= 4 influencias) e SO as acoes
'Repouso' e 'Andar' (Teste_Piloto e Teste_Transicao sao removidas nesta sessao de export; o .blend nao e salvo).
Ossos sem peso: triangulo-guarda degenerado na cabeca do osso (Raiz), como no pipeline.
Antes grava a REFERENCIA do rig original (posicoes avaliadas por acao/quadro) para reimportar_clipes_v12.py.
Uso: blender -b anim_v12/CR_LoboArtico_Anim.blend -P exportar_clipes_v12.py -- <dir_saida> <dir_referencia>"""
import bpy, bmesh, sys, os, json
import numpy as np
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); REF = os.path.abspath(a[1]); os.makedirs(OUT, exist_ok=True); os.makedirs(REF, exist_ok=True)
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; FINAIS = ("Repouso", "Andar", "Trote", "Corrida", "Arrancada", "Frenagem", "VirarEsquerda", "VirarDireita", "AndarParaTrote", "TroteParaAndar", "TroteParaCorrida", "CorridaParaTrote", "Deitar", "Descanso", "Adormecer", "Dormindo", "Despertar", "LevantarDeitado")
for ac in [ac for ac in bpy.data.actions if ac.name not in FINAIS]: bpy.data.actions.remove(ac)
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"],
        "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}
def usar(nome):
    ac = bpy.data.actions[nome]; ARM.animation_data.action = ac
    if ARM.animation_data.action_slot is None and len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    return ac
QA = {"Andar": list(range(0, 37)), "Repouso": list(range(0, 241, 4)), "Trote": list(range(0, int(bpy.data.actions["Trote"].frame_range[1]) + 1)), "Corrida": list(range(0, int(bpy.data.actions["Corrida"].frame_range[1]) + 1)),
      "Arrancada": list(range(0, int(bpy.data.actions["Arrancada"].frame_range[1]) + 1)), "Frenagem": list(range(0, int(bpy.data.actions["Frenagem"].frame_range[1]) + 1)),
      "VirarEsquerda": list(range(0, int(bpy.data.actions["VirarEsquerda"].frame_range[1]) + 1)), "VirarDireita": list(range(0, int(bpy.data.actions["VirarDireita"].frame_range[1]) + 1))}
for _n in ("AndarParaTrote", "TroteParaAndar", "TroteParaCorrida", "CorridaParaTrote", "Deitar", "Descanso", "Adormecer", "Dormindo", "Despertar", "LevantarDeitado"): QA[_n] = list(range(0, int(bpy.data.actions[_n].frame_range[1]) + 1))
rel = {"acoes": {n: {"quadros": [int(bpy.data.actions[n].frame_range[0]), int(bpy.data.actions[n].frame_range[1])]} for n in FINAIS}, "amostras": QA, "lods": {}}
for L, nomes in CONJ.items():
    obs = [bpy.data.objects[n] for n in nomes]; arr = {}
    for acn in FINAIS:
        usar(acn)
        for n, o in zip(nomes, obs): arr["%s|%s" % (acn, n)] = np.zeros((len(QA[acn]) + 1, len(o.data.vertices), 3), np.float32)
        for k, q in enumerate(QA[acn]):
            sc.frame_set(q); dg = bpy.context.evaluated_depsgraph_get()
            for n, o in zip(nomes, obs):
                e = o.evaluated_get(dg); m = e.to_mesh(); arr["%s|%s" % (acn, n)][k + 1] = np.array([v.co[:] for v in m.vertices]); e.to_mesh_clear()
        for n, o in zip(nomes, obs): arr["%s|%s" % (acn, n)][0] = np.array([v.co[:] for v in o.data.vertices])
    np.savez_compressed(os.path.join(REF, "ref_%s.npz" % L), **arr)
usar("Andar"); sc.frame_set(0)
ops = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
def kw(**d): return {k: v for k, v in d.items() if k in ops}
OSS = [b.name for b in ARM.data.bones]
for L, nomes in CONJ.items():
    obs = [bpy.data.objects[n] for n in nomes]; usados = set()
    for o in obs:
        gn = {g.index: g.name for g in o.vertex_groups}
        for v in o.data.vertices:
            for e in v.groups:
                if e.weight > 0.001 and gn[e.group] in OSS: usados.add(gn[e.group])
    alvo = bpy.data.objects[nomes[1]]; me0 = alvo.data; alvo.data = me0.copy(); garant = []
    for bn in ARM.data.bones:
        if bn.name in usados: continue
        me = alvo.data; bm = bmesh.new(); bm.from_mesh(me); vs = [bm.verts.new(bn.head_local) for _ in range(3)]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
        g = alvo.vertex_groups.get(bn.name) or alvo.vertex_groups.new(name=bn.name); ids = list(range(len(me.vertices) - 3, len(me.vertices)))
        for og in alvo.vertex_groups:
            if og is not g: og.remove(ids)
        g.add(ids, 1.0, "REPLACE"); garant.append(bn.name)
    tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs}; assert all(t <= 20000 for t in tris.values()), tris
    for x in sc.objects: x.select_set(False)
    for o in [ARM] + obs: o.hide_viewport = False; o.hide_select = False; o.hide_set(False); o.select_set(True)
    bpy.context.view_layer.objects.active = ARM
    arq = os.path.join(OUT, "CR_LoboArtico_%s_Clipes.glb" % L)
    bpy.ops.export_scene.gltf(filepath=arq, **kw(export_format="GLB", use_selection=True, export_yup=True, export_image_format="AUTO", export_materials="EXPORT",
                                                 export_skins=True, export_all_influences=False, export_influence_nb=4, export_def_bones=False,
                                                 export_animations=True, export_animation_mode="ACTIONS", export_force_sampling=True, export_frame_range=False,
                                                 export_anim_single_armature=True, export_reset_pose_bones=True, export_optimize_animation_size=False,
                                                 export_bake_animation=False, export_morph=False))
    alvo.data = me0
    rel["lods"][L] = {"arquivo": os.path.basename(arq), "MB": round(os.path.getsize(arq) / 1e6, 2), "tris": tris, "ossos_garantidos_triangulo": garant}
    print("EXPORT", L, json.dumps(rel["lods"][L]), flush=True)
json.dump(rel, open(os.path.join(OUT, "export_clipes_v36.json"), "w"), indent=1); print("EXPORT_CLIPES_OK", flush=True)
