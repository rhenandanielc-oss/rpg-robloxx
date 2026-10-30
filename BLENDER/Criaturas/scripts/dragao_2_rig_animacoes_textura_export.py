# Dragao das Montanhas - etapa 3: armature (45 ossos), pesos por proximidade por regiao, animacoes (acoes),
# textura de escamas assada (cor + normal) e exportacao GLB/FBX. Eixos: frente -Y, cima +Z, esquerda da criatura +X.
import bpy, bmesh, math, sys, os, json
from mathutils import Vector, Matrix, Quaternion

OUT = sys.argv[sys.argv.index("--") + 1]
DEST = sys.argv[sys.argv.index("--") + 2]
FORMA = sys.argv[sys.argv.index("--") + 3] if len(sys.argv) > sys.argv.index("--") + 3 else "Montanhas"
# padroes oficiais (RPG_02, secao 10): tons interpretados dos nomes (provisorios); [escuro, claro] das escamas e do couro
PADROES = {"Montanhas": [("Basalto_Cinzento", (0.055, 0.055, 0.06), (0.23, 0.225, 0.22), (0.05, 0.048, 0.047), (0.16, 0.15, 0.145)),
                         ("Cobre_das_Alturas", (0.10, 0.05, 0.03), (0.42, 0.24, 0.14), (0.08, 0.045, 0.03), (0.26, 0.15, 0.09)),
                         ("Verde_da_Montanha", (0.035, 0.06, 0.04), (0.20, 0.29, 0.19), (0.035, 0.05, 0.035), (0.13, 0.18, 0.12))],
           "Glacial": [("Branco_Glacial", (0.42, 0.47, 0.52), (0.88, 0.92, 0.95), (0.35, 0.40, 0.46), (0.70, 0.76, 0.82)),
                       ("Azul_da_Geada", (0.10, 0.22, 0.38), (0.52, 0.72, 0.90), (0.10, 0.18, 0.30), (0.36, 0.52, 0.68)),
                       ("Cinza_da_Nevasca", (0.20, 0.22, 0.25), (0.60, 0.62, 0.66), (0.17, 0.18, 0.20), (0.44, 0.46, 0.50))],
           "Sombrio": [("Negro_Obsidiana", (0.012, 0.012, 0.016), (0.12, 0.11, 0.13), (0.012, 0.012, 0.015), (0.08, 0.075, 0.085)),
                       ("Roxo_Crepuscular", (0.045, 0.02, 0.07), (0.29, 0.16, 0.38), (0.035, 0.015, 0.05), (0.18, 0.09, 0.24)),
                       ("Carmesim_Corrompido", (0.07, 0.01, 0.014), (0.40, 0.06, 0.08), (0.05, 0.01, 0.012), (0.24, 0.04, 0.05))]}[FORMA]
NOME = "Dragao_" + ("das_Montanhas" if FORMA == "Montanhas" else FORMA)
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, "d2_geo_%s.blend" % FORMA))
scn = bpy.context.scene
SK = json.load(open(os.path.join(OUT, "dragao_esqueleto_%s.json" % FORMA)))
sp = [Vector(p) for p in SK["spine"]]
mesh = bpy.data.objects["Dragao_das_Montanhas"]
# remover objetos de previa (chao, cilindro, camera, luz) da cena de exportacao
for o in list(scn.objects):
    if o != mesh: bpy.data.objects.remove(o, do_unlink=True)

# reduzir para caber no limite de malha do Roblox, preservando forma
bpy.context.view_layer.objects.active = mesh; mesh.select_set(True)
dec = mesh.modifiers.new("Dec", "DECIMATE"); dec.ratio = 0.82
bpy.ops.object.modifier_apply(modifier="Dec")
print("TRIS_FINAL", sum(len(p.vertices) - 2 for p in mesh.data.polygons))

