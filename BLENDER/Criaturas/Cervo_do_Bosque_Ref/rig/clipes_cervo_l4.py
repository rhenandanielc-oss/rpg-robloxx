# ================================================================== LOTE 4 (13/11/2026): reacao e derrota.
# Susto, ReacaoFrente, ReacaoE, ReacaoD, DefesaGalhada [PROPOSTA: a ficha so sugere fuga para o cervo], Derrota e Caido
# (pose final de lado, parada, para a interacao de COLETA, que e OFICIAL: derrota seguida de interacao).
# Carregado por exec() em clipes_cervo.py so com CERVO_L4=1 (rodar sem CERVO_L3B). NAO altera lotes aprovados.
# Todos os clipes de pe comecam e terminam no quadro 0 do Repouso. Duracoes/amplitudes = PROPOSTA tecnica.
CAB_O = bpy.data.objects["Cervo_Cabeca"]
_gr = {g.index: g.name for g in CORPO.vertex_groups}
_dom = [(_gr[max(v.groups, key=lambda g: g.weight).group] if v.groups else "") for v in CORPO.data.vertices]
_perna = ("Braco", "Antebraco", "Canela", "Quartela", "Coxa", "Perna")
TRONCO_IDX = np.array([i for i, n in enumerate(_dom) if n and not any(s_ in n for s_ in _perna + ("Cauda", "Cabeca", "Orelha", "Pescoco"))])
PERNA_IDX = np.array([i for i, n in enumerate(_dom) if any(s_ in n for s_ in _perna)])
CADEIA = {k: (BD[m].parent.name, m, f, k) for k, (_p, f, m) in PATAS.items()}
def _malha(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); ev.to_mesh_clear(); return c.reshape(-1, 3)
def janela4(t, a, b, sub, des): return suave((t - a) / sub) * (1 - suave((t - (b - des)) / des))
R0c, Z0c, _p, _e = c_repouso(0.0)
def com_repouso(r, rz, k=1.0):
    for n_, l in R0c.items(): r[n_] = r.get(n_, []) + [(e, a * k) for e, a in l]
    return rz + Z0c * k
def _cop(k_): return [c_ for c_ in PB[k_].constraints if c_.type == "COPY_ROTATION"][0]
# ---------------------------------------------------------------- patas "soltas" (FK): pata relaxada/dobrada sem IK
# Q_SOLTA[estado][osso] = rotacao local; transicao = slerp(solucao do IK em pe, alvo FK, w)
def _q(nome, ang, aby=0.0): return rot_mundo(nome, [(X, R(ang)), (Y, R(aby))])
Q_SOLTA = {
    "dobra_frente": {"BracoE": _q("BracoE", -25), "AntebracoE": _q("AntebracoE", 55), "CanelaE": _q("CanelaE", -95), "QuartelaE": _q("QuartelaE", -30),
                     "BracoD": _q("BracoD", -25), "AntebracoD": _q("AntebracoD", 55), "CanelaD": _q("CanelaD", -95), "QuartelaD": _q("QuartelaD", -30)},
    "relaxada": {"BracoE": _q("BracoE", -12), "AntebracoE": _q("AntebracoE", 8), "CanelaE": _q("CanelaE", -14), "QuartelaE": _q("QuartelaE", -20),
                 "BracoD": _q("BracoD", -20, -16), "AntebracoD": _q("AntebracoD", 16), "CanelaD": _q("CanelaD", -22), "QuartelaD": _q("QuartelaD", -24),
                 "CoxaE": _q("CoxaE", 18), "PernaE": _q("PernaE", -14), "CanelaTrasE": _q("CanelaTrasE", 10), "QuartelaTrasE": _q("QuartelaTrasE", -20),
                 "CoxaD": _q("CoxaD", 10, -16), "PernaD": _q("PernaD", -6), "CanelaTrasD": _q("CanelaTrasD", 4), "QuartelaTrasD": _q("QuartelaTrasD", -16)},
}
_hook_ant = DOBRA_HOOK
def hook_l4(ext):
    if ext.get("dobra") and _hook_ant: _hook_ant(ext)
    sol = ext.get("solta")
    if not sol: return
    for k_ in sol: PB[PATAS[k_][1]].constraints["IK"].influence = 1.0; _cop(k_).influence = 1.0
    bpy.context.view_layer.update()
    qik = {b_: arm.convert_space(pose_bone=PB[b_], matrix=PB[b_].matrix, from_space="POSE", to_space="LOCAL").to_quaternion()
           for k_ in sol for b_ in CADEIA[k_]}
    for k_, (w, estA, estB, m) in sol.items():
        PB[PATAS[k_][1]].constraints["IK"].influence = 0.0; _cop(k_).influence = 0.0
        for b_ in CADEIA[k_]:
            alvo = Q_SOLTA[estA].get(b_, qik[b_]).slerp(Q_SOLTA[estB].get(b_, qik[b_]), m)
            PB[b_].rotation_quaternion = qik[b_].slerp(alvo, w)
    bpy.context.view_layer.update()
