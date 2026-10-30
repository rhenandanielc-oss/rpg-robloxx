"""Esqueletos por especie (pose neutra dos modelos refinados, em studs; frente -Y, Z para cima).
Cada esqueleto e uma lista de ossos (nome, cabeca, cauda, pai) + grupos usados pelo gerador de animacoes.
Familias: canideo, felino, plantigrado, ungulado, reptil, artropode, serpentino, marinho4, dragao, wyvern.
Coordenadas tiradas das proprias construcoes (build_*.py / lobo_base.py / dragao_base.py)."""
import math, os
from mathutils import Vector, Matrix


class Esq:
    def __init__(self, especie, familia):
        self.especie, self.familia = especie, familia
        self.ossos, self.g = [], {"coluna": [], "pescoco": [], "cauda": [], "membros": [], "asas": [], "cabecas": [],
                                   "pernas_artro": [], "pincas": [], "nadadeiras": []}

    def osso(self, nome, a, b, pai=None):
        self.ossos.append((nome, tuple(a), tuple(b), pai))
        return nome

    def cadeia(self, prefixo, pts, pai, grupo=None):
        nomes = []
        for i in range(len(pts) - 1):
            n = self.osso("%s%d" % (prefixo, i + 1), pts[i], pts[i + 1], pai)
            nomes.append(n); pai = n
        if grupo is not None:
            self.g[grupo] += nomes
        return nomes

    def escalar(self, k):
        if abs(k - 1) < 1e-6:
            return self
        self.ossos = [(n, tuple(Vector(a) * k), tuple(Vector(b) * k), p) for n, a, b, p in self.ossos]
        return self


def tronco(e, pelve, peito, n=3):
    """Raiz no chao + Quadril + coluna (n ossos) ate o peito."""
    e.osso("Raiz", (0, pelve[1], 0), (0, pelve[1], 1.0))
    p0, p1 = Vector(pelve), Vector(peito)
    pts = [p0.lerp(p1, i / n) for i in range(n + 1)]
    e.osso("Quadril", p0 + (p0 - p1).normalized() * 0.6, p0, "Raiz")
    col = e.cadeia("Coluna", pts, "Quadril", "coluna")
    return col[-1]


def cabeca(e, pescoco_pts, cranio, focinho, mand_a, mand_b, pai, sufixo=""):
    pc = e.cadeia("Pescoco" + sufixo, pescoco_pts, pai, "pescoco")
    cab = e.osso("Cabeca" + sufixo, pescoco_pts[-1], focinho, pc[-1])
    e.osso("Mandibula" + sufixo, mand_a, mand_b, cab)
    e.g["cabecas"].append((pc, cab, "Mandibula" + sufixo))
    return cab


def membro(e, nome, pts, pai, frente, lado):
    ns = e.cadeia(nome, pts, pai)
    e.g["membros"].append({"ossos": ns, "frente": frente, "lado": lado})
    return ns


def espelhar(p, s):
    return (s * p[0], p[1], p[2])


def quadrupede(e, pelve, peito, pescoco, focinho, mand, cauda, frente, tras):
    """frente/tras = pontos da perna ESQUERDA (x>0), do topo ate a ponta da pata."""
    topo = tronco(e, pelve, peito)
    cabeca(e, pescoco, None, focinho, mand[0], mand[1], topo)
    e.cadeia("Cauda", cauda, "Quadril", "cauda")
    for s, l in ((1, "E"), (-1, "D")):
        membro(e, "PernaD" + l + "_", [espelhar(p, s) for p in frente], topo, True, s)
        membro(e, "PernaT" + l + "_", [espelhar(p, s) for p in tras], "Quadril", False, s)
    return e


