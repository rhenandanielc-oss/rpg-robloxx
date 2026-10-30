# Repteis quadrupedes (Pantano Nebuloso / Deserto de Cristal): Crocodilo Primordial, Basilisco, Lagarto Cristalino.
# 1 BU = 1 stud; frente -Y, cima +Z, esquerda +X. Medidas OFICIAIS usadas (RPG_02):
#  Crocodilo: 5-7 ate os ombros (6) e 24-32 de comprimento (28); Basilisco: 7-10 ate os ombros (8,5), comprimento NAO fixado (provisorio ~26);
#  Lagarto Cristalino: 18-26 de comprimento (22), altura NAO fixada (provisoria). Patas abertas para os lados (marcha de reptil).
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix, Quaternion
OUT = sys.argv[sys.argv.index("--") + 1]; DEST = sys.argv[sys.argv.index("--") + 2]; ESP = sys.argv[sys.argv.index("--") + 3]
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
def tubo(name, path, radii, achatar=None, lados=10):
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
    for f in me.polygons: f.use_smooth = (lados > 6)
    return ob

# ---------- parametros por especie: espinha (focinho -> ponta da cauda) em fracoes do comprimento
if ESP == "Crocodilo":
    NOME = "Crocodilo_Primordial"; L = 28.0; OMBRO = 6.0; z0 = 4.3
    # raios (largura, altura) ao longo do corpo; focinho longo e achatado
    perfil = [(0.00, 0.55, 0.35), (0.06, 0.9, 0.55), (0.12, 1.25, 0.8), (0.17, 1.6, 1.1), (0.21, 1.4, 1.15), (0.27, 1.9, 1.5), (0.34, 2.5, 1.75), (0.42, 2.6, 1.75),
              (0.50, 2.2, 1.55), (0.58, 1.7, 1.3), (0.67, 1.3, 1.1), (0.76, 0.95, 0.85), (0.86, 0.6, 0.6), (1.00, 0.18, 0.2)]
    zprof = lambda t: z0 - (1.0 if t < 0.17 else 0.0) * (0.17 - t) * 3 - max(0, t - 0.55) * 2.2
    ombroI, quadrilI = 0.30, 0.48; abertura = 3.2; perna = 1.0
    PAD = [("Verde_Pantanal", (0.03, 0.05, 0.03), (0.20, 0.27, 0.15), (0.32, 0.33, 0.22)), ("Marrom_Aluvial", (0.05, 0.04, 0.025), (0.28, 0.22, 0.14), (0.40, 0.34, 0.24)),
           ("Negro_de_Rio", (0.012, 0.014, 0.012), (0.10, 0.11, 0.10), (0.24, 0.24, 0.22))]
elif ESP == "Basilisco":
    NOME = "Basilisco"; L = 26.0; OMBRO = 8.5; z0 = 6.3
    perfil = [(0.00, 0.45, 0.4), (0.05, 0.9, 0.75), (0.10, 1.25, 1.05), (0.15, 1.05, 1.0), (0.21, 1.25, 1.2), (0.28, 2.0, 2.0), (0.36, 2.35, 2.2), (0.44, 2.3, 2.1),
              (0.52, 1.9, 1.9), (0.61, 1.4, 1.5), (0.70, 1.0, 1.1), (0.80, 0.7, 0.75), (0.90, 0.4, 0.45), (1.00, 0.12, 0.14)]
    zprof = lambda t: z0 + (0.21 - t) * 6 * (1 if t < 0.21 else 0) - max(0, t - 0.5) * 3.2
    ombroI, quadrilI = 0.31, 0.50; abertura = 2.0; perna = 1.0
    PAD = [("Verde_Pantanoso", (0.03, 0.05, 0.025), (0.22, 0.30, 0.14), (0.45, 0.42, 0.22)), ("Marrom_Lamacento", (0.05, 0.035, 0.02), (0.30, 0.22, 0.13), (0.48, 0.38, 0.22)),
           ("Negro_Musgo", (0.012, 0.016, 0.01), (0.10, 0.14, 0.08), (0.26, 0.30, 0.16))]
