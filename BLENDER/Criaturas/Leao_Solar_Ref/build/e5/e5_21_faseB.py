# E5 Fase B: clipes de atitude agressiva e de ataque (MOVIMENTO apenas: sem poderes, dano, alcance ou VFX; nomes neutros ate o kit
# ser aprovado). Carregado por exec() dentro de e5_20_clipes.py (usa suave, janela, rampa, mist, R, V, MARCHA, CLIPES...).
# Convencoes: x+ = lado direito (DD/TD), frente = -Y; corpo "y" = tronco para a frente; "labio" em studs (0..0,32); "mand" em rad (abre +).
def base_foco(t, fase, T=3.4):
    """repouso firme, sem olhar em volta: base das acoes"""
    c = corpo_base(); b = resp(t, T)
    c.update(resp=b, z=0.03 * b, col_pitch=R(0.6) * b, pesc=R(-1.0) * b, cauda_base=R(4), cauda_amp=R(3), cauda_f=1 / 3.4)
    return c
def pulso(t, a, b): return math.sin(math.pi * min(max((t - a) / (b - a), 0.0), 1.0))       # 0 -> 1 -> 0 entre a e b
def vel_pulso(t, a, b, dist): return dist * math.pi / (2 * (b - a)) * pulso(t, a, b)        # integral = dist
# ------------------------------------------------------------------ 1. alerta a ameaca
def c_alerta(t, fase):
    c = base_foco(t, fase); f = rampa(t, 0.25, 0.6)
    c.update(z=c["z"] + 0.10 * f, y=-0.15 * f, pesc=c["pesc"] + R(-14) * f, cab_pitch=R(6) * f, orelha=(R(-18) * f, R(-18) * f), palp=R(8) * f,
             cauda_amp=R(3) * (1 - f) + R(1) * f, col_pitch=c["col_pitch"] * (1 - 0.8 * f))                      # firma: para de respirar fundo
    c["cauda_base"] = R(4) + R(10) * janela(t, 1.15, 1.6, 0.08, 0.25)                                            # piparote da cauda
    c["palp"] -= R(42) * piscar(t, (1.9,), 0.14)
    return c
# ------------------------------------------------------------------ 2. intimidacao (postura, cauda, orelhas, dentes aos poucos)
def c_intimidacao(t, fase):
    c = c_alerta(t + 2.0, fase); i = rampa(t, 0.3, 1.4); d = rampa(t, 0.7, 2.4)
    c.update(z=c["z"] - 0.45 * i, y=0.30 * i, pitch=R(2.0) * i, pesc=R(-14) * (1 - i) + R(12) * i, cab_pitch=R(6) * (1 - i) + R(-2) * i,
             orelha=(R(-18) * (1 - i) + R(26) * i, R(-18) * (1 - i) + R(26) * i), palp=R(8) * (1 - i) + R(-14) * i,
             labio=0.30 * d, mand=R(9) * rampa(t, 1.4, 2.6) + R(1.5) * math.sin(2 * math.pi * 5 * t) * rampa(t, 2.0, 2.6),
             cauda_base=R(10) * i, cauda_amp=R(4) + R(16) * i, cauda_f=1.15)
    c["col_pitch"] += R(0.35) * math.sin(2 * math.pi * 9 * t) * rampa(t, 2.0, 2.6)                             # rosnado no peito
    return c
# ------------------------------------------------------------------ 3. rosnado (loop): boca semiaberta, labios, peito vibrando
def c_rosnado(t, fase):
    c = base_foco(t, fase, T=1.5); ex = 0.5 + 0.5 * math.cos(2 * math.pi * t / 1.5)                            # expira (rosna) / inspira curta
    c.update(z=-0.35 + 0.04 * c["resp"], y=0.25, pitch=R(1.5), pesc=R(12), cab_pitch=R(-2) + R(1.2) * math.sin(2 * math.pi * t / 1.5), orelha=(R(24), R(24)),
             palp=R(-14), labio=0.26 + 0.04 * ex, mand=R(8) + R(3) * ex + R(1.2) * math.sin(2 * math.pi * 6 * t), lingua=R(4),
             cauda_base=R(8), cauda_amp=R(12), cauda_f=1 / 1.5)
    c["col_pitch"] += R(0.4) * math.sin(2 * math.pi * 9 * t) * ex; c["z"] += 0.012 * math.sin(2 * math.pi * 9 * t) * ex
    return c
