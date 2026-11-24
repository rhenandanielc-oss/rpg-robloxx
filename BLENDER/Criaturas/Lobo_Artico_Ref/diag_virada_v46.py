"""v46 DIAGNOSTICO (20/11/2026, pedido "mudar de direcao caminhando em curva"). So leitura da anim_v45r3 (nada e salvo).
Mede pelos OSSOS (leve, sem malha): MCP = cauda do Metacarpo/Metatarso (no espaco do armature; frente -Y, esquerda +X).
1) Andar aprovado: ciclo, passada, fracao de apoio e fase de cada pata, posicao do MCP no meio do apoio.
2) O que o controlador r10e faz hoje andando (Laco): o clipe RETO toca e o pivo gira CFG.giro.Andar = 60 graus/s em volta de si
   mesmo enquanto avanca 3,0 studs/s. Simulacao mundial (pivo -> corpo): deslize de cada pata apoiada por fase, para 60/45/30/15 graus/s.
3) Viradas (VirarCurto 45, Virar 90): quanto o pivo se desloca x quanto gira (giro no lugar = orientacao gira com a posicao fixa).
4) Clipes de ameaca: quais ossos das patas eles animam (ocupam os membros?).
Uso: blender -b anim_v45r3/CR_LoboArtico_Anim.blend -P diag_virada_v46.py -- <saida_json>"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); SRC = os.path.dirname(bpy.data.filepath)
ARM = bpy.data.objects["LoboArtico_Rig"]; P = ARM.pose.bones; sc = bpy.context.scene
PATAS = {"DE": "Metacarpo_E", "DD": "Metacarpo_D", "TE": "Metatarso_E", "TD": "Metatarso_D"}
PERNA = {"Umero_E", "Antebraco_E", "Metacarpo_E", "Dedos_E", "Umero_D", "Antebraco_D", "Metacarpo_D", "Dedos_D",
         "Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E", "Coxa_D", "Tibia_D", "Metatarso_D", "DedosPe_D"}
def usar(nome):
    ac = bpy.data.actions[nome]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    return ac
def mcp(q):
    sc.frame_set(q); return {k: (ARM.matrix_world @ P[b].tail).copy() for k, b in PATAS.items()}
R = {"metodo": __doc__.split("Uso:")[0]}
# 1) Andar
ac = usar("Andar"); n = int(ac.frame_range[1] - ac.frame_range[0]); f0 = int(ac.frame_range[0])
Q = [mcp(f0 + q) for q in range(n + 1)]; zmin = {k: min(Q[q][k].z for q in range(n)) for k in PATAS}
ap = {k: [Q[q][k].z < zmin[k] + 0.02 for q in range(n)] for k in PATAS}
v = 3.0; FPS = 30; T = n / FPS
info = {}
for k in PATAS:
    fr = sum(ap[k]) / n
    ini = next(q for q in range(n) if ap[k][q] and not ap[k][q - 1])
    ys = [Q[q][k].y for q in range(n) if ap[k][q]]
    info[k] = {"apoio_frac": round(fr, 3), "toque_quadro": ini, "y_toque_saida": [round(max(ys), 3), round(min(ys), 3)], "x": round(Q[ini][k].x, 3),
               "recuo_no_apoio": round(max(ys) - min(ys), 3)}
R["andar"] = {"quadros": n, "ciclo_s": T, "v": v, "passada": v * T, "patas": info}
print("DIAG andar", n, T, json.dumps(info), flush=True)
# 2) controlador: clipe reto + pivo girando om e avancando v
def sim(om_g):
    om = math.radians(om_g); res = {}
    for k in PATAS:
        piores = []
        for ciclo in range(2):
            seg = []
            for q in range(n):
                qq = q + ciclo * n; t = qq / FPS; th = om * t
                # frente no mundo = Rz(th) @ (0,-1,0) = (sin th, -cos th); posicao do pivo = integral de v * frente
                if abs(om) > 1e-9: px, py = (v / om) * (1 - math.cos(th)), -(v / om) * math.sin(th)
                else: px, py = 0.0, -v * t
                Rz = Matrix.Rotation(th, 3, "Z"); w = V((px, py, 0)) + Rz @ Q[q][k]
                if ap[k][q]: seg.append(w)
                elif seg: piores.append(max((a - seg[0]).to_2d().length for a in seg)); seg = []
            if seg: piores.append(max((a - seg[0]).to_2d().length for a in seg))
        res[k] = round(max(piores), 4)
    return res
R["controlador_laco"] = {str(g): sim(g) for g in (60, 45, 30, 15, 0)}
print("DIAG laco", json.dumps(R["controlador_laco"]), flush=True)
# 3) viradas: deslocamento do pivo x giro
VJ = {}
for arq in ("viradas_curtas_v44.json", "viradas_v27.json"):
    p = os.path.join(SRC, arq)
    if os.path.exists(p): VJ.update(json.load(open(p))["acoes"])
R["viradas"] = {}
for nome, d in VJ.items():
    Tq = d["T_por_quadro"]; ps = d["psi_graus_por_quadro"]
    R["viradas"][nome] = {"duracao_s": d["duracao_s"], "giro_graus": round(ps[-1], 2), "pivo_desloca_max": round(max(math.hypot(*t) for t in Tq), 3),
                          "caminho_do_pivo": round(sum(math.hypot(Tq[i][0] - Tq[i - 1][0], Tq[i][1] - Tq[i - 1][1]) for i in range(1, len(Tq))), 3)}
print("DIAG viradas", json.dumps(R["viradas"]), flush=True)
# 4) ossos das patas nos clipes de ameaca / poses
R["poses_ossos_perna"] = {}
for nome in ("AmeacaEntrar", "Ameaca", "AmeacaSair", "InvestidaAviso", "Repouso"):
    if nome not in bpy.data.actions: continue
    ac = usar(nome); f0, f1 = int(ac.frame_range[0]), int(ac.frame_range[1]); var = {}
    sc.frame_set(f0); base = {b: P[b].matrix.copy() for b in PERNA}
    for q in range(f0, f1 + 1, 3):
        sc.frame_set(q)
        for b in PERNA:
            d = (P[b].matrix.to_quaternion().rotation_difference(base[b].to_quaternion())).angle
            var[b] = max(var.get(b, 0.0), math.degrees(d))
    R["poses_ossos_perna"][nome] = {b: round(g, 1) for b, g in var.items() if g > 0.5}
print("DIAG poses", json.dumps(R["poses_ossos_perna"]), flush=True)
json.dump(R, open(OUT, "w"), indent=1); print("DIAG_V46_OK", flush=True)