# ---------------- armature
arm_d = bpy.data.armatures.new("Esqueleto"); arm = bpy.data.objects.new("Dragao_Rig", arm_d); scn.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT")
EB = arm_d.edit_bones
REGIAO = {}
def osso(nome, h, t, pai=None, reg="CORPO", deform=True):
    b = EB.new(nome); b.head = Vector(h); b.tail = Vector(t); b.roll = 0
    if pai: b.parent = EB[pai]
    b.use_deform = deform; REGIAO[nome] = reg
    return b
osso("Raiz", (0, 0, 0), (0, 0, 3), None, "NENHUMA", False)
osso("Pelve", sp[7], sp[8], "Raiz"); osso("Lombo", sp[8], sp[9], "Pelve"); osso("Peito", sp[9], sp[10], "Lombo")
osso("Pescoco1", sp[10], sp[12], "Peito"); osso("Pescoco2", sp[12], sp[13], "Pescoco1"); osso("Pescoco3", sp[13], sp[14], "Pescoco2"); osso("Pescoco4", sp[14], sp[15], "Pescoco3")
osso("Cabeca", sp[15] + Vector((0, 0, 0.6)), sp[17] + Vector((0, 0, 0.7)), "Pescoco4")
osso("Mandibula", sp[15] + Vector((0, -1.6, -1.6)), sp[18] + Vector((0, 0.2, -0.75)), "Cabeca")
prev = "Pelve"
for k in range(7):
    n = "Cauda%d" % (k + 1); osso(n, sp[7 - k] if k else sp[7], sp[6 - k], prev); prev = n
LG = SK["legs"]
for lado in ("E", "D"):
    c = [Vector(p) for p in LG["Dianteira_" + lado]]
    osso("Braco_" + lado, c[0], c[2], "Peito"); osso("Antebraco_" + lado, c[2], c[3], "Braco_" + lado)
    osso("Mao_" + lado, c[3], c[4], "Antebraco_" + lado); osso("DedosMao_" + lado, c[4], c[5], "Mao_" + lado)
    c = [Vector(p) for p in LG["Traseira_" + lado]]
    osso("Coxa_" + lado, c[0], c[2], "Pelve"); osso("Canela_" + lado, c[2], c[3], "Coxa_" + lado)
    osso("Pe_" + lado, c[3], c[4], "Canela_" + lado); osso("DedosPe_" + lado, c[4], c[5], "Pe_" + lado)
    a = SK["asas"][lado]
    osso("AsaUmero_" + lado, a["ombro"], a["cotovelo"], "Peito", "ASA_" + lado)
    osso("AsaAntebraco_" + lado, a["cotovelo"], a["punho"], "AsaUmero_" + lado, "ASA_" + lado)
    for i, d in enumerate(a["dedos"]):
        osso("AsaDedo%d_%s" % (i + 1, lado), a["punho"], d, "AsaAntebraco_" + lado, "ASA_" + lado)
bpy.ops.object.mode_set(mode="OBJECT")
print("OSSOS", len(arm_d.bones))

# ---------------- pesos por proximidade (dentro da regiao), 4 influencias
segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm_d.bones if b.use_deform}
def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
gid = {g.name: g.index for g in mesh.vertex_groups}
vgs = {n: mesh.vertex_groups.new(name=n) for n in segs}
cand = {"CORPO": [n for n in segs if REGIAO[n] == "CORPO"],
        "ASA_E": [n for n in segs if REGIAO[n] == "ASA_E"] + ["Peito", "Lombo"],
        "ASA_D": [n for n in segs if REGIAO[n] == "ASA_D"] + ["Peito", "Lombo"]}
