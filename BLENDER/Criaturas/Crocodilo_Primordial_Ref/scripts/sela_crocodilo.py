"""Lote 5: SELA DEFINITIVA do Crocodilo Primordial (proposta para aprovacao; substitui o volume de teste do Lote 4).
Pecas (uma malha 'CR_Croc_Sela', 3 materiais):
 - manta de tecido grosso que veste o dorso: no meio passa por cima das cristas (envelope suave), na borda cai sobre a
   pele como pano (acompanha as cristas);
 - assento de couro com cabeca (frente, com alca de bronze para a mao) e patilha (atras), apoiado na manta;
 - cilha de couro em volta da barriga (entre as patas dianteiras e traseiras), presa a argolas de bronze na borda da manta;
 - estribos triangulares de bronze nos DOIS lados, pendurados em argolas na lateral do assento, sob o pe do cavaleiro sentado.
Pesos: copiados da pele do crocodilo (media suave em volta do ponto mais proximo, no maximo 4 ossos) para a manta, o
assento e a cilha acompanharem o corpo; argolas, alca e estribos sao rigidos (pesos do ponto de ancoragem).
Nada da criatura e alterado (malha, rig e escala). Eixos: frente -Y, Z para cima, esquerda +X. Modulo + script:
blender -b CR_Crocodilo_Anim.blend -P sela_crocodilo.py -- [saida.blend]"""
import bpy, bmesh, math, sys, os
import numpy as np
from mathutils import Vector as V, Matrix as M
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

NOME = "CR_Croc_Sela"
MANTA = dict(ax=2.05, ay=1.42, yc=-4.66, n=6.0, esp=0.07, nu=24, nv=18, debrum=0.93)
ABA = dict(ax=1.42, ay=0.80, yc=-4.70, n=3.0, esp=0.045, nu=14, nv=10)
ASSENTO = dict(ax=1.00, ay=0.98, yc=-4.66, n=3.2, nu=18, nv=16)
ASSENTO_Y = -4.6                       # quadril do cavaleiro (o mesmo do Lote 4, preso ao osso Coluna1)
DZ_QUADRIL = 0.55                      # quadril acima do topo do assento no centro (coxas de 1 stud apoiadas)
CILHA = dict(y=-3.95, larg=0.42, dentro=0.065, esp=0.08, nseg=44)    # atras do alcance das patas dianteiras recolhidas (nado)
X0, X1, Y0, Y1, PASSO = -2.8, 2.8, -6.8, -2.4, 0.05

def _ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

def _maxf(a, r):
    out = a.copy(); H, W = a.shape; p = np.pad(a, r, mode="edge")
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r: out = np.maximum(out, p[r + dy:r + dy + H, r + dx:r + dx + W])
    return out

def _blur(a, r, it=2):
    for _ in range(it):
        p = np.pad(a, r, mode="edge"); c = np.cumsum(np.cumsum(p, 0), 1); c = np.pad(c, ((1, 0), (1, 0)))
        k = 2 * r + 1; H, W = a.shape
        a = (c[k:k + H, k:k + W] - c[0:H, k:k + W] - c[k:k + H, 0:W] + c[0:H, 0:W]) / (k * k)
    return a

class Campo:
    """campo de alturas (z) amostrado numa grade regular e lido com interpolacao bilinear"""
    def __init__(self, z): self.z = z
    def __call__(self, x, y):
        fx = (x - X0) / PASSO; fy = (y - Y0) / PASSO; H, W = self.z.shape
        i0 = int(np.clip(math.floor(fy), 0, H - 2)); j0 = int(np.clip(math.floor(fx), 0, W - 2)); u = fx - j0; v = fy - i0
        z = self.z
        return float((1 - v) * ((1 - u) * z[i0, j0] + u * z[i0, j0 + 1]) + v * ((1 - u) * z[i0 + 1, j0] + u * z[i0 + 1, j0 + 1]))
    def grad(self, x, y, h=0.05): return ((self(x + h, y) - self(x - h, y)) / (2 * h), (self(x, y + h) - self(x, y - h)) / (2 * h))

def _forma(u, v, ax, ay, yc, n):
    """grade (u, v) em [-1, 1] -> contorno super-elipse (retangulo arredondado); devolve x, y, rho (0 centro, 1 borda)"""
    rho = max(abs(u), abs(v))
    if rho < 1e-9: return 0.0, yc, 0.0
    a, b = abs(u) / rho, abs(v) / rho; t = (a ** n + b ** n) ** (-1.0 / n)
    return u * t * ax, yc + v * t * ay, rho

