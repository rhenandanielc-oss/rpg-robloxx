"""E4 (malha de jogo): copia do build/e3c/c02_boca.py com resolucao reduzida (interior 17x9 + paredes 3, dentes 6x4, lingua 11x7).
--- texto original ---
E3 correcao (E3b): boca e juncao da mandibula refeitas a partir da E3_t2 (topologia + antebracos, antes da boca).
Diferencas para a E3 (e3_05_boca.py):
- pesos da pele CONTINUOS: os labios convergem para 0,5 nas comissuras (a abertura afina ate a comissura, sem rasgo),
  e atras da comissura a faixa de transicao alarga ate a articulacao (bochecha estica como tecido);
  largura da mandibula medida no proprio labio inferior;
- labio com margem enrolada (fina e escura) -> gengiva com crista -> palato/assoalho em arco ate a garganta;
- bochechas internas como membrana com pesos graduados e curvatura (nao um quad plano);
- cavidade mantida DENTRO da pele (afastamento minimo medido contra a pele em repouso);
- denticao de leao por tipo (I1-I3, canino curvo, P2-P4/M1 em lamina), raizes na gengiva, bolsos para os caninos;
- lingua apoiada no assoalho (base afundada, espessura, sulco), com osso proprio para movimento discreto.
Uso: blender -b Leao_Solar_Ref_E3_t2.blend -P c02_boca.py -- <saida.blend>"""
import bpy, bmesh, sys, math
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E")][0]; me = ob.data
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
# ------------------------------------------------------------------ medidas (as mesmas da E3, medidas na v11)
COMIS = V((0, -13.96, 12.23)); FRENTE = V((0, -15.33, 12.43))
d_ = FRENTE - COMIS; NUP = V((0, -d_.z, d_.y)).normalized()
if NUP.z < 0: NUP = -NUP
def sd(p): return (p - FRENTE).dot(NUP)
Y_COMIS = COMIS.y
def z_plano(y): return FRENTE.z + (y - FRENTE.y) * (d_.z / d_.y)
H = V((0, -12.75, z_plano(-12.75) + 0.30)); QUEIXO = V((0, -15.15, 11.95))
def plano(v): return v - NUP * v.dot(NUP)
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
# ------------------------------------------------------------------ 1. fenda (igual a E3)
def na_boca(c): return c.y < Y_COMIS + 0.02 and abs(c.x) < 1.9 and abs(sd(c)) < 0.35 and c.z > 11.4
reg = [f for f in bm.faces if na_boca(f.calc_center_median())]
geom = list({v for f in reg for v in f.verts}) + list({e for f in reg for e in f.edges}) + reg
cut = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=FRENTE, plane_no=NUP, dist=1e-5)["geom_cut"]
cut_e = [e for e in cut if isinstance(e, bmesh.types.BMEdge) and all(v.co.y < Y_COMIS + 0.02 for v in e.verts)]
bmesh.ops.split_edges(bm, edges=cut_e)
bm.edges.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.normal_update()
fenda = [e for e in bm.edges if e.is_boundary and all(v.co.y < Y_COMIS + 0.05 and abs(sd(v.co)) < 0.02 for v in e.verts)]
def lado(e): return 1 if sd(e.link_faces[0].calc_center_median()) > 0 else -1
def cadeia(edges):
    adj = {}
    for e in edges:
        a, b = e.verts; adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    pontas = [v for v, l in adj.items() if len(l) == 1]
    ini = min(pontas, key=lambda v: v.co.x); cam = [ini]; vis = {ini}
    while True:
        prox = [w for w in adj[cam[-1]] if w not in vis]
        if not prox: break
        cam.append(prox[0]); vis.add(prox[0])
    return cam
U = cadeia([e for e in fenda if lado(e) > 0]); D = cadeia([e for e in fenda if lado(e) < 0])
print("FENDA", len(fenda), "sup", len(U), "inf", len(D), "comissuras compartilhadas", U[0] is D[0], U[-1] is D[-1])
assert U[0] is D[0] and U[-1] is D[-1]
# suaviza a linha dos labios NO PLANO (mesma operacao nos dois labios, que seguem coincidentes): tira os degraus do corte
desl = 0.0
for _ in range(7):
    for cam in (U, D):
        novo = [cam[i].co + 0.5 * plano((cam[i - 1].co + cam[i + 1].co) / 2 - cam[i].co) for i in range(1, len(cam) - 1)]
        for i, p in enumerate(novo, 1): desl = max(desl, (p - cam[i].co).length); cam[i].co = p
