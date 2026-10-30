# Urso Silvestre (Floresta Ancestral). RPG_02: 8-10 studs ate os ombros (usado 9,0 no topo da corcova).
# Matte lateral (cabeca a direita): 0,02687 stud/px, eixo y=0 na coluna 273, chao na linha 349.
# Anatomia ursidea: corcova escapular, cabeca abaixo da corcova, focinho medio, orelhas redondas, patas plantigradas,
# cauda curta. Largura (~0,55 do ombro) pela anatomia (# inferred).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from blockout_lib import *

ESPECIE = "Urso_Silvestre"
PASSADA_REF = {"DE": -4, "DD": 25, "TE": 16, "TD": -22}


def construir(pose):
    cena_nova()
    col = colecao(ESPECIE)
    bm = bmesh.new()
    elipsoide(bm, (0, 0.3, 5.2), (2.6, 5.4, 2.8))           # tronco macico: topo ~8,0, barriga ~2,4
    elipsoide(bm, (0, 4.4, 4.6), (2.5, 2.6, 2.3))           # garupa caindo para tras: topo ~6,9 em y +4,4, traseira ~ +7,0
    elipsoide(bm, (0, -3.5, 7.0), (2.2, 2.2, 2.1))          # corcova escapular: topo ~9,1
    elipsoide(bm, (0, 0.0, 6.8), (2.3, 3.0, 1.6))           # dorso: topo ~8,3 (ref 292-307 px)
    elipsoide(bm, (0, -3.4, 5.5), (2.2, 1.2, 2.2))          # peito recuado sob a cabeca (frente ~ -4,6)
    cadeia(bm, [(0, -4.3, 7.2, 1.7), (0, -5.4, 7.1, 1.45)])  # pescoco curto e grosso
    elipsoide(bm, (0, -5.9, 7.25), (1.25, 1.3, 1.15))       # cranio (topo ~8,4)
    trilha(bm, [(0, -6.5, 7.0, 0.78), (0, -7.1, 6.8, 0.62), (0, -7.55, 6.65, 0.46)], achatar=(0.95, 0.85), passo=0.15)   # focinho ursideo alongado
    elipsoide(bm, (0, -7.75, 6.72), (0.36, 0.2, 0.28))      # nariz
    elipsoide(bm, (0, -6.2, 7.75), (1.0, 0.9, 0.45))        # testa inclinada
    elipsoide(bm, (0, -6.7, 6.35), (0.6, 0.75, 0.38))       # mandibula
    for s in (1, -1):
        elipsoide(bm, (s * 0.85, -5.5, 8.3), (0.38, 0.22, 0.36))   # orelhas redondas
        elipsoide(bm, (s * 0.95, -6.05, 7.0), (0.55, 0.8, 0.65))   # bochechas
    elipsoide(bm, (0, 6.9, 5.2), (0.45, 0.5, 0.4))          # cauda curta
    membros = []
    for s, l in ((1, "E"), (-1, "D")):
        membros.append({"pivo": (s * 1.6, -3.4, 5.5), "chave": "D" + l,
                        "cad": [(s * 1.65, -3.4, 5.0, 1.25), (s * 1.6, -3.2, 3.0, 1.0), (s * 1.55, -3.3, 1.0, 0.78)],
                        "musc": [((s * 1.6, -3.3, 3.6), (1.0, 1.2, 1.5), (0, 0, 0)),
                                 ], "pe": (s * 1.55, -3.55, 0.0), "s": s})
        membros.append({"pivo": (s * 1.7, 4.9, 5.0), "chave": "T" + l,
                        "cad": [(s * 1.75, 4.9, 4.6, 1.4), (s * 1.7, 4.3, 2.8, 1.1), (s * 1.6, 5.2, 1.2, 0.78)],
                        "musc": [((s * 1.75, 4.7, 3.7), (1.15, 1.5, 1.6), (15, 0, 0)),
                                 ], "pe": (s * 1.6, 4.75, 0.0), "s": s})
    rg = Partes()
    mm = posar_membros(membros, PASSADA_REF, pose)
    for m in mm:
        cadeia(bm, m["cad"])
        for c, r, rot in m["musc"]:
            elipsoide(bm, c, r, rot)
    estr = massa(bm, voxel=0.07, suav_iter=8, suav_fator=0.55, laplace=14)
    for s in (1, -1):                                          # marcos: escapula sob a corcova, cotovelo, crista iliaca
        elipsoide(estr, (s * 1.9, -3.6, 7.6), (0.35, 1.3, 0.3), rot=(-15, 0, 0))
        elipsoide(estr, (s * 1.75, -3.0, 3.1), (0.5, 0.55, 0.5))
        elipsoide(estr, (s * 1.45, 4.4, 5.9), (0.45, 0.8, 0.35))
    for m in mm:                                               # pes plantigrados com garras longas (painel)
        pe_plantigrado(estr, rg("garra"), m["pe"], m["s"], 1.55, 2.2, garra_comp=0.75 if m["chave"].startswith("D") else 0.5)
    corpo = fundir(ESPECIE + "_Corpo_Blockout", estr, col, voxel=0.065, suav_iter=5, suav_fator=0.5, tris=16000)
    material_papel(corpo, "pelo")
    olhos(rg("olho"), (0.62, -6.55, 7.6), 0.16)
    rg.criar(ESPECIE, col)
    humano(4.0, -10.0)
    md = medidas(col)
    md.update({"ombro_alvo": 9.0, "oficial": "8-10 ombro", "provisorio": "comprimento e largura pela referencia/anatomia"})
    registrar(ESPECIE, pose, md)
    print("MEDIDAS", md)


if __name__ == "__main__":
    a = args()
    construir(a.pose)
    salvar(a.out)

