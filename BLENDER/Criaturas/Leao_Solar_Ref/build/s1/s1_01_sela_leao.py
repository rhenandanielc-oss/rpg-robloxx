"""S1: SELA FELINA do Leao Solar (proposta para aprovacao). Metodo adaptado da sela aprovada do Crocodilo (sela_crocodilo.py,
Lote 5): campo de alturas do dorso por raios, manta que veste o dorso, aba, assento moldado, cilha por raios em volta da
barriga, apoios de pe fixos (o dorso e largo e as pernas do R15 sao curtas: estribo pendurado ficaria solto no ar), pesos
copiados da pele. Nada do leao e alterado (malha, rig, pesos, escala).

Materiais = os oficiais das Planicies Douradas (DOCS/biomas/planicies-douradas.md; RPG_01 25.3.1 / 25.6):
 - Couro das Planicies (material regional estrutural): assento, aba, cilha, apoios de pe;
 - Pele de Antilope (Antilope-das-Planicies): manta sob a sela (pelo curto dourado);
 - Tendao Elastico (do antilope): costura/debrum da manta e cordao das alcas;
 - Chifre Leve (do antilope): alca de apoio da mao na cabeca do assento;
 - Ambar Solar (material regional especial): pedra do adorno solar da cabeca e das argolas (sem emissao nem efeito);
 - Ferro (basico): argolas, guarnicao do adorno e alcas dos apoios de pe.
Eixos: frente -Y, Z para cima, x+ = lado direito do leao. A malha do leao esta ~0,45 deslocada para +X em relacao a
coluna do rig: a sela e centrada no corpo (XC), nao no osso.
Uso: blender -b Leao_Solar_Ref_E5_clipes_r6.blend -P s1_01_sela_leao.py -- <saida.blend> <saida.json>"""
import bpy, bmesh, math, sys, os, json
import numpy as np
from mathutils import Vector as V, Matrix as M
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

NOME = "Leao_Solar_Sela"
NOMES_PECA_MAT = {0: "assento", 1: "manta", 2: "tendao", 3: "alca_chifre", 4: "ambar", 5: "ferro"}
XC = 0.45                                             # centro do corpo no dorso (malha deslocada da coluna do rig)
MANTA = dict(ax=2.05, ay=2.10, yc=0.05, n=5.0, esp=0.07, nu=20, nv=20)   # r2: borda de tras em y 2,15 (o lombo dobra no galope)
ABA = dict(ax=1.45, ay=1.45, yc=0.15, n=3.0, esp=0.05, nu=12, nv=12)
ASSENTO = dict(ax=0.95, ay=1.25, yc=0.15, n=3.2, nu=16, nv=16)
ASSENTO_Y = 0.20                                      # quadril do cavaleiro (atras da juba, no trecho plano do dorso)
DZ_QUADRIL = 0.55
CILHA = dict(y=-2.35, larg=0.45, dentro=0.06, esp=0.08, nseg=36)   # atras dos cotovelos e da borda da juba (y -2,97 nos lados)
X0, X1, Y0, Y1, PASSO = XC - 3.0, XC + 3.0, -3.6, 3.6, 0.05
OSSOS_FORA = ("Juba", "Tufo", "Cauda", "Pescoco", "Cabeca", "Mandibula", "Lingua", "Labio", "Orelha", "Palpebra")   # sela nao balanca com a juba
SENTADO_LEAO = {   # pose sentada do manequim (relativa ao quadril; frente -Y; x+ = esquerda do manequim) - pes sobre os apoios
    ("IK", "LeftFoot"): (1.40, -0.55, -0.85), ("Polo", "LeftFoot"): (2.2, -1.5, 1.6),
    ("IK", "RightFoot"): (-1.40, -0.55, -0.85), ("Polo", "RightFoot"): (-2.2, -1.5, 1.6),     # pes sobre os apoios (a sela foi feita com estes)
    ("IK", "LeftHand"): (0.30, -1.30, 0.55), ("Polo", "LeftHand"): (2.6, 1.0, 1.0),
    ("IK", "RightHand"): (-0.30, -1.30, 0.55), ("Polo", "RightHand"): (-2.6, 1.0, 1.0),
}

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
    """campo de alturas (z) numa grade regular, lido com interpolacao bilinear"""
    def __init__(self, z): self.z = z
    def __call__(self, x, y):
        fx = (x - X0) / PASSO; fy = (y - Y0) / PASSO; H, W = self.z.shape
        i0 = int(np.clip(math.floor(fy), 0, H - 2)); j0 = int(np.clip(math.floor(fx), 0, W - 2)); u = fx - j0; v = fy - i0; z = self.z
        return float((1 - v) * ((1 - u) * z[i0, j0] + u * z[i0, j0 + 1]) + v * ((1 - u) * z[i0 + 1, j0] + u * z[i0 + 1, j0 + 1]))
