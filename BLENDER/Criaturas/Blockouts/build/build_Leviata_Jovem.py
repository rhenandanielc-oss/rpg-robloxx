# Leviata Jovem (Costas Selvagens). RPG_02: "reptil marinho colossal de quatro nadadeiras e cauda musculosa, com 55-80
# studs de comprimento no estagio Adulto" (usado ~70).
# Reconstruido: cabeca macica com mandibula, corpo volumoso, 4 nadadeiras, cauda musculosa com crista vertical, placas
# dorsais (painel oficial: dorso espinhoso). Altura/largura pela referencia (# inferred).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from mathutils import Vector
from blockout_lib import *

ESPECIE = "Leviata_Jovem"


def construir(pose):
    cena_nova()
    col = colecao(ESPECIE)
    bm = bmesh.new()
    trilha(bm, [(0, -22.0, 7.4, 5.2), (0, -14.0, 8.0, 7.2), (0, -2.0, 8.2, 8.0), (0, 10.0, 7.6, 6.6), (0, 20.0, 6.6, 4.4),
                (0, 29.0, 5.6, 2.6), (0, 36.0, 5.0, 1.1)], achatar=(1.05, 0.9), passo=0.9, u=24, v=12)   # corpo + cauda
    elipsoide(bm, (0, -27.0, 7.6), (4.6, 6.0, 4.0))          # cabeca macica
    trilha(bm, [(0, -30.5, 7.2, 2.9), (0, -34.0, 6.6, 2.1), (0, -36.2, 6.2, 1.3)], achatar=(1.2, 0.8))   # focinho reptiliano longo
    elipsoide(bm, (0, -30.5, 4.6), (3.4, 6.4, 1.6))          # mandibula longa
    for s in (1, -1):                                        # 4 nadadeiras em remo, fundidas ao corpo
        elipsoide(bm, (s * 7.4, -12.0, 5.0), (2.4, 2.8, 1.5))
        elipsoide(bm, (s * 12.5, -10.6, 3.4), (4.6, 2.2, 0.75), rot=(0, s * 14, s * 22))
        elipsoide(bm, (s * 6.0, 13.0, 4.6), (1.9, 2.2, 1.2))
        elipsoide(bm, (s * 9.6, 14.2, 3.4), (3.4, 1.7, 0.65), rot=(0, s * 12, -s * 18))
    for s in (1, -1):
        elipsoide(bm, (s * 3.2, -27.5, 9.6), (1.3, 1.6, 1.1))    # arcadas sobre os olhos
    corpo = fundir(ESPECIE + "_Corpo_Blockout", bm, col, voxel=0.22, suav_iter=10, suav_fator=0.55, tris=16000)
    material_papel(corpo, "escama")
    pr = Partes()
    olhos(pr("olho"), (3.0, -29.0, 8.8), 0.55)
    for s in (1, -1):                                         # dentes conicos na maxila e mandibula
        for i in range(10):
            y = -29.5 - 0.65 * i
            w = 2.7 - 0.13 * i
            chifre(pr("osso"), (s * w, y, 5.6), [(s * w * 1.02, y, 4.9)], 0.24, 0.02, seg=6)
    for s in (1, -1):                                         # nadadeiras: bordas osseas (raios) para leitura de remo
        for t in range(3):
            chifre(pr("osso"), (s * 8.5, -12.2 + 0.6 * t, 4.6), [(s * (14.0 + 1.2 * t), -11.0 + 0.8 * t, 2.6)], 0.35, 0.08, seg=6)
    pr.criar(ESPECIE, col)
    rg = bmesh.new()                                          # placas dorsais e crista da cauda
    linha = [(0, y, 8.2 + 7.0 * math.cos(math.pi * (y + 4) / 46)) for y in range(-20, 31, 3)]
    alt = [2.0 + 2.8 * math.sin(math.pi * (i + 1) / (len(linha) + 1)) for i in range(len(linha))]
    fileira(rg, linha, alt, inclinar=(0, 0.6, 0), r0=1.2, seg=6, lados=(-1.4, 1.4))
    fileira(rg, [(0, y, 7.0 - 0.12 * (y - 30)) for y in range(30, 37, 2)], [2.4, 2.0, 1.5, 1.0], inclinar=(0, 0.4, 0), r0=0.9, seg=6)
    placas = rigida(ESPECIE + "_Placas_Blockout", rg, col)
    material_papel(placas, "osso")
    humano(16.0, -30.0)
    md = medidas(col)
    md.update({"comprimento_alvo": 70, "oficial": "55-80 comprimento; quatro nadadeiras"})
    registrar(ESPECIE, pose, md)
    print("MEDIDAS", md)


if __name__ == "__main__":
    a = args()
    construir(a.pose)
    salvar(a.out)
