# Wyvern (Montanhas Altas). RPG_02 [OFICIAL]: 9-13 studs ate os ombros (usado 11), envergadura 30-42 (usada 38), ferrao.
# [PROPOSTA VISUAL do documento]: "corpo mais aerodinamico e leve que um Dragao, duas patas traseiras, membros dianteiros
# associados as asas, cauda terminada em ferrao". Anatomia diferente da base draconica (nao reutilizada).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from mathutils import Vector
from blockout_lib import *
from dragao_base import asa

ESPECIE = "Wyvern"


def construir(pose):
    cena_nova()
    col = colecao(ESPECIE)
    bm = bmesh.new()
    elipsoide(bm, (0, -2.2, 9.4), (3.0, 2.9, 2.7))            # peito largo em quilha (musculos de voo)
    elipsoide(bm, (0, -3.2, 8.2), (2.2, 1.8, 2.0))            # quilha do esterno
    for s in (1, -1):
        elipsoide(bm, (s * 2.0, -2.4, 10.4), (1.4, 2.0, 1.5))   # peitorais/ombros das asas
    elipsoide(bm, (0, 0.2, 9.0), (2.4, 3.6, 2.3))             # tronco
    elipsoide(bm, (0, 3.2, 8.8), (2.1, 2.2, 2.1))             # pelve
    trilha(bm, [(0, -3.8, 10.4, 1.8), (0, -5.6, 12.6, 1.45), (0, -6.8, 14.4, 1.2), (0, -8.0, 15.5, 1.0)])   # pescoco em S
    elipsoide(bm, (0, -9.2, 15.7), (1.05, 1.7, 0.9))          # cabeca predatoria
    for s in (1, -1):
        elipsoide(bm, (s * 0.65, -9.6, 16.25), (0.35, 0.8, 0.25))   # arcadas
    trilha(bm, [(0, -10.4, 15.5, 0.7), (0, -11.8, 15.2, 0.4)], achatar=(1.0, 0.8))   # focinho
    elipsoide(bm, (0, -10.6, 14.9), (0.6, 1.3, 0.3))          # mandibula
    trilha(bm, [(0, 5.0, 9.0, 1.5), (0, 10.0, 8.4, 1.1), (0, 16.0, 7.4, 0.75), (0, 22.0, 6.6, 0.45), (0, 27.0, 6.2, 0.25)],
           achatar=(0.85, 1.0), passo=0.3)                     # cauda longa e fina
    for s in (1, -1):                                          # duas patas traseiras fortes (bipede)
        elipsoide(bm, (s * 2.0, 3.0, 7.4), (1.6, 2.3, 2.7), rot=(20, 0, 0))   # coxas fortes
        cadeia(bm, [(s * 1.9, 3.2, 7.2, 1.25), (s * 2.2, 1.2, 4.6, 1.0), (s * 2.0, 3.6, 1.9, 0.6), (s * 2.0, 2.8, 0.5, 0.5)], seg=16)
        elipsoide(bm, (s * 2.0, 2.2, 0.36), (0.8, 1.4, 0.36))
    for s in (1, -1):                                          # asas = membros dianteiros
        asa(bm, col, "%s_Asa_%s_Blockout" % (ESPECIE, "E" if s > 0 else "D"), s,
            (2.0, -2.2, 11.0), (6.5, -1.0, 14.0), (10.5, 0.5, 16.0), [(19, 2, 15.5), (17, 7, 11), (12.5, 9.5, 8.5)],
            (2.2, 4.2, 7.2), 0.9, 0.25)
        elipsoide(bm, (s * 10.5, 0.2, 16.0), (0.5, 0.7, 0.5))   # garra do punho
    corpo = fundir(ESPECIE + "_Corpo_Blockout", bm, col, voxel=0.07, suav_iter=14, suav_fator=0.6, tris=14000)
    material_papel(corpo, "escama")
    rg = bmesh.new()
    chifre(rg, (0, 27.0, 6.2), [(0, 28.6, 6.6), (0, 29.8, 7.7)], 0.5, 0.05, seg=10)    # ferrao
    for s in (1, -1):
        chifre(rg, (s * 0.6, -8.8, 16.4), [(s * 0.9, -7.6, 17.0), (s * 1.1, -6.4, 17.2)], 0.3, 0.04, seg=8)   # chifres
        for dx in (-0.4, 0.0, 0.4):                            # garras dos pes
            b = Vector((s * 2.0 + dx, 1.6, 0.5))
            chifre(rg, b, [b + Vector((0, -0.6, -0.1)), b + Vector((0, -1.0, -0.35))], 0.22, 0.03, seg=8)
    linha = [(0, -6.0 + 1.4 * i, 11.2 - 0.25 * i) for i in range(8)] + [(0, 6.0 + 2.2 * i, 9.2 - 0.33 * i) for i in range(9)]
    fileira(rg, linha, [0.7] * len(linha), inclinar=(0, 0.8, 0), r0=0.25, seg=6)
    rig = rigida(ESPECIE + "_Ferrao_Chifres_Blockout", rg, col)
    material_papel(rig, "garra")
    pr = Partes(); olhos(pr("olho"), (0.6, -9.9, 16.05), 0.17); pr.criar(ESPECIE, col)
    humano(8.0, -14.0)
    md = medidas(col)
    md.update({"ombro_alvo": 11.0, "envergadura_alvo": 38, "oficial": "9-13 ombro; envergadura 30-42",
               "provisorio": "anatomia bipede (PROPOSTA visual do RPG_02), comprimento"})
    registrar(ESPECIE, pose, md)
    print("MEDIDAS", md)


if __name__ == "__main__":
    a = args()
    construir(a.pose)
    salvar(a.out)