def _placa(fundo, topo, nu, nv, forma, normal_off=None):
    """malha fechada a partir de dois campos sobre a grade da forma: fundo(x, y, rho) e topo(x, y, rho) -> pontos 3D"""
    us = np.linspace(-1, 1, nu); vs = np.linspace(-1, 1, nv); vb, vt = [], []
    for v in vs:
        for u in us:
            x, y, rho = forma(u, v); vb.append(fundo(x, y, rho)); vt.append(topo(x, y, rho))
    n = nu * nv; fs = []; fr = []
    for j in range(nv - 1):
        for i in range(nu - 1):
            a = j * nu + i; fs.append((a, a + 1, a + nu + 1, a + nu)); fs.append((a + n, a + nu + n, a + nu + 1 + n, a + 1 + n))
            r_ = max(abs(us[i] + us[i + 1]), abs(vs[j] + vs[j + 1])) / 2; fr += [r_, r_]
    borda = ([i for i in range(nu)] + [j * nu + nu - 1 for j in range(1, nv)] + [(nv - 1) * nu + i for i in range(nu - 2, -1, -1)]
             + [j * nu for j in range(nv - 2, 0, -1)])
    for a, b in zip(borda, borda[1:] + borda[:1]): fs.append((b, a, a + n, b + n)); fr.append(1.0)
    return vb + vt, fs, fr

def _tubo(pts, raio, lados=6, fechado=False):
    vs, fs = [], []; n = len(pts)
    for k, p in enumerate(pts):
        a = pts[(k + 1) % n] - pts[k - 1] if fechado else (pts[min(k + 1, n - 1)] - pts[max(k - 1, 0)])
        t = a.normalized(); b = t.orthogonal().normalized(); c = t.cross(b)
        for s in range(lados):
            ang = 2 * math.pi * s / lados; vs.append(p + (b * math.cos(ang) + c * math.sin(ang)) * raio)
    for k in range(n if fechado else n - 1):
        k2 = (k + 1) % n
        for s in range(lados):
            s2 = (s + 1) % lados; fs.append((k * lados + s, k * lados + s2, k2 * lados + s2, k2 * lados + s))
    if not fechado:
        fs.append(tuple(range(lados - 1, -1, -1))); fs.append(tuple((n - 1) * lados + s for s in range(lados)))
    return vs, fs

def _caixa_orient(c, ex, ey, ez):
    vs = [c + ex * a + ey * b + ez * d for a in (-1, 1) for b in (-1, 1) for d in (-1, 1)]
    fs = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return vs, fs

