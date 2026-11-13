"""Lote 7 (13/11/2026): BOCA FECHADA por padrao e abertura natural so onde a acao pede (pedido do usuario: "todas as
animacoes com a boca aberta; quando ruge/morde a boca simplesmente abre e faz uma curva; so abrir em animacoes que
precisam, como comer ou morder").
Achados (review/boca/r0_prancha.jpg):
- o modelo tem a boca ENTREABERTA com a mandibula a 0 graus; fechada = +18 graus em X local (memoria do L5). Quase todos
  os clipes deixam ~0 -> boca entreaberta o tempo todo;
- roar/Ameaca abriam -47 e bite -38 A PARTIR da boca ja aberta (~65 graus no total): a mandibula caia na vertical;
- bocejo do Espreguicar, mordiscadas do AlisarAsa e Sacudir giravam para o lado de FECHAR (+31/+9/+5 local), entrando
  no cranio.
Regra: mandibula = +18 (fechada) - abertura(t); abertura(t) = curva do clipe original normalizada para o maximo da
tabela ABRE (graus a partir da boca fechada). Movimentos pequenos (respiracao, ate 3-4 graus) somem. Os demais ossos e
as outras actions nao mudam. Entrada: Wyvern_E7_clipes_L6.blend (preservado); saida: Wyvern_E7_clipes_L7.blend.
Uso: blender -b Wyvern_E7_clipes_L6.blend -P build/23_boca_fechada.py -- <saida.blend>"""
import bpy, sys, math, mathutils, json, os
SAIDA = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
FECHADA = 18.0
# abertura maxima (graus a partir da boca fechada) e de onde vem a curva: "neg" = excursao negativa do clipe original
# (abrir no sentido certo), "pos" = excursao positiva (lote 5 com sinal trocado)
# r2 (13/11): 34/30/24 ainda pareciam escancarados (a mandibula do modelo e fina e comprida) -> valores menores
ABRE = {"roar": (26, "neg"), "Ameaca": (26, "neg"), "bite": (24, "neg"), "Comer": (18, "neg"), "AgarrarPresa": (16, "neg"),
        "GuardaNinho": (14, "neg"), "Morte": (12, "neg"), "ReacaoGolpe": (10, "neg"), "FerraoAtaque": (8, "neg"),
        "Espreguicar": (22, "pos"), "AlisarAsaEsquerda": (8, "pos"), "AlisarAsaDireita": (8, "pos")}
LIMIAR = {"neg": 3.5, "pos": 2.0}            # descarta respiracao/ruido antes de normalizar
A = bpy.data.objects["Wyvern_Rig"]; sc = bpy.context.scene; pb = A.pose.bones["jaw"]
DP = 'pose.bones["jaw"].rotation_quaternion'

def fcurves(act):
    for ly in act.layers:
        for st in ly.strips:
            cb = st.channelbag(act.slots[0])
            if cb: return cb
    return None

relatorio = {}
for act in list(bpy.data.actions):
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = [int(round(x)) for x in act.frame_range]
    xs = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f); xs.append(math.degrees(pb.matrix_basis.to_euler("XYZ").x))
    alvo, modo = ABRE.get(act.name, (0, None))
    if modo == "neg": bruto = [max(0.0, -x - LIMIAR["neg"]) for x in xs]
    elif modo == "pos": bruto = [max(0.0, x - LIMIAR["pos"]) for x in xs]
    else: bruto = [0.0] * len(xs)
    mx = max(bruto) or 1.0
    novo = [FECHADA - alvo * b / mx for b in bruto]
    cb = fcurves(act)
    for fc in [fc for fc in cb.fcurves if fc.data_path == DP]: cb.fcurves.remove(fc)
    fcs = [cb.fcurves.new(DP, index=i) for i in range(4)]
    for k, f in enumerate(range(f0, f1 + 1)):
        q = mathutils.Euler((math.radians(novo[k]), 0, 0)).to_quaternion()
        for i in range(4): fcs[i].keyframe_points.insert(f, q[i], options={"FAST"})
    for fc in fcs:
        for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
        fc.update()
    relatorio[act.name] = {"antes_min": round(min(xs), 1), "antes_max": round(max(xs), 1),
                           "depois_min": round(min(novo), 1), "depois_max": round(max(novo), 1)}
    print("BOCA %-20s antes %6.1f..%6.1f  depois %6.1f..%6.1f" % (act.name, min(xs), max(xs), min(novo), max(novo)))
A.animation_data.action = bpy.data.actions["idle_loop"]; A.animation_data.action_slot = bpy.data.actions["idle_loop"].slots[0]
bpy.ops.wm.save_as_mainfile(filepath=SAIDA, copy=True)
json.dump(relatorio, open(os.path.join(os.path.dirname(SAIDA), "review", "boca", "boca_L7.json"), "w"), indent=1)
print("L7_OK", SAIDA)
