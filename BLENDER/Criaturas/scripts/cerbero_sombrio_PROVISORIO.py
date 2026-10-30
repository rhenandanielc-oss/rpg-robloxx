# Cerbero Sombrio (Terras Corrompidas). OFICIAL: canino quadrupede musculoso, TRES cabecas, pelagem escura, 12-16 ate os ombros (usado ~14),
# sela atras dos tres pescocos; cabecas podem reagir a inimigos diferentes (uma criatura). 1 BU = 1 stud; frente -Y, cima +Z, esquerda +X.
# V2: cada pescoco/cabeca e um objeto proprio com pesos restritos aos seus ossos (cabecas nao se puxam entre si).
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix, Quaternion
OUT = sys.argv[sys.argv.index("--") + 1]; DEST = sys.argv[sys.argv.index("--") + 2]
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
def skin_obj(name, pts, edges, radii, sub=2):
    me = bpy.data.meshes.new(name); me.from_pydata(pts, edges, [])
    ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    sk = ob.modifiers.new("Skin", "SKIN"); sk.use_smooth_shade = True
    ss = ob.modifiers.new("Sub", "SUBSURF"); ss.levels = sub
    for i, r in enumerate(radii):
        v = me.skin_vertices[0].data[i]; v.radius = (r[0], r[1]) if isinstance(r, tuple) else (r, r)
    me.skin_vertices[0].data[0].use_root = True
    return ob
def cadeia(name, chain, radii, sub=2):
    return skin_obj(name, [tuple(p) for p in chain], [(i, i + 1) for i in range(len(chain) - 1)], radii, sub)
def tubo(name, path, radii, achatar=None, lados=8):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []; n = len(path)
    for k in range(n):
        p = Vector(path[k]); d = (Vector(path[min(k + 1, n - 1)]) - Vector(path[max(k - 1, 0)])).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0)); u = d.cross(up).normalized(); v = d.cross(u).normalized()
        rings.append([bm.verts.new(p + u * math.cos(a / lados * 2 * math.pi) * radii[k] + v * math.sin(a / lados * 2 * math.pi) * radii[k] * (achatar or 1)) for a in range(lados)])
    for k in range(n - 1):
        for a in range(lados):
            b = (a + 1) % lados; bm.faces.new((rings[k][a], rings[k][b], rings[k + 1][b], rings[k + 1][a]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1]); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    for f in me.polygons: f.use_smooth = True
    m = ob.modifiers.new("Sub", "SUBSURF"); m.levels = 1
    return ob
# espinha: cauda (0-3) -> pelve 4 -> cintura 5 (recolhida) -> peito 6 (fundo) -> peito frontal 7. Cernelha ~10.2 + 3.7 = 13.9
spine = [(0, 15.2, 5.6), (0, 13.6, 7.4), (0, 11.6, 9.0), (0, 9.6, 10.2), (0, 7.4, 10.6), (0, 3.2, 10.9), (0, -1.2, 10.2), (0, -3.8, 10.5)]
srad = [0.55, 0.95, 1.05, 1.0, (2.6, 2.8), (2.05, 2.2), (3.0, 3.7), (2.7, 3.0)]
pts = list(spine); edges = [(i, i + 1) for i in range(len(spine) - 1)]; rad = list(srad)
I_PEITO, I_PELVE = 6, 4
LEG = {}
for s, lado in ((1, "E"), (-1, "D")):
    ch = [(s * 2.4, -2.2, 9.0), (s * 2.6, -1.8, 5.6), (s * 2.5, -2.4, 1.7), (s * 2.5, -2.9, 0.55), (s * 2.5, -3.8, 0.42)]
    rr = [(1.9, 2.3), (0.95, 1.05), (0.55, 0.55), (0.8, 0.5), (0.72, 0.42)]
    prev = I_PEITO
    for p, r in zip(ch, rr): pts.append(p); rad.append(r); edges.append((prev, len(pts) - 1)); prev = len(pts) - 1
    LEG["Dianteira_" + lado] = ch
    ch = [(s * 2.4, 7.6, 9.2), (s * 2.7, 5.9, 5.9), (s * 2.6, 8.5, 3.0), (s * 2.6, 8.0, 0.55), (s * 2.6, 7.1, 0.42)]
    rr = [(2.2, 2.6), (1.2, 1.35), (0.55, 0.55), (0.8, 0.5), (0.72, 0.42)]
    prev = I_PELVE
    for p, r in zip(ch, rr): pts.append(p); rad.append(r); edges.append((prev, len(pts) - 1)); prev = len(pts) - 1
    LEG["Traseira_" + lado] = ch
