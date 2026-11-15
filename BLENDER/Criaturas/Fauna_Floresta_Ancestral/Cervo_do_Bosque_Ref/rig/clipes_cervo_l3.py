# ================================================================== LOTE 3 bloco A (13/11/2026): vida no habitat.
# Pastar (entrada / laco / saida), Beber (entrada / laco / saida), Alerta (batida de casco), CocarCabeca (pata traseira
# coca a bochecha) e Sacudir. Carregado por exec() em clipes_cervo.py so com CERVO_L3=1; NAO altera lotes 1 e 2.
# Todos comecam e terminam no quadro 0 do Repouso aprovado; lacos comecam/terminam no ultimo quadro da entrada.
# Duracoes, amplitudes e frequencias = PROPOSTA tecnica. Sem mandibula (boca da fauna fechada): mastigar = balanco da cabeca.
# LIMITE ANATOMICO DO MODELO (medido): pescoco+cabeca (~0,74 u) a partir da base do pescoco (z 0,97) nao alcancam o chao
# com as dianteiras retas. Pastar = vegetacao baixa; Beber = dianteiras bem abertas, focinho o mais baixo sem dobrar o carpo.
CAB_O = bpy.data.objects["Cervo_Cabeca"]
_cv = np.array([v.co[:] for v in CAB_O.data.vertices]); NARIZ_Y0 = _cv[:, 1].min()
FOCINHO_IDX = np.nonzero(_cv[:, 1] < NARIZ_Y0 + 0.07)[0]
def _malha(idx):
    dg = bpy.context.evaluated_depsgraph_get(); ev = CAB_O.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); ev.to_mesh_clear(); return c.reshape(-1, 3)[idx]
def avaliar(fn, t):
    """aplica o quadro (mesma ordem do laco principal) e devolve o focinho no mundo"""
    zerar(); rots, raiz, pes, ext = fn(t); raiz = raiz + V((0, 0, BASE_Z))
    PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz
    for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
    for k, d in pes.items(): ALVO[k].location = REP[k] + d
    for k, a_ in ext.get("rot_pe", {}).items(): ALVO[k].rotation_quaternion = Quaternion(X, a_) @ ROT0[k]
    bpy.context.view_layer.update(); return _malha(FOCINHO_IDX)
def soma(*dicts_pesos):
    r = {}
    for d, w in dicts_pesos:
        for n_, l in d.items(): r[n_] = r.get(n_, []) + [(e, a * w) for e, a in l]
    return r
R0, Z0, _p, _e = c_repouso(0.0)                                      # pose do quadro 0 do Repouso (emenda)
def mistura_repouso(r, rz, k):
    """k = peso da pose nova (0 = quadro 0 do Repouso)"""
    return soma((R0, 1 - k), (r, 1.0)), Z0 * (1 - k) + rz
# ---------------------------------------------------------------- cabeca baixa (pastar/beber)
import json as _js
BEB = dict(raiz=12, pesc=74, pesc2=24, cab=2, abre=0.30, frente=-0.18, desce=-0.13)   # escolhido por teste 13/11 (focinho ~0,18 u)
BEB.update(_js.loads(os.environ.get("CERVO_BEBER", "{}")))          # teste de parametros do Beber (sem a variavel: padrao)
def pose_chao(k, beber=False):
    """pescoco desce a frente (nao enrola), focinho aponta para baixo-frente; corpo baixa pouco"""
    r = {"Raiz": [(X, R(BEB["raiz"] if beber else 3) * k)], "Coluna3": [(X, R(4) * k)], "Coluna2": [(X, R(2) * k)],
         "Pescoco": [(X, R(BEB["pesc"] if beber else 60) * k)], "Pescoco2": [(X, R(BEB["pesc2"] if beber else 14) * k)],
         "Cabeca": [(X, R(BEB["cab"] if beber else -10) * k)],
         "OrelhaE": [(Z, R(-10) * k), (X, R(6) * k)], "OrelhaD": [(Z, R(10) * k), (X, R(6) * k)], "Cauda1": [(X, R(4) * k)]}
    if beber:                                                         # as duas dianteiras abrem bem (postura do cervo bebendo)
        sx_, fy_ = BEB["abre"], BEB["frente"]
        return r, V((0, 0, BEB["desce"] * k)), {"QuartelaE": V((sx_, fy_, 0)) * k, "QuartelaD": V((-sx_, fy_, 0)) * k}
    return r, V((0, 0, -0.015 * k)), {"QuartelaE": V((0.02, -0.12, 0)) * k, "QuartelaD": V((-0.03, 0.0, 0)) * k}
CHAO_Z = {}
for _b in (False, True):
    _r, _rz, _pes = pose_chao(1.0, _b)
    CHAO_Z[_b] = float(avaliar(lambda t: (_r, _rz, _pes, {}), 0.0)[:, 2].min())
    print("CHAO", "beber" if _b else "pastar", "focinho z", round(CHAO_Z[_b], 3), "cabeca+galhada z min", round(float(_malha(slice(None))[:, 2].min()), 3))
