"""Olhos do Crocodilo Primordial (etapa O1, 17/11): globo ocular + palpebras com ossos proprios, sobre uma COPIA do rig.
A malha do Meshy tem o olho so pintado na textura (~0,25 x 0,14 stud), sem geometria nem osso. Aqui:
- globo ocular (calota esferica) sobre o olho pintado, preso ao osso OlhoE/OlhoD (o olhar gira o globo no centro);
- palpebra superior e inferior (cascas esfericas um pouco maiores) presas a PalpebraSupE/InfE/SupD/InfD, que giram no
  eixo horizontal do olho (abrir/fechar). Abertas, ficam quase todas sob a pele acima/abaixo do olho;
- iris ambar com pupila VERTICAL pintada numa area livre da UV (textura nova *_olhos_2048.png; as originais ficam);
- pele das palpebras com a UV da pele vizinha (mesma cor da cabeca).
Todos os ossos novos sao filhos de Cabeca. Nada muda nos 28 ossos nem nos pesos da malha original.
Uso: blender -b CR_Crocodilo_Rig.blend -P olhos_crocodilo.py -- <saida.blend>"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.geometry import barycentric_transform
SAIDA = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
RAIZ = os.path.dirname(bpy.data.filepath); TEX = os.path.join(RAIZ, "tex")
A = bpy.data.objects["CR_Croc_Rig"]; M = bpy.data.objects["CR_Croc_LOW"]; me = M.data
assert len(A.data.bones) == 28, "rig ja tem ossos de olho?"

# ------------------------------------------------------------------ medidas (medir_olho.py: raio da camera nos pixels ambar)
OLHOS = {"E": (V((0.938, -11.274, 4.910)), V((0.958, -0.273, -0.088))),
         "D": (V((-0.556, -11.301, 4.901)), V((-0.967, -0.223, -0.122)))}
R_OLHO = 0.20          # raio do globo
PROF = 0.145           # r2: centro abaixo da pele -> globo encontra a pele a ~44 graus (meia largura 0,14) e sai so 0,055
R_PALP = 0.212         # casca das palpebras
# r2: borda em AMENDOA: a elevacao da borda varia com o angulo horizontal (alto no meio, zero nos cantos)
ABERTA_SUP, ABERTA_INF = 22.0, -17.0     # borda aberta no meio (graus); fechar = Sup -22, Inf +17 (giro no X do osso)
TRAS_SUP, TRAS_INF = 100.0, -100.0
LARG = 58.0            # meia largura (graus) das palpebras no sentido horizontal
CALOTA = 90.0          # globo ate 90 graus: olhar ate ~25 graus nao mostra a borda do globo
IRIS_K = 0.72          # sin(angulo) que vira a borda da iris (borda visivel ~44 graus)

bvh_src = M.evaluated_get(bpy.context.evaluated_depsgraph_get())
def normal_local(c, raio=0.15):
    """normal media da pele perto do olho (suaviza a medida da camera)"""
    acc = V((0, 0, 0))
    for p in me.polygons:
        if (p.center - c).length < raio: acc += p.normal * p.area
    return acc.normalized()

def quadro(c, n_med):
    n = (normal_local(c) * 0.5 + n_med.normalized() * 0.5).normalized()
    u = (V((0, 0, 1)) - n * n.z).normalized()           # "cima" do olho
    h = u.cross(n).normalized()                          # horizontal do olho
    return n, u, h

# ------------------------------------------------------------------ area livre da UV (rasterizacao real dos triangulos)
me.calc_loop_triangles(); uvl = me.uv_layers.active.data
RES = 512; occ = np.zeros((RES, RES), bool)
for t in me.loop_triangles:
    P = np.array([uvl[l].uv[:] for l in t.loops]) * RES
    x0, y0 = np.floor(P.min(0)).astype(int); x1, y1 = np.ceil(P.max(0)).astype(int)
    x0, y0 = max(x0 - 1, 0), max(y0 - 1, 0); x1, y1 = min(x1 + 1, RES - 1), min(y1 + 1, RES - 1)
    occ[y0:y1 + 1, x0:x1 + 1] |= True if (x1 - x0) * (y1 - y0) < 6 else False
    if (x1 - x0) * (y1 - y0) >= 6:
        ys, xs = np.mgrid[y0:y1 + 1, x0:x1 + 1]; px = xs + 0.5; py = ys + 0.5
        (ax, ay), (bx, by), (cx, cy) = P
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(d) < 1e-9: continue
        w1 = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / d; w2 = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / d
        dentro = (w1 >= -0.05) & (w2 >= -0.05) & (1 - w1 - w2 >= -0.05)
        occ[y0:y1 + 1, x0:x1 + 1] |= dentro
# maior quadrado livre (com margem de 4 px a 512 = 16 px a 2048)
livre = ~occ; L = np.zeros_like(livre, int)
for y in range(RES):
    for x in range(RES):
        if livre[y, x]: L[y, x] = 1 + (min(L[y - 1, x], L[y, x - 1], L[y - 1, x - 1]) if x and y else 0)
y, x = np.unravel_index(L.argmax(), L.shape); lado = L[y, x]
print("UV_LIVRE maior quadrado %d px (de %d) em x %d..%d y %d..%d" % (lado, RES, x - lado + 1, x, y - lado + 1, y))
assert lado >= 24, "sem area livre suficiente na UV"
MARG = 4; lado_u = (lado - 2 * MARG) / RES
U0 = (x - lado + 1 + MARG) / RES; V0 = (y - lado + 1 + MARG) / RES
IRIS_C = (U0 + lado_u / 2, V0 + lado_u / 2); IRIS_R = lado_u / 2

# ------------------------------------------------------------------ ossos
bpy.context.view_layer.objects.active = A; bpy.ops.object.mode_set(mode="EDIT")
eb = A.data.edit_bones; cab = eb["Cabeca"]
FR = {}
for lado_, (c_pele, n_med) in OLHOS.items():
    n, u, h = quadro(c_pele, n_med); c = c_pele - n * PROF
    FR[lado_] = (c, n, u, h)
    for nome, eixo in (("Olho", n), ("PalpebraSup", n), ("PalpebraInf", n)):
        b = eb.new(nome + lado_); b.head = c; b.tail = c + eixo * 0.35; b.align_roll(u); b.parent = cab
        b.use_deform = True
bpy.ops.object.mode_set(mode="OBJECT")
for lado_, (c, n, u, h) in FR.items():
    bn = A.data.bones["Olho" + lado_]
    print("OSSO_OLHO", lado_, "centro", tuple(round(v, 3) for v in c), "frente", tuple(round(v, 3) for v in n),
          "eixoX", tuple(round(v, 3) for v in bn.matrix_local.col[0].xyz), "eixoZ", tuple(round(v, 3) for v in bn.matrix_local.col[2].xyz))

# ------------------------------------------------------------------ geometria nova (bmesh na propria malha)
def jac_pele(p0, h, u):
    """UV planar continua: UV da pele num ponto + derivadas (h, u) tiradas do proprio triangulo"""
    ok, loc, nor, fi = M.closest_point_on_mesh(p0)
    for t in TRI_DE.get(fi, []):
        a, b, cc = (me.vertices[v].co for v in t.vertices)
        uva, uvb, uvc = (V((*uvl[l].uv, 0)) for l in t.loops)
        f = lambda q: barycentric_transform(q, a, b, cc, uva, uvb, uvc)
        o = f(loc); du = f(loc + h * 0.05) - o; dv = f(loc + u * 0.05) - o
        return lambda q: (o.x + (du.x * (q - loc).dot(h) + dv.x * (q - loc).dot(u)) / 0.05,
                          o.y + (du.y * (q - loc).dot(h) + dv.y * (q - loc).dot(u)) / 0.05)
def uv_pele(p):
    """UV da pele mais proxima (para a palpebra ter a cor da cabeca)"""
    ok, loc, nor, fi = M.closest_point_on_mesh(p)
    best = None
    for t in TRI_DE.get(fi, []):
        a, b, cc = (me.vertices[v].co for v in t.vertices)
        uva, uvb, uvc = (V((*uvl[l].uv, 0)) for l in t.loops)
        r = barycentric_transform(loc, a, b, cc, uva, uvb, uvc)
        best = (r.x, r.y); break
    return best

TRI_DE = {}
for t in me.loop_triangles: TRI_DE.setdefault(t.polygon_index, []).append(t)
bm = bmesh.new(); bm.from_mesh(me); uvL = bm.loops.layers.uv.active
dl = bm.verts.layers.deform.verify()
gidx = {}
for lado_ in OLHOS:
    for nome in ("Olho", "PalpebraSup", "PalpebraInf"):
        g = M.vertex_groups.get(nome + lado_) or M.vertex_groups.new(name=nome + lado_); gidx[nome + lado_] = g.index
mat_i = 0; tris_novos = 0

def grade(pontos, uvs, grupo, fechar_polo=None):
    """pontos[i][j] -> faces quadradas; uvs igual; peso 100% no grupo"""
    global tris_novos
    vs = [[bm.verts.new(p) for p in linha] for linha in pontos]
    for linha in vs:
        for v in linha: v[dl][gidx[grupo]] = 1.0
    for i in range(len(vs) - 1):
        for j in range(len(vs[0]) - 1):
            f = bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
            f.material_index = mat_i; f.smooth = True; tris_novos += 2
            for lp, (a, b) in zip(f.loops, ((i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j))): lp[uvL].uv = uvs[a][b]
    return vs

def d_ang(n, u, h, alfa, beta):
    a, b = math.radians(alfa), math.radians(beta)
    return (math.cos(b) * (math.cos(a) * n + math.sin(a) * u) + math.sin(b) * h).normalized()

for lado_, (c, n, u, h) in FR.items():
    # globo: calota ate 72 graus do eixo (o resto fica dentro da cabeca), polo frontal fechado em leque
    ANEIS, SEG = 6, 14
    pts, uvs = [], []
    for i in range(1, ANEIS + 1):
        th = math.radians(CALOTA * i / ANEIS); linha, luv = [], []
        for j in range(SEG + 1):
            ph = 2 * math.pi * j / SEG
            d = math.cos(th) * n + math.sin(th) * (math.cos(ph) * u + math.sin(ph) * h)
            linha.append(c + d * R_OLHO)
            k = min(1.0, math.sin(th) / IRIS_K)                   # borda visivel (~44 graus) = borda da iris
            luv.append((IRIS_C[0] + IRIS_R * k * math.sin(ph) * 0.98, IRIS_C[1] + IRIS_R * k * math.cos(ph) * 0.98))
        pts.append(linha); uvs.append(luv)
    vs = grade(pts, uvs, "Olho" + lado_)
    polo = bm.verts.new(c + n * R_OLHO); polo[dl][gidx["Olho" + lado_]] = 1.0
    for j in range(SEG):
        f = bm.faces.new((polo, vs[0][j], vs[0][j + 1])); f.smooth = True; tris_novos += 1
        f.loops[0][uvL].uv = IRIS_C; f.loops[1][uvL].uv = uvs[0][j]; f.loops[2][uvL].uv = uvs[0][j + 1]
    # palpebras (r2): casca com borda em amendoa (elev. da borda = A*cos(90*beta/LARG)), aba para dentro na borda;
    # UV planar continua da pele acima/abaixo do olho (sem saltar ilhas)
    for nome, A_, tras in (("PalpebraSup", ABERTA_SUP, TRAS_SUP), ("PalpebraInf", ABERTA_INF, TRAS_INF)):
        NA, NB = 5, 12
        betas = [-LARG + 2 * LARG * j / NB for j in range(NB + 1)]
        borda = [A_ * math.cos(math.radians(90.0 * b / LARG)) for b in betas]
        pts = [[c + d_ang(n, u, h, borda[j], b) * (R_OLHO + 0.004) for j, b in enumerate(betas)]]
        for i in range(NA + 1):
            pts.append([c + d_ang(n, u, h, borda[j] + (tras - borda[j]) * (i / NA) ** 1.3, b) * R_PALP for j, b in enumerate(betas)])
        ancora = c + d_ang(n, u, h, 50.0 if A_ > 0 else -50.0, 0.0) * R_PALP     # r3: pele rente ao olho (60 graus pegava o brilho claro da sobrancelha)
        fuv = jac_pele(ancora, h, u)
        uvs = [[fuv(p) for p in linha] for linha in pts]
        if A_ < 0: pts = [l[::-1] for l in pts]; uvs = [l[::-1] for l in uvs]
        grade(pts, uvs, nome + lado_)
bm.normal_update(); bm.to_mesh(me); bm.free(); me.update()
tris = sum(len(p.vertices) - 2 for p in me.polygons)
print("MALHA tris %d (+%d) ossos %d" % (tris, tris_novos, len(A.data.bones)))
assert tris <= 20000, tris

# ------------------------------------------------------------------ texturas novas (copias) com a iris pintada
mat = M.data.materials[0]; nos = {n.image.name: n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image}
def copiar(nome_img, arq):
    img = bpy.data.images[nome_img]; W, H = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)
    novo = bpy.data.images.new(nome_img + "_olhos", W, H, alpha=True)
    novo.colorspace_settings.name = img.colorspace_settings.name
    return img, novo, px, W, H
def area(W, H):
    ys, xs = np.mgrid[0:H, 0:W]
    cx, cy, r = IRIS_C[0] * W, IRIS_C[1] * H, IRIS_R * W
    dx = (xs + 0.5 - cx) / r; dy = (ys + 0.5 - cy) / r
    return dx, dy, np.sqrt(dx * dx + dy * dy), (np.abs(dx) <= 1.08) & (np.abs(dy) <= 1.08)
rng = np.random.default_rng(7)
for nome_img, arq, tipo in (("CR_Croc_cor", "CR_Croc_cor_olhos_2048.png", "cor"),
                            ("CR_Croc_normal", "CR_Croc_normal_olhos_2048.png", "normal"),
                            ("CR_Croc_rugosidade", "CR_Croc_rugosidade_olhos_2048.png", "rug")):
    img, novo, px, W, H = copiar(nome_img, arq)
    dx, dy, rr, caixa = area(W, H)
    if tipo == "cor":
        ang = np.arctan2(dy, dx)
        estrias = 0.5 + 0.5 * np.sin(ang * 37 + rng.random() * 6) * np.sin(ang * 13 + 1.7)
        claro = np.array([1.0, 0.84, 0.26]); escuro = np.array([0.80, 0.52, 0.10])   # r2: ambar mais amarelo (como o pintado)
        k = np.clip(rr, 0, 1)[..., None]
        cor = claro * (1 - k) + escuro * k
        cor = cor * (0.82 + 0.18 * estrias[..., None])
        cor = cor * np.clip(1.0 - np.clip((rr - 0.80) / 0.20, 0, 1)[..., None] * 0.75, 0, 1)    # anel escuro na borda
        pupila = (dx / 0.17) ** 2 + (dy / 0.88) ** 2                                                # fenda VERTICAL
        cor = np.where((pupila < 1.0)[..., None], np.array([0.02, 0.015, 0.01]), cor)
        borda_p = np.clip(1 - np.abs(np.sqrt(pupila) - 1.0) / 0.25, 0, 1)[..., None]
        cor = cor * (1 - 0.35 * borda_p * (pupila >= 1.0)[..., None])
        px[caixa, :3] = cor[caixa]; px[caixa, 3] = 1.0
    elif tipo == "normal":
        px[caixa, :3] = (0.5, 0.5, 1.0); px[caixa, 3] = 1.0
    else:
        px[caixa, :3] = 0.18; px[caixa, 3] = 1.0
    novo.pixels.foreach_set(px.ravel())
    novo.filepath_raw = os.path.join(TEX, arq); novo.file_format = "PNG"; novo.save()
    nos[nome_img].image = novo
    print("TEX_NOVA", arq, "iris centro uv", tuple(round(v, 4) for v in IRIS_C), "raio uv", round(IRIS_R, 4))

A["olhos"] = "O1 r2 17/11 (fechar: Sup -22, Inf +17 no X): OlhoE/D, PalpebraSup/InfE/D; aberta sup %.0f inf %.0f graus" % (ABERTA_SUP, ABERTA_INF)
bpy.ops.wm.save_as_mainfile(filepath=SAIDA)
print("SALVO", SAIDA)
