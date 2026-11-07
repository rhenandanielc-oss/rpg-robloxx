"""Previa em video das DUAS ENTRADAS de montar (06/11, usuario: "Prefiro a animacao de pulo. E por tras pulando pela
cauda. Deve ser disponivel montar somente por tras e na frente das asas"). Reproduz o AnimCavaleiro do jogo:
  ENTRADA=frente -> M.subir: agacha, salta, agarra a sela, passa a perna, senta (vindo da frente do peito);
  ENTRADA=tras   -> M.subirCauda: agacha, salta na cauda deitada, corre por ela ate o quadril e senta por tras.
Dragao: Abaixar -> Abaixado -> Levantar (asas abertas, sem dobra). Pontos de entrada iguais aos do servidor
(frente = spine_3 + 4 studs a frente, no chao; tras = cauda (tail_3) - 1 stud, no chao). Poses lidas do .luau.
Uso: ENTRADA=frente|tras VISTA=lado|alto blender -b rig/SB_Dragao_M2M_v12_asas.blend -P sela/video_montar_entradas.py -- <pasta>"""
import os, re, math
_base = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "video_montar.py"), encoding="utf-8").read()
exec(_base.split("# ---- trajetoria igual")[0], globals())
def lista(nome):
    bloco = re.search(r"local %s = \{[^\n]*\n(.*?)\n\}\n" % nome, src, re.S).group(1); out = []
    for m in re.finditer(r"\{(\d+\.\d+|DUR), (nil|SENTADO|\{\}|simetrico\(\{.*?\}\))\}", bloco, re.S):
        g = m.group(2); t = DUR if m.group(1) == "DUR" else float(m.group(1))
        out.append((t, None if g == "nil" else {} if g == "{}" else SENTADO if g == "SENTADO" else simetrico(tabela(g[len("simetrico({"):-2]))))
    return out
ANDAR = lista("ANDAR"); ANDAR[-1] = (ANDAR[-1][0], ANDAR[0][1]); SENTAR = lista("SENTAR")
PULO = [KF[0], KF[1], KF[2], (0.75, ANDAR[0][1])]
VEL = float(re.search(r"local VEL_RAMPA = ([\d.]+)", src).group(1))
ENTRADA = os.environ.get("ENTRADA", "frente")
def pose_lista(L, t):
    i = 0
    while i < len(L) - 2 and t > L[i + 1][0]: i += 1
    t0, a0 = L[i]; t1, a1 = L[i + 1]
    k = min(max((t - t0) / (t1 - t0), 0), 1); k = k * k * (3 - 2 * k); r = {}
    for n in ORDEM:
        v0 = a0.get(n, [0, 0, 0, (0, 0, 0)]); v1 = a1.get(n, [0, 0, 0, (0, 0, 0)])
        r[n] = ([v0[j] + (v1[j] - v0[j]) * k for j in range(3)], tuple(v0[3][j] + (v1[3][j] - v0[3][j]) * k for j in range(3)))
    return r
FPS = 30
if not A.animation_data: A.animation_data_create()
def acao(nome): return bpy.data.actions["Silverwing_" + nome]
ab, abx, lev = acao("Abaixar"), acao("Abaixado"), acao("Levantar")
dur = lambda a: (a.frame_range[1] - a.frame_range[0]) / FPS
def por(a, k):
    A.animation_data.action = a
    if a.slots: A.animation_data.action_slot = a.slots[0]
    f0, f1 = a.frame_range; x = f0 + (f1 - f0) * k; sc.frame_set(int(x), subframe=x % 1)
def rbx(p_bl): return (C.transposed() @ (p_bl - O)) * ESC
def olhar_para(d):
    d = V((d.x, 0, d.z)).normalized(); z = -d; x = V((0, 1, 0)).cross(z).normalized(); y = z.cross(x)
    return Matrix((x, y, z)).transposed().to_quaternion()