corpo = skin_obj("Corpo", pts, edges, rad)
OBJ_REG = [(corpo, "CORPO")]
for nome, ch in LEG.items():  # garras presas a frente da pata
    px, py, pz = ch[-1]
    for dx in (-0.32, 0, 0.32):
        a = (px + dx, py + 0.15, 0.38); bb = (px + dx * 1.15, py - 0.5, 0.04)
        OBJ_REG.append((tubo("Garra", [a, tuple(Vector(a).lerp(Vector(bb), 0.5)), bb], [0.15, 0.1, 0.02]), "CORPO"))
# tres pescocos/cabecas: centro mais alto, laterais abertas e um pouco menores
CAB = {}
for nome, ang, esc, dx in (("C", 0, 1.0, 0.0), ("E", 38, 0.92, 1.5), ("D", -38, 0.92, -1.5)):
    a = math.radians(ang); dv = Vector((math.sin(a), -math.cos(a), 0)); z = Vector((0, 0, 1))
    base = Vector((dx, -3.6, 10.8))
    n1 = base + dv * 1.6 + z * 2.0 * esc; n2 = n1 + dv * 1.4 + z * 1.5 * esc
    sk = n2 + dv * 1.2 + z * 0.5; st = sk + dv * 0.85 - z * 0.15; mz = st + dv * 0.85 - z * 0.2; ns = mz + dv * 0.6 - z * 0.05
    chain = [base, n1, n2, sk, st, mz, ns]
    rr = [(2.0 * esc, 2.3 * esc), (1.7 * esc, 1.9 * esc), (1.35 * esc, 1.45 * esc), (1.6 * esc, 1.45 * esc), (1.15 * esc, 1.05 * esc), (0.78 * esc, 0.72 * esc), (0.55 * esc, 0.5 * esc)]
    CAB[nome] = chain
    reg = "CAB_" + nome
    OBJ_REG.append((cadeia("Pescoco_" + nome, chain, rr), reg))
    # mandibula
    OBJ_REG.append((tubo("Mandibula", [tuple(sk - z * 0.55 + dv * 0.2), tuple(mz - z * 0.5), tuple(ns - z * 0.45)], [0.62 * esc, 0.45 * esc, 0.26 * esc], achatar=0.6), reg))
    # orelhas triangulares de base larga, levemente abertas para tras
    lat = dv.cross(z).normalized()
    for s in (-1, 1):
        b = sk + lat * s * 0.8 * esc + z * 1.0 * esc - dv * 0.2
        tip = b + z * 1.7 * esc - dv * 0.5 + lat * s * 0.3
        OBJ_REG.append((tubo("Orelha", [tuple(b), tuple(b.lerp(tip, 0.5)), tuple(tip)], [0.72 * esc, 0.42 * esc, 0.03], achatar=0.35), reg))
    # olhos escuros pequenos (sem brilho magico)
    for s in (-1, 1):
        e = st + lat * s * 0.62 * esc + z * 0.38 * esc - dv * 0.05
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.17 * esc, location=e, segments=10, ring_count=6); OBJ_REG.append((bpy.context.active_object, reg))
objs = [o for o, _ in OBJ_REG]
for o in objs:
    bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.convert(target="MESH")
for o, reg in OBJ_REG:
    g = o.vertex_groups.new(name="REG_" + reg); g.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
bpy.ops.object.select_all(action="DESELECT")
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active = corpo; bpy.ops.object.join()
mesh = bpy.context.view_layer.objects.active; mesh.name = "Cerbero_Sombrio"
tris = sum(len(p.vertices) - 2 for p in mesh.data.polygons)
if tris > 16000:
    dec = mesh.modifiers.new("Dec", "DECIMATE"); dec.ratio = 15500 / tris; bpy.ops.object.modifier_apply(modifier="Dec")