DOBRA_HOOK = hook_l4
# ---------------------------------------------------------------- Susto (1,4 s): recua sobre os cascos plantados
DUR_SUSTO = 1.4
def c_susto(t):
    i = suave(t / 0.16) * (1 - suave((t - 0.45) / 0.9)); r = {}
    r["Pescoco"] = [(X, R(-16) * i)]; r["Pescoco2"] = [(X, R(-6) * i)]; r["Cabeca"] = [(X, R(6) * i)]
    r["Coluna3"] = [(X, R(-4) * i)]; r["Raiz"] = [(X, R(-3) * i)]
    r["Cauda1"] = [(X, R(-50) * i)]; r["Cauda2"] = [(X, R(-15) * i)]
    r["OrelhaE"] = [(X, R(-12) * i), (Z, R(14) * i)]; r["OrelhaD"] = [(X, R(-12) * i), (Z, R(-14) * i)]
    return r, com_repouso(r, V((0, 0.05 * i, -0.03 * i))), {}, {"apoio": {k_: True for k_ in PATAS}}
# ---------------------------------------------------------------- reacoes a golpe (0,9 s): impacto rapido, recupera devagar
DUR_REA = 0.9
def _impacto(t): return suave(t / 0.07) * (1 - suave((t - 0.12) / 0.7))
def c_reacao_frente(t):
    i = _impacto(t); r = {}
    r["Pescoco"] = [(X, R(-14) * i)]; r["Pescoco2"] = [(X, R(-8) * i)]; r["Cabeca"] = [(X, R(-10) * i)]
    r["Coluna3"] = [(X, R(-5) * i)]; r["Coluna2"] = [(X, R(-2) * i)]; r["Raiz"] = [(X, R(-4) * i)]
    r["OrelhaE"] = [(X, R(25) * i)]; r["OrelhaD"] = [(X, R(25) * i)]; r["Cauda1"] = [(X, R(-25) * i)]
    return r, com_repouso(r, V((0, 0.06 * i, -0.02 * i))), {}, {"apoio": {k_: True for k_ in PATAS}}
def _reacao_lado(sinal):
    """sinal +1 = golpe vindo da E: o corpo verga para a D (longe do golpe)"""
    def f(t):
        i = _impacto(t); r = {}
        r["Raiz"] = [(Y, R(5) * sinal * i)]; r["Coluna2"] = [(Z, R(-5) * sinal * i)]; r["Coluna3"] = [(Z, R(-5) * sinal * i), (Y, R(3) * sinal * i)]
        r["Pescoco"] = [(Z, R(-12) * sinal * i), (X, R(-6) * i)]; r["Pescoco2"] = [(Z, R(-6) * sinal * i)]; r["Cabeca"] = [(Z, R(-8) * sinal * i), (Y, R(6) * sinal * i)]
        r["OrelhaE"] = [(X, R(25) * i)]; r["OrelhaD"] = [(X, R(25) * i)]; r["Cauda1"] = [(Z, R(-15) * sinal * i), (X, R(-20) * i)]
        return r, com_repouso(r, V((-0.05 * sinal * i, 0, -0.02 * i))), {}, {"apoio": {k_: True for k_ in PATAS}}
    return f
