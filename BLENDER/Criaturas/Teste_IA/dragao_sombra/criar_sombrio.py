"""SB_Dragao (DRAGAO SOMBRIO, forma regional de Sombra) v1 -- 02/11, referencia dragao_sombra/ref/ref_sombrio.png.
Derivado do gerador do Glacial r9 com as MESMAS articulacoes (rig de 100 ossos do Silverwing, clipes e montaria valem),
mas com identidade propria: corpo massivo e musculoso (peito largo, ombros e coxas pesados), pescoco grosso e arqueado,
cabeca maior e angular, DOIS chifres grandes em crescente (para tras e com a ponta para cima), leque de espinhos atras
do cranio e na mandibula, quatro dedos com garras longas por pata, serra de espinhos do dorso a cauda (ponta lisa,
sem leque), asas de morcego com garra grande no punho, escamas preto-violeta com reflexo violeta, placas ventrais
roxo-acinzentadas, membranas preto-purpura translucidas e olhos ambar. Sem poderes (elemento Sombra pendente).
Uso: blender -b --factory-startup -P criar_sombrio.py -- <saida_dir> [sem_render]
--- texto do gerador de origem (Glacial r9) ---
GL_Dragao (Dragao Glacial) R9 (01/11, "corpo unico, nao pecas encaixadas"): juncoes perna-tronco (ombros e quadris)
e pescoco-peito preenchidas e fundidas (vinco concavo preenchido por suavizacao com preservacao de volume + ponte
muscular), quadril mais largo para a coxa nascer do tronco, transicoes de escama/cor suaves. Juntas iguais. --- r8 ---
SB_Dragao (Dragao Glacial) R8 (01/11, refinamento completo): BOCA como bolsa continua (labios com espessura ->
gengiva -> ceu da boca/assoalho -> garganta, um so pedaco de pele que estica ao abrir; sem paineis colados), lingua
nova, peso da garganta, espinhos superiores do cranio, garras maiores. Corpo, juntas e rig iguais ao r7. --- r7 ---
SB_Dragao (Dragao Glacial) R7 (01/11, "engrosse mais todas as partes menos as pernas, junte-as e deixe natural; o
pescoco esta separado do corpo"): pescoco engrossando de forma CONTINUA da nuca ate o peito (no r6 a base do pescoco
ficava fina e o peito em bola = degrau/colar), tronco e cauda mais grossos, juncao pescoco-peito-ombros suavizada.
Pernas e cabeca iguais ao r6; juntas iguais. --- r6 ---
SB_Dragao (Dragao Glacial) R6 (01/11, "um pouco mais, principalmente entre as asas"): r5 com o corpo todo um pouco
mais grosso (x1,18) e o TRONCO ENTRE AS ASAS bem mais cheio (peito/ombros/alto do dorso), sem mudar juntas. --- r5 ---
SB_Dragao (Dragao Glacial) R5 (01/11, pedido "estrutura corporal mais grossa"): r4 com pescoco, tronco, cauda e
patas ~13% mais grossos e ombros/quadris um pouco mais cheios, sem voltar ao "frango" do r3 (coxa sem bola, barriga
recolhida). Mesmas juntas e mesma cabeca. --- r4 ---
SB_Dragao (Dragao Glacial) R4 (01/11): silhueta esguia -- tronco, peito, barriga e coxas afinados (sem "frango"),
encaixe pescoco -> torax mais longo e fino, cabeca mais estreita e afiada, espinhos maiores na nuca/pescoco, patas finas,
asas mais leves (osso e raiz finos, membrana fina e tensa, recortes pontudos). Juntas iguais ao r3 (rig e clipes).
--- r3 ---
SB_Dragao (Dragao Glacial) R3 -- REFINAMENTO ANATOMICO (pedido 01/11, sobre o r2): rosto angular (quinas do focinho
e da mandibula, crista temporal, maca, placa da palpebra), BOCA REAL (labios separados, cavidade, lingua, grupo de
vertices SB_Mandibula para o rig), chifres com ramos e cristas laterais (assimetria leve), espinhos dorsais em ritmo
maior/menor da nuca a cauda com base esculpida na pele, patas com 3 dedos (falanges com nos) e 3 garras longas.
Mesmas juntas de patas/asas, mesma escala. --- texto do r2 ---
SB_Dragao (Dragao Glacial) CORPO ESGUIO REFINADO (pedido 01/11): mesma base esguia (criar_glacial_esguio.py, e2) com
pescoco em S mais encorpado e nobre, peito com mais presenca, ombros/raiz da asa integrados, rosto afinado (focinho
afilado, olho amendoado e severo, escamas finas na face), coroa de chifres curvos em leque, membrana com recortes mais
fundos, garras longas e curvas, cauda mais encorpada na base e ponta em leque de cristal. Juntas de patas/asas iguais.
--- texto anterior (e2) ---
SB_Dragao (Dragao Glacial) CORPO ESGUIO (pedido do usuario 31/10: outro corpo, mais fiel a referencia): pescoco
longo em S erguido, cabeca pequena com coroa de chifres, tronco estreito e fundo, patas finas, cauda longa em chicote,
azul-po claro. Mantem as juntas que definem a passada e a batida de asa (alturas de ombro/quadril, patas, braco e
dedos da asa) iguais as do CR_Dragao; o pescoco e a cauda mudam de medida (o rig usa os mesmos nomes de ossos).
Base anterior (corpo do CR): criar_glacial_ref.py (v7).
POSE NEUTRA para rig/animacao. Derivado de dragao_novo/criar_dragao_ref.py (CR_Dragao, fogo) com as MESMAS articulacoes
(cabeca, pescoco, ombros, quadril, patas, braco/dedos da asa): o rig do Silverwing e os clipes servem sem refazer.
O que muda (referencia): corpo mais esguio e elegante, pescoco fino, cabeca alongada com coroa de chifres finos
varridos para tras e babado de espinhos na mandibula, espinhos dorsais cristalinos, escamas azul-gelo com bordas
claras, ventre em placas quase brancas, membranas azul-palido translucidas, olhos azul-gelo.
Frente = -Y, pes em Z=0, simetrico em X.
Uso: blender -b --factory-startup -P criar_glacial_ref.py -- <saida_dir> [sem_render]"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, noise

ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; rnd = random.Random(5); V = Vector
def lerp(a, b, t): return a + (b - a) * t
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

# ------------------------------------------------------------------ eixo do corpo (y, z, raio_largura, raio_altura)
# cabeca: os mesmos 7 pontos do CR (raios do glacial), escritos no espaco "canonico" da cabeca; OFF a leva ao alto do
# pescoco novo. Todo o trabalho de rosto (escultura, chifres, dentes, olhos) roda no espaco canonico (malha deslocada
# por -OFF) e depois volta.
OFF = V((0, -0.03, 0.36))
CAB_PTS = [(-0.965, 0.714, 0.018, 0.019), (-0.930, 0.721, 0.031, 0.029), (-0.885, 0.735, 0.041, 0.038), (-0.840, 0.753, 0.049, 0.045),
           (-0.79, 0.773, 0.056, 0.054), (-0.74, 0.781, 0.062, 0.059), (-0.69, 0.757, 0.056, 0.058)]
ESPINHA = [(y + OFF.y, z + OFF.z, rx, ry) for y, z, rx, ry in CAB_PTS] + [
           # refinado: S de cisne (base avanca, meio recua, topo volta a frente sob a cabeca), mais fundo que largo e
           # engrossando ate o peito (sustenta a cabeca; transicao continua pescoco -> peito)
           (-0.625, 1.080, 0.050, 0.057), (-0.578, 1.000, 0.054, 0.063), (-0.582, 0.900, 0.060, 0.071),
           (-0.572, 0.795, 0.068, 0.082), (-0.512, 0.680, 0.086, 0.104),   # r4: encaixe fino                                   # base do pescoco
           (-0.27, 0.514, 0.112, 0.146), (-0.10, 0.500, 0.098, 0.118), (0.05, 0.494, 0.084, 0.092),   # r4: peito fundo mas estreito, cintura         # peito com presenca, cintura fina
           (0.18, 0.478, 0.092, 0.098), (0.30, 0.460, 0.092, 0.092),   # r4                                       # quadril
           (0.46, 0.430, 0.092, 0.086), (0.68, 0.400, 0.075, 0.070), (0.92, 0.364, 0.059, 0.055), (1.18, 0.328, 0.046, 0.043),
           (1.45, 0.296, 0.035, 0.033), (1.72, 0.272, 0.025, 0.024), (2.00, 0.258, 0.016, 0.015), (2.30, 0.256, 0.006, 0.006)]   # cauda: base cheia, afina em chicote
# r7: fator por ponto. Pescoco cresce em rampa da nuca (igual a cabeca, sem "tubo") ate a base, que fica quase da
# espessura do peito -> pescoco nasce do tronco; peito/entre as asas cheios; resto do corpo e cauda x1,26
# SOMBRIO: massa bem maior que o Glacial (referencia musculosa); pescoco grosso desde a nuca, peito largo
ENG = 1.52
FAT = {7: 1.34, 8: 1.55, 9: 1.72, 10: 1.86, 11: 1.98, 12: 1.86, 13: 1.70, 14: 1.58, 15: 1.55, 16: 1.58, 17: 1.66, 18: 1.74,
       19: 1.84, 20: 1.92, 21: 1.98, 22: 2.0, 23: 1.9}   # v2: pescoco grosso ate a nuca; cauda cheia ate o meio
ESPINHA = ESPINHA[:7] + [(y, z, rx * FAT.get(i, ENG), ry * FAT.get(i, ENG)) for i, (y, z, rx, ry) in enumerate(ESPINHA) if i >= 7]
# SOMBRIO v5: tronco com raios EXPLICITOS e graduais (peito fundo -> cintura -> quadril -> base da cauda). Fatores grandes
# sobre os raios do Glacial davam um degrau (o Skin liga nos vizinhos por planos: 'caixa' nas costas)
TRONCO = {12: (0.200, 0.235), 13: (0.180, 0.205), 14: (0.160, 0.180), 15: (0.158, 0.170), 16: (0.160, 0.160), 17: (0.145, 0.140),
          18: (0.126, 0.120), 19: (0.106, 0.100), 20: (0.087, 0.082), 21: (0.068, 0.064), 22: (0.049, 0.046), 23: (0.030, 0.028), 24: (0.010, 0.010)}
ESPINHA = [(y, z) + TRONCO[i] if i in TRONCO else (y, z, rx, ry) for i, (y, z, rx, ry) in enumerate(ESPINHA)]
# cauda mais curta e grossa que a do Glacial (referencia): comprimento atras do quadril x0,82 -> ponta em y=1,90
# (o rig_sombrio redistribui os ossos da cauda ate Y_CAUDA)
Y_CAUDA = 0.30 + (2.30 - 0.30) * 0.82
ESPINHA = [((0.30 + (y - 0.30) * 0.82) if (i >= 16 and y > 0.30) else y, z, rx, ry) for i, (y, z, rx, ry) in enumerate(ESPINHA)]
I_FOC, I_SOBR, I_CRAN, I_NUCA, I_PEITO, I_MEIO, I_QUAD = 1, 4, 5, 6, 12, 13, 16
def O(p): return V(p) + OFF
# (mandibula com os raios do CR: mais fina que o cranio fazia o Skin falhar e o remesh perdia pescoco/tronco)
MANDIBULA = [(O((0, -0.76, 0.720)), 0.058, 0.037), (O((0, -0.82, 0.702)), 0.049, 0.028), (O((0, -0.88, 0.692)), 0.036, 0.020),
             (O((0, -0.932, 0.691)), 0.022, 0.013)]

def perna(s, dianteira):
    F = (1.18, 1.16, 1.12, 1.02, 1.02, 1.04) if dianteira else (0.96, 1.04, 1.10, 1.00, 1.00, 1.04)   # SOMBRIO: patas fortes (v2: coxa sem balao)   # r6   # r5: patas mais grossas   # r4: coxa sem 'coxinha'
    # esguio: musculo em cima, canela fina (referencia)
    return [(p, rx * f, ry * f) for (p, rx, ry), f in zip(_perna(s, dianteira), F)]
def _perna(s, dianteira):
    """articulacoes com angulo real (cotovelo para tras, joelho para frente, jarrete para tras): o rig dobra
    sempre para o lado certo e a silhueta deixa de ser coluna; musculo grosso em cima, canela fina embaixo"""
    if dianteira:
        return [(V((0.105 * s, -0.31, 0.470)), 0.135, 0.145), (V((0.140 * s, -0.27, 0.360)), 0.115, 0.110),
                (V((0.150 * s, -0.20, 0.265)), 0.078, 0.076), (V((0.152 * s, -0.235, 0.170)), 0.066, 0.062),
                (V((0.150 * s, -0.275, 0.075)), 0.050, 0.046), (V((0.152 * s, -0.300, 0.036)), 0.060, 0.032)]
    return [(V((0.115 * s, 0.22, 0.445)), 0.168, 0.168), (V((0.155 * s, 0.15, 0.340)), 0.150, 0.140),
            (V((0.165 * s, 0.07, 0.250)), 0.095, 0.090), (V((0.165 * s, 0.17, 0.150)), 0.066, 0.060),
            (V((0.162 * s, 0.245, 0.060)), 0.046, 0.040), (V((0.162 * s, 0.200, 0.030)), 0.060, 0.030)]

def dedos_pe(s, dianteira):
    base = perna(s, dianteira)[-1][0]
    # R3: TRES dedos principais bem separados (leque de ~50 graus, o do meio mais longo), cada um com falanges: o raio
    # engrossa em cada no e afina entre eles -> dedo com volume e articulacao, nao uma massa unica
    res = []
    for ang, k in ((-0.62, 0.84), (-0.21, 1.0), (0.21, 1.0), (0.62, 0.84)):   # SOMBRIO: 4 dedos
        d = V((math.sin(ang) * s, -math.cos(ang), 0.0)); o0 = base + V((math.sin(ang) * 0.018 * s, -0.008, 0.0))
        def P(L, dz): return o0 + d * (L * k) + V((0, 0, dz))
        res.append([(P(0.040, -0.008), 0.021, 0.017), (P(0.060, -0.012), 0.015, 0.012), (P(0.080, -0.015), 0.017, 0.013),
                    (P(0.098, -0.017), 0.012, 0.010), (P(0.116, -0.018), 0.013, 0.010)])   # SOMBRIO: dedos grossos   # r4: dedos longos e finos
    return res

def asa(s):
    """pose neutra: abertas, erguidas ~12 graus, levemente varridas para tras # inferido (conceito tem asas erguidas)"""
    raiz, cot, pul = V((0.085 * s, -0.31, 0.60)), V((0.50 * s, -0.18, 0.78)), V((1.00 * s, -0.38, 0.90))
    dedos = [[V((1.50 * s, -0.53, 0.95)), V((1.92 * s, -0.45, 0.95)), V((2.20 * s, -0.28, 0.93))],
             [V((1.47 * s, -0.20, 0.89)), V((1.84 * s, 0.01, 0.85)), V((2.09 * s, 0.20, 0.81))],
             [V((1.34 * s, 0.05, 0.83)), V((1.57 * s, 0.36, 0.77)), V((1.71 * s, 0.67, 0.71))],
             [V((1.11 * s, 0.12, 0.79)), V((1.15 * s, 0.47, 0.71)), V((1.13 * s, 0.82, 0.64))]]
    return raiz, cot, pul, dedos