for v in mesh.data.vertices:
    reg = "CORPO"
    for g in v.groups:
        nm = mesh.vertex_groups[g.group].name
        if nm.startswith("REG_ASA_"): reg = "ASA_" + nm[-1]
    p = v.co
    ws = []
    for n in cand[reg]:
        a, b = segs[n]; d = dist_seg(p, a, b)
        ws.append((1.0 / (d ** 4 + 0.05), n))
    ws.sort(reverse=True); ws = ws[:4]
    tot = sum(w for w, _ in ws)
    for w, n in ws:
        if w / tot > 0.02: vgs[n].add([v.index], w / tot, "REPLACE")
# faces das asas (membrana e ossos da asa) recebem material de couro (slot 1)
ASAV = set()
for v in mesh.data.vertices:
    for g in v.groups:
        if mesh.vertex_groups[g.group].name.startswith("REG_ASA_"): ASAV.add(v.index)
for g in [g for g in mesh.vertex_groups if g.name.startswith("REG_")]: mesh.vertex_groups.remove(g)
mod = mesh.modifiers.new("Armature", "ARMATURE"); mod.object = arm
mesh.parent = arm

# ---------------- poses: rotacoes em eixos do corpo convertidas para o espaco de cada osso
PB = arm.pose.bones
for pb in PB: pb.rotation_mode = "QUATERNION"
def R(ax, ay, az):  # graus, eixos do corpo (X esquerda, Y tras, Z cima), ordem Z*Y*X
    return (Matrix.Rotation(math.radians(az), 3, "Z") @ Matrix.Rotation(math.radians(ay), 3, "Y") @ Matrix.Rotation(math.radians(ax), 3, "X"))
def aplicar(pose):
    for pb in PB:
        pb.rotation_quaternion = Quaternion(); pb.location = Vector()
    for nome, val in pose.items():
        pb = PB[nome]; M = pb.bone.matrix_local.to_3x3()
        rot, loc = val if isinstance(val, tuple) else (val, None)
        pb.rotation_quaternion = (M.inverted() @ rot @ M).to_quaternion()
        if loc is not None: pb.location = M.inverted() @ Vector(loc)
def S(x): return math.sin(2 * math.pi * x)
def C(x): return math.cos(2 * math.pi * x)
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
# convencoes (ver comentario do modulo): pata para frente = -X; cabeca/pescoco para cima = -X; cauda para cima = +X
# asa: elevar = -s em Y (s=+1 esquerda, -1 direita); recuar = +s em Z
LADOS = (("E", 1), ("D", -1))
def asas(p, elev, recuo, punho_e, punho_r, dedos_abrir=0, dif=0):
    for lado, s in LADOS:
        e = elev + dif * s
        p["AsaUmero_" + lado] = R(0, -s * e, s * recuo)
        p["AsaAntebraco_" + lado] = R(0, -s * punho_e, s * punho_r)
        for i in range(4):
            p["AsaDedo%d_%s" % (i + 1, lado)] = R(0, -s * (dedos_abrir * 0.3 * i), s * (dedos_abrir * (i - 1.5)))
    return p
REP = dict(elev=38, recuo=36, punho_e=-34, punho_r=68, dedos=-9)  # asas recolhidas ao longo do corpo
def asas_rep(p, resp=0): return asas(p, REP["elev"] + resp, REP["recuo"], REP["punho_e"], REP["punho_r"], REP["dedos"])
def marcha(t, fases, A, bob, pitch):
    p = {}
    nomes = [("Braco_E", "Antebraco_E"), ("Braco_D", "Antebraco_D"), ("Coxa_E", "Canela_E"), ("Coxa_D", "Canela_D")]
    for (a, b), f in zip(nomes, fases):
        x = t - f; sw = A * S(x); lift = max(0, S(x + 0.25))  # dobra o joelho/cotovelo na fase de recuperacao
        tras = a.startswith("Coxa")
        p[a] = R(-sw, 0, 0); p[b] = R((-25 if tras else 30) * lift, 0, 0)
    p["Pelve"] = (R(pitch * S(t + 0.25), 0, 1.2 * S(t)), (0, 0, bob * (0.5 - 0.5 * C(2 * t))))
    p["Pescoco1"] = R(-pitch * 0.6 * S(t + 0.25), 3 * S(t), 0)
    p["Cabeca"] = R(1.5 * S(2 * t), 0, 0)
    for k in range(7): p["Cauda%d" % (k + 1)] = R(-2, 0, 5 * S(t - 0.08 * k))
    return p
