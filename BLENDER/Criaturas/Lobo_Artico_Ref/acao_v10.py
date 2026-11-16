"""v10: a MESMA acao tecnica da v9 (quadros 0-806 identicos: gerada pelo mesmo codigo) + trecho H (806-890): combinacoes
moderadas de cauda com a pata traseira ESQUERDA, para testar a separacao cauda x pata da v10 (rodar tambem numa copia da
v9 para comparar antes/depois com amplitudes iguais).
Acao TECNICA de validacao do rig piloto v9 ('Teste_Piloto', 30 qps). NAO e biblioteca de clipes: cada trecho testa
uma parte, separada ou em combinacao controlada. Amplitudes = PARAMETROS TECNICOS DO PILOTO (nao regras oficiais).
Giros definidos em eixos GLOBAIS do repouso (X lateral, Y comprimento, Z vertical) e convertidos para o espaco local de
cada osso (q = B^-1 R B); palpebras giram no X local (= eixo de fechamento da v8) pelo angulo de fechar_*_graus.
Trechos com o tronco mexendo (coluna, inclinacao, transferencia de peso): as 4 patas ficam PLANTADAS por IK analitico
de 2 ossos (Umero+Antebraco ate o carpo / Coxa+Tibia ate o jarrete, joelho no plano de dobra do repouso) e o
Metacarpo/Metatarso volta a orientacao de repouso; tudo e gravado como giros FK em todos os quadros (sem restricoes).
Uso: blender -b <rig.blend> -P acao_v10.py   (grava acao_v10.json ao lado do .blend)"""
import bpy, os, json, math
from mathutils import Vector as V, Matrix, Quaternion
sc = bpy.context.scene; SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
ARM = bpy.data.objects["LoboArtico_Rig"]; P = ARM.pose.bones; B = ARM.data.bones
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def canal(keys):
    def f(q):
        if q <= keys[0][0]: return keys[0][1]
        for (f0, v0), (f1, v1) in zip(keys, keys[1:]):
            if f0 <= q <= f1: return v0 + (v1 - v0) * suave((q - f0) / max(f1 - f0, 1e-9))
        return keys[-1][1]
    return f
X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
# (osso, eixo global, fracao, canal) ; canal em graus
TR = {}                                                                  # trechos (nome: (inicio, fim)) para registro/pranchas
CH = []
def ch(ossos, eixo, keys, nome=None):
    c = canal(keys)
    for o, fr in ossos: CH.append((o, eixo, fr, c))