# ------------------------------------------------------------------ corpo (grafo Skin)
me = bpy.data.meshes.new("SB_Dragao_Corpo"); ob = bpy.data.objects.new("SB_Dragao_Corpo", me); sc.collection.objects.link(ob)
bm = bmesh.new(); raios = []
def vert(p, rx, ry): v = bm.verts.new(p); raios.append((rx, ry)); return v
def cadeia(pts, inicio=None):
    vs = [vert(p, rx, ry) for p, rx, ry in pts]
    if inicio is not None: bm.edges.new((inicio, vs[0]))
    for a, b in zip(vs, vs[1:]): bm.edges.new((a, b))
    return vs
esp = cadeia([(V((0, y, z)), rx, ry) for y, z, rx, ry in ESPINHA])
cadeia(MANDIBULA, esp[I_CRAN])
for s in (1, -1):
    for dian, ini in ((True, esp[I_PEITO]), (False, esp[I_QUAD])):
        pv = cadeia(perna(s, dian), ini)
        for d in dedos_pe(s, dian): cadeia(d, pv[-1])
    cadeia([(O((0.044 * s, -0.800, 0.802)), 0.025, 0.018), (O((0.053 * s, -0.836, 0.789)), 0.014, 0.011)], esp[I_SOBR])   # sobrancelha
    cadeia([(O((0.058 * s, -0.750, 0.742)), 0.031, 0.026), (O((0.052 * s, -0.800, 0.733)), 0.017, 0.014)], esp[I_CRAN])   # maca
    cadeia([(O((0.018 * s, -0.945, 0.733)), 0.013, 0.012)], esp[I_FOC])                                                   # narina
    raiz, cot, pul, dedos = asa(s)
    # glacial (refino 31/10): braco da asa mais fino e aerodinamico, punho marcado (mesmos pontos de articulacao)
    braco = cadeia([(raiz, 0.060, 0.054), (lerp(raiz, cot, 0.5), 0.038, 0.035), (cot, 0.034, 0.030),
                    (lerp(cot, pul, 0.5), 0.025, 0.022), (pul, 0.031, 0.027)], esp[I_PEITO])   # SOMBRIO: braco forte
    for d in dedos:
        cadeia([(lerp(pul, d[0], 0.5), 0.020, 0.017), (d[0], 0.017, 0.014), (d[1], 0.012, 0.010), (d[2], 0.005, 0.005)], braco[-1])
    cadeia([(pul + V((0.02 * s, -0.045, 0.012)), 0.012, 0.011), (pul + V((0.03 * s, -0.085, 0.008)), 0.005, 0.005)], braco[-1])
bm.to_mesh(me); bm.free()
sk = ob.modifiers.new("Pele", "SKIN"); sk.branch_smoothing = 0.6   # (1,0 quebra o casco do Skin no corpo grosso)
sk.use_smooth_shade = True
for i, d in enumerate(me.skin_vertices[0].data): d.radius = raios[i]; d.use_root = (i == I_MEIO)
sub = ob.modifiers.new("Sub", "SUBSURF"); sub.levels = sub.render_levels = 2
bpy.context.view_layer.objects.active = ob; ob.select_set(True)
for m in list(ob.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)

# massas musculares (conceito: peito largo, ombros e coxas fortes, barriga funda)
for v in ob.data.vertices:
    p = v.co; x, y, z = p
    k = math.exp(-((y + 0.28) / 0.11) ** 2) * math.exp(-((z - 0.50) / 0.13) ** 2); p.x *= 1 + 0.20 * k      # SOMBRIO: ombros pesados; ombros (r6: entre as asas mais largo)
    k = math.exp(-((y + 0.20) / 0.16) ** 2) * suave((z - 0.50) / 0.06)
    if abs(x) < 0.16: p.z += 0.0 * k   # SOMBRIO v5: sem elevacao do dorso (no corpo grosso virava platô com paredes retas, a 'caixa' nas costas)     # r6: alto do dorso entre as asas mais cheio
    k = math.exp(-((y - 0.20) / 0.11) ** 2) * math.exp(-((z - 0.42) / 0.11) ** 2); p.x *= 1 + 0.10 * k      # SOMBRIO: quadris/coxas (v2: menos balao); quadris (r9: a coxa nasce do tronco)
    if -0.30 < y < 0.20 and z < 0.44: p.z -= 0.030 * math.exp(-((y + 0.05) / 0.17) ** 2) * suave((0.42 - z) / 0.08)
    if -0.44 < y < -0.16 and z < 0.64 and abs(x) < 0.14:                                                    # peito projetado (quilha)
        p.y -= 0.024 * suave((0.64 - z) / 0.16) * (1 - abs(x) / 0.14) ** 1.5 * suave((z - 0.36) / 0.08)      # r2: sobe ate a base do pescoco
    # raiz da asa: massa do ombro sobe ate o braco da asa (a asa nasce do corpo, nao fica espetada nele)
    for s_ in (1, -1):
        d = (V((x, y, z)) - V((0.085 * s_, -0.31, 0.585))).length
        if d < 0.16 and x * s_ > 0.03: p.z += 0.012 * math.exp(-(d / 0.06) ** 2); p.x += s_ * 0.006 * math.exp(-(d / 0.06) ** 2)   # r4: raiz limpa   # r2: raiz mais cheia
# r2: pescoco menos cilindrico -- secao oval (laterais um pouco achatadas), crista dorsal baixa, quilha ventral e
# feixe muscular lateral que desce da nuca a frente do peito (liga pescoco -> torax)
PESC = [(y, z) for y, z, _, _ in ESPINHA[7:13]]                      # (y, z) do eixo do pescoco, de cima para baixo
def centro_pesc(z):
    for (ya, za), (yb, zb) in zip(PESC, PESC[1:]):
        if zb <= z <= za: return lerp(ya, yb, (za - z) / (za - zb))
    return None
for v in ob.data.vertices:
    p, nrm = v.co, v.normal; x, y, z = p
    if not (0.64 < z < 1.07) or y > -0.40: continue
    cy = centro_pesc(z)
    if cy is None: continue
    w = suave((z - 0.64) / 0.06) * suave((1.07 - z) / 0.05)
    p.x *= 1 - 0.07 * w * suave((abs(x) - 0.01) / 0.03)
    if y > cy and abs(x) < 0.022: p.y += 0.006 * w * (1 - abs(x) / 0.022) ** 1.5                     # crista dorsal
    if y < cy and abs(x) < 0.030: p.y -= 0.004 * w * (1 - abs(x) / 0.030)                            # quilha ventral
    if abs(nrm.x) > 0.4:                                                                             # feixe lateral
        yl = lerp(cy + 0.03, cy - 0.05, suave((1.05 - z) / 0.40))
        p += nrm * 0.0055 * w * math.exp(-((y - yl) / 0.028) ** 2)
ob.data.update()
# r9: CORPO UNICO -- volumes de ligacao (elipsoides) nas juncoes perna-tronco (ombros e quadris) e pescoco-peito,
# unidos ao corpo pelo remesh voxel: o vinco vira massa continua (como escultura), sem cortes. Ficam DENTRO da silhueta
# das juntas (nao mudam articulacoes nem passadas); o calor do rig pesa essa massa entre perna e tronco (pele que
# estica, nao peca que gira).
bmj = bmesh.new(); bmj.from_mesh(ob.data)
LIGACOES = [((0.0, -0.45, 0.60), (0.125, 0.110, 0.13), 0.0)]                       # peito sob a base do pescoco
for s_ in (1, -1):
    LIGACOES += [((0.112 * s_, -0.295, 0.425), (0.110, 0.135, 0.120), 0.0),          # ombro / axila: envolve o alto da pata
                 ((0.122 * s_, 0.205, 0.400), (0.115, 0.150, 0.120), 0.0)]            # quadril / virilha
for c, r, _ in LIGACOES:
    g = bmesh.ops.create_uvsphere(bmj, u_segments=24, v_segments=14, radius=1.0)
    for v in g["verts"]: v.co = V((c[0] + v.co.x * r[0], c[1] + v.co.y * r[1], c[2] + v.co.z * r[2]))
bmj.to_mesh(ob.data); bmj.free(); ob.data.update()
rm = ob.modifiers.new("Remesh", "REMESH"); rm.mode = "VOXEL"; rm.voxel_size = 0.0048; rm.use_smooth_shade = True
bpy.ops.object.modifier_apply(modifier=rm.name)
sm = ob.modifiers.new("Liso", "SMOOTH"); sm.factor = 0.5; sm.iterations = 4
bpy.ops.object.modifier_apply(modifier=sm.name)
# r7: JUNCAO pescoco -> peito -> ombros suavizada (some o degrau/colar): regioes encaixadas, a interna suaviza mais
bm_ = bmesh.new(); bm_.from_mesh(ob.data)
for ext, it in ((0.00, 10), (0.04, 6), (0.08, 3)):
    sel = [v for v in bm_.verts if -0.66 - ext < v.co.y < -0.20 + ext and 0.50 - ext < v.co.z < 0.92 + ext and abs(v.co.x) < 0.20 + ext]
    for _ in range(it): bmesh.ops.smooth_vert(bm_, verts=sel, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
bm_.to_mesh(ob.data); bm_.free(); ob.data.update()
# r9: suavizacao com DECAIMENTO (sem borda de regiao): posicao suavizada misturada a original por peso gaussiano em
# torno de cada juncao -> o vinco some e nada fica com corte reto
bmz = bmesh.new(); bmz.from_mesh(ob.data); bmz.verts.ensure_lookup_table()
CENT = [(V(c), max(r) * 1.9) for c, r, _ in LIGACOES]
CENT += [(V((0.0, -0.08, 0.66)), 0.20), (V((0.0, 0.14, 0.60)), 0.18)]   # SOMBRIO v5: lombo (arestas do casco do Skin)
peso = {}
for v in bmz.verts:
    w = max(math.exp(-((v.co - c).length / rr) ** 2) for c, rr in CENT)
    if w > 0.02: peso[v.index] = w
orig = {i: bmz.verts[i].co.copy() for i in peso}
sel = [bmz.verts[i] for i in peso]
for _ in range(30): bmesh.ops.smooth_vert(bmz, verts=sel, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
for i, w in peso.items(): bmz.verts[i].co = orig[i].lerp(bmz.verts[i].co, w * 0.85)
bmz.to_mesh(ob.data); bmz.free(); ob.data.update()
# SOMBRIO v5: TRONCO REDONDO. O Skin gera secoes RETANGULARES entre os nos; com os raios grossos do Sombrio o
# Subsurf nao as arredonda (topo plano, laterais retas, quinas: a "caixa" nas costas). Cada vertice da metade de cima
# do tronco e levado ao raio de uma elipse (rx, ry do eixo naquele y); bracos, asas e patas que saem da secao (bem
# alem da elipse) nao sao tocados.
def _tronco_redondo():
    eixo = [(y, z, rx, ry) for y, z, rx, ry in ESPINHA[7:]]
    eixo.sort()
    def no(y):
        for a, b in zip(eixo, eixo[1:]):
            if a[0] <= y <= b[0]:
                t = (y - a[0]) / (b[0] - a[0]); return [lerp(a[k], b[k], t) for k in range(1, 4)]
        return None
    n_ = 0
    for v in ob.data.vertices:
        p = v.co
        if not (-0.36 < p.y < 0.62): continue
        e = no(p.y)
        if e is None: continue
        zc, rx, ry = e
        dz = p.z - zc
        if dz < -0.25 * ry: continue                                   # so a metade de cima (barriga/patas intactas)
        d = V((p.x, dz)); L = d.length
        if L < 1e-6: continue
        c, s_ = d.x / L, d.y / L
        re = 1.0 / math.sqrt((c / rx) ** 2 + (s_ / ry) ** 2)
        lim = 1.30 if (p.y < -0.12 or s_ < 0.12) else 1.9              # atras das asas, acima do eixo nao sai membro (patas saem abaixo)
        if L > re * lim: continue                                      # braco/asa/pata saindo da secao
        w = 0.9 * (1 - suave((L / re - 1.08) / (lim - 1.08))) * suave((p.y + 0.36) / 0.10) * suave((0.62 - p.y) / 0.12)
        w *= suave((dz + 0.25 * ry) / (0.25 * ry))
        if w <= 0: continue
        Ln = lerp(L, re, w); p.x = c * Ln; p.z = zc + s_ * Ln; n_ += 1
    ob.data.update(); print("DRAGAO_TRONCO_REDONDO vertices", n_)
_tronco_redondo()
sm3 = ob.modifiers.new("Liso3", "SMOOTH"); sm3.factor = 0.5; sm3.iterations = 3
bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier=sm3.name)
# SOMBRIO v3: MUSCULATURA. Cada musculo e uma faixa ao longo de um osso da pata (posicao t0 e largura w no osso) que
# empurra a pele pela normal so do lado em que o musculo fica (dir); sulcos entre grupos com altura negativa. As
# articulacoes nao mudam (a pele so sobe/afunda poucos milimetros na escala do master).
def _musculos():
    from mathutils.geometry import intersect_point_line
    bmm = bmesh.new(); bmm.from_mesh(ob.data); bmm.verts.ensure_lookup_table(); bmm.normal_update()
    regras = []
    for s_ in (1, -1):
        fp = [p for p, _, _ in perna(s_, True)]; tp = [p for p, _, _ in perna(s_, False)]
        X = V((s_, 0, 0))
        regras += [   # (a, b, t0, w, direcao do musculo, altura, alcance radial)
            (fp[0], fp[2], 0.42, 0.22, V((0, 1, 0.1)), 0.0075, 0.16),      # triceps (atras do braco)
            (fp[0], fp[2], 0.55, 0.18, V((0, -1, 0)), 0.0050, 0.14),       # biceps (frente)
            (fp[0], fp[2], 0.30, 0.20, X, 0.0045, 0.16),                    # deltoide lateral
            (fp[2], fp[4], 0.28, 0.20, V((0.6 * s_, -0.8, 0)), 0.0050, 0.12),   # extensor do antebraco
            (fp[2], fp[4], 0.30, 0.18, V((-0.3 * s_, 1, 0)), 0.0035, 0.12),     # flexor
            (tp[0], tp[2], 0.50, 0.24, V((0.3 * s_, -1, 0.1)), 0.0080, 0.18),   # quadriceps
            (tp[0], tp[2], 0.42, 0.24, V((0.2 * s_, 1, 0.2)), 0.0070, 0.18),    # posterior da coxa
            (tp[0], tp[2], 0.47, 0.30, X, -0.0030, 0.18),                    # sulco entre os dois (lateral)
            (tp[2], tp[3], 0.40, 0.25, V((0, 1, 0.3)), 0.0060, 0.13),       # panturrilha
        ]
    # peitorais e serratil (tronco)
    for s_ in (1, -1):
        regras += [(V((0.05 * s_, -0.50, 0.50)), V((0.12 * s_, -0.34, 0.42)), 0.45, 0.30, V((0.4 * s_, -1, -0.3)), 0.0070, 0.16),
                   (V((0.10 * s_, -0.20, 0.52)), V((0.11 * s_, 0.05, 0.47)), 0.40, 0.35, V((s_, 0, -0.2)), 0.0035, 0.18)]
    soma = {}
    for a, b, t0, w, dirv, h, alc in regras:
        dirv = dirv.normalized(); ab = b - a
        for v in bmm.verts:
            p = v.co
            if (p - (a + b) * 0.5).length > ab.length * 0.8 + alc: continue
            q, t = intersect_point_line(p, a, b)
            if t < -0.2 or t > 1.2: continue
            rad = p - q
            if rad.length > alc or rad.length < 1e-6: continue
            k = max(0.0, rad.normalized().dot(dirv)) ** 2 if h > 0 else max(0.0, rad.normalized().dot(dirv)) ** 6
            f = h * math.exp(-((t - t0) / w) ** 2) * k
            if f: soma[v.index] = soma.get(v.index, 0.0) + f
    for i, f in soma.items():
        v = bmm.verts[i]; v.co += v.normal * f * 2.4                   # v4: relevo muscular legivel na escala do jogo
    bmm.to_mesh(ob.data); bmm.free(); ob.data.update()
    print("DRAGAO_MUSCULOS vertices", len(soma))
_musculos()
sm2 = ob.modifiers.new("Liso2", "SMOOTH"); sm2.factor = 0.4; sm2.iterations = 2      # funde as bordas dos musculos
bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier=sm2.name)
# corpo inteiro? (Skin com raios incompativeis gera casca aberta e o remesh perde pescoco/tronco sem erro)
for y0 in (-0.6, -0.1, 0.3):
    nv = sum(1 for v in ob.data.vertices if abs(v.co.y - y0) < 0.01 and abs(v.co.x) < 0.25 and v.co.z < 1.3)
    assert nv > 100, "corpo incompleto em y=%.2f (%d vertices): revise os raios do Skin" % (y0, nv)
