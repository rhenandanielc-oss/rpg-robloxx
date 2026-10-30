# Wyvern (Montanhas Altas) - geometria, rig, animacoes, textura assada e exportacao. 1 BU = 1 stud.
# OFICIAL: 9-13 ate os ombros (usado 11), envergadura 30-42 (usada 38), ferrao na cauda, mais agil/rapida que Dragoes.
# PROPOSTA do documento (seguida, marcada como proposta): corpo leve, duas patas traseiras, membros dianteiros nas asas,
# apoio em solo compativel (aqui: punhos das asas no chao, como morcegos/pterossauros).
import bpy, bmesh, math, sys, os, json, itertools
from mathutils import Vector, Matrix, Quaternion

OUT = sys.argv[sys.argv.index("--") + 1]; DEST = sys.argv[sys.argv.index("--") + 2]
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

def skin_obj(name, pts, edges, radii, sub=2):
    me = bpy.data.meshes.new(name); me.from_pydata(pts, edges, [])
    ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    sk = ob.modifiers.new("Skin", "SKIN"); sk.use_smooth_shade = True
    ss = ob.modifiers.new("Sub", "SUBSURF"); ss.levels = sub; ss.render_levels = sub
    for i, r in enumerate(radii):
        v = me.skin_vertices[0].data[i]; v.radius = (r[0], r[1]) if isinstance(r, tuple) else (r, r)
    me.skin_vertices[0].data[0].use_root = True
    return ob
def tubo(name, path, radii, achatar=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []; n = len(path)
    for k in range(n):
        p = Vector(path[k]); d = (Vector(path[min(k + 1, n - 1)]) - Vector(path[max(k - 1, 0)])).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0)); u = d.cross(up).normalized(); v = d.cross(u).normalized()
        rings.append([bm.verts.new(p + u * math.cos(a / 10 * 2 * math.pi) * radii[k] + v * math.sin(a / 10 * 2 * math.pi) * radii[k] * (achatar or 1)) for a in range(10)])
    for k in range(n - 1):
        for a in range(10):
            b = (a + 1) % 10; bm.faces.new((rings[k][a], rings[k][b], rings[k + 1][b], rings[k + 1][a]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1]); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    for f in me.polygons: f.use_smooth = True
    return ob
def arco(a, b, alt, n=8):
    a, b = Vector(a), Vector(b); return [tuple(a.lerp(b, t) + Vector((0, 0, alt * math.sin(t * math.pi)))) for t in [i / (n - 1) for i in range(n)]]

# ---------- espinha: cauda (0-7) -> pelve 8 -> lombo 9 -> peito 10 -> pescoco 11-14 -> nuca 15 -> cranio 16 -> focinho 17-18
spine = [(0, 34.0, 6.6), (0, 30.0, 7.0), (0, 26.0, 7.5), (0, 22.0, 8.0), (0, 18.0, 8.5), (0, 14.0, 9.0), (0, 10.0, 9.3), (0, 7.5, 9.5),
         (0, 5.5, 9.6), (0, 1.5, 9.0), (0, -3.0, 8.2),
         (0, -5.6, 10.0), (0, -7.6, 12.2), (0, -9.6, 14.0), (0, -11.6, 15.3), (0, -13.4, 15.9), (0, -15.2, 15.8), (0, -17.4, 15.4), (0, -19.6, 15.0)]
srad = [0.3, 0.45, 0.65, 0.9, 1.2, 1.55, 1.95, 2.25,
        (2.6, 2.7), (2.9, 2.85), (3.0, 2.8),
        (2.1, 2.0), 1.75, 1.55, 1.45, (1.5, 1.35), (1.55, 1.25), (1.05, 0.85), (0.72, 0.55)]
pts = list(spine); edges = [(i, i + 1) for i in range(len(spine) - 1)]; rad = list(srad)
I_PELVE = 8
LEG = {}
for s, lado in ((-1, "D"), (1, "E")):
    ch = [(s * 2.6, 6.0, 8.0), (s * 3.0, 4.6, 6.1), (s * 3.2, 3.4, 4.5), (s * 3.1, 7.4, 2.0), (s * 3.1, 6.1, 0.55), (s * 3.1, 3.9, 0.35)]
    rr = [(2.3, 2.6), (1.9, 2.1), (1.35, 1.4), (0.8, 0.8), (0.95, 0.45), (0.85, 0.32)]
    prev = I_PELVE
    for p, r in zip(ch, rr):
        pts.append(p); rad.append(r); edges.append((prev, len(pts) - 1)); prev = len(pts) - 1
    LEG["Traseira_" + lado] = ch
