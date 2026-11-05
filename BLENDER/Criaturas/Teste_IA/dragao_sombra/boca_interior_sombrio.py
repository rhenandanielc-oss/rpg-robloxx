"""Interior da boca do Dragao Sombrio (05/11, usuario: "nao quero simplesmente um bloco dentro da boca, quero a boca
interna feita, com dentes, etc."). Mesmo caminho do Dragao das Montanhas (dragao_novo/boca_interior.py): malha
PROPRIA `Silverwing_Boca` (vira um MeshPart a mais no Roblox) presa aos ossos da boca, com textura propria.
- Tira as 2 paredes planas da v9 (SB_Dragao_Boca_Parede_L/R: ilhas finas dentro da boca) da malha de jogo.
- Silverwing_Boca: gengivas superior e inferior (cordao carnudo por dentro da fileira de dentes, da ponta ao canto);
  fileira inferior completa (a v9 tinha 3 dentes por lado embaixo contra 7 em cima: entram 4 por lado entre/atras
  deles) e dentes de tras pequenos no fim das duas fileiras; ceu da boca arqueado com sulcos transversais (pregas do
  palato); bochecha interna nos 45% de tras de cada lado (membrana com dobras que estica entre maxilar e mandibula e
  fecha a vista de lado, no lugar das paredes); garganta em tubo escurecendo para dentro da cabeca.
- Pesos: cada vertice copia os pesos do vertice mais proximo da malha de jogo do MESMO lado da boca (maxilar ou
  mandibula); bochecha mistura os dois pela altura.
Entrada: rig/SB_Dragao_M2M_v9.blend (nao e sobrescrito). Saida: rig/SB_Dragao_M2M_v10_boca.blend e renders
antes/depois em review/v10_boca2/. Uso: blender -b rig/SB_Dragao_M2M_v9.blend -P boca_interior_sombrio.py"""
import bpy, bmesh, os, math
import numpy as np
from mathutils import Vector as V
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "review", "v10_boca2"); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
acao_original = A.animation_data.action if A.animation_data else None
def repouso():
    if A.animation_data: A.animation_data.action = None
    for b in A.pose.bones: b.matrix_basis.identity()
    bpy.context.view_layer.update()
repouso()
mw = A.matrix_world; mm = M.matrix_world; me = M.data
gi = {g.index: g.name for g in M.vertex_groups}
SUP = {"head", "mouth_upper", "mouth_upper_tip"}; INF = {"mouth_lower", "mouth_lower_tip"}
def dono(v): return gi[max(v.groups, key=lambda g: g.weight).group] if v.groups else ""

# ---------------- ilhas da malha de jogo perto da boca: dentes, lingua, paredes ----------------
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); vis = set(); IL = []
for v in bm.verts:
    if v.index in vis: continue
    st, il = [v], []
    while st:
        x = st.pop()
        if x.index in vis: continue
        vis.add(x.index); il.append(x.index); st += [e.other_vert(x) for e in x.link_edges]
    IL.append(il)
bm.free()
P = lambda i: mm @ me.vertices[i].co
dentes, paredes, lingua = [], [], None
for il in IL:
    if len(il) > 400: continue
    c = sum((P(i) for i in il), V()) / len(il)
    if not (c.y < -0.93 and abs(c.x) < 0.1 and 0.70 < c.z < 0.88): continue
    zs = [P(i).z for i in il]; ys = [P(i).y for i in il]
    if len(il) == 26: dentes.append((il, c, dono(me.vertices[il[0]]) in INF))
    elif len(il) > 150 and abs(c.x) < 0.002: lingua = il
    elif max(zs) - min(zs) > 0.04 and max(ys) - min(ys) > 0.08: paredes.append(il)