print("TRIS_FINAL", sum(len(p.vertices) - 2 for p in mesh.data.polygons))
sp = [Vector(p) for p in spine]
arm_d = bpy.data.armatures.new("Esqueleto"); arm = bpy.data.objects.new("Cerbero_Rig", arm_d); scn.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT"); EB = arm_d.edit_bones
def osso(nome, h, t, pai=None, deform=True):
    b = EB.new(nome); b.head = Vector(h); b.tail = Vector(t); b.roll = 0
    if pai: b.parent = EB[pai]
    b.use_deform = deform
osso("Raiz", (0, 0, 0), (0, 0, 2), None, False)
osso("Pelve", sp[4], sp[5], "Raiz"); osso("Peito", sp[5], sp[7], "Pelve")
prev = "Pelve"
for k in range(4):
    n = "Cauda%d" % (k + 1); osso(n, sp[4 - k], sp[3 - k], prev); prev = n
for nome, c in CAB.items():
    osso("Pescoco1_" + nome, c[0], c[1], "Peito"); osso("Pescoco2_" + nome, c[1], c[2], "Pescoco1_" + nome)
    osso("Cabeca_" + nome, c[2], c[5], "Pescoco2_" + nome)
    osso("Mandibula_" + nome, c[3] + Vector((0, 0, -0.7)), c[6] + Vector((0, 0, -0.5)), "Cabeca_" + nome)
for nome, ch in LEG.items():
    c = [Vector(p) for p in ch]; pai = "Peito" if nome.startswith("Dianteira") else "Pelve"; lado = nome[-1]
    pre = "Braco" if nome.startswith("Dianteira") else "Coxa"
    osso(pre + "_" + lado, c[0], c[1], pai); osso(pre + "B_" + lado, c[1], c[2], pre + "_" + lado); osso(pre + "Pe_" + lado, c[2], c[4], pre + "B_" + lado)
bpy.ops.object.mode_set(mode="OBJECT")
print("OSSOS", len(arm_d.bones))
segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm_d.bones if b.use_deform}
def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
CAB_OSSOS = {c: {"Peito", "Pescoco1_" + c, "Pescoco2_" + c, "Cabeca_" + c, "Mandibula_" + c} for c in CAB}
CORPO_OSSOS = {n for n in segs if not any(n.startswith(p) for p in ("Pescoco2_", "Cabeca_", "Mandibula_"))}
idx_reg = {g.index: g.name[4:] for g in mesh.vertex_groups if g.name.startswith("REG_")}
vgs = {n: mesh.vertex_groups.new(name=n) for n in segs}
for v in mesh.data.vertices:
    reg = next((idx_reg[g.group] for g in v.groups if g.group in idx_reg and g.weight > 0.5), "CORPO")
    perm = CAB_OSSOS[reg[4:]] if reg.startswith("CAB_") else CORPO_OSSOS
    ws = sorted(((1.0 / (dist_seg(v.co, *segs[n]) ** 4 + 0.02), n) for n in perm), reverse=True)[:4]
    if reg.startswith("CAB_"):  # mandibula so move a parte de baixo do focinho
        ws = [(w, n) for w, n in ws if not (n.startswith("Mandibula_") and v.co.z > segs[n][0].z + 0.35)] or ws
    tot = sum(w for w, _ in ws)
    for w, n in ws:
        if w / tot > 0.02: vgs[n].add([v.index], w / tot, "REPLACE")
for g in [g for g in mesh.vertex_groups if g.name.startswith("REG_")]: mesh.vertex_groups.remove(g)
m = mesh.modifiers.new("Armature", "ARMATURE"); m.object = arm; mesh.parent = arm
PB = arm.pose.bones
for pb in PB: pb.rotation_mode = "QUATERNION"
def R(ax, ay, az): return Matrix.Rotation(math.radians(az), 3, "Z") @ Matrix.Rotation(math.radians(ay), 3, "Y") @ Matrix.Rotation(math.radians(ax), 3, "X")
def aplicar(pose):
    for pb in PB: pb.rotation_quaternion = Quaternion(); pb.location = Vector()
    for nome, val in pose.items():
        pb = PB[nome]; M3 = pb.bone.matrix_local.to_3x3(); rot, loc = val if isinstance(val, tuple) else (val, None)
        pb.rotation_quaternion = (M3.inverted() @ rot @ M3).to_quaternion()
        if loc is not None: pb.location = M3.inverted() @ Vector(loc)
