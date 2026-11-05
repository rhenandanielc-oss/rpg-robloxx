"""E5 revisao da Patada: mede, quadro a quadro, a rotacao local de cada osso da pata dianteira (escapula -> dedos e auxiliares)
decomposta em torcao (em volta do eixo do osso) e flexao, a direcao da sola no mundo e a continuidade entre quadros
(salto angular e troca de sinal do quaternion). So leitura.
Uso: blender -b Leao_Solar_Ref_E5_clipes.blend -P e5_40_diag_patada.py -- <saida.json> <Acao1,Acao2,...> [pata=auto]"""
import bpy, sys, math, json
from mathutils import Vector as V, Quaternion
A = sys.argv[sys.argv.index("--") + 1:]; OUT = A[0]; ACOES = A[1].split(",")
arm = bpy.data.objects["Leao_Solar_Rig"]; PB = arm.pose.bones; BD = arm.data.bones; sc = bpy.context.scene
def ossos(l):
    if l.startswith("T"): return ["Coxa_" + l, "Canela_" + l, "Metatarso_" + l, "Dedos_" + l]       # traseiras (pata: TD/TE)
    return ["Escapula_" + l, "Umero_" + l, "Antebraco_" + l, "Mao_" + l, "Dedos_" + l, "Cotovelo_Aux_" + l, "Punho_Aux_" + l]
def swing_twist(q):
    """q local (eixos do osso): torcao em volta de Y e flexao restante (graus), com eixo da flexao"""
    if q.w < 0: q = -q
    tw = Quaternion((q.w, 0, q.y, 0)); n = tw.magnitude
    tw = Quaternion() if n < 1e-9 else Quaternion((tw.w / n, 0, tw.y / n, 0))
    sw = q @ tw.inverted(); a_tw = math.degrees(2 * math.atan2(tw.y, tw.w))
    ax, an = sw.to_axis_angle(); return a_tw, math.degrees(an), ax
def rel_pai(b):
    """rotacao do osso relativa ao pai, comparada ao repouso (o que o osso 'faz' na junta)"""
    pb = PB[b]
    if pb.parent is None: return pb.matrix.to_quaternion()
    Mr = BD[b].parent.matrix_local.inverted() @ BD[b].matrix_local
    Mp = pb.parent.matrix.inverted() @ pb.matrix
    return (Mr.to_3x3().inverted() @ Mp.to_3x3()).to_quaternion()
SOLA_N = {}
res = {}
for nome in ACOES:
    act = bpy.data.actions.get(nome)
    if act is None: print("SEM ACAO", nome); continue
    arm.animation_data_create(); arm.animation_data.action = act
    f0, f1 = [int(x) for x in act.frame_range]
    lados = A[2].split(",") if len(A) > 2 else ["DD", "DE"]
    out = {}
    for l in lados:
        L = ossos(l); linhas = []; ant = {}
        n_loc = BD["Dedos_" + l].matrix_local.to_3x3().inverted() @ V((0, 0, -1))           # normal da sola (para baixo) no espaco do osso
        mao_ = ("Metatarso_" if l.startswith("T") else "Mao_") + l; n_mao = BD[mao_].matrix_local.to_3x3().inverted() @ V((0, 0, -1))
        sgx = 1 if l.endswith("D") else -1                                                 # lado de fora da pata (x+ = direita)
        for f in range(f0, f1 + 1):
            sc.frame_set(f); lin = dict(f=f)
            for b in L:
                q = rel_pai(b); tw, sw, ax = swing_twist(q)
                kq = PB[b].rotation_quaternion.copy(); salto = None; sinal = None
                if b in ant:
                    salto = round(math.degrees(ant[b][0].rotation_difference(q).angle), 2); sinal = ant[b][1].dot(kq) < 0
                ant[b] = (q, kq)
                lin[b] = dict(torcao=round(tw, 1), flexao=round(sw, 1), eixo=[round(x, 2) for x in ax], salto=salto, sinal_trocado=sinal)
            Mw = arm.matrix_world.to_3x3()
            n = (Mw @ PB["Dedos_" + l].matrix.to_3x3() @ n_loc).normalized(); nm = (Mw @ PB[mao_].matrix.to_3x3() @ n_mao).normalized()
            lin["sola_normal"] = [round(x, 3) for x in n]; lin["sola_para_fora"] = round(n.x * sgx, 3); lin["sola_para_cima"] = round(-n.z, 3)
            lin["mao_normal"] = [round(x, 3) for x in nm]
            lin["pata_z"] = round((arm.matrix_world @ PB["Dedos_" + l].head).z, 2); lin["punho"] = [round(x, 2) for x in arm.matrix_world @ PB[mao_].head]
            linhas.append(lin)
        out[l] = linhas
        # resumo: maiores |torcao| e saltos por osso
        print("==", nome, l)
        for b in L:
            tws = [abs(x[b]["torcao"]) for x in linhas]; fx = [x[b]["flexao"] for x in linhas]; sal = [x[b]["salto"] or 0 for x in linhas]
            sg = sum(1 for x in linhas if x[b]["sinal_trocado"])
            print("  %-16s torcao_max %6.1f (q%d)  flexao_max %6.1f  salto_max %5.1f (q%d)  trocas_sinal %d" % (
                b, max(tws), linhas[tws.index(max(tws))]["f"], max(fx), max(sal), linhas[sal.index(max(sal))]["f"], sg))
        sf = [x["sola_para_fora"] for x in linhas]; sc_ = [x["sola_para_cima"] for x in linhas]
        print("  sola_para_fora max %.2f (q%d)  sola_para_cima max %.2f (q%d)" % (max(sf), linhas[sf.index(max(sf))]["f"], max(sc_), linhas[sc_.index(max(sc_))]["f"]))
    res[nome] = out
json.dump(res, open(OUT, "w"), indent=0)
print("DIAG_OK")
