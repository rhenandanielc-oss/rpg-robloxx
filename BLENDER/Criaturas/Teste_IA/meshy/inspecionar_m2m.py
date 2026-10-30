"""Inspecao do rig e das animacoes de dragao do Mesh2Motion (CC0): ossos (cabeca/cauda em mundo), acoes, alcance,
e quais ossos cada acao anima. Renderiza o rig de referencia (model-dragon nao e usado)."""
import bpy, sys, os
args = sys.argv[sys.argv.index("--") + 1:]; rig, anim = args[0], args[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=rig)
A = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
print("RIG", A.name, "ossos", len(A.data.bones), "escala", tuple(A.scale), "rot", tuple(A.rotation_euler))
for b in A.data.bones:
    h = A.matrix_world @ b.head_local; t = A.matrix_world @ b.tail_local
    print("OSSO %-24s pai=%-20s h=(%.3f,%.3f,%.3f) t=(%.3f,%.3f,%.3f)" % (b.name, b.parent.name if b.parent else "-", *h, *t))
print("MESHES", [(o.name, len(o.data.vertices)) for o in bpy.data.objects if o.type == "MESH"])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=anim)
arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
print("ANIM_ARMS", [(a.name, len(a.data.bones)) for a in arms], "MESHES", [o.name for o in bpy.data.objects if o.type == "MESH"])
for act in bpy.data.actions:
    ossos = set()
    try:
        for sl in act.layers[0].strips[0].channelbags:
            for fc in sl.fcurves:
                if fc.data_path.startswith('pose.bones["'): ossos.add(fc.data_path.split('"')[1])
    except Exception as e:
        for fc in getattr(act, "fcurves", []):
            if fc.data_path.startswith('pose.bones["'): ossos.add(fc.data_path.split('"')[1])
    print("ACAO", act.name, tuple(act.frame_range), "ossos_animados", len(ossos))
print("FPS", bpy.context.scene.render.fps)
print("M2M_OK")