def canideo(especie, W=1.0, k=1.0, cabecas=1):
    e = Esq(especie, "canideo")
    topo = tronco(e, (0, 2.2, 5.0), (0, -1.9, 5.4))
    base = Vector((0, -2.4, 5.6))
    def cab(ang, dx, dz, esc, suf):
        m = Matrix.Translation(base + Vector((dx, 0, dz))) @ Matrix.Rotation(math.radians(ang), 4, "Z") @ Matrix.Diagonal((esc, esc, esc, 1)) @ Matrix.Translation(-base)
        T = lambda p: tuple(m @ Vector(p))
        cabeca(e, [T((0, -2.6, 5.6)), T((0, -3.8, 6.5)), T((0, -4.8, 7.0))], None, T((0, -6.5, 6.4)),
               T((0, -5.2, 6.3)), T((0, -6.45, 6.05)), topo, suf)
    if cabecas == 3:
        cab(0, 0, 0.35, 1.0, "_C"); cab(32, 0.62 * W, 0.0, 0.95, "_E"); cab(-32, -0.62 * W, -0.25, 0.92, "_D")
    else:
        cab(0, 0, 0, 1.0, "")
    e.cadeia("Cauda", [(0, 2.6, 4.9), (0, 3.2, 4.4), (0, 3.9, 3.6), (0, 4.6, 2.8), (0, 5.3, 2.1), (0, 5.9, 1.3)], "Quadril", "cauda")
    for s, l in ((1, "E"), (-1, "D")):
        membro(e, "PernaD" + l + "_", [(s * 0.7 * W, -2.2, 5.6), (s * 0.72 * W, -2.7, 4.6), (s * 0.62 * W, -2.35, 3.15),
                                       (s * 0.58 * W, -2.62, 1.0), (s * 0.56 * W, -2.85, 0.3), (s * 0.55 * W, -3.4, 0.12)], topo, True, s)
        membro(e, "PernaT" + l + "_", [(s * 0.65 * W, 2.2, 4.6), (s * 0.62 * W, 1.55, 3.0), (s * 0.55 * W, 2.95, 1.25),
                                       (s * 0.52 * W, 2.72, 0.33), (s * 0.52 * W, 2.15, 0.12)], "Quadril", False, s)
    return e.escalar(k)


def canideo_v3(especie="Lobo_Ancestral"):
    """Lobo Ancestral V3: mesmas cadeias/nomes do canideo (animacoes compativeis), articulacoes de lobo_v3.J."""
    suf = os.environ.get("CR_SUFIXO")
    mod = __import__({"_v5": "lobo_v5", "_v4": "lobo_v4"}.get(suf, "lobo_v3"))
    J = mod.J
    e = Esq(especie, "canideo")
    topo = tronco(e, J["pelve"], J["peito"])
    cabeca(e, J["pescoco"], None, J["focinho"], J["mand"][0], J["mand"][1], topo)
    e.cadeia("Cauda", J["cauda"], "Quadril", "cauda")
    for s, l in ((1, "E"), (-1, "D")):
        membro(e, "PernaD" + l + "_", [espelhar(p, s) for p in J["frente"]], topo, True, s)
        membro(e, "PernaT" + l + "_", [espelhar(p, s) for p in J["tras"]], "Quadril", False, s)
    if hasattr(mod, "PELO_OSSOS"):                                   # ossos secundarios de pelagem (balanco)
        e.g["pelo"] = [e.osso(n, a, b, pai) for n, a, b, pai in mod.PELO_OSSOS]
    return e


def felino():
    return quadrupede(Esq("Leao_Solar", "felino"), (0, 4.0, 8.6), (0, -4.6, 9.0),
                      [(0, -5.6, 9.0), (0, -8.2, 10.9), (0, -9.9, 11.7)], (0, -13.1, 11.1), ((0, -11.0, 10.6), (0, -13.0, 10.2)),
                      [(0, 5.9, 9.3), (0, 7.0, 7.8), (0, 8.2, 6.2), (0, 9.4, 5.3), (0, 10.6, 4.9), (0, 12.0, 5.2), (0, 12.9, 6.2),
                       (0, 13.2, 7.7), (0, 12.9, 9.1), (0, 12.2, 10.4)],
                      [(2.0, -6.0, 8.6), (1.95, -5.2, 4.9), (1.9, -5.7, 3.2), (1.85, -6.3, 1.4), (1.85, -6.8, 0.6), (1.85, -8.0, 0.3)],
                      [(1.9, 5.0, 8.4), (2.0, 3.3, 5.7), (1.9, 6.0, 2.4), (1.85, 5.4, 0.7), (1.85, 4.4, 0.3)])


def urso():
    return quadrupede(Esq("Urso_Silvestre", "plantigrado"), (0, 4.4, 5.6), (0, -3.4, 6.6),
                      [(0, -4.3, 7.2), (0, -5.4, 7.1)], (0, -7.8, 6.7), ((0, -6.2, 6.4), (0, -7.5, 6.3)),
                      [(0, 6.0, 5.4), (0, 7.2, 5.1)],
                      [(1.65, -3.4, 5.0), (1.6, -3.2, 3.0), (1.55, -3.3, 1.0), (1.55, -3.55, 0.3), (1.55, -4.7, 0.2)],
                      [(1.75, 4.9, 4.6), (1.7, 4.3, 2.8), (1.6, 5.2, 1.2), (1.6, 4.75, 0.3), (1.6, 3.6, 0.2)])


