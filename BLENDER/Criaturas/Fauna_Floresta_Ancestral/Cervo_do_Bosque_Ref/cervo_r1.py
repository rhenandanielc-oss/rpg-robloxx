# Revisao r1 do Cervo-do-Bosque (fauna de recurso da Floresta Ancestral).
# Derivado de cervo_blockout.py (passagem 2 preservada, nao reexecutar aquele para r1).
# Uso (segundo plano):
#   blender -b --factory-startup --python cervo_r1.py -- revisao_r1        (r1)
#   blender -b --factory-startup --python cervo_r1.py -- revisao_r2 r2     (r2: boca + olhos)
#   blender -b --factory-startup --python cervo_r1.py -- revisao_r3 r3     (r3: + nariz com narinas)
# Gera: r1_A_* (silhueta, material neutro, Workbench), r1_B_* (estudo de pelagem, EEVEE),
#       r1_Cervo_Pelo_Cor_1k.png (textura pintada por script), r1_metricas.json,
#       CR_CervoDoBosque_r1.blend (fonte editavel na colecao Fonte_Editavel).
# Escala: ombro ~1,2 u do Blender (PROPOSTA). Frente = -Y, alto = +Z, direita do animal = -X.
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
SAIDA = os.path.abspath(argv[0]); os.makedirs(SAIDA, exist_ok=True)
V = argv[1] if len(argv) > 1 else "r1"   # r1 = revisao entregue em 12/11; r2 = + boca e olhos realistas
R2 = V != "r1"
R3 = V not in ("r1", "r2")              # r3 = + nariz (rinario) com narinas
bpy.ops.wm.read_factory_settings(use_empty=True)
cena = bpy.context.scene
K = 0.0025
def P(x, y, X=0.0):
    return Vector((X, -(x - 360) * K, (845 - y) * K))
CHAO = (845 - 838) * K          # fundo do casco no desenho -> vira Z = 0
SOBE = -CHAO

# =====================================================================
# 1. CORPO: pecas (ilhas com grupo de vertices) + Remesh/Suavizar/Reduzir
# =====================================================================
bm = bmesh.new(); grupos = []
dl = bm.verts.layers.deform.verify()
def _marca(verts, nome):
    if nome not in grupos: grupos.append(nome)
    gi = grupos.index(nome)
    for v in verts: v[dl][gi] = 1.0
def _rot(r):
    return (Matrix.Rotation(math.radians(r[2]), 4, "Z") @ Matrix.Rotation(math.radians(r[1]), 4, "Y")
            @ Matrix.Rotation(math.radians(r[0]), 4, "X"))
def elip(nome, c, sx, sy, sz, rot=(0, 0, 0)):
    m = Matrix.Translation(c) @ _rot(rot) @ Matrix.Diagonal((sx, sy, sz, 1))
    _marca(bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=1.0, matrix=m)["verts"], nome)
def capsula(nome, a, b, ra, rb):
    d = b - a
    m = Matrix.Translation((a + b) / 2) @ d.normalized().to_track_quat("Z", "Y").to_matrix().to_4x4()
    _marca(bmesh.ops.create_cone(bm, cap_ends=True, segments=14, radius1=ra, radius2=rb,
                                 depth=d.length, matrix=m)["verts"], nome)
    for c, rr in ((a, ra), (b, rb)):
        _marca(bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=8, radius=rr,
                                         matrix=Matrix.Translation(c))["verts"], nome)

# tronco: dorso desce suave da cernelha (1,22) para a garupa (~1,13)
capsula("Tronco", P(185, 462), P(470, 458), 0.165, 0.20)
elip("Tronco_Garupa", P(178, 456), 0.165, 0.22, 0.165)
elip("Tronco_Barriga", P(350, 472), 0.19, 0.42, 0.19)
elip("Tronco_Peito", P(482, 452), 0.18, 0.24, 0.23)
elip("Cernelha", P(478, 394), 0.11, 0.15, 0.075, rot=(8, 0, 0))
# pescoco continuo: base larga dentro do peito, afinando ate a nuca (sem blocos empilhados)
capsula("Pescoco_Base", P(505, 428), P(572, 360), 0.20, 0.15)
capsula("Pescoco", P(572, 360), P(606, 278), 0.165, 0.115)
capsula("Pescoco_Alto", P(606, 278), P(618, 248), 0.115, 0.095)
elip("Peito_Frente", P(540, 445), 0.155, 0.15, 0.225, rot=(-28, 0, 0))   # um volume so, liga pescoco e peito
# cabeca
elip("Cranio", P(626, 246), 0.105, 0.10, 0.095)
capsula("Face", P(640, 254), P(733, 286), 0.085, 0.047)
elip("Focinho_Ponta", P(736, 290), 0.042, 0.03, 0.038)
elip("Mandibula", P(660, 285), 0.07, 0.085, 0.045, rot=(-15, 0, 0))
# cauda (tufo)
capsula("Cauda", P(128, 415), P(110, 492), 0.056, 0.044)

PES = {}
def perna(s, lado):
    X = lambda x, y, k: P(x, y, s * k)
    # dianteira
    elip(f"Escapula_{lado}", X(528, 468, 0.115), 0.07, 0.11, 0.17, rot=(25, 0, 0))
    capsula(f"Braco_{lado}", X(536, 520, 0.105), X(522, 598, 0.10), 0.088, 0.064)
    capsula(f"Antebraco_{lado}", X(522, 598, 0.10), X(504, 714, 0.095), 0.06, 0.04)
    elip(f"Carpo_{lado}", X(504, 716, 0.095), 0.041, 0.043, 0.046)
    capsula(f"Canela_D_{lado}", X(504, 716, 0.095), X(500, 796, 0.095), 0.034, 0.029)
    elip(f"Boleto_D_{lado}", X(500, 799, 0.095), 0.033, 0.037, 0.034)
    capsula(f"Quartela_D_{lado}", X(500, 800, 0.095), X(506, 815, 0.095), 0.028, 0.027)
    PES[f"D_{lado}"] = X(508, 838, 0.095)
    # traseira, com ponta do jarrete (calcaneo) para tras
    elip(f"Coxa_{lado}", X(205, 515, 0.088), 0.10, 0.15, 0.17, rot=(-28, 0, 0))
    capsula(f"Coxa_Baixa_{lado}", X(215, 540, 0.10), X(238, 585, 0.115), 0.10, 0.077)
    capsula(f"Gamba_{lado}", X(238, 585, 0.12), X(142, 698, 0.11), 0.072, 0.043)
    elip(f"Jarrete_{lado}", X(130, 694, 0.11), 0.034, 0.05, 0.05, rot=(-20, 0, 0))
    capsula(f"Canela_T_{lado}", X(142, 700, 0.11), X(150, 796, 0.11), 0.034, 0.029)
    elip(f"Boleto_T_{lado}", X(150, 799, 0.11), 0.033, 0.037, 0.034)
    capsula(f"Quartela_T_{lado}", X(150, 800, 0.11), X(156, 815, 0.11), 0.028, 0.027)
    PES[f"T_{lado}"] = X(158, 838, 0.11)
