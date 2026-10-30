# Leao Solar v2 (corrige o blockout v1 reprovado: cabeca grande, juba oval, peito estreito, patas finas, cauda artificial).
# Medidas: ref/Leao_Solar_matte.png (vista lateral esquerda), S = 0,052801 stud/px, eixo y=0 na coluna 263, chao na linha 366.
# Ombro 11,5 (oficial 10-13). Largura e vista frontal: anatomia de leao (# inferred).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from mathutils import Vector
from blockout_lib import *

S = 0.052801
def px(x, h):
    return (-(x - 263) * S, h * S)

ESPECIE = "Leao_Solar"
PASSADA_REF = {"DE": -15, "DD": 15, "TE": 22, "TD": -26}     # graus, + = para tras (apoios medidos no matte)


def tronco(bm):
    elipsoide(bm, (0, -3.2, 8.0), (2.55, 4.0, 3.2))            # caixa toracica funda
    elipsoide(bm, (0, -6.3, 6.6), (2.3, 1.6, 2.4))             # peitoral entre as patas
    elipsoide(bm, (0, 1.0, 8.1), (2.1, 3.2, 2.55))             # flanco recolhido (barriga ~5,3)
    elipsoide(bm, (0, 0.4, 9.6), (1.7, 3.8, 1.6))              # lombo: topo 11,5
    elipsoide(bm, (0, 3.8, 8.5), (2.35, 2.4, 2.2))             # pelve/garupa inclinada para a cauda
    for s in (1, -1):
        elipsoide(bm, (s * 1.9, -4.5, 9.0), (1.0, 2.0, 2.5), rot=(-18, 0, 0))   # escapula/ombro musculoso
        elipsoide(bm, (s * 1.75, 4.7, 7.1), (1.15, 2.25, 2.75), rot=(15, 0, 0))  # coxa


def pescoco_cabeca(bm):
    cadeia(bm, [(0, -5.6, 9.0, 2.4), (0, -8.2, 10.9, 2.0), (0, -9.9, 11.7, 1.6)])
    elipsoide(bm, (0, -10.9, 12.1), (1.6, 1.5, 1.45))          # cranio (comprimento da cabeca ~0,35 do ombro)
    elipsoide(bm, (0, -11.5, 12.55), (1.15, 0.75, 0.45))       # testa/arcada
    for s in (1, -1):
        elipsoide(bm, (s * 1.0, -11.6, 11.35), (0.7, 0.9, 0.75))    # bochechas
        elipsoide(bm, (s * 1.15, -10.5, 13.45), (0.5, 0.3, 0.55))   # orelhas curtas e redondas, visiveis acima da face
    elipsoide(bm, (0, -12.45, 11.1), (1.12, 1.05, 0.85))       # focinho largo e quadrado
    elipsoide(bm, (0, -13.25, 11.32), (0.55, 0.32, 0.4))       # trufa do nariz
    elipsoide(bm, (0, -12.3, 10.25), (0.85, 1.1, 0.55))        # queixo/mandibula forte
    for s in (1, -1):
        elipsoide(bm, (s * 0.55, -12.85, 10.95), (0.5, 0.55, 0.45))   # almofadas dos bigodes
    elipsoide(bm, (0, -12.3, 11.75), (0.7, 1.0, 0.4))           # dorso do nariz largo


