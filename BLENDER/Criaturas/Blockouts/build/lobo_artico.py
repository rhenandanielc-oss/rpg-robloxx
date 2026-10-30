# Lobo Artico (27/10/2026): refinamento realista com a tecnica da V5 do Lobo Ancestral, em script proprio
# (lobo_v5.py e os arquivos do Ancestral nao sao alterados; so reutilizados por importacao).
# Referencia: REFERENCES/03_CREATURES/01-lobos-urso-leao.png, quadro 02 (robusto, poderoso, resiliente; pelagem branca e
# cinza muito densa, olhos azul-gelo, patas largas para neve). RPG_02: 5,5-7 studs no ombro, "mais robusto" que o Ancestral.
# Mesmas articulacoes (J/PELO_OSSOS do lobo_v5): rig canino e animacoes compativeis.
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix
import lobo_v5 as L5
from lobo_v5 import J, M_CAB, OLHO_X

ESP = "Lobo_Artico"


def atlas_neve():
    """Atlas do Artico: fios finos brancos/cinza, raiz levemente sombreada, sem fendas de casca nem liquen."""
    import numpy as np
    W_, H_ = 128 * L5.NC, 256
    rng = np.random.default_rng(9)
    u = np.arange(W_)[None, :].repeat(H_, 0); v = np.arange(H_)[:, None].repeat(W_, 1) / (H_ - 1)
    fio = np.interp(u.ravel() + 3 * np.sin(v.ravel() * 9), np.arange(W_), 0.86 + 0.28 * rng.random(W_)).reshape(H_, W_)
    grad = (0.82 + 0.22 * np.minimum(1, v * 3)) * (1 - 0.12 * v ** 2)
    img = np.zeros((H_, W_, 4)); img[..., 3] = 1
    for c, cor in enumerate(L5.CORES_ATLAS + [(0.5, 0.5, 0.5)]):
        sl = slice(c * 128, (c + 1) * 128)
        for k in range(3):
            img[:, sl, k] = np.clip(cor[k] * grad[:, sl] * fio[:, sl], 0, 1) ** (1 / 2.2)
    im = bpy.data.images.new(ESP + "_Pelagem_Atlas", W_, H_, alpha=False)
    im.pixels.foreach_set(img.astype(np.float32).ravel()); im.pack()
    return im


def pelo_orelhas(col):
    """Cartoes de pelo nas orelhas (face interna clara e externa), seguindo o eixo da orelha."""
    import random
    rnd = random.Random(8)
    mat = next(m for m in bpy.data.materials if m.name.endswith("_Pelagem"))
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
    for s in (1, -1):
        base, topo = Vector(L5.H((s * 0.3, -3.52, 8.6))), Vector(L5.H((s * 0.45, -3.6, 9.28)))
        eixo = (topo - base).normalized()
        fr = Vector((0, -1, 0)); fr = (fr - eixo * fr.dot(eixo)).normalized(); la = eixo.cross(fr).normalized()
        for i in range(12):
            t = 0.05 + 0.075 * i
            for face, linha in ((fr, 1), (-fr, 0)):
                p = base.lerp(topo, t) + face * 0.05 + la * rnd.uniform(-0.18, 0.18) * (1 - t)
                d = (eixo + la * rnd.uniform(-0.4, 0.4) + face * 0.15).normalized()
                L5.cartao(bm, uvl, p, face, d, rnd.uniform(0.2, 0.32) * (1.2 - t), 0.2 * (1.1 - t), 0.25, linha, rnd)
    m = bpy.data.meshes.new("Lobo_Ancestral_PelagemOrelhas"); bm.to_mesh(m); bm.free()
    ob = bpy.data.objects.new("Lobo_Ancestral_PelagemOrelhas", m); col.objects.link(ob)
    m.materials.append(mat); ob["papel_material"] = "pelagem"


