"""Rodada 1 do complemento (v2) sobre a m11 (low_ref/, preservada): olhos, palpebras e boca refeitos de forma anatomica.
- OLHOS: fenda amendoada recortada na pele (malha refinada em volta), globo atras com a iris projetada da propria
  textura da cabeca (direito reaproveita as UVs do esquerdo: iris iguais) e frames simetrizados pelo meio dos olhos.
- PALPEBRAS: sao a PROPRIA pele da margem (sem cascas): pesos graduais, margem apoiada no globo; o rig gira em torno
  do centro do globo e a margem desliza sobre ele (fechamento na linha de encontro, 30% abaixo do centro).
- BOCA: saco bucal SOLDADO as bordas do corte dos labios (labio enrolado, gengiva, palato, assoalho, garganta),
  dentes de lobo (incisivos, caninos curvos, pre-molares em lamina) e lingua modelada; cores em amostras da faixa u>0,92.
Grupos: Palpebra_Sup/Inf_E/D (pesos), Boca_Superior, Boca_Inferior. Pivos: low_v2/rig_pivos.json.
Uso: blender -b low_ref/CR_LoboArtico_LOW.blend -P rosto_v2.py -- <saida_dir>"""
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
# texturas: copias proprias em low_v2 (a m11 continua apontando para low_ref)
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.exists(fp) and os.path.dirname(fp) != OUT:
        dst = os.path.join(OUT, os.path.basename(fp)); shutil.copy(fp, dst); im.filepath = dst; im.reload()

bm = bmesh.new(); bm.from_mesh(me); dl = bm.verts.layers.deform.verify(); uvl = bm.loops.layers.uv.active
# ------------------------------------------------------------------ 0) remove interior e cascas da m11
antigos = {g.index for g in cab.vertex_groups if g.name.startswith(("Boca_", "Palpebra_"))}
lixo = [v for v in bm.verts if set(v[dl].keys()) & antigos]
bmesh.ops.delete(bm, geom=lixo, context="VERTS")
for g in list(cab.vertex_groups): cab.vertex_groups.remove(g)
G = {n: cab.vertex_groups.new(name=n).index for n in ("Boca_Superior", "Boca_Inferior", "Palpebra_Sup_E", "Palpebra_Inf_E",
                                                       "Palpebra_Sup_D", "Palpebra_Inf_D")}
for v in bm.verts: v[dl].clear()
print("V2 removidos da m11:", len(lixo), flush=True)
bm.faces.ensure_lookup_table(); bvh0 = BVHTree.FromBMesh(bm)
def na_pele(p, n, alcance=0.4):
    loc, nr, i, d = bvh0.ray_cast(p + n * alcance, -n, 2 * alcance); return loc

# ------------------------------------------------------------------ 1) frames dos olhos simetrizados
oE, oD = ROSTO["olhos"]["E"], ROSTO["olhos"]["D"]
cE, cD = V(oE["centro"]), V(oD["centro"]); nE, nD = V(oE["normal"]).normalized(), V(oD["normal"]).normalized()
MX = (cE.x + cD.x) / 2
def esp(p): return V((2 * MX - p.x, p.y, p.z))
def espn(n): return V((-n.x, n.y, n.z))
cS = (cE + esp(cD)) / 2; nS = (nE + espn(nD)).normalized()
LI = (oE["largura_iris"] + oD["largura_iris"]) / 2
A_EL, B_EL, R_E, INCL = 0.85 * LI, 0.40 * LI, 0.16, math.radians(12)
OLHOS = {}
for lado, c, n in (("E", cS, nS), ("D", esp(cS), espn(nS))):
    c = na_pele(c, n) or c
    up = (Z - n * n.dot(Z)).normalized(); fora = V((1 if lado == "E" else -1, 0, 0))
    u = (fora - n * n.dot(fora) - up * up.dot(fora)).normalized()                  # u aponta para o canto de FORA
    uu = (u * math.cos(INCL) + up * math.sin(INCL)).normalized()                    # canto de fora mais alto (amendoa)
    vv = n.cross(uu).normalized()
    if vv.dot(up) < 0: vv = -vv
    S = c - n * R_E
    OLHOS[lado] = dict(c=c, n=n, uu=uu, vv=vv, S=S)
