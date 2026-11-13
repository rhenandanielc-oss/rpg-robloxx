# ================================================================== LOTE 3 bloco B (13/11/2026): Deitar, Deitado, Levantar.
# Carregado por exec() em clipes_cervo.py so com CERVO_L3B=1; NAO altera lotes aprovados. Tecnica adaptada do Bufalo
# (60_clipes.py: resolver_dobra / aplicar_dobra / calibrar_deitado): poses de pata em FK (cada osso mirado num ponto do chao),
# transicao = slerp entre a solucao do IK em pe e a dobra. Ordem dos cervideos: DEITA dobrando as dianteiras primeiro
# (ajoelha) e depois as traseiras; LEVANTA com as traseiras primeiro (garupa sobe com a frente ajoelhada) e depois as dianteiras.
# Deitado = decubito esternal: corpo apoiado sobre as patas dobradas (dianteiras sob o peito: carpo no chao, canela para tras;
# traseiras recolhidas: jarrete no chao atras, canela para a frente junto a barriga), cabeca erguida.
# Ajoelhado = dianteiras com carpo E canela no chao (dobra propria, nao a do deitado girada), traseiras em pe. Duracoes = PROPOSTA.
CADEIA = {k: (BD[m].parent.name, m, f, k) for k, (_p, f, m) in PATAS.items()}       # topo, meio, fim, quartela
_gr = {g.index: g.name for g in CORPO.vertex_groups}
_dom = [(_gr[max(v.groups, key=lambda g: g.weight).group] if v.groups else "") for v in CORPO.data.vertices]
_co0 = np.array([v.co[:] for v in CORPO.data.vertices])
_perna = ("Braco", "Antebraco", "Canela", "Quartela", "Coxa", "Perna")
TRONCO_IDX = np.array([i for i, n in enumerate(_dom) if n and not any(s_ in n for s_ in _perna + ("Cauda", "Cabeca", "Orelha"))])
PEITO_IDX = TRONCO_IDX[_co0[TRONCO_IDX, 1] < -0.10]; VENTRE_IDX = TRONCO_IDX[_co0[TRONCO_IDX, 1] > 0.15]
PERNA_IDX = {k: np.array([i for i, n in enumerate(_dom) if n in CADEIA[k]]) for k in PATAS}
DIANT = ("QuartelaE", "QuartelaD")
def pele():
    dg = bpy.context.evaluated_depsgraph_get(); ev = CORPO.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); ev.to_mesh_clear(); return c.reshape(-1, 3)
def janela3(t, a, b, sub, des): return suave((t - a) / sub) * (1 - suave((t - (b - des)) / des))
FK_DEIT, FK_AJ = {}, {}                                               # quaternions locais da dobra (deitado / ajoelhado)
DEIT = {"dz": -0.45, "pitch": R(4)}; AJ = {"pitch": R(20), "dz": 0.0}
def _cop(k_): return [c_ for c_ in PB[k_].constraints if c_.type == "COPY_ROTATION"][0]
def _alvo_q(b_, wl):
    """dianteira: dobra do ajoelhado -> do deitado conforme wl (peso do deitado); traseira: so a do deitado"""
    if b_ in FK_AJ: return FK_AJ[b_].slerp(FK_DEIT[b_], wl)
    return FK_DEIT[b_]
