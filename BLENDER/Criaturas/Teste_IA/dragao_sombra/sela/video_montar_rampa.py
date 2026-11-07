"""Previa em video da MONTARIA PELA ASA EM RAMPA (06/11, usuario: "para o jogador montar, a animacao deve abrir a asa ao
montar (como uma rampa)"). Reproduz o AnimCavaleiro.subirRampa do jogo: o dragao faz Abaixar_Rampa_E -> Abaixado_Rampa_E
(asa esquerda esticada ate o chao) -> Levantar_Rampa_E; o boneco R15 anda ate a ponta da asa, sobe pela borda (punho ->
cotovelo -> ombro) com a passada Cavaleiro_Andar_Rampa e no ombro faz o Cavaleiro_Sentar ate a sela. Poses lidas do .luau;
pontos da rampa tirados dos ossos animados (como o servidor faz com TransformedWorldCFrame).
Reaproveita a primeira parte de video_montar.py (leitor de poses, boneco, eixos). Env VISTA = lado | alto.
Uso: blender -b rig/SB_Dragao_M2M_v12_asas.blend -P sela/video_montar_rampa.py -- <pasta_quadros>"""
import os, re, math
_base = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "video_montar.py"), encoding="utf-8").read()
exec(_base.split("# ---- trajetoria igual")[0], globals())
def lista(nome):
    bloco = re.search(r"local %s = \{[^\n]*\n(.*?)\n\}\n" % nome, src, re.S).group(1); out = []
    for m in re.finditer(r"\{(\d+\.\d+), (nil|SENTADO|simetrico\(\{.*?\}\))\}", bloco, re.S):
        g = m.group(2)
        out.append((float(m.group(1)), None if g == "nil" else SENTADO if g == "SENTADO" else simetrico(tabela(g[len("simetrico({"):-2]))))
    return out
ANDAR = lista("ANDAR"); ANDAR[-1] = (ANDAR[-1][0], ANDAR[0][1]); SENTAR = lista("SENTAR")
VEL = float(re.search(r"local VEL_RAMPA = ([\d.]+)", src).group(1))
print("RAMPA andar", [k[0] for k in ANDAR], "sentar", [k[0] for k in SENTAR], "vel", VEL)
def pose_lista(L, t):
    i = 0
    while i < len(L) - 2 and t > L[i + 1][0]: i += 1
    t0, a0 = L[i]; t1, a1 = L[i + 1]
    k = min(max((t - t0) / (t1 - t0), 0), 1); k = k * k * (3 - 2 * k); r = {}
    for n in ORDEM:
        v0 = a0.get(n, [0, 0, 0, (0, 0, 0)]); v1 = a1.get(n, [0, 0, 0, (0, 0, 0)])
        r[n] = ([v0[j] + (v1[j] - v0[j]) * k for j in range(3)], tuple(v0[3][j] + (v1[3][j] - v0[3][j]) * k for j in range(3)))
    return r
def mistura_pose(a, b, k):
    return {n: ([a[n][0][j] + (b[n][0][j] - a[n][0][j]) * k for j in range(3)], tuple(a[n][1][j] + (b[n][1][j] - a[n][1][j]) * k for j in range(3))) for n in ORDEM}
FPS = 30
if not A.animation_data: A.animation_data_create()
def acao(nome): return bpy.data.actions["Silverwing_" + nome]
ab, abx, lev = acao("Abaixar_Rampa_E"), acao("Abaixado_Rampa_E"), acao("Levantar_Rampa_E")
dur = lambda a: (a.frame_range[1] - a.frame_range[0]) / FPS
def por(a, k):
    A.animation_data.action = a
    if a.slots: A.animation_data.action_slot = a.slots[0]
    f0, f1 = a.frame_range; x = f0 + (f1 - f0) * k; sc.frame_set(int(x), subframe=x % 1)
# pontos da rampa no Abaixado_Rampa_E (inicio do laco), convertidos para o espaco rbx (studs, origem na sela)
por(abx, 0.0)
def rbx(p_bl): return (C.transposed() @ (p_bl - O)) * ESC
osso = lambda n: rbx(A.matrix_world @ A.pose.bones[n].head)
punho, cotovelo, ombro = osso("wing_3_l"), osso("wing_2_l"), osso("wing_1_l")
up = V((0, 3.0, 0)); chao = lambda p: V((p.x, CHAO, p.z))
fora = V((punho.x - ombro.x, 0, punho.z - ombro.z)).normalized()
P = [chao(punho) + fora * 5 + up, chao(punho) + up, punho + up, cotovelo + up, ombro + up]
side = V((ombro.x, 0, ombro.z)).normalized(); fim_lado = side * 1.0 + V((0, 0.9, 0))
print("RAMPA pontos (studs)", [tuple(round(c, 1) for c in p) for p in P])
SEG = [(P[i], P[i + 1], max(0.15, (P[i + 1] - P[i]).length / VEL)) for i in range(len(P) - 1)]
T_AND = sum(s[2] for s in SEG); T_SENT = SENTAR[-1][0]
def olhar_para(d):
    d = V((d.x, 0, d.z)).normalized(); z = -d; x = V((0, 1, 0)).cross(z).normalized(); y = z.cross(x)
    return Matrix((x, y, z)).transposed().to_quaternion()