print("LABIOS suavizados, maior deslocamento por passo", round(desl, 3))
bm.normal_update()
XM = (U[0].co.x + U[-1].co.x) / 2                         # linha media real do focinho (a malha do Meshy e assimetrica)
pele_faces = list(bm.faces)
bvh_pele = BVHTree.FromPolygons([v.co.copy() for v in bm.verts], [[v.index for v in f.verts] for f in pele_faces])
loc, nor, _, _ = bvh_pele.find_nearest(V((0, -14.6, 13.0)))
assert (V((0, -14.6, 13.0)) - loc).dot(nor) < 0, "normais da pele nao apontam para fora"
# ------------------------------------------------------------------ 2. pesos da pele (campo continuo)
SU, SD_ = set(U), set(D)
yd = [(v.co.y, v.co.x - XM) for v in D]
def x_labio(y, lado_):
    """meia-largura da mandibula na altura y, do lado do vertice = largura do labio inferior (medida na propria malha)"""
    com = abs((U[0] if lado_ < 0 else U[-1]).co.x - XM)
    if y >= Y_COMIS: return com
    perto = [abs(x) for (yy, x) in yd if abs(yy - y) < 0.10 and x * lado_ > 0]
    return max(perto) if perto else com
def s_vert(v):
    if v in SU and v not in SD_: return 0.02
    if v in SD_ and v not in SU: return -0.02
    s = sd(v.co)
    if abs(s) < 0.03 and v.link_faces: s = sum(sd(f.calc_center_median()) for f in v.link_faces) / len(v.link_faces)
    return s
Yg = -12.85                                                 # garganta (antes da articulacao em -12,75)
LT = 1.0                                                    # trecho do labio antes da comissura em que a abertura afina
WC = 0.6                                                    # peso na comissura (>0,5: o labio superior desce junto, como as bochechas)
def w_pele(p, s):
    if p.y < Y_COMIS:
        t = suave((p.y - (Y_COMIS - LT)) / LT); f = 1 - suave(abs(s) / 0.5)
        w = 1 - (1 - WC) * t * f if s < 0 else WC * t * f
    else:
        b = 0.5 + 0.9 * suave((p.y - Y_COMIS) / 1.0); a_ = suave(abs(s) / b)
        w = (WC + (1 - WC) * a_ if s < 0 else WC * (1 - a_)) if abs(s) > 1e-6 else WC
        w *= suave((-12.15 - p.y) / 0.6)                    # atras da articulacao: nao acompanha
    xl = x_labio(p.y, 1 if p.x > XM else -1); dx = abs(p.x - XM)
    if s < 0 and p.y < Yg + 0.15 and dx < xl + 0.05:        # pele/barba SOB o assoalho: acompanha a mandibula inteira
        w = max(w, 1 - suave((p.y - (Yg - 0.35)) / 0.5))   # (senao o assoalho atravessa a barba ao abrir)
    w *= suave((xl + 0.45 - dx) / 0.45)                     # bochecha/juba lateral: so ate a largura da mandibula
    barba = 0.35 + 0.65 * suave((p.z - 11.2) / 0.7)
    w *= lerp(suave((p.z - 10.3) / 0.8), barba, suave((p.y - (Yg - 0.35)) / 0.5))   # barba do queixo acompanha; pescoco, parcial
    w *= suave((p.z - 9.9) / 0.9)
    return w
w = {}
roi = [v for v in bm.verts if v.co.y < -11.6 and v.co.z > 9.6 and abs(v.co.x) < 2.6]
for v in bm.verts: w[v] = 0.0
for v in roi: w[v] = w_pele(v.co, s_vert(v))
for _ in range(5):                                          # suavizacao (a fenda separa os labios na topologia)
    nw = {}
    for v in roi:
        viz = [e.other_vert(v) for e in v.link_edges]
        nw[v] = 0.5 * w[v] + 0.5 * sum(w[x] for x in viz) / max(len(viz), 1)
    for v in roi:
        if v.co.y < Y_COMIS - LT - 0.1 and abs(sd(v.co)) < 0.06: continue   # labios da frente: 0 / 1 exatos
        w[v] = nw[v]
for v in (U[0], U[-1]): w[v] = WC
# ------------------------------------------------------------------ 3. cavidade (posicoes primeiro, malha depois)
def reamostrar(pts, M):
    L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + (b - a).length)
    out = []
    for k in range(M):
        alvo = L[-1] * k / (M - 1)
        for i in range(len(pts) - 1):
            if L[i + 1] >= alvo - 1e-9:
                t = (alvo - L[i]) / max(L[i + 1] - L[i], 1e-9); out.append(lerp(pts[i], pts[i + 1], t)); break
    return out
M, R, C = 17, 9, 3                                          # E4: versao leve (malha de jogo)
def coluna_info(cam):
    """amostras do labio + direcao "para dentro" = perpendicular ao labio (alisado) no plano, apontando para o centro da boca
    (a normal da pele junto ao corte e ruidosa: em trechos quase horizontais ela fazia a margem atravessar o proprio labio)"""
    base = reamostrar([v.co.copy() for v in cam], M); nb, wl = [], []
    lis = [p.copy() for p in base]
    for _ in range(10): lis = [lis[0]] + [0.5 * lis[i] + 0.25 * (lis[i - 1] + lis[i + 1]) for i in range(1, M - 1)] + [lis[-1]]
    cen = sum(base, V()) / M
    for j, p in enumerate(base):
        v = min(cam, key=lambda x: (x.co - p).length_squared)
        tg = plano(lis[min(j + 1, M - 1)] - lis[max(j - 1, 0)]).normalized(); n = NUP.cross(tg).normalized()
        if n.dot(plano(cen - p)) < 0: n = -n
        nb.append(n); wl.append(w[v])
    return base, nb, wl
