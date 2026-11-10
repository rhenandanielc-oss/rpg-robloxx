# Valida o GLB da sela da Wyvern por reimportacao numa cena vazia (somente leitura do GLB; nada e salvo):
#   triangulos/vertices, ossos da armadura, influencias por vertice (<= 4, normalizadas), material e texturas embutidas,
#   e desvio de posicao dos vertices em repouso contra a sela original (Wyvern_Sela_Jogo.blend, mesmo repouso).
# Uso: blender -b --factory-startup -P 18d_validar_glb_sela.py -- <Wyvern_Sela.glb> <Wyvern_Sela_Jogo.blend> <saida.json>
import bpy, sys, json
import numpy as np
from mathutils.kdtree import KDTree
argv = sys.argv[sys.argv.index("--") + 1:]
GLB, BLEND, OUT = argv
with bpy.data.libraries.load(BLEND) as (src, dst): dst.objects = [n for n in src.objects if n in ("Wyvern_Sela", "Wyvern_Rig")]
orig = [o for o in dst.objects if o and o.name.startswith("Wyvern_Sela")][0]
P0 = np.array([orig.matrix_world @ v.co for v in orig.data.vertices])
nb_orig = len([o for o in dst.objects if o and o.type == "ARMATURE"][0].data.bones)
for o in list(bpy.data.objects):
    if o.users_collection == () or True: pass
bpy.ops.import_scene.gltf(filepath=GLB)
imp = [o for o in bpy.context.selected_objects if o.type == "MESH"][0]
arm = [o for o in bpy.context.selected_objects if o.type == "ARMATURE"][0]
dg = bpy.context.evaluated_depsgraph_get(); ev = imp.evaluated_get(dg); me = ev.to_mesh()
P1 = np.array([imp.matrix_world @ v.co for v in me.vertices]); me.calc_loop_triangles(); tris = len(me.loop_triangles); ev.to_mesh_clear()
kd = KDTree(len(P1))
for i, p in enumerate(P1): kd.insert(p, i)
kd.balance()
desv = max(kd.find(p)[2] for p in P0)
infl = [len([g for g in v.groups if g.weight > 1e-6]) for v in imp.data.vertices]
soma = [sum(g.weight for g in v.groups) for v in imp.data.vertices]
mats = [m.name for m in imp.data.materials]
imgs = sorted({n.image.name for m in imp.data.materials for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image})
R = {"tris": tris, "vertices_glb": len(P1), "vertices_original": len(P0), "ossos_glb": len(arm.data.bones), "ossos_rig": nb_orig,
     "grupos": sorted(g.name for g in imp.vertex_groups), "influencias_max": max(infl), "soma_pesos_min_max": [round(min(soma), 4), round(max(soma), 4)],
     "materiais": mats, "imagens": imgs, "desvio_max_repouso": round(float(desv), 5),
     "nota_vertices": "o glTF duplica vertices nas costuras de UV/normal; o desvio e medido do original para o vertice mais perto do GLB"}
json.dump(R, open(OUT, "w"), indent=1); print("VALIDA", json.dumps(R))