def S(x): return math.sin(2 * math.pi * x)
def C(x): return math.cos(2 * math.pi * x)
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
CABS = ("C", "E", "D")
def marcha(t, fases, A, bob, pitch):
    p = {}
    for (a, b), f in zip((("Braco_E", "BracoB_E"), ("Braco_D", "BracoB_D"), ("Coxa_E", "CoxaB_E"), ("Coxa_D", "CoxaB_D")), fases):
        x = t - f; lift = max(0, S(x + 0.25)); tras = a.startswith("Coxa")
        p[a] = R(-A * S(x), 0, 0); p[b] = R((-22 if tras else 26) * lift, 0, 0)
    p["Pelve"] = (R(pitch * S(t + 0.25), 0, 1.5 * S(t)), (0, 0, bob * (0.5 - 0.5 * C(2 * t))))
    for k, c in enumerate(CABS): p["Pescoco1_" + c] = R(-pitch * 0.6 * S(t + 0.25 + 0.07 * k), 0, 0)
    for k in range(4): p["Cauda%d" % (k + 1)] = R(-4, 0, 6 * S(t - 0.1 * k))
    return p
FPS = 30; scn.render.fps = FPS; ACOES = {}
def acao(nome, dur, loop, f):
    act = bpy.data.actions.new(nome); arm.animation_data_create(); arm.animation_data.action = act
    nfr = max(2, int(dur * FPS))
    for fr in range(nfr + 1):
        aplicar(f(fr / nfr))
        for pb in PB: pb.keyframe_insert("rotation_quaternion", frame=fr + 1); pb.keyframe_insert("location", frame=fr + 1)
    act.use_fake_user = True; ACOES[nome] = act
    tr = arm.animation_data.nla_tracks.new(); tr.name = nome; tr.strips.new(nome, 1, act); arm.animation_data.action = None
def respira(t):
    p = {"Peito": (R(0.8 * S(t), 0, 0), (0, 0, 0.08 * S(t)))}
    for k, c in enumerate(CABS): p["Cabeca_" + c] = R(1.5 * S(t + 0.3 * k), 6 * S(t * 0.5 + 0.33 * k), 0)
    for k in range(4): p["Cauda%d" % (k + 1)] = R(-4, 0, 4 * S(t * 0.5 - 0.1 * k))
    return p
acao("Repouso", 4.5, True, respira)
acao("Andar", 1.15, True, lambda t: marcha(t, (0.25, 0.75, 0.0, 0.5), 20, 0.12, 1.2))
acao("Trote", 0.7, True, lambda t: marcha(t, (0.0, 0.5, 0.5, 0.0), 28, 0.22, 2))
acao("Corrida", 0.5, True, lambda t: marcha(t, (0.5, 0.6, 0.0, 0.1), 40, 0.45, 5))
for nome, s in (("VirarEsquerda", 1), ("VirarDireita", -1)):
    acao(nome, 1.15, True, lambda t, s=s: {**marcha(t, (0.0, 0.5, 0.5, 0.0), 12, 0.06, 0.6), "Peito": R(0, 0, 6 * s), **{"Pescoco1_" + c: R(0, 0, 10 * s) for c in CABS}})
# cabecas independentes: cada uma vigia uma direcao (identidade oficial do Cerbero)
acao("Observar", 4.0, True, lambda t: {**respira(t), "Pescoco1_C": R(-8, 0, 0), "Cabeca_C": R(4, 0, 12 * S(t)), "Cabeca_E": R(2, 0, 28 + 10 * S(t + 0.3)), "Cabeca_D": R(2, 0, -28 - 10 * S(t + 0.6))})
def rugido(t):
    u = ease(t / 0.3) * (1 - ease((t - 0.7) / 0.3)); p = respira(t)
    for k, c in enumerate(CABS):
        uu = ease((t - 0.06 * k) / 0.3) * (1 - ease((t - 0.7) / 0.3))
        p["Pescoco1_" + c] = R(-10 * uu, 0, 0); p["Cabeca_" + c] = R(-14 * uu, 0, 0); p["Mandibula_" + c] = R(30 * uu, 0, 0)
    p["Peito"] = (R(-4 * u, 0, 0), (0, 0, 0.2 * u))
    return p
