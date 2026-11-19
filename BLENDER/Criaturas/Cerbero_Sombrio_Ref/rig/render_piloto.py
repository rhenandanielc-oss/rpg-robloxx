"""Renders de revisao dos clipes (piloto 17/11): videos em velocidade normal (MP4, 30 fps, loops repetidos) e quadros de
contato (PNG) do Cerbero; com --lobo, so os quadros do Lobo Artico (anim_v41, so leitura) no mesmo enquadramento relativo.
Uso: blender -b -t 4 CR_Cerbero_Anim.blend -P render_piloto.py -- <saida_dir> [video=1]
     blender -b -t 4 <Lobo_Artico_Ref/anim_v41/CR_LoboArtico_Anim.blend> -P render_piloto.py -- <saida_dir> lobo"""
import bpy, sys, os, math
from mathutils import Vector as V
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
LOBO = "lobo" in ARGS; VIDEO = "video=0" not in ARGS and not LOBO; CONTATO = "contato=0" not in ARGS
sc = bpy.context.scene; sc.render.fps = 30
sc.render.threads_mode = "FIXED"; sc.render.threads = 4
arm = next(o for o in sc.objects if o.type == "ARMATURE")
for o in list(sc.objects):
    if o.type in ("CAMERA", "LIGHT") or o.name.startswith(("LOD1", "LOD2", "IK_", "Polo_")): o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True                  # as acoes ja sao FK assadas
malhas = [o for o in sc.objects if o.type == "MESH" and not o.hide_render]
H = max((o.matrix_world @ V(c)).z for o in malhas for c in o.bound_box); k_ = H / 19.63   # enquadramento relativo ao tamanho
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.42, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
for nome, en, rot in (("K", 3.2, (0.84, 0, -0.61)), ("Rr", 2.0, (2.1, 0, 2.8)), ("F", 1.2, (1.13, 0, 1.92))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=400); ch = bpy.context.object; mc = bpy.data.materials.new("Chao"); mc.use_nodes = True
mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1); ch.data.materials.append(mc)
# grade no chao a cada 2 studs (escala do Cerbero) para ver o apoio
for i in range(-20, 21):
    for eixo in (0, 1):
        bpy.ops.mesh.primitive_cube_add(size=1); g = bpy.context.object
        g.scale = (0.03 * k_, 80 * k_, 0.005) if eixo == 0 else (80 * k_, 0.03 * k_, 0.005)
        g.location = ((i * 2 * k_, 0, 0.003) if eixo == 0 else (0, i * 2 * k_, 0.003)); g.data.materials.append(mc); g.color = (0.2, 0.2, 0.2, 1)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 12; sc.view_settings.view_transform = "AgX"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
VISTAS = {"frente": ((0, -46, 12), (0, 0, 10), 50), "cabf": ((0, -34, 18), (0, -8, 14.5), 55), "cima": ((0, 0.01, 60), (0, 0, 0), 40), "lado": ((-46, 0, 9), (0, 0, 8.5), 50), "34": ((-32, -34, 20), (0, -1, 8.5), 50), "cab": ((-10, -30, 20), (0, -9, 14.5), 60),
          "perfilcab": ((-52, -13, 15), (0, -13, 12.5), 45)}   # r4: perfil das cabecas
def vista(n):
    pos, alvo, lente = VISTAS[n]; pos, alvo = V(pos) * k_, V(alvo) * k_
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
def acao(nome):
    a = bpy.data.actions.get(nome) or bpy.data.actions.get("Cerbero_" + nome)
    if not arm.animation_data: arm.animation_data_create()
    for tr in list(arm.animation_data.nla_tracks): arm.animation_data.nla_tracks.remove(tr)
    arm.animation_data.action = a; return a
QUADROS_CONTATO = {"Andar": ("lado", [0, 6, 12, 18, 24, 30]), "Corrida": ("lado", [0, 2, 4, 6, 8, 10, 12, 14]),
                   "Mordida": ("cab", [0, 9, 13, 17, 33]), "Repouso": ("34", [0, 30, 75, 120, 150]),
                   # lote 2A (17/11)
                   "Trote": ("lado", [0, 3, 6, 9, 12, 15]), "Partida": ("lado", [0, 6, 11, 18, 26, 34, 44, 59]),
                   "Freada": ("lado", [0, 6, 12, 18, 24, 30, 38, 45]), "VirarE": ("cima", [0, 9, 18, 27]), "VirarD": ("cima", [0, 9, 18, 27]),
                   "Salto": ("lado", [0, 10, 13, 17, 21, 25, 29, 33, 38, 45]),
                   # lote 2B (17/11)
                   "Alerta": ("34", [0, 8, 16, 40, 72]), "Observar": ("34", [0, 30, 60, 95, 132]), "ReacaoGolpe": ("34", [0, 3, 6, 12, 30]),
                   "Deitar": ("lado", [0, 15, 30, 45, 60, 78]), "Descanso": ("34", [0, 45, 90, 135]), "Levantar": ("lado", [0, 13, 26, 40, 53, 66]),
                   # lote 3 (18/11): quadros dos EVENTOS
                   "ChamasTriplices": ("cabf", [0, 13, 21, 28, 48]), "FuriaRugido": ("cabf", [0, 8, 15, 23, 48]), "FuriaLoop": ("cabf", [0, 9, 28, 46]),
                   "Investida": ("lado", [0, 6, 9, 13, 18, 24, 33, 41]), "MordidaC": ("cabf", [0, 6, 9, 24]), "MordidaE": ("cabf", [6, 9]),
                   "MordidaD": ("cabf", [6, 9]), "GarraE": ("34", [0, 5, 10, 22]), "GarraD": ("34", [5, 10]),
                   # r4 (18/11): Rugido Infernal separado (inicio, boca maxima de C/E/D, fim) de frente e de perfil
                   "FuriaRugidoR4": ("cabf", [0, 8, 16, 37, 58, 87]), "FuriaRugidoR4@perfilcab": ("perfilcab", [0, 8, 16, 37, 58, 87]),
                   "BolaInfernal": ("cabf", [0, 11, 36, 39, 47, 66])}
