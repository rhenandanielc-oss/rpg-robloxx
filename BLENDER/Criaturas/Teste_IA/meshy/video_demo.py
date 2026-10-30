"""Video de demonstracao do Drake5 (Silverwing): sequencia continua parado -> andar -> correr -> parada -> decolagem ->
voo -> curva -> planeio -> descida -> pairar -> pouso -> rugido, com transicoes cruzadas no NLA, deslocamento do
objeto casado com a passada medida nos pes (sem patinar), inclinacao/arfagem do corpo pelo movimento, camera de
cinema com atraso e cenario (ceu, montanhas com perspectiva aerea, rochas).
NAO salva sobre o .blend de origem (grava video_demo.blend na pasta de saida).
Uso: blender -b Silverwing_M2M.blend -P video_demo.py -- teste <saida> 1,100,200   |   final <saida>   |   mp4 <saida>"""
import bpy, sys, os, math, random, json
from mathutils import Vector, Matrix, Euler, noise

args = sys.argv[sys.argv.index("--") + 1:]
MODO, OUT = args[0], args[1]
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
FPS = 30; sc.render.fps = FPS
A = bpy.data.objects["Silverwing_Rig"]
ACT = lambda n: bpy.data.actions["Silverwing_" + n]

def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def curva(chaves, f):
    """interpolacao suave (smoothstep) entre chaves (quadro, valor)"""
    if f <= chaves[0][0]: return chaves[0][1]
    for (fa, va), (fb, vb) in zip(chaves, chaves[1:]):
        if f <= fb: return va + (vb - va) * suave((f - fa) / (fb - fa))
    return chaves[-1][1]

# ---------------------------------------------------------------- pes e velocidade real da passada
def pose_acao(act, f):
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]; sc.frame_set(f)

A.animation_data_create()
for t in list(A.animation_data.nla_tracks): A.animation_data.nla_tracks.remove(t)
A.location = (0, 0, 0); A.rotation_euler = (0, 0, 0)
pose_acao(ACT("Parado"), 1)
PES = [A.pose.bones[n] for n in ("front_toes_tip_l", "front_toes_tip_r", "back_toes_tip_l", "back_toes_tip_r")]

def vel_passada(act):
    f0, f1 = map(int, act.frame_range); traj = {pb.name: [] for pb in PES}
    for f in range(f0, f1 + 1):
        pose_acao(act, f)
        for pb in PES: traj[pb.name].append(A.matrix_world @ pb.head)
    vs = []
    for nome, ps in traj.items():
        zmin = min(p.z for p in ps)
        for a, b in zip(ps, ps[1:]):
            if a.z < zmin + 0.004 and b.z < zmin + 0.004: vs.append((b.y - a.y) * FPS)   # pe apoiado escorrega p/ +Y
    vs.sort(); return vs[len(vs) // 2] if vs else 0.0

V_ANDAR, V_CORRER = vel_passada(ACT("Andar")), vel_passada(ACT("Correr"))
pose_acao(ACT("Andar"), 1)
ZPE = {}
for f in range(1, 28):
    pose_acao(ACT("Andar"), f)
    for pb in PES: ZPE[pb.name] = min(ZPE.get(pb.name, 9), (A.matrix_world @ pb.head).z)
A.animation_data.action = None

# ---------------------------------------------------------------- roteiro (clipe, inicio, duracao, mistura, quadro inicial do clipe)
ROT = [("Parado", 1, 90, 0, 1), ("Andar", 80, 81, 12, 1), ("Correr", 150, 80, 10, 1), ("Parada", 224, 19, 6, 1),
       ("Parado", 240, 25, 6, 100), ("Decolagem", 258, 31, 7, 1), ("Voo", 283, 96, 6, 1), ("Curva_E", 369, 120, 12, 1),
       ("Planeio", 477, 100, 12, 1), ("Descida", 565, 75, 12, 1), ("Pairar", 628, 84, 12, 1),
       ("Parado", 696, 40, 14, 1), ("Rugido_Combate", 728, 79, 8, 1), ("Parado", 800, 54, 8, 140)]
# pouso: o Pairar desce e toca o chao na fase ALTA da batida (quadros locais 69-83); a transicao para o Parado
# recolhe as asas por cima (o clipe Pouso abre as asas 1,5x rente ao chao e elas varriam o terreno)
F_FIM = 852
sc.frame_start, sc.frame_end = 3, F_FIM        # comeca no 3: o desfoque de movimento do 1 amostra o quadro 0 (sem pose)
for i, (nome, ini, dur, mix, fa) in enumerate(ROT):
    act = ACT(nome); tr = A.animation_data.nla_tracks.new(); tr.name = "%02d_%s" % (i, nome)
    st = tr.strips.new(nome + str(i), ini, act)
    if hasattr(st, "action_slot") and len(act.slots): st.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); ciclo = f1 - f0
    laco = nome in ("Andar", "Correr", "Voo", "Pairar", "Planeio", "Descida", "Curva_E", "Parado")
    if laco and dur > ciclo - (fa - f0):
        st.action_frame_start, st.action_frame_end = f0, f1; st.repeat = dur / ciclo
    else:
        st.action_frame_start, st.action_frame_end = fa, min(f1, fa + dur); st.repeat = 1.0
    if nome == "Pouso": st.scale = dur / (f1 - f0)          # pouso mais lento: asas fecham antes de varrer o chao
    st.extrapolation = "NOTHING"; st.use_auto_blend = False; st.blend_in = mix; st.blend_type = "REPLACE"

