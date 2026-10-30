# Bufalo Colossal (Planicies Douradas). RPG_02: "bisao gigante: corcova pronunciada, pelagem espessa e chifres
# grandes"; 14-18 studs ate os ombros (usado 16 no topo da corcova).
# Matte lateral (cabeca a direita): 0,04638 stud/px, eixo y=0 na coluna 239, chao na linha 355.
# Anatomia bovina/bisao: dianteiro macico com capa de pelo, traseiro menor, cabeca baixa com barba, chifres curtos
# curvos (parte rigida separada), cauda fina com tufo. Largura pela anatomia (# inferred).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from blockout_lib import *

ESPECIE = "Bufalo_Colossal"
PASSADA_REF = {"DE": -4, "DD": 8, "TE": 18, "TD": -15}


def construir(pose):
    cena_nova()
    col = colecao(ESPECIE)
    bm = bmesh.new()
    elipsoide(bm, (0, -1.0, 10.0), (3.6, 5.0, 5.2))          # dianteiro macico
    elipsoide(bm, (0, 0.0, 12.6), (2.8, 3.4, 3.4))           # corcova: topo ~16 (x 240 px)
    elipsoide(bm, (0, 2.6, 12.0), (2.7, 3.2, 1.9))           # corcova descendo longa para tras
    elipsoide(bm, (0, 3.0, 8.3), (3.2, 4.2, 3.9))            # barril/ventre (fundo ~4,4)
    elipsoide(bm, (0, 6.6, 8.6), (2.8, 2.6, 2.8))            # traseiro menor: topo ~11,4
    cadeia(bm, [(0, -4.4, 9.4, 3.0), (0, -6.4, 7.8, 2.4)])   # pescoco baixo
    elipsoide(bm, (0, -7.6, 6.9), (2.0, 2.0, 2.4))           # cabeca larga e baixa
    elipsoide(bm, (0, -9.4, 6.5), (1.5, 1.3, 1.4))           # focinho (meia altura, x 445-470 px)
    elipsoide(bm, (0, 8.0, 8.4), (2.4, 1.8, 2.4))            # nadega (traseira mais longa)
    for s in (1, -1):
        elipsoide(bm, (s * 1.9, -7.3, 8.1), (0.55, 0.35, 0.4))   # orelhas
    pelo = bmesh.new()                                        # capa de pelo, barba e "calcas" das patas dianteiras
    elipsoide(pelo, (0, 2.2, 4.6), (3.0, 4.2, 1.9))          # pelo pendente do ventre (fundo ~2,7)
    elipsoide(pelo, (0, -3.4, 8.7), (3.9, 2.8, 4.6))
    elipsoide(pelo, (0, -7.0, 9.1), (2.4, 2.1, 2.4))         # topete sobre a cabeca
    elipsoide(pelo, (0, -8.4, 4.9), (1.2, 1.3, 1.6))         # barba
    for s in (1, -1):
        elipsoide(pelo, (s * 2.2, -3.3, 4.6), (1.45, 1.6, 2.2))
    juntar(bm, massa(pelo, voxel=0.12, suav_iter=24, suav_fator=0.75))
    cadeia(bm, [(0, 9.0, 10.3, 0.45), (0, 9.9, 8.2, 0.32), (0, 10.2, 5.8, 0.28)])   # cauda fina
    elipsoide(bm, (0, 10.2, 4.8), (0.42, 0.45, 0.95))        # tufo
    membros = []
    for s, l in ((1, "E"), (-1, "D")):
        membros.append({"pivo": (s * 2.2, -3.0, 7.5), "chave": "D" + l,
                        "cad": [(s * 2.3, -3.0, 6.5, 1.5), (s * 2.1, -2.8, 4.0, 1.1), (s * 2.0, -3.2, 1.3, 0.75), (s * 2.0, -3.4, 0.72, 0.7)],
                        "musc": [], "pe": (s * 2.0, -3.45, 0.0), "s": s})
        membros.append({"pivo": (s * 2.1, 7.0, 8.0), "chave": "T" + l,
                        "cad": [(s * 2.1, 7.0, 7.0, 1.6), (s * 2.1, 6.0, 4.6, 1.15), (s * 1.9, 7.2, 2.2, 0.7), (s * 1.9, 6.7, 0.67, 0.65)],
                        "musc": [((s * 2.1, 6.8, 6.0), (1.4, 1.9, 2.4), (10, 0, 0))], "pe": (s * 1.9, 6.6, 0.0), "s": s})
    rg = Partes()
    mm = posar_membros(membros, PASSADA_REF, pose)
    for m in mm:
        cadeia(bm, m["cad"])
        for c, r, rot in m["musc"]:
            elipsoide(bm, c, r, rot)
    estr = massa(bm, voxel=0.12, suav_iter=8, suav_fator=0.55, laplace=14)
    for s in (1, -1):                                          # marcos osseos: arcada, maca do rosto, joelhos, ilio
        elipsoide(estr, (s * 1.3, -8.6, 7.6), (0.6, 0.8, 0.45))
        elipsoide(estr, (s * 1.25, -9.3, 6.4), (0.5, 0.9, 0.5))
        elipsoide(estr, (s * 2.15, -2.9, 2.6), (0.65, 0.7, 0.7))
        elipsoide(estr, (s * 1.85, 6.4, 9.7), (0.7, 1.2, 0.5))
    for m in mm:                                               # casco fendido (material garra/casco)
        casco_fendido(rg("garra"), m["pe"], 1.5 if m["chave"].startswith("D") else 1.35, 0.95)
    corpo = fundir(ESPECIE + "_Corpo_Blockout", estr, col, voxel=0.11, suav_iter=5, suav_fator=0.5, tris=16000)
    material_papel(corpo, "pelo")
    for s in (1, -1):                                          # chifres GRANDES curvos para fora e para cima (painel)
        chifre(rg("osso"), (s * 1.75, -7.5, 8.5), [(s * 3.3, -7.6, 8.5), (s * 4.5, -8.0, 9.1), (s * 5.0, -8.6, 10.4), (s * 4.7, -9.0, 11.7)], 0.75, 0.08, seg=14)
    olhos(rg("olho"), (1.7, -9.1, 7.2), 0.22)
    rg.criar(ESPECIE, col)
    humano(5.5, -14.0)
    md = medidas(col)
    md.update({"ombro_alvo": 16.0, "oficial": "14-18 ombro", "provisorio": "comprimento, largura e chifres pela referencia/anatomia"})
    registrar(ESPECIE, pose, md)
    print("MEDIDAS", md)


if __name__ == "__main__":
    a = args()
    construir(a.pose)
    salvar(a.out)