print("BOCA dentes", len(dentes), "paredes", len(paredes), "lingua", lingua is not None)
assert len(paredes) == 2 and len(dentes) == 20
# parede: da ponta ao canto; teto e chao da boca a 40% da meia-largura
pw = [P(i) for il in paredes for i in il]
Y_CANTO = max(p.y for p in pw) + 0.004; Y_PONTA = min(p.y for p in pw) - 0.018
def faixa_parede(y):
    pts = [p for p in pw if abs(p.y - y) < 0.006]
    if not pts: pts = sorted(pw, key=lambda p: abs(p.y - y))[:10]
    return max(p.z for p in pts), min(p.z for p in pts)
print("BOCA canto %.4f ponta %.4f" % (Y_CANTO, Y_PONTA))

# fileiras de dentes: base (raiz no labio) e ponta de cada dente, por lado
def base_ponta(il, inf):
    pts = sorted((P(i) for i in il), key=lambda p: p.z)
    raiz = pts[:6] if inf else pts[-6:]; pt = pts[-1] if inf else pts[0]
    return sum(raiz, V()) / 6, pt
FIL = {}
for il, c, inf in dentes:
    s = 1 if c.x > 0 else -1; b, t = base_ponta(il, inf)
    FIL.setdefault((s, inf), []).append((b, t))
for k in FIL: FIL[k].sort(key=lambda bt: bt[0].y)          # ponta (y menor) -> canto
def curva(pts, y):
    """interpola (x, z) da fileira em y (extrapola em linha reta nas pontas)"""
    ps = sorted(pts, key=lambda p: p.y)
    if y <= ps[0].y: a, b = ps[0], ps[1]
    elif y >= ps[-1].y: a, b = ps[-2], ps[-1]
    else:
        for a, b in zip(ps, ps[1:]):
            if a.y <= y <= b.y: break
    k = (y - a.y) / ((b.y - a.y) or 1e-9); return a.lerp(b, k)

# ---------------- pesos: vizinho mais proximo do mesmo lado da boca ----------------
kd = {}
for lado, nomes in (("sup", SUP), ("inf", INF)):
    ids = [v.index for v in me.vertices if dono(v) in nomes and (mm @ v.co).y < -0.90 and (mm @ v.co).z > 0.72
           and not any(v.index in il for il in paredes)]
    t = KDTree(len(ids))
    for i in ids: t.insert(mm @ me.vertices[i].co, i)
    t.balance(); kd[lado] = t
def pesos_de(p, lado):
    _, i, _ = kd[lado].find(p)
    return {gi[g.group]: g.weight for g in me.vertices[i].groups if g.weight > 0.001}
def mistura(a, b, k):
    out = {}
    for n, w in a.items(): out[n] = out.get(n, 0) + w * (1 - k)
    for n, w in b.items(): out[n] = out.get(n, 0) + w * k
    return out

# ---------------- textura propria (512): faixas por regiao (v = 0..1 dentro de cada faixa) ----------------
N = 512; rng = np.random.default_rng(11)
img = np.zeros((N, N, 4), np.float32); img[..., 3] = 1
yy, xx = np.mgrid[0:N, 0:N] / (N - 1)
gran = rng.random((N, N)) * 0.06
REG = {"gengiva": (0.00, 0.15), "ceu": (0.15, 0.33), "bochecha": (0.33, 0.47), "assoalho": (0.47, 0.55), "garganta": (0.55, 0.65),
       "lingua": (0.65, 0.80), "dente": (0.80, 1.00)}