def construir():
    from blockout_lib import (cena_nova, colecao, Partes, elipsoide, cadeia, trilha, massa, fundir, juntar,
                              material_papel, pata_digitigrada, humano, medidas)
    cena_nova()
    col = colecao(ESP)
    rg = Partes()
    mole = bmesh.new()                                                   # massas ~8-12% maiores que o Ancestral
    elipsoide(mole, (0, -1.5, 4.85), (0.93, 1.85, 1.66))                 # torax mais largo e fundo
    elipsoide(mole, (0, -2.8, 4.75), (0.68, 0.72, 1.06))
    elipsoide(mole, (0, -0.45, 4.5), (0.78, 1.15, 0.98))
    elipsoide(mole, (0, 0.75, 4.62), (0.74, 1.05, 0.78))
    elipsoide(mole, (0, 0.4, 5.22), (0.72, 1.3, 0.8))
    elipsoide(mole, (0, 1.6, 5.12), (0.82, 1.02, 0.92))                  # garupa forte (propulsao)
    for s in (1, -1):
        elipsoide(mole, (s * 0.52, -1.7, 5.55), (0.24, 0.74, 0.88), rot=(-30, 0, 0))
        elipsoide(mole, (s * 0.62, -2.3, 4.85), (0.3, 0.54, 0.6), rot=(-20, 0, 0))
        elipsoide(mole, (s * 0.58, 1.0, 3.95), (0.28, 0.54, 0.46))
    trilha(mole, [(0, -1.9, 5.5, 1.12), (0, -2.65, 6.3, 0.95), (0, -3.25, 6.95, 0.78), (0, -3.55, 7.35, 0.66)],
           achatar=(0.9, 1.0), passo=0.2, u=20, v=10)                     # pescoco forte
    elipsoide(mole, (0, -3.0, 5.95), (0.64, 0.7, 0.8))
    elipsoide(mole, (0, -1.95, 5.75), (0.86, 0.98, 0.78))
    cab = bmesh.new()                                                    # cabeca: cranio mais largo, focinho um pouco mais curto
    elipsoide(cab, (0, -3.72, 8.35), (0.56, 0.6, 0.5))
    elipsoide(cab, (0, -3.32, 8.38), (0.46, 0.37, 0.43))
    trilha(cab, [(0, -4.15, 8.24, 0.32), (0, -4.58, 8.12, 0.24), (0, -4.9, 8.04, 0.15)], achatar=(0.76, 0.9), passo=0.08, u=16, v=8)
    trilha(cab, [(0, -3.75, 7.83, 0.21), (0, -4.38, 7.83, 0.14), (0, -4.76, 7.86, 0.09)], achatar=(1.0, 0.75), passo=0.08, u=16, v=8)
    for s in (1, -1):
        elipsoide(cab, (s * 0.14, -4.42, 7.98), (0.11, 0.4, 0.12))
        elipsoide(cab, (s * 0.36, -3.8, 8.0), (0.2, 0.33, 0.25))
        elipsoide(cab, (s * 0.48, -3.85, 8.22), (0.13, 0.32, 0.13))
    bmesh.ops.transform(cab, matrix=M_CAB, verts=cab.verts); juntar(mole, cab)
    F, T = J["frente"], J["tras"]
    for s in (1, -1):
        X = lambda p: (s * p[0], p[1], p[2])
        cadeia(mole, [X(F[0]) + (0.2,), X(F[1]) + (0.41,), X(F[2]) + (0.39,), X(F[3]) + (0.31,), (s * 0.53, -2.42, 0.38, 0.28)], seg=18)
        elipsoide(mole, X((0.66, -2.12, 4.1)), (0.34, 0.48, 0.7), rot=(25, 0, 0))
        elipsoide(mole, X((0.68, -2.55, 3.95)), (0.24, 0.26, 0.52))
        elipsoide(mole, X((0.6, -2.12, 2.6)), (0.34, 0.36, 0.72), rot=(-6, 0, 0))
        cadeia(mole, [X(T[0]) + (0.49,), X(T[1]) + (0.37,), X(T[2]) + (0.28,), (s * 0.5, 1.82, 0.36, 0.27)], seg=18)
        elipsoide(mole, X((0.64, 1.15, 4.05)), (0.44, 0.86, 1.06), rot=(-27, 0, 0))
        elipsoide(mole, X((0.54, 1.72, 3.95)), (0.35, 0.53, 0.97), rot=(-20, 0, 0))
        elipsoide(mole, X((0.33, 2.05, 4.55)), (0.37, 0.52, 0.64), rot=(-15, 0, 0))
        elipsoide(mole, X((0.58, 1.25, 2.8)), (0.27, 0.33, 0.68), rot=(35, 0, 0))
    elipsoide(mole, (0, 2.2, 4.85), (0.5, 0.52, 0.58))
    cadeia(mole, [(0, 2.2, 5.1, 0.42), (0, 2.75, 4.55, 0.5), (0, 3.25, 3.7, 0.54), (0, 3.75, 2.8, 0.5),
                  (0, 4.25, 1.9, 0.38), (0, 4.62, 1.15, 0.18)], seg=18)
    estr = massa(mole, voxel=0.045, suav_iter=8, suav_fator=0.5, laplace=16)
    L5.OLHO_X = OLHO_X + 0.03
    esp_orig = L5.espessura
    def esp_artico(p, n):                                                # sem calombo sob a mandibula
        q = L5.local_cabeca(p)
        e = esp_orig(p, n)
        return e * 0.25 if (q is not None and q.z < 7.95) else e
    L5.espessura = esp_artico
    L5.volume_pelo(estr, 1.4)
    L5.espessura = esp_orig                                            # pelagem artica: subpelo ~40% mais espesso
    det = bmesh.new()
    for s in (1, -1):
        elipsoide(estr, (s * 0.66, -1.92, 3.35), (0.17, 0.19, 0.18))
        elipsoide(estr, (s * 0.57, -2.25, 1.0), (0.24, 0.25, 0.22))
        elipsoide(estr, (s * 0.53, 2.1, 1.45), (0.15, 0.18, 0.17))
        elipsoide(det, (s * (OLHO_X + 0.02), -4.12, 8.56), (0.15, 0.2, 0.075), rot=(14, 0, s * -18))
        elipsoide(det, (s * 0.1, -4.02, 8.64), (0.08, 0.18, 0.055))
        pata_digitigrada(estr, rg("garra"), (s * 0.56, -2.62, 0.0), s, 0.48, 0.82, dedos=4, garra_comp=0.17)   # patas de neve, largas
        pata_digitigrada(estr, rg("garra"), (s * 0.52, 1.62, 0.0), s, 0.43, 0.76, dedos=4, garra_comp=0.15)
        elipsoide(estr, (s * 0.62, -2.42, 0.22), (0.07, 0.07, 0.08))
    elipsoide(det, (0, -4.95, 8.07), (0.12, 0.08, 0.09))
    elipsoide(det, (0, -4.1, 8.48), (0.16, 0.24, 0.075))
    bmesh.ops.transform(det, matrix=M_CAB, verts=det.verts); juntar(estr, det)
    ox = OLHO_X + 0.03                                                   # cranio mais largo: olho na superficie
    olho = bmesh.new(); pup = bmesh.new()
    for s in (1, -1):
        elipsoide(olho, (s * ox, -4.19, 8.42), (0.05, 0.086, 0.046), rot=(19, 0, s * -25), u=14, v=7)
        R = Matrix.Rotation(math.radians(s * -25), 3, "Z") @ Matrix.Rotation(math.radians(19), 3, "X")
        elipsoide(pup, Vector((s * ox, -4.19, 8.42)) + R @ Vector((s * 0.046, 0, 0)), (0.012, 0.03, 0.032), rot=(19, 0, s * -25), u=10, v=5)
    bmesh.ops.transform(olho, matrix=M_CAB, verts=olho.verts); juntar(rg("olho"), olho)
    bmesh.ops.transform(pup, matrix=M_CAB, verts=pup.verts); juntar(rg("garra"), pup)
    corpo = fundir(ESP + "_Corpo_Blockout", estr, col, voxel=0.04, suav_iter=5, suav_fator=0.5, tris=12000)
    material_papel(corpo, "pelo")
    rg.criar(ESP, col)
    # pelagem: mesma tecnica, branca/cinza, mais longa e densa, sem vegetacao
    L5.OLHO_X = ox
    L5.CORES_ATLAS = [(0.6, 0.6, 0.6), (0.3, 0.31, 0.32), (0.78, 0.78, 0.76), (0.44, 0.46, 0.48)]   # branco, cinza, branco puro, cinza-prata
    L5.atlas = atlas_neve
    L5.CORES_CARTAO = [(0.62, 0.62, 0.6), (0.8, 0.8, 0.78)]           # branco e branco puro (cinza vem das variacoes)
    m_corpo, m_resto = 1.3, 1.15
    L5.REG = {k: (fl, (a * (m_corpo if k in L5.CASCA | {"peito", "ventre", "bochecha"} else m_resto),
                       b * (m_corpo if k in L5.CASCA | {"peito", "ventre", "bochecha"} else m_resto)), w, el, esp * 0.92, n)
              for k, (fl, (a, b), w, el, esp, n) in L5.REG.items()}
    L5.folha_real = lambda *a, **k: None                                 # sem folhas/samambaias no Artico
    L5.samambaia = lambda *a, **k: None
    pel = L5.pelagem(corpo, col)
    pelo_orelhas(col)
    for o in list(col.objects):
        o.name = o.name.replace("Lobo_Ancestral", ESP)
        if o.type == "MESH":
            o.data.name = o.data.name.replace("Lobo_Ancestral", ESP)
    for m in bpy.data.materials: m.name = m.name.replace("Lobo_Ancestral", ESP)
    for i in bpy.data.images: i.name = i.name.replace("Lobo_Ancestral", ESP)
    humano(-5.0, -9.0)
    md = medidas(col)
    print("MEDIDAS", md, "PELAGEM_TRIS", pel["tris"])
    return col


if __name__ == "__main__":
    from blockout_lib import salvar, RAIZ
    construir()
    salvar(os.path.join(RAIZ, ESP, ESP + "_refinado_v5.blend"))