# ---------------------------------------------------------------- trajetoria do corpo (velocidade, altura, guinada)
VEL = [(1, 0), (80, 0), (92, V_ANDAR), (150, V_ANDAR), (160, V_CORRER), (224, V_CORRER), (243, 0), (268, 0), (276, 1.0),
       (289, 2.4), (310, 3.2), (380, 3.5), (480, 3.6), (570, 3.2), (628, 1.8), (660, 0.6), (690, 0.15), (700, 0), (F_FIM, 0)]
ALT = [(1, 0), (268, 0), (274, 0.3), (282, 0.75), (295, 1.2), (320, 1.8), (380, 2.9), (470, 3.5), (577, 3.0), (630, 1.4), (660, 0.9), (688, 0.68), (697, 0.14), (708, 0), (F_FIM, 0)]
W = 200.0 / 90.0                                          # graus por quadro na curva (total ~200 graus)
GUI = [(1, 0), (372, 0), (392, W), (462, W), (482, 0), (520, 0), (540, -0.35), (600, -0.35), (620, 0), (F_FIM, 0)]
CENTRO = Vector((0, -0.15, 0.3))                          # giro de arfagem/rolagem em torno do tronco, nao dos pes
pos, yaw = Vector((0, 0, 0)), 0.0
traj = {}
for f in range(1, F_FIM + 1):
    v = curva(VEL, f); w = math.radians(curva(GUI, f)); yaw += w
    pos += Vector((math.sin(yaw), -math.cos(yaw), 0)) * v / FPS
    z = curva(ALT, f); vz = (curva(ALT, f + 1) - curva(ALT, f - 1)) * FPS / 2
    arf = max(-0.3, min(0.3, math.atan2(vz, max(v, 0.6)) * 0.7)) if z > 0.05 else 0.0
    rol = max(-0.55, min(0.55, 0.12 * v * w * FPS)) if z > 0.3 else 0.0
    traj[f] = [Vector((pos.x, pos.y, z)), yaw, arf, rol]
# suaviza arfagem/rolagem (o corpo tem inercia)
for k in (2, 3):
    acc = 0.0
    for f in range(1, F_FIM + 1): acc += (traj[f][k] - acc) * (1 - math.exp(-1 / (0.25 * FPS))); traj[f][k] = acc
