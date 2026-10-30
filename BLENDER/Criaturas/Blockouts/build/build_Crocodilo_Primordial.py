# Crocodilo Primordial (Pantano Nebuloso). RPG_02: "crocodiliano quadrupede gigantesco, corpo baixo, escamas grossas e
# cauda musculosa"; 5-7 studs ate os ombros e 24-32 de comprimento com a cauda (usados ~5,8 e ~30).
# REFINADO: cranio largo e plano com mandibula pesada e fileira de dentes, olhos e narinas no topo, osteodermos em escudos
# (fileiras), patas espalhadas com cotovelo para fora e 5 dedos com garras, crista dupla na cauda. Largura pela anatomia.
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from mathutils import Vector
from blockout_lib import *

ESPECIE = "Crocodilo_Primordial"


def construir(pose):
    cena_nova()
    col = colecao(ESPECIE)
    rg = Partes()
    bm = bmesh.new()
    elipsoide(bm, (0, 0.0, 3.5), (3.0, 5.6, 2.1))            # tronco baixo e largo
    elipsoide(bm, (0, -4.6, 3.6), (2.6, 2.2, 1.9))           # peito/ombros
    elipsoide(bm, (0, 4.8, 3.7), (2.5, 2.4, 1.9))            # pelve
    elipsoide(bm, (0, -6.6, 3.7), (2.1, 1.8, 1.55))          # pescoco curto
    elipsoide(bm, (0, -8.2, 3.75), (1.75, 1.9, 1.05))        # cranio largo e chato
    trilha(bm, [(0, -9.4, 3.55, 1.3), (0, -11.4, 3.3, 1.0), (0, -13.2, 3.15, 0.75)], achatar=(1.25, 0.55), passo=0.25)   # focinho
    elipsoide(bm, (0, -13.5, 3.35), (0.75, 0.45, 0.35))      # ponta com narinas elevadas
    trilha(bm, [(0, -8.4, 2.75, 1.3), (0, -11.0, 2.75, 0.95), (0, -13.1, 2.75, 0.68)], achatar=(1.3, 0.45), passo=0.25)  # mandibula pesada
    for s in (1, -1):
        elipsoide(bm, (s * 1.55, -7.9, 3.2), (0.6, 1.1, 0.7))   # musculo da mandibula (bochecha)
        elipsoide(bm, (s * 0.85, -8.3, 4.6), (0.5, 0.6, 0.4))   # orbitas elevadas
    trilha(bm, [(0, 6.6, 3.7, 1.9), (0, 9.5, 3.2, 1.45), (0, 12.5, 2.6, 0.95), (0, 15.2, 2.0, 0.5), (0, 16.6, 1.7, 0.2)],
           achatar=(0.62, 1.0), passo=0.3)                     # cauda musculosa achatada lateralmente
    pes = []
    for s in (1, -1):                                          # patas espalhadas (cotovelo/joelho para fora)
        cadeia(bm, [(s * 2.4, -4.4, 3.2, 1.0), (s * 3.7, -4.2, 2.3, 0.8), (s * 3.7, -4.6, 0.7, 0.62)], seg=18)
        elipsoide(bm, (s * 3.0, -4.3, 2.9), (0.75, 0.8, 0.6))   # biceps/triceps
        cadeia(bm, [(s * 2.3, 4.4, 3.3, 1.2), (s * 3.9, 3.6, 2.4, 0.95), (s * 3.9, 4.6, 0.75, 0.65)], seg=18)
        elipsoide(bm, (s * 3.0, 4.2, 3.1), (0.95, 1.2, 0.85))   # coxa
        pes += [((s * 3.8, -5.0, 0.0), s, 0.8, 1.3), ((s * 4.0, 4.2, 0.0), s, 0.95, 1.6)]
    estr = massa(bm, voxel=0.08, suav_iter=6, suav_fator=0.5, laplace=12)
    for c, s, l, cp in pes:
        pe_reptil(estr, rg("garra"), c, s, l, cp, dedos=5, garra_comp=0.35)
    corpo = fundir(ESPECIE + "_Corpo_Blockout", estr, col, voxel=0.075, suav_iter=4, suav_fator=0.45, tris=16000)
    material_papel(corpo, "escama")
    esc = rg("escama")                                         # osteodermos em escudos: 4 fileiras no dorso, 2 na cauda
    for i in range(11):
        y = -5.2 + 1.1 * i
        ztop = 5.55 - 0.004 * y * y
        for xo in (-1.5, -0.55, 0.55, 1.5):
            z = ztop - 0.12 * abs(xo)
            elipsoide(esc, (xo, y, z), (0.36, 0.45, 0.2), rot=(0, xo * 12, 0), u=8, v=4)
            chifre(esc, (xo, y, z + 0.1), [(xo, y + 0.1, z + 0.38)], 0.16, 0.03, seg=6)
    for i in range(10):                                        # crista dupla da cauda
        y = 6.6 + 1.0 * i; z = 5.45 - 0.33 * i
        for xo in (-0.4, 0.4):
            lamina(esc, (xo, y, z - 0.2), 0.75 - 0.05 * i, 0.7, 0.1, incl=0.4)
    for s in (1, -1):                                          # dentes ao longo da maxila e da mandibula
        for i in range(12):
            y = -8.3 - 0.42 * i
            w = 1.25 - 0.045 * i
            chifre(rg("osso"), (s * w * 0.95, y, 3.05), [(s * w * 0.97, y, 2.75)], 0.09, 0.01, seg=6)
    olhos(rg("olho"), (0.85, -8.45, 4.9), 0.22)
    rg.criar(ESPECIE, col)
    humano(7.0, -12.0)
    md = medidas(col)
    md.update({"ombro_alvo": 5.8, "comprimento_alvo": 30, "oficial": "5-7 ombro; 24-32 comprimento"})
    registrar(ESPECIE, pose, md)
    print("MEDIDAS", md)


if __name__ == "__main__":
    a = args()
    construir(a.pose)
    salvar(a.out)
