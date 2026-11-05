"""Leao Solar adulto, etapa 1 (silhueta e massas) pela referencia principal
REFERENCIAS/planicies-douradas/leao-solar/leao-solar-referencia-principal.png (perfil, frente e traseira).
Unidade: 1 Blender = 1 stud. Frente = -Y, pes em Z=0, simetrico em X. Ombro (cernelha) = 11,5 studs (medida
tecnica de trabalho dentro da faixa oficial 10-13; nao e regra nova).
Conversao: perfil K = 11,5/360 stud/px (cernelha a 360 px do chao); frente/traseira escaladas pelo topo da juba.
Corpo e mandibula = campo de distancia (elipsoides + cones arredondados com uniao suave, build/sdf.py) -> surface nets.
Juba e tufo = nucleo arredondado do volume das 3 vistas + mechas curvas afiladas que terminam no contorno -> remesh.
Pose neutra (patas simetricas, boca fechada). Uso: blender -b --factory-startup -P 02_massas.py -- <ref_dir> <saida.blend>"""
import bpy, bmesh, sys, os, math, random
import numpy as np
from mathutils import Vector, Matrix, kdtree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sdf

ARGS = sys.argv[sys.argv.index("--") + 1:]
REF, SAIDA = os.path.abspath(ARGS[0]), os.path.abspath(ARGS[1])
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; V = Vector; rnd = random.Random(11)
def lerp(a, b, t): return a + (b - a) * t
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

K = 11.5 / 360.0                                   # perfil: stud/px
TOPO = (592 - 8) * K                               # topo da juba (18,66 studs)
KF = TOPO / (1240 - 623); KB = TOPO / (1238 - 624)  # frente / traseira
def P(x, y, X=0.0): return np.array((X, -(x - 620) * K, (592 - y) * K))   # pixel do perfil -> stud
MS = {n: np.load(os.path.join(REF, n + ".npy")) for n in ("juba_lado", "tufo_lado", "frente", "tras")}

