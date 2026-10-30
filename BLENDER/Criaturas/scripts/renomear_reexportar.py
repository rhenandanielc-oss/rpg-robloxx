# Abre o .blend de uma forma, renomeia malha e esqueleto para o nome da forma e reexporta GLB/FBX com as mesmas opcoes.
# Uso: blender -b --factory-startup -P renomear_reexportar.py -- <pasta_destino> <Nome_da_Forma>
import bpy, sys, os
DEST = sys.argv[sys.argv.index("--") + 1]; NOME = sys.argv[sys.argv.index("--") + 2]
bpy.ops.wm.open_mainfile(filepath=os.path.join(DEST, NOME + ".blend"))
print("OBJETOS", [(o.name, o.type) for o in bpy.data.objects])
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
mesh = next(o for o in bpy.data.objects if o.type == "MESH" and o.parent == arm)
mesh.name = NOME; arm.name = NOME + "_Rig"
for o in bpy.context.scene.objects: o.select_set(False)
arm.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=os.path.join(DEST, NOME + ".glb"), export_format="GLB", use_selection=True, export_animations=True, export_animation_mode="ACTIONS", export_skins=True, export_yup=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(DEST, NOME + ".fbx"), use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=True,
                         bake_anim_use_nla_strips=False, path_mode="COPY", embed_textures=True, axis_forward="-Z", axis_up="Y")
bpy.ops.wm.save_mainfile()
print("RENOMEADO", mesh.name, arm.name)