corpo = skin_obj("Corpo", pts, edges, rad)
det = []
cr = Vector(spine[16])
for s in (-1, 1):
    def hp(dx, dy, dz): return tuple(cr + Vector((s * dx, dy, dz)))
    ph = arco(hp(0.7, 0.8, 0.9), hp(1.6, 5.2, 2.2), 0.7, 7); det.append(tubo("Chifre", ph, [0.5 * (1 - i / 7) + 0.04 for i in range(len(ph))]))
    det.append(tubo("Sobrancelha", [hp(1.0, -1.2, 0.5), hp(1.2, 0.2, 0.95), hp(1.1, 1.4, 0.9)], [0.22, 0.28, 0.14]))
    ch = LEG["Traseira_" + ("E" if s > 0 else "D")]; px, py, pz = ch[-1]
    for dx in (-0.45, 0, 0.45):
        a = (px + dx, py - 0.4, 0.4); b = (px + dx * 1.2, py - 1.5, 0.06)
        det.append(tubo("Garra", [a, tuple(Vector(a).lerp(Vector(b), 0.5) + Vector((0, -0.1, 0.1))), b], [0.2, 0.12, 0.02]))
# espinhos dorsais finos (mais leves que as placas do Dragao)
for i in range(15, 1, -1):
    x, y, z = spine[i]; r = srad[i][1] if isinstance(srad[i], tuple) else srad[i]
    if i in (16, 17, 18): continue
    h = 0.45 * r + 0.35; base = (0, y + 0.2, z + r * 0.85); topo = (0, y + 0.9, z + r * 0.85 + h)
    det.append(tubo("Espinho", [base, tuple(Vector(base).lerp(Vector(topo), 0.5)), topo], [0.22 * r + 0.12, 0.13 * r + 0.07, 0.02], achatar=0.4))
# ferrao: lamina curva na ponta da cauda (sem brilho; veneno e biologico, efeitos so em habilidade)
ferrao = [(0, 33.8, 6.6), (0, 35.6, 7.0), (0, 37.0, 7.9), (0, 37.8, 9.1), (0, 37.6, 10.1)]
det.append(tubo("Ferrao", ferrao, [0.55, 0.5, 0.36, 0.2, 0.03], achatar=0.7))
for ob in det:
    m = ob.modifiers.new("Sub", "SUBSURF"); m.levels = 1

# ---------- asas = membros dianteiros (pose aberta)
ASA = {}
def asa(s, lado):
    ombro = Vector((s * 2.5, -3.6, 10.3)); cotov = Vector((s * 6.6, -1.6, 12.8)); punho = Vector((s * 10.6, -4.0, 13.4))
    dedos = [Vector((s * 19.0, -1.8, 13.0)), Vector((s * 18.0, 3.2, 11.4)), Vector((s * 14.6, 7.0, 10.0)), Vector((s * 10.2, 8.6, 9.4))]
    flanco = Vector((s * 2.6, 5.4, 8.6))
    ASA[lado] = {"ombro": tuple(ombro), "cotovelo": tuple(cotov), "punho": tuple(punho), "dedos": [tuple(d) for d in dedos], "flanco": tuple(flanco)}
    arm = [tubo("AsaBraco", [tuple(ombro), tuple(ombro.lerp(cotov, 0.5)), tuple(cotov)], [0.95, 0.8, 0.62]),
           tubo("AsaAntebraco", [tuple(cotov), tuple(cotov.lerp(punho, 0.5)), tuple(punho)], [0.62, 0.52, 0.45])]
    for d in dedos: arm.append(tubo("AsaDedo", [tuple(punho), tuple(punho.lerp(d, 0.5)), tuple(d)], [0.32, 0.18, 0.04]))
    arm.append(tubo("GarraPunho", [tuple(punho), tuple(punho + Vector((s * 0.2, -0.9, 0.7))), tuple(punho + Vector((s * 0.1, -1.4, 0.4)))], [0.26, 0.14, 0.02]))
    cont = [ombro, cotov, punho, dedos[0]]
    for a, b in zip(dedos[:-1], dedos[1:]):
        cont.append(a.lerp(b, 0.5).lerp(punho, 0.24)); cont.append(b)
    cont.append(dedos[-1].lerp(flanco, 0.5).lerp(punho, 0.2)); cont.append(flanco)
    me = bpy.data.meshes.new("Membrana"); bm = bmesh.new(); vs = [bm.verts.new(p) for p in cont]
    for i in range(len(vs)): bm.edges.new((vs[i], vs[(i + 1) % len(vs)]))
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bm.edges[:])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=4, use_grid_fill=True); bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free()
    mob = bpy.data.objects.new("Membrana", me); scn.collection.objects.link(mob)
    so = mob.modifiers.new("Esp", "SOLIDIFY"); so.thickness = 0.09
    for f in me.polygons: f.use_smooth = True
    for o in arm:
        mm = o.modifiers.new("Sub", "SUBSURF"); mm.levels = 1
    for o in arm + [mob]: o["lado"] = lado
    return arm + [mob]
