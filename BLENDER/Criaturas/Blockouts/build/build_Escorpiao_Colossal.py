# Escorpiao Colossal (Deserto de Cristal). RPG_02: "comprimento de 16-24 studs com cauda estendida (NAO altura); anatomia
# de escorpiao com oito pernas, pincas e cauda segmentada". Altura corporal PENDENTE no documento (provisoria aqui).
# REFINADO: exoesqueleto ARTICULADO - cada placa/segmento e rigido e separado por juntas (bom para rig: 1 osso por placa),
# pincas massivas (mao + dedo fixo + dedo movel com dentes), pernas com 4 segmentos e juntas, carapaca com bordas e espinhos,
# cauda erguida com telson e ferrao em gancho (painel oficial).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from mathutils import Vector
from blockout_lib import *

ESPECIE = "Escorpiao_Colossal"


def construir(pose):
    cena_nova()
    col = colecao(ESPECIE)
    rg = Partes()
    bm = bmesh.new()                                           # corpo articulado (suavizacao leve para manter segmentos)
    elipsoide(bm, (0, -2.4, 2.75), (2.6, 2.5, 1.1))            # prossoma
    elipsoide(bm, (0, -3.2, 3.5), (1.6, 1.3, 0.5))             # elevacao ocular
    for i in range(6):                                         # mesossoma: 6 placas com sulcos entre elas
        y = -0.6 + 1.05 * i
        elipsoide(bm, (0, y, 2.8 - 0.05 * i), (2.85 - 0.12 * i, 0.62, 1.12 - 0.04 * i))
    arco = [(0, 5.8, 3.0), (0, 7.2, 4.6), (0, 7.9, 6.7), (0, 7.5, 8.8), (0, 6.2, 10.3), (0, 4.5, 10.8)]
    for i, (a, b) in enumerate(zip(arco, arco[1:])):           # metassoma: 5 segmentos com juntas
        A, Bv = Vector(a), Vector(b)
        elipsoide(bm, A.lerp(Bv, 0.5), (1.05 - 0.06 * i, (Bv - A).length * 0.62, 0.95 - 0.05 * i),
                  rot=(math.degrees(math.atan2(Bv.z - A.z, Bv.y - A.y)), 0, 0))
    trilha(bm, [(0, 5.0, 2.9, 0.75)] + [(p[0], p[1], p[2], 0.62 - 0.04 * i) for i, p in enumerate(arco)], passo=0.4, u=14, v=7)
    elipsoide(bm, (0, 3.6, 10.1), (0.85, 1.05, 0.85))          # telson
    for s in (1, -1):
        cadeia(bm, [(s * 1.6, -4.0, 2.6, 0.7), (s * 3.2, -5.4, 3.0, 0.65), (s * 3.6, -7.0, 3.0, 0.75)], seg=14)
        elipsoide(bm, (s * 3.5, -8.9, 3.0), (1.65, 2.4, 1.25))     # mao da pinca MASSIVA
        for k, (y0, dy) in enumerate(((-2.8, -1.6), (-1.6, -0.5), (-0.3, 0.6), (1.0, 1.8))):
            r = 0.62 - 0.03 * k
            p0, p1, p2, p3 = (s * 2.3, y0, 2.3), (s * 4.3, y0 + dy * 0.6, 3.8), (s * 6.0, y0 + dy, 1.6), (s * 6.5, y0 + dy * 1.2, 0.25)
            cadeia(bm, [p0 + (r,), p1 + (r * 0.92,), p2 + (r * 0.72,), p3 + (r * 0.45,)], seg=12)
            elipsoide(bm, p1, (r * 1.15, r * 1.15, r * 1.15), u=12, v=6)   # junta femur/tibia
            elipsoide(bm, p2, (r * 0.9, r * 0.9, r * 0.9), u=12, v=6)
    corpo = fundir(ESPECIE + "_Corpo_Blockout", bm, col, voxel=0.06, suav_iter=4, suav_fator=0.45, tris=16000)
    material_papel(corpo, "quitina")
    for s in (1, -1):                                          # dedos das pincas com dentes
        fixo = [(s * 2.8, -10.8, 3.0), (s * 2.6, -12.0, 3.05), (s * 3.0, -13.0, 3.0)]
        movel = [(s * 4.3, -10.8, 3.0), (s * 4.6, -12.0, 3.05), (s * 4.1, -12.9, 3.0)]
        chifre(rg("quitina"), fixo[0], fixo[1:], 0.62, 0.06, seg=10)
        chifre(rg("quitina"), movel[0], movel[1:], 0.58, 0.06, seg=10)
        for t in range(4):
            y = -11.0 - 0.45 * t
            chifre(rg("garra"), (s * 3.05, y, 3.0), [(s * 3.35, y - 0.1, 3.0)], 0.1, 0.01, seg=5)
    for i in range(5):                                         # espinhos na carapaca e no metassoma
        for s in (1, -1):
            y = -0.6 + 1.05 * i
            b = Vector((s * (2.4 - 0.1 * i), y, 3.3))
            chifre(rg("garra"), b, [b + Vector((s * 0.3, 0.2, 0.55))], 0.16, 0.02, seg=6)
    for i, p in enumerate(arco[1:-1]):
        b = Vector(p) + Vector((0, 0.4, 0.7))
        chifre(rg("garra"), b, [b + Vector((0, 0.5, 0.6))], 0.18, 0.02, seg=6)
    chifre(rg("garra"), (0, 2.9, 9.8), [(0, 2.1, 9.1), (0, 1.9, 8.2), (0, 2.3, 7.7)], 0.45, 0.03, seg=10)   # ferrao em gancho
    olhos(rg("olho"), (0.5, -3.6, 3.95), 0.18)
    rg.criar(ESPECIE, col)
    humano(9.0, -10.0)
    md = medidas(col)
    md.update({"comprimento_estendido_estimado": 22.5, "oficial": "16-24 comprimento com cauda estendida",
               "provisorio": "altura corporal (PENDENTE no RPG_02) e largura"})
    registrar(ESPECIE, pose, md)
    print("MEDIDAS", md)


if __name__ == "__main__":
    a = args()
    construir(a.pose)
    salvar(a.out)