from mathutils import Matrix
ob.data.transform(Matrix.Translation(-OFF)); ob.data.update()      # -> espaco canonico da cabeca
for v in ob.data.vertices:                                          # cranio largo atras (era no espaco do CR)
    p = v.co; x, y, z = p
    if y < -0.68 and z > 0.67: p.x *= 1 + 0.04 * math.exp(-((y + 0.75) / 0.05) ** 2) * suave((z - 0.70) / 0.05)
    # refinado: focinho afilado (estreita a frente do olho, mais na ponta) e testa -> focinho em linha continua
    if y < -0.83: p.x *= 1 - 0.19 * suave((-0.83 - y) / 0.11)
    if y < -0.70: p.x *= 1 - 0.07 * suave((z - 0.70) / 0.05) * suave((-0.70 - y) / 0.04)        # r4: cranio e bochecha mais estreitos
    if y < -0.80 and z > 0.735 and abs(p.x) < 0.03: p.z += 0.004 * suave((-0.80 - y) / 0.05) * suave((y + 0.97) / 0.04)
    if y < -0.89 and z > 0.722: p.z -= 0.005 * suave((-0.89 - y) / 0.06) * suave((z - 0.722) / 0.02)        # r2: ponta fina e elegante
    if y < -0.86 and z < 0.700: p.z += 0.003 * suave((-0.86 - y) / 0.08) * suave((0.700 - z) / 0.015)        # r2: queixo afinado
ok_, hit, nrm_h, _ = ob.ray_cast(V((0.3, -0.806, 0.775)), V((-1, 0, 0)))
OLHO = hit - nrm_h * 0.0025 if ok_ else V((0.052, -0.815, 0.762))
print("DRAGAO_OLHO", tuple(round(c, 3) for c in OLHO))
for v in ob.data.vertices:                                     # rosto: boca, narinas, orbitas, sobrancelha
    p, nrm = v.co, v.normal; x, y, z = p
    if y < -0.77 and abs(x) > 0.008:
        zb = 0.704 + (y + 0.95) * 0.07
        p -= nrm * 0.005 * math.exp(-((z - zb) / 0.0035) ** 2) * suave((-0.77 - y) / 0.025)
    for s_ in (1, -1):
        d = (p - V((0.018 * s_, -0.958, 0.733))).length
        if d < 0.010: p -= nrm * 0.006 * (1 - d / 0.010) ** 2
        d = (p - V((OLHO.x * s_, OLHO.y, OLHO.z))).length
        if d < 0.02: p -= nrm * 0.008 * (1 - d / 0.02) ** 2
ob.data.update()
# REFINO DO ROSTO (glacial 31/10): orbita mais funda com aro, arcada da sobrancelha saliente (olhar severo), crista
# nasal, narinas em fenda, sulco da maca, linha da mandibula marcada e placas faciais; tudo pequeno (mesmo volume)
for v in ob.data.vertices:
    p, nrm = v.co, v.normal; x, y, z = p
    if y > -0.70: continue
    for s_ in (1, -1):
        olho = V((OLHO.x * s_, OLHO.y, OLHO.z))
        d = (p - olho).length
        if 0.016 < d < 0.032: p += nrm * 0.0035 * math.sin(math.pi * (d - 0.016) / 0.016)        # aro da orbita
        if d < 0.018: p -= nrm * 0.004 * (1 - d / 0.018)                                          # orbita mais funda
        sob = olho + V((0.004 * s_, 0.004, 0.022))                                                # arcada sobre o olho
        e = V(((x - sob.x) / 0.022, (y - sob.y) / 0.034, (z - sob.z) / 0.010))
        if e.length < 1.0: p += nrm * 0.007 * (1 - e.length) ** 1.5
        nar = V((0.020 * s_, -0.950, 0.738))                                                      # narina em fenda
        e = V(((x - nar.x) / 0.008, (y - nar.y) / 0.016, (z - nar.z) / 0.004))
        if e.length < 1.0: p -= nrm * 0.005 * (1 - e.length)
        if -0.90 < y < -0.80 and s_ * x > 0.02:                                                   # sulco da maca
            zs = 0.738 - (y + 0.80) * 0.12
            p -= nrm * 0.0022 * math.exp(-((z - zs) / 0.004) ** 2)
    if abs(x) < 0.016 and y < -0.82 and z > 0.735:                                                # crista nasal
        p += nrm * 0.004 * (1 - abs(x) / 0.016) * suave((-0.82 - y) / 0.04)
    if y < -0.74 and 0.684 < z < 0.700 and abs(x) > 0.015:                                        # borda da mandibula
        p += nrm * 0.0025 * math.exp(-((z - 0.692) / 0.004) ** 2)
ob.data.update()
# REFINO FINAL (31/10, 2o pedido): rosto mais nobre e ameacador so com deslocamentos pequenos na pele (eixo, raios e
# articulacoes iguais): boca com comissura subindo para tras e labio superior encobrindo o maxilar, angulo da mandibula
# e queixo marcados, ponta do focinho em leve gancho, narinas com borda, escamas-escudo na crista nasal, crista
# zigomatica (bochecha) de onde nasce o babado, palpebras, sulco lacrimal e arcada baixa na frente (olhar severo)
def seg_yz(p, a, b):
    """distancia no plano lateral (y,z) ate o segmento a-b e a posicao t ao longo dele"""
    ay, az, by, bz = a[0], a[1], b[0], b[1]; vy, vz = by - ay, bz - az
    t = max(0.0, min(1.0, ((p.y - ay) * vy + (p.z - az) * vz) / (vy * vy + vz * vz)))
    return math.hypot(p.y - (ay + vy * t), p.z - (az + vz * t)), t
OLHO_A = V((abs(OLHO.x), OLHO.y, OLHO.z))
for v in ob.data.vertices:
    p, nrm = v.co, v.normal; x, y, z = p
    if y > -0.66: continue
    ax_ = abs(x); lado = abs(nrm.x) > 0.25                                                          # pele voltada para o lado
    q = V((ax_, y, z))
    if y < -0.745 and ax_ > 0.010 and lado:                                                       # boca
        zb = 0.704 + (y + 0.95) * 0.07 + 0.008 * suave((y + 0.79) / 0.04)                         # comissura sobe no canto
        fade = suave((-0.745 - y) / 0.02)
        p -= nrm * 0.0035 * math.exp(-((z - zb) / 0.0028) ** 2) * fade
        p += nrm * 0.0030 * math.exp(-((z - zb - 0.007) / 0.0045) ** 2) * fade * suave((-0.80 - y) / 0.06)   # labio sup.
        p += nrm * 0.0022 * math.exp(-((z - zb + 0.009) / 0.0045) ** 2) * fade                    # beira do maxilar
    e = V(((ax_ - 0.052) / 0.016, (y + 0.765) / 0.020, (z - 0.700) / 0.014))                      # angulo da mandibula
    if e.length < 1.0: p += nrm * 0.0040 * (1 - e.length) ** 1.5
    if -0.935 < y < -0.84 and z < 0.690 and nrm.z < -0.3:                                        # queixo com massa
        p += nrm * 0.0028 * math.sin(math.pi * (y + 0.935) / 0.095) * (1 - min(1.0, ax_ / 0.03))
    if y < -0.945 and 0.700 < z < 0.722:                                                          # leve gancho na ponta
        p.z -= 0.0030 * suave((-0.945 - y) / 0.02) * math.exp(-((z - 0.711) / 0.008) ** 2)
    nar = V((0.020, -0.950, 0.738))                                                               # borda das narinas
    e = V(((ax_ - nar.x) / 0.008, (y - nar.y) / 0.016, (z - nar.z) / 0.004)).length
    if 0.9 < e < 1.9: p += nrm * 0.0020 * math.sin(math.pi * (e - 0.9))
    if ax_ < 0.014 and -0.93 < y < -0.80 and nrm.z > 0.5:                                         # escudos da crista nasal
        p += nrm * 0.0026 * (1 - ax_ / 0.014) * max(0.0, math.sin(2 * math.pi * (y + 0.93) / 0.032)) ** 2
    if lado:
        d, t = seg_yz(q, (-0.828, 0.734), (-0.708, 0.713))                                         # crista zigomatica
        if ax_ > 0.035:
            p += nrm * 0.0042 * math.exp(-(d / 0.0055) ** 2) * math.sin(math.pi * (0.15 + 0.85 * t))
            d2, _ = seg_yz(q, (-0.828, 0.723), (-0.708, 0.702))                                    # sulco abaixo dela
            p -= nrm * 0.0018 * math.exp(-(d2 / 0.0035) ** 2)
        d, _ = seg_yz(q, (OLHO_A.y - 0.014, OLHO_A.z - 0.004), (OLHO_A.y - 0.052, OLHO_A.z - 0.020))   # sulco lacrimal
        if ax_ > 0.03: p -= nrm * 0.0022 * math.exp(-(d / 0.0035) ** 2)
    e = V(((ax_ - OLHO_A.x) / 0.012, (y - OLHO_A.y) / 0.018, (z - OLHO_A.z) / 0.011)).length       # palpebras
    if 0.85 < e < 1.4: p += nrm * 0.0026 * math.sin(math.pi * (e - 0.85) / 0.55)
    if z > OLHO_A.z + 0.004 and ax_ > OLHO_A.x - 0.025:                                          # arcada baixa na frente
        d, t = seg_yz(q, (OLHO_A.y - 0.026, OLHO_A.z + 0.011), (OLHO_A.y + 0.022, OLHO_A.z + 0.024))
        p += nrm * 0.0052 * math.exp(-(d / 0.0068) ** 2) * math.sin(math.pi * (0.2 + 0.8 * t))   # refinado: olhar mais severo
