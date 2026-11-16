# exportar_studio.py (15/11/2026): GLB de IMPORTACAO no Studio do Lobo Ancestral v31 + sela v28 no MESMO esqueleto.
# Motivo (medido na reimportacao de export31/ e export_sela_v28/): o osso Raiz nao tem peso no lobo e a sela GLB tem 48 ossos
# sem peso; o Import 3D do Roblox descarta ossos sem peso (licao do Drake/urso), e os clipes animam a Raiz (altura/arfagem).
# Solucao: um so GLB com as 2 malhas (lobo LOW v31 + sela v28) na armadura do lobo + 1 triangulo DEGENERADO (area 0) na sela
# com peso 1 em Raiz, dentro do corpo. Sem acoes (os clipes vao pelos dados do adaptador). Nada aprovado e alterado:
# malha do lobo, pesos, UV, texturas e sela iguais (conferido abaixo). Uso:
#   blender -b rig18/Lobo_Ancestral_Anim_v31.blend -P studio/exportar_studio.py
import bpy, os, json
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
OUT = os.path.join(RAIZ, "export31_studio"); os.makedirs(OUT, exist_ok=True)
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
lobo = [o for o in bpy.data.objects if o.type == "MESH" and o.find_armature() == arm and "LOW" in o.name][0]
SELA_BLEND = os.path.join(RAIZ, "montaria", "export_sela_v28", "Lobo_Ancestral_Sela_Jogo_v28.blend")
with bpy.data.libraries.load(SELA_BLEND, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if "Sela" in n and "Rig" not in n]
sela = None
for o in dst.objects:
    if o is not None and o.type == "MESH":
        bpy.context.scene.collection.objects.link(o); sela = o
assert sela, "sela nao encontrada"
# a sela volta a deformar pela armadura do lobo (os ossos tem os mesmos nomes; repouso igual, validado em 10/11)
for m in sela.modifiers:
    if m.type == "ARMATURE": m.object = arm
sela.parent = arm; sela.matrix_parent_inverse = arm.matrix_world.inverted()
dif = max((arm.data.bones[b.name].matrix_local.translation - b.matrix_local.translation).length
          for b in bpy.data.armatures[[a.name for a in bpy.data.armatures if a != arm.data][0]].bones) if len(bpy.data.armatures) > 1 else 0.0
# triangulo degenerado (3 vertices no mesmo ponto, dentro do tronco) com peso 1 em Raiz
me = sela.data
import bmesh
bm = bmesh.new(); bm.from_mesh(me)
c = arm.matrix_world @ arm.data.bones["Pelve"].head_local
cl = sela.matrix_world.inverted() @ c
vs = [bm.verts.new(cl) for _ in range(3)]; bm.faces.new(vs); bm.verts.index_update(); idx = [v.index for v in vs]
bm.to_mesh(me); bm.free()
g = sela.vertex_groups.get("Raiz") or sela.vertex_groups.new(name="Raiz")
g.add(idx, 1.0, "REPLACE")
for o in bpy.data.objects: o.select_set(False)
for o in (arm, lobo, sela): o.select_set(True)
bpy.context.view_layer.objects.active = arm
for o in list(bpy.data.objects):
    if o not in (arm, lobo, sela) and o.type in ("MESH", "ARMATURE") and o.name in bpy.context.view_layer.objects: o.hide_set(True)
glb = os.path.join(OUT, "Lobo_Ancestral_Studio.glb")
bpy.ops.export_scene.gltf(filepath=glb, use_selection=True, export_format="GLB", export_yup=True, export_apply=False,
                          export_animations=False, export_def_bones=False, export_skins=True, export_image_format="AUTO",
                          export_tangents=True, export_reset_pose_bones=True)
info = {"glb": glb, "bytes": os.path.getsize(glb), "lobo": lobo.name, "lobo_tris": sum(len(p.vertices) - 2 for p in lobo.data.polygons),
        "sela": sela.name, "sela_tris": sum(len(p.vertices) - 2 for p in sela.data.polygons), "ossos": len(arm.data.bones),
        "bind_dif_sela_x_lobo": dif, "triangulo_raiz": idx}
json.dump(info, open(os.path.join(OUT, "exportar_studio_info.json"), "w"), indent=1); print("STUDIO_GLB", json.dumps(info))