DUR_ENT, DUR_SAI, DUR_LACO = 1.4, 1.2, 6.0
def _entrada(beber):
    def f(t):
        k = suave(t / DUR_ENT); r, rz, pes = pose_chao(k, beber); r, rz = mistura_repouso(r, rz, k)
        return r, rz, pes, {"apoio": {q: True for q in PATAS}}
    return f
def _saida(beber):
    def f(t):
        k = 1 - suave(t / DUR_SAI); r, rz, pes = pose_chao(k, beber); r, rz = mistura_repouso(r, rz, k)
        return r, rz, pes, {"apoio": {q: True for q in PATAS}}
    return f
def _laco(beber):
    def f(t):
        r, rz, pes = pose_chao(1.0, beber); r, rz = mistura_repouso(r, rz, 1.0)
        if beber:                                                     # lambidas rapidas (3 Hz) + 1 pausa de vigilia
            lam = 0.5 - 0.5 * math.cos(2 * math.pi * t * 3.0)
            pausa = pulso(t, DUR_LACO, 3.0, 1.2)
            r["Cabeca"] = r["Cabeca"] + [(X, R(-3) * lam * (1 - pausa) - R(6) * pausa)]
            r["Pescoco2"] = r["Pescoco2"] + [(X, R(-10) * pausa)]
        else:                                                         # arranca a folhagem (puxao) e mastiga; varre de lado
            arr = pulso(t, 2.0, 0.2, 0.35)
            mast = math.sin(2 * math.pi * t * 2.5) * (1 - arr)
            r["Cabeca"] = r["Cabeca"] + [(X, R(-6) * arr + R(1.5) * mast), (Z, R(4) * arr)]
            r["Pescoco"] = r["Pescoco"] + [(Z, R(6) * math.sin(2 * math.pi * t / DUR_LACO))]
            r["Pescoco2"] = r["Pescoco2"] + [(Z, R(3) * math.sin(2 * math.pi * t / DUR_LACO))]
        oE = pulso(t, DUR_LACO, 1.1, 0.5); oD = pulso(t, DUR_LACO, 4.4, 0.5)
        r["OrelhaE"] = r["OrelhaE"] + [(Z, R(-22) * oE)]; r["OrelhaD"] = r["OrelhaD"] + [(Z, R(22) * oD)]
        sac = pulso(t, DUR_LACO, 2.6, 0.45)
        r["Cauda1"] = r["Cauda1"] + [(Z, R(14) * sac * math.sin(6 * math.pi * ((t - 2.6) % DUR_LACO) / 0.45))]
        return r, rz, pes, {"apoio": {q: True for q in PATAS}}
    return f
# ---------------------------------------------------------------- Alerta
DUR_ALE = 4.5
def c_alerta(t):
    k = suave(t / 0.35) * (1 - suave((t - 3.7) / 0.8))
    r = {"Pescoco": [(X, R(-14) * k)], "Pescoco2": [(X, R(-6) * k)], "Cabeca": [(X, R(8) * k)],
         "Coluna3": [(X, R(-2) * k)], "Cauda1": [(X, R(-35) * k)], "Cauda2": [(X, R(-10) * k)],
         "OrelhaE": [(X, R(-10) * k), (Z, R(12) * k)], "OrelhaD": [(X, R(-10) * k), (Z, R(-12) * k)]}
    u_ = min(1, max(0, (t - 1.6) / 1.8)); olha = math.sin(math.pi * u_) * math.cos(math.pi * u_)   # olha E e depois D
    r["Pescoco"] += [(Z, R(28) * olha)]; r["Cabeca"] += [(Z, R(16) * olha)]
    pes = {}; apoio = {q: True for q in PATAS}; batida = 0.0
    for t0 in (0.55, 1.05):                                             # 2 batidas de casco (aviso): sobe 0,16 s, desce 0,08 s
        u = (t - t0) / 0.24
        if 0 <= u < 1:
            batida = math.sin(math.pi * 0.5 * u / 0.66) if u < 0.66 else math.cos(math.pi * 0.5 * (u - 0.66) / 0.34)
            apoio["QuartelaE"] = False
    pes["QuartelaE"] = V((0, -0.02 * batida, 0.07 * batida))
    r["EscapulaE"] = [(X, R(-6) * batida)]
    r, rz = mistura_repouso(r, V((0, 0, 0.004 * k)), k)
    return r, rz, pes, {"apoio": apoio, "rot_pe": {"QuartelaE": R(20) * batida}}
# ---------------------------------------------------------------- CocarCabeca: cabeca baixa e curva para tras (lado E);
# traseira E sobe ate a bochecha e coca (vai-e-vem 5 Hz); peso nas outras 3 patas. Pose escolhida por busca: bochecha ao
# lado do ombro, abaixo de 0,85 u e ao alcance da pata (<= 86% da cadeia)
KC = [40.0, 1.0]
def _pose_cocar(k):
    xd, c = KC
    r = {"Pescoco": [(X, R(xd) * k), (Z, R(34) * c * k)], "Pescoco2": [(X, R(xd * 0.3) * k), (Z, R(26) * c * k)],
         "Cabeca": [(Z, R(16) * c * k), (Y, R(-25) * k)], "Coluna2": [(Z, R(5) * c * k)], "Coluna3": [(Z, R(7) * c * k), (Y, R(-4) * k)],
         "Pelve": [(Y, R(-5) * k)], "OrelhaE": [(X, R(15) * k)], "OrelhaD": [(Z, R(10) * k)]}
    return r, V((-0.02 * k, 0, -0.02 * k))