def local(o, p):
    q = p - o["c"]; return q.dot(o["uu"]), q.dot(o["vv"]), q.dot(o["n"])
def elip(o, p):
    u, v, d = local(o, p); return math.sqrt((u / A_EL) ** 2 + (v / B_EL) ** 2), u, v, d
print("V2 olho simetrizado: centro E", tuple(round(x, 3) for x in OLHOS["E"]["c"]), "fenda %.3f x %.3f" % (2 * A_EL, 2 * B_EL), flush=True)

# ------------------------------------------------------------------ 2) refina a malha em volta dos olhos
for passo in range(3):
    reg = set()
    for f in bm.faces:
        for o in OLHOS.values():
            if any(elip(o, v.co)[0] < (2.6 if passo < 2 else 1.6) and abs(local(o, v.co)[2]) < 0.2 for v in f.verts): reg.add(f)
    arest = list({e for f in reg for e in f.edges})
    bmesh.ops.subdivide_edges(bm, edges=arest, cuts=1, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])
bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
# BVH da pele ANTES do recorte: o globo copia as UVs dessa superficie (a iris pintada)
bvh1 = BVHTree.FromBMesh(bm); tri = {f.index: ([l.vert.co.copy() for l in f.loops], [l[uvl].uv.copy() for l in f.loops]) for f in bm.faces}
def uv_em(p, n):
    loc, nr, i, d = bvh1.ray_cast(p + n * 0.3, -n, 0.7)
    if loc is None: return None
    cs, uvs = tri[i]
    w = barycentric_transform(loc, cs[0], cs[1], cs[2], V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1)))
    return uvs[0] * w.x + uvs[1] * w.y + uvs[2] * w.z

