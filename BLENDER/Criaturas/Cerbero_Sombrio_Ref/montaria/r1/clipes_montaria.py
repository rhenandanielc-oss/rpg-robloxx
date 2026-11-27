# Montaria M2 (27/11/2026): clipes do CERBERO SOMBRIO para montar/desmontar (so movimento). Decisao do usuario 27/11: o Cerbero
# DEITA para o cavaleiro subir e descer (o dorso em pe fica a ~14 studs; deitado, a sela fica a ~10, e o cavaleiro sobe pelo
# cotovelo e pelo ombro segurando a alca lateral da sela M1 aprovada).
# Reaproveita as poses do Deitar e do Levantar aprovados (pose_deitada, degrau, janelas), SEM a pose de descanso das cabecas:
# aqui ele fica alerta, e a cabeca do lado do cavaleiro olha para ele. Carregado por exec() dentro de anim_cerbero.py quando
# CERB_MONTARIA=1 (os clipes aprovados e a execucao padrao nao mudam).
# Lados como no rig: E = x- (lado da cabeca E), D = x+. sg = -1 (E) / +1 (D). Giro em Z positivo olha para x+.
# Tempos alinhados com o cavaleiro de teste (montaria/m2_demo_montaria.py):
#   Montar (8,7 s): 0,3-2,9 deita; o cavaleiro chega (0-2,4), agarra a alca (3,0), sobe pelo cotovelo e pelo ombro (3,2-5,4),
#   senta (5,9); o Cerbero absorve o peso e levanta com ele (6,5-8,7).
#   Desmontar (7,8 s): 0,3-2,9 deita com o cavaleiro; ele desce pelo ombro e pelo cotovelo segurando a alca (3,0-4,9);
#   levanta (5,6-7,8).
T0D_M = 0.3
HOLD_MONTAR, HOLD_DESMONTAR = 3.6, 2.7
DUR_MONTAR = T0D_M + DUR_DEITAR + HOLD_MONTAR + DUR_LEVANTAR
DUR_DESMONTAR = T0D_M + DUR_DEITAR + HOLD_DESMONTAR + DUR_LEVANTAR
def _deita_m(t):
    """c_deitar sem a pose de descanso das cabecas (fica alerta)"""
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}
    passo, alt = degrau(t, 0.15, 0.75)
    kt = suave((t - 0.55) / 1.25); kd = suave((t - 0.70) / 1.55); kf = suave((t - 1.05) / 1.25)
    z = pose_deitada(r, pes, ext, kd, kt, kf, passo, alt)
    for k_ in PATAS: ext["apoio"][k_] = not (k_.startswith("Mao") and 0.15 < t < 0.75)
    for kk, at in (("C", 0.0), ("E", 0.12), ("D", 0.22)):
        b_ = janela(t, 0.3 + at, 1.6 + at, 0.4, 0.5)
        r["Pescoco%s1" % kk] = r["Pescoco%s1" % kk] + [(S[kk], -R(8) * b_)]
    return r, V((0, 0.35 * kd, BASE_Z + z + 0.25 * kd)), pes, ext
def _deitado_m():
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {k_: True for k_ in PATAS}}
    z = pose_deitada(r, pes, ext, 1.0, 1.0, 1.0, 1.0)
    return r, V((0, 0.35, BASE_Z + z + 0.25)), pes, ext
def _levanta_m(t):
    """c_levantar sem a pose de descanso das cabecas"""
    r = {}; pes = {}; ext = {"rot_pe": {}, "apoio": {}}
    kf = 1 - suave(t / 0.85); kd = 1 - suave((t - 0.25) / 1.15); kt = 1 - suave((t - 0.55) / 1.05)
    passo, alt = degrau(t, 1.25, 1.85); passo = 1 - passo
    z = pose_deitada(r, pes, ext, kd, kt, kf, passo, alt)
    for k_ in PATAS: ext["apoio"][k_] = not (k_.startswith("Mao") and 1.25 < t < 1.85)
    for kk, at in (("C", 0.0), ("E", 0.08), ("D", 0.14)):
        b_ = janela(t, 0.1 + at, 1.4 + at, 0.3, 0.5)
        r["Pescoco%s1" % kk] = r["Pescoco%s1" % kk] + [(S[kk], R(8) * b_)]
    r["Coluna3"] = r["Coluna3"] + [(X, -R(5) * janela(t, 0.0, 1.2, 0.3, 0.5))]
    return r, V((0, 0.35 * kd, BASE_Z + z + 0.25 * kd)), pes, ext
