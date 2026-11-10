"""Referencia do Blender para o lote 2 do Studio (04/11): (a) posicoes de ossos em quadros conhecidos (incluindo extremos),
no espaco do Studio relativo ao pivo [Studio = (-x, z, y) do Blender]; (b) a MESMA metrica de ossos medida no Studio:
cabeca do osso no mundo com o deslocamento/giro simulado, apoio = altura < minimo + 0,04, deriva horizontal desde o
inicio do apoio. Ossos: punho/tornozelo (Mao*/Pe*) e dedos (Dedos*/DedosPe*, aproximacao da garra).
NAO e a metrica da sola deformada do qa_urso.py (vertices), que o Studio nao consegue ler.
Deslocamento: v constante, ou perfil v(t) do manifesto integrado pelo trapezio (como o qa_urso.py); giro em torno da
cabeca da Raiz. Loops: 2 ciclos. Parametros tecnicos desta revisao, NAO regras do jogo.
Uso: blender -b CR_Urso_v2_Anim.blend -P studio/metrica_ossos_blender.py -- <saida.json> [lote3]"""
import bpy, sys, json, math, os
from mathutils import Vector as V, Matrix as Mx
OUT = sys.argv[sys.argv.index("--") + 1]
arm = bpy.data.objects["Urso_Rig"]; sc = bpy.context.scene; FPS = 30
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
man = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "clipes", "manifesto_clipes.json"), encoding="utf-8"))
PIVO = arm.data.bones["Raiz"].head_local.copy()
OSSOS_REF = ["Raiz", "Pelve", "Cabeca", "Mandibula", "MaoD", "MaoE", "PeD", "PeE", "DedosD", "DedosPeE", "OrelhaE", "Cauda2"]
if "lote3" in sys.argv: OSSOS_REF += ["DedosE", "DedosPeD", "Coluna3", "OrelhaD"]
PATAS = ["MaoE", "MaoD", "PeE", "PeD", "DedosE", "DedosD", "DedosPeE", "DedosPeD"]
QREF = {"Corrida": [0, 3, 7, 10], "Arrancada": [0, 12, 24, 40, 53], "Frenagem": [0, 10, 20, 32, 45], "VirarE": [0, 9, 18, 27], "VirarD": [0, 9, 18, 27], "Andar": [9]}
if "lote3" in sys.argv:   # 04/11: os 10 clipes restantes (inicio, extremos de boca/raiz/pata, final)
    QREF = {"Observar": [0, 43, 113, 132], "Sentar": [0, 17, 42], "LevantarSentado": [0, 25, 42], "Deitar": [0, 30, 60],
            "LevantarDeitado": [0, 30, 60], "Comer": [0, 3, 10, 36], "Ameaca": [0, 27, 31, 60, 77, 96],
            "GolpePata": [0, 11, 13, 16, 39], "Mordida": [0, 9, 13, 30], "ReacaoImpacto": [0, 3, 13, 30]}
def studio(p): return [round(-p.x, 4), round(p.z, 4), round(p.y, 4)]
def perfil_s(nome):
    m = man[nome]
    if "v_perfil_PARAMETRO" in m:
        vp = m["v_perfil_PARAMETRO"]; acum = [0.0]
        for q in range(1, len(vp)): acum.append(acum[-1] + 0.5 * (vp[q] + vp[q - 1]) / FPS)
        return lambda i: acum[min(i, len(acum) - 1)]
    v = m.get("velocidade_studs_s_PROPOSTA", 0.0) or 0.0
    return lambda i: v * i / FPS
res = {"ref": {}, "metrica": {}}
if not arm.animation_data: arm.animation_data_create()
for nome in QREF:
    act = bpy.data.actions["Urso_" + nome]; arm.animation_data.action = act
    n = man[nome]["quadros"]; loop = man[nome]["loop"]; w = math.radians(man[nome].get("giro_graus_s_PROPOSTA", 0.0) or 0.0)
    s = perfil_s(nome)
    for q in QREF[nome]:
        sc.frame_set(q + 1)
        res["ref"]["%s:%d" % (nome, q)] = {o: studio(arm.matrix_world @ arm.pose.bones[o].head) for o in OSSOS_REF}
    # metrica: sequencia de quadros (2 ciclos nos loops), mundo com deslocamento -Y e giro no pivo
    seq = list(range(n)) * (2 if loop else 1); am = []
    for k, q in enumerate(seq):
        sc.frame_set(q + 1)
        if loop: desl = s(k)                        # v constante: s cresce com o quadro acumulado
        else: desl = s(q)
        M = Mx.Translation(PIVO) @ Mx.Rotation(w * k / FPS, 4, "Z") @ Mx.Translation(-PIVO) @ Mx.Translation((0, -desl, 0))
        am.append({p: M @ (arm.matrix_world @ arm.pose.bones[p].head) for p in PATAS})
    met = {}
    for p in PATAS:
        zmin = min(a[p].z for a in am); maxd, apo, ini, prev = 0.0, 0, None, False
        for a in am:
            ap = a[p].z < zmin + 0.04
            if ap:
                if not prev: ini = a[p]; apo += 1
                maxd = max(maxd, math.hypot(a[p].x - ini.x, a[p].y - ini.y))
            prev = ap
        met[p] = {"apoios": apo, "deriva_max_osso": round(maxd, 4), "altura_min": round(zmin, 4)}
    res["metrica"][nome] = met
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
print("METRICA_OK")
