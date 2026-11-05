# biblioteca comum (exec): poses de teste iguais as da E4b
import bpy, math
import numpy as np
OB = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; ARM = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
for pb in ARM.pose.bones: pb.rotation_mode = "XYZ"
CO0 = np.array([v.co for v in OB.data.vertices]); E = np.array([e.vertices[:] for e in OB.data.edges]); L0 = np.linalg.norm(CO0[E[:, 0]] - CO0[E[:, 1]], axis=1)
AUX = {"Cotovelo_Aux_DD": "Antebraco_DD", "Cotovelo_Aux_DE": "Antebraco_DE", "Punho_Aux_DD": "Mao_DD", "Punho_Aux_DE": "Mao_DE"}
def upd():
    for t_, c_ in AUX.items():          # auxiliares de volume: metade da rotacao do osso filho (no rig final: Copy Rotation 0,5)
        if t_ in ARM.pose.bones: e = ARM.pose.bones[c_].rotation_euler; ARM.pose.bones[t_].rotation_euler = (e.x * 0.5, e.y * 0.5, e.z * 0.5)
    for t_, c_ in (("Tufo1", "Cauda5"), ("Tufo2", "Cauda6")):
        if t_ in ARM.pose.bones: ARM.pose.bones[t_].rotation_euler = ARM.pose.bones[c_].rotation_euler.copy()
    bpy.context.view_layer.update()
def zerar():
    for pb in ARM.pose.bones: pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
def mundo(nome):
    pb = ARM.pose.bones[nome]; return np.array(ARM.matrix_world @ pb.head), np.array(ARM.matrix_world @ pb.tail)
def angulo(pai, filho):
    a0, a1 = mundo(pai); b0, b1 = mundo(filho); u = (a1 - a0) / np.linalg.norm(a1 - a0); v = (b1 - b0) / np.linalg.norm(b1 - b0)
    return math.degrees(math.acos(np.clip(u @ v, -1, 1)))
def flex(filho, graus):
    pb = ARM.pose.bones[filho]; pai = pb.parent.name; base = pb.rotation_euler.copy(); melhor = None
    for sgn in (1, -1):
        pb.rotation_euler = (base.x + math.radians(sgn * graus), base.y, base.z); bpy.context.view_layer.update()
        a = angulo(pai, filho)
        if melhor is None or a > melhor[0]: melhor = (a, sgn)
    pb.rotation_euler = (base.x + math.radians(melhor[1] * graus), base.y, base.z); upd()
def avanca(nome, graus, direcao):
    pb = ARM.pose.bones[nome]; base = pb.rotation_euler.copy(); melhor = None
    for sgn in (1, -1):
        pb.rotation_euler = (base.x + math.radians(sgn * graus), base.y, base.z); bpy.context.view_layer.update()
        t = mundo(nome)[1] @ np.array(direcao)
        if melhor is None or t > melhor[0]: melhor = (t, sgn)
    pb.rotation_euler = (base.x + math.radians(melhor[1] * graus), base.y, base.z); upd()
def girar(nome, rx=0, ry=0, rz=0):
    pb = ARM.pose.bones[nome]; pb.rotation_euler = (pb.rotation_euler.x + math.radians(rx), pb.rotation_euler.y + math.radians(ry), pb.rotation_euler.z + math.radians(rz)); upd()
def posado():
    dg = bpy.context.evaluated_depsgraph_get(); m = OB.evaluated_get(dg).to_mesh(); p = np.array([v.co for v in m.vertices]); OB.evaluated_get(dg).to_mesh_clear(); return p
POSE = {
 "ombro_avanco": lambda: (avanca("Escapula_DD", 12, (0, -1, 0)), avanca("Umero_DD", 38, (0, -1, 0))),
 "cotovelo_dobra": lambda: flex("Antebraco_DD", 95),
 "punho_dobra": lambda: flex("Mao_DD", 85),
 "passo_dianteiro": lambda: (avanca("Umero_DD", 28, (0, -1, 0)), flex("Antebraco_DD", 70), flex("Mao_DD", 55)),
}