# ------------------------------------------------------------------ 4. rugido completo
def c_rugido(t, fase):
    c = base_foco(t, fase); ins = janela(t, 0.45, 1.55, 0.7, 0.2); ant = janela(t, 1.3, 1.75, 0.2, 0.15)
    rug = janela(t, 1.55, 3.25, 0.18, 0.35); gr = sum(janela(t, a, a + 0.32, 0.08, 0.18) * k for a, k in ((3.25, 0.6), (3.62, 0.42), (3.95, 0.28)))
    vib = math.sin(2 * math.pi * 7 * t) * (rug + gr)
    c.update(z=0.16 * ins - 0.12 * rug + c["z"], y=0.35 * rug + 0.15 * gr, pitch=R(2.5) * rug,
             col_pitch=R(2.5) * ins - R(1.5) * rug,                                                                # torax enche na inspiracao
             pesc=R(-10) * ins + R(10) * ant + R(-4) * rug + R(4) * gr, cab_pitch=R(12) * ins - R(7) * ant + R(9) * rug + R(4) * gr + R(0.8) * vib,
             mand=R(32) * rug + R(22) * gr + R(4) * ant + R(0.8) * vib, lingua=R(14) * rug + R(8) * gr, labio=0.22 * rug + 0.12 * gr,
             palp=R(-20) * (rug + 0.6 * gr) + R(5) * ins, orelha=(R(22) * (rug + gr), R(22) * (rug + gr)),
             cauda_base=R(6) + R(8) * rug, cauda_amp=R(3) + R(6) * rug, cauda_f=0.8)
    c["cab_roll"] = R(1.2) * vib
    return c
# ------------------------------------------------------------------ 5. aproximacao furtiva (loop): peso baixo, passos lentos, olhar fixo
MARCHA["furtiva"] = dict(f=60 / 96, beta=0.70, off={"TE": 0.0, "DE": 0.26, "TD": 0.5, "DD": 0.76}, h=(0.85, 0.65))
def c_furtiva(t, fase):
    c = corpo_base(); p = 2 * math.pi * fase
    c.update(z=-1.35 + 0.03 * math.cos(2 * p), col1=R(3), col2=R(-3.5), roll=R(0.8) * math.sin(p), col_yaw=R(1.5) * math.sin(p + 0.6),
             pesc=R(22), cab_pitch=R(15), orelha=(R(-16), R(-16)), palp=R(-6), cauda_base=R(9), cauda_amp=R(2.5), cauda_f=2.2)   # ponta da cauda treme
    return c
# ------------------------------------------------------------------ 6. bote (alcance maximo 45 studs, aprovado em 05/11; a mira escolhe o pouso ate esse limite)
# r3 (05/11): mais impulso das traseiras. Referencias: no salto do gato a fase de lancamento dura ~0,15 s e os extensores da traseira
# disparam do quadril para o tornozelo (proximal -> distal), depois de uma preparacao que carrega o salto; o leao salta ~10-12 m (~4
# corpos), aqui limitado a 45 studs (~2 corpos). Tempos (s): 0,05-0,52 agacha fundo (traseiras dobradas, quadril rebola, mira fixa);
# 0,52-0,77 impulso (tronco avanca, dianteiras saem em 0,62/0,65, traseiras estendem e saem na ponta dos dedos em 0,73/0,75);
# 0,76-1,65 voo balistico (~7 studs de altura; traseiras saem esticadas, recolhem sob a barriga); 1,65 dianteiras pousam; 1,86 traseiras.
BOTE_DIST = 45.0; T_DEC, T_POUSO = 0.76, 1.65           # T_DEC: inicio do voo (as duas traseiras ja sairam: 0,73/0,75)
def vel_bote(t, dist=BOTE_DIST):
    V_ = dist / (0.10 + (1.58 - 0.77) + 0.10)                                   # integral: rampa de 0,20 s, cruzeiro, freio de 0,20 s
    return V_ * (rampa(t, 0.57, 0.77) - rampa(t, 1.58, 1.78))
