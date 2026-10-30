# Lobo Ancestral V3 (27/10/2026): refinamento do modelo aprovado como base intermediaria.
# Referencias: painel oficial GitHub (REFERENCES/03_CREATURES/01-lobos-urso-leao.png: esguio, agil, pelagem com musgo)
# + silhueta de postura enviada pelo usuario (cabeca alta, pescoco subindo ~55 graus, torax fundo, barriga recolhida,
# traseiras sob o corpo, cauda espessa caida). Ombro (cernelha) 6,5 studs mantido (oficial 5,5-7).
# Corpo: massas anatomicas fundidas (como na V2), com peito/ombros menores e cabeca refeita.
# Pelagem: objeto separado com tufos de geometria (mechas deitadas e sobrepostas) + folhas de musgo, textura atlas unica.
# J = articulacoes compartilhadas com esqueletos.canideo_v3 (rig e malha alinhados).
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree

J = {
    "pelve": (0, 1.6, 5.0), "peito": (0, -1.6, 5.6),
    "pescoco": [(0, -2.3, 5.9), (0, -3.0, 7.0), (0, -3.45, 8.0)],
    "focinho": (0, -5.05, 8.05), "mand": ((0, -3.7, 7.82), (0, -4.9, 7.82)),
    "cauda": [(0, 2.2, 5.1), (0, 2.75, 4.55), (0, 3.25, 3.7), (0, 3.75, 2.8), (0, 4.25, 1.9), (0, 4.65, 1.05)],
    "frente": [(0.52, -1.55, 6.2), (0.62, -2.55, 4.7), (0.6, -2.0, 3.35), (0.55, -2.25, 1.0), (0.53, -2.4, 0.3), (0.52, -2.9, 0.12)],
    "tras": [(0.55, 1.55, 4.9), (0.6, 0.75, 3.3), (0.52, 2.05, 1.4), (0.5, 1.8, 0.3), (0.5, 1.3, 0.12)],
}


