# Base canina dos Lobos e do Cerbero (RPG_02: Lobo Ancestral "esguio/atletico", Lobo Artico "mais robusto"; 5,5-7 studs ate
# os ombros; Cerbero "canino musculoso com tres cabecas", 12-16). Coordenadas medidas no matte do Lobo Ancestral (cernelha
# 270 px = 6,5 studs). REFINAMENTO (fase 3): mantem as massas da silhueta aprovada e acrescenta marcos osseos, grupos
# musculares, pastern/jarrete, patas digitigradas com dedos e garras, cranio em cunha e pelagem em mechas.
# Duas camadas: tecido mole/pelo fundidos e suavizados a parte; marcos osseos entram depois, com suavizacao leve.
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from mathutils import Vector, Matrix
from blockout_lib import *

PASSADA_REF = {"DE": -16, "DD": 16, "TE": 11, "TD": -11}


def cabeca(alvo, rg, P, ang=0.0, dx=0.0, esc=1.0, dz=0.0, rosnar=0.0, pitch=0.0, larg=1.0):
    """Cabeca + pescoco canino (cunha), transformados em torno da base do pescoco. Olhos vao para rg('olho')."""
    hb = bmesh.new()
    trilha(hb, [(0, -2.6, 5.6, 1.05), (0, -3.8, 6.5, 0.9), (0, -4.8, 7.0, 0.72)], passo=0.3, u=18, v=9)
    elipsoide(hb, (0, -5.15, 7.2), (0.62, 0.8, 0.66))                    # cranio (topo ~7,9)
    trilha(hb, [(0, -5.75, 6.82, 0.38), (0, -6.15, 6.6, 0.3), (0, -6.5, 6.42, 0.22)], achatar=(0.95, 0.85), passo=0.1, u=16, v=8)   # focinho longo e estreito
    elipsoide(hb, (0, -6.62, 6.42), (0.16, 0.12, 0.14))                  # trufa
    elipsoide(hb, (0, -5.95, 6.2 - 0.12 * rosnar), (0.26, 0.75, 0.22))    # mandibula
    for s in (1, -1):
        elipsoide(hb, (s * 0.4, -5.2, 6.65), (0.3, 0.45, 0.4))          # bochecha com pelo
        elipsoide(hb, (s * 0.32, -5.62, 7.42), (0.22, 0.3, 0.14))       # arcada sobre o olho (plano osseo)
        elipsoide(hb, (s * 0.5, -5.45, 6.95), (0.17, 0.45, 0.17))       # arco zigomatico
        elipsoide(hb, (s * 0.36, -5.0, 7.72), (0.2, 0.09, 0.33), rot=(-10, 0, s * -14))   # orelha ereta achatada
        elipsoide(hb, (s * 0.42, -5.05, 8.12), (0.1, 0.05, 0.2), rot=(-10, 0, s * -14))
    olho = bmesh.new()
    olhos(olho, (0.36, -5.74, 7.12), 0.085)
    base = Vector((0, -2.4, 5.6))
    if larg > 1.0:                                                     # predador macico: maxilar e nuca largos, rugas do focinho
        for s in (1, -1):
            elipsoide(hb, (s * 0.5, -5.05, 6.45), (0.42, 0.75, 0.5))
            elipsoide(hb, (s * 0.25, -6.0, 6.85), (0.2, 0.55, 0.16), rot=(-12, 0, 0))
        elipsoide(hb, (0, -4.6, 7.55), (0.7, 0.7, 0.45))
    m = (Matrix.Translation(base + Vector((dx, 0, dz))) @ Matrix.Rotation(math.radians(ang), 4, "Z") @ Matrix.Rotation(math.radians(pitch), 4, "X")
         @ Matrix.Diagonal((esc * larg, esc, esc, 1)) @ Matrix.Translation(-base))
    bmesh.ops.transform(hb, matrix=m, verts=hb.verts)
    bmesh.ops.transform(olho, matrix=m, verts=olho.verts)
    juntar(alvo, hb)
    juntar(rg("olho"), olho)