def _forma(u, v, ax, ay, yc, n, xc=XC):
    """grade (u, v) em [-1, 1] -> contorno super-elipse; devolve x, y, rho (0 centro, 1 borda)"""
    rho = max(abs(u), abs(v))
    if rho < 1e-9: return xc, yc, 0.0
    a, b = abs(u) / rho, abs(v) / rho; t = (a ** n + b ** n) ** (-1.0 / n)
    return xc + u * t * ax, yc + v * t * ay, rho
def _placa(fundo, topo, nu, nv, forma):
    us = np.linspace(-1, 1, nu); vs = np.linspace(-1, 1, nv); vb, vt = [], []
    for v in vs:
        for u in us:
            x, y, rho = forma(u, v); vb.append(fundo(x, y, rho)); vt.append(topo(x, y, rho))
    n = nu * nv; fs = []
    for j in range(nv - 1):
        for i in range(nu - 1):
            a = j * nu + i; fs.append((a, a + 1, a + nu + 1, a + nu)); fs.append((a + n, a + nu + n, a + nu + 1 + n, a + 1 + n))
    borda = ([i for i in range(nu)] + [j * nu + nu - 1 for j in range(1, nv)] + [(nv - 1) * nu + i for i in range(nu - 2, -1, -1)]
             + [j * nu for j in range(nv - 2, 0, -1)])
    for a, b in zip(borda, borda[1:] + borda[:1]): fs.append((b, a, a + n, b + n))
    return vb + vt, fs
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
def _cabochao(c, nrm, raio, alt, nseg=12, aneis=4):
    """pedra arredondada (calota) sobre o ponto c, voltada para nrm"""
    t1 = nrm.orthogonal().normalized(); t2 = nrm.cross(t1); vs = []; fs = []
    for a in range(aneis + 1):
        f = a / aneis; r = raio * math.cos(f * math.pi / 2); h = alt * math.sin(f * math.pi / 2)
        for s in range(nseg if a < aneis else 1):
            ang = 2 * math.pi * s / nseg; vs.append(c + (t1 * math.cos(ang) + t2 * math.sin(ang)) * r + nrm * h)
    for a in range(aneis - 1):
        for s in range(nseg):
            s2 = (s + 1) % nseg; fs.append((a * nseg + s, a * nseg + s2, (a + 1) * nseg + s2, (a + 1) * nseg + s))
    topo = len(vs) - 1
    for s in range(nseg): fs.append(((aneis - 1) * nseg + s, (aneis - 1) * nseg + (s + 1) % nseg, topo))
    fs.append(tuple(range(nseg - 1, -1, -1)))
    return vs, fs