FPS = 30; scn.render.fps = FPS
ACOES = {}
def acao(nome, dur, loop, f):
    act = bpy.data.actions.new(nome); arm.animation_data_create(); arm.animation_data.action = act
    n = max(2, int(dur * FPS))
    for fr in range(n + 1):
        t = fr / n
        aplicar(f(t))
        for pb in PB:
            pb.keyframe_insert("rotation_quaternion", frame=fr + 1); pb.keyframe_insert("location", frame=fr + 1)
    act.use_fake_user = True; act["loop"] = loop; ACOES[nome] = act
    # trilha NLA para exportar cada acao separadamente
    tr = arm.animation_data.nla_tracks.new(); tr.name = nome; tr.strips.new(nome, 1, act)
    arm.animation_data.action = None
# --- solo
acao("Repouso", 5.0, True, lambda t: asas_rep({"Peito": (R(0.8 * S(t), 0, 0), (0, 0, 0.12 * S(t))), "Pescoco2": R(-1.5 * S(t + 0.2), 4 * S(t * 0.5), 0), "Cabeca": R(1.5 * S(t), 6 * S(t * 0.5), 0),
                                         **{"Cauda%d" % (k + 1): R(-2, 0, 4 * S(t - 0.1 * k)) for k in range(7)}}, 2 * S(t)))
acao("Andar", 2.0, True, lambda t: asas_rep(marcha(t, (0.25, 0.75, 0.0, 0.5), 18, 0.35, 1.5), 3 * S(2 * t)))
acao("Corrida", 1.1, True, lambda t: asas_rep(marcha(t, (0.5, 0.6, 0.0, 0.1), 30, 0.9, 4), 5 * S(2 * t)))
for nome, s in (("VirarEsquerda", 1), ("VirarDireita", -1)):
    acao(nome, 2.0, True, lambda t, s=s: asas_rep({**marcha(t, (0.0, 0.5, 0.5, 0.0), 11, 0.2, 0.8), "Peito": R(0, 0, 6 * s), "Pescoco2": R(0, 0, 10 * s), "Cabeca": R(0, 0, 14 * s)}))
acao("Observar", 4.0, True, lambda t: asas_rep({"Pescoco1": R(-10, 0, 0), "Pescoco3": R(-6, 0, 0), "Cabeca": R(4, 0, 26 * S(t)), **{"Cauda%d" % (k + 1): R(3, 0, 3 * S(t - 0.1 * k)) for k in range(7)}}))
def rugido(t):
    u = ease(t * 3) * ease((1 - t) * 2.5)
    p = {"Peito": R(-4 * u, 0, 0), "Pescoco1": R(-14 * u, 0, 0), "Pescoco3": R(-8 * u, 0, 0), "Cabeca": R(-10 * u + 3 * u * S(t * 6), 0, 0), "Mandibula": R(18 * u, 0, 0),
         **{"Cauda%d" % (k + 1): R(4 * u, 0, 6 * S(t * 2 - 0.1 * k)) for k in range(7)}}
    return asas(p, REP["elev"] + (40 - REP["elev"]) * u, REP["recuo"] * (1 - u) + 15 * u, REP["punho_e"] * (1 - u) - 10 * u, REP["punho_r"] * (1 - u) + 20 * u, REP["dedos"] * (1 - u) + 6 * u)
acao("Rugido", 3.2, False, rugido)
def abrir(u):
    return asas({}, REP["elev"] * (1 - u) + 6 * u, REP["recuo"] * (1 - u), REP["punho_e"] * (1 - u), REP["punho_r"] * (1 - u), REP["dedos"] * (1 - u) + 4 * u)
