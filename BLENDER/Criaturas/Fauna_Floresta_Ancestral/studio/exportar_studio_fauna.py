# exportar_studio_fauna.py (16/11/2026): GLB de IMPORTACAO no Studio para a fauna da Floresta Ancestral
# (Cervo rig r2, Javali rig r4, Coruja rig r4). Mesmo metodo do Lobo Ancestral (Lobo_Ancestral_Ref/studio/exportar_studio.py):
# o osso Raiz nao tem peso (use_deform False) e o Import 3D do Roblox descarta ossos sem peso, mas os clipes animam a Raiz.
# Solucao: 1 triangulo DEGENERADO (area 0, invisivel) no Corpo, dentro do tronco, com peso 1 em Raiz.
# Malhas, pesos, UV e texturas aprovados nao mudam; o .blend de origem NAO e salvo. Sem acoes (clipes vao pelos dados).
# Escala: exporta em metros do Blender (1 m -> 1 stud no Import 3D); o tamanho de jogo e ajustado no Studio (porte PENDENTE).
# Uso: blender -b <rig.blend> -P studio/exportar_studio_fauna.py -- <Animal>
import bpy, bmesh, os, sys, json
AQUI = os.path.dirname(os.path.abspath(__file__))
animal = sys.argv[sys.argv.index("--") + 1]
OUT = os.path.join(AQUI, "export"); os.makedirs(OUT, exist_ok=True)
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
malhas = [o for o in bpy.data.objects if o.type == "MESH" and o.find_armature() == arm]
corpo = [o for o in malhas if o.name.endswith("_Corpo")][0]
tris0 = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in malhas}
# triangulo degenerado no centro da Pelve, com peso 1 so em Raiz
c = corpo.matrix_world.inverted() @ (arm.matrix_world @ arm.data.bones["Pelve"].head_local)
bm = bmesh.new(); bm.from_mesh(corpo.data)
vs = [bm.verts.new(c) for _ in range(3)]; bm.faces.new(vs); bm.verts.index_update(); idx = [v.index for v in vs]
bm.to_mesh(corpo.data); bm.free()
if corpo.data.uv_layers:
    pass  # UV dos 3 vertices novos fica em (0,0): area zero, nao aparece
g = corpo.vertex_groups.get("Raiz") or corpo.vertex_groups.new(name="Raiz")
g.add(idx, 1.0, "REPLACE")
arm.data.bones["Raiz"].use_deform = True
# FAUNA_NOVO_HASH=n (16/11): o Roblox reaproveita assets de imagem com o mesmo conteudo; se um upload ficou cinza, mudar
# 1 pixel do canto em n/255 (so na copia em memoria; os PNG aprovados no disco nao mudam) forca assets novos no Import 3D.
_nh = int(os.environ.get("FAUNA_NOVO_HASH", "0"))
if _nh:
    for im in {n.image for o in malhas for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image}:
        import numpy as np
        a = np.empty(im.size[0] * im.size[1] * im.channels, dtype=np.float32); im.pixels.foreach_get(a)
        a[0] = a[0] + _nh / 255.0 if a[0] < 0.5 else a[0] - _nh / 255.0
        im.pixels.foreach_set(a); im.update()
        im.pack()  # empacota os pixels em memoria (PNG novo) so nesta sessao; o .blend nao e salvo
for o in bpy.data.objects: o.select_set(False)
for o in [arm] + malhas: o.hide_set(False); o.select_set(True)
bpy.context.view_layer.objects.active = arm
glb = os.path.join(OUT, animal + "_Studio.glb")
bpy.ops.export_scene.gltf(filepath=glb, use_selection=True, export_format="GLB", export_yup=True, export_apply=False,
                          export_animations=False, export_def_bones=False, export_skins=True, export_image_format="AUTO",
                          export_tangents=True, export_reset_pose_bones=True)
info = {"glb": os.path.relpath(glb, AQUI), "bytes": os.path.getsize(glb), "origem": os.path.basename(bpy.data.filepath),
        "malhas_tris_origem": tris0, "ossos": len(arm.data.bones), "triangulo_raiz": idx,
        "altura_m": round(max((o.matrix_world @ __import__("mathutils").Vector(b)).z for o in malhas for b in o.bound_box), 3)}
json.dump(info, open(os.path.join(OUT, animal + "_Studio_info.json"), "w"), indent=1)
print("STUDIO_GLB", json.dumps(info))
