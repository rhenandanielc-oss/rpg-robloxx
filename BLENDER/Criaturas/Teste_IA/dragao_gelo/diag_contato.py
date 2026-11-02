"""Diagnostico fino (certificacao 02/11): por quadro, z da ponta do dedo de cada pata e o seu deslocamento em Y
(esteira descontada), e o z minimo das ASAS (pontas no chao) nos clipes pedidos.
Uso: blender -b rig.blend -P diag_contato.py -- Clipe1,Clipe2 [v_esteira_por_clipe=Clipe:v,...]"""
import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]; nomes = a[0].split(",")
VE = dict((k, float(v)) for k, v in (x.split(":") for x in a[1].split(","))) if len(a) > 1 and a[1] else {}
sc = bpy.context.scene; FPS = sc.render.fps
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
gi = {g.index: g.name for g in M.vertex_groups}
ASA = [v.index for v in M.data.vertices if v.groups and gi[max(v.groups, key=lambda g: g.weight).group].startswith(("wing_", "shoulder_"))]
PT = ["front_toes_tip_l", "front_toes_tip_r", "back_toes_tip_l", "back_toes_tip_r"]
for nome in nomes:
    act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); v = VE.get(nome, 0.0); ant = None
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        ps = [A.matrix_world @ A.pose.bones[n].head for n in PT]
        dg = bpy.context.evaluated_depsgraph_get(); ev = M.evaluated_get(dg); me = ev.to_mesh()
        za = min((M.matrix_world @ me.vertices[i].co).z for i in ASA); ev.to_mesh_clear()
        lin = "F%03d asa_z=%6.2f | " % (f, za * 17.5)
        for i, p in enumerate(ps):
            dy = ((p.y - ant[i].y) * FPS - v) * 17.5 / FPS if ant else 0
            lin += "%s z=%5.3f dy=%+6.3f  " % (PT[i][:7] + PT[i][-1], p.z * 17.5, dy)
        print(nome, lin); ant = ps
