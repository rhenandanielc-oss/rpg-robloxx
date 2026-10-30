# Lobo Ancestral V5 (27/10/2026): refinamento realista sobre a V4 (lobo_v4.py preservado; mesmo esqueleto J/DH).
# Referencia oficial: REFERENCES/03_CREATURES/01-lobos-urso-leao.png (painel 01: corpo, cabeca, pelagem com musgo e
# samambaias, patas com garras escuras, silhueta com humano, paleta oliva/castanho) + RPG_02 secao 5 (5,5-7 studs no
# ombro, "esguio/atletico"; Artico mais robusto). Interpretacao: atletico e musculoso, volume vindo da pelagem densa.
# Mudancas: massas de peito/ombro/coxa/pescoco maiores (moderadas), patas maiores com garras longas; pelagem em duas
# camadas: (1) mechas de geometria exportaveis na silhueta e cobrindo o corpo, (2) fios finos de alta resolucao usados
# so para assar normal + oclusao na textura do corpo (exportavel como imagem; nada de particulas no GLB);
# samambaias e musgo ("natural armor").
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
from lobo_v4 import J, DH, _cauda, folha

# Equilibrio corpo/cabeca: a cabeca (referencial V3) cresce HS em torno do topo do pescoco P0 e depois desce DH.
HS = 1.12
P0 = Vector((0, -3.45, 8.0))
M_CAB = Matrix.Translation(DH + P0) @ Matrix.Diagonal((HS, HS, HS, 1)) @ Matrix.Translation(-P0)
H = lambda p: tuple(M_CAB @ Vector(p))


def local_cabeca(p):
    """Coordenada no referencial V3 da cabeca (para regioes de pelo e mascara); None fora da cabeca."""
    q = P0 + (Vector(p) - DH - P0) / HS
    return q if (q.y < -3.2 and q.z > 7.3) else None


J = dict(J)
J["focinho"] = H((0, -5.05, 8.05)); J["mand"] = (H((0, -3.7, 7.82)), H((0, -4.9, 7.82)))
# ossos secundarios de pelagem (balanco gravado nas animacoes; o corpo nao usa estes ossos)
PELO_OSSOS = [("Pelo_JubaE", (0.55, -2.6, 6.2), (0.72, -2.45, 5.3), "Pescoco1"), ("Pelo_JubaD", (-0.55, -2.6, 6.2), (-0.72, -2.45, 5.3), "Pescoco1"),
              ("Pelo_Peito", (0, -3.15, 5.6), (0, -3.2, 4.6), "Pescoco1"), ("Pelo_Nuca", (0, -2.7, 6.95), (0, -2.0, 6.55), "Pescoco2"),
              ("Pelo_VentreE", (0.4, -0.5, 3.95), (0.45, -0.4, 3.4), "Coluna2"), ("Pelo_VentreD", (-0.4, -0.5, 3.95), (-0.45, -0.4, 3.4), "Coluna2"),
              ("Pelo_BochechaE", H((0.4, -3.7, 8.0)), H((0.55, -3.3, 7.75)), "Cabeca"), ("Pelo_BochechaD", H((-0.4, -3.7, 8.0)), H((-0.55, -3.3, 7.75)), "Cabeca"),
              ("Pelo_CoxaE", (0.6, 2.0, 3.6), (0.62, 2.2, 3.0), "Quadril"), ("Pelo_CoxaD", (-0.6, 2.0, 3.6), (-0.62, 2.2, 3.0), "Quadril")]

OLHO_COR = (0.4, 0.33, 0.06)                       # ambar-esverdeado (painel oficial)
OLHO_X = 0.29                                      # cranio mais largo: olho na nova superficie (referencial V3)