qsela = Quaternion()
def hrp_e_pose(t):                              # t = 0 no inicio da subida
    if t < 0: return P[0], olhar_para(P[1] - P[0]), pose_lista(ANDAR, 0.0)
    if t < T_AND:
        acc = 0
        for a, b, d in SEG:
            if t < acc + d:
                k = (t - acc) / d; return a.lerp(b, k), olhar_para(b - a), pose_lista(ANDAR, t % ANDAR[-1][0])
            acc += d
    t2 = t - T_AND; q0 = olhar_para(P[-1] - P[-2])
    if t2 < T_SENT:
        k = t2 / T_SENT; qm = q0.slerp(qsela, 0.6)
        if k < 0.45: kk = k / 0.45; kk = kk * kk * (3 - 2 * kk); pos, q = P[-1].lerp(fim_lado, kk), q0.slerp(qm, kk)
        else: kk = (k - 0.45) / 0.55; kk = kk * kk * (3 - 2 * kk); pos, q = fim_lado.lerp(V((0, 0, 0)), kk), qm.slerp(qsela, kk)
        pz = pose_lista(SENTAR, t2)
        if t2 < 0.15: pz = mistura_pose(pose_lista(ANDAR, 0.0), pz, t2 / 0.15)
        return pos, q, pz
    return V((0, 0, 0)), qsela, pose_lista(SENTAR, T_SENT)
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
S_ = bpy.data.objects["Silverwing_Sela"]
for m_ in S_.data.materials:
    c = TEMAS.get(m_.name.replace("M_Sela_", ""))
    if c and m_.node_tree: m_.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*[x ** 2.2 for x in c], 1)
def colocar(t):
    pos, q, ang = hrp_e_pose(t)
    mw = {"HRP": Matrix.Translation(pos) @ q.to_matrix().to_4x4()}
    for n in ORDEM:
        pai, junta, centro, tam = R15[n]; a, p = ang[n]
        mw[n] = mw[pai] @ Matrix.Translation(V(junta)) @ Matrix.Translation(V(p)) @ Rang(a) @ Matrix.Translation(V(centro))
        pecas[n].matrix_world = Matrix.Translation(bl(mw[n].translation)) @ (C @ mw[n].to_3x3()).to_4x4() @ Matrix.Diagonal((*[x / ESC for x in tam], 1))
DAB = dur(ab); T_SOBE = DAB + 0.2; T_LEV = T_SOBE + T_AND + T_SENT + 0.6; T_FIM = T_LEV + dur(lev) + 0.6
def dragao(t):
    if t < DAB: por(ab, t / DAB)
    elif t < T_LEV: d = dur(abx); por(abx, ((t - DAB) % d) / d)
    else: por(lev, min(1, (t - T_LEV) / dur(lev)))
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 960, 540
cam = bpy.data.objects.new("CamVideo", bpy.data.cameras.new("CamVideo")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 35
if not [o for o in sc.objects if o.type == "LIGHT"]:
    l = bpy.data.objects.new("SolV", bpy.data.lights.new("SolV", "SUN")); l.data.energy = 3.0; sc.collection.objects.link(l); l.rotation_euler = (0.8, 0.1, 0.9)
VISTA = os.environ.get("VISTA", "lado")
alvo0 = bl((P[2] + V((0, 0, 0))) * 0.5) + V((0, 0, -0.05))
OFF = {"lado": V((1.0, -1.9, 0.55)), "alto": V((1.3, -0.6, 1.6))}[VISTA]
cam.location = alvo0 + OFF; cam.rotation_euler = (alvo0 - cam.location).to_track_quat("-Z", "Y").to_euler()
n = int(T_FIM * FPS)
for f in range(n):
    t = f / FPS; dragao(t); colocar(t - T_SOBE)
    sc.render.filepath = os.path.join(OUT, "f%05d.jpg" % f); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
print("VIDEO_RAMPA_OK", n, "quadros", round(T_FIM, 2), "s; subida", round(T_AND, 2), "s")
