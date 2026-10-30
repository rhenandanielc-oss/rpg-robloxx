"""GL_Dragao (Dragao Glacial): dragao de GELO inspirado em ref/ref_glacial.png (referencia do usuario 31/10), em POSE
NEUTRA para rig/animacao. Derivado de dragao_novo/criar_dragao_ref.py (CR_Dragao, fogo) com as MESMAS articulacoes
(cabeca, pescoco, ombros, quadril, patas, braco/dedos da asa): o rig do Silverwing e os clipes servem sem refazer.
O que muda (referencia): corpo mais esguio e elegante, pescoco fino, cabeca alongada com coroa de chifres finos
varridos para tras e babado de espinhos na mandibula, espinhos dorsais cristalinos, escamas azul-gelo com bordas
claras, ventre em placas quase brancas, membranas azul-palido translucidas, olhos azul-gelo.
Frente = -Y, pes em Z=0, simetrico em X.
Uso: blender -b --factory-startup -P criar_glacial_ref.py -- <saida_dir> [sem_render]"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, noise

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; rnd = random.Random(5); V = Vector
def lerp(a, b, t): return a + (b - a) * t
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

# ------------------------------------------------------------------ eixo do corpo (y, z, raio_largura, raio_altura)
ESPINHA = [(-0.965, 0.714, 0.020, 0.020), (-0.930, 0.721, 0.034, 0.031), (-0.885, 0.735, 0.045, 0.040), (-0.840, 0.753, 0.054, 0.048),
           (-0.79, 0.773, 0.060, 0.056), (-0.74, 0.781, 0.066, 0.061), (-0.69, 0.757, 0.062, 0.063),           # cabeca (conceito: focinho curto e alto)
           (-0.63, 0.712, 0.072, 0.076), (-0.57, 0.664, 0.083, 0.087), (-0.51, 0.617, 0.096, 0.100),            # pescoco grosso
           (-0.45, 0.572, 0.113, 0.118), (-0.37, 0.530, 0.148, 0.156),
           (-0.25, 0.497, 0.170, 0.180), (-0.10, 0.480, 0.174, 0.174), (0.05, 0.474, 0.162, 0.156),             # torax / ventre
           (0.18, 0.465, 0.146, 0.140), (0.30, 0.452, 0.128, 0.122),                                           # quadril
           (0.44, 0.430, 0.125, 0.115), (0.62, 0.400, 0.102, 0.094), (0.82, 0.362, 0.080, 0.074), (1.04, 0.322, 0.061, 0.057),
           (1.26, 0.287, 0.045, 0.042), (1.46, 0.262, 0.031, 0.029), (1.64, 0.247, 0.019, 0.018), (1.80, 0.240, 0.006, 0.006)]
I_FOC, I_SOBR, I_CRAN, I_NUCA, I_PEITO, I_MEIO, I_QUAD = 1, 4, 5, 6, 12, 13, 16
# GLACIAL: mesmos pontos, raios menores (referencia esguia): focinho fino, pescoco delgado, tronco enxuto, cauda longa fina
def _fator(i):
    if i <= 3: return 0.90, 0.94               # focinho um pouco mais fino que o do fogo (nao de crocodilo)
    if i <= 6: return 0.94, 0.96               # cranio
    if i <= 11: return 0.88, 0.92              # pescoco elegante (mais fino que o do fogo, com massa)
    if i <= 16: return 0.92, 0.92              # torax/ventre/quadril
    return 0.90, 0.90                          # cauda
ESPINHA = [(y, z, rx * _fator(i)[0], ry * _fator(i)[1]) for i, (y, z, rx, ry) in enumerate(ESPINHA)]
# (mandibula com os raios do CR: mais fina que o cranio fazia o Skin falhar e o remesh perdia pescoco/tronco)
MANDIBULA = [(V((0, -0.76, 0.720)), 0.058, 0.037), (V((0, -0.82, 0.702)), 0.049, 0.028), (V((0, -0.88, 0.692)), 0.036, 0.020),
             (V((0, -0.932, 0.691)), 0.022, 0.013)]

def perna(s, dianteira):
    return [(p, rx * 0.93, ry * 0.93) for p, rx, ry in _perna(s, dianteira)]
def _perna(s, dianteira):
    """articulacoes com angulo real (cotovelo para tras, joelho para frente, jarrete para tras): o rig dobra
    sempre para o lado certo e a silhueta deixa de ser coluna; musculo grosso em cima, canela fina embaixo"""
    if dianteira:
        return [(V((0.105 * s, -0.31, 0.470)), 0.135, 0.145), (V((0.140 * s, -0.27, 0.360)), 0.115, 0.110),
                (V((0.150 * s, -0.20, 0.265)), 0.078, 0.076), (V((0.152 * s, -0.235, 0.170)), 0.066, 0.062),
                (V((0.150 * s, -0.275, 0.075)), 0.050, 0.046), (V((0.152 * s, -0.300, 0.036)), 0.060, 0.032)]
    return [(V((0.115 * s, 0.22, 0.445)), 0.168, 0.168), (V((0.155 * s, 0.15, 0.340)), 0.150, 0.140),
            (V((0.165 * s, 0.07, 0.250)), 0.095, 0.090), (V((0.165 * s, 0.17, 0.150)), 0.066, 0.060),
            (V((0.162 * s, 0.245, 0.060)), 0.046, 0.040), (V((0.162 * s, 0.200, 0.030)), 0.060, 0.030)]

def dedos_pe(s, dianteira):
    base = perna(s, dianteira)[-1][0]
    return [[(base + V((dx * s, -0.060, -0.012)), 0.025, 0.018), (base + V((dx * 1.3 * s, -0.100, -0.017)), 0.018, 0.013)]
            for dx in (-0.042, -0.014, 0.014, 0.042)]

def asa(s):
    """pose neutra: abertas, erguidas ~12 graus, levemente varridas para tras # inferido (conceito tem asas erguidas)"""
    raiz, cot, pul = V((0.085 * s, -0.31, 0.60)), V((0.50 * s, -0.18, 0.78)), V((1.00 * s, -0.38, 0.90))
    dedos = [[V((1.50 * s, -0.53, 0.95)), V((1.92 * s, -0.45, 0.95)), V((2.20 * s, -0.28, 0.93))],
             [V((1.47 * s, -0.20, 0.89)), V((1.84 * s, 0.01, 0.85)), V((2.09 * s, 0.20, 0.81))],
             [V((1.34 * s, 0.05, 0.83)), V((1.57 * s, 0.36, 0.77)), V((1.71 * s, 0.67, 0.71))],
             [V((1.11 * s, 0.12, 0.79)), V((1.15 * s, 0.47, 0.71)), V((1.13 * s, 0.82, 0.64))]]
    return raiz, cot, pul, dedos

