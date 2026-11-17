"""QA de fases das garras (r4 x r5), 17/11/2026. Para cada variante, base e FASE DE INICIO possivel da locomocao:
golpe sobreposto como no Roblox (Action2 por cima; ossos sem chave seguem a locomocao) com o fade de entrada do jogo
(Play(0.06) = 1,8 q: peso 0 -> 1 por slerp) e fim seco no q15 (o servidor nao da Stop no fim).
Mede na pata do golpe (pontos da sola: ponta e base dos Dedos, ponta do Metacarpo; apoio = altura desses pontos no
Repouso): afundamento (altura abaixo do apoio), arrasto no mundo enquanto apoiada (deslocamento da marcha incluido:
Andar 3,0 / Trote 6,667 / Corrida 20,357 studs/s), apoio (pes no chao: composto x locomocao; perda CAUSADA pelo golpe =
quadro em que a locomocao tinha a dianteira do golpe apoiada e nenhuma dianteira fica apoiada no composto), virada VISIVEL
do pe (direcao dos dedos no chao e rolagem da sola, em relacao a locomocao no mesmo quadro), torcao AXIAL do Metacarpo e
dos Dedos (swing-twist da diferenca para a locomocao, em torno do proprio osso), salto da pata no fim (q15 -> passada) e
folga ate o alvo de ensaio (HRP 2x5x2 com centro a 8 studs do pivo, face a 7).
Saida: review/v43r5/revisao/qa_garra_r5.json + resumo (pior fase de cada variante) no console.
Uso: blender -b anim_v43r5/CR_LoboArtico_Anim.blend -P medir_garra_r5.py"""
import bpy, json, math, os
from mathutils import Vector as V
rig = bpy.data.objects["LoboArtico_Rig"]; sc = bpy.context.scene; P = rig.pose.bones; W = rig.matrix_world
VEL = {"Repouso": 0.0, "Andar": 3.0, "Trote": 6.667, "Corrida": 20.357}
FADE_Q = 1.8; FACE_ALVO_Y = -7.0
def aplicar(n, q):
    ac = bpy.data.actions[n]; rig.animation_data.action = ac
    if len(ac.slots): rig.animation_data.action_slot = ac.slots[0]
    sc.frame_set(q); bpy.context.view_layer.update(); rig.animation_data.action = None
def canais(ac):
    r = {}
    for ly in ac.layers:
        for st in ly.strips:
            for cb in st.channelbags:
                for fc in cb.fcurves: r.setdefault(fc.data_path.split('"')[1], set()).add(fc.data_path.split(".")[-1])
    return r
CH = {}
def ler(nome, q):
    for pb in P: pb.matrix_basis.identity()
    aplicar(nome, q); return {pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P}
def compor(golpe, qg, base, qb, w):
    if golpe not in CH: CH[golpe] = canais(bpy.data.actions[golpe])
    g = ler(golpe, qg); l = ler(base, qb)
    for pb in P: pb.matrix_basis.identity()
    for n, (r, t) in l.items():
        if n in CH[golpe]:
            rg = g[n][0]
            if r.dot(rg) < 0: rg = -rg
            r = r.slerp(rg, w)
            if "location" in CH[golpe][n]: t = t.lerp(g[n][1], w)
        P[n].rotation_quaternion = r; P[n].location = t
    bpy.context.view_layer.update()
    return l
def pontos(lado):
    return [W @ P["Dedos_" + lado].tail, W @ P["Dedos_" + lado].head, W @ P["Metacarpo_" + lado].tail]
for pb in P: pb.matrix_basis.identity()
aplicar("Repouso", 0)
APOIO = {l: [p.z for p in pontos(l)] for l in ("E", "D")}
APOIO_T = {l: [(W @ P["DedosPe_" + l].tail).z] for l in ("E", "D")}
def no_chao(l, tras=False):
    if tras: return (W @ P["DedosPe_" + l].tail).z < APOIO_T[l][0] + 0.03
    return min(p.z - a for p, a in zip(pontos(l), APOIO[l])) < 0.03
def pe_dir():
    d = (W.to_3x3() @ P["Dedos_E"].matrix.to_3x3()).col[1]; return d
def visivel(l):
    m = (W.to_3x3() @ P["Metacarpo_" + l].matrix.to_3x3())
    ex = m.col[0]                                                         # eixo lateral da pata: a dobra natural NAO o move
    yaw = math.degrees(math.atan2(ex.y, ex.x)) if math.hypot(ex.x, ex.y) > 0.5 else None
    roll = math.degrees(math.asin(max(-1, min(1, m.col[0].z))))
    return yaw, roll
LOCO_W = {}
def guardar_loco_w(l):
    for n in ("Metacarpo_" + l, "Dedos_" + l): LOCO_W[n] = (W.to_3x3() @ P[n].matrix.to_3x3()).to_quaternion()
def axial(l, base_rot):
    """r5c: giro que NAO e flexao: diferenca no mundo (composto x passada no mesmo quadro) sem a componente em torno do eixo
    lateral do corpo (X = dobra natural do carpo/dedos). O que sobra e virada/rolagem artificial."""
    r = {}
    for n in ("Metacarpo_" + l, "Dedos_" + l):
        cw = (W.to_3x3() @ P[n].matrix.to_3x3()).to_quaternion(); d = cw @ LOCO_W[n].inverted()
        sw, tw = d.to_swing_twist("X"); r[n] = abs(math.degrees(sw.angle)) if sw.angle <= math.pi else abs(math.degrees(2 * math.pi - sw.angle))
    return r