asas = []
for s, lado in ((-1, "D"), (1, "E")): asas += asa(s, lado)
def marcar(o, g):
    vg = o.vertex_groups.new(name=g); vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
for o in [corpo] + det:
    bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.convert(target="MESH"); marcar(o, "REG_CORPO")
for o in asas:
    bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.convert(target="MESH"); marcar(o, "REG_ASA_" + o["lado"])
bpy.ops.object.select_all(action="DESELECT")
for o in [corpo] + det + asas: o.select_set(True)
bpy.context.view_layer.objects.active = corpo; bpy.ops.object.join()
mesh = bpy.context.view_layer.objects.active; mesh.name = "Wyvern"
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.remove_doubles(threshold=0.001); bpy.ops.object.mode_set(mode="OBJECT")
dec = mesh.modifiers.new("Dec", "DECIMATE"); dec.ratio = 0.85; bpy.ops.object.modifier_apply(modifier="Dec")
print("TRIS_FINAL", sum(len(p.vertices) - 2 for p in mesh.data.polygons))

# ---------- armature
sp = [Vector(p) for p in spine]
arm_d = bpy.data.armatures.new("Esqueleto"); arm = bpy.data.objects.new("Wyvern_Rig", arm_d); scn.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT"); EB = arm_d.edit_bones; REGIAO = {}
def osso(nome, h, t, pai=None, reg="CORPO", deform=True):
    b = EB.new(nome); b.head = Vector(h); b.tail = Vector(t); b.roll = 0
    if pai: b.parent = EB[pai]
    b.use_deform = deform; REGIAO[nome] = reg
osso("Raiz", (0, 0, 0), (0, 0, 2), None, "NENHUMA", False)
osso("Pelve", sp[8], sp[9], "Raiz"); osso("Lombo", sp[9], sp[10] + Vector((0, 1.2, 0.3)), "Pelve"); osso("Peito", sp[10] + Vector((0, 1.2, 0.3)), sp[10] + Vector((0, -1.6, 1.0)), "Lombo")
osso("Pescoco1", sp[11], sp[12], "Peito"); osso("Pescoco2", sp[12], sp[13], "Pescoco1"); osso("Pescoco3", sp[13], sp[14], "Pescoco2"); osso("Pescoco4", sp[14], sp[15], "Pescoco3")
osso("Cabeca", sp[15] + Vector((0, 0, 0.35)), sp[17] + Vector((0, 0, 0.4)), "Pescoco4")
osso("Mandibula", sp[15] + Vector((0, -0.8, -0.8)), sp[18] + Vector((0, 0.1, -0.35)), "Cabeca")
prev = "Pelve"
for k in range(7):
    n = "Cauda%d" % (k + 1); osso(n, sp[8 - k] if k == 0 else sp[7 - k + 1], sp[7 - k], prev); prev = n
osso("Ferrao", sp[0], Vector(ferrao[-1]), prev)
for lado in ("E", "D"):
    c = [Vector(p) for p in LEG["Traseira_" + lado]]
    osso("Coxa_" + lado, c[0], c[2], "Pelve"); osso("Canela_" + lado, c[2], c[3], "Coxa_" + lado); osso("Pe_" + lado, c[3], c[4], "Canela_" + lado); osso("DedosPe_" + lado, c[4], c[5], "Pe_" + lado)
    a = ASA[lado]
    osso("AsaUmero_" + lado, a["ombro"], a["cotovelo"], "Peito", "ASA_" + lado); osso("AsaAntebraco_" + lado, a["cotovelo"], a["punho"], "AsaUmero_" + lado, "ASA_" + lado)
    for i, d in enumerate(a["dedos"]): osso("AsaDedo%d_%s" % (i + 1, lado), a["punho"], d, "AsaAntebraco_" + lado, "ASA_" + lado)
