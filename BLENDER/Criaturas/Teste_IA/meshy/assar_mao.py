"""Reassa a 'mao' das asas (wing_3..tip + 5 dedos de membrana) do Silverwing quadro a quadro por DESLOCAMENTO DE
POSICAO: cada junta segue o mesmo deslocamento que a junta equivalente do molde Mesh2Motion faz em relacao ao pulso
(referencial do antebraco wing_2, escala pelo tamanho da mao), e cada osso e apontado (giro minimo) para o alvo.
Converter rotacoes nao serve: o leque do Silverwing e o 'pente' do molde tem eixos diferentes e dobravam errado.
Uso: blender -b Silverwing_M2M.blend -P assar_mao.py -- dragon-animations.glb"""
import bpy, sys
from mathutils import Vector, Matrix
anim = sys.argv[sys.argv.index("--") + 1:][0]
sc = bpy.context.scene
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
for m in M.modifiers: m.show_viewport = False          # nao avaliar a malha durante o assado
antes = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=anim)
novos = [o for o in bpy.data.objects if o not in antes]
T = [o for o in novos if o.type == "ARMATURE"][0]
for t in T.animation_data.nla_tracks: t.mute = True
def mao(n): return n.startswith("wing_feather_") or n.split("_")[0] == "wing" and n.split("_")[1] in ("3", "4", "5", "tip")
ordem = []
def visita(b):
    ordem.append(b.name)
    for c in b.children: visita(c)
for b in [b for b in A.data.bones if b.parent is None]: visita(b)
MAO = [n for n in ordem if mao(n)]
def rot(m): return m.to_3x3().normalized()
# repouso
REST_A = {b.name: b.matrix_local.copy() for b in A.data.bones}
REL = {n: REST_A[A.data.bones[n].parent.name].inverted() @ REST_A[n] for n in MAO}
LEN = {n: A.data.bones[n].length for n in MAO}
def quadro_rest(Ar, s):        # (origem pulso, rotacao antebraco) no repouso
    b = Ar.data.bones["wing_2_" + s]; return Ar.matrix_world @ b.tail_local, rot(Ar.matrix_world @ b.matrix_local)
def local_rest(Ar, s, n):
    o, R = quadro_rest(Ar, s); return R.inverted() @ (Ar.matrix_world @ Ar.data.bones[n].tail_local - o)
ESC, L0A, L0T = {}, {}, {}
for s in "lr":
    L0A.update({n: local_rest(A, s, n) for n in MAO if n.endswith("_" + s)})
    L0T.update({n: local_rest(T, s, n) for n in MAO if n.endswith("_" + s)})
    ESC[s] = L0A["wing_tip_" + s].length / L0T["wing_tip_" + s].length
print("ESCALA_MAO", {s: round(v, 4) for s, v in ESC.items()})
n_q = 0
for act in sorted([a for a in bpy.data.actions if a.name.startswith("Silverwing_")], key=lambda a: a.name):
    nome_t = act.name.replace("Silverwing_", "").replace("_", " ")
    at = bpy.data.actions.get(nome_t)
    if at is None: print("SEM_MOLDE", act.name); continue
    # remove canais de rotacao/posicao antigos da mao
    for lay in act.layers:
        for st in lay.strips:
            for cb in st.channelbags:
                for fc in [fc for fc in cb.fcurves if fc.data_path.startswith('pose.bones["') and mao(fc.data_path.split('"')[1])]:
                    cb.fcurves.remove(fc)
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    T.animation_data.action = at; T.animation_data.action_slot = at.slots[0]
    f0, f1 = map(int, act.frame_range)
    for f in range(f0, f1 + 1):
        for n in MAO:
            pb = A.pose.bones[n]; pb.rotation_mode = "QUATERNION"; pb.matrix_basis.identity()
        sc.frame_set(f)
        POSE = {}
        for s in "lr":
            pw = T.pose.bones["wing_2_" + s]; oT = T.matrix_world @ pw.tail; RT = rot(T.matrix_world @ pw.matrix)
            pa = A.pose.bones["wing_2_" + s]; oA = pa.tail.copy(); RA = rot(pa.matrix)
            for n in [m for m in MAO if m.endswith("_" + s)]:
                lt = RT.inverted() @ (T.matrix_world @ T.pose.bones[n].tail - oT)
                alvo = oA + RA @ (L0A[n] + (lt - L0T[n]) * ESC[s])
                p = A.data.bones[n].parent.name
                Mp = POSE[p] if p in POSE else A.pose.bones[p].matrix.copy()
                Mc = Mp @ REL[n]                                  # osso carregado pelo pai, base identidade
                cab = Mc.translation; y = rot(Mc) @ Vector((0, 1, 0))
                d = alvo - cab
                sw = y.rotation_difference(d.normalized()).to_matrix() if d.length > 1e-6 else Matrix.Identity(3)
                Md = Matrix.Translation(cab) @ (sw @ rot(Mc)).to_4x4()
                POSE[n] = Md
                base = (Mc.inverted() @ Md).to_quaternion()
                A.pose.bones[n].rotation_quaternion = base
                A.pose.bones[n].keyframe_insert("rotation_quaternion", frame=f, group=n)
        n_q += 1
    print("ASSADO", act.name, f0, f1)
for n in MAO: A.pose.bones[n].matrix_basis.identity()
A.animation_data.action = None
for o in novos: bpy.data.objects.remove(o, do_unlink=True)
for a in [a for a in bpy.data.actions if not a.name.startswith("Silverwing_")]: bpy.data.actions.remove(a)
for m in M.modifiers: m.show_viewport = True
bpy.ops.wm.save_mainfile()
print("ASSAR_OK quadros", n_q)