else:
    NOME = "Lagarto_Cristalino"; L = 22.0; OMBRO = 5.6; z0 = 4.3
    perfil = [(0.00, 0.5, 0.4), (0.06, 1.0, 0.8), (0.12, 1.35, 1.05), (0.17, 1.2, 1.05), (0.23, 1.6, 1.35), (0.31, 2.3, 1.75), (0.40, 2.5, 1.8), (0.49, 2.3, 1.7),
              (0.58, 1.7, 1.35), (0.68, 1.2, 1.0), (0.78, 0.85, 0.75), (0.89, 0.5, 0.45), (1.00, 0.15, 0.15)]
    zprof = lambda t: z0 + (0.17 - t) * 3 * (1 if t < 0.17 else 0) - max(0, t - 0.55) * 2.6
    ombroI, quadrilI = 0.30, 0.50; abertura = 2.6; perna = 1.0
    PAD = [("Quartzo_Claro", (0.20, 0.17, 0.13), (0.55, 0.47, 0.36), (0.90, 0.92, 0.95)), ("Ambar_Dourado", (0.18, 0.12, 0.06), (0.50, 0.38, 0.22), (0.95, 0.66, 0.22)),
           ("Ametista_Rochosa", (0.14, 0.12, 0.13), (0.42, 0.37, 0.40), (0.62, 0.42, 0.78))]
spine = [(0, -L / 2 + L * t, zprof(t)) for t, _, _ in perfil]
rad = [(w, h) for _, w, h in perfil]
def idx(fr):
    return min(range(len(perfil)), key=lambda i: abs(perfil[i][0] - fr))
iO, iQ = idx(ombroI), idx(quadrilI)
pts = list(spine); edges = [(i, i + 1) for i in range(len(spine) - 1)]; rr = list(rad)
LEG = {}
for s, lado in ((1, "E"), (-1, "D")):
    for nome, ib, fr in (("Dianteira", iO, 1.0), ("Traseira", iQ, 1.12)):
        sx, sy, sz = spine[ib]; w = rad[ib][0]
        # patas abertas: ombro lateral -> cotovelo para fora -> pulso no chao -> pata -> dedos
        ch = [(s * w * 0.75, sy, sz - rad[ib][1] * 0.2), (s * (w + abertura), sy + 0.3, sz - rad[ib][1] * 0.45), (s * (w + abertura * 0.95), sy - 0.3, 0.9 * fr),
              (s * (w + abertura * 1.05), sy - 0.8, 0.45), (s * (w + abertura * 1.15), sy - 2.0 * fr, 0.3)]
        r = rad[ib][1]
        radl = [(r * 0.75 * fr, r * 0.8 * fr), (r * 0.5 * fr, r * 0.52 * fr), (r * 0.32 * fr, r * 0.32 * fr), (r * 0.4 * fr, r * 0.2 * fr), (r * 0.36 * fr, r * 0.16 * fr)]
        prev = ib
        for p, rl in zip(ch, radl):
            pts.append(p); rr.append(rl); edges.append((prev, len(pts) - 1)); prev = len(pts) - 1
        LEG[nome + "_" + lado] = ch
corpo = skin_obj("Corpo", pts, edges, rr)
det = []
# detalhes por especie
for i in range(2, len(spine) - 1):
    x, y, z = spine[i]; w, h = rad[i]
    if ESP == "Crocodilo" and i >= 4:
        for s in (-0.45, 0.45):  # fileiras de osteodermos (escudos osseos)
            det.append(tubo("Osteoderma", [(s * w, y, z + h * 0.85), (s * w, y + 0.5, z + h * 0.85 + 0.45), (s * w, y + 1.0, z + h * 0.85)], [0.35, 0.28, 0.05], achatar=0.6, lados=4))
    if ESP == "Basilisco" and i >= 3:  # crista dorsal alta e serrilhada
        hh = (0.9 + 0.8 * math.sin(math.pi * min(1, (i - 3) / 6))) * (1.6 if i < 9 else 1.0)
        det.append(tubo("Crista", [(0, y - 0.3, z + h * 0.85), (0, y + 0.3, z + h * 0.85 + hh), (0, y + 0.9, z + h * 0.85)], [0.5, 0.18, 0.05], achatar=0.25, lados=4))
    if ESP == "Lagarto" and 3 <= i <= len(spine) - 3:  # aglomerados de cristais naturais nas costas e cauda
        for k, (dx, ang) in enumerate(((0, 0), (0.6 * w, 25), (-0.6 * w, -25))):
            hh = (1.4 + 0.9 * (1 - abs(i - 6) / 6)) * (1.0 if k == 0 else 0.65)
            base = Vector((dx, y + 0.2 * k, z + h * 0.7)); topo = base + Vector((math.sin(math.radians(ang)) * hh, 0.35 * hh, math.cos(math.radians(ang)) * hh))
            det.append(tubo("Cristal", [tuple(base), tuple(base.lerp(topo, 0.75)), tuple(topo)], [0.42, 0.36, 0.02], lados=6))