# (r4, usuario: "dentes maiores, lingua melhor, tirar manchas escuras") escala dos dentes: comprimento x raio
ESC_L, ESC_R = 1.55, 1.3
def regiao(nome, u): a, b = REG[nome]; return a + (b - a) * min(0.98, max(0.02, u))
for nome, (a, b) in REG.items():
    m = (xx >= a) & (xx < b); u = (xx - a) / (b - a)
    if nome == "gengiva":     # rosa-violeta palido, mais escuro no sulco do dente (v alto)
        cor = np.dstack([0.66 - 0.14 * yy + gran, 0.36 - 0.10 * yy + gran * 0.5, 0.44 - 0.08 * yy + gran * 0.5])
    elif nome == "ceu":       # rosa, com pregas transversais mais escuras (v = ponta -> canto)
        prega = 0.5 + 0.5 * np.cos(yy * 2 * math.pi * 9); esc = 1 - 0.55 * yy
        cor = np.dstack([(0.74 - 0.16 * prega) * esc + gran, (0.40 - 0.10 * prega) * esc + gran * 0.5, (0.47 - 0.10 * prega) * esc + gran * 0.5])
    elif nome == "bochecha":  # rosa com dobras verticais escuras (u = ao longo da bochecha)
        dob = (0.5 + 0.5 * np.cos(u * 2 * math.pi * 3)) ** 2          # (r2) dobras suaves: a 1a versao parecia cortina
        cor = np.dstack([0.64 - 0.09 * dob + gran, 0.32 - 0.05 * dob + gran * 0.5, 0.40 - 0.05 * dob + gran * 0.5])
    elif nome == "assoalho":  # (r4) assoalho rosado liso sob a lingua (cobre a pele escura que aparecia ao lado dela)
        cor = np.dstack([0.66 - 0.18 * yy + gran, 0.34 - 0.10 * yy + gran * 0.5, 0.42 - 0.10 * yy + gran * 0.5])
    elif nome == "lingua":    # (r4) vermelho-rosado umido, sulco central escuro (u 0,5), mais claro em cima
        sulco = np.exp(-((u - 0.5) / 0.06) ** 2)
        cor = np.dstack([0.74 - 0.20 * sulco - 0.10 * yy + gran * 1.5, 0.26 - 0.08 * sulco + gran * 0.6, 0.32 - 0.08 * sulco + gran * 0.6])
    elif nome == "garganta":  # da boca (v 0) ao fundo (v 1): rosa escuro -> quase preto
        f = (1 - yy) ** 1.5
        cor = np.dstack([0.42 * f + 0.02, 0.10 * f + 0.005, 0.15 * f + 0.008])
    else:                     # (r7, usuario: "dentes mais brancos") marfim claro: raiz levemente amarelada -> ponta quase branca
        cor = np.dstack([0.80 + 0.16 * yy + gran * 0.3, 0.76 + 0.18 * yy + gran * 0.3, 0.66 + 0.24 * yy + gran * 0.3])
    img[..., :3] = np.where(m[..., None], np.clip(cor, 0, 1), img[..., :3])
TEXP = os.path.join(AQUI, "low", "SB_Boca_interior.png")
im = bpy.data.images.get("SB_Boca_interior") or bpy.data.images.new("SB_Boca_interior", N, N, alpha=True)
im.pixels.foreach_set(img.ravel()); im.filepath_raw = TEXP; im.file_format = "PNG"; im.save()

# ---------------- malha nova ----------------
velho = bpy.data.objects.get("Silverwing_Boca")
if velho: bpy.data.objects.remove(velho, do_unlink=True)
bo = bmesh.new(); uvl = bo.loops.layers.uv.new("UVMap"); GP = {}
def vert(p, w): v = bo.verts.new(p); GP[v] = w; return v
def face(vs, uvs):
    try: f = bo.faces.new(vs)
    except ValueError: return None
    for l, uv in zip(f.loops, uvs): l[uvl].uv = uv
    return f
def grade(G, reg, fechar_u=False, inverter=False):
    """G[i][j] = vertice; u = i, v = j (normalizados) -> faixa da regiao"""
    ni, nj = len(G), len(G[0])
    for i in range(ni - 1 + (1 if fechar_u else 0)):
        i2 = (i + 1) % ni
        for j in range(nj - 1):
            q = [G[i][j], G[i2][j], G[i2][j + 1], G[i][j + 1]]
            u0, u1 = i / (ni - 1 + fechar_u), (i + 1) / (ni - 1 + fechar_u); v0, v1 = j / (nj - 1), (j + 1) / (nj - 1)
            uv = [(regiao(reg, u0), v0), (regiao(reg, u1), v0), (regiao(reg, u1), v1), (regiao(reg, u0), v1)]
            if inverter: q, uv = q[::-1], uv[::-1]
            face(q, uv)
