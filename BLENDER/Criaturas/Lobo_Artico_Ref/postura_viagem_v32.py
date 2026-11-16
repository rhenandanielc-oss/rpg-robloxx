"""v32: POSTURA DE VIAGEM (auditoria contra lobos reais, 11/11/2026: o lobo se desloca com a cabeca no nivel do dorso - Heptner &
Naumov - e cauda neutra ~45 graus abaixo do dorso - etograma IWC; o nosso trotava com a cabeca 0,95 acima da cernelha e a cauda ~70 graus).
Pos-processo sobre a anim_v31, so nos ossos Pescoco1, Pescoco2, Cabeca e Cauda1..Cauda4 (nenhum osso de perna: apoios inalterados por
construcao). Giro em torno do eixo X do corpo na cabeca de cada osso (+ = abaixa o que aponta para a frente / ergue o que aponta para tras),
em cadeia: Pescoco1 a1, Pescoco2 a2, Cabeca c (compensa para o focinho nao apontar para o chao); Cauda1 t1, Cauda2 t2.
Peso por acao: Trote 1, Andar 0,5, Corrida cabeca 0,7 / cauda 1; Repouso e viradas 0. Transicoes: peso = mistura gravada (s_por_quadro,
com o mesmo atraso da v28: cabeca 0,08 s, cauda 0,14 s) entre origem e destino; Arrancada/Frenagem: peso da Corrida x v/v_corrida.
As pontas ficam iguais as marchas vizinhas (pesos iguais nas pontas) e os lacos continuam lacos.
Uso: blender -b anim_v31/CR_LoboArtico_Anim.blend -P postura_viagem_v32.py -- <dir_saida>"""
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V
import marcha_v21 as M
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
PAR = {"a1": 14.0, "a2": 9.0, "c": -12.0, "t1": 15.0, "t2": 5.0, "peso_cabeca": {"Andar": 0.5, "Trote": 1.0, "Corrida": 0.7}, "peso_cauda": {"Andar": 0.5, "Trote": 1.0, "Corrida": 1.0},
       "atraso_cabeca_s": 0.08, "atraso_cauda_s": 0.14}
if os.environ.get("AJUSTE_V32"): PAR.update(json.loads(os.environ["AJUSTE_V32"]))
ARM = M.ARM; P = M.P; sc = bpy.context.scene; FPS = 30
TJ = {}
for fn in ("marchas_v29.json", "transicoes_v25.json"):
    for k, v in json.load(open(os.path.join(SRC, fn)))["acoes"].items(): TJ[k] = v
VCOR = json.load(open(os.path.join(SRC, "transicoes_v25.json")))["v_corrida"]
def s_atrasado(lst, q, atraso):
    x = q - atraso * FPS
    if x <= 0: return lst[0]
    i0 = int(math.floor(x)); i1 = min(len(lst) - 1, i0 + 1); return lst[i0] + (lst[i1] - lst[i0]) * (x - i0)
def pesos(ac, q):
    """(peso_cabeca, peso_cauda) no quadro q da acao"""
    if ac in PAR["peso_cabeca"]: return PAR["peso_cabeca"][ac], PAR["peso_cauda"][ac]
    if ac in TJ and "origem" in TJ[ac]:
        A = TJ[ac]; o, d = A["origem"], A["destino"]; sl = A["s_por_quadro"]
        sh = s_atrasado(sl, q, PAR["atraso_cabeca_s"]); st = s_atrasado(sl, q, PAR["atraso_cauda_s"])
        return (PAR["peso_cabeca"][o] + (PAR["peso_cabeca"][d] - PAR["peso_cabeca"][o]) * sh, PAR["peso_cauda"][o] + (PAR["peso_cauda"][d] - PAR["peso_cauda"][o]) * st)
    if ac in ("Arrancada", "Frenagem"):
        vl = [v / VCOR for v in TJ[ac]["v_por_quadro"]]
        return PAR["peso_cabeca"]["Corrida"] * s_atrasado(vl, q, PAR["atraso_cabeca_s"]), PAR["peso_cauda"]["Corrida"] * s_atrasado(vl, q, PAR["atraso_cauda_s"])
    return 0.0, 0.0
def girar(osso, graus):
    pb = P[osso]; h = pb.head.copy(); pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, "X") @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()
OSSOS = ["Pescoco1", "Pescoco2", "Cabeca", "Cauda1", "Cauda2", "Cauda3", "Cauda4"]; REL = {"parametros": PAR, "acoes": {}}
for pb in P: pb.rotation_mode = "QUATERNION"
for acn in [a for a in bpy.data.actions if not a.name.startswith("Teste")]:
    ARM.animation_data.action = acn
    if len(acn.slots): ARM.animation_data.action_slot = acn.slots[0]
    f0, f1 = (int(x) for x in acn.frame_range); NOVOS = []; PW = []
    for q in range(f0, f1 + 1):
        ARM.animation_data.action = acn; sc.frame_set(q); bpy.context.view_layer.update()
        orig = {n: P[n].rotation_quaternion.copy() for n in OSSOS}; wc, wt = pesos(acn.name, q - f0); PW.append((round(wc, 4), round(wt, 4)))
        base = {pb.name: pb.matrix.copy() for pb in P}; ARM.animation_data.action = None
        for pb in P: pb.matrix = base[pb.name]
        bpy.context.view_layer.update()
        if wc > 1e-6:
            girar("Pescoco1", PAR["a1"] * wc); girar("Pescoco2", PAR["a2"] * wc); girar("Cabeca", PAR["c"] * wc)
        if wt > 1e-6:
            girar("Cauda1", PAR["t1"] * wt); girar("Cauda2", PAR["t2"] * wt)
        r = {}
        for n in OSSOS:
            qn = P[n].rotation_quaternion.copy()
            if qn.dot(orig[n]) < 0: qn = -qn
            r[n] = qn
        NOVOS.append(r)
    if max(max(p) for p in PW) > 1e-6:
        cb = acn.layers[0].strips[0].channelbag(acn.slots[0])
        for n in OSSOS:
            for i in range(4):
                fc = cb.fcurves.find('pose.bones["%s"].rotation_quaternion' % n, index=i)
                kp = {int(round(p.co.x)): p for p in fc.keyframe_points}
                for qi, q in enumerate(range(f0, f1 + 1)):
                    if q in kp: p = kp[q]; p.co.y = NOVOS[qi][n][i]; p.handle_left_type = "AUTO_CLAMPED"; p.handle_right_type = "AUTO_CLAMPED"
                fc.update()
    ARM.animation_data.action = None
    for pb in P: pb.matrix_basis.identity()
    REL["acoes"][acn.name] = {"peso_cabeca_cauda_por_quadro": PW, "peso_max": [max(p[0] for p in PW), max(p[1] for p in PW)]}
    print("V32", acn.name, REL["acoes"][acn.name]["peso_max"], "pontas", PW[0], PW[-1], flush=True)
ARM.animation_data.action = bpy.data.actions["Andar"]
json.dump(REL, open(os.path.join(OUT, "postura_viagem_v32.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("POSTURA_VIAGEM_V32_OK", flush=True)
