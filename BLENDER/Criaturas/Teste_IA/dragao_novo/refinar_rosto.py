"""Refino do rosto do CR_Dragao SOBRE o rig atual (CR_Dragao_M2M.blend), sem mudar esqueleto, UV do corpo nem clipes:
1. Boca real: separa os labios (corta as faces que cruzam a linha da boca), a mandibula de baixo passa a seguir 100% o
   osso mouth_lower; cavidade (palato + assoalho + garganta + bochechas), gengiva, lingua e dentes nos ossos da boca.
2. Olho: troca a esfera pintada por globo com iris ambar, pupila em fenda, anel escuro e brilho umido + palpebras.
3. Rosto: arco da sobrancelha mais saliente sobre o olho, narinas mais abertas, linha da mandibula marcada.
As pecas novas ficam numa malha propria "Silverwing_Detalhes" (1 material, atlas 1024 gerado aqui) para nao passar
de 20k tris por MeshPart no Roblox. Uso: blender -b CR_Dragao_M2M.blend -P refinar_rosto.py -- <pasta_saida_atlas>"""
import bpy, bmesh, sys, os, math, random
import numpy as np
from mathutils import Vector as V, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
assert not bpy.data.objects.get("Silverwing_Detalhes"), "ja refinado (rode sobre o rig sem detalhes)"
for pb in A.pose.bones: pb.matrix_basis = Matrix.Identity(4)
if A.animation_data: A.animation_data.action = None
rnd = random.Random(3)
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
me = M.data
# ------------------------------------------------------------------ geometria da boca (espaco do rig)
def z_boca(y): return 0.531 + 0.069 * (y + 0.941)          # linha da boca (master: zb do sculpt, cabeca 1,3x, K=0,744)
Y_CANTO = -0.938                                            # canto da boca
H_LOWER = A.data.bones["mouth_lower"].head_local.copy()     # dobradica da mandibula
def raio(o, d):
    ok, p, n, i = M.ray_cast(o, d, distance=1.0); return (p, n) if ok else (None, None)
ponta, _ = raio(V((0, -1.4, z_boca(-1.1))), V((0, 1, 0)))
Y_PONTA = ponta.y
print("BOCA ponta y %.3f canto %.3f" % (Y_PONTA, Y_CANTO))
def borda(y, cima):                                         # meia-largura do labio (antes do corte)
    z = z_boca(y) + (0.006 if cima else -0.006)
    p, n = raio(V((0.3, y, z)), V((-1, 0, 0)))
    return (p.x if p else 0.004)
YS = [lerp(Y_PONTA + 0.004, Y_CANTO, i / 11) for i in range(12)]
LARG = {y: max(0.004, min(borda(y, True), borda(y, False)) - 0.004) for y in YS}

# ------------------------------------------------------------------ 1a. corpo: mandibula separada + pesos
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
dl = bm.verts.layers.deform.active
gi = {g.name: g.index for g in M.vertex_groups}
def na_mandibula(p): return p.y < Y_CANTO + 0.002 and p.z < z_boca(p.y) and p.z > 0.43
inferior = {v.index for v in bm.verts if na_mandibula(v.co)}
# faces que cruzam a linha (labios colados) sao removidas -> fenda da boca
cruz = [f for f in bm.faces if f.calc_center_median().y < Y_CANTO and 0 < sum(v.index in inferior for v in f.verts) < len(f.verts)]
bmesh.ops.delete(bm, geom=cruz, context="FACES_ONLY")
bm.verts.ensure_lookup_table()
for v in bm.verts:
    if v.is_boundary and v.co.y < Y_CANTO + 0.004:          # fecha a fenda em repouso: labios encostam na linha
        v.co.z = z_boca(v.co.y) + (-0.0012 if v.index in inferior else 0.0012)
# pesos: tudo abaixo da linha, a frente da dobradica, segue o mouth_lower (transicao suave atras do canto = bochecha)
ml = gi["mouth_lower"]
for v in bm.verts:
    p = v.co
    if p.z >= z_boca(min(p.y, Y_CANTO)) or p.z < 0.43 or p.y > H_LOWER.y + 0.03: continue
    w = 1.0 if p.y < Y_CANTO else (1 - suave((p.y - Y_CANTO) / (H_LOWER.y + 0.03 - Y_CANTO))) * 0.85
    if w <= 0.01: continue
    d = v[dl]; outros = {k: wt for k, wt in d.items() if k != ml}
    for k in list(outros): d[k] = outros[k] * (1 - w)
    d[ml] = w