bpy.ops.object.mode_set(mode="OBJECT")
print("OSSOS", len(arm_d.bones))
segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm_d.bones if b.use_deform}
def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
vgs = {n: mesh.vertex_groups.new(name=n) for n in segs}
cand = {"CORPO": [n for n in segs if REGIAO[n] == "CORPO"], "ASA_E": [n for n in segs if REGIAO[n] == "ASA_E"] + ["Peito", "Lombo"], "ASA_D": [n for n in segs if REGIAO[n] == "ASA_D"] + ["Peito", "Lombo"]}
ASAV = set()
for v in mesh.data.vertices:
    reg = "CORPO"
    for g in v.groups:
        nm = mesh.vertex_groups[g.group].name
        if nm.startswith("REG_ASA_"): reg = "ASA_" + nm[-1]; ASAV.add(v.index)
    ws = sorted(((1.0 / (dist_seg(v.co, *segs[n]) ** 4 + 0.01), n) for n in cand[reg]), reverse=True)[:4]
    tot = sum(w for w, _ in ws)
    for w, n in ws:
        if w / tot > 0.02: vgs[n].add([v.index], w / tot, "REPLACE")
for g in [g for g in mesh.vertex_groups if g.name.startswith("REG_")]: mesh.vertex_groups.remove(g)
m = mesh.modifiers.new("Armature", "ARMATURE"); m.object = arm; mesh.parent = arm

# ---------- poses (rotacoes em eixos do corpo: X esquerda, Y tras, Z cima)
PB = arm.pose.bones
for pb in PB: pb.rotation_mode = "QUATERNION"
def R(ax, ay, az):
    return Matrix.Rotation(math.radians(az), 3, "Z") @ Matrix.Rotation(math.radians(ay), 3, "Y") @ Matrix.Rotation(math.radians(ax), 3, "X")
def aplicar(pose):
    for pb in PB: pb.rotation_quaternion = Quaternion(); pb.location = Vector()
    for nome, val in pose.items():
        pb = PB[nome]; M3 = pb.bone.matrix_local.to_3x3()
        rot, loc = val if isinstance(val, tuple) else (val, None)
        pb.rotation_quaternion = (M3.inverted() @ rot @ M3).to_quaternion()
        if loc is not None: pb.location = M3.inverted() @ Vector(loc)
def S(x): return math.sin(2 * math.pi * x)
def C(x): return math.cos(2 * math.pi * x)
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
LADOS = (("E", 1), ("D", -1))
def asaR(elev, recuo, s): return R(0, -s * elev, s * recuo)
# --- pose de solo: punho apoiado no chao a frente das patas (busca por cinematica direta)
A0 = ASA["E"]; Sh, El, Wr = Vector(A0["ombro"]), Vector(A0["cotovelo"]), Vector(A0["punho"])
ALVO = Vector((4.6, -6.8, 0.7))
melhor = (0, 0, 0, 0, 0, (0, 0, 0))
for e1, r1, e2, r2 in []:
    R1 = asaR(e1, r1, 1); R2 = asaR(e2, r2, 1)
    W = Sh + R1 @ (El - Sh) + R1 @ R2 @ (Wr - El)
    E2 = Sh + R1 @ (El - Sh)
    custo = (W - ALVO).length + 0.15 * max(0, 3.0 - E2.z) + 0.05 * abs(E2.x - 5.5)
    if melhor is None or custo < melhor[0]: melhor = (custo, e1, r1, e2, r2, tuple(W))
print("SOLO_ASA", melhor)
_, SE1, SR1, SE2, SR2, _ = melhor
DOBRA_DEDOS = (-35, 150)  # dedos recolhidos para tras ao longo do antebraco
# solo: apoio bipede com as asas meio recolhidas e erguidas (dobra forte dos dedos rigidos amassava a membrana)
SE1, SR1, SE2, SR2 = 42, 30, -38, 70
DOBRA_DEDOS = (0, -9)
def asas_solo(p, apoioE=0.0, apoioD=0.0, resp=0):
    for lado, s in LADOS:
        lev = apoioE if lado == "E" else apoioD
        p["AsaUmero_" + lado] = asaR(SE1 + 6 * lev + resp, SR1 - 4 * lev, s)
        p["AsaAntebraco_" + lado] = asaR(SE2, SR2, s)
        for i in range(4): p["AsaDedo%d_%s" % (i + 1, lado)] = asaR(0, DOBRA_DEDOS[1] * (i - 1.5), s)
    return p
def asas_ar(p, elev, recuo, pe, pr, ab=0, dif=0):
    for lado, s in LADOS:
        e = elev + dif * s
        p["AsaUmero_" + lado] = asaR(e, recuo, s); p["AsaAntebraco_" + lado] = asaR(pe, pr, s)
        for i in range(4): p["AsaDedo%d_%s" % (i + 1, lado)] = asaR(ab * 0.3 * i, ab * (i - 1.5), s)
    return p
