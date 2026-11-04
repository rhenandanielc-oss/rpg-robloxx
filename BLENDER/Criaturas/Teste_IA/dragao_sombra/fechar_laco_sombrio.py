"""Fecha o LACO de clipes do Sombrio que saltam na volta (fim != inicio), sem mexer no gerador compartilhado.
Achado 03/11: Curva_E/Curva_D do Sombrio (gerados com NB_VOO 4 / T_VOO 3,2 e curvas de 4 s) terminam com a cauda 10,5 graus
longe do inicio (no Glacial: 0). Correcao: para cada osso com diferenca, a rotacao que leva o ultimo quadro ao primeiro e
distribuida ao longo do clipe inteiro (peso linear 0 -> 1), entao a volta do laco fica continua e cada quadro muda pouco.
Uso: blender -b rig_com_clipes.blend -P fechar_laco_sombrio.py -- <saida.blend> Clipe1,Clipe2 [limiar_graus=0.5]"""
import bpy, sys, math
from mathutils import Quaternion
a = sys.argv[sys.argv.index("--") + 1:]; SAIDA = a[0]; NOMES = a[1].split(","); LIM = float(a[2]) if len(a) > 2 else 0.5
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
for nome in NOMES:
    act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range)
    orig = {}
    for f in range(f0, f1 + 1):
        sc.frame_set(f); orig[f] = {b.name: b.matrix_basis.to_quaternion() for b in A.pose.bones}
    mexidos = {}
    for b in A.pose.bones:
        q0, q1 = orig[f0][b.name], orig[f1][b.name]
        if q0.dot(q1) < 0: q1 = -q1
        ang = math.degrees(q1.rotation_difference(q0).angle)
        if ang > LIM: mexidos[b.name] = (q1.inverted() @ q0, ang)          # delta local: q1 @ delta = q0
    for f in range(f0, f1 + 1):
        w = (f - f0) / (f1 - f0)
        for n, (delta, _) in mexidos.items():
            pb = A.pose.bones[n]; pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = orig[f][n] @ Quaternion().slerp(delta, w)
            pb.keyframe_insert("rotation_quaternion", frame=f, group=n)
    print("LACO_FECHADO", nome, {n: round(g, 1) for n, (_, g) in mexidos.items()})
A.animation_data.action = None
for x in bpy.data.actions: x.use_fake_user = True
bpy.ops.wm.save_as_mainfile(filepath=SAIDA); print("FECHAR_OK")
