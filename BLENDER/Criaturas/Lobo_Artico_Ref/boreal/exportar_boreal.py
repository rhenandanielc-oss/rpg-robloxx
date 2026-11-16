"""Exporta a camada Boreal (rig + Linhas_* com pele + Espinho_* rigidos) para o Import 3D do Roblox.
Mesmas opcoes do exportar_clipes_v41.py (Y para cima, pele 4 influencias), SEM animacoes. Os espinhos saem soltos
(sem pai de osso) na posicao de REPOUSO, para o Studio medir o encaixe em cada osso.
Uso: blender -b boreal/CR_LoboArtico_Boreal_rN.blend -P boreal/exportar_boreal.py -- rN"""
import bpy, os, sys, json
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
VER = ARGS[0] if ARGS else "r3"
AQUI = os.path.dirname(os.path.abspath(__file__)); EXP = os.path.join(AQUI, "export"); os.makedirs(EXP, exist_ok=True)
rig = bpy.data.objects["LoboArtico_Rig"]; rig.data.pose_position = "REST"
fx = [o for o in bpy.data.objects if o.name.startswith(("Linhas_", "Espinho_"))]
for o in fx:
    if o.name.startswith("Espinho_"):
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
bpy.ops.object.select_all(action="DESELECT")
rig.select_set(True)
for o in fx: o.select_set(True)
bpy.context.view_layer.objects.active = rig
ops = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
def kw(**d): return {k: v for k, v in d.items() if k in ops}
arq = os.path.join(EXP, "CR_LoboArtico_BorealFX_%s.glb" % VER)
bpy.ops.export_scene.gltf(filepath=arq, **kw(export_format="GLB", use_selection=True, export_yup=True, export_materials="EXPORT",
                                             export_skins=True, export_all_influences=False, export_influence_nb=4,
                                             export_def_bones=False, export_animations=False, export_morph=False))
print("EXPORT_BOREAL_OK", arq, round(os.path.getsize(arq) / 1e6, 3), "MB", [o.name for o in fx])
