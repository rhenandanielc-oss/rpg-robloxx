"""Exporta o Lobo Ancestral (malha de jogo + esqueleto + todas as acoes Lobo_*) em GLB para o Roblox e valida por
reimportacao. Cuidados do projeto: o Roblox liga malha a osso PELO NOME e descarta osso sem peso -> a Raiz (movimento do
corpo) recebe um peso minimo num vertice interno; restricoes de IK sao removidas (as acoes ja estao assadas em FK).
Uso: blender -b rig/Lobo_Ancestral_Anim.blend -P exportar_lobo.py -- <saida_dir>"""
import bpy, sys, os, json, math
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for pb in arm.pose.bones:
    for c in list(pb.constraints): pb.constraints.remove(c)
for o in list(sc.objects):
    if o.type == "EMPTY": bpy.data.objects.remove(o)
arm.data.bones["Raiz"].use_deform = True
g = LO.vertex_groups.get("Raiz") or LO.vertex_groups.new(name="Raiz")
me = LO.data
cand = min((v for v in me.vertices if abs(v.co.x) < 0.3), key=lambda v: (v.co - V((0, -1.5, 3.6))).length)   # ventre, por dentro do pelo
g.add([cand.index], 0.02, "REPLACE")
pesos = {vg.name: 0.0 for vg in LO.vertex_groups}
nomes_g = {vg.index: vg.name for vg in LO.vertex_groups}
for v in me.vertices:
    for q in v.groups: pesos[nomes_g[q.group]] += q.weight
sem_peso = [b.name for b in arm.data.bones if b.use_deform and pesos.get(b.name, 0.0) <= 0.0]
print("OSSOS_SEM_PESO", sem_peso)
acoes = sorted(a.name for a in bpy.data.actions if a.name.startswith("Lobo_"))
print("ACOES", len(acoes), acoes)
if not arm.animation_data: arm.animation_data_create()
arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
bpy.ops.object.select_all(action="DESELECT"); LO.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
destino = os.path.join(OUT, "Lobo_Ancestral.glb")
bpy.ops.export_scene.gltf(filepath=destino, use_selection=True, export_format="GLB", export_yup=True, export_apply=False,
                          export_animations=True, export_animation_mode="ACTIONS", export_force_sampling=True,
                          export_def_bones=False, export_skins=True, export_image_format="AUTO", export_anim_single_armature=True,
                          export_reset_pose_bones=True)
print("GLB", destino, round(os.path.getsize(destino) / 1e6, 2), "MB")
# referencia para a validacao: posicao mundial de alguns ossos em quadros escolhidos
ref = {}
for nome, q in (("Lobo_Andar", 10), ("Lobo_Corrida", 5), ("Lobo_Uivo", 60), ("Lobo_Deitado", 0), ("Lobo_Mordida", 14)):
    act = bpy.data.actions[nome]; arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    sc.frame_set(int(act.frame_range[0]) + q)
    ref[nome] = {b: list(arm.matrix_world @ arm.pose.bones[b].head) for b in ("Cabeca", "Mandibula", "MaoE", "PeD", "Cauda6", "Pelve")}
arm.animation_data.action = None
json.dump({"ref": ref, "acoes": acoes, "tris": sum(len(p.vertices) - 2 for p in me.polygons)}, open(os.path.join(OUT, "referencia_export.json"), "w"), indent=1)
print("EXPORT_OK")
