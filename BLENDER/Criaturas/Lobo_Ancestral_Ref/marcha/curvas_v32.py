# Curvas v32 (16/11/2026). Usuario (video do Studio 15/11): "ao virar deve ser mais natural, em vez de parar para virar,
# poder virar andando, e suas patas ficam estranhas ao virar".
# Carregado por exec() dentro de anim_lobo.py com LOBO_MARCHA30=1 LOBO_CURVAS=1 (depois da marcha v30). Acrescenta:
#   AndarCurvaE / AndarCurvaD - o Andar v30 andando em curva (o JOGO gira o modelo a GIRO graus/s em volta de O_GIRO e avanca
#     a v do Andar). Cada pata APOIADA fica parada no chao do mundo (posicao E direcao: no referencial do corpo ela recua num
#     arco e gira -GIRO*t); no ar ela vai do ponto de saida ao de pouso e ja pousa virada para dentro da curva. Corpo: coluna
#     dobrada para dentro, cabeca olhando a curva, leve inclinacao para dentro, cauda de contrapeso.
#   VirarE / VirarD (r2) - o giro de 90 graus no lugar com as PATAS girando junto (r1 movia as patas no circulo mas elas
#     continuavam apontando para a frente antiga: ao fim do giro ficavam 90 graus tortas em relacao ao corpo).
# Nada aprovado e alterado: Andar, Trote, Corrida e os demais clipes sao os mesmos (so leitura de marcha29/ANDAR29).
GIRO = float(os.environ.get("LOBO_CURVA_GIRO", "30"))                 # graus/s no Andar -> raio = v/omega ~ 5,8 studs
O_GIRO = V((0.0, Y_MEIO, 0.0))                                         # centro do giro do jogo (sob o meio do corpo)
_BASE_ANDAR = marcha29(**ANDAR29)
_T, _AP, _FA = ANDAR29["T"], ANDAR29["apoio"], ANDAR29["fases"]
_V = vel29(ANDAR29); _TS = _AP * _T
def _mj(w): return w * w * w * (10 - 15 * w + 6 * w * w)
def _curva_local(M, tau, om):
    """posicao no referencial do corpo, no instante tau (s, relativo ao meio do apoio), de um ponto FIXO NO MUNDO que no
    meio do apoio estava em M; o corpo avanca a _V para -Y e gira om rad/s (+ = esquerda) em volta de O_GIRO."""
    if abs(om) < 1e-9: return M + V((0, _V * tau, 0))
    th = om * tau
    P = V(((_V / om) * (1 - math.cos(th)), -(_V / om) * math.sin(th), 0.0))
    d = M - O_GIRO - P
    return O_GIRO + V((math.cos(-th) * d.x - math.sin(-th) * d.y, math.sin(-th) * d.x + math.cos(-th) * d.y, d.z))
def andar_curva(sinal):
    om = math.radians(GIRO) * sinal
    meio = {}
    for k in PES:                                                      # ponto do meio do apoio (marcha reta, com a correcao do jarrete)
        tm = ((_FA[k] + _AP / 2) % 1.0) * _T; meio[k] = _BASE_ANDAR(tm)["pes"][k][0].copy()
    def delta(k, tau):
        M = meio[k]; return _curva_local(M, tau, om) - (M + V((0, _V * tau, 0)))
    def f(t):
        p = _BASE_ANDAR(t); u = (t / _T) % 1.0; yaw = {}
        for k in PES:
            bola, incl, dedo = p["pes"][k]; uk = (u - _FA[k]) % 1.0
            if uk < _AP:
                tau = (uk / _AP - 0.5) * _TS; d = delta(k, tau); y_ = -math.degrees(om * tau)
            else:
                w = _mj((uk - _AP) / (1 - _AP))
                d = delta(k, _TS / 2).lerp(delta(k, -_TS / 2), w)
                y_ = lerp(-math.degrees(om * _TS / 2), math.degrees(om * _TS / 2), w)
            p["pes"][k] = (bola + V((d.x, d.y, 0.0)), incl, dedo); yaw[k] = y_
        p["yaw_pe"] = yaw; p["yaw_dedos"] = True
        s = sinal                                                      # corpo na curva (graus; + = para a esquerda)
        somar_ossos(p["ossos"], {"Coluna1": {"Z": 1.5 * s}, "Coluna2": {"Z": 2.0 * s}, "Peito": {"Z": 2.0 * s},
                                 "Pescoco1": {"Z": 4.0 * s}, "Pescoco2": {"Z": 2.0 * s}, "Cabeca": {"Z": 3.0 * s}})
        for i, nm in enumerate(CAUDA): somar_ossos(p["ossos"], {nm: {"Z": -2.5 * s * (i + 1) / NC}})
        p["raiz"][4] += 1.5 * s                                        # inclina para dentro da curva
        return p
    return f
def virar_r2(sinal, dur=2.4):
    """= virar() (r1) + cada pata gira junto com o proprio passo (yaw_pe = parte do giro ja feita por ela)"""
    ordem = (["MaoE", "MetatarsoD", "MaoD", "MetatarsoE"] if sinal > 0 else ["MaoD", "MetatarsoE", "MaoE", "MetatarsoD"]) * 4
    jan = [(0.02 + 0.0595 * i, 0.02 + 0.0595 * i + 0.11) for i in range(16)]
    ANG = 90.0 * sinal; piv = V((0, Y_MEIO, 0))
    def girado(v, ang): return piv + Matrix.Rotation(rad(ang), 3, "Z") @ (v - piv)
    def f(t):
        u = t / dur; p = pose_base(); prog = {}; yaw = {}
        for k in PES:
            feitos, alt, inc = 0.0, 0.0, 0.0
            for i, kk in enumerate(ordem):
                if kk != k: continue
                a0, a1 = jan[i]; x_ = max(0.0, min(1.0, (u - a0) / (a1 - a0)))
                feitos += suave(x_); alt = max(alt, 0.32 * math.sin(math.pi * x_)); inc = max(inc, 22 * math.sin(math.pi * x_))
            prog[k] = feitos
            p["pes"][k] = (girado(B0[k], ANG / 4 * feitos) + V((0, 0, alt)), inc, 0.0)
            yaw[k] = ANG / 4 * feitos
        psi = ANG / 4 * sum(prog.values()) / 4
        p["raiz"] = [0, 0, -0.06 * math.sin(math.pi * u), 0, 0, psi]
        p["yaw_pe"] = yaw; p["yaw_dedos"] = True
        lat = 10 * sinal * math.sin(math.pi * u)
        p["ossos"] = {"Pescoco1": {"Z": lat * 0.8}, "Cabeca": {"Z": lat * 0.6}, "Coluna2": {"Z": lat * 0.3}, "Peito": {"Z": lat * 0.3}}
        for i, nm in enumerate(CAUDA): p["ossos"][nm] = {"Z": -lat * 0.6 * (i + 1) / NC}
        return p
    return f
CLIPES["AndarCurvaE"] = (andar_curva(+1), _T, True, _V, {})
CLIPES["AndarCurvaD"] = (andar_curva(-1), _T, True, _V, {})
CLIPES["VirarE"] = (virar_r2(+1), 2.4, False, 0.0, {"GiroCompleto": 2.35})
CLIPES["VirarD"] = (virar_r2(-1), 2.4, False, 0.0, {"GiroCompleto": 2.35})
ROT_RAIZ["AndarCurvaE"] = GIRO * _T; ROT_RAIZ["AndarCurvaD"] = -GIRO * _T      # graus por ciclo (o jogo gira GIRO graus/s)
