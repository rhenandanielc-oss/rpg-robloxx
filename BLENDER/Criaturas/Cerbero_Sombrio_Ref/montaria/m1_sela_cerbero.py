"""Montaria M1 (27/11/2026): SELA REFORCADA do Cerbero Sombrio (proposta para aprovacao).
Oficial (ficha): montavel desde o Adulto com "sela reforcada atras dos tres pescocos"; decisao do usuario 17/11: a sela vai POR
CIMA da armadura do dorso. Decisoes 27/11: couro escuro grosso, bordas de ferro enegrecido, cintas largas, costuras em vermelho
sombrio; cavaleiro sentado com as maos numa alca na frente; o Cerbero deita para subir/descer (alca lateral de subida).

Metodo = o da sela reforcada do Urso Silvestre (m1_sela_urso.py, aprovada 09/11): campo de alturas do dorso por raios, manta
que veste o dorso, aba, assento moldado, cilha por raios em volta do peito, apoios de pe, pesos copiados da pele (sem cabecas,
pescocos e cauda). Nada do Cerbero e alterado (malha, rig, pesos, escala).
Diferencas: o dorso desce ~2 studs da frente para tras (M0) -> o assento ganha uma cunha que nivela o assento; arcao e
cintas de FERRO enegrecido; placas de ferro rebitadas na borda da manta (lembram a armadura do dorso); costuras vermelhas;
pedra rubra escura (sem brilho) no adorno da frente; alca lateral de subida nos dois lados.
Eixos: frente -Y, Z para cima; centro do corpo em x = XC (-0,57). x+ = lado esquerdo do CAVALEIRO (o rig chama -x de lado E).
Uso: blender -b -t 1 rig/clipes_L3r7/CR_Cerbero_Anim.blend -P montaria/m1_sela_cerbero.py -- <saida.blend> <saida.json>"""
import bpy, bmesh, math, sys, os, json
import numpy as np
from mathutils import Vector as V, Matrix as M
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