ob.data.update()
# R3 (01/11): cabeca angular e esculpida sem virar bloco -- quinas por "afiacao pela normal" (sobe a pele no meio da
# faixa de normal da quina e afunda dos dois lados: aresta nitida, volume igual), maca marcada, placa da palpebra
# inferior (assenta o olho), crista temporal da sobrancelha ate o chifre e testa levemente plana entre as cristas
def faixa(c, w): return math.exp(-(c / w) ** 2)
for v in ob.data.vertices:
    p, nrm = v.co, v.normal; x, y, z = p
    if y > -0.68: continue
    ax_, nx = abs(x), abs(nrm.x); q = V((ax_, y, z)); zb = 0.704 + (y + 0.95) * 0.07
    if -0.945 < y < -0.79 and z > zb + 0.012:                                                     # quina do focinho
        f = suave((y + 0.945) / 0.02) * suave((-0.79 - y) / 0.03); c = math.atan2(nx, nrm.z) - 0.95
        p += nrm * f * (0.0048 * faixa(c, 0.15) - 0.0020 * (faixa(c - 0.42, 0.14) + faixa(c + 0.45, 0.14)))
    if -0.93 < y < -0.74 and z < zb - 0.006:                                                      # linha da mandibula
        f = suave((y + 0.93) / 0.03) * suave((-0.74 - y) / 0.02); c = math.atan2(nx, -nrm.z) - 0.85
        p += nrm * f * (0.0045 * faixa(c, 0.14) - 0.0018 * (faixa(c - 0.40, 0.13) + faixa(c + 0.42, 0.13)))
    if nx > 0.25:
        d, t = seg_yz(q, (-0.825, 0.736), (-0.712, 0.716))                                        # maca marcada
        if ax_ > 0.035: p += nrm * 0.0034 * math.exp(-(d / 0.0040) ** 2) * math.sin(math.pi * (0.1 + 0.9 * t))
        d, t = seg_yz(q, (OLHO_A.y - 0.016, OLHO_A.z - 0.010), (OLHO_A.y + 0.016, OLHO_A.z - 0.008))   # palpebra inferior
        p += nrm * 0.0016 * math.exp(-(d / 0.0030) ** 2) * math.sin(math.pi * t)
    if z > OLHO_A.z:                                                                              # crista temporal
        d, t = seg_yz(q, (OLHO_A.y + 0.020, OLHO_A.z + 0.024), (-0.742, 0.826))
        f = faixa(math.atan2(nx, nrm.z) - 0.80, 0.30)
        if ax_ > 0.018: p += nrm * 0.0045 * f * math.exp(-(d / 0.0050) ** 2) * math.sin(math.pi * (0.15 + 0.7 * t))
    if -0.80 < y < -0.72 and z > 0.80 and ax_ < 0.022 and nrm.z > 0.8: p.z -= 0.0018 * (1 - ax_ / 0.022)   # testa
ob.data.update()
# R3: BOCA REAL -- as faces que cruzam a linha da boca a frente do canto saem (labios separados, encostados em repouso)
# e entra a cavidade (palato, assoalho, garganta, bochechas, lingua); grupo SB_Mandibula marca o que segue o maxilar
Y_CANTO, Y_DOBRA = -0.772, -0.700
def z_boca(y): y = max(y, -0.99); return 0.704 + (y + 0.95) * 0.07 + 0.008 * suave((y + 0.79) / 0.04)
bm = bmesh.new(); bm.from_mesh(ob.data)
def abaixo(p): return p.z < z_boca(p.y)
cruz = [f for f in bm.faces if all(v.co.y < Y_CANTO for v in f.verts) and 0 < sum(abaixo(v.co) for v in f.verts) < len(f.verts)]
bmesh.ops.delete(bm, geom=cruz, context="FACES_ONLY")
for v in bm.verts:
    if v.is_boundary and v.co.y < Y_CANTO + 0.003: v.co.z = z_boca(v.co.y) + (-0.0010 if abaixo(v.co) else 0.0010)
bm.to_mesh(ob.data); bm.free(); ob.data.update()
print("DRAGAO_BOCA faces cortadas", len(cruz))
# R8: BOCA COMO BOLSA CONTINUA. A borda da fenda e extrudada para dentro em aneis: labio com espessura -> gengiva ->
# ceu da boca (em cima) / assoalho (embaixo) -> garganta no fundo (o canto liga cima e baixo). E a MESMA pele do corpo:
# ao abrir, o lado de cima segue a cabeca e o de baixo a mandibula, e o que fica entre estica como tecido (sem pecas
# coladas). Profundidade de cada lado = fracao da meia-altura real da cabeca naquele ponto (nunca fura a pele).
def meia_altura(y, cima):
    if cima: ok, h, _, _ = ob.ray_cast(V((0, y, 1.2)), V((0, 0, -1)))
    else: ok, h, _, _ = ob.ray_cast(V((0, y, 0.40)), V((0, 0, 1)))
    return max(0.006, abs(h.z - z_boca(y))) if ok else 0.012
bm = bmesh.new(); bm.from_mesh(ob.data)
kl = bm.verts.layers.float.new("boca_k")            # (antes de guardar vertices: nova camada invalida as referencias)
bm.verts.ensure_lookup_table()
borda = [e for e in bm.edges if e.is_boundary]
lab = {v for e in borda for v in e.verts}
info = {}
for v in lab:
    zb = z_boca(v.co.y); sd = 1 if v.co.z > zb else -1
    info[v] = (v.co.copy(), sd, meia_altura(min(v.co.y, Y_CANTO - 0.004), sd > 0))
Y_PONTA_L = min(v.co.y for v in lab)                # ponta do focinho (labios): ali a cabeca e fina
ANEIS = [(0.84, 0.10, 0.000), (0.68, 0.30, 0.002), (0.46, 0.48, 0.004), (0.22, 0.56, 0.006), (0.0, 0.58, 0.007)]
atual, mapa, n_boca = borda, {v: v for v in lab}, 0
for k, (fx, fz, dy) in enumerate(ANEIS):
    r = bmesh.ops.extrude_edge_only(bm, edges=atual)
    nvs = [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]
    nes = [g for g in r["geom"] if isinstance(g, bmesh.types.BMEdge)]
    novo_mapa = {}
    from mathutils import kdtree as _kd
    ants = list(mapa); kt = _kd.KDTree(len(ants))
    for i_, a_ in enumerate(ants): kt.insert(a_.co, i_)
    kt.balance()
    for nv in nvs:                                      # o vertice novo nasce em cima do anterior (extrusao sem mover)
        _, i_, dd = kt.find(nv.co)
        o = mapa[ants[i_]]; p0, sd, Hm = info[o]
        zb = z_boca(min(p0.y, Y_CANTO))
        fp = 0.30 + 0.70 * suave((p0.y - Y_PONTA_L) / 0.05)                         # rasa na ponta (nao sai pelo queixo)
        nv.co = V((p0.x * fx, p0.y + dy, zb + sd * (0.0012 + fz * Hm * fp)))
        nv[kl] = (k + 1) / len(ANEIS); novo_mapa[nv] = o
    for f_ in {f_ for v in nvs for f_ in v.link_faces}: f_.material_index = 1; f_.smooth = True; n_boca += 1
    mapa = novo_mapa; atual = [e for e in nes if e.is_boundary]
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(ob.data); bm.free(); ob.data.update()
print("DRAGAO_BOCA bolsa faces", n_boca)
Y_DOBRA = -0.685
vg = ob.vertex_groups.new(name="SB_Mandibula")
for v in ob.data.vertices:
    p = v.co
    if p.y < Y_CANTO + 0.008 and abs(p.z - z_boca(min(p.y, Y_CANTO))) < 0.05 and p.y > -1.0:
        d = p.z - z_boca(min(p.y, Y_CANTO))
        w = 1.0 if d < -0.0005 else (0.0 if d > 0.0005 else 0.5)          # labio/gengiva/ceu = 0, assoalho = 1
        if p.y > Y_CANTO: w = min(w, 0.85)
    elif p.y < Y_DOBRA and 0.655 < p.z < z_boca(Y_CANTO):                                         # bochecha: transicao
        w = (1 - suave((p.y - Y_CANTO) / (Y_DOBRA - Y_CANTO))) * 0.85 * suave((z_boca(Y_CANTO) - p.z) / 0.008)
    elif -0.735 < p.y < -0.62 and p.z < 0.69:                                                     # garganta reage (r8)
        w = 0.30 * (1 - suave((p.y + 0.735) / 0.115)) * suave((0.69 - p.z) / 0.02)
    else: continue
    if w > 0.01: vg.add([v.index], w, "REPLACE")
ok_, pt_, _, _ = ob.ray_cast(V((0, -1.2, z_boca(-0.97))), V((0, 1, 0))); Y_PONTA = pt_.y if ok_ else -0.975
def larg(y):
    ok, h, _, _ = ob.ray_cast(V((0.3, y, z_boca(y) + 0.005)), V((-1, 0, 0)))
    return max(0.004, (h.x if ok else 0.01) - 0.0035)
Y0, Y1 = Y_PONTA + 0.006, Y_CANTO - 0.004
LG = [(Y0 + (Y1 - Y0) * i / 12, larg(min(Y0 + (Y1 - Y0) * i / 12, Y_CANTO - 0.002))) for i in range(13)]
def lw(y):
    for (ya, wa), (yb, wb) in zip(LG, LG[1:]):
        if ya <= y <= yb: return lerp(wa, wb, (y - ya) / (yb - ya))
    return LG[0][1] if y < LG[0][0] else LG[-1][1]
def malha_grades(nome, grades):
    pts_, fcs = [], []
    for P, nu, nv in grades:
        b0 = len(pts_)
        for j in range(nv + 1):
            for i in range(nu + 1): pts_.append(P(i / nu, j / nv))
        for j in range(nv):
            for i in range(nu): a = b0 + j * (nu + 1) + i; fcs.append((a, a + 1, a + nu + 2, a + nu + 1))
    m = bpy.data.meshes.new(nome); m.from_pydata([tuple(p) for p in pts_], [], fcs)
    for pl in m.polygons: pl.use_smooth = True
    o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o); return o
def lingua(t, j):
    """lingua (r8): lamina carnuda deitada sobre o assoalho, mais larga atras, ponta fina, sulco central"""
    y = lerp(Y0 + 0.050, Y_CANTO - 0.006, j); w = lw(y) * 0.46 * (0.30 + 0.70 * suave(j * 2.0)); a = math.pi * t
    zf = z_boca(min(y, Y_CANTO)) - 0.0012 - 0.40 * meia_altura(min(y, Y_CANTO - 0.004), False) * (0.30 + 0.70 * suave((y - Y0) / 0.05))
    return V((-w * math.cos(a), y, zf + 0.0050 * math.sin(a) ** 0.7 - 0.0016 * math.exp(-((t - 0.5) / 0.10) ** 2)))
BOCA_INF = malha_grades("SB_Dragao_Boca_Inf", [(lingua, 12, 16)])
BOCA = [BOCA_INF]
K_CAB, PIV = 1.14, V((0, -0.64, 0.725))   # SOMBRIO: cabeca maior e mais imponente         # esguio: cabeca pequena como na referencia (sem aumento)         # glacial: cabeca proporcional (referencia elegante); articulacoes iguais
def cabeca(p, w=None):
    w = suave((-0.61 - p.y) / 0.09) if w is None else w
    return PIV + (p - PIV) * (1 + (K_CAB - 1) * w)
for v in ob.data.vertices: v.co = cabeca(v.co)
ob.data.update()

# ------------------------------------------------------------------ membranas (presas so ao flanco, a frente do quadril)
def membrana(s):
    raiz, cot, pul, dedos = asa(s); pts, faces, uvs = [], [], []
    regiao = [0]
    def grade(P, nu, nv):
        base = len(pts)
        for j in range(nv + 1):
            for i in range(nu + 1):
                pts.append(P(i / nu, j / nv)); uvs.append((regiao[0] + i / nu, j / nv))   # U = setor + posicao no setor
        for j in range(nv):
            for i in range(nu):
                a = base + j * (nu + 1) + i; faces.append((a, a + 1, a + nu + 2, a + nu + 1))
    def dedo(d, t):
        cad = [pul, d[0], d[1], d[2]]; L = [0]
        for a, b in zip(cad, cad[1:]): L.append(L[-1] + (b - a).length)
        alvo = t * L[-1]
        for k in range(3):
            if alvo <= L[k + 1]: return lerp(cad[k], cad[k + 1], (alvo - L[k]) / (L[k + 1] - L[k]))
        return cad[-1]
    for a, b in zip(dedos, dedos[1:]):
        def P(u, t, a=a, b=b):
            pa, pb = dedo(a, t), dedo(b, t); p = lerp(pa, pb, u); corda = (pb - pa).length
            p += (pul - p).normalized() * 0.62 * corda * math.sin(math.pi * u) ** 0.85 * t ** 2.2   # r4: pontas afiadas nos dedos   # refinado: recorte mais fundo e elegante
            p.z -= 0.030 * math.sin(math.pi * u) * t ** 0.8                                    # r2: barriga de vela mais viva
            p.z -= 0.004 * math.sin(math.pi * 2 * u) ** 2 * t * (1 - t) * 4                     # prega suave no meio do setor
            p.z -= 0.003 * (math.exp(-(u / 0.10) ** 2) + math.exp(-((1 - u) / 0.10) ** 2)) * t * (1 - t) * 4   # tensao junto aos dedos
            return p
        grade(P, 14, 22); regiao[0] += 1
    flanco = V((0.090 * s, 0.30, 0.52))                       # r4: presa mais alta no flanco (base limpa)
    def braco(u):
        if u < 0.55: return lerp(pul, cot, u / 0.55)
        return lerp(cot, raiz + V((0.0, 0.07, -0.02)), (u - 0.55) / 0.45)
    def borda(u):
        p = lerp(dedos[3][2], flanco, u); p += (cot - p).normalized() * 0.40 * math.sin(math.pi * u) ** 1.2; return p   # r2: recorte interno
    def Pc(u, t):
        p = lerp(braco(u), borda(u), t); p.z -= 0.025 * math.sin(math.pi * u) * math.sin(math.pi * t)
        return lerp(p, dedo(dedos[3], t), (1 - u) ** 3)
    grade(Pc, 14, 18); regiao[0] += 1
    # membrana da frente (propatagio), refino final: antes era uma fita reta solta do ombro ao punho com um vao ate o
    # braco; agora preenche do braco (ombro -> cotovelo -> punho) ate a borda de ataque, tensa e levemente convexa
    l1, l2 = (cot - raiz).length, (pul - cot).length
    def osso_braco(u):
        a = u * (l1 + l2)
        return lerp(raiz, cot, a / l1) if a <= l1 else lerp(cot, pul, (a - l1) / l2)
    def Pp(u, t):
        a = osso_braco(u)
        b = lerp(raiz + V((0, -0.03, 0.0)), pul + V((0, -0.012, 0.0)), u) + V((0, -0.035, 0.004)) * math.sin(math.pi * u)
        p = lerp(a, b, t); p.z -= 0.010 * math.sin(math.pi * u) * math.sin(math.pi * t)          # leve barriga entre osso e borda
        return p
    grade(Pp, 16, 6)
    m = bpy.data.meshes.new("Membrana"); m.from_pydata([tuple(p) for p in pts], [], faces)
    uvl = m.uv_layers.new(name="UVMembrana")
    for pl in m.polygons:
        for li in pl.loop_indices: uvl.data[li].uv = uvs[m.loops[li].vertex_index]
    o = bpy.data.objects.new("SB_Dragao_Membrana_" + ("L" if s > 0 else "R"), m); sc.collection.objects.link(o)
    for p in m.polygons: p.use_smooth = True
    o.modifiers.new("Solda", "WELD").merge_threshold = 0.002
    so = o.modifiers.new("Espessura", "SOLIDIFY"); so.thickness = 0.0035; so.offset = 0
    ss = o.modifiers.new("Sub", "SUBSURF"); ss.levels = ss.render_levels = 1
    return o