def membros_caninos(W, pr):
    out = []
    for s, l in ((1, "E"), (-1, "D")):
        out.append({"pivo": (s * 0.7 * W, -2.7, 5.0), "chave": "D" + l, "pe": (s * 0.55 * W, -3.0, 0.0), "s": s,
                    "cad": [(s * 0.72 * W, -2.7, 4.6, 0.55 * pr), (s * 0.62 * W, -2.35, 3.15, 0.4 * pr),     # ombro -> cotovelo
                            (s * 0.58 * W, -2.62, 1.0, 0.24 * pr), (s * 0.56 * W, -2.78, 0.35, 0.22 * pr)],    # carpo -> pastern inclinado                                          # pastern inclinado
                    "musc": [((s * 0.72 * W, -2.3, 4.05), (0.42 * pr, 0.55, 0.78), (20, 0, 0)),                # triceps/braco
                             ((s * 0.62 * W, -2.42, 2.45), (0.3 * pr, 0.36 * pr, 0.62), (0, 0, 0))]})          # flexores do antebraco
        out.append({"pivo": (s * 0.65 * W, 2.2, 4.8), "chave": "T" + l, "pe": (s * 0.52 * W, 2.58, 0.0), "s": s,
                    "cad": [(s * 0.65 * W, 2.2, 4.6, 0.6 * pr), (s * 0.62 * W, 1.55, 3.0, 0.45 * pr),       # quadril -> joelho
                            (s * 0.55 * W, 2.95, 1.25, 0.24 * pr), (s * 0.52 * W, 2.72, 0.33, 0.22 * pr)],     # jarrete -> metatarso                                           # metatarso
                    "musc": [((s * 0.68 * W, 2.0, 4.35), (0.52 * pr, 1.0, 1.25), (15, 0, 0)),                 # quadriceps
                             ((s * 0.6 * W, 2.75, 4.0), (0.38 * pr, 0.55, 1.0), (-10, 0, 0)),                  # isquiotibiais
                             ((s * 0.57 * W, 2.55, 2.2), (0.27 * pr, 0.36 * pr, 0.6), (-40, 0, 0))]})          # gastrocnemio
    return out