perna(1, "E"); perna(-1, "D")

me = bpy.data.meshes.new("Cervo_Pecas_r1"); bm.to_mesh(me); bm.free()
fonte = bpy.data.objects.new("Cervo_Corpo_Pecas", me)
for g in grupos: fonte.vertex_groups.new(name=g)
rm = fonte.modifiers.new("Remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.009
sm = fonte.modifiers.new("Suavizar", "SMOOTH"); sm.factor = 0.55; sm.iterations = 10
dc = fonte.modifiers.new("Reduzir", "DECIMATE"); dc.ratio = 0.10
fonte.location.z = SOBE
col_fonte = bpy.data.collections.new("Fonte_Editavel"); cena.collection.children.link(col_fonte)
col_fonte.objects.link(fonte)

# =====================================================================
# 2. GALHADA: esqueleto Skin; ramos saem para os lados e curvam para cima
# =====================================================================
gn, gr, ga, raizes = [], [], [], []
def gno(p, r):
    gn.append(Vector(p)); gr.append(r); return len(gn) - 1
def gliga(*ids):
    for a, b in zip(ids, ids[1:]): ga.append((a, b))
def galhada(s):
    v = lambda x, y, z: (s * x, y, z)
    b = [gno(v(0.040, -0.672, 1.565), 0.033),   # pedicelo (base no cranio)
         gno(v(0.110, -0.650, 1.625), 0.029),
         gno(v(0.200, -0.600, 1.690), 0.025),
         gno(v(0.290, -0.520, 1.775), 0.021),
         gno(v(0.360, -0.420, 1.880), 0.017),
         gno(v(0.395, -0.320, 1.985), 0.013),
         gno(v(0.385, -0.240, 2.070), 0.008),
         gno(v(0.355, -0.200, 2.115), 0.004)]
    raizes.append(b[0])
    gliga(*b)
    def ponta(i, *pts):
        ids = [b[i]] + [gno(p, r) for p, r in pts]; gliga(*ids)
    ponta(0, (v(0.075, -0.745, 1.640), 0.016), (v(0.085, -0.830, 1.705), 0.004))      # testa (frente)
    ponta(2, (v(0.190, -0.660, 1.800), 0.013), (v(0.180, -0.700, 1.900), 0.004))      # 2a, sobe para a frente
    ponta(3, (v(0.275, -0.580, 1.880), 0.012), (v(0.265, -0.615, 1.985), 0.004))      # 3a, sobe para a frente
    ponta(4, (v(0.405, -0.470, 1.975), 0.010), (v(0.430, -0.480, 2.060), 0.004))      # coroa, para fora
    ponta(5, (v(0.330, -0.360, 2.070), 0.009), (v(0.300, -0.380, 2.130), 0.004))      # coroa, para dentro
galhada(1); galhada(-1)
gm = bpy.data.meshes.new("Galhada_Esqueleto_r1")
gm.from_pydata([tuple(p) for p in gn], ga, [])
gfonte = bpy.data.objects.new("Cervo_Galhada_Skin", gm)
col_fonte.objects.link(gfonte)
gsk = gfonte.modifiers.new("Skin", "SKIN"); gsk.use_smooth_shade = True
for i, r in enumerate(gr):
    gm.skin_vertices[0].data[i].radius = (r, r)
    gm.skin_vertices[0].data[i].use_root = i in raizes
gss = gfonte.modifiers.new("Subdiv", "SUBSURF"); gss.levels = 1; gss.render_levels = 1
gfonte.location.z = SOBE

# =====================================================================
# 3. Pecas provisorias: orelhas, olhos, nariz, cascos fendidos
# =====================================================================
def objeto_bm(nome, bmx):
    m = bpy.data.meshes.new(nome); bmx.to_mesh(m); bmx.free()
    o = bpy.data.objects.new(nome, m); cena.collection.objects.link(o)
    for p in o.data.polygons: p.use_smooth = True
    return o

def orelha(s, lado):
    base = Vector((s * 0.090, -0.628, 1.578))
    L = Vector((s * math.cos(math.radians(26)), 0.22, math.sin(math.radians(26)))).normalized()
    T = Vector((0, -1, 0.15)); T = (T - L * T.dot(L)).normalized()   # frente da orelha
    W = L.cross(T).normalized()
    c = base + L * 0.080
    M = Matrix(((L.x * 0.086, T.x * 0.020, W.x * 0.048, c.x),
                (L.y * 0.086, T.y * 0.020, W.y * 0.048, c.y),
                (L.z * 0.086, T.z * 0.020, W.z * 0.048, c.z), (0, 0, 0, 1)))
    b2 = bmesh.new(); bmesh.ops.create_uvsphere(b2, u_segments=14, v_segments=9, radius=1.0)
    # forma de folha: ponta afinada, frente levemente concava
    for v in b2.verts:
        x, y, z = v.co
        t = (x + 1) / 2
        v.co.z = z * (0.55 + 0.75 * math.sin(math.pi * min(1, t * 1.05)) ** 0.8)
        if y > 0: v.co.y = y * (0.45 + 0.55 * abs(z))
    b2.transform(M)
    o = objeto_bm(f"Cervo_Orelha_{lado}", b2); o.location.z = SOBE
    # cor de vertice: interior claro rosado, borda e costas castanhas
    ca = o.data.color_attributes.new("Cor", "BYTE_COLOR", "POINT")
    Mi = M.inverted()
    for i, v in enumerate(o.data.vertices):
        lx, ly, lz = Mi @ v.co
        dentro = ly > -0.15 and ((lz / 1.2) ** 2 + (lx * 0.9) ** 2) < 0.62
        ca.data[i].color_srgb = (0.86, 0.73, 0.64, 1) if dentro else (0.58, 0.33, 0.18, 1)
    return o
orelhas = [orelha(1, "E"), orelha(-1, "D")]

def esfera(nome, loc, esc):
    b2 = bmesh.new()
    bmesh.ops.create_uvsphere(b2, u_segments=12, v_segments=8, radius=1.0,
                              matrix=Matrix.Translation(loc) @ Matrix.Diagonal((*esc, 1)))
    o = objeto_bm(nome, b2); o.location.z = SOBE; return o
olhos = [] if R2 else [esfera(f"Cervo_Olho_{l}", (s * 0.074, -0.782, 1.488), (0.019, 0.017, 0.017)) for s, l in ((1, "E"), (-1, "D"))]
nariz = esfera("Cervo_Nariz", (0, -0.958, 1.392), (0.032, 0.02, 0.024))

# cascos: duas pinças por pata (frustos), com a fenda entre elas
b2 = bmesh.new()
for nome, c in PES.items():
    for k in (-1, 1):
        base = Vector((c.x + k * 0.0165, c.y - 0.014, c.z))   # c.z = fundo do casco
        m = (Matrix.Translation(base + Vector((0, 0, 0.028))) @ Matrix.Rotation(math.radians(-16), 4, "X")
             @ Matrix.Diagonal((1.0, 1.6, 1.0, 1)))
        bmesh.ops.create_cone(b2, cap_ends=True, segments=10, radius1=0.0165, radius2=0.0125, depth=0.056, matrix=m)
cascos = objeto_bm("Cervo_Cascos", b2); cascos.location.z = SOBE
for p in cascos.data.polygons: p.use_smooth = False
# cascos apoiados: menor Z de cada casco vai exatamente para 0
dg = bpy.context.evaluated_depsgraph_get()
zc = min((cascos.matrix_world @ v.co).z for v in cascos.data.vertices)
for o in [fonte, gfonte, cascos, nariz] + orelhas + olhos:
    o.location.z -= zc

# =====================================================================
# 4. Malhas visiveis = copias aplicadas das fontes
# =====================================================================
dg = bpy.context.evaluated_depsgraph_get()
def aplica(obj, nome):
    m = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    o = bpy.data.objects.new(nome, m); o.matrix_world = obj.matrix_world
    cena.collection.objects.link(o)
    return o
corpo = aplica(fonte, "Cervo_Corpo")
galha = aplica(gfonte, "Cervo_Galhada")
for o in (fonte, gfonte):
    o.hide_render = True; o.hide_viewport = True
# aplica transformacao (origem no chao) para cores em espaco do mundo
for o in [corpo, galha]:
    o.data.transform(o.matrix_world); o.matrix_world = Matrix.Identity(4)
    for p in o.data.polygons: p.use_smooth = True

bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
chao = bpy.context.active_object; chao.name = "Plano_Apoio"

# =====================================================================
# 5. Cameras e render
# =====================================================================
def camera(nome, loc, rot=None, orto=None, alvo=None, lente=50):
    c = bpy.data.cameras.new(nome); o = bpy.data.objects.new(nome, c); cena.collection.objects.link(o)
    o.location = loc
    if orto: c.type = "ORTHO"; c.ortho_scale = orto
    else: c.lens = lente
    if rot: o.rotation_euler = [math.radians(a) for a in rot]
    if alvo: o.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    c.clip_end = 50
    return o
cv = [v.co for v in corpo.data.vertices]
nariz_y = min(min(v.y for v in cv), min((nariz.matrix_world @ v.co).y for v in nariz.data.vertices))
PPM = 400                      # px por unidade nas vistas ortograficas (mesmo da prancha)
JAN_Z = (-0.10, 2.15)          # janela vertical comum
cz = sum(JAN_Z) / 2; hz = JAN_Z[1] - JAN_Z[0]
VISTAS = {
    "frente": (camera("Cam_Frente", (0, -6, cz), rot=(90, 0, 0), orto=hz), (384, int(hz * PPM))),
    "lado": (camera("Cam_Lado", (-6, nariz_y + 0.9, cz), rot=(90, 0, -90), orto=hz), (800, int(hz * PPM))),
    "tres_quartos": (camera("Cam_TresQuartos", (-1.35, -2.05, 0.72), alvo=(0, -0.2, 1.02), lente=28), (700, 1024)),
    "apoios": (camera("Cam_Apoios", (-2.5, -1.1, 0.85), alvo=(0, -0.12, 0.32), lente=32), (760, 560)),
}
def render(cam, res, arquivo, transparente=True, com_chao=False):
    cena.camera = cam
    cena.render.resolution_x, cena.render.resolution_y = res
    cena.render.resolution_percentage = 100
    cena.render.film_transparent = transparente
    chao.hide_render = not com_chao
    cena.render.filepath = os.path.join(SAIDA, arquivo)
    bpy.ops.render.render(write_still=True)
cena.render.image_settings.file_format = "PNG"
cena.render.image_settings.color_mode = "RGBA"
cena.view_settings.view_transform = "Standard"
mundo = bpy.data.worlds.new("Fundo"); cena.world = mundo
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
mundo.color = lin("7d746f")
def mat(nome, cor, rug=0.5):
    m = bpy.data.materials.new(nome); m.diffuse_color = (*cor, 1); m.roughness = rug; return m
M_CHAO = mat("M_Chao", lin("6c6460"), 0.9); chao.data.materials.append(M_CHAO)

# =====================================================================
# 4b. r2: boca e olhos realistas, ajustados a superficie real da cabeca
# =====================================================================
BOCA_PTS, OLHOS_INFO, extras_r2 = [], [], []
if R2:
    from mathutils.bvhtree import BVHTree
    OFF = SOBE - zc                                  # desenho -> mundo (so Z)
    bvh = BVHTree.FromPolygons([v.co.copy() for v in corpo.data.vertices],
                               [tuple(p.vertices) for p in corpo.data.polygons])
    def na_pele(origem, direcao):
        hit = bvh.ray_cast(Vector(origem), Vector(direcao).normalized(), 1.0)
        return (hit[0], hit[1]) if hit[0] is not None else (None, None)
    def obj_bm(nome, bmx, liso=True):
        m = bpy.data.meshes.new(nome); bmx.to_mesh(m); bmx.free()
        o = bpy.data.objects.new(nome, m); cena.collection.objects.link(o)
        for p in m.polygons: p.use_smooth = liso
        return o
    # ---- boca: linha dos labios de um canto ao outro, contornando a frente do focinho ----
    # (Y, Z) no desenho; a linha fica ~1/3 acima da base do focinho e sobe um pouco no canto
    perfil = [(-0.868, 1.390), (-0.880, 1.384), (-0.898, 1.380), (-0.918, 1.378), (-0.936, 1.377), (-0.950, 1.377)]
    lados = {}
    for s in (1, -1):
        pts = []
        for yy, zz in perfil:
            h, n = na_pele((s * 0.3, yy, zz + OFF), (-s, 0, 0))
            if h is not None: pts.append(h - n * 0.0015)
        lados[s] = pts
    frente, nf = na_pele((0, -1.3, 1.377 + OFF), (0, 1, 0))
    BOCA_PTS = list(reversed(lados[1])) + ([frente - nf * 0.0015] if frente is not None else []) + lados[-1]
    cu = bpy.data.curves.new("Boca_Curva", "CURVE"); cu.dimensions = "3D"
    sp = cu.splines.new("POLY"); sp.points.add(len(BOCA_PTS) - 1)
    for i, pnt in enumerate(BOCA_PTS): sp.points[i].co = (*pnt, 1)
    cu.bevel_depth = 0.0019; cu.bevel_resolution = 1
    co_b = bpy.data.objects.new("Boca_Curva", cu); cena.collection.objects.link(co_b)
    dgb = bpy.context.evaluated_depsgraph_get()
    mb = bpy.data.meshes.new_from_object(co_b.evaluated_get(dgb))
    boca = bpy.data.objects.new("Cervo_Boca", mb); cena.collection.objects.link(boca)
    for p in mb.polygons: p.use_smooth = True
    bpy.data.objects.remove(co_b, do_unlink=True); bpy.data.curves.remove(cu)
    extras_r2.append(boca)
    # ---- olhos: globo com iris castanho-escura, pupila horizontal, cornea brilhante; palpebras escuras ----
    for s, lado in ((1, "E"), (-1, "D")):
        d = Vector((s * 0.86, -0.46, 0.12)).normalized()             # olho de presa: lateral e um pouco a frente
        guia = Vector((s * 0.074, -0.782, 1.488 + OFF))
        h, n = na_pele(guia + d * 0.25, -d)
        if h is None: h = guia
        R = 0.0185
        c = h - d * 0.0095                                            # globo afundado: so a calota aparece
        u = Vector((0, 0, 1)).cross(d).normalized(); w = d.cross(u).normalized()
        ang = math.radians(-12 * s)                                   # canto lacrimal (frente) mais baixo
        u, w = (u * math.cos(ang) + w * math.sin(ang)), (w * math.cos(ang) - u * math.sin(ang))
        B = Matrix(((u.x, w.x, d.x), (u.y, w.y, d.y), (u.z, w.z, d.z)))
        b2 = bmesh.new()
        bmesh.ops.create_uvsphere(b2, u_segments=48, v_segments=24, radius=1.0)
        for v in b2.verts: v.co = c + B @ Vector((v.co.x * R, v.co.y * R, v.co.z * R * 0.92))
        olho = obj_bm(f"Cervo_Olho_{lado}", b2)
        ca = olho.data.color_attributes.new("Cor", "BYTE_COLOR", "POINT")
        Bi = B.inverted()
        for i, v in enumerate(olho.data.vertices):
            l = Bi @ (v.co - c); l = Vector((l.x / R, l.y / R, l.z / (R * 0.92)))
            if l.z > 0.40:                                            # iris ocupa quase toda a abertura (cervideo)
                rr = math.hypot(l.x, l.y) / 0.917
                th = math.atan2(l.y, l.x)
                if (l.x / 0.34) ** 2 + (l.y / 0.12) ** 2 < 1:          # pupila horizontal
                    col = (0.03, 0.025, 0.02)
                else:
                    raio = 0.82 + 0.18 * abs(math.sin(th * 11 + 1.3) * math.sin(th * 5))
                    base = (0.27, 0.16, 0.09) if rr < 0.55 else (0.20, 0.12, 0.07)
                    k = raio * (1 - 0.55 * max(0, rr - 0.70) / 0.30)    # anel limbal escuro
                    col = tuple(min(1, ch * k) for ch in base)
            elif l.z > 0.30:
                col = (0.08, 0.05, 0.035)                              # limbo
            else:
                col = (0.62, 0.52, 0.42)                               # esclera (quase toda escondida)
            ca.data[i].color_srgb = (*col, 1)
        extras_r2.append(olho)
        # palpebras: anel amendoado escuro sobre a calota, mais fino no canto lacrimal
        a_l, b_l, tubo = 0.0198, 0.0122, 0.0030
        cc = h - d * 0.0012
        b3 = bmesh.new(); N, M = 32, 8; aneis = []
        for i in range(N):
            t = 2 * math.pi * i / N
            lacrimal = max(0, math.cos(t) * (1 if (B @ Vector((1, 0, 0))).y < 0 else -1))
            pc = cc + B @ Vector((a_l * math.cos(t), b_l * math.sin(t) * (1 - 0.28 * lacrimal), 0))
            rad = (pc - cc).normalized()
            anel = []
            for j in range(M):
                q = 2 * math.pi * j / M
                anel.append(b3.verts.new(pc + rad * (tubo * math.cos(q)) + d * (tubo * 0.8 * math.sin(q))))
            aneis.append(anel)
        for i in range(N):
            for j in range(M):
                b3.faces.new((aneis[i][j], aneis[(i + 1) % N][j], aneis[(i + 1) % N][(j + 1) % M], aneis[i][(j + 1) % M]))
        bmesh.ops.recalc_face_normals(b3, faces=b3.faces)
        extras_r2.append(obj_bm(f"Cervo_Palpebras_{lado}", b3))
        OLHOS_INFO.append((h, d, s))

# =====================================================================
# 4c. r3: nariz (rinario) umido na ponta do focinho, com narinas em virgula e sulco
# =====================================================================
if R3:
    # rinario = volume proprio embutido na ponta do focinho: o contorno nasce da intersecao
    # com a pele (liso); narinas e sulco afundam dentro do proprio volume (sem furar a pele)
    frente_n, _ = na_pele((0, -1.3, 1.392 + OFF), (0, 1, 0))
    Z0, YT = frente_n.z, frente_n.y
    AX, AY, AZ = 0.041, 0.030, 0.031
    CEN = Vector((0, YT + AY - 0.010, Z0 + 0.003))            # frente do volume 10 mm alem da ponta
    bmn = bmesh.new()
    bmesh.ops.create_uvsphere(bmn, u_segments=64, v_segments=32, radius=1.0)
    for v in bmn.verts:
        x_, y_, z_ = v.co
        z_ = z_ * (0.92 if z_ > 0 else 1.0)                    # topo um pouco achatado
        v.co = CEN + Vector((x_ * AX, y_ * AY, z_ * AZ))
    bmesh.ops.recalc_face_normals(bmn, faces=bmn.faces)
    bmn.normal_update()
    def dist_seg(p, pts):
        if len(pts) == 1: return (p - pts[0]).length
        best = 9.0
        for a_, b_ in zip(pts[:-1], pts[1:]):
            ab = b_ - a_; t = max(0, min(1, (p - a_).dot(ab) / max(ab.length_squared, 1e-12)))
            best = min(best, (p - (a_ + ab * t)).length)
        return best
    # narina em virgula: cabeca redonda junto do centro, fenda para fora/baixo contornando o lado
    narinas = []
    for s in (1, -1):
        narinas.append(([Vector((s * 0.0125, 0, Z0 - 0.0005))], 0.0072, 0.0068))
        narinas.append(([Vector((s * x_, 0, Z0 + z_)) for x_, z_ in
                         ((0.0125, -0.0005), (0.019, -0.004), (0.026, -0.008), (0.031, -0.013), (0.034, -0.019))],
                        0.0035, 0.0048))
    lab_z = BOCA_PTS[len(BOCA_PTS) // 2].z
    sulco_pts = [Vector((0, 0, Z0 - 0.007)), Vector((0, 0, lab_z - 0.004))]
    tons = []
    for v in bmn.verts:
        n = v.normal
        frontal = max(0.0, min(1.0, (-n.y - 0.05) / 0.35))    # so a face que olha para a frente/lado
        pf = Vector((v.co.x, 0, v.co.z))
        dmax = 0.0; esc = 0.0
        for pts, larg, prof in narinas:
            k = max(0.0, 1 - (dist_seg(pf, pts) / larg) ** 2)
            dmax = max(dmax, prof * k); esc = max(esc, min(1.0, k * 1.7))
        ks = max(0.0, 1 - (dist_seg(pf, sulco_pts) / 0.0030) ** 2)
        dmax = max(dmax, 0.0018 * ks)
        v.co = v.co - n * (dmax * frontal)
        tons.append((esc * frontal, ks * frontal))
    novo_nariz = obj_bm("Cervo_Nariz", bmn)
    ca = novo_nariz.data.color_attributes.new("Cor", "BYTE_COLOR", "POINT")
    for i, (esc, ks) in enumerate(tons):
        base = (0.15, 0.13, 0.12)
        ca.data[i].color_srgb = (*[b * (1 - 0.88 * esc) * (1 - 0.3 * ks) for b in base], 1)
    bpy.data.objects.remove(nariz, do_unlink=True)
    novo_nariz.name = "Cervo_Nariz"; novo_nariz.data.name = "Cervo_Nariz"
    nariz = novo_nariz
    RINARIO = (Z0, YT)

visiveis = [corpo, galha, cascos, nariz] + orelhas + olhos + extras_r2
# ---------------- Passagem A: silhueta, material neutro ----------------
cena.render.engine = "BLENDER_WORKBENCH"
sh = cena.display.shading
sh.light = "STUDIO"; sh.color_type = "SINGLE"; sh.single_color = (0.62, 0.60, 0.58)
sh.show_shadows = False; sh.show_cavity = True; sh.cavity_type = "WORLD"
for n in ("frente", "lado", "tres_quartos"):
    render(VISTAS[n][0], VISTAS[n][1], f"{V}_A_{n}.png")
sh.show_shadows = True
render(VISTAS["apoios"][0], VISTAS["apoios"][1], f"{V}_A_apoios.png", transparente=False, com_chao=True)
render(VISTAS["tres_quartos"][0], (120, 176), f"{V}_A_miniatura.png")

# =====================================================================
# 6. Passagem B: textura de pelagem pintada por script (UV + numpy)
# =====================================================================
bpy.context.view_layer.objects.active = corpo
for o in bpy.context.view_layer.objects: o.select_set(False)
corpo.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.006)
bpy.ops.object.mode_set(mode="OBJECT")

RES = 1024
me = corpo.data; me.calc_loop_triangles()
nT = len(me.loop_triangles)
lt_loops = np.zeros(nT * 3, np.int32); me.loop_triangles.foreach_get("loops", lt_loops)
lt_verts = np.zeros(nT * 3, np.int32); me.loop_triangles.foreach_get("vertices", lt_verts)
uvs = np.zeros(len(me.loops) * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", uvs)
uvs = uvs.reshape(-1, 2)
co = np.zeros(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
nv = np.zeros(len(me.vertices) * 3, np.float32); me.vertex_normals.foreach_get("vector", nv); nv = nv.reshape(-1, 3)
TU = uvs[lt_loops].reshape(-1, 3, 2) * RES
TP = co[lt_verts].reshape(-1, 3, 3); TN = nv[lt_verts].reshape(-1, 3, 3)
pix, PP, NN = [], [], []
for t in range(nT):
    a, b, c = TU[t]
    x0, y0 = np.floor(np.minimum(np.minimum(a, b), c)).astype(int)
    x1, y1 = np.ceil(np.maximum(np.maximum(a, b), c)).astype(int)
    xs, ys = np.meshgrid(np.arange(max(x0, 0), min(x1 + 1, RES)), np.arange(max(y0, 0), min(y1 + 1, RES)))
    px = np.stack([xs.ravel() + 0.5, ys.ravel() + 0.5], 1)
    v0, v1 = b - a, c - a; d = v0[0] * v1[1] - v1[0] * v0[1]
    if abs(d) < 1e-9: continue
    w = px - a
    l1 = (w[:, 0] * v1[1] - v1[0] * w[:, 1]) / d
    l2 = (v0[0] * w[:, 1] - w[:, 0] * v0[1]) / d
    l0 = 1 - l1 - l2
    ok = (l0 >= -0.02) & (l1 >= -0.02) & (l2 >= -0.02)
    if not ok.any(): continue
    L = np.stack([l0[ok], l1[ok], l2[ok]], 1)
    pix.append((xs.ravel()[ok], ys.ravel()[ok]))
    PP.append(L @ TP[t]); NN.append(L @ TN[t])
PX = np.concatenate([p[0] for p in pix]); PY = np.concatenate([p[1] for p in pix])
Pp = np.concatenate(PP); Nn = np.concatenate(NN)
Nn /= np.linalg.norm(Nn, axis=1, keepdims=True) + 1e-9
x, y, z = Pp[:, 0], Pp[:, 1], Pp[:, 2]
nx, ny, nz = Nn[:, 0], Nn[:, 1], Nn[:, 2]

def ss(v, a, b):
    t = np.clip((v - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def hx(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
def ruido(p):  # ruido de valor 3D com interpolacao suave
    pi = np.floor(p).astype(np.int64); f = p - pi; f = f * f * (3 - 2 * f)
    def h(o):
        q = pi + np.array(o)
        k = (q[:, 0] * 73856093) ^ (q[:, 1] * 19349663) ^ (q[:, 2] * 83492791)
        k = (k * 2654435761) & 0xFFFFFFFF
        return (k % 10007) / 10006.0
    r = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                r = r + w * h((dx, dy, dz))
    return r
def fbm(p, oit=3):
    s, a, t = 0, 0.5, 0
    for _ in range(oit):
        s += a * ruido(p); t += a; p = p * 2.03; a *= 0.5
    return s / t

# --- regioes anatomicas (mascaras suaves) ---
perna = ss(0.74 - z, 0, 0.10)                                   # abaixo do ventre
pescoco = ss(-0.42 - y, 0, 0.08) * ss(z, 0.95, 1.05)
tronco = (1 - perna) * (1 - pescoco)
# direcao do pelo: tronco ao longo de Y, pernas ao longo de Z, pescoco ao longo do eixo do pescoco
eixo_pesc = np.array([0, -0.38, 0.92]); eixo_pesc /= np.linalg.norm(eixo_pesc)
q_tr = np.stack([x * 230, y * 30, z * 230], 1)
q_pe = np.stack([x * 230, y * 230, z * 30], 1)
al = Pp @ eixo_pesc; perp = Pp - np.outer(al, eixo_pesc)
q_pc = np.concatenate([perp[:, :2] * 230, (al * 30)[:, None]], 1)
fios = (tronco * fbm(q_tr) + perna * fbm(q_pe) + pescoco * fbm(q_pc))
fios_largos = fbm(np.stack([x * 45, y * 9, z * 45], 1), 2)
manchas = fbm(Pp * 7.0, 4)                                       # variacao larga de tom

# --- cores base (sRGB) ---
C_CASTANHO = hx("8f4c28"); C_DORSO = hx("6a3418"); C_PERNA = hx("7a4225"); C_CANELA = hx("4c2b1a")
C_CREME = hx("d6bf98"); C_FOLHA = hx("b56a33"); C_FOLHA_B = hx("8c4a22"); C_FOCINHO = hx("4a3127")
cor = np.tile(C_CASTANHO, (len(x), 1))
dorso = ss(nz, 0.35, 0.85) * ss(z, 1.0, 1.15) * (1 - perna)
cor = cor * (1 - 0.55 * dorso[:, None]) + C_DORSO * (0.55 * dorso[:, None])
cor = cor * (1 - perna[:, None]) + (C_PERNA * (1 - ss(0.45 - z, 0, 0.25))[:, None] +
                                    C_CANELA * ss(0.45 - z, 0, 0.25)[:, None]) * perna[:, None]
# ventre e interior das coxas claros; borda com o ruido do pelo (sem serrilhado)
borda = (fios - 0.5) * 0.45 + (fios_largos - 0.5) * 0.35
ventre = ss(-nz + borda, 0.50, 0.85) * ss(z, 0.62, 0.70) * ss(0.92 - z, 0, 0.12) * ss(0.40 - y, 0, 0.12) * ss(y + 0.50, 0, 0.12)
coxa_int = ss(-nx * np.sign(x) + borda, 0.25, 0.65) * ss(y - 0.12, 0, 0.12) * ss(z, 0.45, 0.6) * ss(0.98 - z, 0, 0.1)
garganta = (ss(-ny + borda, 0.10, 0.55) * ss(0.10 - np.abs(x) + borda * 0.06, 0, 0.05) *
            ss(-0.44 - y, 0, 0.06) * ss(z, 0.70, 0.82) * ss(1.42 - z, 0, 0.06))
queixo = ss(-nz + borda, 0.2, 0.6) * ss(z, 1.30, 1.36) * ss(-0.68 - y, 0, 0.05)
cauda = ss(y - 0.60, 0, 0.03) * ss(z, 0.76, 0.84) * ss(1.06 - z, 0, 0.05) * ss(-ny * 0 + 1, 0, 1) * ss(0.09 - np.abs(x), 0, 0.03)
creme = np.clip(ventre * 0.9 + coxa_int * 0.6 + garganta * 0.92 + queixo + cauda * 1.2, 0, 1)
cor = cor * (1 - creme[:, None]) + C_CREME * creme[:, None]
# focinho escuro na ponta, olhos com aro leve mais claro
focinho = ss(-0.935 - y, 0, 0.025) * ss(z, 1.30, 1.34)
if R2:
    def dist_poli(pts):
        best = np.full(len(x), 9.0, np.float32)
        P3 = np.array([tuple(p) for p in pts], np.float32)
        for a_, b_ in zip(P3[:-1], P3[1:]):
            ab = b_ - a_; t = np.clip(((Pp - a_) @ ab) / max(float(ab @ ab), 1e-9), 0, 1)
            best = np.minimum(best, np.linalg.norm(Pp - (a_ + np.outer(t, ab)), axis=1))
        return best
    labio = 1 - ss(dist_poli(BOCA_PTS), 0.004, 0.010)       # labios escuros ao redor da linha da boca
    cor = cor * (1 - labio[:, None]) + hx("2a1c16") * labio[:, None]
    for h_, d_, s_ in OLHOS_INFO:
        e = np.array(tuple(h_), np.float32); dd = np.linalg.norm(Pp - e, axis=1)
        aro = (1 - ss(dd, 0.025, 0.037)) * ss(dd, 0.019, 0.023)        # aro claro em volta do olho
        cor = cor * (1 - 0.45 * aro[:, None]) + hx("c9a27a") * (0.45 * aro[:, None])
        # glandula pre-orbital: lagrima escura a frente e abaixo do olho
        g0 = e + np.array([-s_ * 0.003, -0.024, -0.008], np.float32)
        g1 = e + np.array([-s_ * 0.002, -0.038, -0.017], np.float32)
        gl = 1 - ss(dist_poli([g0, g1]), 0.002, 0.006)
        cor = cor * (1 - 0.45 * gl[:, None]) + hx("3a271c") * (0.45 * gl[:, None])
        sombra = (1 - ss(dd, 0.020, 0.026)) * ss(dd, 0.014, 0.018)   # sombra fina junto da palpebra
        cor *= (1 - 0.25 * sombra)[:, None]
cor = cor * (1 - focinho[:, None]) + C_FOCINHO * focinho[:, None]
# --- marcas de folhas secas pintadas no dorso/flancos altos ---
rng = np.random.default_rng(7)
cand = np.where((co[:, 2] > 0.97) & (nv[:, 2] > 0.15) & (co[:, 1] > -0.48) & (co[:, 1] < 0.58))[0]
rng.shuffle(cand); folhas = []
for i in cand:
    p = co[i]
    if all(np.linalg.norm(p - f[0]) > 0.105 for f in folhas):
        folhas.append((p, nv[i], rng.uniform(0, 2 * np.pi), rng.uniform(0.045, 0.078)))
    if len(folhas) >= 36: break
folha = np.zeros(len(x), np.float32); veio = np.zeros(len(x), np.float32)
for c0, n0, ang, R in folhas:
    d = Pp - c0
    perto = (np.abs(d @ n0) < 0.05) & (np.einsum("ij,ij->i", d, d) < (R * 1.3) ** 2)
    if not perto.any(): continue
    u = np.cross(n0, [0, 0, 1.0]);
    if np.linalg.norm(u) < 1e-3: u = np.cross(n0, [0, 1.0, 0])
    u /= np.linalg.norm(u); v = np.cross(n0, u)
    dd = d[perto]; a = dd @ u; b = dd @ v
    r = np.hypot(a, b); th = np.arctan2(b, a) - ang
    # bordo: lobo central maior, dois laterais medios, dois de baixo pequenos; borda levemente serrilhada
    lobos = (0.42 + 0.58 * np.abs(np.cos(2.5 * th)) ** 1.6) * (0.78 + 0.22 * np.cos(th))
    lobos = lobos * (1 + 0.05 * np.cos(17 * th))
    m = 1 - ss(r / R - lobos, -0.10, 0.04)
    caule = (np.abs(np.sin(th + np.pi) * r) < R * 0.04) & (np.cos(th + np.pi) * r > 0) & (r < R * 1.15)
    m = np.maximum(m, caule * 0.8)
    folha[perto] = np.maximum(folha[perto], m)
    veio[perto] = np.maximum(veio[perto], m * (1 - ss(np.abs(np.sin(5 * th) * r) / R, 0.0, 0.06)) * ss(r / R, 0.05, 0.25))
folha *= 0.55 * (0.6 + 0.8 * fios)             # integrada ao pelo: semitransparente e cortada pelos fios
cor = cor * (1 - folha[:, None]) + C_FOLHA * folha[:, None]
cor = cor * (1 - 0.35 * veio[:, None]) + C_FOLHA_B * (0.35 * veio[:, None])
# --- variacao de tom na direcao do pelo e manchas largas ---
cor *= (0.88 + 0.24 * fios)[:, None] * (0.93 + 0.14 * manchas)[:, None] * (0.95 + 0.10 * fios_largos)[:, None]
# oclusao leve nas dobras (peito/axila e virilha): escurece por proximidade do tronco
dobra = ss(0.80 - z, 0, 0.10) * ss(z, 0.55, 0.70) * (1 - creme)
cor *= (1 - 0.12 * dobra)[:, None]
cor = np.clip(cor, 0, 1)

img = np.zeros((RES, RES, 4), np.float32); cheio = np.zeros((RES, RES), bool)
img[PY, PX, :3] = cor; img[PY, PX, 3] = 1; cheio[PY, PX] = True
for _ in range(10):   # dilatacao para evitar costuras
    soma = np.zeros_like(img); cont = np.zeros((RES, RES), np.float32)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        s_img = np.roll(img, (dy, dx), (0, 1)); s_c = np.roll(cheio, (dy, dx), (0, 1))
        soma += s_img * s_c[..., None]; cont += s_c
    novo = (~cheio) & (cont > 0)
    img[novo] = soma[novo] / cont[novo][:, None]; cheio |= novo
img[~cheio] = (*C_CASTANHO, 1)
tex = bpy.data.images.new(f"{V}_Cervo_Pelo_Cor_1k", RES, RES, alpha=False)
tex.pixels.foreach_set(img.ravel())
tex.filepath_raw = os.path.join(SAIDA, f"{V}_Cervo_Pelo_Cor_1k.png"); tex.file_format = "PNG"; tex.save()

# galhada: cor de vertice da base escura para pontas claras (distancia ao pedicelo)
gca = galha.data.color_attributes.new("Cor", "BYTE_COLOR", "POINT")
bases = [Vector((s * 0.04, -0.672, 1.565 + SOBE - zc)) for s in (1, -1)]
for i, v in enumerate(galha.data.vertices):
    d = min((v.co - b).length for b in bases)
    t = min(1, max(0, (d - 0.05) / 0.42)) ** 0.9
    base, ponta = hx("4b3426"), hx("e2d3b4")
    c = base * (1 - t) + ponta * t
    gca.data[i].color_srgb = (*c, 1)

# --- materiais (Principled) ---
def principled(nome, rug, spec=0.3, cor=None, imagem=None, atributo=None, sheen=0.0, bump=0.0, coat=0.0):
    m = bpy.data.materials.new(nome); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rug
    b.inputs["Specular IOR Level"].default_value = spec
    if sheen:
        b.inputs["Sheen Weight"].default_value = sheen; b.inputs["Sheen Roughness"].default_value = 0.5
    if coat:
        b.inputs["Coat Weight"].default_value = coat; b.inputs["Coat Roughness"].default_value = 0.08
    src = None
    if imagem:
        src = nt.nodes.new("ShaderNodeTexImage"); src.image = imagem
    elif atributo:
        src = nt.nodes.new("ShaderNodeVertexColor"); src.layer_name = atributo
    if src:
        nt.links.new(src.outputs["Color"], b.inputs["Base Color"])
        if bump:
            bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
            bp.inputs["Distance"].default_value = 0.002
            nt.links.new(src.outputs["Color"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    elif cor:
        b.inputs["Base Color"].default_value = (*cor, 1)
    m.diffuse_color = (*(cor or (0.5, 0.3, 0.2)), 1)
    return m
M_PELO = principled("M_Pelo_Corpo", 0.88, 0.22, imagem=tex, sheen=0.35, bump=0.25)
M_GALHA = principled("M_Galhada", 0.55, 0.35, atributo="Cor", bump=0.0)
M_CASCO = principled("M_Casco", 0.45, 0.4, cor=lin("2b2420"))
M_NARIZ = (principled("M_Nariz_Umido", 0.34, 0.5, atributo="Cor", coat=0.12) if R3
           else principled("M_Nariz_Umido", 0.28, 0.5, cor=lin("1f1a19")))
M_OLHO = (principled("M_Olho", 0.18, 0.5, atributo="Cor", coat=1.0) if R2
          else principled("M_Olho", 0.06, 0.6, cor=lin("150d0a"), coat=0.8))
M_PALP = principled("M_Palpebra", 0.45, 0.4, cor=lin("1c1410"))
M_BOCA = principled("M_Labios", 0.40, 0.4, cor=lin("1d1512"))
for o in extras_r2:
    if "Olho" in o.name: o.data.materials.append(M_OLHO)
    elif "Palpebra" in o.name: o.data.materials.append(M_PALP)
    elif "Boca" in o.name: o.data.materials.append(M_BOCA)
M_ORELHA = principled("M_Orelha", 0.85, 0.2, atributo="Cor", sheen=0.3)
for o, m in ((corpo, M_PELO), (galha, M_GALHA), (cascos, M_CASCO), (nariz, M_NARIZ)):
    o.data.materials.clear(); o.data.materials.append(m)
for o in olhos: o.data.materials.append(M_OLHO)
for o in orelhas: o.data.materials.append(M_ORELHA)

# --- luz neutra (EEVEE) ---
motor = "BLENDER_EEVEE"
try: cena.render.engine = motor
except TypeError: cena.render.engine = motor = "BLENDER_EEVEE_NEXT"
mundo.use_nodes = True
bg = mundo.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (*lin("8a8580"), 1)
bg.inputs["Strength"].default_value = 0.9
sol_d = bpy.data.lights.new("Sol", "SUN"); sol_d.energy = 2.0; sol_d.angle = math.radians(12)
sol = bpy.data.objects.new("Sol", sol_d); cena.collection.objects.link(sol)
sol.rotation_euler = (math.radians(50), 0, math.radians(-35))
try: cena.eevee.taa_render_samples = 48
except Exception: pass
for n in ("frente", "lado", "tres_quartos"):
    render(VISTAS[n][0], VISTAS[n][1], f"{V}_B_{n}.png")
render(VISTAS["tres_quartos"][0], (120, 176), f"{V}_B_miniatura.png")
if R2:  # closes do rosto para avaliar boca e olhos
    alvo_r = Vector((0, -0.84, 1.44 + OFF))
    c34 = camera("Cam_Rosto_34", tuple(alvo_r + Vector((-0.42, -0.50, 0.06))), alvo=tuple(alvo_r), lente=60)
    clado = camera("Cam_Rosto_Lado", tuple(alvo_r + Vector((-0.75, -0.02, 0.0))), alvo=tuple(alvo_r + Vector((0, -0.02, 0))), lente=60)
    render(c34, (900, 700), f"{V}_B_rosto_34.png")
    render(clado, (900, 700), f"{V}_B_rosto_lado.png")
render(VISTAS["apoios"][0], VISTAS["apoios"][1], f"{V}_B_apoios.png", transparente=False, com_chao=True)
# arame (Workbench, malha final por cima da cor)
cena.render.engine = "BLENDER_WORKBENCH"; sh.color_type = "TEXTURE"; sh.light = "STUDIO"
fios_obj = []
M_FIO = bpy.data.materials.new("M_Fio"); M_FIO.diffuse_color = (0.02, 0.02, 0.02, 1)
for o in visiveis:
    f = o.copy(); f.data = o.data.copy(); f.name = o.name + "_FIO"; cena.collection.objects.link(f)
    w = f.modifiers.new("Fio", "WIREFRAME"); w.thickness = 0.0035; w.use_replace = True; w.use_even_offset = False
    f.data.materials.clear(); f.data.materials.append(M_FIO); fios_obj.append(f)
render(VISTAS["tres_quartos"][0], VISTAS["tres_quartos"][1], f"{V}_B_arame.png")
for f in fios_obj: bpy.data.objects.remove(f, do_unlink=True)
bpy.data.materials.remove(M_FIO)
cena.render.engine = motor

# =====================================================================
# 7. Metricas e verificacoes de apoio
# =====================================================================
dg = bpy.context.evaluated_depsgraph_get()
met = {"motor_estudo": motor, "objetos": {}, "tris_total": 0}
for o in visiveis:
    m = o.evaluated_get(dg).to_mesh()
    pts = [o.matrix_world @ v.co for v in m.vertices]
    tris = sum(len(p.vertices) - 2 for p in m.polygons)
    met["objetos"][o.name] = {"tris": tris, "dim_xyz": [round(max(p[i] for p in pts) - min(p[i] for p in pts), 3) for i in range(3)],
                              "materiais": [s.material.name for s in o.material_slots if s.material]}
    met["tris_total"] += tris
    o.evaluated_get(dg).to_mesh_clear()
apo = {}
cw = [cascos.matrix_world @ v.co for v in cascos.data.vertices]
for nome, c in PES.items():
    pts = [p for p in cw if abs(p.x - c.x) < 0.05 and abs(p.y - c.y) < 0.07]
    apo[nome] = {"min_z": round(min(p.z for p in pts), 4), "topo_z": round(max(p.z for p in pts), 4)}
met["cascos_apoio"] = apo
met["corpo_min_z"] = round(min(v.co.z for v in corpo.data.vertices), 4)
met["corpo_altura"] = round(max(v.co.z for v in corpo.data.vertices), 3)
met["cernelha_z"] = round(max(v.co.z for v in corpo.data.vertices if -0.35 < v.co.y < -0.15 and abs(v.co.x) < 0.05), 3)
met["galhada_abertura_x"] = round(max(v.co.x for v in galha.data.vertices) - min(v.co.x for v in galha.data.vertices), 3)
met["galhada_topo_z"] = round(max(v.co.z for v in galha.data.vertices), 3)
met["nariz_y"] = round(nariz_y, 3)
met["textura"] = {"arquivo": f"{V}_Cervo_Pelo_Cor_1k.png", "resolucao": RES, "folhas_pintadas": len(folhas)}
met["materiais_total"] = len([m for m in bpy.data.materials if m.users and m.name != "M_Chao"])
with open(os.path.join(SAIDA, f"{V}_metricas.json"), "w", encoding="utf-8") as fh:
    json.dump(met, fh, ensure_ascii=False, indent=1)
cena.camera = VISTAS["tres_quartos"][0]
tex.filepath = f"//{V}_Cervo_Pelo_Cor_1k.png"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SAIDA, f"CR_CervoDoBosque_{V}.blend"), relative_remap=True)
print("OK", json.dumps(met))