acao("RugidoInfernal", 3.0, False, rugido)
def mordidas(t):  # Mordidas Triplices: as tres cabecas mordem em sequencia
    p = respira(t)
    for k, c in enumerate(("C", "E", "D")):
        x = (t - 0.22 * k) / 0.35; u = math.sin(math.pi * max(0, min(1, x)))
        p["Pescoco1_" + c] = R(6 * u, 0, 0); p["Pescoco2_" + c] = R(-8 * u, 0, 0); p["Cabeca_" + c] = R(8 * u, 0, 0); p["Mandibula_" + c] = R(28 * u * (1 if x < 0.5 else 0.2), 0, 0)
    return p
acao("MordidasTriplices", 1.5, False, mordidas)
def investida(t):
    ag = ease(t / 0.25) * (1 - ease((t - 0.25) / 0.1)); sl = math.sin(math.pi * max(0, min(1, (t - 0.25) / 0.5)))
    p = marcha(t * 2, (0.5, 0.6, 0.0, 0.1), 40 * sl, 0.3 * sl, 4 * sl)
    p["Pelve"] = (R(4 * ag - 6 * sl, 0, 0), (0, -2.5 * sl, -1.0 * ag + 0.4 * sl))
    for c in CABS: p["Pescoco1_" + c] = R(8 * sl, 0, 0)
    return p
acao("InvestidaSombria", 1.4, False, investida)
def furia(t):
    p = marcha(t * 1.5, (0.0, 0.5, 0.5, 0.0), 10, 0.1, 1)
    for k, c in enumerate(CABS):
        x = t * 3 - k * 0.33; u = max(0, S(x))
        p["Pescoco1_" + c] = R(6 * u, 0, (14 if c == "E" else (-14 if c == "D" else 0)) * u); p["Cabeca_" + c] = R(8 * u, 0, 0); p["Mandibula_" + c] = R(26 * u, 0, 0)
    return p
acao("FuriaDasTresCabecas", 3.0, True, furia)
print("ACOES", len(ACOES))
PAD = [("Negro_Carbonizado", (0.012, 0.011, 0.012), (0.10, 0.09, 0.09)), ("Cinza_Sepulcral", (0.08, 0.08, 0.085), (0.36, 0.36, 0.37)), ("Vermelho_Sombrio", (0.05, 0.008, 0.008), (0.30, 0.05, 0.04))]
bpy.context.view_layer.objects.active = mesh
for o in scn.objects: o.select_set(False)
mesh.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003); bpy.ops.object.mode_set(mode="OBJECT")
mat = bpy.data.materials.new("Pelagem"); mat.use_nodes = True; Nn = mat.node_tree.nodes; Lk = mat.node_tree.links
b = Nn["Principled BSDF"]; tc = Nn.new("ShaderNodeTexCoord")
# pelagem: manchas suaves + gradiente (dorso mais claro, patas/focinho mais escuros) + grao fino de pelo no relevo
nz = Nn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.5; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.6; Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
sx = Nn.new("ShaderNodeSeparateXYZ"); Lk.new(tc.outputs["Object"], sx.inputs[0])
mr = Nn.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 2.0; mr.inputs["From Max"].default_value = 13.0; Lk.new(sx.outputs["Z"], mr.inputs["Value"])
mu = Nn.new("ShaderNodeMath"); mu.operation = "MULTIPLY_ADD"; Lk.new(nz.outputs["Fac"], mu.inputs[0]); mu.inputs[1].default_value = 0.7; Lk.new(mr.outputs["Result"], mu.inputs[2])
mu2 = Nn.new("ShaderNodeMath"); mu2.operation = "MULTIPLY"; Lk.new(mu.outputs[0], mu2.inputs[0]); mu2.inputs[1].default_value = 0.62
rp = Nn.new("ShaderNodeValToRGB"); Lk.new(mu2.outputs[0], rp.inputs["Fac"]); Lk.new(rp.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.88
fp = Nn.new("ShaderNodeTexNoise"); fp.inputs["Scale"].default_value = 22; fp.inputs["Detail"].default_value = 3; Lk.new(tc.outputs["Object"], fp.inputs["Vector"])
bp = Nn.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.22; bp.inputs["Distance"].default_value = 0.04; Lk.new(fp.outputs["Fac"], bp.inputs["Height"]); Lk.new(bp.outputs["Normal"], b.inputs["Normal"])
mesh.data.materials.clear(); mesh.data.materials.append(mat)
scn.render.engine = "CYCLES"; scn.cycles.samples = 4
def assar(tipo, nome, cs):
    img = bpy.data.images.new(nome, 2048, 2048, alpha=False); img.colorspace_settings.name = cs
    tn = Nn.new("ShaderNodeTexImage"); tn.image = img
    for n in Nn: n.select = False
    tn.select = True; Nn.active = tn
    if tipo == "DIFFUSE": bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4)
    else: bpy.ops.object.bake(type="NORMAL", margin=4)
    img.filepath_raw = os.path.join(DEST, nome + ".png"); img.file_format = "PNG"; img.save(); return tn