acao("AbrirAsas", 1.8, False, lambda t: abrir(ease(t)))
acao("RecolherAsas", 1.8, False, lambda t: abrir(ease(1 - t)))
# --- ar
def corpo_voo(t, amp):
    return {"Pelve": (R(1.5 * S(t) * amp, 0, 0), (0, 0, 0.5 * S(t + 0.25) * amp)), "Pescoco1": R(8 + 3 * S(t + 0.1) * amp, 0, 0), "Cabeca": R(-6 - 2 * S(t + 0.2) * amp, 0, 0),
            "Braco_E": R(55, 0, 0), "Braco_D": R(55, 0, 0), "Antebraco_E": R(-60, 0, 0), "Antebraco_D": R(-60, 0, 0),
            "Coxa_E": R(-65, 0, 0), "Coxa_D": R(-65, 0, 0), "Canela_E": R(50, 0, 0), "Canela_D": R(50, 0, 0),
            **{"Cauda%d" % (k + 1): R(1 + 3 * S(t - 0.1 * k) * amp, 0, 3 * S(t * 0.5 - 0.1 * k)) for k in range(7)}}
def voo(t):
    p = corpo_voo(t, 1)
    # umero bate; antebraco e dedos atrasam (onda ao longo da asa) e dobram na subida
    e = 38 * S(t); pe = 22 * S(t - 0.12) - 18 * max(0, C(t - 0.12)); pr = 12 * max(0, S(t - 0.2))
    return asas(p, e, -4 * C(t), pe, pr, 6 * S(t - 0.2))
acao("Voo", 1.5, True, voo)
acao("Planeio", 4.0, True, lambda t: asas(corpo_voo(t, 0.3), 6 + 2 * S(t), -3, -3 + 2 * S(t + 0.15), 0, 3))
for nome, s in (("CurvaAereaEsquerda", 1), ("CurvaAereaDireita", -1)):
    def curva(t, s=s):
        p = corpo_voo(t, 0.3); p["Peito"] = R(0, 22 * s, 0); p["Cabeca"] = R(-6, 0, 12 * s)
        for k in range(7): p["Cauda%d" % (k + 1)] = R(1, 0, -6 * s)
        return asas(p, 6 + 2 * S(t), -3, -3, 0, 3, dif=7 * s)
    acao(nome, 3.0, True, curva)
def decolagem(t):
    ag = ease(t / 0.3) * (1 - ease((t - 0.3) / 0.15)); vo = ease((t - 0.35) / 0.3)
    base = {"Pelve": (R(5 * ag, 0, 0), (0, 0, -2.2 * ag)), "Braco_E": R(14 * ag, 0, 0), "Braco_D": R(14 * ag, 0, 0), "Coxa_E": R(16 * ag, 0, 0), "Coxa_D": R(16 * ag, 0, 0), "Pescoco1": R(8 * ag, 0, 0)}
    cv = corpo_voo(t, 1); p = {}
    for k in set(base) | set(cv):
        a = base.get(k, Matrix.Identity(3)); b = cv.get(k, Matrix.Identity(3))
        ra = a[0] if isinstance(a, tuple) else a; rb = b[0] if isinstance(b, tuple) else b
        la = Vector(a[1]) if isinstance(a, tuple) else Vector(); lb = Vector(b[1]) if isinstance(b, tuple) else Vector()
        q = ra.to_quaternion().slerp(rb.to_quaternion(), vo)
        p[k] = (q.to_matrix(), tuple(la.lerp(lb, vo)))
    ab = ease(t / 0.3); bat = S((t - 0.3) / 0.7 * 2) if t > 0.3 else 0
    e = (1 - vo) * (REP["elev"] + (45 - REP["elev"]) * ab) + vo * 46 * bat
    pe = (1 - vo) * REP["punho_e"] * (1 - ab) + vo * 26 * S((t - 0.3) / 0.7 * 2 - 0.12)
    return asas(p, e, REP["recuo"] * (1 - ab), pe, REP["punho_r"] * (1 - ab), 4 * vo)
