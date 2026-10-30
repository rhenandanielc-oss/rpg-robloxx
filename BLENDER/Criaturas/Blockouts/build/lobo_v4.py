# Lobo Ancestral V4 (27/10/2026): ajustes localizados sobre a V3 aprovada como base (lobo_v3.py preservado).
# 1) pescoco mais curto e menos vertical (cabeca desce DH, rig junto); 2) pelagem em tufos organicos de 3 pontas,
# direcionados pelo crescimento do pelo (no lugar das placas/folhas); 3) flanco e prega do joelho ligando peito,
# abdomen e quadril; 4) rosto: masseter/focinho mais finos, trufa, mandibula, olhos mais fundos; 5) cauda em pincel
# volumoso (mais larga no meio, ponta escura). Referencias: painel oficial GitHub + silhueta do usuario.
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix

DH = Vector((0, -0.12, -0.7))                     # deslocamento da cabeca em relacao a V3
_h = lambda p: tuple(Vector(p) + DH)

J = {
    "pelve": (0, 1.6, 5.0), "peito": (0, -1.6, 5.6),
    "pescoco": [(0, -2.3, 5.85), (0, -3.0, 6.6), (0, -3.57, 7.3)],
    "focinho": _h((0, -5.05, 8.05)), "mand": (_h((0, -3.7, 7.82)), _h((0, -4.9, 7.82))),
    "cauda": [(0, 2.2, 5.1), (0, 2.75, 4.55), (0, 3.25, 3.7), (0, 3.75, 2.8), (0, 4.25, 1.9), (0, 4.65, 1.05)],
    "frente": [(0.52, -1.55, 6.2), (0.62, -2.55, 4.7), (0.6, -2.0, 3.35), (0.55, -2.25, 1.0), (0.53, -2.4, 0.3), (0.52, -2.9, 0.12)],
    "tras": [(0.55, 1.55, 4.9), (0.6, 0.75, 3.3), (0.52, 2.05, 1.4), (0.5, 1.8, 0.3), (0.5, 1.3, 0.12)],
}


def local_cabeca(p):
    """Coordenada no referencial da cabeca da V3 (para regioes de pelo e mascara); None fora da cabeca."""
    q = Vector(p) - DH
    return q if (q.y < -3.2 and q.z > 7.3) else None