def suave(t): t = min(1, max(0, t)); return t * t * (3 - 2 * t)
NY = 22
YS = [Y_PONTA + 0.006 + (Y_CANTO - Y_PONTA - 0.006) * k / (NY - 1) for k in range(NY)]   # ponta -> canto (r3: ate mais perto da ponta)

# GENGIVAS: cordao carnudo (meio tubo voltado para dentro da boca) cobrindo as raizes, por lado e por arcada
def raio_gengiva(y, inf=True):
    r = 0.0022 + 0.0010 * suave((y - Y_PONTA) / (Y_CANTO - Y_PONTA))
    return r if inf else r * 1.3                                 # (r3) a de cima mais grossa: cobre a borda do labio
def centro_gengiva(s, inf, y):
    """(r2) centro do cordao SEMPRE por dentro da fileira (na 1a versao a gengiva de baixo saia para fora do labio).
    (r3) a de cima sobe para DENTRO do labio: a borda interna do labio (pele escura serrilhada entre os dentes) fica
    escondida atras dela"""
    b = curva([bt[0] for bt in FIL[(s, inf)]], y); r = raio_gengiva(y, inf)
    if inf: return V((b.x - s * r * 0.95, y, b.z + r * 0.15)), r
    return V((b.x - s * r * 0.85, y, b.z + r * 0.45)), r
def gengiva(s, inf):
    G = []
    dz = 1 if inf else -1                                       # para dentro da boca (para cima embaixo, para baixo em cima)
    for y in YS:
        c, r = centro_gengiva(s, inf, y)
        anel = []
        for j in range(7):                                      # do lado do labio (sem passar da raiz) ate o lado da lingua
            a = math.pi * j / 6
            p = c + V((s * r * math.cos(a) * 0.75, 0, dz * r * math.sin(a)))
            anel.append(vert(p, pesos_de(p, "inf" if inf else "sup")))
        G.append(anel)
    grade(G, "gengiva", inverter=(s > 0) != inf)
for s in (1, -1):
    for inf in (False, True): gengiva(s, inf)