def corpo_solo(t=0):
    # tronco inclinado para frente (apoio nos punhos), cabeca erguida, cauda com ferrao levemente alta
    return {"Pelve": R(-2, 0, 0), "Pescoco1": R(4, 0, 0), "Pescoco3": R(-2, 0, 0), "Cabeca": R(6, 0, 0),
            **{"Cauda%d" % (k + 1): R(3 + 2 * S(t - 0.1 * k), 0, 4 * S(t - 0.1 * k)) for k in range(7)}, "Ferrao": R(6, 0, 0)}
FPS = 30; scn.render.fps = FPS; ACOES = {}
def acao(nome, dur, loop, f):
    act = bpy.data.actions.new(nome); arm.animation_data_create(); arm.animation_data.action = act
    n = max(2, int(dur * FPS))
    for fr in range(n + 1):
        aplicar(f(fr / n))
        for pb in PB: pb.keyframe_insert("rotation_quaternion", frame=fr + 1); pb.keyframe_insert("location", frame=fr + 1)
    act.use_fake_user = True; ACOES[nome] = act
    tr = arm.animation_data.nla_tracks.new(); tr.name = nome; tr.strips.new(nome, 1, act); arm.animation_data.action = None
acao("Repouso", 4.0, True, lambda t: asas_solo({**corpo_solo(t), "Peito": (R(0.8 * S(t), 0, 0), (0, 0, 0.06 * S(t))), "Cabeca": R(16 + 2 * S(t), 10 * S(t * 0.5), 0)}, resp=1.5 * S(t)))
def andar(t, T=1.0, A=24):
    p = corpo_solo(t)
    for lado, f in (("E", 0.0), ("D", 0.5)):
        x = t - f; p["Coxa_" + lado] = R(-A * S(x), 0, 0); p["Canela_" + lado] = R(-28 * max(0, S(x + 0.25)), 0, 0)
    # punhos alternam com a pata do lado oposto (marcha quadrupedal de morcego/pterossauro)
    lE = max(0, S(t - 0.25)); lD = max(0, S(t + 0.25))
    p["Pelve"] = (R(-2 + 2 * S(2 * t), 0, 3 * S(t)), (0, 0, 0.25 * (0.5 - 0.5 * C(2 * t))))
    p["Pescoco1"] = R(4 - 3 * S(2 * t + 0.2), 4 * S(t), 0)
    return asas_solo(p, apoioE=lE, apoioD=lD)
acao("Andar", 1.0, True, lambda t: andar(t, A=28))
acao("Corrida", 0.55, True, lambda t: andar(t, A=36))
for nome, s in (("VirarEsquerda", 1), ("VirarDireita", -1)):
    acao(nome, 1.0, True, lambda t, s=s: {**andar(t, A=14), "Peito": R(0, 0, 8 * s), "Pescoco2": R(0, 0, 12 * s), "Cabeca": R(16, 0, 18 * s)})
acao("Observar", 3.5, True, lambda t: asas_solo({**corpo_solo(t), "Cabeca": R(10, 30 * S(t), 0),
                                                 **{"Cauda%d" % (k + 1): R(9, 0, 3 * S(t - 0.1 * k)) for k in range(7)}, "Ferrao": R(18, 0, 0), "Pescoco1": R(-4, 0, 0)}))
def vocal(t):
    u = ease(t * 4) * ease((1 - t) * 3)
    return asas_solo({**corpo_solo(t), "Pescoco1": R(-14 - 6 * u, 0, 0), "Pescoco3": R(-6 + 10 * u, 0, 0), "Cabeca": R(16 - 8 * u, 0, 0), "Mandibula": R(24 * u, 0, 0)}, apoioE=0.2 * u, apoioD=0.2 * u)
acao("Vocalizar", 2.2, False, vocal)
def abrir(u, base=None):
    p = base or corpo_solo()
    for lado, s in LADOS:
        p["AsaUmero_" + lado] = Matrix.Lerp(asaR(SE1, SR1, s), asaR(10, -4, s), u) if False else asaR(SE1 * (1 - u) + 10 * u, SR1 * (1 - u) - 4 * u, s)
        p["AsaAntebraco_" + lado] = asaR(SE2 * (1 - u), SR2 * (1 - u), s)
        for i in range(4): p["AsaDedo%d_%s" % (i + 1, lado)] = asaR((DOBRA_DEDOS[0] + 4 * i) * (1 - u), (DOBRA_DEDOS[1] - 6 * i) * (1 - u), s)
    return p
