"""Valida cada GLB V5 por reimportacao: objetos, tris por malha (<20k), ossos, acoes, imagens, materiais com textura.
Uso: blender -b --factory-startup -P validar_glb.py -- <saida.json> <Esp1> <Esp2> ..."""
import bpy, sys, os, json
a = sys.argv[sys.argv.index("--") + 1:]; out, esps = a[0], a[1:]
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res = {}
for e in esps:
    glb = os.path.join(RAIZ, "_Export", e + "_v5.glb")
    if not os.path.exists(glb): res[e] = {"erro": "GLB ausente"}; continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        bpy.ops.import_scene.gltf(filepath=glb)
    except Exception as ex:
        res[e] = {"erro": str(ex)[:200]}; continue
    ms = [o for o in bpy.data.objects if o.type == "MESH"]; arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    tris = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in ms}
    semtex = [m.name for m in bpy.data.materials if m.node_tree and not any(n.type == "TEX_IMAGE" for n in m.node_tree.nodes) and "Garra" not in m.name and "Olho" not in m.name and "Osso" not in m.name]
    res[e] = {"KB": int(os.path.getsize(glb) / 1024), "malhas": len(ms), "tris_total": sum(tris.values()), "maior_malha": max(tris.values()) if tris else 0,
              "acima_20k": [k for k, v in tris.items() if v > 20000], "esqueletos": len(arms), "ossos": len(arms[0].data.bones) if arms else 0,
              "acoes": len(bpy.data.actions), "imagens": len([i for i in bpy.data.images if i.size[0] > 0]),
              "materiais_sem_textura": semtex, "ok": bool(arms) and len(bpy.data.actions) > 0 and not [k for k, v in tris.items() if v > 20000]}
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("VALIDADO", {k: v.get("ok") for k, v in res.items()})