if ESP == "Basilisco":
    cab = Vector(spine[2])
    for s in (-1, 1):  # crista/coroa da cabeca (olhar ameacador)
        det.append(tubo("Coroa", [tuple(cab + Vector((s * 0.6, 0.4, 0.9))), tuple(cab + Vector((s * 1.3, 2.0, 2.4))), tuple(cab + Vector((s * 1.0, 3.3, 2.9)))], [0.35, 0.18, 0.03], achatar=0.4, lados=4))
# garras
for nome, ch in LEG.items():
    px, py, pz = ch[-1]
    for dx in (-0.4, 0, 0.4):
        a = (px + dx, py - 0.3, 0.3); b = (px + dx * 1.3, py - 1.2, 0.05)
        det.append(tubo("Garra", [a, tuple(Vector(a).lerp(Vector(b), 0.5)), b], [0.18, 0.11, 0.02], lados=6))
for o in det:
    if o.name.startswith("Garra"):
        m = o.modifiers.new("Sub", "SUBSURF"); m.levels = 1
CRIST = [o for o in det if o.name.startswith("Cristal")]
def marcar(o, g):
    vg = o.vertex_groups.new(name=g); vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
for o in [corpo] + det:
    bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.convert(target="MESH")
    marcar(o, "REG_CRISTAL" if o in CRIST else "REG_CORPO")
bpy.ops.object.select_all(action="DESELECT")
for o in [corpo] + det: o.select_set(True)
bpy.context.view_layer.objects.active = corpo; bpy.ops.object.join()
mesh = bpy.context.view_layer.objects.active; mesh.name = NOME
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.remove_doubles(threshold=0.001); bpy.ops.object.mode_set(mode="OBJECT")
tris = sum(len(p.vertices) - 2 for p in mesh.data.polygons)
if tris > 16000:
    dec = mesh.modifiers.new("Dec", "DECIMATE"); dec.ratio = 15500 / tris; bpy.ops.object.modifier_apply(modifier="Dec")
print("TRIS_FINAL", sum(len(p.vertices) - 2 for p in mesh.data.polygons))

# ---------- armature: coluna (cabeca, pescoco, tronco 3, cauda 5) + mandibula + 4 patas (3 ossos)
sp = [Vector(p) for p in spine]
arm_d = bpy.data.armatures.new("Esqueleto"); arm = bpy.data.objects.new(NOME + "_Rig", arm_d); scn.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT"); EB = arm_d.edit_bones
def osso(nome, h, t, pai=None, deform=True):
    b = EB.new(nome); b.head = Vector(h); b.tail = Vector(t); b.roll = 0
    if pai: b.parent = EB[pai]
    b.use_deform = deform
osso("Raiz", (0, 0, 0), (0, 0, 2), None, False)
iP = idx(0.40)
osso("Peito", sp[iP], sp[iO], "Raiz"); osso("Lombo", sp[iP], sp[iQ], "Raiz")
iN = idx(0.17 if ESP != "Basilisco" else 0.17)
osso("Pescoco", sp[iO], sp[iN], "Peito"); osso("Cabeca", sp[iN], sp[1], "Pescoco")
osso("Mandibula", sp[iN] + Vector((0, 0, -rad[iN][1] * 0.55)), sp[0] + Vector((0, 0.2, -rad[0][1] * 0.6)), "Cabeca")
cauda = [iQ] + [idx(f) for f in (0.62, 0.72, 0.82, 0.91)] + [len(spine) - 1]
prev = "Lombo"
for k in range(5):
    n = "Cauda%d" % (k + 1); osso(n, sp[cauda[k]], sp[cauda[k + 1]], prev); prev = n