acao("AbrirAsas", 1.0, False, lambda t: abrir(ease(t)))
acao("RecolherAsas", 1.0, False, lambda t: abrir(ease(1 - t)))
def corpo_ar(t, amp):
    return {"Pelve": (R(1.5 * S(t) * amp, 0, 0), (0, 0, 0.3 * S(t + 0.25) * amp)), "Pescoco1": R(8 + 2 * S(t + 0.1) * amp, 0, 0), "Cabeca": R(-6, 0, 0),
            "Coxa_E": R(-70, 0, 0), "Coxa_D": R(-70, 0, 0), "Canela_E": R(45, 0, 0), "Canela_D": R(45, 0, 0),
            **{"Cauda%d" % (k + 1): R(0.5 + 2 * S(t - 0.1 * k) * amp, 0, 3 * S(t * 0.5 - 0.1 * k)) for k in range(7)}, "Ferrao": R(4, 0, 0)}
def voo(t):  # batida mais rapida e ampla que a do Dragao
    p = corpo_ar(t, 1)
    return asas_ar(p, 44 * S(t), -6 * C(t), 26 * S(t - 0.12) - 20 * max(0, C(t - 0.12)), 14 * max(0, S(t - 0.2)), 8 * S(t - 0.2))
acao("Voo", 0.85, True, voo)
acao("Planeio", 3.0, True, lambda t: asas_ar(corpo_ar(t, 0.3), 7 + 2 * S(t), -3, -2 + 2 * S(t + 0.15), 0, 3))
for nome, s in (("CurvaAereaEsquerda", 1), ("CurvaAereaDireita", -1)):
    def curva(t, s=s):
        p = corpo_ar(t, 0.4); p["Peito"] = R(0, 34 * s, 0); p["Cabeca"] = R(-6, 0, 16 * s)
        for k in range(7): p["Cauda%d" % (k + 1)] = R(0.5, 0, -7 * s)
        return asas_ar(p, 7 + 2 * S(t), -3, -3, 0, 3, dif=10 * s)
    acao(nome, 2.0, True, curva)
def decolagem(t):  # salto curto e batidas rapidas
    ag = ease(t / 0.22) * (1 - ease((t - 0.22) / 0.1)); vo = ease((t - 0.25) / 0.25)
    p = corpo_ar(t, vo)
    p["Pelve"] = (R(-8 * (1 - vo) + 6 * ag, 0, 0), (0, 0, -1.0 * ag))
    p["Coxa_E"] = R(-70 * vo + 18 * ag, 0, 0); p["Coxa_D"] = R(-70 * vo + 18 * ag, 0, 0); p["Canela_E"] = R(45 * vo, 0, 0); p["Canela_D"] = R(45 * vo, 0, 0)
    if t < 0.25:
        return asas_solo(p, apoioE=ag, apoioD=ag)
    return asas_ar(p, 48 * S((t - 0.25) / 0.75 * 2.5), -6, 26 * S((t - 0.25) / 0.75 * 2.5 - 0.12), 0, 6)
acao("Decolagem", 1.6, False, decolagem)
def pouso(t):
    fr = ease(t / 0.4); toque = ease((t - 0.5) / 0.2); rec = ease((t - 0.7) / 0.3)
    p = corpo_ar(t, 0.4 * (1 - toque))
    p["Coxa_E"] = R(-70 * (1 - fr) - 15 * fr * (1 - toque), 0, 0); p["Coxa_D"] = R(-70 * (1 - fr) - 15 * fr * (1 - toque), 0, 0)
    p["Canela_E"] = R(45 * (1 - fr), 0, 0); p["Canela_D"] = R(45 * (1 - fr), 0, 0)
    p["Pelve"] = (R(-10 * fr * (1 - toque) - 8 * rec, 0, 0), (0, 0, -0.6 * toque * (1 - rec)))
    if rec > 0.01:
        a = asas_ar({}, 34 * (1 - rec), -16 * (1 - rec), -10 * (1 - rec), 0, 8 * (1 - rec)); b = asas_solo({})
        for k in b: p[k] = Quaternion.slerp(a[k].to_quaternion(), b[k].to_quaternion(), rec).to_matrix()
        return p
    return asas_ar(p, 34 * fr, -16 * fr, -10 * fr, 0, 8 * fr)
acao("Pouso", 1.8, False, pouso)
# habilidades oficiais (so a animacao; sem efeitos): Rasante Predatorio, Ferrao Venenoso, Guinada Evasiva
acao("Rasante", 1.4, False, lambda t: asas_ar({**corpo_ar(t, 0.2), "Peito": R(-16 * ease(t / 0.3) * (1 - ease((t - 0.7) / 0.3)), 0, 0), "Pescoco1": R(14, 0, 0)},
                                               20 * (1 - ease(t / 0.3)) + 8 * ease((t - 0.7) / 0.3), 45 * ease(t / 0.3) * (1 - ease((t - 0.7) / 0.3)), -20 * ease(t / 0.3), 30 * ease(t / 0.3) * (1 - ease((t - 0.7) / 0.3))))