NOME = "Cerbero_Sombrio_Sela"
NOMES_PECA_MAT = {0: "assento", 1: "manta", 2: "costura", 3: "couro_cinta", 4: "pedra", 5: "ferro", 6: "placa"}
XC = -0.57
def P_(n, d): return float(os.environ.get("CERB_S_" + n, d))
MANTA = dict(ax=P_("MX", 2.70), ay=P_("MY", 2.35), yc=P_("MYC", -1.30), n=4.0, esp=0.12, nu=24, nv=24)
ABA = dict(ax=1.80, ay=1.80, yc=-1.25, n=3.0, esp=0.07, nu=14, nv=14)
ASSENTO = dict(ax=1.00, ay=1.30, yc=-1.20, n=3.2, nu=18, nv=18)
ASSENTO_Y = P_("AY", -0.95)                           # quadril do cavaleiro
DZ_QUADRIL = 0.55
NIVELAR = P_("NIV", 0.75)                             # fracao da descida do dorso compensada pela cunha do assento
CILHA = dict(y=P_("CY", -2.20), larg=0.75, dentro=0.07, esp=0.12, nseg=44)
X0, X1, Y0, Y1, PASSO = XC - 4.3, XC + 4.3, -4.6, 2.2, 0.06
Z_PISO = 9.0
Z_RAIO = 26.0
OSSOS_FORA = ("Cauda", "Pescoco", "Cabeca", "Mandibula", "Lingua", "Olho", "Palpebra", "Aura")
SENTADO_CERB = {   # pose sentada do manequim (relativa ao quadril; frente -Y; x+ = esquerda do manequim) - pes sobre os apoios
    ("IK", "LeftFoot"): (1.30, -0.45, -0.95), ("Polo", "LeftFoot"): (2.4, -1.5, 1.4),
    ("IK", "RightFoot"): (-1.30, -0.45, -0.95), ("Polo", "RightFoot"): (-2.4, -1.5, 1.4),
    ("IK", "LeftHand"): (0.30, -1.25, 0.60), ("Polo", "LeftHand"): (2.6, 1.0, 1.0),
    ("IK", "RightHand"): (-0.30, -1.25, 0.60), ("Polo", "RightHand"): (-2.6, 1.0, 1.0),
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
    """raio pode ser numero ou lista (um por ponto)"""
    vs, fs = [], []; n = len(pts); rr = raio if isinstance(raio, (list, tuple)) else [raio] * n
    for k, p in enumerate(pts):
        a = pts[(k + 1) % n] - pts[k - 1] if fechado else (pts[min(k + 1, n - 1)] - pts[max(k - 1, 0)])
        t = a.normalized(); b = t.orthogonal().normalized(); c = t.cross(b)
        for s in range(lados):
            ang = 2 * math.pi * s / lados; vs.append(p + (b * math.cos(ang) + c * math.sin(ang)) * rr[k])
    for k in range(n if fechado else n - 1):
        k2 = (k + 1) % n
        for s in range(lados):
            s2 = (s + 1) % lados; fs.append((k * lados + s, k * lados + s2, k2 * lados + s2, k2 * lados + s))
    if not fechado:
        fs.append(tuple(range(lados - 1, -1, -1))); fs.append(tuple((n - 1) * lados + s for s in range(lados)))
    return vs, fs
def _cabochao(c, nrm, raio, alt, nseg=12, aneis=4, alongar=1.0):
    """pedra arredondada (calota) sobre o ponto c, voltada para nrm; alongar > 1 = gota (eixo t2)"""
    t1 = nrm.orthogonal().normalized(); t2 = nrm.cross(t1); vs = []; fs = []
    for a in range(aneis + 1):
        f = a / aneis; r = raio * math.cos(f * math.pi / 2); h = alt * math.sin(f * math.pi / 2)
        for s in range(nseg if a < aneis else 1):
            ang = 2 * math.pi * s / nseg; vs.append(c + (t1 * math.cos(ang) + t2 * math.sin(ang) * alongar) * r + nrm * h)
    for a in range(aneis - 1):
        for s in range(nseg):
            s2 = (s + 1) % nseg; fs.append((a * nseg + s, a * nseg + s2, (a + 1) * nseg + s2, (a + 1) * nseg + s))
    topo = len(vs) - 1
    for s in range(nseg): fs.append(((aneis - 1) * nseg + s, (aneis - 1) * nseg + (s + 1) % nseg, topo))
    fs.append(tuple(range(nseg - 1, -1, -1)))
    return vs, fs
def _folha(base, eixo, nrm, comp, larg, esp, superficie=None, nv=7, nu=5, curva=0.0):
    """folha recortada (ponta fina, base arredondada) deitada sobre uma superficie: base = ponto do peciolo, eixo = direcao
    da ponta (no plano), nrm = normal. superficie(p) -> ponto apoiado (opcional). Placa com espessura e nervura central."""
    lado = nrm.cross(eixo).normalized(); vb, vt = [], []
    for j in range(nv):
        t = j / (nv - 1); w = larg * math.sin(math.pi * min(1.0, t * 1.08)) ** 0.75 * (1 - 0.25 * t)
        for i in range(nu):
            s = -1 + 2 * i / (nu - 1); p = base + eixo * (t * comp) + lado * (s * w) + nrm * (curva * (s * s) * w)
            if superficie: p = superficie(p)
            ner = 0.35 * esp * (1 - abs(s)) * (1 - t)                   # nervura central um pouco mais alta
            vb.append(p); vt.append(p + nrm * (esp + ner))
    n = nu * nv; fs = []
    for j in range(nv - 1):
        for i in range(nu - 1):
            a = j * nu + i; fs.append((a, a + nu, a + nu + 1, a + 1)); fs.append((a + n, a + 1 + n, a + nu + 1 + n, a + nu + n))
    borda = ([i for i in range(nu)] + [j * nu + nu - 1 for j in range(1, nv)] + [(nv - 1) * nu + i for i in range(nu - 2, -1, -1)]
             + [j * nu for j in range(nv - 2, 0, -1)])
    for a, b in zip(borda, borda[1:] + borda[:1]): fs.append((a, b, b + n, a + n))
    return vb + vt, fs

def _placa_local(c, e1, comp, larg, superficie, esp, nu=6, nv=6, n=3.0):
    """placa retangular arredondada (super-elipse) centrada em c (x, y), eixo e1 (no plano), apoiada em superficie(x, y) -> z"""
    e1 = V((e1.x, e1.y, 0)).normalized(); e2 = V((-e1.y, e1.x, 0))
    def forma(u, v):
        rho = max(abs(u), abs(v))
        if rho < 1e-9: return c.x, c.y, 0.0
        a, b = abs(u) / rho, abs(v) / rho; t = (a ** n + b ** n) ** (-1.0 / n)
        p = V((c.x, c.y, 0)) + e1 * (u * t * comp / 2) + e2 * (v * t * larg / 2); return p.x, p.y, rho
    def fundo(x, y, rho): return V((x, y, superficie(x, y)))
    def topo(x, y, rho): return V((x, y, superficie(x, y) + esp * (1 - 0.35 * float(_ss(0.85, 1.0, rho)))))
    return _placa(fundo, topo, nu, nv, forma)

def criar(arm, malhas, colecao=None):
    sc = bpy.context.scene; col = colecao or sc.collection
    acao0 = arm.animation_data.action if arm.animation_data else None
    if arm.animation_data: arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); pele_v, tris, Wl = [], [], []
    ossos = [b.name for b in arm.data.bones if b.use_deform]; oi = {n: i for i, n in enumerate(ossos)}
    for lo in malhas:
        ev = lo.evaluated_get(dg); me = ev.to_mesh(); W = lo.matrix_world; k = len(pele_v)
        pele_v += [W @ v.co for v in me.vertices]; me.calc_loop_triangles(); tris += [tuple(i + k for i in t.vertices) for t in me.loop_triangles]
        gn = {g.index: g.name for g in lo.vertex_groups}; Wp_ = np.zeros((len(me.vertices), len(ossos)))
        for v in lo.data.vertices:
            for g in v.groups:
                nm = gn.get(g.group)
                if nm in oi and not nm.startswith(OSSOS_FORA): Wp_[v.index, oi[nm]] = g.weight
        Wl.append(Wp_); ev.to_mesh_clear()
    Wp = np.vstack(Wl)
    bvh = BVHTree.FromPolygons(pele_v, tris); kd = KDTree(len(pele_v))
    for i, p in enumerate(pele_v): kd.insert(p, i)
    kd.balance()
    xs = np.arange(X0, X1 + 1e-6, PASSO); ys = np.arange(Y0, Y1 + 1e-6, PASSO); H = np.zeros((len(ys), len(xs)))
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            hit = bvh.ray_cast(V((x, y, Z_RAIO)), V((0, 0, -1))); H[j, i] = hit[0].z if (hit[0] and hit[0].z > Z_PISO) else Z_PISO
    # envelope do meio liso (nunca abaixo da pele: as placas da armadura ficam por baixo) e borda caida sobre a pele
    piso = _maxf(H, 2) + 0.12; E = _maxf(H, 7) + 0.09
    for _ in range(7): E = np.maximum(_blur(E, 6), piso)
    E = np.maximum(_blur(np.maximum(E, piso), 2, 1), piso)
    B = _maxf(H, 3) + 0.09; B = np.maximum(_blur(B, 2, 1), _maxf(H, 2) + 0.08)
    env, borda_pele = Campo(E), Campo(B)
    m = MANTA
    def forma_m(u, v): return _forma(u, v, m["ax"], m["ay"], m["yc"], m["n"])
    def manta_fundo_z(x, y, rho):
        w = float(_ss(0.45, 0.97, rho)); return env(x, y) * (1 - w) + borda_pele(x, y) * w
    def manta_fundo(x, y, rho): return V((x, y, manta_fundo_z(x, y, rho)))
    def manta_normal(x, y, rho, h=0.08):
        dzx = (manta_fundo_z(x + h, y, rho) - manta_fundo_z(x - h, y, rho)) / (2 * h); dzy = (manta_fundo_z(x, y + h, rho) - manta_fundo_z(x, y - h, rho)) / (2 * h)
        return V((-dzx, -dzy, 1)).normalized()
    def manta_topo(x, y, rho):
        e = m["esp"] * (0.55 + 0.45 * (1 - float(_ss(0.9, 1.0, rho)))); return manta_fundo(x, y, rho) + manta_normal(x, y, rho) * e
    def rho_m(x, y): return ((abs(x - XC) / m["ax"]) ** m["n"] + (abs(y - m["yc"]) / m["ay"]) ** m["n"]) ** (1 / m["n"])
    def manta_z(x, y): return manta_topo(x, y, min(1.0, rho_m(x, y))).z
    pecas = []; NOMES_PECA = {}                             # (vs, fs, material, tipo de peso, ancora)
    vs, fs = _placa(manta_fundo, manta_topo, m["nu"], m["nv"], forma_m); NOMES_PECA[len(pecas)] = "manta"; pecas.append((vs, fs, 1, "pele", None))
    cord = []
    for k in range(64):
        c_, s_ = math.cos(2 * math.pi * k / 64), math.sin(2 * math.pi * k / 64); mx_ = max(abs(c_), abs(s_))
        x, y, _ = forma_m(c_ / mx_, s_ / mx_); cord.append(manta_topo(x, y, 1.0) - manta_normal(x, y, 1.0) * 0.02)
    vs, fs = _tubo(cord, 0.06, 5, fechado=True); NOMES_PECA[len(pecas)] = "debrum"; pecas.append((vs, fs, 2, "pele", None))   # debrum vermelho
    # placas de ferro enegrecido rebitadas na borda da manta (lembram a armadura do dorso); a frente (juba) fica livre
    NP = int(P_("NP", 22))
    for k in range(NP):
        ang = 2 * math.pi * (k + 0.5) / NP; c_, s_ = math.cos(ang), math.sin(ang); mx_ = max(abs(c_), abs(s_))
        if s_ < -0.6 and abs(c_) < 0.55: continue
        x, y, _ = forma_m(c_ / mx_ * 0.86, s_ / mx_ * 0.86); xo, yo, _ = forma_m(c_ / mx_ * 1.0, s_ / mx_ * 1.0)
        e1 = V((xo - x, yo - y, 0)); cen = V((x + (xo - x) * 0.45, y + (yo - y) * 0.45, 0))
        vs, fs = _placa_local(cen, e1, 0.60, 0.62, lambda xx, yy: manta_z(xx, yy) + 0.012, 0.08)
        NOMES_PECA[len(pecas)] = "placa"; pecas.append((vs, fs, 6, "pele", None))
        e1n = e1.normalized(); e2 = V((-e1n.y, e1n.x, 0))
        for dd in (-0.15, 0.15):
            pr = cen + e2 * dd - e1n * 0.12; pz = V((pr.x, pr.y, manta_z(pr.x, pr.y) + 0.06))
            vs, fs = _cabochao(pz, manta_normal(pr.x, pr.y, 0.9), 0.05, 0.04, 8, 2); pecas.append((vs, fs, 5, "pele", None))
    manta_top_z = lambda x, y: manta_topo(x, y, 0.0).z
    b_ = ABA
    def forma_b(u, v): return _forma(u, v, b_["ax"], b_["ay"], b_["yc"], b_["n"])
    def aba_fundo(x, y, rho): return V((x, y, manta_top_z(x, y) + 0.02))
    def aba_topo(x, y, rho): return aba_fundo(x, y, rho) + V((0, 0, b_["esp"]))
    vs, fs = _placa(aba_fundo, aba_topo, b_["nu"], b_["nv"], forma_b); NOMES_PECA[len(pecas)] = "aba"; pecas.append((vs, fs, 0, "pele", None))
    def aba_top_z(x, y):
        dentro_ = (abs(x - XC) / b_["ax"]) ** b_["n"] + (abs(y - b_["yc"]) / b_["ay"]) ** b_["n"] <= 1
        return manta_top_z(x, y) + 0.02 + (b_["esp"] if dentro_ else 0.0)
    pontos = []
    for k in range(40):
        c_, s_ = math.cos(2 * math.pi * k / 40), math.sin(2 * math.pi * k / 40); mx_ = max(abs(c_), abs(s_))
        u, v = c_ / mx_ * 0.92, s_ / mx_ * 0.92; x, y, _ = forma_b(u, v); pontos.append(V((x, y, aba_top_z(x, y) + 0.005)))
    for k in range(0, 40, 2):
        vs, fs = _tubo([pontos[k], pontos[k + 1]], 0.028, 3); NOMES_PECA[len(pecas)] = "costura"; pecas.append((vs, fs, 2, "pele", None))
    # ---------------------------------------------------------------- assento de couro grosso, com cunha que nivela o dorso inclinado
    a = ASSENTO
    def forma_a(u, v): return _forma(u, v, a["ax"], a["ay"], a["yc"], a["n"])
    def uv_a(x, y): return (x - XC) / a["ax"], (y - a["yc"]) / a["ay"]
    z_frente = aba_top_z(XC, a["yc"] - 0.85 * a["ay"])
    def cunha(y): return NIVELAR * max(0.0, z_frente - aba_top_z(XC, y))
    def espessura(x, y, rho):
        u, v = uv_a(x, y)
        t = 0.16 + 0.05 * float(_ss(0.0, 0.6, abs(v)))
        t += 0.38 * math.exp(-((v + 0.80) / 0.17) ** 2) * math.exp(-(u / 0.45) ** 2)          # cabeca alta (frente, -Y, colada a juba)
        t += 0.14 * math.exp(-((v + 0.72) / 0.22) ** 2) * math.exp(-(u / 0.75) ** 2)
        t += 0.26 * float(_ss(0.30, 0.84, v)) * (1 - 0.50 * u * u)                            # patilha (atras)
        t += 0.08 * float(_ss(0.55, 0.95, abs(u))) * (1 - float(_ss(0.3, 0.9, abs(v))))
        e = 1 - float(_ss(0.82, 1.0, rho)) ** 1.5
        e2 = 1 - float(_ss(0.93, 1.0, rho))                    # r2: a cunha so cai na beirada (bloco firme, arcos sem gancho)
        return 0.06 + (t - 0.06) * e + cunha(y) * e2
    def assento_fundo(x, y, rho): return V((x, y, aba_top_z(x, y) - 0.005))
    def assento_topo(x, y, rho): return assento_fundo(x, y, rho) + V((0, 0, espessura(x, y, rho)))
    vs, fs = _placa(assento_fundo, assento_topo, a["nu"], a["nv"], forma_a); NOMES_PECA[len(pecas)] = "assento"; pecas.append((vs, fs, 0, "pele", None))
    z_assento = assento_topo(XC, ASSENTO_Y, 0.0).z; Zq = z_assento + DZ_QUADRIL
    def topo_a(x, y):
        u, v = uv_a(x, y); r = max(0.0, min(1.0, ((abs(u)) ** a["n"] + (abs(v)) ** a["n"]) ** (1 / a["n"]))); return assento_topo(x, y, r)
    cs = []                                                               # costura vermelha em volta do assento
    for k in range(48):
        c_, s_ = math.cos(2 * math.pi * k / 48), math.sin(2 * math.pi * k / 48); mx_ = max(abs(c_), abs(s_))
        x, y, _ = forma_a(c_ / mx_ * 0.93, s_ / mx_ * 0.93); cs.append(topo_a(x, y) + V((0, 0, 0.006)))
    for k in range(0, 48, 2):
        vs, fs = _tubo([cs[k], cs[k + 1]], 0.022, 3); NOMES_PECA[len(pecas)] = "costura"; pecas.append((vs, fs, 2, "pele", None))
    # ---------------------------------------------------------------- arcao reforcado: arcos de ferro enegrecido com rebites
    def arco(vrel, alt, raio, lados_x):
        y = a["yc"] + vrel * a["ay"]; pts, rr = [], []
        for k in range(15):
            u = -lados_x + 2 * lados_x * k / 14; x = XC + u * a["ax"]
            p = topo_a(x, y); h = alt * (1 - (u / max(lados_x, 1e-6)) ** 2) ** 0.5
            pts.append(p + V((0, 0, h - raio * 0.4))); rr.append(raio)
        return pts, rr
    for vrel, alt, raio, lx, nome in ((-0.80, 0.18, 0.13, 0.80, "cabeca"), (0.86, 0.12, 0.12, 0.84, "patilha")):
        pts, rr = arco(vrel, alt, raio, lx)
        vs, fs = _tubo(pts, rr, 8); NOMES_PECA[len(pecas)] = "arcao_" + nome; pecas.append((vs, fs, 5, "pele", None))
        for k in (1, 4, 7, 10, 13):                                       # rebites ao longo do arco
            d = (pts[k + 1] - pts[k - 1]).normalized(); up = V((0, 0, 1)); nrm = (up - d * d.dot(up)).normalized()
            vs, fs = _cabochao(pts[k] + nrm * (rr[k] * 0.9), nrm, 0.05, 0.04, 8, 2); pecas.append((vs, fs, 5, "pele", None))
    # alca da frente: aro de ferro enrolado em tira de couro (mao do cavaleiro)
    yh = a["yc"] - 0.80 * a["ay"]; zc = topo_a(XC, yh).z
    alca = []; ra_ = []
    for k in range(13):
        t = k / 12; ang = math.pi * t
        alca.append(V((XC + 0.34 * math.cos(ang), yh - 0.10 - 0.05 * math.sin(ang), zc - 0.06 + 0.40 * math.sin(ang)))); ra_.append(0.06)
    vs, fs = _tubo(alca, ra_, 8); NOMES_PECA[len(pecas)] = "alca"; pecas.append((vs, fs, 5, "rigido", V((XC, yh, zc))))
    espiral = []
    for k in range(70):
        t = 0.22 + 0.56 * k / 69; i = t * 12; i0 = int(i); f = i - i0; p = alca[i0].lerp(alca[min(i0 + 1, 12)], f)
        d = (alca[min(i0 + 1, 12)] - alca[i0]).normalized(); b1 = d.cross(V((0, 1, 0))).normalized(); b2 = d.cross(b1)
        ang = k * 1.1; espiral.append(p + (b1 * math.cos(ang) + b2 * math.sin(ang)) * 0.07)
    vs, fs = _tubo(espiral, 0.022, 4); NOMES_PECA[len(pecas)] = "alca"; pecas.append((vs, fs, 3, "rigido", V((XC, yh, zc))))
    # adorno: placa de ferro em ponta (como as placas da armadura) na frente da cabeca, com pedra rubra escura em aro de ferro
    pf = V((XC, yh - 0.30, zc - 0.18)); nf = V((0, -1, 0.30)).normalized(); t1 = V((1, 0, 0)); t2 = nf.cross(t1).normalized()
    if t2.z < 0: t2 = -t2
    vs, fs = _folha(pf - t2 * 0.38, t2, nf, 0.85, 0.32, 0.07, None, curva=0.06); NOMES_PECA[len(pecas)] = "adorno"; pecas.append((vs, fs, 5, "rigido", pf))
    pr = pf + nf * 0.07
    anel = [pr + (t1 * math.cos(2 * math.pi * k / 16) + t2 * math.sin(2 * math.pi * k / 16) * 1.25) * 0.12 for k in range(16)]
    vs, fs = _tubo(anel, 0.026, 5, fechado=True); pecas.append((vs, fs, 5, "rigido", pf))
    vs, fs = _cabochao(pr, nf, 0.11, 0.08, alongar=1.25); NOMES_PECA[len(pecas)] = "pedra"; pecas.append((vs, fs, 4, "rigido", pf))
    # ---------------------------------------------------------------- cilha larga de couro + argolas de ferro
    c = CILHA; cy = c["y"]; zc0 = P_("CZ", 10.5); cx0 = XC
    def raio_corte(phi):
        d = V((math.cos(phi), 0, math.sin(phi))); best = 0.0
        for dy in (-c["larg"] / 2, 0.0, c["larg"] / 2):
            o = V((cx0, cy + dy, zc0)) + d * 14.0; hit = bvh.ray_cast(o, -d)
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
    NOMES_PECA[len(pecas)] = "cilha"; pecas.append((cvs, cfs, 3, "pele", None))
    for s, ab in ((1, aE), (-1, aD)):
        ang = ab if s > 0 else math.pi - ab
        ang2 = ang - s * math.radians(18)                                 # argola um pouco abaixo da borda da manta
        cen = V((cx0, cy, zc0)) + V((math.cos(ang2), 0, math.sin(ang2))) * (raio_corte(ang2) + c["dentro"] + c["esp"] + 0.06)
        dn = (cen - V((cx0, cy, zc0))).normalized(); t1_ = V((0, 1, 0)); t2_ = dn.cross(t1_).normalized()
        anel = [cen + (t1_ * math.cos(2 * math.pi * k / 14) + t2_ * math.sin(2 * math.pi * k / 14)) * 0.30 for k in range(14)]
        vs, fs = _tubo(anel, 0.07, 6, fechado=True); NOMES_PECA[len(pecas)] = "argola"; pecas.append((vs, fs, 5, "rigido", cen))
    # ---------------------------------------------------------------- alca lateral de subida (dois lados): tira de couro + aro de ferro
    info = {"alca_subida": {}}
    for lado, s in (("Left", 1), ("Right", -1)):
        vb = (P_("ASY", -2.55) - m["yc"]) / m["ay"]; xb, yb, _ = forma_m(s * 0.97, vb); base = manta_topo(xb, yb, 0.97)
        nb = manta_normal(xb, yb, 0.97); fora = V((s, 0, 0)); desce = (fora * 0.25 + V((0, 0, -1))).normalized()
        topo_t = base + nb * 0.03; ponta = topo_t + desce * 0.55
        vs, fs = _tubo([topo_t.lerp(ponta, t) for t in np.linspace(0, 1, 6)], 0.09, 4); NOMES_PECA[len(pecas)] = "alca_subida"; pecas.append((vs, fs, 3, "rigido", base))
        cen = ponta + desce * 0.28; t1_ = V((0, 1, 0)); t2_ = desce
        anel = [cen + (t1_ * math.cos(2 * math.pi * k / 16) * 0.30 + t2_ * math.sin(2 * math.pi * k / 16) * 0.30) for k in range(16)]
        vs, fs = _tubo(anel, 0.055, 6, fechado=True); NOMES_PECA[len(pecas)] = "alca_subida"; pecas.append((vs, fs, 5, "rigido", base))
        info["alca_subida"][lado] = [round(c_, 3) for c_ in cen]
    # ---------------------------------------------------------------- apoios de pe (dois lados) sob o pe do cavaleiro sentado
    PERNA = 1.62; yp = ASSENTO_Y - 0.45; pes = {}
    for lado, s in (("Left", 1), ("Right", -1)):
        hip = V((XC + 0.5 * s, ASSENTO_Y, Zq)); best = None
        for k in range(200):
            x = XC + s * (0.6 + 0.015 * k); r_ = rho_m(x, yp)
            if r_ > 1.0: break
            tz_ = V((x, yp, manta_topo(x, yp, r_).z + 0.32))
            if best is None or abs((tz_ - hip).length - PERNA) < abs((best - hip).length - PERNA): best = tz_
        pes[lado] = best; rel = best - V((XC, ASSENTO_Y, Zq)) - V((0.5 * s, 0, 0))
        SENTADO_CERB[("IK", lado + "Foot")] = (round(rel.x, 3), round(rel.y, 3), round(rel.z, 3))
    info.update({"z_quadril": Zq, "z_assento_centro": z_assento, "quadril": [XC, ASSENTO_Y, Zq], "apoios_pe": {}, "alca": [XC, yh - 0.12, zc + 0.30],
                 "cunha_max": round(cunha(a["yc"] + 0.85 * a["ay"]), 3)})
    for lado, s in (("Left", 1), ("Right", -1)):
        tz = pes[lado]
        def forma_p(u, v, tz=tz): return _forma(u, v, 0.42, 0.55, tz.y - 0.10, 4.0, xc=tz.x)
        def p_fundo(x, y, rho, tz=tz): return V((x, y, manta_topo(x, y, min(1.0, rho_m(x, y))).z - 0.03))
        def p_topo(x, y, rho, tz=tz):
            f = p_fundo(x, y, rho); return V((f.x, f.y, f.z + 0.09))
        vs, fs = _placa(p_fundo, p_topo, 10, 10, forma_p); NOMES_PECA[len(pecas)] = "apoio_pe"; pecas.append((vs, fs, 0, "pele", None))
        x0, x1 = XC + s * (ABA["ax"] - 0.12), tz.x - s * 0.42; yt = tz.y - 0.05; tira = []
        if abs(x1 - XC) > abs(x0 - XC):
            for k in range(7):
                x = x0 + (x1 - x0) * k / 6
                for dy in (-0.18, 0.18): tira.append((x, yt + dy))
            tv = [V((x, y, manta_z(x, y) - 0.01)) for x, y in tira] + [V((x, y, manta_z(x, y) + 0.045)) for x, y in tira]
            nt_ = len(tira); tf = []
            for k in range(6):
                a0, a1 = 2 * k, 2 * k + 2
                tf += [(a0 + nt_, a1 + nt_, a1 + 1 + nt_, a0 + 1 + nt_), (a0, a0 + 1, a1 + 1, a1), (a0, a1, a1 + nt_, a0 + nt_), (a0 + 1, a0 + 1 + nt_, a1 + 1 + nt_, a1 + 1)]
            tf += [(0, nt_, nt_ + 1, 1), (12, 13, 13 + nt_, 12 + nt_)]
            NOMES_PECA[len(pecas)] = "apoio_pe"; pecas.append((tv, tf, 3, "pele", None))
        ya = tz.y - 0.42; za = manta_z(tz.x, ya) + 0.03
        arco_ = [V((tz.x + 0.42 * math.cos(math.pi * k / 10), ya, za + 0.42 * math.sin(math.pi * k / 10))) for k in range(11)]
        vs, fs = _tubo(arco_, 0.055, 6); NOMES_PECA[len(pecas)] = "apoio_pe"; pecas.append((vs, fs, 5, "pele", None))
        info["apoios_pe"][lado] = {"tornozelo": [round(c_, 3) for c_ in tz], "perna": round((tz - V((XC + 0.5 * s, ASSENTO_Y, Zq))).length, 3),
                                   "pele_sob_pe": round(Campo(H)(tz.x, tz.y), 3)}
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
    for nm, cor, rug, met in (("M_SelaCerb_CouroEscuro", (0.085, 0.045, 0.032), 0.55, 0.0), ("M_SelaCerb_CouroManta", (0.055, 0.040, 0.038), 0.8, 0.0),
                              ("M_SelaCerb_CosturaRubra", (0.42, 0.045, 0.035), 0.6, 0.0), ("M_SelaCerb_CouroCinta", (0.11, 0.065, 0.045), 0.65, 0.0),
                              ("M_SelaCerb_PedraRubra", (0.28, 0.02, 0.02), 0.15, 0.0), ("M_SelaCerb_FerroEnegrecido", (0.14, 0.13, 0.13), 0.45, 1.0),
                              ("M_SelaCerb_PlacaFerro", (0.17, 0.16, 0.16), 0.42, 1.0)):
        me.materials.append(bpy.data.materials.get(nm) or _material(nm, cor, rug, met))
    bpy.context.view_layer.objects.active = ob
    for o_ in bpy.context.selected_objects: o_.select_set(False)
    ob.select_set(True); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.01); bpy.ops.object.mode_set(mode="OBJECT")
    grupos = {n: ob.vertex_groups.new(name=n) for n in ossos if not n.startswith(OSSOS_FORA)}
    def peso_em(p, raio=1.0):
        loc = bvh.find_nearest(p)[0] or p; acc = np.zeros(len(ossos)); tot = 0.0
        for (_, i, d) in kd.find_range(loc, raio):
            g = math.exp(-(d / (raio * 0.5)) ** 2); acc += Wp[i] * g; tot += g
        if tot == 0 or acc.sum() == 0: acc = np.zeros(len(ossos)); acc[oi["Coluna2"]] = 1.0; tot = 1.0
        acc /= max(acc.sum(), 1e-9); idx = np.argsort(acc)[::-1][:4]; w = acc[idx]; w = w / w.sum()
        return [(ossos[k], float(x)) for k, x in zip(idx, w) if x > 1e-3]
    def raio_de(vi):
        if vpeca[vi] in ("cilha",): return 1.3
        x, y, _ = allv[vi]; rho = rho_m(x, y)
        return 1.4 - 0.5 * float(_ss(0.62, 0.95, rho))
    for o, n, tp, anc in tipos:
        fixo = peso_em(anc, 1.2) if tp == "rigido" else None
        for vi in range(o, o + n):
            for nm, w in (fixo or peso_em(V(allv[vi]), raio_de(vi))):
                if nm in grupos: grupos[nm].add([vi], w, "REPLACE")
    ob.parent = arm; ob.matrix_parent_inverse = arm.matrix_world.inverted()
    md = ob.modifiers.new("Armature", "ARMATURE"); md.object = arm
    ob["etapa"] = "M1 sela reforcada do Cerbero (proposta)"; ob["z_quadril"] = Zq; ob["quadril"] = info["quadril"]
    ob["sentado"] = json.dumps({"%s|%s" % k: v for k, v in SENTADO_CERB.items()})
    if arm.animation_data: arm.animation_data.action = acao0
    info["tris"] = sum(len(p.vertices) - 2 for p in me.polygons); info["vertices"] = len(me.vertices)
    info["materiais"] = [mt.name for mt in me.materials]
    return ob, Zq, info