for nome, ch in LEG.items():
    c = [Vector(p) for p in ch]; pai = "Peito" if nome.startswith("Dianteira") else "Lombo"
    osso("Braco_" + nome, c[0], c[1], pai); osso("Antebraco_" + nome, c[1], c[2], "Braco_" + nome); osso("Pe_" + nome, c[2], c[4], "Antebraco_" + nome)
bpy.ops.object.mode_set(mode="OBJECT")
print("OSSOS", len(arm_d.bones))
segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm_d.bones if b.use_deform}
def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
vgs = {n: mesh.vertex_groups.new(name=n) for n in segs}
CRV = set()
for v in mesh.data.vertices:
    cr = any(mesh.vertex_groups[g.group].name == "REG_CRISTAL" for g in v.groups)
    if cr: CRV.add(v.index)
    lst = [n for n in segs if not (cr and ("Braco" in n or "Antebraco" in n or "Pe_" in n))]
    ws = sorted(((1.0 / (dist_seg(v.co, *segs[n]) ** 4 + 0.02), n) for n in lst), reverse=True)[:4]
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
PATAS = [("Dianteira_E", 0.0, 1), ("Traseira_D", 0.0, -1), ("Dianteira_D", 0.5, -1), ("Traseira_E", 0.5, 1)]
def marcha(t, amp=28, ond=10, erg=0.0):
    # marcha de reptil: pares diagonais; braco gira no plano horizontal (Z) e levanta na recuperacao; coluna e cauda ondulam
    p = {}
    for nome, f, s in PATAS:
        x = t - f; sw = amp * S(x); lift = max(0, S(x + 0.25))
        p["Braco_" + nome] = R(0, -s * (14 * lift + erg), s * sw)
        p["Antebraco_" + nome] = R(0, s * 10 * lift, 0)
    p["Peito"] = (R(0, 2 * S(t), -ond * 0.5 * S(t)), (0, 0, 0.1 * erg / 20))
    p["Lombo"] = R(0, -2 * S(t), ond * 0.5 * S(t))
    p["Pescoco"] = R(0, 0, ond * 0.4 * S(t - 0.15)); p["Cabeca"] = R(0, 0, -ond * 0.3 * S(t - 0.15))
    for k in range(5): p["Cauda%d" % (k + 1)] = R(0, 0, ond * (0.6 + 0.25 * k) * S(t - 0.12 * (k + 1)))
    return p
def repouso(t, resp=0.8):
    p = {"Peito": R(resp * S(t), 0, 0), "Cabeca": R(1.0 * S(t), 4 * S(t * 0.5), 0)}
    for k in range(5): p["Cauda%d" % (k + 1)] = R(0, 0, 3 * S(t * 0.5 - 0.1 * k))
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
acao("Repouso", 5.0, True, repouso)
acao("Andar", 1.6 if ESP != "Lagarto" else 1.8, True, lambda t: marcha(t))
acao("Corrida", 0.8 if ESP == "Basilisco" else 0.9, True, lambda t: marcha(t, 38, 14, erg=18))  # postura mais erguida ao correr
for nome, s in (("VirarEsquerda", 1), ("VirarDireita", -1)):
    acao(nome, 1.6, True, lambda t, s=s: {**marcha(t, 16, 6), "Peito": R(0, 0, 10 * s), "Pescoco": R(0, 0, 12 * s), "Cabeca": R(0, 0, 10 * s)})
acao("Observar", 4.0, True, lambda t: {**repouso(t), "Pescoco": R(-10, 0, 0), "Cabeca": R(-6, 0, 22 * S(t))})
def mordida(t, gira=False):
    u = ease(t / 0.3) * (1 - ease((t - 0.5) / 0.5)); p = repouso(t)
    p["Peito"] = (R(-4 * u, 0, 0), (0, -0.8 * u, 0)); p["Pescoco"] = R(-6 * u, 0, 0); p["Mandibula"] = R(32 * u * (1 - ease((t - 0.3) / 0.12)), 0, 0)
    return p
