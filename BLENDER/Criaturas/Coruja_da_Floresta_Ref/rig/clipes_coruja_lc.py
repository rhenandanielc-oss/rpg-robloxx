# ================================================================== LOTE C da Coruja-da-Floresta (15/11/2026): vida e caca.
# Carregado com CORUJA_LC=1 (traz o lote B junto; rig r3: CORUJA_R3=1, CORUJA_DOBRA=rig/r3/dobra_asas.json).
# Espreitar, Piar, MergulhoCaca (Planar q0 -> MantoFim), Comer (MantoFim -> Repouso q0), Adormecer, Dormindo (laco), Despertar.
# Comportamento (noturna, caca, sono) e [PROPOSTA]; presa e coleta nao estao definidas (nenhum objeto de presa aqui).
# Asas por quaternions explicitos (ext["asa_q"]) para encadear FECHADA, ABERTA e MANTO sem salto.
def sq(a, b, f):
    if a.dot(b) < 0: b = -b
    return a.slerp(b, max(0.0, min(1.0, f)))
def asas_q(fn_q):
    """fn_q(l, nm) -> quat de cada osso da asa"""
    return {l: {nm: fn_q(l, nm) for nm in ASA_OSSOS} for l in PES}
def F_(l, nm): return FECHADA[nm + l]
MANTO_E = quats_de({"BracoAsa": [(Y, float(os.environ.get("CORUJA_MANTO_Y", "22")) * math.pi / 180), (Z, R(-28))], "AntebracoAsa": [(Y, R(6)), (Z, R(-8))], "MaoAsa": [(Y, R(6))], "Primarias": [(Y, R(2))]})
# (r2: com 48 graus as primarias entravam 9,6 cm no chao; o manto deve cobrir a presa encostando no chao)
MANTO = {"E": MANTO_E, "D": espelha(MANTO_E)}
SONO_E = {nm: FECHADA[nm + "E"].slerp(Quaternion(), 0.08) for nm in ASA_OSSOS}    # asas um pouco soltas (penas fofas)
SONO = {"E": SONO_E, "D": espelha(SONO_E)}
# ---------------------------------------------------------------- ESPREITAR: agacha, balanca a cabeca (triangula), volta
DUR_ESP = 3.4
def c_espreitar(t):
    r, raiz = base_rep(); k = suave(t / 0.45) * (1 - suave((t - 2.85) / 0.5))
    soma(r, "Coluna2", [(X, R(9) * k)]); soma(r, "Coluna1", [(X, R(4) * k)])
    bob = 0.0; lado = 0.0
    for i, t0 in enumerate((0.55, 1.05, 1.55, 2.05)):             # 4 balancos rapidos de cabeca (sobe/desce e de lado)
        p = pulso(t, t0, 0.42); bob += p * (1 if i % 2 == 0 else -0.7); lado += p * (1 if i % 2 else -1)
    soma(r, "Pescoco", [(X, R(10) * k)]); soma(r, "Pescoco2", [(X, R(-6) * bob), (Y, R(8) * lado)])
    soma(r, "Cabeca", [(X, R(-14) * k + R(10) * bob), (Z, R(10) * lado), (Y, R(-12) * lado)])   # olhar fixo no alvo, cabeca compensa
    for l in "ED": soma(r, "Tufo" + l, [(X, R(-20) * k)])                 # tufos baixam (atencao)
    return r, raiz + V((0, -0.008 * k, -0.012 * k)), {}, {}