def construir():
    from blockout_lib import (cena_nova, colecao, Partes, elipsoide, cadeia, trilha, massa, fundir, juntar,
                              material_papel, pata_digitigrada, humano, medidas, olhos)
    cena_nova()
    col = colecao("Lobo_Ancestral")
    rg = Partes()
    mole = bmesh.new()                                                   # camada 1: massas (suavizacao forte)
    elipsoide(mole, (0, -1.5, 4.85), (0.76, 1.75, 1.52))                 # torax fundo e estreito
    elipsoide(mole, (0, -2.8, 4.75), (0.52, 0.62, 0.95))                 # peito (manubrio)
    elipsoide(mole, (0, -0.45, 4.5), (0.64, 1.1, 0.92))                  # transicao torax -> abdomen
    elipsoide(mole, (0, 0.4, 5.22), (0.58, 1.3, 0.74))                   # lombo (barriga recolhida)
    elipsoide(mole, (0, 1.6, 5.12), (0.66, 0.95, 0.84))                  # garupa
    for s in (1, -1):
        elipsoide(mole, (s * 0.46, -1.7, 5.6), (0.24, 0.72, 0.85), rot=(-30, 0, 0))    # escapula (achatada)
    trilha(mole, [(0, -1.95, 5.55, 0.92), (0, -2.65, 6.55, 0.74), (0, -3.15, 7.45, 0.6), (0, -3.4, 8.05, 0.5)],
           achatar=(0.82, 1.0), passo=0.2, u=20, v=10)                    # pescoco subindo
    elipsoide(mole, (0, -2.95, 6.1), (0.48, 0.6, 0.72))                  # garganta
    # cabeca: cranio, focinho afinando, maxila, mandibula, bochechas
    elipsoide(mole, (0, -3.72, 8.35), (0.47, 0.58, 0.47))
    elipsoide(mole, (0, -3.32, 8.38), (0.38, 0.35, 0.4))                 # occipital
    trilha(mole, [(0, -4.15, 8.24, 0.29), (0, -4.6, 8.12, 0.22), (0, -4.96, 8.02, 0.13)], achatar=(0.76, 0.86), passo=0.08, u=16, v=8)
    trilha(mole, [(0, -3.75, 7.82, 0.19), (0, -4.4, 7.82, 0.12), (0, -4.82, 7.85, 0.075)], achatar=(1.0, 0.72), passo=0.08, u=16, v=8)
    for s in (1, -1):
        elipsoide(mole, (s * 0.13, -4.45, 7.97), (0.1, 0.42, 0.12))     # maxila / labio superior
        elipsoide(mole, (s * 0.34, -3.8, 8.02), (0.19, 0.34, 0.26))      # masseter
        elipsoide(mole, (s * 0.42, -3.85, 8.22), (0.13, 0.33, 0.13))      # arco zigomatico
    # membros
    F, T = J["frente"], J["tras"]
    for s in (1, -1):
        X = lambda p: (s * p[0], p[1], p[2])
        cadeia(mole, [X(F[0]) + (0.36,), X(F[1]) + (0.33,), X(F[2]) + (0.29,), X(F[3]) + (0.2,), (s * 0.53, -2.42, 0.38, 0.17)], seg=18)
        elipsoide(mole, X((0.6, -2.12, 4.1)), (0.27, 0.4, 0.6), rot=(25, 0, 0))       # triceps
        elipsoide(mole, X((0.62, -2.55, 3.95)), (0.2, 0.22, 0.48))                     # braquial
        elipsoide(mole, X((0.57, -2.12, 2.6)), (0.25, 0.27, 0.62), rot=(-6, 0, 0))     # flexores do antebraco
        cadeia(mole, [X(T[0]) + (0.42,), X(T[1]) + (0.29,), X(T[2]) + (0.17,), (s * 0.5, 1.82, 0.36, 0.16)], seg=18)
        elipsoide(mole, X((0.6, 1.15, 4.05)), (0.36, 0.8, 1.0), rot=(-27, 0, 0))    # quadriceps / coxa
        elipsoide(mole, X((0.55, 2.0, 3.95)), (0.3, 0.46, 0.95), rot=(-25, 0, 0))    # isquiotibiais
        elipsoide(mole, X((0.55, 1.25, 2.8)), (0.18, 0.24, 0.6), rot=(35, 0, 0))   # gastrocnemio
    cadeia(mole, [(0, 2.2, 5.1, 0.33), (0, 2.75, 4.55, 0.4), (0, 3.25, 3.7, 0.42), (0, 3.75, 2.8, 0.38),
                  (0, 4.25, 1.9, 0.28), (0, 4.62, 1.15, 0.14)], seg=18)        # cauda (o volume vem da pelagem)
    estr = massa(mole, voxel=0.045, suav_iter=6, suav_fator=0.5, laplace=10)
    for s in (1, -1):                                                    # camada 2: marcos osseos e detalhes do rosto
        elipsoide(estr, (s * 0.5, -1.62, 5.95), (0.1, 0.6, 0.09), rot=(-30, 0, 0))    # espinha da escapula
        elipsoide(estr, (s * 0.6, -1.92, 3.35), (0.15, 0.17, 0.16))                    # olecrano
        elipsoide(estr, (s * 0.45, 1.65, 5.6), (0.2, 0.42, 0.16))                      # crista iliaca
        elipsoide(estr, (s * 0.55, 2.25, 4.4), (0.16, 0.2, 0.16))                      # tuberosidade isquiatica
        elipsoide(estr, (s * 0.55, -2.25, 1.0), (0.17, 0.18, 0.16))                    # carpo
        elipsoide(estr, (s * 0.52, 2.12, 1.45), (0.09, 0.12, 0.13))                    # calcaneo (jarrete)
        elipsoide(estr, (s * 0.24, -4.12, 8.56), (0.17, 0.22, 0.085), rot=(14, 0, s * -18))   # arcada (olhar de predador)
        elipsoide(estr, (s * 0.1, -4.02, 8.66), (0.09, 0.2, 0.06))                    # testa franzida
        pata_digitigrada(estr, rg("garra"), (s * 0.53, -2.58, 0.0), s, 0.36, 0.66, dedos=4, garra_comp=0.12)
        pata_digitigrada(estr, rg("garra"), (s * 0.5, 1.63, 0.0), s, 0.33, 0.6, dedos=4, garra_comp=0.11)
    elipsoide(estr, (0, -5.02, 8.07), (0.11, 0.07, 0.085))                 # trufa
    elipsoide(estr, (0, -4.1, 8.48), (0.16, 0.25, 0.08))                 # stop (degrau da testa)
    for s in (1, -1):                                                    # olhos amendoados, canto externo mais alto
        elipsoide(rg("olho"), (s * 0.255, -4.2, 8.43), (0.045, 0.078, 0.042), rot=(19, 0, s * -25), u=14, v=7)
    corpo = fundir("Lobo_Ancestral_Corpo_Blockout", estr, col, voxel=0.04, suav_iter=5, suav_fator=0.5, tris=12000)
    material_papel(corpo, "pelo")
    rg.criar("Lobo_Ancestral", col)
    pel = pelagem(corpo, col)
    humano(-5.0, -9.0)
    md = medidas(col)
    print("MEDIDAS", md, "PELAGEM_TRIS", pel["tris"])
    return col


