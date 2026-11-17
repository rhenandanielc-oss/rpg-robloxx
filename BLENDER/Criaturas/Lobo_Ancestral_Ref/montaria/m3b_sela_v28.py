"""Montaria M3b (10/11/2026): reexporta a MESMA sela de jogo (M3 aprovada; montaria/export_sela/) no esqueleto da marcha v28
(60 ossos: os 58 de antes + CarpoE/CarpoD, auxiliares do carpo). A malha, o material unico, o UV, as texturas, a escala, a
posicao e os pesos da sela nao mudam; so a armadura ganha os 2 ossos (mesma posicao de repouso do rig v28, sem peso na sela).
Antes de exportar, confere que os 58 ossos antigos tem o MESMO repouso no rig da sela e no rig v28 (bind pose compativel).
Le export_sela/Lobo_Ancestral_Sela_Jogo.blend (nao e salvo por cima) e grava em <pasta_saida>.
Uso: blender -b montaria/export_sela/Lobo_Ancestral_Sela_Jogo.blend -P montaria/m3b_sela_v28.py -- <rig_v28.blend> <pasta_saida>"""
import bpy, sys, os, json
A = sys.argv[sys.argv.index("--") + 1:]; RIG28 = os.path.abspath(A[0]); OUT = os.path.abspath(A[1]); os.makedirs(OUT, exist_ok=True)
arm = bpy.data.objects["Lobo_Ancestral_Rig"]; sela = bpy.data.objects["Lobo_Ancestral_Sela"]
with bpy.data.libraries.load(RIG28) as (src, dst): dst.armatures = ["Lobo_Ancestral_Rig"]
a28 = dst.armatures[0]
# 1. bind pose: os 58 ossos antigos tem o mesmo repouso?
dif = 0.0
for b in arm.data.bones:
    b2 = a28.bones[b.name]
    dif = max(dif, max(abs(x - y) for r1, r2 in zip(b.matrix_local, b2.matrix_local) for x, y in zip(r1, r2)))
    assert (b.parent.name if b.parent else None) == (b2.parent.name if b2.parent else None), b.name
print("BIND_DIF_MAX", dif)
assert dif < 1e-4, "repouso diferente"
novos = [b for b in a28.bones if b.name not in arm.data.bones]
print("NOVOS", [b.name for b in novos])
# 2. acrescenta os ossos novos (edit mode) com o mesmo repouso do v28
if arm.animation_data: arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
for o in list(bpy.context.selected_objects): o.select_set(False)
bpy.context.view_layer.objects.active = arm; arm.select_set(True); bpy.ops.object.mode_set(mode="EDIT"); eb = arm.data.edit_bones
for b in novos:
    e = eb.new(b.name); e.head = b.head_local; e.tail = b.tail_local
    e.align_roll((b.matrix_local.to_3x3() @ __import__("mathutils").Vector((0, 0, 1))))
    e.parent = eb[b.parent.name]; e.use_connect = False; e.use_deform = b.use_deform
bpy.ops.object.mode_set(mode="OBJECT")
for b in novos:
    m1 = arm.data.bones[b.name].matrix_local; m2 = b.matrix_local
    print("REPOUSO", b.name, max(abs(x - y) for r1, r2 in zip(m1, m2) for x, y in zip(r1, r2)))
# 3. a sela nao recebe peso nos ossos novos (grupos vazios nao sao criados); exporta igual ao m3
for o in list(bpy.context.selected_objects): o.select_set(False)
sela.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = sela
glb = os.path.join(OUT, "Lobo_Ancestral_Sela.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_animations=False, export_skins=True, export_yup=True,
                          export_apply=False, export_image_format="AUTO", export_tangents=True)
me = sela.data
info = {"tris": sum(len(p.vertices) - 2 for p in me.polygons), "vertices": len(me.vertices), "ossos_armadura": len(arm.data.bones),
        "grupos_sela": len(sela.vertex_groups), "glb": os.path.basename(glb), "glb_bytes": os.path.getsize(glb), "bind_dif_max": dif,
        "ossos_novos": [b.name for b in novos], "base": "export_sela/Lobo_Ancestral_Sela_Jogo.blend (M3 aprovada)"}
json.dump(info, open(os.path.join(OUT, "sela_jogo_info.json"), "w"), indent=1); print("SELA_V28", json.dumps(info))
bpy.ops.file.make_paths_absolute(); bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Sela_Jogo_v28.blend"), copy=True); print("SELA_V28_OK")