def cores(pd): rp.color_ramp.elements[0].color = pd[1] + (1,); rp.color_ramp.elements[1].color = pd[2] + (1,)
cores(PAD[0]); tnor = assar("NORMAL", "Cerbero_Sombrio_Normal", "Non-Color")
for pd in PAD[1:]: cores(pd); assar("DIFFUSE", "Cerbero_Sombrio_Cor_" + pd[0], "sRGB")
cores(PAD[0]); tcor = assar("DIFFUSE", "Cerbero_Sombrio_Cor_" + PAD[0][0], "sRGB")
for n in list(Nn):
    if n not in (tcor, tnor): Nn.remove(n)
o_ = Nn.new("ShaderNodeOutputMaterial"); b_ = Nn.new("ShaderNodeBsdfPrincipled"); nm = Nn.new("ShaderNodeNormalMap")
Lk.new(tcor.outputs["Color"], b_.inputs["Base Color"]); Lk.new(tnor.outputs["Color"], nm.inputs["Color"]); Lk.new(nm.outputs["Normal"], b_.inputs["Normal"]); b_.inputs["Roughness"].default_value = 0.85; Lk.new(b_.outputs["BSDF"], o_.inputs["Surface"])
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 960; scn.render.resolution_y = 600
sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 3.4; so = bpy.data.objects.new("Sol", sun); scn.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(35))
scn.world = bpy.data.worlds.new("W"); scn.world.use_nodes = True; scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.40, 0.44, 1)
bpy.ops.mesh.primitive_plane_add(size=200); ch = bpy.context.active_object
cm = bpy.data.materials.new("Chao"); cm.use_nodes = True; cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.22, 0.2, 0.2, 1); ch.data.materials.append(cm)
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=4.2, location=(8, -10, 2.1)); h1 = bpy.context.active_object
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(8, -10, 4.7)); h2 = bpy.context.active_object
cam = bpy.data.cameras.new("Cam"); co = bpy.data.objects.new("Cam", cam); scn.collection.objects.link(co); scn.camera = co; cam.lens = 35
def foto(nome, an, t, loc, alvo):
    act = ACOES[an]; arm.animation_data.action = act; scn.frame_set(1 + int(t * (act.frame_range[1] - 1)))
    co.location = loc; co.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = os.path.join(OUT, "Cerbero_%s.png" % nome); bpy.ops.render.render(write_still=True); arm.animation_data.action = None
foto("34", "Repouso", 0, (24, -30, 18), (0, 0, 8)); foto("frente", "Observar", 0.25, (0, -34, 12), (0, 0, 10)); foto("lateral", "Andar", 0.25, (34, 2, 9), (0, 2, 8))
foto("rugido", "RugidoInfernal", 0.5, (24, -30, 18), (0, -2, 10)); foto("mordidas", "MordidasTriplices", 0.3, (24, -30, 18), (0, -2, 10))
for o in (ch, h1, h2, co, so): bpy.data.objects.remove(o, do_unlink=True)
for o in scn.objects: o.select_set(False)
arm.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=os.path.join(DEST, "Cerbero_Sombrio.glb"), export_format="GLB", use_selection=True, export_animations=True, export_animation_mode="ACTIONS", export_skins=True, export_yup=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(DEST, "Cerbero_Sombrio.fbx"), use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=True,
                         bake_anim_use_nla_strips=False, path_mode="COPY", embed_textures=True, axis_forward="-Z", axis_up="Y")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DEST, "Cerbero_Sombrio.blend"))
d = mesh.dimensions; print("DIM %.1f x %.1f x %.1f" % (d.x, d.y, d.z)); print("EXPORTADO")