# ---------------------------------------------------------------- PIAR: incha o pescoco/peito, inclina, dois pios
DUR_PIA = 2.6
def c_piar(t):
    r, raiz = base_rep(); k = janela(t, 0.15, 2.35, 0.3, 0.35)
    pio = pulso(t, 0.75, 0.45) + 0.85 * pulso(t, 1.45, 0.45)
    soma(r, "Coluna2", [(X, R(10) * k + R(4) * pio)]); soma(r, "Coluna1", [(X, R(3) * k)])        # inclina para a frente
    soma(r, "Pescoco", [(X, R(-6) * k - R(8) * pio)]); soma(r, "Pescoco2", [(X, R(-5) * pio)]); soma(r, "Cabeca", [(X, R(-6) * k + R(9) * pio)])   # garganta estica e o bico aponta para baixo no pio
    soma(r, "Cauda", [(X, R(10) * k + R(4) * pio)])                        # cauda sobe ao piar (r2: o sinal negativo a enfiava no chao)
    for l in "ED": soma(r, "Tufo" + l, [(X, R(8) * k)])
    asa = {l: (MEIO_ABERTA_E if l == "E" else ASA_D(MEIO_ABERTA_E), 0.15 * pio) for l in "ED"}
    return r, raiz + V((0, 0, -0.004 * k)), {}, {"asa": asa}
# ---------------------------------------------------------------- MERGULHO DE CACA: Planar q0 -> mergulho -> garras -> manto
DUR_MER = 1.55; T_IMP = 0.95
def pitch_mer(t):
    if t < 0.55: return PITCH + R(22) * suave(t / 0.45)               # mergulha
    return (PITCH + R(22)) * (1 - suave((t - 0.55) / 0.35)) + R(10) * suave((t - 0.55) / 0.35)   # corpo levanta e joga as garras
def c_mergulho(t):
    rv, _rz = corpo_voo(t, 0.0, 0.0, 1.0 - suave(t / 0.3))          # sai do planeio (deltas do planeio somem)
    pt = pitch_mer(t); rv["Raiz"] = [(X, pt)]
    soma(rv, "Pescoco", [(X, (PITCH - pt) * 0.30)]); soma(rv, "Pescoco2", [(X, (PITCH - pt) * 0.30)]); soma(rv, "Cabeca", [(X, (PITCH - pt) * 0.35 + R(12) * suave(t / 0.5))])   # olho na presa
    desce = suave(t / T_IMP) ** 1.4
    raiz_v = raiz_para(pt, 0.0, (0, 0, H_VOO * (1 - desce) + (CENTRO.z + 0.03) * desce))
    # manto (no chao): corpo inclinado sobre a presa (pela coluna, nao pela Raiz), cabeca olhando a presa nos pes
    r0, raiz0 = base_rep(); m = suave((t - T_IMP + 0.05) / 0.35)
    soma(r0, "Coluna1", [(X, R(12))]); soma(r0, "Coluna2", [(X, R(16))]); soma(r0, "Pescoco", [(X, R(20))]); soma(r0, "Cabeca", [(X, R(12))])
    soma(r0, "Cauda", [(X, R(14))]); soma(r0, "CaudaLequeE", [(Y, R(-14))]); soma(r0, "CaudaLequeD", [(Y, R(14))])
    for l in "ED": soma(r0, "Tufo" + l, [(X, R(-18))])
    r = mistura(rv, r0, m); raiz = raiz_v.lerp(raiz0 + V((0, 0, -0.025)), m)
    rec = R(20) * suave((t - 0.15) / 0.3) * (1 - suave((t - 0.55) / 0.3))   # asas meio recolhidas no mergulho
    def asa_t(l, nm):
        base = sq(Quaternion(), FECHADA[nm + l], 0.45 * suave(t / 0.3) * (1 - suave((t - 0.6) / 0.3)))   # aberta -> meio fechada -> abre para frear
        return sq(base, MANTO[l][nm], m)
    garras = suave((t - 0.55) / 0.35)                               # pernas: recolhidas -> estendidas a frente -> no chao
    pes = {l: V((0, -0.05 * (1 - m), 0)) for l in PES}
    return r, raiz, pes, {"asa_q": asas_q(asa_t), "pernas_fk": pernas_no_ar(1 - garras), "apoio": {l: t >= T_IMP for l in PES}}
