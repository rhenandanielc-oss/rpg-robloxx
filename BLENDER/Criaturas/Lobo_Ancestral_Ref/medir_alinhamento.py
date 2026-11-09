"""Alinhamento da malha (so leitura): por fatias de y, centro em X do tronco (meio do contorno e media), topo e base;
centro das 4 patas (z<0,3) e, havendo rig, posicao dos pares de ossos (ombros, quadris, punhos, jarretes) e a pose avaliada
num quadro de uma acao. Uso: blender -b <blend> -P medir_alinhamento.py -- <objeto> <saida.json> [acao] [quadro]"""
import bpy, sys, json
import numpy as np
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; NOME, SAIDA = A[0], A[1]; ACAO = A[2] if len(A) > 2 else None; Q = int(A[3]) if len(A) > 3 else 0
ob = bpy.data.objects[NOME]; arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
if arm and ACAO:
    for pb in arm.pose.bones:
        for c in pb.constraints: c.mute = True
    act = bpy.data.actions[ACAO]; arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    bpy.context.scene.frame_set(int(act.frame_range[0]) + Q)
elif arm:
    for pb in arm.pose.bones:
        for c in pb.constraints: c.mute = True
        pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
dg = bpy.context.evaluated_depsgraph_get(); me = ob.evaluated_get(dg).data
co = np.array([ob.matrix_world @ v.co for v in me.vertices]); x, y, z = co.T
r = {"objeto": NOME, "acao": ACAO, "quadro": Q, "fatias": [], "patas": {}, "ossos": {}}
for y0 in np.arange(y.min(), y.max(), 0.5):
    s = (y >= y0) & (y < y0 + 0.5)
    for nome, m in (("alto", s & (z > 4.0)), ("tronco", s & (z > 2.8))):
        if m.sum() < 50: continue
        xs = x[m]; r["fatias"].append({"y": round(float(y0 + 0.25), 2), "faixa": nome, "x_meio": round(float((xs.min() + xs.max()) / 2), 3),
                                       "x_media": round(float(xs.mean()), 3), "x_min": round(float(xs.min()), 3), "x_max": round(float(xs.max()), 3),
                                       "z_topo": round(float(z[m].max()), 3), "n": int(m.sum())})
pe = (z < 0.30)
if pe.any():
    yp = y[pe]; ym = (yp.min() + yp.max()) / 2
    for lado, sx in (("E", 1), ("D", -1)):
        for par, c in (("dian", y < ym), ("tras", y >= ym)):
            q = pe & (x * sx > 0.1) & c
            if q.any(): r["patas"][lado + "_" + par] = [round(float(v), 3) for v in co[q].mean(axis=0)]
if arm:
    for b in ("Pelve", "Peito", "Pescoco1", "Cabeca", "Cauda1", "Cauda7", "EscapulaE", "EscapulaD", "BracoE", "BracoD", "AntebracoE", "AntebracoD",
              "MaoE", "MaoD", "CoxaE", "CoxaD", "CanelaE", "CanelaD", "MetatarsoE", "MetatarsoD"):
        if b in arm.pose.bones:
            pb = arm.pose.bones[b]; r["ossos"][b] = [round(c, 3) for c in arm.matrix_world @ pb.head] + [round(c, 3) for c in arm.matrix_world @ pb.tail]
json.dump(r, open(SAIDA, "w"), indent=1)
print("ALINH", NOME, ACAO, Q)
for f in r["fatias"]:
    if f["faixa"] == "tronco": print("  y=%6.2f x_meio=%+.3f x_media=%+.3f [%+.2f %+.2f] topo=%.2f" % (f["y"], f["x_meio"], f["x_media"], f["x_min"], f["x_max"], f["z_topo"]))
print("  PATAS", r["patas"])
for b in ("Pelve", "Peito", "Cabeca", "EscapulaE", "EscapulaD", "BracoE", "BracoD", "CoxaE", "CoxaD"):
    if b in r["ossos"]: print("  OSSO", b, r["ossos"][b])