LOBO_MAP = {"Deitar": "Deitar", "Descanso": "Descanso", "Levantar": "LevantarDeitado", "Trote": "Trote", "Partida": "Arrancada", "Freada": "Frenagem", "Andar": "Andar", "Corrida": "Corrida"}
CLIPES_SEL = next((a.split("=")[1].split(",") for a in ARGS if a.startswith("clipes=")), None)
sc.render.resolution_x, sc.render.resolution_y = (560, 400)
for nome, (vn, qs) in (QUADROS_CONTATO.items() if CONTATO else []):
    if CLIPES_SEL and nome.split("@")[0] not in CLIPES_SEL: continue
    if LOBO and nome not in LOBO_MAP: continue
    nome_v = nome; nome = nome.split("@")[0]
    a = acao(LOBO_MAP[nome] if LOBO else nome)
    if a is None: print("SEM_ACAO", nome); continue
    f0 = int(a.frame_range[0]); vista(vn)
    for q in qs:
        sc.frame_set(f0 + q); sc.render.filepath = os.path.join(OUT, "%s_%s_%s_q%02d.png" % ("lobo" if LOBO else "cerbero", nome, vn, q)) if "@" in nome_v or nome.endswith("R4") else os.path.join(OUT, "%s_%s_q%02d.png" % ("lobo" if LOBO else "cerbero", nome, q))
        bpy.ops.render.render(write_still=True)
print("CONTATO_OK", flush=True)
if VIDEO:
    sc.render.image_settings.media_type = "VIDEO"                      # Blender 5.x: video e um media_type
    sc.render.image_settings.file_format = "FFMPEG"; sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"
    sc.render.ffmpeg.constant_rate_factor = "MEDIUM"; sc.render.resolution_x, sc.render.resolution_y = (640, 400)
    for nome, vns, rep in (("Repouso", ["34"], 1), ("Andar", ["lado", "34"], 3), ("Corrida", ["lado", "34"], 4), ("Mordida", ["cab", "34"], 1),
                           ("Trote", ["lado", "34"], 4), ("Partida", ["lado"], 1), ("Freada", ["lado"], 1), ("VirarE", ["cima", "34"], 3),
                           ("VirarD", ["cima", "34"], 3), ("Salto", ["lado", "34"], 1),
                           ("Alerta", ["34"], 1), ("Observar", ["34"], 1), ("ReacaoGolpe", ["34"], 1), ("Deitar", ["lado", "34"], 1),
                           ("Descanso", ["34"], 1), ("Levantar", ["lado", "34"], 1),
                           ("Prev_MordidaC_Andar", ["lado", "34"], 1), ("Prev_MordidaE_Corrida", ["lado"], 1), ("Prev_GarraE_Andar", ["lado", "34"], 1),
                           ("Prev_GarraD_Trote", ["34"], 1), ("Prev_Chamas_Repouso", ["cabf", "34"], 1), ("Prev_Chamas_Andar", ["34"], 1),
                           ("Investida", ["lado", "34"], 1), ("Prev_Furia_Andar", ["frente", "34"], 1),
                           ("FuriaRugidoR4", ["cabf", "perfilcab"], 1), ("Prev_FuriaR4", ["cabf", "perfilcab"], 1),
                           ("Prev_Bola_Repouso", ["cabf", "34"], 1), ("Prev_Bola_Andar", ["lado", "34"], 1)):
        if CLIPES_SEL and nome not in CLIPES_SEL: continue
        a = acao(nome); f0, f1 = int(a.frame_range[0]), int(a.frame_range[1]); n = f1 - f0 + 1
        if a.get("loop"):                                     # loop: chave extra em f1+1 = quadro f0, e a faixa NLA repete
            fcs = list(getattr(a, "fcurves", None) or [fc for ly in a.layers for st in ly.strips for cb in st.channelbags for fc in cb.fcurves])
            for fc in fcs: fc.keyframe_points.insert(f1 + 1, fc.evaluate(f0))
            arm.animation_data.action = None
            for tr in list(arm.animation_data.nla_tracks): arm.animation_data.nla_tracks.remove(tr)
            st = arm.animation_data.nla_tracks.new().strips.new(nome, f0, a); st.action_frame_start = f0; st.action_frame_end = f1 + 1
            st.repeat = rep; st.frame_end = f0 + n * rep
        sc.frame_start = f0; sc.frame_end = f0 + n * rep - 1 + (15 if not a.get("loop") else 0)
        for vn in vns:
            vista(vn); sc.render.filepath = os.path.join(OUT, "Cerbero_%s_%s.mp4" % (nome, vn)); bpy.ops.render.render(animation=True)
            print("VIDEO", nome, vn, flush=True)
print("RENDER_OK", flush=True)