Ub, Unb, Uw = coluna_info(U); Db, Dnb, Dw = coluna_info(D)
JC = min(range(M), key=lambda j: abs(Ub[j].x - XM) + 2 * max(0.0, Ub[j].y + 15.0))
print("LINHA MEDIA x", round(XM, 3), "JC", JC, tuple(round(c, 2) for c in Ub[JC]))
G = [V((XM + lerp(-0.36, 0.36, j / (M - 1)), Yg, z_plano(Yg))) for j in range(M)]
def dist_centro(base):
    L = [0.0]
    for a, b in zip(base, base[1:]): L.append(L[-1] + (b - a).length)
    return [abs(L[j] - L[JC]) for j in range(M)]
ARO = [(0.05, 0.040), (0.12, 0.090), (0.24, 0.105), (0.37, 0.065)]   # (para dentro, para cima/baixo): margem -> gengiva
def superficie(base, nb, sinal, alt, bolso_d, bolso_a):
    dc = dist_centro(base); P = []
    for r in range(1, 5):
        ins, lev = ARO[r - 1]; lin = []
        for j in range(M):
            lv = lev + (bolso_a * math.exp(-((dc[j] - bolso_d) / 0.10) ** 2) if r >= 2 else 0)
            if j in (0, M - 1): lv *= 0.5
            lin.append(base[j] + nb[j] * ins + NUP * (sinal * lv))
        P.append(lin)
    for r in range(5, R + 1):
        u = (r - 4) / (R - 3); lin = []
        for j in range(M):
            s = j / (M - 1)
            prof = alt * math.sin(math.pi * u) ** 0.55 * (1 + (0.35 * u if sinal < 0 else 0))   # abobada; assoalho mais fundo atras
            p = lerp(P[3][j], G[j], u ** 0.9) + NUP * (sinal * prof * math.sin(math.pi * s) ** 0.45)
            lin.append(p)
        P.append(lin)
    return P
PAL = superficie(Ub, Unb, +1, 0.46, 0.44, 0.16)            # bolso do palato para o canino inferior
ASS = superficie(Db, Dnb, -1, 0.34, 0.55, 0.18)            # bolso do assoalho para o canino superior
MARG = 0.07
DIRS = [V((0.31, 0.05, 0.95)).normalized(), V((-0.6, -0.7, 0.38)).normalized(), V((0.7, -0.2, -0.68)).normalized()]
def dentro(p):
    """paridade de intersecoes com a pele (repouso, labios coincidentes = casca fechada), voto em 3 direcoes"""
    votos = 0
    for dv in DIRS:
        n, q = 0, p.copy()
        for _ in range(60):
            hit = bvh_pele.ray_cast(q, dv, 40.0)
            if hit[0] is None: break
            n += 1; q = hit[0] + dv * 1e-4
        votos += n % 2
    return votos >= 2
def manter_dentro(p, direcao, marg=MARG):
    """se o ponto esta fora da pele (paridade) ou a menos de marg dela, anda na direcao dada ate ficar dentro com folga"""
    q = p.copy()
    for _ in range(40):
        loc, nor, _, dd = bvh_pele.find_nearest(q)
        if dentro(q) and dd >= marg: return q
        q = q + direcao * 0.015
    return q
def suavizar(P, rows):
    for _ in range(3):
        Q = [[p.copy() for p in lin] for lin in P]
        for r in rows:
            for j in range(1, M - 1):
                viz = [P[r][j - 1], P[r][j + 1]] + ([P[r - 1][j]] if r - 1 >= 0 else []) + ([P[r + 1][j]] if r + 1 < len(P) else [G[j]])
                Q[r][j] = 0.5 * P[r][j] + 0.5 * sum(viz, V()) / len(viz)
        for r in rows: P[r] = Q[r]
MOV = 0
for P, dz in ((PAL, -NUP), (ASS, NUP)):
    suavizar(P, range(4, R))
    for _ in range(2):
        for r in range(2, R):
            for j in range(M):
                q = manter_dentro(P[r][j], dz); MOV += (q - P[r][j]).length > 1e-6; P[r][j] = q
        suavizar(P, range(4, R))
for P, nbs in ((PAL, Unb), (ASS, Dnb)):                  # margem do labio (fileiras 1-2): dentro da pele, recuando para a boca
    for r in (0, 1):
        for j in range(1, M - 1):
            q = manter_dentro(P[r][j], nbs[j], 0.015); MOV += (q - P[r][j]).length > 1e-6; P[r][j] = q
OFF = [V((0, 0, 0)), V((0.09, 0, 0)), V((-0.09, 0, 0)), V((0, 0.09, 0)), V((0, -0.09, 0))]
def folga_dir(p, dv, alcance=0.8):
    """menor distancia ate a pele na direcao dv, amostrada em volta do ponto (a dobra sob o queixo e estreita)"""
    m = alcance
    for o in OFF:
        hit = bvh_pele.ray_cast(p + o, dv, alcance)
        if hit[0] is not None: m = min(m, hit[3])
    return m