A.rotation_mode = "YXZ"
A.animation_data.action = None
mov = bpy.data.actions.new("Video_Movimento"); A.animation_data.action = mov
def chavear(f):
    p, y_, a_, r_ = traj[f]
    R = Euler((-a_, r_, y_), "YXZ").to_matrix()
    c_mundo = p + Matrix.Rotation(y_, 3, "Z") @ CENTRO
    A.location = c_mundo - R @ CENTRO; A.rotation_euler = Euler((-a_, r_, y_), "YXZ")
    A.keyframe_insert("location", frame=f); A.keyframe_insert("rotation_euler", frame=f)
for f in range(1, F_FIM + 1): chavear(f)
if hasattr(A.animation_data, "action_slot") and len(mov.slots): A.animation_data.action_slot = mov.slots[0]
# folga do solo: no trecho aereo, ergue o corpo o minimo para que nenhuma ponta de asa/dedo atravesse o chao
PONTAS_ASA = [b.name for b in A.data.bones if b.name.startswith("wing") and not b.children]
AR0, AR1 = 262, 712
falta = {}
for f in range(AR0, AR1 + 1):
    sc.frame_set(f)
    falta[f] = max(0.0, 0.07 - min((A.matrix_world @ A.pose.bones[n].head).z for n in PONTAS_ASA))
ergue = {f: max(falta[g] for g in range(max(AR0, f - 5), min(AR1, f + 5) + 1)) for f in falta}
for _ in range(2):
    ergue = {f: sum(ergue[g] for g in range(max(AR0, f - 4), min(AR1, f + 4) + 1)) / (min(AR1, f + 4) - max(AR0, f - 4) + 1) * 1.08 for f in ergue}
for f, e in ergue.items():
    if e > 0.001: traj[f][0].z += e; chavear(f)
print("VIDEO_FOLGA max %.2f em %d" % max((e, f) for f, e in ergue.items()))
# o NLA avalia por cima da acao ativa; a acao ativa so tem location/rotacao do objeto, entao convivem
A.animation_data.action_blend_type = "REPLACE"; A.animation_data.action_influence = 1.0
POUSO = traj[F_FIM][0]

# ---------------------------------------------------------------- cenario
for o in ("chao_revisao", "cam_rev", "sol"):
    ob = bpy.data.objects.get(o)
    if ob: bpy.data.objects.remove(ob, do_unlink=True)

def no(nt, tipo, **kw):
    n = nt.nodes.new(tipo)
    for k, v in kw.items(): setattr(n, k, v)
    return n