REL = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "ataque_v43.json")))
SINC = REL.get("sincronizacao_r5b", {})
VARIANTES = []          # (golpe, base, fases): None = todas as fases de inicio; lista = so essas
for g in ("GarraE", "GarraD"):
    VARIANTES += [("R4_" + g, "Repouso", None), (g, "Repouso", None)]
    for b in ("Andar", "Trote", "Corrida"):
        r4 = "R4_" + g + ("_Corrida" if b == "Corrida" else "")
        VARIANTES += [(r4, b, None)]
        if g + "_" + b in SINC:
            VARIANTES += [(g + "_" + b, b, [SINC[g + "_" + b]["quadro_descolamento"]]), (g + "_" + b + "|fora_de_fase", b, None)]
RES = {}
for rotulo, base, fases_ok in VARIANTES:
    golpe = rotulo.split("|")[0]
    if golpe not in bpy.data.actions: continue
    lado = "E" if "GarraE" in golpe else "D"; outra = "D" if lado == "E" else "E"
    nb = max(1, int(bpy.data.actions[base].frame_range[1])); v = VEL[base] / 30.0
    fases = fases_ok if fases_ok is not None else (range(nb) if base != "Repouso" else [0])
    por_fase = {}
    for f in fases:
        afund = 0.0; arrasto = 0.0; perda = []; arr_loco = 0.0; antl = None; yawmax = 0.0; rollmax = 0.0; axmax = 0.0; ant = None; salto = 0.0; folga = None
        for q in range(16):
            w = min(1.0, q / FADE_Q)
            loco_rot = ler(base, (f + q) % nb)
            for pb in P: pb.matrix_basis.identity()
            aplicar(base, (f + q) % nb)
            yl, rl = visivel(lado); loco_g = no_chao(lado); loco_o = no_chao(outra); guardar_loco_w(lado)
            pl = pontos(lado)[0]; myl = pl.y - v * q                       # passada SOZINHA (referencia de arrasto)
            if antl is not None and loco_g and antl[1]: arr_loco = max(arr_loco, abs(myl - antl[0]))
            antl = (myl, loco_g)
            compor(golpe, q, base, (f + q) % nb, w)
            pts = pontos(lado)
            afund = max(afund, max(a - p.z for p, a in zip(pts, APOIO[lado])))
            yc, rc = visivel(lado); rollmax = max(rollmax, abs(rc - rl))
            if yc is not None and yl is not None: yawmax = max(yawmax, abs(yc - yl))
            ax = axial(lado, loco_rot); axmax = max(axmax, max(ax.values()))
            g_chao = no_chao(lado); o_chao = no_chao(outra)
            # perda de apoio CAUSADA pelo golpe: a locomocao tinha a dianteira do golpe no chao e no composto nenhuma dianteira apoia
            if loco_g and not g_chao and not o_chao: perda.append(q)
            # arrasto: pata do golpe apoiada em dois quadros seguidos -> deslocamento no mundo (marcha anda v por quadro)
            p = pts[0]; mundo_y = p.y - v * q
            if ant is not None and g_chao and ant[1]: arrasto = max(arrasto, abs(mundo_y - ant[0]))
            ant = (mundo_y, g_chao)
            if q == 7: folga = round(p.y - FACE_ALVO_Y, 3); alt_cont = round(min(x.z for x in pts) - min(APOIO[lado]), 3)
        # fim seco: q15 do golpe -> passada no quadro seguinte
        compor(golpe, 15, base, (f + 15) % nb, 1.0); p15 = pontos(lado)[0]
        for pb in P: pb.matrix_basis.identity()
        aplicar(base, (f + 16) % nb); p16 = pontos(lado)[0]; salto = (p16 - p15).length
        for pb in P: pb.matrix_basis.identity()
        aplicar(base, (f + 15) % nb); p15l = pontos(lado)[0]; salto_loco = (p16 - p15l).length   # o que a passada sozinha anda nesse quadro
        por_fase[f] = {"afund": round(afund, 3), "arrasto": round(arrasto, 3), "perda_apoio_q": perda, "yaw_visivel": round(yawmax, 1),
                       "roll_visivel": round(rollmax, 1), "torcao_axial": round(axmax, 1), "salto_fim": round(salto, 3), "salto_fim_extra": round(max(0.0, salto - salto_loco), 3), "arrasto_passada": round(arr_loco, 3), "arrasto_extra": round(max(0.0, arrasto - arr_loco), 3),
                       "folga_alvo_contato": folga, "altura_contato": alt_cont}
    pior = max(por_fase, key=lambda k: (por_fase[k]["afund"], len(por_fase[k]["perda_apoio_q"]), por_fase[k]["arrasto"]))
    RES["%s|%s" % (rotulo, base)] = {"fases": por_fase, "pior_fase": pior}
    agg = lambda key: max(x[key] for x in por_fase.values())
    print("QA5 %-34s %-8s pior fase %2d | afund max %.3f | arrasto max %.3f | fases c/ perda de apoio %d/%d | virada %.0f rolagem %.0f giro-nao-flexao %.0f | salto fim max %.2f (extra %.2f) | arrasto extra %.2f | folga alvo %.2f alt contato %.2f" % (
        rotulo[:34], base, pior, agg("afund"), agg("arrasto"), sum(1 for x in por_fase.values() if x["perda_apoio_q"]), len(por_fase),
        agg("yaw_visivel"), agg("roll_visivel"), agg("torcao_axial"), agg("salto_fim"), agg("salto_fim_extra"), agg("arrasto_extra"), por_fase[pior]["folga_alvo_contato"], por_fase[pior]["altura_contato"]), flush=True)
os.makedirs("review/v43r5/revisao", exist_ok=True)
json.dump(RES, open("review/v43r5/revisao/qa_garra_r5.json", "w"), indent=0)
print("QA_GARRA_R5_OK", flush=True)