def hook_dobra(ext):
    """patas em dobra: 1) IK no alvo em pe (REP+base) e le as rotacoes locais; 2) desliga IK e poe slerp(IK, dobra, s)"""
    tr = ext["dobra"]; wl = ext.get("wl", 1.0)
    for k_, (f, base) in tr.items():
        PB[PATAS[k_][1]].constraints["IK"].influence = 1.0; _cop(k_).influence = 1.0
        dian = PATAS[k_][0] == "dian"
        if BOL and not ext.get("sem_corr"):
            # IK de partida: o alvo vai da posicao em pe ate o boleto da dobra; a dianteira LEVANTA o casco num arco
            # (a pata sai do chao antes de dobrar), a traseira corre rente ao chao sustentando a garupa
            fim_ = (BOL["aj"][k_].lerp(BOL["deit"][k_], wl) if (dian and k_ in BOL["aj"]) else BOL["deit"][k_])
            sobe = suave(min(1.0, f / 0.3)) * (1 - suave((f - 0.75) / 0.25))
            ALVO[k_].location = REP[k_] + base.lerp(fim_ - REP[k_], suave(f)) + V((0, 0, (0.10 if dian else 0.0) * sobe))
            ALVO[k_].rotation_quaternion = Quaternion(X, (R(45) if dian else 0.0) * sobe) @ ROT0[k_]
        else:
            ALVO[k_].location = REP[k_] + base
    bpy.context.view_layer.update()
    qik = {b_: arm.convert_space(pose_bone=PB[b_], matrix=PB[b_].matrix, from_space="POSE", to_space="LOCAL").to_quaternion()
           for k_ in tr for b_ in CADEIA[k_]}
    for k_, (f, base) in tr.items():
        PB[PATAS[k_][1]].constraints["IK"].influence = 0.0; _cop(k_).influence = 0.0
        dian = PATAS[k_][0] == "dian"
        for i_, b_ in enumerate(CADEIA[k_]):
            # dianteira dobra de baixo para cima (o casco sai do chao antes); traseira fica no IK ate a garupa quase assentar
            s_ = suave((f - 0.10 * (3 - i_)) / 0.70) if dian else suave((f - 0.35) / 0.65)
            PB[b_].rotation_quaternion = qik[b_].slerp(_alvo_q(b_, wl), s_)
    bpy.context.view_layer.update()
    # casco em transicao nunca abaixo do chao: correcao em canela/quartela com partida quente (a do quadro anterior),
    # passos de 1,5 graus (<= 6 por quadro); some nas pontas da transicao (f perto de 0 ou 1) e relaxa quando ha folga
    if not ext.get("sem_corr"):
        base_q = {b_: PB[b_].rotation_quaternion.copy() for k_ in tr for b_ in CADEIA[k_]}
        def _ap(k_, c):
            topo, meio, fim, qt = CADEIA[k_]; f = tr[k_][0]; we = min(1.0, f / 0.12, (1.0 - f) / 0.12)
            for b_, a_ in ((qt, c[0]), (fim, c[1])): PB[b_].rotation_quaternion = rot_mundo(b_, [(X, a_ * we)]) @ base_q[b_]
        for k_ in tr: CORR.setdefault(k_, [0.0, 0.0]); _ap(k_, CORR[k_])
        bpy.context.view_layer.update()
        for it in range(6):
            cs = cascos(); mud = False
            for k_ in tr:
                if len(cs[k_]) == 0: continue
                z0 = float(cs[k_][:, 2].min()); c = CORR[k_]
                if z0 < -0.004:
                    melhor = None
                    for i_ in (0, 1):
                        for sg in (1.0, -1.0):
                            t_ = list(c); t_[i_] += R(1.5) * sg; _ap(k_, t_); bpy.context.view_layer.update(); z_ = float(cascos()[k_][:, 2].min())
                            if melhor is None or z_ > melhor[0]: melhor = (z_, t_)
                    CORR[k_] = melhor[1]; mud = True
                elif z0 > 0.03 and (abs(c[0]) > 1e-4 or abs(c[1]) > 1e-4):
                    CORR[k_] = [a_ - math.copysign(min(abs(a_), R(0.75)), a_) for a_ in c]; mud = True
                _ap(k_, CORR[k_])
            bpy.context.view_layer.update()
            if not mud: break
    for k_ in list(CORR):
        if k_ not in tr: CORR[k_] = [0.0, 0.0]
CORR = {}; BOL = {}
DOBRA_HOOK = hook_dobra
def corpo_deitado(r, bk, bl):
    pitch = AJ["pitch"] * bk * (1 - bl) + DEIT["pitch"] * bl; dz = AJ["dz"] * bk * (1 - bl) + DEIT["dz"] * bl
    r["Raiz"] = r.get("Raiz", []) + [(X, pitch)]
    return dz
def cabeca_deitada(r, k):
    r["Pescoco"] = r.get("Pescoco", []) + [(X, R(-18) * k)]; r["Pescoco2"] = r.get("Pescoco2", []) + [(X, R(-6) * k)]
    r["Cabeca"] = r.get("Cabeca", []) + [(X, R(14) * k)]; r["Cauda1"] = r.get("Cauda1", []) + [(X, R(18) * k)]
