"""CR_Crocodilo_Ref: Crocodilo Primordial adulto fiel a ref/referencia.png (ver asset-brief.md), POSE NEUTRA (boca fechada,
patas retas, cauda reta). 1 unidade = 1 stud. Frente = -Y, pes em Z=0, simetrico em X.
Corpo = grafo Skin -> subsurf -> remesh voxel -> esculpido por deslocamento; boca cortada por boolean (fenda dos labios +
cavidade + garganta). Pecas rigidas (dentes, gengivas, lingua, olhos, cristas, garras) unidas por tipo.
Uso: blender -b --factory-startup -P criar_crocodilo.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, noise

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; rnd = random.Random(7); V = Vector
def lerp(a, b, t): return a + (b - a) * t
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def interp(tab, y):
    """tabela [(y, v...)] -> valores interpolados em y"""
    if y <= tab[0][0]: return tab[0][1:]
    for a, b in zip(tab, tab[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0]); return tuple(lerp(p, q, t) for p, q in zip(a[1:], b[1:]))
    return tab[-1][1:]

# ------------------------------------------------------------------ perfil (y, topo, base, meia-largura)
# referencia: cabeca grande e plana, pescoco curto e grosso, tronco fundo com barriga baixa, cauda longa achatada
PERFIL = [(-13.55, 4.95, 4.05, 0.50), (-13.30, 5.30, 3.85, 1.05), (-12.90, 5.36, 3.80, 1.16), (-12.40, 5.28, 3.80, 1.10),
          (-11.70, 5.48, 3.72, 1.26), (-10.80, 5.78, 3.62, 1.48), (-9.90, 6.15, 3.52, 1.74), (-9.10, 6.55, 3.45, 1.95),
          (-8.40, 6.70, 3.38, 2.15), (-7.50, 6.60, 3.20, 2.30), (-6.30, 6.60, 2.85, 2.55),                          # cabeca, nuca
          (-4.80, 6.62, 2.15, 2.95), (-3.00, 6.62, 1.50, 3.36), (-1.00, 6.55, 1.22, 3.52), (1.00, 6.40, 1.52, 3.30),
          (2.60, 6.20, 2.20, 2.62),                                                                                # tronco
          (4.20, 5.85, 2.60, 2.10), (6.00, 5.40, 2.90, 1.58), (8.00, 4.92, 3.08, 1.12), (10.00, 4.42, 3.00, 0.80),
          (12.00, 3.92, 2.86, 0.52), (13.80, 3.46, 2.72, 0.30), (15.40, 3.08, 2.62, 0.07)]                          # cauda
I_NARIZ, I_OLHO, I_NUCA, I_OMBRO, I_MEIO, I_QUADRIL = 1, 7, 8, 11, 13, 15
Y_CANTO, Z_CANTO = -8.35, 4.85                     # canto da boca = dobradica da mandibula (rig)
LABIO = [(-13.9, 4.55), (-13.0, 4.45), (-12.4, 4.55), (-11.3, 4.40), (-10.0, 4.45), (-9.0, 4.62), (Y_CANTO, Z_CANTO)]
def labio(y): return interp(LABIO, y)[0]
def fenda(y): return max(0.010, 0.035 * suave((Y_CANTO - y) / 1.3))          # altura da fenda dos labios (fechada)
def meia_larg(y): return interp(PERFIL, y)[2]

def perna(s, dianteira):
    """high walk da referencia: umero/femur curtos para fora e para baixo, cotovelo/joelho laterais, antebraco/canela
    grossos e quase verticais; maos e pes largos apontando para frente e um pouco para fora. (ponto, raio)"""
    if dianteira:
        return [(V((1.40 * s, -4.75, 3.80)), 1.50), (V((2.65 * s, -4.60, 2.85)), 1.42), (V((3.45 * s, -4.42, 2.00)), 1.22),
                (V((3.62 * s, -4.62, 1.35)), 1.05), (V((3.68 * s, -4.85, 0.95)), 0.86)]
    return [(V((1.40 * s, 2.50, 3.90)), 1.85), (V((2.65 * s, 2.25, 3.05)), 1.72), (V((3.45 * s, 1.90, 2.10)), 1.36),
            (V((3.66 * s, 2.40, 1.35)), 1.12), (V((3.72 * s, 2.75, 0.98)), 0.90)]
def mao(s, dianteira):
    """palma achatada: (centro, meia-largura, meia-altura, comprimento para frente)"""
    p = perna(s, dianteira)[-1][0]
    return (p + V((0.08 * s, -0.45, -0.55)), 0.95 if dianteira else 1.00, 0.40, 1.05 if dianteira else 1.25)
def dedos(s, dianteira):
    """5 dedos na mao, 4 no pe (crocodilo real); leque para frente/fora. [(ponto, raio)]"""
    c, lw, lh, lc = mao(s, dianteira)
    angs = (-42, -18, 4, 26, 50) if dianteira else (-30, -8, 14, 38)
    comp = (0.72, 0.95, 1.02, 0.92, 0.70) if dianteira else (1.00, 1.25, 1.25, 1.00)
    out = []
    for i, (a, L) in enumerate(zip(angs, comp)):
        d = V((math.sin(math.radians(a)) * s, -math.cos(math.radians(a)), 0))
        b0 = c + d * lc * 0.45 + V((0, 0, -0.10))
        out.append([(b0, 0.32), (b0 + d * L * 0.5 + V((0, 0, -0.10)), 0.26), (b0 + d * L + V((0, 0, -0.17)), 0.19)])
    return out

# ------------------------------------------------------------------ corpo: secoes elipticas continuas (loft) unidas por voxel
def catmull(pts, n):
    """reamostra uma lista de valores (tuplas) por Catmull-Rom"""
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    out.append(tuple(pts[-1])); return out
def loft(secoes, nome, lados=48, expo=2.4):
    """secoes [(centro V, eixo_x V, eixo_z V, rx, rz)] -> tubo fechado; superelipse (expo>2 = mais 'quadrado' e cheio)"""
    b = bmesh.new(); aneis = []
    for c, ex, ez, rx, rz in secoes:
        anel = []
        for k in range(lados):
            a = 2 * math.pi * k / lados; ca, sa = math.cos(a), math.sin(a)
            u = math.copysign(abs(ca) ** (2 / expo), ca); w = math.copysign(abs(sa) ** (2 / expo), sa)
            anel.append(b.verts.new(c + ex * (u * rx) + ez * (w * rz)))
        aneis.append(anel)
    for a, c in zip(aneis, aneis[1:]):
        for k in range(lados): b.faces.new((a[k], a[(k + 1) % lados], c[(k + 1) % lados], c[k]))
    b.faces.new(aneis[0][::-1]); b.faces.new(aneis[-1])
    m = bpy.data.meshes.new(nome); b.to_mesh(m); b.free(); return m
def loft_caminho(pts_r, nome, achatar=1.0, n=6, expo=2.2):
    """membro: pontos (p, r) suavizados; quadro por transporte paralelo; achatar < 1 = mais baixo que largo"""
    am = catmull([(p.x, p.y, p.z, r) for p, r in pts_r], n)
    ps = [V(a[:3]) for a in am]; rs = [a[3] for a in am]
    secoes = []; ref = V((0, 0, 1))
    for i, p in enumerate(ps):
        t = (ps[min(i + 1, len(ps) - 1)] - ps[max(i - 1, 0)]).normalized()
        ex = t.cross(ref); ex = ex.normalized() if ex.length > 1e-4 else t.orthogonal().normalized()
        ez = ex.cross(t).normalized()
        secoes.append((p, ex, ez, rs[i], rs[i] * achatar))
    return loft(secoes, nome, 24, expo)
def loft_mao(pts, nome, n=5):
    """punho -> palma continuo: pontos (p, rx, rz); rz no plano vertical que contem a tangente"""
    am = catmull([(p.x, p.y, p.z, a, b_) for p, a, b_ in pts], n)
    secoes = []
    for i, a in enumerate(am):
        p = V(a[:3])
        t = (V(am[min(i + 1, len(am) - 1)][:3]) - V(am[max(i - 1, 0)][:3])).normalized()
        ez = V((0, 0, 1)) - t * t.z
        if ez.length < 0.25: ez = V((0, -1, 0)) - t * (-t.y)
        ez.normalize(); ex = t.cross(ez).normalized()
        secoes.append((p, ex, ez, a[3], a[4]))
    return loft(secoes, nome, 28, 2.3)
PECAS = []
am = catmull([(y, t, b, w) for y, t, b, w in PERFIL], 8)
secs = [(V((0, y, (t + b) / 2)), V((1, 0, 0)), V((0, 0, 1)), max(w, 0.02), max((t - b) / 2, 0.02)) for y, t, b, w in am]
PECAS.append(loft(secs, "Tronco", 64, 2.5))
for s in (1, -1):
    for dian in (True, False):
        PECAS.append(loft_caminho(perna(s, dian), "Perna", 1.0))
        c, lw, lh, lc = mao(s, dian)
        pf, rf = perna(s, dian)[-2]; pu, ru_ = perna(s, dian)[-1]
        PECAS.append(loft_mao([(pf, rf, rf), (pu, ru_, ru_), (c + V((0, 0.42 * lc, 0.22)), lw * 0.92, lh * 1.25),
                               (c + V((0, 0.05 * lc, 0.02)), lw, lh), (c + V((0, -0.40 * lc, -0.04)), lw * 0.88, lh * 0.80)], "Mao"))
        for d in dedos(s, dian): PECAS.append(loft_caminho(d, "Dedo", 0.78, 4))
def elipsoide_m(c, r, nome="Massa"):
    b = bmesh.new(); bmesh.ops.create_uvsphere(b, u_segments=32, v_segments=16, radius=1.0)
    for v in b.verts: v.co = c + V((v.co.x * r[0], v.co.y * r[1], v.co.z * r[2]))
    m = bpy.data.meshes.new(nome); b.to_mesh(m); b.free(); return m
for s in (1, -1):
    PECAS.append(elipsoide_m(V((1.05 * s, -9.45, 6.00)), (0.46, 0.58, 0.34)))           # orbita elevada
    PECAS.append(elipsoide_m(V((1.55 * s, -8.45, 4.80)), (0.75, 1.05, 0.95)))           # musculo da mandibula
    PECAS.append(elipsoide_m(V((2.05 * s, -4.65, 3.55)), (1.45, 1.55, 1.40)))           # ombro (transicao pata-corpo)
    PECAS.append(elipsoide_m(V((2.05 * s, 2.40, 3.55)), (1.65, 1.85, 1.60)))            # quadril/coxa
PECAS.append(elipsoide_m(V((0, -13.15, 5.22)), (0.62, 0.48, 0.32)))                     # cupula das narinas
b = bmesh.new()
for mm in PECAS: b.from_mesh(mm); bpy.data.meshes.remove(mm)
me = bpy.data.meshes.new("CR_Croc_Corpo"); b.to_mesh(me); b.free()
ob = bpy.data.objects.new("CR_Croc_Corpo", me); sc.collection.objects.link(ob)
bpy.context.view_layer.objects.active = ob; ob.select_set(True)
rm = ob.modifiers.new("Remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.05; rm.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=rm.name)
# suaviza as emendas (pata-corpo, dedos, orbitas) sem amolecer a silhueta inteira
JUNTAS = []
for s in (1, -1):
    for dian in (True, False):
        pl = perna(s, dian); JUNTAS += [(pl[0][0] + V((0.5 * s, 0, -0.3)), 1.9), (pl[2][0], 0.9), (mao(s, dian)[0] + V((0, -0.3, -0.05)), 0.9)]
    JUNTAS += [(V((1.05 * s, -9.45, 6.0)), 0.9), (V((1.55 * s, -8.45, 4.8)), 1.2)]
JUNTAS.append((V((0, -13.15, 5.22)), 0.7))
vg = ob.vertex_groups.new(name="Juntas")
for v in me.vertices:
    w_ = max(max(0.0, 1 - (v.co - c).length / r) for c, r in JUNTAS)
    if w_ > 0: vg.add([v.index], min(1.0, w_ * 1.6), "REPLACE")
sm = ob.modifiers.new("LisoJuntas", "SMOOTH"); sm.factor = 0.8; sm.iterations = 18; sm.vertex_group = "Juntas"
sm2 = ob.modifiers.new("Liso", "SMOOTH"); sm2.factor = 0.4; sm2.iterations = 3
for m in list(ob.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
ob.vertex_groups.clear()

# mandibula inferior mais estreita que o focinho (sobremordida: dentes de cima por fora)
for v in ob.data.vertices:
    p = v.co
    if p.y < -7.6 and p.z < labio(min(p.y, Y_CANTO)) + 0.05:
        w = suave((-7.6 - p.y) / 0.9) * suave((labio(min(p.y, Y_CANTO)) + 0.05 - p.z) / 0.25)
        p.x *= 1 - 0.13 * w
ob.data.update()

# olhos: raio ate a orbita
ok_, hit, nrm_h, _ = ob.ray_cast(V((1.30, -9.50, 9.0)), V((0, 0, -1)))
OLHO = hit - nrm_h * 0.07 if ok_ else None
print("CROC_OLHO", ok_, tuple(round(c, 3) for c in OLHO) if ok_ else None, "normal", tuple(round(c, 2) for c in nrm_h) if ok_ else None)
NARINAS = [V((0.24 * s, -13.30, 5.55)) for s in (1, -1)]
for v in ob.data.vertices:                                     # rosto: orbitas, arcada, narinas, sulcos
    p, nrm = v.co, v.normal
    for s_ in (1, -1):
        c = V((OLHO.x * s_, OLHO.y, OLHO.z)); d = (p - c).length
        if d < 0.42: p -= nrm * 0.12 * (1 - d / 0.42) ** 2                                   # cavidade do olho
        dz = p.z - (OLHO.z + 0.22); dy = p.y - OLHO.y
        if abs(p.x - c.x) < 0.5 and abs(dy) < 0.55 and 0 < dz < 0.35 and p.x * s_ > 0:          # arcada ossea marcada
            p += nrm * 0.06 * (1 - abs(dy) / 0.55) * (1 - dz / 0.35)
    for na in NARINAS:
        ok2, hn, nn, _ = ob.ray_cast(na + V((0, 0, 0.6)), V((0, 0, -1)))
        if ok2:
            d = (p - hn).length
            if d < 0.13: p -= nrm * 0.10 * (1 - d / 0.13) ** 1.5
ob.data.update()

# ------------------------------------------------------------------ boca: fenda dos labios + cavidade + garganta
def cortador_fenda():
    ys = [-14.6 + (Y_CANTO + 0.02 + 14.6) * i / 80 for i in range(81)]; xs = [-3.5, 3.5]
    vs, fs = [], []
    for y in ys:
        g = fenda(min(y, Y_CANTO)); z = labio(min(max(y, -14.4), Y_CANTO))
        for x in xs: vs.append((x, y, z + g / 2))
        for x in xs: vs.append((x, y, z - g / 2))
    n = len(ys)
    for i in range(n - 1):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, a + 1, b + 1, b), (a + 2, b + 2, b + 3, a + 3), (a, b, b + 2, a + 2), (a + 1, a + 3, b + 3, b + 1)]
    fs += [(0, 2, 3, 1), (4 * (n - 1), 4 * (n - 1) + 1, 4 * (n - 1) + 3, 4 * (n - 1) + 2)]
    m = bpy.data.meshes.new("Corte_Fenda"); m.from_pydata(vs, [], fs); m.update()
    o = bpy.data.objects.new("Corte_Fenda", m); sc.collection.objects.link(o); return o
def elipsoide(nome, c, r):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1, location=c)
    o = bpy.context.object; o.name = nome; o.scale = r; bpy.ops.object.transform_apply(scale=True); return o
CAV = [(V((0, -11.75, labio(-11.75) - 0.10)), (0.58, 1.40, 0.24)),       # cavidade do focinho (assoalho fundo, palato abobadado)
       (V((0, -9.9, labio(-9.9) - 0.10)), (1.00, 1.70, 0.30)),         # cavidade maior
       (V((0, -8.35, Z_CANTO - 0.12)), (0.75, 0.85, 0.32))]            # garganta
cortes = [cortador_fenda()] + [elipsoide("Corte_Cav", c, r) for c, r in CAV]
for c in cortes:
    bo = ob.modifiers.new("Boca", "BOOLEAN"); bo.operation = "DIFFERENCE"; bo.object = c
    try: bo.solver = "EXACT"
    except Exception: pass
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier=bo.name)
for c in cortes: bpy.data.objects.remove(c, do_unlink=True)
def na_cavidade(p, folga):
    for c, r in CAV:
        q = p - c
        if (q.x / (r[0] + folga)) ** 2 + (q.y / (r[1] + folga)) ** 2 + (q.z / (r[2] + folga)) ** 2 < 1: return True
    return False
# indice de material: 0 pele, 1 boca (palato/assoalho), 2 garganta
ob.data.materials.clear()
N_BOCA = N_GARG = 0
for f in ob.data.polygons:
    c = f.center
    if c.y > Y_CANTO + 1.3: continue
    dentro = na_cavidade(c, 0.03)
    if c.y < Y_CANTO + 0.05 and abs(c.z - labio(c.y)) < fenda(c.y) / 2 + 0.035 and abs(f.normal.z) > 0.5: dentro = True
    if dentro:
        f.material_index = 2 if (c - CAV[2][0]).length < 0.75 else 1
        N_BOCA += 1
print("CROC_BOCA faces", N_BOCA)

# ------------------------------------------------------------------ pecas rigidas
def tubo(pts, raios_, nome, lados=8):
    """cone/tubo por aneis: pts com raio por ponto; ponta fechada"""
    b = bmesh.new(); aneis = []; lp = b.verts.layers.float.new("ponta"); npt = len(pts)
    for i, (p, r) in enumerate(zip(pts, raios_)):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        u = t.orthogonal().normalized(); w = t.cross(u)
        if r <= 1e-4: aneis.append([b.verts.new(p)]); continue
        aneis.append([b.verts.new(p + (u * math.cos(2 * math.pi * k / lados) + w * math.sin(2 * math.pi * k / lados)) * r) for k in range(lados)])
    for i, a in enumerate(aneis):
        for v in a: v[lp] = i / (npt - 1)
    for a, c in zip(aneis, aneis[1:]):
        if len(c) == 1:
            for k in range(lados): b.faces.new((a[k], a[(k + 1) % lados], c[0]))
        else:
            for k in range(lados): b.faces.new((a[k], a[(k + 1) % lados], c[(k + 1) % lados], c[k]))
    b.faces.new(aneis[0][::-1])
    m = bpy.data.meshes.new(nome); b.to_mesh(m); b.free()
    for pl in m.polygons: pl.use_smooth = True
    return m

def raio_pele(origem, direcao, dist=6.0):
    ok, h, n, _ = ob.ray_cast(origem, direcao.normalized(), distance=dist)
    return (h, n) if ok else (None, None)

# dentes conicos de tamanhos variados, levemente curvos para tras; gengiva continua ao longo de cada fileira
DENTES, GENG = [], []
def borda_labio(y, de_cima, s):
    """x externo do labio logo acima (focinho) / abaixo (mandibula) da fenda"""
    z = labio(y) + (fenda(y) / 2 + 0.05) * (1 if de_cima else -1)
    h, n = raio_pele(V((4.0 * s, y, z)), V((-s, 0, 0)), 4.0)
    return (abs(h.x) if h else meia_larg(y) * 0.8), z
def espessura_oposta(y, de_cima):
    """espessura da arcada oposta acima/abaixo da fenda (perfil antes da escala da cabeca)"""
    t, b_, w = interp(PERFIL, y)
    return (labio(y) - b_) if de_cima else (t - labio(y))
def fileira(de_cima, s, ys, comps):
    pts_g = []
    for y, L in zip(ys, comps):
        L = min(L, espessura_oposta(y, de_cima) * (0.55 if de_cima else 0.45))
        xe, _ = borda_labio(y, de_cima, s)
        zc = labio(y) + (fenda(y) / 2) * (1 if de_cima else -1)
        raiz = V(((xe - 0.16) * s, y, zc))
        pts_g.append(raiz)
        sent = -1 if de_cima else 1
        d0 = V((0.20 * s, 0.10, sent)).normalized()
        r0 = 0.07 + 0.11 * L
        pts = [raiz - d0 * 0.12]
        for k in range(1, 6):
            t = k / 5
            pts.append(raiz + d0 * (L * t) + V((0, 0.10 * L * t * t, 0)))          # curva para tras
        rs = [r0 * 1.05] + [r0 * (1 - (k / 5) ** 1.3) + 0.004 for k in range(1, 5)] + [0.0]
        DENTES.append(tubo(pts, rs, "Dente", 8))
    # gengiva: tubo baixo e liso ao longo das raizes, meio enterrado na superficie cortada
    for a, b_ in zip(pts_g, pts_g[1:]): pass
    rg = [0.085] * len(pts_g); rg[0] = rg[-1] = 0.05
    GENG.append(tubo(pts_g, rg, "Gengiva", 10))
def tamanhos(n, grandes, base, jit):
    return [base * (1 + jit * (rnd.random() * 2 - 1)) * grandes.get(i, 1.0) for i in range(n)]
for s in (1, -1):
    ys_c = [-13.42 + (Y_CANTO + 0.75 + 13.42) * (i / 14) ** 1.05 for i in range(15)]
    fileira(True, s, ys_c, tamanhos(15, {0: 1.3, 3: 1.9, 4: 1.6, 8: 1.5, 9: 1.35, 13: 0.75, 14: 0.6}, 0.40, 0.18))
    ys_b = [-13.36 + (Y_CANTO + 0.85 + 13.36) * (i / 12) ** 1.05 for i in range(13)]
    fileira(False, s, ys_b, tamanhos(13, {0: 1.5, 3: 2.0, 4: 1.3, 10: 1.3, 11: 0.8, 12: 0.65}, 0.36, 0.18))

# lingua: larga e baixa no fundo da cavidade (sem tocar o palato com a boca fechada)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=(0, -10.3, CAV[1][0].z - CAV[1][1][2] + 0.10))
LINGUA = bpy.context.object; LINGUA.name = "CR_Croc_Lingua"; LINGUA.scale = (0.70, 1.75, 0.13)
bpy.ops.object.transform_apply(scale=True); bpy.ops.object.shade_smooth()

# olhos amarelo-dourados, pequenos, pupila vertical (material); bola meio enterrada na orbita
OLHOS = []
for s in (1, -1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(OLHO.x * s, OLHO.y, OLHO.z), segments=24, ring_count=12)
    o = bpy.context.object; o.name = "CR_Croc_Olho"; o.scale = (0.9, 1.15, 0.85); o.rotation_euler = (0, 0, 0)
    bpy.ops.object.shade_smooth(); OLHOS.append(o)

# cristas/osteodermos triangulares em fileiras (dorso: 2 centrais + 2 laterais + escudos menores; cauda: dupla -> simples)
def crista(alt, larg, comp, inclina):
    """piramide de 4 lados com quilha, curvada para tras; base (origem) em z=0"""
    b = bmesh.new(); lp = b.verts.layers.float.new("ponta")
    base = [b.verts.new(v) for v in ((-larg, 0, 0), (0, -comp, 0), (larg, 0, 0), (0, comp * 0.9, 0))]
    meio = [b.verts.new((v.co.x * 0.5, v.co.y * 0.5 + inclina * 0.45 * alt, alt * 0.5)) for v in base]
    topo = b.verts.new((0, inclina * alt, alt))
    for i in range(4):
        j = (i + 1) % 4
        b.faces.new((base[i], base[j], meio[j], meio[i])); b.faces.new((meio[i], meio[j], topo))
    b.faces.new(base[::-1])
    for v in b.verts: v[lp] = v.co.z / alt
    m = bpy.data.meshes.new("Crista"); b.to_mesh(m); b.free()
    return m
CRISTAS = []
def por_crista(x, y, alt, larg, comp):
    h, n = raio_pele(V((x, y, 9.0)), V((0, 0, -1)), 9.0)
    if h is None: return
    m = crista(alt, larg, comp, 0.35)
    n = (n + V((0, 0, 1))).normalized()                          # meio termo entre a normal e a vertical
    rot = V((0, 0, 1)).rotation_difference(n).to_matrix().to_4x4()
    m.transform(rot); m.transform(__import__("mathutils").Matrix.Translation(h - n * 0.10))
    CRISTAS.append(m)
y = -7.7
while y < 15.0:
    t, b_, w = interp(PERFIL, y)
    cauda = suave((y - 3.0) / 2.0)
    alt = (0.70 + 0.12 * math.exp(-((y + 2.0) / 3.5) ** 2)) * (1 - 0.50 * suave((y - 5.0) / 10.0))
    if y < -6.3: alt *= 0.70                                      # nuca: escudos menores
    passo = 0.82 - 0.24 * suave((y - 5.0) / 9.0)
    if y < 10.5:
        xc = lerp(w * 0.20, max(0.16, w * 0.30), cauda)
        for s in (1, -1): por_crista(xc * s, y, alt, 0.26 + 0.16 * alt, 0.36 + 0.18 * alt)
    else:
        por_crista(0.0, y, alt * 1.05, 0.22 + 0.14 * alt, 0.32 + 0.16 * alt)
    if -6.8 < y < 4.5:                                            # fileiras laterais do dorso (escudos menores)
        for frac, k in ((0.50, 0.60), (0.74, 0.40)):
            for s in (1, -1): por_crista(w * frac * s, y + 0.25, alt * k, 0.22, 0.30)
    elif 4.5 <= y < 9.0:
        for s in (1, -1): por_crista(w * 0.62 * s, y + 0.25, alt * 0.45, 0.20, 0.28)
    y += passo
for yy, xx, a in ((-8.15, 0.55, 0.22), (-7.95, 1.05, 0.18)):     # escudos pos-occipitais
    for s in (1, -1): por_crista(xx * s, yy, a, 0.18, 0.22)

# garras claras curvas na ponta de cada dedo
GARRAS = []
for s in (1, -1):
    for dian in (True, False):
        for d in dedos(s, dian):
            ponta = d[-1][0]; dirv = (ponta - d[0][0]); dirv.z = 0; dirv.normalize()
            L = 0.62 if dian else 0.70
            pts = [ponta - dirv * 0.05 + V((0, 0, 0.02)), ponta + dirv * L * 0.35 + V((0, 0, 0.02)),
                   ponta + dirv * L * 0.70 + V((0, 0, -0.06)), ponta + dirv * L + V((0, 0, -0.17))]
            GARRAS.append(tubo(pts, [0.13, 0.11, 0.07, 0.0], "Garra", 8))

def objeto(malhas, nome):
    b = bmesh.new()
    for mm in malhas: b.from_mesh(mm); bpy.data.meshes.remove(mm)
    m = bpy.data.meshes.new(nome); b.to_mesh(m); b.free()
    for pl in m.polygons: pl.use_smooth = True
    o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o); return o
O_DENTES, O_GENG = objeto(DENTES, "CR_Croc_Dentes"), objeto(GENG, "CR_Croc_Gengivas")
O_CRISTAS, O_GARRAS = objeto(CRISTAS, "CR_Croc_Cristas"), objeto(GARRAS, "CR_Croc_Garras")
for p in O_CRISTAS.data.polygons: p.use_smooth = False
O_CRISTAS.modifiers.new("Bisel", "BEVEL").width = 0.02

# ------------------------------------------------------------------ materiais (procedurais; bake para o jogo depois)
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
def ops(nt, L):
    def mr(ent, a, b_, c=0.0, d=1.0):
        x = n(nt, "ShaderNodeMapRange"); x.inputs[1].default_value = a; x.inputs[2].default_value = b_
        x.inputs[3].default_value = c; x.inputs[4].default_value = d; L.new(ent, x.inputs[0]); return x.outputs[0]
    def op(o_, a, b_=None, v=None):
        x = n(nt, "ShaderNodeMath", operation=o_)
        if isinstance(a, (int, float)): x.inputs[0].default_value = a
        else: L.new(a, x.inputs[0])
        if b_ is not None: L.new(b_, x.inputs[1])
        if v is not None: x.inputs[1].default_value = v
        return x.outputs[0]
    def mix(f, a, b_):
        x = n(nt, "ShaderNodeMix", data_type="RGBA")
        if isinstance(f, (int, float)): x.inputs["Factor"].default_value = f
        else: L.new(f, x.inputs["Factor"])
        for i, c in ((6, a), (7, b_)):
            if isinstance(c, tuple): x.inputs[i].default_value = c
            else: L.new(c, x.inputs[i])
        return x.outputs[2]
    return mr, op, mix
def mat_pele():
    """paleta da referencia: dorso carvao com placas verde-oliva e musgo discreto; flanco baixo ocre/terroso; ventre claro
    em placas largas; aros ocre-dourados nas placas erguidas, frestas pretas; cauda com faixas escuras nos flancos"""
    m, nt, b, L = mat("M_Croc_Pele"); mr, op, mix = ops(nt, L)
    tc = n(nt, "ShaderNodeTexCoord"); geo = n(nt, "ShaderNodeNewGeometry")
    pos = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], pos.inputs[0])
    nr = n(nt, "ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], nr.inputs[0])
    dors = mr(nr.outputs["Z"], 0.20, 0.80)                        # 1 = face para cima
    vent = mr(nr.outputs["Z"], -0.45, -0.80)                      # 1 = face para baixo (ventre)
    cab = mr(pos.outputs["Y"], -9.0, -7.6)                        # 0 cabeca -> 1 corpo
    perna = mr(pos.outputs["Z"], 2.2, 1.4)                        # 1 = parte baixa das patas
    # tamanho das escamas: placas grandes no dorso, medias nos flancos, pequenas na cabeca e nas patas
    tam = op("ADD", op("MULTIPLY", op("SUBTRACT", 1.0, dors), v=1.5), v=1.05)
    tam = op("MULTIPLY", tam, op("ADD", op("MULTIPLY", op("SUBTRACT", 1.0, cab), v=0.8), v=1.0))
    tam = op("MULTIPLY", tam, op("ADD", op("MULTIPLY", perna, v=0.6), v=1.0))
    est = n(nt, "ShaderNodeVectorMath", operation="MULTIPLY"); est.inputs[1].default_value = (1.0, 0.85, 1.25)
    L.new(tc.outputs["Object"], est.inputs[0])
    dist_ = n(nt, "ShaderNodeTexNoise"); dist_.inputs["Scale"].default_value = 0.7; L.new(tc.outputs["Object"], dist_.inputs["Vector"])
    warp = n(nt, "ShaderNodeVectorMath", operation="MULTIPLY_ADD"); L.new(dist_.outputs["Color"], warp.inputs[0])
    warp.inputs[1].default_value = (0.22, 0.22, 0.22); L.new(est.outputs[0], warp.inputs[2])
    ve = n(nt, "ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE"); vc = n(nt, "ShaderNodeTexVoronoi")
    for t in (ve, vc): L.new(warp.outputs[0], t.inputs["Vector"]); L.new(tam, t.inputs["Scale"])
    ed = ve.outputs["Distance"]
    br = n(nt, "ShaderNodeTexBrick"); br.offset = 0.0; br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.03; br.inputs["Mortar Smooth"].default_value = 0.4
    br.inputs["Brick Width"].default_value = 0.62; br.inputs["Row Height"].default_value = 0.46
    bvec = n(nt, "ShaderNodeCombineXYZ"); L.new(pos.outputs["X"], bvec.inputs[0]); L.new(pos.outputs["Y"], bvec.inputs[1])
    L.new(bvec.outputs[0], br.inputs["Vector"])
    ru = n(nt, "ShaderNodeTexNoise"); ru.inputs["Scale"].default_value = 0.45; ru.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], ru.inputs["Vector"])
    mus = n(nt, "ShaderNodeTexNoise"); mus.inputs["Scale"].default_value = 0.9; mus.inputs["Detail"].default_value = 8
    mus.inputs["Roughness"].default_value = 0.65; L.new(tc.outputs["Object"], mus.inputs["Vector"])
    sep_c = n(nt, "ShaderNodeSeparateColor"); L.new(vc.outputs["Color"], sep_c.inputs[0])
    var = op("ADD", op("MULTIPLY", sep_c.outputs[0], v=0.6), op("MULTIPLY", ru.outputs["Fac"], v=0.4))
    # placa do dorso/flanco alto: carvao <-> verde-oliva escuro
    alto = rampa(nt, L, var, [(0.30, (0.006, 0.007, 0.005, 1)), (0.58, (0.014, 0.017, 0.008, 1)), (0.85, (0.034, 0.040, 0.013, 1))])
    # flanco baixo e patas: ocre-terroso escurecido
    baixo = rampa(nt, L, var, [(0.25, (0.030, 0.024, 0.010, 1)), (0.55, (0.090, 0.064, 0.024, 1)), (0.85, (0.170, 0.120, 0.045, 1))])
    flb = op("MULTIPLY", mr(nr.outputs["Z"], 0.30, -0.25), op("SUBTRACT", 1.0, vent))
    flb = op("MULTIPLY", flb, mr(pos.outputs["Z"], 5.2, 3.6))   # so abaixo do meio do flanco
    faixa = op("MULTIPLY", mr(op("SINE", op("MULTIPLY", pos.outputs["Y"], v=1.25)), 0.2, 0.7), mr(pos.outputs["Y"], 3.0, 5.0))
    flb = op("MULTIPLY", flb, op("SUBTRACT", 1.0, op("MULTIPLY", faixa, v=0.75)))   # faixas escuras na cauda
    c0 = mix(flb, alto.outputs["Color"], baixo.outputs["Color"])
    # aro ocre-dourado na borda erguida das placas, fresta preta
    aro = op("MULTIPLY", mr(ed, 0.02, 0.085, 1.0, 0.0), mr(ed, 0.003, 0.012))
    ru2 = n(nt, "ShaderNodeTexNoise"); ru2.inputs["Scale"].default_value = 2.5; L.new(tc.outputs["Object"], ru2.inputs["Vector"])
    aro = op("MULTIPLY", aro, mr(ru2.outputs["Fac"], 0.35, 0.65, 0.35, 1.0))
    ocre = mix(flb, (0.30, 0.20, 0.055, 1), (0.46, 0.33, 0.12, 1))
    c1 = mix(op("MULTIPLY", aro, v=0.92), c0, ocre)
    musgo = op("MULTIPLY", mr(mus.outputs["Fac"], 0.57, 0.66), op("ADD", op("MULTIPLY", dors, v=0.8), v=0.25))
    musgo = op("MULTIPLY", musgo, mr(ed, 0.03, 0.09))             # musgo no centro das placas, nao nas frestas
    c2 = mix(op("MULTIPLY", musgo, v=0.75), c1, (0.085, 0.125, 0.012, 1))
    barriga = rampa(nt, L, ru.outputs["Fac"], [(0.35, (0.20, 0.145, 0.06, 1)), (0.65, (0.32, 0.235, 0.10, 1))])
    cb = mix(br.outputs["Fac"], barriga.outputs["Color"], (0.035, 0.025, 0.010, 1))
    vfat = op("MULTIPLY", vent, op("SUBTRACT", 1.0, perna))
    c3 = mix(vfat, c2, cb)
    fr = op("MULTIPLY", op("SUBTRACT", 1.0, mr(ed, 0.0, 0.016)), op("SUBTRACT", 1.0, vfat))
    corf = mix(fr, c3, (0.006, 0.006, 0.005, 1))
    L.new(corf, b.inputs["Base Color"])
    rg = mr(aro, 0.0, 1.0, 0.74, 0.55); L.new(rg, b.inputs["Roughness"])
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.0
    # relevo: placa em domo + fresta funda; ventre por tijolo; poros/rugas finas
    domo = op("POWER", mr(ed, 0.0, 0.18), v=0.5)
    alt_v = op("SUBTRACT", 1.0, br.outputs["Fac"])
    alt = op("ADD", op("MULTIPLY", domo, op("SUBTRACT", 1.0, vfat)), op("MULTIPLY", alt_v, vfat))
    fino = n(nt, "ShaderNodeTexNoise"); fino.inputs["Scale"].default_value = 16; fino.inputs["Detail"].default_value = 4
    L.new(tc.outputs["Object"], fino.inputs["Vector"])
    alt = op("ADD", alt, op("MULTIPLY", fino.outputs["Fac"], v=0.22))
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 1.0; bp.inputs["Distance"].default_value = 0.07
    L.new(alt, bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m
def mat_liso(nome, cor, rug, bump=0.0, esc=None):
    m, nt, b, L = mat(nome); b.inputs["Base Color"].default_value = cor; b.inputs["Roughness"].default_value = rug
    if bump:
        tc = n(nt, "ShaderNodeTexCoord"); no = n(nt, "ShaderNodeTexNoise"); no.inputs["Scale"].default_value = esc or 8
        L.new(tc.outputs["Object"], no.inputs["Vector"]); bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
        L.new(no.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
        if "Subsurface Weight" in b.inputs: b.inputs["Subsurface Weight"].default_value = 0.15
    return m
def mat_marfim(nome, raiz, ponta, rug, comp):
    """gradiente raiz escura -> ponta clara pelo atributo 'ponta' (0 raiz, 1 ponta) gravado na geracao"""
    m, nt, b, L = mat(nome); mr, op, mix = ops(nt, L)
    at = n(nt, "ShaderNodeAttribute"); at.attribute_name = "ponta"
    tc = n(nt, "ShaderNodeTexCoord"); an = n(nt, "ShaderNodeTexWave"); an.inputs["Scale"].default_value = 40
    an.bands_direction = "Z"; L.new(tc.outputs["Object"], an.inputs["Vector"])
    gr = rampa(nt, L, at.outputs["Fac"], [(0.0, raiz), (comp, (raiz[0] * 1.7, raiz[1] * 1.7, raiz[2] * 1.6, 1)), (1.0, ponta)])
    L.new(gr.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rug
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; L.new(an.outputs["Fac"], bp.inputs["Height"])
    L.new(bp.outputs[0], b.inputs["Normal"])
    return m
def mat_crista():
    """base carvao como a pele, ponta ocre/dourada envelhecida (referencia)"""
    m, nt, b, L = mat("M_Croc_Crista"); mr, op, mix = ops(nt, L)
    at = n(nt, "ShaderNodeAttribute"); at.attribute_name = "ponta"
    tc = n(nt, "ShaderNodeTexCoord"); no = n(nt, "ShaderNodeTexNoise"); no.inputs["Scale"].default_value = 4
    L.new(tc.outputs["Object"], no.inputs["Vector"])
    f = op("ADD", at.outputs["Fac"], op("MULTIPLY", op("SUBTRACT", no.outputs["Fac"], v=0.5), v=0.35))
    gr = rampa(nt, L, f, [(0.20, (0.010, 0.011, 0.008, 1)), (0.48, (0.04, 0.04, 0.016, 1)), (0.70, (0.30, 0.19, 0.05, 1)), (0.92, (0.55, 0.40, 0.14, 1))])
    L.new(gr.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.6
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.4; L.new(no.outputs["Fac"], bp.inputs["Height"])
    L.new(bp.outputs[0], b.inputs["Normal"])
    return m
def mat_olho():
    m, nt, b, L = mat("M_Croc_Olho"); mr, op, mix = ops(nt, L)
    tc = n(nt, "ShaderNodeTexCoord"); sep = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    # pupila vertical: fenda estreita em Y (frente-tras) olhando para fora (X)
    # calota voltada para fora e para cima (normal da orbita ~ (0,44; 0; 0,89)); coordenadas do objeto ~ raio 0,24
    cal = op("ADD", op("MULTIPLY", op("ABSOLUTE", sep.outputs["X"]), v=0.44 / 0.24), op("MULTIPLY", sep.outputs["Z"], v=0.89 / 0.24))
    na_cal = mr(cal, 0.45, 0.65)
    d = op("ABSOLUTE", sep.outputs["Y"]); pup = op("MULTIPLY", mr(d, 0.045, 0.025), na_cal)
    anel = rampa(nt, L, cal, [(0.35, (0.20, 0.10, 0.01, 1)), (0.65, (0.62, 0.36, 0.03, 1)), (0.95, (0.85, 0.58, 0.06, 1))])
    cor = mix(pup, anel.outputs["Color"], (0.004, 0.003, 0.002, 1))
    L.new(cor, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.06
    return m
MP = mat_pele()
MB = mat_liso("M_Croc_Boca", (0.36, 0.075, 0.06, 1), 0.38, 0.25, 6)
MGA = mat_liso("M_Croc_Garganta", (0.06, 0.012, 0.010, 1), 0.5)
MG = mat_liso("M_Croc_Gengiva", (0.42, 0.15, 0.11, 1), 0.38, 0.2, 10)
ML = mat_liso("M_Croc_Lingua", (0.42, 0.12, 0.09, 1), 0.32, 0.35, 9)
MD = mat_marfim("M_Croc_Dente", (0.26, 0.18, 0.09, 1), (0.66, 0.56, 0.36, 1), 0.40, 0.25)
MGR = mat_marfim("M_Croc_Garra", (0.06, 0.05, 0.03, 1), (0.72, 0.62, 0.42, 1), 0.40, 0.35)
MC, MO = mat_crista(), mat_olho()
for mm in (MP, MB, MGA): ob.data.materials.append(mm)
O_DENTES.data.materials.append(MD); O_GENG.data.materials.append(MG); LINGUA.data.materials.append(ML)
O_CRISTAS.data.materials.append(MC); O_GARRAS.data.materials.append(MGR)
for o in OLHOS: o.data.materials.append(MO)
col = bpy.data.collections.new("CR_Croc"); sc.collection.children.link(col)
for o in [ob, O_DENTES, O_GENG, LINGUA, O_CRISTAS, O_GARRAS] + OLHOS:
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o)

# ------------------------------------------------------------------ cabeca maior (referencia: cranio e focinho pesados)
# escala a partir da nuca com peso suave: articulacoes do tronco nao mudam; dobradica da mandibula acompanha
def aplicar_transf():
    for o in col.objects:
        bpy.context.view_layer.objects.active = o
        for oo in col.objects: oo.select_set(oo == o)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
aplicar_transf()                                    # coordenadas locais = mundo (a escala abaixo atua em v.co)
K_CAB, PIV = 1.20, V((0, -7.6, 4.7))
def cabeca(p):
    w = suave((-7.4 - p.y) / 1.4)
    return PIV + (p - PIV) * (1 + (K_CAB - 1) * w)
for o in col.objects:
    for v in o.data.vertices: v.co = cabeca(v.co)
    o.data.update()
DOBRADICA = cabeca(V((0, Y_CANTO + 0.15, Z_CANTO)))
col["dobradica"] = tuple(DOBRADICA)

# ------------------------------------------------------------------ pes no chao (z=0)
DZ = -min(v.co.z for v in ob.data.vertices)
for o in col.objects: o.location.z += DZ
col["deslocZ"] = DZ; col["dobradica"] = (DOBRADICA.x, DOBRADICA.y, DOBRADICA.z + DZ); print("CROC_DZ", round(DZ, 3), "dobradica", col["dobradica"][:])
aplicar_transf()
for o in OLHOS:
    for oo in col.objects: oo.select_set(oo == o)
    bpy.context.view_layer.objects.active = o; bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
# ------------------------------------------------------------------ medidas reais
mn = V((1e9,) * 3); mx = V((-1e9,) * 3)
for v in ob.data.vertices: mn = V(map(min, mn, v.co)); mx = V(map(max, mx, v.co))
def alt_em(y, x=0.0):
    bpy.context.view_layer.update()
    ok, h, _, _ = ob.ray_cast(V((x, y, 12)), V((0, 0, -1)), distance=12); return h.z if ok else float("nan")
print("CROC_MEDIDAS comprimento %.2f largura %.2f altura_pele %.2f ombro(y=-4.8) %.2f quadril(y=2.6) %.2f chao %.3f" % (
    mx.y - mn.y, mx.x - mn.x, mx.z, alt_em(-4.8), alt_em(2.6), mn.z))
dg = bpy.context.evaluated_depsgraph_get()
for o in col.objects:
    e = o.evaluated_get(dg); me_ = e.to_mesh(); me_.calc_loop_triangles()
    print("CROC_TRIS", o.name, len(me_.loop_triangles)); e.to_mesh_clear()

# ------------------------------------------------------------------ cena de revisao (luz neutra, fundo cinza claro como a referencia)
w = bpy.data.worlds.new("Neutro"); sc.world = w
if w.node_tree is None: w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.43, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.3
for nome, en, rot in (("Chave", 3.6, (math.radians(45), 0, math.radians(140))), ("Preench", 1.0, (math.radians(60), 0, math.radians(-60))),
                      ("Contra", 1.6, (math.radians(120), 0, math.radians(10)))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.angle = math.radians(8); lo = bpy.data.objects.new(nome, l)
    sc.collection.objects.link(lo); lo.rotation_euler = rot
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 48
for k, v in (("use_raytracing", True), ("use_shadows", True)):
    if hasattr(sc.eevee, k): setattr(sc.eevee, k, v)
sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 1672, 941
sc.render.film_transparent = False
camd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", camd); sc.collection.objects.link(cam); sc.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Crocodilo_Ref.blend"))
print("CROC_OK")
