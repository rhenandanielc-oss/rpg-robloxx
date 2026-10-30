# Serpente Marinha (Costas Selvagens). RPG_02: "anatomia serpentina SEM PATAS, com nadadeiras e cristas naturais";
# 30-45 studs de COMPRIMENTO (usado ~39 ao longo do corpo).
# Reconstruido: cabeca draconiana com babados, corpo longo em S horizontal (pose de nado, boa para rig em cadeia),
# crista dorsal continua, pares de nadadeiras laterais, cauda afinando sem nadadeira de peixe (painel oficial).
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bmesh
from mathutils import Vector
from blockout_lib import *

ESPECIE = "Serpente_Marinha"


def eixo(t):
    """t 0 (cabeca) -> 1 (cauda): ponto no S horizontal e raio do corpo."""
    y = -17.0 + 34.0 * t
    x = 2.6 * math.sin(t * 2.2 * math.pi)
    r = 1.15 + 0.55 * math.sin(min(1.0, t * 2.2) * math.pi * 0.5) if t < 0.45 else 1.7 * (1 - (t - 0.45) / 0.55) ** 0.9 + 0.12
    return Vector((x, y, r * 1.15)), r


def construir(pose):
    cena_nova()
    col = colecao(ESPECIE)
    bm = bmesh.new()
    pts = []
    for i in range(41):
        p, r = eixo(i / 40)
        pts.append((p.x, p.y, p.z, r))
    trilha(bm, pts, achatar=(0.8, 1.15), passo=0.3, u=18, v=9)       # secao oval vertical (hidrodinamica)
    hx, hy, hz = pts[0][0], pts[0][1], pts[0][2]
    elipsoide(bm, (hx, hy - 1.4, hz + 0.35), (1.35, 1.9, 1.1))      # cranio draconico maior
    trilha(bm, [(hx, hy - 2.9, hz + 0.2, 0.95), (hx, hy - 4.6, hz - 0.05, 0.6)], achatar=(1.1, 0.75), passo=0.15)   # focinho
    elipsoide(bm, (hx, hy - 3.1, hz - 0.65), (0.95, 1.7, 0.42))     # mandibula
    for s in (1, -1):
        elipsoide(bm, (hx + s * 0.85, hy - 2.0, hz + 1.05), (0.4, 0.8, 0.3))   # arcadas
    corpo = fundir(ESPECIE + "_Corpo_Blockout", bm, col, voxel=0.07, suav_iter=8, suav_fator=0.55, tris=15000)
    material_papel(corpo, "escama")
    pr = Partes()
    olhos(pr("olho"), (hx + 0.8, hy - 2.2, hz + 0.75), 0.17)
    for s in (1, -1):                                                # dentes
        for i in range(7):
            y = hy - 2.3 - 0.33 * i
            chifre(pr("osso"), (hx + s * (0.75 - 0.05 * i), y, hz - 0.3), [(hx + s * (0.75 - 0.05 * i), y, hz - 0.58)], 0.07, 0.01, seg=5)
    pr.criar(ESPECIE, col)
    rg = bmesh.new()                                                 # babados/espinhos da cabeca e crista dorsal
    for s in (1, -1):
        for k, (dz, dy) in enumerate(((0.6, 0.2), (0.1, 0.6), (-0.4, 0.9))):
            b = Vector((hx + s * 0.8, hy - 0.8, hz + dz))
            chifre(rg, b, [b + Vector((s * 0.7, 1.0 + dy, 0.4 - 0.2 * k)), b + Vector((s * 1.2, 2.1 + dy, 0.6 - 0.3 * k))], 0.28, 0.03, seg=8)
    base = [(pts[i][0], pts[i][1], pts[i][2] + pts[i][3] * 0.9) for i in range(1, 34, 2)]
    fileira(rg, base, [0.9 + 0.5 * math.sin(math.pi * i / 16) for i in range(len(base))], inclinar=(0, 0.9, 0), r0=0.35, seg=6)
    rig = rigida(ESPECIE + "_Cristas_Blockout", rg, col)
    material_papel(rig, "osso")
    for k, i in enumerate((6, 14, 22)):                              # 3 pares de nadadeiras laterais (membranas)
        p, r = eixo(i / 40)
        for s in (1, -1):
            b = Vector((p.x + s * r * 0.8, p.y, p.z - r * 0.2))
            sz = 1.7 - 0.3 * k
            membrana(ESPECIE + "_Nadadeira_%d_%s_Blockout" % (k, "E" if s > 0 else "D"), col,
                     [b + Vector((0, -0.9 * sz, 0)), b + Vector((s * 2.2 * sz, 0.2, -0.4 * sz)), b + Vector((s * 1.4 * sz, 1.6 * sz, -0.3)),
                      b + Vector((0, 1.1 * sz, 0))], b, esp=0.15)
    for ob in col.objects:
        if "Nadadeira" in ob.name:
            material_papel(ob, "membrana")
    humano(7.0, -12.0)
    md = medidas(col)
    comp = sum((Vector(a[:3]) - Vector(b[:3])).length for a, b in zip(pts, pts[1:])) + 3.7
    md.update({"comprimento_ao_longo_do_corpo": round(comp, 1), "oficial": "30-45 comprimento (sem patas)"})
    registrar(ESPECIE, pose, md)
    print("MEDIDAS", md)


if __name__ == "__main__":
    a = args()
    construir(a.pose)
    salvar(a.out)