def construir():
    from blockout_lib import (cena_nova, colecao, Partes, elipsoide, cadeia, trilha, massa, fundir, juntar,
                              material_papel, pata_digitigrada, humano, medidas)
    cena_nova()
    col = colecao("Lobo_Ancestral")
    rg = Partes()
    mole = bmesh.new()                                                   # camada 1: massas (suavizacao forte)
    elipsoide(mole, (0, -1.5, 4.85), (0.76, 1.75, 1.52))                 # torax fundo e estreito
    elipsoide(mole, (0, -2.8, 4.75), (0.52, 0.62, 0.95))                 # peito (manubrio)
    elipsoide(mole, (0, -0.45, 4.5), (0.64, 1.1, 0.92))                  # transicao torax -> abdomen
    elipsoide(mole, (0, 0.75, 4.62), (0.6, 1.05, 0.72))                  # flanco: abdomen -> quadril sem degrau
    elipsoide(mole, (0, 0.4, 5.22), (0.58, 1.3, 0.74))                   # lombo (barriga recolhida)
    elipsoide(mole, (0, 1.6, 5.12), (0.66, 0.95, 0.84))                  # garupa
    for s in (1, -1):
        elipsoide(mole, (s * 0.46, -1.7, 5.6), (0.24, 0.72, 0.85), rot=(-30, 0, 0))    # escapula (achatada)
        elipsoide(mole, (s * 0.48, 1.0, 3.95), (0.24, 0.5, 0.42))                       # prega do joelho (flanco -> coxa)
    trilha(mole, [(0, -1.95, 5.5, 0.92), (0, -2.7, 6.3, 0.76), (0, -3.3, 6.95, 0.62), (0, -3.55, 7.35, 0.52)],
           achatar=(0.82, 1.0), passo=0.2, u=20, v=10)                    # pescoco (~45 graus, mais curto)
    elipsoide(mole, (0, -3.0, 5.95), (0.5, 0.6, 0.68))                   # garganta
    cab = bmesh.new()                                                    # cabeca no referencial da V3, deslocada por DH
    elipsoide(cab, (0, -3.72, 8.35), (0.47, 0.58, 0.47))
    elipsoide(cab, (0, -3.32, 8.38), (0.38, 0.35, 0.4))                  # occipital
    trilha(cab, [(0, -4.15, 8.24, 0.28), (0, -4.6, 8.12, 0.21), (0, -4.96, 8.03, 0.13)], achatar=(0.72, 0.86), passo=0.08, u=16, v=8)
    trilha(cab, [(0, -3.75, 7.83, 0.19), (0, -4.4, 7.83, 0.12), (0, -4.8, 7.86, 0.08)], achatar=(1.0, 0.75), passo=0.08, u=16, v=8)
    for s in (1, -1):
        elipsoide(cab, (s * 0.12, -4.45, 7.98), (0.09, 0.42, 0.11))      # maxila / labio superior
        elipsoide(cab, (s * 0.3, -3.8, 8.0), (0.16, 0.3, 0.22))          # masseter (mais estreito)
        elipsoide(cab, (s * 0.42, -3.85, 8.22), (0.12, 0.32, 0.12))      # arco zigomatico
    bmesh.ops.translate(cab, vec=DH, verts=cab.verts); juntar(mole, cab)
    F, T = J["frente"], J["tras"]
    for s in (1, -1):
        X = lambda p: (s * p[0], p[1], p[2])
        cadeia(mole, [X(F[0]) + (0.36,), X(F[1]) + (0.33,), X(F[2]) + (0.29,), X(F[3]) + (0.2,), (s * 0.53, -2.42, 0.38, 0.17)], seg=18)
        elipsoide(mole, X((0.6, -2.12, 4.1)), (0.27, 0.4, 0.6), rot=(25, 0, 0))       # triceps
        elipsoide(mole, X((0.62, -2.55, 3.95)), (0.2, 0.22, 0.48))                     # braquial
        elipsoide(mole, X((0.57, -2.12, 2.6)), (0.25, 0.27, 0.62), rot=(-6, 0, 0))     # flexores do antebraco
        cadeia(mole, [X(T[0]) + (0.42,), X(T[1]) + (0.29,), X(T[2]) + (0.17,), (s * 0.5, 1.82, 0.36, 0.16)], seg=18)
        elipsoide(mole, X((0.58, 1.15, 4.05)), (0.34, 0.76, 0.98), rot=(-27, 0, 0))   # quadriceps / coxa (menos esferica)
        elipsoide(mole, X((0.54, 2.0, 3.95)), (0.28, 0.44, 0.92), rot=(-25, 0, 0))   # isquiotibiais
        elipsoide(mole, X((0.55, 1.25, 2.8)), (0.18, 0.24, 0.6), rot=(35, 0, 0))     # gastrocnemio
    cadeia(mole, [(0, 2.2, 5.1, 0.33), (0, 2.75, 4.55, 0.42), (0, 3.25, 3.7, 0.48), (0, 3.75, 2.8, 0.45),
                  (0, 4.25, 1.9, 0.34), (0, 4.62, 1.15, 0.16)], seg=18)        # cauda: mais cheia no meio
    estr = massa(mole, voxel=0.045, suav_iter=6, suav_fator=0.5, laplace=12)
    det = bmesh.new()                                                    # camada 2 da cabeca (referencial V3)
    for s in (1, -1):
        elipsoide(estr, (s * 0.5, -1.62, 5.95), (0.1, 0.6, 0.09), rot=(-30, 0, 0))    # espinha da escapula
        elipsoide(estr, (s * 0.6, -1.92, 3.35), (0.15, 0.17, 0.16))                    # olecrano
        elipsoide(estr, (s * 0.45, 1.65, 5.6), (0.2, 0.42, 0.16))                      # crista iliaca
        elipsoide(estr, (s * 0.55, 2.25, 4.4), (0.16, 0.2, 0.16))                      # tuberosidade isquiatica
        elipsoide(estr, (s * 0.55, -2.25, 1.0), (0.17, 0.18, 0.16))                    # carpo
        elipsoide(estr, (s * 0.52, 2.12, 1.45), (0.09, 0.12, 0.13))                    # calcaneo (jarrete)
        elipsoide(det, (s * 0.24, -4.12, 8.55), (0.15, 0.2, 0.075), rot=(14, 0, s * -18))   # arcada
        elipsoide(det, (s * 0.1, -4.02, 8.64), (0.08, 0.18, 0.055))                   # testa franzida
        pata_digitigrada(estr, rg("garra"), (s * 0.53, -2.58, 0.0), s, 0.36, 0.66, dedos=4, garra_comp=0.12)
        pata_digitigrada(estr, rg("garra"), (s * 0.5, 1.63, 0.0), s, 0.33, 0.6, dedos=4, garra_comp=0.11)
    elipsoide(det, (0, -5.0, 8.07), (0.1, 0.07, 0.08))                   # trufa
    elipsoide(det, (0, -4.1, 8.48), (0.15, 0.24, 0.075))                  # stop
    bmesh.ops.translate(det, vec=DH, verts=det.verts); juntar(estr, det)
    olho = bmesh.new()
    for s in (1, -1):                                                    # olhos amendoados, mais fundos sob a arcada
        elipsoide(olho, (s * 0.245, -4.19, 8.42), (0.042, 0.076, 0.04), rot=(19, 0, s * -25), u=14, v=7)
    bmesh.ops.translate(olho, vec=DH, verts=olho.verts); juntar(rg("olho"), olho)
    corpo = fundir("Lobo_Ancestral_Corpo_Blockout", estr, col, voxel=0.04, suav_iter=5, suav_fator=0.5, tris=12000)
    material_papel(corpo, "pelo")
    rg.criar("Lobo_Ancestral", col)
    pel = pelagem(corpo, col)
    humano(-5.0, -9.0)
    md = medidas(col)
    print("MEDIDAS", md, "PELAGEM_TRIS", pel["tris"])
    return col