# ---------------------------------------------------------------- DefesaGalhada [PROPOSTA] (2,2 s): baixa a galhada a frente,
# raspa uma dianteira, estocada curta a frente sobre os cascos plantados, volta
DUR_DEF = 2.2
def c_defesa(t):
    a = janela4(t, 0.0, DUR_DEF, 0.35, 0.5)                             # galhada abaixada/apontada
    est = math.sin(math.pi * min(1, max(0, (t - 1.05) / 0.32))) ** 1.5   # estocada
    r = {"Pescoco": [(X, R(30) * a - R(6) * est)], "Pescoco2": [(X, R(10) * a)], "Cabeca": [(X, R(30) * a + R(10) * est)],
         "Coluna3": [(X, R(6) * a)], "Raiz": [(X, R(4) * a + R(3) * est)],
         "OrelhaE": [(X, R(30) * a)], "OrelhaD": [(X, R(30) * a)], "Cauda1": [(X, R(-20) * a)]}
    pes = {}; apoio = {k_: True for k_ in PATAS}
    u = (t - 0.45) / 0.45                                              # raspa o chao com a dianteira D (aviso)
    if 0 <= u < 1:
        pes["QuartelaD"] = V((0, -0.06 * math.sin(math.pi * u), 0.05 * math.sin(math.pi * u))); apoio["QuartelaD"] = False
    return r, com_repouso(r, V((0, -0.09 * est, -0.04 * a)), 1.0), pes, {"apoio": apoio}
# ---------------------------------------------------------------- Derrota (2,8 s) e Caido (pose final de lado, 2 s parado)
ROLL = R(-84)                                                         # cai para o lado D
CAI = {"dz": -0.5, "pesc": R(-20), "giro": R(40)}
def pose_caido(k=1.0):
    r = {"Raiz": [(Y, ROLL * k), (X, R(3) * k)], "Coluna2": [(Z, R(4) * k)],
         "Pescoco": [(Z, CAI["pesc"] * k), (X, R(10) * k)], "Pescoco2": [(Z, CAI["pesc"] * 0.6 * k)], "Cabeca": [(Z, CAI["pesc"] * 0.4 * k), (X, R(6) * k), (Y, CAI["giro"] * k)],
         "OrelhaE": [(X, R(20) * k)], "OrelhaD": [(X, R(20) * k)], "Cauda1": [(X, R(15) * k)]}
    return r, V((0, 0, CAI["dz"] * k))
def _aplicar_caido():
    zerar(); r, rz = pose_caido(1.0)
    PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ (rz + V((0, 0, BASE_Z)))
    for nm, eixos in r.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
    bpy.context.view_layer.update()
    hook_l4({"solta": {k_: (1.0, "relaxada", "relaxada", 0.0) for k_ in PATAS}})
# corpo: o flanco toca o chao; cabeca: o pescoco verga ate a cabeca encostar
lo_, hi_ = -1.2, 0.2
for _ in range(20):
    CAI["dz"] = (lo_ + hi_) / 2; _aplicar_caido()
    _cc = _malha(CORPO)
    if min(float(_cc[TRONCO_IDX, 2].min()), float(_cc[PERNA_IDX, 2].min()) + 0.006) > 0.008: hi_ = CAI["dz"]
    else: lo_ = CAI["dz"]
CAI["dz"] = hi_
# cabeca: gira contra o tombo (galhada escora para cima, como no animal abatido) e o pescoco verga; busca o par em que a
# cabeca/galhada encosta no chao (z min ~1,2 cm) com a menor curva de pescoco
melhor = None
for g_ in range(0, 100, 10):
    for p_ in range(-50, 55, 5):
        CAI["giro"], CAI["pesc"] = R(g_), R(p_); _aplicar_caido(); zc_ = float(_malha(CAB_O)[:, 2].min())
        if zc_ < 0.004: continue
        nota = abs(zc_ - 0.012) * 40 + abs(p_) / 50 + g_ / 200
        if melhor is None or nota < melhor[0]: melhor = (nota, g_, p_, zc_)
