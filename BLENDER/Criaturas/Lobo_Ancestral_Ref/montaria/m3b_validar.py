"""Montaria M3b: valida por REIMPORTACAO (cena vazia, so leitura) a sela v28 contra a sela M3 (58 ossos) e o lobo v28 (export28):
- esqueleto da sela v28 = esqueleto do lobo v28 (nomes, pais e repouso mundial de cada osso);
- malha da sela v28 = sela M3 (vertices, UV, material, imagens, pesos), sem peso nos ossos novos, <= 4 influencias.
Uso: blender -b --factory-startup -P m3b_validar.py -- <sela_m3.glb> <sela_v28.glb> <lobo_v28.glb> <saida.json>"""
import bpy, sys, json
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]
def importa(caminho):
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    for c in (bpy.data.meshes, bpy.data.armatures, bpy.data.materials, bpy.data.images):
        for x in list(c): c.remove(x)
    bpy.ops.import_scene.gltf(filepath=caminho)
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    ossos = {b.name: {"pai": b.parent.name if b.parent else None, "M": [list(r) for r in (arm.matrix_world @ b.matrix_local)]} for b in arm.data.bones}
    malhas = {}
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.vertex_groups: continue
        me = o.data; co = np.array([list(o.matrix_world @ v.co) for v in me.vertices])
        uv = np.array([list(d.uv) for d in me.uv_layers[0].data]) if me.uv_layers else np.zeros((0, 2))
        gi = {g.index: g.name for g in o.vertex_groups}
        pes = [{gi[g.group]: round(g.weight, 4) for g in v.groups if g.weight > 1e-4} for v in me.vertices]
        malhas[o.name] = {"co": co, "uv": uv, "pesos": pes, "materiais": [m.name for m in me.materials], "tris": sum(len(p.vertices) - 2 for p in me.polygons)}
    imgs = sorted((i.name, tuple(i.size)) for i in bpy.data.images if i.size[0])
    return ossos, malhas, imgs
o_m3, m_m3, i_m3 = importa(A[0]); o_28, m_28, i_28 = importa(A[1]); o_lobo, _, _ = importa(A[2])
res = {}
# esqueleto da sela v28 x lobo v28
dif = {n: float(np.abs(np.array(o_28[n]["M"]) - np.array(o_lobo[n]["M"])).max()) for n in o_lobo if n in o_28}
res["ossos"] = {"sela_m3": len(o_m3), "sela_v28": len(o_28), "lobo_v28": len(o_lobo),
                "faltam_na_sela_v28": sorted(set(o_lobo) - set(o_28)), "sobram_na_sela_v28": sorted(set(o_28) - set(o_lobo)),
                "pais_diferentes": [n for n in o_lobo if n in o_28 and o_28[n]["pai"] != o_lobo[n]["pai"]],
                "repouso_dif_max_vs_lobo": round(max(dif.values()), 6),
                "repouso_dif_max_vs_sela_m3": round(max(float(np.abs(np.array(o_28[n]["M"]) - np.array(o_m3[n]["M"])).max()) for n in o_m3), 6)}
# malha da sela
s3 = next(iter(m_m3.values())); s8 = next(iter(m_28.values()))
infl = max(len(p) for p in s8["pesos"]); sem = sum(1 for p in s8["pesos"] if not p)
novos = sorted({k for p in s8["pesos"] for k in p if k.startswith("Carpo")})
pesos_iguais = all(a == b for a, b in zip(s3["pesos"], s8["pesos"]))
res["sela"] = {"vertices": [len(s3["co"]), len(s8["co"])], "tris": [s3["tris"], s8["tris"]],
               "posicao_dif_max": round(float(np.abs(s3["co"] - s8["co"]).max()), 6) if s3["co"].shape == s8["co"].shape else "formas diferentes",
               "uv_dif_max": round(float(np.abs(s3["uv"] - s8["uv"]).max()), 6) if s3["uv"].shape == s8["uv"].shape else "formas diferentes",
               "materiais": [s3["materiais"], s8["materiais"]], "imagens": [i_m3, i_28], "pesos_iguais": pesos_iguais,
               "max_influencias": infl, "vertices_sem_peso": sem, "peso_em_ossos_novos": novos,
               "bbox_z": [round(float(s8["co"][:, 2].min()), 3), round(float(s8["co"][:, 2].max()), 3)]}
json.dump(res, open(A[3], "w"), indent=1, default=str); print("VALIDA_SELA", json.dumps(res, default=str))
