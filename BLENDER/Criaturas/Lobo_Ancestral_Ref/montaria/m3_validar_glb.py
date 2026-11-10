"""Montaria M3 do Lobo Ancestral (copia do m3_validar_glb.py do Urso): valida o GLB da sela reimportando numa cena vazia (so leitura): malhas, triangulos, materiais, imagens (tamanho), armadura
(ossos), pesos (max influencias, vertices sem peso) e altura/posicao da sela. Uso: blender -b --factory-startup -P montaria/m3_validar_glb.py -- <glb> <saida.json>"""
import bpy, sys, json
A = sys.argv[sys.argv.index("--") + 1:]
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=A[0])
res = {"malhas": [], "armaduras": [], "imagens": [{"nome": i.name, "tamanho": list(i.size)} for i in bpy.data.images if i.size[0]]}
for o in bpy.data.objects:
    if o.type == "MESH":
        me = o.data; mx = max((len([g for g in v.groups if g.weight > 1e-4]) for v in me.vertices), default=0)
        sem = sum(1 for v in me.vertices if not any(g.weight > 1e-4 for g in v.groups))
        zs = [(o.matrix_world @ v.co).z for v in me.vertices]
        res["malhas"].append({"nome": o.name, "tris": sum(len(p.vertices) - 2 for p in me.polygons), "vertices": len(me.vertices), "materiais": [m.name for m in me.materials],
                              "uv": [u.name for u in me.uv_layers], "max_influencias": mx, "sem_peso": sem, "grupos": len(o.vertex_groups),
                              "z_min_max": [round(min(zs), 2), round(max(zs), 2)], "pai": o.parent.name if o.parent else None})
    if o.type == "ARMATURE": res["armaduras"].append({"nome": o.name, "ossos": len(o.data.bones)})
json.dump(res, open(A[1], "w"), indent=1); print("VALIDA", json.dumps(res))
