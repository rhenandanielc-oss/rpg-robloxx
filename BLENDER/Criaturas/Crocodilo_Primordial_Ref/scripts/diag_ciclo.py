"""Somente leitura: por quadro (incluindo o RETORNO ultimo->primeiro), variacao no MUNDO de posicao (cabeca do osso) e
rotacao de cada osso de uma acao assada. Uso: blender -b CR_Crocodilo_Anim.blend -P diag_ciclo.py -- <clipe> [ossos,...]"""
import bpy, sys, math
A = sys.argv[sys.argv.index("--") + 1:]; CL = A[0]; FOCO = A[1].split(",") if len(A) > 1 else None
sc = bpy.context.scene; arm = bpy.data.objects["CR_Croc_Rig"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
act = bpy.data.actions["Croc_" + CL]; arm.animation_data.action = act
if act.slots: arm.animation_data.action_slot = act.slots[0]
f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
Q = []
for f in range(f0, f1 + 1):
    sc.frame_set(f); Q.append({pb.name: ((arm.matrix_world @ pb.matrix).to_quaternion(), (arm.matrix_world @ pb.matrix).translation.copy(), pb.tail.copy()) for pb in arm.pose.bones})
n = len(Q); ossos = FOCO or [pb.name for pb in arm.pose.bones]
print("CICLO", CL, "quadros", n)
res = {}
for o in ossos:
    rot = []; pos = []; pon = []
    for k in range(n):
        a, b = Q[k][o], Q[(k + 1) % n][o]
        rot.append(math.degrees(a[0].rotation_difference(b[0]).angle)); pos.append((b[1] - a[1]).length); pon.append((b[2] - a[2]).length)
    res[o] = (rot, pos, pon)
    print("OSSO %-11s rot_max %.2f (q%d) retorno %.2f | pos_max %.3f retorno %.3f | ponta_max %.3f retorno %.3f" % (
        o, max(rot[:-1]), rot.index(max(rot[:-1])), rot[-1], max(pos[:-1]), pos[-1], max(pon[:-1]), pon[-1]))
if FOCO:
    for o in FOCO:
        print("SERIE", o, "rot", [round(x, 1) for x in res[o][0]], "ponta", [round(x, 2) for x in res[o][2]])
