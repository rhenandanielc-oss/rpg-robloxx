# Correcao do Comer (lote 2), SO esta action; parte de Wyvern_E7_clipes_L2b.blend e usa 08_base.py sem alterar.
# M0 (13a_m0_comer.py): a cabeca/mandibula NAO afundam (z min 0,22); afundam o pe ESQUERDO (ate -0,136 em 55 de 91
# quadros: o agachamento da v1 prendia so bola e ponta do pe e deixava o jarrete livre, e a IK girava o pe) e a ponta da
# cauda (ate -0,057 no balanco mais baixo, com o corpo 1,5 stud abaixo).
# Correcao: agachamento leva o JARRETE ao ponto do idle (coxa em 2 eixos + canela) e copia a orientacao de mundo do pe
# e do dedo do idle (o pe fica identico ao idle; a dobra fica so em coxa/canela) e a base da cauda sobe o minimo para a ponta ficar >= 0,06 no ciclo todo. Pescoco, cabeca, asas,
# mordida/puxao e tempos = v1 (angulos do manifesto_L2.json).
# Uso: blender -b Wyvern_E7_clipes_L2b.blend -P 13_comer_v2.py -- <08_base.py> <manifesto_L2.json> <saida.blend> <manifesto_saida.json>
import bpy, sys, math, json
argv = sys.argv[sys.argv.index("--") + 1:]
exec(open(argv[0], encoding="utf-8").read())
CAL = json.load(open(argv[1], encoding="utf-8"))["_calibracao"]["comer_param_graus"]
OUT, MANI = argv[2], argv[3]
I0, FI0 = amostra("idle_loop", 0.0)
def I(t): return amostra("idle_loop", t)
PARAM = {k: R(v) for k, v in CAL.items()}; PARAM["cauda_com"] = 0.0
DIST_PESC = [0.40, 0.28, 0.18, 0.10, 0.04]
def baixar_pescoco(P, A):
    for b, k in zip(PESCOCO, DIST_PESC): girar(P, b, X, A * k)
def _juntas(M, s): return (ponta(M, "calf_" + s), ponta(M, "foot_" + s), ponta(M, "toe_" + s))   # jarrete, bola, ponta
LEG0 = {s: _juntas(fk(I0, PERNA[s]), s) for s in "LR"}
FK0 = fk(I0)
def agachar(P):
    """coxa (2 eixos) + canela levam o JARRETE exatamente ao ponto do idle; pe e dedo recebem a mesma orientacao de
    mundo do idle: o pe fica identico ao idle e so coxa/canela absorvem a descida"""
    res = {}
    for s in "LR":
        alvos = [(lambda M, s=s: ponta(M, "calf_" + s), LEG0[s][0], 1.0)]
        res[s] = ik_perna(P, s, alvos, eixos=[("thigh_" + s, X), ("thigh_" + s, FRENTE), ("calf_" + s, X)], it=80)
        M = fk(P, ["calf_" + s]); Mc = M["calf_" + s]
        alvo_rot = FK0["foot_" + s].to_3x3()                         # orientacao do pe no idle (espaco do armature)
        base_rot = (Mc @ REL["foot_" + s]).to_3x3()
        q = (base_rot.inverted() @ alvo_rot).to_quaternion()
        l, _, e = P["foot_" + s]; P["foot_" + s] = (l, q, e)
        P["toe_" + s] = tuple(x.copy() for x in I0["toe_" + s])
    return res
T_COM = DUR["idle_loop"]; QC = 1.5
def comer_base(P):
    mover(P, "root", V((0, 0, -QC))); agachar(P)
    for b in COLUNA: girar(P, b, X, R(7))
    baixar_pescoco(P, PARAM["comer_pesc"])
    girar(P, "head", X, PARAM["cab_com"])
    for s in "LR":
        sx = 1.0 if BD["upperarm_" + s].head_local.x > 0 else -1.0
        girar(P, "shoulder_" + s, Y, -PARAM["asa_com_" + s] * sx)
    for b in CAUDA[:2]: girar(P, b, X, PARAM["cauda_com"] / 2)      # + = ergue
def c_comer(t):
    P, fold = I(t)
    comer_base(P)
    u = (t / T_COM) * 2 % 1.0
    mord = suave(u / 0.18) * (1 - suave((u - 0.22) / 0.12))
    puxa = suave((u - 0.30) / 0.22) * (1 - suave((u - 0.62) / 0.30))
    girar(P, "jaw", X, R(18) * mord + R(5) * puxa)
    for b in PESCOCO[1:]: girar(P, b, X, R(-3.5) * puxa)
    girar(P, "head", X, R(6) * puxa)
    sac = math.sin(2 * math.pi * (u - 0.30) / 0.16) * puxa * (1 if int(t / T_COM * 2) % 2 == 0 else -1)
    girar(P, "head", Z, R(9) * sac); girar(P, "neck_05", Z, R(4) * sac)
    return P, fold
# cauda: menor elevacao que deixa a ponta >= 0,06 em todo o ciclo (amostras a cada 0,1 s)
TS = [k * 0.1 for k in range(int(T_COM / 0.1) + 1)]
def zcauda_ciclo(a):
    PARAM["cauda_com"] = a; return min(zmin_reg(*c_comer(t))["cauda"] for t in TS)
z0 = zcauda_ciclo(0.0)
PARAM["cauda_com"] = bissecao(zcauda_ciclo, 0.0, R(6), 0.06, it=12) if z0 < 0.06 else 0.0
LOG = {"param_v1_graus": CAL, "cauda_com_graus": round(math.degrees(PARAM["cauda_com"]), 3), "cauda_zmin_sem_ajuste": round(z0, 3),
       "ik_res_agachar": {s: round(v, 4) for s, v in agachar(c_comer(0)[0]).items()}}
print("CALIB", json.dumps(LOG), flush=True)
mani = {"_fonte": "Wyvern_E7_clipes_L2b.blend; so Comer regravado (13_comer_v2.py)", "_hz": HZ, "_calibracao": LOG}
mani["Comer"] = gravar_clipe("Comer", c_comer, T_COM, True); print("CLIPE", mani["Comer"], flush=True)
zerar()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(mani, open(MANI, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OK")