# ------------------------------------------------------------------ 3) fenda, margem no globo, globo e pesos das palpebras
PIVO_OLHOS = {}; PINTAR_PALP = []
IRIS_C, IRIS_R = V((0.96, 0.54)), 0.036                                 # amostra propria da iris (faixa u>0,92)
K_UV = IRIS_R * 0.92 / (LI / 2)                                          # raio da iris no mundo -> raio na amostra
for lado, o in OLHOS.items():
    dentro = [f for f in bm.faces if elip(o, f.calc_center_median())[0] < 1.0 and abs(local(o, f.calc_center_median())[2]) < 0.1]
    bmesh.ops.delete(bm, geom=dentro, context="FACES_ONLY")
    arest_b = [e for e in bm.edges if e.is_boundary and all(elip(o, v.co)[0] < 1.8 for v in e.verts)]
    bmesh.ops.subdivide_edges(bm, edges=arest_b, cuts=1)                # margem mais densa (linha de encontro sem frestas)
    borda = [v for v in bm.verts if v.is_boundary and elip(o, v.co)[0] < 1.8 and abs(local(o, v.co)[2]) < 0.15]
    c, n, uu, vv = o["c"], o["n"], o["uu"], o["vv"]
    marg = []
    for v in borda:                                                   # margem exatamente na amendoa (mantem a altura da pele)
        e, u, vq, d = elip(o, v.co); u, vq = u / max(e, 1e-4), vq / max(e, 1e-4)
        marg.append((v, c + uu * u + vv * vq + n * d))
    # raio do globo ajustado para a esfera passar pela pele da margem (sem cratera nem fresta)
    dl_ = 0.004; Rs = []
    for v, m in marg:
        q = m - c; den = 2 * dl_ - 2 * n.dot(q)
        if den > 1e-4: Rs.append((q.length_squared - dl_ * dl_) / den)
    R = float(np.clip(np.median(Rs), 0.08, 0.40)) if Rs else R_E
    S = c - n * R; o["S"], o["R"] = S, R
    for v, m in marg:                                                 # de cima um pouco por fora da de baixo (sem coplanaridade)
        v.co = S + (m - S).normalized() * (R + (0.006 if (m - c).dot(vv) > 0 else 0.002))
    print("V2 olho", lado, "faces recortadas", len(dentro), "margem", len(borda), "raio do globo %.3f" % R, flush=True)
    # globo: calota; UV plana na amostra da iris (os dois olhos usam a mesma iris)
    # calota com o FORMATO da amendoa, so 15% alem da fenda: fora disso nao ha globo para atravessar a pele esticada
    NR, NS = 6, 24
    pts = [[S + n * R]] + [[S + (n * R + uu * (1.15 * A_EL * k / NR * math.cos(2 * math.pi * s_ / NS))
                                 + vv * (1.15 * B_EL * k / NR * math.sin(2 * math.pi * s_ / NS))).normalized() * R
                            for s_ in range(NS)] for k in range(1, NR + 1)]
    def uv_iris(p):
        q = p - S; return IRIS_C + V((q.dot(uu), q.dot(vv))) * K_UV
    vs = [[bm.verts.new(p) for p in anel] for anel in pts]
    fglobo = []
    def fz(vv_):
        f = bm.faces.new(vv_)
        for l_ in f.loops: l_[uvl].uv = uv_iris(l_.vert.co)
        f.smooth = True; fglobo.append(f); return f
    for s_ in range(NS): fz((vs[0][0], vs[1][s_], vs[1][(s_ + 1) % NS]))
    for k in range(1, NR):
        for s_ in range(NS): fz((vs[k][s_], vs[k + 1][s_], vs[k + 1][(s_ + 1) % NS], vs[k][(s_ + 1) % NS]))
    bmesh.ops.recalc_face_normals(bm, faces=fglobo)
    if fglobo[0].normal.dot(fglobo[0].calc_center_median() - S) < 0:
        for f in fglobo: f.normal_flip()
    # anel de pele em volta da fenda suavizado (sem pontas nos cantos); a margem fica parada
    marg_set = {v for v, m in marg}
    anel_v = [v for v in bm.verts if v not in marg_set and 1.0 < elip(o, v.co)[0] < 1.7 and abs(local(o, v.co)[2]) < 0.15]
    for _ in range(3): bmesh.ops.smooth_vert(bm, verts=anel_v, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    # pesos pela geometria REAL: cada coluna gira o que falta para a margem chegar a linha de encontro
    def elev(p): q = p - S; return math.atan2(q.dot(vv), q.dot(n))
    t_meet = -0.30 * math.atan2(B_EL, R); SOBRA_S, SOBRA_I = math.radians(1.5), math.radians(0.5)
    ms = sorted([(elip(o, v.co)[1], elev(v.co)) for v in marg_set if elip(o, v.co)[2] > 0])
    mi = sorted([(elip(o, v.co)[1], elev(v.co)) for v in marg_set if elip(o, v.co)[2] <= 0])
    def interp(tab, u):
        if not tab: return 0.0
        if u <= tab[0][0]: return tab[0][1]
        if u >= tab[-1][0]: return tab[-1][1]
        for (u0, t0), (u1, t1) in zip(tab, tab[1:]):
            if u0 <= u <= u1: return t0 + (t1 - t0) * (u - u0) / max(u1 - u0, 1e-6)
        return tab[-1][1]
    A_S = max(t - t_meet + SOBRA_S for u, t in ms); A_I = max(t_meet + SOBRA_I - t for u, t in mi)
    globo_v = {v for a in vs for v in a}
    for v in bm.verts:
        if v in globo_v: continue
        e, u, vq, d = elip(o, v.co)
        if e < 0.90 or e > 2.4 or abs(d) > 0.25: continue
        e = max(e, 1.0); uc = max(-A_EL, min(A_EL, u / e))
        if vq > 0:
            w = (1 - suave((e - 1) / 1.3)) * max(0.0, interp(ms, uc) - t_meet + SOBRA_S) / A_S
            if v in marg_set: w = max(0.0, elev(v.co) - t_meet + SOBRA_S) / A_S
            if w > 0.01: v[dl][G["Palpebra_Sup_" + lado]] = min(w, 1.0)
        else:
            w = (1 - suave((e - 1) / 0.8)) * max(0.0, t_meet + SOBRA_I - interp(mi, uc)) / A_I
            if v in marg_set: w = max(0.0, t_meet + SOBRA_I - elev(v.co)) / A_I
            if w > 0.01: v[dl][G["Palpebra_Inf_" + lado]] = min(w, 1.0)
    # triangulos de UV da pele em volta da fenda (para repintar a iris que o Meshy pintou alem da fenda)
    for f in bm.faces:
        if f.verts[0] in globo_v or len(f.verts) != 3: continue
        es = [elip(o, v.co)[0] for v in f.verts]
        if min(es) < 2.0 and all(abs(local(o, v.co)[2]) < 0.2 for v in f.verts):
            PINTAR_PALP.append(([l[uvl].uv.copy() for l in f.loops], es))
    eixo = n.cross(vv).normalized()                                       # +ang leva n para vv (abre a de cima)
    PIVO_OLHOS[lado] = {"centro_globo": list(S), "raio_globo": R, "eixo": list(eixo), "fechar_sup_graus": -math.degrees(A_S),
                        "fechar_inf_graus": math.degrees(A_I), "fenda": [2 * A_EL, 2 * B_EL], "inclinacao_graus": math.degrees(INCL),
                        "nota": "girar a pele ponderada em torno do eixo no centro do globo; a margem desliza sobre ele"}

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
    ini = max(pontas, key=lambda v: v.co.x) if pontas else next(iter(viz))   # comeca no canto esquerdo (+X)
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
print("V2 boca: labio superior", len(CS), "inferior", len(CI), "cx %.3f" % CX, flush=True)
def espessuras(y):
    c = V((CX, y, z_boca(y))); up_, dn_ = saida(c, Z), saida(c, -Z)
    return (up_ or 0.20), (dn_ or 0.10)
AMOSTRAS = {"labio": (0.10, 0.09, 0.10), "gengiva": (0.62, 0.32, 0.34), "palato": (0.48, 0.20, 0.22), "assoalho": (0.40, 0.15, 0.17),
            "lingua": (0.70, 0.36, 0.38), "dente": (0.92, 0.89, 0.80), "garganta": (0.10, 0.03, 0.04)}
FAIXA = {k: 0.02 + 0.06 * i for i, k in enumerate(AMOSTRAS)}
def uvq(k): return V((0.96, FAIXA[k] + 0.03))
novos_sup, novos_inf, faces_novas = [], [], {}
def face(vs_, tipo):
    try: f = bm.faces.new(vs_)
    except ValueError: return None
    for l_ in f.loops: l_[uvl].uv = uvq(tipo)
    faces_novas[f] = tipo; return f
def anel_interno(C, sinal, lista):
    """para cada vertice da borda: rolo do labio (para dentro) e crista da gengiva"""
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
    return Gg[:im + 1][::-1], Gg[im:]                                   # cada metade com y crescente
for Gg, SP, tipo in ((GS, SP_S, "palato"), (GI, SP_I, "assoalho")):
    esq, dir_ = metades(Gg); ziper(esq, SP, tipo); ziper(dir_, SP, tipo)
# garganta: fecha o fundo entre cima e baixo, recuada para dar profundidade
def fileira(R_, Gg, SP): return [R_[0], Gg[0], SP[-1], Gg[-1], R_[-1]]
fs, fi = fileira(RS, GS, SP_S), fileira(RI, GI, SP_I)
gar = [bm.verts.new((a.co + b.co) / 2 + V((0, 0.10, 0))) for a, b in zip(fs, fi)]
for k in range(4):
    face((fs[k], fs[k + 1], gar[k + 1], gar[k]), "garganta"); face((gar[k], gar[k + 1], fi[k + 1], fi[k]), "garganta")
for C, R1, R2 in ((CS[0], RS[0], RI[0]), (CS[-1], RS[-1], RI[-1])):
    face((C, R1, R2), "labio")
# normais para dentro da boca
for f, tipo in faces_novas.items():
    c = f.calc_center_median(); alvo = V((CX, min(c.y, CANTO - 0.12), z_boca(c.y)))
    f.normal_update()
    if f.normal.dot(alvo - c) < 0: f.normal_flip()
# dentes nas cristas da gengiva
DENTES = []
def dente(base, eixo_, comp, larg, prof, curva, tipo_lista):
    """cone afilado e curvo, achatado (larg x prof), 4 aneis x 6"""
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
    """posicoes ao longo de cada metade, a partir da frente: distancia acumulada"""
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
# lingua sobre o assoalho
yl = np.linspace(ys[0] + 0.05, CANTO - 0.07, 8); aneis = []
for k, y in enumerate(yl):
    up_, dn_ = espessuras(y); hw = max(abs(v.co.x - CX) for v in CI if abs(v.co.y - y) < 0.06) if any(abs(v.co.y - y) < 0.06 for v in CI) else 0.1
    t = k / (len(yl) - 1); larg = 0.55 * hw * (math.sqrt(min(1.0, t * 3.0)) * 0.7 + 0.3); esp_ = 0.22 * dn_ + 0.008
    c = V((CX, y, z_boca(y) - 0.45 * dn_ + esp_ * 0.9))
    anel = []
    for i in range(10):
        an = 2 * math.pi * i / 10; zz = math.sin(an) * esp_ * (0.75 if math.sin(an) < 0 else 1.0)
        if abs(math.cos(an)) < 0.35 and math.sin(an) > 0: zz -= 0.3 * esp_                    # sulco no meio
        anel.append(bm.verts.new(c + V((math.cos(an) * larg, 0, zz))))
    aneis.append(anel)
for a1, a2 in zip(aneis, aneis[1:]):
    for i in range(10): face((a1[i], a1[(i + 1) % 10], a2[(i + 1) % 10], a2[i]), "lingua")
face(aneis[0][::-1], "lingua"); face(aneis[-1], "lingua")
novos_inf += [v for a in aneis for v in a]
for f in [f for f, t in faces_novas.items() if t in ("lingua", "dente")]:
    f.normal_update()
bmesh.ops.recalc_face_normals(bm, faces=[f for f, t in faces_novas.items() if t in ("lingua", "dente")])
pele_bvh = bvh2; movidos = 0
for lista, sinal in ((novos_inf + gar, -1), (novos_sup, +1)):
    d_ = Z * sinal                                                     # dentro = ao seguir d_ sai-se da pele
    for v in lista:
        loc, nr, i, dd = pele_bvh.ray_cast(v.co, d_, 2.0)
        if loc is not None and nr.dot(d_) > 0: continue                 # ja esta dentro
        loc, nr, i, dd = pele_bvh.ray_cast(v.co, -d_, 2.0)               # fora: volta ate a pele e entra um pouco
        if loc is not None and dd < 0.12: v.co = loc - d_ * 0.018; movidos += 1
print("V2 boca: vertices do interior trazidos para dentro da pele", movidos, flush=True)
for v in novos_sup: v[dl][G["Boca_Superior"]] = 1.0
for v in novos_inf: v[dl][G["Boca_Inferior"]] = 1.0
for v in gar: v[dl][G["Boca_Superior"]] = 0.5; v[dl][G["Boca_Inferior"]] = 0.5
for f in faces_novas: f.smooth = True
bm.to_mesh(me); me.update(); bm.free()
print("V2 boca: faces novas", len(faces_novas), "dentes", len(DENTES), flush=True)

# ------------------------------------------------------------------ 5) amostras de cor e brilho do olho nas texturas
mat = me.materials[0]; imgs = {n.image.name.split("_")[-1]: n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE"}
for k, im in imgs.items():
    W = im.size[0]; arr = np.empty(W * W * 4, np.float32); im.pixels.foreach_get(arr); arr = arr.reshape(W, W, 4)
    c0 = int(0.92 * W)
    for nome, cor in AMOSTRAS.items():
        r0, r1 = int(FAIXA[nome] * W), int((FAIXA[nome] + 0.06) * W)
        if k == "cor": arr[r0:r1, c0:, :3] = cor
        elif k == "normal": arr[r0:r1, c0:, :3] = (0.5, 0.5, 1.0)
        elif k == "rugosidade": arr[r0:r1, c0:, :3] = 0.35 if nome == "dente" else (0.30 if nome in ("lingua", "gengiva", "palato") else 0.6)
        else: arr[r0:r1, c0:, :3] = 0.0
    # palpebras: margem escura (borda palpebral fina) e a tinta azul do Meshy fora da fenda vira pelo claro
    if k in ("cor", "rugosidade"):
        for uvs, es in PINTAR_PALP:
            P = np.array([[uv.x * W, uv.y * W] for uv in uvs]); x0, y0 = np.floor(P.min(0)).astype(int); x1, y1 = np.ceil(P.max(0)).astype(int) + 1
            x0, y0 = max(x0, 0), max(y0, 0); x1, y1 = min(x1, W), min(y1, W)
            if x1 <= x0 or y1 <= y0: continue
            gy, gx = np.mgrid[y0:y1, x0:x1]; px_ = gx + 0.5; py_ = gy + 0.5
            (ax_, ay_), (bx_, by_), (cx_, cy_) = P
            den = (by_ - cy_) * (ax_ - cx_) + (cx_ - bx_) * (ay_ - cy_)
            if abs(den) < 1e-9: continue
            l1 = ((by_ - cy_) * (px_ - cx_) + (cx_ - bx_) * (py_ - cy_)) / den; l2 = ((cy_ - ay_) * (px_ - cx_) + (ax_ - cx_) * (py_ - cy_)) / den
            l3 = 1 - l1 - l2; dentro_t = (l1 >= -0.02) & (l2 >= -0.02) & (l3 >= -0.02)
            e_px = l1 * es[0] + l2 * es[1] + l3 * es[2]
            sub = arr[y0:y1, x0:x1]
            borda = dentro_t & (e_px < 1.10)
            azul = dentro_t & (e_px >= 1.10) & (sub[..., 2] > sub[..., 0] + 0.06)
            if k == "cor":
                sub[borda, :3] = (0.07, 0.07, 0.08)
                mix_ = np.clip((e_px - 1.10) / 0.35, 0, 1)[..., None]
                alvo = (1 - mix_) * np.array([0.42, 0.43, 0.46]) + mix_ * np.array([0.86, 0.87, 0.90])
                sub[azul, :3] = alvo[azul]
            else:
                sub[borda, :3] = 0.45
    # iris azul-gelo pintada na amostra propria: pupila, iris clara perto da pupila, anel escuro e entorno escuro
    yy, xx = np.mgrid[0:W, 0:W]; du = (xx + 0.5) / W - IRIS_C.x; dv = (yy + 0.5) / W - IRIS_C.y
    r = np.sqrt(du * du + dv * dv) / IRIS_R; ang = np.arctan2(dv, du)
    zona = r < 1.25
    if k == "cor":
        raios = 0.06 * np.sin(ang * 23) + 0.04 * np.sin(ang * 51 + 1.3)
        t = np.clip((r - 0.24) / 0.66, 0, 1)
        iris = np.stack([0.62 - 0.30 * t, 0.90 - 0.22 * t, 1.0 - 0.05 * t], -1) * (1 + raios[..., None])
        cor = np.where((r < 0.24)[..., None], np.array([0.02, 0.02, 0.025]), iris)
        cor = np.where(((r >= 0.86) & (r < 1.0))[..., None], np.array([0.10, 0.22, 0.34]), cor)
        cor = np.where((r >= 1.0)[..., None], np.array([0.06, 0.055, 0.06]), cor)
        arr[zona, :3] = np.clip(cor[zona], 0, 1)
    elif k == "normal": arr[zona, :3] = (0.5, 0.5, 1.0)
    elif k == "rugosidade": arr[zona, :3] = 0.10
    else:
        arr[zona, :3] = 0.0; brilho = zona & (r >= 0.30) & (r < 0.86); arr[brilho, :3] = (0.05, 0.12, 0.16)
    im.pixels.foreach_set(arr.ravel()); im.update(); im.save()
print("V2 texturas atualizadas", list(imgs), flush=True)

# ------------------------------------------------------------------ 6) LODs da cabeca, export, pivos
def tris(o): return sum(len(p.vertices) - 2 for p in o.data.polygons)
for nome, alvo in (("LOD1_Cabeca", 3600), ("LOD2_Cabeca", 1100)):
    old = bpy.data.objects.get(nome)
    if old: bpy.data.objects.remove(old)
    c = cab.copy(); c.data = cab.data.copy(); c.name = c.data.name = nome; sc.collection.objects.link(c)
    bpy.ops.object.select_all(action="DESELECT"); c.select_set(True); bpy.context.view_layer.objects.active = c
    d = c.modifiers.new("D", "DECIMATE"); d.ratio = alvo / tris(c); bpy.ops.object.modifier_apply(modifier="D"); c.hide_render = True
ob = {o.name: o for o in sc.objects}
def exportar(nomes, arq):
    bpy.ops.object.select_all(action="DESELECT")
    for n_ in nomes: ob[n_].hide_set(False); ob[n_].select_set(True)
    bpy.context.view_layer.objects.active = ob[nomes[0]]
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, arq), export_format="GLB", use_selection=True, export_image_format="AUTO", export_yup=True)
PEL = [n for n in ("LOW_Pelagem", "LOW_Marca") if n in ob]; PEL1 = [n for n in ("LOD1_Pelagem", "LOW_Marca") if n in ob]
exportar(["LOW_Cabeca", "LOW_Corpo", "LOW_Cristais"] + PEL, "CR_LoboArtico_LOW.glb")
exportar(["LOD1_Cabeca", "LOD1_Corpo", "LOW_Cristais"] + PEL1, "CR_LoboArtico_LOD1.glb")
exportar(["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"], "CR_LoboArtico_LOD2.glb")
piv = dict(PIV0); piv["olhos"] = PIVO_OLHOS
piv["mandibula"]["nota"] = "corte dos labios a frente do canto; saco bucal soldado as bordas: grupo Boca_Inferior segue a mandibula, Boca_Superior o cranio"
json.dump(piv, open(os.path.join(OUT, "rig_pivos.json"), "w"), indent=1)
reg = {k: tris(ob[k]) for k in ("LOW_Cabeca", "LOW_Corpo", "LOW_Cristais", "LOD1_Cabeca", "LOD1_Corpo", "LOD2_Cabeca", "LOD2_Corpo") + tuple(dict.fromkeys(PEL + PEL1))}
json.dump(reg, open(os.path.join(OUT, "custo_v2.json"), "w"), indent=1); print("V2_TRIS", reg, flush=True)
for n_ in ("LOD1_Cabeca", "LOD1_Corpo", "LOD2_Cabeca", "LOD2_Corpo") + tuple(n for n in PEL1 if n.startswith("LOD")): ob[n_].hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_LOW.blend"))
print("V2_OK")
