# ================================================================== LOTE E da Coruja-da-Floresta (17/11/2026): BEBER.
# Pedido (IA de vivencia 17/11): visita ocasional a margem da lagoa, pousa e "toca a agua com o bico". Nao havia clipe.
# Clipe MINIMO sobre o rig r4 (sem redesenhar): Repouso q0 -> agacha (pernas flexionam, tronco inclina) -> 3 goles
# (bico desce ate a linha d'agua junto dos pes e a cabeca sobe para engolir, como as aves fazem) -> volta ao Repouso q0.
# Pes plantados (IK), asas fechadas. Carregado com CORUJA_LC=1 CORUJA_LE=1. Numeros [PROPOSTA]/[A TESTAR].
# Alvo do bico (no jogo): linha d'agua ~ no plano dos pes, a frente dos dedos (a coruja para na beira da lamina rasa).
_E = lambda n, d: float(os.environ.get(n, d))
AG_C1, AG_C2 = _E("CJ_C1", 24), _E("CJ_C2", 34)            # tronco inclina (graus)
GO_P, GO_P2, GO_C = _E("CJ_P", 50), _E("CJ_P2", 20), _E("CJ_CB", 4)   # gole: pescoco/cabeca descem (graus)
AG_Z = _E("CJ_Z", -0.02)                                   # corpo desce (m): pernas flexionam
DUR_BEB_C = 5.6
GOLES_C = (1.05, 2.45, 3.85)
def c_beber_coruja(t):
    r, raiz = base_rep(); k = suave(t / 0.75) * (1 - suave((t - (DUR_BEB_C - 0.85)) / 0.85))
    dip = 0.0; eng = 0.0
    for t0 in GOLES_C:
        dip += janela(t, t0 - 0.40, t0 + 0.45, 0.32, 0.30)    # bico desce e encosta na agua
        eng += pulso(t, t0 + 0.72, 0.55)                     # ergue a cabeca para engolir
    dip = min(1.0, dip) * k; eng = min(1.0, eng) * k
    soma(r, "Coluna1", [(X, R(AG_C1) * k)]); soma(r, "Coluna2", [(X, R(AG_C2) * k)])
    soma(r, "Pescoco", [(X, R(GO_P) * dip - R(10) * eng)]); soma(r, "Pescoco2", [(X, R(GO_P2) * dip - R(6) * eng)])
    soma(r, "Cabeca", [(X, R(GO_C) * dip - R(24) * eng)])
    soma(r, "Cauda", [(X, R(_E("CJ_CAUDA", 0)) * k)])            # cauda acompanha o tronco (r2: +12 abria em leque para cima)
    for l in "ED": soma(r, "Tufo" + l, [(X, R(-10) * k)])
    palpebras(r, 0.35 * eng)                                    # olhos semicerram ao engolir
    return r, raiz + V((0, 0, AG_Z * k)), {}, {}
CLIPES.update({"Beber": (c_beber_coruja, DUR_BEB_C, False, 0.0, 0.0, "Repouso q0", "Repouso q0")})
print("LOTE_E", {"Beber": DUR_BEB_C, "goles": GOLES_C})
# medicao do bico (so leitura): ponto mais baixo da malha da cabeca e seu avanco, no meio de cada gole
def _medir_bico():
    import numpy as _np
    for t0 in GOLES_C:
        pose = QUADROS["Beber"][int(round((t0 + 0.05) * 30))]
        for pb in PB: m_ = pose[pb.name]; pb.rotation_quaternion = m_.to_quaternion(); pb.location = m_.translation
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get(); ev = CAB.evaluated_get(dg); m = ev.to_mesh()
        c = _np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); ev.to_mesh_clear(); c = c.reshape(-1, 3)
        M = CAB.matrix_world; i = int(c[:, 2].argmin()); w = M @ V(tuple(c[i]))
        dedos = {l: [round(x * 100, 1) for x in (arm.matrix_world @ PB[PES[l]].head)] for l in PES}
        print("BICO", t0, {"z_cm": round(w.z * 100, 2), "x_cm": round(w.x * 100, 2), "y_cm": round(w.y * 100, 2), "dedos_cm": dedos})
def _medir_e_soltar():
    _medir_bico(); arm.animation_data.action = None; zerar()
if os.environ.get("CJ_MEDIR"): MEDIR_BICO = _medir_e_soltar   # (17/11: a leitura no Blender nao refletiu a pose; a calibracao vale no Studio)
