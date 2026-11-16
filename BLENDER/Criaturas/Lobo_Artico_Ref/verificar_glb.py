"""Confere um GLB exportado reimportando-o numa cena vazia: malhas, tris por malha, materiais, imagens (tamanho),
altura da cernelha (Z max no trecho do ombro) e pes no chao. Saida: JSON ao lado do GLB.
Uso: blender -b --factory-startup -P verificar_glb.py -- <arquivo.glb> [<arquivo2.glb> ...]"""
import bpy, sys, os, json
for caminho in sys.argv[sys.argv.index("--") + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=caminho)
    malhas = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    rel = {"arquivo": os.path.basename(caminho), "malhas": {}, "imagens": {}}
    zs_ombro, zmin = [], 1e9
    for o in malhas:
        me = o.data; mw = o.matrix_world
        t = sum(len(p.vertices) - 2 for p in me.polygons)
        rel["malhas"][o.name] = {"tris": t, "materiais": [m.name for m in me.materials if m], "uv": len(me.uv_layers),
                                 "acima_20k": t > 20000}
        for v in me.vertices:
            w = mw @ v.co; zmin = min(zmin, w.z)
            if "Corpo" in o.name and -3.6 < w.y < -2.6 and abs(w.x) < 0.3: zs_ombro.append(w.z)
    for im in bpy.data.images:
        if im.size[0]: rel["imagens"][im.name] = list(im.size)
    rel["tris_total"] = sum(m["tris"] for m in rel["malhas"].values())
    rel["cernelha_z"] = round(max(zs_ombro), 3) if zs_ombro else None
    rel["z_min"] = round(zmin, 3)
    json.dump(rel, open(caminho[:-4] + "_verificacao.json", "w"), indent=1)
    print("VERIFICA", json.dumps(rel))
