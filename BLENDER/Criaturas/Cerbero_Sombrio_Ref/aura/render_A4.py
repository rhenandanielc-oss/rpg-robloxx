"""Render de comparacao das auras (A3 aceita x A4) com LUZ e ENQUADRAMENTO iguais. Serve para os dois .blend.
Modo leve (PC compartilhado): 2 threads, EEVEE 8 amostras, pausa entre quadros.
Uso: blender -b -t 2 <CR_Cerbero_Fogo_A3|A4.blend> -P render_A4.py -- <saida> <rotulo> quadros|videos [luz=noite,dia] [furia]
  quadros: Repouso em 3 instantes + Corrida (quadro do meio) nas vistas 34/lado/frente/cab, noite e dia
  videos : Repouso (corpo 34 + cabecas) e Corrida (corpo 34 + perfil + cabecas), noite; com 'furia', Repouso 34 violeta"""
import bpy, sys, os, math, time
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]
OUT, ROT, MODO = os.path.abspath(A[0]), A[1], A[2]; os.makedirs(OUT, exist_ok=True)
LUZ = next((a.split("=")[1].split(",") for a in A if a.startswith("luz=")), ["noite", "dia"])
FURIA = "furia" in A
VS_SO = next((a.split("=")[1].split(",") for a in A if a.startswith("vs=")), None)
QS = [int(x) for x in next((a.split("=")[1].split(",") for a in A if a.startswith("qs=")), ["20", "47", "81"])]
SEM_CORRIDA = "sem_corrida" in A
LENTO = "lento" in A          # 20/11 pedido do usuario: o mais leve possivel, mesmo demorando -> ultra + pausa 4 s por quadro
ULTRA = "ultra" in A or LENTO # 20/11: PC travando -> 1 thread, 4 amostras, imagem menor, pausa 1,5 s, video a 15 qps (velocidade normal)
sc = bpy.context.scene; sc.render.fps = 30; sc.render.threads_mode = "FIXED"; sc.render.threads = 1 if ULTRA else 2
bpy.app.handlers.render_post.append(lambda *_: time.sleep(4.0 if LENTO else (1.5 if ULTRA else 0.5)))
rig = bpy.data.objects["Cerbero_Rig"]
for o in list(sc.objects):
    if o.type == "CAMERA" or (o.type == "LIGHT" and not o.name.startswith("Luz_")) or o.name.startswith(("IK_", "Polo_")): o.hide_render = True
for k in ("inclina", "inclina_atraso", "violeta"):
    if k not in sc.keys(): sc[k] = 0.0
MATS = [m for m in bpy.data.materials if m.node_tree and "tempo" in m.node_tree.nodes]
w = bpy.data.worlds.new("Mundo"); sc.world = w; w.use_nodes = True; BG = w.node_tree.nodes["Background"]
SOIS = []
for nome, rot in (("Sol1", (0.9, 0, -0.7)), ("Sol2", (2.2, 0, 2.6))):
    l = bpy.data.lights.new(nome, "SUN"); lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot; SOIS.append(l)
def luz(modo):
    if modo == "noite":
        BG.inputs[0].default_value = (0.05, 0.045, 0.06, 1); BG.inputs[1].default_value = 1.0
        SOIS[0].energy, SOIS[0].color = 1.2, (0.75, 0.75, 0.9); SOIS[1].energy, SOIS[1].color = 0.8, (0.9, 0.5, 0.45)
    else:
        BG.inputs[0].default_value = (0.55, 0.62, 0.75, 1); BG.inputs[1].default_value = 1.0
        SOIS[0].energy, SOIS[0].color = 4.0, (1.0, 0.96, 0.9); SOIS[1].energy, SOIS[1].color = 1.0, (0.8, 0.85, 1.0)
bpy.ops.mesh.primitive_plane_add(size=300); ch = bpy.context.object; mch = bpy.data.materials.new("Chao"); mch.use_nodes = True
mch.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.06, 0.055, 0.06, 1); ch.data.materials.append(mch)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 4 if ULTRA else 8; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
VISTAS = {"34": ((-30, -32, 19), (0, -1, 9), 50), "cab": ((-6, -32, 18), (0, -8, 14.5), 55), "lado": ((-44, 0, 9), (0, 0, 8.5), 50),
          "frente": ((0, -46, 12), (0, -2, 9.5), 50)}
ALVO = bpy.data.objects.get("AlvoCamera")
CHAMAS_A3 = [o for o in bpy.data.objects if "rot_repouso" in o.keys() and "rot_andar" in o.keys()]
def vista(n):
    pos, alvo, lente = VISTAS[n]; cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
    if ALVO: ALVO.location = pos
def usar(nome, rep):
    a = bpy.data.actions["Cerbero_" + nome]; f0, f1 = int(a.frame_range[0]), int(a.frame_range[1]); n = f1 - f0 + 1
    if not rig.animation_data: rig.animation_data_create()
    rig.animation_data.action = None
    for tr in list(rig.animation_data.nla_tracks): rig.animation_data.nla_tracks.remove(tr)
    st = rig.animation_data.nla_tracks.new().strips.new(nome, f0, a); st.repeat = rep
    return f0, f0 + n * rep - 1