def construir(especie, pose, P):
    """P: escala (ombro/6,5), largura (robustez), colar/cauda (pelo), perna (grossura), dorso/ventre, cabecas (1|3)."""
    cena_nova()
    col = colecao(especie)
    W, k, pr = P["largura"], P["escala"], P["perna"]
    dz, V, C, T = P.get("dorso", 0.0), P.get("ventre", 0.0), P["colar"], P["cauda"]
    rg = Partes()
    mole = bmesh.new()                                                     # camada 1: massas e musculos (suaviza mais)
    elipsoide(mole, (0, -1.6, 4.65), (1.0 * W, 1.9, 1.75))                 # torax fundo
    elipsoide(mole, (0, 0.8, 5.0 + dz), (0.78 * W, 1.6, 1.15))             # cintura
    elipsoide(mole, (0, 2.0, 5.1 + dz), (0.88 * W, 1.2, 1.0))              # garupa
    if V:
        elipsoide(mole, (0, -0.2, 4.2), (0.9 * W, 2.0, 1.2 + V))
    for s in (1, -1):
        elipsoide(mole, (s * 0.7 * W, -1.9, 5.25), (0.42 * pr, 0.9, 1.0), rot=(-18, 0, 0))    # escapula/deltoide
    if P.get("cabecas", 1) == 3:                                           # Cerbero: raiz unica dos tres pescocos
        elipsoide(mole, (0, -2.9, 6.0), (1.6 * W, 1.6, 1.6))              # raiz unica e macica dos tres pescocos
        elipsoide(mole, (0, -3.3, 5.0), (1.4 * W, 1.2, 1.3))
        cabeca(mole, rg, P, 0, 0, 1.08, 0.7, rosnar=1.0, pitch=-6, larg=1.25)      # central: mais alta, dominante
        cabeca(mole, rg, P, 34, 0.66 * W, 1.0, -0.1, rosnar=1.0, pitch=8, larg=1.2)     # esquerda: mais baixa, rosnando
        cabeca(mole, rg, P, -30, -0.66 * W, 0.97, -0.55, rosnar=1.0, pitch=16, larg=1.2)  # direita: baixa, em ataque
    else:
        cabeca(mole, rg, P)
    membros = posar_membros(membros_caninos(W, pr), P.get("passada", PASSADA_REF), pose)
    for m in membros:
        cadeia(mole, m["cad"], seg=18)
        for c, r, rot in m["musc"]:
            elipsoide(mole, c, r, rot, u=18, v=9)
    pelo = bmesh.new()                                                     # pelagem em mechas grandes (sem pelo fino)
    elipsoide(pelo, (0, -3.4, 6.45), (0.95 * W * C, 1.4 * C, 1.05 * C))    # colar sobre pescoco/cernelha
    elipsoide(pelo, (0, -3.55, 4.6), (0.85 * W * C, 1.0 * C, 1.35 * C))    # peito
    elipsoide(pelo, (0, -4.4, 5.6), (0.7 * W * C, 0.8 * C, 0.95 * C))      # garganta
    elipsoide(pelo, (0, -2.1, 6.0), (1.0 * W * C, 1.1, 0.75 * C))
    for i in range(10):                                                    # mechas do colar, caindo para tras e para baixo
        a = math.pi * (0.1 + 0.8 * i / 9)
        p = Vector((math.cos(a) * 0.95 * W * C, -3.3 + 0.15 * math.sin(3 * i), 6.2 + math.sin(a) * 0.9 * C))
        elipsoide(pelo, p, (0.22 * C, 0.5 * C, 0.36 * C), rot=(35, 0, 0), u=12, v=6)
    if P.get("calcas", 0):                                                 # "calcas" de pelo nas coxas (Artico)
        for s in (1, -1):
            for j in range(3):
                elipsoide(pelo, (s * 0.85 * W, 2.4 + 0.3 * j, 3.3 - 0.35 * j), (0.32, 0.4, 0.6) , rot=(-20, 0, 0), u=12, v=6)
    cauda = [(0, 2.3, 4.9, 0.45 * T), (0, 2.85, 4.55, 0.8 * T), (0, 3.7, 3.85, 1.2 * T), (0, 4.5, 2.85, 1.0 * T),
             (0, 5.2, 2.15, 0.8 * T), (0, 5.7, 1.5, 0.7 * T), (0, 5.95, 1.1, 0.35 * T)]
    cadeia(pelo, cauda, seg=18)
    for i in range(2, 6):                                                  # mechas da cauda em pincel
        y, z, r = cauda[i][1], cauda[i][2], cauda[i][3]
        for t in (-1, 1):
            elipsoide(pelo, (t * r * 0.45, y + 0.2, z - 0.15), (r * 0.55, r * 0.6, r * 0.75), rot=(25, 0, 0), u=12, v=6)
    juntar(mole, massa(pelo, voxel=0.05, suav_iter=20, suav_fator=0.75))
    estr = massa(mole, voxel=0.05, suav_iter=6, suav_fator=0.5, laplace=12)          # tecido mole unido e suavizado
    for s in (1, -1):                                                      # camada 2: marcos osseos (suavizacao leve)
        elipsoide(estr, (s * 0.78 * W, -1.75, 5.7), (0.14, 0.75, 0.12), rot=(-25, 0, 0))     # espinha da escapula
        elipsoide(estr, (s * 0.66 * W, -1.95, 3.15), (0.2, 0.22, 0.2))                    # cotovelo (olecrano)
        elipsoide(estr, (s * 0.52 * W, 2.0, 5.65), (0.28, 0.55, 0.22))                     # crista iliaca
    for m in membros:                                                      # carpo/jarrete e patas no lugar da pose
        s = m["s"]
        if m["chave"].startswith("T"):
            j = Vector(m["cad"][2][:3])
            elipsoide(estr, j + Vector((0, 0.06, 0.04)), (0.1 * pr, 0.12, 0.13))          # calcaneo (ponta do jarrete)
        else:
            elipsoide(estr, Vector(m["cad"][2][:3]), (0.25 * pr, 0.24 * pr, 0.2))           # carpo
        pata_digitigrada(estr, rg("garra"), m["pe"], s, 0.34 * pr, 0.62 * pr, dedos=4, garra_comp=0.1 * pr)   # pata ~12% do ombro
    corpo = fundir(especie + "_Corpo_Blockout", estr, col, voxel=0.045, suav_iter=6, suav_fator=0.5, tris=14000)
    material_papel(corpo, "pelo")
    rg.criar(especie, col)
    if abs(k - 1) > 1e-3:                                                  # escala oficial da forma (ombro), todas as partes
        for ob in col.objects:
            ob.data.transform(Matrix.Diagonal((k, k, k, 1)))
    humano(-5.0 * k, -9.0 * k)
    md = medidas(col)
    md.update({"ombro_alvo": round(6.5 * k, 2), "oficial": P.get("oficial", "5,5-7 ombro"), "provisorio": "comprimento, largura e cauda pela referencia/anatomia"})
    registrar(especie, pose, md)
    print("MEDIDAS", md)