def criar(arm, lo, colecao=None):
    sc = bpy.context.scene; col = colecao or sc.collection
    acao0 = arm.animation_data.action if arm.animation_data else None
    if arm.animation_data: arm.animation_data.action = None
    for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); ev = lo.evaluated_get(dg); me = ev.to_mesh(); W = lo.matrix_world
    pele_v = [W @ v.co for v in me.vertices]; me.calc_loop_triangles(); tris = [tuple(t.vertices) for t in me.loop_triangles]
    gn = {g.index: g.name for g in lo.vertex_groups}; ossos = [b.name for b in arm.data.bones if b.use_deform]; oi = {n: i for i, n in enumerate(ossos)}
    Wp = np.zeros((len(me.vertices), len(ossos)))
    for v in me.vertices:
        for g in v.groups:
            nm = gn.get(g.group)
            if nm in oi and not nm.startswith(OSSOS_FORA): Wp[v.index, oi[nm]] = g.weight
    juba_v = np.array([any(gn.get(g.group, "").startswith("Juba") and g.weight > 0.5 for g in v.groups) for v in me.vertices])
    ev.to_mesh_clear()
    # pele sem os fios da juba (a manta apoia na pele; a juba fica por cima/na frente)
    tris_p = [t for t in tris if not any(juba_v[i] for i in t)]
    bvh = BVHTree.FromPolygons(pele_v, tris_p); bvh_tudo = BVHTree.FromPolygons(pele_v, tris); kd = KDTree(len(pele_v))
    for i, p in enumerate(pele_v): kd.insert(p, i)
    kd.balance()
    xs = np.arange(X0, X1 + 1e-6, PASSO); ys = np.arange(Y0, Y1 + 1e-6, PASSO); H = np.zeros((len(ys), len(xs)))
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            hit = bvh.ray_cast(V((x, y, 20.0)), V((0, 0, -1))); H[j, i] = hit[0].z if (hit[0] and hit[0].z > 6.0) else 6.0
    # envelope do meio liso (nunca abaixo da pele) e borda caida sobre a pele
    piso = _maxf(H, 2) + 0.095; E = _maxf(H, 6) + 0.06                  # r2: +0,06 de folga (o dorso sobe ao agachar e no galope)
    for _ in range(6): E = np.maximum(_blur(E, 5), piso)
    E = np.maximum(_blur(np.maximum(E, piso), 2, 1), piso)
    B = _maxf(H, 3) + 0.06; B = np.maximum(_blur(B, 2, 1), _maxf(H, 2) + 0.05)              # r2: mais folga na borda
    env, borda_pele = Campo(E), Campo(B)
    m = MANTA
    def forma_m(u, v): return _forma(u, v, m["ax"], m["ay"], m["yc"], m["n"])
    def manta_fundo_z(x, y, rho):
        w = float(_ss(0.50, 0.97, rho)); return env(x, y) * (1 - w) + borda_pele(x, y) * w
    def manta_fundo(x, y, rho): return V((x, y, manta_fundo_z(x, y, rho)))
    def manta_normal(x, y, rho, h=0.06):
        dzx = (manta_fundo_z(x + h, y, rho) - manta_fundo_z(x - h, y, rho)) / (2 * h); dzy = (manta_fundo_z(x, y + h, rho) - manta_fundo_z(x, y - h, rho)) / (2 * h)
        return V((-dzx, -dzy, 1)).normalized()
    def manta_topo(x, y, rho):
        e = m["esp"] * (0.55 + 0.45 * (1 - float(_ss(0.9, 1.0, rho)))); return manta_fundo(x, y, rho) + manta_normal(x, y, rho) * e
    pecas = []                                             # (vs, fs, material, tipo de peso, ancora)
    NOMES_PECA = {}                                        # indice da peca -> nome (o resto e nomeado pelo material)
    vs, fs = _placa(manta_fundo, manta_topo, m["nu"], m["nv"], forma_m); pecas.append((vs, fs, 1, "pele", None))
    cord = []
    for k in range(44):
        c_, s_ = math.cos(2 * math.pi * k / 44), math.sin(2 * math.pi * k / 44); mx_ = max(abs(c_), abs(s_))
        x, y, _ = forma_m(c_ / mx_, s_ / mx_); cord.append(manta_topo(x, y, 1.0) - manta_normal(x, y, 1.0) * 0.015)
    vs, fs = _tubo(cord, 0.045, 4, fechado=True); pecas.append((vs, fs, 2, "pele", None))            # debrum de tendao
    manta_top_z = lambda x, y: manta_topo(x, y, 0.0).z
    b_ = ABA
    def forma_b(u, v): return _forma(u, v, b_["ax"], b_["ay"], b_["yc"], b_["n"])
    def aba_fundo(x, y, rho): return V((x, y, manta_top_z(x, y) + 0.015))
    def aba_topo(x, y, rho): return aba_fundo(x, y, rho) + V((0, 0, b_["esp"]))
    vs, fs = _placa(aba_fundo, aba_topo, b_["nu"], b_["nv"], forma_b); NOMES_PECA[len(pecas)] = "aba"; pecas.append((vs, fs, 0, "pele", None))
    def aba_top_z(x, y):
        dentro_ = (abs(x - XC) / b_["ax"]) ** b_["n"] + (abs(y - b_["yc"]) / b_["ay"]) ** b_["n"] <= 1
        return manta_top_z(x, y) + 0.015 + (b_["esp"] if dentro_ else 0.0)
    # costura de tendao na borda da aba (pontos)
    pontos = []
    for k in range(28):
        c_, s_ = math.cos(2 * math.pi * k / 28), math.sin(2 * math.pi * k / 28); mx_ = max(abs(c_), abs(s_))
        u, v = c_ / mx_ * 0.92, s_ / mx_ * 0.92; x, y, _ = forma_b(u, v); pontos.append(V((x, y, aba_top_z(x, y) + 0.004)))
    for k in range(0, 28, 2):
        vs, fs = _tubo([pontos[k], pontos[k + 1]], 0.022, 3); pecas.append((vs, fs, 2, "pele", None))
    # ---------------------------------------------------------------- assento (Couro das Planicies)
    a = ASSENTO
    def forma_a(u, v): return _forma(u, v, a["ax"], a["ay"], a["yc"], a["n"])
    def uv_a(x, y): return (x - XC) / a["ax"], (y - a["yc"]) / a["ay"]
    def espessura(x, y, rho):
        u, v = uv_a(x, y)
        t = 0.13 + 0.05 * float(_ss(0.0, 0.6, abs(v)))
        t += 0.42 * math.exp(-((v + 0.80) / 0.17) ** 2) * math.exp(-(u / 0.40) ** 2)          # cabeca (frente, -Y)
        t += 0.14 * math.exp(-((v + 0.72) / 0.22) ** 2) * math.exp(-(u / 0.75) ** 2)
        t += 0.40 * float(_ss(0.30, 0.84, v)) * (1 - 0.50 * u * u)                            # patilha (atras)
        t += 0.07 * float(_ss(0.55, 0.95, abs(u))) * (1 - float(_ss(0.3, 0.9, abs(v))))
        e = 1 - float(_ss(0.80, 1.0, rho)) ** 1.5
        return 0.045 + (t - 0.045) * e
    def assento_fundo(x, y, rho): return V((x, y, aba_top_z(x, y) - 0.004))
    def assento_topo(x, y, rho): return assento_fundo(x, y, rho) + V((0, 0, espessura(x, y, rho)))
    vs, fs = _placa(assento_fundo, assento_topo, a["nu"], a["nv"], forma_a); pecas.append((vs, fs, 0, "pele", None))
    z_assento = assento_topo(XC, ASSENTO_Y, 0.0).z; Zq = z_assento + DZ_QUADRIL
    # alca de Chifre Leve na cabeca do assento (mao) + adorno solar: Ambar Solar em guarnicao de ferro com 8 raios
    yh = a["yc"] - 0.80 * a["ay"]; zc = assento_topo(XC, yh, 0.0).z
    arco = [V((XC + 0.30 * math.cos(math.pi * k / 10), yh - 0.10, zc - 0.10 + 0.30 * math.sin(math.pi * k / 10))) for k in range(11)]
    vs, fs = _tubo(arco, 0.07, 6); pecas.append((vs, fs, 3, "rigido", V((XC, yh, zc))))
    pf = V((XC, yh - 0.20, zc - 0.20)); nf = V((0, -1, 0.35)).normalized()          # face da frente da cabeca
    anel = [pf + (nf.orthogonal().normalized() * math.cos(2 * math.pi * k / 16) + nf.cross(nf.orthogonal().normalized()) * math.sin(2 * math.pi * k / 16)) * 0.15 for k in range(16)]
    vs, fs = _tubo(anel, 0.03, 5, fechado=True); pecas.append((vs, fs, 5, "rigido", pf))
    vs, fs = _cabochao(pf, nf, 0.13, 0.08); pecas.append((vs, fs, 4, "rigido", pf))
    t1 = nf.orthogonal().normalized(); t2 = nf.cross(t1)
    for k in range(8):
        d = t1 * math.cos(2 * math.pi * k / 8 + 0.39) + t2 * math.sin(2 * math.pi * k / 8 + 0.39)
        vs, fs = _tubo([pf + d * 0.19, pf + d * 0.30 + nf * 0.01], 0.022, 4); pecas.append((vs, fs, 5, "rigido", pf))
    # ---------------------------------------------------------------- cilha (Couro das Planicies + argolas de ferro com Ambar)
    c = CILHA; cy = c["y"]; zc0 = 8.0; cx0 = XC
    def raio_corte(phi):
        d = V((math.cos(phi), 0, math.sin(phi))); best = 0.0
        for dy in (-c["larg"] / 2, 0.0, c["larg"] / 2):
            o = V((cx0, cy + dy, zc0)) + d * 12.0; hit = bvh.ray_cast(o, -d)
            if hit[0]: best = max(best, (hit[0] - V((cx0, cy + dy, zc0))).length)
        return best
    def borda_lado(s):
        x, y, _ = _forma(s * 1.0, (cy - m["yc"]) / m["ay"], m["ax"], m["ay"], m["yc"], m["n"]); p = manta_fundo(x, y, 1.0)
        return p, math.atan2(p.z - zc0, s * (p.x - cx0))
    pE, aE = borda_lado(1); pD, aD = borda_lado(-1)
    ph = np.linspace(aE - math.radians(1.5), -math.pi - aD + math.radians(1.5), c["nseg"])
    r = np.array([raio_corte(p) for p in ph]); r = np.maximum(r, np.convolve(np.pad(r, 2, mode="edge"), np.ones(5) / 5, "valid"))
    r = np.convolve(np.pad(r, 2, mode="edge"), np.ones(5) / 5, "valid") + c["dentro"]
    cvs = []
    for k, p in enumerate(ph):
        d = V((math.cos(p), 0, math.sin(p)))
        for off in (0.0, c["esp"]):
            for dy in (-c["larg"] / 2, c["larg"] / 2): cvs.append(V((cx0, cy + dy, zc0)) + d * (r[k] + off))
    cfs = []
    for k in range(len(ph) - 1):
        a0 = 4 * k; a1 = 4 * (k + 1)
        cfs += [(a0 + 2, a0 + 3, a1 + 3, a1 + 2), (a0 + 1, a0, a1, a1 + 1), (a0, a0 + 2, a1 + 2, a1), (a0 + 3, a0 + 1, a1 + 1, a1 + 3)]
    cfs += [(0, 1, 3, 2), tuple(4 * (len(ph) - 1) + i for i in (2, 3, 1, 0))]
    NOMES_PECA[len(pecas)] = "cilha"; pecas.append((cvs, cfs, 0, "pele", None))
    for s, ab in ((1, aE), (-1, aD)):
        ang = ab if s > 0 else math.pi - ab
        cen = V((cx0, cy, zc0)) + V((math.cos(ang), 0, math.sin(ang))) * (raio_corte(ang) + 0.24)
        dn = (cen - V((cx0, cy, zc0))).normalized(); t1 = V((0, 1, 0)); t2 = dn.cross(t1).normalized()
        anel = [cen + (t1 * math.cos(2 * math.pi * k / 12) + t2 * math.sin(2 * math.pi * k / 12)) * 0.17 for k in range(12)]
        vs, fs = _tubo(anel, 0.045, 6, fechado=True); pecas.append((vs, fs, 5, "rigido", cen))
        vs, fs = _cabochao(cen - t2 * 0.0 + dn * 0.02, dn, 0.08, 0.05, 10, 3); pecas.append((vs, fs, 4, "rigido", cen))
    # ---------------------------------------------------------------- apoios de pe (dois lados) sob o pe do cavaleiro sentado
    Mq = M.Translation(V((XC, ASSENTO_Y, Zq)))
    pes = {lado: Mq @ (V((0.5 * s, 0, 0)) + V(SENTADO_LEAO[("IK", lado + "Foot")])) for lado, s in (("Left", 1), ("Right", -1))}
    info = {"z_quadril": Zq, "z_assento_centro": z_assento, "quadril": [XC, ASSENTO_Y, Zq], "apoios_pe": {}, "alca": [XC, yh - 0.10, zc + 0.20]}
    TG = math.tan(math.radians(20.0))
    for lado, s in (("Left", 1), ("Right", -1)):
        tz = pes[lado]
        def sola(y, tz=tz): return tz.z - 0.30 / math.cos(math.radians(20.0)) - (tz.y - y) * TG - 0.025
        def forma_p(u, v, tz=tz): return _forma(u, v, 0.48, 0.44, tz.y - 0.05, 4.0, xc=tz.x)
        def p_fundo(x, y, rho, tz=tz): return V((x, y, manta_topo(x, y, 0.9).z - 0.03))
        def p_topo(x, y, rho, tz=tz):
            f = p_fundo(x, y, rho); z = max(sola(y), f.z + 0.06); e = float(_ss(0.35, 1.0, rho)) ** 1.6
            return V((f.x, f.y, f.z + 0.05 + (z - f.z - 0.05) * (1 - e)))
        vs, fs = _placa(p_fundo, p_topo, 10, 10, forma_p); NOMES_PECA[len(pecas)] = "apoio_pe"; pecas.append((vs, fs, 0, "pele", None))
        x0, x1 = XC + s * (ABA["ax"] - 0.12), tz.x - s * 0.40; yt = tz.y - 0.05; tira = []
        for k in range(7):
            x = x0 + (x1 - x0) * k / 6
            for dy in (-0.16, 0.16): tira.append((x, yt + dy))
        tv = [V((x, y, manta_topo(x, y, 0.8).z - 0.01)) for x, y in tira] + [V((x, y, manta_topo(x, y, 0.8).z + 0.035)) for x, y in tira]
        nt_ = len(tira); tf = []
        for k in range(6):
            a0, a1 = 2 * k, 2 * k + 2
            tf += [(a0 + nt_, a1 + nt_, a1 + 1 + nt_, a0 + 1 + nt_), (a0, a0 + 1, a1 + 1, a1), (a0, a1, a1 + nt_, a0 + nt_), (a0 + 1, a0 + 1 + nt_, a1 + 1 + nt_, a1 + 1)]
        tf += [(0, nt_, nt_ + 1, 1), (12, 13, 13 + nt_, 12 + nt_)]
        NOMES_PECA[len(pecas)] = "apoio_pe"; pecas.append((tv, tf, 0, "pele", None))
        ya = tz.y - 0.28; za = sola(ya)
        arco = [V((tz.x + 0.40 * math.cos(math.pi * k / 10), ya, za - 0.03 + 0.44 * math.sin(math.pi * k / 10))) for k in range(11)]
        vs, fs = _tubo(arco, 0.05, 6); pecas.append((vs, fs, 5, "pele", None))
        info["apoios_pe"][lado] = {"tornozelo": [round(c_, 3) for c_ in tz], "altura_bloco": round(sola(tz.y) - p_fundo(tz.x, tz.y, 0).z, 3)}
    # ---------------------------------------------------------------- junta, materiais, UV, pesos
    allv, allf, mats, tipos, vpeca = [], [], [], [], []
    for k, (vs, fs, mt, tp, anc) in enumerate(pecas):
        o = len(allv); allv += [tuple(p) for p in vs]; allf += [tuple(i + o for i in f) for f in fs]; mats += [mt] * len(fs); tipos.append((o, len(vs), tp, anc))
        vpeca += [NOMES_PECA.get(k, NOMES_PECA_MAT[mt])] * len(vs)
    me = bpy.data.meshes.new(NOME); me.from_pydata(allv, [], allf); me.update()
    for p, mt in zip(me.polygons, mats): p.material_index = mt
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(NOME, me); col.objects.link(ob)
    for p in me.polygons: p.use_smooth = True
    PL = sorted(set(vpeca)); at = me.attributes.new("peca", "INT", "POINT"); at.data.foreach_set("value", [PL.index(x) for x in vpeca]); ob["pecas"] = PL
    for nm, cor, rug, met in (("M_Sela_CouroPlanicies", (0.20, 0.105, 0.05), 0.55, 0.0), ("M_Sela_PeleAntilope", (0.50, 0.30, 0.11), 0.9, 0.0),
                              ("M_Sela_Tendao", (0.46, 0.37, 0.24), 0.75, 0.0), ("M_Sela_ChifreLeve", (0.74, 0.64, 0.47), 0.38, 0.0),
                              ("M_Sela_AmbarSolar", (0.86, 0.42, 0.05), 0.15, 0.0), ("M_Sela_Ferro", (0.26, 0.25, 0.24), 0.48, 1.0)):
        me.materials.append(bpy.data.materials.get(nm) or _material(nm, cor, rug, met))
    bpy.context.view_layer.objects.active = ob
    for o_ in bpy.context.selected_objects: o_.select_set(False)
    ob.select_set(True); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.01); bpy.ops.object.mode_set(mode="OBJECT")
    grupos = {n: ob.vertex_groups.new(name=n) for n in ossos if not n.startswith(OSSOS_FORA)}
    def peso_em(p, raio=0.45):                                   # r2: raio menor (0,7 suavizava demais e a pele passava a sela)
        loc = bvh.find_nearest(p)[0] or p; acc = np.zeros(len(ossos)); tot = 0.0
        for (_, i, d) in kd.find_range(loc, raio):
            g = math.exp(-(d / (raio * 0.5)) ** 2); acc += Wp[i] * g; tot += g
        if tot == 0 or acc.sum() == 0: acc = np.zeros(len(ossos)); acc[oi["Coluna1"]] = 1.0; tot = 1.0
        acc /= max(acc.sum(), 1e-9); idx = np.argsort(acc)[::-1][:4]; w = acc[idx]; w = w / w.sum()
        return [(ossos[k], float(x)) for k, x in zip(idx, w) if x > 1e-3]
    def raio_de(vi):
        """r2: centro e cilha com media larga (o dorso tem saliencias que a manta cobre por cima); borda da manta com media
        curta (segue a pele que dobra no lombo e nos ombros)"""
        if vpeca[vi] in ("cilha",): return 0.7
        x, y, _ = allv[vi]; rho = ((abs(x - XC) / m["ax"]) ** m["n"] + (abs(y - m["yc"]) / m["ay"]) ** m["n"]) ** (1 / m["n"])
        return 0.7 - 0.25 * float(_ss(0.62, 0.95, rho))
    for o, n, tp, anc in tipos:
        fixo = peso_em(anc) if tp == "rigido" else None
        for vi in range(o, o + n):
            for nm, w in (fixo or peso_em(V(allv[vi]), raio_de(vi))):
                if nm in grupos: grupos[nm].add([vi], w, "REPLACE")
    ob.parent = arm; ob.matrix_parent_inverse = arm.matrix_world.inverted()
    md = ob.modifiers.new("Armature", "ARMATURE"); md.object = arm
    ob["etapa"] = "S1 sela felina (proposta)"; ob["z_quadril"] = Zq; ob["quadril"] = info["quadril"]
    if arm.animation_data: arm.animation_data.action = acao0
    info["tris"] = sum(len(p.vertices) - 2 for p in me.polygons); info["vertices"] = len(me.vertices)
    info["materiais"] = [mt.name for mt in me.materials]
    return ob, Zq, info