FOLGA_V = 0.10; SUB = 0
for _ in range(3):                                          # folga vertical: assoalho acima da dobra da barba, palato abaixo do focinho
    for P, dv in ((ASS, -NUP), (PAL, NUP)):
        for r in range(2, R):
            for j in range(M):
                g_ = folga_dir(P[r][j], dv)
                if g_ < FOLGA_V: P[r][j] = P[r][j] - dv * (FOLGA_V - g_); SUB += 1
    for P in (PAL, ASS): suavizar(P, range(4, R))
print("CAVIDADE vertices recolocados para dentro da pele:", MOV, "| ajustados por folga vertical:", SUB)
# pesos do interior: margem herda o labio, gengiva e fundo sao rigidos
# perto das comissuras o labio so abre em parte (peso -> 0,5): a gengiva/mucosa atras dele acompanha o labio e vai
# ficando rigida para dentro (senao o assoalho cai inteiro e aparece por fora da comissura como uma aba escura)
QUEDA = [0.8, 0.6, 0.42, 0.28, 0.16, 0.08]
def fall(r): return QUEDA[r - 1] if r <= len(QUEDA) else 0.0
def w_pal(r, j): return Uw[j] * fall(r)
def w_ass(r, j): return 1 - (1 - Dw[j]) * fall(r)
# bochechas internas (membrana graduada entre a coluna lateral do palato e a do assoalho)
PAREDE = {}
for j in (0, M - 1):
    lat = V((-1 if j == 0 else 1, 0, 0)); lat = plano(lat).normalized()
    cols = []
    for k in range(1, R + 1):
        pp, pf = PAL[k - 1][j], ASS[k - 1][j]; wp, wf = w_pal(k, j), w_ass(k, j); lin = []
        for c in range(1, C + 1):
            t = c / (C + 1)
            junto = suave((k - 1) / 3.0)                      # 0 na comissura -> 1 a partir da 4a fileira
            p = lerp(pp, pf, t) + lat * (0.10 * math.sin(math.pi * t) * math.sin(math.pi * k / (R + 1)) ** 0.6 * junto
                                         - 0.05 * math.sin(math.pi * t) * (1 - junto))
            lin.append((manter_dentro(p, -lat) if k >= 2 else p, lerp(wp, wf, t)))
        cols.append(lin)
    for _ in range(3):                                      # suaviza a membrana (sem dobras) e volta a garantir que fica dentro
        novo = [[q for q, _ in lin] for lin in cols]
        for k in range(1, R - 1):
            for c in range(C):
                cima = cols[k][c - 1][0] if c > 0 else PAL[k][j]; baixo = cols[k][c + 1][0] if c < C - 1 else ASS[k][j]
                viz = [cols[k - 1][c][0], cols[k + 1][c][0], cima, baixo]
                novo[k][c] = 0.5 * cols[k][c][0] + 0.5 * sum(viz, V()) / 4
        cols = [[(manter_dentro(novo[k][c], -lat) if k >= 1 else novo[k][c], cols[k][c][1]) for c in range(C)] for k in range(R)]
    PAREDE[j] = cols
# ------------------------------------------------------------------ 4. malha do interior
mat_boca = len(me.materials)
cor, peso = {}, {}
def nv(p, c, wt):
    v = bm.verts.new(p); cor[v] = c; peso[v] = wt; return v
def cor_pal(r, j, dc):
    if r == 1: return (46, 28, 26)
    if r == 2: return (112, 50, 54)
    if r == 3: return (182, 92, 98)
    if r == 4: return (164, 76, 84)
    u = (r - 4) / (R - 3); base = (152, 68, 76) if (r % 2 == 0) else (134, 56, 64)   # rugas do palato
    return tuple(int(lerp(c0, c1, u ** 1.4)) for c0, c1 in zip(base, (52, 16, 22)))
def cor_ass(r, j, dc):
    if r == 1: return (46, 28, 26)
    if r == 2: return (112, 50, 54)
    if r == 3: return (180, 90, 96)
    if r == 4: return (160, 74, 82)
    u = (r - 4) / (R - 3)
    return tuple(int(lerp(c0, c1, u ** 1.4)) for c0, c1 in zip((146, 62, 70), (50, 15, 20)))
dcU, dcD = dist_centro(Ub), dist_centro(Db)
gv = [nv(p, (34, 10, 14), 0.5) for p in G]
def canto(c, j, wl_):
    """perto das comissuras a margem e a dobra interna (mucosa escura), nao a borda preta do labio"""
    k = suave(abs(wl_ - (0.0 if wl_ < 0.5 else 1.0)) / 0.25)
    return tuple(int(lerp(a, b, k)) for a, b in zip(c, (112, 48, 56))) if c[0] < 120 else c