if ESP == "Crocodilo":
    acao("Natacao", 2.0, True, lambda t: {**{"Braco_" + n: R(0, -s * 25, s * 60) for n, _, s in PATAS}, "Peito": R(0, 0, -4 * S(t)), "Lombo": R(0, 0, 6 * S(t)),
                                           **{"Cauda%d" % (k + 1): R(0, 0, (12 + 6 * k) * S(t - 0.14 * (k + 1))) for k in range(5)}})
    acao("Submersao", 2.0, False, lambda t: {**repouso(t), **{"Braco_" + n: R(0, -s * 20 * ease(t), s * 55 * ease(t)) for n, _, s in PATAS}, "Cabeca": R(4 * ease(t), 0, 0)})
    acao("MordidaDeAgarrao", 1.2, False, mordida)
    acao("GiroPredatorio", 1.6, False, lambda t: {**mordida(min(t, 0.35)), "Peito": R(0, 360 * ease(t), 0), "Lombo": R(0, 0, 0)})
    acao("CaudaDeMare", 1.2, False, lambda t: {**repouso(t), "Lombo": R(0, 0, -15 * S(t / 2)), **{"Cauda%d" % (k + 1): R(0, 0, (18 + 6 * k) * S(t / 2 - 0.05 * k) * (1 - ease((t - 0.7) / 0.3))) for k in range(5)}})
elif ESP == "Basilisco":
    acao("OlharAmeacador", 3.0, False, lambda t: {**repouso(t), "Peito": R(-10 * ease(t / 0.3), 0, 0), "Pescoco": R(-18 * ease(t / 0.3), 0, 0), "Cabeca": R(8 * ease(t / 0.3), 0, 0),
                                                  **{"Braco_" + n: R(0, -s * 12 * ease(t / 0.3), 0) for n, _, s in PATAS[:1] + PATAS[2:3]}})
    acao("MordidaToxica", 1.2, False, mordida)
    def espiral(t):
        u = ease(t / 0.4) * (1 - ease((t - 0.8) / 0.2)); p = repouso(t)
        p["Peito"] = (R(0, 0, 0), (0, 0, -1.6 * u)); p["Lombo"] = (R(0, 0, 18 * u), (0, 0, -1.4 * u))
        for k in range(5): p["Cauda%d" % (k + 1)] = R(0, 0, 32 * u)
        p["Pescoco"] = R(-8 * u, 0, -14 * u)
        return p
    acao("EspiralDefensiva", 3.0, False, espiral)
    acao("Emboscada", 2.0, True, lambda t: {**marcha(t, 14, 5, erg=-14), "Peito": (R(0, 0, 0), (0, 0, -1.8)), "Lombo": (R(0, 0, 0), (0, 0, -1.6)), "Pescoco": R(6, 0, 0)})
else:
    acao("GolpeDeCauda", 1.3, False, lambda t: {**repouso(t), "Lombo": R(0, 0, -12 * S(t / 2)), **{"Cauda%d" % (k + 1): R(0, 0, (16 + 6 * k) * S(t / 2 - 0.06 * k) * (1 - ease((t - 0.7) / 0.3))) for k in range(5)}})
    acao("EscamasCristalinas", 2.5, False, lambda t: {**repouso(t), "Peito": (R(0, 0, 0), (0, 0, -0.8 * ease(t / 0.3) * (1 - ease((t - 0.8) / 0.2)))), "Pescoco": R(8 * ease(t / 0.3) * (1 - ease((t - 0.8) / 0.2)), 0, 0),
                                                       **{"Cauda%d" % (k + 1): R(-4, 0, 14 * ease(t / 0.3) * (1 - ease((t - 0.8) / 0.2))) for k in range(5)}})
    acao("DisparoPrismatico", 1.8, False, lambda t: {**repouso(t), "Pescoco": R(-8 * ease(t / 0.3), 0, 0), "Cabeca": R(-4 * ease(t / 0.3), 0, 0), "Peito": R(-6 * ease(t / 0.3), 0, 0)})
    def escalada(t):  # postura de escalada em parede rochosa (tronco inclinado para cima, patas alcancando)
        p = marcha(t, 30, 8); p["Peito"] = R(-55, 0, 0); p["Pescoco"] = R(20, 0, 0)
        for k in range(5): p["Cauda%d" % (k + 1)] = R(10 if k == 0 else 0, 0, 6 * S(t - 0.1 * k))
        return p
    acao("Escalada", 1.8, True, escalada)