MEMB = [membrana(1), membrana(-1)]
def para_cabeca(o):
    o.location = PIV + (o.location - PIV) * K_CAB; o.scale = o.scale * K_CAB

# ------------------------------------------------------------------ pecas rigidas
def tubo(pts, r0, nome, expo=1.15):
    m = bpy.data.meshes.new(nome); o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    o.location = pts[0]                                       # origem na base: o material mede a distancia ate ela
    b = bmesh.new(); vs = [b.verts.new(p - pts[0]) for p in pts]
    for a, c in zip(vs, vs[1:]): b.edges.new((a, c))
    b.to_mesh(m); b.free()
    k = o.modifiers.new("Pele", "SKIN"); k.use_smooth_shade = True
    n = len(pts)
    for i, d in enumerate(m.skin_vertices[0].data):
        r = r0 * (1 - i / (n - 1)) ** expo + 0.0012; d.radius = (r, r); d.use_root = i == 0
    s2 = o.modifiers.new("Sub", "SUBSURF"); s2.levels = s2.render_levels = 2
    return o
CHIFRES, ESPINHOS, GARRAS, OLHOS, DENTES = [], [], [], [], []
ARCO_PRINC, PRINC = {}, {}
for s in (1, -1):
    # COROA (referencia): chifre principal longo e fino varrido para tras, 3 pontas menores em leque atras/fora
    # refinado: chifres em ARCO (a direcao gira suave da base a ponta) -> sobem e varrem para tras como lamina de gelo,
    # e a coroa vira um leque de 4 pontas por lado, decrescentes, abrindo para tras/fora atras do chifre principal
    def arco(b0, d0, d1, comp, n_=7):
        pts_, p_ = [b0], b0.copy()
        for i_ in range(n_):
            t_ = (i_ + 0.5) / n_; p_ = p_ + lerp(V(d0).normalized(), V(d1).normalized(), suave(t_)).normalized() * comp / n_
            pts_.append(p_.copy())
        return pts_
    # SOMBRIO: DOIS chifres grandes (referencia): base grossa atras da arcada, sobem varrendo para tras e a ponta
    # curva para cima (crescente), leve abertura para fora
    ARCO_PRINC[s] = arco(V((0.034 * s, -0.738, 0.820)), (0.10 * s, 1.0, 0.10), (0.05 * s, 0.75, 0.80), 0.36, 10)   # v4: quase horizontal para tras, ponta sobe
    CHIFRES.append(tubo(ARCO_PRINC[s], 0.025, "Chifre", 1.05)); PRINC[s] = CHIFRES[-1]
    continue
    # r2: coroa de gelo lendaria -- 6 pontas finas por lado em leque continuo (de cima para o lado) e 3 pontas baixas
    # na linha media do cranio; todas em arco, finas na ponta
    # R3: 5 pontas por lado (menos excesso, mais espaco entre elas) com leve assimetria natural de comprimento e angulo
    rv_ = random.Random(17 if s > 0 else 23)
    for k, (comp, r0) in enumerate(((0.195, 0.0105), (0.165, 0.0094), (0.135, 0.0084), (0.105, 0.0072), (0.078, 0.0060))):
        b0 = V(((0.044 + 0.008 * k) * s, -0.730 + 0.015 * k, 0.820 - 0.019 * k))
        d0 = V(((0.20 + 0.13 * k) * s, 0.70, 1.0 - 0.26 * k + 0.08 * (rv_.random() - 0.5)))
        d1 = ((0.16 + 0.10 * k) * s, 1.0, 0.32 - 0.16 * k)
        CHIFRES.append(tubo(arco(b0, d0, d1, comp * (1 + 0.08 * (rv_.random() - 0.5)), 6), r0, "Chifre_Coroa", 1.45))
for yy, comp in ((-0.770, 0.026), (-0.748, 0.036)):                                        # SOMBRIO: crista media baixa
    CHIFRES.append(tubo(arco(V((0.0, yy, 0.825)), (0, 0.55, 1.0), (0, 1.0, 0.30), comp, 4), 0.0060, "Chifre_Coroa", 1.5))
for s in (1, -1):
    # babado de espinhos finos ao longo da mandibula e da bochecha, abrindo para tras (referencia); refinado: curvos
    # R3: cristas laterais -- chifre da bochecha (nasce na maca e varre para tras) e crista do angulo da mandibula
    ESPINHOS.append(tubo(arco(V((0.058 * s, -0.752, 0.748)), (0.42 * s, 1.0, 0.30), (0.28 * s, 1.0, 0.08), 0.150, 6), 0.0110, "Espinho_Bochecha", 1.3))
    for k in range(4):                                        # SOMBRIO: leque occipital (atras e abaixo do chifre)
        b0 = V(((0.050 - 0.004 * k) * s, -0.712 + 0.010 * k, 0.800 - 0.026 * k))
        ESPINHOS.append(tubo(arco(b0, (0.40 * s, 1.0, 0.45 - 0.12 * k), (0.26 * s, 1.0, 0.10 - 0.06 * k), 0.150 - 0.020 * k, 6),
                             0.0105 - 0.0012 * k, "Espinho_Bochecha", 1.3))
    ESPINHOS.append(tubo(arco(V((0.054 * s, -0.738, 0.712)), (0.45 * s, 1.0, -0.10), (0.30 * s, 1.0, 0.02), 0.085, 5), 0.0068, "Espinho_Bochecha", 1.4))   # r8: na dobradica (nao aparece no canto da boca aberta)
    rv_ = random.Random(41 if s > 0 else 43)
    for k in range(2, 6):                                     # babado (R3: 4; os 2 da frente ficavam enterrados na maca)
        base = V((0.048 * s, -0.805 + 0.020 * k, 0.716 - 0.004 * k)); comp = (0.110 - 0.010 * k) * (1 + 0.10 * (rv_.random() - 0.5))
        ESPINHOS.append(tubo(arco(base, (0.55 * s, 1.0, 0.10 - 0.05 * k), (0.30 * s, 1.0, 0.16 - 0.03 * k), comp, 4),
                             0.0068 - 0.0005 * k, "Espinho_Bochecha", 1.45))
def eixo_em(y):
    for a, b in zip(ESPINHA, ESPINHA[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0]); return lerp(a[1], b[1], t), lerp(a[3], b[3], t)
    return ESPINHA[-1][1], ESPINHA[-1][3]
def espinho_dorsal(p, alt, larg, inc, nome, curva=0.5):
    """lamina curvada para tras (R3: borda da frente concava como espinho de rosa, ponta mais varrida conforme 'curva',
    espessura proporcional a altura); folga entre espinhos para o pescoco dobrar"""
    m = bpy.data.meshes.new(nome); b = bmesh.new()
    perfil = [(-larg, 0.0), (larg * 0.55, 0.0), (larg * 0.30 + alt * curva * 0.30, alt * 0.55), (-larg * 0.15 + alt * curva, alt),
              (-larg * 0.55 + alt * curva * 0.30, alt * 0.45)]   # (y, z)
    anel = []; esp_ = 0.0035 + alt * 0.07
    for (yy, zz) in perfil:
        anel.append([b.verts.new((xx, yy, zz)) for xx in (-esp_ * (1 - zz / alt * 0.8), esp_ * (1 - zz / alt * 0.8))])
    for i in range(len(anel)):
        j = (i + 1) % len(anel)
        b.faces.new((anel[i][0], anel[j][0], anel[j][1], anel[i][1]))
    b.faces.new([a[0] for a in anel][::-1]); b.faces.new([a[1] for a in anel])
    b.to_mesh(m); b.free()
    o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o)
    o.location = p; o.rotation_euler = (inc, 0, 0)
    sd = o.modifiers.new("Sub", "SUBSURF"); sd.levels = sd.render_levels = 2
    for pl in m.polygons: pl.use_smooth = True
    return o
ENC_DORSAL = {}
EIXO = [V((0, y, z)) for y, z, _, _ in ESPINHA]; RAIO_H = [ry for _, _, _, ry in ESPINHA]
def eixo_s(dist):
    """ponto, tangente e raio no eixo a 'dist' do inicio (focinho)"""
    for k in range(len(EIXO) - 1):
        a, b = EIXO[k], EIXO[k + 1]; L_ = (b - a).length
        if dist <= L_: t = dist / L_; return lerp(a, b, t), (b - a).normalized(), lerp(RAIO_H[k], RAIO_H[k + 1], t)
        dist -= L_
    return EIXO[-1], (EIXO[-1] - EIXO[-2]).normalized(), RAIO_H[-1]
# R3: sequencia organica da nuca a cauda -- maiores na nuca e no alto do pescoco (como na referencia), ritmo
# maior/menor alternado com pequena variacao, mais varridos para tras no pescoco; base esculpida na pele depois
rvd = random.Random(31)
dist = sum((EIXO[k + 1] - EIXO[k]).length for k in range(I_NUCA)) - 0.012; i = 0
while True:
    c, tg, r = eixo_s(dist)
    if c.y > Y_CAUDA - 0.20: break                                     # SOMBRIO: cauda mais curta
    if c.y < -0.40 and 0.60 < c.z < 0.785 and i % 2: dist += 0.012; continue   # r4: folga na juncao concava pescoco -> dorso (dobra)
    up = V((0, -tg.z, tg.y))                                         # lado dorsal (perpendicular ao eixo)
    alt = 0.018 + 0.016 * math.exp(-((c.y + 0.25) / 0.40) ** 2) + 0.006 * math.exp(-((c.y - 0.30) / 0.4) ** 2)
    if c.y < -0.45: alt += 0.050 * math.exp(-((c.z - 1.03) / 0.16) ** 2) + 0.020 * math.exp(-((c.z - 0.82) / 0.16) ** 2)   # r4: leitura clara
    alt *= 1.25 * (1 - 0.45 * suave((c.y - 0.5) / 1.6))                       # SOMBRIO: serra marcada ate a cauda
    alt *= (0.78 if i % 2 else 1.0) * (1 + 0.12 * (rvd.random() - 0.5))
    e = espinho_dorsal(c + up * r * 0.93, alt, 0.010 + alt * 0.34, 0.0, "Espinho_Dorsal_%02d" % i, (0.85 if c.z > 0.96 else 0.50) if c.y < -0.40 else 0.60)
    e.rotation_euler = (math.atan2(-up.y, up.z) - (0.12 if (c.y < -0.40 and c.z < 0.96) else 0.30), 0, 0); ESPINHOS.append(e); ENC_DORSAL[e.name] = -up; e["alt"] = alt
    dist += (0.030 + alt * 0.52 + 0.14 * r if c.y < -0.40 else 0.022 + alt * 0.34); i += 1   # pescoco: folga p/ dobrar para tras
for s in (1, -1):
    for dian in (True, False):
        for d in dedos_pe(s, dian):
            ponta = d[-1][0]; dirv = (ponta - d[0][0]).normalized()
            dirv = V((dirv.x, dirv.y, 0)).normalized(); cai = ponta.z - 0.003          # R3: ponta encosta no chao
            pts = [ponta + dirv * 0.002, ponta + dirv * 0.026 + V((0, 0, 0.007)), ponta + dirv * 0.050 + V((0, 0, 0.003)),
                   ponta + dirv * 0.070 + V((0, 0, -0.35 * cai)), ponta + dirv * 0.082 + V((0, 0, -0.75 * cai)), ponta + dirv * 0.086 + V((0, 0, -cai))]
            GARRAS.append(tubo([ponta + (q - ponta) * 1.22 for q in pts], 0.0160, "Garra", 1.5))   # SOMBRIO: garras longas   # r8: maiores/afiadas                     # R3: 3 garras longas em gancho por pata
    raiz, cot, pul, dedos = asa(s)
    for d in dedos[:1]:                                         # garra na ponta do dedo de ataque
        GARRAS.append(tubo([d[2], d[2] + (d[2] - d[1]).normalized() * 0.05 + V((0, 0, -0.018))], 0.0085, "Garra_Asa"))
    for d in dedos[1:]:                                         # refinado: esporao de gelo fino na ponta dos outros dedos
        dv = (d[2] - d[1]).normalized()
        GARRAS.append(tubo([d[2] - dv * 0.004, d[2] + dv * 0.030, d[2] + dv * 0.050 + V((0, 0, -0.004))], 0.0045, "Garra_Asa"))
    pol = pul + V((0.03 * s, -0.085, 0.008))
    # SOMBRIO: garra do punho grande, em gancho que sobe (silhueta da referencia)
    GARRAS.append(tubo([pol, pol + V((0.010 * s, -0.030, 0.018)), pol + V((0.012 * s, -0.040, 0.050)), pol + V((0.006 * s, -0.020, 0.080))],
                       0.0150, "Garra_Polegar", 1.3))
# (dentes: criados depois do encaixe, ja na escala final da cabeca; ver "dentes (refino final)")
# ponta da cauda (refino): tres laminas finas de gelo em leque, discretas (seguem o ultimo osso)
# refinado: leque de cristal (5 laminas: central alta, duas em diagonal, duas quase de lado) -> ponta marcante
for k, (yy, ang, alt, lg) in enumerate(()):                 # SOMBRIO: sem leque na ponta (cauda termina afiada)
    z, r = eixo_em(yy)
    lam = espinho_dorsal(V((0, yy, z + r * 0.6)), alt, lg, -0.55, "Espinho_Dorsal_Cauda_%d" % k)
    lam.rotation_euler = (-0.62, ang, 0); ESPINHOS.append(lam)