VP = [[nv(PAL[r][j], canto(cor_pal(r + 1, j, dcU[j]), j, Uw[j]), w_pal(r + 1, j)) for j in range(M)] for r in range(R)]
VA = [[nv(ASS[r][j], canto(cor_ass(r + 1, j, dcD[j]), j, Dw[j]), w_ass(r + 1, j)) for j in range(M)] for r in range(R)]
VW = {}
for j, cols in PAREDE.items():
    VW[j] = []
    for k, lin in enumerate(cols):
        u = k / R
        cw = (112, 48, 56) if k == 0 else tuple(int(lerp(c0, c1, u ** 1.2)) for c0, c1 in zip((132, 54, 62), (48, 15, 20)))
        VW[j].append([nv(p, cw, wt) for p, wt in lin])
novas = []
def face(vs):
    vs = [x for i_, x in enumerate(vs) if x not in vs[:i_]]
    if len(vs) < 3: return
    try: f = bm.faces.new(vs); f.material_index = mat_boca; novas.append(f)
    except ValueError: pass
def zipper(a, b):
    i = j = 0
    while i < len(a) - 1 or j < len(b) - 1:
        ta = (i + 1) / (len(a) - 1) if i < len(a) - 1 else 9; tb = (j + 1) / (len(b) - 1) if j < len(b) - 1 else 9
        if ta <= tb: face([a[i], a[i + 1], b[j]]); i += 1
        else: face([a[i], b[j + 1], b[j]]); j += 1
def grade(l1, l2):
    for j in range(len(l1) - 1): face([l1[j], l1[j + 1], l2[j + 1], l2[j]])
for cam, VV in ((U, VP), (D, VA)):
    zipper(cam, VV[0])
    for a, b in zip(VV, VV[1:]): grade(a, b)
    grade(VV[-1], gv)
for j in (0, M - 1):
    canto = U[0] if j == 0 else U[-1]
    linhas = [[canto]] + [[VP[k][j]] + VW[j][k] + [VA[k][j]] for k in range(R)] + [[gv[j]]]
    for a, b in zip(linhas, linhas[1:]):
        if len(a) == 1:
            for x, y in zip(b, b[1:]): face([a[0], x, y])
        elif len(b) == 1:
            for x, y in zip(a, a[1:]): face([x, y, b[0]])
        else: grade(a, b)
# orientacao: normal para dentro da cavidade
bm.normal_update()
S_W = {v for cols in VW.values() for lin in cols for v in lin}; S_P = {v for lin in VP for v in lin} | (SU - SD_)
for f in novas:
    c = f.calc_center_median(); vs = set(f.verts)
    if vs & S_W: alvo = V((XM - c.x, 0, 0))
    elif vs & S_P: alvo = -NUP
    else: alvo = NUP
    if f.normal.dot(alvo) < 0: f.normal_flip()
for f in novas: f.smooth = True
for e in bm.edges:
    if len({f.material_index for f in e.link_faces}) > 1: e.smooth = False
print("INTERIOR faces", len(novas), "verts", len(peso))
for v, x in peso.items(): w[v] = x
# ------------------------------------------------------------------ 5. dentes e lingua (objetos proprios)
bm.verts.index_update(); bm.to_mesh(me); me.update()
mats = bpy.data.materials.new("M_Leao_Boca"); mats.use_nodes = True
nt = mats.node_tree; bs = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "CorBoca"; nt.links.new(vc.outputs["Color"], bs.inputs["Base Color"])
bs.inputs["Roughness"].default_value = 0.55; bs.inputs["Specular IOR Level"].default_value = 0.30
me.materials.append(mats)
md = bpy.data.materials.new("M_Leao_Dentes"); md.use_nodes = True
nt = md.node_tree; bs = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "CorBoca"; nt.links.new(vc.outputs["Color"], bs.inputs["Base Color"])
bs.inputs["Roughness"].default_value = 0.35; bs.inputs["Specular IOR Level"].default_value = 0.45
at = me.color_attributes.new("CorBoca", "BYTE_COLOR", "POINT")
idx = {v.index: c for v, c in cor.items()}
for i in range(len(me.vertices)):
    c = idx.get(i, (46, 28, 26)); at.data[i].color_srgb = (c[0] / 255, c[1] / 255, c[2] / 255, 1)
ga = ob.vertex_groups.new(name="Mandibula"); gc = ob.vertex_groups.new(name="Cabeca")
wi = {v.index: x for v, x in w.items()}
for i in range(len(me.vertices)):
    x = wi.get(i, 0.0)
    if x > 1e-4: ga.add([i], x, "REPLACE")
    if x < 1 - 1e-4: gc.add([i], 1 - x, "REPLACE")
gp = ob.vertex_groups.new(name="Boca_Profundo")
prof = [v.index for lin in VP[2:] + VA[2:] for v in lin] + [v.index for cols in VW.values() for lin in cols[2:] for v in lin]
gp.add(prof, 1.0, "REPLACE")
print("PESOS mandibula>0.5:", sum(1 for x in wi.values() if x > 0.5), "transicao:", sum(1 for x in wi.values() if 0.05 < x < 0.95))
def objeto(nome, vs, fs, cores, grupos, mat):
    m = bpy.data.meshes.new(nome); m.from_pydata([tuple(p) for p in vs], [], fs); o = bpy.data.objects.new(nome, m)
    for c in ob.users_collection: c.objects.link(o)
    b2 = bmesh.new(); b2.from_mesh(m); bmesh.ops.recalc_face_normals(b2, faces=b2.faces); b2.to_mesh(m); b2.free()
    for p in m.polygons: p.use_smooth = True
    a = m.color_attributes.new("CorBoca", "BYTE_COLOR", "POINT")
    for i, c in enumerate(cores): a.data[i].color_srgb = (c[0] / 255, c[1] / 255, c[2] / 255, 1)
    m.materials.append(mat)
    for gname, ws in grupos.items():
        g = o.vertex_groups.new(name=gname)
        for i, x in enumerate(ws):
            if x > 1e-4: g.add([i], x, "REPLACE")
    return o