def c_deitado_pose(t=0.0):
    r = {}; ext = {"dobra": {k_: (1.0, V((0, 0, 0))) for k_ in PATAS}, "apoio": {k_: False for k_ in PATAS}, "wl": 1.0}
    dz = corpo_deitado(r, 0.0, 1.0); cabeca_deitada(r, 1.0); return r, V((0, 0, dz)), {}, ext
def pose_ajoelhado(t=0.0):
    r = {}; ext = {"dobra": {k_: (1.0, V((0, 0, 0))) for k_ in DIANT}, "apoio": {k_: PATAS[k_][0] == "tras" for k_ in PATAS}, "wl": 0.0}
    dz = corpo_deitado(r, 1.0, 0.0); return r, V((0, 0, dz)), {}, ext
def _corpo(fn):
    """aplica so o corpo (Raiz/rotacoes) da pose e deixa as patas da dobra sem IK, para mirar"""
    zerar(); rots, raiz, pes, ext = fn(); raiz = raiz + V((0, 0, BASE_Z))
    PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz
    for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
    for k_ in ext["dobra"]: PB[PATAS[k_][1]].constraints["IK"].influence = 0.0; _cop(k_).influence = 0.0
    bpy.context.view_layer.update(); return ext
def _aplicar(fn):
    zerar(); rots, raiz, pes, ext = fn(); raiz = raiz + V((0, 0, BASE_Z))
    PB["Raiz"].location = BD["Raiz"].matrix_local.to_3x3().inverted() @ raiz
    for nm, eixos in rots.items(): PB[nm].rotation_quaternion = rot_mundo(nm, eixos)
    bpy.context.view_layer.update(); ext["sem_corr"] = True; hook_dobra(ext)
def _circ(P0, P1, l0, l1, lado):
    d = (P1 - P0); L = max(1e-6, d.length); L = min(L, l0 + l1 - 1e-3); a = (l0 * l0 - l1 * l1 + L * L) / (2 * L); h = math.sqrt(max(0.0, l0 * l0 - a * a))
    u = d.normalized(); per = V((0, -u.z, u.y)) if (-u.z) * lado > 0 else V((0, u.z, -u.y))
    return P0 + u * a + per * h
def _mirar(b_, alvo, dq=None):
    bpy.context.view_layer.update(); pb = PB[b_]; cur = pb.tail - pb.head
    des = (dq if alvo is None else (alvo - pb.head)); da = math.atan2(des.z, des.y) - math.atan2(cur.z, cur.y)
    da = (da + math.pi) % (2 * math.pi) - math.pi
    pb.rotation_quaternion = rot_mundo(b_, [(X, da)]) @ pb.rotation_quaternion
def mirar_patas(fn, patas, guarda):
    """com o corpo da pose fn: mira cada osso da pata no ponto desejado (no chao), de cima para baixo, 3 passadas"""
    for passada in range(3):
        _corpo(fn)
        for b_, q_ in guarda.items(): PB[b_].rotation_quaternion = q_
        bpy.context.view_layer.update()
        for k_ in patas:
            topo, meio, fim, qt = CADEIA[k_]; H = PB[topo].head.copy(); x = H.x
            if PATAS[k_][0] == "dian":   # carpo no chao a frente do ombro; canela deitada para tras; casco para tras/cima
                C = V((x, H.y - 0.08, 0.085)); J1 = _circ(V((0, H.y, H.z)), V((0, C.y, C.z)), BD[topo].length, BD[meio].length, +1)
                F = V((x, C.y + BD[fim].length * 0.97, 0.09)); alvos = [(topo, V((x, J1.y, J1.z))), (meio, C), (fim, F)]; dq = V((0, 0.85, 0.35))
            else:                        # jarrete no chao atras do quadril; canela deitada a frente; casco a frente
                K = V((x, H.y + 0.16, 0.135)); J1 = _circ(V((0, H.y, H.z)), V((0, K.y, K.z)), BD[topo].length, BD[meio].length, -1)
                F = V((x, K.y - BD[fim].length * 0.97, 0.12)); alvos = [(topo, V((x, J1.y, J1.z))), (meio, K), (fim, F)]; dq = V((0, -0.90, -0.30))
            for b_, alvo in alvos: _mirar(b_, alvo)
            _mirar(qt, None, dq)
            for b_ in CADEIA[k_]: guarda[b_] = PB[b_].rotation_quaternion.copy()
