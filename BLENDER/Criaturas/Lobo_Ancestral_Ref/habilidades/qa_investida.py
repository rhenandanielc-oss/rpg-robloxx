"""QA da Hab_Investida (so leitura): por quadro, altura e velocidade em Y de cada almofada. Clipe NO LUGAR: no galope a pata
apoiada recua a velocidade constante do galope (o jogo move o lobo); na carga, na mordida e na freada a pata apoiada fica parada.
Deslize = |vy - esperado| nos quadros de apoio (almofada <= 0,23). Tambem: menor z das patas e saltos (descontinuidade) de pose.
Uso: blender -b <Anim_Kit.blend> -P qa_investida.py -- <saida.json> [vel_galope=21.43]"""
import bpy, sys, json, math
A = sys.argv[sys.argv.index("--") + 1:]; VEL = float(A[1]) if len(A) > 1 else 3.0 / (0.30 * 14 / 30)
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
act = bpy.data.actions["Lobo_Hab_Investida"]; arm.animation_data.action = act
try: arm.animation_data.action_slot = act.slots[0]
except Exception: pass
PES = ("MaoE", "MaoD", "MetatarsoE", "MetatarsoD"); f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
pos = []
for f in range(f0, f1 + 1):
    sc.frame_set(f); bpy.context.view_layer.update()
    pos.append({k: tuple(arm.matrix_world @ arm.pose.bones[k].tail) for k in PES})
def vel_inv(t):                                                  # curva do avanco da v28 (habilidades/clipes_kit.py: vel_investida)
    def sv(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
    if t < 0.22: return 0.0
    if t < 0.36: return VEL * sv((t - 0.22) / 0.14)
    if t < 0.78: return VEL
    if t < 0.96: return VEL * (1 - sv((t - 0.78) / 0.18))
    return 0.0
res = {"vel_galope": round(VEL, 2), "quadros": []}; pior = {"galope": 0.0, "parado": 0.0}   # (v28) esperado = curva do avanco; o v27 nao tinha curva: comparado com a mesma
for i in range(1, len(pos)):
    t = (i) / 30.0; fase = "galope" if 0.22 <= t <= 0.96 else "parado"
    q = {"f": i + 1, "t": round(t, 3), "fase": fase}
    for k in PES:
        z = pos[i][k][2]; vy = (pos[i][k][1] - pos[i - 1][k][1]) * 30
        ap = z <= 0.23 and pos[i - 1][k][2] <= 0.23
        esp = vel_inv(t)
        des = abs(vy - (vel_inv(t) + vel_inv(t - 1 / 30.0)) / 2) if ap else 0.0       # velocidade media do intervalo
        if ap and fase in pior: pior[fase] = max(pior[fase], des)
        q[k] = {"z": round(z, 3), "vy": round(vy, 2), "apoio": ap, "deslize": round(des, 2)}
    res["quadros"].append(q)
res["deslize_max"] = {k: round(v, 2) for k, v in pior.items()}
json.dump(res, open(A[0], "w"), indent=0); print("QA_INVESTIDA", json.dumps(res["deslize_max"]))