def altura_bote(dist): return 7.0 * min(1.0, 0.45 + 0.55 * dist / BOTE_DIST)   # mira mais perto: arco mais baixo, mesmo tempo de voo
def c_bote(t, fase, dist=BOTE_DIST):
    c = base_foco(t, fase); ag = janela(t, 0.05, 0.80, 0.42, 0.26); emp = pulso(t, 0.52, 0.95)
    s_ = min(max((t - T_DEC) / (T_POUSO - T_DEC), 0.0), 1.0); voo = 4 * s_ * (1 - s_) if T_DEC < t < T_POUSO else 0.0   # parabola do voo
    ate = janela(t, T_POUSO - 0.04, 2.6, 0.16, 0.7)
    # r4 (05/11): o usuario pediu para abaixar mais antes do bote: agachamento de 1,9 para 2,9 studs (3,2 encostava o peito no chao)
    c.update(z=-2.9 * ag + altura_bote(dist) * voo - 1.4 * ate, y=-1.5 * ag + 0.3 * emp,             # agacha fundo recuando o quadril sobre as traseiras
             pitch=R(-2.5) * ag - R(11) * pulso(t, 0.55, 1.05) + R(9) * pulso(t, 1.30, 1.85),         # quadril mais baixo (traseiras carregadas), nariz sobe no impulso
             col1=R(8) * ag - R(9) * emp + R(5) * ate, col2=R(-9) * ag + R(10) * emp - R(6) * ate,    # coluna dobra (carrega) e estende (lanca)
             roll=R(2.4) * math.sin(2 * math.pi * 4.5 * t) * janela(t, 0.18, 0.50, 0.08, 0.08),        # o quadril "rebola" antes do salto
             pesc=R(22) * ag + R(-6) * voo + R(12) * ate, cab_pitch=R(12) * ag + R(3) * voo + R(-4) * ate,   # cabeca baixa, olhar no alvo
             orelha=(R(-16) * ag + R(22) * voo, R(-16) * ag + R(22) * voo), palp=R(-10) - R(6) * ag,
             mand=R(16) * pulso(t, 1.25, 1.85) + R(6) * rampa(t, 1.9, 2.6), labio=0.22 * pulso(t, 1.15, 1.9),
             cauda_base=R(16) * ag + R(10) * emp + R(18) * voo + R(16) * ate, cauda_amp=R(5) * ag + R(2), cauda_f=1.0)   # cauda equilibra e nao toca o chao
    c["z"] += 0.07 * math.sin(2 * math.pi * t / 0.9) * rampa(t, 2.3, 2.8)                                        # respiracao pesada depois
    return c
def _bote_dian(t0, t1, k):
    """k = +1 (DD) / -1 (DE). via_ombro: pata em relacao ao OMBRO no meio do balanco (repouso: ~(0,24, -0,8, -7,6));
    via: caminho no mundo que segura a decolagem e o pouso no chao"""
    via = [(0.14, V((0, 0.5, 1.3))), (0.45, V((0, -3.4, 2.0))), (0.82, V((0, -1.6, 1.3)))]
    ombro = [(0.08, V((0.24 * k, -0.2, -6.7))), (0.18, V((0.22 * k, 0.2, -5.6))), (0.32, V((0.21 * k, -2.6, -5.6))), (0.52, V((0.20 * k, -4.8, -5.9))),
             (0.84, V((0.22 * k, -3.4, -6.9)))]
    punho = [(0.0, 20), (0.12, 42), (0.28, 12), (0.45, -8), (0.75, -6), (0.92, 6), (1.0, 0)]
    dedos = [(0.0, 0), (0.12, 14), (0.35, 0), (0.70, -12), (0.92, -8), (1.0, 0)]
    return [dict(t0=t0, t1=t1, rel=dict(via=via, via_ombro=ombro, punho=punho, dedos=dedos, escapula=0.40, alcance_suave=True))]