# olhos antigos (esferas pintadas) saem
OLHO = V((0.0522, -0.974, 0.588))
ilhas = []
for f in bm.faces: f.tag = False
vis = set()
for v in bm.verts:
    if v.index in vis: continue
    pilha, ilha = [v], []
    while pilha:
        x = pilha.pop()
        if x.index in vis: continue
        vis.add(x.index); ilha.append(x)
        for e in x.link_edges: pilha.append(e.other_vert(x))
    ilhas.append(ilha)
olhos_velhos = [il for il in ilhas if len(il) < 400 and min(((sum((x.co for x in il), V()) / len(il)) - V((s * OLHO.x, OLHO.y, OLHO.z))).length for s in (1, -1)) < 0.02]
CENTROS = [sum((x.co for x in il), V()) / len(il) for il in olhos_velhos]
bmesh.ops.delete(bm, geom=[x for il in olhos_velhos for x in il], context="VERTS")
print("BOCA faces cortadas %d, verts mandibula %d, olhos removidos %d" % (len(cruz), len(inferior), len(olhos_velhos)))
# 3. rosto: sobrancelha saliente, narinas, linha da mandibula (desloca pela normal; UV preservada)
bm.verts.ensure_lookup_table(); bm.normal_update()
for v in bm.verts:
    p, n = v.co, v.normal
    for s in (1, -1):
        sob = V((s * 0.050, -0.966, 0.602)); d = (p - sob).length          # arco acima e a frente do olho
        if d < 0.022: v.co += n * 0.0055 * (1 - d / 0.022) ** 2
        nar = V((s * 0.0125, Y_PONTA + 0.012, z_boca(Y_PONTA) + 0.016)); d = (p - nar).length
        if d < 0.010: v.co -= n * 0.0035 * (1 - d / 0.010) ** 2           # narina mais funda
        elif d < 0.016: v.co += n * 0.0018 * (1 - (d - 0.010) / 0.006)       # aba da narina
    if Y_CANTO + 0.01 < p.y < H_LOWER.y + 0.02 and abs(p.z - (z_boca(Y_CANTO) - 0.02)) < 0.006 and abs(p.x) > 0.03:
        v.co += n * 0.002                                                   # quina da mandibula
bm.to_mesh(me); bm.free(); me.update()

# ------------------------------------------------------------------ atlas 1024 dos detalhes (cor + rugosidade)
N = 1024
cor = np.zeros((N, N, 3), np.float32); rug = np.ones((N, N), np.float32) * 0.6
yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) / N
def regiao(u0, v0, u1, v1):
    return (xx >= u0) & (xx < u1) & (yy >= v0) & (yy < v1)