def _material(nome, cor, rug, met):
    mt = bpy.data.materials.new(nome); mt.use_nodes = True; nt = mt.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rug; b.inputs["Metallic"].default_value = met
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    ramp.color_ramp.elements[0].color = tuple(c * 0.72 for c in cor) + (1,); ramp.color_ramp.elements[1].color = tuple(min(1, c * 1.25) for c in cor) + (1,)
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump"); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    if nome == "M_Sela_PeleAntilope":                  # pelo curto: ruido fino alongado
        nz.inputs["Scale"].default_value = 40.0; nz.inputs["Detail"].default_value = 8.0; bump.inputs["Strength"].default_value = 0.35
        nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    elif nome == "M_Sela_AmbarSolar":                  # resina: lisa, um pouco translucida (sem emissao)
        b.inputs["Transmission Weight"].default_value = 0.35; b.inputs["IOR"].default_value = 1.54; bump.inputs["Strength"].default_value = 0.02
        nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    elif nome == "M_Sela_Tendao":                      # cordao torcido
        w_ = nt.nodes.new("ShaderNodeTexWave"); w_.inputs["Scale"].default_value = 30; nt.links.new(tc.outputs["Object"], w_.inputs["Vector"])
        bump.inputs["Strength"].default_value = 0.25; nt.links.new(w_.outputs["Fac"], bump.inputs["Height"])
    else:
        bump.inputs["Strength"].default_value = 0.15; nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    return mt

if __name__ == "__main__":
    A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    arm = bpy.data.objects["Leao_Solar_Rig"]; lo = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]
    ob, Zq, info = criar(arm, lo)
    print("SELA", json.dumps(info))
    if len(A) > 1: json.dump(info, open(A[1], "w"), indent=1)
    if A: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A[0]))
    print("SELA_OK")