def calibrar_deitado(alvo_peito, alvo_ventre):
    for it in range(10):
        _aplicar(c_deitado_pose); c = pele()
        ip = PEITO_IDX[np.argmin(c[PEITO_IDX, 2])]; iv = VENTRE_IDX[np.argmin(c[VENTRE_IDX, 2])]
        zp, yp, zv, yv = c[ip, 2], c[ip, 1], c[iv, 2], c[iv, 1]
        A = np.array([[1, (yp - PIVO.y)], [1, (yv - PIVO.y)]]); d = np.linalg.solve(A, [alvo_peito - zp, alvo_ventre - zv])
        DEIT["dz"] += max(-0.15, min(0.15, float(d[0]))); DEIT["pitch"] += max(R(-4), min(R(4), float(d[1])))
# deitado: o corpo descansa sobre as patas dobradas -> alvo do peito/ventre ajustado ate a pele das patas tocar o chao
AL = [0.28, 0.28]                                                    # o tronco apoia sobre as patas dobradas (~0,28 u de espessura)
for _r in range(2):
    mirar_patas(c_deitado_pose, PATAS, FK_DEIT); calibrar_deitado(*AL)
    mirar_patas(c_deitado_pose, PATAS, FK_DEIT); _aplicar(c_deitado_pose)
    _c = pele(); _zp = min(float(_c[PERNA_IDX[k_], 2].min()) for k_ in PATAS)
    print("DEITADO it", _r, "alvo", [round(a_, 3) for a_ in AL], "pernas z min", round(_zp, 3), "peito", round(float(_c[PEITO_IDX, 2].min()), 3), "ventre", round(float(_c[VENTRE_IDX, 2].min()), 3))
print("CALIB deitado dz", round(DEIT["dz"], 3), "pitch", round(math.degrees(DEIT["pitch"]), 2))
# ajoelhado: ombro na altura natural (antebraco ~vertical sobre o carpo no chao); a descida mantem a altura do quadril
YQ = BD["CoxaE"].head_local.y - PIVO.y
H_AJ = 0.085 + BD["AntebracoE"].length * 0.97 + BD["BracoE"].length * 0.55
lo_, hi_ = R(0), R(45)
for _ in range(18):
    AJ["pitch"] = (lo_ + hi_) / 2; AJ["dz"] = -YQ * math.sin(AJ["pitch"]); _corpo(pose_ajoelhado)
    if PB["BracoE"].head.z > H_AJ: lo_ = AJ["pitch"]
    else: hi_ = AJ["pitch"]
AJ["dz"] = -YQ * math.sin(AJ["pitch"])
mirar_patas(pose_ajoelhado, DIANT, FK_AJ); _aplicar(pose_ajoelhado); _c = pele()
print("CALIB ajoelhado pitch", round(math.degrees(AJ["pitch"]), 2), "dz", round(AJ["dz"], 3), "ombro z alvo", round(H_AJ, 3),
      "dianteiras z min", round(min(float(_c[PERNA_IDX[k_], 2].min()) for k_ in DIANT), 3), "peito z", round(float(_c[PEITO_IDX, 2].min()), 3))
_aplicar(c_deitado_pose); _bd = {k_: PB[k_].head.copy() for k_ in PATAS}
_aplicar(pose_ajoelhado); _ba = {k_: PB[k_].head.copy() for k_ in DIANT}
BOL.update({"deit": _bd, "aj": _ba})
for k_ in PATAS: PB[PATAS[k_][1]].constraints["IK"].influence = 1.0; _cop(k_).influence = 1.0
zerar(); bpy.context.view_layer.update()
R0b, Z0b, _p, _e = c_repouso(0.0)
def com_repouso(r, rz, k):
    for n_, l in R0b.items(): r[n_] = r.get(n_, []) + [(e, a * k) for e, a in l]
    return rz + Z0b * k
