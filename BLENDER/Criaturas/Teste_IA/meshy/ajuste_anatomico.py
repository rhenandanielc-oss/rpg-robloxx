"""Ajuste anatomico LOCALIZADO do Silverwing (sem reescalar o corpo): cauda mais longa e grossa, asas maiores, pernas um
pouco mais robustas. Como: escala de pose nos ossos-raiz de cada regiao (os filhos herdam), aplicada a malha pelo
proprio esqueleto (pesos ja suaves nas juncoes = transicao sem degrau) e depois tornada o NOVO repouso. As orientacoes
dos ossos nao mudam (so comprimentos/posicoes), entao as acoes (rotacoes locais) continuam validas; as animacoes
proprias devem ser REGERADAS (pes, cauda e asas sao calculados a partir do repouso).
Uso: blender -b Silverwing_M2M.blend -P ajuste_anatomico.py -- [cauda_comp cauda_esp asa perna_comp perna_esp]"""
import bpy, sys
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
CC, CE, ASA, PC, PE = [float(x) for x in a] if len(a) == 5 else (1.20, 1.35, 1.22, 1.06, 1.10)
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
A.animation_data.action = None
# chao = ponta dos dedos (nao o vertice mais baixo: asas maiores em repouso podem descer abaixo dos pes)
PONTAS = ("front_toes_tip_l", "front_toes_tip_r", "back_toes_tip_l", "back_toes_tip_r")
def z_pes(): return min(A.data.bones[n].tail_local.z for n in PONTAS)
Z0 = z_pes()
bpy.context.view_layer.objects.active = A; A.select_set(True)
bpy.ops.object.mode_set(mode="POSE")
for pb in A.pose.bones:
    pb.matrix_basis.identity(); pb.scale = (1, 1, 1)
# escala por regiao (eixo Y do osso = comprimento; X/Z = espessura)
ESC = {"tail_1": (CE, CC, CE)}
for s in ("l", "r"):
    ESC["wing_1_" + s] = (ASA, ASA, ASA)                                  # asa inteira (braco, dedos, membrana)
    ESC["front_leg_collar_" + s] = (PE, PC, PE)                            # ombro/braco dianteiro
    ESC["back_leg_hip_" + s] = (PE, PC, PE)                                # coxa/perna traseira
for n, s in ESC.items():
    A.pose.bones[n].scale = Vector(s)
bpy.context.view_layer.update()
def medir():
    def comp(c): return sum(A.pose.bones[n].length for n in c)
    return {"cauda": round(sum((A.pose.bones[n].tail - A.pose.bones[n].head).length for n in ["tail_1", "tail_2", "tail_3", "tail_4", "tail_5", "tail_6", "tail_tip"]), 3),
            "envergadura": round((A.pose.bones["wing_tip_l"].tail - A.pose.bones["wing_tip_r"].tail).length, 3),
            "pata_d": round((A.pose.bones["front_foot_l"].head - A.pose.bones["front_leg_l"].head).length, 3)}
print("MEDIDAS_POSADAS", medir())
bpy.ops.object.mode_set(mode="OBJECT")
# 1) malha: aplica a deformacao do esqueleto (copia do modificador Armature, mantendo o original)
for o in bpy.data.objects: o.select_set(False)
bpy.context.view_layer.objects.active = M; M.select_set(True)
arm = [m for m in M.modifiers if m.type == "ARMATURE"][0]
for m in M.modifiers: m.show_viewport = (m == arm)
bpy.ops.object.modifier_copy(modifier=arm.name)
copia = M.modifiers[-1]
while M.modifiers[0] != copia:
    bpy.ops.object.modifier_move_up(modifier=copia.name)
bpy.ops.object.modifier_apply(modifier=copia.name)
for m in M.modifiers: m.show_viewport = True
# 2) esqueleto: pose atual vira o novo repouso
M.select_set(False)
bpy.context.view_layer.objects.active = A; A.select_set(True)
bpy.ops.object.mode_set(mode="POSE")
bpy.ops.pose.armature_apply(selected=False)
for pb in A.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode="OBJECT")
# 3) pernas mais longas empurram os pes para baixo do chao: sobe malha + esqueleto pelo que afundou (pes de novo em z=0)
from mathutils import Matrix
dz = Z0 - z_pes()
if abs(dz) > 1e-5:
    M.data.transform(Matrix.Translation((0, 0, dz)))
    bpy.ops.object.mode_set(mode="EDIT")
    for eb in A.data.edit_bones: eb.head.z += dz; eb.tail.z += dz
    bpy.ops.object.mode_set(mode="OBJECT")
print("SUBIDA_PARA_O_CHAO dz %.4f" % dz)
d = {}
def comp_rest(nomes): return sum(A.data.bones[n].length for n in nomes)
print("REPOUSO_NOVO cauda %.3f | envergadura %.3f | z_min_pes %.3f" % (
    comp_rest(["tail_1", "tail_2", "tail_3", "tail_4", "tail_5", "tail_6", "tail_tip"]),
    (A.data.bones["wing_tip_l"].tail_local - A.data.bones["wing_tip_r"].tail_local).length,
    min(A.data.bones[n].tail_local.z for n in ("front_toes_tip_l", "back_toes_tip_l"))))
zs = [v.co.z for v in M.data.vertices]
print("MALHA z_min %.3f z_max %.3f" % (min(zs), max(zs)))
bpy.ops.wm.save_mainfile()
print("ANATOMIA_OK escalas", ESC)