# ------------------------------------------------------------------ corpo (grafo Skin)
me = bpy.data.meshes.new("GL_Dragao_Corpo"); ob = bpy.data.objects.new("GL_Dragao_Corpo", me); sc.collection.objects.link(ob)
bm = bmesh.new(); raios = []
def vert(p, rx, ry): v = bm.verts.new(p); raios.append((rx, ry)); return v
def cadeia(pts, inicio=None):
    vs = [vert(p, rx, ry) for p, rx, ry in pts]
    if inicio is not None: bm.edges.new((inicio, vs[0]))
    for a, b in zip(vs, vs[1:]): bm.edges.new((a, b))
    return vs
esp = cadeia([(V((0, y, z)), rx, ry) for y, z, rx, ry in ESPINHA])
cadeia(MANDIBULA, esp[I_CRAN])
for s in (1, -1):
    for dian, ini in ((True, esp[I_PEITO]), (False, esp[I_QUAD])):
        pv = cadeia(perna(s, dian), ini)
        for d in dedos_pe(s, dian): cadeia(d, pv[-1])
    cadeia([(V((0.044 * s, -0.800, 0.802)), 0.025, 0.018), (V((0.053 * s, -0.836, 0.789)), 0.014, 0.011)], esp[I_SOBR])   # sobrancelha
    cadeia([(V((0.058 * s, -0.750, 0.742)), 0.031, 0.026), (V((0.052 * s, -0.800, 0.733)), 0.017, 0.014)], esp[I_CRAN])   # maca
    cadeia([(V((0.018 * s, -0.945, 0.733)), 0.013, 0.012)], esp[I_FOC])                                                   # narina
    raiz, cot, pul, dedos = asa(s)
    braco = cadeia([(raiz, 0.062, 0.058), (lerp(raiz, cot, 0.5), 0.042, 0.038), (cot, 0.033, 0.030),
                    (lerp(cot, pul, 0.5), 0.024, 0.021), (pul, 0.026, 0.023)], esp[I_PEITO])
    for d in dedos:
        cadeia([(lerp(pul, d[0], 0.5), 0.016, 0.013), (d[0], 0.013, 0.011), (d[1], 0.009, 0.008), (d[2], 0.004, 0.004)], braco[-1])
    cadeia([(pul + V((0.02 * s, -0.045, 0.012)), 0.012, 0.011), (pul + V((0.03 * s, -0.085, 0.008)), 0.005, 0.005)], braco[-1])
bm.to_mesh(me); bm.free()
sk = ob.modifiers.new("Pele", "SKIN"); sk.branch_smoothing = 0.6; sk.use_smooth_shade = True
for i, d in enumerate(me.skin_vertices[0].data): d.radius = raios[i]; d.use_root = (i == I_MEIO)
sub = ob.modifiers.new("Sub", "SUBSURF"); sub.levels = sub.render_levels = 2
bpy.context.view_layer.objects.active = ob; ob.select_set(True)
for m in list(ob.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)

# massas musculares (conceito: peito largo, ombros e coxas fortes, barriga funda)
for v in ob.data.vertices:
    p = v.co; x, y, z = p
    k = math.exp(-((y + 0.28) / 0.11) ** 2) * math.exp(-((z - 0.47) / 0.13) ** 2); p.x *= 1 + 0.12 * k      # ombros
    k = math.exp(-((y - 0.20) / 0.11) ** 2) * math.exp(-((z - 0.42) / 0.11) ** 2); p.x *= 1 + 0.11 * k      # quadris
    if -0.30 < y < 0.20 and z < 0.42: p.z -= 0.022 * math.exp(-((y + 0.05) / 0.17) ** 2) * suave((0.42 - z) / 0.08)
    if -0.36 < y < -0.18 and z < 0.48 and abs(x) < 0.12: p.y -= 0.025 * suave((0.48 - z) / 0.1) * (1 - abs(x) / 0.12)  # peito projetado
    if y < -0.68 and z > 0.67:                                                                               # cranio largo atras
        p.x *= 1 + 0.12 * math.exp(-((y + 0.75) / 0.05) ** 2) * suave((z - 0.70) / 0.05)
