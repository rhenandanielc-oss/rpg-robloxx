"""v5: correcao dos OLHOS e das LATERAIS DA BOCA sobre low_ref2/ (v4 em low_v4/ preservada). Depois roda-se ajuste_r3.py.
- OLHOS: a pele em volta da fenda e REFEITA como anel limpo (40 colunas x 5 aneis em elipse), sem triangulos longos;
  globo menor e RECUADO na orbita (a margem passa 0,016 por fora dele); textura do anel reamostrada da pele original
  num remendo proprio da UV (sem a tinta azul do Meshy, borda palpebral fina cinza-escura, normal suavizada perto do
  olho = sulcos atenuados so ali). Palpebras: pesos por coluna (cada coluna fecha exatamente na linha de encontro).
- BOCA: canto e bochecha refinados (2 subdivisoes locais); grupo Mandibula com gradiente continuo atras do canto (a pele
  da bochecha estica em muitas faces); bochecha interna em faixas no lugar do triangulo unico; garganta em 3 fileiras.
Grupos: Palpebra_Sup/Inf_E/D, Boca_Superior, Boca_Inferior, Mandibula. Pivos: rig_pivos.json.
Uso: blender -b low_ref2/CR_LoboArtico_LOW.blend -P rosto_v5.py -- <saida_dir>"""
import bpy, bmesh, sys, os, json, math, shutil
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
a_ = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a_[0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); AQUI = os.path.dirname(SRC)
PIV0 = json.load(open(os.path.join(SRC, "rig_pivos.json"))); ROSTO = json.load(open(os.path.join(AQUI, "meshy", "rosto.json")))
sc = bpy.context.scene; cab = bpy.data.objects["LOW_Cabeca"]; me = cab.data
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
Z = V((0, 0, 1))
BA, BB = PIV0["mandibula"]["linha_boca"]; CANTO = PIV0["mandibula"]["canto_y"]
def z_boca(y): return BA + BB * y
N_BOCA = V((0, -BB, 1)).normalized(); P_BOCA = V((0, CANTO, z_boca(CANTO)))
for im in bpy.data.images:                                              # texturas: copias proprias da v5
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.exists(fp) and os.path.dirname(fp) != OUT:
        dst = os.path.join(OUT, os.path.basename(fp)); shutil.copy(fp, dst); im.filepath = dst; im.reload()

bm = bmesh.new(); bm.from_mesh(me); dl = bm.verts.layers.deform.verify(); uvl = bm.loops.layers.uv.active
# ------------------------------------------------------------------ 0) remove interior/cascas antigos (se houver) e cria os grupos
antigos = {g.index for g in cab.vertex_groups if g.name.startswith(("Boca_", "Palpebra_", "Mandibula"))}
lixo = [v for v in bm.verts if set(v[dl].keys()) & antigos]
bmesh.ops.delete(bm, geom=lixo, context="VERTS")
for g in list(cab.vertex_groups): cab.vertex_groups.remove(g)
G = {n: cab.vertex_groups.new(name=n).index for n in ("Boca_Superior", "Boca_Inferior", "Palpebra_Sup_E", "Palpebra_Inf_E",
                                                       "Palpebra_Sup_D", "Palpebra_Inf_D", "Mandibula")}
for v in bm.verts: v[dl].clear()
print("V5 removidos da base:", len(lixo), flush=True)
bm.faces.ensure_lookup_table(); bvh0 = BVHTree.FromBMesh(bm)
TRI0 = {f.index: ([l.vert.co.copy() for l in f.loops], [l[uvl].uv.copy() for l in f.loops]) for f in bm.faces}
IMGS = {n.image.name.split("_")[-1]: n.image for n in me.materials[0].node_tree.nodes if n.type == "TEX_IMAGE"}
ORIG = {}
for k, im in IMGS.items():
    W0 = im.size[0]; a0 = np.empty(W0 * W0 * 4, np.float32); im.pixels.foreach_get(a0); ORIG[k] = a0.reshape(W0, W0, 4).copy()
def uv_original(p, n):
    """ponto e UV da pele original onde o raio (ao longo de -n) a atinge"""
    loc, nr, i, d = bvh0.ray_cast(p + n * 0.3, -n, 0.8)
    if loc is None: return None, None
    cs, uvs = TRI0[i]
    w = barycentric_transform(loc, cs[0], cs[1], cs[2], V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1)))
    return loc, uvs[0] * w.x + uvs[1] * w.y + uvs[2] * w.z

# ------------------------------------------------------------------ 1) frames dos olhos simetrizados
oE, oD = ROSTO["olhos"]["E"], ROSTO["olhos"]["D"]
cE, cD = V(oE["centro"]), V(oD["centro"]); nE, nD = V(oE["normal"]).normalized(), V(oD["normal"]).normalized()
MX = (cE.x + cD.x) / 2
def esp(p): return V((2 * MX - p.x, p.y, p.z))
def espn(n): return V((-n.x, n.y, n.z))
cS = (cE + esp(cD)) / 2; nS = (nE + espn(nD)).normalized()
LI = (oE["largura_iris"] + oD["largura_iris"]) / 2
A_EL, B_EL, INCL = 0.85 * LI, 0.40 * LI, math.radians(12)
OLHOS = {}
for lado, c, n in (("E", cS, nS), ("D", esp(cS), espn(nS))):
    loc, _ = uv_original(c, n); c = loc or c
    up = (Z - n * n.dot(Z)).normalized(); fora = V((1 if lado == "E" else -1, 0, 0))
    u = (fora - n * n.dot(fora) - up * up.dot(fora)).normalized()
    uu = (u * math.cos(INCL) + up * math.sin(INCL)).normalized(); vv = n.cross(uu).normalized()
    if vv.dot(up) < 0: vv = -vv
    OLHOS[lado] = dict(c=c, n=n, uu=uu, vv=vv)
