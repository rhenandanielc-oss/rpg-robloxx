"""CR_UrsoSilvestre v2 — corpo (pele) com cabeca ursidea reconstruida, olhos em orbitas com palpebras, orelhas em
concha, boca com labios/comissuras, gengivas, palato, lingua e denticao (incisivos, caninos fortes, pre-molares,
molares), patas largas com dedos volumosos e garras de queratina. POSE NEUTRA, boca fechada.
1 unidade = 1 stud; frente = -Y; pes em Z = 0; esquerda do urso = +X. Referencia: ../ref/urso-silvestre-referencia.png
Uso: blender -b --factory-startup -P corpo_v2.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, Euler
from mathutils.bvhtree import BVHTree

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; V = Vector; rnd = random.Random(31)
def lerp(a, b, t): return a + (b - a) * t
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def gauss(x, c, w): return math.exp(-((x - c) / w) ** 2)
K_MB = 0.574                                   # raio de superficie por unidade de "radius" de metaball (medido na v1)

# ================================================================== VOLUMES
TRONCO = [((0, -2.85, 5.95), (2.50, 2.00, 2.20)),                 # torax largo e fundo
          ((0, -3.15, 7.05), (1.75, 1.65, 1.10)),                 # corcova escapular (integrada a coluna)
          ((0, -1.60, 6.95), (1.55, 1.40, 0.80)),                 # linha do dorso atras da corcova
          ((0, -0.40, 5.75), (2.45, 2.30, 1.95)), ((0, 1.15, 5.20), (2.25, 2.10, 1.80)),
          ((0, 2.85, 5.85), (2.15, 1.90, 1.70)), ((0, 4.55, 5.80), (2.05, 1.75, 1.65)),
          ((0, 5.85, 5.55), (1.55, 0.95, 1.30)), ((0, 6.75, 5.45), (0.36, 0.50, 0.36)),
          ((0, -4.15, 5.15), (1.70, 1.10, 1.60)),                 # peito projetado entre os bracos
          ((0, -4.70, 6.35), (1.70, 1.25, 1.55)), ((0, -5.60, 6.45), (1.45, 0.95, 1.30))]   # pescoco grosso
for s in (1, -1):
    TRONCO.append(((1.65 * s, -3.05, 6.55), (1.05, 1.45, 1.20)))   # massa do ombro (escapula + deltoide)
# cabeca em volumes anatomicos (resolucao fina)
CABECA = [((0, -6.75, 6.60), (1.12, 1.00, 0.95)),                 # cranio largo
          ((0, -6.55, 7.35), (0.62, 0.85, 0.30)),                 # crista/topo do cranio
          ((0, -7.42, 6.98), (0.74, 0.50, 0.36)),                 # testa
          ((0.40, -7.62, 6.98), (0.34, 0.30, 0.17), (0, 0, -18)), ((-0.40, -7.62, 6.98), (0.34, 0.30, 0.17), (0, 0, 18)),  # arcadas
          ((0.84, -7.05, 6.36), (0.46, 0.62, 0.42)), ((-0.84, -7.05, 6.36), (0.46, 0.62, 0.42)),   # zigomas/bochechas
          ((0.74, -7.15, 5.88), (0.40, 0.55, 0.45)), ((-0.74, -7.15, 5.88), (0.40, 0.55, 0.45)),   # masseteres
          ((0, -8.12, 6.70), (0.36, 0.78, 0.17)),                 # ponte nasal (transicao testa -> focinho)
          ((0, -8.15, 6.32), (0.62, 0.82, 0.44)), ((0, -8.72, 6.30), (0.56, 0.40, 0.38)),          # focinho largo
          ((0.36, -8.55, 6.05), (0.30, 0.48, 0.20)), ((-0.36, -8.55, 6.05), (0.30, 0.48, 0.20)),   # labios superiores
          ((0, -9.02, 6.44), (0.37, 0.19, 0.27)),                 # nariz
          ((0, -8.00, 5.70), (0.56, 0.85, 0.31)), ((0, -8.62, 5.71), (0.42, 0.30, 0.25)),          # mandibula / queixo
          ((0.60, -7.30, 5.74), (0.36, 0.48, 0.36)), ((-0.60, -7.30, 5.74), (0.36, 0.48, 0.36))]   # angulo da mandibula
def perna(s, dianteira):
    if dianteira:
        return [(V((1.60 * s, -2.95, 6.10)), 1.45), (V((1.85 * s, -2.55, 3.65)), 1.18), (V((1.82 * s, -3.15, 1.00)), 0.92)]
    return [(V((1.62 * s, 4.40, 5.80)), 1.55), (V((1.92 * s, 3.40, 3.00)), 1.12), (V((1.80 * s, 4.70, 0.62)), 0.72)]
def massas_perna(s, dianteira):
    if dianteira:
        return [((1.82 * s, -3.05, 4.70), (1.40, 1.45, 1.55)), ((1.86 * s, -2.95, 2.35), (1.22, 1.22, 1.25)),   # braco e antebraco fortes
                ((1.88 * s, -3.78, 0.44), (1.15, 1.12, 0.44))]                                                 # pe largo
    return [((1.88 * s, 4.00, 4.45), (1.50, 1.75, 1.65)), ((1.84 * s, 4.05, 1.85), (0.98, 1.05, 1.08)),
            ((1.84 * s, 3.95, 0.42), (0.98, 1.30, 0.42))]
PE_FRENTE = {True: -4.62, False: 2.78}
def dedos(s, dianteira):
    """5 dedos volumosos em arco; o interno (lado do corpo) e o menor. [(centro do bulbo, raio)]"""
    pe = massas_perna(s, dianteira)[2][0]; out = []
    for k, dx in enumerate((-0.80, -0.40, 0.0, 0.40, 0.78)):
        yf = PE_FRENTE[dianteira] + 0.22 * (abs(dx) / 0.8) ** 1.6
        r = (0.25 if k else 0.21) * (1.0 if dianteira else 0.88)
        out.append((V((pe[0] + dx * s, yf + 0.22, 0.30)), r))
    return out

def metaball(nome, elems, res):
    mb = bpy.data.metaballs.new(nome); o = bpy.data.objects.new(nome, mb); sc.collection.objects.link(o)
    mb.resolution = mb.render_resolution = res
    for item in elems:
        c, eixos = item[0], item[1]; rot = item[2] if len(item) > 2 else (0, 0, 0)
        e = mb.elements.new(type="ELLIPSOID"); m = max(eixos); e.co = c; e.radius = m / K_MB
        e.size_x, e.size_y, e.size_z = eixos[0] / m, eixos[1] / m, eixos[2] / m
        e.rotation = Euler([math.radians(a) for a in rot]).to_quaternion()
    return mb, o
def capsula(mb, a, b, r):
    d = b - a; e = mb.elements.new(type="CAPSULE"); e.co = (a + b) * 0.5; e.radius = r * 0.92 / K_MB; e.size_x = d.length * 0.5
    e.rotation = V((1, 0, 0)).rotation_difference(d.normalized())
mbc, oc = metaball("Vol_Corpo", TRONCO, 0.085)
for s in (1, -1):
    for dian in (True, False):
        j = perna(s, dian)
        for (a, ra), (b, rb) in zip(j, j[1:]): capsula(mbc, a, b, (ra + rb) * 0.45)
        for c, e_ in massas_perna(s, dian):
            e = mbc.elements.new(type="ELLIPSOID"); m = max(e_); e.co = c; e.radius = m / K_MB
            e.size_x, e.size_y, e.size_z = e_[0] / m, e_[1] / m, e_[2] / m
mbh, oh = metaball("Vol_Cabeca", CABECA, 0.035)
mbd, od = metaball("Vol_Dedos", [], 0.04)
for s in (1, -1):
    for dian in (True, False):
        for c, r in dedos(s, dian):
            e = mbd.elements.new(type="ELLIPSOID"); e.co = c; e.radius = r * 1.15 / K_MB; e.size_x, e.size_y, e.size_z = 0.85, 1.0, 0.95
dg = bpy.context.evaluated_depsgraph_get()
partes = []
for o in (oc, oh, od):
    m = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); p = bpy.data.objects.new("tmp", m); sc.collection.objects.link(p); partes.append(p)
    bpy.data.objects.remove(o)
for p in sc.objects: p.select_set(p in partes)
bpy.context.view_layer.objects.active = partes[0]; bpy.ops.object.join()
ob = bpy.context.object; ob.name = ob.data.name = "CR_Urso_Corpo"
rm = ob.modifiers.new("Remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.045; rm.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=rm.name)
zmin = min(v.co.z for v in ob.data.vertices)
for v in ob.data.vertices: v.co.z -= zmin
ZMIN = zmin
# suavizacao forte no corpo, leve na cabeca (preserva arcadas, ponte nasal, labios)
vg = ob.vertex_groups.new(name="liso")
for v in ob.data.vertices: vg.add([v.index], 1.0 - 0.8 * suave((-6.0 - v.co.y) / 0.6), "REPLACE")
sm = ob.modifiers.new("Liso", "SMOOTH"); sm.factor = 0.5; sm.iterations = 8; sm.vertex_group = "liso"
bpy.ops.object.modifier_apply(modifier=sm.name)
sm = ob.modifiers.new("Liso2", "SMOOTH"); sm.factor = 0.3; sm.iterations = 2
bpy.ops.object.modifier_apply(modifier=sm.name)
for v in ob.data.vertices:                                   # sola achatada (apoio plantigrado)
    if v.co.z < 0.16: v.co.z = 0.16 * suave(v.co.z / 0.16) ** 0.5 if v.co.z > 0.02 else 0.0

# ================================================================== ROSTO (escultura por deslocamento)
OLHO_C = {1: V((0.50, -7.86, 6.72)), -1: V((-0.50, -7.86, 6.72))}
OLHAR = {s: V((0.38 * s, -1.0, 0.02)).normalized() for s in (1, -1)}
R_OLHO = 0.115
def labio_z(y): return 6.00 - 0.05 * suave((y + 9.0) / 1.6)     # linha da boca desce de leve para o canto
CANTO_Y = -7.30
bm = bmesh.new(); bm.from_mesh(ob.data); bm.normal_update()
for v in bm.verts:
    p, nrm = v.co, v.normal; x, y, z = p
    for s in (1, -1):
        e = OLHO_C[s]; d = (p - e).length
        if d < 0.34: p -= nrm * 0.11 * (1 - d / 0.34) ** 1.5                        # orbita funda
        d = (p - (e + V((0.02 * s, 0.04, 0.17)))).length
        if d < 0.30: p += nrm * 0.045 * (1 - d / 0.30) ** 2                          # arcada sobre o olho (olhar pesado)
        d = (p - V((0.16 * s, -9.16, 6.40))).length
        if d < 0.13: p -= nrm * 0.10 * (1 - d / 0.13) ** 1.2                         # narinas
        d = (p - V((0.24 * s, -9.07, 6.38))).length
        if d < 0.10: p += nrm * 0.02 * (1 - d / 0.10)                                # aba da narina
    if y < -6.9 and z > 7.05 and abs(x) < 0.10: p -= nrm * 0.03 * (1 - abs(x) / 0.10) * suave((-6.9 - y) / 0.4)  # sulco frontal
    if -9.25 < y < -8.6 and abs(x) < 0.05 and 6.05 < z < 6.30: p -= nrm * 0.025 * (1 - abs(x) / 0.05)  # filtro do labio
    if -9.2 < y < CANTO_Y and z < 6.35:                                                # dobra do labio superior sobre o inferior
        dz = z - (labio_z(y) + 0.05)
        if -0.05 < dz < 0.10: p += nrm * 0.03 * gauss(dz, 0.03, 0.04) * suave((abs(x) - 0.15) / 0.2)
bm.to_mesh(ob.data); bm.free(); ob.data.update()

# ================================================================== BOCA (fenda ate a comissura + cavidade profunda)
def mat_simples(nome, cor, rug=0.6):
    m = bpy.data.materials.new(nome); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = cor; b.inputs["Roughness"].default_value = rug
    return m
M_PELE = bpy.data.materials.new("M_Urso_Pele"); ob.data.materials.append(M_PELE)
M_BOCA = mat_simples("M_Urso_Boca", (0.20, 0.03, 0.03, 1), 0.35)
def fenda():
    m = bpy.data.meshes.new("Fenda"); b = bmesh.new(); N = 16; secs = []
    for i in range(N + 1):
        t = i / N; y = lerp(-10.2, CANTO_Y, t); z = labio_z(y)
        meia = 0.012 * (1 - suave((t - 0.84) / 0.16)) + 0.002
        secs.append([b.verts.new((xx, y, z + zz)) for xx, zz in ((-1.6, -meia), (1.6, -meia), (1.6, meia), (-1.6, meia))])
    for a, c in zip(secs, secs[1:]):
        for k in range(4): b.faces.new((a[k], a[(k + 1) % 4], c[(k + 1) % 4], c[k]))
    b.faces.new(secs[0][::-1]); b.faces.new(secs[-1]); bmesh.ops.recalc_face_normals(b, faces=b.faces)
    b.to_mesh(m); b.free(); o = bpy.data.objects.new("Fenda", m); sc.collection.objects.link(o); return o
def elipsoide_obj(nome, c, r, seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=c, segments=seg, ring_count=seg // 2)
    o = bpy.context.object; o.name = nome; o.scale = r; bpy.ops.object.transform_apply(scale=True); return o
# cavidade: espaco entre palato e assoalho, mais larga atras (molares); deixa paredes de 0,10 para os labios
CORTES = [fenda(), elipsoide_obj("Cav1", (0, -8.30, labio_z(-8.3) + 0.01), (0.36, 0.72, 0.15)),
          elipsoide_obj("Cav2", (0, -7.70, labio_z(-7.7) + 0.00), (0.42, 0.42, 0.18))]
for c in CORTES: c.data.materials.append(M_BOCA)
for c in CORTES:
    bo = ob.modifiers.new("Boca", "BOOLEAN"); bo.operation = "DIFFERENCE"; bo.solver = "EXACT"; bo.object = c; bo.material_mode = "TRANSFER"
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier=bo.name); bpy.data.objects.remove(c)
BVH = BVHTree.FromObject(ob, bpy.context.evaluated_depsgraph_get())
def bater(o_, d_, dist=4.0):
    h = BVH.ray_cast(o_, d_.normalized(), dist); return h[0], h[1]
def arcada(y, z, s, recuo):
    """ponto da arcada: parede externa do focinho na altura z, recuada para dentro"""
    ult = None; o_ = V((0, y, z))
    for _ in range(6):
        h, n_ = bater(o_, V((s, 0, 0)))
        if h is None: break
        ult = h; o_ = h + V((s * 0.005, 0, 0))
    return None if ult is None else ult - V((s * recuo, 0, 0))

# ================================================================== PECAS RIGIDAS
def tubo(pts, raios, nome, achat=0.85):
    m = bpy.data.meshes.new(nome); o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    o.location = pts[0]; b = bmesh.new(); vs = [b.verts.new(p - pts[0]) for p in pts]
    for a, c in zip(vs, vs[1:]): b.edges.new((a, c))
    b.to_mesh(m); b.free()
    k = o.modifiers.new("Pele", "SKIN"); k.use_smooth_shade = True
    for i, d in enumerate(m.skin_vertices[0].data): d.radius = (raios[i], raios[i] * achat); d.use_root = i == 0
    s2 = o.modifiers.new("Sub", "SUBSURF"); s2.levels = s2.render_levels = 2
    bpy.context.view_layer.objects.active = o
    for mm in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mm.name)
    return o
# --- dentes: por lado 3 incisivos, canino forte, diastema, 3 pre-molares pequenos, 2 molares largos
DENTES, GENGIVAS = [], []
for sup in (True, False):
    dz = -1 if sup else 1; zg = (lambda y: labio_z(y) + (0.030 if sup else -0.030))
    for s in (1, -1):
        arco = []
        for y in [lerp(-9.00, -7.45, i / 14) for i in range(15)]:
            p = arcada(y, zg(y), s, 0.13 + 0.05 * suave((y + 8.9) / 0.4))
            if p is not None: p.z = zg(y); arco.append(p)
        if len(arco) > 3:                                                  # gengiva: cordao rosado ao longo da arcada
            GENGIVAS.append(tubo([a - V((0, 0, dz * 0.01)) for a in arco], [0.055] * len(arco), "Gengiva_" + ("Sup" if sup else "Inf"), 0.7))
        def em(y):
            return min(arco, key=lambda a: abs(a.y - y)).copy() if arco else None
        TAB = [(-8.98, 0.07, 0.030, 0.45), (-8.93, 0.08, 0.034, 0.75), (-8.86, 0.09, 0.038, 1.0),       # incisivos
               (-8.70, 0.36 if sup else 0.30, 0.085, 1.0),                                                    # canino
               (-8.22, 0.06, 0.035, 1.0), (-8.05, 0.07, 0.040, 1.0), (-7.88, 0.08, 0.050, 1.0),            # pre-molares
               (-7.68, 0.09, 0.075, 1.0), (-7.50, 0.08, 0.072, 1.0)]                                         # molares
        for k, (y, comp, r, fx) in enumerate(TAB):
            p = em(y)
            if p is None: continue
            p.x *= fx; p.z = zg(y) + dz * (-0.03)
            curva = V((0, -0.025 if k == 3 else 0.0, 0)) * (1 if sup else -1)
            pts = [p, p + V((0, 0, dz * comp * 0.55)) + curva * 0.5, p + V((0, 0, dz * comp)) + curva]
            ra = [r, r * (0.72 if k == 3 else 0.85), 0.006 if k <= 3 else r * 0.6]
            DENTES.append(tubo(pts, ra, "Dente_" + ("Sup" if sup else "Inf"), 0.80 if k == 3 else 0.6))
LINGUA = elipsoide_obj("Lingua", (0, -8.05, labio_z(-8.05) - 0.12), (0.30, 0.62, 0.075))
for v in LINGUA.data.vertices:                                             # sulco central e ponta arredondada
    v.co.z -= 0.025 * math.exp(-(v.co.x / 0.06) ** 2) * (v.co.z > LINGUA.location.z * 0 + 0)
# --- olhos (globo com iris/pupila pelo eixo local -Y) e palpebras em amendoa
OLHOS, PALP = [], []
for s in (1, -1):
    c = OLHO_C[s] - OLHAR[s] * 0.035
    bpy.ops.mesh.primitive_uv_sphere_add(radius=R_OLHO, location=c, segments=28, ring_count=14)
    o = bpy.context.object; o.name = "Olho"; bpy.ops.object.shade_smooth()
    o.rotation_euler = V((0, -1, 0)).rotation_difference(OLHAR[s]).to_euler(); OLHOS.append(o)
    # palpebras: anel em amendoa no plano perpendicular ao olhar; superior mais baixa e grossa (expressao)
    up = V((0, 0, 1)); hz = OLHAR[s].cross(up).normalized(); vt = hz.cross(OLHAR[s]).normalized()
    pts, rr = [], []
    for i in range(25):
        a = 2 * math.pi * i / 24
        sup_ = math.sin(a) > 0
        q = c + OLHAR[s] * (R_OLHO * 0.55) + hz * math.cos(a) * R_OLHO * 1.05 + vt * math.sin(a) * R_OLHO * (0.62 if sup_ else 0.72)
        if sup_: q -= vt * 0.012
        pts.append(q); rr.append(0.030 if sup_ else 0.022)
    PALP.append(tubo(pts, rr, "Palpebra", 0.8))
# --- orelhas: concha arredondada com espessura e inserção no cranio
ORELHAS = []
for s in (1, -1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.36, segments=24, ring_count=12, location=(0, 0, 0))
    o = bpy.context.object; o.name = "Orelha"
    bmo = bmesh.new(); bmo.from_mesh(o.data)
    bmesh.ops.delete(bmo, geom=[v for v in bmo.verts if v.co.y < -0.06], context="VERTS")     # meia esfera: concha aberta para -Y
    for v in bmo.verts: v.co.y *= 0.55; v.co.z *= 1.05
    bmo.to_mesh(o.data); bmo.free()
    so = o.modifiers.new("Esp", "SOLIDIFY"); so.thickness = 0.07; so.offset = 1
    bpy.ops.object.modifier_apply(modifier=so.name)
    o.location = V((0.86 * s, -6.62, 7.50)); o.rotation_euler = Euler((math.radians(-12), 0, math.radians(-28 * s)))
    bpy.ops.object.shade_smooth(); ORELHAS.append(o)
# --- garras: base grossa dentro do bulbo do dedo, curva forte para baixo, leque de orientacoes
GARRAS = []
for s in (1, -1):
    for dian in (True, False):
        L = 1.05 if dian else 0.68; r0 = 0.20 if dian else 0.15
        for k, (c, r) in enumerate(dedos(s, dian)):
            c = c - V((0, 0, ZMIN))
            ang = math.radians((-14, -6, 0, 7, 15)[k]) * s + math.radians(rnd.uniform(-4, 4))
            dirv = Matrix.Rotation(ang, 3, "Z") @ V((0, -1, 0))
            base = c + dirv * (r * 0.35) + V((0, 0, 0.02))
            pts = [base + dirv * L * t + V((0, 0, 0.10 * math.sin(math.pi * t * 0.8) * L - (base.z - 0.035) * t ** 2.2)) for t in (0, 0.25, 0.5, 0.75, 1.0)]
            esc = rnd.uniform(0.9, 1.08)
            GARRAS.append(tubo(pts, [r0 * esc, r0 * 0.88 * esc, r0 * 0.65 * esc, r0 * 0.38 * esc, 0.012], "Garra", 1.25))
print("URSO_PECAS dentes", len(DENTES), "gengivas", len(GENGIVAS), "garras", len(GARRAS))

# ================================================================== MATERIAIS
def n(nt, t, **kw):
    x = nt.nodes.new(t)
    for k, v in kw.items(): setattr(x, k, v)
    return x
def rampa(nt, L, ent, pares):
    r = n(nt, "ShaderNodeValToRGB"); L.new(ent, r.inputs[0]); el = r.color_ramp.elements
    el[0].position, el[0].color = pares[0]; el[1].position, el[1].color = pares[-1]
    for pos, cor in pares[1:-1]: e = el.new(pos); e.color = cor
    return r
def mr(nt, L, ent, a, b_, c=0.0, d=1.0):
    x = n(nt, "ShaderNodeMapRange"); x.inputs[1].default_value = a; x.inputs[2].default_value = b_
    x.inputs[3].default_value = c; x.inputs[4].default_value = d; L.new(ent, x.inputs[0]); return x.outputs[0]
def mix(nt, L, fac, a, b_):
    x = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(fac, x.inputs["Factor"])
    for i, c in ((6, a), (7, b_)):
        if isinstance(c, tuple): x.inputs[i].default_value = c
        else: L.new(c, x.inputs[i])
    return x.outputs[2]
def op(nt, L, o_, a, b_=None, v=None):
    x = n(nt, "ShaderNodeMath", operation=o_); L.new(a, x.inputs[0])
    if b_ is not None: L.new(b_, x.inputs[1])
    if v is not None: x.inputs[1].default_value = v
    return x.outputs[0]
def mat_pele():
    m = M_PELE; m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; L = nt.links
    at = n(nt, "ShaderNodeAttribute", attribute_name="Pos_Repouso"); pos = n(nt, "ShaderNodeSeparateXYZ"); L.new(at.outputs["Vector"], pos.inputs[0])
    ax = n(nt, "ShaderNodeMath", operation="ABSOLUTE"); L.new(pos.outputs["X"], ax.inputs[0])
    ru = n(nt, "ShaderNodeTexNoise"); ru.inputs["Scale"].default_value = 1.4; ru.inputs["Detail"].default_value = 6; L.new(at.outputs["Vector"], ru.inputs["Vector"])
    # pelo curto pintado: estrias finas orientadas para tras (Y) e para baixo
    est = n(nt, "ShaderNodeVectorMath", operation="MULTIPLY"); est.inputs[1].default_value = (9.0, 2.2, 1.4); L.new(at.outputs["Vector"], est.inputs[0])
    fino = n(nt, "ShaderNodeTexNoise"); fino.inputs["Scale"].default_value = 14; fino.inputs["Detail"].default_value = 8; fino.inputs["Roughness"].default_value = 0.7
    L.new(est.outputs[0], fino.inputs["Vector"])
    medio = rampa(nt, L, ru.outputs["Fac"], [(0.35, (0.070, 0.036, 0.016, 1)), (0.65, (0.125, 0.068, 0.030, 1))])
    cor = mix(nt, L, op(nt, L, "MULTIPLY", mr(nt, L, pos.outputs["Z"], 3.2, 0.8), v=0.8), medio.outputs["Color"], (0.028, 0.015, 0.008, 1))
    cab = mr(nt, L, pos.outputs["Y"], -6.6, -7.6)                                   # rosto castanho-dourado
    cor = mix(nt, L, op(nt, L, "MULTIPLY", cab, v=0.85), cor, (0.20, 0.115, 0.055, 1))
    foc = op(nt, L, "MULTIPLY", mr(nt, L, pos.outputs["Y"], -7.9, -8.5), mr(nt, L, pos.outputs["Z"], 6.85, 6.55))
    cor = mix(nt, L, op(nt, L, "MULTIPLY", foc, v=0.75), cor, (0.30, 0.19, 0.10, 1))  # focinho mais claro
    # mascara da orbita (pele escura ao redor do olho)
    for s in (1, -1):
        e = OLHO_C[s]
        dv = n(nt, "ShaderNodeVectorMath", operation="DISTANCE"); L.new(at.outputs["Vector"], dv.inputs[0]); dv.inputs[1].default_value = e
        cor = mix(nt, L, mr(nt, L, dv.outputs["Value"], 0.24, 0.15), cor, (0.035, 0.022, 0.014, 1))
    nariz = op(nt, L, "MULTIPLY", mr(nt, L, pos.outputs["Y"], -8.80, -8.92), mr(nt, L, pos.outputs["Z"], 6.14, 6.22))
    nariz = op(nt, L, "MULTIPLY", nariz, mr(nt, L, ax.outputs[0], 0.40, 0.33))
    cor = mix(nt, L, nariz, cor, (0.010, 0.009, 0.009, 1))
    # labios: borda preta continua ate a comissura (faixa fina ao redor da fenda)
    zl = n(nt, "ShaderNodeMath", operation="SUBTRACT"); L.new(pos.outputs["Z"], zl.inputs[0]); zl.inputs[1].default_value = labio_z(-8.4)
    azl = n(nt, "ShaderNodeMath", operation="ABSOLUTE"); L.new(zl.outputs[0], azl.inputs[0])
    lab = op(nt, L, "MULTIPLY", mr(nt, L, azl.outputs[0], 0.12, 0.05), mr(nt, L, pos.outputs["Y"], CANTO_Y + 0.10, CANTO_Y - 0.05))
    cor = mix(nt, L, lab, cor, (0.014, 0.010, 0.009, 1))
    estr = mix(nt, L, op(nt, L, "MULTIPLY", fino.outputs["Fac"], v=0.55), cor, (0.0, 0.0, 0.0, 1))
    L.new(estr, b.inputs["Base Color"])
    rg = mr(nt, L, op(nt, L, "MAXIMUM", nariz, lab), 0, 1, 0.80, 0.32); L.new(rg, b.inputs["Roughness"])
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.45; bp.inputs["Distance"].default_value = 0.02
    L.new(fino.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
def mat_boca():
    """interior: escuro perto dos labios (boca fechada so mostra linha preta), rosado no fundo; rugas no palato"""
    m = M_BOCA; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; L = nt.links
    at = n(nt, "ShaderNodeAttribute", attribute_name="Pos_Repouso"); pos = n(nt, "ShaderNodeSeparateXYZ"); L.new(at.outputs["Vector"], pos.inputs[0])
    ax = n(nt, "ShaderNodeMath", operation="ABSOLUTE"); L.new(pos.outputs["X"], ax.inputs[0])
    fundo = op(nt, L, "MULTIPLY", mr(nt, L, ax.outputs[0], 0.42, 0.25), mr(nt, L, pos.outputs["Y"], -9.05, -8.85))
    rug = n(nt, "ShaderNodeMath", operation="SINE"); L.new(op(nt, L, "MULTIPLY", pos.outputs["Y"], v=48.0), rug.inputs[0])
    rosa = mix(nt, L, mr(nt, L, rug.outputs[0], 0.6, 1.0), (0.42, 0.10, 0.10, 1), (0.22, 0.04, 0.05, 1))
    cor = mix(nt, L, fundo, (0.018, 0.010, 0.010, 1), rosa)
    L.new(cor, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.30
def mat_garra():
    """queratina marfim: base escura dentro do dedo, estrias longitudinais, ponta clara, brilho moderado"""
    m = bpy.data.materials.new("M_Urso_Garra"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; L = nt.links
    tc = n(nt, "ShaderNodeTexCoord"); dist = n(nt, "ShaderNodeVectorMath", operation="LENGTH"); L.new(tc.outputs["Object"], dist.inputs[0])
    wv = n(nt, "ShaderNodeTexWave"); wv.wave_type = "RINGS"; wv.inputs["Scale"].default_value = 40; wv.inputs["Distortion"].default_value = 3
    L.new(tc.outputs["Object"], wv.inputs["Vector"])
    gr = rampa(nt, L, mr(nt, L, dist.outputs["Value"], 0.0, 1.0), [(0.0, (0.10, 0.07, 0.045, 1)), (0.22, (0.36, 0.27, 0.16, 1)),
                                                                    (0.65, (0.62, 0.52, 0.36, 1)), (1.0, (0.80, 0.72, 0.56, 1))])
    cor = mix(nt, L, op(nt, L, "MULTIPLY", wv.outputs["Fac"], v=0.18), gr.outputs["Color"], (0.20, 0.15, 0.09, 1))
    L.new(cor, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.42
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; L.new(wv.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m
def mat_dente():
    m = bpy.data.materials.new("M_Urso_Dente"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; L = nt.links
    tc = n(nt, "ShaderNodeTexCoord"); dist = n(nt, "ShaderNodeVectorMath", operation="LENGTH"); L.new(tc.outputs["Object"], dist.inputs[0])
    gr = rampa(nt, L, mr(nt, L, dist.outputs["Value"], 0.0, 0.3), [(0.0, (0.50, 0.40, 0.28, 1)), (0.4, (0.78, 0.70, 0.55, 1)), (1.0, (0.90, 0.86, 0.76, 1))])
    L.new(gr.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.30; return m
def mat_olho():
    """iris ambar com raios, pupila redonda, cornea brilhante; sem emissao"""
    m = bpy.data.materials.new("M_Urso_Olho"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; L = nt.links
    tc = n(nt, "ShaderNodeTexCoord"); sep = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    # distancia ao eixo do olhar (-Y local)
    xz = n(nt, "ShaderNodeCombineXYZ"); L.new(sep.outputs["X"], xz.inputs[0]); L.new(sep.outputs["Z"], xz.inputs[2])
    rr = n(nt, "ShaderNodeVectorMath", operation="LENGTH"); L.new(xz.outputs[0], rr.inputs[0])
    frente = mr(nt, L, sep.outputs["Y"], 0.0, -0.05)
    raios = n(nt, "ShaderNodeTexNoise"); raios.inputs["Scale"].default_value = 60; L.new(tc.outputs["Object"], raios.inputs["Vector"])
    iris = mix(nt, L, mr(nt, L, rr.outputs["Value"], 0.035, 0.075), (0.62, 0.36, 0.06, 1), (0.30, 0.13, 0.02, 1))
    iris = mix(nt, L, op(nt, L, "MULTIPLY", raios.outputs["Fac"], v=0.35), iris, (0.12, 0.05, 0.01, 1))
    cor = mix(nt, L, mr(nt, L, rr.outputs["Value"], 0.030, 0.024), iris, (0.006, 0.004, 0.003, 1))     # pupila
    cor = mix(nt, L, op(nt, L, "SUBTRACT", mr(nt, L, rr.outputs["Value"], 0.080, 0.092), op(nt, L, "SUBTRACT", frente, v=1.0)), cor, (0.05, 0.03, 0.02, 1))
    L.new(cor, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.06
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 1.0
    return m
mat_pele(); mat_boca()
MG, MD, MO = mat_garra(), mat_dente(), mat_olho()
MGEN = mat_simples("M_Urso_Gengiva", (0.36, 0.07, 0.08, 1), 0.35); ML = mat_simples("M_Urso_Lingua", (0.45, 0.10, 0.11, 1), 0.38)
MPAL = mat_simples("M_Urso_Palpebra", (0.016, 0.011, 0.010, 1), 0.45); MOR = M_PELE
for o in DENTES: o.data.materials.append(MD)
for o in GENGIVAS: o.data.materials.append(MGEN)
for o in GARRAS: o.data.materials.append(MG)
for o in OLHOS: o.data.materials.append(MO)
for o in PALP: o.data.materials.append(MPAL)
for o in ORELHAS: o.data.materials.append(MOR)
LINGUA.data.materials.append(ML)
# posicao de repouso para materiais procedurais (nao muda com pose de teste)
for o in [ob] + ORELHAS:
    at = o.data.attributes.new("Pos_Repouso", "FLOAT_VECTOR", "POINT")
    for i, v in enumerate(o.data.vertices): at.data[i].vector = o.matrix_world @ v.co
col = bpy.data.collections.new("CR_Urso"); sc.collection.children.link(col)
for o in [ob, LINGUA] + DENTES + GENGIVAS + OLHOS + PALP + ORELHAS + GARRAS:
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o)
omb = max(v.co.z for v in ob.data.vertices if -4.0 < v.co.y < -2.0)
ys = [v.co.y for v in ob.data.vertices]; xs = [v.co.x for v in ob.data.vertices]
print("URSO_MEDIDAS pele: corcova %.2f comprimento %.2f largura %.2f faces %d" % (omb, max(ys) - min(ys), max(xs) - min(xs), len(ob.data.polygons)))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Urso_v2_corpo.blend"))
print("URSO_OK")