print("BUSCA cabeca caido", melhor)
CAI["giro"], CAI["pesc"] = R(melhor[1]), R(melhor[2]); _aplicar_caido()
_c = _malha(CORPO)
print("CALIB caido dz", round(CAI["dz"], 3), "pescoco", round(math.degrees(CAI["pesc"]), 1), "tronco z", round(float(_c[TRONCO_IDX, 2].min()), 3),
      "pernas z", round(float(_c[PERNA_IDX, 2].min()), 3), "cabeca z", round(float(_malha(CAB_O)[:, 2].min()), 3))
for k_ in PATAS: PB[PATAS[k_][1]].constraints["IK"].influence = 1.0; _cop(k_).influence = 1.0
zerar(); bpy.context.view_layer.update()
DUR_DER = 2.8
def c_derrota(t):
    """golpe final (recuo) -> dianteiras cedem (dobra) e a frente desce -> tomba de lado, pernas soltas -> cabeca
    cai por ultimo e o corpo assenta (pequeno quique)"""
    i = _impacto(t)                                                   # recuo do golpe
    fd = suave((t - 0.15) / 0.55)                                    # dianteiras cedem
    rl = suave((t - 0.55) / 0.85) ** 1.4                              # tomba (acelera ao cair)
    cab = suave((t - 1.10) / 0.70)                                    # cabeca cai por ultimo
    qui = math.sin(math.pi * min(1, max(0, (t - 1.40) / 0.30))) * 0.25   # quique ao bater no chao
    r, rz = pose_caido(1.0)
    r = {"Raiz": [(Y, ROLL * rl), (X, R(3) * rl + R(14) * fd * (1 - rl))], "Coluna2": [(Z, R(4) * rl)],
         "Pescoco": [(Z, CAI["pesc"] * cab), (X, R(10) * cab - R(14) * i)], "Pescoco2": [(Z, CAI["pesc"] * 0.6 * cab)],
         "Cabeca": [(Z, CAI["pesc"] * 0.4 * cab), (X, R(6) * cab), (Y, CAI["giro"] * cab)], "OrelhaE": [(X, R(20) * cab)], "OrelhaD": [(X, R(20) * cab)],
         "Cauda1": [(X, R(15) * rl - R(30) * i)]}
    dz = CAI["dz"] * rl - 0.07 * fd * (1 - rl) + 0.02 * qui
    sol = {}
    for k_ in PATAS:
        if PATAS[k_][0] == "dian": sol[k_] = (max(fd, rl), "dobra_frente", "relaxada", rl)
        elif rl > 0: sol[k_] = (rl, "relaxada", "relaxada", 0.0)
    ext = {"solta": sol, "apoio": {k_: (k_ not in sol) for k_ in PATAS}}
    return r, com_repouso(r, V((0, 0.03 * i, dz)), 1 - suave(t / 0.3)), {}, ext
def c_caido(t):
    r, rz = pose_caido(1.0)
    return r, rz, {}, {"solta": {k_: (1.0, "relaxada", "relaxada", 0.0) for k_ in PATAS}, "apoio": {k_: False for k_ in PATAS}}
CLIPES.update({"Susto": (c_susto, DUR_SUSTO, False, 0.0, None, 0.0), "ReacaoFrente": (c_reacao_frente, DUR_REA, False, 0.0, None, 0.0),
               "ReacaoE": (_reacao_lado(1), DUR_REA, False, 0.0, None, 0.0), "ReacaoD": (_reacao_lado(-1), DUR_REA, False, 0.0, None, 0.0),
               "DefesaGalhada": (c_defesa, DUR_DEF, False, 0.0, None, 0.0), "Derrota": (c_derrota, DUR_DER, False, 0.0, None, 0.0),
               "Caido": (c_caido, 2.0, True, 0.0, None, 0.0)})