for s in (1, -1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0092, location=(OLHO.x * s, OLHO.y, OLHO.z), segments=24, ring_count=12)
    o = bpy.context.object; o.name = "Olho"; o.scale = (0.74, 1.50, 0.70); bpy.ops.object.shade_smooth(); OLHOS.append(o)   # refinado: amendoado (sem sumir sob a arcada)

# ------------------------------------------------------------------ materiais
def mat(nome):
    m = bpy.data.materials.new(nome)
    if m.node_tree is None: m.use_nodes = True
    nt = m.node_tree; return m, nt, nt.nodes["Principled BSDF"], nt.links
def n(nt, t, **kw):
    x = nt.nodes.new(t)
    for k, v in kw.items(): setattr(x, k, v)
    return x
def rampa(nt, L, ent, pares):
    r = n(nt, "ShaderNodeValToRGB"); L.new(ent, r.inputs[0]); el = r.color_ramp.elements
    el[0].position, el[0].color = pares[0]; el[1].position, el[1].color = pares[-1]
    for pos, cor in pares[1:-1]: e = el.new(pos); e.color = cor
    return r
def mat_corpo():
    m, nt, b, L = mat("M_Dragao_Escamas")
    tc = n(nt, "ShaderNodeTexCoord"); geo = n(nt, "ShaderNodeNewGeometry")
    pos = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], pos.inputs[0])
    nr = n(nt, "ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], nr.inputs[0])
    # escamas SOBREPOSTAS (conceito): maiores no dorso/patas, menores na cabeca/pescoco, alongadas ao longo do
    # corpo; cada escama sobe na borda de tras (+Y) e afunda sob a da frente -> leitura de placas em telhado
    def mr(ent, a, b_, c=0.0, d=1.0):
        x = n(nt, "ShaderNodeMapRange"); x.inputs[1].default_value = a; x.inputs[2].default_value = b_
        x.inputs[3].default_value = c; x.inputs[4].default_value = d; L.new(ent, x.inputs[0]); return x.outputs[0]
    def op(o_, a, b_=None, v=None):
        x = n(nt, "ShaderNodeMath", operation=o_); L.new(a, x.inputs[0])
        if b_ is not None: L.new(b_, x.inputs[1])
        if v is not None: x.inputs[1].default_value = v
        return x.outputs[0]
    corpo_f = mr(pos.outputs["Y"], -0.72, -0.45)                         # 0 cabeca -> 1 corpo
    dors_f = mr(nr.outputs["Z"], 0.0, 0.7)                               # dorso (face para cima) = escamas maiores
    # HIERARQUIA (refino): face fina -> pescoco/tronco medio -> faixa dorsal e ombros/coxas maiores; laterais do pescoco
    # e dobras das patas menores (areas flexiveis)
    axn = op("ABSOLUTE", nr.outputs["X"]); axpos = op("ABSOLUTE", pos.outputs["X"])
    faixa_dors = op("MULTIPLY", mr(nr.outputs["Z"], 0.70, 0.95), mr(axpos, 0.07, 0.025))
    pesc_lat = op("MULTIPLY", op("MULTIPLY", mr(pos.outputs["Y"], -0.30, -0.42), mr(pos.outputs["Y"], -0.74, -0.66)), mr(axn, 0.35, 0.75))
    flex = op("MULTIPLY", mr(pos.outputs["Z"], 0.30, 0.20), mr(pos.outputs["Z"], 0.05, 0.12))        # canela/punho
    massa = op("MULTIPLY", mr(pos.outputs["Z"], 0.30, 0.40), mr(axn, 0.55, 0.85))                     # ombro/coxa (lateral alto)
    # (refinado: o mosaico grande no topo da cabeca parecia rachado; agora so um pouco maior que as laterais)
    # topo da cabeca (focinho/testa): escudos maiores que as laterais finas do rosto (hierarquia do refino final)
    cab_topo = op("MULTIPLY", mr(nr.outputs["Z"], 0.50, 0.85), op("SUBTRACT", op("MULTIPLY", corpo_f, v=-1.0), v=-1.0))
    tam0 = op("SUBTRACT", mr(corpo_f, 0, 1, 330, 175), op("ADD", op("MULTIPLY", dors_f, v=30.0), op("MULTIPLY", cab_topo, v=35.0)))
    tam1 = op("SUBTRACT", op("ADD", tam0, op("ADD", op("MULTIPLY", pesc_lat, v=90.0), op("MULTIPLY", flex, v=80.0))),
              op("ADD", op("MULTIPLY", faixa_dors, v=85.0), op("MULTIPLY", massa, v=12.0)))
    tam = op("MAXIMUM", tam1, v=60.0)
    estica = n(nt, "ShaderNodeVectorMath", operation="MULTIPLY"); estica.inputs[1].default_value = (1.0, 0.72, 1.0)
    L.new(tc.outputs["Object"], estica.inputs[0])
    # REFINO FINAL: escala da escama em CAMADAS FIXAS (fina/media/grande/escudo) trocadas em faixas estreitas; a escala
    # continua do Voronoi esticava as celulas em riscos onde o tamanho mudava (pescoco, rosto)
    def camada(esc):
        ve_ = n(nt, "ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE"); vc_ = n(nt, "ShaderNodeTexVoronoi")
        for t in (ve_, vc_): L.new(estica.outputs[0], t.inputs["Vector"]); t.inputs["Scale"].default_value = esc
        rel_ = n(nt, "ShaderNodeVectorMath", operation="SUBTRACT"); L.new(estica.outputs[0], rel_.inputs[0]); L.new(vc_.outputs["Position"], rel_.inputs[1])
        rx_ = n(nt, "ShaderNodeSeparateXYZ"); L.new(rel_.outputs[0], rx_.inputs[0])
        return ve_.outputs["Distance"], vc_.outputs["Color"], mr(op("MULTIPLY", rx_.outputs["Y"], v=esc), -0.5, 0.5)
    def misturar(a, b_, f, cor_=False):
        x = n(nt, "ShaderNodeMix", data_type="RGBA" if cor_ else "FLOAT"); L.new(f, x.inputs["Factor"])
        L.new(a, x.inputs[6 if cor_ else 2]); L.new(b_, x.inputs[7 if cor_ else 3]); return x.outputs[2 if cor_ else 0]
    DIST, CORV, tras = camada(340.0)
    for esc, corte in ((225.0, 282.0), (150.0, 187.0), (95.0, 122.0)):
        f = mr(tam, corte + 24.0, corte - 24.0)            # r9: troca de tamanho de escama gradual (sem "remendo")
        d_, c_, t_ = camada(esc)
        DIST, CORV, tras = misturar(DIST, d_, f), misturar(CORV, c_, f, True), misturar(tras, t_, f)
    ruido = n(nt, "ShaderNodeTexNoise"); ruido.inputs["Scale"].default_value = 7; L.new(tc.outputs["Object"], ruido.inputs["Vector"])
    # vermelho-alaranjado vivo do conceito (lineares; sRGB ~ 220,60,40 no tom medio)
    verm = rampa(nt, L, ruido.outputs["Fac"], [(0.3, (0.008, 0.005, 0.013, 1)), (0.55, (0.014, 0.008, 0.024, 1)), (0.8, (0.024, 0.013, 0.040, 1))])   # SOMBRIO: preto-violeta   # azul-gelo saturado
    tom = n(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); tom.inputs["Factor"].default_value = 0.20   # cada escama com tom proprio
    L.new(verm.outputs["Color"], tom.inputs[6]); L.new(CORV, tom.inputs[7])
    fr_ = mr(DIST, 0.0, 0.12)
    fr = n(nt, "ShaderNodeMath", operation="ADD"); L.new(fr_, fr.inputs[0]); fr.inputs[1].default_value = 0.0   # compat: fr.outputs[0]
    brilho = op("MULTIPLY", op("POWER", fr.outputs[0], v=0.5), tras)     # borda de tras erguida pega luz
    realce = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(op("MULTIPLY", brilho, v=0.28), realce.inputs["Factor"])
    # dorso mais profundo e saturado, flancos mais claros (contraste dorso/ventre da referencia)
    dorsal_cor = n(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); L.new(op("MULTIPLY", mr(nr.outputs["Z"], 0.2, 0.9), v=0.40), dorsal_cor.inputs["Factor"])
    L.new(tom.outputs[2], dorsal_cor.inputs[6]); dorsal_cor.inputs[7].default_value = (0.45, 0.38, 0.55, 1)
    L.new(dorsal_cor.outputs[2], realce.inputs[6]); realce.inputs[7].default_value = (0.11, 0.04, 0.24, 1)    # SOMBRIO: borda com reflexo violeta
    esc = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(op("POWER", fr.outputs[0], v=0.6), esc.inputs["Factor"])
    # refinado: na cabeca as fendas ficam bem mais suaves (o mosaico escuro lia como rachadura)
    fenda = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(op("SUBTRACT", op("MULTIPLY", corpo_f, v=-1.0), v=-1.0), fenda.inputs["Factor"])
    fenda.inputs[6].default_value = (0.004, 0.002, 0.008, 1); fenda.inputs[7].default_value = (0.012, 0.007, 0.020, 1)
    L.new(fenda.outputs[2], esc.inputs[6]); L.new(realce.outputs[2], esc.inputs[7])     # fendas azul-marinho (suaves)
    ALT_ESC = op("MULTIPLY", op("POWER", fr.outputs[0], v=0.5), op("ADD", op("MULTIPLY", tras, v=0.7), v=0.3))
    # ventre marfim em placas: faixa central de baixo (tronco/cauda) e frente do pescoco/garganta
    ax = n(nt, "ShaderNodeMath", operation="ABSOLUTE"); L.new(nr.outputs["X"], ax.inputs[0])
    lat = n(nt, "ShaderNodeMapRange"); lat.inputs[1].default_value = 0.62; lat.inputs[2].default_value = 0.45; L.new(ax.outputs[0], lat.inputs[0])
    baixo = n(nt, "ShaderNodeMapRange"); baixo.inputs[1].default_value = -0.15; baixo.inputs[2].default_value = -0.40; L.new(nr.outputs["Z"], baixo.inputs[0])
    frente = n(nt, "ShaderNodeMapRange"); frente.inputs[1].default_value = -0.25; frente.inputs[2].default_value = -0.55; L.new(nr.outputs["Y"], frente.inputs[0])
    pesc = n(nt, "ShaderNodeMapRange"); pesc.inputs[1].default_value = -0.30; pesc.inputs[2].default_value = -0.42; L.new(pos.outputs["Y"], pesc.inputs[0])
    cab = n(nt, "ShaderNodeMapRange"); cab.inputs[1].default_value = -0.74; cab.inputs[2].default_value = -0.68; L.new(pos.outputs["Y"], cab.inputs[0])
    garg0 = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(frente.outputs[0], garg0.inputs[0]); L.new(pesc.outputs[0], garg0.inputs[1])
    garg = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(garg0.outputs[0], garg.inputs[0]); L.new(cab.outputs[0], garg.inputs[1])
    zb = n(nt, "ShaderNodeMath", operation="MAXIMUM"); L.new(baixo.outputs[0], zb.inputs[0]); L.new(garg.outputs[0], zb.inputs[1])
    nas_asas = n(nt, "ShaderNodeMapRange"); nas_asas.inputs[1].default_value = 0.095; nas_asas.inputs[2].default_value = 0.07
    axp = n(nt, "ShaderNodeMath", operation="ABSOLUTE"); L.new(pos.outputs["X"], axp.inputs[0]); L.new(axp.outputs[0], nas_asas.inputs[0])
    pernas = n(nt, "ShaderNodeMapRange"); pernas.inputs[1].default_value = 0.30; pernas.inputs[2].default_value = 0.36
    L.new(pos.outputs["Z"], pernas.inputs[0])                       # nao pinta a parte de baixo das patas
    vz0 = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(zb.outputs[0], vz0.inputs[0]); L.new(lat.outputs[0], vz0.inputs[1])
    vz1 = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(vz0.outputs[0], vz1.inputs[0]); L.new(nas_asas.outputs[0], vz1.inputs[1])
    ventre = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(vz1.outputs[0], ventre.inputs[0]); L.new(pernas.outputs[0], ventre.inputs[1])
    # placas transversais: ao longo do tronco seguem Y; no pescoco seguem o eixo inclinado do pescoco
    eix = n(nt, "ShaderNodeVectorMath", operation="DOT_PRODUCT"); eix.inputs[1].default_value = (0, 0.22, -0.975)    # pescoco quase vertical (S refinado)
    L.new(tc.outputs["Object"], eix.inputs[0])
    sel = n(nt, "ShaderNodeMix", data_type="FLOAT"); L.new(pesc.outputs[0], sel.inputs["Factor"])
    L.new(pos.outputs["Y"], sel.inputs[2]); L.new(eix.outputs["Value"], sel.inputs[3])
    onda = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(sel.outputs[0], onda.inputs[0]); onda.inputs[1].default_value = 2 * math.pi * 24
    sen = n(nt, "ShaderNodeMath", operation="SINE"); L.new(onda.outputs[0], sen.inputs[0])
    sulco = n(nt, "ShaderNodeMapRange"); sulco.inputs[1].default_value = -1.0; sulco.inputs[2].default_value = -0.86   # sulco fino e nitido (placas largas)
    L.new(sen.outputs[0], sulco.inputs[0])
    # placa abaulada: clara no meio, levemente mais escura nas bordas (le o volume de cada placa)
    meio_placa = mr(sen.outputs[0], -0.6, 1.0)
    marfim0 = rampa(nt, L, ruido.outputs["Fac"], [(0.3, (0.040, 0.031, 0.052, 1)), (0.7, (0.070, 0.055, 0.088, 1))])   # SOMBRIO: placas roxo-acinzentadas
    marfim = n(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); L.new(op("SUBTRACT", op("MULTIPLY", meio_placa, v=-1.0), v=-1.0), marfim.inputs["Factor"])
    L.new(marfim0.outputs["Color"], marfim.inputs[6]); marfim.inputs[7].default_value = (0.70, 0.62, 0.78, 1)
    placa = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(sulco.outputs[0], placa.inputs["Factor"])
    placa.inputs[6].default_value = (0.020, 0.012, 0.030, 1); L.new(marfim.outputs[2], placa.inputs[7])     # SOMBRIO: sulco escuro
    cor = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(ventre.outputs[0], cor.inputs["Factor"])
    L.new(esc.outputs[2], cor.inputs[6]); L.new(placa.outputs[2], cor.inputs[7])
    # dedos da asa mais claros (pessego)
    ded = n(nt, "ShaderNodeMapRange"); ded.inputs[1].default_value = 0.55; ded.inputs[2].default_value = 0.85; L.new(axp.outputs[0], ded.inputs[0])
    cor2 = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(ded.outputs[0], cor2.inputs["Factor"])
    L.new(cor.outputs[2], cor2.inputs[6]); cor2.inputs[7].default_value = (0.030, 0.016, 0.050, 1)   # SOMBRIO: ossos da asa escuros
    L.new(cor2.outputs[2], b.inputs["Base Color"])
    rg = n(nt, "ShaderNodeMapRange"); rg.inputs[3].default_value = 0.72; rg.inputs[4].default_value = 0.50; L.new(fr.outputs[0], rg.inputs[0])   # fosco natural
    # geada: pontos finos que brilham frio (moderado) -> rugosidade menor nesses pontos, nao plastico no resto
    geada = n(nt, "ShaderNodeTexNoise"); geada.inputs["Scale"].default_value = 520; L.new(tc.outputs["Object"], geada.inputs["Vector"])
    pontos = mr(geada.outputs["Fac"], 0.66, 0.74)
    rugf = op("SUBTRACT", rg.outputs[0], op("MULTIPLY", pontos, v=0.30))
    L.new(rugf, b.inputs["Roughness"])
    if "Coat Weight" in b.inputs:
        L.new(op("ADD", op("MULTIPLY", fr.outputs[0], v=0.10), v=0.03), b.inputs["Coat Weight"])   # SOMBRIO: verniz leve (reflexo das escamas)
        if "Coat Tint" in b.inputs: b.inputs["Coat Tint"].default_value = (0.62, 0.40, 1.0, 1)   # reflexo violeta
        if "Coat Roughness" in b.inputs: b.inputs["Coat Roughness"].default_value = 0.25
    # relevo: escamas (fora do ventre) + sulcos das placas (no ventre)
    alt_esc = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(fr.outputs[0], alt_esc.inputs[0])
    inv = n(nt, "ShaderNodeMath", operation="SUBTRACT"); inv.inputs[0].default_value = 1.0; L.new(ventre.outputs[0], inv.inputs[1])
    L.new(inv.outputs[0], alt_esc.inputs[1])
    alt_pl = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(op("MULTIPLY", sulco.outputs[0], op("ADD", op("MULTIPLY", meio_placa, v=0.5), v=0.5)), alt_pl.inputs[0]); L.new(ventre.outputs[0], alt_pl.inputs[1])
    alt_esc2 = n(nt, "ShaderNodeMath", operation="MULTIPLY"); L.new(ALT_ESC, alt_esc2.inputs[0]); L.new(inv.outputs[0], alt_esc2.inputs[1])
    alt = n(nt, "ShaderNodeMath", operation="ADD"); L.new(alt_esc2.outputs[0], alt.inputs[0]); L.new(alt_pl.outputs[0], alt.inputs[1])
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.004
    L.new(alt.outputs[0], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m
def mat_membrana():
    """membrana de gelo (refino): azul muito claro, translucida; veios finos ramificados que seguem cada setor (UV:
    U = setor + posicao entre os dedos, V = da base a borda); borda de fuga mais clara e fina; base junto aos ossos
    mais densa; textura organica leve (sem plastico)"""
    m, nt, b, L = mat("M_Dragao_Membrana")
    uv = n(nt, "ShaderNodeUVMap"); uv.uv_map = "UVMembrana"
    sp = n(nt, "ShaderNodeSeparateXYZ"); L.new(uv.outputs["UV"], sp.inputs[0])
    tc = n(nt, "ShaderNodeTexCoord")
    def op(o_, a, b_=None, v=None):
        x = n(nt, "ShaderNodeMath", operation=o_); L.new(a, x.inputs[0])
        if b_ is not None: L.new(b_, x.inputs[1])
        if v is not None: x.inputs[1].default_value = v
        return x.outputs[0]
    def mr(ent, a, b_, c=0.0, d=1.0):
        x = n(nt, "ShaderNodeMapRange"); x.inputs[1].default_value = a; x.inputs[2].default_value = b_
        x.inputs[3].default_value = c; x.inputs[4].default_value = d; L.new(ent, x.inputs[0]); return x.outputs[0]
    fracu = op("FRACT", sp.outputs["X"])
    # veios principais: 2 por setor, ondulados por ruido; secundarios via voronoi esticado ao longo de V
    rn = n(nt, "ShaderNodeTexNoise"); rn.inputs["Scale"].default_value = 6; L.new(tc.outputs["Object"], rn.inputs["Vector"])
    # REFINO FINAL (membrana limpa): veios suaves e pouco ondulados, grossos na base e afinando ate sumir antes da borda;
    # um veio secundario fraco por setor; sem a rede de rachaduras do Voronoi
    ond = op("ADD", fracu, op("MULTIPLY", op("SUBTRACT", rn.outputs["Fac"], v=0.5), v=0.035))
    larg = mr(sp.outputs["Y"], 0.0, 1.0, 0.020, 0.005); some = mr(sp.outputs["Y"], 0.95, 0.70)
    def veio(centro, forca):
        x = n(nt, "ShaderNodeMapRange"); x.inputs[1].default_value = 0.0; x.inputs[3].default_value = 1.0; x.inputs[4].default_value = 0.0
        L.new(op("ABSOLUTE", op("SUBTRACT", ond, v=centro)), x.inputs[0]); L.new(larg, x.inputs[2])
        return op("MULTIPLY", op("POWER", x.outputs[0], v=1.5), op("MULTIPLY", some, v=forca))
    veios = op("MAXIMUM", op("MAXIMUM", veio(0.36, 1.0), veio(0.70, 0.85)), op("MULTIPLY", veio(0.53, 0.35), mr(sp.outputs["Y"], 0.3, 0.6)))
    borda = mr(sp.outputs["Y"], 0.86, 1.0)                                   # borda de fuga (r8: aro de gelo mais fino e nitido)
    base_ = mr(sp.outputs["Y"], 0.18, 0.0)                                   # junto ao braco/dedos
    grao = n(nt, "ShaderNodeTexNoise"); grao.inputs["Scale"].default_value = 60; grao.inputs["Detail"].default_value = 4; L.new(tc.outputs["Object"], grao.inputs["Vector"])
    cor0 = rampa(nt, L, grao.outputs["Fac"], [(0.35, (0.014, 0.004, 0.032, 1)), (0.65, (0.030, 0.008, 0.068, 1))])   # SOMBRIO: purpura escuro
    c1 = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(op("MULTIPLY", base_, v=0.6), c1.inputs["Factor"])
    L.new(cor0.outputs["Color"], c1.inputs[6]); c1.inputs[7].default_value = (0.010, 0.004, 0.018, 1)   # base junto aos ossos quase preta
    c2 = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(op("MULTIPLY", veios, v=0.88), c2.inputs["Factor"])
    L.new(c1.outputs[2], c2.inputs[6]); c2.inputs[7].default_value = (0.075, 0.025, 0.16, 1)   # veios violeta
    c3 = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(op("MULTIPLY", borda, v=0.80), c3.inputs["Factor"])
    L.new(c2.outputs[2], c3.inputs[6]); c3.inputs[7].default_value = (0.012, 0.005, 0.022, 1)   # borda de fuga escura
    L.new(c3.outputs[2], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.42
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.15
    tr = n(nt, "ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = (0.30, 0.06, 0.62, 1)   # contra a luz: violeta
    mx = n(nt, "ShaderNodeMixShader")
    L.new(mr(op("ADD", borda, op("MULTIPLY", base_, v=-0.6)), 0.0, 1.0, 0.22, 0.40), mx.inputs[0])   # SOMBRIO: translucidez moderada
    out = nt.nodes["Material Output"]; L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs[0])
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.45; bp.inputs["Distance"].default_value = 0.003   # r8: veios legiveis
    L.new(op("ADD", veios, op("MULTIPLY", grao.outputs["Fac"], v=0.12)), bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
    return m
def mat_marfim(nome, base, ponta, rug, comp):
    m, nt, b, L = mat(nome)
    tc = n(nt, "ShaderNodeTexCoord")
    # gradiente base -> ponta pela distancia ate a origem do objeto (a base da peca)
    dist = n(nt, "ShaderNodeVectorMath", operation="LENGTH"); L.new(tc.outputs["Object"], dist.inputs[0])
    mx_ = n(nt, "ShaderNodeMapRange"); mx_.inputs[2].default_value = comp; L.new(dist.outputs["Value"], mx_.inputs[0])
    an = n(nt, "ShaderNodeTexWave"); an.inputs["Scale"].default_value = 30; an.inputs["Distortion"].default_value = 2
    L.new(tc.outputs["Object"], an.inputs["Vector"])
    gr = rampa(nt, L, mx_.outputs[0], [(0.0, base), (1.0, ponta)])
    L.new(gr.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rug
    bp = n(nt, "ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25; L.new(an.outputs["Fac"], bp.inputs["Height"])
    L.new(bp.outputs[0], b.inputs["Normal"]); return m
def mat_cristal(nome, base, ponta, comp, aneis=30):
    """chifre/garra de gelo (refino): gradiente base azul -> ponta branca, aneis de crescimento, brilho frio e um pouco
    de transmissao (levemente cristalino, sem virar vidro)"""
    m = mat_marfim(nome, base, ponta, 0.28, comp)
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    for k, v in (("Transmission Weight", 0.0), ("Coat Weight", 0.45), ("Coat Roughness", 0.18), ("Specular IOR Level", 0.55),
                 ("Coat Tint", (0.62, 0.40, 1.0, 1))):   # SOMBRIO: queratina escura (sem gelo translucido)
        if k in b.inputs: b.inputs[k].default_value = v
    for x in nt.nodes:
        if x.bl_idname == "ShaderNodeTexWave": x.inputs["Scale"].default_value = aneis
    return m
def mat_espinho():
    m, nt, b, L = mat("M_Dragao_Espinho")
    tc = n(nt, "ShaderNodeTexCoord"); sep = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sep.inputs[0])
    gr = rampa(nt, L, sep.outputs["Z"], [(0.0, (0.018, 0.010, 0.028, 1)), (0.6, (0.040, 0.022, 0.065, 1)), (1.0, (0.070, 0.040, 0.110, 1))])
    L.new(gr.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.22
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.4
    if "Coat Tint" in b.inputs: b.inputs["Coat Tint"].default_value = (0.62, 0.40, 1.0, 1)
    return m
def mat_olho():
    """olho glacial (refino): iris radial azul-gelo com fibras, centro claro, aro limbal escuro, pupila em fenda
    vertical, cornea com verniz (reflexo vivo) e brilho frio contido (sem olho de desenho)"""
    m, nt, b, L = mat("M_Dragao_Olho")
    tc = n(nt, "ShaderNodeTexCoord"); sep = n(nt, "ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sep.inputs[0])
    def op(o_, a, b_=None, v=None):
        x = n(nt, "ShaderNodeMath", operation=o_); L.new(a, x.inputs[0])
        if b_ is not None: L.new(b_, x.inputs[1])
        if v is not None: x.inputs[1].default_value = v
        return x.outputs[0]
    def mr(ent, a, b_, c=0.0, d=1.0):
        x = n(nt, "ShaderNodeMapRange"); x.inputs[1].default_value = a; x.inputs[2].default_value = b_
        x.inputs[3].default_value = c; x.inputs[4].default_value = d; L.new(ent, x.inputs[0]); return x.outputs[0]
    dy = op("SUBTRACT", sep.outputs["Y"], v=0.5); dz = op("SUBTRACT", sep.outputs["Z"], v=0.5)
    r = op("SQRT", op("ADD", op("MULTIPLY", dy, dy), op("MULTIPLY", dz, dz)))
    ang = op("ARCTAN2", dz, dy)
    fib = n(nt, "ShaderNodeTexNoise"); fib.inputs["Scale"].default_value = 3.0
    cmb = n(nt, "ShaderNodeCombineXYZ"); L.new(op("MULTIPLY", ang, v=8.0), cmb.inputs[0]); L.new(op("MULTIPLY", r, v=4.0), cmb.inputs[1]); L.new(cmb.outputs[0], fib.inputs["Vector"])
    iris = rampa(nt, L, mr(r, 0.0, 0.5), [(0.0, (1.0, 0.78, 0.22, 1)), (0.35, (0.98, 0.45, 0.03, 1)), (0.75, (0.55, 0.12, 0.0, 1)), (1.0, (0.06, 0.01, 0.0, 1))])   # SOMBRIO: ambar
    vfib = n(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); vfib.inputs["Factor"].default_value = 0.45
    L.new(iris.outputs["Color"], vfib.inputs[6]); L.new(fib.outputs["Color"], vfib.inputs[7])
    pup = mr(op("ABSOLUTE", dy), 0.025, 0.045)                               # fenda vertical
    pup2 = op("MAXIMUM", pup, mr(op("ABSOLUTE", dz), 0.30, 0.36))           # a fenda nao passa do centro da iris
    cor = n(nt, "ShaderNodeMix", data_type="RGBA"); L.new(pup2, cor.inputs["Factor"])
    cor.inputs[6].default_value = (0.002, 0.004, 0.01, 1); L.new(vfib.outputs[2], cor.inputs[7])
    L.new(cor.outputs[2], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.2
    for k, v in (("Coat Weight", 1.0), ("Coat Roughness", 0.02)):
        if k in b.inputs: b.inputs[k].default_value = v
    b.inputs["Emission Color"].default_value = (1.0, 0.48, 0.05, 1)
    L.new(op("MULTIPLY", op("MULTIPLY", pup2, mr(r, 0.45, 0.15)), v=1.1), b.inputs["Emission Strength"])   # r2: brilho glacial
    return m
MC, MM, ME, MO = mat_corpo(), mat_membrana(), mat_espinho(), mat_olho()
MH = mat_cristal("M_Dragao_Chifre", (0.022, 0.012, 0.032, 1), (0.075, 0.045, 0.110, 1), 0.38, 55)   # SOMBRIO: quase preto, aneis de queratina
MG = mat_cristal("M_Dragao_Garra", (0.018, 0.010, 0.026, 1), (0.060, 0.035, 0.090, 1), 0.08, 60)
MD = mat_cristal("M_Dragao_Dente", (0.42, 0.37, 0.34, 1), (0.78, 0.74, 0.68, 1), 0.02, 80)   # SOMBRIO: dentes marfim sujo
ob.data.materials.append(MC)
for o in MEMB: o.data.materials.append(MM)
for o in CHIFRES: o.data.materials.append(MH)
# (crista do focinho: as gotas soltas viraram escudos esculpidos na pele -- refino final)
for s in (1, -1):                                                                          # pontas da sobrancelha
    for k in range(2):                                                                     # (refino final: finas, varridas)
        b0 = V((0.046 * s, -0.800 + 0.022 * k, 0.792 - 0.004 * k))
        ESPINHOS.append(tubo([b0, b0 + V((0.010 * s, 0.020, 0.010)), b0 + V((0.017 * s, 0.036, 0.018)), b0 + V((0.021 * s, 0.047, 0.023))],   # R3: mais curto e erguido (giro lateral)
                             0.0058, "Espinho_Sobrancelha", 1.6))
    for k in range(3):                    # r8: espinhos SUPERIORES do cranio (entre a coroa e a linha media, para tras)
        b0 = V((0.024 * s, -0.792 + 0.022 * k, 0.808 - 0.003 * k))
        ESPINHOS.append(tubo(arco(b0, (0.15 * s, 0.55, 1.0), (0.10 * s, 1.0, 0.35), 0.026 + 0.006 * k, 4), 0.0042, "Espinho_Sobrancelha", 1.5))
for o in CHIFRES + OLHOS + [e for e in ESPINHOS if e.name.split(".")[0] in ("Espinho_Bochecha", "Espinho_Sobrancelha")]:
    para_cabeca(o)
for e in ESPINHOS:
    if e.name.startswith("Espinho_Dorsal"): e.location = cabeca(e.location)
CENTRO_CAB = cabeca(V((0, -0.80, 0.745)), 1.0)
def encaixar(o, dirv, fundo):
    """leva a base (origem) da peca ate a pele ao longo de dirv e afunda um pouco para dentro"""
    dirv = dirv.normalized(); ini = o.location - dirv * 0.25
    ok, hit, nrm, _ = ob.ray_cast(ini, dirv, distance=0.6)
    if ok: o.location = hit + dirv * fundo
    return ok
falhas = 0
for o in CHIFRES + [e for e in ESPINHOS if not e.name.startswith("Espinho_Dorsal")]:
    falhas += not encaixar(o, CENTRO_CAB - o.location, 0.010 if o in CHIFRES else 0.005)
print("DRAGAO_ENCAIXE cabeca falhas", falhas)
# chifres e cristas integrados (refino final): cada chifre nasce de uma base ossea elevada na pele, as bases da coroa
# ligadas por uma crista baixa ate o chifre principal; espinhos da bochecha/sobrancelha com raiz discreta
def realce_pele(centros, segs, alt, raio):
    for v in ob.data.vertices:
        p = v.co
        if p.y > -0.55: continue
        h = 0.0
        for c, a, r in centros:
            d = (p - c).length
            if d < r * 2.5: h = max(h, a * math.exp(-(d / r) ** 2))
        for a_, b_ in segs:
            ab = b_ - a_; t = max(0.0, min(1.0, (p - a_).dot(ab) / ab.length_squared)); d = (p - (a_ + ab * t)).length
            if d < raio * 2.5: h = max(h, alt * math.exp(-(d / raio) ** 2) * math.sin(math.pi * (0.25 + 0.5 * t)))
        if h > 0: p += v.normal * h
    ob.data.update()
K = K_CAB; centros, segs = [], []
for o in CHIFRES: centros.append((o.location.copy(), (0.008 if o.name.split(".")[0] == "Chifre" else 0.005) * K, 0.016 * K))
for e in ESPINHOS:
    if e.name.split(".")[0] in ("Espinho_Bochecha", "Espinho_Sobrancelha"): centros.append((e.location.copy(), 0.0025 * K, 0.007 * K))
for s in (1, -1):
    lado_ = sorted([o.location.copy() for o in CHIFRES if o.location.x * s > 0], key=lambda c: c.y)
    segs += [(a, b) for a, b in zip(lado_, lado_[1:])]
realce_pele(centros, segs, 0.004 * K, 0.008 * K)
# R3: ramos do chifre principal (2 por chifre, saem para tras/fora e curvam para cima) -- seguem o chifre ja encaixado
for s in (1, -1):
    pts_, delta = ARCO_PRINC[s], PRINC[s].location - ARCO_PRINC[s][0]
    for k_, comp, r0 in ():                                  # SOMBRIO: chifre liso, sem ramos
        o = tubo(arco(pts_[k_] + delta, (0.55 * s, 0.55, 0.70), (0.25 * s, 1.0, 0.45), comp, 5), r0, "Chifre_Ramo", 1.35)
        o.data.materials.append(MH); CHIFRES.append(o)
# dentes (refino final): fileira regular no labio superior (presa maior na 2a posicao) e presas inferiores menores que
# sobem por fora do labio, alternadas; base achada por raio na pele ja na escala final, afundada na gengiva
def dente(s, yy, zrel, comp, r0, sobe):
    alvo = cabeca(V((0.0, yy, 0.704 + (yy + 0.95) * 0.07 + zrel)), 1.0)
    ok, hit, _, _ = ob.ray_cast(V((0.4 * s, alvo.y, alvo.z)), V((-s, 0, 0)))
    if not ok: return
    b0 = hit - V((0.0045 * K * s, 0, 0)); c = comp * K; sz = 1 if sobe else -1
    o = tubo([b0, b0 + V((0.0018 * s, -0.001, sz * c * 0.55)), b0 + V((0.0012 * s, -0.003, sz * c))], r0 * K, "Dente_Inf" if sobe else "Dente_Sup", 1.5)
    o.data.materials.append(MD); DENTES.append(o)
for s in (1, -1):
    for k, (yy, comp) in enumerate(((-0.924, 0.010), (-0.902, 0.018), (-0.880, 0.011), (-0.858, 0.010), (-0.836, 0.009), (-0.814, 0.008), (-0.793, 0.006))):
        dente(s, yy, 0.002, comp * 1.25, 0.0046 if k == 1 else 0.0034, False)
    for yy, comp in ((-0.913, 0.011), (-0.869, 0.008), (-0.825, 0.007)):
        dente(s, yy, -0.004, comp, 0.0032, True)
print("DRAGAO_DENTES", len(DENTES))
ob.data.transform(Matrix.Translation(OFF)); ob.data.update()        # volta ao lugar
for o in CHIFRES + OLHOS + DENTES + BOCA + [e for e in ESPINHOS if not e.name.startswith("Espinho_Dorsal")]: o.location += OFF
ob["mandibula_eixo"] = tuple(cabeca(V((0.0, -0.735, 0.712)), 1.0) + OFF)            # dobradica da mandibula (teste / rig)
for e in ESPINHOS:
    if e.name.startswith("Espinho_Dorsal"):
        falhas += not encaixar(e, ENC_DORSAL.get(e.name, V((0, 0, -1))), 0.004)
print("DRAGAO_ENCAIXE falhas", falhas)
# R3: espinhos dorsais nascem da pele -- cada base ganha um colar elevado e uma crista baixa liga as bases (nao parece
# peca colada); KD-tree para nao percorrer o corpo inteiro por espinho
from mathutils import kdtree
kd = kdtree.KDTree(len(ob.data.vertices))
for k_, v in enumerate(ob.data.vertices): kd.insert(v.co, k_)
kd.balance(); desl = {}
DORS = [e for e in ESPINHOS if e.name.startswith("Espinho_Dorsal_") and "Cauda" not in e.name]
for e in DORS:
    a = e["alt"]; rr = 0.009 + a * 0.22
    for co, k_, d in kd.find_range(e.location, rr * 2.2): desl[k_] = max(desl.get(k_, 0.0), (0.0015 + a * 0.06) * math.exp(-(d / rr) ** 2))
for e1, e2 in zip(DORS, DORS[1:]):
    L_ = (e2.location - e1.location).length
    for j in range(int(L_ / 0.005) + 1):
        c = e1.location.lerp(e2.location, j * 0.005 / max(L_, 1e-6))
        for co, k_, d in kd.find_range(c, 0.012): desl[k_] = max(desl.get(k_, 0.0), 0.0022 * math.exp(-(d / 0.006) ** 2))
for k_, h in desl.items(): ob.data.vertices[k_].co += ob.data.vertices[k_].normal * h
ob.data.update()
def mat_boca():
    """interior (r8): labio/gengiva azul-violeta palido -> ceu e assoalho rosados frios -> garganta escura (atributo boca_k)"""
    m, nt, b, L = mat("M_Dragao_Boca")
    at = n(nt, "ShaderNodeAttribute"); at.attribute_name = "boca_k"
    r = rampa(nt, L, at.outputs["Fac"], [(0.15, (0.16, 0.07, 0.14, 1)), (0.45, (0.30, 0.07, 0.12, 1)), (0.8, (0.10, 0.02, 0.05, 1)), (1.0, (0.02, 0.005, 0.012, 1))])
    L.new(r.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.30
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.35       # umido
    return m
MBOCA = mat_boca(); ob.data.materials.append(MBOCA)
ML, _, bl_, _ = mat("M_Dragao_Lingua"); bl_.inputs["Base Color"].default_value = (0.30, 0.07, 0.14, 1); bl_.inputs["Roughness"].default_value = 0.28
BOCA_INF.data.materials.append(ML)
for o in ESPINHOS: o.data.materials.append(ME)
for o in GARRAS: o.data.materials.append(MG)
for o in OLHOS: o.data.materials.append(MO)
col = bpy.data.collections.new("SB_Dragao"); sc.collection.children.link(col)
for o in [ob] + MEMB + CHIFRES + ESPINHOS + GARRAS + OLHOS + DENTES + BOCA:
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o)
dg = bpy.context.evaluated_depsgraph_get()
print("DRAGAO_POLIGONOS", sum(len(o.evaluated_get(dg).data.polygons) for o in col.objects if o.type == "MESH"), "corpo", len(ob.data.polygons))

# ------------------------------------------------------------------ cena de revisao
w = bpy.data.worlds.new("Ceu"); sc.world = w
if w.node_tree is None: w.use_nodes = True
bg = w.node_tree.nodes["Background"]; ceu = w.node_tree.nodes.new("ShaderNodeTexSky")
for t in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA", "HOSEK_WILKIE"):
    try: ceu.sky_type = t; break
    except Exception: pass
if hasattr(ceu, "sun_elevation"): ceu.sun_elevation = math.radians(30)
w.node_tree.links.new(ceu.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.10   # ceu fraco: nao tinge de azul
for nome, en, cor, rot in (("Sol", 6.0, (1.0, 0.97, 0.94), (math.radians(50), 0, math.radians(30))),
                           ("Contra", 4.5, (0.92, 0.90, 1.0), (math.radians(115), 0, math.radians(200))),
                           ("Preench", 1.2, (0.88, 0.94, 1.0), (math.radians(60), 0, math.radians(-120)))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.color = cor; lo = bpy.data.objects.new(nome, l)
    sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=40); chao = bpy.context.object
mch, _, bch, _ = mat("Chao"); bch.inputs["Base Color"].default_value = (0.42, 0.42, 0.43, 1); bch.inputs["Roughness"].default_value = 0.95
chao.data.materials.append(mch)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 64
for k, v in (("use_raytracing", True), ("use_shadows", True)):
    if hasattr(sc.eevee, k): setattr(sc.eevee, k, v)
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
camd = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", camd); sc.collection.objects.link(cam); sc.camera = cam
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "SB_Dragao_master.blend"))
if "sem_render" not in ARGS:
    VISTAS = [("34_frente", V((-2.4, -3.6, 1.3)), V((0, -0.15, 0.5)), 42), ("lado", V((-6.4, 0.55, 0.85)), V((0, 0.55, 0.6)), 42),
              ("frente", V((0, -5.2, 1.0)), V((0, 0, 0.6)), 42), ("34_tras", V((2.9, 3.4, 2.0)), V((0, 0.1, 0.55)), 42),
              ("cima", V((0.01, 0.3, 6.2)), V((0, 0.3, 0.4)), 42), ("cabeca", O((-0.85, -1.75, 1.02)), O((0, -0.82, 0.77)), 62),
              ("conceito", V((-1.6, -2.3, 0.62)), V((0, -0.2, 0.62)), 35),
              # closes do refino: olho/rosto, asa (membrana e ossos), escamas do pescoco/ombro/peito
              ("olho", O((-0.42, -1.12, 0.86)), O((0.03, -0.85, 0.79)), 85), ("asa_perto", V((-1.55, -0.95, 1.75)), V((-1.05, -0.05, 0.86)), 40),
              ("escamas", V((-0.62, -0.78, 0.70)), V((-0.08, -0.36, 0.56)), 50), ("peito_pescoco", V((-0.35, -1.45, 0.55)), V((0, -0.50, 0.80)), 40),
              ("ref", V((2.3, -3.3, 1.45)), V((0, -0.05, 0.72)), 40),
              ("uniao_ombro", V((-1.05, -0.95, 0.58)), V((-0.12, -0.30, 0.40)), 40), ("uniao_quadril", V((-1.05, 0.80, 0.58)), V((-0.13, 0.20, 0.38)), 40),
              ("uniao_pescoco", V((-0.95, -1.20, 0.86)), V((-0.03, -0.48, 0.66)), 38),
              ("cauda", V((-0.75, 1.45, 0.62)), V((0, 1.80, 0.30)), 45), ("pata", V((-0.75, -0.95, 0.25)), V((-0.15, -0.30, 0.10)), 45),
              ("pescoco", V((-0.95, -0.10, 1.20)), V((0, -0.55, 0.90)), 40), ("boca", O((-0.55, -1.05, 0.70)), O((0, -0.86, 0.72)), 60)]                                # angulo parecido com o da referencia
    for o in MEMB: o.visible_shadow = False         # r9: revisao da FORMA sem a faixa de sombra das asas abertas
    for nome, pos, alvo, lente in VISTAS:
        cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
        sc.render.filepath = os.path.join(OUT, "vista_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("DRAGAO_OK")