def juba():
    """Juba como UMA massa continua (fundida e bem suavizada a parte): colar em volta do rosto,
    volume sobre o pescoco e a cernelha, caimento nos ombros e babado no peito ate entre as patas."""
    bm = bmesh.new()
    anel(bm, (0, -9.5, 12.0), 2.9, 3.05, 1.3, n=32)                # colar em volta do rosto (cabeca projeta ~2,5 a frente)
    anel(bm, (0, -8.4, 12.4), 3.15, 3.6, 1.55, n=32)               # segunda camada, mais atras e mais larga
    elipsoide(bm, (0, -7.4, 14.9), (3.5, 3.6, 3.75))               # volume superior ATRAS da cabeca: topo ~18,6
    elipsoide(bm, (0, -9.9, 15.0), (2.6, 1.6, 2.0))                # coroa logo atras das orelhas (testa livre)
    elipsoide(bm, (0, -10.4, 8.6), (1.9, 1.3, 1.7))                # babado sob o queixo
    elipsoide(bm, (0, -5.4, 13.4), (3.2, 3.2, 2.7))                # descendo para a cernelha
    elipsoide(bm, (0, -2.9, 12.2), (2.5, 2.2, 1.5))                # termina na cernelha (y ~ -1,2)
    for s in (1, -1):
        elipsoide(bm, (s * 2.55, -7.2, 10.6), (1.6, 3.1, 3.6))     # caimento sobre os ombros
        elipsoide(bm, (s * 2.1, -10.5, 11.6), (1.25, 1.15, 2.4))   # costeletas: parte da frente do colar, ao lado da face
    elipsoide(bm, (0, -9.0, 8.0), (2.6, 1.9, 3.3))                 # babado do peito
    elipsoide(bm, (0, -7.8, 4.9), (2.0, 1.7, 2.4))                 # entre as patas (fundo ~2,5)
    for i in range(14):                                            # franja de mechas grandes no topo/traseira (nao na frente da face)
        t = math.pi * (0.3 + 0.85 * i / 13)
        elipsoide(bm, (0, -8.6 - 4.0 * math.cos(t) * 0.55, 13.0 + 4.95 * math.sin(t)), (2.4, 1.15, 1.15), u=16, v=8)
    juba_lisa = massa(bm, voxel=0.15, suav_iter=6, suav_fator=0.6, laplace=10)
    mech = bmesh.new()                                             # mechas em camadas (volume legivel sem pelo fino)
    import random
    rnd = random.Random(7)
    for camada, (cy, rx, rz, tam) in enumerate(((-10.2, 3.9, 4.0, 1.0), (-8.8, 4.4, 4.7, 1.2), (-7.0, 4.5, 5.0, 1.3), (-5.0, 3.9, 4.2, 1.15))):
        n = 16 + 2 * camada
        for i in range(n):
            a = 2 * math.pi * i / n + rnd.uniform(-0.12, 0.12)
            ca, sa = math.cos(a), math.sin(a)
            if sa < -0.55 and camada == 0:
                continue                                           # deixa livre o queixo/frente da face
            base = Vector((rx * ca, cy, 12.6 + rz * sa))
            fora = Vector((ca, 0.55, sa - 0.45)).normalized()      # mechas caem para tras e para baixo
            L = tam * rnd.uniform(1.0, 1.5)
            c = base + fora * L * 0.55
            rot_x = -math.degrees(math.atan2(fora.z, fora.y))
            rot_y = math.degrees(math.atan2(fora.x, max(0.2, abs(fora.z))))
            elipsoide(mech, c, (0.42 * tam, 0.55 * L, 0.42 * tam), rot=(rot_x, rot_y, 0), u=10, v=6)
            chifre(mech, c + fora * L * 0.3, [c + fora * L * 0.75], 0.32 * tam, 0.05, seg=6)   # ponta afilada da mecha
    for i in range(10):                                            # babado do peito em mechas pendentes
        x = (i - 4.5) * 0.45
        elipsoide(mech, (x, -9.3 + 0.1 * abs(x), 6.0 - 0.15 * abs(x)), (0.4, 0.6, 1.3), rot=(-15, 0, x * 6), u=10, v=6)
        chifre(mech, (x, -9.1, 5.0), [(x * 1.05, -8.8, 3.8)], 0.3, 0.05, seg=6)
    mech.free()                                                    # mechas geometricas reprovadas (ficam espinhosas); detalhe vai na textura
    return juba_lisa