def local(o, p):
    q = p - o["c"]; return q.dot(o["uu"]), q.dot(o["vv"]), q.dot(o["n"])
def elip(o, p):
    u, v, d = local(o, p); return math.sqrt((u / A_EL) ** 2 + (v / B_EL) ** 2), u, v, d

# ------------------------------------------------------------------ 2) olhos: anel limpo, globo recuado, pesos por coluna
PIVO_OLHOS = {}
IRIS_C, IRIS_R = V((0.96, 0.54)), 0.036                                 # amostra propria da iris
K_UV = IRIS_R * 0.92 / (0.76 * A_EL)                                     # iris ~76% da largura da fenda (lobo: quase sem esclera; 60% parecia disco)
EK = (1.0, 1.10, 1.25, 1.45, 1.70); QUEDA = (1.0, 0.85, 0.55, 0.25, 0.0); NS = 40; E_FURO = 1.75; E_MAX = 3.4; PINTAR = []
PATCH_C = {"E": V((0.952, 0.660)), "D": V((0.952, 0.722))}; PH = V((0.044, 0.022))   # remendos de UV do anel (u>0,90)
def uv_patch(lado, o, p):
    q = p - o["c"]; lu, lv = q.dot(o["uu"]), q.dot(o["vv"])
    return PATCH_C[lado] + V((lu / (A_EL * E_MAX) * PH.x, lv / (B_EL * E_MAX) * PH.y))