print("ACOES", len(ACOES))

# ---------- material (escamas; cristais com cor propria no padrao) assado em atlas
bpy.context.view_layer.objects.active = mesh
for o in scn.objects: o.select_set(False)
mesh.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003); bpy.ops.object.mode_set(mode="OBJECT")
mat = bpy.data.materials.new("Escamas"); mat.use_nodes = True; Nn = mat.node_tree.nodes; Lk = mat.node_tree.links
b = Nn["Principled BSDF"]; tc = Nn.new("ShaderNodeTexCoord")
vo = Nn.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 3.2 if ESP == "Crocodilo" else 5.0; vo.feature = "DISTANCE_TO_EDGE"; Lk.new(tc.outputs["Object"], vo.inputs["Vector"])
nz = Nn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.25; nz.inputs["Detail"].default_value = 5; Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
eg = Nn.new("ShaderNodeMapRange"); eg.inputs["From Max"].default_value = 0.1; Lk.new(vo.outputs["Distance"], eg.inputs["Value"])
geo = Nn.new("ShaderNodeNewGeometry"); sz = Nn.new("ShaderNodeSeparateXYZ"); Lk.new(geo.outputs["Normal"], sz.inputs[0])
mr = Nn.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -0.7; mr.inputs["From Max"].default_value = 0.3; Lk.new(sz.outputs["Z"], mr.inputs["Value"])
mu = Nn.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; Lk.new(eg.outputs["Result"], mu.inputs[0]); Lk.new(nz.outputs["Fac"], mu.inputs[1])
mu2 = Nn.new("ShaderNodeMath"); mu2.operation = "MULTIPLY"; Lk.new(mu.outputs[0], mu2.inputs[0]); Lk.new(mr.outputs["Result"], mu2.inputs[1])
rp = Nn.new("ShaderNodeValToRGB"); Lk.new(mu2.outputs[0], rp.inputs["Fac"]); Lk.new(rp.outputs["Color"], b.inputs["Base Color"])
# barriga mais clara
b.inputs["Roughness"].default_value = 0.7
bp = Nn.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.55; bp.inputs["Distance"].default_value = 0.1; Lk.new(eg.outputs["Result"], bp.inputs["Height"]); Lk.new(bp.outputs["Normal"], b.inputs["Normal"])
mat2 = bpy.data.materials.new("Cristal"); mat2.use_nodes = True; b2 = mat2.node_tree.nodes["Principled BSDF"]; b2.inputs["Roughness"].default_value = 0.15
mesh.data.materials.clear(); mesh.data.materials.append(mat); mesh.data.materials.append(mat2)
for poly in mesh.data.polygons:
    if all(i in CRV for i in poly.vertices): poly.material_index = 1
scn.render.engine = "CYCLES"; scn.cycles.samples = 4
def cores(pd):
    rp.color_ramp.elements[0].color = pd[1] + (1,); rp.color_ramp.elements[1].color = pd[2] + (1,); b2.inputs["Base Color"].default_value = pd[3] + (1,)
def assar(tipo, nome, cs):
    img = bpy.data.images.new(nome, 2048, 2048, alpha=False); img.colorspace_settings.name = cs; nodes = []
    for mt in (mat, mat2):
        N_ = mt.node_tree.nodes; tn = N_.new("ShaderNodeTexImage"); tn.image = img
        for n in N_: n.select = False
        tn.select = True; N_.active = tn; nodes.append(tn)
    if tipo == "DIFFUSE": bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4)
    else: bpy.ops.object.bake(type="NORMAL", margin=4)
    img.filepath_raw = os.path.join(DEST, nome + ".png"); img.file_format = "PNG"; img.save(); return nodes[0]
