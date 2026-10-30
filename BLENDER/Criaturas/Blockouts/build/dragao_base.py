# Base draconica (RPG_02: Dragoes "quadrupedes com duas asas independentes; compartilham estrutura-base, porem com chifres,
# asas, escamas e proporcoes regionais distintos"; adultos 18-24 studs ate os ombros, usado ~21).
# Comprimento e envergadura NAO definidos no documento: provisorios (~89 e ~62 com as asas meio erguidas).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from mathutils import Vector
from blockout_lib import *


def asa(bm, col, nome, s, ombro, cotovelo, pulso, pontas, raiz, r_osso, esp, espora=0.0):
    """Ossos da asa (fundidos ao corpo) + membrana em leque (objeto proprio). s = +1 esquerda, -1 direita."""
    P = lambda p: Vector((s * p[0], p[1], p[2]))
    cadeia(bm, [tuple(P(ombro)) + (r_osso,), tuple(P(cotovelo)) + (r_osso * 0.8,), tuple(P(pulso)) + (r_osso * 0.62,)], seg=16)
    for t in pontas:
        segmento(bm, P(pulso), P(t), r_osso * 0.45, r_osso * 0.12, seg=10)
    cont = [P(cotovelo), P(ombro), P(raiz)]
    tips = [P(t) for t in reversed(pontas)]
    w = P(pulso)
    for i, t in enumerate(tips):
        cont.append(t)
        if i + 1 < len(tips):
            m = (t + tips[i + 1]) / 2
            cont.append(m.lerp(w, 0.28))                        # recorte entre dedos
    mem = membrana(nome, col, cont, w, esp=esp)
    material_papel(mem, "membrana")
    return [P(t) for t in pontas]