acao("Decolagem", 2.6, False, decolagem)
def pouso(t):
    fr = ease(t / 0.45); toque = ease((t - 0.55) / 0.25); rec = ease((t - 0.75) / 0.25)
    p = {"Pelve": (R(-10 * (1 - toque) * fr, 0, 0), (0, 0, -1.2 * toque * (1 - rec))), "Braco_E": R(-18 * (1 - toque) * fr, 0, 0), "Braco_D": R(-18 * (1 - toque) * fr, 0, 0),
         "Coxa_E": R(-10 * (1 - toque) * fr, 0, 0), "Coxa_D": R(-10 * (1 - toque) * fr, 0, 0), "Pescoco1": R(6 * (1 - toque), 0, 0),
         **{"Cauda%d" % (k + 1): R(-6 * (1 - toque), 0, 0) for k in range(7)}}
    e = 32 * fr * (1 - rec) + REP["elev"] * rec
    return asas(p, e, -16 * fr * (1 - rec) + REP["recuo"] * rec, -10 * fr * (1 - rec) + REP["punho_e"] * rec, REP["punho_r"] * rec, 8 * fr * (1 - rec) + REP["dedos"] * rec)
acao("Pouso", 2.2, False, pouso)
print("ACOES", len(ACOES))

# ---------------- material: escamas de basalto (procedural) assado em textura
bpy.context.view_layer.objects.active = mesh
for o in scn.objects: o.select_set(False)
mesh.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003)
bpy.ops.object.mode_set(mode="OBJECT")
mat = bpy.data.materials.new("Basalto"); mat.use_nodes = True; nt = mat.node_tree; N = nt.nodes; L = nt.links
for n in list(N): N.remove(n)
outn = N.new("ShaderNodeOutputMaterial"); bsdf = N.new("ShaderNodeBsdfPrincipled")
tc = N.new("ShaderNodeTexCoord")
vor = N.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 2.5; vor.feature = "F1"
vor2 = N.new("ShaderNodeTexVoronoi"); vor2.inputs["Scale"].default_value = 2.5; vor2.feature = "DISTANCE_TO_EDGE"
noi = N.new("ShaderNodeTexNoise"); noi.inputs["Scale"].default_value = 0.08; noi.inputs["Detail"].default_value = 6
L.new(tc.outputs["Object"], vor.inputs["Vector"]); L.new(tc.outputs["Object"], vor2.inputs["Vector"]); L.new(tc.outputs["Object"], noi.inputs["Vector"])
ramp = N.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].color = PADROES[0][1] + (1,); ramp.color_ramp.elements[1].color = PADROES[0][2] + (1,)
mixf = N.new("ShaderNodeMath"); mixf.operation = "MULTIPLY_ADD"
L.new(vor.outputs["Color"], mixf.inputs[0]); mixf.inputs[1].default_value = 0.0
sep = N.new("ShaderNodeSeparateColor"); L.new(vor.outputs["Color"], sep.inputs[0])
add = N.new("ShaderNodeMath"); add.operation = "ADD"; L.new(sep.outputs[0], add.inputs[0]); L.new(noi.outputs["Fac"], add.inputs[1])
mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 0.55; L.new(add.outputs[0], mul.inputs[0])
L.new(mul.outputs[0], ramp.inputs["Fac"])
# frisos entre escamas mais escuros
edge = N.new("ShaderNodeMapRange"); edge.inputs["From Min"].default_value = 0.0; edge.inputs["From Max"].default_value = 0.12
L.new(vor2.outputs["Distance"], edge.inputs["Value"])
mixc = N.new("ShaderNodeMix"); mixc.data_type = "RGBA"; mixc.inputs["B"].default_value = (0.02, 0.02, 0.022, 1)
L.new(edge.outputs["Result"], mixc.inputs["Factor"]); L.new(ramp.outputs["Color"], mixc.inputs["B"])
mixc.inputs["A"].default_value = (0.02, 0.02, 0.022, 1)
L.new(mixc.outputs["Result"], bsdf.inputs["Base Color"])
bsdf.inputs["Roughness"].default_value = 0.82
bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.6; bump.inputs["Distance"].default_value = 0.25
L.new(edge.outputs["Result"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
L.new(bsdf.outputs["BSDF"], outn.inputs["Surface"])
mesh.data.materials.clear(); mesh.data.materials.append(mat)
# couro da membrana: cinza-escuro liso com variacao suave e nervuras discretas
mat2 = bpy.data.materials.new("Couro"); mat2.use_nodes = True; N2 = mat2.node_tree.nodes; L2 = mat2.node_tree.links
b2 = N2["Principled BSDF"]; tc2 = N2.new("ShaderNodeTexCoord"); nz = N2.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 4
L2.new(tc2.outputs["Object"], nz.inputs["Vector"])
r2 = N2.new("ShaderNodeValToRGB"); r2.color_ramp.elements[0].color = PADROES[0][3] + (1,); r2.color_ramp.elements[1].color = PADROES[0][4] + (1,)
L2.new(nz.outputs["Fac"], r2.inputs["Fac"]); L2.new(r2.outputs["Color"], b2.inputs["Base Color"]); b2.inputs["Roughness"].default_value = 0.7
wv = N2.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 0.6; wv.inputs["Distortion"].default_value = 6
L2.new(tc2.outputs["Object"], wv.inputs["Vector"])
bp2 = N2.new("ShaderNodeBump"); bp2.inputs["Strength"].default_value = 0.25; L2.new(wv.outputs["Fac"], bp2.inputs["Height"]); L2.new(bp2.outputs["Normal"], b2.inputs["Normal"])
mesh.data.materials.append(mat2)
for poly in mesh.data.polygons:
    if all(i in ASAV for i in poly.vertices): poly.material_index = 1
# assar
scn.render.engine = "CYCLES"; scn.cycles.samples = 4; scn.cycles.device = "CPU"
def assar(tipo, nome, cor):
    img = bpy.data.images.new(nome, 2048, 2048, alpha=False); img.colorspace_settings.name = cor
    tn = N.new("ShaderNodeTexImage"); tn.image = img; N.active = tn
    for n in N: n.select = False
    tn.select = True
    # mesma imagem ativa no material de couro para assar as duas regioes no mesmo atlas
    t2 = N2.new("ShaderNodeTexImage"); t2.image = img; N2.active = t2
    for n in N2: n.select = False
    t2.select = True
    if tipo == "DIFFUSE":
        bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4)
    else:
        bpy.ops.object.bake(type="NORMAL", margin=4)
    img.filepath_raw = os.path.join(DEST, nome + ".png"); img.file_format = "PNG"; img.save()
    return tn
tnor = assar("NORMAL", NOME + "_Normal", "Non-Color")
# os outros dois padroes: so a cor muda (mesma malha, UV, rig e animacoes)
for pad in PADROES[1:]:
    ramp.color_ramp.elements[0].color = pad[1] + (1,); ramp.color_ramp.elements[1].color = pad[2] + (1,)
    r2.color_ramp.elements[0].color = pad[3] + (1,); r2.color_ramp.elements[1].color = pad[4] + (1,)
    assar("DIFFUSE", NOME + "_Cor_" + pad[0], "sRGB")
pad = PADROES[0]
ramp.color_ramp.elements[0].color = pad[1] + (1,); ramp.color_ramp.elements[1].color = pad[2] + (1,)
r2.color_ramp.elements[0].color = pad[3] + (1,); r2.color_ramp.elements[1].color = pad[4] + (1,)
tcor = assar("DIFFUSE", NOME + "_Cor_" + pad[0], "sRGB")
# material final para exportacao: imagens assadas
for n in list(N):
    if n not in (tcor, tnor): N.remove(n)
outn = N.new("ShaderNodeOutputMaterial"); bsdf = N.new("ShaderNodeBsdfPrincipled"); nm = N.new("ShaderNodeNormalMap")
L.new(tcor.outputs["Color"], bsdf.inputs["Base Color"]); L.new(tnor.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Roughness"].default_value = 0.82; L.new(bsdf.outputs["BSDF"], outn.inputs["Surface"])
# um unico material com o atlas assado (menos materiais no Roblox)
for poly in mesh.data.polygons: poly.material_index = 0
mesh.data.materials.pop(index=1)

# ---------------- previas renderizadas de poses-chave (EEVEE)
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 960; scn.render.resolution_y = 600
sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 3.2; so = bpy.data.objects.new("Sol", sun); scn.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(35))
scn.world = bpy.data.worlds.new("W"); scn.world.use_nodes = True; scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.58, 0.68, 1)
bpy.ops.mesh.primitive_plane_add(size=500, location=(0, 10, 0)); chao = bpy.context.active_object
cm = bpy.data.materials.new("Chao"); cm.use_nodes = True; cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.25, 0.32, 0.2, 1); chao.data.materials.append(cm)
bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=5.2, location=(16, -20, 2.6)); hum = bpy.context.active_object
cam = bpy.data.cameras.new("Cam"); co = bpy.data.objects.new("Cam", cam); scn.collection.objects.link(co); scn.camera = co; cam.lens = 35
def foto(nome, acao_nome, t, loc, alvo, voar=0):
    act = ACOES[acao_nome]; arm.animation_data.action = act
    fr = 1 + int(t * (act.frame_range[1] - 1)); scn.frame_set(fr)
    arm.location = (0, 0, voar)
    co.location = loc; co.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = os.path.join(OUT, nome + "_" + FORMA + ".png"); bpy.ops.render.render(write_still=True)
    arm.location = (0, 0, 0); arm.animation_data.action = None