# iris (u 0-0.5, v 0.5-1): ambar dourado radial, anel escuro, fenda vertical, veios
cu, cv, R = 0.25, 0.75, 0.24
dx, dy = (xx - cu) / R, (yy - cv) / R; r = np.sqrt(dx ** 2 + dy ** 2); ang = np.arctan2(dy, dx)
fibras = 0.5 + 0.5 * np.sin(ang * 48 + np.sin(ang * 7) * 2.0) * np.exp(-((r - 0.55) / 0.35) ** 2)
base = np.stack([1.0 - 0.15 * r, 0.58 - 0.38 * r, 0.04 + 0.02 * r], -1) * (0.75 + 0.35 * fibras[..., None])
base[r > 0.82] *= np.clip(1 - (r[r > 0.82] - 0.82) / 0.1, 0.15, 1)[..., None] * np.array([0.55, 0.35, 0.2])  # anel limbal
fenda = (np.abs(dx) < 0.11 * np.sqrt(np.clip(1 - dy ** 2, 0, 1))) & (r < 0.95)
base[fenda] = [0.015, 0.008, 0.005]
borda_fenda = (np.abs(dx) < 0.16 * np.sqrt(np.clip(1 - dy ** 2, 0, 1))) & ~fenda & (r < 0.95)
base[borda_fenda] *= 0.55
fora = r > 1.0; base[fora] = [0.55, 0.32, 0.12]                      # esclera ambar escura (reptil)
m = regiao(0, 0.5, 0.5, 1); cor[m] = base[m]; rug[m] = 0.08
# cavidade (u 0.5-1, v 0.5-1): gengiva rosada nos labios -> vermelho profundo -> garganta escura
t = (yy - 0.5) / 0.5
cav = np.stack([0.78 - 0.45 * t, 0.26 - 0.20 * t, 0.24 - 0.18 * t], -1)
ruido = np.random.default_rng(1).random((N, N)).astype(np.float32)
cav *= (0.88 + 0.24 * ruido[..., None])
m = regiao(0.5, 0.5, 1, 1); cor[m] = cav[m]; rug[m] = 0.22
# lingua (u 0-0.5, v 0-0.5): vermelho-rosado com sulco central
lt = np.abs(xx - 0.25) / 0.25
ling = np.stack([0.62 - 0.2 * lt, 0.12 + 0.02 * lt, 0.12 + 0 * lt], -1) * (0.85 + 0.2 * ruido[..., None])
ling[np.abs(xx - 0.25) < 0.012] *= 0.6
m = regiao(0, 0, 0.5, 0.5); cor[m] = ling[m]; rug[m] = 0.25
# dentes (u 0.5-0.75, v 0-0.5): marfim, raiz mais escura (v baixo)
tv = yy / 0.5
den = np.stack([0.62 + 0.3 * tv, 0.52 + 0.3 * tv, 0.36 + 0.28 * tv], -1)
m = regiao(0.5, 0, 0.75, 0.5); cor[m] = den[m]; rug[m] = 0.3
# palpebra (u 0.75-1, v 0-0.5): pele vermelha escura com borda quase preta (v alto = borda)
pal = np.stack([0.42 - 0.3 * tv, 0.05 - 0.03 * tv, 0.03 - 0.02 * tv], -1) * (0.85 + 0.25 * ruido[..., None])
m = regiao(0.75, 0, 1, 0.5); cor[m] = pal[m]; rug[m] = 0.55
def salvar(nome, rgb):                                       # bpy: linha 0 = v 0 (mesma convencao das UVs acima)
    im = bpy.data.images.new(nome, N, N, alpha=False)
    rgba = np.concatenate([rgb, np.ones((N, N, 1), np.float32)], -1)
    im.pixels.foreach_set(rgba.ravel()); im.filepath_raw = os.path.join(OUT, nome + ".png"); im.file_format = "PNG"; im.save()
    bpy.data.images.remove(im)
salvar("CR_Dragao_detalhes_cor", np.clip(cor, 0, 1) ** (1 / 2.2))
salvar("CR_Dragao_detalhes_rugosidade", np.repeat(rug[..., None], 3, -1))

# ------------------------------------------------------------------ malha de detalhes
pts, faces, uvs, pesos = [], [], [], []
def add_grade(P, nu, nv, uvbox, peso, fechar_u=False):
    """P(i,j) -> ponto; uvbox (u0,v0,u1,v1); peso(i,j,ponto) -> {osso: w}"""
    base = len(pts)
    for j in range(nv + 1):
        for i in range(nu + 1):
            p = P(i / nu, j / nv); pts.append(p); pesos.append(peso(i / nu, j / nv, p))
    for j in range(nv):
        for i in range(nu):
            a = base + j * (nu + 1) + i; fc = (a, a + 1, a + nu + 2, a + nu + 1); faces.append(fc)
            u0, v0, u1, v1 = uvbox
            uvs.append([(lerp(u0, u1, (i + di) / nu), lerp(v0, v1, (j + dj) / nv)) for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1))])
def larg(y):
    ys = sorted(LARG); y = max(ys[0], min(ys[-1], y))
    for a, b in zip(ys, ys[1:]):
        if a <= y <= b: return lerp(LARG[a], LARG[b], (y - a) / (b - a))
    return LARG[ys[-1]]
Y0, Y1 = Y_PONTA + 0.004, Y_CANTO + 0.012
UP, LO = {"mouth_upper": 1.0}, {"mouth_lower": 1.0}
# palato (cima) e assoalho (baixo): arcos entre as bordas dos labios
def palato(t, j):
    y = lerp(Y0, Y1, j); w = larg(min(y, Y_CANTO)) * (1 - 0.15 * j); x = -w + 2 * w * t
    return V((x, y, z_boca(min(y, Y_CANTO)) + 0.0015 + 0.55 * w * math.sin(math.pi * t) * (0.4 + 0.6 * suave(j * 3))))
def assoalho(t, j):
    y = lerp(Y0, Y1, j); w = larg(min(y, Y_CANTO)) * (1 - 0.15 * j); x = -w + 2 * w * t
    return V((x, y, z_boca(min(y, Y_CANTO)) - 0.0015 - 0.50 * w * math.sin(math.pi * t) * (0.4 + 0.6 * suave(j * 3))))