def construir(especie, pose, P):
    cena_nova()
    col = colecao(especie)
    W, N, RN = P["largura"], P["pescoco"], P["raio_pescoco"]
    bm = bmesh.new()
    elipsoide(bm, (0, -8.0, 15.0), (6.5 * W, 7.0, 7.0))          # peito macico: topo ~22
    elipsoide(bm, (0, 0.0, 15.5), (6.2 * W, 9.0, 6.2))           # tronco: ventre ~9,3
    elipsoide(bm, (0, 9.0, 15.0), (5.5 * W, 5.5, 5.8))           # pelve
    for s in (1, -1):
        elipsoide(bm, (s * 5.0 * W, -8.0, 18.5), (2.6, 4.5, 3.5), rot=(-15, 0, 0))   # escapulas/ombros
        elipsoide(bm, (s * 5.0 * W, 9.5, 13.0), (3.0, 5.0, 6.0), rot=(15, 0, 0))     # coxas
    base = Vector((0, -12.0, 19.0))
    nk = [(0, -12.0, 19.0, 5.4), (0, -16.5, 23.5, 4.7), (0, -20.0, 27.5, 4.1), (0, -22.8, 30.5, 3.6), (0, -25.6, 32.0, 3.2)]
    nk = [tuple(base + (Vector(p[:3]) - base) * N) + (p[3] * RN,) for p in nk]   # pescoco em S erguido
    trilha(bm, nk, passo=0.5)
    h = Vector(nk[-1][:3])
    HC = P.get("cabeca", 1.0)
    elipsoide(bm, h + Vector((0, -2.4, 0.4)), (2.6 * RN * HC, 3.4 * HC, 2.3 * RN * HC))   # cranio
    trilha(bm, [tuple(h + Vector((0, -4.8, 0.0))) + (1.9 * RN,), tuple(h + Vector((0, -7.6, -0.6))) + (1.45 * RN,),
                tuple(h + Vector((0, -10.0, -1.1))) + (1.0 * RN,)], achatar=(1.05, 0.7), passo=0.3)        # focinho longo em cunha
    trilha(bm, [tuple(h + Vector((0, -3.6, -1.9))) + (1.4 * RN,), tuple(h + Vector((0, -9.6, -2.3))) + (0.8 * RN,)], achatar=(1.2, 0.5), passo=0.3)   # mandibula
    for s in (1, -1):
        elipsoide(bm, h + Vector((s * 2.0 * RN, -2.2, -0.8)), (0.9, 1.6, 1.3))       # musculo mandibular
        elipsoide(bm, h + Vector((s * 0.7 * RN, -9.4, -0.4)), (0.5, 0.6, 0.45))      # narinas
    for s in (1, -1):
        elipsoide(bm, h + Vector((s * 1.6 * RN, -3.5, 1.9)), (1.0, 1.4, 0.7))        # arcadas
    trilha(bm, [(0, 13, 15, 4.8), (0, 22, 13, 3.6), (0, 32, 10, 2.6), (0, 42, 7, 1.6), (0, 52, 5, 0.8), (0, 58, 4.5, 0.35)],
           achatar=(0.85, 1.0), passo=0.6)                                             # cauda longa e grossa
    for s in (1, -1):                                                                  # patas grossas
        G = P.get("perna", 1.0)
        cadeia(bm, [(s * 5.5 * W, -8, 13, 3.4 * G), (s * 6.2 * W, -6.5, 8, 2.7 * G), (s * 6.0 * W, -8.5, 3, 2.0 * G)], seg=20)
        elipsoide(bm, (s * 6.0 * W, -9.8, 1.0), (2.2 * G, 3.0 * G, 1.0))
        cadeia(bm, [(s * 5.4 * W, 9, 13, 4.0 * G), (s * 6.3 * W, 5.5, 8.5, 3.0 * G), (s * 6.0 * W, 11, 4.0, 1.9 * G)], seg=20)
        elipsoide(bm, (s * 6.0 * W, 9.6, 1.0), (2.2 * G, 3.2 * G, 1.0))
    pontas = {}
    for s in (1, -1):
        pontas[s] = asa(bm, col, "%s_Asa_%s_Blockout" % (especie, "E" if s > 0 else "D"), s,
                        (4.8 * W, -7, 21), (13, -4, 31), (18, 2, 38), P["dedos"], (5.2 * W, 11.5, 15.5), 1.6, 0.5)
    corpo = fundir(especie + "_Corpo_Blockout", bm, col, voxel=0.2, suav_iter=16, suav_fator=0.65, tris=16000)
    material_papel(corpo, "escama")
    rg = bmesh.new()                                                                   # partes rigidas por forma
    linha = [tuple(Vector(p[:3]) + Vector((0, 0, p[3] * 0.98))) for p in nk[::-1]]
    linha += [(0, y, 15.5 + 6.2 * math.sqrt(max(0, 1 - (y / 9.6) ** 2)) * 1.0) for y in (-5, -2, 1, 4, 7)]
    linha += [(0, y, 15 - 0.25 * (y - 13) + 4.8 * max(0.1, 1 - (y - 13) / 46) * 1.0) for y in range(13, 56, 4)]
    alt = [P["espinho"] * (0.6 + 0.4 * math.sin(math.pi * i / max(1, len(linha) - 1))) for i in range(len(linha))]
    fileira(rg, linha, alt, inclinar=(0.25, 0.7, 0), r0=P["espinho_r"], seg=P.get("espinho_seg", 8), lados=P.get("fileiras", (0.0,)))
    for chif in P["chifres"]:                                                          # chifres (pares)
        for s in (1, -1):
            pts = [h + Vector((s * c[0], c[1], c[2])) for c in chif["pts"]]
            chifre(rg, pts[0], pts[1:], chif["r"], 0.06, seg=10)
    for s in (1, -1):                                                                  # garras
        for (y, z) in ((-12.6, 0.6), (11.8, 0.6)):
            for dx in (-1.1, 0.0, 1.1):
                b = Vector((s * 6.0 * W + dx, y + 1.0, z + 0.5))
                chifre(rg, b, [b + Vector((0, -1.2, -0.2)), b + Vector((0, -2.0, -0.55))], 0.45, 0.04, seg=8)
        if P.get("espora", 0):                                                         # esporas nas pontas das asas (Sombrio)
            for t in pontas[s]:
                chifre(rg, t, [t + (t - Vector((s * 18, 2, 38))).normalized() * P["espora"] * 0.6,
                               t + (t - Vector((s * 18, 2, 38))).normalized() * P["espora"]], 0.35, 0.03, seg=8)
    rig = rigida(especie + "_Chifres_Espinhos_Blockout", rg, col)
    material_papel(rig, "osso")
    pr = Partes()
    olhos(pr("olho"), (1.95 * RN, h.y - 4.4, h.z + 1.0), 0.45)
    for s in (1, -1):                                                                  # dentes
        for i in range(9):
            y = h.y - 5.2 - 0.55 * i
            chifre(pr("osso"), (s * (1.5 - 0.06 * i) * RN, y, h.z - 1.15 - 0.06 * i), [(s * (1.52 - 0.06 * i) * RN, y, h.z - 1.75 - 0.06 * i)], 0.17, 0.02, seg=6)
    pr.criar(especie, col)
    humano(14.0, -36.0)
    md = medidas(col)
    md.update({"ombro_alvo": 21.0, "oficial": "18-24 ombro (quadrupede + 2 asas)", "provisorio": "comprimento (~89) e envergadura (asas meio erguidas)"})
    registrar(especie, pose, md)
    print("MEDIDAS", md)


DEDOS = [(31, 6, 35), (29, 15, 27), (22, 20, 20), (14, 19, 17)]