# ------------------------------------------------------------------ PELAGEM (tufos de geometria + folhas de musgo)
CORES_ATLAS = [(0.19, 0.165, 0.12), (0.135, 0.118, 0.09), (0.29, 0.25, 0.19), (0.12, 0.15, 0.06)]   # base, escura, clara, musgo


def atlas():
    """Atlas 512x256 em 4 colunas (base, escura, clara, musgo): raiz escura -> ponta clara, com fios finos."""
    W_, H_ = 512, 256
    rng = np.random.default_rng(7)
    u = np.arange(W_)[None, :].repeat(H_, 0); v = np.arange(H_)[:, None].repeat(W_, 1) / (H_ - 1)
    fio = np.interp(u.ravel() + 3 * np.sin(v.ravel() * 9), np.arange(W_), 0.82 + 0.36 * rng.random(W_)).reshape(H_, W_)
    grad = 1.02 - 0.22 * v ** 1.5                                        # pontas um pouco mais escuras (aguti)
    img = np.zeros((H_, W_, 4)); img[..., 3] = 1
    for c, cor in enumerate(CORES_ATLAS):
        sl = slice(c * 128, (c + 1) * 128)
        for k in range(3):
            lin = np.clip(cor[k] * grad[:, sl] * fio[:, sl], 0, 1)
            img[:, sl, k] = lin ** (1 / 2.2)
    im = bpy.data.images.new("Lobo_Ancestral_Pelagem_Atlas", W_, H_, alpha=False)
    im.pixels.foreach_set(img.astype(np.float32).ravel()); im.pack()
    return im


def regiao(p, n=None):
    x, y, z = p
    if n is not None and 1.5 < z < 3.3 and -2.6 < y < -1.5 and abs(x) > 0.3 and n.y > 0.35:
        return "antebraco"
    if -4.0 < y < -3.05 and z > 8.45 and n is not None and n.z > 0.2:
        return "cabeca"
    if y < -3.2 and z > 7.3:
        return "bochecha" if (-3.85 < y and z < 8.3 and abs(x) > 0.28) else None
    if y > 2.1 and z < 5.15 and _dist_cauda(Vector(p)) < 0.62:
        return "cauda"
    if z < 2.7:
        return None
    if y < -1.55 and z > 4.1:
        return "colar"
    if y < -1.0 and z < 4.1 and abs(x) < 0.45:
        return "peito"
    if z > 5.45:
        return "dorso"
    if z < 3.95 and -1.6 < y < 0.7 and abs(x) < 0.6:
        return "ventre"
    if y > 1.5 and 2.9 < z < 4.7 and abs(x) > 0.3:
        return "coxa"
    return None