LC = sum(BD[b_].length for b_ in ("CoxaE", "PernaE", "CanelaTrasE"))
def _bochecha_de(xd, c):
    KC[0], KC[1] = xd, c; _r, _rz = _pose_cocar(1.0); zerar()
    for nm, eixos in _r.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
    PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ (_rz + V((0, 0, BASE_Z))); bpy.context.view_layer.update()
    m = PB["Cabeca"].head.lerp(PB["Cabeca"].tail, 0.35)
    return m + V((0.04, 0.0, -0.03)), PB["CoxaE"].head.copy()
melhor = None
for xd in (30, 40, 50, 60, 70):
    for c_ in (0.8, 1.0, 1.2, 1.4, 1.6, 1.8):
        bo, qd = _bochecha_de(xd, c_); d_ = (bo - qd).length
        pena = d_ + 2.0 * max(0.0, bo.z - 0.85) + 2.0 * max(0.0, abs(bo.x) - 0.30) + 4.0 * max(0.0, d_ - 0.86 * LC)
        if melhor is None or pena < melhor[0]: melhor = (pena, xd, c_, bo, d_)
KC[0], KC[1] = melhor[1], melhor[2]; _bochecha = melhor[3]
ALVO_COCAR = _bochecha - REP["QuartelaTrasE"]
print("COCAR pescoco", KC[0], "curva", KC[1], "bochecha", tuple(round(c, 3) for c in _bochecha), "dist ao quadril", round(melhor[4], 3), "cadeia", round(LC, 3))
zerar()
DUR_COC = 4.0
def c_cocar(t):
    kc = suave(t / 0.9) * (1 - suave((t - 3.2) / 0.8))
    kp = suave((t - 0.45) / 0.6) * (1 - suave((t - 2.9) / 0.6))
    r, rz = _pose_cocar(kc)
    vai = math.sin(2 * math.pi * 5.0 * t) * suave((t - 1.05) / 0.2) * (1 - suave((t - 2.6) / 0.2))
    pes = {"QuartelaTrasE": ALVO_COCAR * kp + V((0, 0.025, -0.02)) * vai * kp + V((0, 0, 0.06 * math.sin(math.pi * kp)))}
    r["Cabeca"] = r["Cabeca"] + [(Y, R(-4) * vai * kp)]
    r["Cauda1"] = [(Z, R(10) * kc)]
    r, rz = mistura_repouso(r, rz, max(kc, kp))
    return r, rz, pes, {"apoio": {q: (q != "QuartelaTrasE" or kp < 1e-3) for q in PATAS}, "rot_pe": {"QuartelaTrasE": R(60) * kp}}
# ---------------------------------------------------------------- Sacudir
DUR_SAC = 1.8
def c_sacudir(t):
    env = suave(t / 0.2) * (1 - suave((t - 1.1) / 0.6))
    def w(atraso, amp): return R(amp) * env * math.sin(2 * math.pi * 4.2 * (t - atraso))
    r = {"Cabeca": [(Y, w(0.00, 22))], "Pescoco2": [(Y, w(0.02, 14))], "Pescoco": [(Y, w(0.04, 10)), (X, R(6) * env)],
         "Coluna3": [(Y, w(0.06, 9))], "Coluna2": [(Y, w(0.09, 8))], "Coluna1": [(Y, w(0.12, 7))], "Pelve": [(Y, w(0.15, 6))],
         "Cauda1": [(Z, w(0.18, 30))], "Cauda2": [(Z, w(0.22, 30))], "OrelhaE": [(X, w(0.03, 35))], "OrelhaD": [(X, w(0.03, -35))]}
    r, rz = mistura_repouso(r, V((0, 0, -0.006 * env)), 1.0)
    return r, rz, {}, {"apoio": {q: True for q in PATAS}}
for b_, nome_ in ((False, "Pastar"), (True, "Beber")):
    CLIPES[nome_ + "Entrar"] = (_entrada(b_), DUR_ENT, False, 0.0, None, 0.0)
    CLIPES[nome_] = (_laco(b_), DUR_LACO, True, 0.0, None, 0.0)
    CLIPES[nome_ + "Sair"] = (_saida(b_), DUR_SAI, False, 0.0, None, 0.0)
CLIPES.update({"Alerta": (c_alerta, DUR_ALE, False, 0.0, None, 0.0), "CocarCabeca": (c_cocar, DUR_COC, False, 0.0, None, 0.0),
               "Sacudir": (c_sacudir, DUR_SAC, False, 0.0, None, 0.0)})