add_grade(palato, 10, 12, (0.5, 0.5, 1.0, 0.75), lambda i, j, p: UP)
add_grade(assoalho, 10, 12, (0.5, 0.5, 1.0, 0.75), lambda i, j, p: LO)
# garganta (fundo) e bochechas (laterais perto do canto): ligam cima e baixo e esticam quando a boca abre
def garganta(t, j):
    return lerp(palato(t, 1.0), assoalho(t, 1.0), j)
add_grade(garganta, 10, 4, (0.5, 0.92, 1.0, 1.0), lambda i, j, p: {"mouth_upper": 1 - j, "mouth_lower": j} if 0 < j < 1 else (UP if j == 0 else LO))
for lado in (0.0, 1.0):
    def bochecha(t, j, lado=lado):
        jj = lerp(0.55, 1.0, t); return lerp(palato(lado, jj), assoalho(lado, jj), j)
    add_grade(bochecha, 6, 3, (0.5, 0.75, 1.0, 0.92), lambda i, j, p: {"mouth_upper": 1 - j, "mouth_lower": j})
# lingua: elipsoide achatado no assoalho
def lingua(t, j):
    y = lerp(Y0 + 0.02, Y1 - 0.004, j); w = larg(min(y, Y_CANTO)) * 0.55 * (0.55 + 0.45 * suave(j * 2.5))
    a = math.pi * t; x = -w * math.cos(a); topo = math.sin(a)
    return V((x, y, z_boca(min(y, Y_CANTO)) - 0.45 * larg(min(y, Y_CANTO)) * 0.55 + 0.006 * topo))
add_grade(lingua, 8, 10, (0.0, 0.0, 0.5, 0.5), lambda i, j, p: LO)
# dentes: cones nas bordas (presas maiores na frente), de cima para baixo e de baixo para cima
def dente(base_p, ponta_p, r, peso):
    eixo = (ponta_p - base_p); L = eixo.length; eixo.normalize()
    a = eixo.orthogonal().normalized(); b = eixo.cross(a)
    ib = len(pts); seg = 6
    for k in range(seg):
        ang = 2 * math.pi * k / seg; pts.append(base_p + (a * math.cos(ang) + b * math.sin(ang)) * r); pesos.append(peso)
    for k in range(seg):
        ang = 2 * math.pi * k / seg; pts.append(base_p + eixo * L * 0.55 + (a * math.cos(ang) + b * math.sin(ang)) * r * 0.6); pesos.append(peso)
    ip = len(pts); pts.append(ponta_p); pesos.append(peso)
    for k in range(seg):
        k2 = (k + 1) % seg
        faces.append((ib + k, ib + k2, ib + seg + k2, ib + seg + k)); uvs.append([(0.52, 0.02), (0.73, 0.02), (0.73, 0.3), (0.52, 0.3)])
        faces.append((ib + seg + k, ib + seg + k2, ip)); uvs.append([(0.52, 0.3), (0.73, 0.3), (0.62, 0.48)])
n_dentes = 0
for s in (1, -1):
    for cima in (True, False):
        k = 0; y = Y_PONTA + 0.010 + (0.0 if cima else 0.006)
        while y < Y_CANTO - 0.004:
            w = larg(y) - 0.0015; zb = z_boca(y)
            presa = (k == 1); L = (0.016 if presa else 0.0085 - 0.0035 * (y - Y_PONTA) / (Y_CANTO - Y_PONTA))
            r = (0.0034 if presa else 0.0021)
            b0 = V((s * w, y, zb + (0.003 if cima else -0.003)))
            p0 = V((s * (w - 0.0015), y + 0.001, zb + (-L if cima else L)))
            dente(b0, p0, r, UP if cima else LO); y += 0.0115 + rnd.uniform(-0.001, 0.001); k += 1; n_dentes += 1
    # incisivos na ponta do focinho
for cima in (True, False):
    for xi in (-0.010, -0.0035, 0.0035, 0.010):
        y = Y_PONTA + 0.006 + abs(xi) * 0.5; zb = z_boca(y)
        dente(V((xi, y, zb + (0.003 if cima else -0.003))), V((xi * 0.9, y + 0.001, zb + (-0.007 if cima else 0.007))), 0.0018, UP if cima else LO)
        n_dentes += 1