def membros(pose):
    """Cada membro: cadeia (x,y,z,r) + musculos (centro, raios, rot) com pivo para a pose de comparacao."""
    out = []
    for s, l in ((1, "E"), (-1, "D")):
        d = {"pivo": (s * 2.0, -6.0, 8.6), "cad": [(s * 2.0, -6.0, 7.6, 1.45), (s * 1.95, -5.2, 4.9, 1.15),
             (s * 1.9, -5.7, 3.2, 1.05), (s * 1.85, -6.3, 1.4, 0.82), (s * 1.85, -6.8, 0.65, 0.72)],
             "musc": [((s * 1.95, -5.5, 4.0), (1.25, 1.3, 1.9), (0, 0, 0))], "pe": (s * 1.85, -7.0, 0.0), "s": s,
             "chave": "D" + l}
        t = {"pivo": (s * 1.9, 5.0, 9.0), "cad": [(s * 1.9, 5.0, 8.4, 1.5), (s * 2.0, 3.3, 5.7, 1.2),
             (s * 1.9, 6.0, 2.4, 0.62), (s * 1.85, 5.4, 0.7, 0.55)],
             "musc": [((s * 1.9, 4.8, 4.0), (0.9, 1.1, 1.6), (-45, 0, 0))], "pe": (s * 1.85, 4.95, 0.0), "s": s,
             "chave": "T" + l}
        out += [d, t]
    return posar_membros(out, PASSADA_REF, pose)


def cauda(bm):
    linha = [(152, 176), (130, 148), (108, 118), (85, 100), (62, 92), (36, 98), (19, 118), (13, 145), (19, 172), (28, 194), (42, 206)]
    pts = []
    for i, (x, h) in enumerate(linha):
        y, z = px(x, h)
        pts.append((0, y, z, 0.55 - 0.23 * i / (len(linha) - 1)))
    cadeia(bm, pts, seg=16)
    tufo = bmesh.new()                                                     # tufo em pluma, fundido a parte
    elipsoide(tufo, (0, *px(60, 214)), (0.8, 1.0, 1.9), rot=(-10, 0, 0))
    elipsoide(tufo, (0, *px(60, 252)), (0.6, 1.35, 0.85), rot=(28, 0, 0))  # pluma diagonal (x 25-90, h 242-262)
    juntar(bm, massa(tufo, voxel=0.08, suav_iter=24, suav_fator=0.8))


def construir(pose):
    cena_nova()
    col = colecao(ESPECIE)
    bm = bmesh.new()
    rg = Partes()
    tronco(bm); pescoco_cabeca(bm); cauda(bm)
    mm = membros(pose)
    for m in mm:
        cadeia(bm, m["cad"])
        for c, r, rot in m["musc"]:
            elipsoide(bm, c, r, rot)
    estr = massa(bm, voxel=0.11, suav_iter=6, suav_fator=0.5, laplace=12)     # tecido mole unido
    for s in (1, -1):                                                          # marcos osseos
        elipsoide(estr, (s * 2.15, -4.4, 10.6), (0.35, 1.6, 0.3), rot=(-20, 0, 0))   # espinha da escapula
        elipsoide(estr, (s * 2.05, -5.0, 4.95), (0.55, 0.6, 0.55))                   # cotovelo
        elipsoide(estr, (s * 1.55, 3.6, 9.75), (0.55, 1.1, 0.4))                     # crista iliaca
    for m in mm:                                                               # patas felinas largas (4 dedos + garras retrateis)
        f = m["chave"].startswith("D")
        pata_digitigrada(estr, rg("garra"), m["pe"], m["s"], 1.25 if f else 1.05, 1.7 if f else 1.45, dedos=4, garra_comp=0.22)
    juntar(estr, juba())
    corpo = fundir(ESPECIE + "_Corpo_Blockout", estr, col, voxel=0.1, suav_iter=5, suav_fator=0.5, tris=18000)
    material_papel(corpo, "pelo")
    olhos(rg("olho"), (0.62, -12.0, 12.2), 0.2)
    rg.criar(ESPECIE, col)
    humano(6.5, -9.0)
    bpy.context.scene["pose"] = pose
    md = medidas(col)
    md.update({"ombro_alvo": 11.5, "oficial": "10-13 ombro", "provisorio": "largura, comprimento e cauda pela referencia/anatomia"})
    registrar(ESPECIE, pose, md)
    print("MEDIDAS", md)


if __name__ == "__main__":
    a = args()
    construir(a.pose)
    salvar(a.out)