def mat_terreno():
    m = bpy.data.materials.new("Video_Terreno"); m.use_nodes = True; nt = m.node_tree; L = nt.links
    bsdf = nt.nodes["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.92
    geo = no(nt, "ShaderNodeNewGeometry"); sep = no(nt, "ShaderNodeSeparateXYZ"); L.new(geo.outputs["Position"], sep.inputs[0])
    sepn = no(nt, "ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sepn.inputs[0])
    tc = no(nt, "ShaderNodeTexCoord")
    n1 = no(nt, "ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.35; n1.inputs["Detail"].default_value = 8
    n2 = no(nt, "ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 6.0; n2.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], n1.inputs["Vector"]); L.new(tc.outputs["Object"], n2.inputs["Vector"])
    # grama seca / verde
    rg = no(nt, "ShaderNodeValToRGB"); L.new(n1.outputs["Fac"], rg.inputs[0])
    rg.color_ramp.elements[0].position = 0.38; rg.color_ramp.elements[0].color = (0.10, 0.16, 0.045, 1)
    rg.color_ramp.elements[1].position = 0.66; rg.color_ramp.elements[1].color = (0.30, 0.27, 0.10, 1)
    mixd = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); mixd.inputs["Factor"].default_value = 0.5
    rgd = no(nt, "ShaderNodeValToRGB"); L.new(n2.outputs["Fac"], rgd.inputs[0])
    rgd.color_ramp.elements[0].color = (0.55, 0.55, 0.5, 1); rgd.color_ramp.elements[1].color = (1.15, 1.1, 1.0, 1)
    L.new(rg.outputs["Color"], mixd.inputs[6]); L.new(rgd.outputs["Color"], mixd.inputs[7])
    # rocha nas encostas
    inc = no(nt, "ShaderNodeMapRange"); inc.inputs[1].default_value = 0.82; inc.inputs[2].default_value = 0.68
    L.new(sepn.outputs["Z"], inc.inputs[0])
    rocha = no(nt, "ShaderNodeMix", data_type="RGBA"); L.new(inc.outputs[0], rocha.inputs["Factor"])
    L.new(mixd.outputs[2], rocha.inputs[6]); rocha.inputs[7].default_value = (0.26, 0.24, 0.22, 1)
    # neve nos picos
    alt = no(nt, "ShaderNodeMapRange"); alt.inputs[1].default_value = 38; alt.inputs[2].default_value = 46
    L.new(sep.outputs["Z"], alt.inputs[0])
    neve = no(nt, "ShaderNodeMix", data_type="RGBA"); L.new(alt.outputs[0], neve.inputs["Factor"])
    L.new(rocha.outputs[2], neve.inputs[6]); neve.inputs[7].default_value = (0.85, 0.87, 0.9, 1)
    # perspectiva aerea: longe tende a cor do ceu
    cam = no(nt, "ShaderNodeCameraData"); nev = no(nt, "ShaderNodeMapRange")
    nev.inputs[1].default_value = 25; nev.inputs[2].default_value = 420; nev.inputs[4].default_value = 0.78
    L.new(cam.outputs["View Distance"], nev.inputs[0])
    nebl = no(nt, "ShaderNodeMix", data_type="RGBA"); L.new(nev.outputs[0], nebl.inputs["Factor"])
    L.new(neve.outputs[2], nebl.inputs[6]); nebl.inputs[7].default_value = (0.55, 0.66, 0.80, 1)
    L.new(nebl.outputs[2], bsdf.inputs["Base Color"])
    em = nev.outputs[0]; L.new(nebl.outputs[2], bsdf.inputs["Emission Color"]); L.new(em, bsdf.inputs["Emission Strength"])
    bmp = no(nt, "ShaderNodeBump"); bmp.inputs["Strength"].default_value = 0.35; L.new(n2.outputs["Fac"], bmp.inputs["Height"])
    L.new(bmp.outputs[0], bsdf.inputs["Normal"])
    return m

def terreno():
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=320, y_subdivisions=320, size=900, location=(POUSO.x * 0.5, POUSO.y * 0.5, 0))
    ob = bpy.context.object; ob.name = "Video_Terreno"; me = ob.data
    cx, cy = POUSO.x * 0.5, POUSO.y * 0.5
    pontos_chao = [traj[f][0] for f in range(1, F_FIM + 1, 10) if traj[f][0].z < 0.01]
    for v in me.vertices:
        x, y = v.co.x + cx, v.co.y + cy; r = math.hypot(x - cx, y - cy)
        dmin = min(math.hypot(x - p.x, y - p.y) for p in pontos_chao[::3])
        plano = suave((dmin - 6) / 30)                     # perto do caminho a pe: chao plano
        ondula = noise.fractal(Vector((x * 0.03, y * 0.03, 0)), 0.5, 2.0, 4) * 0.8 * plano
        monte = noise.hetero_terrain(Vector((x * 0.006, y * 0.006, 0.3)), 0.8, 2.1, 6, 0.4) * 34 * suave((r - 90) / 160)
        v.co.z = ondula + max(0.0, monte)
    for p in me.polygons: p.use_smooth = True
    me.materials.append(mat_terreno()); return ob

def rochas():
    m = bpy.data.materials.new("Video_Rocha"); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.85
    tx = no(nt, "ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = 3.0; tx.inputs["Detail"].default_value = 10
    rg = no(nt, "ShaderNodeValToRGB"); nt.links.new(tx.outputs["Fac"], rg.inputs[0])
    rg.color_ramp.elements[0].color = (0.13, 0.12, 0.11, 1); rg.color_ramp.elements[1].color = (0.42, 0.40, 0.36, 1)
    nt.links.new(rg.outputs["Color"], b.inputs["Base Color"])
    bm = no(nt, "ShaderNodeBump"); bm.inputs["Strength"].default_value = 0.6; nt.links.new(tx.outputs["Fac"], bm.inputs["Height"])
    nt.links.new(bm.outputs[0], b.inputs["Normal"])
    rnd = random.Random(7); pontos = [traj[f][0] for f in range(1, F_FIM + 1, 4)]
    base = None; n = 0
    while n < 70:
        ang, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(3, 70)
        x, y = POUSO.x * 0.5 + math.cos(ang) * r, POUSO.y * 0.5 + math.sin(ang) * r
        if min(math.hypot(x - p.x, y - p.y) for p in pontos if p.z < 0.5) < 2.2: continue
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1)
        ob = bpy.context.object; ob.name = "Video_Rocha_%02d" % n
        s = rnd.uniform(0.12, 0.9) * (1.6 if r > 30 else 1.0)
        for v in ob.data.vertices:
            v.co *= 1 + 0.35 * noise.fractal(v.co * 1.3 + Vector((n, 0, 0)), 0.6, 2.0, 4)
        ob.scale = (s * rnd.uniform(0.8, 1.4), s * rnd.uniform(0.8, 1.4), s * rnd.uniform(0.45, 0.8))
        ob.rotation_euler = (0, 0, rnd.uniform(0, 6.3)); ob.location = (x, y, -s * 0.2)
        for p in ob.data.polygons: p.use_smooth = True
        ob.data.materials.append(m); n += 1

def mundo():
    w = bpy.data.worlds.new("Video_Ceu"); sc.world = w; w.use_nodes = True; nt = w.node_tree
    bg = nt.nodes["Background"]; ceu = nt.nodes.new("ShaderNodeTexSky")
    for t in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA", "HOSEK_WILKIE", "PREETHAM"):
        try: ceu.sky_type = t; break
        except Exception: pass
    for k, v in (("sun_elevation", math.radians(22)), ("sun_rotation", math.radians(215)), ("altitude", 300), ("air_density", 1.2),
                 ("dust_density", 2.5), ("sun_intensity", 0.35)):
        if hasattr(ceu, k): setattr(ceu, k, v)
    nt.links.new(ceu.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.22
    sol = bpy.data.lights.new("Video_Sol", "SUN"); sol.energy = 4.2; sol.color = (1.0, 0.86, 0.68); sol.angle = math.radians(1.5)
    so = bpy.data.objects.new("Video_Sol", sol); sc.collection.objects.link(so)
    so.rotation_euler = Euler((math.radians(90 - 22), 0, math.radians(215 - 180 + 90)), "XYZ")
    pre = bpy.data.lights.new("Video_Preenchimento", "SUN"); pre.energy = 0.6; pre.color = (0.62, 0.74, 1.0)
    po = bpy.data.objects.new("Video_Preenchimento", pre); sc.collection.objects.link(po)
    po.rotation_euler = Euler((math.radians(55), 0, math.radians(20)), "XYZ")
    if hasattr(sol, "use_contact_shadow"): sol.use_contact_shadow = True

terreno(); rochas(); mundo()

# ---------------------------------------------------------------- camera de cinema (atraso critico + enquadramentos)
camd = bpy.data.cameras.new("Video_Cam"); cam = bpy.data.objects.new("Video_Cam", camd); sc.collection.objects.link(cam); sc.camera = cam
camd.clip_start = 0.05; camd.clip_end = 2000; camd.sensor_width = 36
OFS = [(1, (1.5, -2.3, 0.28)), (70, (2.1, -1.1, 0.42)), (110, (2.6, -0.9, 0.55)), (215, (2.4, -1.2, 0.5)),
       (250, (2.3, -2.6, 0.22)), (290, (2.6, -1.6, 0.25)), (330, (4.2, 3.0, 0.7)), (395, (-4.4, 0.8, -0.6)),
       (470, (-4.2, -0.8, -0.2)), (520, (4.6, -2.2, 0.25)), (610, (4.0, -3.2, 0.5)), (690, (2.8, -3.0, 0.45)),
       (740, (1.6, -2.4, 0.38)), (F_FIM, (1.15, -1.9, 0.33))]
LENTE = [(1, 52), (90, 45), (250, 38), (330, 34), (520, 38), (660, 45), (F_FIM, 55)]
def ofs(f):
    for (fa, va), (fb, vb) in zip(OFS, OFS[1:]):
        if f <= fb: k = suave((f - fa) / (fb - fa)); return Vector(va).lerp(Vector(vb), k)
    return Vector(OFS[-1][1])
alvo_f = cpos_f = None; yaw_f = 0.0
cam.rotation_mode = "QUATERNION"
for f in range(1, F_FIM + 1):
    p, y_, _, _ = traj[f]; centro = p + Matrix.Rotation(y_, 3, "Z") @ CENTRO
    lead = (traj[min(F_FIM, f + 8)][0] - p) * 0.6                              # olha um pouco a frente do movimento
    a = 1 - math.exp(-1 / (0.14 * FPS)); b = 1 - math.exp(-1 / (0.30 * FPS)); c = 1 - math.exp(-1 / (0.55 * FPS))
    alvo_f = centro + lead if alvo_f is None else alvo_f.lerp(centro + lead, a)
    cpos_f = centro if cpos_f is None else cpos_f.lerp(centro, b)
    yaw_f += (y_ - yaw_f) * (c if f > 1 else 1)
    cp = cpos_f + Matrix.Rotation(yaw_f, 3, "Z") @ ofs(f)
    cp.z = max(cp.z, 0.12)
    cam.location = cp; cam.rotation_quaternion = (alvo_f - cp).to_track_quat("-Z", "Y")
    camd.lens = curva(LENTE, f)
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_quaternion", frame=f); camd.keyframe_insert("lens", frame=f)

# ---------------------------------------------------------------- render
sc.render.engine = "BLENDER_EEVEE"
ee = sc.eevee
for k, v in (("taa_render_samples", 48), ("use_raytracing", True), ("use_shadows", True), ("shadow_ray_count", 2),
             ("shadow_step_count", 8), ("use_gtao", True), ("gtao_distance", 0.4)):
    if hasattr(ee, k): setattr(ee, k, v)
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.45
if hasattr(ee, "motion_blur_steps"): ee.motion_blur_steps = 1
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.view_settings.exposure = 0.0
sc.render.film_transparent = False

# relatorio: escorregamento dos pes no chao (m/s) nos trechos a pe
def escorrega(fa, fb):
    ult = {}; vs = []
    for f in range(fa, fb):
        sc.frame_set(f)
        for pb in PES:
            t = A.matrix_world @ pb.head
            if pb.name in ult and t.z < ZPE[pb.name] + 0.004 and ult[pb.name].z < ZPE[pb.name] + 0.004:
                vs.append(((t - ult[pb.name]).xy.length) * FPS)
            ult[pb.name] = t
    vs.sort(); return (round(vs[len(vs) // 2], 3), round(vs[int(len(vs) * 0.9)], 3)) if vs else None
rel = {"V_ANDAR": round(V_ANDAR, 4), "V_CORRER": round(V_CORRER, 4), "pes": [p.name for p in PES],
       "pouso": tuple(round(c, 2) for c in POUSO)}
if MODO == "teste":
    rel["escorrega_andar(med,p90)"] = escorrega(95, 148); rel["escorrega_correr"] = escorrega(162, 222)
    rel["escorrega_rugido"] = escorrega(690, 780)
print("VIDEO_REL" + json.dumps(rel))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "video_demo.blend"), copy=True)

if MODO == "teste":
    sc.render.resolution_x, sc.render.resolution_y = 960, 540; ee.taa_render_samples = 16
    for f in map(int, args[2].split(",")):
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, "teste_%04d.png" % f)
        bpy.ops.render.render(write_still=True)
elif MODO == "final":
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.image_settings.file_format = "PNG"; sc.render.use_overwrite = False; sc.render.use_placeholder = True
    sc.render.filepath = os.path.join(OUT, "quadros", "f_")
    bpy.ops.render.render(animation=True)
print("VIDEO_OK")
