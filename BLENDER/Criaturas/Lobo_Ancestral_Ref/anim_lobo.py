"""Clipes do Lobo Ancestral (procedurais, NO LUGAR: o jogo desloca/gira o modelo; as velocidades e duracoes abaixo sao
parametros dos clipes, NAO regras oficiais). Cada quadro: raiz (corpo), coluna/pescoco/cabeca/mandibula/orelhas/juba/cauda
e as 4 patas (almofada + inclinacao do metacarpo/metatarso via IK; dedos mantem a orientacao de repouso = deitados no
chao). Pose final de cada osso gravada em FK (matrix_basis) -> acao 'Lobo_<clipe>' + JSON para o Studio + QA.
Uso: blender -b rig/Lobo_Ancestral_Rig.blend -P anim_lobo.py -- <saida_dir> [clipes,separados]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, Quaternion
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; PB = arm.pose.bones; BD = arm.data.bones
PES = ("MaoE", "MaoD", "MetatarsoE", "MetatarsoD"); DEDO = {"MaoE": "DedosE", "MaoD": "DedosD", "MetatarsoE": "PeE", "MetatarsoD": "PeD"}
ALVO = {k: bpy.data.objects["IK_" + k] for k in PES}
B0 = {k: BD[k].tail_local.copy() for k in PES}                       # almofada (base dos dedos) no repouso
W0 = {k: BD[k].head_local.copy() for k in PES}                       # punho / jarrete no repouso
Q0 = {k: BD[k].matrix_local.to_quaternion() for k in PES}
CAUDA = sorted([b.name for b in BD if b.name.startswith("Cauda")], key=lambda s: int(s[5:]))
NC = len(CAUDA)
Y_MEIO = (B0["MaoE"].y + B0["MetatarsoE"].y) / 2
C = V((0, Y_MEIO, 4.5))                                              # centro do corpo (pivo da raiz)
QUADRIL = (BD["CoxaE"].head_local + BD["CoxaD"].head_local) / 2
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def rad(g): return math.radians(g)
EIXO = {"X": V((1, 0, 0)), "Y": V((0, 1, 0)), "Z": V((0, 0, 1))}
def rot_mundo(nome, ang):
    """{eixo: graus} em eixos do MUNDO no referencial de repouso do osso -> quaternion local (ordem Z, X, Y)"""
    r = BD[nome].matrix_local.to_3x3(); q = Matrix.Identity(3)
    for e in ("Z", "X", "Y"):
        if ang.get(e): q = Matrix.Rotation(rad(ang[e]), 3, e) @ q
    return (r.inverted() @ q @ r).to_quaternion()
def zerar():
    for pb in PB:
        pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0); pb.scale = (1, 1, 1)

# ------------------------------------------------------------------ uma pose = dicionario
# raiz: (dx, dy, dz, pitch, roll, yaw) graus; pivo = C (pitch < 0 = nariz para cima)
# ossos: {osso: {eixo: graus}};  pes: {pe: (bola_mundo V, inclinacao graus, dedos graus)}
def pose_raiz(r):
    dx, dy, dz, pit, rol, yaw = r
    R = (Matrix.Rotation(rad(yaw), 4, "Z") @ Matrix.Rotation(rad(pit), 4, "X") @ Matrix.Rotation(rad(rol), 4, "Y"))
    return Matrix.Translation(C + V((dx, dy, dz))) @ R @ Matrix.Translation(-C)
DEDOS_SOLTOS = 8.0                                                    # v20: dedos soltos (leve flexao)
GIRO_PE = {"MaoE": 14.0, "MaoD": -14.0, "MetatarsoE": 0.0, "MetatarsoD": 0.0}   # v20: dianteiras relaxadas para fora (traseiras giradas erguiam o corpo)
PALP_FECHA = json.loads(arm["palpebra_fecha_graus"]) if "palpebra_fecha_graus" in arm else {}   # rig18 (palpebras.py)
POLOS = {o.name: o for o in bpy.data.objects if o.name.startswith("Polo_")}
POLO0 = {n: o.location.copy() for n, o in POLOS.items()}
def aplicar(p):
    zerar()
    M = pose_raiz(p["raiz"])
    PB["Raiz"].matrix = M @ BD["Raiz"].matrix_local
    # v17: os POLOS do IK (direcao de cotovelos/joelhos) acompanham o corpo quando ele desce ao chao. Eram empties
    # parados na altura de pe: deitado (corpo 3,5 mais baixo) puxavam cotovelos e joelhos PARA CIMA (cotovelo z 1,8,
    # joelho 2,0) e os antebracos nao deitavam. Peso 0 de pe (andar/correr intactos) -> 1 quando a raiz desce > 1,3.
    wp = max(0.0, min(1.0, (-p["raiz"][2] - 0.3) / 1.0))
    for n, o in POLOS.items(): o.location = POLO0[n].lerp(M @ POLO0[n], wp)
    for nm, ang in p["ossos"].items():
        if nm in PB: PB[nm].rotation_quaternion = rot_mundo(nm, ang)
    for l_, g_ in PALP_FECHA.items():                                   # v25: palpebras - "F" = fracao fechada (0 aberto, 1 fechado)
        PB["Palpebra" + l_].rotation_quaternion = Quaternion((1, 0, 0), rad(g_ * p["ossos"].get("Palpebra" + l_, {}).get("F", 0.0)))
    wy = max(0.0, min(1.0, (-p["raiz"][2] - 2.0) / 0.8))               # 0 de pe/sentado -> 1 deitado
    for k, (bola, incl, dedo) in p["pes"].items():
        R = Matrix.Rotation(rad(incl), 4, "X")
        if wy > 0: R = Matrix.Rotation(rad(GIRO_PE[k] * wy), 4, "Z") @ R     # deitado: patas relaxadas, viradas um pouco para fora
        ALVO[k].location = bola + (R @ (W0[k] - B0[k]))
        ALVO[k].rotation_quaternion = R.to_quaternion() @ Q0[k]
    bpy.context.view_layer.update()
    for k, (bola, incl, dedo) in p["pes"].items():                  # dedos: orientacao de repouso (deitados) + curvatura
        pb = PB[DEDO[k]]; base = PB[k].tail
        Rd = Matrix.Rotation(rad(dedo), 3, "X") @ BD[DEDO[k]].matrix_local.to_3x3()
        pb.matrix = Matrix.Translation(base) @ Rd.to_4x4()
    bpy.context.view_layer.update()
    cauda_acima()
CAUDA_MALHA = True
CAUDA_LIMITE = 0.04                                                   # pelo da cauda mais baixo permitido (passo de malha)
CAUDA_ZMIN = 0.62                                                     # raio do pelo da cauda: a pelagem nao entra no chao
def cauda_acima():
    """se a ponta de um osso da cauda desce abaixo de CAUDA_ZMIN, gira o osso para cima (eixo horizontal perpendicular)"""
    for nm in CAUDA:
        pb = PB[nm]; h, t = pb.head.copy(), pb.tail.copy(); L = (t - h).length
        if t.z >= CAUDA_ZMIN or L < 1e-4: continue
        a0 = math.asin(max(-1.0, min(1.0, (t.z - h.z) / L))); a1 = math.asin(max(-1.0, min(1.0, (CAUDA_ZMIN - h.z) / L)))
        d = t - h; eixo = V((d.y, -d.x, 0.0))
        if eixo.length < 1e-5: continue
        R = Matrix.Translation(h) @ Matrix.Rotation(a1 - a0, 4, eixo.normalized()) @ Matrix.Translation(-h)
        pb.matrix = R @ pb.matrix; bpy.context.view_layer.update()
    # pelagem da cauda (malha): o vertice mais baixo da cauda fica acima de 0,04; gira o osso anterior ao trecho baixo.
    # Desligado (CAUDA_MALHA = False) quando a cauda REPOUSA no chao: o cauda_no_chao ja a deixa encostada e este passo,
    # ao erguer o osso anterior, levantava a cauda inteira como pluma.
    for _ in range(5 if CAUDA_MALHA else 0):
        ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        zmin, iv = 9.0, -1
        for i in V_CAUDA:
            zz = ev[i].co.z
            if zz < zmin: zmin, iv = zz, i
        if zmin >= CAUDA_LIMITE: break
        j = max(0, DONO_CAUDA[iv] - 1); pb = PB[CAUDA[j]]; h = pb.head.copy(); pv = ev[iv].co.copy()
        d = pv - h; dist = max(0.3, (V((d.x, d.y, 0))).length)
        ang = min(rad(20), math.asin(min(1.0, (CAUDA_LIMITE + 0.02 - zmin) / dist))); eixo = V((d.y, -d.x, 0.0))
        if eixo.length < 1e-5: break
        R = Matrix.Translation(h) @ Matrix.Rotation(ang, 4, eixo.normalized()) @ Matrix.Translation(-h)
        pb.matrix = R @ pb.matrix; bpy.context.view_layer.update()
V_CAUDA, DONO_CAUDA = [], {}
_gi = {g.index: g.name for g in LO.vertex_groups}
for v in LO.data.vertices:
    if not v.groups: continue
    g = max(v.groups, key=lambda q: q.weight); nm = _gi[g.group]
    if nm in CAUDA: V_CAUDA.append(v.index); DONO_CAUDA[v.index] = CAUDA.index(nm)
CORPO_G = {"Pelve", "Coluna1", "Coluna2", "Peito", "Pescoco1", "Pescoco2", "Cabeca", "Mandibula", "OrelhaE", "OrelhaD", "JubaE", "JubaD", "JubaPeito"} | set(CAUDA) | {b.name for b in BD if b.name.startswith("Pelo")}
V_CORPO = [v.index for v in LO.data.vertices if v.groups and _gi[max(v.groups, key=lambda q: q.weight).group] in CORPO_G]
V_TRONCO = [v.index for v in LO.data.vertices if v.groups and _gi[max(v.groups, key=lambda q: q.weight).group] in ("Pelve", "Coluna1", "Coluna2", "Peito")]
print("CAUDA verts", len(V_CAUDA), "CORPO verts", len(V_CORPO), "TRONCO verts", len(V_TRONCO))
def alinhamento():
    """medidas de alinhamento da malha VISIVEL e dos apoios (x = 0 e a linha central do lobo)"""
    ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
    xs = [ev[i].co.x for i in V_TRONCO]
    m = {"tronco_x_meio": (min(xs) + max(xs)) / 2, "tronco_x_media": sum(xs) / len(xs)}
    b = {k: PB[k].tail for k in PES}
    m["apoio_dian_x_centro"] = (b["MaoE"].x + b["MaoD"].x) / 2; m["apoio_tras_x_centro"] = (b["MetatarsoE"].x + b["MetatarsoD"].x) / 2
    m["apoio_dian_dy"] = b["MaoE"].y - b["MaoD"].y; m["apoio_tras_dy"] = b["MetatarsoE"].y - b["MetatarsoD"].y
    m["ombros_dz"] = PB["BracoE"].head.z - PB["BracoD"].head.z; m["quadris_dz"] = PB["CoxaE"].head.z - PB["CoxaD"].head.z
    m["ombros_x_centro"] = (PB["BracoE"].head.x + PB["BracoD"].head.x) / 2; m["quadris_x_centro"] = (PB["CoxaE"].head.x + PB["CoxaD"].head.x) / 2
    return m
def pose_base():
    return {"raiz": [0, 0, 0, 0, 0, 0], "ossos": {}, "pes": {k: (B0[k].copy(), 0.0, 0.0) for k in PES}}
def somar_ossos(d, extra):
    for nm, ang in extra.items():
        a = d.setdefault(nm, {})
        for e, g in ang.items(): a[e] = a.get(e, 0.0) + g

# ------------------------------------------------------------------ acompanhamento secundario (cauda/juba/orelhas)
def secundario(p, t, vel_raiz, amp=1.0, T_resp=0.0):
    """cauda e juba atrasam em relacao a aceleracao do corpo (vel_raiz = (vy, vz) do pivo em studs/s)"""
    vy, vz = vel_raiz
    o = {}
    for i, nm in enumerate(CAUDA):
        k = (i + 1) / NC
        o[nm] = {"X": amp * (-1.6 * vz * k), "Z": 0.0}
    for nm in ("JubaE", "JubaD", "JubaPeito"): o[nm] = {"X": amp * (2.0 * vy * 0.15 - 1.5 * vz)}
    for nm in ("OrelhaE", "OrelhaD"): o[nm] = {"X": amp * (-1.0 * vz)}
    somar_ossos(p["ossos"], o)

# ------------------------------------------------------------------ VENTO no pelo (ossos Pelo*, cauda e juba)
# Cada mecha gira empurrada pelo ar relativo (vento ambiente + ar do proprio movimento), com rajada lenta e tremulacao
# rapida; frequencias com numero INTEIRO de ciclos na duracao do clipe (o loop fecha sem salto). As cadeias "...2" e a
# ponta da cauda atrasam (fase) e balancam mais. Angulos em graus, eixos do mundo no repouso (rot_mundo).
# O vento do jogo e o workspace.GlobalWind (muda com o clima): o pelo reage a ele EM TEMPO REAL (VentoPelo_Cliente).
# Por isso os clipes saem SEM vento (FORCA_VENTO = 0). LOBO_VENTO_ASSADO=<forca> grava um vento fixo so para revisao.
FORCA_VENTO = float(os.environ.get("LOBO_VENTO_ASSADO", "0"))
VENTO_AMB = V((-0.80, 0.45, 0.0))                                     # sopra da frente-esquerda (+X/-Y) para a traseira-direita
VENTO = {"PeloNuca1": (7, 0.0), "PeloNuca2": (9, 0.9), "PeloJubaE1": (7, 0.4), "PeloJubaD1": (7, 0.7), "PeloJubaE2": (9, 1.3),
         "PeloJubaD2": (9, 1.6), "PeloBochechaE": (4, 0.2), "PeloBochechaD": (4, 0.5), "PeloPeito1": (6, 0.6), "PeloPeito2": (8, 1.4),
         "PeloDorso1": (4, 1.0), "PeloDorso2": (4, 1.8), "PeloBarriga": (6, 2.2), "PeloCotoveloE": (5, 0.3), "PeloCotoveloD": (5, 0.8),
         "PeloCoxaE": (4, 2.6), "PeloCoxaD": (4, 2.9), "JubaE": (2.5, 0.5), "JubaD": (2.5, 0.8), "JubaPeito": (2.0, 1.1)}
for i, nm in enumerate(CAUDA): VENTO.setdefault(nm, (1.2 + 3.3 * (i + 1) / NC, 0.45 * i))
DIR0 = {nm: (BD[nm].tail_local - BD[nm].head_local).normalized() for nm in VENTO if nm in BD}
CAUDA_NO_CHAO = {"Sentar", "Sentado", "LevantarSentado", "Deitar", "Deitado", "Descanso", "Adormecer", "Despertar", "LevantarDeitado"}
def vento(p, t, dur, vel=0.0, clipe=""):
    if FORCA_VENTO <= 0: return
    ar = VENTO_AMB + V((0.0, min(abs(vel), 12.0) * 0.12, 0.0))      # o lobo anda para -Y: o ar vem de -Y para +Y
    o = {}
    for nm, (amp, fase) in VENTO.items():
        if nm not in DIR0: continue
        b = DIR0[nm]; emp = ar - b * ar.dot(b); mag = min(1.6, emp.length)
        if mag < 1e-4: continue
        eixo = b.cross(emp).normalized()
        k1 = max(1, round(0.35 * dur)); k2 = max(k1 + 1, round(1.6 * dur)); k3 = max(k2 + 1, round(3.1 * dur))
        g = (0.55 + 0.30 * math.sin(2 * math.pi * k1 / dur * t + fase) + 0.12 * math.sin(2 * math.pi * k2 / dur * t + 1.7 * fase)
             + 0.05 * math.sin(2 * math.pi * k3 / dur * t + 2.3 * fase))
        ang = amp * mag * g * FORCA_VENTO
        if clipe in CAUDA_NO_CHAO and nm in CAUDA: ang *= 0.2               # cauda apoiada: o ajuste ao chao nao "pula"
        o[nm] = {"X": ang * eixo.x, "Y": ang * eixo.y, "Z": ang * eixo.z}
    somar_ossos(p["ossos"], o)

# ------------------------------------------------------------------ marchas (ciclos)
def marcha(T, L, apoio, fases, alt, flex, bob, cfg):
    """fases: {pe: fase 0..1 do toque}; o pe apoiado recua de -L/2 a +L/2 (o lobo anda para -Y)."""
    def f(t):
        u = (t / T) % 1.0; p = pose_base(); pes = {}
        for k in PES:
            uk = (u - fases[k]) % 1.0
            if uk < apoio:
                s = uk / apoio; dy = -L / 2 + L * s; dz = 0.0
                incl = lerp(-cfg.get("incl_toque", 4), cfg.get("incl_saida", 14), s)
                dedo = -incl * 0.0
            else:
                s = (uk - apoio) / (1 - apoio); e = suave(s)
                dy = L / 2 - L * e; dz = alt * math.sin(math.pi * s) ** 0.85
                incl = cfg.get("incl_saida", 14) * (1 - s) + flex * math.sin(math.pi * s ** 0.8) - cfg.get("incl_toque", 4) * suave((s - 0.8) / 0.2)
                dedo = cfg.get("dedo_balanco", 18) * math.sin(math.pi * s)
            dx = cfg.get("abre", 0.0) * (1 if k.endswith("E") else -1) * (math.sin(math.pi * ((uk - apoio) / (1 - apoio))) if uk >= apoio else 0)
            if k.startswith("Meta"): dy += cfg.get("tras_atras", 0.30) * L          # apoio traseiro centrado atras do quadril
            pes[k] = (B0[k] + V((dx, dy, dz)), incl, dedo)
        p["pes"] = pes
        w = 2 * math.pi * u
        z = bob * math.cos(2 * w + cfg.get("fase_bob", 0.0))
        pit = cfg.get("arfagem", 0.0) * math.sin(w + cfg.get("fase_arf", 0.0))
        rol = cfg.get("rolagem", 0.0) * math.sin(w)
        p["raiz"] = [0, 0, z + cfg.get("baixa", 0.0), pit + cfg.get("inclina", 0.0), rol, 0]
        fl = cfg.get("flexao", 0.0) * math.cos(w - 2 * math.pi * cfg.get("fase_flex", 0.0))     # galope: dobra/estende a coluna
        lat = cfg.get("lateral", 0.0) * math.sin(w)
        o = {"Pelve": {"X": -fl * 0.6, "Z": -lat * 0.5}, "Coluna1": {"X": fl * 0.5, "Z": lat * 0.6}, "Coluna2": {"X": fl * 0.5, "Z": lat * 0.5},
             "Peito": {"X": fl * 0.4, "Z": lat * 0.3},
             "Pescoco1": {"X": -pit * 0.5 - fl * 0.3 + cfg.get("pescoco", 0.0), "Z": -lat * 0.6},
             "Cabeca": {"X": cfg.get("aceno", 0.0) * math.sin(2 * w + 0.8) - pit * 0.4 + cfg.get("cabeca", 0.0), "Z": -lat * 0.4},
             "Mandibula": {"X": cfg.get("boca", 0.0)}}
        for i, nm in enumerate(CAUDA):
            k = (i + 1) / NC
            o[nm] = {"Z": cfg.get("cauda_lat", 0.0) * k * math.sin(w - 0.9 * k * math.pi),
                     "X": cfg.get("cauda_alt", 0.0) + cfg.get("cauda_bob", 0.0) * k * math.sin(2 * w - 1.2 - 1.5 * k)}
        for nm, sx in (("OrelhaE", 1), ("OrelhaD", -1)):
            o[nm] = {"X": cfg.get("orelha", 0.0) + 1.5 * math.sin(2 * w - 1.6), "Y": 0.0}
        for nm in ("JubaE", "JubaD", "JubaPeito"):
            o[nm] = {"X": cfg.get("juba", 0.0) * math.sin(2 * w - 1.4)}
        for lado in ("E", "D"):                                      # escapula acompanha a pata dianteira (alcance)
            dy_ = pes["Mao" + lado][0].y - B0["Mao" + lado].y
            o["Escapula" + lado] = {"X": cfg.get("escapula", 9.0) * dy_}
        p["ossos"] = o
        return p
    return f

ANDAR = dict(T=36 / FPS, L=2.0, apoio=0.62, fases={"MetatarsoE": 0.0, "MaoE": 0.25, "MetatarsoD": 0.5, "MaoD": 0.75}, alt=0.32, flex=28, bob=0.05,
             cfg=dict(arfagem=0.8, rolagem=1.6, lateral=2.2, aceno=2.0, cauda_lat=7, cauda_alt=4, cauda_bob=2, juba=3, orelha=0, fase_bob=0.6, baixa=-0.10))
TROTE = dict(T=20 / FPS, L=2.3, apoio=0.45, fases={"MaoE": 0.0, "MetatarsoD": 0.0, "MaoD": 0.5, "MetatarsoE": 0.5}, alt=0.52, flex=45, bob=0.09,
             cfg=dict(arfagem=0.6, rolagem=1.0, lateral=1.2, aceno=1.6, cauda_lat=5, cauda_alt=8, cauda_bob=4, juba=5, orelha=-4, pescoco=4,
                      fase_bob=0.5, incl_saida=18, baixa=-0.22))
GALOPE = dict(T=14 / FPS, L=3.0, apoio=0.30, fases={"MetatarsoE": 0.0, "MetatarsoD": 0.10, "MaoE": 0.42, "MaoD": 0.52}, alt=0.80, flex=60, bob=0.0,
              cfg=dict(arfagem=5.0, fase_arf=-0.9, flexao=9.0, fase_flex=0.95, rolagem=0.6, lateral=0.0, aceno=0.0, cauda_lat=2, cauda_alt=14,
                       cauda_bob=6, juba=7, orelha=-14, pescoco=10, cabeca=-6, abre=0.12, incl_saida=24, incl_toque=6, baixa=-0.40, dedo_balanco=26, escapula=12.0))
def vel(M): return M["L"] / (M["apoio"] * M["T"])

# ------------------------------------------------------------------ clipes por poses-chave
def chaves(lista, vel_sec=True):
    """lista de (t, pose, flags). Interpola raiz/ossos/pes com suavizacao entre chaves vizinhas.
    flags por pe: 'arco' = levanta no meio do trajeto (altura)."""
    def f(t):
        for i in range(len(lista) - 1):
            if lista[i][0] <= t <= lista[i + 1][0]: break
        else: i = len(lista) - 2
        t0, a, fa = lista[i]; t1, b, fb = lista[i + 1]
        s = suave((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
        p = {"raiz": [lerp(x, y, s) for x, y in zip(a["raiz"], b["raiz"])], "ossos": {}, "pes": {}}
        nomes = set(a["ossos"]) | set(b["ossos"])
        for nm in nomes:
            ea, eb = a["ossos"].get(nm, {}), b["ossos"].get(nm, {})
            p["ossos"][nm] = {e: lerp(ea.get(e, 0.0), eb.get(e, 0.0), s) for e in set(ea) | set(eb)}
        for k in PES:
            (ba, ia, da), (bb, ib, db) = a["pes"][k], b["pes"][k]
            bola = ba.lerp(bb, s); arco = (fb or {}).get(k, 0.0)
            if arco: bola = bola + V((0, 0, arco * math.sin(math.pi * s)))
            p["pes"][k] = (bola, lerp(ia, ib, s), lerp(da, db, s))
        return p
    return f
def P(raiz=None, ossos=None, pes=None):
    p = pose_base()
    if raiz: p["raiz"] = list(raiz) + [0] * (6 - len(raiz))
    if ossos: p["ossos"] = ossos
    if pes:
        for k, v in pes.items():
            d, incl, dedo = v; p["pes"][k] = (B0[k] + V(d), incl, dedo)
    return p
def mundo_pe(M, k, extra=V((0, 0, 0))):
    """posicao da almofada presa ao corpo (fase aerea)"""
    return (M @ (B0[k] + extra))
NEUTRO = P()
# ---- parado / observar
def clipe_repouso(t):
    T = 4.0; w = 2 * math.pi * t / T; p = pose_base()
    p["raiz"] = [0, 0, 0.018 * math.sin(w), -0.3 * math.sin(w), 0, 0]
    p["ossos"] = {"Peito": {"X": -0.8 * math.sin(w)}, "Coluna2": {"X": 0.4 * math.sin(w)}, "Pescoco1": {"X": 0.6 * math.sin(w - 0.5)},
                  "Cabeca": {"X": -0.5 * math.sin(w - 0.8), "Z": 1.2 * math.sin(w * 0.5)},
                  "JubaPeito": {"X": 1.5 * math.sin(w - 1.0)}, "JubaE": {"X": 1.0 * math.sin(w - 1.2)}, "JubaD": {"X": 1.0 * math.sin(w - 1.2)},
                  "OrelhaE": {"X": 4.0 * max(0.0, math.sin(2 * w * 2)) ** 8}, "OrelhaD": {"X": 0.0}}
    for i, nm in enumerate(CAUDA):
        k = (i + 1) / NC; p["ossos"][nm] = {"Z": 3.0 * k * math.sin(w * 0.5 - 1.2 * k)}
    return p
def clipe_observar(t):
    """olha para a esquerda, pausa, para a direita, volta; orelhas viram para o lado do olhar"""
    ks = [(0.0, 0), (0.6, 38), (1.6, 38), (2.4, -34), (3.4, -34), (4.2, 0), (4.5, 0)]
    for i in range(len(ks) - 1):
        if ks[i][0] <= t <= ks[i + 1][0]:
            yaw = lerp(ks[i][1], ks[i + 1][1], suave((t - ks[i][0]) / (ks[i + 1][0] - ks[i][0]))); break
    else: yaw = 0
    p = clipe_repouso(t)
    somar_ossos(p["ossos"], {"Pescoco1": {"Z": yaw * 0.35}, "Pescoco2": {"Z": yaw * 0.35}, "Cabeca": {"Z": yaw * 0.3, "X": -3 * abs(yaw) / 38},
                             "OrelhaE": {"Z": yaw * 0.25, "X": 3 * (yaw > 0)}, "OrelhaD": {"Z": yaw * 0.25, "X": 3 * (yaw < 0)},
                             "Peito": {"Z": yaw * 0.06}})
    return p
# ---- partida / freada (transicao parado <-> trote, mesma fase do ciclo)
def rampa_trote(sobe, dur):
    tr = marcha(**TROTE)
    def f(t):
        a = suave(t / dur) if sobe else 1 - suave(t / dur)
        p = tr(t); n = pose_base()
        for k in PES:
            bola, incl, dedo = p["pes"][k]
            d = bola - B0[k]; p["pes"][k] = (B0[k] + d * a, incl * a, dedo * a)
        p["raiz"] = [x * a for x in p["raiz"]]
        p["raiz"][3] += (4.0 if sobe else -5.0) * math.sin(math.pi * min(1, t / dur)) * (1 if sobe else 1)   # inclina para frente na partida / para tras na freada
        p["raiz"][1] += (-0.15 if sobe else 0.20) * math.sin(math.pi * min(1, t / dur))
        for nm, ang in p["ossos"].items():
            for e in ang: ang[e] *= a
        if not sobe: somar_ossos(p["ossos"], {"Cabeca": {"X": -6 * math.sin(math.pi * t / dur)}, "OrelhaE": {"X": 4 * math.sin(math.pi * t / dur)}, "OrelhaD": {"X": 4 * math.sin(math.pi * t / dur)}})
        return p
    return f
# ---- virada no lugar (com rotacao da raiz: o jogo aplica o giro ao modelo no fim)
def virar(sinal, dur=2.4):
    """giro de 90 graus em 12 passos de 30 (cada pata pisa 3 vezes); o corpo acompanha o progresso medio dos pes"""
    ordem = (["MaoE", "MetatarsoD", "MaoD", "MetatarsoE"] if sinal > 0 else ["MaoD", "MetatarsoE", "MaoE", "MetatarsoD"]) * 4
    jan = [(0.02 + 0.0595 * i, 0.02 + 0.0595 * i + 0.11) for i in range(16)]
    ANG = 90.0 * sinal; piv = V((0, Y_MEIO, 0))
    def girado(v, ang): return piv + Matrix.Rotation(rad(ang), 3, "Z") @ (v - piv)
    def f(t):
        u = t / dur; p = pose_base(); prog = {}
        for k in PES:
            feitos, alt, inc = 0.0, 0.0, 0.0
            for i, kk in enumerate(ordem):
                if kk != k: continue
                a0, a1 = jan[i]; x_ = max(0.0, min(1.0, (u - a0) / (a1 - a0)))
                feitos += suave(x_); alt = max(alt, 0.32 * math.sin(math.pi * x_)); inc = max(inc, 22 * math.sin(math.pi * x_))
            prog[k] = feitos
            p["pes"][k] = (girado(B0[k], ANG / 4 * feitos) + V((0, 0, alt)), inc, 0.0)
        psi = ANG / 4 * sum(prog.values()) / 4
        p["raiz"] = [0, 0, -0.06 * math.sin(math.pi * u), 0, 0, psi]
        lat = 10 * sinal * math.sin(math.pi * u)
        p["ossos"] = {"Pescoco1": {"Z": lat * 0.8}, "Cabeca": {"Z": lat * 0.6}, "Coluna2": {"Z": lat * 0.3}, "Peito": {"Z": lat * 0.3}}
        for i, nm in enumerate(CAUDA): p["ossos"][nm] = {"Z": -lat * 0.6 * (i + 1) / NC}
        return p
    return f
# ---- sentar / deitar (poses-chave)
def assentar(p, alvo=0.03, nome=""):
    """desce/sobe a raiz ate o vertice mais baixo do CORPO (sem patas) tocar o chao (z = alvo)"""
    for _ in range(4):
        aplicar(p); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        zm = min(ev[i].co.z for i in V_CORPO); d = alvo - zm
        p["raiz"][2] += d
        if abs(d) < 0.01: break
    print("ASSENTAR", nome, "raiz dz %.3f" % p["raiz"][2])
    return p
# ---- poses de chao (06/11, referencias de lobo real: LMU canid ethogram "sit = traseiro no chao, patas traseiras dobradas,
# dianteiras estendidas"; "lie = torso apoiado no chao, cabeca para cima ou para baixo"; esternal = peito no chao com as
# traseiras dos lados). v1 (anterior) ficava "agachado": corpo alto nas patas e cabeca erguida.
V_CABECA = [v.index for v in LO.data.vertices if v.groups and _gi[max(v.groups, key=lambda q: q.weight).group] in ("Cabeca", "Mandibula")]
def _pele(v):                                                          # corpo SEM pelo solto nem base da cauda
    return sum(g.weight for g in v.groups if _gi[g.group].startswith(("Pelo", "Cauda"))) < 0.05
V_FRENTE = [v.index for v in LO.data.vertices if v.groups and _pele(v) and _gi[max(v.groups, key=lambda q: q.weight).group] in ("Peito", "Coluna2")]
V_TRAS = [v.index for v in LO.data.vertices if v.groups and _pele(v) and _gi[max(v.groups, key=lambda q: q.weight).group] in ("Pelve", "Coluna1")]
V_NUCLEO = V_FRENTE + V_TRAS
def NUCLEO_(): return V_NUCLEO
V_PE = {k: [v.index for v in LO.data.vertices if v.groups and _gi[max(v.groups, key=lambda q: q.weight).group] in gs]
        for k, gs in (("MaoE", ("MaoE", "DedosE")), ("MaoD", ("MaoD", "DedosD")),
                      ("MetatarsoE", ("MetatarsoE", "PeE")), ("MetatarsoD", ("MetatarsoD", "PeD")))}
def apoiar_membros(p, alvo=0.02, nome="", pes_deitados=()):
    """1) pes_deitados: busca a inclinacao (passo 4 graus, +-40 em torno da inicial) que deixa a pata (Mao/Dedos ou
    Metatarso/Pe) mais RENTE ao chao - menor diferenca entre o ponto mais baixo e o percentil 40 com a bola no lugar
    (v16: -86/-88 fixos enterravam o punho/jarrete 0,6-1,0; -50/-63 fixos levantavam antebracos e joelhos).
    2) sobe a bola do pe ate a malha dele encostar (percentil 5 = alvo)."""
    for k in pes_deitados:
        b_, inc0, de = p["pes"][k]
        def espessura(inc):
            p["pes"][k] = (b_, inc, de); aplicar(p); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
            z = np.array([ev[i].co.z for i in V_PE[k]]); return float(np.percentile(z, 40) - z.min()) + 0.15 * max(0.0, -z.min())
        melhor = min(range(int(inc0) - 40, int(inc0) + 41, 4), key=espessura)
        p["pes"][k] = (b_, float(melhor), de)
    if pes_deitados: print("INCLINACAO", nome, " ".join("%s:%.0f" % (k, p["pes"][k][1]) for k in pes_deitados))
    """membro deitado (antebraco/metatarso no chao): sobe a bola do pe ate a malha dele encostar no chao em vez de
    atravessa-lo (v16: patas -0,90 e jarretes -0,80 abaixo do solo no Deitado/Sentado)"""
    for _ in range(5):
        aplicar(p); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        mx = 0.0
        for k, idx in V_PE.items():
            zm = float(np.percentile([ev[i].co.z for i in idx], 12)); b_, inc, de = p["pes"][k]
            sobe = min(alvo - zm, 0.30 - (b_.z - B0[k].z))                  # no maximo 0,30 acima do repouso (nao suspende o lobo)
            if sobe > 0.01: p["pes"][k] = (b_ + V((0, 0, sobe)), inc, de); mx = max(mx, sobe)
        if mx < 0.01: break
    print("APOIAR_MEMBROS", nome, " ".join("%s:%.2f" % (k, p["pes"][k][0].z) for k in PES)); return p
def assentar_tronco(p, alvo, nome=""):
    """desce a raiz ate o vertice mais baixo do TRONCO (Pelve/Coluna/Peito) tocar z = alvo (o pelo solto pode encostar)"""
    for _ in range(5):
        aplicar(p); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        zm = min(ev[i].co.z for i in NUCLEO_()); d = alvo - zm
        p["raiz"][2] += d
        if abs(d) < 0.005: break
    print("ASSENTAR_TRONCO", nome, "raiz dz %.3f" % p["raiz"][2]); return p
def nivelar_tronco(p, nome="", folga_tras=0.30):
    """deitado de verdade: peito E quadril no chao. Ajusta o pitch da raiz ate o ponto mais baixo da frente (Peito/Coluna2)
    e o de tras (Pelve/Coluna1) ficarem a folga_tras de diferenca: o peito no chao e o quadril sobre as coxas dobradas
    (v2 deixava o quadril alto, como lobo de tocaia; v4 com folga 0 empinava o tronco 18 graus, cernelha alta)."""
    for _ in range(8):
        aplicar(p); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        zf = min(ev[i].co.z for i in V_FRENTE); zr = min(ev[i].co.z for i in V_TRAS)
        e_ = (zr - zf) - folga_tras                                   # quadril apoiado nas coxas dobradas, um pouco acima do chao
        p["raiz"][3] -= 12.0 * e_
        if abs(e_) < 0.02: break
    print("NIVELAR", nome, "pitch %.1f  frente %.2f tras %.2f" % (p["raiz"][3], zf, zr)); return p
def cara_no_chao(p, alvo=0.06, nome="", amin=0):
    """leva o QUEIXO ao chao como lobo deitado: ombros/peito baixam um pouco, pescoco estende para a frente e para baixo
    (Peito 0,15 / Pescoco1 0,55 / Pescoco2 0,30 do angulo a) e a cabeca compensa (-0,85 a + 8) para a cara ficar quase
    nivelada, apoiada. v1 (so dobrar pescoco/cabeca) trazia o focinho contra o peito e nao alcancava o chao."""
    def tenta(a_):
        q = {"raiz": list(p["raiz"]), "ossos": {k: dict(v) for k, v in p["ossos"].items()}, "pes": dict(p["pes"])}
        # v18: SEM girar o peito (0,15 do angulo erguia a cernelha e fazia corcunda com a cara no chao); so o pescoco desce
        somar_ossos(q["ossos"], {"Pescoco1": {"X": 0.62 * a_}, "Pescoco2": {"X": 0.38 * a_},
                                 "Cabeca": {"X": -0.85 * a_ + 8}, "Mandibula": {"X": 0.0}})
        aplicar(q); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        return min(ev[i].co.z for i in V_CABECA), q
    zs = [(a_, tenta(a_)[0]) for a_ in range(amin, 121, 10)]   # amin < 0: pode ERGUER a cabeca ja baixa
    print("CARA_NO_CHAO varredura", nome, " ".join("a%d:%.2f" % x for x in zs))
    lo = max([a_ for a_, z in zs if z > alvo], default=amin); hi = min([a_ for a_, z in zs if z <= alvo and a_ > lo], default=120)
    for _ in range(14):
        m = (lo + hi) / 2
        if tenta(m)[0] > alvo: lo = m
        else: hi = m
    z, q = tenta((lo + hi) / 2)
    print("CARA_NO_CHAO", nome, "a %.1f graus, queixo z %.3f" % ((lo + hi) / 2, z)); return q
def cauda_no_chao(p, curva=-12.0, nome="", atras=True, comprime=0.03):
    """cauda PESADA repousando: cada osso (da base a ponta) desce ate a ponta encostar no pelo do chao (CAUDA_ZMIN) e
    dai segue rente ao solo, curvando para o lado (curva, graus em Z por osso a partir do 3o). v15 deixava a cauda
    apontando para baixo e o cauda_acima a dobrava para CIMA, como pluma."""
    global CAUDA_MALHA
    CAUDA_MALHA = False
    q = {"raiz": list(p["raiz"]), "ossos": {k: dict(v) for k, v in p["ossos"].items()}, "pes": dict(p["pes"])}
    for i, nm in enumerate(CAUDA):
        q["ossos"][nm] = {"X": 0.0, "Z": (curva if i >= 2 else 0.0)}
    ant = 0.0
    for i, nm in enumerate(CAUDA):
        def custo(ang):
            q["ossos"][nm]["X"] = ang; aplicar(q); h, t = PB[nm].head, PB[nm].tail; L = (t - h).length
            alvo = max(0.55, h.z - 0.95 * L)                              # eixo da cauda desce ate ~0,55 (raio do pelo) e segue rente
            para_frente = max(0.0, (h.y - t.y) + 0.1 * L) if (atras and i < 4) else 0.0  # sentado: base ATRAS/ao lado
            return (t.z - alvo) ** 2 + 0.004 * ((ang - ant) / 10.0) ** 2 + 0.6 * para_frente ** 2
        melhor = min(range(-120, 121, 8), key=custo)
        for passo in (4, 2, 1):
            melhor = min([melhor + k * passo for k in (-1, 0, 1)], key=custo)
        q["ossos"][nm]["X"] = float(melhor); ant = float(melhor)
    extras = [0.0] * NC
    for passada in range(4):                                            # o pelo da cauda (volumoso) nao atravessa o chao
        aplicar(q); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
        fundo = [min([ev[v].co.z for v, d in DONO_CAUDA.items() if d == i] or [1.0]) for i in range(NC)]
        if min(fundo) > comprime - 0.07: break
        ant = q["ossos"][CAUDA[0]]["X"]
        for i, nm in enumerate(CAUDA):
            extras[i] += max(0.0, comprime - fundo[i]); extra = extras[i]
            def custo2(ang):
                q["ossos"][nm]["X"] = ang; aplicar(q); h, t = PB[nm].head, PB[nm].tail; L = (t - h).length
                alvo = max(0.55, h.z - 0.95 * L) + extra
                para_frente = max(0.0, (h.y - t.y) + 0.1 * L) if (atras and i < 4) else 0.0
                return (t.z - alvo) ** 2 + 0.004 * ((ang - ant) / 10.0) ** 2 + 0.6 * para_frente ** 2
            melhor = min([q["ossos"][nm]["X"] + k for k in range(-60 if i < 2 else -40, 61 if i < 2 else 41, 4)], key=custo2)
            for passo in (2, 1): melhor = min([melhor + k * passo for k in (-1, 0, 1)], key=custo2)
            q["ossos"][nm]["X"] = float(melhor); ant = float(melhor)
    aplicar(q); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
    print("CAUDA_NO_CHAO", nome, "angulos", " ".join("%.0f" % q["ossos"][nm]["X"] for nm in CAUDA),
          "| pelo mais baixo por osso", " ".join("%.2f" % min([ev[v].co.z for v, d in DONO_CAUDA.items() if d == i] or [9]) for i in range(NC)))
    CAUDA_MALHA = True
    return q
def sentado_pose(cab=0.0):
    """lobo sentado (06/11 v2): pelve LARGA no chao atras dos jarretes; patas traseiras recolhidas junto ao quadril
    (bola quase no lugar de pe, metatarso deitado para a frente, jarrete no chao); dianteiras PLANTADAS onde estavam,
    quase verticais sob os ombros (o pitch e buscado para o ombro ficar sobre a pata); cabeca equilibrada; cauda
    repousando no chao atras/ao lado. v15: quadril adiantado (bolas traseiras 1,05 a frente -> deslizavam), dianteiras
    puxadas 0,55 para tras, garupa num ponto estreito e cauda em pluma."""
    def montar(ang):
        R = Matrix.Rotation(rad(ang), 4, "X"); Hd = V((0, QUADRIL.y - 0.85, 1.20))
        T_ = Hd - (R @ (QUADRIL - C) + C)
        o = {"Pescoco1": {"X": 0.55 * -ang - 2}, "Pescoco2": {"X": 0.20 * -ang}, "Cabeca": {"X": 0.30 * -ang + 2 + cab},
             "Peito": {"X": -4}, "JubaPeito": {"X": -10}, "OrelhaE": {"X": 3}, "OrelhaD": {"X": 3},
             "CoxaE": {"Z": -14}, "CoxaD": {"Z": 14}}
        return P(raiz=(T_.x, T_.y, T_.z, ang, 0, 0), ossos=o,
                 pes={"MaoE": ((0, 0.05, 0), -3, 0), "MaoD": ((0, 0.05, 0), -3, 0),
                      "MetatarsoE": ((0.24, -1.20, 0.02), -86, 0), "MetatarsoD": ((-0.24, -1.20, 0.02), -86, 0)})
    def erro_ombro(ang):
        p = assentar_tronco(montar(ang), 0.03, "")
        return abs(PB["BracoE"].head.y - (B0["MaoE"].y + 0.35)), p
    ang = min(range(-60, -23, 2), key=lambda a_: erro_ombro(a_)[0])
    e, p = erro_ombro(ang)
    print("SENTADO pitch %d, ombro-pata %.2f" % (ang, e))
    for k in ("MetatarsoE", "MetatarsoD"): p = pe_rente(p, k)
    p = assentar_tronco(p, 0.03, "sentado")
    for k in ("MetatarsoE", "MetatarsoD"): p = pe_rente(p, k)
    print("PES_SENTADO", " ".join("%s inc %.0f z %.2f" % (k, p["pes"][k][1], p["pes"][k][0].z) for k in ("MetatarsoE", "MetatarsoD")))
    return cauda_no_chao(p, -12.0, "sentado")
# ---- apoios v17 (07/11). Diagnostico (diag_apoios.py) do v16 Deitado: metacarpo a -32 graus e metatarso a -24 graus
# (passavam do plano: inclinacao fixa -86/-88 sobre ~53/64 graus de repouso) -> punho z -0,31 e jarrete z -0,41, e a
# malha do metacarpo (-0,89), do antebraco (-0,61), do metatarso (-0,80) e da canela (-0,58) entrava no chao; o
# assentar so olhava o tronco, entao o corpo descia ate os membros afundarem.
def _idx(gs): return [v.index for v in LO.data.vertices if v.groups and _gi[max(v.groups, key=lambda q: q.weight).group] in gs]
PATA = {"MaoE": _idx(("MaoE", "DedosE")), "MaoD": _idx(("MaoD", "DedosD")), "MetatarsoE": _idx(("MetatarsoE", "PeE")), "MetatarsoD": _idx(("MetatarsoD", "PeD"))}
MEMBRO = {"MaoE": _idx(("AntebracoE",)), "MaoD": _idx(("AntebracoD",)), "MetatarsoE": _idx(("CanelaE",)), "MetatarsoD": _idx(("CanelaD",))}
DEDOS_IDX = {"MaoE": _idx(("DedosE",)), "MaoD": _idx(("DedosD",)), "MetatarsoE": _idx(("PeE",)), "MetatarsoD": _idx(("PeD",))}
PLANO = {"MaoE": -53.0, "MaoD": -53.0, "MetatarsoE": -64.0, "MetatarsoD": -64.0}   # inclinacao que deixa o osso rente ao chao
def _ev():
    return LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
def pata_reta(p, k, nome=""):
    """v21 (usuario: "perna da frente reta no chao, descansando"): dianteira DEITADA RETA - metacarpo no plano do
    antebraco (punho no chao, sem carpo erguido); a bola so sobe o necessario para os dedos encostarem e o tufo de
    pelo sob o carpo comprimir no maximo PELO_CARPO. v20 escolhia carpo erguido (punho z 0,85 com cotovelo 0,20)."""
    b0_, inc0, de = p["pes"][k]
    base = V((b0_.x, b0_.y, B0[k].z + 0.02)); inc = PLANO[k] + INC_RETA
    p["pes"][k] = (base, inc, de); aplicar(p); ev = _ev(); by = PB[k].tail.y
    frente_ = [i for i in PATA[k] if ev[i].co.y < by - 0.03]
    dz = max(0.02 - min(ev[i].co.z for i in frente_), -PELO_CARPO - min(ev[i].co.z for i in PATA[k]))
    p["pes"][k] = (base + V((0, 0, dz)), inc, de + DEDOS_SOLTOS)
    if nome: aplicar(p); print("PATA_RETA", nome, k, "inc %.0f bola z %.2f punho z %.2f cotovelo z %.2f" % (inc, base.z + dz, PB[k].head.z, PB["Antebraco" + k[-1]].head.z))
    return p
INC_RETA = float(os.environ.get("LOBO_INC_RETA", "4"))
PELO_CARPO = float(os.environ.get("LOBO_PELO_CARPO", "0.40"))   # tufo sob o carpo comprime (perna deita reta)
def pe_rente(p, k, nome=""):
    """pata DEITADA (v17b): os DEDOS/almofadas (malha da pata a frente da bola) encostam no chao (z 0,02) - a bola sobe
    ou desce o necessario; entre as inclinacoes perto do plano (carpo/jarrete de rente a um pouco erguido) escolhe a que
    menos enterra o resto da pata (o tufo de pelo atras do carpo/jarrete). v17a erguia a bola ate o TUFO encostar e os
    dedos ficavam 0,5-0,7 no ar (a malha da pata e quase toda pesada no Mao/Metatarso, nao nos Dedos/Pe)."""
    b0_, inc0, de = p["pes"][k]
    base = V((b0_.x, b0_.y, B0[k].z + 0.02))
    melhor = None
    for inc in range(int(PLANO[k]) - 9, int(PLANO[k]) + 25, 3):
        p["pes"][k] = (base, float(inc), de); aplicar(p); ev = _ev(); by = PB[k].tail.y
        frente_ = [i for i in PATA[k] if ev[i].co.y < by - 0.03]
        if len(frente_) < 5: continue
        dz = 0.02 - min(ev[i].co.z for i in frente_)
        p["pes"][k] = (base + V((0, 0, dz)), float(inc), de); aplicar(p); ev = _ev()
        pen = max(0.0, -min(ev[i].co.z for i in PATA[k]))
        custo = 3.0 * pen + 0.01 * abs(inc - PLANO[k])
        if melhor is None or custo < melhor[0]: melhor = (custo, float(inc), dz, pen)
    _, inc, dz, pen = melhor
    if pen > 0.08: dz += pen - 0.08; pen = 0.08                          # o pelo de tras do carpo/jarrete comprime no maximo 0,08
    p["pes"][k] = (base + V((0, 0, dz)), inc, de)
    if nome: print("PE_RENTE", nome, k, "inc %.0f bola z %.2f tufo enterra %.2f" % (inc, base.z + dz, pen))
    return p
def contatos(p):
    """frente = antebracos (o peito repousa entre eles); tras = pelve ou canelas dobradas"""
    aplicar(p); ev = _ev()
    zf = min(min(ev[i].co.z for i in MEMBRO["MaoE"]), min(ev[i].co.z for i in MEMBRO["MaoD"]))
    zr = min(min(ev[i].co.z for i in V_TRAS), min(ev[i].co.z for i in MEMBRO["MetatarsoE"]), min(ev[i].co.z for i in MEMBRO["MetatarsoD"]))
    zp = min(ev[i].co.z for i in V_FRENTE)
    return zf, zr, zp
def assentar_deitado(p, nome="", pitch_alvo=None):
    """corpo DEITADO (v17b): antebracos (frente) e pelve/canelas (tras) encostam a 0,03 - o pitch iguala frente e tras e
    o dz desce ate o contato; o esterno, entre os antebracos, pode encostar (ate -0,05, pelo comprimido) mas nao afunda.
    v17a usava o esterno como contato da frente: o tronco empinava 18 graus e os ombros altos deixavam os cotovelos no ar."""
    for _ in range(12):
        zf, zr, zp = contatos(p)
        if pitch_alvo is None: p["raiz"][3] -= 12.0 * (zr - zf)
        else: p["raiz"][3] = pitch_alvo                               # costas niveladas; o quadril repousa nas coxas dobradas
        zf, zr, zp = contatos(p); p["raiz"][2] += 0.03 - min(zf, zr, zp + 0.08)
        if (pitch_alvo is not None or abs(zr - zf) < 0.02) and abs(0.03 - min(zf, zr, zp + 0.08)) < 0.01: break
    zf, zr, zp = contatos(p)
    print("ASSENTAR_DEITADO", nome, "pitch %.1f dz %.2f antebracos %.3f tras %.3f esterno %.3f" % (p["raiz"][3], p["raiz"][2], zf, zr, zp)); return p
DEIT_ABRE = float(os.environ.get("LOBO_ABRE", "0.45"))              # antebracos para fora: o peito afunda entre eles
DEIT_ESCAP = float(os.environ.get("LOBO_ESCAP", "-25"))             # giro das escapulas (cernelha mais baixa)
DEIT_COXA = float(os.environ.get("LOBO_COXA", "24"))                 # abertura das coxas (o quadril desce entre elas)
DEIT_SAG = float(os.environ.get("LOBO_SAG", "0"))                    # coluna cede para a barriga encostar
DEIT_SAG_P = float(os.environ.get("LOBO_SAGP", "15"))            # v19: peito cede, cernelha desce
DEIT_PELO = float(os.environ.get("LOBO_PELO", "-35"))                 # pelo da nuca/dorso/juba assentado sobre o corpo
QUEIXO_ALVO = float(os.environ.get("LOBO_QUEIXO", "0.05"))          # queixo no chao (0,05) ou sobre os antebracos (~0,4)
PITCH_DEITADO = float(os.environ.get("LOBO_PITCH", "-8.0"))        # v19 -8 (v18 -4; v17 igualava antebracos e pelve e empinava 18 graus: corcunda)
def deitado_pose(cabeca_baixa=False):
    """deitado esternal de lobo: peito e barriga no chao, antebracos deitados para a frente, patas traseiras dobradas ao
    lado do corpo (metatarsos no chao, joelhos para fora), cauda enrolada no chao. cabeca_baixa: queixo apoiado no chao
    entre as patas (cara no chao); senao cabeca erguida (alerta)."""
    o = {"Pescoco1": {"X": -6}, "Pescoco2": {"X": -4}, "Cabeca": {"X": -2}, "Peito": {"X": 2}, "JubaPeito": {"X": -14},
         "JubaE": {"X": -8}, "JubaD": {"X": -8}, "OrelhaE": {"X": 0 if not cabeca_baixa else -14}, "OrelhaD": {"X": 0 if not cabeca_baixa else -14},
         "CoxaE": {"Z": -DEIT_COXA}, "CoxaD": {"Z": DEIT_COXA}, "EscapulaE": {"X": DEIT_ESCAP}, "EscapulaD": {"X": DEIT_ESCAP},
         "Coluna1": {"X": DEIT_SAG}, "Coluna2": {"X": DEIT_SAG}, "Peito": {"X": DEIT_SAG_P},
         "PeloNuca1": {"X": DEIT_PELO}, "PeloNuca2": {"X": DEIT_PELO}, "PeloDorso1": {"X": DEIT_PELO}, "PeloDorso2": {"X": DEIT_PELO},
         "JubaE": {"X": -8 + DEIT_PELO}, "JubaD": {"X": -8 + DEIT_PELO}}
    for i, nm in enumerate(CAUDA): o[nm] = {"X": (30 if i == 0 else -2), "Z": (-16 if i > 1 else -6)}
    p = P(raiz=(0, -0.3, -2.9, -1.0, 0, 0), ossos=o,
          pes={"MaoE": ((DEIT_ABRE, -2.90, 0.02), PLANO["MaoE"], 6), "MaoD": ((-DEIT_ABRE, -2.90, 0.02), PLANO["MaoD"], 6),
               "MetatarsoE": ((0.75, -2.15, 0.02), PLANO["MetatarsoE"], 0), "MetatarsoD": ((-0.75, -2.15, 0.02), PLANO["MetatarsoD"], 0)})
    for volta in range(3):                                             # corpo e patas se acomodam juntos
        p = assentar_deitado(p, "deitado", PITCH_DEITADO)
        for k in PES:
            p = (pata_reta if k.startswith("Mao") else pe_rente)(p, k, "deitado" if volta == 2 else "")
    p["pes"] = {k: (v[0], v[1], v[2]) for k, v in p["pes"].items()}
    p = assentar_deitado(p, "deitado", PITCH_DEITADO)
    print("PES_DEITADO", " ".join("%s inc %.0f z %.2f dedos %.0f" % (k, p["pes"][k][1], p["pes"][k][0].z, p["pes"][k][2]) for k in PES))
    p = cauda_no_chao(p, -13.0, "deitado", atras=False, comprime=-0.30)
    if cabeca_baixa:
        p = cara_no_chao(p, QUEIXO_ALVO, "deitado_baixa"); p = assentar_deitado(p, "deitado_baixa", PITCH_DEITADO)
        p = cara_no_chao(p, QUEIXO_ALVO, "deitado_baixa")
        p = cauda_no_chao(p, -13.0, "deitado_baixa", atras=False, comprime=-0.30)   # cauda DEITADA rente ao chao (pelo comprime)
    return p
def agachado_pose():
    return P(raiz=(0, 0.25, -0.65, 4.0), ossos={"Pescoco1": {"X": -4}, "OrelhaE": {"X": -6}, "OrelhaD": {"X": -6}},
             pes={"MaoE": ((0, 0, 0), -8, 0), "MaoD": ((0, 0, 0), -8, 0), "MetatarsoE": ((0, 0, 0), -22, 0), "MetatarsoD": ((0, 0, 0), -22, 0)})
SENT, DEIT, DEIT_B = sentado_pose(), deitado_pose(), deitado_pose(True)
def meio_sentar(f=0.4):
    """fracao f do caminho de pe -> sentado: o peso vai para TRAS (quadril recua e desce, jarretes dobram) com as
    dianteiras PLANTADAS; o corpo desce o necessario para elas alcancarem (v16: IK das dianteiras 0,45 no meio)."""
    p = SENT; r = p["raiz"]
    q = P(raiz=(r[0] * f, r[1] * f + 0.10 * math.sin(math.pi * f), r[2] * f, r[3] * f, 0, 0), ossos={k: {e: g * f for e, g in v.items()} for k, v in p["ossos"].items()},
          pes={"MaoE": (p["pes"]["MaoE"][0] * f + B0["MaoE"] * (1 - f) - B0["MaoE"], p["pes"]["MaoE"][1] * f, 0),
               "MaoD": (p["pes"]["MaoD"][0] * f + B0["MaoD"] * (1 - f) - B0["MaoD"], p["pes"]["MaoD"][1] * f, 0),
               "MetatarsoE": (V((0.08, -0.10, 0.0)) * min(1, f / 0.4), -36 * min(1, f / 0.4) + (p["pes"]["MetatarsoE"][1] + 36) * max(0, (f - 0.4) / 0.6), 0),
               "MetatarsoD": (V((-0.08, -0.10, 0.0)) * min(1, f / 0.4), -36 * min(1, f / 0.4) + (p["pes"]["MetatarsoD"][1] + 36) * max(0, (f - 0.4) / 0.6), 0)})
    if f > 0.4:                                                        # traseiras: o passo para a frente comeca depois de 40%
        for k in ("MetatarsoE", "MetatarsoD"):
            g = (f - 0.4) / 0.6; b_ = p["pes"][k][0]; q["pes"][k] = (B0[k] + (V((0.08 if k[-1] == "E" else -0.08, -0.10, 0.0))).lerp(b_ - B0[k], g), q["pes"][k][1], 0)
    for _ in range(8):
        aplicar(q); d_ = min(ALVO[k].location.z - PB["Antebraco" + k[-1]].tail.z for k in ("MaoE", "MaoD"))
        e_ = max((PB["Antebraco" + k[-1]].tail - ALVO[k].location).length for k in ("MaoE", "MaoD"))
        if e_ < 0.01: break
        q["raiz"][2] += d_ if d_ < 0 else -e_
    print("MEIO_SENTAR f %.2f raiz dz %.2f erro dianteiras %.3f" % (f, q["raiz"][2], e_))
    return q
def cotovelos_pose():
    """1a fase do deitar: dianteiras dobram, cotovelos e antebracos no chao (patas ja na posicao final), peito desce;
    o quadril ainda alto sobre as traseiras pouco dobradas. pitch buscado para o IK das traseiras alcancar."""
    d = DEIT
    def montar(pit, dz):
        o = {"Pescoco1": {"X": -10}, "Pescoco2": {"X": -6}, "Cabeca": {"X": -4}, "Peito": {"X": 2}, "OrelhaE": {"X": -2}, "OrelhaD": {"X": -2}}
        for nm in CAUDA: o[nm] = dict(d["ossos"].get(nm, {}))
        return P(raiz=(0, -0.25, dz, pit, 0, 0), ossos=o,
                 pes={"MaoE": (d["pes"]["MaoE"][0] - B0["MaoE"], d["pes"]["MaoE"][1], d["pes"]["MaoE"][2]),
                      "MaoD": (d["pes"]["MaoD"][0] - B0["MaoD"], d["pes"]["MaoD"][1], d["pes"]["MaoD"][2]),
                      "MetatarsoE": ((0.05, -0.10, 0), -18, 0), "MetatarsoD": ((-0.05, -0.10, 0), -18, 0)})
    melhor = None
    for pit in range(0, 31, 2):
        p = montar(pit, 0.0)
        for _ in range(4):                                                 # peito a 0,35 do chao
            aplicar(p); ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
            zf = min(ev[i].co.z for i in V_FRENTE); p["raiz"][2] += 0.35 - zf
        aplicar(p)
        e = max((PB["Canela" + s_].tail - ALVO["Metatarso" + s_].location).length for s_ in "ED") + \
            max((PB["Antebraco" + s_].tail - ALVO["Mao" + s_].location).length for s_ in "ED")
        if e < 0.01: melhor = (e, pit, p)                                   # o maior pitch que ainda alcanca
        elif melhor is None: melhor = (e, pit, p)
    print("COTOVELOS pitch %d erro IK %.3f raiz dz %.2f" % (melhor[1], melhor[0], melhor[2]["raiz"][2]))
    q = melhor[2]
    for k in ("MaoE", "MaoD"): q = pe_rente(q, k)
    # cauda tambem repousa nesta fase (quadril alto): sem isso ela pendia ate o chao e o passo de malha a erguia em pluma
    q = cauda_no_chao(q, -13.0, "cotovelos", atras=False, comprime=-0.30)
    return q
def meio_deitar():
    return cotovelos_pose()
def apoios_pose():
    """antes de levantar: ainda deitado, traz as patas para debaixo do corpo (dianteiras sob os ombros, traseiras sob o
    quadril) - patas rentes ao chao, corpo continua apoiado"""
    d = DEIT
    q = P(raiz=list(d["raiz"][:3]) + [d["raiz"][3], 0, 0], ossos={k: dict(v) for k, v in d["ossos"].items()},
          pes={"MaoE": (d["pes"]["MaoE"][0] - B0["MaoE"], d["pes"]["MaoE"][1], d["pes"]["MaoE"][2]),
               "MaoD": (d["pes"]["MaoD"][0] - B0["MaoD"], d["pes"]["MaoD"][1], d["pes"]["MaoD"][2]),
               "MetatarsoE": ((0.45, -1.10, 0.02), PLANO["MetatarsoE"], 0), "MetatarsoD": ((-0.45, -1.10, 0.02), PLANO["MetatarsoD"], 0)})
    # dianteiras FICAM onde estavam (empurram o peito para cima); so as traseiras vem para debaixo do quadril
    for k in ("MetatarsoE", "MetatarsoD"): q = pe_rente(q, k)
    q = assentar_deitado(q, "apoios")
    for k in ("MetatarsoE", "MetatarsoD"): q = pe_rente(q, k)
    return q
COTOV, APOIO = cotovelos_pose(), apoios_pose()
MS = [meio_sentar(0.3), meio_sentar(0.6), meio_sentar(0.85)]
RESP_PESC = float(os.environ.get("LOBO_RESP_PESC", "1.8"))
def respira(base, amp=1.0, T=4.0, cabeca_apoiada=False):
    def f(t):
        w = 2 * math.pi * t / T
        p = {"raiz": list(base["raiz"]), "ossos": {k: dict(v) for k, v in base["ossos"].items()}, "pes": dict(base["pes"])}
        p["raiz"][2] += 0.006 * amp * (1 + math.sin(w))                  # so sobe (nao atravessa o chao)
        somar_ossos(p["ossos"], {"Peito": {"X": -0.8 * amp * math.sin(w)}, "JubaPeito": {"X": 1.2 * amp * math.sin(w - 1)},
                                 "Cabeca": {"X": (0.0 if cabeca_apoiada else 0.6) * amp * math.sin(w - 0.7)}})
        if cabeca_apoiada == "fixa":                                   # v24 (dormindo): o pescoco desfaz o giro do peito -> a cara fica PARADA encostada
            somar_ossos(p["ossos"], {"Pescoco1": {"X": RESP_PESC * 0.8 * amp * math.sin(w)}})
        return p
    return f
# ---- DORMINDO (09/11, foto do usuario ref/dormir/lobo_dormindo_referencia.webp): lobo dormindo de lado sobre o quadril
# direito - tronco tombado para a direita, as DUAS traseiras estendidas para o lado esquerdo e para tras, dianteira
# esquerda esticada a frente rente ao chao, dianteira direita recolhida sob o peito, cabeca deitada com a bochecha/queixo
# no chao, orelhas para tras, cauda ao longo do corpo. (Olhos fechados: o rig nao tem palpebras - ver ficha.)
def _ev_env(n, d): return float(os.environ.get(n, d))
DORM_ROLL = _ev_env("LOBO_D_ROLL", "0")            # v23: o PEITO nao tomba (tombar o tronco erguia o ombro direito a 3,3 e o cotovelo a 2,2)
DORM_PELVE = _ev_env("LOBO_D_PELVE", "-30")        # so o QUADRIL tomba sobre o lado esquerdo (graus em Y)
def dormindo_pose():
    """v23 - foto ref/dormir lida detalhe por detalhe (camera na frente-direita do lobo, baixa):
    - tombado sobre o quadril ESQUERDO, flanco direito para cima, dorso alto e arredondado, corpo encurtado (enrolado);
    - traseira DIREITA (a de cima) vem para a FRENTE ao longo da barriga, rente ao chao, pata perto do cotovelo direito;
    - traseira esquerda dobrada por baixo do corpo (nao aparece);
    - dianteira DIREITA: cotovelo sob o peito, ANTEBRACO deitado no chao para a frente (nao a perna toda esticada),
      pata pousada com os dedos para a frente, logo ao lado do focinho;
    - dianteira esquerda recolhida sob o peito/queixo (nao aparece);
    - cabeca com o QUEIXO no chao POR DENTRO da pata direita, focinho para a frente-direita (para a camera), cabeca um
      pouco tombada sobre a bochecha esquerda; orelhas em pe, soltas.
    v22 errava: traseira direita esticada para TRAS (corpo comprido), perna dianteira inteira esticada e virada para
    fora, cabeca atravessando o antebraco; e o queixo do clipe ficava a -0,28 (a busca de giro repetia o cara_no_chao
    sobre o pescoco ja dobrado e nao podia subir a cabeca)."""
    d = DEIT_B
    o = {k: dict(v) for k, v in d["ossos"].items()}
    curva = _ev_env("LOBO_D_CURVA", "0")                               # coluna enrolada para a direita (graus em Z por osso)
    somar_ossos(o, {"Pelve": {"Y": -DORM_PELVE, "Z": curva}, "Coluna1": {"Y": -DORM_PELVE * _ev_env("LOBO_D_COL_Y", "0.15"), "Z": curva}, "Coluna2": {"Z": curva},
                    "Pescoco1": {"Z": _ev_env("LOBO_D_PESC_YAW", "0")},
                    "Cabeca": {"X": _ev_env("LOBO_D_CAB_X", "-25"), "Y": _ev_env("LOBO_D_CAB_ROLL", "14"), "Z": _ev_env("LOBO_D_CAB_YAW", "-14")},
                    "Mandibula": {"X": _ev_env("LOBO_D_BOCA", "-5")}, "OrelhaE": {"X": -6}, "OrelhaD": {"X": -6}})
    for nm in ("CoxaE", "CoxaD"): o[nm] = {}
    r = list(d["raiz"]); r[4] = -DORM_ROLL
    pe = {k: (d["pes"][k][0] - B0[k], d["pes"][k][1], d["pes"][k][2]) for k in PES}
    pe["MaoD"] = ((-_ev_env("LOBO_D_MD_X", "0.8"), -_ev_env("LOBO_D_MD_Y", "2.7"), 0.02), PLANO["MaoD"], 6)
    pe["MaoE"] = ((_ev_env("LOBO_D_ME_X", "-0.4"), _ev_env("LOBO_D_ME_Y", "2.0"), 0.02), PLANO["MaoE"], 6)   # dianteira esquerda recolhida sob o peito (na foto nao aparece)
    pe["MetatarsoD"] = ((-_ev_env("LOBO_D_TD_X", "1.0"), -_ev_env("LOBO_D_TD_Y", "1.3"), 0.02), PLANO["MetatarsoD"], 0)
    pe["MetatarsoE"] = ((_ev_env("LOBO_D_TE_X", "0.2"), -_ev_env("LOBO_D_TE_Y", "1.3"), 0.02), PLANO["MetatarsoE"], 0)
    q = P(raiz=r, ossos=o, pes=pe)
    for volta in range(3):
        q = assentar_deitado(q, "dormindo", PITCH_DEITADO)
        q = pata_reta(q, "MaoD", "dormindo" if volta == 2 else ""); q = pe_rente(q, "MaoE")
        for k in ("MetatarsoE", "MetatarsoD"): q = pe_rente(q, k)
    q = assentar_deitado(q, "dormindo", PITCH_DEITADO)
    q = cauda_no_chao(q, -_ev_env("LOBO_D_CAUDA", "12"), "dormindo", atras=False, comprime=-0.30)
    # v23: com o quadril tombado 30 graus o pelo da BASE da cauda (Cauda2) entrava 0,65 no chao; ergue Cauda1/Cauda2
    # (o sinal que sobe e testado) ate o pelo comprimir no maximo 0,30
    V_C2 = [v.index for v in LO.data.vertices if v.groups and _gi[max(v.groups, key=lambda g_: g_.weight).group] in (CAUDA[0], CAUDA[1])]
    def zc(qq):                                                        # como no clipe: sem o passo de malha da cauda
        m0 = globals()["CAUDA_MALHA"]; globals()["CAUDA_MALHA"] = False
        aplicar(qq); ev = _ev(); z_ = min(ev[i].co.z for i in V_C2); globals()["CAUDA_MALHA"] = m0; return z_
    z0 = zc(q)
    if z0 < -0.30:
        sinal = 1.0
        q["ossos"].setdefault(CAUDA[0], {}); q["ossos"][CAUDA[0]]["X"] = q["ossos"][CAUDA[0]].get("X", 0.0) + 2.0
        if zc(q) < z0: sinal = -1.0
        q["ossos"][CAUDA[0]]["X"] -= 2.0
        for _ in range(30):
            if zc(q) >= -0.30: break
            q["ossos"][CAUDA[0]]["X"] += 1.5 * sinal; q["ossos"].setdefault(CAUDA[1], {}); q["ossos"][CAUDA[1]]["X"] = q["ossos"][CAUDA[1]].get("X", 0.0) + 0.5 * sinal
        print("CAUDA_BASE dormindo de %.2f para %.2f" % (z0, zc(q)))
    V_CAB = [v.index for v in LO.data.vertices if v.groups and _gi[max(v.groups, key=lambda g_: g_.weight).group] in ("Cabeca", "Mandibula")]
    def invade(qq):
        aplicar(qq); ev = _ev(); n = 0
        for b_ in ("AntebracoD", "MaoD", "AntebracoE", "MaoE"):
            a_, c_ = PB[b_].head, PB[b_].tail; ab = c_ - a_; L2 = ab.dot(ab)
            for i in V_CAB:
                pv = ev[i].co; t = max(0.0, min(1.0, (pv - a_).dot(ab) / L2))
                if (pv - (a_ + ab * t)).length < 0.40: n += 1
        return n
    # o pescoco (Pescoco1/2 em Z) leva a cabeca para DENTRO da pata direita; cada giro parte da cabeca erguida e o
    # cara_no_chao pousa o queixo do zero (v22 repetia sobre o pescoco ja dobrado)
    base_o = {k: dict(v) for k, v in q["ossos"].items()}
    melhor = None
    for yaw in range(-6, 31, 4):                                        # (+ = pescoco para a esquerda, longe da pata direita)
        qq = {"raiz": list(q["raiz"]), "ossos": {k: dict(v) for k, v in base_o.items()}, "pes": dict(q["pes"])}
        somar_ossos(qq["ossos"], {"Pescoco1": {"Z": yaw * 0.5}, "Pescoco2": {"Z": yaw * 0.5}, "Cabeca": {"Z": -yaw * 0.6}})
        qq = cara_no_chao(qq, _ev_env("LOBO_D_QUEIXO", "0.0"), "", amin=-60)   # v24: encosta (0), nao paira (v23 0,05)
        n = invade(qq)
        if melhor is None or (n, abs(yaw)) < (melhor[0], abs(melhor[1])): melhor = (n, yaw, qq)
    print("CABECA_FORA_DA_PERNA giro do pescoco %d graus, vertices dentro %d" % (melhor[1], melhor[0])); q = melhor[2]
    for l_ in PALP_FECHA: q["ossos"]["Palpebra" + l_] = {"F": 1.0}       # v25: dorme de olhos fechados
    aplicar(q); ev = _ev(); print("DORMINDO queixo z %.3f" % min(ev[i].co.z for i in V_CAB), " ".join("%s:(%.2f,%.2f,%.2f)" % (k, *PB[k].tail) for k in PES))
    return q
DORM = dormindo_pose()
ERGUE_PEITO = _ev_env("LOBO_D_ERGUE", "0.35")
def ergue_peito(p, u):
    """v23: enquanto a dianteira esquerda recolhe para baixo do peito (ou sai dali), o peito sobe um pouco (u 0..1, pico
    no meio) - sem isso o braco esquerdo dobrava para dentro do chao (-0,6)"""
    u = min(1.0, max(0.0, u)); h = ERGUE_PEITO * math.sin(math.pi * u)
    if h > 0: p["raiz"][2] += h; p["raiz"][3] -= 6.0 * h
    return p
def olhos(p, f):
    for l_ in PALP_FECHA: p["ossos"]["Palpebra" + l_] = {"F": max(0.0, min(1.0, f))}
    return p
def curva_olhos(t, pts):
    """pts = [(t, fracao fechada)], suavizado entre pontos"""
    if t <= pts[0][0]: return pts[0][1]
    for (t0, f0), (t1, f1) in zip(pts, pts[1:]):
        if t <= t1: return lerp(f0, f1, suave((t - t0) / (t1 - t0)))
    return pts[-1][1]
OLHOS_ADORMECER = [(0.0, 0.0), (0.5, 0.0), (0.9, 0.55), (1.15, 0.6), (1.35, 0.3), (1.6, 0.35), (2.1, 1.0)]   # pesam, piscam, fecham
OLHOS_DESPERTAR = [(0.0, 1.0), (0.3, 1.0), (0.55, 0.45), (0.7, 0.5), (0.8, 0.95), (0.95, 0.9), (1.2, 0.0)]   # entreabre, pisca, abre
def adormecer(t):
    """deitado com a cara no chao -> tomba devagar para o lado e estende as traseiras (2,4 s); os olhos pesam e fecham"""
    p = chaves([(0.0, DEIT_B, None), (1.0, DEIT_B, None), (2.4, DORM, {"MetatarsoE": 0.25, "MetatarsoD": 0.25, "MaoE": 0.15})])(t)
    return olhos(ergue_peito(p, (t - 1.0) / 1.4), curva_olhos(t, OLHOS_ADORMECER))
def despertar(t):
    base = chaves([(0.0, DORM, None), (0.9, DEIT_B, {"MetatarsoE": 0.25, "MetatarsoD": 0.25, "MaoE": 0.15}), (1.4, DEIT, None), (3.0, DEIT, None)])(t)
    # v23: a pata esquerda sai de baixo do peito enquanto a cabeca ainda esta baixa -> a cabeca sobe um pouco na troca
    somar_ossos(base["ossos"], {"Pescoco1": {"X": -14 * math.sin(math.pi * min(1.0, max(0.0, t / 0.9)))}})
    base = ergue_peito(base, t / 0.9)
    olhos(base, curva_olhos(t, OLHOS_DESPERTAR))
    t = t - 0.4                                                       # (v22: acorda do sono de lado; o olhar em volta vem depois)
    yaw = 26 * math.sin(math.pi * suave((t - 0.9) / 1.4) * 2) * (0.9 < t < 2.3)
    somar_ossos(base["ossos"], {"Pescoco2": {"Z": yaw * 0.5}, "Cabeca": {"Z": yaw * 0.5},
                                "OrelhaE": {"X": 6 * suave((t - 0.3) / 0.4) - 6 * suave((t - 0.0) / 0.3) * 0}, "OrelhaD": {"X": 6 * suave((t - 0.3) / 0.4)}})
    return base
# ---- salto / uivo / rosnado / mordida / garra / impacto
def clipe_salto(t):
    agach = agachado_pose()
    imp = P(raiz=(0, 0.1, 0.35, -10.0), ossos={"Pescoco1": {"X": -8}, "Cabeca": {"X": -4}},
            pes={"MaoE": ((0, -0.2, 0.55), 30, 20), "MaoD": ((0, -0.2, 0.55), 30, 20), "MetatarsoE": ((0, 0.1, 0.30), 28, 10), "MetatarsoD": ((0, 0.1, 0.30), 28, 10)})
    ar_r = (0, -0.4, 2.1, -4.0); M_ar = pose_raiz(list(ar_r) + [0, 0])
    ar = P(raiz=ar_r, ossos={"Pescoco1": {"X": -4}, "OrelhaE": {"X": -12}, "OrelhaD": {"X": -12}})
    for k, ext, inc in (("MaoE", V((0, 0.35, 0.75)), 70), ("MaoD", V((0, 0.35, 0.75)), 70), ("MetatarsoE", V((0, -0.35, 0.55)), 55), ("MetatarsoD", V((0, -0.35, 0.55)), 55)):
        ar["pes"][k] = (mundo_pe(M_ar, k, ext), inc, 25)
    desce_r = (0, -0.6, 0.9, 6.0); M_d = pose_raiz(list(desce_r) + [0, 0])
    desce = P(raiz=desce_r, ossos={"Pescoco1": {"X": 6}, "Cabeca": {"X": -6}})
    for k, ext, inc in (("MaoE", V((0, -0.45, -0.1)), -10, ), ("MaoD", V((0, -0.45, -0.1)), -10), ("MetatarsoE", V((0, -0.2, 0.75)), 50), ("MetatarsoD", V((0, -0.2, 0.75)), 50)):
        desce["pes"][k] = (mundo_pe(M_d, k, ext), inc, 0)
    toque = P(raiz=(0, -0.7, -0.15, 7.0), ossos={"Pescoco1": {"X": 8}},
              pes={"MaoE": ((0, -0.7, 0), -6, 0), "MaoD": ((0, -0.7, 0), -6, 0), "MetatarsoE": ((0, -0.5, 0.35), 25, 10), "MetatarsoD": ((0, -0.5, 0.35), 25, 10)})
    amort = P(raiz=(0, -0.7, -0.55, 2.0), ossos={"Pescoco1": {"X": 4}},
              pes={"MaoE": ((0, -0.7, 0), -8, 0), "MaoD": ((0, -0.7, 0), -8, 0), "MetatarsoE": ((0, -0.7, 0), -20, 0), "MetatarsoD": ((0, -0.7, 0), -20, 0)})
    fim = P(raiz=(0, -0.7, 0, 0), pes={k: ((0, -0.7, 0), 0, 0) for k in PES})
    return chaves([(0.0, NEUTRO, None), (0.28, agach, None), (0.40, imp, None), (0.62, ar, None), (0.84, desce, None),
                   (0.92, toque, None), (1.08, amort, None), (1.45, fim, None)])(t)
def boca_aberta(g): return {"Mandibula": {"X": g}}
def clipe_uivo(t):
    cab = {"Pescoco1": {"X": -22}, "Pescoco2": {"X": -16}, "Cabeca": {"X": -14}, "Peito": {"X": -3},
           "OrelhaE": {"X": -10, "Y": 6}, "OrelhaD": {"X": -10, "Y": -6}, "JubaPeito": {"X": -6}}
    prep = P(raiz=(0, 0.05, 0.05, -3.0), ossos=dict(cab))
    abre = P(raiz=(0, 0.05, 0.08, -4.0), ossos={**cab, **boca_aberta(20)})
    sus = P(raiz=(0, 0.05, 0.10, -5.0), ossos={**{k: {e: g * 1.08 for e, g in v.items()} for k, v in cab.items()}, **boca_aberta(24)})
    fecha = P(raiz=(0, 0.05, 0.05, -3.0), ossos={**cab, **boca_aberta(2)})
    p = chaves([(0.0, NEUTRO, None), (0.55, prep, None), (0.80, abre, None), (3.0, sus, None), (3.35, fecha, None), (4.0, NEUTRO, None)])(t)
    if 0.8 < t < 3.0: somar_ossos(p["ossos"], {"Mandibula": {"X": 1.5 * math.sin(2 * math.pi * t * 1.3)}, "Cabeca": {"X": -0.8 * math.sin(2 * math.pi * t * 0.7)}})
    return p
def clipe_rosnar(t):
    pos = P(raiz=(0, 0.25, -0.35, 6.0), ossos={"Pescoco1": {"X": 16}, "Pescoco2": {"X": 4}, "Cabeca": {"X": -12}, "Peito": {"X": 2},
                                               "OrelhaE": {"X": -34, "Y": 10}, "OrelhaD": {"X": -34, "Y": -10}, "Mandibula": {"X": 9},
                                               "JubaE": {"X": 6}, "JubaD": {"X": 6}, "JubaPeito": {"X": 4},
                                               **{nm: {"X": 10 if i == 0 else 2} for i, nm in enumerate(CAUDA)}},
            pes={"MaoE": ((0, -0.15, 0), -10, 0), "MaoD": ((0, -0.15, 0), -10, 0), "MetatarsoE": ((0, 0, 0), -12, 0), "MetatarsoD": ((0, 0, 0), -12, 0)})
    p = chaves([(0.0, NEUTRO, None), (0.40, pos, None), (2.0, pos, None), (2.4, NEUTRO, None)])(t)
    if 0.4 < t < 2.0:
        somar_ossos(p["ossos"], {"Mandibula": {"X": 1.2 * math.sin(2 * math.pi * t * 11)}, "Cabeca": {"X": 0.5 * math.sin(2 * math.pi * t * 9)}})
        p["raiz"][2] += 0.01 * math.sin(2 * math.pi * t * 10)
    return p
def clipe_mordida(t):
    ant = P(raiz=(0, 0.35, -0.25, 2.0), ossos={"Pescoco1": {"X": -6}, "Cabeca": {"X": -4}, "Mandibula": {"X": 24}, "OrelhaE": {"X": -18}, "OrelhaD": {"X": -18}},
            pes={k: ((0, 0, 0), -8 if k.startswith("Mao") else -14, 0) for k in PES})
    bote = P(raiz=(0, -0.85, -0.10, 6.0), ossos={"Pescoco1": {"X": 10}, "Pescoco2": {"X": 6}, "Cabeca": {"X": 4}, "Mandibula": {"X": 22}, "OrelhaE": {"X": -22}, "OrelhaD": {"X": -22}},
             pes={k: ((0, 0, 0), 14 if k.startswith("Mao") else 18, 0) for k in PES})
    fecha = P(raiz=(0, -0.80, -0.12, 6.0), ossos={"Pescoco1": {"X": 11}, "Pescoco2": {"X": 6}, "Cabeca": {"X": 6}, "Mandibula": {"X": 0}, "OrelhaE": {"X": -22}, "OrelhaD": {"X": -22}},
              pes={k: ((0, 0, 0), 14 if k.startswith("Mao") else 18, 0) for k in PES})
    return chaves([(0.0, NEUTRO, None), (0.26, ant, None), (0.42, bote, None), (0.48, fecha, None), (0.62, fecha, None), (1.0, NEUTRO, None)])(t)
def clipe_garra(t):
    """golpe com a pata dianteira direita: peso para tras/esquerda, ergue, varre para frente e para baixo"""
    carga = P(raiz=(0.15, 0.30, -0.15, -4.0, -4.0), ossos={"Pescoco1": {"X": -4, "Z": -6}, "Cabeca": {"Z": -4}, "OrelhaE": {"X": -16}, "OrelhaD": {"X": -16}},
              pes={"MaoE": ((0, 0, 0), -6, 0), "MaoD": ((-0.1, 0.30, 1.45), 55, 30), "MetatarsoE": ((0, 0, 0), -12, 0), "MetatarsoD": ((0, 0, 0), -12, 0)})
    golpe = P(raiz=(0.05, -0.30, -0.10, 4.0, -2.0), ossos={"Pescoco1": {"X": 6, "Z": 4}, "Cabeca": {"X": 2}, "OrelhaE": {"X": -18}, "OrelhaD": {"X": -18}},
              pes={"MaoE": ((0, 0, 0), 8, 0), "MaoD": ((0.25, -1.30, 0.45), -10, -10), "MetatarsoE": ((0, 0, 0), 6, 0), "MetatarsoD": ((0, 0, 0), 6, 0)})
    apoio = P(raiz=(0, -0.20, -0.05, 2.0), pes={"MaoE": ((0, 0, 0), 4, 0), "MaoD": ((0.1, -0.9, 0), -4, 0), "MetatarsoE": ((0, 0, 0), 2, 0), "MetatarsoD": ((0, 0, 0), 2, 0)})
    return chaves([(0.0, NEUTRO, None), (0.30, carga, None), (0.50, golpe, None), (0.64, apoio, None), (1.05, NEUTRO, {"MaoD": 0.30})])(t)
def clipe_impacto(t):
    hit = P(raiz=(-0.10, 0.40, 0.05, -4.0, 6.0, -4.0), ossos={"Pescoco1": {"Z": -10, "X": -6}, "Cabeca": {"Z": -10, "X": -6},
                                                             "OrelhaE": {"X": -30}, "OrelhaD": {"X": -30}, "Mandibula": {"X": 6}, "Peito": {"Z": -3}})
    meio = P(raiz=(-0.05, 0.20, -0.08, 1.0, 2.0, -1.5), ossos={"Pescoco1": {"Z": -4}, "Cabeca": {"Z": -3}, "OrelhaE": {"X": -14}, "OrelhaD": {"X": -14}})
    return chaves([(0.0, NEUTRO, None), (0.10, hit, None), (0.32, meio, None), (0.65, NEUTRO, None)])(t)

CLIPES = {  # nome: (funcao, duracao s, loop, velocidade de deslocamento studs/s (parametro do clipe), marcadores {nome: t})
    "Repouso": (clipe_repouso, 4.0, True, 0.0, {}),
    "Observar": (clipe_observar, 4.5, False, 0.0, {"OlharEsquerda": 0.6, "OlharDireita": 2.4}),
    "Andar": (marcha(**ANDAR), ANDAR["T"], True, vel(ANDAR), {}),
    "Trote": (marcha(**TROTE), TROTE["T"], True, vel(TROTE), {}),
    "Corrida": (marcha(**GALOPE), GALOPE["T"], True, vel(GALOPE), {}),
    "Partida": (rampa_trote(True, 2 * TROTE["T"]), 2 * TROTE["T"], False, vel(TROTE), {"EmTrote": 2 * TROTE["T"]}),
    "Freada": (rampa_trote(False, 2 * TROTE["T"]), 2 * TROTE["T"], False, 0.0, {"Parado": 2 * TROTE["T"]}),
    "VirarE": (virar(+1), 2.4, False, 0.0, {"GiroCompleto": 2.35}),
    "VirarD": (virar(-1), 2.4, False, 0.0, {"GiroCompleto": 2.35}),
    "Sentar": (chaves([(0.0, NEUTRO, None), (0.45, MS[0], None), (0.8, MS[1], None), (1.15, MS[2], {"MetatarsoE": 0.10, "MetatarsoD": 0.10}),
                       (1.6, SENT, {"MetatarsoE": 0.10, "MetatarsoD": 0.10})]), 1.6, False, 0.0, {"Sentado": 1.6}),
    "Sentado": (respira(SENT), 4.0, True, 0.0, {}),
    "LevantarSentado": (chaves([(0.0, SENT, None), (0.35, MS[2], {"MetatarsoE": 0.10, "MetatarsoD": 0.10}), (0.7, MS[1], {"MetatarsoE": 0.10, "MetatarsoD": 0.10}),
                                (1.0, MS[0], None), (1.4, NEUTRO, None)]), 1.4, False, 0.0, {"EmPe": 1.4}),
    "Deitar": (chaves([(0.0, NEUTRO, None), (0.9, COTOV, {"MaoE": 0.30, "MaoD": 0.30}), (1.9, DEIT, {"MetatarsoE": 0.22, "MetatarsoD": 0.22}),
                       (2.3, DEIT, None), (3.1, DEIT_B, None)]), 3.1, False, 0.0, {"Cotovelos": 0.9, "Deitado": 1.9, "CaraNoChao": 3.1}),
    "Deitado": (respira(DEIT_B, 1.0, 4.0, True), 4.0, True, 0.0, {}),
    "Descanso": (respira(DORM, 0.7, 5.5, "fixa"), 5.5, True, 0.0, {}),                   # dorme de lado (foto do usuario)
    "Adormecer": (adormecer, 2.4, False, 0.0, {"Dormindo": 2.4}),
    "Despertar": (despertar, 3.0, False, 0.0, {"Alerta": 1.1}),
    "LevantarDeitado": (chaves([(0.0, DEIT_B, None), (0.5, DEIT, None), (1.1, APOIO, {"MaoE": 0.18, "MaoD": 0.18, "MetatarsoE": 0.18, "MetatarsoD": 0.18}),
                               (1.8, agachado_pose(), {"MaoE": 0.25, "MaoD": 0.25}), (2.3, NEUTRO, None)]), 2.3, False, 0.0, {"Apoios": 1.1, "EmPe": 2.3}),
    "Salto": (clipe_salto, 1.45, False, 0.0, {"Impulso": 0.30, "Decolagem": 0.42, "Aterrissagem": 0.90, "Recuperado": 1.45}),
    "Uivo": (clipe_uivo, 4.0, False, 0.0, {"UivoInicio": 0.78, "UivoFim": 3.2}),
    "Rosnar": (clipe_rosnar, 2.4, False, 0.0, {"RosnadoInicio": 0.42, "RosnadoFim": 2.0}),
    "Mordida": (clipe_mordida, 1.0, False, 0.0, {"Antecipacao": 0.26, "Contato": 0.48, "Recuperacao": 0.62}),
    "Garra": (clipe_garra, 1.05, False, 0.0, {"Antecipacao": 0.30, "Contato": 0.50, "Recuperacao": 0.64}),
    "Impacto": (clipe_impacto, 0.65, False, 0.0, {"Impacto": 0.10}),
}
QUAIS = A[1].split(",") if len(A) > 1 else list(CLIPES)
ROT_RAIZ = {"VirarE": 90.0, "VirarD": -90.0}

# ------------------------------------------------------------------ amostragem -> QA -> FK -> acao + JSON
APOIO = {"Andar": ANDAR, "Trote": TROTE, "Corrida": GALOPE}
dg = bpy.context.evaluated_depsgraph_get()
manifesto = {}; QUADROS = {}
paw_idx = None
def malha_zmin():
    ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    bolas = [PB[k].tail for k in PES]
    zmin, onde = 9.0, None
    for v in ev.vertices:
        c = v.co
        if c.z < zmin and all((c - b).length > 1.1 for b in bolas): zmin, onde = c.z, c.copy()
    return zmin, onde
for nome in QUAIS:
    fn, dur, loop, vel_, marc = CLIPES[nome]
    # poses de chao paradas: a cauda ja repousa (sem passo de malha, que a erguia como pluma); TRANSICOES: o passo de
    # malha volta com limite -0,15, so para a cauda nao varar o chao no meio do movimento (v17a: ate -0,97)
    TRANSICAO = nome in ("Sentar", "LevantarSentado", "Deitar", "LevantarDeitado", "Despertar", "Adormecer")
    CAUDA_MALHA = (nome not in CAUDA_NO_CHAO) or TRANSICAO
    CAUDA_LIMITE = -0.15 if TRANSICAO else 0.04
    nq = int(round(dur * FPS)) + (0 if loop else 1)
    alin = {}
    quadros = []; erro_ik = 0.0; erro_pe = {k: 0.0 for k in PES}; desliza = 0.0; dedo_min = 9.0; prev = None; malha_min = (9.0, None); perto = 9.0
    raiz_hist = []
    eleva = [0.0] * nq
    if nome not in APOIO and nome not in CAUDA_NO_CHAO:              # 1a passada: quanto a malha (fora das patas) desce do chao
        # (v17: fora dos clipes de chao - as poses deitada/sentada ja sao assentadas pelo nucleo do corpo; aqui o pelo da
        #  cauda e as mechas encostados no solo ERGUIAM o lobo inteiro 0,3-0,4 e deixavam peito e cotovelos suspensos)
        def malha_min_fora():
            ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
            return min(ev[i].co.z for i in V_CORPO)
        bruto = []
        for qi in range(0, nq, 2):
            aplicar(fn(qi / FPS)); bruto.append(max(0.0, 0.03 - malha_min_fora()))
        bruto = [bruto[min(len(bruto) - 1, qi // 2)] for qi in range(nq)]
        mx = [max(bruto[max(0, i - 5):i + 6]) for i in range(nq)]
        eleva = [sum(mx[max(0, i - 5):i + 6]) / len(mx[max(0, i - 5):i + 6]) for i in range(nq)]
        if loop: eleva = [max(eleva)] * nq                            # ciclo parado: elevacao constante (fecha o loop)
        if max(eleva) > 0: print("   ELEVACAO", nome, "max %.3f" % max(eleva))
    for qi in range(nq):
        t = qi / FPS
        p = fn(t); p["raiz"][2] += eleva[qi]
        # secundario por velocidade do corpo (diferenca finita da raiz)
        r_ = p["raiz"]; raiz_hist.append((r_[1], r_[2]))
        if len(raiz_hist) > 1:
            vy = (raiz_hist[-1][0] - raiz_hist[-2][0]) * FPS; vz = (raiz_hist[-1][1] - raiz_hist[-2][1]) * FPS
            secundario(p, t, (vy, vz), amp=1.0)
        vento(p, t, dur, vel_, nome)
        if nome in ("Sentar", "LevantarSentado", "Deitar", "LevantarDeitado"):   # patas PLANTADAS alcancam o chao em todo
            for _ in range(8):                                           # quadro (v16: 0,41-0,44 entre as chaves); o corpo
                aplicar(p)                                               # desce, mas o nucleo nao entra no chao
                e_ = max((PB[("Antebraco" if k.startswith("Mao") else "Canela") + k[-1]].tail - ALVO[k].location).length for k in PES)
                if e_ < 0.008: break
                ev_ = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
                folga_ = min(min(ev_[i].co.z for i in V_NUCLEO) - 0.02, min(ev_[i].co.z for k in ("MaoE", "MaoD") for i in MEMBRO[k]) + 0.10)
                if folga_ <= 0.005: break
                p["raiz"][2] -= min(0.8 * e_, folga_)
        aplicar(p)
        pose = {pb.name: arm.convert_space(pose_bone=pb, matrix=pb.matrix, from_space="POSE", to_space="LOCAL").copy() for pb in PB}
        for k in PES:
            lado = k[-1]; ant = "Antebraco" + lado if k.startswith("Mao") else "Canela" + lado
            e_ = (PB[ant].tail - ALVO[k].location).length; erro_ik = max(erro_ik, e_); erro_pe[k] = max(erro_pe[k], e_)
            dedo_min = min(dedo_min, PB[DEDO[k]].tail.z)
        perto = min(perto, (PB["MaoE"].tail - PB["MetatarsoE"].tail).length, (PB["MaoD"].tail - PB["MetatarsoD"].tail).length,
                    abs(PB["MaoE"].tail.x - PB["MaoD"].tail.x), abs(PB["MetatarsoE"].tail.x - PB["MetatarsoD"].tail.x))
        if nome in APOIO and prev is not None:                       # pe apoiado: a almofada recua a +v (o lobo avanca para -Y)
            M_ = APOIO[nome]
            for k in PES:
                u = ((t / M_["T"]) - M_["fases"][k]) % 1.0; up = (((t - 1 / FPS) / M_["T"]) - M_["fases"][k]) % 1.0
                if u < M_["apoio"] and up < M_["apoio"] and up < u:
                    vy = (PB[k].tail.y - prev[k]) * FPS; desliza = max(desliza, abs(vy - vel_))
        prev = {k: PB[k].tail.y for k in PES}
        if qi % 3 == 0:
            al = alinhamento()
            for k_, v_ in al.items():
                a_ = alin.setdefault(k_, [9e9, -9e9, 0.0, 0]); a_[0] = min(a_[0], v_); a_[1] = max(a_[1], v_); a_[2] += v_; a_[3] += 1
            zm, onde = malha_zmin()
            if zm < malha_min[0]: malha_min = (zm, onde)
        quadros.append(pose)
    QUADROS[nome] = quadros
    manifesto[nome] = {"duracao_s": round(dur, 3), "loop": loop, "quadros": nq, "velocidade_studs_s": round(vel_, 2),
                       "marcadores": marc, "rotacao_raiz_graus": ROT_RAIZ.get(nome, 0.0),
                       "erro_ik_max": round(erro_ik, 4), "desliza_pe_max_studs_s": round(desliza, 3), "dedo_min_z": round(dedo_min, 3),
                       "malha_min_z_fora_das_patas": round(malha_min[0], 3), "onde": tuple(round(c, 2) for c in malha_min[1]) if malha_min[1] else None,
                       "patas_dist_min": round(perto, 3), "erro_ik_por_pe": {k: round(v, 3) for k, v in erro_pe.items()},
                       "alinhamento": {k: {"min": round(a[0], 3), "max": round(a[1], 3), "media": round(a[2] / a[3], 3)} for k, a in alin.items()}}
    print("CLIPE", nome, json.dumps(manifesto[nome], ensure_ascii=False), flush=True)
    dado = {"nome": "LoboAncestral_" + nome, "fps": FPS, "loop": loop, "quadros": nq, "duracao": dur, "velocidade": round(vel_, 3),
            "marcadores": [{"nome": k, "t": v} for k, v in marc.items()], "rotacao_raiz_graus": ROT_RAIZ.get(nome, 0.0), "ossos": {}}
    for pb in PB:
        if pb.name == "Raiz" and False: continue
        seq = []
        for pose in quadros:
            m = pose[pb.name]; q = m.to_quaternion(); tt = m.translation
            seq += [round(q.x, 5), round(q.y, 5), round(q.z, 5), round(q.w, 5), round(tt.x, 5), round(tt.y, 5), round(tt.z, 5)]
        dado["ossos"][pb.name] = seq
    with open(os.path.join(OUT, "LoboAncestral_%s.json" % nome), "w") as fh: json.dump(dado, fh, separators=(",", ":"))
# acoes FK assadas (restricoes desligadas para tocar a acao); marcadores como pose_markers
for pb in PB:
    for c in pb.constraints: c.mute = True
if not arm.animation_data: arm.animation_data_create()
for nome, quadros in QUADROS.items():
    act = bpy.data.actions.get("Lobo_" + nome)
    if act: bpy.data.actions.remove(act)
    act = bpy.data.actions.new("Lobo_" + nome); act["loop"] = CLIPES[nome][2]; act["velocidade"] = manifesto[nome]["velocidade_studs_s"]
    arm.animation_data.action = act
    for qi, pose in enumerate(quadros):
        for pb in PB:
            m = pose[pb.name]; pb.rotation_quaternion = m.to_quaternion(); pb.location = m.translation
            pb.keyframe_insert("rotation_quaternion", frame=qi + 1); pb.keyframe_insert("location", frame=qi + 1)
    for mk, tm in CLIPES[nome][4].items():
        pm = act.pose_markers.new(mk); pm.frame = int(round(tm * FPS)) + 1
    act.use_fake_user = True
arm.animation_data.action = None; zerar()
for pb in PB:
    for c in pb.constraints: c.mute = False
antigo = {}
caminho_m = os.path.join(OUT, "manifesto_clipes.json")
if os.path.exists(caminho_m): antigo = json.load(open(caminho_m, encoding="utf-8"))
antigo.update(manifesto)
json.dump(antigo, open(caminho_m, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.dirname(bpy.data.filepath), "Lobo_Ancestral_Anim.blend"))
print("ANIM_OK", list(QUADROS))