def v_mergulho(t): return (V_PLA + 0.9 * suave(t / 0.5)) * (1 - suave((t - 0.5) / (T_IMP - 0.5)))
# ---------------------------------------------------------------- COMER: MantoFim -> 3 bicadas (puxa e engole) -> fecha asas -> Repouso q0
DUR_COM = 3.4
def c_comer(t):
    r_m, raiz_m, _p, e_m = c_mergulho(DUR_MER)                       # comeca exatamente no fim do mergulho
    r0, raiz0 = base_rep(); vol = suave((t - 2.35) / 0.9)             # volta ao repouso no fim
    r = mistura(r_m, r0, vol)
    bic = 0.0; puxa = 0.0
    for t0 in (0.35, 1.05, 1.75):
        bic += pulso(t, t0, 0.38); puxa += pulso(t, t0 + 0.22, 0.30)
    soma(r, "Pescoco", [(X, R(26) * bic - R(8) * puxa)]); soma(r, "Pescoco2", [(X, R(14) * bic), (Z, R(10) * puxa)])
    soma(r, "Cabeca", [(X, R(22) * bic - R(16) * puxa), (Y, R(14) * puxa)])          # bica, puxa e torce (rasga)
    eng = pulso(t, 2.15, 0.35); soma(r, "Pescoco", [(X, R(-10) * eng)]); soma(r, "Cabeca", [(X, R(-12) * eng)])   # engole (cabeca sobe)
    # (r2: a bicada inclinava o tronco e levava a ponta da asa em manto 2,8 cm abaixo do chao -> bicada so com o pescoco)
    fecha = suave((t - 1.0) / 1.6)
    MEIO = {"E": MEIO_ABERTA_E, "D": ASA_D(MEIO_ABERTA_E)}
    def asa_t(l, nm):                                               # fecha em 2 etapas: recolhe junto ao corpo e so entao dobra
        f1 = suave(fecha * 2); f2 = suave(fecha * 2 - 1)            # (r2: direto do manto para a fechada a ponta passava 2,4 cm abaixo do chao)
        return sq(sq(MANTO[l][nm], Quaternion(), f1), FECHADA[nm + l], f2)   # sobe para a horizontal e fecha (mesmo caminho do Pousar)
    return r, raiz_m.lerp(raiz0, vol), {}, {"asa_q": asas_q(asa_t)}
# ---------------------------------------------------------------- PALPEBRAS (rig r4; pedido 15/11 "ele dorme com os olhos fechados")
_PJ = os.environ.get("CORUJA_PALPEBRAS")
PALP = json.load(open(_PJ))["olhos"] if _PJ and os.path.exists(_PJ) else None
def palpebras(r, f):
    """f = 0 aberta (repouso do rig) ... 1 fechada; sem o rig r4 nao faz nada"""
    if not PALP or f <= 1e-4: return
    for l in ("E", "D"): soma(r, "Palpebra" + l, [(V(PALP[l]["eixo"]), math.radians(PALP[l]["fechar_graus"]) * min(1.0, f))])
def piscada(t, t0, dur=0.22): return pulso(t, t0, dur)                   # fecha e abre
# ---------------------------------------------------------------- SONO pousada: Adormecer -> Dormindo (laco) -> Despertar
def pose_sono(r, k):
    soma(r, "Pescoco", [(X, R(-10) * k)]); soma(r, "Pescoco2", [(X, R(14) * k)]); soma(r, "Cabeca", [(X, R(10) * k), (Y, R(5) * k)])   # cabeca afunda nos ombros
    soma(r, "Coluna2", [(X, R(-3) * k)]); soma(r, "Coluna1", [(X, R(-2) * k)])
    for l in "ED": soma(r, "Tufo" + l, [(X, R(-30) * k)])            # tufos deitados
    soma(r, "Cauda", [(X, R(7) * k)])                                  # (r2: com o corpo baixo a ponta da cauda tocava o chao)