def _bote_tras(t0, t1):
    """impulso: calcanhar sobe ate 62 graus nos ultimos 0,28 s do apoio (empurra na ponta dos dedos) e a perna sai esticada atras;
    via_quadril: deltas sobre o vetor quadril->pata do repouso (x, y+ = para tras, z+ = para cima)"""
    quad = [(0.04, V((0, 3.0, 0.9))), (0.14, V((0, 3.2, 1.8))), (0.28, V((0, 2.0, 3.3))), (0.48, V((0, -1.0, 3.9))), (0.78, V((0, -1.2, 1.6)))]
    jarrete = [(0.0, 30), (0.12, 38), (0.32, -15), (0.52, -32), (0.80, -6), (1.0, 0)]   # graus: + abre (perna esticada atras), - fecha (recolhe)
    return [dict(t0=t0, t1=t1, empurra=62, t_emp=0.28, via=[(0.5, V((0, 0.0, 2.5)), None)], via_quadril=quad, solta_q=0.08, jarrete=jarrete)]
AG_BOTE = {"DD": _bote_dian(0.62, T_POUSO, 1), "DE": _bote_dian(0.65, T_POUSO + 0.04, -1), "TD": _bote_tras(0.75, 1.86), "TE": _bote_tras(0.73, 1.90)}
# ------------------------------------------------------------------ 7. patada dianteira (apoio nas outras tres, transferencia de massa)
# r2 (05/11): a versao 1 orientava o metacarpo por angulo no mundo e o punho dobrava ~155 graus e torcia ao erguer/golpear (ver
# e5_20 posar_golpe). Agora: caminho Hermite com tempos reais, punho e dedos so em flexao relativa, cotovelo como dobradica.
# Tempos (s): 0-0,32 peso para as outras tres e peito/escapula iniciam; 0,32 decola; 0,76 armada (maior elevacao, pausa curta);
# 0,90 contato (golpe rapido em diagonal para dentro); 0,98 seguimento curto; 1,36 pousa macio a frente.
T_PAT = (0.32, 1.36); T_CONT = 0.90
def c_patada(lado):
    sg = 1 if lado == "D" else -1
    def f(t, fase):
        c = base_foco(t, fase); w = janela(t, 0.06, 1.62, 0.26, 0.42)            # peso nas outras tres (lado oposto e para tras)
        er = pulso(t, 0.24, 0.86); g = pulso(t, 0.78, 1.08); imp = janela(t, T_CONT - 0.01, T_CONT + 0.14, 0.02, 0.11)   # ergue / golpe / impacto
        c.update(x=-0.45 * sg * w, y=-0.35 * w + 0.55 * g, z=0.05 * er - 0.10 * imp, pitch=R(-1.5) * w - R(1.5) * er + R(6) * g + R(1.5) * imp,
                 roll=-sg * R(3) * w, peito_roll=-sg * R(3) * er + sg * R(2) * g, col_yaw=-sg * R(3) * er + sg * R(5) * g,
                 pesc=R(8) * w + R(3) * imp, pesc_yaw=sg * R(6) * w, cab_pitch=R(-3) * w - R(2) * imp, orelha=(R(22) * w, R(22) * w), palp=R(-14) * w - R(6) * imp,
                 labio=0.26 * w, mand=R(9) * w + R(6) * g, cauda_base=R(8) * w, cauda_amp=R(10) * w, cauda_f=1.1, cauda_yaw=-sg * R(10) * g)
        return c
    return f