def ferroada(t):
    u = ease(t / 0.35) * (1 - ease((t - 0.55) / 0.45)); p = asas_solo(corpo_solo())
    for k in range(7): p["Cauda%d" % (k + 1)] = R(10 + 16 * u, 0, 0)
    p["Ferrao"] = R(30 + 40 * u, 0, 0); p["Pelve"] = R(-8 - 8 * u, 0, 0); p["Pescoco1"] = R(-14 + 10 * u, 0, 0)
    return p
acao("FerraoAtaque", 1.3, False, ferroada)
acao("GuinadaEvasiva", 0.9, False, lambda t: asas_ar({**corpo_ar(t, 0.3), "Peito": R(0, 360 * ease(t) * 0 + 70 * S(t / 2), 0)}, 10, -2, -4, 0, 2, dif=20 * S(t / 2)))
print("ACOES", len(ACOES))

# ---------- material (escamas finas + couro) assado em atlas; 3 padroes oficiais da Wyvern
PAD = [("Verde_Musgo", (0.04, 0.06, 0.03), (0.30, 0.36, 0.20), (0.05, 0.06, 0.035), (0.22, 0.25, 0.14)),
       ("Marrom_Rochoso", (0.06, 0.045, 0.03), (0.34, 0.26, 0.18), (0.06, 0.045, 0.035), (0.24, 0.18, 0.13)),
       ("Cinza_Acinzentado", (0.06, 0.06, 0.062), (0.36, 0.36, 0.37), (0.05, 0.05, 0.052), (0.24, 0.24, 0.25))]