def construir():
    from blockout_lib import (cena_nova, colecao, Partes, elipsoide, cadeia, trilha, massa, fundir, juntar,
                              material_papel, pata_digitigrada, humano, medidas)
    cena_nova()
    col = colecao("Lobo_Ancestral")
    rg = Partes()
    mole = bmesh.new()
    elipsoide(mole, (0, -1.5, 4.85), (0.84, 1.8, 1.6))                   # torax fundo
    elipsoide(mole, (0, -2.8, 4.75), (0.6, 0.68, 1.02))                  # peito (manubrio) mais cheio
    elipsoide(mole, (0, -0.45, 4.5), (0.7, 1.12, 0.95))                  # torax -> abdomen
    elipsoide(mole, (0, 0.75, 4.62), (0.66, 1.05, 0.74))                 # flanco
    elipsoide(mole, (0, 0.4, 5.22), (0.64, 1.3, 0.76))                   # lombo
    elipsoide(mole, (0, 1.6, 5.12), (0.74, 1.0, 0.88))                   # garupa
    for s in (1, -1):
        elipsoide(mole, (s * 0.46, -1.7, 5.55), (0.22, 0.72, 0.85), rot=(-30, 0, 0))    # escapula (achatada, sem borda)
        elipsoide(mole, (s * 0.56, -2.3, 4.85), (0.26, 0.5, 0.56), rot=(-20, 0, 0))     # deltoide / ombro
        elipsoide(mole, (s * 0.52, 1.0, 3.95), (0.26, 0.52, 0.44))                      # prega do joelho
    trilha(mole, [(0, -1.9, 5.5, 1.04), (0, -2.65, 6.3, 0.88), (0, -3.25, 6.95, 0.72), (0, -3.55, 7.35, 0.62)],
           achatar=(0.88, 1.0), passo=0.2, u=20, v=10)                    # pescoco forte
    elipsoide(mole, (0, -3.0, 5.95), (0.58, 0.66, 0.76))                 # garganta
    elipsoide(mole, (0, -1.95, 5.75), (0.78, 0.95, 0.75))                # trapezio: pescoco -> cernelha -> ombros sem degrau
    cab = bmesh.new()                                                    # cabeca (referencial V3, deslocada por DH)
    elipsoide(cab, (0, -3.72, 8.35), (0.52, 0.6, 0.49))                  # cranio mais largo
    elipsoide(cab, (0, -3.32, 8.38), (0.42, 0.36, 0.42))
    trilha(cab, [(0, -4.15, 8.24, 0.3), (0, -4.6, 8.12, 0.225), (0, -4.95, 8.03, 0.14)], achatar=(0.74, 0.9), passo=0.08, u=16, v=8)
    trilha(cab, [(0, -3.75, 7.83, 0.2), (0, -4.4, 7.83, 0.13), (0, -4.8, 7.86, 0.085)], achatar=(1.0, 0.75), passo=0.08, u=16, v=8)
    for s in (1, -1):
        elipsoide(cab, (s * 0.13, -4.45, 7.98), (0.1, 0.42, 0.115))
        elipsoide(cab, (s * 0.33, -3.8, 8.0), (0.18, 0.32, 0.24))       # masseter
        elipsoide(cab, (s * 0.45, -3.85, 8.22), (0.13, 0.32, 0.13))      # zigomatico
    bmesh.ops.transform(cab, matrix=M_CAB, verts=cab.verts); juntar(mole, cab)
    F, T = J["frente"], J["tras"]
    for s in (1, -1):
        X = lambda p: (s * p[0], p[1], p[2])
        cadeia(mole, [X(F[0]) + (0.2,), X(F[1]) + (0.38,), X(F[2]) + (0.36,), X(F[3]) + (0.29,), (s * 0.53, -2.42, 0.38, 0.26)], seg=18)
        elipsoide(mole, X((0.62, -2.12, 4.1)), (0.31, 0.45, 0.66), rot=(25, 0, 0))     # triceps
        elipsoide(mole, X((0.64, -2.55, 3.95)), (0.22, 0.24, 0.5))                     # braquial
        elipsoide(mole, X((0.58, -2.12, 2.6)), (0.31, 0.33, 0.7), rot=(-6, 0, 0))      # antebraco (mais grosso)
        cadeia(mole, [X(T[0]) + (0.45,), X(T[1]) + (0.34,), X(T[2]) + (0.26,), (s * 0.5, 1.82, 0.36, 0.25)], seg=18)
        elipsoide(mole, X((0.6, 1.15, 4.05)), (0.4, 0.82, 1.02), rot=(-27, 0, 0))     # quadriceps
        elipsoide(mole, X((0.5, 1.72, 3.95)), (0.32, 0.5, 0.95), rot=(-20, 0, 0))     # isquiotibiais (integrados a coxa)
        elipsoide(mole, X((0.3, 2.05, 4.55)), (0.34, 0.5, 0.62), rot=(-15, 0, 0))     # nadega: liga coxa, garupa e cauda
        elipsoide(mole, X((0.56, 1.25, 2.8)), (0.24, 0.31, 0.66), rot=(35, 0, 0))     # gastrocnemio
    elipsoide(mole, (0, 2.2, 4.85), (0.46, 0.5, 0.55))                   # raiz da cauda fundida a garupa
    cadeia(mole, [(0, 2.2, 5.1, 0.38), (0, 2.75, 4.55, 0.46), (0, 3.25, 3.7, 0.5), (0, 3.75, 2.8, 0.46),
                  (0, 4.25, 1.9, 0.34), (0, 4.62, 1.15, 0.16)], seg=18)
    estr = massa(mole, voxel=0.045, suav_iter=8, suav_fator=0.5, laplace=16)
    volume_pelo(estr, 1.0)                                               # subpelo: volume real da pelagem
    det = bmesh.new()
    for s in (1, -1):
        elipsoide(estr, (s * 0.62, -1.92, 3.35), (0.16, 0.18, 0.17))                  # olecrano
        elipsoide(estr, (s * 0.56, -2.25, 1.0), (0.22, 0.23, 0.2))                    # carpo
        elipsoide(estr, (s * 0.52, 2.1, 1.45), (0.14, 0.17, 0.16))                    # calcaneo
        elipsoide(det, (s * (OLHO_X - 0.01), -4.12, 8.56), (0.15, 0.2, 0.075), rot=(14, 0, s * -18))   # arcada
        elipsoide(det, (s * 0.1, -4.02, 8.64), (0.08, 0.18, 0.055))
        pata_digitigrada(estr, rg("garra"), (s * 0.54, -2.6, 0.0), s, 0.42, 0.76, dedos=4, garra_comp=0.17)   # patas grandes
        pata_digitigrada(estr, rg("garra"), (s * 0.5, 1.62, 0.0), s, 0.38, 0.7, dedos=4, garra_comp=0.15)
        elipsoide(estr, (s * 0.6, -2.42, 0.22), (0.07, 0.07, 0.08))                   # dedo vestigial (ergot)
    elipsoide(det, (0, -5.0, 8.07), (0.11, 0.075, 0.085))                 # trufa
    elipsoide(det, (0, -4.1, 8.48), (0.15, 0.24, 0.075))                  # stop
    bmesh.ops.transform(det, matrix=M_CAB, verts=det.verts); juntar(estr, det)
    olho = bmesh.new()
    for s in (1, -1):
        elipsoide(olho, (s * OLHO_X, -4.19, 8.42), (0.05, 0.086, 0.046), rot=(19, 0, s * -25), u=14, v=7)
    bmesh.ops.transform(olho, matrix=M_CAB, verts=olho.verts); juntar(rg("olho"), olho)
    pup = bmesh.new()                                                    # pupilas (material escuro) na face externa do olho
    for s in (1, -1):
        R = Matrix.Rotation(math.radians(s * -25), 3, "Z") @ Matrix.Rotation(math.radians(19), 3, "X")
        c = Vector((s * OLHO_X, -4.19, 8.42)) + R @ Vector((s * 0.046, 0, 0))
        elipsoide(pup, c, (0.012, 0.03, 0.032), rot=(19, 0, s * -25), u=10, v=5)
    bmesh.ops.transform(pup, matrix=M_CAB, verts=pup.verts); juntar(rg("garra"), pup)
    corpo = fundir("Lobo_Ancestral_Corpo_Blockout", estr, col, voxel=0.04, suav_iter=5, suav_fator=0.5, tris=12000)
    material_papel(corpo, "pelo")
    rg.criar("Lobo_Ancestral", col)
    pel = pelagem(corpo, col)
    humano(-5.0, -9.0)
    md = medidas(col)
    print("MEDIDAS", md, "PELAGEM_TRIS", pel["tris"])
    return col