# A) mandibula: fechada -> meio (15) -> maxima prevista (32, a mesma dos testes v7/v8) -> fechada
JAW = [(0, 0), (10, 0), (22, 15), (28, 15), (40, 32), (46, 32), (58, 0)]; TR["A_mandibula"] = (0, 58)
# B) piscar completo nos dois olhos (meio e total)
PISCA = canal([(58, 0), (63, 0.5), (66, 0.5), (70, 1.0), (74, 1.0), (82, 0)]); TR["B_piscar"] = (58, 82)
# C) cabeca olhando: esquerda/direita 35 graus (pescoco 30% + 30% + cabeca 40%), cima 25 (como os lados) e baixo 18 (mais na base do
#    pescoco: 45% + 35% + cabeca 20%, para nao dobrar a garganta contra o peito)
CAB = [("Pescoco1", 0.3), ("Pescoco2", 0.3), ("Cabeca", 0.4)]; CABP = [("Pescoco1", 0.45), ("Pescoco2", 0.35), ("Cabeca", 0.2)]
ch(CAB, Z, [(82, 0), (96, 35), (102, 35), (116, -35), (122, -35), (134, 0)]); ch(CAB, X, [(134, 0), (146, -25), (152, -25), (158, 0)]); ch(CABP, X, [(158, 0), (166, 18), (172, 18), (184, 0)])
TR["C_cabeca"] = (82, 184)
# D) coluna curvando (12 graus no total, patas plantadas), inclinacao do tronco (8) e transferencia de peso (0,18 lateral; 0,20 frente/tras)
COL = [("Coluna1", 0.25), ("Coluna2", 0.35), ("Coluna3", 0.4)]
ch(COL, Z, [(184, 0), (198, 12), (204, 12), (218, -12), (224, -12), (236, 0)]); TR["D1_coluna"] = (184, 236)
ch([("Quadril", 1.0)], Y, [(236, 0), (248, 8), (254, 8), (266, -8), (272, -8), (282, 0)]); TR["D2_inclinacao"] = (236, 282)
DX = canal([(282, 0), (292, 0.18), (298, 0.18), (310, -0.18), (316, -0.18), (326, 0)])
DY = canal([(326, 0), (336, -0.20), (342, -0.20), (352, 0.20), (358, 0.20), (366, 0)]); TR["D3_peso"] = (282, 366)
TRONCO = (184, 366)
# E) cada membro: ombro/quadril p/ frente e p/ tras, passo (cotovelo/joelho + carpo/jarrete), dedos com a pata no ar
def membro(t0, sup, meio, baixo, dedos, passo, esc=None):
    """passo = (ombro/quadril, cotovelo/joelho, carpo/jarrete) no passo com a pata no ar"""
    ch([(sup, 1.0)], X, [(t0, 0), (t0 + 10, -18), (t0 + 14, -18), (t0 + 24, 15), (t0 + 28, 15), (t0 + 34, passo[0]), (t0 + 50, passo[0]), (t0 + 58, 0)])
    ch([(meio, 1.0)], X, [(t0 + 28, 0), (t0 + 38, passo[1]), (t0 + 50, passo[1]), (t0 + 58, 0)])
    ch([(baixo, 1.0)], X, [(t0 + 28, 0), (t0 + 38, passo[2]), (t0 + 50, passo[2]), (t0 + 58, 0)])
    ch([(dedos, 1.0)], X, [(t0 + 38, 0), (t0 + 42, -20), (t0 + 45, 25), (t0 + 50, 0)])
    if esc: ch([(esc, 1.0)], X, [(t0, 0), (t0 + 10, -6), (t0 + 14, -6), (t0 + 24, 4), (t0 + 28, 4), (t0 + 34, 0)])
for i, (lado, fr) in enumerate((("E", True), ("D", True), ("E", False), ("D", False))):
    t0 = 366 + i * 60
    if fr: membro(t0, "Umero_" + lado, "Antebraco_" + lado, "Metacarpo_" + lado, "Dedos_" + lado, (-18, 45, 95), "Escapula_" + lado); TR["E_dianteira_" + lado] = (t0, t0 + 60)
    else: membro(t0, "Coxa_" + lado, "Tibia_" + lado, "Metatarso_" + lado, "DedosPe_" + lado, (-10, 50, -65)); TR["E_traseira_" + lado] = (t0, t0 + 60)
