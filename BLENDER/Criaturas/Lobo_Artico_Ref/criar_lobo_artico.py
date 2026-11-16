"""CR_LoboArtico: Lobo Artico ADULTO novo, a partir de ref/lobo-artico-referencia.png (ver asset-brief.md).
Nao usa malha, rig, materiais nem scripts dos prototipos antigos (Blockouts/lobo_*.py).
1 unidade = 1 stud. Frente = -Y, pes em Z=0, lado ESQUERDO do lobo = +X (lado visivel na referencia).
Corpo = grafo Skin (aneis nas articulacoes) -> Subsurf -> massas musculares -> remesh voxel -> mechas/rosto.
Pelagem: volume principal em geometria + cartoes de mechas com alpha (tex/pelo_atlas.png) so onde a silhueta pede.
Uso: blender -b --factory-startup -P criar_lobo_artico.py -- <saida_dir> [sem_render]"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
AQUI = os.path.dirname(os.path.abspath(__file__)); TEX = os.path.join(AQUI, "tex")
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; rnd = random.Random(7); V = Vector
def lerp(a, b, t): return a + (b - a) * t
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def gauss(d, s): return math.exp(-(d / s) ** 2)
import time; T0 = time.time()
def marco(txt): print("LOBO_T %6.1fs %s" % (time.time() - T0, txt), flush=True)
VOXEL = float(os.environ.get("LOBO_VOXEL", "0.04"))

# ------------------------------------------------------------------ eixo do corpo (y, z, raio_largura, raio_altura)
# raios ja incluem a espessura da pelagem; cernelha (topo do corpo sobre o ombro) ~6,3 studs
ESPINHA = [(-7.08, 6.07, 0.13, 0.14), (-6.74, 6.11, 0.20, 0.22), (-6.40, 6.19, 0.28, 0.30),           # focinho estreito
           (-6.05, 6.36, 0.44, 0.44), (-5.75, 6.48, 0.68, 0.52), (-5.42, 6.36, 0.76, 0.56),             # stop / cranio / nuca
           (-5.05, 5.90, 1.02, 0.92), (-4.60, 5.62, 1.28, 1.22), (-4.05, 5.24, 1.40, 1.40),            # pescoco com juba (atras das orelhas)
           (-3.35, 4.78, 1.18, 1.50), (-2.45, 4.76, 1.12, 1.45),                                       # peito fundo
           (-1.45, 4.86, 1.02, 1.24), (-0.45, 4.95, 0.92, 1.02), (0.55, 5.00, 0.92, 0.97),             # costelas -> lombo (barriga recolhida)
           (1.50, 5.00, 1.00, 1.02), (2.40, 4.90, 0.95, 0.95), (3.05, 4.72, 0.76, 0.80),               # quadril / garupa
           (3.45, 4.62, 0.44, 0.44),                                                                   # raiz da cauda
           (3.90, 4.32, 0.62, 0.64), (4.35, 3.72, 0.78, 0.80), (4.70, 3.02, 0.86, 0.86), (4.95, 2.32, 0.82, 0.82),
           (5.10, 1.68, 0.68, 0.68), (5.18, 1.18, 0.45, 0.45), (5.21, 0.86, 0.16, 0.16)]               # cauda cheia, pendendo
K_CAB, PIV_CAB = 1.12, V((0, -5.20, 6.20))       # cabeca maior que no blockout (referencia), juncao do pescoco fixa
def cab_y(y): return PIV_CAB.y + (y - PIV_CAB.y) * K_CAB
def cab_z(z): return PIV_CAB.z + (z - PIV_CAB.z) * K_CAB + 0.30   # cabeca um pouco mais erguida (referencia)
def cab(p): return V((p.x * K_CAB, cab_y(p.y), cab_z(p.z)))
ESPINHA = [((cab_y(y), cab_z(z), rx * K_CAB, rz * K_CAB) if y < -5.2 else (y, z, rx, rz)) for y, z, rx, rz in ESPINHA]
I_FOC, I_STOP, I_CRAN, I_NUCA, I_PESC, I_PEITO, I_QUAD, I_MEIO = 1, 3, 4, 5, 7, 9, 14, 12
MANDIBULA = [(cab(V((0, -5.70, 5.86))), 0.44 * K_CAB, 0.30 * K_CAB), (cab(V((0, -6.15, 5.86))), 0.24 * K_CAB, 0.15 * K_CAB),
             (cab(V((0, -6.75, 5.92))), 0.14 * K_CAB, 0.09 * K_CAB)]

def perna(s, dianteira):
    """digitigrada: cotovelo para tras, carpo reto, quartela levemente inclinada; joelho para frente, jarrete
    para tras, metatarso quase vertical. Musculo grosso em cima, canela fina embaixo (com pelo)."""
    if dianteira:
        return [(V((0.80 * s, -3.35, 4.30)), 0.60, 0.72), (V((0.80 * s, -2.98, 3.15)), 0.46, 0.50),
                (V((0.76 * s, -3.05, 2.20)), 0.36, 0.38), (V((0.74 * s, -3.12, 1.10)), 0.28, 0.29),
                (V((0.74 * s, -3.25, 0.50)), 0.25, 0.25), (V((0.74 * s, -3.40, 0.22)), 0.42, 0.21)]
    return [(V((0.86 * s, 1.72, 4.20)), 0.72, 0.82), (V((0.90 * s, 1.15, 3.00)), 0.50, 0.55),
            (V((0.84 * s, 2.42, 1.62)), 0.27, 0.30), (V((0.82 * s, 2.14, 0.58)), 0.24, 0.24),
            (V((0.82 * s, 1.92, 0.22)), 0.40, 0.21)]

def dedos(s, dianteira):
    base = perna(s, dianteira)[-1][0]; k = 1.0 if dianteira else 0.92
    return [[(base + V((dx * k * s, -0.38 * k, -0.06)), 0.15 * k, 0.12)] for dx in (-0.30, -0.10, 0.10, 0.30)]

# ------------------------------------------------------------------ corpo (grafo de nos -> metaballs elipsoidais)
# Cada aresta do grafo vira uma fileira densa de elipsoides (raios interpolados). Metaball = uniao suave, sempre
# fechada (o Skin quebrava com raios grandes e o voxel descartava o tronco). Calibrado: numa fileira com passo de
# 0,35 x raio, a superficie fica a 0,714 do raio do elemento -> R = 1/0,714.
NOS, ARESTAS = [], []
def cadeia(pts, inicio=None):
    ids = []
    for p, rx, ry in pts: NOS.append((V(p), rx, ry)); ids.append(len(NOS) - 1)
    if inicio is not None: ARESTAS.append((inicio, ids[0]))
    for a, b in zip(ids, ids[1:]): ARESTAS.append((a, b))
    return ids
esp = cadeia([(V((0, y, z)), rx, ry) for y, z, rx, ry in ESPINHA])
cadeia(MANDIBULA, esp[I_CRAN])
cadeia([(V((0, -4.72, 4.62)), 0.95, 0.80), (V((0, -4.52, 3.92)), 0.62, 0.52)], esp[I_PESC])      # babador da juba (peito)
for s in (1, -1):
    for dian, ini in ((True, esp[I_PEITO]), (False, esp[I_QUAD])):
        pv = cadeia(perna(s, dian), ini)
        for d in dedos(s, dian): cadeia(d, pv[-1])
    cadeia([(cab(V((0.60 * s, -5.55, 6.00))), 0.56, 0.56), (V((0.86 * s, -5.25, 5.75)), 0.46, 0.48)], esp[I_NUCA])   # colar das bochechas
    cadeia([(cab(V((0.34 * s, -5.88, 6.66))), 0.22, 0.16)], esp[I_STOP])                                            # arco da sobrancelha
mb = bpy.data.metaballs.new("Corpo_MB"); mb.resolution = mb.render_resolution = 0.05; mb.threshold = 0.6
omb = bpy.data.objects.new("Corpo_MB", mb); sc.collection.objects.link(omb)
K_MB = 1 / 0.714
def elipsoide(p, t, rx, ry):
    a1 = V((1, 0, 0)) - t * t.x
    if a1.length < 0.3: a1 = V((0, 1, 0)) - t * t.y
    a1.normalize(); a2 = t.cross(a1).normalized()
    rot = Matrix((a1, a2, t)).transposed().to_quaternion()
    e = mb.elements.new(type="ELLIPSOID"); e.co = p; e.rotation = rot; e.radius = K_MB; e.stiffness = 2.0
    e.size_x, e.size_y, e.size_z = rx, ry, min(rx, ry)
for a, b in ARESTAS:
    (pa, rxa, rya), (pb, rxb, ryb) = NOS[a], NOS[b]
    d = pb - pa; L = d.length; t = d.normalized() if L > 1e-6 else V((0, 1, 0))
    passo = 0.35 * min(rxa, rya, rxb, ryb); n_ = max(1, int(math.ceil(L / passo)))
    for i in range(n_ + 1):
        u = i / n_; elipsoide(pa + d * u, t, lerp(rxa, rxb, u), lerp(rya, ryb, u))
dg = bpy.context.evaluated_depsgraph_get()
me = bpy.data.meshes.new_from_object(omb.evaluated_get(dg)); me.name = "CR_LoboArtico_Corpo"
bpy.data.objects.remove(omb)
ob = bpy.data.objects.new("CR_LoboArtico_Corpo", me); sc.collection.objects.link(ob)
bpy.context.view_layer.objects.active = ob; ob.select_set(True)
marco("metaball %d verts (%d nos, %d arestas)" % (len(me.vertices), len(NOS), len(ARESTAS)))

# massas musculares sob o pelo (ombro, coxa, peito projetado, barriga recolhida, crista da juba)
for v in ob.data.vertices:
    p = v.co; x, y, z = p
    k = gauss(y + 3.25, 0.7) * gauss(z - 4.45, 0.9); p.x *= 1 + 0.10 * k                                   # escapula/ombro
    k = gauss(y - 1.75, 0.8) * gauss(z - 4.15, 0.9); p.x *= 1 + 0.12 * k                                   # coxa
    if -4.6 < y < -2.6 and z < 4.6 and abs(x) < 1.0: p.y -= 0.18 * suave((4.6 - z) / 0.8) * (1 - abs(x))  # peito projetado
    if -1.6 < y < 1.4 and z < 4.2: p.z += 0.16 * gauss(y + 0.1, 0.9) * suave((4.2 - z) / 0.5)              # barriga recolhida
    if -5.0 < y < -2.4 and z > 5.6: p.z += 0.06 * gauss(y + 3.8, 0.75) * suave((z - 5.6) / 0.7)            # crista da juba
    if y < -5.8 and z > 6.4: p.x *= 1 - 0.10 * suave((z - 6.4) / 0.25)                                    # testa mais estreita
rm = ob.modifiers.new("Remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = VOXEL; rm.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=rm.name)
sm = ob.modifiers.new("Liso", "SMOOTH"); sm.factor = 0.5; sm.iterations = 6
bpy.ops.object.modifier_apply(modifier=sm.name)
marco("voxel %d faces" % len(ob.data.polygons))

# ------------------------------------------------------------------ campo de fluxo do pelo
def fluxo(p, nrm):
    """direcao de crescimento do pelo, CONTINUA (mistura suave entre regioes, sem degraus no relevo):
    da cabeca para a cauda, juba para tras/baixo, peito e pernas para baixo, cauda ao longo do eixo"""
    x, y, z = p
    d_tr = V((0, 1.0, -0.25 - 0.55 * suave(-nrm.z + 0.2)))
    d_ju = lerp(V((0, 0.55, -0.85)), V((0, -0.05, -1)), suave((-nrm.y - 0.2) / 0.5))
    d_ca = V((0.25 * math.copysign(1, x) * suave((abs(x) - 0.2) / 0.3), 1, -0.15 - 0.6 * suave((abs(x) - 0.3) / 0.4)))
    d_pe = V((0, 0.12, -1))
    d_cd = V((0, 0.05, -1))
    for a, b in zip(ESPINHA[16:], ESPINHA[17:]):
        if a[0] <= y <= b[0]: d_cd = V((0, b[0] - a[0], b[1] - a[1])).normalized(); break
    w_cab = suave((-5.1 - y) / 0.5); w_ju = suave((-1.9 - y) / 0.9)
    w_pe = suave((3.7 - z) / 0.6) * suave((abs(x) - 0.25) / 0.25); w_cd = suave((y - 3.15) / 0.4)
    d = lerp(d_tr, d_ju, w_ju); d = lerp(d, d_ca, w_cab); d = lerp(d, d_pe, w_pe * (1 - w_cab)); d = lerp(d, d_cd, w_cd)
    d = d - nrm * d.dot(nrm)
    return d.normalized() if d.length > 1e-4 else V((0, 1, 0))

# mechas em geometria: relevo baixo e alongado no sentido do fluxo (volume, nao espinhos)
ob.data.update()
def normais():                                                        # le uma vez: v.normal depois de mover vertices recalcula tudo
    return [v.normal.copy() for v in ob.data.vertices]
NRM = normais()
for v, nrm in zip(ob.data.vertices, NRM):
    p = v.co.copy()
    f = fluxo(p, nrm); u = p.dot(f)
    q = (p - f * u) * 2.6 + f * u * 0.75                              # comprime ao longo do fluxo -> mechas alongadas
    juba = gauss(p.y + 3.9, 1.3) * suave((p.z - 3.8) / 0.8) + 0.8 * suave((p.y - 3.4) / 0.3)
    amp = 0.035 + 0.06 * min(juba, 1.0)
    n1 = noise.noise(q); n2 = noise.noise(q * 2.3 + V((3.1, 1.7, 0.4)))
    v.co = p + nrm * amp * (0.7 * n1 + 0.3 * n2)
ob.data.update()

marco("mechas geometria")
# ------------------------------------------------------------------ rosto: olhos, nariz, boca
def ray(o, d, dist=6.0):
    ok, hit, nrm, _ = ob.ray_cast(o, d.normalized(), distance=dist); return (hit, nrm) if ok else (None, None)
hit, nrm = ray(V((0.33 * K_CAB, -9.0, cab_z(6.56))), V((0, 1, 0)))  # olhos frontais, no stop
OLHO = (hit - nrm * 0.065) if hit is not None else cab(V((0.30, -6.0, 6.58))); NRM_OLHO = nrm if nrm is not None else V((0.7, -0.7, 0))
print("LOBO_OLHO", tuple(round(c, 3) for c in OLHO))
NRM = normais()
for v, nrm in zip(ob.data.vertices, NRM):
    p = v.co; x, y, z = p
    if y < cab_y(-6.0) and abs(x) > 0.05:                             # linha da boca
        zb = cab_z(5.92) - (y - cab_y(-6.0)) * 0.04
        p -= nrm * 0.03 * gauss(z - zb, 0.025) * suave((cab_y(-6.0) - y) / 0.15)
    for s_ in (1, -1):
        d = (p - cab(V((0.06 * s_, -7.21, 6.11)))).length                  # narinas
        if d < 0.07: p -= nrm * 0.035 * (1 - d / 0.07) ** 2
        d = (p - V((OLHO.x * s_, OLHO.y, OLHO.z))).length             # orbita
        if d < 0.17: p -= nrm * 0.045 * (1 - d / 0.17) ** 2
ob.data.update()

# ------------------------------------------------------------------ pecas: orelhas, olhos, garras
PECAS = []
def orelha(s):
    """triangular, base larga e grossa, ponta arredondada; concha aberta para a frente (pele interna escura);
    base enterrada no cranio. Pelos: cartoes curtos na borda/dorso e tufos claros dentro (ver semear_orelha)."""
    m = bpy.data.meshes.new("Orelha"); b = bmesh.new()
    alt, larg, prof, NV = 0.86, 0.92, 0.48, 12
    aneis = []
    for j in range(8):
        t = j / 7; w = larg * 0.5 * (1 - t ** 1.6) ** 0.9 * (1 - 0.55 * t) + 0.02; dp = prof * 0.5 * (1 - t) ** 0.8 + 0.01
        anel = []
        for i in range(NV):
            a = 2 * math.pi * i / NV; cx, cy = math.cos(a) * w, math.sin(a) * dp
            if cy < 0: cy *= 0.15 + 0.85 * t                          # face da frente concava (concha)
            anel.append(b.verts.new((cx, cy, t * alt - 0.15)))
        aneis.append(anel)
    for j in range(7):
        for i in range(NV):
            f = b.faces.new((aneis[j][i], aneis[j][(i + 1) % NV], aneis[j + 1][(i + 1) % NV], aneis[j + 1][i]))
            a = 2 * math.pi * (i + 0.5) / NV
            f.material_index = 1 if (math.sin(a) < -0.25 and j < 6) else 0
    b.faces.new(aneis[-1][::-1]); b.faces.new(aneis[0])
    b.to_mesh(m); b.free()
    o = bpy.data.objects.new("CR_LoboArtico_Orelha_" + ("E" if s > 0 else "D"), m); sc.collection.objects.link(o)
    o.location = cab(V((0.42 * s, -5.62, 6.86))); o.scale = (K_CAB,) * 3
    o.rotation_euler = (math.radians(-12), math.radians(18 * s), math.radians(-22 * s))
    sd = o.modifiers.new("Sub", "SUBSURF"); sd.levels = sd.render_levels = 2
    for pl in m.polygons: pl.use_smooth = True
    return o
ORELHAS = [orelha(1), orelha(-1)]
OLHOS = []
for s in (1, -1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.092, location=(OLHO.x * s, OLHO.y, OLHO.z), segments=24, ring_count=12)
    o = bpy.context.object; o.name = "CR_LoboArtico_Olho_" + ("E" if s > 0 else "D")
    n_ = V((NRM_OLHO.x * s, NRM_OLHO.y, NRM_OLHO.z)).normalized()
    o.rotation_euler = n_.to_track_quat("Z", "Y").to_euler(); o.scale = (1.45, 0.55, 0.62)
    bpy.ops.object.shade_smooth(); OLHOS.append(o)
def tubo(pts, r0, nome, expo=1.2):
    m = bpy.data.meshes.new(nome); o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    o.location = pts[0]; b = bmesh.new(); vs = [b.verts.new(p - pts[0]) for p in pts]
    for a, c in zip(vs, vs[1:]): b.edges.new((a, c))
    b.to_mesh(m); b.free()
    k = o.modifiers.new("Pele", "SKIN"); k.use_smooth_shade = True
    for i, d in enumerate(m.skin_vertices[0].data):
        r = r0 * (1 - i / (len(pts) - 1)) ** expo + 0.006; d.radius = (r, r); d.use_root = i == 0
    s2 = o.modifiers.new("Sub", "SUBSURF"); s2.levels = s2.render_levels = 1
    return o
GARRAS = []
for s in (1, -1):
    for dian in (True, False):
        for d in dedos(s, dian):
            c = d[0][0] + V((0, -0.11, -0.05))
            GARRAS.append(tubo([c, c + V((0, -0.08, -0.02)), c + V((0, -0.12, -0.07))], 0.042, "CR_LoboArtico_Garra"))

# ------------------------------------------------------------------ cristais do dorso (aparencia; nao definem elemento)
def cristal(base, direc, alt, raio, nome, lados=6):
    m = bpy.data.meshes.new(nome); b = bmesh.new()
    z0 = -0.25 * alt                                                   # base enterrada no pelo
    aneis = []
    for zf, rf in ((z0, 0.85), (0.0, 1.0), (0.62 * alt, 0.92)):
        anel = []
        for i in range(lados):
            a = 2 * math.pi * i / lados + 0.2; jit = 1 + rnd.uniform(-0.12, 0.12)
            anel.append(b.verts.new((math.cos(a) * raio * rf * jit, math.sin(a) * raio * rf * jit * 0.8, zf)))
        aneis.append(anel)
    topo = b.verts.new((raio * 0.15, 0, alt))
    for j in range(2):
        for i in range(lados):
            b.faces.new((aneis[j][i], aneis[j][(i + 1) % lados], aneis[j + 1][(i + 1) % lados], aneis[j + 1][i]))
    for i in range(lados): b.faces.new((aneis[2][i], aneis[2][(i + 1) % lados], topo))
    b.faces.new(aneis[0][::-1]); b.to_mesh(m); b.free()
    o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    o.location = base; o.rotation_euler = direc.normalized().to_track_quat("Z", "Y").to_euler()
    for pl in m.polygons: pl.use_smooth = False
    return o
CRISTAIS = []
# referencia: 4-5 cristais logo atras da crista da juba, no alto da cernelha, inclinados para tras.
# folga entre eles (pescoco/coluna dobram) e todos sobre o trecho toracico (pouca flexao).
for (y, dx, alt, r, inc, lat) in ((-3.05, 0.18, 0.80, 0.24, 0.60, 0.20), (-2.58, 0.30, 0.66, 0.21, 0.68, 0.35),
                                  (-2.15, 0.12, 0.55, 0.18, 0.75, 0.15), (-1.78, 0.30, 0.42, 0.15, 0.82, 0.40),
                                  (-3.45, 0.42, 0.48, 0.16, 0.50, 0.45), (-2.38, -0.14, 0.42, 0.15, 0.70, -0.25)):
    hit, nrm = ray(V((dx, y, 9.0)), V((0, 0, -1)))
    base = hit if hit is not None else V((dx, y, 6.2))
    CRISTAIS.append(cristal(base, V((lat, inc, 1.0)), alt, r, "CR_LoboArtico_Cristal"))

# ------------------------------------------------------------------ cartoes de mechas (alpha)
MARCA_C, MARCA_T = V((0.0, -3.05, 5.15)), 1.75                         # centro (y,z) e tamanho da marca no ombro esquerdo
def regiao(p, nrm):
    """(densidade, comprimento, largura, inclinacao, coluna do atlas) por regiao; densidade em cartoes/stud^2"""
    x, y, z = p
    if y > 3.35: return (12.0, rnd.uniform(0.95, 1.45), rnd.uniform(0.40, 0.55), rnd.uniform(0.30, 0.55), rnd.choice((0, 1, 1)))   # cauda
    if y < -5.1:
        if abs(x) > 0.48 and z < cab_z(6.4) and y > cab_y(-5.95): return (9.0, rnd.uniform(0.45, 0.75), rnd.uniform(0.22, 0.30), 0.40, 0)   # colar da bochecha
        if z > cab_z(6.55) and y > cab_y(-6.05) and nrm.z > 0.2: return (5.0, rnd.uniform(0.22, 0.38), rnd.uniform(0.14, 0.20), 0.10, 1)  # testa/cranio: curtos
        return (0.0, 0, 0, 0, 0)                                                                                                     # focinho: so geometria
    if z < 1.3:                                                                                                                      # patas: tufos curtos (nao por baixo)
        return ((6.0, rnd.uniform(0.18, 0.30), rnd.uniform(0.13, 0.18), 0.30, 0) if nrm.z > -0.3 and z > 0.12 else (0.0, 0, 0, 0, 0))
    if z < 3.5 and abs(x) > 0.35:                                                                                                    # pernas: franja atras
        atras = (y > -3.0 and y < -2.4) or (y > 1.9 and y < 2.7)
        return ((7.0 if atras else 4.5), rnd.uniform(0.32, 0.55), rnd.uniform(0.18, 0.26), 0.20, rnd.choice((0, 0, 0, 2)))
    juba = gauss(y + 4.1, 1.3) * suave((z - 3.6) / 0.7)
    if juba > 0.25: return (5.0 + 5.0 * juba, rnd.uniform(0.85, 1.35), rnd.uniform(0.36, 0.52), rnd.uniform(0.30, 0.50), rnd.choice((0, 0, 1)))
    if nrm.z < -0.45: return (2.6, rnd.uniform(0.45, 0.80), rnd.uniform(0.26, 0.36), 0.35, 2)                                       # franja da barriga
    if y > 1.0 and z < 4.6 and nrm.y > 0.2: return (3.0, rnd.uniform(0.55, 0.85), rnd.uniform(0.28, 0.38), 0.25, 0)                # "calcas" das coxas
    return (4.0, rnd.uniform(0.65, 1.05), rnd.uniform(0.30, 0.40), rnd.uniform(0.10, 0.20), rnd.choice((0, 1)))                    # tronco
def perto_marca(p):
    if p.x < 0.4: return 99.0
    return math.hypot((p.y - MARCA_C.y) / (MARCA_T * 0.55), (p.z - MARCA_C.z) / (MARCA_T * 0.6))
def perto_cristal(p): return min((p - c.location).length for c in CRISTAIS)

bm_c = bmesh.new(); bm_c.from_mesh(ob.data); bm_c.faces.ensure_lookup_table()
bvh = BVHTree.FromBMesh(bm_c)
cards_bm = bmesh.new(); uvl = cards_bm.loops.layers.uv.new("UVMap")
N_CARDS = 0; SEG = 3; DENS_K = float(os.environ.get("LOBO_DENS", "3.4"))
def cartao(c, nrm, t1, L, Wd, inc, col):
    """faixa curva com 2-3 segmentos, UV na coluna 'col' do atlas (raiz v=0, ponta v=1)"""
    global N_CARDS
    t2 = nrm.cross(t1).normalized()
    t1 = (t1 * math.cos(inc) + nrm * math.sin(inc)).normalized()      # sobe do corpo e volta a deitar na ponta
    giro = rnd.uniform(-0.25, 0.25); t1 = (t1 + t2 * giro).normalized(); t2 = nrm.cross(t1).normalized()
    raiz = c - nrm * 0.03
    ponta = raiz + t1 * L - nrm * (L * math.sin(inc) * 0.55)
    if ponta.z < 0.05:                                                 # nenhuma mecha atravessa o chao
        if raiz.z < 0.2: return
        L *= (raiz.z - 0.05) / max(raiz.z - ponta.z, 1e-4)
    u0, u1 = col * 0.25 + 0.012, col * 0.25 + 0.238
    fileira = []; seg = SEG if L >= 0.45 else 2                       # cartoes curtos com menos segmentos
    for j in range(seg + 1):
        t = j / seg
        eixo = raiz + t1 * L * t - nrm * (L * math.sin(inc) * 0.55) * t * t   # curva: ponta volta para a pele
        w = Wd * (1.0 - 0.15 * t)
        par = [cards_bm.verts.new(eixo - t2 * w * 0.5), cards_bm.verts.new(eixo + t2 * w * 0.5)]
        fileira.append((par, t))
    for (a, ta), (b_, tb) in zip(fileira, fileira[1:]):
        fc = cards_bm.faces.new((a[0], a[1], b_[1], b_[0]))
        for lp, uv in zip(fc.loops, ((u0, ta), (u1, ta), (u1, tb), (u0, tb))): lp[uvl].uv = uv
    N_CARDS += 1
for f in bm_c.faces:
    c = f.calc_center_median(); nrm = f.normal
    dens, L, Wd, inc, col = regiao(c, nrm)
    if dens <= 0: continue
    dm = perto_marca(c)
    if dm < 1.0: continue                                              # a marca fica visivel (pelo assentado, so geometria)
    if dm < 1.6: col = 3; L *= 0.7; inc *= 0.5                         # pontas azul-gelo em volta da marca
    pc = perto_cristal(c)
    if pc < 0.45: continue                                             # nao atravessar os cristais
    if pc < 0.9: col = 3
    if rnd.random() > DENS_K * dens * f.calc_area(): continue
    cartao(c, nrm, fluxo(c, nrm), L, Wd, inc, col)
N_CORPO = N_CARDS
dg0 = bpy.context.evaluated_depsgraph_get()
for o in ORELHAS:                                                      # pelos das orelhas
    me_o = o.evaluated_get(dg0).to_mesh(); mw = o.matrix_world; mn = mw.to_3x3().inverted().transposed()
    sobe = (mw.to_3x3() @ V((0, 0, 1))).normalized()
    for pl in me_o.polygons:
        c = mw @ pl.center; nrm = (mn @ pl.normal).normalized(); zl = pl.center.z
        dentro = pl.material_index == 1
        dens = (14.0 if zl < 0.45 else 6.0) if dentro else 9.0
        if rnd.random() > 4.0 * dens * pl.area * K_CAB ** 2: continue
        if dentro: cartao(c, nrm, sobe, rnd.uniform(0.28, 0.42), 0.16, 0.55, 1)
        else: cartao(c, nrm, sobe, rnd.uniform(0.18, 0.30), 0.14, 0.15, 0)
    o.evaluated_get(dg0).to_mesh_clear()
print("LOBO_CARTOES_ORELHAS", N_CARDS - N_CORPO)
marco("cartoes")
m_c = bpy.data.meshes.new("CR_LoboArtico_Pelagem"); cards_bm.to_mesh(m_c); cards_bm.free(); bm_c.free()
PELAGEM = bpy.data.objects.new("CR_LoboArtico_Pelagem", m_c); sc.collection.objects.link(PELAGEM)
for pl in m_c.polygons: pl.use_smooth = True
print("LOBO_CARTOES", N_CARDS, "faces", len(m_c.polygons))

# ------------------------------------------------------------------ materiais
def mat(nome):
    m = bpy.data.materials.new(nome)
    if m.node_tree is None: m.use_nodes = True
    nt = m.node_tree; return m, nt, nt.nodes["Principled BSDF"], nt.links
def n(nt, t, **kw):
    x = nt.nodes.new(t)
    for k, v in kw.items(): setattr(x, k, v)
    return x
def mr(nt, L, ent, a, b_, c=0.0, d=1.0):
    x = n(nt, "ShaderNodeMapRange"); x.inputs[1].default_value = a; x.inputs[2].default_value = b_
    x.inputs[3].default_value = c; x.inputs[4].default_value = d; L.new(ent, x.inputs[0]); return x.outputs[0]
def op(nt, L, o_, a, b_=None, v=None):
    x = n(nt, "ShaderNodeMath", operation=o_); L.new(a, x.inputs[0])
    if b_ is not None: L.new(b_, x.inputs[1])
    if v is not None: x.inputs[1].default_value = v
    return x.outputs[0]
def mix(nt, L, fac, a, b_):
    x = n(nt, "ShaderNodeMix", data_type="RGBA")
    if isinstance(fac, float): x.inputs["Factor"].default_value = fac
    else: L.new(fac, x.inputs["Factor"])
    for i, c in ((6, a), (7, b_)):
        if isinstance(c, tuple): x.inputs[i].default_value = c
        else: L.new(c, x.inputs[i])
    return x.outputs[2]
def mat_pelo_corpo():
    m, nt, b, L = mat("M_LoboArtico_Pelo")
    tc = n(nt, "ShaderNodeTexCoord"); geo = n(nt, "ShaderNodeNewGeometry")
    pos = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], pos.inputs[0])
    nr = n(nt, "ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], nr.inputs[0])
    # fios finos: ruido esticado no sentido dominante (Y no tronco, Z nas pernas)
    est_t = n(nt, "ShaderNodeMapping"); est_t.inputs["Scale"].default_value = (26, 4, 26); L.new(tc.outputs["Object"], est_t.inputs[0])
    est_p = n(nt, "ShaderNodeMapping"); est_p.inputs["Scale"].default_value = (26, 26, 4); L.new(tc.outputs["Object"], est_p.inputs[0])
    fios_t = n(nt, "ShaderNodeTexNoise"); fios_p = n(nt, "ShaderNodeTexNoise")
    for t_, e_ in ((fios_t, est_t), (fios_p, est_p)):
        t_.inputs["Scale"].default_value = 3.0; t_.inputs["Detail"].default_value = 6; L.new(e_.outputs[0], t_.inputs["Vector"])
    perna_f = mr(nt, L, pos.outputs["Z"], 3.4, 3.0)
    fx = n(nt, "ShaderNodeMix", data_type="FLOAT"); L.new(perna_f, fx.inputs["Factor"])
    L.new(fios_t.outputs["Fac"], fx.inputs[2]); L.new(fios_p.outputs["Fac"], fx.inputs[3]); fios = fx.outputs[0]
    manchas = n(nt, "ShaderNodeTexNoise"); manchas.inputs["Scale"].default_value = 1.2; L.new(tc.outputs["Object"], manchas.inputs["Vector"])
    # branco com sombras cinza frias: ventre, lado de baixo, dobras (AO) e raiz das mechas
    base = mix(nt, L, mr(nt, L, fios, 0.35, 0.7), (0.78, 0.80, 0.84, 1), (0.97, 0.975, 0.98, 1))
    base = mix(nt, L, op(nt, L, "MULTIPLY", mr(nt, L, manchas.outputs["Fac"], 0.4, 0.7), v=0.15), base, (0.88, 0.90, 0.94, 1))
    baixo = mr(nt, L, nr.outputs["Z"], -0.1, -0.8, 0.0, 0.45)
    base = mix(nt, L, baixo, base, (0.66, 0.70, 0.77, 1))
    ao = n(nt, "ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.6
    base = mix(nt, L, mr(nt, L, ao.outputs["AO"], 0.3, 1.0, 0.55, 0.0), base, (0.42, 0.47, 0.55, 1))
    # rosto: nariz negro, labios e contorno dos olhos cinza-escuro, leve creme frio no focinho
    nariz = op(nt, L, "MULTIPLY", mr(nt, L, pos.outputs["Y"], cab_y(-7.06), cab_y(-7.14)), mr(nt, L, pos.outputs["Z"], cab_z(5.96), cab_z(6.04)))
    base = mix(nt, L, nariz, base, (0.025, 0.025, 0.03, 1))
    ax = op(nt, L, "ABSOLUTE", pos.outputs["X"])
    labio_z = op(nt, L, "ADD", op(nt, L, "MULTIPLY", pos.outputs["Y"], v=-0.04), v=cab_z(5.92) + cab_y(-6.0) * 0.04)
    labio = op(nt, L, "MULTIPLY", mr(nt, L, op(nt, L, "ABSOLUTE", op(nt, L, "SUBTRACT", pos.outputs["Z"], labio_z)), 0.05, 0.025),
               mr(nt, L, pos.outputs["Y"], cab_y(-6.05), cab_y(-6.2)))
    base = mix(nt, L, op(nt, L, "MULTIPLY", labio, v=0.7), base, (0.10, 0.10, 0.11, 1))
    # contorno escuro dos olhos ("delineado" da referencia)
    axv = n(nt, "ShaderNodeCombineXYZ"); L.new(ax, axv.inputs[0]); L.new(pos.outputs["Y"], axv.inputs[1]); L.new(pos.outputs["Z"], axv.inputs[2])
    dv = n(nt, "ShaderNodeVectorMath", operation="DISTANCE"); L.new(axv.outputs[0], dv.inputs[0]); dv.inputs[1].default_value = tuple(OLHO)
    base = mix(nt, L, mr(nt, L, dv.outputs["Value"], 0.13, 0.105, 0.0, 0.85), base, (0.10, 0.10, 0.11, 1))
    # marca ciano em espiral no ombro ESQUERDO (+X); o lado direito fica sem marca [PROPOSTA]
    mu = mr(nt, L, pos.outputs["Y"], MARCA_C.y - MARCA_T / 2, MARCA_C.y + MARCA_T / 2)
    mv = mr(nt, L, pos.outputs["Z"], MARCA_C.z - MARCA_T / 2, MARCA_C.z + MARCA_T / 2)
    cxy = n(nt, "ShaderNodeCombineXYZ"); L.new(mu, cxy.inputs[0]); L.new(mv, cxy.inputs[1])
    timg = n(nt, "ShaderNodeTexImage", extension="CLIP"); timg.image = bpy.data.images.load(os.path.join(TEX, "marca_mascara.png"))
    timg.image.colorspace_settings.name = "Non-Color"; L.new(cxy.outputs[0], timg.inputs[0])
    sep = n(nt, "ShaderNodeSeparateColor"); L.new(timg.outputs["Color"], sep.inputs[0])
    lado = mr(nt, L, pos.outputs["X"], 0.45, 0.75)
    linha = op(nt, L, "MULTIPLY", sep.outputs[0], lado); halo = op(nt, L, "MULTIPLY", sep.outputs[1], lado)
    base = mix(nt, L, op(nt, L, "MULTIPLY", halo, v=0.45), base, (0.62, 0.86, 1.0, 1))
    base = mix(nt, L, linha, base, (0.45, 0.95, 1.0, 1))
    L.new(base, b.inputs["Base Color"])
    b.inputs["Emission Color"].default_value = (0.25, 0.92, 1.0, 1)
    L.new(op(nt, L, "ADD", op(nt, L, "MULTIPLY", linha, v=2.2), op(nt, L, "MULTIPLY", halo, v=0.12)), b.inputs["Emission Strength"])
    L.new(mr(nt, L, nariz, 0, 1, 0.78, 0.35), b.inputs["Roughness"])
    if "Sheen Weight" in b.inputs: b.inputs["Sheen Weight"].default_value = 0.35
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.55; bp.inputs["Distance"].default_value = 0.02
    L.new(fios, bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m
def mat_cartao():
    m, nt, b, L = mat("M_LoboArtico_Mechas")
    t = n(nt, "ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(TEX, "pelo_atlas.png"))
    uv = n(nt, "ShaderNodeUVMap"); L.new(uv.outputs[0], t.inputs[0])
    ao = n(nt, "ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.25
    cor = mix(nt, L, mr(nt, L, ao.outputs["AO"], 0.2, 1.0, 0.18, 0.0), t.outputs["Color"], (0.62, 0.67, 0.75, 1))
    L.new(cor, b.inputs["Base Color"]); L.new(t.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.7
    if "Sheen Weight" in b.inputs: b.inputs["Sheen Weight"].default_value = 0.4
    m.surface_render_method = "DITHERED"; m.use_backface_culling = False
    if hasattr(m, "use_transparent_shadow"): m.use_transparent_shadow = True
    return m
def mat_simples(nome, cor, rug, emis=None, forca=0.0):
    m, nt, b, L = mat(nome); b.inputs["Base Color"].default_value = cor; b.inputs["Roughness"].default_value = rug
    if emis: b.inputs["Emission Color"].default_value = emis; b.inputs["Emission Strength"].default_value = forca
    return m
def mat_olho():
    m, nt, b, L = mat("M_LoboArtico_Olho")
    tc = n(nt, "ShaderNodeTexCoord"); sep = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sep.inputs[0])
    d = op(nt, L, "ABSOLUTE", op(nt, L, "SUBTRACT", sep.outputs["Z"], v=0.5))       # Z local = eixo do olhar
    iris = mr(nt, L, sep.outputs["Z"], 0.52, 0.60)                                    # frente do globo
    pup = mr(nt, L, sep.outputs["Z"], 0.975, 0.985)
    anel = mix(nt, L, mr(nt, L, sep.outputs["Z"], 0.62, 0.95), (0.10, 0.38, 0.66, 1), (0.58, 0.90, 1.0, 1))
    cor = mix(nt, L, iris, (0.03, 0.03, 0.035, 1), anel)
    cor = mix(nt, L, pup, cor, (0.005, 0.005, 0.008, 1))
    L.new(cor, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.05
    b.inputs["Emission Color"].default_value = (0.3, 0.75, 1.0, 1)
    L.new(op(nt, L, "MULTIPLY", op(nt, L, "SUBTRACT", iris, pup), v=0.6), b.inputs["Emission Strength"])
    return m
def mat_cristal():
    m, nt, b, L = mat("M_LoboArtico_Cristal")
    tc = n(nt, "ShaderNodeTexCoord"); sep = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    gr = mix(nt, L, mr(nt, L, sep.outputs["Z"], -0.1, 0.8), (0.30, 0.62, 0.90, 1), (0.78, 0.95, 1.0, 1))
    L.new(gr, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.06
    b.inputs["Alpha"].default_value = 0.62
    b.inputs["Emission Color"].default_value = (0.45, 0.85, 1.0, 1); b.inputs["Emission Strength"].default_value = 0.35
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.6
    m.surface_render_method = "BLENDED"; m.use_backface_culling = False
    return m
MP, MCA = mat_pelo_corpo(), mat_cartao()
ob.data.materials.append(MP); PELAGEM.data.materials.append(MCA)
MOR = mat_simples("M_LoboArtico_OrelhaInterna", (0.34, 0.33, 0.34, 1), 0.7)
for o in ORELHAS:
    o.data.materials.append(MP)
    o.data.materials.append(MOR)
    for _ in ():
        pass
for o in OLHOS: o.data.materials.append(mat_olho()) if not o.data.materials else None
MG = mat_simples("M_LoboArtico_Garra", (0.06, 0.06, 0.065, 1), 0.35)
for o in GARRAS: o.data.materials.append(MG)
MCR = mat_cristal()
for o in CRISTAIS: o.data.materials.append(MCR)
# mechas nas bordas das orelhas (pelos claros na concha)
col = bpy.data.collections.new("CR_LoboArtico"); sc.collection.children.link(col)
for o in [ob, PELAGEM] + ORELHAS + OLHOS + GARRAS + CRISTAIS:
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o)
dg = bpy.context.evaluated_depsgraph_get()
def tris_ev(o): return sum(len(p.vertices) - 2 for p in o.evaluated_get(dg).data.polygons)
print("LOBO_TRIS_HIGH", {o.name: tris_ev(o) for o in (ob, PELAGEM)}, "total", sum(tris_ev(o) for o in col.objects if o.type == "MESH"))
zs = [v.co.z for v in ob.data.vertices if -3.6 < v.co.y < -2.6 and abs(v.co.x) < 0.3]
print("LOBO_CERNELHA_Z", round(max(zs), 2), "comprimento", round(min(v.co.y for v in ob.data.vertices), 2), round(max(v.co.y for v in ob.data.vertices), 2))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_HIGH.blend"))
print("LOBO_OK")
