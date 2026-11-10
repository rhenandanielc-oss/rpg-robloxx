"""Montaria M1 (10/11/2026): SELA LEVE do Lobo Ancestral (rig18) - proposta para aprovacao. Pedido do usuario: "a sela de
acordo com o visual de seus ingredientes". Oficial (ficha do lobo): montavel desde o Adulto com SELA LEVE; referencia =
pelagem com musgo e folhas; o lobo tem marcas verdes na cara/peito.

Metodo = o da sela do Urso Silvestre (m1_sela_urso.py, aprovada 09/11), que veio do Leao/Crocodilo: campo de alturas do
dorso por raios, manta que veste o dorso, aba, assento moldado, cilha por raios em volta do peito, pesos copiados da pele
(sem os ossos de pelo Pelo*/Juba*, que balancam ao vento). Nada do lobo e alterado (malha, rig, pesos, escala).
Sela LEVE (diferente da reforcada do urso): manta fina, assento baixo, sem arcao de madeira nem placas; so um galho fino
de pegada na frente; estribos de cordao (o dorso do lobo e estreito: o pe do R15 alcanca um estribo pendurado).

Materiais (DOCS/biomas/floresta-ancestral.md: regionais oficiais Madeira Ancestral e Resina Viva; DOCS/fauna/floresta-
ancestral.md: Couro de Javali, Pele de Cervo, Tendao de Cervo = nomes de trabalho):
 - Pele de Cervo: manta sob a sela (pelo curto, cor de musgo seco);
 - Couro de Javali: assento, aba, cilha; folhas recortadas em couro curtido verde-musgo na borda (as folhas do lobo);
 - Tendao de Cervo: debrum, costuras, cordao dos estribos e enrolado na pegada;
 - Madeira Ancestral: pegada de galho fino na frente e degrau dos estribos;
 - Resina Viva: gotas verdes na pegada e nas fivelas (lembram as marcas verdes do lobo; sem brilho proprio);
 - Ferro: so as fivelas pequenas da cilha.
Eixos: frente -Y, Z para cima, x+ = lado esquerdo do lobo (lado E). Malha simetrica (XC = 0).
Uso: blender -b rig18/Lobo_Ancestral_Rig.blend -P montaria/m1_sela_lobo.py -- <saida.blend> <saida.json>"""
import bpy, bmesh, math, sys, os, json
import numpy as np
from mathutils import Vector as V, Matrix as M
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