for lado, o in OLHOS.items():
    c, n, uu, vv = o["c"], o["n"], o["uu"], o["vv"]
    def ponto(e, ph):
        q = c + uu * (A_EL * e * math.cos(ph)) + vv * (B_EL * e * math.sin(ph)); loc, _ = uv_original(q, n)
        return loc if loc is not None else q
    phis = [2 * math.pi * s_ / NS for s_ in range(NS)]
    pele = [[ponto(e, ph) for ph in phis] for e in EK]
    Rs = []
    for m in pele[0]:
        qq = m - c; den = -2 * n.dot(qq)
        if den > 1e-4: Rs.append(qq.length_squared / den)
    R = float(np.clip(np.median(Rs), 0.10, 0.40)) if Rs else 0.18
    S = c - n * R; RG = R - 0.016                                          # o globo visivel fica 0,016 atras da margem
    for passo in range(3):                                                 # pele em volta mais densa: a borda do buraco ~ 40 vertices
        reg = [f for f in bm.faces if any(elip(o, v.co)[0] < (3.2 if passo < 2 else 2.4) and abs(local(o, v.co)[2]) < 0.3 for v in f.verts)]
        bmesh.ops.subdivide_edges(bm, edges=list({e for f in reg for e in f.edges}), cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
    velhas =[f for f in bm.faces if any(elip(o, v.co)[0] < E_FURO and abs(local(o, v.co)[2]) < 0.25 for v in f.verts)]
    bmesh.ops.delete(bm, geom=velhas, context="FACES"); bm.verts.ensure_lookup_table()
    borda = [v for v in bm.verts if v.is_boundary and elip(o, v.co)[0] < 3.2 and abs(local(o, v.co)[2]) < 0.3]
    aneis = []
    for k, e in enumerate(EK):
        fil = []
        for s_, ph in enumerate(phis):
            p = pele[k][s_]
            if k == 0: p = S + (p - S).normalized() * (R + (0.004 if math.sin(ph) > 0 else 0.0015))
            elif k == 1: p = p.lerp(S + (p - S).normalized() * (R + 0.012), 0.5)
            fil.append(bm.verts.new(p))
        aneis.append(fil)
    for _ in range(2):
        bmesh.ops.smooth_vert(bm, verts=[v for a in aneis[2:4] for v in a], factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    fz_anel = []
    def fz(vs_):
        try: f = bm.faces.new(vs_)
        except ValueError: return None
        for l_ in f.loops: l_[uvl].uv = uv_patch(lado, o, l_.vert.co)
        f.smooth = True; fz_anel.append(f); return f
    for k in range(len(EK) - 1):
        for s_ in range(NS):
            s2 = (s_ + 1) % NS; fz((aneis[k][s_], aneis[k][s2], aneis[k + 1][s2], aneis[k + 1][s_]))
    def ang(p): q = p - c; return math.atan2(q.dot(vv) / B_EL, q.dot(uu) / A_EL) % (2 * math.pi)
    bor = sorted(borda, key=lambda v: ang(v.co)); ext = aneis[-1]
    a0 = ang(bor[0].co); s0 = min(range(NS), key=lambda s_: (phis[s_] - a0) % (2 * math.pi))   # ziper comeca alinhado
    ext = ext[s0:] + ext[:s0]; pe = [(phis[(s0 + j) % NS] - a0) % (2 * math.pi) for j in range(NS)]
    pb = [(ang(v.co) - a0) % (2 * math.pi) for v in bor]
    i = j = 0; nb = len(bor)
    while i < nb or j < NS:
        ab = pb[i] if i < nb else 2 * math.pi; ae = pe[j] if j < NS else 2 * math.pi
        if j < NS and (i >= nb or ae <= ab): fz((ext[j], ext[(j + 1) % NS], bor[i % nb])); j += 1
        else: fz((bor[i % nb], ext[j % NS], bor[(i + 1) % nb])); i += 1
    for f in fz_anel:
        f.normal_update()
        if f.normal.dot(n) < -0.2: f.normal_flip()
    NRg = 6; phg = phis[::2]; NG = len(phg)
    pts = [[S + n * RG]] + [[S + (n * RG + uu * (1.04 * A_EL * k / NRg * math.cos(ph)) + vv * (1.04 * B_EL * k / NRg * math.sin(ph))).normalized() * RG
                             for ph in phg] for k in range(1, NRg + 1)]
    def uv_iris(p):
        q = p - S; return IRIS_C + V((q.dot(uu), q.dot(vv))) * K_UV
    gv = [[bm.verts.new(p) for p in a] for a in pts]; fglobo = []
    def fg(vs_):
        f = bm.faces.new(vs_)
        for l_ in f.loops: l_[uvl].uv = uv_iris(l_.vert.co)
        f.smooth = True; fglobo.append(f)
    for s_ in range(NG): fg((gv[0][0], gv[1][s_], gv[1][(s_ + 1) % NG]))
    for k in range(1, NRg):
        for s_ in range(NG): fg((gv[k][s_], gv[k + 1][s_], gv[k + 1][(s_ + 1) % NG], gv[k][(s_ + 1) % NG]))
    for f in fglobo:
        f.normal_update()
        if f.normal.dot(f.calc_center_median() - S) < 0: f.normal_flip()
    def elev(p): q = p - S; return math.atan2(q.dot(vv), q.dot(n))
    A_u, A_l = [0.0] * NS, [0.0] * NS
    for s_ in range(NS):
        if math.sin(phis[s_]) <= 0.02: continue
        sl = (NS - s_) % NS; tu, tl = elev(aneis[0][s_].co), elev(aneis[0][sl].co)
        tm = tl + 0.35 * (tu - tl)                                        # a de cima faz a maior parte do fechamento
        A_u[s_] = tu - tm + math.radians(0.6); A_l[sl] = tm - tl + math.radians(0.2)
    A_S, A_I = max(A_u), max(A_l)
    for k, fil in enumerate(aneis):
        for s_, v in enumerate(fil):
            if A_u[s_] > 0: v[dl][G["Palpebra_Sup_" + lado]] = QUEDA[k] * A_u[s_] / A_S
            if A_l[s_] > 0: v[dl][G["Palpebra_Inf_" + lado]] = QUEDA[k] * A_l[s_] / A_I
    eixo = n.cross(vv).normalized()
    PIVO_OLHOS[lado] = {"centro_globo": list(S), "raio_globo": RG, "raio_margem": R, "eixo": list(eixo), "fechar_sup_graus": -math.degrees(A_S),
                        "fechar_inf_graus": math.degrees(A_I), "fenda": [2 * A_EL, 2 * B_EL], "inclinacao_graus": math.degrees(INCL),
                        "nota": "palpebras = pele do anel; girar com os pesos em torno do eixo no centro do globo (a margem desliza por fora dele)"}
    o["S"] = S
    anel_set = set(fz_anel) | set(fglobo)                                  # pele original em volta (fora do anel): tinta escura do Meshy
    for f in bm.faces:
        if f in anel_set or len(f.verts) != 3: continue
        es = [elip(o, v.co)[0] for v in f.verts]
        if min(es) < 3.6 and all(abs(local(o, v.co)[2]) < 0.3 for v in f.verts): PINTAR.append(([l[uvl].uv.copy() for l in f.loops], es))
    print("V5 olho", lado, "raio margem %.3f globo %.3f" % (R, RG), "borda do buraco", len(borda), "faces do anel", len(fz_anel),
          "globo", len(fglobo), "fechar sup %.1f inf %.1f graus" % (math.degrees(A_S), math.degrees(A_I)), flush=True)

# ------------------------------------------------------------------ 3) boca: canto/bochecha refinados
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
pre = [e for e in bm.edges if e.is_boundary and all(v.co.y < CANTO + 0.03 and abs(v.co.z - z_boca(v.co.y)) < 0.12 for v in e.verts)]
cantos = []
for lado_x in (1, -1):
    vs_ = [v for e in pre for v in e.verts if (v.co.x - 0.05) * lado_x > 0]
    if vs_: cantos.append(max(vs_, key=lambda v: v.co.y).co.copy())
for passo in range(2):
    reg = [f for f in bm.faces if any((f.calc_center_median() - cc).length < (0.42 if passo == 0 else 0.30) for cc in cantos)
           and f.calc_center_median().y > CANTO - 0.30]
    bmesh.ops.subdivide_edges(bm, edges=list({e for f in reg for e in f.edges}), cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
reg = [f for f in bm.faces if f.calc_center_median().y < CANTO + 0.05 and -0.40 < (f.calc_center_median() - P_BOCA).dot(N_BOCA) < 0.0
       and abs(f.calc_center_median().x - 0.05) < 0.6]
bmesh.ops.subdivide_edges(bm, edges=list({e for f in reg for e in f.edges}), cuts=1, use_grid_fill=True)
bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
print("V5 boca: mandibula da frente refinada, faces", len(reg), flush=True)
print("V5 boca: cantos refinados", [tuple(round(x, 2) for x in cc) for cc in cantos], flush=True)

# ------------------------------------------------------------------ 4) boca: saco bucal soldado aos labios
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table(); bvh2 = BVHTree.FromBMesh(bm)
def saida(p, d, dist=2.0):
    loc, nr, i, dd = bvh2.ray_cast(p, d.normalized(), dist)
    return dd if loc is not None and nr.dot(d.normalized()) > 0 else None
labio = [e for e in bm.edges if e.is_boundary and all(v.co.y < CANTO + 0.03 and abs(v.co.z - z_boca(v.co.y)) < 0.12 for v in e.verts)]
def cadeia(arest):
    viz = {}
    for e in arest:
        a, b = e.verts; viz.setdefault(a, []).append(b); viz.setdefault(b, []).append(a)
    pontas = [v for v, l in viz.items() if len(l) == 1]
    ini = max(pontas, key=lambda v: v.co.x) if pontas else next(iter(viz))
    ordem, vis = [ini], {ini}
    while True:
        prox = [w for w in viz[ordem[-1]] if w not in vis]
        if not prox: break
        ordem.append(prox[0]); vis.add(prox[0])
    return ordem
sup_e = [e for e in labio if e.link_faces and e.link_faces[0].calc_center_median().z > z_boca(e.link_faces[0].calc_center_median().y)]
inf_e = [e for e in labio if e not in sup_e]
CS, CI = cadeia(sup_e), cadeia(inf_e)
CX = sum(v.co.x for v in CS) / len(CS)
print("V5 boca: labio superior", len(CS), "inferior", len(CI), "cx %.3f" % CX, flush=True)
def espessuras(y):
    c = V((CX, y, z_boca(y))); up_, dn_ = saida(c, Z), saida(c, -Z)
    return (up_ or 0.20), (dn_ or 0.10)
AMOSTRAS = {"labio": (0.10, 0.09, 0.10), "gengiva": (0.62, 0.32, 0.34), "palato": (0.48, 0.20, 0.22), "assoalho": (0.40, 0.15, 0.17),
            "lingua": (0.70, 0.36, 0.38), "dente": (0.92, 0.89, 0.80), "garganta": (0.10, 0.03, 0.04), "bochecha": (0.46, 0.20, 0.22)}
FAIXA = {k: 0.02 + 0.06 * i for i, k in enumerate(AMOSTRAS)}
assert FAIXA["bochecha"] + 0.06 < 0.636                                  # nao invade os remendos do anel dos olhos
def uvq(k): return V((0.96, FAIXA[k] + 0.03))
novos_sup, novos_inf, faces_novas, pesos_mand = [], [], {}, {}
def face(vs_, tipo):
    try: f = bm.faces.new(vs_)
    except ValueError: return None
    for l_ in f.loops: l_[uvl].uv = uvq(tipo)
    faces_novas[f] = tipo; return f
def anel_interno(C, sinal, lista):
    R_, Gg = [], []
    for P in C:
        d = V((CX - P.co.x, 0.35, 0)).normalized(); up_, dn_ = espessuras(P.co.y)
        prof = (dn_ if sinal < 0 else up_)
        R_.append(bm.verts.new(P.co + d * 0.026 + Z * sinal * min(0.010, 0.10 * prof)))
        Gg.append(bm.verts.new(P.co + d * 0.060 + Z * sinal * min(0.035, 0.30 * prof)))
    lista += R_ + Gg
    for i in range(len(C) - 1):
        face((C[i], C[i + 1], R_[i + 1], R_[i]), "labio"); face((R_[i], R_[i + 1], Gg[i + 1], Gg[i]), "gengiva")
    return R_, Gg
RS, GS = anel_interno(CS, +1, novos_sup); RI, GI = anel_interno(CI, -1, novos_inf)
ys = np.linspace(min(v.co.y for v in CS) + 0.03, CANTO - 0.01, 10)
ESP = [espessuras(y) for y in ys]
SP_S = [bm.verts.new(V((CX, y, z_boca(y) + 0.55 * up_))) for y, (up_, dn_) in zip(ys, ESP)]
SP_I = [bm.verts.new(V((CX, y, z_boca(y) - 0.45 * dn_))) for y, (up_, dn_) in zip(ys, ESP)]
novos_sup += SP_S; novos_inf += SP_I
def ziper(A, B, tipo):
    i = j = 0
    while i < len(A) - 1 or j < len(B) - 1:
        if j >= len(B) - 1 or (i < len(A) - 1 and A[i + 1].co.y <= B[j + 1].co.y): face((A[i], A[i + 1], B[j]), tipo); i += 1
        else: face((A[i], B[j + 1], B[j]), tipo); j += 1
def metades(Gg):
    im = min(range(len(Gg)), key=lambda k: Gg[k].co.y)
    return Gg[:im + 1][::-1], Gg[im:]
for Gg, SP, tipo in ((GS, SP_S, "palato"), (GI, SP_I, "assoalho")):
    esq, dir_ = metades(Gg); ziper(esq, SP, tipo); ziper(dir_, SP, tipo)
# garganta em 3 fileiras intermediarias (pesos 0,25/0,5/0,75) recuadas: o fundo estica em faixas, nao numa placa
def fileira(R_, Gg, SP): return [R_[0], Gg[0], SP[-1], Gg[-1], R_[-1]]
fs, fi = fileira(RS, GS, SP_S), fileira(RI, GI, SP_I)
linhas = [fs]
for t in (0.25, 0.5, 0.75):
    fil = [bm.verts.new(a.co.lerp(b.co, t) + V((0, 0.10 * math.sin(math.pi * t), 0))) for a, b in zip(fs, fi)]
    for v in fil: pesos_mand[v] = t
    linhas.append(fil)
linhas.append(fi)
for l1, l2 in zip(linhas, linhas[1:]):
    for k in range(4): face((l1[k], l1[k + 1], l2[k + 1], l2[k]), "garganta")
# bochecha interna: leque do canto (C) ate as colunas das pontas da garganta (as mesmas fileiras 0,25/0,5/0,75), que
# passam a ter cor de bochecha. v5_r6 tinha uma faixa propria por cima delas (aresta rolo-gengiva com 3 faces = nao-manifold).
for C, col in ((CS[0], 0), (CS[-1], 4)):
    col_r = [l_[col] for l_ in linhas]
    for a_, b_ in zip(col_r, col_r[1:]): face((C, a_, b_), "bochecha")
    k = 0 if col == 0 else 3
    for l1, l2 in zip(linhas, linhas[1:]):
        f_ = next((g for g in l1[k].link_faces if g in faces_novas and l2[k] in g.verts and l1[k + 1] in g.verts), None)
        if f_ is not None:
            for l_ in f_.loops: l_[uvl].uv = uvq("bochecha")
            faces_novas[f_] = "bochecha"
for f, tipo in faces_novas.items():
    c = f.calc_center_median(); alvo = V((CX, min(c.y, CANTO - 0.12), z_boca(c.y)))
    f.normal_update()
    if f.normal.dot(alvo - c) < 0: f.normal_flip()
DENTES = []
def dente(base, eixo_, comp, larg, prof, curva, tipo_lista):
    lado_ = eixo_.cross(V((0, 1, 0))).normalized() if abs(eixo_.y) < 0.9 else V((1, 0, 0))
    tras = eixo_.cross(lado_).normalized(); aneis = []
    for k in range(4):
        t = k / 3; c = base + eixo_ * comp * t + tras * curva * comp * t * t; s = (1 - t) ** 0.85 + 0.05
        aneis.append([bm.verts.new(c + (lado_ * math.cos(2 * math.pi * i / 6) * larg + tras * math.sin(2 * math.pi * i / 6) * prof) * s) for i in range(6)])
    ponta = bm.verts.new(base + eixo_ * comp * 1.08 + tras * curva * comp)
    for k in range(3):
        for i in range(6): face((aneis[k][i], aneis[k][(i + 1) % 6], aneis[k + 1][(i + 1) % 6], aneis[k + 1][i]), "dente")
    for i in range(6): face((aneis[3][i], aneis[3][(i + 1) % 6], ponta), "dente")
    vs_ = [v for a in aneis for v in a] + [ponta]; tipo_lista += vs_; DENTES.append(vs_)
def arco(Gg, R_):
    im = min(range(len(Gg)), key=lambda k: Gg[k].co.y); res = []
    for idx in (range(im, -1, -1), range(im, len(Gg))):
        s, ant = 0.0, None
        for k in idx:
            p = (Gg[k].co + R_[k].co) / 2
            if ant is not None: s += (p - ant).length
            res.append((s, p, Gg[k].co.y)); ant = p
    return res
for Gg, R_, sinal, lista in ((GS, RS, -1, novos_sup), (GI, RI, +1, novos_inf)):
    pos = arco(Gg, R_); feitos = set()
    for alvo_s, tipo in ((0.012, "inc"), (0.035, "inc"), (0.058, "inc"), (0.10, "can"), (0.17, "pm"), (0.24, "pm"), (0.31, "pm"), (0.38, "pm")):
        for metade in (0, 1):
            cand = [q for q in pos if (q[1].x - CX) * (1 if metade == 0 else -1) >= -0.005]
            if not cand: continue
            s, p, y = min(cand, key=lambda q: abs(q[0] - alvo_s))
            if abs(s - alvo_s) > 0.03 or y > CANTO - 0.04 or (round(p.x, 3), round(p.y, 3)) in feitos: continue
            feitos.add((round(p.x, 3), round(p.y, 3)))
            up_, dn_ = espessuras(y); lim = (0.70 * dn_) if sinal < 0 else (0.60 * up_)
            ax = (Z * sinal + V((CX - p.x, 0.0, 0)) * 0.4).normalized()
            if tipo == "inc": dente(p, ax, min(0.040, lim), 0.010, 0.007, 0.0, lista)
            elif tipo == "can": dente(p, ax, min(0.12 if sinal < 0 else 0.095, lim), 0.022, 0.020, 0.35, lista)
            else: dente(p, ax, min(0.045, lim), 0.020, 0.008, 0.10, lista)
yl = np.linspace(ys[0] + 0.05, CANTO - 0.07, 8); aneis = []
for k, y in enumerate(yl):
    up_, dn_ = espessuras(y); hw = max(abs(v.co.x - CX) for v in CI if abs(v.co.y - y) < 0.06) if any(abs(v.co.y - y) < 0.06 for v in CI) else 0.1
    t = k / (len(yl) - 1); larg = 0.55 * hw * (math.sqrt(min(1.0, t * 3.0)) * 0.7 + 0.3); esp_ = 0.22 * dn_ + 0.008
    c = V((CX, y, z_boca(y) - 0.45 * dn_ + esp_ * 0.9)); anel = []
    for i in range(10):
        an = 2 * math.pi * i / 10; zz = math.sin(an) * esp_ * (0.75 if math.sin(an) < 0 else 1.0)
        if abs(math.cos(an)) < 0.35 and math.sin(an) > 0: zz -= 0.3 * esp_
        anel.append(bm.verts.new(c + V((math.cos(an) * larg, 0, zz))))
    aneis.append(anel)
for a1, a2 in zip(aneis, aneis[1:]):
    for i in range(10): face((a1[i], a1[(i + 1) % 10], a2[(i + 1) % 10], a2[i]), "lingua")
face(aneis[0][::-1], "lingua"); face(aneis[-1], "lingua")
novos_inf += [v for a in aneis for v in a]
bmesh.ops.recalc_face_normals(bm, faces=[f for f, t in faces_novas.items() if t in ("lingua", "dente")])
movidos = 0
fixos = {v for d_ in DENTES for v in d_} | {v for a in aneis for v in a}            # dentes e lingua NAO sao empurrados
for lista, sinal in (([v for v in novos_inf + list(pesos_mand) if v not in fixos], -1), ([v for v in novos_sup if v not in fixos], +1)):
    d_ = Z * sinal
    for v in lista:
        loc, nr, i, dd = bvh2.ray_cast(v.co, d_, 2.0)
        if loc is not None and nr.dot(d_) > 0: continue
        loc, nr, i, dd = bvh2.ray_cast(v.co, -d_, 2.0)
        if loc is not None and dd < 0.12: v.co = loc - d_ * 0.018; movidos += 1
print("V5 boca: vertices do interior trazidos para dentro da pele", movidos, flush=True)
for v in novos_sup: v[dl][G["Boca_Superior"]] = 1.0
for v in novos_inf: v[dl][G["Boca_Inferior"]] = 1.0; v[dl][G["Mandibula"]] = 1.0
for v, t in pesos_mand.items():
    v[dl][G["Boca_Superior"]] = 1 - t; v[dl][G["Boca_Inferior"]] = t; v[dl][G["Mandibula"]] = t
# grupo Mandibula da PELE por CONECTIVIDADE: parte das faces do labio de baixo e se espalha pela pele a frente do canto
# (o corte separa os labios: o lado de cima nunca e alcancado). Atras do canto: gradiente largo (vertical e para tras).
interior = set(novos_sup) | set(novos_inf) | set(pesos_mand)
palp_g = {G[k] for k in G if k.startswith("Palpebra")}
# BFS em DUAS frentes (labio de cima x de baixo): cada face fica com o lado mais proximo em saltos. Uma frente so
# (v5_r5) contornava a ponta do corte no canto e subia pela aba do labio superior que pende abaixo do plano.
def regiao(c_): return c_.y < CANTO - 0.08 and abs(c_.x - CX) < 0.80
dono = {}
fr_s = [f for e in sup_e for f in e.link_faces if f not in faces_novas]; fr_i = [f for e in inf_e for f in e.link_faces if f not in faces_novas]
for f in fr_s: dono[f] = "S"
for f in fr_i: dono.setdefault(f, "I")
frente = list(dono)
while frente:
    prox = []
    for f in frente:
        for e in f.edges:
            for g in e.link_faces:
                if g in dono or g in faces_novas: continue
                c_ = g.calc_center_median()
                if not regiao(c_): continue
                if dono[f] == "I" and (c_ - P_BOCA).dot(N_BOCA) > 0.03: continue          # o queixo nao sobe acima do plano
                dono[g] = dono[f]; prox.append(g)
    frente = prox
queixo = {f for f, k in dono.items() if k == "I"}
vs_sup = {v for f, k in dono.items() if k == "S" for v in f.verts}
vq = {v for f in queixo for v in f.verts}
vq_meio = vq & vs_sup                                                     # vertices na fronteira das frentes (ponta do corte)
vq -= vs_sup
for v in bm.verts:
    if v in interior or set(v[dl].keys()) & palp_g: continue
    p = v.co; d = (p - P_BOCA).dot(N_BOCA)
    if v in vq: w = 1.0
    elif v in vq_meio: w = 0.5
    elif p.y >= CANTO - 0.10: w = (1 - suave((d + 0.25) / 0.50)) * (1 - suave((p.y - CANTO) / 0.70))
    else: continue                                                         # pele do focinho a frente do canto: fica no cranio
    w *= 1 - suave((-d - 0.32) / 0.30)                                     # garganta sob o queixo: sai aos poucos
    if abs(p.x - CX) > 0.80: w = 0.0
    if w > 0.01: v[dl][G["Mandibula"]] = w
print("V5 boca: pele da mandibula por conectividade, faces", len(queixo), "labio sup", len(dono) - len(queixo), "fronteira", len(vq_meio), flush=True)
for f in faces_novas: f.smooth = True
# furos acidentais minusculos deixados pelo refino em volta dos olhos (o ajuste_r3 os tapava DOBRANDO a pele): fundir no centro
fundidos = 0
for o_ in OLHOS.values():
    bv = {v for v in bm.verts if v.is_boundary and (v.co - o_["S"]).length < 0.9}
    while bv:
        v0 = bv.pop(); comp, pilha = [v0], [v0]
        while pilha:
            v = pilha.pop()
            for e in v.link_edges:
                if e.is_boundary:
                    w_ = e.other_vert(v)
                    if w_ in bv: bv.discard(w_); comp.append(w_); pilha.append(w_)
        cc = sum((v.co for v in comp), V()) / len(comp)
        if len(comp) <= 8 and max((v.co - cc).length for v in comp) < 0.03:
            bmesh.ops.pointmerge(bm, verts=comp, merge_co=cc); fundidos += 1
print("V5 olhos: furos minusculos fundidos", fundidos, flush=True)
bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges[:])
# enrolamento: cada face do anel/globo segue a vizinha ja orientada (partindo da pele original); antes era pelo sinal da normal
from collections import deque
anel_todo = {f for f in bm.faces if f.is_valid and len(f.loops) and f.loops[0][uvl].uv.x > 0.90 and f not in faces_novas}
def mesma_ordem(f, a_, b_):
    vs = list(f.verts); i = vs.index(a_); return vs[(i + 1) % len(vs)] is b_
fila, feitos = deque(), set()
for f in anel_todo:
    for e in f.edges:
        for g in e.link_faces:
            if g not in anel_todo and g not in faces_novas and len(e.link_faces) == 2: fila.append((g, f, e))
virados = 0
while fila:
    g, f, e = fila.popleft()
    if f in feitos: continue
    a_, b_ = e.verts
    if mesma_ordem(g, a_, b_) == mesma_ordem(f, a_, b_): f.normal_flip(); virados += 1
    feitos.add(f)
    for e2 in f.edges:
        if len(e2.link_faces) != 2: continue
        for h in e2.link_faces:
            if h in anel_todo and h not in feitos: fila.append((f, h, e2))
print("V5 olhos: faces do anel orientadas pela pele", len(feitos), "viradas", virados, flush=True)
bm.to_mesh(me); me.update(); bm.free()
print("V5 boca: faces novas", len(faces_novas), "dentes", len(DENTES), flush=True)

# ------------------------------------------------------------------ 5) texturas: amostras, iris e remendos do anel (reamostrados da pele)
for k, im in IMGS.items():
    W = im.size[0]; arr = np.empty(W * W * 4, np.float32); im.pixels.foreach_get(arr); arr = arr.reshape(W, W, 4)
    c0 = int(0.92 * W)
    for nome, cor in AMOSTRAS.items():
        r0, r1 = int(FAIXA[nome] * W), int((FAIXA[nome] + 0.06) * W)
        if k == "cor": arr[r0:r1, c0:, :3] = cor
        elif k == "normal": arr[r0:r1, c0:, :3] = (0.5, 0.5, 1.0)
        elif k == "rugosidade": arr[r0:r1, c0:, :3] = 0.35 if nome == "dente" else (0.30 if nome in ("lingua", "gengiva", "palato", "bochecha") else 0.6)
        else: arr[r0:r1, c0:, :3] = 0.0
    # iris: pupila, iris clara perto da pupila, anel limbar fino; entorno castanho-escuro (esclera de lobo), sem preto chapado
    yy, xx = np.mgrid[0:W, 0:W]; du = (xx + 0.5) / W - IRIS_C.x; dv = (yy + 0.5) / W - IRIS_C.y
    r = np.sqrt(du * du + dv * dv) / IRIS_R; angp = np.arctan2(dv, du); zona = r < 1.35
    if k == "cor":
        raios = 0.06 * np.sin(angp * 23) + 0.04 * np.sin(angp * 51 + 1.3); t = np.clip((r - 0.22) / 0.70, 0, 1)
        iris = np.stack([0.66 - 0.30 * t, 0.92 - 0.22 * t, 1.0 - 0.05 * t], -1) * (1 + raios[..., None])
        cor = np.where((r < 0.22)[..., None], np.array([0.02, 0.02, 0.025]), iris)
        lim_ = np.clip((r - 0.84) / 0.24, 0, 1)[..., None]                 # anel limbar em degrade (sem borda recortada de disco)
        entorno = np.array([0.30, 0.27, 0.26])
        cor = np.where((r >= 0.84)[..., None], cor * (1 - lim_) + (np.array([0.16, 0.28, 0.38]) * (1 - lim_) + entorno * lim_) * lim_, cor)
        cor = np.where((r >= 1.08)[..., None], entorno, cor)
        arr[zona, :3] = np.clip(cor[zona], 0, 1)
    elif k == "normal": arr[zona, :3] = (0.5, 0.5, 1.0)
    elif k == "rugosidade": arr[zona, :3] = np.where((r[zona] < 1.0)[..., None], 0.10, 0.32)   # entorno menos brilhante: sem crescente branco
    else: arr[zona, :3] = 0.0; arr[zona & (r >= 0.22) & (r < 0.92), :3] = (0.04, 0.10, 0.13)
    # remendos do anel: cada texel -> ponto da pele original -> cor/normal/rugosidade originais; depois a pintura da palpebra
    for lado, o in OLHOS.items():
        pc = PATCH_C[lado]; x0, x1 = int((pc.x - PH.x) * W), int((pc.x + PH.x) * W) + 1; y0, y1 = int((pc.y - PH.y) * W), int((pc.y + PH.y) * W) + 1
        for py in range(y0, y1):
            for px in range(x0, x1):
                lu = ((px + 0.5) / W - pc.x) / PH.x * A_EL * E_MAX; lv = ((py + 0.5) / W - pc.y) / PH.y * B_EL * E_MAX
                e = math.sqrt((lu / A_EL) ** 2 + (lv / B_EL) ** 2)
                loc, uv0 = uv_original(o["c"] + o["uu"] * lu + o["vv"] * lv, o["n"])
                src = ORIG[k]; Ws = src.shape[0]
                val = src[min(Ws - 1, max(0, int(uv0.y * Ws))), min(Ws - 1, max(0, int(uv0.x * Ws))), :3].copy() if uv0 is not None else np.array([0.85, 0.86, 0.89])
                if k == "cor":
                    if val[2] > val[0] + 0.06: val = np.array([0.85, 0.86, 0.89])                # tinta azul do Meshy fora da fenda -> pelo
                    lum = float(val @ np.array([0.3, 0.59, 0.11]))
                    if e >= 1.16 and lum < 0.40:                                                   # delineado do Meshy: mais claro
                        f_ = 0.75 * (1 - suave((e - 2.4) / 1.0)); val = val * (1 - f_) + np.array([0.80, 0.81, 0.84]) * f_
                    if e < 1.06: val = np.array([0.15, 0.14, 0.15])                              # borda palpebral fina
                    elif e < 1.16: val = np.array([0.32, 0.30, 0.32])                            # espessura da palpebra
                    elif e < 1.35: val = val * suave((e - 1.16) / 0.19) + np.array([0.50, 0.50, 0.53]) * (1 - suave((e - 1.16) / 0.19))
                elif k == "normal":
                    f_ = 0.75 * (1 - suave((e - 1.4) / 1.0)); val = val * (1 - f_) + np.array([0.5, 0.5, 1.0]) * f_   # sulcos suavizados perto do olho
                elif k == "rugosidade":
                    if e < 1.06: val = np.array([0.45, 0.45, 0.45])
                else: val = np.zeros(3)
                arr[py, px, :3] = val
    if k == "cor":                                                         # fora do remendo: delineado escuro do Meshy atenuado
        for uvs, es in PINTAR:
            P = np.array([[uv.x * W, uv.y * W] for uv in uvs]); x0, y0 = np.floor(P.min(0)).astype(int); x1, y1 = np.ceil(P.max(0)).astype(int) + 1
            x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, W), min(y1, W)
            if x1 <= x0 or y1 <= y0 or x0 >= int(0.90 * W): continue
            gy, gx = np.mgrid[y0:y1, x0:x1]; px_ = gx + 0.5; py_ = gy + 0.5
            (ax_, ay_), (bx_, by_), (cx_, cy_) = P
            den = (by_ - cy_) * (ax_ - cx_) + (cx_ - bx_) * (ay_ - cy_)
            if abs(den) < 1e-9: continue
            l1 = ((by_ - cy_) * (px_ - cx_) + (cx_ - bx_) * (py_ - cy_)) / den; l2 = ((cy_ - ay_) * (px_ - cx_) + (ax_ - cx_) * (py_ - cy_)) / den
            l3 = 1 - l1 - l2; dentro_t = (l1 >= -0.02) & (l2 >= -0.02) & (l3 >= -0.02)
            e_px = l1 * es[0] + l2 * es[1] + l3 * es[2]; sub = arr[y0:y1, x0:x1]
            lum = sub[..., :3] @ np.array([0.3, 0.59, 0.11]); alvo_ = dentro_t & (lum < 0.40)
            f_ = (0.65 * (1 - np.clip((e_px - 2.4) / 1.2, 0, 1)))[..., None]
            sub[alvo_, :3] = (sub[..., :3] * (1 - f_) + np.array([0.80, 0.81, 0.84]) * f_)[alvo_]
    im.pixels.foreach_set(arr.ravel()); im.update(); im.save()
print("V5 texturas atualizadas", list(IMGS), flush=True)

# ------------------------------------------------------------------ 6) pivos e saida (LODs/exports ficam com ajuste_r3.py)
piv = dict(PIV0); piv["olhos"] = PIVO_OLHOS
piv["mandibula"]["nota"] = ("grupo Mandibula: 1 no queixo abaixo do corte, gradiente continuo atras do canto; saco bucal: Boca_Inferior/"
                            "Boca_Superior com faixas intermediarias na garganta e na bochecha interna")
json.dump(piv, open(os.path.join(OUT, "rig_pivos.json"), "w"), indent=1)
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
print("V5_TRIS cabeca", tris(cab), flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_LOW.blend"))
print("V5_OK")