# F) cauda (lados 35, cima 30, baixo 10) e orelhas (tras 35, frente 15, giro 25)
CAU = [("Cauda1", 0.15), ("Cauda2", 0.25), ("Cauda3", 0.3), ("Cauda4", 0.3)]
ch(CAU, Z, [(606, 0), (618, 35), (624, 35), (636, -35), (642, -35), (652, 0)]); ch(CAU, X, [(652, 0), (662, 30), (668, 30), (676, -10), (680, -10), (688, 0)])
TR["F_cauda"] = (606, 688)
ORE = [("Orelha_E", 1.0), ("Orelha_D", 1.0)]
ch(ORE, X, [(688, 0), (696, -35), (702, -35), (710, 15), (714, 15), (722, 0)])
ch([("Orelha_E", 1.0)], Z, [(722, 0), (730, 25), (734, 25), (740, 0)]); ch([("Orelha_D", 1.0)], Z, [(740, 0), (748, -25), (752, -25), (758, 0)])
TR["F_orelhas"] = (688, 758)
# G) combinacao: cabeca virada (30) + pescoco flexionado p/ baixo (15) + boca maxima (32)
ch(CAB, Z, [(758, 0), (774, 30), (790, 30), (806, 0)]); ch(CABP, X, [(758, 0), (774, 15), (790, 15), (806, 0)])
JAW += [(758, 0), (774, 32), (790, 32), (806, 0)]; TR["G_combinacao"] = (758, 806)
# H) combinacoes moderadas cauda + pata traseira E (70% das amplitudes dos trechos isolados):
#    cauda E 25 + passo E (-7/35/-45); cauda cima 20 + quadril E tras 12; cauda D 25 + quadril E frente 13
ch(CAU, Z, [(806, 0), (818, 25), (832, 25), (838, 0), (850, 0), (864, -25), (878, -25), (890, 0)])
ch(CAU, X, [(832, 0), (838, 20), (850, 20), (858, 0)])
ch([("Coxa_E", 1.0)], X, [(806, 0), (818, -7), (832, -7), (838, 12), (850, 12), (864, -13), (878, -13), (890, 0)])
ch([("Tibia_E", 1.0)], X, [(806, 0), (818, 35), (832, 35), (838, 0)])
ch([("Metatarso_E", 1.0)], X, [(806, 0), (818, -45), (832, -45), (838, 0)])
TR["H_cauda_pata_E"] = (806, 890)
JAWC = canal(JAW); FIM = 890

REST = {pb.name: B[pb.name].matrix_local.copy() for pb in P}
def q_global(nome, R):
    Bm = REST[nome].to_3x3(); return (Bm.inverted() @ R @ Bm).to_quaternion()
PATAS = [("Umero_E", "Antebraco_E", "Metacarpo_E"), ("Umero_D", "Antebraco_D", "Metacarpo_D"),
         ("Coxa_E", "Tibia_E", "Metatarso_E"), ("Coxa_D", "Tibia_D", "Metatarso_D")]
def ik(sup, inf, pe):
    """2 ossos ate a cabeca de repouso do 'pe' (carpo/jarrete); joelho no plano de dobra do repouso levado pelo pai."""
    bs, bi = B[sup], B[inf]; a, b = bs.length, bi.length; T = bi.tail_local.copy()
    S = P[sup].head.copy()                                              # ombro/quadril ja posado
    Mpai = P[sup].parent.matrix @ B[sup].parent.matrix_local.inverted()  # movimento do pai (espaco do armature)
    K0 = bs.tail_local; S0 = bs.head_local; d0 = (T - S0).normalized()
    dob = (K0 - S0) - d0 * (K0 - S0).dot(d0); dob = (Mpai.to_3x3() @ dob)
    dv = T - S; d = min(dv.length, (a + b) * 0.999); dn = dv.normalized()
    al = (a * a - b * b + d * d) / (2 * d); h = math.sqrt(max(a * a - al * al, 0.0))
    perp = (dob - dn * dob.dot(dn)).normalized(); K = S + dn * al + perp * h
    for nome, h0, t0 in ((sup, S, K), (inf, K, S + dn * d)):
        yv = (t0 - h0).normalized(); xr = (Mpai.to_3x3() @ REST[nome].col[0].to_3d()); xv = (xr - yv * xr.dot(yv)).normalized()
        M = Matrix((xv, yv, xv.cross(yv))).transposed().to_4x4(); M.translation = h0
        P[nome].matrix = M; bpy.context.view_layer.update()
    M = REST[pe].copy(); M.translation = P[inf].tail.copy(); P[pe].matrix = M; bpy.context.view_layer.update()