def criar(croc, lo, colecao=None, pes_cavaleiro=None):
    """constroi a sela na pose de DESCANSO do crocodilo. pes_cavaleiro: {"Left": tornozelo, "Right": tornozelo} no mundo
    (pose sentada); sem isso usa os alvos do manequim (manequim_r15.SENTADO). Devolve (objeto, z do quadril sentado, info)."""
    sc = bpy.context.scene; col = colecao or sc.collection
    acao0 = croc.animation_data.action if croc.animation_data else None
    if croc.animation_data: croc.animation_data.action = None
    for pb in croc.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); ev = lo.evaluated_get(dg); me = ev.to_mesh(); W = lo.matrix_world
    pele_v = [W @ v.co for v in me.vertices]; me.calc_loop_triangles()
    tris = [tuple(t.vertices) for t in me.loop_triangles]
    gn = {g.index: g.name for g in lo.vertex_groups}; ossos = [b.name for b in croc.data.bones]; oi = {n: i for i, n in enumerate(ossos)}
    Wp = np.zeros((len(me.vertices), len(ossos)))
    for v in me.vertices:
        for g in v.groups:
            nm = gn.get(g.group)
            if nm in oi: Wp[v.index, oi[nm]] = g.weight
    ev.to_mesh_clear()
    bvh = BVHTree.FromPolygons(pele_v, tris); kd = KDTree(len(pele_v))
    for i, p in enumerate(pele_v): kd.insert(p, i)
    kd.balance()
    # ---------------------------------------------------------------- campo de alturas da pele (raio de cima para baixo)
    xs = np.arange(X0, X1 + 1e-6, PASSO); ys = np.arange(Y0, Y1 + 1e-6, PASSO); H = np.full((len(ys), len(xs)), 0.0)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            hit = bvh.ray_cast(V((x, y, 12.0)), V((0, 0, -1))); H[j, i] = hit[0].z if hit[0] else 0.0
    pele = Campo(H)
    # envelope do meio: passa por cima das cristas e e liso (iteracoes de suavizar + nunca abaixo das cristas)
    piso = _maxf(H, 2) + 0.035; E = _maxf(H, 7)
    for _ in range(6): E = np.maximum(_blur(E, 5), piso)
    E = _blur(np.maximum(E, piso), 2, 1); E = np.maximum(E, piso)
    # borda: pano caido sobre a pele (suave de leve, acompanha as cristas)
    B = _maxf(H, 4) + 0.03; B = np.maximum(_blur(B, 2, 1), _maxf(H, 3) + 0.02)
    env, borda_pele = Campo(E), Campo(B)
    m = MANTA
    def forma_m(u, v): return _forma(u, v, m["ax"], m["ay"], m["yc"], m["n"])
    def manta_fundo_z(x, y, rho):
        w = float(_ss(0.55, 0.97, rho)); return env(x, y) * (1 - w) + borda_pele(x, y) * w
    def manta_fundo(x, y, rho): return V((x, y, manta_fundo_z(x, y, rho)))
    def manta_normal(x, y, rho, h=0.06):
        dzx = (manta_fundo_z(x + h, y, rho) - manta_fundo_z(x - h, y, rho)) / (2 * h); dzy = (manta_fundo_z(x, y + h, rho) - manta_fundo_z(x, y - h, rho)) / (2 * h)
        return V((-dzx, -dzy, 1)).normalized()
    def manta_topo(x, y, rho):
        e = m["esp"] * (0.55 + 0.45 * (1 - float(_ss(0.9, 1.0, rho))))        # borda um pouco mais fina (bainha)
        return manta_fundo(x, y, rho) + manta_normal(x, y, rho) * e
    pecas = []                                                   # (vs, fs, material, tipo de peso, ancora)
    vs, fs, fr = _placa(manta_fundo, manta_topo, m["nu"], m["nv"], forma_m)
    pecas.append((vs, fs, 1, "pele", None))
    # debrum: cordao de tecido ocre ao longo da borda de cima da manta (acabamento e esconde a espessura)
    cord = []
    for k in range(48):
        c_, s_ = math.cos(2 * math.pi * k / 48), math.sin(2 * math.pi * k / 48); mx_ = max(abs(c_), abs(s_))
        x, y, _ = forma_m(c_ / mx_, s_ / mx_); cord.append(manta_topo(x, y, 1.0) - manta_normal(x, y, 1.0) * 0.015)
    vs, fs = _tubo(cord, 0.05, 5, fechado=True); pecas.append((vs, fs, 3, "pele", None))
    manta_top_z = lambda x, y: manta_topo(x, y, 0.0).z           # topo da manta no meio (vertical)
    # aba de couro escuro entre a manta e o assento (mais larga que o assento, protege a manta das pernas)
    b_ = ABA
    def forma_b(u, v): return _forma(u, v, b_["ax"], b_["ay"], b_["yc"], b_["n"])
    def aba_fundo(x, y, rho): return V((x, y, manta_top_z(x, y) + 0.015))          # folga: a manta e mais grossa entre os vertices
    def aba_topo(x, y, rho): return aba_fundo(x, y, rho) + V((0, 0, b_["esp"]))
    vs, fs, fr = _placa(aba_fundo, aba_topo, b_["nu"], b_["nv"], forma_b); pecas.append((vs, fs, 4, "pele", None))
    def aba_top_z(x, y):
        dentro_ = (abs(x) / b_["ax"]) ** b_["n"] + (abs(y - b_["yc"]) / b_["ay"]) ** b_["n"] <= 1
        return manta_top_z(x, y) + 0.015 + (b_["esp"] if dentro_ else 0.0)
    # ---------------------------------------------------------------- assento
    a = ASSENTO
    def forma_a(u, v): return _forma(u, v, a["ax"], a["ay"], a["yc"], a["n"])
    def uv_a(x, y): return x / a["ax"], (y - a["yc"]) / a["ay"]
    def espessura(x, y, rho):
        u, v = uv_a(x, y)
        t = 0.13 + 0.05 * float(_ss(0.0, 0.6, abs(v)))                                           # assento fundo no meio
        t += 0.46 * math.exp(-((v + 0.80) / 0.17) ** 2) * math.exp(-(u / 0.38) ** 2)              # cabeca (frente, -Y)
        t += 0.16 * math.exp(-((v + 0.72) / 0.22) ** 2) * math.exp(-(u / 0.75) ** 2)              # arcada da cabeca
        t += 0.46 * float(_ss(0.30, 0.84, v)) * (1 - 0.50 * u * u)                               # patilha (atras)
        t += 0.07 * float(_ss(0.55, 0.95, abs(u))) * (1 - float(_ss(0.3, 0.9, abs(v))))          # bordas laterais (joelheiras)
        e = 1 - float(_ss(0.80, 1.0, rho)) ** 1.5
        return 0.045 + (t - 0.045) * e
    def assento_fundo(x, y, rho): return V((x, y, aba_top_z(x, y) - 0.004))
    def assento_topo(x, y, rho): return assento_fundo(x, y, rho) + V((0, 0, espessura(x, y, rho)))
    vs, fs, fr = _placa(assento_fundo, assento_topo, a["nu"], a["nv"], forma_a); pecas.append((vs, fs, 0, "pele", None))
    z_fundo_c = aba_top_z(0.0, ASSENTO_Y) - 0.004; z_assento = z_fundo_c + espessura(0.0, ASSENTO_Y, 0.0)
    Zq = z_assento + DZ_QUADRIL
    # alca de bronze na cabeca do assento
    yh = a["yc"] - 0.80 * a["ay"]; zc = assento_topo(0.0, yh, 0.0).z
    arco = [V((0.30 * math.cos(math.pi * k / 10), yh - 0.04, zc - 0.10 + 0.30 * math.sin(math.pi * k / 10))) for k in range(11)]
    vs, fs = _tubo(arco, 0.065, 6); pecas.append((vs, fs, 2, "rigido", V((0, yh, zc))))
    # ---------------------------------------------------------------- cilha (barriga) + argolas na borda da manta
    c = CILHA; cy = c["y"]; zc0 = 3.0
    def raio_corte(phi):
        d = V((math.cos(phi), 0, math.sin(phi))); best = 0.0
        for dy in (-c["larg"] / 2, 0.0, c["larg"] / 2):
            o = V((0, cy + dy, zc0)) + d * 9.0; hit = bvh.ray_cast(o, -d)
            if hit[0]: best = max(best, (hit[0] - V((0, cy + dy, zc0))).length)
        return best
    # angulo da borda da manta de cada lado (na altura do y da cilha)
    def borda_lado(s):
        x, y, _ = _forma(s * 1.0, (cy - m["yc"]) / m["ay"], m["ax"], m["ay"], m["yc"], m["n"]); p = manta_fundo(x, y, 1.0)
        return p, math.atan2(p.z - zc0, s * p.x)
    pE, aE = borda_lado(1); pD, aD = borda_lado(-1)
    ph = np.linspace(aE - math.radians(1.5), -math.pi - aD + math.radians(1.5), c["nseg"])
    r = np.array([raio_corte(p) for p in ph]); r = np.maximum(r, np.convolve(np.pad(r, 2, mode="edge"), np.ones(5) / 5, "valid"))
    r = np.convolve(np.pad(r, 2, mode="edge"), np.ones(5) / 5, "valid")
    r = r + c["dentro"]
    cvs = []
    for k, p in enumerate(ph):
        d = V((math.cos(p), 0, math.sin(p)))
        for off in (0.0, c["esp"]):
            for dy in (-c["larg"] / 2, c["larg"] / 2): cvs.append(V((0, cy + dy, zc0)) + d * (r[k] + off))
    cfs = []
    for k in range(len(ph) - 1):
        a0 = 4 * k; a1 = 4 * (k + 1)
        cfs += [(a0 + 2, a0 + 3, a1 + 3, a1 + 2), (a0 + 1, a0, a1, a1 + 1), (a0, a0 + 2, a1 + 2, a1), (a0 + 3, a0 + 1, a1 + 1, a1 + 3)]
    cfs += [(0, 1, 3, 2), tuple(4 * (len(ph) - 1) + i for i in (2, 3, 1, 0))]
    pecas.append((cvs, cfs, 0, "pele", None))
    for s, pb_, ab in ((1, pE, aE), (-1, pD, aD)):
        dn = V((s * math.cos(ab), 0, math.sin(ab))).normalized()
        cen = V((0, cy, zc0)) + V((math.cos(ab if s > 0 else math.pi - ab), 0, math.sin(ab if s > 0 else math.pi - ab))) * (raio_corte(ab if s > 0 else math.pi - ab) + 0.24)
        t1 = V((0, 1, 0)); t2 = dn.cross(t1).normalized()
        anel = [cen + (t1 * math.cos(2 * math.pi * k / 12) + t2 * math.sin(2 * math.pi * k / 12)) * 0.17 for k in range(12)]
        vs, fs = _tubo(anel, 0.045, 6, fechado=True); pecas.append((vs, fs, 2, "rigido", cen))
    # ---------------------------------------------------------------- apoios de pe (dois lados) sob o pe do cavaleiro sentado
    # o dorso e largo e as pernas do R15 sao curtas: o pe nao alcanca a manta. Em vez de estribo pendurado (ficaria solto
    # no ar sem cavaleiro), um bloco de couro fixo na manta sob a sola, com alca de bronze sobre o peito do pe. O corpo nao
    # e simetrico: cada bloco tem a altura do seu lado.
    if pes_cavaleiro is None:
        import manequim_r15 as mq
        Mq = M.Translation(V((0, ASSENTO_Y, Zq)))
        pes_cavaleiro = {lado: Mq @ (V((0.5 * s, 0, 0)) + V(mq.SENTADO[("IK", lado + "Foot")])) for lado, s in (("Left", 1), ("Right", -1))}
    info = {"z_quadril": Zq, "z_assento_centro": z_assento, "apoios_pe": {}}
    TG = math.tan(math.radians(20.0))                            # sola inclinada (dedos para baixo, como na pose sentada)
    for lado, s in (("Left", 1), ("Right", -1)):
        tz = pes_cavaleiro[lado]
        def sola(y, tz=tz): return tz.z - 0.30 / math.cos(math.radians(20.0)) - (tz.y - y) * TG - 0.025
        def forma_p(u, v, tz=tz): return _forma(u, v, 0.50, 0.46, tz.y - 0.05, 4.0)
        def p_fundo(x, y, rho, tz=tz): return V((tz.x + x, y, manta_topo(tz.x + x, y, 0.9).z - 0.03))
        def p_topo(x, y, rho, tz=tz):
            f = p_fundo(x, y, rho); z = max(sola(y), f.z + 0.06); e = float(_ss(0.35, 1.0, rho)) ** 1.6
            return V((f.x, f.y, f.z + 0.05 + (z - f.z - 0.05) * (1 - e)))       # almofada: topo plano sob a sola, borda redonda
        vs, fs, fr = _placa(p_fundo, p_topo, 10, 10, forma_p); pecas.append((vs, fs, 4, "pele", None))
        # tira de couro escuro da aba ate a almofada (sobre a manta)
        x0, x1 = s * (ABA["ax"] - 0.12), tz.x - s * 0.40; yt = tz.y - 0.05
        tira = []
        for k in range(7):
            x = x0 + (x1 - x0) * k / 6
            for dy in (-0.16, 0.16): tira.append((x, yt + dy))
        tv = [V((x, y, manta_topo(x, y, 0.8).z - 0.01)) for x, y in tira] + [V((x, y, manta_topo(x, y, 0.8).z + 0.035)) for x, y in tira]
        nt_ = len(tira); tf = []
        for k in range(6):
            a0, a1 = 2 * k, 2 * k + 2
            tf += [(a0 + nt_, a1 + nt_, a1 + 1 + nt_, a0 + 1 + nt_), (a0, a0 + 1, a1 + 1, a1), (a0, a1, a1 + nt_, a0 + nt_), (a0 + 1, a0 + 1 + nt_, a1 + 1 + nt_, a1 + 1)]
        tf += [(0, nt_, nt_ + 1, 1), (12, 13, 13 + nt_, 12 + nt_)]
        pecas.append((tv, tf, 4, "pele", None))
        ya = tz.y - 0.28; za = sola(ya)
        arco = [V((tz.x + 0.42 * math.cos(math.pi * k / 10), ya, za - 0.03 + 0.46 * math.sin(math.pi * k / 10))) for k in range(11)]
        vs, fs = _tubo(arco, 0.055, 6); pecas.append((vs, fs, 2, "pele", None))           # pontas na almofada (segue a almofada)
        info["apoios_pe"][lado] = {"tornozelo": [round(c_, 3) for c_ in tz], "sola_no_tornozelo": round(sola(tz.y) + 0.025, 3),
                                   "altura_bloco": round(sola(tz.y) - p_fundo(0, tz.y, 0).z, 3)}
    # ---------------------------------------------------------------- junta, materiais, UV, pesos
    allv, allf, mats, tipos = [], [], [], []
    for vs, fs, mt, tp, anc in pecas:
        o = len(allv); allv += [tuple(p) for p in vs]; allf += [tuple(i + o for i in f) for f in fs]
        mats += (mt if isinstance(mt, list) else [mt] * len(fs)); tipos.append((o, len(vs), tp, anc))
    me = bpy.data.meshes.new(NOME); me.from_pydata(allv, [], allf); me.update()
    for p, mt in zip(me.polygons, mats): p.material_index = mt
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(NOME, me); col.objects.link(ob)
    for p in me.polygons: p.use_smooth = True
    for nm, cor, rug, met in (("M_Sela_Couro", (0.16, 0.085, 0.04), 0.55, 0.0), ("M_Sela_Manta", (0.055, 0.075, 0.045), 0.92, 0.0),
                              ("M_Sela_Bronze", (0.55, 0.38, 0.16), 0.42, 1.0), ("M_Sela_Debrum", (0.26, 0.15, 0.05), 0.88, 0.0),
                              ("M_Sela_CouroEscuro", (0.07, 0.045, 0.03), 0.6, 0.0)):
        mt = bpy.data.materials.get(nm) or _material(nm, cor, rug, met); me.materials.append(mt)
    bpy.context.view_layer.objects.active = ob
    for o_ in bpy.context.selected_objects: o_.select_set(False)
    ob.select_set(True); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.01); bpy.ops.object.mode_set(mode="OBJECT")
    grupos = {n: ob.vertex_groups.new(name=n) for n in ossos if croc.data.bones[n].use_deform}
    def peso_em(p, raio=0.6):
        loc = bvh.find_nearest(p)[0] or p; acc = np.zeros(len(ossos)); tot = 0.0
        for (_, i, d) in kd.find_range(loc, raio):
            g = math.exp(-(d / (raio * 0.5)) ** 2); acc += Wp[i] * g; tot += g
        if tot == 0: _, i, _ = kd.find(loc); acc = Wp[i].copy(); tot = 1.0
        acc /= tot; idx = np.argsort(acc)[::-1][:4]; w = acc[idx]; w = w / w.sum() if w.sum() > 0 else w
        return [(ossos[k], float(x)) for k, x in zip(idx, w) if x > 1e-3]
    for o, n, tp, anc in tipos:
        fixo = peso_em(anc) if tp == "rigido" else None
        for vi in range(o, o + n):
            for nm, w in (fixo or peso_em(V(allv[vi]))):
                if nm in grupos: grupos[nm].add([vi], w, "REPLACE")
    ob.parent = croc; ob.matrix_parent_inverse = croc.matrix_world.inverted()
    md = ob.modifiers.new("Armature", "ARMATURE"); md.object = croc
    ob["lote"] = "L5 sela definitiva (proposta)"; ob["z_quadril"] = Zq
    if croc.animation_data: croc.animation_data.action = acao0
    info["tris"] = sum(len(p.vertices) - 2 for p in me.polygons); info["vertices"] = len(me.vertices)
    return ob, Zq, info