def arcada(P3, d, lado_):
    """ponto da crista da gengiva a distancia d (ao longo do arco) do centro, para o lado -1 (X-) ou +1 (X+)"""
    L = [0.0]
    for a, b in zip(P3, P3[1:]): L.append(L[-1] + (b - a).length)
    alvo = L[JC] + lado_ * d; alvo = max(0.0, min(L[-1], alvo))
    for i in range(M - 1):
        if L[i + 1] >= alvo:
            t = (alvo - L[i]) / max(L[i + 1] - L[i], 1e-9); p = lerp(P3[i], P3[i + 1], t)
            tg = plano(P3[min(i + 2, M - 1)] - P3[max(i - 1, 0)]).normalized(); return p, tg, i
    return P3[-1], plano(P3[-1] - P3[-3]).normalized(), M - 2
def alisar_arco(P3, n=12):
    """arcada alisada (o corte do labio e a gengiva tem degraus): so para posicionar e orientar os dentes"""
    Q = [p.copy() for p in P3]
    for _ in range(n): Q = [Q[0]] + [0.5 * Q[i] + 0.25 * (Q[i - 1] + Q[i + 1]) for i in range(1, M - 1)] + [Q[-1]]
    return Q
POST = plano(V((0, 1, 0))).normalized(); AJUSTE = []
def dentes(P3, nbs, sinal, tabela, nome, grupo):
    vs, fs, cs = [], [], []
    SEG, K = 6, 4
    for lado_ in (-1, 1):
        for (d, L_, wt, wo, curva, ponta, incl) in tabela:
            raiz, tg, i = arcada(P3, d, lado_)
            fora = NUP.cross(tg).normalized()                 # perpendicular ao arco, no plano, para o lado do labio
            if fora.dot(-nbs[i]) < 0: fora = -fora
            eixo = (-NUP * sinal + fora * incl).normalized()
            raiz = raiz + NUP * (sinal * 0.05)
            n0 = len(vs)
            def gerar(raiz, L_):
                tv = []
                for k in range(K):
                    h = k / K; esc = (1 - h ** ponta) ** 0.55
                    c = raiz + eixo * ((L_ + 0.05) * h) + POST * (curva * h * h)
                    for a in range(SEG):
                        ang = 2 * math.pi * a / SEG
                        tv.append(c + tg * (math.cos(ang) * wt * esc) + fora * (math.sin(ang) * wo * esc))
                return tv + [raiz + eixo * (L_ + 0.05) + POST * curva, raiz - eixo * 0.03]
            def folga(tv):                                   # menor distancia para dentro da pele (fechada = repouso); fora = negativa
                m = 9.0
                for q in tv:
                    loc, nor, _, _ = bvh_pele.find_nearest(q); dd = (q - loc).length
                    m = min(m, dd if dentro(q) else -dd)
                return m
            tv = gerar(raiz, L_); passos = 0
            while folga(tv) < 0.03 and passos < 10:          # aflora com a boca fechada: recua para dentro, depois encurta
                if passos < 6: raiz = raiz - fora * 0.02
                else: L_ *= 0.88
                tv = gerar(raiz, L_); passos += 1
            if passos: AJUSTE.append((nome, round(d, 2), lado_, passos, round(folga(tv), 3)))
            vs += tv; cs += [k / K for k in range(K) for _ in range(SEG)] + [1.0, 0.0]
            pt, rz = len(vs) - 2, len(vs) - 1
            for k in range(K - 1):
                for a in range(SEG):
                    a2 = (a + 1) % SEG; fs.append((n0 + k * SEG + a, n0 + k * SEG + a2, n0 + (k + 1) * SEG + a2, n0 + (k + 1) * SEG + a))
            for a in range(SEG):
                a2 = (a + 1) % SEG
                fs.append((n0 + (K - 1) * SEG + a, n0 + (K - 1) * SEG + a2, pt)); fs.append((n0 + a2, n0 + a, rz))
    cores = [tuple(int(lerp(c0, c1, h ** 0.7)) for c0, c1 in zip((196, 172, 132), (244, 238, 222))) for h in cs]
    return objeto(nome, vs, fs, cores, {grupo: [1.0] * len(vs)}, md)
