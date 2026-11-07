"""Previa em video da animacao de MONTAR (06/11, usuario: "Me mostre antes de importar").
Reproduz no Blender o que src/ReplicatedStorage/Montaria_Dragoes/AnimCavaleiro.luau faz no jogo: boneco R15 em blocos
(proporcoes aproximadas do R15), os MESMOS angulos por articulacao (lidos do .luau) e a mesma trajetoria do HRP (agacha ao
lado do flanco, salta, agarra a sela, passa a perna, senta), com o dragao no clipe Abaixar -> Abaixado -> Levantar e a sela.
A conta e feita no espaco do Roblox (X direita, Y cima, -Z frente, studs) e convertida para o Blender (1 unidade = 17,5 studs;
o dragao olha para -Y). Uso: blender -b rig/SB_Dragao_M2M_v11_sela.blend -P sela/video_montar.py -- <pasta_quadros>"""
import bpy, os, sys, re, math
from mathutils import Vector as V, Matrix, Quaternion
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
LUAU = os.path.join(RAIZ, "src", "ReplicatedStorage", "Montaria_Dragoes", "AnimCavaleiro.luau")
src = open(LUAU, encoding="utf-8").read()
# ---- le as poses do .luau (SENTADO e KF) ----
def tabela(txt):
    """converte o corpo de simetrico({...}) em dict junta -> (x, z, y, p)"""
    d = {}
    for m in re.finditer(r"(\w+)\s*=\s*\{([^{}]*?(?:Vector3\.new\([^)]*\))?[^{}]*?)\}", txt):
        nome, corpo = m.group(1), m.group(2)
        p = re.search(r"p\s*=\s*Vector3\.new\(([^)]*)\)", corpo)
        corpo_n = re.sub(r"p\s*=\s*Vector3\.new\([^)]*\)", "", corpo)
        nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", corpo_n)]
        d[nome] = (nums + [0, 0, 0])[:3] + [tuple(float(x) for x in p.group(1).split(",")) if p else (0, 0, 0)]
    return d
def simetrico(t):
    r = {}
    for k, v in t.items():
        if k.startswith(("Left", "Right")) or k in ("LowerTorso", "UpperTorso", "Head"): r[k] = v
        else:
            r["Right" + k] = [v[0], v[1], v[2], v[3]]; r["Left" + k] = [v[0], -v[1], -v[2], v[3]]
    return r
sent = re.search(r"local SENTADO = simetrico\(\{(.*?)\}\)\n", src, re.S).group(1)
SENTADO = simetrico(tabela(sent))
DUR = float(re.search(r"local DUR = ([\d.]+)", src).group(1))
KF = []
bloco = re.search(r"local KF = \{\n(.*?)\n\}\n", src, re.S).group(1)
for linha in re.finditer(r"\{(\d+\.\d+|DUR), (\{\}|SENTADO|simetrico\(\{.*?\}\))\}", bloco, re.S):
    t = DUR if linha.group(1) == "DUR" else float(linha.group(1)); g = linha.group(2)
    KF.append((t, {} if g == "{}" else SENTADO if g == "SENTADO" else simetrico(tabela(g[len("simetrico({"):-2]))))
print("VIDEO keyframes", [k[0] for k in KF], "juntas no sentado", len(SENTADO))
# ---- boneco R15 em blocos (studs): (pai, posicao da junta no pai, centro da peca a partir da junta, tamanho) ----
R15 = {
    "LowerTorso": ("HRP", (0, -0.2, 0), (0, 0, 0), (2, 0.4, 1)),
    "UpperTorso": ("LowerTorso", (0, 0.2, 0), (0, 0.8, 0), (2, 1.6, 1)),
    "Head": ("UpperTorso", (0, 0.8, 0), (0, 0.6, 0), (1.2, 1.2, 1.2)),
    "RightUpperArm": ("UpperTorso", (1.5, 0.6, 0), (0, -0.55, 0), (1, 1.15, 1)), "LeftUpperArm": ("UpperTorso", (-1.5, 0.6, 0), (0, -0.55, 0), (1, 1.15, 1)),
    "RightLowerArm": ("RightUpperArm", (0, -0.55, 0), (0, -0.5, 0), (0.9, 1.0, 0.9)), "LeftLowerArm": ("LeftUpperArm", (0, -0.55, 0), (0, -0.5, 0), (0.9, 1.0, 0.9)),
    "RightHand": ("RightLowerArm", (0, -0.5, 0), (0, -0.15, 0), (0.9, 0.3, 0.9)), "LeftHand": ("LeftLowerArm", (0, -0.5, 0), (0, -0.15, 0), (0.9, 0.3, 0.9)),
    "RightUpperLeg": ("LowerTorso", (0.5, -0.2, 0), (0, -0.58, 0), (1, 1.15, 1)), "LeftUpperLeg": ("LowerTorso", (-0.5, -0.2, 0), (0, -0.58, 0), (1, 1.15, 1)),
    "RightLowerLeg": ("RightUpperLeg", (0, -0.58, 0), (0, -0.55, 0), (0.95, 1.1, 0.95)), "LeftLowerLeg": ("LeftUpperLeg", (0, -0.58, 0), (0, -0.55, 0), (0.95, 1.1, 0.95)),
    "RightFoot": ("RightLowerLeg", (0, -0.55, 0), (0, -0.15, -0.15), (1, 0.3, 1.3)), "LeftFoot": ("LeftLowerLeg", (0, -0.55, 0), (0, -0.15, -0.15), (1, 0.3, 1.3)),
}
ORDEM = ["LowerTorso", "UpperTorso", "Head", "RightUpperArm", "LeftUpperArm", "RightLowerArm", "LeftLowerArm", "RightHand", "LeftHand",
         "RightUpperLeg", "LeftUpperLeg", "RightLowerLeg", "LeftLowerLeg", "RightFoot", "LeftFoot"]
