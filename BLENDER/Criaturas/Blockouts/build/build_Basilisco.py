# Basilisco (Pantano Nebuloso). RPG_02: "quadrupede gigante, escamas, cristas e cauda longa"; 7-10 studs ATE OS OMBROS
# (usado 8,3); comprimento NAO fixado -> ~27 PROVISORIO pela referencia.
# REFINADO: cabeca reptiliana angulosa com arcadas pesadas (olhar ameacador oficial), cristas em LAMINAS espinhosas,
# patas semi-eretas com cotovelo e 5 dedos com garras, pescoco mais grosso, cauda com ponta enrolada (painel oficial).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from mathutils import Vector
from blockout_lib import *

ESPECIE = "Basilisco"


def construir(pose):
    cena_nova()
    col = colecao(ESPECIE)
    rg = Partes()
    bm = bmesh.new()
    elipsoide(bm, (0, 0.0, 5.5), (3.1, 5.4, 2.8))            # tronco pesado: topo ~8,3
    elipsoide(bm, (0, -3.8, 5.6), (2.9, 2.4, 2.8))           # peito
    elipsoide(bm, (0, 4.2, 5.8), (2.7, 2.6, 2.5))            # pelve
    trilha(bm, [(0, -4.8, 7.2, 1.85), (0, -6.4, 8.6, 1.45), (0, -7.6, 9.6, 1.15)], achatar=(0.95, 0.9), passo=0.25)   # pescoco reptiliano
    elipsoide(bm, (0, -8.4, 9.85), (1.25, 1.7, 0.78))        # cranio baixo e largo (reptil)
    trilha(bm, [(0, -9.4, 9.75, 0.95), (0, -10.8, 9.55, 0.7), (0, -11.8, 9.4, 0.45)], achatar=(1.3, 0.5), passo=0.12)   # focinho longo e chato
    trilha(bm, [(0, -8.6, 9.15, 0.9), (0, -11.6, 9.0, 0.42)], achatar=(1.35, 0.42), passo=0.12)   # mandibula plana
    for s in (1, -1):
        elipsoide(bm, (s * 1.05, -8.3, 9.4), (0.45, 0.9, 0.55))   # musculo da mandibula alargando a nuca
    for s in (1, -1):
        elipsoide(bm, (s * 0.8, -9.0, 10.45), (0.42, 0.75, 0.28))   # arcadas pesadas sobre os olhos (olhar ameacador)
    trilha(bm, [(0, 6.2, 6.3, 1.7), (0, 9.0, 5.6, 1.25), (0, 12.0, 5.0, 0.92), (0, 14.4, 5.0, 0.66), (0, 15.9, 6.2, 0.5),
                (0, 15.8, 7.6, 0.4), (0, 14.9, 7.9, 0.32), (0, 14.4, 7.2, 0.25)], achatar=(0.8, 1.0), passo=0.25)
    pes = []
    for s in (1, -1):
        cadeia(bm, [(s * 2.6, -3.8, 5.0, 1.15), (s * 3.4, -3.5, 3.0, 0.85), (s * 3.3, -4.0, 0.85, 0.6)], seg=18)
        elipsoide(bm, (s * 3.0, -3.6, 4.2), (0.85, 0.95, 1.0), rot=(0, s * 30, 0))   # umero lateral (reptil semi-ereto)
        cadeia(bm, [(s * 2.6, 4.2, 5.2, 1.35), (s * 3.4, 3.2, 3.1, 0.95), (s * 3.3, 4.6, 0.9, 0.62)], seg=18)
        elipsoide(bm, (s * 3.0, 3.9, 4.5), (1.05, 1.4, 1.3), rot=(15, 0, s * 15))
        pes += [((s * 3.25, -4.5, 0.0), s, 1.0, 1.45), ((s * 3.25, 4.15, 0.0), s, 1.05, 1.6)]
    estr = massa(bm, voxel=0.08, suav_iter=6, suav_fator=0.5, laplace=12)
    for c, s, l, cp in pes:
        pe_reptil(estr, rg("garra"), c, s, l, cp, dedos=5, garra_comp=0.42, abertura=44)
    corpo = fundir(ESPECIE + "_Corpo_Blockout", estr, col, voxel=0.075, suav_iter=4, suav_fator=0.45, tris=16000)
    material_papel(corpo, "escama")
    linha = [(0, -6.6, 9.9), (0, -5.4, 8.9), (0, -4.0, 8.25), (0, -2.6, 8.2), (0, -1.2, 8.25), (0, 0.2, 8.25), (0, 1.6, 8.2),
             (0, 3.0, 8.1), (0, 4.4, 8.0), (0, 5.8, 7.6), (0, 7.2, 6.9), (0, 8.6, 6.6), (0, 10.0, 6.1), (0, 11.4, 5.75)]
    alt = [0.9, 1.2, 1.6, 2.0, 2.2, 2.2, 2.1, 1.9, 1.7, 1.4, 1.2, 1.0, 0.8, 0.6]
    for p, h in zip(linha, alt):                                # cristas em laminas espinhosas
        lamina(rg("escama"), (p[0], p[1], p[2] - 0.25), h, 1.0, 0.13, incl=0.55)
    for s in (1, -1):                                           # espinhos menores nos flancos do pescoco
        for i in range(4):
            b = Vector((s * 1.3, -6.0 + 0.7 * i, 9.0 - 0.6 * i))
            chifre(rg("osso"), b, [b + Vector((s * 0.4, 0.4, 0.5))], 0.18, 0.02, seg=6)
    olhos(rg("olho"), (0.85, -9.1, 10.2), 0.19)
    rg.criar(ESPECIE, col)
    humano(6.0, -11.0)
    md = medidas(col)
    md.update({"ombro_alvo": 8.3, "oficial": "7-10 ombro; comprimento nao fixado", "provisorio": "comprimento ~27 pela referencia"})
    registrar(ESPECIE, pose, md)
    print("MEDIDAS", md)


if __name__ == "__main__":
    a = args()
    construir(a.pose)
    salvar(a.out)