def fcurves(idb):
    a = idb.animation_data.action
    return getattr(a, "fcurves", None) or [fc for ly in a.layers for st in ly.strips for cb in st.channelbags for fc in cb.fcurves]
def anima_tempo(f0, f1):
    for mat in MATS:
        nt = mat.node_tree; tempo = nt.nodes["tempo"].outputs[0]
        if nt.animation_data: nt.animation_data_clear()
        tempo.default_value = 0.0; tempo.keyframe_insert("default_value", frame=f0)
        tempo.default_value = (f1 - f0) / 30; tempo.keyframe_insert("default_value", frame=f1)
        for fc in fcurves(nt):
            for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
def anima_inclina(f0, f1, correndo):
    if sc.animation_data: sc.animation_data_clear()
    for k, atraso in (("inclina", 0.0), ("inclina_atraso", 0.25)):
        sc[k] = 0.0; sc.keyframe_insert('["%s"]' % k, frame=f0)
        sc[k] = 0.0 if not correndo else 0.0; sc.keyframe_insert('["%s"]' % k, frame=f0 + int(atraso * 30))
        sc[k] = 1.0 if correndo else 0.0; sc.keyframe_insert('["%s"]' % k, frame=f0 + int((0.45 + atraso) * 30))
    for o in CHAMAS_A3: o.rotation_euler = o["rot_andar"] if correndo else o["rot_repouso"]   # A3: chave fixa (como na A3 aceita)
def set_violeta(v):
    sc["violeta"] = float(v)
    for o in CHAMAS_A3:
        if "violeta" in o.keys(): o["violeta"] = float(v)
existe = lambda n: ("Cerbero_" + n) in bpy.data.actions
CORRE = "Corrida" if existe("Corrida") else "Andar"
if MODO == "quadros":
    sc.render.resolution_x, sc.render.resolution_y = (520, 370) if ULTRA else (760, 540)
    for lz in LUZ:
        luz(lz)
        f0, f1 = usar("Repouso", 1); anima_tempo(f0, f0 + 240); anima_inclina(f0, f0 + 240, False)
        for q in QS:
            sc.frame_set(f0 + q)
            for v in [x for x in ("34", "lado", "frente", "cab") if VS_SO is None or x in VS_SO]:
                vista(v); sc.render.filepath = os.path.join(OUT, "%s_%s_repouso_%s_q%02d.png" % (ROT, lz, v, q)); bpy.ops.render.render(write_still=True)
        f0, f1 = usar(CORRE, 6); anima_tempo(f0, f1); anima_inclina(f0, f1, True)
        sc.frame_set(f0 + 40)
        for v in ([] if SEM_CORRIDA else [x for x in ("34", "lado") if VS_SO is None or x in VS_SO]):
            vista(v); sc.render.filepath = os.path.join(OUT, "%s_%s_corrida_%s.png" % (ROT, lz, v)); bpy.ops.render.render(write_still=True)
        if FURIA:
            set_violeta(1); f0, f1 = usar("Repouso", 1); anima_tempo(f0, f0 + 240); anima_inclina(f0, f0 + 240, False); sc.frame_set(f0 + 47)
            for v in ("34", "cab"):
                vista(v); sc.render.filepath = os.path.join(OUT, "%s_%s_furia_%s.png" % (ROT, lz, v)); bpy.ops.render.render(write_still=True)
            set_violeta(0)
        print("QUADROS", lz, flush=True)
else:
    sc.render.image_settings.media_type = "VIDEO"; sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"; sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
    sc.render.resolution_x, sc.render.resolution_y = (420, 300) if ULTRA else (560, 400); luz(LUZ[0])
    if ULTRA: sc.frame_step = 2; sc.render.fps = 15
    LISTA = [("Repouso", 1, False, 120, ["34", "cab"]), (CORRE, 6, True, 120, ["34", "lado", "cab"])]
    if ULTRA: LISTA = [("Repouso", 1, False, 90, ["34", "cab"]), (CORRE, 6, True, 90, ["34", "cab"])]
    if FURIA: LISTA = [("Repouso", 1, False, 90 if ULTRA else 120, ["34"])]
    if FURIA: set_violeta(1)
    SO = next((a.split("=")[1] for a in A if a.startswith("so=")), None)   # so=<clipe>:<vista> renderiza um unico video
    if SO: LISTA = [(n, r, c, d, [SO.split(":")[1]]) for n, r, c, d, vs in LISTA if n == SO.split(":")[0] and SO.split(":")[1] in vs]
    for nome, rep, correndo, dur, vs in LISTA:
        f0, f1 = usar(nome, rep); f1 = f0 + dur - 1; anima_tempo(f0, f1); anima_inclina(f0, f1, correndo); sc.frame_start, sc.frame_end = f0, f1
        for v in vs:
            vista(v); sc.render.filepath = os.path.join(OUT, "%s_%s%s_%s_%s.mp4" % (ROT, nome, "_furia" if FURIA else "", LUZ[0], v))
            bpy.ops.render.render(animation=True); print("VIDEO", nome, v, flush=True)
print("RENDER_A4_OK", flush=True)