cores(PAD[0]); tnor = assar("NORMAL", NOME + "_Normal", "Non-Color")
for pd in PAD[1:]: cores(pd); assar("DIFFUSE", NOME + "_Cor_" + pd[0], "sRGB")
cores(PAD[0]); tcor = assar("DIFFUSE", NOME + "_Cor_" + PAD[0][0], "sRGB")
for n in list(Nn):
    if n not in (tcor, tnor): Nn.remove(n)
o_ = Nn.new("ShaderNodeOutputMaterial"); b_ = Nn.new("ShaderNodeBsdfPrincipled"); nm = Nn.new("ShaderNodeNormalMap")
Lk.new(tcor.outputs["Color"], b_.inputs["Base Color"]); Lk.new(tnor.outputs["Color"], nm.inputs["Color"]); Lk.new(nm.outputs["Normal"], b_.inputs["Normal"]); b_.inputs["Roughness"].default_value = 0.65; Lk.new(b_.outputs["BSDF"], o_.inputs["Surface"])
for poly in mesh.data.polygons: poly.material_index = 0
mesh.data.materials.pop(index=1)
# medidas reais
tr_top = max((v.co.z for v in mesh.data.vertices if abs(v.co.y - spine[iO][1]) < 1.0 and abs(v.co.x) < rad[iO][0]), default=0)
print("ALTURA_OMBRO %.2f" % tr_top)

scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 960; scn.render.resolution_y = 600
sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 3.2; so = bpy.data.objects.new("Sol", sun); scn.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(35))
scn.world = bpy.data.worlds.new("W"); scn.world.use_nodes = True; scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.58, 0.68, 1)
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0)); ch = bpy.context.active_object
cm = bpy.data.materials.new("Chao"); cm.use_nodes = True; cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.3, 0.22, 1); ch.data.materials.append(cm)
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=4.2, location=(L * 0.35, -L * 0.45, 2.1)); h1 = bpy.context.active_object
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(L * 0.35, -L * 0.45, 4.7)); h2 = bpy.context.active_object
cam = bpy.data.cameras.new("Cam"); co = bpy.data.objects.new("Cam", cam); scn.collection.objects.link(co); scn.camera = co; cam.lens = 35
def foto(nome, an, t, loc, alvo):
    act = ACOES[an]; arm.animation_data.action = act; scn.frame_set(1 + int(t * (act.frame_range[1] - 1)))
    co.location = loc; co.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = os.path.join(OUT, "%s_%s.png" % (ESP, nome)); bpy.ops.render.render(write_still=True); arm.animation_data.action = None
foto("34", "Repouso", 0, (L * 0.85, -L * 0.95, L * 0.45), (0, -L * 0.05, 3))
foto("lateral", "Andar", 0.25, (L * 1.25, 0, 5), (0, 0, 3))
foto("cima", "Andar", 0.25, (0, 0.01, L * 1.3), (0, 0, 0))
esp = {"Crocodilo": "MordidaDeAgarrao", "Basilisco": "OlharAmeacador", "Lagarto": "EscamasCristalinas"}[ESP]
foto("especial", esp, 0.4, (L * 0.85, -L * 0.95, L * 0.45), (0, -L * 0.05, 3))
for o in (ch, h1, h2, co, so): bpy.data.objects.remove(o, do_unlink=True)
for o in scn.objects: o.select_set(False)
arm.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=os.path.join(DEST, NOME + ".glb"), export_format="GLB", use_selection=True, export_animations=True, export_animation_mode="ACTIONS", export_skins=True, export_yup=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(DEST, NOME + ".fbx"), use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=True,
                         bake_anim_use_nla_strips=False, path_mode="COPY", embed_textures=True, axis_forward="-Z", axis_up="Y")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DEST, NOME + ".blend"))
d = mesh.dimensions; print("DIM %.1f x %.1f x %.1f" % (d.x, d.y, d.z)); print("EXPORTADO")