def bufalo():
    return quadrupede(Esq("Bufalo_Colossal", "ungulado"), (0, 6.6, 9.0), (0, -3.0, 11.0),
                      [(0, -4.4, 9.4), (0, -6.4, 7.8)], (0, -9.8, 5.8), ((0, -8.0, 5.4), (0, -9.6, 4.9)),
                      [(0, 9.0, 10.3), (0, 9.9, 8.2), (0, 10.2, 5.8), (0, 10.2, 4.3)],
                      [(2.3, -3.0, 6.5), (2.1, -2.8, 4.0), (2.0, -3.2, 1.3), (2.0, -3.4, 0.72), (2.0, -3.6, 0.0)],
                      [(2.1, 7.0, 7.0), (2.1, 6.0, 4.6), (1.9, 7.2, 2.2), (1.9, 6.7, 0.67), (1.9, 6.5, 0.0)])


def reptil(especie, pelve, peito, pescoco, focinho, mand, cauda, frente, tras):
    e = quadrupede(Esq(especie, "reptil"), pelve, peito, pescoco, focinho, mand, cauda, frente, tras)
    return e


def crocodilo():
    return reptil("Crocodilo_Primordial", (0, 4.8, 3.7), (0, -4.6, 3.6), [(0, -6.6, 3.7), (0, -8.0, 3.75)], (0, -13.6, 3.3),
                  ((0, -8.4, 2.75), (0, -13.1, 2.7)), [(0, 6.6, 3.7), (0, 9.5, 3.2), (0, 12.5, 2.6), (0, 15.2, 2.0), (0, 16.6, 1.7)],
                  [(2.4, -4.4, 3.2), (3.7, -4.2, 2.3), (3.7, -4.6, 0.7), (3.8, -5.7, 0.2)],
                  [(2.3, 4.4, 3.3), (3.9, 3.6, 2.4), (3.9, 4.6, 0.75), (4.0, 3.3, 0.2)])


def basilisco():
    return reptil("Basilisco", (0, 4.2, 5.8), (0, -3.8, 5.8), [(0, -4.8, 7.2), (0, -6.4, 8.8), (0, -7.5, 10.0)], (0, -10.8, 9.7),
                  ((0, -8.6, 9.3), (0, -10.6, 9.1)),
                  [(0, 6.2, 6.3), (0, 9.0, 5.6), (0, 12.0, 5.0), (0, 14.4, 5.0), (0, 15.9, 6.2), (0, 15.8, 7.6), (0, 14.9, 7.9), (0, 14.4, 7.2)],
                  [(2.6, -3.8, 5.0), (3.3, -3.4, 2.9), (3.2, -4.0, 0.85), (3.25, -5.5, 0.2)],
                  [(2.6, 4.2, 5.2), (3.3, 3.2, 3.1), (3.2, 4.6, 0.9), (3.25, 3.1, 0.2)])


def lagarto():
    return reptil("Lagarto_Cristalino", (0, 3.4, 5.0), (0, -3.8, 4.3), [(0, -5.3, 4.2), (0, -6.9, 3.8)], (0, -10.0, 3.4),
                  ((0, -8.0, 3.1), (0, -9.6, 2.9)), [(0, 5.8, 5.5), (0, 8.8, 4.5), (0, 11.6, 3.3), (0, 13.6, 2.4)],
                  [(2.7, -3.8, 3.8), (3.5, -3.8, 2.3), (3.4, -4.3, 0.75), (3.35, -5.7, 0.2)],
                  [(2.7, 3.6, 4.5), (3.6, 2.8, 2.5), (3.5, 4.0, 0.8), (3.45, 2.5, 0.2)])