rm = ob.modifiers.new("Remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.0048; rm.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=rm.name)
sm = ob.modifiers.new("Liso", "SMOOTH"); sm.factor = 0.5; sm.iterations = 4
bpy.ops.object.modifier_apply(modifier=sm.name)
# corpo inteiro? (Skin com raios incompativeis gera casca aberta e o remesh perde pescoco/tronco sem erro)
for y0 in (-0.6, -0.1, 0.3):
    nv = sum(1 for v in ob.data.vertices if abs(v.co.y - y0) < 0.01 and abs(v.co.x) < 0.25 and v.co.z < 0.75)
    assert nv > 100, "corpo incompleto em y=%.2f (%d vertices): revise os raios do Skin" % (y0, nv)
ok_, hit, nrm_h, _ = ob.ray_cast(V((0.3, -0.806, 0.775)), V((-1, 0, 0)))
OLHO = hit - nrm_h * 0.004 if ok_ else V((0.052, -0.815, 0.762))
print("DRAGAO_OLHO", tuple(round(c, 3) for c in OLHO))
for v in ob.data.vertices:                                     # rosto: boca, narinas, orbitas, sobrancelha
    p, nrm = v.co, v.normal; x, y, z = p
    if y < -0.77 and abs(x) > 0.008:
        zb = 0.704 + (y + 0.95) * 0.07
        p -= nrm * 0.005 * math.exp(-((z - zb) / 0.0035) ** 2) * suave((-0.77 - y) / 0.025)
    for s_ in (1, -1):
        d = (p - V((0.018 * s_, -0.958, 0.733))).length
        if d < 0.010: p -= nrm * 0.006 * (1 - d / 0.010) ** 2
        d = (p - V((OLHO.x * s_, OLHO.y, OLHO.z))).length
        if d < 0.02: p -= nrm * 0.008 * (1 - d / 0.02) ** 2
ob.data.update()
K_CAB, PIV = 1.2, V((0, -0.64, 0.725))         # glacial: cabeca proporcional (referencia elegante); articulacoes iguais
def cabeca(p, w=None):
    w = suave((-0.61 - p.y) / 0.09) if w is None else w
    return PIV + (p - PIV) * (1 + (K_CAB - 1) * w)
for v in ob.data.vertices: v.co = cabeca(v.co)
ob.data.update()

# ------------------------------------------------------------------ membranas (presas so ao flanco, a frente do quadril)
def membrana(s):
    raiz, cot, pul, dedos = asa(s); pts, faces = [], []
    def grade(P, nu, nv):
        base = len(pts)
        for j in range(nv + 1):
            for i in range(nu + 1): pts.append(P(i / nu, j / nv))
        for j in range(nv):
            for i in range(nu):
                a = base + j * (nu + 1) + i; faces.append((a, a + 1, a + nu + 2, a + nu + 1))
    def dedo(d, t):
        cad = [pul, d[0], d[1], d[2]]; L = [0]
        for a, b in zip(cad, cad[1:]): L.append(L[-1] + (b - a).length)
        alvo = t * L[-1]
        for k in range(3):
            if alvo <= L[k + 1]: return lerp(cad[k], cad[k + 1], (alvo - L[k]) / (L[k + 1] - L[k]))
        return cad[-1]
    for a, b in zip(dedos, dedos[1:]):
        def P(u, t, a=a, b=b):
            pa, pb = dedo(a, t), dedo(b, t); p = lerp(pa, pb, u); corda = (pb - pa).length
            p += (pul - p).normalized() * 0.40 * corda * math.sin(math.pi * u) * t ** 3
            p.z -= 0.035 * math.sin(math.pi * u) * t
            return p
        grade(P, 10, 18)
    flanco = V((0.115 * s, 0.30, 0.47))
    def braco(u):
        if u < 0.55: return lerp(pul, cot, u / 0.55)
        return lerp(cot, raiz + V((0.0, 0.07, -0.02)), (u - 0.55) / 0.45)
    def borda(u):
        p = lerp(dedos[3][2], flanco, u); p += (cot - p).normalized() * 0.30 * math.sin(math.pi * u); return p
    def Pc(u, t):
        p = lerp(braco(u), borda(u), t); p.z -= 0.04 * math.sin(math.pi * u) * math.sin(math.pi * t)
        return lerp(p, dedo(dedos[3], t), (1 - u) ** 3)
    grade(Pc, 12, 16)
    def Pp(u, t):
        a = lerp(raiz + V((0, -0.02, 0.0)), pul, u); b = a + V((0, -0.08, 0.006)) * math.sin(math.pi * u)
        return lerp(a, b, t)
    grade(Pp, 10, 3)
    m = bpy.data.meshes.new("Membrana"); m.from_pydata([tuple(p) for p in pts], [], faces)
    o = bpy.data.objects.new("GL_Dragao_Membrana_" + ("L" if s > 0 else "R"), m); sc.collection.objects.link(o)
    for p in m.polygons: p.use_smooth = True
    o.modifiers.new("Solda", "WELD").merge_threshold = 0.002
    so = o.modifiers.new("Espessura", "SOLIDIFY"); so.thickness = 0.006; so.offset = 0
    ss = o.modifiers.new("Sub", "SUBSURF"); ss.levels = ss.render_levels = 1
    return o
MEMB = [membrana(1), membrana(-1)]
def para_cabeca(o):
    o.location = PIV + (o.location - PIV) * K_CAB; o.scale = o.scale * K_CAB

# ------------------------------------------------------------------ pecas rigidas
def tubo(pts, r0, nome, expo=1.15):
    m = bpy.data.meshes.new(nome); o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    o.location = pts[0]                                       # origem na base: o material mede a distancia ate ela
    b = bmesh.new(); vs = [b.verts.new(p - pts[0]) for p in pts]
    for a, c in zip(vs, vs[1:]): b.edges.new((a, c))
    b.to_mesh(m); b.free()
    k = o.modifiers.new("Pele", "SKIN"); k.use_smooth_shade = True
    n = len(pts)
    for i, d in enumerate(m.skin_vertices[0].data):
        r = r0 * (1 - i / (n - 1)) ** expo + 0.0012; d.radius = (r, r); d.use_root = i == 0
    s2 = o.modifiers.new("Sub", "SUBSURF"); s2.levels = s2.render_levels = 2
    return o
CHIFRES, ESPINHOS, GARRAS, OLHOS = [], [], [], []
for s in (1, -1):
    # COROA (referencia): chifre principal longo e fino varrido para tras, 3 pontas menores em leque atras/fora
    CHIFRES.append(tubo([V((0.030 * s, -0.745, 0.830)), V((0.044 * s, -0.690, 0.868)), V((0.056 * s, -0.625, 0.900)),
                         V((0.064 * s, -0.555, 0.925)), V((0.068 * s, -0.490, 0.950)), V((0.066 * s, -0.430, 0.985))], 0.017, "Chifre", 1.3))
    for k, (dx, dy, dz, comp, r0) in enumerate(((0.030, 0.050, 0.020, 0.115, 0.011), (0.046, 0.040, -0.006, 0.100, 0.010), (0.056, 0.026, -0.030, 0.080, 0.008))):
        b0 = V(((0.050 + 0.012 * k) * s, -0.722 + 0.016 * k, 0.820 - 0.022 * k))
        d = V((dx * s, dy, dz)).normalized()
        CHIFRES.append(tubo([b0, b0 + d * comp * 0.45 + V((0, 0, 0.006)), b0 + d * comp * 0.8 + V((0, 0, 0.010)), b0 + d * comp], r0, "Chifre_Coroa", 1.3))
    # babado de espinhos finos ao longo da mandibula e da bochecha, abrindo para tras (referencia)
    for k in range(5):
        base = V((0.048 * s, -0.800 + 0.022 * k, 0.722 - 0.004 * k)); comp = 0.070 - 0.007 * k
        dirv = V((0.45 * s, 1.0, 0.06 - 0.05 * k)).normalized()
        ESPINHOS.append(tubo([base, base + dirv * comp * 0.5 + V((0, 0, 0.004)), base + dirv * comp], 0.0070 - 0.0006 * k, "Espinho_Bochecha", 1.3))
def eixo_em(y):
    for a, b in zip(ESPINHA, ESPINHA[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0]); return lerp(a[1], b[1], t), lerp(a[3], b[3], t)
    return ESPINHA[-1][1], ESPINHA[-1][3]
def espinho_dorsal(p, alt, larg, inc, nome):
    """lamina triangular curvada para tras; folga entre espinhos para o pescoco dobrar"""
    m = bpy.data.meshes.new(nome); b = bmesh.new()
    perfil = [(-larg, 0.0), (larg * 0.55, 0.0), (larg * 0.25, alt * 0.55), (-larg * 0.15 + alt * 0.5, alt)]   # (y, z)
    anel = []
    for (yy, zz) in perfil:
        anel.append([b.verts.new((xx, yy, zz)) for xx in (-0.007 * (1 - zz / alt * 0.8), 0.007 * (1 - zz / alt * 0.8))])
    for i in range(len(anel)):
        j = (i + 1) % len(anel)
        b.faces.new((anel[i][0], anel[j][0], anel[j][1], anel[i][1]))
    b.faces.new([a[0] for a in anel][::-1]); b.faces.new([a[1] for a in anel])
    b.to_mesh(m); b.free()
    o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    o.location = p; o.rotation_euler = (inc, 0, 0)
    sd = o.modifiers.new("Sub", "SUBSURF"); sd.levels = sd.render_levels = 2
    for pl in m.polygons: pl.use_smooth = True
    return o
y = -0.69; i = 0
while y < 1.70:
    z, r = eixo_em(y)
    alt = 0.026 + 0.024 * math.exp(-((y + 0.40) / 0.40) ** 2) + 0.010 * math.exp(-((y - 0.30) / 0.4) ** 2)
    alt *= 1 - 0.35 * suave((y - 0.6) / 1.0)
    ESPINHOS.append(espinho_dorsal(V((0, y, z + r * 0.93)), alt, 0.011 + alt * 0.22, -0.20, "Espinho_Dorsal_%02d" % i))
    y += 0.030 + alt * 0.30; i += 1
for s in (1, -1):
    for dian in (True, False):
        for d in dedos_pe(s, dian):
            ponta = d[-1][0]; dirv = (ponta - d[0][0]).normalized()
            pts = [ponta + dirv * 0.004, ponta + dirv * 0.026 + V((0, 0, 0.002)), ponta + dirv * 0.046 + V((0, 0, -0.010)),
                   ponta + dirv * 0.058 + V((0, 0, -0.028))]
            GARRAS.append(tubo(pts, 0.0125, "Garra"))
    raiz, cot, pul, dedos = asa(s)
    for d in dedos[:1]:                                         # garra na ponta do dedo de ataque
        GARRAS.append(tubo([d[2], d[2] + (d[2] - d[1]).normalized() * 0.03 + V((0, 0, -0.012))], 0.006, "Garra_Asa"))
    pol = pul + V((0.03 * s, -0.085, 0.008))
    GARRAS.append(tubo([pol, pol + V((0.008 * s, -0.03, -0.006)), pol + V((0.012 * s, -0.045, -0.022))], 0.0075, "Garra_Polegar"))
for s in (1, -1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0092, location=(OLHO.x * s, OLHO.y, OLHO.z), segments=24, ring_count=12)
    o = bpy.context.object; o.name = "Olho"; o.scale = (0.7, 1.35, 0.72); bpy.ops.object.shade_smooth(); OLHOS.append(o)

# ------------------------------------------------------------------ materiais
def mat(nome):
    m = bpy.data.materials.new(nome)
    if m.node_tree is None: m.use_nodes = True
    nt = m.node_tree; return m, nt, nt.nodes["Principled BSDF"], nt.links
def n(nt, t, **kw):
    x = nt.nodes.new(t)
    for k, v in kw.items(): setattr(x, k, v)
    return x
def rampa(nt, L, ent, pares):
    r = n(nt, "ShaderNodeValToRGB"); L.new(ent, r.inputs[0]); el = r.color_ramp.elements
    el[0].position, el[0].color = pares[0]; el[1].position, el[1].color = pares[-1]
    for pos, cor in pares[1:-1]: e = el.new(pos); e.color = cor
    return r
def mat_corpo():
    m, nt, b, L = mat("M_Dragao_Escamas")
    tc = n(nt, "ShaderNodeTexCoord"); geo = n(nt, "ShaderNodeNewGeometry")
    pos = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], pos.inputs[0])
    nr = n(nt, "ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], nr.inputs[0])
    # escamas SOBREPOSTAS (conceito): maiores no dorso/patas, menores na cabeca/pescoco, alongadas ao longo do
    # corpo; cada escama sobe na borda de tras (+Y) e afunda sob a da frente -> leitura de placas em telhado
    def mr(ent, a, b_, c=0.0, d=1.0):
        x = n(nt, "ShaderNodeMapRange"); x.inputs[1].default_value = a; x.inputs[2].default_value = b_
        x.inputs[3].default_value = c; x.inputs[4].default_value = d; L.new(ent, x.inputs[0]); return x.outputs[0]
    def op(o_, a, b_=None, v=None):
        x = n(nt, "ShaderNodeMath", operation=o_); L.new(a, x.inputs[0])
        if b_ is not None: L.new(b_, x.inputs[1])
        if v is not None: x.inputs[1].default_value = v
        return x.outputs[0]
    corpo_f = mr(pos.outputs["Y"], -0.72, -0.45)                         # 0 cabeca -> 1 corpo
    dors_f = mr(nr.outputs["Z"], 0.0, 0.7)                               # dorso (face para cima) = escamas maiores
    tam = op("SUBTRACT", mr(corpo_f, 0, 1, 250, 165), op("MULTIPLY", dors_f, v=30.0))       # glacial: escamas mais finas
    estica = n(nt, "ShaderNodeVectorMath", operation="MULTIPLY"); estica.inputs[1].default_value = (1.0, 0.72, 1.0)
    L.new(tc.outputs["Object"], estica.inputs[0])
    ve = n(nt, "ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE"); vc = n(nt, "ShaderNodeTexVoronoi")
    for t in (ve, vc): L.new(estica.outputs[0], t.inputs["Vector"]); L.new(tam, t.inputs["Scale"])
    rel = n(nt, "ShaderNodeVectorMath", operation="SUBTRACT"); L.new(estica.outputs[0], rel.inputs[0]); L.new(vc.outputs["Position"], rel.inputs[1])
    relxyz = n(nt, "ShaderNodeSeparateXYZ"); L.new(rel.outputs[0], relxyz.inputs[0])
    tras = mr(op("MULTIPLY", relxyz.outputs["Y"], tam), -0.5, 0.5)       # 0 borda da frente -> 1 borda de tras
    ruido = n(nt, "ShaderNodeTexNoise"); ruido.inputs["Scale"].default_value = 7; L.new(tc.outputs["Object"], ruido.inputs["Vector"])
    # vermelho-alaranjado vivo do conceito (lineares; sRGB ~ 220,60,40 no tom medio)
    verm = rampa(nt, L, ruido.outputs["Fac"], [(0.3, (0.08, 0.26, 0.60, 1)), (0.55, (0.20, 0.46, 0.82, 1)), (0.8, (0.40, 0.66, 0.94, 1))])   # azul-gelo saturado
    tom = n(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); tom.inputs["Factor"].default_value = 0.18
    L.new(verm.outputs["Color"], tom.inputs[6]); L.new(vc.outputs["Color"], tom.inputs[7])
    fr_ = mr(ve.outputs["Distance"], 0.0, 0.12)
    fr = n(nt, "ShaderNodeMath", operation="ADD"); L.new(fr_, fr.inputs[0]); fr.inputs[1].default_value = 0.0   # compat: fr.outputs[0]
    brilho = op("MULTIPLY", op("POWER", fr.outputs[0], v=0.5), tras)     # borda de tras erguida pega luz
    realce = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(op("MULTIPLY", brilho, v=0.55), realce.inputs["Factor"])
    L.new(tom.outputs[2], realce.inputs[6]); realce.inputs[7].default_value = (0.82, 0.92, 1.0, 1)    # borda clara (gelo)
    esc = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(op("POWER", fr.outputs[0], v=0.6), esc.inputs["Factor"])
    esc.inputs[6].default_value = (0.012, 0.03, 0.09, 1); L.new(realce.outputs[2], esc.inputs[7])    # fendas azul-marinho
    ALT_ESC = op("MULTIPLY", op("POWER", fr.outputs[0], v=0.5), op("ADD", op("MULTIPLY", tras, v=0.7), v=0.3))
    # ventre marfim em placas: faixa central de baixo (tronco/cauda) e frente do pescoco/garganta
    ax = n(nt, "ShaderNodeMath", operation="ABSOLUTE"); L.new(nr.outputs["X"], ax.inputs[0])
    lat = n(nt, "ShaderNodeMapRange"); lat.inputs[1].default_value = 0.62; lat.inputs[2].default_value = 0.45; L.new(ax.outputs[0], lat.inputs[0])
    baixo = n(nt, "ShaderNodeMapRange"); baixo.inputs[1].default_value = -0.15; baixo.inputs[2].default_value = -0.40; L.new(nr.outputs["Z"], baixo.inputs[0])
    frente = n(nt, "ShaderNodeMapRange"); frente.inputs[1].default_value = -0.25; frente.inputs[2].default_value = -0.55; L.new(nr.outputs["Y"], frente.inputs[0])
    pesc = n(nt, "ShaderNodeMapRange"); pesc.inputs[1].default_value = -0.30; pesc.inputs[2].default_value = -0.42; L.new(pos.outputs["Y"], pesc.inputs[0])
    cab = n(nt, "ShaderNodeMapRange"); cab.inputs[1].default_value = -0.74; cab.inputs[2].default_value = -0.68; L.new(pos.outputs["Y"], cab.inputs[0])
    garg0 = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(frente.outputs[0], garg0.inputs[0]); L.new(pesc.outputs[0], garg0.inputs[1])
    garg = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(garg0.outputs[0], garg.inputs[0]); L.new(cab.outputs[0], garg.inputs[1])
    zb = n(nt, "ShaderNodeMath", operation="MAXIMUM"); L.new(baixo.outputs[0], zb.inputs[0]); L.new(garg.outputs[0], zb.inputs[1])
    nas_asas = n(nt, "ShaderNodeMapRange"); nas_asas.inputs[1].default_value = 0.095; nas_asas.inputs[2].default_value = 0.07
    axp = n(nt, "ShaderNodeMath", operation="ABSOLUTE"); L.new(pos.outputs["X"], axp.inputs[0]); L.new(axp.outputs[0], nas_asas.inputs[0])
    pernas = n(nt, "ShaderNodeMapRange"); pernas.inputs[1].default_value = 0.30; pernas.inputs[2].default_value = 0.36
    L.new(pos.outputs["Z"], pernas.inputs[0])                       # nao pinta a parte de baixo das patas
    vz0 = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(zb.outputs[0], vz0.inputs[0]); L.new(lat.outputs[0], vz0.inputs[1])
    vz1 = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(vz0.outputs[0], vz1.inputs[0]); L.new(nas_asas.outputs[0], vz1.inputs[1])
    ventre = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(vz1.outputs[0], ventre.inputs[0]); L.new(pernas.outputs[0], ventre.inputs[1])
    # placas transversais: ao longo do tronco seguem Y; no pescoco seguem o eixo inclinado do pescoco
    eix = n(nt, "ShaderNodeVectorMath", operation="DOT_PRODUCT"); eix.inputs[1].default_value = (0, 0.62, -0.78)
    L.new(tc.outputs["Object"], eix.inputs[0])
    sel = n(nt, "ShaderNodeMix", data_type="FLOAT"); L.new(pesc.outputs[0], sel.inputs["Factor"])
    L.new(pos.outputs["Y"], sel.inputs[2]); L.new(eix.outputs["Value"], sel.inputs[3])
    onda = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(sel.outputs[0], onda.inputs[0]); onda.inputs[1].default_value = 2 * math.pi * 26
    sen = n(nt, "ShaderNodeMath", operation="SINE"); L.new(onda.outputs[0], sen.inputs[0])
    sulco = n(nt, "ShaderNodeMapRange"); sulco.inputs[1].default_value = -1.0; sulco.inputs[2].default_value = -0.82
    L.new(sen.outputs[0], sulco.inputs[0])
    marfim = rampa(nt, L, ruido.outputs["Fac"], [(0.3, (0.62, 0.76, 0.90, 1)), (0.7, (0.84, 0.93, 1.0, 1))])   # placas quase brancas
    placa = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(sulco.outputs[0], placa.inputs["Factor"])
    placa.inputs[6].default_value = (0.20, 0.34, 0.52, 1); L.new(marfim.outputs["Color"], placa.inputs[7])
    cor = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(ventre.outputs[0], cor.inputs["Factor"])
    L.new(esc.outputs[2], cor.inputs[6]); L.new(placa.outputs[2], cor.inputs[7])
    # dedos da asa mais claros (pessego)
    ded = n(nt, "ShaderNodeMapRange"); ded.inputs[1].default_value = 0.55; ded.inputs[2].default_value = 0.85; L.new(axp.outputs[0], ded.inputs[0])
    cor2 = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(ded.outputs[0], cor2.inputs["Factor"])
    L.new(cor.outputs[2], cor2.inputs[6]); cor2.inputs[7].default_value = (0.70, 0.84, 0.96, 1)   # dedos da asa claros
    L.new(cor2.outputs[2], b.inputs["Base Color"])
    rg = n(nt, "ShaderNodeMapRange"); rg.inputs[3].default_value = 0.75; rg.inputs[4].default_value = 0.52; L.new(fr.outputs[0], rg.inputs[0])
    L.new(rg.outputs[0], b.inputs["Roughness"])
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.25          # brilho frio de gelo
    # relevo: escamas (fora do ventre) + sulcos das placas (no ventre)
    alt_esc = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(fr.outputs[0], alt_esc.inputs[0])
    inv = n(nt, "ShaderNodeMath", operation="SUBTRACT"); inv.inputs[0].default_value = 1.0; L.new(ventre.outputs[0], inv.inputs[1])
    L.new(inv.outputs[0], alt_esc.inputs[1])
    alt_pl = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(sulco.outputs[0], alt_pl.inputs[0]); L.new(ventre.outputs[0], alt_pl.inputs[1])
    alt_esc2 = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(ALT_ESC, alt_esc2.inputs[0]); L.new(inv.outputs[0], alt_esc2.inputs[1])
    alt = n(nt, "ShaderNodeMath", operation="ADD"); L.new(alt_esc2.outputs[0], alt.inputs[0]); L.new(alt_pl.outputs[0], alt.inputs[1])
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.85; bp.inputs["Distance"].default_value = 0.004
    L.new(alt.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m
def mat_membrana():
    m, nt, b, L = mat("M_Dragao_Membrana")
    tc = n(nt, "ShaderNodeTexCoord")
    veia = n(nt, "ShaderNodeTexNoise"); veia.inputs["Scale"].default_value = 18; veia.inputs["Detail"].default_value = 3
    veia.inputs["Distortion"].default_value = 1.2; L.new(tc.outputs["Object"], veia.inputs["Vector"])
    vr = rampa(nt, L, veia.outputs["Fac"], [(0.35, (0.36, 0.56, 0.80, 1)), (0.65, (0.62, 0.80, 0.96, 1))])
    L.new(vr.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.5
    tr = n(nt, "ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = (0.55, 0.80, 1.0, 1)
    mx = n(nt, "ShaderNodeMixShader"); mx.inputs[0].default_value = 0.42                  # membrana translucida azul
    out = nt.nodes["Material Output"]; L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs[0])
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.3; L.new(veia.outputs["Fac"], bp.inputs["Height"])
    L.new(bp.outputs[0], b.inputs["Normal"]); return m
def mat_marfim(nome, base, ponta, rug, comp):
    m, nt, b, L = mat(nome)
    tc = n(nt, "ShaderNodeTexCoord")
    # gradiente base -> ponta pela distancia ate a origem do objeto (a base da peca)
    dist = n(nt, "ShaderNodeVectorMath", operation="LENGTH"); L.new(tc.outputs["Object"], dist.inputs[0])
    mx_ = n(nt, "ShaderNodeMapRange"); mx_.inputs[2].default_value = comp; L.new(dist.outputs["Value"], mx_.inputs[0])
    an = n(nt, "ShaderNodeTexWave"); an.inputs["Scale"].default_value = 30; an.inputs["Distortion"].default_value = 2
    L.new(tc.outputs["Object"], an.inputs["Vector"])
    gr = rampa(nt, L, mx_.outputs[0], [(0.0, base), (1.0, ponta)])
    L.new(gr.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rug
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25; L.new(an.outputs["Fac"], bp.inputs["Height"])
    L.new(bp.outputs[0], b.inputs["Normal"]); return m
def mat_espinho():
    m, nt, b, L = mat("M_Dragao_Espinho")
    tc = n(nt, "ShaderNodeTexCoord"); sep = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sep.inputs[0])
    gr = rampa(nt, L, sep.outputs["Z"], [(0.0, (0.22, 0.40, 0.64, 1)), (0.6, (0.52, 0.72, 0.92, 1)), (1.0, (0.86, 0.95, 1.0, 1))])
    L.new(gr.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.22
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.5             # cristal de gelo
    return m
def mat_olho():
    m, nt, b, L = mat("M_Dragao_Olho")
    tc = n(nt, "ShaderNodeTexCoord"); sep = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sep.inputs[0])
    d = n(nt, "ShaderNodeMath", operation="ABSOLUTE"); sub_ = n(nt, "ShaderNodeMath", operation="SUBTRACT")
    L.new(sep.outputs["Y"], sub_.inputs[0]); sub_.inputs[1].default_value = 0.5; L.new(sub_.outputs[0], d.inputs[0])
    pup = n(nt, "ShaderNodeMapRange"); pup.inputs[1].default_value = 0.05; pup.inputs[2].default_value = 0.09; L.new(d.outputs[0], pup.inputs[0])
    cor = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(pup.outputs[0], cor.inputs["Factor"])
    cor.inputs[6].default_value = (0.005, 0.01, 0.03, 1); cor.inputs[7].default_value = (0.40, 0.80, 1.0, 1)
    L.new(cor.outputs[2], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.05
    b.inputs["Emission Color"].default_value = (0.35, 0.75, 1.0, 1)
    em = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(pup.outputs[0], em.inputs[0]); em.inputs[1].default_value = 0.35
    L.new(em.outputs[0], b.inputs["Emission Strength"])
    return m
MC, MM, ME, MO = mat_corpo(), mat_membrana(), mat_espinho(), mat_olho()
MH = mat_marfim("M_Dragao_Chifre", (0.26, 0.44, 0.66, 1), (0.88, 0.95, 1.0, 1), 0.30, 0.22)   # chifre azul -> ponta branca de gelo
MG = mat_marfim("M_Dragao_Garra", (0.40, 0.52, 0.66, 1), (0.88, 0.94, 1.0, 1), 0.30, 0.06)
ob.data.materials.append(MC)
for o in MEMB: o.data.materials.append(MM)
for o in CHIFRES: o.data.materials.append(MH)
for yy, zz, a in ((-0.868, 0.776, 0.010), (-0.83, 0.792, 0.014)):                          # crista do focinho
    ESPINHOS.append(espinho_dorsal(V((0, yy, zz)), a, 0.010, -0.35, "Espinho_Focinho"))
for s in (1, -1):                                                                          # pontas da sobrancelha
    for k in range(2):
        b0 = V((0.046 * s, -0.800 + 0.022 * k, 0.792 - 0.004 * k))
        ESPINHOS.append(tubo([b0, b0 + V((0.012 * s, 0.022, 0.012)), b0 + V((0.020 * s, 0.040, 0.016))], 0.0065, "Espinho_Sobrancelha"))
for o in CHIFRES + OLHOS + [e for e in ESPINHOS if e.name.split(".")[0] in ("Espinho_Bochecha", "Espinho_Focinho", "Espinho_Sobrancelha")]:
    para_cabeca(o)
for e in ESPINHOS:
    if e.name.startswith("Espinho_Dorsal"): e.location = cabeca(e.location)
CENTRO_CAB = cabeca(V((0, -0.80, 0.745)), 1.0)
def encaixar(o, dirv, fundo):
    """leva a base (origem) da peca ate a pele ao longo de dirv e afunda um pouco para dentro"""
    dirv = dirv.normalized(); ini = o.location - dirv * 0.25
    ok, hit, nrm, _ = ob.ray_cast(ini, dirv, distance=0.6)
    if ok: o.location = hit + dirv * fundo
    return ok
falhas = 0
for o in CHIFRES + [e for e in ESPINHOS if not e.name.startswith("Espinho_Dorsal")]:
    falhas += not encaixar(o, CENTRO_CAB - o.location, 0.010 if o in CHIFRES else 0.005)
for e in ESPINHOS:
    if e.name.startswith("Espinho_Dorsal") or e.name.startswith("Espinho_Focinho"):
        falhas += not encaixar(e, V((0, 0, -1)), 0.004)
print("DRAGAO_ENCAIXE falhas", falhas)
for o in ESPINHOS: o.data.materials.append(ME)
for o in GARRAS: o.data.materials.append(MG)
for o in OLHOS: o.data.materials.append(MO)
col = bpy.data.collections.new("GL_Dragao"); sc.collection.children.link(col)
for o in [ob] + MEMB + CHIFRES + ESPINHOS + GARRAS + OLHOS:
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o)
dg = bpy.context.evaluated_depsgraph_get()
print("DRAGAO_POLIGONOS", sum(len(o.evaluated_get(dg).data.polygons) for o in col.objects if o.type == "MESH"), "corpo", len(ob.data.polygons))

# ------------------------------------------------------------------ cena de revisao
w = bpy.data.worlds.new("Ceu"); sc.world = w
if w.node_tree is None: w.use_nodes = True
bg = w.node_tree.nodes["Background"]; ceu = w.node_tree.nodes.new("ShaderNodeTexSky")
for t in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA", "HOSEK_WILKIE"):
    try: ceu.sky_type = t; break
    except Exception: pass
if hasattr(ceu, "sun_elevation"): ceu.sun_elevation = math.radians(30)
w.node_tree.links.new(ceu.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.10   # ceu fraco: nao tinge de azul
for nome, en, cor, rot in (("Sol", 4.0, (1.0, 0.97, 0.94), (math.radians(50), 0, math.radians(30))),
                           ("Contra", 3.0, (0.85, 0.92, 1.0), (math.radians(115), 0, math.radians(200))),
                           ("Preench", 1.2, (0.88, 0.94, 1.0), (math.radians(60), 0, math.radians(-120)))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.color = cor; lo = bpy.data.objects.new(nome, l)
    sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=40); chao = bpy.context.object
mch, _, bch, _ = mat("Chao"); bch.inputs["Base Color"].default_value = (0.24, 0.25, 0.27, 1); bch.inputs["Roughness"].default_value = 0.95
chao.data.materials.append(mch)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 64
for k, v in (("use_raytracing", True), ("use_shadows", True)):
    if hasattr(sc.eevee, k): setattr(sc.eevee, k, v)
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
camd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", camd); sc.collection.objects.link(cam); sc.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "GL_Dragao_master.blend"))
if "sem_render" not in ARGS:
    VISTAS = [("34_frente", V((-2.4, -3.6, 1.3)), V((0, -0.15, 0.5)), 42), ("lado", V((-5.6, 0.25, 0.75)), V((0, 0.25, 0.5)), 42),
              ("frente", V((0, -5.2, 1.0)), V((0, 0, 0.6)), 42), ("34_tras", V((2.9, 3.4, 2.0)), V((0, 0.1, 0.55)), 42),
              ("cima", V((0.01, 0.3, 6.2)), V((0, 0.3, 0.4)), 42), ("cabeca", V((-0.85, -1.75, 1.02)), V((0, -0.82, 0.77)), 62),
              ("conceito", V((-1.6, -2.3, 0.62)), V((0, -0.2, 0.62)), 35)]
    for nome, pos, alvo, lente in VISTAS:
        cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
        sc.render.filepath = os.path.join(OUT, "vista_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("DRAGAO_OK")