# (distancia do centro, comprimento exposto, meia-largura no arco, meia-espessura, curvatura para tras, ponta, inclinacao p/ fora)
SUP = [(0.07, 0.11, 0.050, 0.040, 0.00, 1.3, 0.00), (0.18, 0.12, 0.054, 0.042, 0.00, 1.3, 0.00),
       (0.31, 0.19, 0.068, 0.055, 0.02, 1.6, 0.05),
       (0.52, 0.42, 0.105, 0.088, 0.07, 1.9, 0.10),
       (0.80, 0.05, 0.040, 0.036, 0.00, 1.4, 0.00), (0.98, 0.13, 0.090, 0.050, 0.01, 1.0, 0.03), (1.24, 0.16, 0.135, 0.056, 0.02, 1.0, 0.03)]
INF = [(0.06, 0.09, 0.046, 0.038, 0.00, 1.3, 0.00), (0.16, 0.10, 0.050, 0.040, 0.00, 1.3, 0.00), (0.26, 0.12, 0.055, 0.044, 0.00, 1.4, 0.00),
       (0.42, 0.34, 0.095, 0.082, 0.06, 1.9, 0.08),
       (0.86, 0.09, 0.075, 0.046, 0.01, 1.0, 0.02), (1.06, 0.12, 0.100, 0.050, 0.01, 1.0, 0.02), (1.28, 0.14, 0.120, 0.054, 0.02, 1.0, 0.02)]
P3U = alisar_arco(PAL[2])
P3D = alisar_arco([p - (p - V((XM, p.y, p.z))).normalized() * (0.05 + 0.08 * suave((dd - 0.30) / 0.5)) if abs(p.x - XM) > 0.1 else p
                   for p, dd in zip(ASS[2], dist_centro(ASS[2]))])          # arcada inferior por dentro da superior (mordida em tesoura)
def d_mais_perto(P3, alvo, lado_):
    melhor = min((abs(dd) for dd in [k * 0.01 for k in range(0, 250)]), key=lambda dd: (arcada(P3, dd, lado_)[0] - alvo).length)
    return melhor
for lado_ in (-1, 1):                                        # canino inferior entre o I3 e o canino superiores (encaixe ao fechar)
    alvo = lerp(arcada(P3U, 0.52, lado_)[0], arcada(P3U, 0.31, lado_)[0], 0.55)
    print("CANINO inferior lado", lado_, "d =", d_mais_perto(P3D, alvo, lado_))   # arcada inferior por dentro da superior
print("ARCADA meia-length sup", round(dist_centro(P3U)[0], 3), round(dist_centro(P3U)[-1], 3), "inf", round(dist_centro(P3D)[0], 3))
dentes(P3U, Unb, +1, SUP, "Leao_Dentes_Sup", "Cabeca"); dentes(P3D, Dnb, -1, INF, "Leao_Dentes_Inf", "Mandibula")
print("DENTES ajustados (nome, dist, lado, passos, folga):", AJUSTE)
# lingua: estacoes ao longo da linha media do assoalho; ventre afundado no assoalho, dorso limitado pelo palato (boca fechada)
me.calc_loop_triangles()
fl = [t for t in me.loop_triangles if me.polygons[t.polygon_index].material_index == mat_boca and all(wi.get(i, 0) > 0.9 for i in t.vertices)]
fp = [t for t in me.loop_triangles if me.polygons[t.polygon_index].material_index == mat_boca and all(wi.get(i, 1) < 0.1 for i in t.vertices)]
bvh_ass = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [list(t.vertices) for t in fl])
bvh_pal = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [list(t.vertices) for t in fp])
meio = [ASS[r][JC] for r in range(3, R)] + [G[JC]]
caminho = reamostrar(meio, 101)
N, KX = 11, 7
f0, f1 = 0.10, 0.84                                          # ponta logo atras dos incisivos ... raiz antes da garganta
def chao(p):
    hit = bvh_ass.ray_cast(p + NUP * 0.5, -NUP, 1.5)
    return hit[0] if hit[0] is not None else None
def teto(p):
    hit = bvh_pal.ray_cast(p, NUP, 1.5)
    return hit[0] if hit[0] is not None else None
def construir(esc):
    vs, cs, wl = [], [], []; aneis = []; min_folga = 9
    for i in range(N):
        f = i / (N - 1); c = caminho[int(round(lerp(f0, f1, f) * 100))]
        hw = (0.13 + 0.25 * suave(f / 0.35) - 0.04 * suave((f - 0.7) / 0.3)) * esc[i]   # meia-largura
        th = 0.08 + 0.18 * suave(f / 0.32) - 0.26 * suave((f - 0.70) / 0.30)       # espessura acima do assoalho
        anel = []; base_c = chao(c) or c
        for k in range(KX + 1):                                   # dorso, de X- para X+
            x = -hw + 2 * hw * k / KX; q = max(1 - (x / hw) ** 2, 0)
            fl_ = chao(c + V((x, 0, 0))) or (base_c + V((x, 0, 0)))
            top = fl_ + NUP * (th * q ** 0.75 - 0.025 * math.exp(-(x / 0.06) ** 2) * suave(f / 0.25) * suave((0.8 - f) / 0.2))
            tt = teto(fl_)
            if tt is not None:
                lim = (tt - fl_).dot(NUP) - 0.05
                if (top - fl_).dot(NUP) > lim: top = fl_ + NUP * max(lim, 0.0)
                min_folga = min(min_folga, (tt - top).dot(NUP))
            anel.append(top); cs.append(0)
        for k in range(KX - 1, 0, -1):                            # ventre, de volta (abaixo do assoalho)
            x = -hw + 2 * hw * k / KX
            fl_ = chao(c + V((x * 0.85, 0, 0))) or (base_c + V((x * 0.85, 0, 0)))
            afund = max(0.0, min(0.07, folga_dir(fl_, -NUP) - 0.05))
            anel.append(fl_ - NUP * afund); cs.append(1)
        aneis.append(anel); vs += anel; wl += [1 - f] * len(anel)
    return vs, cs, wl, aneis, min_folga