# ------------------------------------------------------------------ PELAGEM
CORES_ATLAS = [(0.19, 0.165, 0.12), (0.1, 0.088, 0.07), (0.34, 0.29, 0.21), (0.12, 0.15, 0.06)]   # base (= corpo), escura, creme, musgo


def atlas():
    """Atlas 512x256, 4 colunas; fios finos ao longo da mecha, ponta levemente mais escura (aguti)."""
    W_, H_ = 512, 256
    rng = np.random.default_rng(7)
    u = np.arange(W_)[None, :].repeat(H_, 0); v = np.arange(H_)[:, None].repeat(W_, 1) / (H_ - 1)
    fio = np.interp(u.ravel() + 3 * np.sin(v.ravel() * 9), np.arange(W_), 0.84 + 0.32 * rng.random(W_)).reshape(H_, W_)
    grad = 1.0 - 0.2 * v ** 1.5
    img = np.zeros((H_, W_, 4)); img[..., 3] = 1
    for c, cor in enumerate(CORES_ATLAS):
        sl = slice(c * 128, (c + 1) * 128)
        for k in range(3):
            img[:, sl, k] = np.clip(cor[k] * grad[:, sl] * fio[:, sl], 0, 1) ** (1 / 2.2)
    im = bpy.data.images.new("Lobo_Ancestral_Pelagem_Atlas", W_, H_, alpha=False)
    im.pixels.foreach_set(img.astype(np.float32).ravel()); im.pack()
    return im


def regiao(p, n):
    x, y, z = p
    q = local_cabeca(p)
    if q is not None:
        if -4.0 < q.y < -3.05 and q.z > 8.45 and n.z > 0.2: return "cabeca"
        if -3.9 < q.y and q.z < 8.3 and abs(x) > 0.27: return "bochecha"
        return None
    if 1.5 < z < 3.3 and -2.6 < y < -1.5 and abs(x) > 0.3 and n.y > 0.35:
        return "antebraco"
    if y > 2.1 and z < 5.15 and _cauda(Vector(p))[0] < 0.7:
        return "cauda"
    if z < 2.7:
        return None
    if y < -1.55 and z > 4.1:
        return "colar"
    if y < -1.0 and z < 4.1 and abs(x) < 0.45:
        return "peito"
    if z > 5.45:
        return "dorso"
    if z < 3.95 and -1.6 < y < 0.9 and abs(x) < 0.6:
        return "ventre"
    if y > 1.5 and 2.9 < z < 4.7 and abs(x) > 0.3:
        return "coxa"
    return None


#            fluxo (crescimento)  comp (min,max)  larg  elev  espaco
REG = {"colar": ((0, 0.55, -1), (0.6, 0.9), 0.075, 0.32, 0.165), "peito": ((0, 0.25, -1), (0.5, 0.68), 0.07, 0.25, 0.16),
       "bochecha": (None, (0.36, 0.5), 0.06, 0.25, 0.1), "cabeca": ((0, 1, 0.1), (0.2, 0.28), 0.045, 0.12, 0.11),
       "dorso": ((0, 1, -0.2), (0.4, 0.55), 0.065, 0.16, 0.21), "ventre": ((0, 0.2, -1), (0.32, 0.45), 0.06, 0.22, 0.18),
       "coxa": ((0, 0.45, -1), (0.32, 0.45), 0.06, 0.18, 0.18), "cauda": (None, (0.5, 1.0), 0.085, 0.3, 0.135),
       "antebraco": ((0, 0.6, -1), (0.3, 0.4), 0.055, 0.25, 0.14)}
