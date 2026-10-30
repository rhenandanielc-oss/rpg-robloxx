# Lagarto Cristalino (Deserto de Cristal). RPG_02: "quadrupede de anatomia reptiliana robusta, com formacoes naturais de
# cristais nas costas e cauda"; 18-26 studs de COMPRIMENTO TOTAL (usado ~24). Altura/largura pela referencia (# inferred).
# REFINADO: AGLOMERADOS naturais de prismas hexagonais (tamanhos e inclinacoes variados, assimetricos), placas na cabeca,
# patas robustas com 5 dedos e garras. Cristais = objeto proprio (material cristal), presos as placas do dorso.
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from mathutils import Vector
from blockout_lib import *

ESPECIE = "Lagarto_Cristalino"


def construir(pose):
    cena_nova()
    col = colecao(ESPECIE)
    rg = Partes()
    bm = bmesh.new()
    elipsoide(bm, (0, 0.0, 4.6), (3.3, 5.0, 3.0))            # tronco arqueado e pesado
    elipsoide(bm, (0, 3.4, 5.2), (2.9, 2.8, 2.7))            # quadril alto
    elipsoide(bm, (0, -3.8, 4.1), (2.9, 2.4, 2.5))           # peito
    trilha(bm, [(0, -5.3, 4.2, 1.7), (0, -6.9, 3.8, 1.35)], passo=0.25)   # pescoco baixo
    elipsoide(bm, (0, -7.8, 3.7), (1.3, 1.7, 0.75))          # cabeca baixa, larga e chata (lagarto)
    trilha(bm, [(0, -8.9, 3.6, 0.95), (0, -10.2, 3.45, 0.65), (0, -11.0, 3.35, 0.4)], achatar=(1.3, 0.5), passo=0.12)
    trilha(bm, [(0, -8.0, 3.05, 0.9), (0, -10.8, 2.95, 0.38)], achatar=(1.35, 0.42), passo=0.12)   # mandibula
    for s in (1, -1):
        elipsoide(bm, (s * 1.1, -7.6, 3.3), (0.5, 0.9, 0.55))     # musculo da mandibula
    trilha(bm, [(0, 5.8, 5.5, 1.8), (0, 8.8, 4.5, 1.25), (0, 11.6, 3.3, 0.8), (0, 13.6, 2.4, 0.4)], achatar=(0.85, 1.0), passo=0.25)
    pes = []
    for s in (1, -1):
        cadeia(bm, [(s * 2.7, -3.8, 3.8, 1.1), (s * 3.7, -3.8, 2.3, 0.82), (s * 3.6, -4.3, 0.75, 0.6)], seg=18)
        elipsoide(bm, (s * 3.2, -3.8, 3.2), (0.85, 0.9, 0.8), rot=(0, s * 30, 0))
        cadeia(bm, [(s * 2.7, 3.6, 4.5, 1.3), (s * 3.8, 2.8, 2.5, 0.92), (s * 3.7, 4.0, 0.8, 0.62)], seg=18)
        elipsoide(bm, (s * 3.3, 3.4, 3.7), (1.05, 1.3, 1.1), rot=(0, s * 20, 0))
        pes += [((s * 3.35, -4.75, 0.0), s, 1.0, 1.4), ((s * 3.45, 3.6, 0.0), s, 1.05, 1.55)]
    estr = massa(bm, voxel=0.08, suav_iter=6, suav_fator=0.5, laplace=12)
    for s in (1, -1):                                          # placas osseas da cabeca
        elipsoide(estr, (s * 0.7, -7.9, 4.6), (0.55, 0.8, 0.22), rot=(0, s * 20, 0))
    for c, s, l, cp in pes:
        pe_reptil(estr, rg("garra"), c, s, l, cp, dedos=5, garra_comp=0.4)
    linha = [(0, -5.6, 5.4), (0, -4.2, 6.6), (0, -2.6, 7.4), (0, -1.0, 7.6), (0, 0.6, 7.7), (0, 2.2, 7.85), (0, 3.8, 7.8),
             (0, 5.4, 7.3), (0, 7.0, 6.5), (0, 8.6, 5.6), (0, 10.2, 4.6), (0, 11.8, 3.6)]
    alt = [1.0, 1.6, 2.4, 3.0, 3.3, 3.4, 3.1, 2.6, 2.0, 1.5, 1.1, 0.8]
    locais = []
    for i, (p, h) in enumerate(zip(linha, alt)):               # aglomerados naturais, alternando os lados
        for lado in (-1, 1):
            dx = lado * (0.55 + 0.25 * ((i * 7 + (lado > 0) * 3) % 3))
            elipsoide(estr, (dx, p[1], p[2] - 0.3), (0.65, 0.75, 0.45), u=10, v=5)       # base mineralizada que nasce da pele
            locais.append((i, lado, dx, p, h))
    corpo = fundir(ESPECIE + "_Corpo_Blockout", estr, col, voxel=0.075, suav_iter=4, suav_fator=0.45, tris=16000)
    material_papel(corpo, "escama")
    for i, lado, dx, p, h in locais:
        aglomerado(rg("cristal"), (dx, p[1], p[2] - 0.3), (lado * 0.35, 0.12, 1.0), 2 + (i % 3), h * 0.7, h * 1.2,
                   0.18 + 0.05 * h, 0.26 + 0.07 * h, semente=i * 11 + (lado > 0), abertura=24)
    olhos(rg("olho"), (0.85, -8.6, 4.1), 0.17)
    rg.criar(ESPECIE, col)
    humano(6.0, -10.0)
    md = medidas(col)
    md.update({"comprimento_alvo": 24, "oficial": "18-26 comprimento total", "provisorio": "altura e largura pela referencia"})
    registrar(ESPECIE, pose, md)
    print("MEDIDAS", md)


if __name__ == "__main__":
    a = args()
    construir(a.pose)
    salvar(a.out)