#            fluxo            comp (min,max)  larg   elev  espaco
REG = {"colar": ((0, 0.55, -1), (0.55, 0.85), 0.09, 0.34, 0.14), "peito": ((0, 0.25, -1), (0.45, 0.6), 0.1, 0.25, 0.16),
       "bochecha": ((0, 1, -0.45), (0.34, 0.46), 0.08, 0.3, 0.1), "cabeca": ((0, 1, 0.1), (0.2, 0.28), 0.06, 0.12, 0.1), "dorso": ((0, 1, -0.15), (0.35, 0.5), 0.09, 0.15, 0.19),
       "ventre": ((0, 0.2, -1), (0.3, 0.42), 0.08, 0.2, 0.18), "coxa": ((0, 0.5, -1), (0.3, 0.42), 0.08, 0.18, 0.18),
       "cauda": (None, (0.55, 0.8), 0.11, 0.25, 0.14), "antebraco": ((0, 0.6, -1), (0.28, 0.38), 0.08, 0.25, 0.13)}


def _dist_cauda(p):
    C = [Vector(c) for c in J["cauda"]]
    d = 1e9
    for a, b in zip(C, C[1:]):
        ab = b - a; t = max(0, min(1, (p - a).dot(ab) / ab.length_squared)); d = min(d, (p - (a + ab * t)).length)
    return d


def _tangente_cauda(p):
    C = [Vector(c) for c in J["cauda"]]
    best, d = None, 1e9
    for a, b in zip(C, C[1:]):
        ab = b - a; t = max(0, min(1, (p - a).dot(ab) / ab.length_squared)); q = a + ab * t
        if (p - q).length < d: d, best = (p - q).length, ab.normalized()
    return best


def tufo(bm, uvl, p, n, d, L, w, elev, col):
    b = n.cross(d).normalized()
    """Mecha deitada: secao em V (esquerda, crista, direita; a face de baixo encosta no corpo), 9 triangulos."""
    aneis = []
    for s in (0.0, 0.5):
        c = p - n * 0.04 + d * L * s + n * L * (elev * s - (elev * 0.75) * s * s)
        ww = w * (1 - 0.55 * s); t = w * 0.45 * (1 - 0.5 * s)
        aneis.append([bm.verts.new(c + b * ww), bm.verts.new(c + n * t), bm.verts.new(c - b * ww)])
    ponta = bm.verts.new(p - n * 0.04 + d * L + n * L * elev * 0.25)
    u0, u1 = col * 0.25 + 0.03, (col + 1) * 0.25 - 0.03
    us = [u0, (u0 + u1) / 2, u1]
    vs = (0.0, 0.5)
    for k in range(2):
        f = bm.faces.new((aneis[0][k], aneis[0][k + 1], aneis[1][k + 1], aneis[1][k]))
        for lp, (uu, vv) in zip(f.loops, ((us[k], 0), (us[k + 1], 0), (us[k + 1], 0.5), (us[k], 0.5))):
            lp[uvl].uv = (uu, vv)
        f = bm.faces.new((aneis[1][k], aneis[1][k + 1], ponta))
        for lp, (uu, vv) in zip(f.loops, ((us[k], 0.5), (us[k + 1], 0.5), ((u0 + u1) / 2, 1.0))):
            lp[uvl].uv = (uu, vv)
    f = bm.faces.new((aneis[0][2], aneis[0][0], aneis[1][0], aneis[1][2]))      # face de baixo (aparece quando a mecha levanta)
    for lp, (uu, vv) in zip(f.loops, ((u1, 0), (u0, 0), (u0, 0.5), (u1, 0.5))): lp[uvl].uv = (uu, vv)
    f = bm.faces.new((aneis[1][2], aneis[1][0], ponta))
    for lp, (uu, vv) in zip(f.loops, ((u1, 0.5), (u0, 0.5), ((u0 + u1) / 2, 1.0))): lp[uvl].uv = (uu, vv)


def folha(bm, uvl, p, n, d, L, w):
    b = n.cross(d).normalized(); c = p + n * 0.05
    pts = [c, c + d * L * 0.45 + b * w + n * 0.03, c + d * L, c + d * L * 0.45 - b * w + n * 0.03, c + d * L * 0.5 + n * 0.06]
    for lado in (1, -1):
        vs = [bm.verts.new(q - n * (0 if lado > 0 else 0.012)) for q in pts]
        tris = ((0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4))
        uvs = {0: (0.79, 0.15), 1: (0.76, 0.5), 2: (0.79, 0.9), 3: (0.82, 0.5), 4: (0.79, 0.5)}
        for t in tris:
            t = t if lado > 0 else t[::-1]
            f = bm.faces.new([vs[i] for i in t])
            for lp, i in zip(f.loops, t): lp[uvl].uv = uvs[i]