# olhos: globo (iris projetada na direcao do olhar) + palpebras
def esfera_olho(c, r, olhar):
    olhar = olhar.normalized(); a = V((0, 0, 1)).cross(olhar).normalized(); b = olhar.cross(a)
    ib = len(pts); NU, NV = 16, 10
    for j in range(NV + 1):
        th = math.pi * j / NV
        for i in range(NU):
            ph = 2 * math.pi * i / NU
            d = olhar * math.cos(th) + (a * math.cos(ph) + b * math.sin(ph)) * math.sin(th)
            pts.append(c + V((d.x * r.x, d.y * r.y, d.z * r.z))); pesos.append({"head": 1.0})
    for j in range(NV):
        for i in range(NU):
            i2 = (i + 1) % NU; q = [ib + j * NU + i, ib + j * NU + i2, ib + (j + 1) * NU + i2, ib + (j + 1) * NU + i]
            faces.append(tuple(q)); uv = []
            for idx in q:
                p = pts[idx] - c; p = V((p.x / r.x, p.y / r.y, p.z / r.z))
                uv.append((0.25 + 0.24 * p.dot(a) * 0.98, 0.75 + 0.24 * p.dot(b) * 0.98))   # iris na frente do globo
            uvs.append(uv)
def palpebra(c, r, olhar, cima):
    olhar = olhar.normalized(); a = V((0, 0, 1)).cross(olhar).normalized(); b = olhar.cross(a)
    def P(t, j):
        ph = math.radians(lerp(-80, 80, t)); vert = math.radians(lerp(30 if cima else 26, 78, j)) * (1 if cima else -1)
        d = (olhar * math.cos(vert) + b * math.sin(vert)) * math.cos(ph) + a * math.sin(ph)
        k = 1.28 + 0.05 * j
        return c + V((d.x * r.x * k, d.y * r.y * k, d.z * r.z * k))
    add_grade(P, 8, 3, (0.75, 0.0, 1.0, 0.5), lambda i, j, p: {"head": 1.0})
for c0 in CENTROS:
    s = 1 if c0.x > 0 else -1
    olhar = V((s * 0.85, -0.45, 0.05)); r = V((0.0085, 0.0105, 0.0078))
    c = c0 + V((s * -0.0015, 0, 0))
    esfera_olho(c, r, olhar); palpebra(c, r, olhar, True); palpebra(c, r, olhar, False)
md = bpy.data.meshes.new("Silverwing_Detalhes"); md.from_pydata([tuple(p) for p in pts], [], faces)
uvl = md.uv_layers.new(name="UVMap")
li = 0
for poly, uv in zip(md.polygons, uvs):
    for k, li_ in enumerate(poly.loop_indices): uvl.data[li_].uv = uv[k]
for p in md.polygons: p.use_smooth = True
det = bpy.data.objects.new("Silverwing_Detalhes", md); sc.collection.objects.link(det)
for i, pw in enumerate(pesos):
    for n, w in pw.items():
        g = det.vertex_groups.get(n) or det.vertex_groups.new(name=n); g.add([i], w, "REPLACE")
det.parent = A; am = det.modifiers.new("Armature", "ARMATURE"); am.object = A
mat = bpy.data.materials.new("M_CR_Dragao_Detalhes")
if mat.node_tree is None: mat.use_nodes = True
nt = mat.node_tree; bs = nt.nodes["Principled BSDF"]
tc = nt.nodes.new("ShaderNodeTexImage"); tc.image = bpy.data.images.load(os.path.join(OUT, "CR_Dragao_detalhes_cor.png")); tc.image.pack()
tr = nt.nodes.new("ShaderNodeTexImage"); tr.image = bpy.data.images.load(os.path.join(OUT, "CR_Dragao_detalhes_rugosidade.png")); tr.image.pack()
tr.image.colorspace_settings.name = "Non-Color"
nt.links.new(tc.outputs["Color"], bs.inputs["Base Color"]); nt.links.new(tr.outputs["Color"], bs.inputs["Roughness"])
if "Coat Weight" in bs.inputs: bs.inputs["Coat Weight"].default_value = 0.35      # brilho umido (olho/boca)
md.materials.append(mat)
print("DETALHES tris", sum(len(p.vertices) - 2 for p in md.polygons), "dentes", n_dentes, "olhos", len(CENTROS))
print("CORPO tris", sum(len(p.vertices) - 2 for p in me.polygons))
bpy.ops.wm.save_mainfile()
print("ROSTO_REFINADO_OK")