# DENTES novos: completa a fileira de baixo (4 por lado) + 1 dente de tras pequeno em cada fileira
def dente(base, ponta_dir, comp, r, s, inf):
    eixo = ponta_dir.normalized(); lado = V((1, 0, 0)).cross(eixo).normalized() if abs(eixo.x) < 0.9 else V((0, 1, 0))
    frente = eixo.cross(lado).normalized(); aneis = []
    for k, (t, rr) in enumerate(((0, 1.0), (0.45, 0.72), (0.8, 0.38))):
        c = base + eixo * comp * t; anel = []
        for j in range(6):
            a = 2 * math.pi * j / 6
            p = c + (lado * math.cos(a) + frente * math.sin(a)) * r * rr
            anel.append(vert(p, pesos_de(p, "inf" if inf else "sup")))
        aneis.append(anel)
    pt = vert(base + eixo * comp, pesos_de(base + eixo * comp, "inf" if inf else "sup"))
    for k in range(2):
        for j in range(6):
            q = [aneis[k][j], aneis[k][(j + 1) % 6], aneis[k + 1][(j + 1) % 6], aneis[k + 1][j]]
            u0, u1 = regiao("dente", j / 6), regiao("dente", (j + 1) / 6); v0, v1 = k / 2.5, (k + 1) / 2.5
            face(q, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
    for j in range(6): face([aneis[2][j], aneis[2][(j + 1) % 6], pt], [(regiao("dente", 0.5), 0.8)] * 2 + [(regiao("dente", 0.5), 0.99)])
novos = 0
for s in (1, -1):
    inf_b = FIL[(s, True)]; sup_b = FIL[(s, False)]
    comp_inf = sum((t - b).length for b, t in inf_b) / len(inf_b); r_inf = 0.0022
    # entre os 3 de baixo e atras deles (fileira regular; nada na frente do primeiro, que ja e a presa)
    ys_inf = sorted(b.y for b, _ in inf_b); passo = (ys_inf[-1] - ys_inf[0]) / (len(ys_inf) - 1)
    alvos = [(a + b) / 2 for a, b in zip(ys_inf, ys_inf[1:])] + [ys_inf[-1] + passo * 0.5, ys_inf[-1] + passo]
    for y in alvos[:4]:
        b = curva([x[0] for x in inf_b], y); t = curva([x[1] for x in inf_b], y)
        d = (t - b); d.z = abs(d.z)
        dente(b + V((-s * 0.0008, 0, 0)), d, comp_inf * 0.85 * ESC_L, r_inf * ESC_R, s, True); novos += 1
    for inf, fil in ((False, sup_b), (True, inf_b)):              # dente de tras pequeno junto do canto
        y = min(Y_CANTO - 0.008, max(b.y for b, _ in fil) + 0.016)
        b = curva([x[0] for x in fil], y); t = curva([x[1] for x in fil], y); d = t - b
        dente(b + V((-s * 0.0012, 0, 0)), d, d.length * 0.6 * (ESC_L if inf else 1.28), 0.0019 * ESC_R, s, inf); novos += 1
print("BOCA dentes novos", novos)

# (r7) DENTES DA V9 -> Silverwing_Boca: usavam pedacos da textura do corpo (manchas escuras por dentro, mais visiveis
# depois de aumentados). Cada dente e copiado com a mesma forma, ja na escala nova (raiz fixa), com os pesos do proprio
# vertice e UV limpa (u = volta em torno do eixo, v = raiz -> ponta); o original sai da malha do corpo.
maior = max((base_ponta(il, inf)[1] - base_ponta(il, inf)[0]).length for il, c, inf in dentes)
for il, c, inf in dentes:
    b, t = base_ponta(il, inf); eixo = (t - b).normalized(); L_ = (t - b).length
    sl = ESC_L if inf else 1.28     # (r5) os de cima crescem menos: com x1,55 atravessavam a mandibula fechada
    ref = (V((0, 1, 0)) - eixo * eixo.y).normalized(); ref2 = eixo.cross(ref)
    novo_v = {}
    for i in il:
        rel = P(i) - b; al = rel.dot(eixo); perp = rel - eixo * al
        q = b + eixo * al * sl + perp * ESC_R
        novo_v[i] = vert(q, {gi[g.group]: g.weight for g in me.vertices[i].groups if g.weight > 0.001})
    ilset = set(il)
    for pol in me.polygons:
        if pol.vertices[0] not in ilset or not all(x in ilset for x in pol.vertices): continue
        uvs = []
        for x in pol.vertices:
            rel = P(x) - b; al = max(0.0, min(1.0, rel.dot(eixo) / (L_ or 1))); perp = rel - eixo * rel.dot(eixo)
            ang = (math.atan2(perp.dot(ref2), perp.dot(ref)) / (2 * math.pi)) % 1
            uvs.append((regiao("dente", ang), 0.05 + 0.9 * al))
        face([novo_v[x] for x in pol.vertices], uvs)
print("BOCA dentes da v9 copiados para a boca", len(dentes))

# CEU DA BOCA: superficie arqueada entre as gengivas de cima, da ponta ao canto (logo abaixo do teto da bolsa)
# (r2) cada ponto e medido por raio contra a pele de cima: fica sempre 1,5 mm abaixo dela (a pele escura atravessava
# o ceu em manchas serrilhadas)
_ign = set(i for il in paredes for i in il) | set(lingua or [])
_fs = [tuple(p.vertices) for p in me.polygons if not any(i in _ign for i in p.vertices)]
BVH = BVHTree.FromPolygons([mm @ v.co for v in me.vertices], _fs)
NX = 9; G = []
for y in YS:
    cl, _ = centro_gengiva(1, False, y); cr, _ = centro_gengiva(-1, False, y)
    zt, _ = faixa_parede(min(y, Y_CANTO - 0.006))
    linha = []
    for i in range(NX):
        k = i / (NX - 1); x = cr.x * (1 - k) + cl.x * k
        borda = (cl.z + cr.z) / 2
        arco = math.sin(math.pi * k)                              # sobe no meio
        z = borda + (zt - 0.0012 - borda) * arco ** 0.6
        h = BVH.ray_cast(V((x, y, borda - 0.004)), V((0, 0, 1)), 0.05)[0]
        if h is not None: z = min(z, h.z - 0.0015) if h.z - 0.0015 > borda - 0.002 else z
        p = V((x, y, z)); linha.append(vert(p, pesos_de(p, "sup")))
    G.append(linha)
GT = [[G[j][i] for j in range(NY)] for i in range(NX)]           # u = de lado a lado, v = ponta -> canto
grade(GT, "ceu")

# BOCHECHAS: membrana com dobras nos 45% de tras de cada lado, entre a gengiva de cima e a de baixo
NB, NV = 12, 7
y_ini = Y_CANTO - (Y_CANTO - Y_PONTA) * 0.45
for s in (1, -1):
    G = []
    for i in range(NB):
        col = []
        for j in range(NV):
            k = j / (NV - 1)
            # (r3) borda da frente reta: o arco testado virou uma ponta que sobe da mandibula ao abrir; a borda so se
            # dobra levemente para dentro (vira uma prega, nao uma aresta de pe)
            y = y_ini + (Y_CANTO - 0.002 - y_ini) * i / (NB - 1)
            prega = (1 - i / 2) if i < 2 else 0
            # (r2) presa ao lado de dentro das gengivas (antes: na raiz dos dentes -> borda serrilhada entre o labio e os dentes)
            cs, rs_ = centro_gengiva(s, False, y); ci, ri_ = centro_gengiva(s, True, y)
            bs = cs + V((0, 0, -rs_ * 0.6)); bi = ci + V((0, 0, ri_ * 0.6))
            z = bs.z * (1 - k) + bi.z * k
            x = bs.x * (1 - k) + bi.x * k + s * 0.0007 * math.sin(math.pi * k) - s * 0.0012 * prega * math.sin(math.pi * k)
            p = V((x, y, z))
            col.append(vert(p, mistura(pesos_de(p, "sup"), pesos_de(p, "inf"), suave(k))))
        G.append(col)
    grade(G, "bochecha", inverter=s < 0)

# (r4) ASSOALHO: superficie entre as gengivas de baixo, 1,2 mm acima da pele (raio para baixo), da ponta ao canto
G = []
for y in YS:
    cl, _ = centro_gengiva(1, True, y); cr, _ = centro_gengiva(-1, True, y)
    linha = []
    for i in range(NX):
        k = i / (NX - 1); x = cr.x * (1 - k) + cl.x * k; topo = (cl.z + cr.z) / 2
        h = BVH.ray_cast(V((x, y, topo + 0.004)), V((0, 0, -1)), 0.05)[0]
        z = (h.z + 0.0012) if h is not None and h.z > topo - 0.02 else topo - 0.002 * math.sin(math.pi * k)
        p = V((x, y, min(z, topo))); linha.append(vert(p, pesos_de(p, "inf")))
    G.append(linha)
grade([[G[j][i] for j in range(NY)] for i in range(NX)], "assoalho", inverter=True)
ASSO = {round(y, 5): [v.co.z for v in G[j]] for j, y in enumerate(YS)}

# (r4) LINGUA NOVA (substitui a da v9, que era uma lamina chata): volumosa, larga atras, afina para a ponta, sulco
# central, ponta solta e levemente erguida; assenta no assoalho novo. 100% mandibula (pesos do vizinho de baixo).
lz = [P(i) for i in lingua]; LY0, LY1 = max(p.y for p in lz), min(p.y for p in lz)       # fundo -> ponta (v9)
LW = max(abs(p.x) for p in lz)
NL, NR = 14, 12; aneis = []
y_tras, y_ponta = min(LY0 + 0.006, Y_CANTO - 0.004), LY1 - 0.010
for i in range(NL + 1):
    t = i / NL; y = y_tras + (y_ponta - y_tras) * t
    cl, _ = centro_gengiva(1, True, y); cr, _ = centro_gengiva(-1, True, y)
    meia = abs(cl.x - cr.x) / 2
    w = min(meia * 0.58, LW * 1.0) * ((1 - t) ** 0.55 * 0.85 + 0.15)   # (r6) mais estreita: com 0,78 cobria o assoalho como um tapete
    h = 0.0050 * (1 - 0.5 * t)
    jj = min(range(NY), key=lambda q: abs(YS[q] - y)); chao = ASSO[round(YS[jj], 5)][NX // 2]
    zc = chao + h * 0.75 + 0.0016 * t ** 2.5                    # ponta solta: sobe um pouco no fim
    anel = []
    for j in range(NR):
        a = 2 * math.pi * j / NR; cx, sz = math.cos(a), math.sin(a)
        z = zc + h * (sz if sz > 0 else sz * 0.55)
        if sz > 0: z -= 0.0011 * math.exp(-(cx / 0.28) ** 2) * (1 - 0.6 * t)      # sulco central
        p = V((w * cx, y, z)); anel.append(vert(p, pesos_de(p, "inf")))
    aneis.append(anel)
pontaL = vert(V((0, y_ponta - 0.004, sum(v.co.z for v in aneis[-1]) / NR + 0.0004)), pesos_de(V((0, y_ponta, zc)), "inf"))
for i in range(NL):
    for j in range(NR):
        q = [aneis[i][j], aneis[i][(j + 1) % NR], aneis[i + 1][(j + 1) % NR], aneis[i + 1][j]]
        u0, u1 = regiao("lingua", j / NR), regiao("lingua", (j + 1) / NR); v0, v1 = i / NL, (i + 1) / NL
        face(q[::-1], [(u0, v0), (u1, v0), (u1, v1), (u0, v1)][::-1])
for j in range(NR): face([aneis[-1][(j + 1) % NR], aneis[-1][j], pontaL], [(regiao("lingua", 0.5), 0.95)] * 3)

# GARGANTA: tubo atras do canto, fechando para dentro da cabeca (cima no maxilar, baixo na mandibula, fundo na cabeca)
zt0, zf0 = faixa_parede(Y_CANTO - 0.006); zm, hz = (zt0 + zf0) / 2, (zt0 - zf0) / 2 * 0.9
hx = abs(curva([bt[0] for bt in FIL[(1, False)]], Y_CANTO).x) * 0.8
NG, NT = 6, 14; G = []
for k in range(NG + 1):
    sk = k / NG; y = Y_CANTO - 0.004 + 0.022 * sk; esc = 1 - 0.7 * sk ** 1.2
    anel = []
    for j in range(NT):
        a = 2 * math.pi * j / NT; p = V((hx * esc * math.cos(a), y, zm + hz * esc * math.sin(a)))
        if sk < 0.5: w = pesos_de(p, "sup") if math.sin(a) > 0.1 else pesos_de(p, "inf") if math.sin(a) < -0.1 else mistura(pesos_de(p, "sup"), pesos_de(p, "inf"), 0.5)
        else: w = {"head": 1.0}
        anel.append(vert(p, w))
    G.append(anel)
fundo = vert(V((0, G[-1][0].co.y + 0.003, zm)), {"head": 1.0})
GJ = [[G[k][j] for k in range(NG + 1)] for j in range(NT)]
grade(GJ, "garganta", fechar_u=True, inverter=True)
for j in range(NT): face([G[-1][(j + 1) % NT], G[-1][j], fundo], [(regiao("garganta", 0.5), 0.98)] * 3)
bo.normal_update()
mesh = bpy.data.meshes.new("Silverwing_Boca"); bo.to_mesh(mesh)
ob = bpy.data.objects.new("Silverwing_Boca", mesh); sc.collection.objects.link(ob)
ob.matrix_world = mm.copy(); inv = mm.inverted()
for v in mesh.vertices: v.co = inv @ v.co                        # mesmas coordenadas de mundo que medimos
for v, w in zip(bo.verts, [GP[v] for v in bo.verts]):
    tot = sum(w.values()) or 1
    for n, x in w.items(): (ob.vertex_groups.get(n) or ob.vertex_groups.new(name=n)).add([v.index], x / tot, "REPLACE")
bo.free()
for p in mesh.polygons: p.use_smooth = True
ob.parent = A; ob.matrix_parent_inverse = A.matrix_world.inverted()
mod = ob.modifiers.new("Armature", "ARMATURE"); mod.object = A
mat = bpy.data.materials.get("M_SB_Boca") or bpy.data.materials.new("M_SB_Boca"); mat.use_nodes = True
nt = mat.node_tree; bs_ = nt.nodes.get("Principled BSDF")
tx = nt.nodes.get("TexBoca") or nt.nodes.new("ShaderNodeTexImage"); tx.name = "TexBoca"; tx.image = im
nt.links.new(tx.outputs["Color"], bs_.inputs["Base Color"]); bs_.inputs["Roughness"].default_value = 0.42
mesh.materials.append(mat)
TRIS = sum(len(p.vertices) - 2 for p in mesh.polygons)
print("BOCA tris", TRIS, "verts", len(mesh.vertices))

# ---------------- render ANTES (paredes) e tira as paredes ----------------
def pose_aberta():
    act = bpy.data.actions.get("Silverwing_Rugido_Territorial")
    if not A.animation_data: A.animation_data_create()
    A.animation_data.action = act
    if hasattr(A.animation_data, "action_slot") and act.slots: A.animation_data.action_slot = act.slots[0]
    f0, f1 = act.frame_range; sc.frame_set(int(f0 + (f1 - f0) * 0.45))
pose_aberta()
up = A.matrix_world @ A.pose.bones["mouth_upper_tip"].head; lo = A.matrix_world @ A.pose.bones["mouth_lower_tip"].head
hd = A.matrix_world @ A.pose.bones["head"].head
alvo = (up + lo) / 2 * 0.6 + hd * 0.4; frente = (up - hd).normalized(); dist = (up - hd).length * 2.6
lado = frente.cross(V((0, 0, 1))).normalized()
VISTAS = {"frente": frente * dist + V((0, 0, dist * 0.15)), "34": (frente * 0.75 + lado * 0.65).normalized() * dist + V((0, 0, dist * 0.1)),
          "lado": lado * dist * 1.1, "dentro": frente * dist * 0.55 + V((0, 0, dist * 0.05))}
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 640, 480
cam = bpy.data.objects.get("CamBoca") or bpy.data.objects.new("CamBoca", bpy.data.cameras.new("CamBoca"))
if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
sc.camera = cam; cam.data.lens = 50; cam.data.clip_start = 0.002
if not any(o.type == "LIGHT" for o in sc.objects):
    l = bpy.data.objects.new("SolBoca", bpy.data.lights.new("SolBoca", "SUN")); l.data.energy = 3.5; sc.collection.objects.link(l); l.rotation_euler = (0.8, 0.2, 0.6)
def renders(fase):
    for nome, off in VISTAS.items():
        cam.location = alvo + off; cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (fase, nome)); bpy.ops.render.render(write_still=True)
ob.hide_render = True; renders("antes"); ob.hide_render = False
repouso()
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
tirar = set(i for il in paredes for i in il) | set(lingua) | set(i for il, c, inf in dentes for i in il)   # paredes + lingua da v9 + dentes (r7: vao para a boca)
bmesh.ops.delete(bm, geom=[bm.verts[i] for i in tirar], context="VERTS"); bm.to_mesh(me); bm.free(); me.update()
print("BOCA paredes, lingua e dentes da v9 removidos do corpo (vertices)", len(tirar))
pose_aberta(); renders("depois")
if A.animation_data: A.animation_data.action = acao_original
repouso()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(AQUI, "rig", "SB_Dragao_M2M_v10_boca.blend"))
print("BOCA_OK", TRIS)