def orelha(bm, uvl, s):
    """Orelha triangular ereta, levemente voltada para a frente, concha na face anterior."""
    base, topo = Vector((s * 0.29, -3.52, 8.6)), Vector((s * 0.42, -3.62, 9.3))
    eixo = (topo - base).normalized()
    fr = Vector((0, -1, 0)); fr = (fr - eixo * fr.dot(eixo)).normalized(); la = eixo.cross(fr).normalized()
    def anel(c, ry, rx, conc):
        out = []
        for k in range(6):
            a = 2 * math.pi * k / 6
            off = la * math.cos(a) * ry + fr * math.sin(a) * rx
            if math.sin(a) > 0.3: off -= fr * conc                         # concha
            out.append(bm.verts.new(c + off))
        return out
    A = anel(base, 0.25, 0.08, 0.0); B = anel(base.lerp(topo, 0.5), 0.15, 0.055, 0.05); tip = bm.verts.new(topo)
    for R0, R1, v0, v1 in ((A, B, 0.05, 0.5),):
        for k in range(6):
            f = bm.faces.new((R0[k], R0[(k + 1) % 6], R1[(k + 1) % 6], R1[k]))
            for lp, vv in zip(f.loops, (v0, v0, v1, v1)): lp[uvl].uv = (0.1 + 0.03 * (k % 2), vv)
    for k in range(6):
        f = bm.faces.new((B[k], B[(k + 1) % 6], tip))
        for lp, vv in zip(f.loops, (0.5, 0.5, 0.95)): lp[uvl].uv = (0.37, vv)


def pelagem(corpo, col, semente=11):
    rnd = random.Random(semente)
    me = corpo.data
    cands = [(Vector(v.co), Vector(v.normal)) for v in me.vertices]
    rnd.shuffle(cands)
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    cont = {k: 0 for k in REG}; pos = {k: [] for k in REG}
    for p, n in cands:
        r = regiao(p, n)
        if not r: continue
        fluxo, (L0, L1), w, elev, esp = REG[r]
        if pos[r] and min((p - q).length for q in pos[r]) < esp: continue
        pos[r].append(p)
        f = _tangente_cauda(p) + Vector((0, 0, -0.25)) if r == "cauda" else Vector(fluxo)
        d = f - n * f.dot(n)
        if d.length < 1e-3: d = Vector((0, 1, 0)) - n * n.y
        d.normalize()
        d = Matrix.Rotation(math.radians(rnd.uniform(-14, 14)), 3, n) @ d
        L = rnd.uniform(L0, L1); ww = w * rnd.uniform(0.85, 1.15)
        colr = 0
        x = rnd.random()
        if r == "dorso" and x < 0.14: colr = 3
        elif r in ("dorso", "cauda", "cabeca") and x < 0.4: colr = 1
        elif r in ("ventre", "peito", "bochecha") or (r == "colar" and p.z < 5.4): colr = 2 if x < 0.7 else 0
        elif x < 0.25: colr = 2
        tufo(bm, uvl, p, n, d, L, ww, elev, colr)
        cont[r] += 1
    nf = 0
    for p, n in cands:                                               # folhas de musgo ("natural armor") no dorso/cernelha
        if nf >= 22: break
        if p.z > 5.75 and -1.9 < p.y < 1.2 and n.z > 0.35:
            d = Vector((rnd.uniform(-1, 1), rnd.uniform(-0.2, 1), 0)); d = (d - n * d.dot(n)).normalized()
            folha(bm, uvl, p, n, d, rnd.uniform(0.26, 0.38), rnd.uniform(0.09, 0.13)); nf += 1
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
    salvar(os.path.join(RAIZ, "Lobo_Ancestral", "Lobo_Ancestral_refinado_v3.blend"))