foto("p_repouso_34", "Repouso", 0.0, (70, -95, 42), (0, 2, 16))
foto("p_repouso_lateral", "Repouso", 0.0, (115, 2, 22), (0, 8, 15))
foto("p_andar", "Andar", 0.375, (115, -10, 20), (0, 6, 14))
foto("p_rugido", "Rugido", 0.55, (60, -80, 36), (0, -10, 20))
foto("p_voo_cima", "Voo", 0.25, (60, -90, 85), (0, 4, 40), voar=30)
foto("p_voo_baixo", "Voo", 0.75, (60, -90, 85), (0, 4, 40), voar=30)
foto("p_planeio_frente", "Planeio", 0.0, (0, -120, 50), (0, 0, 40), voar=30)

# ---------------- exportar (sem chao/camera/luz/cilindro)
for o in (chao, hum, co, so): bpy.data.objects.remove(o, do_unlink=True)
arm.animation_data.action = None
mesh.name = NOME; arm.name = NOME + "_Rig"  # nome do MeshPart no Roblox = nome da forma
for o in scn.objects: o.select_set(False)
arm.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=os.path.join(DEST, NOME + ".glb"), export_format="GLB", use_selection=True,
                          export_animations=True, export_animation_mode="ACTIONS", export_skins=True, export_yup=True, export_apply=False)
bpy.ops.export_scene.fbx(filepath=os.path.join(DEST, NOME + ".fbx"), use_selection=True, object_types={"ARMATURE", "MESH"},
                         add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False, path_mode="COPY", embed_textures=True,
                         axis_forward="-Z", axis_up="Y")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DEST, NOME + ".blend"))
print("EXPORTADO")