def _fase(t, hold):
    td = t - T0D_M
    if td < DUR_DEITAR: return _deita_m(max(td, 0.0))
    if td < DUR_DEITAR + hold: return _deitado_m()
    return _levanta_m(td - DUR_DEITAR - hold)
def _olhar(r, sg, k, k_c=0.45):
    """cabeca do lado do cavaleiro vira e abaixa um pouco para ele; a central acompanha; a do outro lado vigia"""
    kk = "D" if sg > 0 else "E"; ko = "E" if sg > 0 else "D"
    r["Pescoco%s1" % kk] = r["Pescoco%s1" % kk] + [(Z, sg * R(26) * k), (S[kk], -R(6) * k)]
    r["Cabeca" + kk] = r.get("Cabeca" + kk, []) + [(Z, sg * R(16) * k), (S[kk], -R(4) * k)]
    r["PescocoC1"] = r["PescocoC1"] + [(Z, sg * R(12) * k * k_c / 0.45)]
    r["CabecaC"] = r.get("CabecaC", []) + [(Z, sg * R(8) * k * k_c / 0.45)]
    r["Pescoco%s1" % ko] = r["Pescoco%s1" % ko] + [(Z, -sg * R(6) * k)]          # a do outro lado olha para fora (vigia)
def c_montar_cb(sg):
    def f(t):
        r, raiz, pes, ext = _fase(t, HOLD_MONTAR)
        _olhar(r, sg, janela(t, 0.2, 7.2, 0.6, 0.8))
        puxa = janela(t, 3.2, 5.6, 0.3, 0.4)                                        # cavaleiro subindo pelo lado: rola um pouco
        senta = janela(t, 5.6, 7.0, 0.15, 0.5)
        r["Coluna2"] = r.get("Coluna2", []) + [(Y, sg * R(2.5) * puxa)]
        r["Coluna1"] = r.get("Coluna1", []) + [(Y, sg * R(1.2) * puxa)]
        return r, raiz - V((0, 0, 0.05 * puxa + 0.10 * senta)), pes, ext
    return f
def c_desmontar_cb(sg):
    def f(t):
        r, raiz, pes, ext = _fase(t, HOLD_DESMONTAR)
        _olhar(r, sg, janela(t, 2.4, 6.6, 0.6, 0.8))
        desce = janela(t, 3.0, 4.9, 0.25, 0.4)
        r["Coluna2"] = r.get("Coluna2", []) + [(Y, sg * R(2.5) * desce)]
        r["Coluna1"] = r.get("Coluna1", []) + [(Y, sg * R(1.2) * desce)]
        return r, raiz - V((0, 0, 0.04 * desce)), pes, ext
    return f
EV_MONTAR = {"deita": T0D_M, "deitado": round(T0D_M + DUR_DEITAR, 3), "agarra": 3.0, "sentado": 5.9,
             "levanta": round(T0D_M + DUR_DEITAR + HOLD_MONTAR, 3), "em_pe": round(DUR_MONTAR, 3)}
EV_DESMONTAR = {"deita": T0D_M, "deitado": round(T0D_M + DUR_DEITAR, 3), "solta_sela": 3.0, "no_chao": 4.9,
                "levanta": round(T0D_M + DUR_DEITAR + HOLD_DESMONTAR, 3), "em_pe": round(DUR_DESMONTAR, 3)}
EVENTOS_MONTARIA = {}
for lado_, sg_ in (("E", -1), ("D", 1)):
    CLIPES["Montar" + lado_] = (c_montar_cb(sg_), DUR_MONTAR, False, 0.0)
    CLIPES["Desmontar" + lado_] = (c_desmontar_cb(sg_), DUR_DESMONTAR, False, 0.0)
    EVENTOS_MONTARIA["Montar" + lado_] = EV_MONTAR; EVENTOS_MONTARIA["Desmontar" + lado_] = EV_DESMONTAR
