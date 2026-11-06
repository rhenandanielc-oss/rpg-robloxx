# Estabilidade do dorso na montaria (somente leitura): por clipe, desvio angular maximo da rotacao de mundo do osso da sela
# em relacao a media do ciclo, e faixa de altura/deslocamento do ponto da sela (cabeca de spine_02), em todos os quadros.
# Uso: blender -b <v.blend> -P 16b_sela.py -- <saida.json> <clipe1,clipe2,...>
import bpy, sys, json, math
from mathutils import Quaternion
argv = sys.argv[sys.argv.index("--") + 1:]
scn = bpy.context.scene; arm = bpy.data.objects["Wyvern_Rig"]; key = bpy.data.objects["Wyvern"].data.shape_keys
R = {}
for nome in argv[1].split(","):
    a = bpy.data.actions[nome]
    for ob, tipo in ((arm, "OBJECT"), (key, "KEY")):
        ob.animation_data.action = a; ob.animation_data.action_slot = [s for s in a.slots if s.target_id_type == tipo][0]
    qs, ps = [], []; f = 0.0
    while f <= a.frame_range[1] + 1e-6:
        scn.frame_set(int(f), subframe=f - int(f)); pb = arm.pose.bones["spine_02"]
        M = arm.matrix_world @ pb.matrix; qs.append(M.to_quaternion()); ps.append(M.translation.copy()); f += 0.8
    m = Quaternion((0, 0, 0, 0))
    for q in qs:
        if q.dot(qs[0]) < 0: q = -q
        m = Quaternion([m[i] + q[i] for i in range(4)])
    m.normalize()
    ang = lambda q: math.degrees(m.rotation_difference(q).angle) % 360
    dev = max(min(ang(q), 360 - ang(q)) for q in qs)
    R[nome] = {"desvio_ang_max_graus": round(dev, 2), "faixa_z": round(max(p.z for p in ps) - min(p.z for p in ps), 3),
               "faixa_xy": round(max((p - ps[0]).xy.length for p in ps), 3)}
json.dump(R, open(argv[0], "w"), indent=1); print("SELA", json.dumps(R))