COR = {"Head": (0.95, 0.78, 0.6), "UpperTorso": (0.25, 0.45, 0.85), "LowerTorso": (0.2, 0.2, 0.25), "Arm": (0.25, 0.45, 0.85),
       "Hand": (0.95, 0.78, 0.6), "Leg": (0.22, 0.22, 0.28), "Foot": (0.12, 0.1, 0.1)}
def cor(n):
    for k in ("Head", "UpperTorso", "LowerTorso", "Hand", "Foot"):
        if k in n: return COR[k]
    return COR["Arm"] if "Arm" in n else COR["Leg"]
def Rang(a):                                   # CFrame.Angles(x, y, z) = Rx * Ry * Rz (rbx); a = (x, z, y) em graus
    x, z, y = math.radians(a[0]), math.radians(a[1]), math.radians(a[2])
    return Matrix.Rotation(x, 4, "X") @ Matrix.Rotation(y, 4, "Y") @ Matrix.Rotation(z, 4, "Z")
def pose_em(t):                                # interpola as poses (suave, como o Cubic InOut)
    i = 0
    while i < len(KF) - 2 and t > KF[i + 1][0]: i += 1
    t0, a0 = KF[i]; t1, a1 = KF[i + 1]
    k = min(max((t - t0) / (t1 - t0), 0), 1); k = k * k * (3 - 2 * k)
    r = {}
    for n in ORDEM:
        v0 = a0.get(n, [0, 0, 0, (0, 0, 0)]); v1 = a1.get(n, [0, 0, 0, (0, 0, 0)])
        r[n] = ([v0[j] + (v1[j] - v0[j]) * k for j in range(3)], tuple(v0[3][j] + (v1[3][j] - v0[3][j]) * k for j in range(3)))
    return r
# ---- mundo: espaco rbx (studs) com origem no alvo do HRP sentado ----
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
ESC = 17.5
C = Matrix(((-1, 0, 0), (0, 0, 1), (0, 1, 0)))                  # rbx -> blender (direita do dragao = -X, cima = Z, frente = -Y)
S = bpy.data.objects["Silverwing_Sela"]
O = V(S["HRP"]) - V((0, 0, 1.8 * 0.25 / ESC))                    # sela do jogo: assento - 25% do AssentoAcima (dragao abaixado)
CHAO = -O.z * ESC                                                 # y do chao no espaco rbx
def bl(p): return O + C @ V(p) / ESC
# ---- trajetoria igual ao AnimCavaleiro.subir ----
lado = -1                                                         # flanco esquerdo do dragao
side = V((lado, 0, 0)); up = V((0, 1, 0))
de = V((lado * 7.5, CHAO + 3.0, 0.4))
flanco = side * 2.4 + up * 0.4
P = [de, de, de.lerp(flanco, 0.55) + up * 1.2, flanco, side * 1.0 + up * 0.9, V((0, 0, 0))]
def olhar_para(d):                                                 # rotacao rbx com LookVector = d (no plano)
    d = V((d.x, 0, d.z)).normalized(); z = -d; x = V((0, 1, 0)).cross(z).normalized(); y = z.cross(x)
    return Matrix((x, y, z)).transposed().to_quaternion()
qde = olhar_para(-side); qsela = Quaternion()
R = [qde, qde, qde, qde, qde.slerp(qsela, 0.6), qsela]
T = [k[0] for k in KF]
def hrp_em(t):
    if t >= DUR: return V((0, 0, 0)), qsela
    i = 0
    while i < len(T) - 2 and t > T[i + 1]: i += 1
    k = min(max((t - T[i]) / (T[i + 1] - T[i]), 0), 1); k = k * k * (3 - 2 * k)
    return P[i].lerp(P[i + 1], k), R[i].slerp(R[i + 1], k)