qsela = Quaternion(); up = V((0, 1, 0)); fwd = V((0, 0, -1))
# (06/11) assento do jogo com a sela: HRP 3,6 studs acima do osso Coluna2 (spine_1) em repouso; a subida termina no
# assento ANIMADO do Abaixado (igual ao servidor) -> a origem O do espaco rbx passa a ser esse ponto
S1R = A.matrix_world @ A.data.bones["spine_1"].matrix_local
SEAT_REST = A.matrix_world @ A.data.bones["spine_1"].head_local + V((0, 0, 3.6 / ESC))
por(abx, 0.0)
O = ((A.matrix_world @ A.pose.bones["spine_1"].matrix) @ S1R.inverted()) @ SEAT_REST
CHAO = -O.z * ESC
for b in A.pose.bones: b.matrix_basis.identity()
A.animation_data.action = None; bpy.context.view_layer.update()
rep = lambda n: rbx(A.matrix_world @ A.data.bones[n].head_local)
if ENTRADA == "frente": ini = rep("wing_1_l") + fwd * 3.5 + V((-2.5, 0, 0))   # canto a frente da asa esquerda (igual ao servidor)
else: ini = rep("tail_tip") - fwd * 3
ini = V((ini.x, CHAO + 3.0, ini.z))
por(abx, 0.0)
osso = lambda n: rbx(A.matrix_world @ A.pose.bones[n].head)
FASES = []                                       # (duracao, funcao(t) -> pos, quat, pose)
if ENTRADA == "frente":                           # = AnimCavaleiro.subir
    side = V((ini.x, 0, ini.z)).normalized()
    perto = side * 2.4 + up * 0.4
    P = [ini, ini, ini.lerp(perto, 0.55) + up * 1.2, perto, side * 1.0 + up * 0.9, V((0, 0, 0))]
    qolhar = olhar_para(-side); R = [qolhar, qolhar, qolhar, qolhar, qolhar.slerp(qsela, 0.6), qsela]
    T = [k[0] for k in KF]
    def f_sub(t):
        i = 0
        while i < len(T) - 2 and t > T[i + 1]: i += 1
        k = min(max((t - T[i]) / (T[i + 1] - T[i]), 0), 1); k = k * k * (3 - 2 * k)
        return P[i].lerp(P[i + 1], k), R[i].slerp(R[i + 1], k), pose_em(t)
    FASES.append((DUR, f_sub))
else:                                             # = AnimCavaleiro.subirCauda
    pts = [osso(n) + up * 3 for n in ("tail_5", "tail_4", "tail_3", "tail_2", "hips")]
    alvo = pts[0]; chaoA = V((alvo.x, ini.y, alvo.z)); ate = chaoA - ini; ate.y = 0
    if ate.length > 4.5:                         # longe: anda pelo chao ate perto da cauda (igual ao jogo)
        b0 = chaoA - ate.normalized() * 3.5; d0 = (b0 - ini).length / VEL; qa = olhar_para(ate); ini0 = ini.copy()
        FASES.append((d0, lambda t, ini0=ini0, b0=b0, d0=d0, qa=qa: (ini0.lerp(b0, t / d0), qa, pose_lista(ANDAR, t % ANDAR[-1][0]))))
        ini = b0
    qo = olhar_para(alvo - ini)
    def f_pulo(t, ini=ini):
        if t < 0.30: return ini, qo, pose_lista(PULO, t)
        k = min(1, (t - 0.30) / 0.40); k = k * k * (3 - 2 * k)
        return ini.lerp(alvo, k) + up * math.sin(math.pi * k) * 2.2, qo, pose_lista(PULO, t)
    FASES.append((0.75, f_pulo))
    P = list(pts) + [-fwd * 1.2 + up * 0.9]
    acc = [0.0]
    for i in range(len(P) - 2):
        a_, b_ = P[i], P[i + 1]; d = max(0.15, (b_ - a_).length / VEL); q_ = olhar_para(b_ - a_)
        FASES.append((d, (lambda a_, b_, d, q_: lambda t: (a_.lerp(b_, t / d), q_, pose_lista(ANDAR, (acc[0] + t) % ANDAR[-1][0])))(a_, b_, d, q_)))
    q0 = olhar_para(P[-2] - P[-3])
    def f_sentar(t):
        k = t / 0.8; qm = q0.slerp(qsela, 0.6)
        if k < 0.45: kk = k / 0.45; kk = kk * kk * (3 - 2 * kk); pos, q = P[-2].lerp(P[-1], kk), q0.slerp(qm, kk)
        else: kk = (k - 0.45) / 0.55; kk = kk * kk * (3 - 2 * kk); pos, q = P[-1].lerp(V((0, 0, 0)), kk), qm.slerp(qsela, kk)
        return pos, q, pose_lista(SENTAR, t)
    FASES.append((0.8, f_sentar))
