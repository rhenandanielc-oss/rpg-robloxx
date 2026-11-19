"""Previa da aura A1: quadros e videos (Repouso e Andar) em luz baixa de Terras Corrompidas, para julgar o brilho.
Uso: blender -b -t 4 CR_Cerbero_Aura_A1.blend -P render_aura.py -- <saida_dir>"""
import bpy, sys, os, math
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; sc.render.fps = 30; sc.render.threads_mode = "FIXED"; sc.render.threads = 4
rig = bpy.data.objects["Cerbero_Rig"]
for o in list(sc.objects):
    if o.type in ("CAMERA", "LIGHT") or o.name.startswith(("IK_", "Polo_")): o.hide_render = True
MATS = [m for m in bpy.data.materials if m.use_nodes and m.node_tree and "tempo" in m.node_tree.nodes]   # A2: peles + chamas
w = bpy.data.worlds.new("Noite"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.045, 0.06, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
for nome, en, rot, cor in (("Lua", 1.2, (0.9, 0, -0.7), (0.75, 0.75, 0.9)), ("Contra", 0.8, (2.2, 0, 2.6), (0.9, 0.5, 0.45))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.color = cor; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=300); ch = bpy.context.object; mc = bpy.data.materials.new("Chao"); mc.use_nodes = True
mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.06, 0.055, 0.06, 1); ch.data.materials.append(mc)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16; sc.view_settings.view_transform = "Standard"                      # A2: cores do fogo saturadas (AgX lavava)
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
VISTAS = {"34": ((-30, -32, 19), (0, -1, 9), 50), "cab": ((-6, -32, 18), (0, -8, 14.5), 55), "lado": ((-44, 0, 9), (0, 0, 8.5), 50)}
ALVO = bpy.data.objects.get("AlvoCamera")                  # A3: chamas giram no proprio eixo para olhar a camera
CHAMAS = [o for o in bpy.data.objects if "rot_repouso" in o.keys()]
def vista(n):
    pos, alvo, lente = VISTAS[n]; cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
    if ALVO: ALVO.location = pos
def modo_chamas(andando):
    for o in CHAMAS: o.rotation_euler = o["rot_andar"] if andando else o["rot_repouso"]
def usar(nome, rep):
    a = bpy.data.actions["Cerbero_" + nome]; f0, f1 = int(a.frame_range[0]), int(a.frame_range[1]); n = f1 - f0 + 1
    if not rig.animation_data: rig.animation_data_create()
    rig.animation_data.action = None
    for tr in list(rig.animation_data.nla_tracks): rig.animation_data.nla_tracks.remove(tr)
    st = rig.animation_data.nla_tracks.new().strips.new(nome, f0, a); st.repeat = rep
    return f0, f0 + n * rep - 1
def anima_tempo(f0, f1):
    for mat in MATS:
        nt = mat.node_tree; tempo = nt.nodes["tempo"].outputs[0]
        if nt.animation_data: nt.animation_data_clear()
        tempo.default_value = 0.0; tempo.keyframe_insert("default_value", frame=f0)
        tempo.default_value = (f1 - f0) / 30; tempo.keyframe_insert("default_value", frame=f1)
        a = nt.animation_data.action
        fcs = getattr(a, "fcurves", None) or [fc for ly in a.layers for st in ly.strips for cb in st.channelbags for fc in cb.fcurves]
        for fc in fcs:
            for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
sc.render.resolution_x, sc.render.resolution_y = 900, 640
f0, f1 = usar("Repouso", 1); anima_tempo(f0, f0 + 180); modo_chamas(False)
for q in (0, 14, 27, 40):                                   # quadros ao longo de um pulso (1,8 s)
    sc.frame_set(f0 + q)
    for v in ("34", "cab", "lado"):
        vista(v); sc.render.filepath = os.path.join(OUT, "aura_%s_q%02d.png" % (v, q)); bpy.ops.render.render(write_still=True)
print("QUADROS_OK", flush=True)
sc.render.image_settings.media_type = "VIDEO"; sc.render.image_settings.file_format = "FFMPEG"
sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"; sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
sc.render.resolution_x, sc.render.resolution_y = 640, 440
VIDEOS = (("Repouso", 1, ["cab"], 120), ("Andar", 3, ["34", "lado"], None))
if CHAMAS: VIDEOS = (("Repouso", 1, ["34", "lado"], 120), ("Andar", 3, ["34", "lado"], None))     # A3: perfil e 3/4 nos dois
for nome, rep, vs, dur in VIDEOS:
    f0, f1 = usar(nome, rep); f1 = f0 + dur - 1 if dur else f1; anima_tempo(f0, f1); sc.frame_start, sc.frame_end = f0, f1
    modo_chamas(nome != "Repouso")
    for v in vs:
        vista(v); sc.render.filepath = os.path.join(OUT, "Aura_%s_%s.mp4" % (nome, v)); bpy.ops.render.render(animation=True); print("VIDEO", nome, v, flush=True)
print("RENDER_AURA_OK", flush=True)
