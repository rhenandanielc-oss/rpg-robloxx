"""PARADA (frenagem) propria do Dragao Sombrio, sem mexer no gerador compartilhado (meshy/anim_silverwing.py).
Problema medido em Play (03/11): a montaria toca Correr_Frenagem -> Parada por 0,9 s enquanto o corpo ainda freia de 22 a
~8,5 studs/s (freioChao 15 studs/s2); a Parada antiga mantem os pes parados em relacao ao corpo -> um pe apoiado
escorregava ate 15 studs. Solucao: a passada do proprio Correr com o tempo DESACELERADO na mesma taxa do corpo
(fase avanca v(t)/RitmoCorrerBase), entao cada pe apoiado fica parado no chao; por cima, a postura de frenagem da
Parada antiga so no pescoco, cabeca, mandibula e cauda (ossos que nao movem as patas), entrando em 0,25 s.
Uso: blender -b rig/SB_Dragao_M2M.blend -P clipe_parada_sombrio.py -- <saida.blend> [v0=22] [freio=15] [dur=0.9]"""
import bpy, sys, math
from mathutils import Quaternion
a = sys.argv[sys.argv.index("--") + 1:]; SAIDA = a[0]
V0 = float(a[1]) if len(a) > 1 else 22.0; FREIO = float(a[2]) if len(a) > 2 else 15.0; DUR = float(a[3]) if len(a) > 3 else 0.9
RITMO = 18.94                                         # RitmoCorrerBase (studs/s em que o Correr nao patina)
sc = bpy.context.scene; FPS = sc.render.fps; A = bpy.data.objects["Silverwing_Rig"]
COR = bpy.data.actions["Silverwing_Correr"]; PAR = bpy.data.actions["Silverwing_Parada"]
c0, c1 = COR.frame_range; DC = (c1 - c0) / FPS           # duracao do ciclo do Correr (s)
p0, p1 = PAR.frame_range; DP = (p1 - p0) / FPS
POSTURA = [b.name for b in A.pose.bones if b.name.startswith(("spine_2", "spine_3", "spine_4", "head", "mouth_", "tail_"))]
def amostrar(act, tseg, f0):
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f = f0 + tseg * FPS; sc.frame_set(int(f), subframe=f - int(f))
    return {b.name: (b.matrix_basis.to_quaternion(), b.matrix_basis.translation.copy()) for b in A.pose.bones}
nq = int(round(DUR * FPS)) + 1; quadros = []
for i in range(nq):
    t = i / FPS; v = max(0.0, V0 - FREIO * t)
    s_corpo = V0 * t - 0.5 * FREIO * t * t if v > 0 else V0 * V0 / (2 * FREIO)
    fase = (s_corpo / RITMO) % DC                       # tempo do Correr que mantem o pe parado no chao
    cor = amostrar(COR, fase, c0); par = amostrar(PAR, min(DP, t * DP / DUR), p0)
    w = 0.70 * min(1.0, t / 0.25)                       # postura de frenagem entra em 0,25 s
    pose = {}
    for n, (q, tr) in cor.items():
        if n in POSTURA: qp, tp = par[n]; pose[n] = (q.slerp(qp, w), tr.lerp(tp, w))
        else: pose[n] = (q, tr)
    quadros.append(pose)
nova = bpy.data.actions.new("Silverwing_Parada_Sombrio")
A.animation_data.action = nova
slot = nova.slots.new(id_type="OBJECT", name="Silverwing_Rig") if hasattr(nova, "slots") and len(nova.slots) == 0 else nova.slots[0]
A.animation_data.action_slot = slot
for i, pose in enumerate(quadros):
    f = p0 + i
    for b in A.pose.bones:
        q, tr = pose[b.name]; b.rotation_mode = "QUATERNION"; b.rotation_quaternion = q; b.location = tr
        b.keyframe_insert("rotation_quaternion", frame=f); b.keyframe_insert("location", frame=f)
nova["loop"] = False; nova.use_fake_user = True; PAR.use_fake_user = True   # sem usuario a acao nao e salva
# troca: a antiga fica guardada como Silverwing_Parada_antiga (recuperavel)
PAR.name = "Silverwing_Parada_antiga"; nova.name = "Silverwing_Parada"
A.animation_data.action = None
bpy.ops.wm.save_as_mainfile(filepath=SAIDA)
print("PARADA_OK quadros", nq, "ciclo_correr", round(DC, 3), "s; avanco de fase", round((V0 * DUR - 0.5 * FREIO * DUR * DUR) / RITMO, 3), "s")