def escorpiao():
    e = Esq("Escorpiao_Colossal", "artropode")
    e.osso("Raiz", (0, 0, 0), (0, 0, 1.0))
    e.osso("Corpo", (0, 4.8, 2.7), (0, -0.6, 2.8), "Raiz")
    e.g["coluna"].append("Corpo")
    pros = e.osso("Prossoma", (0, -0.6, 2.8), (0, -4.4, 2.75), "Corpo")
    e.cadeia("Cauda", [(0, 4.8, 2.7), (0, 5.8, 3.0), (0, 7.2, 4.6), (0, 7.9, 6.7), (0, 7.5, 8.8), (0, 6.2, 10.3), (0, 4.5, 10.8),
                       (0, 3.4, 10.1)], "Corpo", "cauda")
    e.osso("Ferrao", (0, 3.4, 10.1), (0, 2.1, 8.2), "Cauda7")
    for s, l in ((1, "E"), (-1, "D")):
        p = e.cadeia("Pinca" + l + "_", [(s * 1.6, -4.0, 2.6), (s * 3.2, -5.4, 3.0), (s * 3.6, -7.0, 3.0), (s * 3.5, -10.6, 3.0)], pros)
        dm = e.osso("PincaDedo" + l, (s * 4.3, -10.8, 3.0), (s * 4.1, -12.9, 3.0), p[-1])
        e.g["pincas"].append({"ossos": p, "dedo": dm, "lado": s})
        for k, (y0, dy) in enumerate(((-2.8, -1.6), (-1.6, -0.5), (-0.3, 0.6), (1.0, 1.8))):
            pts = [(s * 2.3, y0, 2.3), (s * 4.3, y0 + dy * 0.6, 3.8), (s * 6.0, y0 + dy, 1.6), (s * 6.5, y0 + dy * 1.2, 0.25)]
            ns = e.cadeia("Pata%d%s_" % (k + 1, l), pts, "Corpo" if k >= 2 else pros)
            e.g["pernas_artro"].append({"ossos": ns, "indice": k, "lado": s})
    return e


def serpente():
    e = Esq("Serpente_Marinha", "serpentino")
    pts = []
    for i in range(25):
        t = i / 24
        y = -17.0 + 34.0 * t
        x = 2.6 * math.sin(t * 2.2 * math.pi)
        r = 1.15 + 0.55 * math.sin(min(1.0, t * 2.2) * math.pi * 0.5) if t < 0.45 else 1.7 * (1 - (t - 0.45) / 0.55) ** 0.9 + 0.12
        pts.append((x, y, r * 1.15))
    e.osso("Raiz", (0, 0, 0), (0, 0, 1.0))
    hx, hy, hz = pts[0]
    corpo = e.cadeia("Coluna", list(reversed(pts[:9])), "Raiz", "coluna")         # do meio para a cabeca
    e.cadeia("Cauda", pts[8:], "Raiz", "cauda")
    cab = e.osso("Cabeca", pts[0], (hx, hy - 4.6, hz), corpo[-1])
    e.osso("Mandibula", (hx, hy - 1.6, hz - 0.5), (hx, hy - 4.4, hz - 0.7), cab)
    e.g["cabecas"].append(([], cab, "Mandibula"))
    return e


def leviata():
    e = Esq("Leviata_Jovem", "marinho4")
    e.osso("Raiz", (0, 0, 0), (0, 0, 1.0))
    col = e.cadeia("Coluna", [(0, 10.0, 7.6), (0, -2.0, 8.2), (0, -14.0, 8.0), (0, -22.0, 7.4)], "Raiz", "coluna")
    cab = e.osso("Cabeca", (0, -22.0, 7.4), (0, -36.0, 6.4), col[-1])
    e.osso("Mandibula", (0, -25.0, 4.8), (0, -35.0, 4.4), cab)
    e.g["cabecas"].append(([], cab, "Mandibula"))
    e.cadeia("Cauda", [(0, 10.0, 7.6), (0, 20.0, 6.6), (0, 29.0, 5.6), (0, 36.0, 5.0), (0, 39.0, 4.9)], "Raiz", "cauda")
    for s, l in ((1, "E"), (-1, "D")):
        for nome, pts, pai in (("NadD", [(s * 5.5, -12.0, 5.2), (s * 9.0, -11.4, 4.2), (s * 13.0, -10.4, 3.2), (s * 16.5, -9.6, 2.4)], col[1]),
                               ("NadT", [(s * 4.6, 13.0, 4.8), (s * 7.4, 13.6, 4.0), (s * 10.2, 14.4, 3.3), (s * 12.6, 15.0, 2.6)], "Raiz")):
            ns = e.cadeia(nome + l + "_", pts, pai)
            e.g["nadadeiras"].append({"ossos": ns, "frente": nome == "NadD", "lado": s})
    return e


DEDOS = [(31, 6, 35), (29, 15, 27), (22, 20, 20), (14, 19, 17)]


def asas(e, s, l, ombro, cotovelo, pulso, dedos, pai):
    braco = e.cadeia("Asa" + l + "_", [ombro, cotovelo, pulso], pai)
    ds = []
    for i, d in enumerate(dedos):
        p = Vector(pulso); q = Vector(d)
        ds.append(e.cadeia("Dedo%d%s_" % (i + 1, l), [tuple(p), tuple(p.lerp(q, 0.5)), tuple(q)], braco[-1]))
    e.g["asas"].append({"braco": braco, "dedos": ds, "lado": s})