def _material(nome, cor, rug, met):
    mt = bpy.data.materials.new(nome); mt.use_nodes = True; nt = mt.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rug; b.inputs["Metallic"].default_value = met
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 6.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    ramp.color_ramp.elements[0].color = tuple(c * 0.70 for c in cor) + (1,); ramp.color_ramp.elements[1].color = tuple(min(1, c * 1.30) for c in cor) + (1,)
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump"); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    if "Couro" in nome:                                   # couro grosso: poros e rugas
        nz.inputs["Scale"].default_value = 22.0; nz.inputs["Detail"].default_value = 6.0; bump.inputs["Strength"].default_value = 0.3
        nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    elif nome == "M_SelaCerb_PedraRubra":                 # pedra lisa, um pouco translucida (sem emissao)
        b.inputs["Transmission Weight"].default_value = 0.35; b.inputs["IOR"].default_value = 1.6; bump.inputs["Strength"].default_value = 0.02
        nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    elif nome == "M_SelaCerb_CosturaRubra":               # linha torcida
        w_ = nt.nodes.new("ShaderNodeTexWave"); w_.inputs["Scale"].default_value = 30; nt.links.new(tc.outputs["Object"], w_.inputs["Vector"])
        bump.inputs["Strength"].default_value = 0.25; nt.links.new(w_.outputs["Fac"], bump.inputs["Height"])
    else:                                                 # ferro batido
        nz.inputs["Scale"].default_value = 14.0; bump.inputs["Strength"].default_value = 0.2; nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    return mt

if __name__ == "__main__":
    A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    arm = bpy.data.objects["Cerbero_Rig"]; malhas = [bpy.data.objects[n] for n in ("Cerbero_Corpo", "Cerbero_Cabecas")]
    ob, Zq, info = criar(arm, malhas)
    print("SELA", json.dumps(info))
    if len(A) > 1: json.dump(info, open(A[1], "w"), indent=1)
    if A: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A[0]))
    print("SELA_OK")