def aplicar(ob):
    bpy.context.view_layer.objects.active = ob
    for o in sc.objects: o.select_set(o == ob)
    for m in list(ob.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
def alisar(ob, it, fator=0.5):
    sm = ob.modifiers.new("Liso", "SMOOTH"); sm.factor = fator; sm.iterations = it; aplicar(ob)
def remesh(ob, voxel, liso=2):
    rm = ob.modifiers.new("Remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = voxel; rm.use_smooth_shade = True
    aplicar(ob)
    if liso: alisar(ob, liso)
def objeto(nome, verts, faces):
    me = bpy.data.meshes.new(nome); me.from_pydata([tuple(v) for v in verts], [], [tuple(int(i) for i in f) for f in faces])
    ob = bpy.data.objects.new(nome, me); sc.collection.objects.link(ob)
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return ob
def malha_do_campo(nome, campo, liso=3):
    v, q = sdf.surface_nets(campo.F, campo.o, campo.g)
    ob = objeto(nome, v, q); alisar(ob, liso); return ob

# ------------------------------------------------------------------ corpo (pontos em px do perfil; raios em studs)
C = sdf.Campo(((-4.6, 4.6), (-16.4, 14.6), (-0.3, 17.6)), 0.07)
def EL(x, y, r, k, X=0.0, menos=False): C.elipsoide(P(x, y, X), r, k, menos)
# tronco: dorso em y~232-240, ventre ~400, peito ~468 (por baixo da juba)
for x, y, hw, hl, hh in [(428, 312, 1.85, 1.6, 2.25), (488, 320, 2.30, 2.2, 2.75), (560, 318, 2.15, 2.3, 2.62),
                         (628, 316, 2.02, 2.0, 2.52), (712, 334, 2.42, 2.6, 3.15), (808, 350, 2.62, 2.6, 3.72),
                         (898, 350, 2.35, 1.8, 3.25)]:
    EL(x, y, (hw, hl, hh), 1.1)
C.cadeia([(P(902, 325), 2.35), (P(950, 268), 2.05), (P(990, 212), 1.80)], k=0.9, k_ini=1.0)            # pescoco
# cabeca: cranio, testa, macas, focinho quadrado e almofadas dos bigodes
EL(1020, 152, (1.75, 1.75, 1.75), 0.8)
EL(1050, 136, (1.50, 1.25, 1.10), 0.5)
for s in (1, -1):
    EL(1036, 170, (1.05, 1.25, 1.0), 0.5, X=1.15 * s)                                                      # macas
    EL(1084, 176, (0.62, 0.75, 0.58), 0.35, X=0.52 * s)                                                     # bigodes
    EL(992, 94, (0.30, 0.50, 0.62), 0.25, X=1.62 * s)                                                       # orelhas
EL(1076, 160, (1.12, 1.25, 0.92), 0.5)
EL(1092, 160, (0.78, 0.72, 0.74), 0.45)
EL(1101, 150, (0.48, 0.30, 0.36), 0.15)                                                                     # trufa do nariz
for s in (1, -1):
    X = lambda v: v * s
    # dianteira: escapula, braco, triceps, antebraco, carpo, pata e dedos (cotovelo para tras)
    EL(872, 292, (0.95, 1.65, 2.5), 0.8, X=X(2.0))
    C.cadeia([(P(888, 345, X(2.0)), 1.45), (P(856, 462, X(1.86)), 1.22), (P(884, 545, X(1.76)), 0.95),
              (P(893, 566, X(1.76)), 0.88)], k=0.35, k_ini=0.6)
    EL(856, 410, (1.15, 1.5, 1.55), 0.5, X=X(1.95))
    EL(862, 488, (1.05, 1.1, 1.05), 0.4, X=X(1.84))
    EL(902, 575, (1.40, 1.55, 0.56), 0.35, X=X(1.76))
    for dx in (-1.02, -0.36, 0.36, 1.02):
        EL(931, 577, (0.42, 0.55, 0.47), 0.18, X=X(1.76 + dx))
    # traseira: coxa (pernil), joelho para frente, gastrocnemio, jarrete para tras, metatarso, pata e dedos
    EL(486, 362, (1.40, 2.45, 2.65), 0.9, X=X(2.05))
    C.cadeia([(P(500, 330, X(2.0)), 1.6), (P(540, 442, X(2.1)), 1.18), (P(470, 512, X(2.12)), 0.78),
              (P(482, 558, X(2.18)), 0.76)], k=0.35, k_ini=0.6)
    EL(516, 466, (0.98, 1.25, 1.05), 0.4, X=X(2.1))
    EL(500, 576, (1.34, 1.50, 0.56), 0.35, X=X(2.2))
    for dx in (-0.92, -0.32, 0.32, 0.92):
        EL(527, 577, (0.42, 0.52, 0.45), 0.18, X=X(2.2 + dx))
CAUDA = [(420, 284, 0.62), (392, 314, 0.55), (360, 352, 0.48), (328, 393, 0.44), (292, 426, 0.42), (256, 445, 0.40),
         (222, 452, 0.38), (196, 455, 0.36)]
C.cadeia([(P(x, y), r) for x, y, r in CAUDA], k=0.2, k_ini=0.6)
corpo = malha_do_campo("Leao_Corpo", C, 3)

# mandibula separavel (boca fechada; pivo na articulacao temporo-mandibular)
CM = sdf.Campo(((-1.6, 1.6), (-15.9, -12.0), (11.2, 13.6)), 0.05)
for s in (1, -1):
    CM.cadeia([(P(1018, 190, 0.95 * s), 0.46), (P(1060, 204, 0.62 * s), 0.40), (P(1086, 208, 0.40 * s), 0.34)], k=0.3)
CM.elipsoide(P(1052, 204), (0.85, 1.25, 0.38), 0.35)
CM.elipsoide(P(1090, 209), (0.62, 0.42, 0.38), 0.3)
mand = malha_do_campo("Leao_Mandibula", CM, 2)
ATM = V(P(1018, 184)); mand.data.transform(Matrix.Translation(-ATM)); mand.location = ATM

# ------------------------------------------------------------------ cores (sRGB 0-255)
def corv(rgb): return tuple(c / 255 for c in rgb) + (1.0,)
def pintar(ob, f):
    me = ob.data; mw = ob.matrix_world
    at = me.color_attributes.new("Cor", "BYTE_COLOR", "POINT"); me.color_attributes.active_color = at
    for i, v in enumerate(me.vertices): at.data[i].color_srgb = corv(f(mw @ v.co))
PAL_JUBA = [(0.0, (100, 32, 13)), (0.28, (160, 55, 18)), (0.52, (218, 108, 26)), (0.78, (243, 166, 42)), (1.0, (252, 214, 104))]
def paleta(t, pal=PAL_JUBA):
    t = max(0.0, min(1.0, t))
    for (a, ca), (b, cb) in zip(pal, pal[1:]):
        if t <= b: u = (t - a) / (b - a); return tuple(lerp(ca[i], cb[i], u) for i in range(3))
    return pal[-1][1]
def mistura(c, d, t): return tuple(lerp(c[i], d[i], t) for i in range(3))
Y_FOC = P(1064, 0)[1]; Y_NARIZ = P(1093, 0)[1]
def cor_corpo(p):
    x, y, z = p
    c = (198, 128, 64)
    c = mistura(c, (182, 114, 54), suave((z - 9.8) / 1.8))                                       # dorso
    c = mistura(c, (224, 172, 112), suave((7.4 - z) / 1.4) * (1 - suave((abs(x) - 1.3) / 1.0)) * (z > 3.5))  # ventre
    c = mistura(c, (226, 178, 122), suave((1.3 - z) / 0.9))                                      # patas
    if y < Y_FOC + 0.5:                                                                            # focinho claro
        c = mistura(c, (238, 214, 174), suave((Y_FOC + 0.5 - y) / 0.7) * suave((14.5 - z) / 0.5))
    if y < Y_NARIZ and z > 13.95 and abs(x) < 0.5 * suave((z - 13.85) / 0.45): c = (66, 40, 34)                              # nariz
    return c
pintar(corpo, cor_corpo)
pintar(mand, lambda p: (236, 212, 172) if p[1] < Y_FOC + 0.3 else (226, 186, 134))
def elipsoide_obj(nome, c, r, cor):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=c)
    o = bpy.context.object; o.name = nome; o.scale = r
    bpy.ops.object.transform_apply(scale=True); o.data.name = nome
    pintar(o, lambda p: cor); return o
olhos = []
for s in (1, -1):
    org = V(P(1160, 131, 1.02 * s)); ok, hit, nrm, _ = corpo.ray_cast(org, V((0.12 * s, 1, 0)).normalized())
    c = hit - nrm * 0.07 if ok else V(P(1044, 130, 1.02 * s))
    olhos.append(elipsoide_obj("Leao_Olho_" + ("L" if s > 0 else "R"), c, (0.25, 0.17, 0.19), (222, 150, 40)))

# ------------------------------------------------------------------ juba e tufo
def blur(a, r):
    for ax in range(3):
        c = np.cumsum(np.pad(a, [(r + 1, r) if i == ax else (0, 0) for i in range(3)]), axis=ax)
        hi = [slice(None)] * 3; lo = [slice(None)] * 3
        hi[ax] = slice(2 * r + 1, None); lo[ax] = slice(0, -2 * r - 1)
        a = (c[tuple(hi)] - c[tuple(lo)]) / (2 * r + 1)
    return a
def amostra(mask, xs, ys):
    xs = np.clip(np.round(xs).astype(int), 0, mask.shape[1] - 1); ys = np.clip(np.round(ys).astype(int), 0, mask.shape[0] - 1)
    return mask[ys, xs]
MEIA_FRENTE = np.array([(np.nonzero(r)[0].max() - 335) * KF if r.any() else 0.0 for r in MS["frente"]])
def colunas(mask):
    """por coluna do perfil: centro e meia altura (em studs) da mascara"""
    zc = np.zeros(mask.shape[1]); hz = np.zeros(mask.shape[1])
    for x in range(mask.shape[1]):
        ys = np.nonzero(mask[:, x])[0]
        if len(ys): zc[x] = (592 - (ys.min() + ys.max()) / 2) * K; hz[x] = (ys.max() - ys.min()) / 2 * K
    return zc, hz
COL = {n: colunas(MS[n]) for n in ("juba_lado", "tufo_lado")}
ROSTO_C, ROSTO_R = P(1066, 150), np.array((2.85, 2.3, 2.6))          # zona do rosto livre de juba
def no_rosto(p, folga=0.0):
    d = (np.asarray(p) - ROSTO_C) / (ROSTO_R + folga)
    return (d @ d) < 1.0 and p[1] < ROSTO_C[1] + 1.25
def volume(lado, g, lim, larg_max, expo):
    (x0, x1), (y0, y1), (z0, z1) = lim
    X, Y, Z = np.meshgrid(np.arange(x0, x1, g), np.arange(y0, y1, g), np.arange(z0, z1, g), indexing="ij")
    xs = 620 - Y / K; ys = 592 - Z / K
    occ = amostra(MS[lado], xs, ys)
    occ &= amostra(MS["frente"], 335 + X / KF, 1240 - Z / KF) & amostra(MS["tras"], 875 - X / KB, 1238 - Z / KB)
    zc, hz = COL[lado]; xi = np.clip(np.round(xs).astype(int), 0, len(zc) - 1)
    dz = np.abs(Z - zc[xi]) / np.maximum(hz[xi], 1e-3)
    W = larg_max(X, Y, Z, xs)
    occ &= np.abs(X) <= W * np.clip(1 - dz ** expo, 0, 1) ** (1 / expo)      # secao superelipse (sem paredes retas)
    if lado == "juba_lado":
        d = ((X - ROSTO_C[0]) / ROSTO_R[0]) ** 2 + ((Y - ROSTO_C[1]) / ROSTO_R[1]) ** 2 + ((Z - ROSTO_C[2]) / ROSTO_R[2]) ** 2
        occ &= ~((d < 1) & (Y < ROSTO_C[1] + 1.25))
        for s in (1, -1):
            o = P(992, 94, 1.62 * s); occ &= ((X - o[0]) ** 2 + (Y - o[1]) ** 2 + (Z - o[2]) ** 2) > 0.75 ** 2
    return X, Y, Z, occ.astype(float)
def larg_juba(X, Y, Z, xs):
    hf = MEIA_FRENTE[np.clip(np.round(1240 - Z / KF).astype(int), 0, len(MEIA_FRENTE) - 1)]
    t = np.clip(0.45 + 0.55 * (xs - 650) / 260, 0.45, 1.0)
    return np.maximum(hf * t, np.clip(2.9 + 0.5 * (xs - 650) / 80, 2.9, 3.4))
def larg_tufo(X, Y, Z, xs): return np.full_like(X, 1.0)

def juba_volume(nome, lado, g, lim, larg, expo, fluxo, esp_min, comp, larg0, voxel, tipo, limiar=0.58, nucleo=0.82, ponta=0.6):
    global PONTA; PONTA = ponta
    X, Y, Z, occ = volume(lado, g, lim, larg, expo)
    occ = (blur(occ, 1) > limiar).astype(float)
    sm = blur(occ, 1)
    borda = (occ > 0.5) & (sm < 0.92)
    gx, gy, gz = np.gradient(blur(occ, 2))
    pts = np.argwhere(borda & (X >= -0.01)).tolist(); rnd.shuffle(pts)
    kd = kdtree.KDTree(len(pts))
    for i, p in enumerate(pts): kd.insert((X[tuple(p)], Y[tuple(p)], Z[tuple(p)]), i)
    kd.balance(); usado = np.zeros(len(pts), bool); aceitos = []
    for i, p in enumerate(pts):
        if usado[i]: continue
        co = V((X[tuple(p)], Y[tuple(p)], Z[tuple(p)]))
        for _, j, _ in kd.find_range(co, esp_min): usado[j] = True
        nv = -V((gx[tuple(p)], gy[tuple(p)], gz[tuple(p)]))
        if nv.length > 1e-6: aceitos.append((co, nv.normalized()))
    # nuvem da superficie (os dois lados) para as mechas seguirem o volume como linhas de fluxo
    sup = np.argwhere(borda); SP, SN = [], []
    for q_ in sup:
        q_ = tuple(q_); nv = -V((gx[q_], gy[q_], gz[q_]))
        SP.append(V((X[q_], Y[q_], Z[q_]))); SN.append(nv.normalized() if nv.length > 1e-6 else V((0, 0, 1)))
    kds = kdtree.KDTree(len(SP))
    for i, q_ in enumerate(SP): kds.insert(q_, i)
    kds.balance()
    def superficie(p):
        r = kds.find_n(p, 6)
        return sum((SP[i] for _, i, _ in r), V()) / len(r), sum((SN[i] for _, i, _ in r), V()).normalized()
    def tangente(p, n):
        F = fluxo(p); Ft = F - n * n.dot(F)
        if Ft.length < 0.2: Ft = V((0, 1, 0)) - n * n.y
        return Ft.normalized()
    EIXO = TUFO_B - TUFO_A
    def u_tufo(p): return (p - TUFO_A).dot(EIXO) / EIXO.length_squared
    def linha_fluxo(c, L, passo=0.25):
        """caminha CONTRA o fluxo a partir da ponta c, sempre projetando na superficie; devolve raiz -> ponta"""
        s_, n = superficie(c); cam = [(s_, n)]; p = s_
        for _ in range(int(L / passo)):
            p = p - tangente(p, n) * passo
            if tipo == "juba" and Y_BOCHECHA_Z[0] < p.z < Y_BOCHECHA_Z[1] and p.y < Y_BOCHECHA: break
            if tipo == "tufo" and u_tufo(p) < 0.04: break
            s_, n = superficie(p)
            if (s_ - p).length > 0.8: break
            p = s_; cam.append((s_, n))
        return cam[::-1]
    verts, faces, linha = [], [], []
    def mecha(cam, w0, val, prof, lift):
        if len(cam) < 4: return False
        pts_ = [q_ for q_, _ in cam]; ns = [n for _, n in cam]
        for _ in range(3): pts_ = [pts_[0]] + [(pts_[i - 1] + pts_[i] * 2 + pts_[i + 1]) / 4 for i in range(1, len(pts_) - 1)] + [pts_[-1]]
        M = len(pts_) - 1
        cl = [pts_[i] - ns[i] * (prof * (1 - i / M) ** 1.2) + ns[i] * (lift * (i / M) ** 3) for i in range(M + 1)]
        dfim = (cl[-1] - cl[-2]).normalized(); cl.append(cl[-1] + dfim * PONTA + ns[-1] * lift * 0.4); ns = ns + [ns[-1]]
        if tipo == "juba" and any(no_rosto(q_, 0.1) for q_ in cl): return False
        N, RING = len(cl) - 1, 8; base = len(verts)
        for k, q_ in enumerate(cl):
            t = k / N
            if k == N: verts.append(tuple(q_)); continue
            d = (cl[k + 1] - q_).normalized()
            a = d.cross(ns[k]); a = a.normalized() if a.length > 1e-6 else V((1, 0, 0)); b = a.cross(d)
            w = w0 * (1 - t) ** 0.9 * (1 + 0.3 * math.sin(math.pi * min(1.0, t * 1.5))) + 0.01; h = 0.8 * w
            for j in range(RING):
                ang = 2 * math.pi * j / RING
                verts.append(tuple(q_ + a * (w * math.cos(ang)) + b * (h * math.sin(ang))))
            linha.append((q_, min(1.0, val + 0.32 * t)))
        for k in range(N - 1):
            for j in range(RING):
                a0 = base + k * RING + j; a1 = base + k * RING + (j + 1) % RING
                faces.append((a0, a1, a1 + RING, a0 + RING))
        tip = base + N * RING
        for j in range(RING): faces.append((base + (N - 1) * RING + j, base + (N - 1) * RING + (j + 1) % RING, tip))
        faces.append(tuple(base + j for j in reversed(range(RING))))
        return True
    feitas = 0
    for co, nv in aceitos:
        for s in ((1, -1) if co.x > 0.2 else (1,)):
            c = V((co.x * s, co.y, co.z))
            if tipo == "juba":
                L = comp * rnd.uniform(0.8, 1.25) * (1 + 0.2 * suave((c.z - 12) / 5))
                h = suave((c.z - 6.0) / 12.0); fr = suave((-c.y - 9.5) / 5.0)
                val = 0.08 + 0.58 * h + 0.26 * fr + rnd.uniform(-0.08, 0.08)
                feitas += mecha(linha_fluxo(c, L), larg0 * rnd.uniform(0.8, 1.2), val, prof=0.55, lift=rnd.uniform(0.12, 0.24))
            else:
                if u_tufo(c) < 0.3: continue
                val = 0.40 + 0.30 * suave((c.z - 2.0) / 3.5) + rnd.uniform(-0.08, 0.08)
                feitas += mecha(linha_fluxo(c, comp * 4, 0.15), larg0 * rnd.uniform(0.8, 1.2), val, prof=0.22, lift=0.08)
    # nucleo arredondado: surface nets do volume suavizado, recuado para dentro das mechas
    nuc = blur(occ, 2)
    v, q = sdf.surface_nets(nucleo - nuc, np.array((X[0, 0, 0], Y[0, 0, 0], Z[0, 0, 0])), g)
    v = np.asarray(v); base = len(verts)
    verts += [tuple(x) for x in v]; faces += [tuple(int(i) + base for i in f) for f in q]
    ob = objeto(nome, verts, faces)
    print(nome, "mechas", feitas, "pontos", len(aceitos))
    remesh(ob, voxel, 2)
    kd2 = kdtree.KDTree(len(linha))
    for i, (p, val) in enumerate(linha): kd2.insert(p, i)
    kd2.balance()
    def cor(p):
        _, i, d = kd2.find(V(p))
        return paleta(linha[i][1] - 0.35 * suave((d - 0.3) / 0.6))          # fundo entre mechas = cobre escuro
    pintar(ob, cor)
    return ob

PONTA = 0.6
CF = V(P(1048, 150))
Y_BOCHECHA, Y_BOCHECHA_Z = P(1040, 0)[1], (P(0, 250)[2], P(0, 92)[2])     # linha das bochechas no perfil
TUFO_A, TUFO_B = V(P(200, 455)), V(P(64, 520))                             # eixo do tufo (raiz -> ponta)
def fluxo_juba(c): return (c - CF).normalized() + V((0, 0.55, 0)) + V((0, 0, -0.32 if c.z < 10.5 else 0.10))
FIM_CAUDA = V(P(200, 455))
def fluxo_tufo(c): return (TUFO_B - TUFO_A).normalized() + (c - FIM_CAUDA).normalized() * 0.25
juba = juba_volume("Leao_Juba", "juba_lado", 0.2, ((-6.5, 6.5), (-16.4, 1.2), (2.0, 19.6)), larg_juba, 3.0, fluxo_juba,
                   esp_min=0.88, comp=3.7, larg0=0.86, voxel=0.08, tipo="juba", ponta=0.5)
tufo = juba_volume("Leao_Cauda_Tufo", "tufo_lado", 0.1, ((-1.4, 1.4), (12.2, 18.6), (0.6, 6.6)), larg_tufo, 2.0, fluxo_tufo,
                   esp_min=0.32, comp=1.3, larg0=0.42, voxel=0.05, tipo="tufo", limiar=0.45, nucleo=0.75, ponta=0.4)

# ------------------------------------------------------------------ materiais (cor por atributo), colecao e medidas
def material(nome):
    m = bpy.data.materials.new(nome); nt = m.node_tree if m.node_tree else None
    if nt is None: m.use_nodes = True; nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    at = nt.nodes.new("ShaderNodeVertexColor"); at.layer_name = "Cor"
    nt.links.new(at.outputs["Color"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.85
    return m
for o, mn in ((corpo, "M_Leao_Pelo"), (mand, "M_Leao_Pelo"), (juba, "M_Leao_Juba"), (tufo, "M_Leao_Juba"),
              (olhos[0], "M_Leao_Olho"), (olhos[1], "M_Leao_Olho")):
    o.data.materials.append(bpy.data.materials.get(mn) or material(mn))
col = bpy.data.collections.new("CR_Leao_Solar_E1"); sc.collection.children.link(col)
for o in list(sc.collection.objects): sc.collection.objects.unlink(o); col.objects.link(o)
tris = 0
for o in col.objects:
    t = sum(len(p.vertices) - 2 for p in o.data.polygons); tris += t
    bb = [o.matrix_world @ V(c) for c in o.bound_box]
    print("OBJ", o.name, "tris", t, "X", round(min(b.x for b in bb), 2), round(max(b.x for b in bb), 2),
          "Y", round(min(b.y for b in bb), 2), round(max(b.y for b in bb), 2), "Z", round(min(b.z for b in bb), 2), round(max(b.z for b in bb), 2))
zs = [v.co.z for v in corpo.data.vertices]
cern = max(v.co.z for v in corpo.data.vertices if abs(v.co.y - P(860, 0)[1]) < 0.3 and abs(v.co.x) < 0.3)
print("TRIS_TOTAL", tris, "PE_Z", round(min(zs), 3), "CERNELHA_Z", round(cern, 2), "TOPO_JUBA", round(max(v.co.z for v in juba.data.vertices), 2))
bpy.ops.wm.save_as_mainfile(filepath=SAIDA)