def dragao(especie, W=1.0, N=1.0):
    e = Esq(especie, "dragao")
    topo = tronco(e, (0, 9.0, 15.0), (0, -8.0, 16.5))
    base = Vector((0, -12.0, 19.0))
    nk = [tuple(base + (Vector(p) - base) * N) for p in ((0, -12.0, 19.0), (0, -16.5, 23.5), (0, -20.0, 27.5), (0, -22.8, 30.5), (0, -25.6, 32.0))]
    h = Vector(nk[-1])
    cabeca(e, nk, None, tuple(h + Vector((0, -10.0, -1.1))), tuple(h + Vector((0, -3.6, -1.9))), tuple(h + Vector((0, -9.6, -2.3))), topo)
    e.cadeia("Cauda", [(0, 13, 15), (0, 22, 13), (0, 32, 10), (0, 42, 7), (0, 52, 5), (0, 58, 4.5)], "Quadril", "cauda")
    for s, l in ((1, "E"), (-1, "D")):
        membro(e, "PernaD" + l + "_", [(s * 5.5 * W, -8, 13), (s * 6.2 * W, -6.5, 8), (s * 6.0 * W, -8.5, 3), (s * 6.0 * W, -11.0, 0.8)], topo, True, s)
        membro(e, "PernaT" + l + "_", [(s * 5.4 * W, 9, 13), (s * 6.3 * W, 5.5, 8.5), (s * 6.0 * W, 11, 4.0), (s * 6.0 * W, 8.2, 0.8)], "Quadril", False, s)
        asas(e, s, l, (s * 4.8 * W, -7, 21), (s * 13, -4, 31), (s * 18, 2, 38), [espelhar(d, s) for d in DEDOS], topo)
    return e


def wyvern():
    e = Esq("Wyvern", "wyvern")
    topo = tronco(e, (0, 3.2, 8.8), (0, -2.2, 9.8))
    cabeca(e, [(0, -3.8, 10.4), (0, -5.6, 12.6), (0, -6.8, 14.4), (0, -8.0, 15.5)], None, (0, -11.8, 15.2),
           (0, -9.6, 15.0), (0, -11.4, 14.8), topo)
    e.cadeia("Cauda", [(0, 5, 9), (0, 10, 8.4), (0, 16, 7.4), (0, 22, 6.6), (0, 27, 6.2), (0, 29.8, 7.7)], "Quadril", "cauda")
    for s, l in ((1, "E"), (-1, "D")):
        membro(e, "PernaT" + l + "_", [(s * 1.9, 3.2, 7.2), (s * 2.2, 1.2, 4.6), (s * 2.0, 3.6, 1.9), (s * 2.0, 2.8, 0.5), (s * 2.0, 1.2, 0.2)], "Quadril", False, s)
        asas(e, s, l, (s * 2.0, -2.2, 11.0), (s * 6.5, -1.0, 14.0), (s * 10.5, 0.5, 16.0),
             [espelhar(d, s) for d in ((19, 2, 15.5), (17, 7, 11), (12.5, 9.5, 8.5))], topo)
    return e


def todos():
    return {
        "Lobo_Ancestral": canideo_v3() if os.environ.get("CR_SUFIXO") in ("_v3", "_v4", "_v5") else canideo("Lobo_Ancestral"),
        "Lobo_Artico": canideo_v3("Lobo_Artico") if os.environ.get("CR_SUFIXO") == "_v5" else canideo("Lobo_Artico", W=1.2, k=6.6 / 6.5),
        "Cerbero_Sombrio": canideo("Cerbero_Sombrio", W=1.4, k=14 / 6.5, cabecas=3),
        "Leao_Solar": felino(), "Urso_Silvestre": urso(), "Bufalo_Colossal": bufalo(),
        "Crocodilo_Primordial": crocodilo(), "Basilisco": basilisco(), "Lagarto_Cristalino": lagarto(),
        "Escorpiao_Colossal": escorpiao(), "Serpente_Marinha": serpente(), "Leviata_Jovem": leviata(),
        "Wyvern": wyvern(), "Dragao_das_Montanhas": dragao("Dragao_das_Montanhas"),
        "Dragao_Glacial": dragao("Dragao_Glacial", W=0.85, N=1.15), "Dragao_Sombrio": dragao("Dragao_Sombrio"),
    }