bpy.context.view_layer.objects.active = mesh
for o in scn.objects: o.select_set(False)
mesh.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003); bpy.ops.object.mode_set(mode="OBJECT")
def mk(nome, escala):
    mat = bpy.data.materials.new(nome); mat.use_nodes = True; N = mat.node_tree.nodes; L = mat.node_tree.links
    b = N["Principled BSDF"]; tc = N.new("ShaderNodeTexCoord")
    vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = escala; L.new(tc.outputs["Object"], vo.inputs["Vector"])
    v2 = N.new("ShaderNodeTexVoronoi"); v2.inputs["Scale"].default_value = escala; v2.feature = "DISTANCE_TO_EDGE"; L.new(tc.outputs["Object"], v2.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.2; nz.inputs["Detail"].default_value = 5; L.new(tc.outputs["Object"], nz.inputs["Vector"])
    sp_ = N.new("ShaderNodeSeparateColor"); L.new(vo.outputs["Color"], sp_.inputs[0])
    ad = N.new("ShaderNodeMath"); ad.operation = "ADD"; L.new(sp_.outputs[0], ad.inputs[0]); L.new(nz.outputs["Fac"], ad.inputs[1])
    mu = N.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; mu.inputs[1].default_value = 0.55; L.new(ad.outputs[0], mu.inputs[0])
    rp = N.new("ShaderNodeValToRGB"); L.new(mu.outputs[0], rp.inputs["Fac"])
    eg = N.new("ShaderNodeMapRange"); eg.inputs["From Max"].default_value = 0.12; L.new(v2.outputs["Distance"], eg.inputs["Value"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.inputs["A"].default_value = (0.02, 0.02, 0.02, 1)
    L.new(eg.outputs["Result"], mx.inputs["Factor"]); L.new(rp.outputs["Color"], mx.inputs["B"]); L.new(mx.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.75
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5; bp.inputs["Distance"].default_value = 0.12; L.new(eg.outputs["Result"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return mat, rp
mat, rp = mk("Escamas", 5.0); mat2, rp2 = mk("Couro", 1.2)
# couro da membrana sem celulas de escama: so ruido suave
for n in list(mat2.node_tree.nodes):
    if n.type == "TEX_VORONOI": mat2.node_tree.nodes.remove(n)
mesh.data.materials.clear(); mesh.data.materials.append(mat); mesh.data.materials.append(mat2)
for poly in mesh.data.polygons:
    if all(i in ASAV for i in poly.vertices): poly.material_index = 1
scn.render.engine = "CYCLES"; scn.cycles.samples = 4
def cores(pd):
    rp.color_ramp.elements[0].color = pd[1] + (1,); rp.color_ramp.elements[1].color = pd[2] + (1,)
    rp2.color_ramp.elements[0].color = pd[3] + (1,); rp2.color_ramp.elements[1].color = pd[4] + (1,)
def assar(tipo, nome, cs):
    img = bpy.data.images.new(nome, 2048, 2048, alpha=False); img.colorspace_settings.name = cs
    nodes = []
    for mt in (mat, mat2):
        N = mt.node_tree.nodes; tn = N.new("ShaderNodeTexImage"); tn.image = img
        for n in N: n.select = False
        tn.select = True; N.active = tn; nodes.append(tn)
    if tipo == "DIFFUSE": bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4)
    else: bpy.ops.object.bake(type="NORMAL", margin=4)
    img.filepath_raw = os.path.join(DEST, nome + ".png"); img.file_format = "PNG"; img.save()
    return nodes[0]
cores(PAD[0]); tnor = assar("NORMAL", "Wyvern_Normal", "Non-Color")
for pd in PAD[1:]:
    cores(pd); assar("DIFFUSE", "Wyvern_Cor_" + pd[0], "sRGB")
cores(PAD[0]); tcor = assar("DIFFUSE", "Wyvern_Cor_" + PAD[0][0], "sRGB")
N = mat.node_tree.nodes; L = mat.node_tree.links
for n in list(N):
    if n not in (tcor, tnor): N.remove(n)
o_ = N.new("ShaderNodeOutputMaterial"); b_ = N.new("ShaderNodeBsdfPrincipled"); nm = N.new("ShaderNodeNormalMap")
L.new(tcor.outputs["Color"], b_.inputs["Base Color"]); L.new(tnor.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], b_.inputs["Normal"]); b_.inputs["Roughness"].default_value = 0.75; L.new(b_.outputs["BSDF"], o_.inputs["Surface"])
for poly in mesh.data.polygons: poly.material_index = 0
mesh.data.materials.pop(index=1)

# ---------- previas
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 960; scn.render.resolution_y = 600
sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 3.2; so = bpy.data.objects.new("Sol", sun); scn.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(35))
scn.world = bpy.data.worlds.new("W"); scn.world.use_nodes = True; scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.58, 0.68, 1)
bpy.ops.mesh.primitive_plane_add(size=300, location=(0, 5, 0)); chao = bpy.context.active_object
cm = bpy.data.materials.new("Chao"); cm.use_nodes = True; cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.25, 0.32, 0.2, 1); chao.data.materials.append(cm)
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=4.2, location=(9, -10, 2.1)); h1 = bpy.context.active_object
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(9, -10, 4.7)); h2 = bpy.context.active_object
cam = bpy.data.cameras.new("Cam"); co = bpy.data.objects.new("Cam", cam); scn.collection.objects.link(co); scn.camera = co; cam.lens = 35
def foto(nome, an, t, loc, alvo, voar=0):
    act = ACOES[an]; arm.animation_data.action = act; scn.frame_set(1 + int(t * (act.frame_range[1] - 1))); arm.location = (0, 0, voar)
    co.location = loc; co.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = os.path.join(OUT, "w_" + nome + ".png"); bpy.ops.render.render(write_still=True); arm.location = (0, 0, 0); arm.animation_data.action = None
foto("repouso_34", "Repouso", 0, (34, -42, 18), (0, 2, 7))
foto("repouso_lateral", "Repouso", 0, (52, 4, 9), (0, 6, 7))
foto("andar", "Andar", 0.25, (52, -6, 9), (0, 4, 7))
foto("observar", "Observar", 0.25, (34, -42, 18), (0, 4, 8))
foto("voo", "Voo", 0.25, (30, -45, 40), (0, 2, 22), voar=14)
foto("planeio", "Planeio", 0, (0, -55, 26), (0, 0, 22), voar=14)
foto("ferrao", "FerraoAtaque", 0.42, (40, -20, 14), (0, 10, 8))
for o in (chao, h1, h2, co, so): bpy.data.objects.remove(o, do_unlink=True)
arm.animation_data.action = None
for o in scn.objects: o.select_set(False)
arm.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=os.path.join(DEST, "Wyvern.glb"), export_format="GLB", use_selection=True, export_animations=True, export_animation_mode="ACTIONS", export_skins=True, export_yup=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(DEST, "Wyvern.fbx"), use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=True,
                         bake_anim_use_nla_strips=False, path_mode="COPY", embed_textures=True, axis_forward="-Z", axis_up="Y")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DEST, "Wyvern.blend"))
dims = mesh.dimensions
print("DIM %.1f x %.1f x %.1f" % (dims.x, dims.y, dims.z))
print("EXPORTADO")