if ARM.animation_data: ARM.animation_data_clear()                       # calcula SEM acao (a avaliacao da acao sobrescreveria a pose)
for pb in P: pb.rotation_mode = "QUATERNION"
sc.render.fps = 30; sc.frame_start = 0; sc.frame_end = FIM; VAL = []
for q in range(FIM + 1):
    for pb in P: pb.matrix_basis.identity()
    acum = {}
    for nome, eixo, fr, c in CH:
        ang = c(q) * fr
        if abs(ang) > 1e-6: acum[nome] = Matrix.Rotation(math.radians(ang), 3, eixo) @ acum.get(nome, Matrix.Identity(3))
    j = JAWC(q)
    if abs(j) > 1e-6: acum["Mandibula"] = Matrix.Rotation(math.radians(j), 3, X)
    for nome, R in acum.items(): P[nome].rotation_quaternion = q_global(nome, R)
    for lado, ol in PIV["olhos"].items():
        for k, ang in (("Sup", ol["fechar_sup_graus"]), ("Inf", ol["fechar_inf_graus"])):
            P["Palpebra_%s_%s" % (k, lado)].rotation_quaternion = Quaternion(X, math.radians(ang * PISCA(q)))
    P["Quadril"].location = REST["Quadril"].to_3x3().inverted() @ V((DX(q), DY(q), -0.25 * (abs(DX(q)) + abs(DY(q)))))
    bpy.context.view_layer.update()
    if TRONCO[0] < q < TRONCO[1]:
        for cad in PATAS: ik(*cad)
        for cad in PATAS:
            for nome in cad: P[nome].location = (0, 0, 0)
    VAL.append({pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P})
for pb in P: pb.matrix_basis.identity()
for a_ in [a_ for a_ in bpy.data.actions if a_.name.startswith("Teste_Piloto")]: bpy.data.actions.remove(a_)
ac = bpy.data.actions.new("Teste_Piloto"); ARM.animation_data_create(); ARM.animation_data.action = ac
for q, vals in enumerate(VAL):                                          # grava sem atualizar a cena entre as chaves
    for pb in P:
        pb.rotation_quaternion, pb.location = vals[pb.name]
        pb.keyframe_insert("rotation_quaternion", frame=q, group=pb.name)
        if pb.name == "Quadril": pb.keyframe_insert("location", frame=q, group=pb.name)
for m in list(sc.timeline_markers): sc.timeline_markers.remove(m)
for nome, (i, f) in TR.items(): sc.timeline_markers.new(nome, frame=i)
ac.use_fake_user = True
json.dump({"acao": "Teste_Piloto", "qps": 30, "quadros": [0, FIM], "trechos": TR,
           "limites_piloto_graus": {"mandibula": 32, "palpebras": "fechar_sup/inf de rig_pivos (100%)", "cabeca_lados": 35, "cabeca_cima": 25, "cabeca_baixo": 18,
                                    "coluna_lados_total": 12, "inclinacao_tronco": 8, "peso_lateral_studs": 0.18, "peso_frente_tras_studs": 0.20,
                                    "ombro_quadril_frente_tras": [-18, 15], "passo_dianteira_ombro_cotovelo_carpo": [-18, 45, 95], "passo_traseira_quadril_joelho_jarrete": [-10, 50, -65], "dedos": [-20, 25],
                                    "cauda_lados_total": 35, "cauda_cima_baixo": [30, -10], "orelhas_tras_frente_giro": [-35, 15, 25],
                                    "combinacao": {"cabeca_lado": 30, "pescoco_baixo": 15, "mandibula": 32},
                                    "H_cauda_pata_E": {"cauda_lados": 25, "cauda_cima": 20, "passo_quadril_joelho_jarrete": [-7, 35, -45], "quadril_tras_frente": [12, -13]}},
           "nota": "parametros tecnicos do piloto, nao regras oficiais"}, open(os.path.join(SRC, "acao_v10.json"), "w"), indent=1)
bpy.ops.wm.save_mainfile(); print("ACAO_V9_OK", FIM, flush=True)