# ------------------------------------------------------------------ PELAGEM EXPORTAVEL
CORES_ATLAS = [(0.13, 0.125, 0.115), (0.045, 0.043, 0.04), (0.19, 0.186, 0.176), (0.06, 0.09, 0.025)]   # claro bem mais discreto   # Cinza da Floresta: cinza, grafite, cinza-claro, musgo
NC = 5                                                             # colunas do atlas: 0-3 pelo, 4 folhas
FOLHA_VERDES = [(0.018, 0.038, 0.01), (0.035, 0.065, 0.016), (0.08, 0.1, 0.028)]   # escuro, medio, amarelado


def atlas():
    """Atlas 640x256: 4 colunas de pelo (fios finos, raiz sombreada) + 1 coluna de folhas (3 faixas de verde, nervuras)."""
    W_, H_ = 128 * NC, 256
    rng = np.random.default_rng(7)
    u = np.arange(W_)[None, :].repeat(H_, 0); v = np.arange(H_)[:, None].repeat(W_, 1) / (H_ - 1)
    fio = np.interp(u.ravel() + 3 * np.sin(v.ravel() * 9), np.arange(W_), 0.8 + 0.4 * rng.random(W_)).reshape(H_, W_)
    grad = (0.8 + 0.25 * np.minimum(1, v * 3)) * (1 - 0.25 * v ** 2)
    # casca: fibras longitudinais + fendas escuras interrompidas + liquen claro esverdeado em manchas
    fib = 0.75 + 0.5 * np.interp(u.ravel() + 6 * np.sin(v.ravel() * 5 + u.ravel() * 0.05), np.arange(W_), rng.random(W_)).reshape(H_, W_)
    fenda = np.ones((H_, W_))
    for _ in range(90):
        x0 = rng.integers(0, W_); y0, y1 = sorted(rng.integers(0, H_, 2)); wd = rng.integers(1, 3)
        fenda[y0:y1, x0:x0 + wd] = 0.35
    liq = (np.interp(u.ravel() * 0.07 + v.ravel() * 11, np.arange(64), rng.random(64)).reshape(H_, W_) > 0.8) & (rng.random((H_, W_)) > 0.35)
    img = np.zeros((H_, W_, 4)); img[..., 3] = 1
    for c, cor in enumerate(CORES_ATLAS):
        sl = slice(c * 128, (c + 1) * 128)
        for k in range(3):
            val = cor[k] * grad[:, sl] * fio[:, sl] * fib[:, sl] * fenda[:, sl]
            if c != 3: val = np.where(liq[:, sl], val * 0.5 + (0.16, 0.18, 0.13)[k] * 0.5, val)
            img[:, sl, k] = np.clip(val, 0, 1) ** (1 / 2.2)
    uu = (np.arange(128) - 64) / 64.0                                  # coluna de folhas: nervura central e laterais
    for bnd, cor in enumerate(FOLHA_VERDES):
        vv = np.linspace(0, 1, H_ // 3)[:, None]
        nerv = 1 + 0.35 * np.exp(-(uu[None, :] / 0.05) ** 2) + 0.15 * (np.abs(np.sin((vv * 9 - np.abs(uu[None, :]) * 3) * math.pi)) > 0.93)
        mancha = 0.85 + 0.3 * rng.random((H_ // 3, 128))
        for k in range(3):
            img[bnd * (H_ // 3):(bnd + 1) * (H_ // 3), 512:640, k] = np.clip(cor[k] * nerv * mancha * (0.8 + 0.3 * vv), 0, 1) ** (1 / 2.2)
    im = bpy.data.images.new("Lobo_Ancestral_Pelagem_Atlas", W_, H_, alpha=False)
    im.pixels.foreach_set(img.astype(np.float32).ravel()); im.pack()
    return im


def regiao(p, n):
    x, y, z = p
    q = local_cabeca(p)
    if q is not None:
        if -3.95 < q.y and q.z < 8.15 and abs(x) > 0.27: return "bochecha"     # so a parte baixa: nada perto das orelhas
        if q.y > -4.78 and all((q - Vector((s * OLHO_X, -4.19, 8.42))).length > 0.15 for s in (1, -1)): return "cabeca"
        return None
    if y > 2.1 and z < 5.2 and _cauda(Vector(p))[0] < 0.75: return "cauda"
    if 1.4 < z < 3.3 and -2.7 < y < -1.5 and abs(x) > 0.3 and n.y > 0.3: return "antebraco"
    if 1.5 < z < 2.9 and 1.0 < y < 2.4 and n.y > 0.3: return "canela"
    if 0.28 < z < 3.3 and abs(x) > 0.22: return "perna"                # pernas cobertas ate as patas
    if z < 2.7: return None
    if y < -1.55 and z > 4.1 and (z > 5.2 or abs(x) < 0.5): return "colar"
    if y < -1.0 and z < 4.1 and abs(x) < 0.5: return "peito"
    if z > 5.45: return "dorso"
    if z < 3.95 and -1.6 < y < 0.9 and abs(x) < 0.62: return "ventre"
    if y > 0.6 and 2.9 < z < 5.1 and abs(x) > 0.35: return "coxa"
    if -2.9 < y < -1.3 and 3.2 < z < 5.2 and abs(x) > 0.45: return "ombro"
    if -2.0 < y < 1.6 and 3.9 < z < 5.45 and abs(x) > 0.4: return "flanco"
    return None


#            fluxo (crescimento)   comp (min,max)  larg   elev  espaco  fios
REG = {"colar": ((0, 0.5, -1), (0.6, 0.9), 0.08, 0.28, 0.15, 3), "peito": ((0, 0.2, -1), (0.5, 0.68), 0.075, 0.14, 0.16, 3),
       "bochecha": (None, (0.42, 0.58), 0.065, 0.28, 0.1, 3), "cabeca": ((0, 1, 0.05), (0.14, 0.22), 0.04, 0.08, 0.1, 2),
       "dorso": ((0, 1, -0.25), (0.45, 0.65), 0.07, 0.18, 0.16, 3), "ventre": ((0, 0.2, -1), (0.4, 0.55), 0.065, 0.22, 0.18, 2),
       "coxa": ((0, 0.45, -1), (0.35, 0.5), 0.065, 0.14, 0.15, 2), "ombro": ((0, 0.35, -1), (0.3, 0.42), 0.06, 0.12, 0.14, 2),
       "flanco": ((0, 1, -0.45), (0.3, 0.42), 0.06, 0.1, 0.14, 2), "perna": ((0, 0.12, -1), (0.3, 0.42), 0.06, 0.17, 0.15, 2), "cauda": (None, (0.55, 1.05), 0.085, 0.3, 0.13, 3),
       "antebraco": ((0, 0.6, -1), (0.3, 0.42), 0.055, 0.12, 0.14, 2), "canela": ((0, 0.6, -1), (0.25, 0.32), 0.05, 0.1, 0.16, 2)}


def fio(bm, uvl, p, n, d, L, w, elev, u0, u1):
    """Um fio pontiagudo deitado (secao em V, 6 triangulos), UV ao longo do comprimento."""
    b = n.cross(d).normalized(); um = (u0 + u1) / 2
    def eixo(s): return p - n * 0.025 + d * L * s + n * (L * (elev * s - elev * 0.7 * s * s) + 0.035 * s)   # ponta sempre fora da pele
    c0, c1 = eixo(0.0), eixo(0.5)
    r0 = [bm.verts.new(c0 + b * w * 0.5), bm.verts.new(c0 + n * w * 0.45), bm.verts.new(c0 - b * w * 0.5)]
    r1 = [bm.verts.new(c1 + b * w * 0.32), bm.verts.new(c1 + n * w * 0.3), bm.verts.new(c1 - b * w * 0.32)]
    tp = bm.verts.new(eixo(1.0))
    UV = {r0[0]: (u0, 0), r0[1]: (um, 0), r0[2]: (u1, 0), r1[0]: (u0, 0.5), r1[1]: (um, 0.5), r1[2]: (u1, 0.5), tp: (um, 1.0)}
    for fv in ((r0[0], r0[1], r1[1], r1[0]), (r0[1], r0[2], r1[2], r1[1]), (r1[0], r1[1], tp), (r1[1], r1[2], tp)):
        f = bm.faces.new(fv)
        if uvl is not None:
            for lp in f.loops: lp[uvl].uv = UV[lp.vert]


CASCA = {"colar", "dorso", "ombro", "coxa", "flanco", "cauda"}       # mechas em tiras de casca (mais largas, com crista)


def espessura(p, n):
    """Espessura do pelo (studs) por regiao: juba e peito grossos, dorso/flancos medios, pernas e rosto curtos."""
    q = local_cabeca(p)
    if q is not None:
        if q.y < -4.3 or any((q - Vector((s * OLHO_X, -4.19, 8.42))).length < 0.18 for s in (1, -1)): return 0.0
        if abs(q.x) > 0.3 and q.z < 8.2 and q.y > -3.95: return 0.17                  # colar facial (bochechas)
        return 0.05
    x, y, z = p
    if z < 0.4: return 0.0
    if y > 2.1 and z < 5.2 and _cauda(Vector(p))[0] < 0.8: return 0.22
    if z < 3.3 and abs(x) > 0.22: return 0.04 + 0.05 * (z / 3.3)
    if y < -1.55 and z > 4.1: return 0.3
    if y < -1.0 and z < 4.1: return 0.26
    if z > 5.45: return 0.19
    if z < 3.95: return 0.16
    return 0.14


def volume_pelo(bm, fator=1.0, semente=3.0):
    """Infla a superficie pela espessura do pelo, com mechas alongadas no sentido do crescimento (ruido anisotropico):
    o corpo passa a ter o volume e a silhueta de uma pelagem real; o remesh da fusao junta tudo."""
    from mathutils import noise
    bm.normal_update()
    novo = []
    for v in bm.verts:
        p = v.co.copy(); n = v.normal.copy()
        t = espessura(p, n) * fator
        if t <= 0: novo.append(p); continue
        f = fluxo_geral(p, n); d = f - n * f.dot(n)
        if d.length < 1e-3: d = Vector((0, 1, 0))
        d.normalize(); b = n.cross(d)
        c = Vector((p.dot(d) * 1.3 + semente, p.dot(b) * 5.5, p.dot(n) * 2.0))
        mech = 0.5 + 0.5 * noise.noise(c)
        novo.append(p + n * t * (0.5 + 0.7 * mech))
    for v, p in zip(bm.verts, novo): v.co = p


def mecha(bm, uvl, p, n, d, L, w, elev, u0, u1):
    """Mecha macia: secao arredondada, deitada sobre o subpelo, ponta ARREDONDADA (sem bico) que volta para a
    pelagem, como pelo real assentado. 14 triangulos."""
    b = n.cross(d).normalized(); um = (u0 + u1) / 2
    e = elev * 0.5
    def eixo(s): return p - n * 0.03 + d * L * s + n * (L * (e * s - e * 1.1 * s * s) + 0.03 * s)
    perfil = [(-1, 0), (-0.7, 0.75), (0, 1), (0.7, 0.75), (1, 0)]
    aneis = []
    for s, esc in ((0.0, 1.0), (0.6, 0.78)):
        c = eixo(s); aneis.append([bm.verts.new(c + b * w * esc * a + n * w * 0.5 * esc * h) for a, h in perfil])
    c = eixo(1.0)                                                       # ponta romba: 3 pontos baixos
    ponta = [bm.verts.new(c + b * w * 0.32), bm.verts.new(c + n * w * 0.12), bm.verts.new(c - b * w * 0.32)]
    us = [u0, u0 + (um - u0) * 0.5, um, um + (u1 - um) * 0.5, u1]
    for k in range(4):
        f = bm.faces.new((aneis[0][k], aneis[0][k + 1], aneis[1][k + 1], aneis[1][k]))
        if uvl is not None:
            for lp, uv in zip(f.loops, ((us[k], 0), (us[k + 1], 0), (us[k + 1], 0.6), (us[k], 0.6))): lp[uvl].uv = uv
    liga = ((0, 1, 0), (1, 2, 1), (2, 3, 1), (3, 4, 2))                # anel do meio -> ponta romba
    for k0, k1, j in liga:
        f = bm.faces.new((aneis[1][k0], aneis[1][k1], ponta[j]))
        if uvl is not None:
            for lp, uv in zip(f.loops, ((us[k0], 0.6), (us[k1], 0.6), (us[j * 2], 1.0))): lp[uvl].uv = uv
    for k, j in ((1, 0), (3, 1)):                                       # fecha os vaos entre a ponta e o anel
        f = bm.faces.new((aneis[1][k], ponta[j + 1], ponta[j]))
        if uvl is not None:
            for lp, uv in zip(f.loops, ((us[k], 0.6), (us[(j + 1) * 2], 1.0), (us[j * 2], 1.0))): lp[uvl].uv = uv

def tufo(bm, uvl, p, n, d, L, w, elev, col, fios, rnd):
    w *= 0.75                                                        # fios mais finos (le como pelo, nao como lamina)
    u0, u1 = col / NC + 0.02, (col + 1) / NC - 0.02
    for i in range(fios):
        ang = (i - (fios - 1) / 2) * 7 + rnd.uniform(-3, 3)                # leque fechado: mecha unida
        di = Matrix.Rotation(math.radians(ang), 3, n) @ d
        Li = L * (1.0 if i == (fios - 1) // 2 else rnd.uniform(0.7, 0.9))
        b = n.cross(di).normalized()
        mecha(bm, uvl, p + b * (i - (fios - 1) / 2) * w * 0.6, n, di, Li, w, elev, u0, u1)


def samambaia(bm, uvl, p, n, d, L):
    """Fronde de samambaia: raque + foliolos alternados (triangulos), dupla face, ~44 tris."""
    b = n.cross(d).normalized()
    for lado in (1, -1):
        off = -n * (0.0 if lado > 0 else 0.01)
        base = [p + n * 0.04 + off + d * L * s + n * L * 0.18 * math.sin(math.pi * s) for s in (0, 0.25, 0.5, 0.75, 1.0)]
        vs = [bm.verts.new(q) for q in base]
        for k in range(4):
            s = (k + 0.5) / 4; larg = L * 0.32 * (1 - s * 0.7)
            for sg in (1, -1):
                pt = bm.verts.new((vs[k].co + vs[k + 1].co) / 2 + b * sg * larg + d * larg * 0.4)
                t = (vs[k], vs[k + 1], pt) if sg * lado > 0 else (vs[k + 1], vs[k], pt)
                f = bm.faces.new(t)
                for lp in f.loops: lp[uvl].uv = (0.9 if lp.vert is not pt else 0.83, (1 + s * 0.9) / 3)


def folha_real(bm, uvl, p, n, d, L, w, banda, rnd):
    """Folha: peciolo enfiado no pelo, limbo oval de ponta aguda dobrado na nervura (V) e curvado; dupla face, 24 tris."""
    b = n.cross(d).normalized()
    curva = rnd.uniform(0.1, 0.25); tor = rnd.uniform(-0.3, 0.3)
    def eixo(s): return p - n * 0.02 + d * L * s + n * L * (0.12 + curva * math.sin(math.pi * s * 0.9))
    S = (0.12, 0.4, 0.75, 1.0); W = (0.12, 1.0, 0.75, 0.0)
    v0 = 1 / 3 * banda
    for lado in (1, -1):
        off = -n * (0.0 if lado > 0 else 0.008)
        mid = [bm.verts.new(eixo(s) + off) for s in S]
        ed = {sg: [bm.verts.new(eixo(s) + off + b * sg * w * ww * (1 + tor * sg) - n * w * ww * 0.25) for s, ww in zip(S, W)] for sg in (1, -1)}
        for sg in (1, -1):
            for k in range(3):
                quad = (mid[k], mid[k + 1], ed[sg][k + 1], ed[sg][k])
                if sg * lado < 0: quad = quad[::-1]
                f = bm.faces.new(quad)
                for lp in f.loops:
                    i = (mid + ed[sg]).index(lp.vert) if lp.vert in mid + ed[sg] else 0
                    kk = i % 4; borda = lp.vert not in mid
                    lp[uvl].uv = (0.9 + (0.085 * sg if borda else 0), v0 + (0.05 + 0.27 * S[kk]))
    pec = bm.verts.new(p - n * 0.06)                                   # peciolo
    m0 = bm.verts.new(eixo(S[0]) + n * 0.005); m1 = bm.verts.new(eixo(S[0]) + b * 0.012)
    f = bm.faces.new((pec, m1, m0))
    for lp in f.loops: lp[uvl].uv = (0.9, v0 + 0.03)


def orelha(bm, uvl, s, rnd):
    base, topo = Vector(H((s * 0.3, -3.52, 8.6))), Vector(H((s * 0.45, -3.6, 9.28)))
    eixo = (topo - base).normalized()
    fr = Vector((0, -1, 0)); fr = (fr - eixo * fr.dot(eixo)).normalized(); la = eixo.cross(fr).normalized()
    def anel(c, ry, rx, conc):
        out = []
        for k in range(8):
            a = 2 * math.pi * k / 8
            off = la * math.cos(a) * ry + fr * math.sin(a) * rx
            if math.sin(a) > 0.3: off -= fr * conc
            out.append((bm.verts.new(c + off), math.sin(a) > 0.3))
        return out
    A = anel(base, 0.27, 0.09, 0.0); B = anel(base.lerp(topo, 0.5), 0.17, 0.06, 0.06); tip = bm.verts.new(topo)
    for k in range(8):
        frente = A[k][1] and A[(k + 1) % 8][1]
        uu = 0.5 if frente else 0.1
        f = bm.faces.new((A[k][0], A[(k + 1) % 8][0], B[(k + 1) % 8][0], B[k][0]))
        for lp, vv in zip(f.loops, (0.1, 0.1, 0.5, 0.5)): lp[uvl].uv = (uu, vv)
        f = bm.faces.new((B[k][0], B[(k + 1) % 8][0], tip))
        for lp, vv in zip(f.loops, (0.5, 0.5, 0.95)): lp[uvl].uv = (0.3, vv)


CARTOES = True                                                     # pelo em cartoes com transparencia (sobre o subpelo)
CORES_CARTAO = [(0.13, 0.125, 0.115), (0.21, 0.205, 0.19)]          # cor principal e clara (Cinza da Floresta)


def atlas_cartoes(nome):
    """Atlas 1024x1024 com transparencia: 4 variantes de tufo (colunas) x 2 cores (linhas). Cada tufo tem ~55 fios
    finos que nascem juntos na raiz, curvam e afinam ate a ponta (alpha recorta a forma do tufo)."""
    rng = np.random.default_rng(13)
    W_, H_ = 1024, 1024; cw, rh = 256, 512
    img = np.zeros((H_, W_, 4))
    yy, xx = np.mgrid[-3:4, -3:4]
    for linha, base in enumerate(CORES_CARTAO):
        for col in range(4):
            A = np.zeros((rh, cw)); C = np.zeros((rh, cw, 3))
            for _ in range(110 + col * 15):
                u0 = np.clip(rng.normal(cw / 2, 30), 20, cw - 20); Lr = rng.uniform(0.5, 0.97) * rh
                curva = rng.uniform(-45, 45); tom = rng.uniform(0.7, 1.3)
                t = np.linspace(0, 1, 90)
                px = u0 + curva * t ** 2 + (t * (u0 - cw / 2) * 0.6); py = 6 + t * Lr
                larg = 3.4 * (1 - t) + 0.8
                for x, y, lw, tt in zip(px, py, larg, t):
                    xi, yi = int(x), int(y)
                    if not (3 <= xi < cw - 3 and 3 <= yi < rh - 3): continue
                    g = np.exp(-(xx ** 2 + yy ** 2) / (2 * (lw * 0.6) ** 2))
                    A[yi - 3:yi + 4, xi - 3:xi + 4] = np.maximum(A[yi - 3:yi + 4, xi - 3:xi + 4], g)
                    cor = np.array(base) * tom * (0.75 + 0.45 * tt)
                    msk = g > 0.3
                    C[yi - 3:yi + 4, xi - 3:xi + 4][msk] = cor
            A[:int(rh * 0.06), :] *= np.linspace(0.6, 1, int(rh * 0.06))[:, None]
            y0, x0 = linha * rh, col * cw
            img[y0:y0 + rh, x0:x0 + cw, :3] = np.clip(C, 0, 1) ** (1 / 2.2)
            img[y0:y0 + rh, x0:x0 + cw, 3] = np.clip(A, 0, 1)
    im = bpy.data.images.new(nome, W_, H_, alpha=True)
    im.pixels.foreach_set(img.astype(np.float32).ravel()); im.pack()
    return im


def cartao(bm, uvl, p, n, d, L, W, elev, linha, rnd):
    """Cartao de pelo: faixa levemente curva e afilada, deitada no sentido do pelo; a textura com alpha da a forma
    do tufo. 4 triangulos."""
    b = n.cross(d).normalized(); e = elev * 0.6
    col = rnd.randrange(4); u0, u1 = col * 0.25 + 0.005, (col + 1) * 0.25 - 0.005; v0 = linha * 0.5
    def eixo(s): return p - n * 0.03 + d * L * s + n * (L * (e * s - e * 0.5 * s * s) + 0.02 * s)
    lin = []
    for s in (0.0, 0.5, 1.0):
        c = eixo(s); hw = W * 0.5 * (1 - 0.25 * s)
        lin.append((bm.verts.new(c + b * hw), bm.verts.new(c - b * hw), s))
    for (a0, a1, s0), (b0, b1, s1) in zip(lin, lin[1:]):
        f = bm.faces.new((a0, a1, b1, b0))
        for lp, uv in zip(f.loops, ((u0, v0 + s0 * 0.5), (u1, v0 + s0 * 0.5), (u1, v0 + s1 * 0.5), (u0, v0 + s1 * 0.5))):
            lp[uvl].uv = uv


def pelagem(corpo, col, semente=11):
    rnd = random.Random(semente)
    cands = [(Vector(v.co), Vector(v.normal)) for v in corpo.data.vertices]
    rnd.shuffle(cands)
    bms = {}                                                         # MeshParts: frente, tras e pernas (cada um < 20 mil tris)
    def bm_de(p):
        k = "Pernas" if (p.z < 3.3 and not (p.y > 2.1 and _cauda(Vector(p))[0] < 0.75)) else ("Pescoco" if p.y < -2.2 else ("Tronco" if p.y < 1.0 else "Tras"))
        if k not in bms:
            b = bmesh.new(); bms[k] = (b, b.loops.layers.uv.new("UVMap"))
        return bms[k]
    cont = {k: 0 for k in REG}; pos = {k: [] for k in REG}
    for p, n in cands:
        bm, uvl = bm_de(p)
        r = regiao(p, n)
        if not r: continue
        fluxo, (L0, L1), w, elev, esp, nf = REG[r]
        if r == "cabeca" and not CARTOES: continue
        fat = (0.6 if r not in ("perna",) else 0.7) if CARTOES else (1.3 if r not in ("perna",) else 1.7)
        if pos[r] and min((p - q).length for q in pos[r]) < esp * fat: continue
        pos[r].append(p)
        L = rnd.uniform(L0, L1) * 1.05; ww = w * rnd.uniform(0.85, 1.15) * (1.35 if r in CASCA else 1.0) * 1.7; tt = 0.0
        if r == "cauda":
            _, tg, tt = _cauda(p)
            f = tg + Vector((0, 0, -0.15))
            L = (0.5 + 0.55 * math.sin(math.pi * min(1.0, 0.12 + tt * 0.85))) * rnd.uniform(0.9, 1.1)
        elif r == "bochecha":                                          # colar facial: emoldura o rosto, para fora e para tras
            f = Vector((math.copysign(0.6, p.x), 1, -0.5)); L *= 1.3
        elif r == "colar" and p.z > 6.6:                               # nuca: curto e para baixo (sem crista)
            f = Vector((0, 0.4, -1)); L *= 0.5
        else:
            f = Vector(fluxo)
        d = f - n * f.dot(n)
        if d.length < 1e-3: d = Vector((0, 1, 0)) - n * n.y
        d.normalize()
        d = Matrix.Rotation(math.radians(rnd.uniform(-18, 18)), 3, n) @ d
        if d.z > 0.1 and r != "cauda":                                   # pelo nunca cresce para cima
            d.z = 0.1; d = d - n * d.dot(n)
            if d.length < 1e-3: continue
            d.normalize()
        x = rnd.random(); colr = 0
        if r == "cauda" and tt > 0.8: colr = 1
        elif r in ("dorso", "ombro", "colar") and p.z > 5.2 and x < 0.16: colr = 3          # mechas com musgo
        elif r in ("dorso", "cauda", "cabeca", "flanco") and x < 0.35: colr = 1
        elif r in ("ventre", "peito", "bochecha") or (r == "colar" and p.z < 5.4): colr = 2 if x < 0.5 else 0
        elif r in ("antebraco", "canela"): colr = 2 if x < 0.3 else 0          # pernas: claro raro (sem espetos brancos)
        if CARTOES:
            cartao(bm, uvl, p, n, d, L, ww * (4.6 if r != "cabeca" else 3.6), elev, 1 if colr == 2 else 0, rnd)
        else:
            tufo(bm, uvl, p, n, d, L, ww, elev, colr, nf, rnd)
        cont[r] += 1
    fb = bmesh.new(); folhas = (fb, fb.loops.layers.uv.new("UVMap"))   # folhas e orelhas: objeto opaco separado
    nf = 0; nfol = 0; centros = []                                   # guardiao da floresta: tufos de vegetacao na pelagem
    pesos = {"dorso": 1.0, "colar": 0.9, "ombro": 0.7, "coxa": 0.7, "cauda": 0.35, "flanco": 0.35, "perna": 0.25, "cabeca": 0.15, "peito": 0.2}
    for p, n in cands:
        if len(centros) >= 24: break
        r = regiao(p, n)
        if r not in pesos or rnd.random() > pesos[r] * 0.08: continue
        if (r == "cabeca" and local_cabeca(p).y < -4.0) or any((p - c).length < 1.0 for c, _ in centros): continue
        centros.append((p, r))
    pts = [(p, n) for p, n in cands]
    for c, r in centros:
        viz = [(p, n) for p, n in pts if (p - c).length < 0.55]
        rnd.shuffle(viz)
        nfo = rnd.randint(5, 9) if r not in ("perna", "cabeca") else rnd.randint(2, 4)
        for i, (p, n) in enumerate(viz[:nfo + 1]):
            f = fluxo_geral(p, n); d = f - n * f.dot(n)
            if d.length < 1e-3: continue
            d = Matrix.Rotation(math.radians(rnd.uniform(-70, 70)), 3, n) @ d.normalized()
            bm, uvl = folhas
            if i == 0 and r in ("dorso", "colar", "coxa", "ombro") and nf < 18:
                samambaia(bm, uvl, p, n, d, rnd.uniform(0.6, 0.9)); nf += 1
            else:
                esc = 0.7 if r in ("perna", "cabeca") else 1.0
                folha_real(bm, uvl, p, n, d, rnd.uniform(0.36, 0.55) * esc, rnd.uniform(0.13, 0.2) * esc, rnd.choice((0, 0, 1, 1, 2)), rnd); nfol += 1
    bm, uvl = folhas
    for s in (1, -1): orelha(bm, uvl, s, rnd)
    matf = bpy.data.materials.new("MAT_Lobo_Ancestral_Folhagem")
    ntf = matf.node_tree; bf = next(x for x in ntf.nodes if x.type == "BSDF_PRINCIPLED")
    txf = ntf.nodes.new("ShaderNodeTexImage"); txf.image = atlas()
    ntf.links.new(txf.outputs["Color"], bf.inputs["Base Color"]); bf.inputs["Roughness"].default_value = 0.8
    mat = bpy.data.materials.new("MAT_Lobo_Ancestral_Pelagem")
    nt = mat.node_tree; bsdf = next(x for x in nt.nodes if x.type == "BSDF_PRINCIPLED")
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = atlas_cartoes("Lobo_Ancestral_Pelagem_Cartoes") if CARTOES else atlas()
    nt.links.new(tx.outputs["Color"], bsdf.inputs["Base Color"])
    if CARTOES:
        nt.links.new(tx.outputs["Alpha"], bsdf.inputs["Alpha"])
        if hasattr(mat, "surface_render_method"): mat.surface_render_method = "DITHERED"
        mat.use_backface_culling = False
    bsdf.inputs["Roughness"].default_value = 0.95
    if "Specular IOR Level" in bsdf.inputs: bsdf.inputs["Specular IOR Level"].default_value = 0.25
    tris = {}
    bms["Folhas"] = folhas
    for k, (bm, uvl) in bms.items():
        m = bpy.data.meshes.new("Lobo_Ancestral_Pelagem" + k); bm.to_mesh(m); bm.free()
        for pl in m.polygons: pl.use_smooth = True
        ob = bpy.data.objects.new("Lobo_Ancestral_Pelagem" + k, m); col.objects.link(ob)
        m.materials.append(matf if k == "Folhas" else mat)
        ob["papel_material"] = "pelagem"
        tris[k] = ob["tris"] = sum(len(pl.vertices) - 2 for pl in m.polygons)
    print("TUFOS", cont, "SAMAMBAIAS", nf, "FOLHAS", nfol, "TRIS", tris)
    return {"tris": sum(tris.values()), "tufos": cont}


# ------------------------------------------------------------------ FIOS DE ALTA (so para assar normal/oclusao)
def fluxo_geral(p, n):
    q = local_cabeca(p)
    if q is not None:
        return Vector((math.copysign(0.3, p.x), 1, 0.05)) if q.y < -3.9 else Vector((0, 1, -0.2))
    if p.y > 2.1 and p.z < 5.2 and _cauda(p)[0] < 0.75:
        return _cauda(p)[1]
    if p.z < 3.2: return Vector((0, 0.15, -1))                      # pernas: para baixo
    if p.y < -1.6: return Vector((0, 0.5, -1))                      # pescoco/peito
    return Vector((0, 1, -0.35))                                    # tronco: para tras e para baixo


def fios_alta(corpo, n_fios=26000, semente=5):
    """Malha de alta (copia do corpo + milhares de fios finos deitados no sentido do pelo) para assar no corpo."""
    rnd = random.Random(semente)
    me = corpo.data; M = corpo.matrix_world
    polys = list(me.polygons); areas = np.array([p.area for p in polys]); acc = np.cumsum(areas) / areas.sum()
    bm = bmesh.new(); bm.from_mesh(me)
    nr = np.random.default_rng(semente)
    for idx in np.searchsorted(acc, nr.random(n_fios)):
        pl = polys[min(idx, len(polys) - 1)]
        vs = [me.vertices[i].co for i in pl.vertices[:3]]
        a, b = sorted((rnd.random(), rnd.random()))
        p = M @ (vs[0] * a + vs[1] * (b - a) + vs[2] * (1 - b)); n = (M.to_3x3() @ pl.normal).normalized()
        q = local_cabeca(p)
        if p.z < 0.3 or q is not None:
            continue                                                 # sem fios assados na cabeca (viram manchas) e almofadas
        f = fluxo_geral(p, n); d = f - n * f.dot(n)
        if d.length < 1e-3: continue
        d.normalize(); d = Matrix.Rotation(math.radians(rnd.uniform(-20, 20)), 3, n) @ d
        curto = q is not None or p.z < 2.6
        L = rnd.uniform(0.07, 0.12) if curto else rnd.uniform(0.14, 0.26)
        fio(bm, None, p + n * 0.065, n, d, L, 0.028 if curto else 0.036, 0.12, 0, 0)    # acima da pele: o raio do bake encontra o fio
    m = bpy.data.meshes.new("_FiosAlta"); bm.to_mesh(m); bm.free()
    ob = bpy.data.objects.new("_FiosAlta", m); bpy.context.scene.collection.objects.link(ob)
    return ob


if __name__ == "__main__":
    from blockout_lib import salvar, RAIZ
    construir()
    salvar(os.path.join(RAIZ, "Lobo_Ancestral", "Lobo_Ancestral_refinado_v5.blend"))