def ag_patada(lado):
    """pata de ataque: offsets locais (x+ = para fora no lado D; frente = -Y) somados ao ponto de repouso da pata.
    punho = flexao palmar relativa ao antebraco (graus; + = almofadas para tras, 0 = alinhado, - = extensao); dedos: + fecha, - abre (garras)"""
    sg = 1 if lado == "D" else -1; p_ = "D" + lado
    via = [(0.14, V((0.15 * sg, 0.3, 1.8))),                      # decola: sobe junto ao corpo, punho dobrando
           (0.30, V((0.80 * sg, -1.6, 4.8))),                     # sobe a frente e para fora (fora da juba)
           (0.42, V((1.00 * sg, -2.6, 6.6)), True),               # armada: maior elevacao (altura do queixo), pausa curta
           (0.555, V((0.25 * sg, -5.0, 3.0))),                    # contato: diagonal para baixo e para dentro, rapido
           (0.64, V((-0.30 * sg, -4.7, 1.6)), True),              # seguimento curto e para
           (0.82, V((-0.05 * sg, -2.6, 1.0)))]                    # recolhe baixo e volta ao chao
    # r3: com 75-84 graus de flexao mantidos na subida a pele do punho vincava (pata "contorcida" no close); limite ~40 graus
    punho = [(0.0, 20), (0.14, 38), (0.30, 40), (0.42, 36), (0.50, 14), (0.555, -4), (0.64, 6), (0.82, 22), (0.93, 8), (1.0, 0)]
    dedos = [(0.0, 0), (0.14, 6), (0.42, 5), (0.50, -20), (0.60, -22), (0.70, 4), (0.85, 5), (1.0, 0)]
    return {p_: [dict(t0=T_PAT[0], t1=T_PAT[1], alvo=V((0, -0.9, 0)), rel=dict(via=via, punho=punho, dedos=dedos, escapula=0.45))]}
# ------------------------------------------------------------------ 8. mordida (aproximacao, fechamento, recuo)
def c_mordida(t, fase):
    c = base_foco(t, fase); ap = janela(t, 0.25, 0.85, 0.35, 0.12); ab = janela(t, 0.32, 0.79, 0.3, 0.04); sac = janela(t, 0.80, 1.18, 0.04, 0.12)
    rec = janela(t, 1.15, 1.9, 0.2, 0.45)
    c.update(y=0.95 * ap + 0.3 * sac - 0.4 * rec, z=-0.55 * ap - 0.25 * sac, pitch=R(4) * ap, pesc=R(12) * ap - R(5) * rec, cab_pitch=R(4) * ap + R(3) * sac,
             mand=R(30) * ab + R(3) * sac + R(6) * rec * (1 - rampa(t, 1.6, 1.95)), labio=0.30 * (ab + sac) + 0.1 * rec, lingua=R(6) * ab,
             palp=R(-18) * (ap + sac), orelha=(R(24) * (ap + sac + rec), R(24) * (ap + sac + rec)), cauda_base=R(8), cauda_amp=R(8), cauda_f=1.2)
    c["cab_yaw"] = R(7) * math.sin(2 * math.pi * 5.5 * (t - 0.8)) * sac; c["cab_roll"] = R(5) * math.sin(2 * math.pi * 5.5 * (t - 0.8) + 0.8) * sac   # sacode
    return c
AG_MORDIDA = {"DD": [dict(t0=0.36, t1=0.66, h=0.9), dict(t0=1.22, t1=1.48, h=0.6)], "DE": [dict(t0=0.43, t1=0.72, h=0.9), dict(t0=1.28, t1=1.55, h=0.6)],
              "TD": [dict(t0=0.50, t1=0.80, h=0.7), dict(t0=1.36, t1=1.62, h=0.5)], "TE": [dict(t0=0.55, t1=0.85, h=0.7), dict(t0=1.40, t1=1.66, h=0.5)]}
# ------------------------------------------------------------------ 9. esquiva curta lateral e recuperacao
def c_esquiva(lado):
    sg = -1 if lado == "E" else 1
    def f(t, fase):
        c = base_foco(t, fase); ag = janela(t, 0.0, 0.30, 0.2, 0.06); voo = pulso(t, 0.30, 0.74); ate = janela(t, 0.72, 1.45, 0.06, 0.5)
        c.update(z=-0.9 * ag + 0.9 * voo - 0.8 * ate, x=-0.25 * sg * ag, roll=sg * R(6) * voo - sg * R(3) * ate, col_yaw=-sg * R(5) * voo,
                 pesc=R(10) * (ag + ate), cab_yaw=-sg * R(8) * voo, orelha=(R(24) * (ag + voo), R(24) * (ag + voo)), palp=R(-10),
                 labio=0.16 * (voo + ate), mand=R(6) * voo, cauda_base=R(6), cauda_yaw=-sg * R(22) * voo, cauda_amp=R(4), cauda_f=1.0)
        return c
    return f