T_SUB = sum(f[0] for f in FASES)
def hrp_e_pose(t):
    if t < 0: return FASES[0][1](0.0)
    for d, fn in FASES:
        if t < d: return fn(t)
        t -= d
    return V((0, 0, 0)), qsela, pose_lista(SENTAR, SENTAR[-1][0])
def mat(nome, c):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*c, 1); return m
pecas = {}
for n in ORDEM:
    bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.name = "Cav_" + n
    o.data.materials.append(mat("M_cav_" + n, cor(n))); pecas[n] = o
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); bpy.context.object.data.materials.append(mat("M_chao_video", (0.32, 0.33, 0.3)))
for o in sc.objects:
    if o.name.startswith("chao_revisao"): o.hide_render = True
TEMAS = {"couro": (0.24, 0.15, 0.22), "madeira": (0.26, 0.17, 0.16), "metal": (0.42, 0.40, 0.46), "adorno": (0.55, 0.28, 0.90)}
for m_ in bpy.data.objects["Silverwing_Sela"].data.materials:
    c = TEMAS.get(m_.name.replace("M_Sela_", ""))
    if c and m_.node_tree: m_.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*[x ** 2.2 for x in c], 1)
SEGUIR = 1.0                                     # Cfg.assento.seguirOsso do jogo (06/11: 1,0)
def montado():
    """sentado: como o Montaria_Cliente faz (weld no assento de repouso + 75% do movimento do osso do dorso)"""
    rest = SEAT_REST
    Mo = (A.matrix_world @ A.pose.bones["spine_1"].matrix) @ (A.matrix_world @ A.data.bones["spine_1"].matrix_local).inverted()
    anim = Mo @ rest; pbl = rest.lerp(anim, SEGUIR); qbl = Quaternion().slerp(Mo.to_quaternion(), SEGUIR)
    qr = (C.transposed() @ qbl.to_matrix() @ C).to_quaternion()
    return rbx(pbl), qr
def colocar(t):
    pos, q, ang = hrp_e_pose(t)
    if t >= T_SUB: pos, q = montado()
    mw = {"HRP": Matrix.Translation(pos) @ q.to_matrix().to_4x4()}
    for n in ORDEM:
        pai, junta, centro, tam = R15[n]; a, p = ang[n]
        mw[n] = mw[pai] @ Matrix.Translation(V(junta)) @ Matrix.Translation(V(p)) @ Rang(a) @ Matrix.Translation(V(centro))
        pecas[n].matrix_world = Matrix.Translation(bl(mw[n].translation)) @ (C @ mw[n].to_3x3()).to_4x4() @ Matrix.Diagonal((*[x / ESC for x in tam], 1))
DAB = dur(ab); T_SOBE = DAB + 0.4; T_LEV = T_SOBE + T_SUB + 0.6; T_FIM = T_LEV + dur(lev) + 0.6
def dragao(t):
    if t < DAB: por(ab, t / DAB)
    elif t < T_LEV: d = dur(abx); por(abx, ((t - DAB) % d) / d)
    else: por(lev, min(1, (t - T_LEV) / dur(lev)))
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 960, 540
cam = bpy.data.objects.new("CamVideo", bpy.data.cameras.new("CamVideo")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 35
if not [o for o in sc.objects if o.type == "LIGHT"]:
    l = bpy.data.objects.new("SolV", bpy.data.lights.new("SolV", "SUN")); l.data.energy = 3.0; sc.collection.objects.link(l); l.rotation_euler = (0.8, 0.1, 0.9)
VISTA = os.environ.get("VISTA", "lado")
alvo0 = bl(ini * 0.5) + V((0, 0, 0.02))
OFF = {("frente", "lado"): V((1.25, -1.05, 0.45)), ("frente", "alto"): V((0.6, -0.9, 1.2)),
       ("tras", "lado"): V((1.3, 0.9, 0.45)), ("tras", "alto"): V((0.6, 1.0, 1.2))}[(ENTRADA, VISTA)]
cam.location = alvo0 + OFF; cam.rotation_euler = (alvo0 - cam.location).to_track_quat("-Z", "Y").to_euler()
n = int(T_FIM * FPS)
for f in range(n):
    t = f / FPS; dragao(t); colocar(t - T_SOBE)
    sc.render.filepath = os.path.join(OUT, "f%05d.jpg" % f); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
print("VIDEO_ENTRADA_OK", ENTRADA, n, "quadros", round(T_FIM, 2), "s; subida", round(T_SUB, 2), "s; inicio", tuple(round(c, 1) for c in ini))