FIOS = {"colar": 3, "cauda": 3, "bochecha": 3, "peito": 3}


def _cauda(p):
    """(distancia ao eixo da cauda, tangente rumo a ponta, posicao 0..1 ao longo da cauda)."""
    C = [Vector(c) for c in J["cauda"]]
    Ls = [(b - a).length for a, b in zip(C, C[1:])]; tot = sum(Ls)
    best = (1e9, None, 0.0); acc = 0.0
    for (a, b), L in zip(zip(C, C[1:]), Ls):
        ab = b - a; t = max(0, min(1, (p - a).dot(ab) / ab.length_squared)); dd = (p - (a + ab * t)).length
        if dd < best[0]: best = (dd, ab.normalized(), (acc + t * L) / tot)
        acc += L
    return best


def tufo(bm, uvl, p, n, d, L, w, elev, col, fios=3, rnd=None):
    """Tufo organico: 2-3 fios finos e pontiagudos saindo da mesma raiz, abrindo em leque e curvando com o
    crescimento do pelo (le como mecha, nao como placa). Cada fio: secao em V, 6 triangulos."""
    rnd = rnd or random
    u0, u1 = col * 0.25 + 0.03, (col + 1) * 0.25 - 0.03; um = (u0 + u1) / 2
    for i in range(fios):
        ang = (i - (fios - 1) / 2) * 13 + rnd.uniform(-5, 5)
        di = Matrix.Rotation(math.radians(ang), 3, n) @ d
        Li = L * (1.0 if i == (fios - 1) // 2 else rnd.uniform(0.7, 0.9))
        b = n.cross(di).normalized()
        pi = p + b * (i - (fios - 1) / 2) * w * 0.5
        def eixo(s): return pi - n * 0.05 + di * Li * s + n * Li * (elev * s - elev * 0.7 * s * s)
        c0, c1 = eixo(0.0), eixo(0.5)
        r0 = [bm.verts.new(c0 + b * w * 0.5), bm.verts.new(c0 + n * w * 0.45), bm.verts.new(c0 - b * w * 0.5)]
        r1 = [bm.verts.new(c1 + b * w * 0.32), bm.verts.new(c1 + n * w * 0.3), bm.verts.new(c1 - b * w * 0.32)]
        tp = bm.verts.new(eixo(1.0))
        UV = {r0[0]: (u0, 0), r0[1]: (um, 0), r0[2]: (u1, 0), r1[0]: (u0, 0.5), r1[1]: (um, 0.5), r1[2]: (u1, 0.5), tp: (um, 1.0)}
        for fv in ((r0[0], r0[1], r1[1], r1[0]), (r0[1], r0[2], r1[2], r1[1]), (r1[0], r1[1], tp), (r1[1], r1[2], tp)):
            f = bm.faces.new(fv)
            for lp in f.loops: lp[uvl].uv = UV[lp.vert]

def folha(bm, uvl, p, n, d, L, w):
    b = n.cross(d).normalized(); c = p + n * 0.05
    pts = [c, c + d * L * 0.45 + b * w + n * 0.03, c + d * L, c + d * L * 0.45 - b * w + n * 0.03, c + d * L * 0.5 + n * 0.06]
    for lado in (1, -1):
        vs = [bm.verts.new(q - n * (0 if lado > 0 else 0.012)) for q in pts]
        uvs = {0: (0.79, 0.15), 1: (0.76, 0.5), 2: (0.79, 0.9), 3: (0.82, 0.5), 4: (0.79, 0.5)}
        for t in ((0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)):
            t = t if lado > 0 else t[::-1]
            f = bm.faces.new([vs[i] for i in t])
            for lp, i in zip(f.loops, t): lp[uvl].uv = uvs[i]


def orelha(bm, uvl, s):
    """Orelha triangular ereta, concha anterior em creme, dorso e ponta escuros."""
    base, topo = Vector((s * 0.29, -3.52, 8.6)) + DH, Vector((s * 0.43, -3.6, 9.25)) + DH
    eixo = (topo - base).normalized()
    fr = Vector((0, -1, 0)); fr = (fr - eixo * fr.dot(eixo)).normalized(); la = eixo.cross(fr).normalized()
    def anel(c, ry, rx, conc):
        out = []
        for k in range(6):
            a = 2 * math.pi * k / 6
            off = la * math.cos(a) * ry + fr * math.sin(a) * rx
            if math.sin(a) > 0.3: off -= fr * conc
            out.append((bm.verts.new(c + off), math.sin(a) > 0.3))
        return out
    A = anel(base, 0.25, 0.085, 0.0); B = anel(base.lerp(topo, 0.5), 0.15, 0.055, 0.05); tip = bm.verts.new(topo)
    for k in range(6):
        frente = A[k][1] and A[(k + 1) % 6][1]
        uu = 0.62 if frente else 0.3
        f = bm.faces.new((A[k][0], A[(k + 1) % 6][0], B[(k + 1) % 6][0], B[k][0]))
        for lp, vv in zip(f.loops, (0.1, 0.1, 0.5, 0.5)): lp[uvl].uv = (uu, vv)
        f = bm.faces.new((B[k][0], B[(k + 1) % 6][0], tip))
        for lp, vv in zip(f.loops, (0.5, 0.5, 0.95)): lp[uvl].uv = (0.37, vv)


def pelagem(corpo, col, semente=11):
    rnd = random.Random(semente)
    cands = [(Vector(v.co), Vector(v.normal)) for v in corpo.data.vertices]
    rnd.shuffle(cands)
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    cont = {k: 0 for k in REG}; pos = {k: [] for k in REG}
    for p, n in cands:
        r = regiao(p, n)
        if not r: continue
        fluxo, (L0, L1), w, elev, esp = REG[r]
        if pos[r] and min((p - q).length for q in pos[r]) < esp: continue
        pos[r].append(p)
        L = rnd.uniform(L0, L1); ww = w * rnd.uniform(0.85, 1.15); tt = 0.0
        if r == "cauda":                                              # pincel: curto na base, longo no meio, ponta fechada
            _, tg, tt = _cauda(p)
            f = tg + Vector((0, 0, -0.15))
            L = (0.45 + 0.55 * math.sin(math.pi * min(1.0, 0.12 + tt * 0.85))) * rnd.uniform(0.9, 1.1)
            if tt > 0.8: ww *= 0.8
        elif r == "bochecha":                                          # colar facial abre para fora e para tras
            f = Vector((math.copysign(0.4, p.x), 1, -0.4))
        else:
            f = Vector(fluxo)
        d = f - n * f.dot(n)
        if d.length < 1e-3: d = Vector((0, 1, 0)) - n * n.y
        d.normalize()
        d = Matrix.Rotation(math.radians(rnd.uniform(-18, 18)), 3, n) @ d
        x = rnd.random(); colr = 0
        if r == "cauda" and tt > 0.8: colr = 1                         # ponta da cauda escura
        elif r == "dorso" and x < 0.1: colr = 3
        elif r in ("dorso", "cauda", "cabeca") and x < 0.35: colr = 1
        elif r in ("ventre", "peito", "bochecha") or (r == "colar" and p.z < 5.4): colr = 2 if x < 0.75 else 0
        tufo(bm, uvl, p, n, d, L, ww, elev, colr, FIOS.get(r, 2), rnd)
        cont[r] += 1
    nf = 0
    for p, n in cands:                                               # poucas folhas de musgo, so na cernelha/dorso
        if nf >= 14: break
        if p.z > 5.75 and -1.6 < p.y < 1.0 and n.z > 0.5:
            d = Vector((rnd.uniform(-1, 1), rnd.uniform(-0.2, 1), 0)); d = (d - n * d.dot(n)).normalized()
            folha(bm, uvl, p, n, d, rnd.uniform(0.24, 0.32), rnd.uniform(0.08, 0.11)); nf += 1
    for s in (1, -1): orelha(bm, uvl, s)
    m = bpy.data.meshes.new("Lobo_Ancestral_Pelagem"); bm.to_mesh(m); bm.free()
    for pl in m.polygons: pl.use_smooth = True
    ob = bpy.data.objects.new("Lobo_Ancestral_Pelagem", m); col.objects.link(ob)
    mat = bpy.data.materials.new("MAT_Lobo_Ancestral_Pelagem")
    nt = mat.node_tree; bsdf = next(x for x in nt.nodes if x.type == "BSDF_PRINCIPLED")
    tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = atlas()
    nt.links.new(tx.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.95
    m.materials.append(mat)
    ob["papel_material"] = "pelagem"
    tris = sum(len(pl.vertices) - 2 for pl in m.polygons)
    ob["tris"] = tris
    print("TUFOS", cont, "FOLHAS", nf)
    return {"tris": tris, "tufos": cont}


if __name__ == "__main__":
    from blockout_lib import salvar, RAIZ
    construir()
    salvar(os.path.join(RAIZ, "Lobo_Ancestral", "Lobo_Ancestral_refinado_v4.blend"))