NOME = "Lobo_Ancestral_Sela"
NOMES_PECA_MAT = {0: "assento", 1: "manta", 2: "tendao", 3: "madeira", 4: "resina", 5: "ferro", 6: "folha"}
XC = 0.0
def P_(n, d): return float(os.environ.get("LOBO_S_" + n, d))
MANTA = dict(ax=P_("MX", 1.02), ay=P_("MY", 1.40), yc=P_("MYC", -0.80), n=4.0, esp=0.055, nu=22, nv=22)
ABA = dict(ax=0.78, ay=1.02, yc=-0.78, n=3.0, esp=0.04, nu=12, nv=12)
ASSENTO = dict(ax=0.58, ay=0.86, yc=-0.74, n=3.0, nu=16, nv=16)
ASSENTO_Y = -0.62                                     # quadril do cavaleiro (meio do dorso, entre a juba e a garupa)
DZ_QUADRIL = 0.50
CILHA = dict(y=P_("CY", -2.05), larg=0.36, dentro=0.05, esp=0.07, nseg=40)
X0, X1, Y0, Y1, PASSO = XC - 2.0, XC + 2.0, -3.6, 1.8, 0.04
Z_PISO = 3.2
OSSOS_FORA = ("Cauda", "Pescoco", "Cabeca", "Mandibula", "Orelha", "Pelo", "Juba", "Palpebra")
SENTADO_LOBO = {   # pose sentada do manequim (relativa ao quadril; frente -Y; x+ = esquerda do manequim) - pes nos estribos
    ("IK", "LeftFoot"): (0.80, -0.30, -1.35), ("Polo", "LeftFoot"): (2.2, -1.6, 0.6),
    ("IK", "RightFoot"): (-0.80, -0.30, -1.35), ("Polo", "RightFoot"): (-2.2, -1.6, 0.6),
    ("IK", "LeftHand"): (0.22, -1.05, 0.55), ("Polo", "LeftHand"): (2.4, 1.0, 1.0),
    ("IK", "RightHand"): (-0.22, -1.05, 0.55), ("Polo", "RightHand"): (-2.4, 1.0, 1.0),
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

def criar(arm, malhas, colecao=None):
    sc = bpy.context.scene; col = colecao or sc.collection
    acao0 = arm.animation_data.action if arm.animation_data else None
    if arm.animation_data: arm.animation_data.action = None
    for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
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
            hit = bvh.ray_cast(V((x, y, 20.0)), V((0, 0, -1))); H[j, i] = hit[0].z if (hit[0] and hit[0].z > Z_PISO) else Z_PISO
    piso = _maxf(H, 2) + 0.07; E = _maxf(H, 6) + 0.05
    for _ in range(7): E = np.maximum(_blur(E, 6), piso)
    E = np.maximum(_blur(np.maximum(E, piso), 2, 1), piso)
    B = _maxf(H, 3) + 0.05; B = np.maximum(_blur(B, 2, 1), _maxf(H, 2) + 0.045)
    env, borda_pele = Campo(E), Campo(B)
    m = MANTA
    def forma_m(u, v): return _forma(u, v, m["ax"], m["ay"], m["yc"], m["n"])
    def manta_fundo_z(x, y, rho):
        w = float(_ss(0.40, 0.97, rho)); return env(x, y) * (1 - w) + borda_pele(x, y) * w
    def manta_fundo(x, y, rho): return V((x, y, manta_fundo_z(x, y, rho)))
    def manta_normal(x, y, rho, h=0.05):
        dzx = (manta_fundo_z(x + h, y, rho) - manta_fundo_z(x - h, y, rho)) / (2 * h); dzy = (manta_fundo_z(x, y + h, rho) - manta_fundo_z(x, y - h, rho)) / (2 * h)
        return V((-dzx, -dzy, 1)).normalized()
    def manta_topo(x, y, rho):
        e = m["esp"] * (0.55 + 0.45 * (1 - float(_ss(0.9, 1.0, rho)))); return manta_fundo(x, y, rho) + manta_normal(x, y, rho) * e
    def rho_m(x, y): return ((abs(x - XC) / m["ax"]) ** m["n"] + (abs(y - m["yc"]) / m["ay"]) ** m["n"]) ** (1 / m["n"])
    pecas = []; NOMES_PECA = {}
    vs, fs = _placa(manta_fundo, manta_topo, m["nu"], m["nv"], forma_m); pecas.append((vs, fs, 1, "pele", None))
    cord = []
    for k in range(52):
        c_, s_ = math.cos(2 * math.pi * k / 52), math.sin(2 * math.pi * k / 52); mx_ = max(abs(c_), abs(s_))
        x, y, _ = forma_m(c_ / mx_, s_ / mx_); cord.append(manta_topo(x, y, 1.0) - manta_normal(x, y, 1.0) * 0.012)
    vs, fs = _tubo(cord, 0.035, 5, fechado=True); pecas.append((vs, fs, 2, "pele", None))            # debrum de tendao
    # folhas de couro verde-musgo na borda da manta (as folhas da pelagem do lobo), menores e mais finas que as do urso
    NF = int(P_("NF", 22))
    for k in range(NF):
        ang = 2 * math.pi * (k + 0.5) / NF; c_, s_ = math.cos(ang), math.sin(ang); mx_ = max(abs(c_), abs(s_))
        if abs(c_) < 0.35: continue                                       # frente e tras: sem folha (juba / garupa)
        x, y, _ = forma_m(c_ / mx_ * 0.52, s_ / mx_ * 0.52); xo, yo, _ = forma_m(c_ / mx_ * 1.04, s_ / mx_ * 1.04)
        eixo = V((xo - x, yo - y, 0)); comp = eixo.length; eixo.normalize(); base = V((x, y, 0))
        larg = 0.085 + 0.015 * math.cos(k * 1.7); gir = math.radians(12 * math.sin(k * 3.1))
        eixo = (M.Rotation(gir, 3, "Z") @ eixo).normalized()
        def apoio(p):
            r = rho_m(p.x, p.y)
            if r > 1.0:
                p = V((XC + (p.x - XC) / r * 0.995, m["yc"] + (p.y - m["yc"]) / r * 0.995, 0)); r = 0.995
            return V((p.x, p.y, manta_topo(p.x, p.y, r).z + 0.010))
        vs, fs = _folha(base, eixo, V((0, 0, 1)), comp, larg, 0.025, apoio, curva=0.15)
        NOMES_PECA[len(pecas)] = "folha"; pecas.append((vs, fs, 6, "pele", None))
    manta_top_z = lambda x, y: manta_topo(x, y, 0.0).z
    b_ = ABA
    def forma_b(u, v): return _forma(u, v, b_["ax"], b_["ay"], b_["yc"], b_["n"])
    def aba_fundo(x, y, rho): return V((x, y, manta_top_z(x, y) + 0.012))
    def aba_topo(x, y, rho): return aba_fundo(x, y, rho) + V((0, 0, b_["esp"]))
    vs, fs = _placa(aba_fundo, aba_topo, b_["nu"], b_["nv"], forma_b); NOMES_PECA[len(pecas)] = "aba"; pecas.append((vs, fs, 0, "pele", None))
    def aba_top_z(x, y):
        dentro_ = (abs(x - XC) / b_["ax"]) ** b_["n"] + (abs(y - b_["yc"]) / b_["ay"]) ** b_["n"] <= 1
        return manta_top_z(x, y) + 0.012 + (b_["esp"] if dentro_ else 0.0)
    pontos = []
    for k in range(30):
        c_, s_ = math.cos(2 * math.pi * k / 30), math.sin(2 * math.pi * k / 30); mx_ = max(abs(c_), abs(s_))
        u, v = c_ / mx_ * 0.90, s_ / mx_ * 0.90; x, y, _ = forma_b(u, v); pontos.append(V((x, y, aba_top_z(x, y) + 0.003)))
    for k in range(0, 30, 2):
        vs, fs = _tubo([pontos[k], pontos[k + 1]], 0.016, 3); pecas.append((vs, fs, 2, "pele", None))
    # ---------------------------------------------------------------- assento baixo (Couro de Javali)
    a = ASSENTO
    def forma_a(u, v): return _forma(u, v, a["ax"], a["ay"], a["yc"], a["n"])
    def uv_a(x, y): return (x - XC) / a["ax"], (y - a["yc"]) / a["ay"]
    def espessura(x, y, rho):
        u, v = uv_a(x, y)
        t = 0.09 + 0.03 * float(_ss(0.0, 0.6, abs(v)))
        t += 0.12 * math.exp(-((v + 0.82) / 0.16) ** 2) * math.exp(-(u / 0.45) ** 2)          # cabeca baixa (frente, -Y)
        t += 0.16 * float(_ss(0.35, 0.86, v)) * (1 - 0.50 * u * u)                            # patilha baixa (atras)
        e = 1 - float(_ss(0.80, 1.0, rho)) ** 1.5
        return 0.035 + (t - 0.035) * e
    def assento_fundo(x, y, rho): return V((x, y, aba_top_z(x, y) - 0.003))
    def assento_topo(x, y, rho): return assento_fundo(x, y, rho) + V((0, 0, espessura(x, y, rho)))
    vs, fs = _placa(assento_fundo, assento_topo, a["nu"], a["nv"], forma_a); NOMES_PECA[len(pecas)] = "assento"; pecas.append((vs, fs, 0, "pele", None))
    z_assento = assento_topo(XC, ASSENTO_Y, 0.0).z; Zq = z_assento + DZ_QUADRIL
    def topo_a(x, y):
        u, v = uv_a(x, y); r = max(0.0, min(1.0, ((abs(u)) ** a["n"] + (abs(v)) ** a["n"]) ** (1 / a["n"]))); return assento_topo(x, y, r)
    cs = []                                                               # costura de tendao em volta do assento
    for k in range(40):
        c_, s_ = math.cos(2 * math.pi * k / 40), math.sin(2 * math.pi * k / 40); mx_ = max(abs(c_), abs(s_))
        x, y, _ = forma_a(c_ / mx_ * 0.93, s_ / mx_ * 0.93); cs.append(topo_a(x, y) + V((0, 0, 0.004)))
    for k in range(0, 40, 2):
        vs, fs = _tubo([cs[k], cs[k + 1]], 0.014, 3); pecas.append((vs, fs, 2, "pele", None))
    # ---------------------------------------------------------------- pegada de galho fino (Madeira Ancestral) na frente
    yh = a["yc"] - 0.86 * a["ay"]; zc = topo_a(XC, yh).z
    galho = []; rg = []
    for k in range(13):
        t = k / 12; ang = math.pi * t
        galho.append(V((XC + 0.20 * math.cos(ang) + 0.012 * math.sin(7 * t), yh - 0.03 - 0.03 * math.sin(ang), zc - 0.04 + 0.22 * math.sin(ang))))
        rg.append(0.042 * (1.0 - 0.15 * math.sin(ang)) * (1 + 0.08 * math.sin(11 * t)))
    vs, fs = _tubo(galho, rg, 7); NOMES_PECA[len(pecas)] = "pegada"; pecas.append((vs, fs, 3, "rigido", V((XC, yh, zc))))
    espiral = []
    for k in range(50):
        t = 0.25 + 0.50 * k / 49; i = t * 12; i0 = int(i); f = i - i0; p = galho[i0].lerp(galho[min(i0 + 1, 12)], f)
        d = (galho[min(i0 + 1, 12)] - galho[i0]).normalized(); b1 = d.cross(V((0, 1, 0))).normalized(); b2 = d.cross(b1)
        ang = k * 0.9; espiral.append(p + (b1 * math.cos(ang) + b2 * math.sin(ang)) * 0.050)
    vs, fs = _tubo(espiral, 0.011, 4); pecas.append((vs, fs, 2, "rigido", V((XC, yh, zc))))
    topo_g = galho[6]; nf = V((0, -0.55, 1.0)).normalized(); t1 = V((1, 0, 0))
    for s in (1, -1):                                                     # duas folhinhas de madeira e uma gota de Resina Viva
        e2 = (V((0, 0.5, 0.2)) + t1 * s * 0.9).normalized()
        vs, fs = _folha(topo_g + V((0, 0.02, 0.02)), e2, nf, 0.20, 0.07, 0.022, None, curva=0.10); pecas.append((vs, fs, 3, "rigido", topo_g))
    vs, fs = _cabochao(topo_g + nf * 0.035, nf, 0.045, 0.035, alongar=1.3); pecas.append((vs, fs, 4, "rigido", topo_g))
    # ---------------------------------------------------------------- cilha fina (Couro de Javali) + fivelas de ferro com Resina Viva
    c = CILHA; cy = c["y"]; zc0 = 4.6; cx0 = XC
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
    for k_f in (int(len(ph) * 0.18), int(len(ph) * 0.82)):              # fivelas pequenas nos flancos, sobre a cilha
        p = ph[k_f]; d = V((math.cos(p), 0, math.sin(p))); cen = V((cx0, cy, zc0)) + d * (r[k_f] + c["esp"] + 0.015)
        t1_ = V((0, 1, 0)); t2_ = d.cross(t1_).normalized()
        anel = [cen + (t1_ * math.cos(2 * math.pi * k / 12) * 0.17 + t2_ * math.sin(2 * math.pi * k / 12) * 0.12) for k in range(12)]
        vs, fs = _tubo(anel, 0.022, 5, fechado=True); NOMES_PECA[len(pecas)] = "fivela"; pecas.append((vs, fs, 5, "rigido", cen))
        vs, fs = _cabochao(cen + d * 0.01, d, 0.05, 0.035, 10, 3); pecas.append((vs, fs, 4, "rigido", cen))
    # ---------------------------------------------------------------- estribos leves: cordao de tendao + degrau de Madeira Ancestral
    PERNA = 1.62; yp = ASSENTO_Y - 0.30; info = {"z_quadril": Zq, "z_assento_centro": z_assento, "quadril": [XC, ASSENTO_Y, Zq],
                                                "estribos": {}, "pegada": [XC, yh - 0.05, zc + 0.20]}
    for lado, s in (("Left", 1), ("Right", -1)):
        hip = V((XC + 0.5 * s, ASSENTO_Y, Zq)); best = None
        for k in range(120):                                              # tornozelo: perna PERNA, 0,30 fora do flanco
            zt = Zq - 0.4 - 0.02 * k
            hit = bvh.ray_cast(V((XC + s * 6.0, yp, zt)), V((-s, 0, 0)))
            xf = (hit[0].x if hit[0] else XC) + s * P_("FOLGA_PE", 0.62)   # r2: 0,30 deixava canela e pe do R15 dentro do pelo (-0,45)
            tz_ = V((xf, yp, zt))
            if best is None or abs((tz_ - hip).length - PERNA) < abs((best - hip).length - PERNA): best = tz_
        rel = best - V((XC, ASSENTO_Y, Zq)) - V((0.5 * s, 0, 0))
        SENTADO_LOBO[("IK", lado + "Foot")] = (round(rel.x, 3), round(rel.y, 3), round(rel.z, 3))
        sola_z = best.z - 0.30
        deg = []; dw, dl, de = 0.20, 0.30, 0.06
        for zz in (sola_z - de - 0.005, sola_z - 0.005):
            for dx in (-dw, dw):
                for dy in (-dl, dl): deg.append(V((best.x + dx, best.y - 0.12 + dy, zz)))
        dfs = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        NOMES_PECA[len(pecas)] = "estribo"; pecas.append((deg, dfs, 3, "rigido", best))
        xb, yb, _ = forma_m(s * 1.0, (best.y - 0.12 - m["yc"]) / m["ay"])
        topo_b = manta_topo(xb, yb, 1.0) - V((0, 0, 0.02))
        for dy in (-0.24, 0.24):
            a_ = V((best.x - s * 0.02, best.y - 0.12 + dy, sola_z - 0.03)); b2_ = V((topo_b.x - s * 0.03, topo_b.y + dy * 0.6, topo_b.z))
            pts = [a_.lerp(b2_, t) + V((s * 0.06 * math.sin(math.pi * t), 0, 0)) for t in np.linspace(0, 1, 8)]
            vs, fs = _tubo(pts, 0.022, 5); NOMES_PECA[len(pecas)] = "estribo"; pecas.append((vs, fs, 2, "rigido", best))
        info["estribos"][lado] = {"tornozelo": [round(c_, 3) for c_ in best], "perna": round((best - hip).length, 3), "sola_z": round(sola_z, 3)}
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
    for nm, cor, rug, met in (("M_SelaLobo_CouroJavali", (0.15, 0.08, 0.04), 0.55, 0.0), ("M_SelaLobo_PeleCervo", (0.11, 0.075, 0.04), 0.9, 0.0),
                              ("M_SelaLobo_TendaoCervo", (0.50, 0.42, 0.28), 0.75, 0.0), ("M_SelaLobo_MadeiraAncestral", (0.30, 0.22, 0.14), 0.85, 0.0),
                              ("M_SelaLobo_ResinaViva", (0.30, 0.62, 0.30), 0.12, 0.0), ("M_SelaLobo_Ferro", (0.26, 0.25, 0.24), 0.5, 1.0),
                              ("M_SelaLobo_CouroFolha", (0.10, 0.14, 0.05), 0.6, 0.0)):
        me.materials.append(bpy.data.materials.get(nm) or _material(nm, cor, rug, met))
    bpy.context.view_layer.objects.active = ob
    for o_ in bpy.context.selected_objects: o_.select_set(False)
    ob.select_set(True); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.01); bpy.ops.object.mode_set(mode="OBJECT")
    grupos = {n: ob.vertex_groups.new(name=n) for n in ossos if not n.startswith(OSSOS_FORA)}
    def peso_em(p, raio=0.40):
        loc = bvh.find_nearest(p)[0] or p; acc = np.zeros(len(ossos)); tot = 0.0
        for (_, i, d) in kd.find_range(loc, raio):
            g = math.exp(-(d / (raio * 0.5)) ** 2); acc += Wp[i] * g; tot += g
        if tot == 0 or acc.sum() == 0: acc = np.zeros(len(ossos)); acc[oi["Coluna2"]] = 1.0; tot = 1.0
        acc /= max(acc.sum(), 1e-9); idx = np.argsort(acc)[::-1][:4]; w = acc[idx]; w = w / w.sum()
        return [(ossos[k], float(x)) for k, x in zip(idx, w) if x > 1e-3]
    def raio_de(vi):
        if vpeca[vi] in ("cilha",): return 0.55
        x, y, _ = allv[vi]; rho = rho_m(x, y)
        return 0.6 - 0.2 * float(_ss(0.62, 0.95, rho))
    ASS = peso_em(V((XC, ASSENTO_Y, z_assento)))                         # estribos rigidos no osso do assento (o cavaleiro tambem)
    for o, n, tp, anc in tipos:
        fixo = ASS if (tp == "rigido" and vpeca[o] == "estribo") else (peso_em(anc) if tp == "rigido" else None)
        for vi in range(o, o + n):
            for nm, w in (fixo or peso_em(V(allv[vi]), raio_de(vi))):
                if nm in grupos: grupos[nm].add([vi], w, "REPLACE")
    ob.parent = arm; ob.matrix_parent_inverse = arm.matrix_world.inverted()
    md = ob.modifiers.new("Armature", "ARMATURE"); md.object = arm
    ob["etapa"] = "M1 sela leve da Floresta (proposta)"; ob["z_quadril"] = Zq; ob["quadril"] = info["quadril"]
    ob["sentado"] = json.dumps({"%s|%s" % k: v for k, v in SENTADO_LOBO.items()})
    if arm.animation_data: arm.animation_data.action = acao0
    info["tris"] = sum(len(p.vertices) - 2 for p in me.polygons); info["vertices"] = len(me.vertices)
    info["materiais"] = [mt.name for mt in me.materials]; info["peso_assento"] = ASS
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
    if nome == "M_SelaLobo_PeleCervo":                     # pelo curto: ruido fino
        nz.inputs["Scale"].default_value = 40.0; nz.inputs["Detail"].default_value = 8.0; bump.inputs["Strength"].default_value = 0.35
        nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    elif nome == "M_SelaLobo_ResinaViva":                  # resina: lisa, um pouco translucida (sem emissao)
        b.inputs["Transmission Weight"].default_value = 0.4; b.inputs["IOR"].default_value = 1.54; bump.inputs["Strength"].default_value = 0.02
        nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    elif nome == "M_SelaLobo_TendaoCervo":                 # cordao torcido
        w_ = nt.nodes.new("ShaderNodeTexWave"); w_.inputs["Scale"].default_value = 30; nt.links.new(tc.outputs["Object"], w_.inputs["Vector"])
        bump.inputs["Strength"].default_value = 0.25; nt.links.new(w_.outputs["Fac"], bump.inputs["Height"])
    elif nome == "M_SelaLobo_MadeiraAncestral":            # casca: veios alongados e sulcos
        w_ = nt.nodes.new("ShaderNodeTexWave"); w_.inputs["Scale"].default_value = 6; w_.inputs["Distortion"].default_value = 8
        w_.wave_type = "BANDS"; nt.links.new(tc.outputs["Object"], w_.inputs["Vector"])
        nt.links.new(w_.outputs["Fac"], ramp.inputs["Fac"]); bump.inputs["Strength"].default_value = 0.6; nt.links.new(w_.outputs["Fac"], bump.inputs["Height"])
    else:
        bump.inputs["Strength"].default_value = 0.15; nt.links.new(nz.outputs["Fac"], bump.inputs["Height"])
    return mt

if __name__ == "__main__":
    A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    arm = bpy.data.objects["Lobo_Ancestral_Rig"]; malhas = [bpy.data.objects["Lobo_Ancestral_LOW"]]
    ob, Zq, info = criar(arm, malhas)
    print("SELA", json.dumps(info))
    if len(A) > 1: json.dump(info, open(A[1], "w"), indent=1)
    if A: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A[0]))
    print("SELA_OK")