AG_ESQ = {p_: [dict(t0=t0, t1=t1, h=h)] for p_, t0, t1, h in (("DD", 0.30, 0.70, 1.3), ("DE", 0.30, 0.70, 1.3), ("TD", 0.34, 0.76, 1.1), ("TE", 0.34, 0.76, 1.1))}
# ------------------------------------------------------------------ 10. fadiga leve e recuperacao (apos sequencia intensa)
_FAD_T = np.arange(0, 6.0, 1 / 300); _FAD_F = 0.4 + 0.95 * np.array([1 - rampa(x, 0.4, 4.4) for x in _FAD_T])
_FAD_PH = np.concatenate([[0.0], np.cumsum(_FAD_F[:-1]) / 300]) * 2 * math.pi                 # fase do ofego: frequencia cai de 1,35 para 0,4 Hz
def c_fadiga(t, fase):
    c = corpo_base(); k = 1 - rampa(t, 0.4, 4.4); b = math.sin(float(np.interp(t, _FAD_T, _FAD_PH)))
    c.update(resp=b, z=-0.25 * k + (0.08 * k + 0.035) * b, col_pitch=(R(1.8) * k + R(0.7)) * b, pesc=R(12) * k + R(2), cab_pitch=R(-6) * k,
             mand=(R(7) * k + R(0.5)) * (0.6 + 0.4 * b), lingua=R(10) * k, palp=R(-12) * k + R(-3), orelha=(R(8) * k, R(8) * k),
             cauda_base=R(2), cauda_amp=R(3), cauda_f=0.35)
    return c
FB = {
    "Alerta_Ameaca": dict(dur=2.6, loop=False, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_alerta),
    "Intimidacao": dict(dur=4.2, loop=False, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_intimidacao),
    "Rosnado": dict(dur=3.0, loop=True, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_rosnado),
    "Rugido": dict(dur=4.6, loop=False, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_rugido),
    "Aproximacao_Furtiva": dict(dur=96 / 30, loop=True, marcha=lambda t: MARCHA["furtiva"], vel=lambda t: MARCHA["furtiva"]["f"] * 6.0, rumo=lambda t: 0.0, corpo=c_furtiva),
    "Bote": dict(dur=3.0, loop=False, inicio_repouso=True, dmin_tras=0.55, agenda=AG_BOTE, marcha=lambda t: MARCHA["parado"], vel=vel_bote, rumo=lambda t: 0.0, corpo=c_bote),   # alcance maximo
    "Patada_D": dict(dur=1.9, loop=False, inicio_repouso=True, agenda=ag_patada("D"), marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_patada("D")),
    "Patada_E": dict(dur=1.9, loop=False, inicio_repouso=True, agenda=ag_patada("E"), marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_patada("E")),
    "Mordida": dict(dur=2.0, loop=False, inicio_repouso=True, agenda=AG_MORDIDA, marcha=lambda t: MARCHA["parado"],
                    vel=lambda t: vel_pulso(t, 0.34, 0.80, 5.0) - vel_pulso(t, 1.18, 1.62, 3.5), rumo=lambda t: 0.0, corpo=c_mordida),
    "Esquiva_E": dict(dur=1.6, loop=False, inicio_repouso=True, agenda=AG_ESQ, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0,
                      vel_lat=lambda t: -vel_pulso(t, 0.30, 0.74, 4.5), rumo=lambda t: 0.0, corpo=c_esquiva("E")),
    "Esquiva_D": dict(dur=1.6, loop=False, inicio_repouso=True, agenda=AG_ESQ, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0,
                      vel_lat=lambda t: vel_pulso(t, 0.30, 0.74, 4.5), rumo=lambda t: 0.0, corpo=c_esquiva("D")),
    "Fadiga_Recuperacao": dict(dur=4.8, loop=False, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_fadiga),
}
if os.environ.get("E5_BOTE_MIRA"):   # so revisao: bote com a mira mais perto (o jogo escolhe o pouso ate BOTE_DIST)
    _dm = float(os.environ["E5_BOTE_MIRA"]); FB["Bote_Mira%d" % _dm] = dict(FB["Bote"], vel=lambda t: vel_bote(t, _dm), corpo=lambda t, fase: c_bote(t, fase, _dm))
CLIPES.update(FB)