# ---- objetos ----
def mat(nome, c):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*c, 1); return m
pecas = {}
for n in ORDEM:
    bpy.ops.mesh.primitive_cube_add(size=1); o = bpy.context.object; o.name = "Cav_" + n
    o.data.materials.append(mat("M_cav_" + n, cor(n))); pecas[n] = o
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0)); chao = bpy.context.object
chao.data.materials.append(mat("M_chao_video", (0.32, 0.33, 0.3)))
for o in sc.objects:
    if o.name.startswith("chao_revisao"): o.hide_render = True
TEMAS = [(0.24, 0.15, 0.22), (0.26, 0.17, 0.16), (0.42, 0.40, 0.46), (0.55, 0.28, 0.90)]
for m_ in S.data.materials:
    k = m_.name.replace("M_Sela_", ""); c = {"couro": TEMAS[0], "madeira": TEMAS[1], "metal": TEMAS[2], "adorno": TEMAS[3]}.get(k)
    if c and m_.node_tree: m_.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*[x ** 2.2 for x in c], 1)
def colocar(t):
    pos, q = hrp_em(t); ang = pose_em(min(t, DUR)) if t < DUR + 9 else pose_em(DUR)
    mw = {"HRP": Matrix.Translation(pos) @ q.to_matrix().to_4x4()}
    for n in ORDEM:
        pai, junta, centro, tam = R15[n]; a, p = ang[n]
        jm = mw[pai] @ Matrix.Translation(V(junta)) @ Matrix.Translation(V(p)) @ Rang(a)
        mw[n] = jm @ Matrix.Translation(V(centro))
        m3 = (C @ mw[n].to_3x3()).to_4x4()
        pecas[n].matrix_world = Matrix.Translation(bl(mw[n].translation)) @ m3 @ Matrix.Diagonal((*[x / ESC for x in tam], 1))
# ---- linha do tempo: dragao Abaixar -> Abaixado (cavaleiro sobe) -> pose montada -> Levantar ----
FPS = 30
def acao(nome): return bpy.data.actions.get("Silverwing_" + nome)
ab, abx, lev = acao("Abaixar"), acao("Abaixado"), acao("Levantar")
dab = (ab.frame_range[1] - ab.frame_range[0]) / FPS; dlev = (lev.frame_range[1] - lev.frame_range[0]) / FPS
T_SOBE = dab + 0.2; T_FIM = T_SOBE + DUR + 0.5 + dlev + 0.6
if not A.animation_data: A.animation_data_create()
def dragao(t):
    if t < dab: a, k = ab, t / dab
    elif t < T_SOBE + DUR + 0.5:
        a = abx; f0, f1 = abx.frame_range; k = ((t - dab) * FPS % max(1, f1 - f0)) / max(1, f1 - f0)
    else: a, k = lev, min(1, (t - T_SOBE - DUR - 0.5) / dlev)
    A.animation_data.action = a
    if hasattr(A.animation_data, "action_slot") and a.slots: A.animation_data.action_slot = a.slots[0]
    f0, f1 = a.frame_range; sc.frame_set(int(f0 + (f1 - f0) * k), subframe=((f0 + (f1 - f0) * k) % 1))
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 960, 540
cam = bpy.data.objects.new("CamVideo", bpy.data.cameras.new("CamVideo")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 42
if not [o for o in sc.objects if o.type == "LIGHT"]:
    l = bpy.data.objects.new("SolV", bpy.data.lights.new("SolV", "SUN")); l.data.energy = 3.0; sc.collection.objects.link(l); l.rotation_euler = (0.8, 0.1, 0.9)
alvo0 = O + V((0.10, -0.02, -0.05))
VISTA = os.environ.get("VISTA", "lado")
OFF = {"lado": V((1.55, -0.85, 0.42)), "alto": V((1.1, -0.35, 1.05))}[VISTA]
alvo0 = O + V((0.12, -0.02, -0.12))
cam.location = alvo0 + OFF; cam.rotation_euler = (alvo0 - cam.location).to_track_quat("-Z", "Y").to_euler()
n = int(T_FIM * FPS)
for f in range(n):
    t = f / FPS; dragao(t); colocar(t - T_SOBE if t >= T_SOBE else -1)
    sc.render.filepath = os.path.join(OUT, "f%05d.jpg" % f); sc.render.image_settings.file_format = "JPEG"
    bpy.ops.render.render(write_still=True)
print("VIDEO_OK", n, "quadros", round(T_FIM, 2), "s")
