"""Exporta o piloto v9 por LOD: GLB com armature (37 ossos, nomes finais), malhas skinned (<= 20k tris cada, no maximo
4 influencias) e a acao tecnica 'Teste_Piloto' (30 qps). Ossos sem peso somem na importacao do Roblox: cada osso sem
peso no LOD recebe um triangulo degenerado (invisivel) na sua cabeca, 100% nele (como no Urso v2).
Antes de exportar grava a REFERENCIA do Blender (posicoes das malhas avaliadas pelo rig nos quadros de amostra), que
reimportar_rig_v9.py compara com o esqueleto reimportado. Nao salva o .blend (o triangulo extra so vai no GLB).
Uso: blender -b rig_v9/CR_LoboArtico_Rig.blend -P exportar_rig_v9.py -- <dir_saida> <dir_referencia>"""
import bpy, bmesh, sys, os, json
import numpy as np
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); REF = os.path.abspath(a[1]); os.makedirs(OUT, exist_ok=True); os.makedirs(REF, exist_ok=True)
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; AC = bpy.data.actions["Teste_Piloto"]; ARM.animation_data.action = AC
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"],
        "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}
QA = sorted(set(list(range(0, int(AC.frame_range[1]) + 1, 8)) + [25, 43, 72, 99, 119, 149, 169, 201, 221, 251, 269, 295, 313, 339, 355, 410, 470, 530, 590, 621, 665, 699, 782]))
OSS = [b.name for b in ARM.data.bones]
rel = {"quadros_amostra": QA, "acao": AC.name, "quadros": [int(AC.frame_range[0]), int(AC.frame_range[1])], "qps": sc.render.fps, "lods": {}}
# referencia do Blender (rig original)
for L, nomes in CONJ.items():
    obs = [bpy.data.objects[n] for n in nomes]; arr = {n: np.zeros((len(QA) + 1, len(o.data.vertices), 3), np.float32) for n, o in zip(nomes, obs)}
    for n, o in zip(nomes, obs): arr[n][0] = np.array([v.co[:] for v in o.data.vertices])
    for k, q in enumerate(QA):
        sc.frame_set(q); dg = bpy.context.evaluated_depsgraph_get()
        for n, o in zip(nomes, obs):
            e = o.evaluated_get(dg); m = e.to_mesh(); arr[n][k + 1] = np.array([v.co[:] for v in m.vertices]); e.to_mesh_clear()
    np.savez_compressed(os.path.join(REF, "ref_%s.npz" % L), **arr)
sc.frame_set(0)
ops = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
def kw(**d): return {k: v for k, v in d.items() if k in ops}
for L, nomes in CONJ.items():
    obs = [bpy.data.objects[n] for n in nomes]; usados = set()
    for o in obs:
        gn = {g.index: g.name for g in o.vertex_groups}
        for v in o.data.vertices:
            for e in v.groups:
                if e.weight > 0.001 and gn[e.group] in OSS: usados.add(gn[e.group])
    alvo = bpy.data.objects[nomes[1]]; alvo_me0 = alvo.data; alvo.data = alvo_me0.copy(); garant = []
    for bn in ARM.data.bones:
        if bn.name in usados: continue
        me = alvo.data; bm = bmesh.new(); bm.from_mesh(me); vs = [bm.verts.new(bn.head_local) for _ in range(3)]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
        g = alvo.vertex_groups.get(bn.name) or alvo.vertex_groups.new(name=bn.name); ids = list(range(len(me.vertices) - 3, len(me.vertices)))
        for og in alvo.vertex_groups:
            if og is not g: og.remove(ids)
        g.add(ids, 1.0, "REPLACE"); garant.append(bn.name)
    tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in obs}; assert all(t <= 20000 for t in tris.values()), tris
    for x in sc.objects: x.select_set(False)
    for o in [ARM] + obs:                                               # as malhas de LOD1/LOD2 ficam ocultas no .blend da v8
        o.hide_viewport = False; o.hide_select = False; o.hide_set(False); o.select_set(True)
    assert all(o.select_get() for o in [ARM] + obs), [o.name for o in obs if not o.select_get()]
    bpy.context.view_layer.objects.active = ARM
    arq = os.path.join(OUT, "CR_LoboArtico_%s_Rig.glb" % L)
    bpy.ops.export_scene.gltf(filepath=arq, **kw(export_format="GLB", use_selection=True, export_yup=True, export_image_format="AUTO", export_materials="EXPORT",
                                                 export_skins=True, export_all_influences=False, export_influence_nb=4, export_def_bones=False,
                                                 export_animations=True, export_animation_mode="ACTIONS", export_force_sampling=True, export_frame_range=False,
                                                 export_anim_single_armature=True, export_reset_pose_bones=True, export_optimize_animation_size=False,
                                                 export_bake_animation=False, export_morph=False))
    alvo.data = alvo_me0
    rel["lods"][L] = {"arquivo": os.path.basename(arq), "MB": round(os.path.getsize(arq) / 1e6, 2), "tris": tris, "ossos_garantidos_triangulo": garant}
    print("EXPORT", L, json.dumps(rel["lods"][L]), flush=True)
json.dump(rel, open(os.path.join(OUT, "export_rig_v9.json"), "w"), indent=1); print("EXPORT_RIG_OK", flush=True)