dentes_bvh = []
for nome_ in ("Leao_Dentes_Sup", "Leao_Dentes_Inf"):
    m_ = bpy.data.objects[nome_].data; m_.calc_loop_triangles()
    dentes_bvh.append(BVHTree.FromPolygons([v.co.copy() for v in m_.vertices], [list(t.vertices) for t in m_.loop_triangles]))
esc = [1.0] * N
for it in range(10):                                         # a lingua nao pode tocar os dentes: estreita as estacoes que tocam
    vs, cs, wl, aneis, min_folga = construir(esc); NA_ = len(aneis[0])
    quads = [(i * NA_ + k, i * NA_ + (k + 1) % NA_, (i + 1) * NA_ + (k + 1) % NA_, (i + 1) * NA_ + k) for i in range(N - 1) for k in range(NA_)]
    bl_ = BVHTree.FromPolygons(vs, quads); toca = {quads[a][0] // NA_ for b_ in dentes_bvh for a, _ in bl_.overlap(b_)}
    if not toca: break
    for i in toca:
        for i2, fat in ((i, 0.88), (i + 1, 0.94), (i - 1, 0.94)):
            if 0 <= i2 < N: esc[i2] *= fat
print("LINGUA ajuste de largura: iteracoes", it, "escala minima", round(min(esc), 2), "estacoes tocando no fim", len(toca))
NA = len(aneis[0]); fs = []
for i in range(N - 1):
    for k in range(NA):
        k2 = (k + 1) % NA; fs.append((i * NA + k, i * NA + k2, (i + 1) * NA + k2, (i + 1) * NA + k))
c0 = sum(aneis[0], V()) / NA; dirp = plano(aneis[0][KX // 2] - aneis[1][KX // 2]).normalized()
vs.append(c0 + dirp * 0.07 + NUP * 0.02); cs.append(0); wl.append(1.0); pt = len(vs) - 1
c1 = sum(aneis[-1], V()) / NA - NUP * 0.04; vs.append(c1); cs.append(1); wl.append(0.0); rz = len(vs) - 1
for k in range(NA):
    k2 = (k + 1) % NA; fs.append((k2, k, pt)); fs.append(((N - 1) * NA + k, (N - 1) * NA + k2, rz))
cores = []
for i, (c, x) in enumerate(zip(cs, wl)):
    if c: cores.append((132, 52, 60)); continue
    k = i % NA; lat = abs(k - KX / 2) / (KX / 2)              # bordas mais escuras, centro do dorso mais claro
    cores.append(tuple(int(lerp(lerp(a, b, x ** 1.2), e, lat ** 2 * 0.6)) for a, b, e in zip((168, 72, 82), (212, 118, 124), (150, 60, 70))))
wlin = [0.85 * suave((x - 0.15) / 0.75) for x in wl]      # osso Lingua: ponta 85%, raiz 0
objeto("Leao_Lingua", vs, fs, cores, {"Lingua": wlin, "Mandibula": [1 - x for x in wlin]}, mats)
zs = [(q - FRENTE).dot(NUP) for q in vs]
print("LINGUA verts", len(vs), "altura sobre o plano min/max", round(min(zs), 3), round(max(zs), 3), "folga min ao palato", round(min_folga, 3))
# ------------------------------------------------------------------ 6. armature de teste
arm_d = bpy.data.armatures.new("Leao_Rig_Teste_Boca"); arm = bpy.data.objects.new("Leao_Rig_Teste_Boca", arm_d)
for c in ob.users_collection: c.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT")
bc = arm_d.edit_bones.new("Cabeca"); bc.head = (0, -11.0, 13.4); bc.tail = (0, -13.4, 14.6)
bmd = arm_d.edit_bones.new("Mandibula"); bmd.head = H; bmd.tail = QUEIXO; bmd.roll = 0; bmd.parent = bc
bl = arm_d.edit_bones.new("Lingua"); bl.head = caminho[int(f1 * 100)]; bl.tail = caminho[int(f0 * 100)]; bl.roll = 0; bl.parent = bmd
bpy.ops.object.mode_set(mode="OBJECT")
for o in [ob] + [x for x in bpy.data.objects if x.name.startswith(("Leao_Lingua", "Leao_Dentes"))]:
    mo = o.modifiers.new("Armature", "ARMATURE"); mo.object = arm
print("BOCA_OK")
bpy.ops.wm.save_as_mainfile(filepath=A[0])
