"""Exporta Silverwing_M2M.blend -> <nome>.glb (malha + esqueleto + so as animacoes PROPRIAS; as antigas do molde ficam
no .blend como fonte das asas) e grava MP4 curtos (fps da cena) dos clipes pedidos. Reimporta o GLB para conferir.
Uso: blender -b Silverwing_M2M.blend -P exportar_silverwing.py -- saida_dir nome_glb [clipes,para,video|nenhum]"""
import bpy, sys, os
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]; out = args[0]; nome = args[1] if len(args) > 1 else "Silverwing_M2M"
videos = None if len(args) < 3 else ([] if args[2] == "nenhum" else args[2].split(","))
os.makedirs(out, exist_ok=True)
ANTIGAS = {"Silverwing_Idle", "Silverwing_Walk", "Silverwing_Fly_Flap", "Silverwing_Fly_Glide", "Silverwing_Rest_Pose"}
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
acoes = sorted([a for a in bpy.data.actions if a.name.startswith("Silverwing_") and a.name not in ANTIGAS], key=lambda a: a.name)
A.animation_data_create(); A.animation_data.action = None
for t in list(A.animation_data.nla_tracks): A.animation_data.nla_tracks.remove(t)
for act in acoes:
    tr = A.animation_data.nla_tracks.new(); tr.name = act.name
    st = tr.strips.new(act.name, int(act.frame_range[0]), act)
    if len(act.slots): st.action_slot = act.slots[0]
    tr.mute = True
for o in bpy.data.objects: o.select_set(o in (A, M))
bpy.context.view_layer.objects.active = A
glb = os.path.join(out, nome + ".glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_animations=True,
                          export_animation_mode="NLA_TRACKS", export_image_format="JPEG", export_skins=True)
print("GLB", glb, round(os.path.getsize(glb) / 1e6, 2), "MB", "acoes", len(acoes))
sc = bpy.context.scene; sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 640, 400
if hasattr(sc.render.image_settings, "media_type"): sc.render.image_settings.media_type = "VIDEO"
sc.render.image_settings.file_format = "FFMPEG"
sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"
cam = bpy.data.objects["cam_rev"]; sc.camera = cam
for act in acoes:
    curto = act.name.replace("Silverwing_", "")
    if videos is not None and curto not in videos: continue
    A.animation_data.action = act
    if len(act.slots): A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); dur = f1 - f0
    sc.frame_start = f0; sc.frame_end = f0 + dur * (3 if dur < 30 else (2 if dur < 60 else 1))
    c = Vector((0, -0.1, 0.3)); cam.location = c + Vector((1.25, -1.45, 0.6)) * 1.1
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, "v2_" + curto + ".mp4")
    bpy.ops.render.render(animation=True)
    print("VIDEO", curto)
A.animation_data.action = None
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
print("REIMPORT ossos", len(arm.data.bones), "acoes", sorted(a.name for a in bpy.data.actions))
print("EXPORTAR_OK")