# ---------------------------------------------------------------- Deitar (4,2 s)
DUR_DEITAR = 4.2
def c_deitar(t):
    r = {}; ext = {"dobra": {}, "apoio": {}}
    fa = janela3(t, 0.0, 1.6, 0.45, 0.6)                              # fareja/escolhe o lugar (cabeca baixa)
    f = {"QuartelaE": suave((t - 0.55) / 0.85), "QuartelaD": suave((t - 0.80) / 0.85),
         "QuartelaTrasE": suave((t - 1.75) / 1.25), "QuartelaTrasD": suave((t - 1.85) / 1.25)}
    for k_, v_ in f.items():
        if v_ > 0: ext["dobra"][k_] = (v_, V((0, 0, 0)))
        ext["apoio"][k_] = v_ <= 0
    bk = suave((t - 0.70) / 0.95); bl = suave((t - 1.80) / 1.35); ext["wl"] = bl
    dz = corpo_deitado(r, bk, bl)
    r["Pescoco"] = [(X, R(22) * fa)]; r["Pescoco2"] = [(X, R(8) * fa)]
    cabeca_deitada(r, suave((t - 2.8) / 1.1))
    r["Pelve"] = [(X, R(-3) * janela3(t, 1.8, 3.3, 0.4, 0.6))]
    return r, com_repouso(r, V((0, 0, dz)), 1 - suave(t / 0.6)), {}, ext
# ---------------------------------------------------------------- Deitado (laco 6 s)
def c_deitado(t):
    r, rz, pes, ext = c_deitado_pose(); b = onda(t, 3.0)
    r["Coluna1"] = [(X, R(0.6) * b)]; r["Coluna2"] = [(X, R(-0.8) * b)]
    r["Pescoco"] = r["Pescoco"] + [(Z, R(4) * onda(t, 6.0)), (X, R(1.0) * b)]
    r["Cabeca"] = r["Cabeca"] + [(Z, R(3) * onda(t, 6.0, 0.08)), (X, R(-0.8) * b)]
    oE = pulso(t, 6.0, 1.0, 0.5); oD = pulso(t, 6.0, 3.7, 0.5)
    r["OrelhaE"] = [(Z, R(-22) * oE)]; r["OrelhaD"] = [(Z, R(22) * oD)]
    r["Cauda2"] = [(Z, R(8) * pulso(t, 6.0, 4.6, 0.4) * math.sin(6 * math.pi * ((t - 4.6) % 6.0) / 0.4))]
    return r, rz, pes, ext
# ---------------------------------------------------------------- Levantar (3,6 s): traseiras primeiro
DUR_LEVANTAR = 3.6
def c_levantar(t):
    r = {}; ext = {"dobra": {}, "apoio": {}}
    bal = janela3(t, 0.0, 1.4, 0.4, 0.5)
    f = {"QuartelaTrasE": 1 - suave((t - 0.45) / 0.85), "QuartelaTrasD": 1 - suave((t - 0.55) / 0.85),
         "QuartelaE": 1 - suave((t - 1.55) / 0.85), "QuartelaD": 1 - suave((t - 1.80) / 0.85)}
    for k_, v_ in f.items():
        if v_ > 0: ext["dobra"][k_] = (v_, V((0, 0, 0)))
        ext["apoio"][k_] = v_ <= 0
    sobe_tras = suave((t - 0.50) / 0.95); sobe_frente = suave((t - 1.65) / 1.05)
    bl = 1 - sobe_tras; bk = sobe_tras * (1 - sobe_frente); ext["wl"] = bl
    dz = corpo_deitado(r, bk, bl)
    cabeca_deitada(r, 1 - suave((t - 0.15) / 0.6))
    r["Pescoco"] = r.get("Pescoco", []) + [(X, R(16) * bal - R(8) * janela3(t, 1.6, 2.9, 0.4, 0.6))]
    return r, com_repouso(r, V((0, -0.03 * bal, dz)), suave((t - (DUR_LEVANTAR - 0.6)) / 0.6)), {}, ext
CLIPES.update({"Deitar": (c_deitar, DUR_DEITAR, False, 0.0, None, 0.0), "Deitado": (c_deitado, 6.0, True, 0.0, None, 0.0),
               "Levantar": (c_levantar, DUR_LEVANTAR, False, 0.0, None, 0.0)})