def _material(nome, cor, rug, met):
    mt = bpy.data.materials.new(nome); mt.use_nodes = True; nt = mt.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rug; b.inputs["Metallic"].default_value = met
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    ramp.color_ramp.elements[0].color = tuple(c * 0.70 for c in cor) + (1,); ramp.color_ramp.elements[1].color = tuple(min(1, c * 1.30) for c in cor) + (1,)
    if nome in ("M_Sela_Manta", "M_Sela_Debrum"):                # tecido: trama fina (bump de ondas cruzadas) + variacao
        nz.inputs["Scale"].default_value = 4.0
        nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
        w1 = nt.nodes.new("ShaderNodeTexWave"); w1.inputs["Scale"].default_value = 60; w1.bands_direction = "X"
        w2 = nt.nodes.new("ShaderNodeTexWave"); w2.inputs["Scale"].default_value = 60; w2.bands_direction = "Y"
        for w_ in (w1, w2): nt.links.new(tc.outputs["Object"], w_.inputs["Vector"])
        mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MULTIPLY"; nt.links.new(w1.outputs["Fac"], mx.inputs[0]); nt.links.new(w2.outputs["Fac"], mx.inputs[1])
        bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.18; nt.links.new(mx.outputs[0], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    else:
        nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
        bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.15; nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return mt

if __name__ == "__main__":
    import json
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    croc = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]
    for pb in croc.pose.bones:
        for c_ in pb.constraints: c_.mute = True
    ob, Zq, info = criar(croc, lo)
    print("SELA", json.dumps(info))
    if A: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A[0]))
    print("SELA_OK")
