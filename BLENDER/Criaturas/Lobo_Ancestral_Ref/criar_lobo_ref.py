"""Lobo Ancestral (referencia 03/11/2026: ref/lobo-ancestral-referencia.png) - modelo de conceito HIGH em POSE NEUTRA.
Unidade = stud. Frente = -Y, pes em Z=0, simetrico em X (esquerda do lobo = +X). Ombro (cernelha) 6,5 (oficial 5,5-7).
Corpo = grafo Skin -> remesh voxel -> escultura do rosto; cores por regiao em atributo de vertice ("Cor") e marcas verdes
discretas ("Marca", so aparencia, sem elemento/poder). Pelagem = mechas de malha opaca (raiz afundada na pele) com
estrias de fios no material. Os arquivos da V2-V5 (Blockouts/) nao sao tocados.
Uso: blender -b --factory-startup -P criar_lobo_ref.py -- <saida_dir> [sem_render]"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, noise, kdtree
from mathutils.bvhtree import BVHTree

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; rnd = random.Random(7); V = Vector
def lerp(a, b, t): return a + (b - a) * t
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def faixa(x, a, b, c, d): return suave((x - a) / (b - a)) * (1 - suave((x - c) / (d - c)))
# cabeca maior (referencia: cabeca + colar facial volumosos): escala KC em torno do alto do pescoco. As regras de
# rosto/cor sao escritas no referencial de projeto e avaliadas em INV(p).
KC, PIV = 1.15, Vector((0, -3.05, 7.55))
def wcab(y): return suave((-3.0 - y) / 0.45)
def CAB(p): return PIV + (p - PIV) * (1 + (KC - 1) * wcab(p.y))
def INV(p):
    q = p.copy()
    for _ in range(4): q = PIV + (p - PIV) / (1 + (KC - 1) * wcab(q.y))
    return q

# ------------------------------------------------------------------ eixo do corpo (y, z, raio_largura, raio_altura)
ESPINHA = [(-5.05, 7.62, 0.17, 0.16), (-4.85, 7.66, 0.27, 0.27), (-4.55, 7.76, 0.34, 0.36), (-4.25, 7.93, 0.43, 0.43),  # focinho
           (-3.92, 8.08, 0.57, 0.53), (-3.55, 8.06, 0.63, 0.59), (-3.25, 7.86, 0.58, 0.58),                            # cranio
           (-3.00, 7.30, 0.72, 0.85), (-2.75, 6.60, 0.85, 1.05), (-2.50, 5.95, 0.95, 1.25),                            # pescoco
           (-2.05, 5.10, 1.00, 1.60), (-1.20, 5.05, 1.00, 1.62), (-0.30, 5.25, 0.90, 1.30),                            # torax
           (0.60, 5.45, 0.78, 1.00), (1.40, 5.50, 0.85, 1.00), (2.15, 5.40, 0.95, 1.10), (2.80, 5.40, 0.75, 0.90),     # lombo/quadril
           (3.25, 5.60, 0.38, 0.38), (3.80, 5.35, 0.50, 0.50), (4.35, 4.85, 0.62, 0.62), (4.85, 4.15, 0.68, 0.68),     # cauda
           (5.25, 3.35, 0.66, 0.66), (5.55, 2.55, 0.55, 0.55), (5.72, 1.85, 0.30, 0.30)]
I_FOC, I_CRAN, I_PEITO, I_QUAD = 1, 5, 10, 15
CAUDA = [V((0, y, z)) for y, z, _, _ in ESPINHA[16:]]
MANDIBULA = [(V((0, -3.80, 7.62)), 0.50, 0.32), (V((0, -4.30, 7.44)), 0.33, 0.19), (V((0, -4.75, 7.40)), 0.21, 0.12)]

def perna(s, dianteira):
    """digitigrado: cotovelo para tras, joelho para frente, jarrete para tras; musculo em cima, canela grossa de pelo"""
    if dianteira:
        return [(V((0.60 * s, -2.05, 5.30)), 0.50, 0.75), (V((0.70 * s, -2.45, 4.50)), 0.50, 0.55),
                (V((0.62 * s, -1.95, 3.55)), 0.38, 0.40), (V((0.58 * s, -2.05, 2.50)), 0.32, 0.32),
                (V((0.56 * s, -2.15, 1.30)), 0.25, 0.24), (V((0.56 * s, -2.22, 0.70)), 0.24, 0.22),
                (V((0.56 * s, -2.35, 0.28)), 0.30, 0.22)]
    return [(V((0.65 * s, 2.05, 5.20)), 0.75, 1.00), (V((0.75 * s, 1.75, 3.95)), 0.70, 0.75),
            (V((0.68 * s, 1.50, 3.15)), 0.45, 0.45), (V((0.62 * s, 2.15, 2.20)), 0.33, 0.38),
            (V((0.58 * s, 2.60, 1.45)), 0.24, 0.26), (V((0.56 * s, 2.50, 0.80)), 0.22, 0.21),
            (V((0.56 * s, 2.40, 0.28)), 0.28, 0.21)]

_perna = perna
def perna(s, dianteira):
    k = (1.1, 1.1, 1.15, 1.22, 1.32, 1.32, 1.25) if dianteira else (1.05, 1.05, 1.1, 1.2, 1.32, 1.32, 1.25)
    return [(p, rx * f, ry * f) for (p, rx, ry), f in zip(_perna(s, dianteira), k)]

def dedos(s, dianteira):
    base = perna(s, dianteira)[-1][0]
    return [[(base + V((dx * s, -0.30, -0.12)), 0.15, 0.12), (base + V((dx * 1.1 * s, -0.46, -0.15)), 0.12, 0.09)]
            for dx in (-0.24, -0.08, 0.08, 0.24)]

# ------------------------------------------------------------------ corpo (grafo Skin)
me = bpy.data.meshes.new("Lobo_Corpo"); ob = bpy.data.objects.new("Lobo_Corpo", me); sc.collection.objects.link(ob)
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
        for d in dedos(s, dian): cadeia(d, pv[-1])
    cadeia([(V((0.45 * s, -3.65, 7.80)), 0.30, 0.26)], esp[I_CRAN])          # arco zigomatico / bochecha
bm.to_mesh(me); bm.free()
sk = ob.modifiers.new("Pele", "SKIN"); sk.branch_smoothing = 0.7; sk.use_smooth_shade = True
for i, d in enumerate(me.skin_vertices[0].data): d.radius = raios[i]; d.use_root = (i == 11)
sub = ob.modifiers.new("Sub", "SUBSURF"); sub.levels = sub.render_levels = 2
bpy.context.view_layer.objects.active = ob; ob.select_set(True)
for m in list(ob.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)

for v in ob.data.vertices:                                 # massas: peito fundo e estreito, barriga recolhida
    p = v.co; x, y, z = p
    if -0.6 < y < 1.6 and z < 4.9: p.z += 0.22 * math.exp(-((y - 0.6) / 0.7) ** 2) * suave((4.9 - z) / 0.5)
    k = math.exp(-((y + 2.35) / 0.55) ** 2) * math.exp(-((z - 4.9) / 0.6) ** 2); p.x *= 1 + 0.10 * k      # ombro
    k = math.exp(-((y - 2.0) / 0.6) ** 2) * math.exp(-((z - 4.6) / 0.7) ** 2); p.x *= 1 + 0.08 * k       # coxa
    if y < -3.9 and z > 8.0 and abs(x) < 0.45: p.z += 0.08 * math.exp(-((y + 4.15) / 0.2) ** 2)          # testa / stop
    v.co = CAB(v.co)
rm = ob.modifiers.new("Remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.034; rm.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=rm.name)
sm = ob.modifiers.new("Liso", "SMOOTH"); sm.factor = 0.5; sm.iterations = 6
bpy.ops.object.modifier_apply(modifier=sm.name)

OLHO = CAB(V((0.36, -4.16, 8.02))); NARIZ = V((0, -5.17, 7.70))
ok_, hit, nrm_h, _ = ob.ray_cast(V((3.0, OLHO.y, OLHO.z)), V((-1, 0, 0)))
if ok_: OLHO = hit - nrm_h * 0.085
OLHO_D = INV(OLHO)                                          # olho no referencial de projeto
print("LOBO_OLHO", tuple(round(c, 3) for c in OLHO))
for v in ob.data.vertices:                                 # rosto: linha da boca, narinas, orbitas, sobrancelha
    p, nrm = v.co, v.normal; q = INV(p); x, y, z = q
    if y < -4.0 and abs(x) > 0.05:
        zb = 7.52 + (y + 5.05) * 0.10
        p -= nrm * 0.024 * KC * math.exp(-((z - zb) / 0.03) ** 2) * suave((-4.0 - y) / 0.25)
    for s_ in (1, -1):
        d = (q - V((0.075 * s_, -5.21, 7.72))).length
        if d < 0.07: p -= nrm * 0.04 * KC * (1 - d / 0.07) ** 2
        o = V((OLHO_D.x * s_, OLHO_D.y, OLHO_D.z)); d = (q - o).length
        if d < 0.21: p -= nrm * 0.06 * KC * (1 - d / 0.21) ** 2
        b = o + V((0.0, 0.03, 0.16)); d = (q - b).length
        if d < 0.2 and z > o.z: p += nrm * 0.045 * KC * (1 - d / 0.2) ** 2                             # sobrancelha
ob.data.update()

# ------------------------------------------------------------------ cores por regiao (albedo linear)
CREME, CREME_Q = V((0.66, 0.56, 0.44)), V((0.58, 0.46, 0.33))
CINZA_E, CINZA, CINZA_C = V((0.050, 0.046, 0.043)), V((0.16, 0.145, 0.135)), V((0.34, 0.32, 0.30))
CAST, CAST_E, CAST_C = V((0.26, 0.165, 0.10)), V((0.13, 0.075, 0.042)), V((0.46, 0.34, 0.23))
PRETO = V((0.018, 0.016, 0.015)); VERDE = V((0.22, 0.85, 0.45))

def cor(p, n):
    p = INV(p) if p.y < -2.9 else p
    x, y, z = p; ax = abs(x); s = 1 if x >= 0 else -1
    r1 = noise.noise(p * 1.6); r2 = noise.noise(V((x * 9, y * 1.5, z * 9)))       # manchas + estrias ao longo do corpo
    c = lerp(CAST, CAST_C, (1 - suave((z - 2.2) / 1.2)) * 0.7)                      # base castanha; canelas mais claras
    c = lerp(c, CAST_E, faixa(z, 2.6, 3.4, 5.6, 6.2) * (y > 1.0) * (0.45 + 0.4 * suave((n.y - 0.1) / 0.5)))   # coxa
    dors = suave((n.z + 0.25) / 0.5) * suave((z - 4.95 + 0.45 * r2) / 0.55)          # sela cinza-escura: dorso e alto do flanco
    if y > 3.1: dors = suave((n.z + 0.35) / 0.6)                                    # cauda: escura por cima
    if -3.4 < y < -1.9 and z > 5.8: dors = max(dors, suave((n.y + 0.1) / 0.5) * suave((z - 5.8) / 0.4))   # nuca
    c = lerp(c, lerp(CINZA_E, CINZA, 0.5 + 0.5 * r2), dors * (0.9 + 0.1 * r1))
    cr = 0.0                                                                         # creme: peito, garganta, ventre, interno
    if y < -1.8 and z < 7.5: cr = max(cr, suave((-n.y - 0.15) / 0.4) * suave((-2.0 - y) / 0.5))
    cr = max(cr, suave((-n.z - 0.35) / 0.4) * (y < 3.0))
    if z < 4.2 and y < 3.0: cr = max(cr, suave((-n.x * s - 0.1) / 0.4) * 0.85)
    if z < 1.4 and y < 3.0: cr = max(cr, 0.55 * (1 - suave((z - 0.9) / 0.5)) + 0.2)
    if y > 4.6: cr = max(cr, suave((y - 4.7) / 0.6) * 0.75)                          # ponta da cauda clara
    if y < -3.3 and z > 6.9:                                                        # cabeca
        cr = 0.0
        c = lerp(CINZA, CAST, 0.35 + 0.25 * r1)
        masc = suave((7.95 - z) / 0.22) * suave((-n.z + 0.35) / 0.5)                 # mascara creme baixa
        masc = max(masc, suave((-n.z - 0.2) / 0.3))
        masc = max(masc, suave((ax - 0.30) / 0.12) * suave((7.85 - z) / 0.2) * (y > -4.3))   # bochechas
        if y < -4.25: c = lerp(c, lerp(CAST_C, CREME, 0.5), 0.75 * suave((-4.25 - y) / 0.3))   # focinho claro
        c = lerp(c, CREME, masc)
        if -4.4 < y < -3.7 and z > 7.95 and ax < 0.28: c = lerp(c, CINZA_E, 0.5)    # risca escura da testa
        o = V((OLHO_D.x * s, OLHO_D.y, OLHO_D.z)); d = (p - o).length
        c = lerp(c, PRETO, suave((0.26 - d) / 0.06) * 0.85)                         # contorno do olho
        b = o + V((0.0, 0.0, 0.17)); c = lerp(c, CREME, suave((0.11 - (p - b).length) / 0.05) * 0.7)   # "sobrancelha"
        if y < -4.0 and abs(z - (7.52 + (y + 5.05) * 0.10)) < 0.03 and ax > 0.05: c = PRETO.copy()     # labios
        if (p - NARIZ).length < 0.24 and y < -5.0: c = PRETO.copy()
    c = lerp(c, lerp(CREME_Q, CREME, 0.5 + 0.5 * r2), cr)
    return c * (0.92 + 0.1 * r1)

def marca(p, n):
    """marcas verdes discretas (referencia): espiral no ombro, chevrons no peito, risca acima do olho"""
    p = INV(p) if p.y < -2.9 else p
    x, y, z = p; ax = abs(x); m = 0.0
    if ax > 0.45 and -3.0 < y < -1.3 and 4.3 < z < 6.4:
        q = (y + 2.15, z - 5.35); r = math.hypot(*q); th = math.atan2(q[1], q[0]) % (2 * math.pi)
        for k in range(3):
            rr = 0.06 + 0.06 * (th + 2 * math.pi * k)
            if rr < 0.55: m = max(m, suave((0.022 - abs(r - rr)) / 0.01))
    if y < -2.3 and 4.6 < z < 6.6 and ax < 0.75:
        for z0 in (6.25, 5.85):
            zc = z0 - 0.9 * ax; m = max(m, suave((0.024 - abs(z - zc)) / 0.01) * (ax > 0.06))
    if y < -3.3 and z > 7.9:
        q = V((ax - 0.30, y + 3.85, z - 8.22))
        m = max(m, suave((0.025 - abs(q.z - 0.25 * q.y)) / 0.01) * suave((0.28 - abs(q.y)) / 0.05) * suave((0.12 - abs(q.x)) / 0.04))
    return m


# ------------------------------------------------------------------ pelagem: mechas opacas na direcao do crescimento
def cauda_tangente(p):
    best, t = 1e9, V((0, 1, 0))
    for a, b in zip(CAUDA, CAUDA[1:]):
        ab = b - a; u = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)); d = (a + ab * u - p).length
        if d < best: best, t = d, ab.normalized()
    return t

def regiao(p, n):
    """(comprimento, largura, densidade relativa, direcao bruta) da mecha nesta regiao do corpo"""
    p = INV(p) if p.y < -2.9 else p
    x, y, z = p; ax = abs(x); s = 1 if x >= 0 else -1
    if y > 3.2: return 1.45 + 0.3 * suave((y - 3.5) / 1.2), 0.34, 2.6, cauda_tangente(p)
    if y < -3.35 and z > 6.9:                                                        # cabeca
        if ax > 0.36 and y > -4.1 and z < 8.1: return 0.62, 0.19, 2.6, V((0.45 * s, 1.0, -0.55))  # bochecha/colar facial
        if y > -4.0 and z > 8.05: return 0.36, 0.14, 1.4, V((0, 1.0, 0.15))         # alto da cabeca
        return 0, 0, 0, None
    if y < -1.6 and z > 3.6:                                                         # juba e peito
        alt = suave((z - 4.2) / 2.0)
        return 1.1 + 0.4 * alt, 0.32, 2.5, V((0.15 * s * (n.x * s > 0), 0.45, -1.0))
    if z < 3.4:                                                                      # pernas: pelo curto no alto
        if z < 1.3: return 0, 0, 0, None
        tras = n.y > (0.3 if y < 0 else 0.15)
        return (0.55 if tras else 0.40), 0.18, 1.3, V((0, 0.25, -1.0))
    if n.z < -0.3 and -1.4 < y < 1.6: return 0.72, 0.24, 1.7, V((0, 0.35, -1.0))  # franja da barriga
    if y > 1.2 and n.y > 0.15 and z < 5.5: return 0.75, 0.26, 1.7, V((0, 0.5, -1.0)) # culote
    return 0.90, 0.28, 1.6, V((0.1 * s, 1.0, -0.55))                                # dorso e flancos

BVH = None
def mecha(bm, uvl, cl, ml, p, n, d, L, w, rnd, ergue=0.05):
    """mecha deitada que ANDA pela superficie (cada anel e reprojetado na pele): secao lenticular achatada, larga
    perto da raiz e afinando ate a ponta, sobreposta as vizinhas como telhas; so a ponta descola um pouco"""
    anel = 6; vs = []; pos = p.copy(); dd = d.copy(); nn = n.copy(); passo = L / anel
    curva = rnd.uniform(-0.12, 0.12)
    for i in range(anel + 1):
        t = i / anel
        if i > 0:
            pos = pos + dd * passo
            loc, nf, _, _ = BVH.find_nearest(pos)
            if loc is not None: pos, nn = loc, nf
            dd = dd - nn * dd.dot(nn)
            if dd.length < 1e-4: dd = d.copy()
            dd.normalize(); dd = (dd + nn.cross(dd) * curva / anel).normalized()
        b = nn.cross(dd).normalized()
        off = 0.012 + L * ergue * math.sin(math.pi * t) + 0.05 * L * t ** 3
        c = pos + nn * off
        hw = w * (0.62 + 0.38 * math.sin(math.pi * (0.15 + 0.5 * t))) * (1 - t) ** 0.65
        ht = hw * 0.26 + 0.004
        vs.append([bm.verts.new(c + b * hw - nn * ht * 0.3), bm.verts.new(c + nn * ht), bm.verts.new(c - b * hw - nn * ht * 0.3), bm.verts.new(c - nn * ht * 0.9)])
    ponta = bm.verts.new(pos + dd * (passo * 0.6) + nn * (0.012 + 0.06 * L))
    for i in range(anel):
        for k in range(4):
            k2 = (k + 1) % 4
            f = bm.faces.new((vs[i][k], vs[i][k2], vs[i + 1][k2], vs[i + 1][k]))
            for lp, uv in zip(f.loops, ((k / 4, i / anel), ((k + 1) / 4, i / anel), ((k + 1) / 4, (i + 1) / anel), (k / 4, (i + 1) / anel))):
                lp[uvl].uv = uv
    for k in range(4):
        f = bm.faces.new((vs[anel][k], vs[anel][(k + 1) % 4], ponta))
        for lp, uv in zip(f.loops, ((k / 4, 1 - 1 / anel), ((k + 1) / 4, 1 - 1 / anel), ((k + 0.5) / 4, 1.0))): lp[uvl].uv = uv
    var = rnd.uniform(0.85, 1.12); c_raiz = cor(p, n)
    for i, ring in enumerate(vs + [[ponta]]):
        t = min(1.0, i / anel)
        for v in ring:
            c0 = lerp(c_raiz, cor(v.co, n), 0.5) * var * (0.8 + 0.2 * t)
            c0 = lerp(c0, c0 * 1.2 + V((0.02, 0.02, 0.02)), t * 0.4)                          # ponta mais clara
            v[cl] = (min(c0.x, 1), min(c0.y, 1), min(c0.z, 1), 1.0); v[ml] = marca(v.co, n)
    return vs

def pelagem(corpo, total=1900):
    me_ = corpo.data; areas = []
    for f in me_.polygons:
        L, w, den, dr = regiao(f.center, f.normal)
        areas.append(f.area * den if L > 0 else 0.0)
    soma = sum(areas); escala = total / soma
    pm = bpy.data.meshes.new("Lobo_Pelagem"); po = bpy.data.objects.new("Lobo_Pelagem", pm); sc.collection.objects.link(po)
    b = bmesh.new(); uvl = b.loops.layers.uv.new("UVMap")
    cl = b.verts.layers.float_color.new("Cor"); ml = b.verts.layers.float.new("Marca"); n_m = 0
    for f, a in zip(me_.polygons, areas):
        k = a * escala; q = int(k) + (rnd.random() < k - int(k))
        for _ in range(q):
            u, v_ = rnd.random(), rnd.random()
            if u + v_ > 1: u, v_ = 1 - u, 1 - v_
            vv = [me_.vertices[i].co for i in f.vertices[:3]]
            p = vv[0] + (vv[1] - vv[0]) * u + (vv[2] - vv[0]) * v_; n = f.normal.copy()
            L, w, den, dr = regiao(p, n)
            if L <= 0: continue
            dr = dr.normalized() + V((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * 0.18
            d = dr - n * dr.dot(n)
            if d.length < 1e-3: continue
            ergue = 0.07 if (p.y > 3.2 or (p.y < -1.6 and p.z > 3.6)) else 0.035
            mecha(b, uvl, cl, ml, p, n, d.normalized(), L * rnd.uniform(0.8, 1.2), w * rnd.uniform(0.85, 1.2), rnd, ergue); n_m += 1
    b.to_mesh(pm); b.free()
    for pl in pm.polygons: pl.use_smooth = True
    print("LOBO_MECHAS", n_m, "tris", sum(len(pl.vertices) - 2 for pl in pm.polygons))
    return po
def espessura(p, n):
    """subpelo: espessura do pelo por regiao (infla a pele ao longo da normal)"""
    q = INV(p) if p.y < -2.9 else p; x, y, z = q; ax = abs(x)
    if y > 3.2: return 0.20
    if y < -3.35 and z > 6.9: return 0.13 * suave((ax - 0.34) / 0.12) * (y > -4.1) * (z < 8.1)
    if y < -1.6 and z > 3.6: return 0.16 + 0.16 * suave((z - 4.2) / 1.6)
    if z < 3.4: return 0.07 * suave((z - 0.6) / 0.5)
    if n.z < -0.3: return 0.13
    return 0.10

def traco(p, n):
    """tufo esculpido na pele: (comprimento, largura, densidade, direcao)"""
    q = INV(p) if p.y < -2.9 else p; x, y, z = q; ax = abs(x); s = 1 if x >= 0 else -1
    if y > 3.2: return 1.05, 0.30, 1.5, cauda_tangente(q) + n * 0.1
    if y < -3.35 and z > 6.9:
        if ax > 0.36 and y > -4.1 and z < 8.1: return 0.45, 0.16, 2.0, V((0.5 * s, 1.0, -0.5))
        if y > -4.15 and z > 8.0: return 0.28, 0.11, 1.4, V((0, 1.0, 0.25))
        return 0, 0, 0, None
    if y < -1.6 and z > 3.6: return 0.95, 0.27, 1.5, V((0.2 * s * (n.x * s > 0), 0.45, -1.0))
    if z < 3.4:
        if z < 0.42: return 0, 0, 0, None
        return (0.38, 0.14, 1.1, V((0, 0.2, -1.0))) if z > 1.0 else (0.22, 0.09, 0.9, V((0, -0.1, -1.0)))
    if n.z < -0.3 and -1.4 < y < 1.6: return 0.55, 0.20, 1.1, V((0, 0.35, -1.0))
    if y > 1.2 and n.y > 0.15 and z < 5.5: return 0.60, 0.22, 1.1, V((0, 0.5, -1.0))
    return 0.72, 0.24, 1.0, V((0.1 * s, 1.0, -0.55))

def sortear(me_, fn, total):
    pesos = []
    for f in me_.polygons:
        L, w, den, dr = fn(f.center, f.normal); pesos.append(f.area * den if L > 0 else 0.0)
    esc = total / sum(pesos); out = []
    for f, a in zip(me_.polygons, pesos):
        k = a * esc; q = int(k) + (rnd.random() < k - int(k))
        vv = [me_.vertices[i].co for i in f.vertices[:3]]
        for _ in range(q):
            u, v_ = rnd.random(), rnd.random()
            if u + v_ > 1: u, v_ = 1 - u, 1 - v_
            out.append((vv[0] + (vv[1] - vv[0]) * u + (vv[2] - vv[0]) * v_, f.normal.copy()))
    return out

def esculpir_pelo(o, total=5200):
    """subpelo inflado + tufos esculpidos (crista no meio, sulco entre tufos, ponta afinando no sentido do pelo)"""
    me_ = o.data
    for v in me_.vertices: v.co += v.normal * espessura(v.co, v.normal)
    me_.update()
    sm2 = o.modifiers.new("Liso", "SMOOTH"); sm2.factor = 0.5; sm2.iterations = 3
    bpy.ops.object.modifier_apply(modifier=sm2.name); me_ = o.data
    if total == 0: return [0.6] * len(me_.vertices)
    N = len(me_.vertices); cos = [v.co.copy() for v in me_.vertices]; nrs = [v.normal.copy() for v in me_.vertices]
    kd = kdtree.KDTree(N)
    for i, c in enumerate(cos): kd.insert(c, i)
    kd.balance()
    disp = [0.0] * N; alt = [0.0] * N; n_t = 0
    for p, n in sortear(me_, traco, total):
        L, w, den, dr = traco(p, n)
        if L <= 0: continue
        L *= rnd.uniform(0.8, 1.2); w *= rnd.uniform(0.85, 1.2)
        dr = dr.normalized() + V((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * 0.15
        d = dr - n * dr.dot(n)
        if d.length < 1e-3: continue
        d.normalize(); H = min(0.11, 0.36 * w); n_t += 1
        for co, i, _ in kd.find_range(p + d * (L * 0.5), L * 0.55 + w):
            if nrs[i].dot(n) < 0.3: continue
            r = co - p; t = r.dot(d) / L
            if t < -0.08 or t > 1.0: continue
            lat = r - d * r.dot(d); lat -= n * lat.dot(n); rl = lat.length
            tt = max(t, 0.0)
            wt = w * (0.55 + 0.45 * math.sin(math.pi * (0.2 + 0.6 * tt))) * (1 - tt) ** 0.75 + 1e-4
            if rl >= wt: continue
            prof = (1 - (rl / wt) ** 2) ** 0.7 * suave((t + 0.08) / 0.12)
            h = H * prof * (0.35 + 0.65 * (1 - tt))
            if h > disp[i]: disp[i] = h; alt[i] = prof
    for v in me_.vertices: v.co += nrs[v.index] * disp[v.index]
    me_.update()
    print("LOBO_TUFOS", n_t)
    return alt

ALT = esculpir_pelo(ob, total=0)
sm3 = ob.modifiers.new("Liso", "SMOOTH"); sm3.factor = 0.35; sm3.iterations = 1
bpy.ops.object.modifier_apply(modifier=sm3.name); me = ob.data
cor_at = me.color_attributes.new("Cor", "FLOAT_COLOR", "POINT")
mar_at = me.attributes.new("Marca", "FLOAT", "POINT")
for v in me.vertices:
    c = cor(v.co, v.normal) * (0.9 + 0.1 * noise.noise(v.co * 6))
    cor_at.data[v.index].color = (c.x, c.y, c.z, 1); mar_at.data[v.index].value = marca(v.co, v.normal)
BVH = BVHTree.FromObject(ob, bpy.context.evaluated_depsgraph_get())
PELO = pelagem(ob, total=3000)

# ------------------------------------------------------------------ orelhas, olhos, trufa, garras
def orelha(s):
    m = bpy.data.meshes.new("Orelha"); b = bmesh.new()
    base = CAB(V((0.42 * s, -3.58, 8.42))); topo = CAB(V((0.62 * s, -3.46, 9.50))); fr = V((0.30 * s, -1.0, 0.05)).normalized()
    ok, hit, nh, _ = ob.ray_cast(base + V((0, 0, 1.5)), V((0, 0, -1)))
    if ok: topo += hit - V((0, 0, 0.10)) - base; base = hit - V((0, 0, 0.10))
    lado = V((1, 0, 0)) * s; an = []
    for i in range(7):
        t = i / 6; h = lerp(base, topo, t); W = KC * (0.36 * (1 - t) ** 0.8 + 0.012); T = KC * (0.20 * (1 - t) + 0.012)
        ring = []
        for k in range(10):
            a = 2 * math.pi * k / 10; cx, cy = math.cos(a), math.sin(a)
            dep = -0.55 * T * max(0.0, -cy) * (1 - abs(cx)) * (t < 0.95)            # concha frontal
            ring.append(b.verts.new(h + lado * (W * cx) + fr * (T * cy + dep * 1.6)))
        an.append(ring)
    for i in range(6):
        for k in range(10): b.faces.new((an[i][k], an[i][(k + 1) % 10], an[i + 1][(k + 1) % 10], an[i + 1][k]))
    pt = b.verts.new(topo + V((0, 0.02, 0.06)))
    for k in range(10): b.faces.new((an[6][k], an[6][(k + 1) % 10], pt))
    b.faces.new(an[0][::-1]); b.to_mesh(m); b.free()
    o = bpy.data.objects.new("Lobo_Orelha_" + ("E" if s > 0 else "D"), m); sc.collection.objects.link(o)
    ca = m.color_attributes.new("Cor", "FLOAT_COLOR", "POINT"); ma = m.attributes.new("Marca", "FLOAT", "POINT")
    for v in m.vertices:
        frente = (v.co - lerp(base, topo, 0.5)).dot(fr) < -0.02
        c = lerp(CINZA_E, CINZA, 0.4) if not frente else lerp(CREME, CINZA, suave((v.co.z - 8.9) / 0.3) * 0.6)
        c = lerp(c, CINZA_E, suave((v.co.z - 9.15) / 0.25))
        ca.data[v.index].color = (c.x, c.y, c.z, 1); ma.data[v.index].value = 0.0
    for pl in m.polygons: pl.use_smooth = True
    o.modifiers.new("Sub", "SUBSURF").levels = 1
    return o
ORELHAS = [orelha(1), orelha(-1)]

def esfera(nome, loc, raio, esc, seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=raio, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.object; o.name = nome; o.scale = esc; bpy.ops.object.shade_smooth(); return o
OLHOS = []
for s in (1, -1):
    o = esfera("Lobo_Olho", (OLHO.x * s, OLHO.y, OLHO.z), 1.0, (0.10 * KC, 0.10 * KC, 0.10 * KC))
    o.rotation_euler = (math.radians(-8), 0, math.radians(-38 * s))   # olhar para frente-lado; local -Y = pupila
    OLHOS.append(o)
TRUFA = esfera("Lobo_Trufa", CAB(NARIZ + V((0, -0.02, 0.0))), 1.0, (0.19 * KC, 0.15 * KC, 0.13 * KC))
GARRAS = []
def tubo(pts, r0, nome):
    m = bpy.data.meshes.new(nome); o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    b = bmesh.new(); vs = [b.verts.new(p) for p in pts]
    for a, c in zip(vs, vs[1:]): b.edges.new((a, c))
    b.to_mesh(m); b.free()
    k = o.modifiers.new("Pele", "SKIN"); k.use_smooth_shade = True
    for i, dd in enumerate(m.skin_vertices[0].data):
        r = r0 * (1 - i / (len(pts) - 1)) ** 1.1 + 0.004; dd.radius = (r, r); dd.use_root = i == 0
    o.modifiers.new("Sub", "SUBSURF").levels = 1
    return o
for s in (1, -1):
    for dian in (True, False):
        for dd in dedos(s, dian):
            pta = dd[-1][0] + V((0, -0.05, -0.01))
            GARRAS.append(tubo([pta, pta + V((0, -0.09, -0.02)), pta + V((0, -0.14, -0.09))], 0.04, "Lobo_Garra"))

# ------------------------------------------------------------------ materiais
def mat(nome):
    m = bpy.data.materials.new(nome)
    if m.node_tree is None: m.use_nodes = True
    nt = m.node_tree; return m, nt, nt.nodes["Principled BSDF"], nt.links
def n_(nt, t, **kw):
    x = nt.nodes.new(t)
    for k, v in kw.items(): setattr(x, k, v)
    return x
def mat_pelo(nome, estrias):
    m, nt, b, L = mat(nome)
    ca = n_(nt, "ShaderNodeVertexColor"); ca.layer_name = "Cor"
    mk = n_(nt, "ShaderNodeAttribute"); mk.attribute_name = "Marca"
    if estrias:                                                  # fios ao longo da mecha (U atravessa, V ao longo)
        uv = n_(nt, "ShaderNodeUVMap")
        sep = n_(nt, "ShaderNodeSeparateXYZ"); L.new(uv.outputs[0], sep.inputs[0])
        cmb = n_(nt, "ShaderNodeCombineXYZ"); L.new(sep.outputs[0], cmb.inputs[0])
        mv = n_(nt, "ShaderNodeMath", operation="MULTIPLY"); mv.inputs[1].default_value = 0.08; L.new(sep.outputs[1], mv.inputs[0]); L.new(mv.outputs[0], cmb.inputs[1])
        ob_ = n_(nt, "ShaderNodeTexCoord")
        rn = n_(nt, "ShaderNodeTexNoise"); rn.inputs["Scale"].default_value = 3.0; L.new(ob_.outputs["Object"], rn.inputs["Vector"])
        sm_ = n_(nt, "ShaderNodeVectorMath", operation="ADD"); L.new(cmb.outputs[0], sm_.inputs[0]); L.new(rn.outputs["Color"], sm_.inputs[1])
        fio = n_(nt, "ShaderNodeTexNoise"); fio.inputs["Scale"].default_value = 26.0; fio.inputs["Detail"].default_value = 4
        fio.noise_dimensions = "3D"; L.new(sm_.outputs[0], fio.inputs["Vector"])
        fr = n_(nt, "ShaderNodeMapRange"); fr.inputs[1].default_value = 0.35; fr.inputs[2].default_value = 0.65
        fr.inputs[3].default_value = 0.62; fr.inputs[4].default_value = 1.12; L.new(fio.outputs["Fac"], fr.inputs[0])
        raiz = n_(nt, "ShaderNodeMapRange"); raiz.inputs[2].default_value = 0.35; raiz.inputs[3].default_value = 0.55
        L.new(sep.outputs[1], raiz.inputs[0])
        k1 = n_(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(fr.outputs[0], k1.inputs[0]); L.new(raiz.outputs[0], k1.inputs[1])
        bp = n_(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.45; bp.inputs["Distance"].default_value = 0.01
        L.new(fio.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    else:
        ob_ = n_(nt, "ShaderNodeTexCoord")
        fio = n_(nt, "ShaderNodeTexNoise"); fio.inputs["Scale"].default_value = 14.0; fio.inputs["Detail"].default_value = 5
        L.new(ob_.outputs["Object"], fio.inputs["Vector"])
        k1 = n_(nt, "ShaderNodeMapRange"); k1.inputs[3].default_value = 0.8; k1.inputs[4].default_value = 1.1; L.new(fio.outputs["Fac"], k1.inputs[0])
        bp = n_(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.01
        L.new(fio.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    mx = n_(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); mx.inputs["Factor"].default_value = 1.0
    L.new(ca.outputs["Color"], mx.inputs[6]); L.new(k1.outputs[0], mx.inputs[7])
    vm = n_(nt, "ShaderNodeMix", data_type="RGBA"); L.new(mk.outputs["Fac"], vm.inputs["Factor"])
    L.new(mx.outputs[2], vm.inputs[6]); vm.inputs[7].default_value = (VERDE.x * 0.35, VERDE.y * 0.45, VERDE.z * 0.38, 1)
    L.new(vm.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.78
    b.inputs["Emission Color"].default_value = (VERDE.x, VERDE.y, VERDE.z, 1)
    em = n_(nt, "ShaderNodeMath", operation="MULTIPLY"); em.inputs[1].default_value = 0.45; L.new(mk.outputs["Fac"], em.inputs[0])
    L.new(em.outputs[0], b.inputs["Emission Strength"])
    if "Sheen Weight" in b.inputs: b.inputs["Sheen Weight"].default_value = 0.25
    return m
def mat_olho():
    m, nt, b, L = mat("M_Lobo_Olho")
    tc = n_(nt, "ShaderNodeTexCoord"); sep = n_(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    cmb = n_(nt, "ShaderNodeCombineXYZ"); L.new(sep.outputs[0], cmb.inputs[0]); L.new(sep.outputs[2], cmb.inputs[2])
    ln = n_(nt, "ShaderNodeVectorMath", operation="LENGTH"); L.new(cmb.outputs[0], ln.inputs[0])
    rp = n_(nt, "ShaderNodeValToRGB"); L.new(ln.outputs["Value"], rp.inputs[0]); el = rp.color_ramp.elements
    el[0].position, el[0].color = 0.24, (0.01, 0.006, 0.003, 1); el[1].position, el[1].color = 0.95, (0.10, 0.05, 0.02, 1)
    e = el.new(0.30); e.color = (0.85, 0.42, 0.05, 1); e = el.new(0.72); e.color = (0.62, 0.30, 0.04, 1)
    L.new(rp.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.08
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.6
    return m
def mat_liso(nome, c, rug):
    m, nt, b, L = mat(nome); b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = rug; return m
MC, MP = mat_pelo("M_Lobo_Corpo", False), mat_pelo("M_Lobo_Mecha", True)
ob.data.materials.append(MC); PELO.data.materials.append(MP)
for o in ORELHAS: o.data.materials.append(MC)
MO = mat_olho()
for o in OLHOS: o.data.materials.append(MO)
TRUFA.data.materials.append(mat_liso("M_Lobo_Trufa", (0.015, 0.013, 0.012), 0.35))
MG = mat_liso("M_Lobo_Garra", (0.03, 0.025, 0.02), 0.4)
for o in GARRAS: o.data.materials.append(MG)

col = bpy.data.collections.new("Lobo_Ancestral_Ref"); sc.collection.children.link(col)
for o in [ob, PELO] + ORELHAS + OLHOS + [TRUFA] + GARRAS:
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o)
cern0 = max(v.co.z for v in ob.data.vertices if -1.9 < v.co.y < -1.0 and abs(v.co.x) < 0.25)
K_ESC = 6.6 / cern0                                         # oficial 5,5-7 no ombro
for o in col.objects:
    if o.type == "MESH":
        o.location *= K_ESC; o.scale *= K_ESC
        bpy.context.view_layer.objects.active = o
        for o2 in col.objects: o2.select_set(o2 is o)
        for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
print("LOBO_ESCALA", round(K_ESC, 3))
dg = bpy.context.evaluated_depsgraph_get()
tris = {o.name: sum(len(p.vertices) - 2 for p in o.evaluated_get(dg).data.polygons) for o in col.objects if o.type == "MESH"}
cern = max(v.co.z for v in ob.data.vertices if -1.9 < v.co.y < -1.0 and abs(v.co.x) < 0.25)
print("LOBO_MEDIDAS cernelha", round(cern, 2), "altura_total", round(max(v.co.z for o in ORELHAS for v in o.data.vertices), 2),
      "comprimento", round(max(v.co.y for v in ob.data.vertices) - min(v.co.y for v in ob.data.vertices), 2))
print("LOBO_TRIS corpo", tris.get("Lobo_Corpo"), "pelagem", tris.get("Lobo_Pelagem"), "total", sum(tris.values()))

# ------------------------------------------------------------------ cena de revisao (luz de mata: sol quente de tras + ceu esverdeado)
w = bpy.data.worlds.new("Ceu"); sc.world = w
if w.node_tree is None: w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.32, 0.40, 0.30, 1); bg.inputs[1].default_value = 0.4
for nome, en, cor_, rot in (("Sol", 2.4, (1.0, 0.86, 0.66), (math.radians(55), 0, math.radians(150))),
                            ("Chave", 1.5, (1.0, 0.95, 0.88), (math.radians(60), 0, math.radians(-50))),
                            ("Preench", 0.5, (0.85, 0.95, 0.85), (math.radians(75), 0, math.radians(60)))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.color = cor_; l.angle = math.radians(4); lo = bpy.data.objects.new(nome, l)
    sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=80); chao = bpy.context.object
mch = mat_liso("Chao", (0.10, 0.12, 0.06), 0.95); chao.data.materials.append(mch)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32
for k, v in (("use_raytracing", True), ("use_shadows", True)):
    if hasattr(sc.eevee, k): setattr(sc.eevee, k, v)
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
camd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", camd); sc.collection.objects.link(cam); sc.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_ref_HIGH.blend"))
if "sem_render" not in ARGS:
    ALVO = V((0, 0.0, 4.6))
    VISTAS = [("referencia", V((13.5, -15.0, 4.2)), V((0, 0.2, 4.6)), 50), ("lado", V((26, 0.0, 4.6)), ALVO, 50),
              ("frente", V((0, -26, 5.2)), V((0, 0, 4.8)), 50), ("tras", V((0, 26, 5.2)), V((0, 0, 4.6)), 50),
              ("tres_quartos", V((15, -15, 9.0)), V((0, 0, 4.4)), 50), ("cabeca", V((3.8, -9.6, 8.6)), V((0, -4.4, 8.0)), 60)]
    for nome, pos, alvo, lente in VISTAS:
        cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
        sc.render.filepath = os.path.join(OUT, "vista_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("LOBO_OK")