T_DOR = 6.0
def c_dormindo(t):
    r, raiz = base_rep(); pose_sono(r, 1.0); b = onda(t, T_DOR / 2)     # respiracao lenta (2 por laco)
    soma(r, "Coluna1", [(X, R(0.8) * b)]); soma(r, "Coluna2", [(X, R(-0.6) * b)]); soma(r, "Cabeca", [(X, R(1.2) * b)])
    palpebras(r, 1.0)                                                # olhos fechados
    return r, raiz + V((0, 0, -0.018 + 0.002 * b)), {}, {"asa_q": {l: SONO[l] for l in PES}}
DUR_ADO = 1.8
def c_adormecer(t):
    r, raiz = base_rep(); k = suave(t / DUR_ADO) ** 1.2
    boc = pulso(t, 0.25, 0.5)                                        # ultimo olhar / ajeita antes de dormir
    soma(r, "Cabeca", [(Z, R(10) * boc)]); pose_sono(r, k)
    # olhos pesando: duas piscadas lentas (cada vez fecha mais) e fecha de vez
    palpebras(r, max(0.6 * piscada(t, 0.55, 0.40), 0.85 * piscada(t, 1.0, 0.45), suave((t - 1.25) / 0.45)))
    rd, raizd, _p, ed = c_dormindo(0.0)
    def asa_t(l, nm): return sq(FECHADA[nm + l], SONO[l][nm], k)
    return r, raiz.lerp(raizd, k), {}, {"asa_q": asas_q(asa_t)}
DUR_DES = 1.4
def c_despertar(t):
    rd, raizd, _p, _e = c_dormindo(0.0); r0, raiz0 = base_rep(); k = suave(t / 1.0)
    r = mistura(rd, r0, k); sac = pulso(t, 0.95, 0.35)                # acorda e da uma sacudidela curta
    soma(r, "Coluna2", [(Z, R(5) * math.sin(2 * math.pi * 6 * (t - 0.95)) * sac)]); soma(r, "Cabeca", [(Z, R(8) * math.sin(2 * math.pi * 6 * (t - 1.0)) * sac)])
    r.pop("PalpebraE", None); r.pop("PalpebraD", None)               # a mistura com o sono ja traria a palpebra; a curva abaixo manda
    palpebras(r, max(1 - suave((t - 0.10) / 0.35), piscada(t, 0.62, 0.22)))   # abre devagar e da uma piscada
    def asa_t(l, nm): return sq(SONO[l][nm], FECHADA[nm + l], k)
    return r, raizd.lerp(raiz0, k), {}, {"asa_q": asas_q(asa_t)}
REF_EXTRA_C = {"MantoFim": (c_mergulho, DUR_MER), "DormindoQ0": (c_dormindo, 0.0)}
CLIPES.update({"Espreitar": (c_espreitar, DUR_ESP, False, 0.0, 0.0, "Repouso q0", "Repouso q0"),
               "Piar": (c_piar, DUR_PIA, False, 0.0, 0.0, "Repouso q0", "Repouso q0"),
               "MergulhoCaca": (c_mergulho, DUR_MER, False, 0.0, 0.0, "Planar q0", "MantoFim", v_mergulho),
               "Comer": (c_comer, DUR_COM, False, 0.0, 0.0, "MantoFim", "Repouso q0"),
               "Adormecer": (c_adormecer, DUR_ADO, False, 0.0, 0.0, "Repouso q0", "Dormindo q0"),
               "Dormindo": (c_dormindo, T_DOR, True, 0.0, 0.0, "laco", "laco"),
               "Despertar": (c_despertar, DUR_DES, False, 0.0, 0.0, "Dormindo q0", "Repouso q0")})
print("LOTE_C", {k: CLIPES[k][1] for k in ("Espreitar", "Piar", "MergulhoCaca", "Comer", "Adormecer", "Dormindo", "Despertar")})
