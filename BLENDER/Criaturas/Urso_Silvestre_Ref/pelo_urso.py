"""CR_UrsoSilvestre — etapa 2: cartoes de pelo (mechas sobrepostas) e vegetacao (placas de casca, cipo, musgo,
samambaias, folhas) sobre o corpo da etapa 1. Texturas de tex/ (texturas_urso.py). A vegetacao e so aparencia.
Regras de movimento: nada no pescoco/cabeca alem de pelo; casca em placas separadas sobre o dorso (telhas);
cipo do ombro ate abaixo do cotovelo; tudo deforma com a pele (pesos copiados no rig).
Uso: blender -b CR_Urso_corpo.blend -P pelo_urso.py -- <saida_dir> [densidade=1.0]"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
DENS = float(next((a.split("=")[1] for a in ARGS if a.startswith("densidade=")), 1.0))
AQUI = os.path.dirname(os.path.abspath(__file__)); TEX = os.path.join(AQUI, "tex")
sc = bpy.context.scene; rnd = random.Random(23)
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
CORPO = bpy.data.objects["CR_Urso_Corpo"]; me = CORPO.data
col = bpy.data.collections["CR_Urso"]
OLHOS = [o.matrix_world.translation.copy() for o in bpy.data.objects if o.name.startswith("Olho")]
def labio_z(y): return 5.98 + 0.04 * suave((y + 9.1) / 1.6)          # igual a criar_urso_corpo.py

bm0 = bmesh.new(); bm0.from_mesh(me); bm0.faces.ensure_lookup_table()
BVH = BVHTree.FromBMesh(bm0)
def na_pele(p):
    """ponto mais proximo da pele e normal suave"""
    loc, nrm, idx, d = BVH.find_nearest(p)
    return loc, nrm
def acima(p, h):
    loc, nrm = na_pele(p); return loc + nrm * h, nrm

# ------------------------------------------------------------------ eixos das patas (para classificar regioes)
PERNAS = []
for s in (1, -1):
    PERNAS.append([V((1.55 * s, -2.90, 6.1)), V((1.80 * s, -2.55, 3.65)), V((1.78 * s, -3.15, 1.0))])
    PERNAS.append([V((1.60 * s, 4.40, 5.8)), V((1.90 * s, 3.40, 3.0)), V((1.78 * s, 4.70, 0.62))])
def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
def na_perna(p): return min(min(dist_seg(p, c[0], c[1]), dist_seg(p, c[1], c[2])) for c in PERNAS)

# ------------------------------------------------------------------ vegetacao: placas de casca primeiro (o pelo some por baixo)
PLACAS = []                                                          # (centro, raio)
def placa_alvos():
    out = []
    for y, x, a, b in ((-4.6, 0.15, 1.05, 0.70), (-3.9, -0.55, 1.35, 0.85), (-3.6, 0.75, 1.20, 0.80), (-2.9, -0.10, 1.70, 1.00),
                       (-2.2, -1.05, 1.30, 0.80), (-2.0, 0.95, 1.35, 0.85), (-1.3, 0.05, 1.50, 0.90), (-0.6, -0.85, 1.10, 0.70),
                       (-0.3, 0.80, 1.00, 0.65), (0.5, -0.15, 1.10, 0.70), (1.4, 0.55, 0.85, 0.55), (-3.2, -1.75, 1.10, 0.70),
                       (-2.6, 1.85, 1.00, 0.65), (2.4, -0.45, 0.75, 0.50)):
        out.append((V((x, y, 12.0)), V((0, 0, -1)), a * 1.30, b * 0.75))   # lascas alongadas
    # laterais dos ombros e alto do flanco (o lado direito aparece na referencia; o esquerdo e diferente, nao espelhado)
    for s, y, z, a, b in ((-1, -3.4, 7.2, 1.2, 0.7), (-1, -2.5, 6.5, 1.4, 0.8), (-1, -1.5, 7.3, 1.1, 0.7), (-1, -3.1, 5.8, 1.0, 0.6),
                          (-1, -0.6, 6.6, 0.9, 0.55), (1, -3.0, 7.0, 1.2, 0.7), (1, -1.9, 6.3, 1.2, 0.7), (1, -0.8, 7.0, 0.9, 0.6)):
        out.append((V((12.0 * s, y, z)), V((-s, 0, 0)), a * 1.3, b * 0.75))
    return out
def criar_placa(topo, dirr, a, b, ang, nome):
    hit = BVH.ray_cast(topo, dirr)
    if hit[0] is None: return None
    c = hit[0]; nrm = hit[1]
    eixo = V((math.sin(ang), math.cos(ang), 0)); eixo = (eixo - nrm * eixo.dot(nrm)).normalized(); lat = nrm.cross(eixo).normalized()
    bmp = bmesh.new(); N = 10; aneis = []
    jit = [rnd.uniform(0.58, 1.0) for _ in range(N)]                      # contorno anguloso (lasca de casca)
    for k, f in enumerate((0.0, 0.45, 0.80, 1.0)):
        anel = []
        for i in range(N if f > 0 else 1):
            th = 2 * math.pi * i / N; r = f * (jit[i] if f == 1.0 else 1.0)
            q = c + eixo * math.cos(th) * a * 0.5 * r + lat * math.sin(th) * b * 0.5 * r
            borda_tras = max(0.0, -math.cos(th)) * f                        # borda de tras (para a cauda) ergue: telha
            p, _n = acima(q, 0.46 + 0.12 * borda_tras + 0.05 * (1 - f))
            anel.append(bmp.verts.new(p))
        aneis.append(anel)
    for i in range(N): bmp.faces.new((aneis[0][0], aneis[1][i], aneis[1][(i + 1) % N]))
    for a_, b_ in zip(aneis[1:], aneis[2:]):
        for i in range(N): bmp.faces.new((a_[i], b_[i], b_[(i + 1) % N], a_[(i + 1) % N]))
    bmesh.ops.recalc_face_normals(bmp, faces=bmp.faces)
    # espessura para baixo (na direcao da pele)
    ext = bmesh.ops.extrude_face_region(bmp, geom=bmp.faces[:])
    for v in [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]: v.co -= nrm * rnd.uniform(0.22, 0.30)
    bmesh.ops.recalc_face_normals(bmp, faces=bmp.faces)
    uv = bmp.loops.layers.uv.new("UVMap"); u0, v0, u1, v1 = 0.5, 0.0, 1.0, 0.25
    ox, oy = rnd.uniform(0, 0.4), rnd.uniform(0, 0.4)
    for f in bmp.faces:
        for l in f.loops:
            d = l.vert.co - c; uu = (d.dot(lat) / 2.4 + 0.5) * 0.55 + ox; vv = (d.dot(eixo) / 2.4 + 0.5) * 0.55 + oy
            l[uv].uv = (u0 + (u1 - u0) * min(0.99, max(0.01, uu)), v0 + (v1 - v0) * min(0.99, max(0.01, vv)))
    m = bpy.data.meshes.new(nome); bmp.to_mesh(m); bmp.free()
    for p_ in m.polygons: p_.use_smooth = False
    PLACAS.append((c, max(a, b) * 0.5))
    return m
CASCA = []
for i, (topo, dirr, a, b) in enumerate(placa_alvos()):
    ang = math.radians(rnd.uniform(-30, 30) + (math.copysign(55, topo.x) if abs(topo.x) > 0.7 else 0))   # nas laterais descem pelo flanco
    if dirr.z == 0: ang = math.radians(rnd.uniform(-20, 20))                  # laterais: casca descendo o flanco
    m = criar_placa(topo, dirr, a, b, ang, "Casca_%02d" % i)
    if m: CASCA.append(m)
def juntar(meshes, nome):
    bmj = bmesh.new()
    for m in meshes: bmj.from_mesh(m)
    mj = bpy.data.meshes.new(nome); bmj.to_mesh(mj); bmj.free()
    for m in meshes: bpy.data.meshes.remove(m)
    o = bpy.data.objects.new(nome, mj); col.objects.link(o); return o
OB_CASCA = juntar(CASCA, "CR_Urso_Casca")

# ------------------------------------------------------------------ pelo
TRIS = [(t.vertices[:], t.area) for t in (me.calc_loop_triangles() or me.loop_triangles) if me.polygons[t.polygon_index].material_index == 0]
ACUM = []; s_ = 0.0
for _, a in TRIS: s_ += a; ACUM.append(s_)
AREA = s_
def amostra():
    tri = rnd.choices(TRIS, cum_weights=ACUM)[0][0]
    a, b, c = (me.vertices[i] for i in tri)
    r1, r2 = rnd.random(), rnd.random()
    if r1 + r2 > 1: r1, r2 = 1 - r1, 1 - r2
    p = a.co + (b.co - a.co) * r1 + (c.co - a.co) * r2
    n = (a.normal * (1 - r1 - r2) + b.normal * r1 + c.normal * r2).normalized()
    return p, n
def regiao(p, n):
    x, y, z = p
    if y < -6.0 and z > 4.9:
        if y < -8.45: return None                                       # ponta do focinho/nariz: pele curta (textura)
        if any((p - o).length < 0.34 for o in OLHOS): return None
        if y < -7.0 and abs(z - labio_z(y)) < 0.13: return None          # labios livres
        if n.z < -0.35 and y < -6.4: return "garganta"
        if -7.4 < y < -6.0 and abs(x) > 0.75: return "bochecha"
        if y < -7.0 and abs(x) < 0.75: return None                        # rosto: pelo curto so na textura da pele
        return "focinho" if y < -7.75 else "cabeca"
    if z < 0.16 and n.z < -0.2: return None                                # sola
    dp = na_perna(p)
    if z < 4.4 and dp < 1.9:
        if z < 0.95:
            for s in (1, -1):                                             # dedos/garras livres
                for yf in (-4.55, 2.85):
                    if abs(x - 1.82 * s) < 1.1 and y < yf + 0.55 and y > yf - 1.0 and z < 0.55: return None
            return "pe"
        return "perna_baixa" if z < 2.2 else "perna"
    if n.z < -0.45 and z < 4.6: return "barriga"
    if y > 6.4 and z > 4.6: return "cauda"
    if y < -4.2: return "pescoco"
    return "corpo"
#           comprimento     largura  tons (pesos esc/med/claro)  fluxo                 levanta  pendurado
PARAM = {"focinho":   ((0.18, 0.26), 0.22, (0.0, 0.25, 0.75), V((0, 1.0, 0.15)), 0.05, False),
         "cabeca":    ((0.30, 0.48), 0.32, (0.0, 0.45, 0.55), V((0, 1.0, -0.15)), 0.10, False),
         "bochecha":  ((0.85, 1.20), 0.55, (0.0, 0.55, 0.45), V((0.45, 1.0, -0.5)), 0.26, False),
         "garganta":  ((0.80, 1.10), 0.52, (0.10, 0.65, 0.25), V((0, 0.5, -1.0)), 0.18, False),
         "pescoco":   ((1.25, 1.75), 0.68, (0.08, 0.62, 0.30), V((0, 1.0, -0.75)), 0.30, False),
         "corpo":     ((1.05, 1.45), 0.70, (0.15, 0.70, 0.15), V((0, 1.0, -0.95)), 0.24, False),
         "barriga":   ((1.30, 1.75), 0.62, (0.45, 0.50, 0.05), V((0, 0.35, -1.0)), 0.0, True),
         "cauda":     ((0.60, 0.85), 0.50, (0.3, 0.6, 0.1), V((0, 1.0, -0.4)), 0.16, False),
         "perna":     ((1.05, 1.40), 0.66, (0.35, 0.58, 0.07), V((0, 0.15, -1.0)), 0.32, False),
         "perna_baixa": ((0.80, 1.05), 0.58, (0.65, 0.35, 0.0), V((0, 0.05, -1.0)), 0.26, False),
         "pe":        ((0.40, 0.55), 0.38, (0.80, 0.20, 0.0), V((0, -0.35, -1.0)), 0.08, False)}
ESPACO = {"focinho": 0.55, "cabeca": 0.62, "bochecha": 0.75, "garganta": 0.8}     # rosto mais denso (mechas curtas)
GRADE = {}; CEL = 0.5
def livre(p, r):
    k = (int(p.x // CEL), int(p.y // CEL), int(p.z // CEL)); rr = int(r // CEL) + 1
    for i in range(-rr, rr + 1):
        for j in range(-rr, rr + 1):
            for l in range(-rr, rr + 1):
                for q in GRADE.get((k[0] + i, k[1] + j, k[2] + l), ()):
                    if (q - p).length < r: return False
    GRADE.setdefault(k, []).append(p.copy()); return True
def sob_placa(p):
    for c, r in PLACAS:
        if (p - c).length < r * 0.95: return True
    return False
bmf = bmesh.new(); uvf = bmf.loops.layers.uv.new("UVMap")
NC, NL = 4, 3; n_mechas = 0; por_reg = {}
ALVO = int(AREA * 7.5 * DENS)
tent = 0
while n_mechas < ALVO and tent < ALVO * 30:
    tent += 1
    p, n = amostra(); reg = regiao(p, n)
    if reg is None: continue
    (l0, l1), W, tons, fluxo, lev, pend = PARAM[reg]
    if sob_placa(p) and rnd.random() < 0.92: continue
    L = rnd.uniform(l0, l1); Wl = W * rnd.uniform(0.85, 1.15)
    if not livre(p, Wl * 0.40 * ESPACO.get(reg, 1.0) / math.sqrt(DENS)): continue
    d = fluxo.copy()
    if reg in ("bochecha",): d.x *= 1 if p.x > 0 else -1
    if not pend: d = d - n * d.dot(n)
    if d.length < 1e-3: d = n.orthogonal()
    d.normalize(); d = Matrix.Rotation(math.radians(rnd.uniform(-18, 18)), 3, n) @ d
    c = rnd.randrange(NC); r = rnd.choices(range(NL), weights=tons)[0]
    # eixo da mecha seguindo a pele (sem atravessar) com altura crescente; barriga: cai livre
    anel_pts = []
    for i in range(4):
        t = i / 3
        if pend:
            q = p + n * 0.02 + d * L * t; nq = (n * 0.4 + d.cross(n.cross(d)).normalized() * 0.0).normalized() if False else n
            if t > 0: q += V((0, 0, -0.10 * L * t * t))
        else:
            q0 = p + d * L * t
            loc, nq = na_pele(q0); q = loc + nq * (0.015 + lev * L * math.sin(math.pi * 0.5 * t) + 0.04 * t)
            q += V((0, 0, -0.06 * L * t * t))                               # gravidade leve
        anel_pts.append((q, nq if not pend else n))
    vs = []
    for i, (q, nq) in enumerate(anel_pts):
        t = i / 3
        dd = (anel_pts[min(3, i + 1)][0] - anel_pts[max(0, i - 1)][0]).normalized()
        b = nq.cross(dd).normalized() if not pend else n.cross(dd).normalized()
        largura = Wl * (1.0 - 0.10 * t)
        cup = 0.10 * Wl
        anel = []
        for j, sj in enumerate((-1, 0, 1)):
            pos = q + b * largura * 0.5 * sj - nq * cup * abs(sj) * (0.6 + 0.4 * t)
            anel.append(bmf.verts.new(pos))
        vs.append(anel)
    for i in range(3):
        for j in range(2):
            f = bmf.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
            for l in f.loops:
                ii = next(k for k in range(4) if l.vert in vs[k]); jj = vs[ii].index(l.vert)
                l[uvf].uv = ((c + 0.01 + 0.98 * jj / 2) / NC, (r + 0.01 + 0.97 * ii / 3) / NL)
            f.smooth = True
    n_mechas += 1; por_reg[reg] = por_reg.get(reg, 0) + 1
mp = bpy.data.meshes.new("CR_Urso_Pelo"); bmf.to_mesh(mp); bmf.free()
OB_PELO = bpy.data.objects.new("CR_Urso_Pelo", mp); col.objects.link(OB_PELO)
print("URSO_PELO mechas", n_mechas, "area_pele %.0f" % AREA, por_reg)

# ------------------------------------------------------------------ cartoes de vegetacao
bmv = bmesh.new(); uvv = bmv.loops.layers.uv.new("UVMap")
def cartao(pontos, normais, larguras, uvbox, twist=0.0):
    """faixa ao longo de pontos (lista), largura por ponto, uvbox=(u0,v0,u1,v1) com v ao longo do comprimento"""
    u0, v0, u1, v1 = uvbox; N = len(pontos); an = []
    for i in range(N):
        dd = (pontos[min(N - 1, i + 1)] - pontos[max(0, i - 1)]).normalized()
        b = normais[i].cross(dd).normalized()
        b = Matrix.Rotation(twist * i / max(1, N - 1), 3, dd) @ b
        an.append([bmv.verts.new(pontos[i] + b * larguras[i] * 0.5 * s - normais[i] * 0.06 * larguras[i] * abs(s)) for s in (-1, 0, 1)])
    for i in range(N - 1):
        for j in range(2):
            f = bmv.faces.new((an[i][j], an[i][j + 1], an[i + 1][j + 1], an[i + 1][j])); f.smooth = True
            for l in f.loops:
                ii = next(k for k in range(N) if l.vert in an[k]); jj = an[ii].index(l.vert)
                l[uvv].uv = (u0 + (u1 - u0) * (0.02 + 0.96 * jj / 2), v0 + (v1 - v0) * (0.01 + 0.98 * ii / (N - 1)))
SAMAMBAIA = [(0.0, 0.0, 0.25, 1.0), (0.25, 0.0, 0.5, 1.0)]
FOLHA, RAMINHO, MUSGO = (0.5, 0.5, 0.75, 1.0), (0.75, 0.5, 1.0, 1.0), (0.5, 0.25, 1.0, 0.5)
n_sam = n_mus = n_fol = 0
comp_z = [7.0, 6.6, 7.3, 6.8, 6.9, 6.7]                                # z das raizes das samambaias laterais
# samambaias: nascem entre as placas do dorso e dos ombros, arqueiam para fora e caem pelo flanco
for (x, y, comp, lado_ang) in ((0.5, -4.2, 1.9, 0), (-0.9, -3.3, 2.3, 0), (1.25, -2.9, 2.1, 0), (-0.3, -2.4, 1.7, 1),
                               (-1.6, -2.7, 2.0, 0), (1.5, -1.7, 1.8, 0), (-1.25, -1.6, 2.2, 1), (0.55, -0.9, 1.6, 0),
                               (-0.6, -0.1, 1.5, 0), (1.0, 0.4, 1.3, 1), (-1.0, 1.0, 1.2, 0), (0.2, -3.7, 1.4, 1),
                               (-1.9, -3.6, 1.6, 0), (2.0, -2.3, 1.5, 0), (-0.4, -4.6, 1.6, 0), (0.9, -3.6, 2.0, 1),
                               (-1.3, -2.1, 1.9, 0), (1.7, -3.3, 1.7, 1), (-2.1, -2.9, 1.7, 1), (0.1, -1.6, 1.4, 0),
                               (-2.4, -3.0, 1.8, 2), (-2.4, -2.0, 1.6, 3), (-2.4, -3.6, 1.5, 3), (-2.4, -1.0, 1.4, 2), (2.4, -2.6, 1.6, 2), (2.4, -1.4, 1.4, 3)):
    hit = BVH.ray_cast(V((x, y, 12)), V((0, 0, -1))) if lado_ang < 2 else BVH.ray_cast(V((math.copysign(12, x), y, comp_z.pop(0))), V((-math.copysign(1, x), 0, 0)))
    lateral = lado_ang >= 2; lado_ang %= 2
    if hit[0] is None: continue
    raiz, nr = hit[0] + hit[1] * 0.42, hit[1]
    lado = V((1 if x >= 0 else -1, rnd.uniform(-0.2, 0.5), 0)).normalized()
    if abs(x) < 0.35: lado = V((1 if rnd.random() < 0.5 else -1, rnd.uniform(0, 0.4), 0)).normalized()
    if lateral: lado = V((math.copysign(0.35, x), rnd.uniform(0.1, 0.5), -1.0)).normalized()        # pende pelo flanco
    pts, nrs = [], []
    for i in range(9):
        t = i / 8
        q = raiz + (lado * 0.85 + nr * 0.50).normalized() * comp * t + V((0, 0, -0.50 * comp * t * t))
        loc, nq = na_pele(q)
        if (q - loc).dot(nq) < 0.40: q = loc + nq * 0.40                    # nunca entra no corpo
        pts.append(q); nrs.append((nq * 0.6 + V((0, 0, 1)) * 0.4).normalized())
    cartao(pts, nrs, [comp * 0.62 * math.sin(math.pi * min(1.0, 0.15 + t * 0.95)) ** 0.5 for t in [i / 8 for i in range(9)]],
           SAMAMBAIA[lado_ang], twist=math.radians(rnd.uniform(-25, 25)))
    n_sam += 1
# musgo: tufos baixos no alto do dorso, ao redor das placas, na garupa e no alto do antebraco
ZONAS_MUSGO = [((-4.8, 2.0), 1.9, 80), ((2.0, 4.8), 1.4, 22)]
for (ya, yb), xm, qt in ZONAS_MUSGO:
    for _ in range(qt):
        x, y = rnd.uniform(-xm, xm), rnd.uniform(ya, yb)
        hit = BVH.ray_cast(V((x, y, 12)), V((0, 0, -1)))
        if hit[0] is None: continue
        q0, nq = hit[0], hit[1]; dd = Matrix.Rotation(rnd.uniform(0, 6.28), 3, nq) @ nq.orthogonal().normalized()
        L = rnd.uniform(0.45, 0.85); pts, nrs = [], []
        for i in range(3):
            loc, nn = na_pele(q0 + dd * L * (i / 2 - 0.5)); pts.append(loc + nn * (0.40 + 0.10 * (i == 1))); nrs.append(nn)
        k_ = rnd.randrange(4); uu = 0.5 + 0.125 * k_
        cartao(pts, nrs, [L * rnd.uniform(0.7, 1.0)] * 3, (uu, MUSGO[1], uu + 0.125, MUSGO[3])); n_mus += 1
for _ in range(40):                                                       # alto do flanco/ombro (lateral)
    s = -1 if rnd.random() < 0.6 else 1
    hit = BVH.ray_cast(V((12 * s, rnd.uniform(-4.0, 1.0), rnd.uniform(6.0, 7.6))), V((-s, 0, 0)))
    if hit[0] is None: continue
    q0, nq = hit[0], hit[1]; dd = V((0, 0, -1)); dd = (dd - nq * dd.dot(nq)).normalized(); L = rnd.uniform(0.45, 0.8)
    pts = [na_pele(q0 + dd * L * (i / 2 - 0.5))[0] + nq * (0.40 + 0.08 * (i == 1)) for i in range(3)]
    uu = 0.5 + 0.125 * rnd.randrange(4); cartao(pts, [nq] * 3, [L * 0.9] * 3, (uu, MUSGO[1], uu + 0.125, MUSGO[3])); n_mus += 1
for s in (1, -1):                                                         # antebraco: musgo no alto, como na referencia
    for _ in range(7):
        q = V((s * rnd.uniform(2.3, 2.75), rnd.uniform(-3.7, -2.6), rnd.uniform(3.2, 4.6)))
        loc, nq = na_pele(q); dd = V((0, 0, -1)); dd = (dd - nq * dd.dot(nq)).normalized()
        pts = [loc + nq * 0.36 + dd * 0.28 * k for k in (-1, 0, 1)]; uu = 0.5 + 0.125 * rnd.randrange(4)
        cartao(pts, [nq] * 3, [0.55] * 3, (uu, MUSGO[1], uu + 0.125, MUSGO[3])); n_mus += 1
# folhas: tres grupos (garupa, ombro, alto da pata dianteira), cada lado diferente
for (cx, cy, cz, n_) in ((2.3, 3.0, 6.2, 5), (-2.3, 3.4, 6.0, 4), (-2.2, -2.2, 7.2, 4), (2.1, -2.6, 7.0, 3), (-2.55, -3.1, 4.6, 4)):
    for _ in range(n_):
        q = V((cx, cy, cz)) + V((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.5, 0.5), rnd.uniform(-0.4, 0.4)))
        loc, nq = na_pele(q); raiz = loc + nq * 0.36
        dd = (nq * 0.55 + V((0, rnd.uniform(-0.3, 0.6), -0.6)) + V((rnd.uniform(-0.3, 0.3), 0, 0))).normalized()
        L = rnd.uniform(0.45, 0.70); pts = [raiz + dd * L * t + V((0, 0, -0.12 * L * t * t)) for t in (0, 0.5, 1)]
        nrs = [(nq + V((0, 0, 0.4))).normalized()] * 3
        cartao(pts, nrs, [L * 0.55] * 3, FOLHA if rnd.random() < 0.6 else RAMINHO, twist=math.radians(rnd.uniform(-30, 30))); n_fol += 1
mv = bpy.data.meshes.new("CR_Urso_Vegetacao"); bmv.to_mesh(mv); bmv.free()
OB_VEG = bpy.data.objects.new("CR_Urso_Vegetacao", mv); col.objects.link(OB_VEG)
print("URSO_VEG samambaias", n_sam, "musgo", n_mus, "folhas", n_fol)

# ------------------------------------------------------------------ cipo/raiz: do alto do ombro ate abaixo do cotovelo (lado direito); menor no esquerdo
def cipo(guia, r0, r1, nome):
    pts = []
    for (a, b) in zip(guia, guia[1:]):
        for k in range(6): pts.append(a.lerp(b, k / 6))
    pts.append(guia[-1])
    sup = []
    for i, p in enumerate(pts):
        loc, nq = na_pele(p); sup.append(loc + nq * (0.40 - 0.10 * i / len(pts)))
    bmc = bmesh.new(); uvc = bmc.loops.layers.uv.new("UVMap"); NS = 6; an = []
    for i, p in enumerate(sup):
        dd = (sup[min(len(sup) - 1, i + 1)] - sup[max(0, i - 1)]).normalized(); a = dd.orthogonal().normalized(); b = dd.cross(a)
        r = lerp(r0, r1, i / (len(sup) - 1)) * (1 + 0.15 * math.sin(i * 1.7))
        an.append([bmc.verts.new(p + (a * math.cos(2 * math.pi * k / NS) + b * math.sin(2 * math.pi * k / NS)) * r) for k in range(NS)])
    for i in range(len(an) - 1):
        for k in range(NS):
            f = bmc.faces.new((an[i][k], an[i][(k + 1) % NS], an[i + 1][(k + 1) % NS], an[i + 1][k])); f.smooth = True
            for l in f.loops:
                ii = next(m for m in range(len(an)) if l.vert in an[m]); kk = an[ii].index(l.vert)
                l[uvc].uv = (0.5 + 0.5 * (0.05 + 0.9 * kk / NS), 0.02 + 0.2 * (ii / len(an)))
    m = bpy.data.meshes.new(nome); bmc.to_mesh(m); bmc.free(); return m
CIPOS = [cipo([V((-0.7, -3.2, 8.4)), V((-1.9, -2.9, 7.4)), V((-2.5, -3.0, 6.0)), V((-2.75, -3.3, 4.8)),
               V((-2.7, -3.55, 3.7)), V((-2.55, -3.65, 2.7))], 0.10, 0.045, "Cipo_D"),
         cipo([V((-2.5, -3.0, 6.0)), V((-2.7, -2.4, 5.6)), V((-2.85, -2.1, 4.9))], 0.05, 0.025, "Cipo_D2"),
         cipo([V((0.6, -2.4, 8.2)), V((1.8, -2.5, 7.3)), V((2.45, -2.8, 6.2)), V((2.7, -3.1, 5.1))], 0.075, 0.035, "Cipo_E")]
OB_CIPO = juntar(CIPOS, "CR_Urso_Cipo")

# ------------------------------------------------------------------ materiais com as texturas (as mesmas que vao para o Roblox)
def mat_cartao(nome, cor, normal, alfa=True, rug=0.8):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]; L = nt.links
    ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = bpy.data.images.load(os.path.join(TEX, cor)); ti.interpolation = "Cubic"
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = bpy.data.images.load(os.path.join(TEX, normal)); tn.image.colorspace_settings.name = "Non-Color"
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.8
    L.new(ti.outputs["Color"], b.inputs["Base Color"]); L.new(tn.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs[0], b.inputs["Normal"])
    if alfa: L.new(ti.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = rug
    if hasattr(m, "surface_render_method"): m.surface_render_method = "DITHERED"
    m.use_backface_culling = False
    return m
MPELO = mat_cartao("M_Urso_Pelo", "T_Urso_Pelo_Cor.png", "T_Urso_Pelo_Normal.png")
MVEG = mat_cartao("M_Urso_Vegetacao", "T_Urso_Veg_Cor.png", "T_Urso_Veg_Normal.png", rug=0.65)
MCASCA = mat_cartao("M_Urso_Casca", "T_Urso_Veg_Cor.png", "T_Urso_Veg_Normal.png", alfa=False, rug=0.9)
OB_PELO.data.materials.append(MPELO); OB_VEG.data.materials.append(MVEG)
OB_CASCA.data.materials.append(MCASCA); OB_CIPO.data.materials.append(MCASCA)
# pele por baixo do pelo: mais escura (o pelo da a cor); evita "buracos claros" entre mechas
pele = CORPO.data.materials[0]
bsdf = pele.node_tree.nodes["Principled BSDF"]
lk = bsdf.inputs["Base Color"].links[0]; src = lk.from_socket
esc = pele.node_tree.nodes.new("ShaderNodeMix"); esc.data_type = "RGBA"; esc.blend_type = "MULTIPLY"; esc.inputs["Factor"].default_value = 0.55
pele.node_tree.links.new(src, esc.inputs[6]); esc.inputs[7].default_value = (0.55, 0.50, 0.46, 1)
pele.node_tree.links.new(esc.outputs[2], bsdf.inputs["Base Color"])

dg = bpy.context.evaluated_depsgraph_get()
def tris(o): return sum(len(p.vertices) - 2 for p in o.evaluated_get(dg).data.polygons)
for o in col.objects:
    if o.type == "MESH": pass
print("URSO_TRIS", {o.name: tris(o) for o in (CORPO, OB_PELO, OB_VEG, OB_CASCA, OB_CIPO)})
zt = max(max((o.matrix_world @ v.co).z for v in o.data.vertices if -4.0 < (o.matrix_world @ v.co).y < -2.0) for o in (CORPO, OB_PELO))
print("URSO_MEDIDAS ombro_com_pelo %.2f" % zt)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Urso_master.blend"))
print("URSO_PELO_OK")
