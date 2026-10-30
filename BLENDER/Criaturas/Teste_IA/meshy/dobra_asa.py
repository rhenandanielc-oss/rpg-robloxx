"""Dobra de asa PROPRIA do Silverwing para Idle e Walk (substitui a dobra do molde, feita para o 'pente' dele).
Tudo e RELATIVO a asa aberta de repouso (a membrana so tolera mudancas moderadas com skin linear):
 1) no plano da asa (u = dedo-guia, n = normal): cotovelo dobra ALFA_E, pulso ALFA_W, leque fecha (angulo x FECHA);
 2) a asa inteira gira como bloco a partir do ombro: varre para tras GAMA e cai DELTA (no referencial do tronco).
Direcoes absolutas e dobra fechada de 180 graus no pulso esticavam a membrana ate 27x.
Secundario ciclico: respiracao (Idle) / balanco do passo (Walk). Ombro, tronco, patas e cauda do Mesh2Motion.
Uso: blender -b Silverwing_M2M.blend -P dobra_asa.py -- [GAMA DELTA ALFA_E ALFA_W FECHA] (graus/fator)"""
import bpy, sys, math
from mathutils import Vector, Matrix
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
GAMA, DELTA, ALFA_E, ALFA_W, FECHA, DEDO2, QB, QG = ([float(a) for a in args] + [35, 35, 30, 35, 0.6, 0.0, 0.3, 1.0][len(args):])[:8]
sc = bpy.context.scene
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
for m in M.modifiers: m.show_viewport = False
def eh_mao(n): return n.startswith("wing_feather_") and n.split("_")[2] in ("3", "4", "5") or \
    (n.startswith("wing_") and n.split("_")[1] in ("3", "4", "5", "tip"))
def grupo(n):
    if n.startswith("wing_1_") or n.startswith("wing_feather_1_"): return "braco"
    if n.startswith("wing_2_"): return "antebraco"
    if n.startswith("wing_feather_2_"): return "dedo2"
    return "mao"
ALVO = [b.name for b in A.data.bones if b.name.startswith("wing_")]
ordem = []
def visita(b):
    ordem.append(b.name)
    for c in b.children: visita(c)
for b in [b for b in A.data.bones if b.parent is None]: visita(b)
ORD = [n for n in ordem if n in ALVO]
REST = {b.name: b.matrix_local.copy() for b in A.data.bones}
REL = {n: REST[A.data.bones[n].parent.name].inverted() @ REST[n] for n in ORD}
def rot(m): return m.to_3x3().normalized()
def ydir(n): return (rot(REST[n]) @ Vector((0, 1, 0))).normalized()
def corpo(fun):
    s0, s1 = fun("spine_0"), fun("spine_1")
    fwd = (s1.translation + rot(s1) @ Vector((0, A.data.bones["spine_1"].length, 0)) - s0.translation).normalized()
    up = Vector((0, 0, 1)); up = (up - fwd * up.dot(fwd)).normalized(); return fwd, up, fwd.cross(up)
fwd0, up0, r0 = corpo(lambda n: REST[n])
B0 = Matrix((fwd0, up0, r0)).transposed()
# direcoes dobradas no repouso (antes da varredura)
DOB = {}
for s in "lr":
    W = A.data.bones["wing_3_" + s].head_local; tip = A.data.bones["wing_tip_" + s].tail_local
    u = (tip - W).normalized()
    dedos = [A.data.bones["wing_feather_%d_tip_%s" % (i, s)].tail_local for i in (3, 4, 5)]
    v = sum(dedos, Vector()) / 3 - W; v = (v - u * v.dot(u)).normalized(); n = u.cross(v)
    for b in [b for b in ORD if b.endswith("_" + s)]:
        d = ydir(b); g = grupo(b)
        if g == "mao" and b.startswith("wing_feather_"):        # fecha o leque em direcao ao dedo-guia
            cu, cv, cn = d.dot(u), d.dot(v), d.dot(n); th = math.atan2(cv, cu) * FECHA; r = math.hypot(cu, cv)
            d = (u * math.cos(th) * r + v * math.sin(th) * r + n * cn).normalized()
        # dedo 2 (membrana interna do cotovelo) dobra AO CONTRARIO, para fora do dorso: dobrando junto ela afundava
        # na pele das costas (spine_0) ate 5 cm
        ang = {"braco": 0, "dedo2": -ALFA_E * DEDO2, "antebraco": ALFA_E, "mao": ALFA_E + ALFA_W}[g]
        DOB[b] = (Matrix.Rotation(math.radians(ang), 3, n) @ d).normalized()
def varredura(s, fwd, up, rgt, gama, delta):
    out = -rgt if s == "l" else rgt
    best = None
    for sg in (1, -1):
        R1 = Matrix.Rotation(math.radians(gama) * sg, 3, up)
        if best is None or (R1 @ out).dot(fwd) < (best @ out).dot(fwd): best = R1
    o1 = best @ out
    R2 = None
    for sg in (1, -1):
        Rt = Matrix.Rotation(math.radians(delta) * sg, 3, fwd)
        if R2 is None or (Rt @ o1).dot(up) < (R2 @ o1).dot(up): R2 = Rt
    return R2 @ best
for act in [bpy.data.actions["Silverwing_Idle"], bpy.data.actions["Silverwing_Walk"]]:
    for lay in act.layers:
        for st in lay.strips:
            for cb in st.channelbags:
                for fc in [fc for fc in cb.fcurves if fc.data_path.startswith('pose.bones["') and fc.data_path.split('"')[1] in ALVO]:
                    cb.fcurves.remove(fc)
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); per = f1 - f0
    andar = "Walk" in act.name
    for f in range(f0, f1 + 1):
        for n in ORD:
            pb = A.pose.bones[n]; pb.rotation_mode = "QUATERNION"; pb.matrix_basis.identity()
        sc.frame_set(f)
        ph = 2 * math.pi * (f - f0) / per
        fwd, up, rgt = corpo(lambda n: A.pose.bones[n].matrix)
        Bt = Matrix((fwd, up, rgt)).transposed(); Rcorpo = Bt @ B0.inverted()
        RS = {}
        for s in "lr":
            osc = math.sin(2 * ph + (0 if s == "l" else math.pi)) if andar else math.sin(ph)
            amp = 4.0 if andar else 2.5
            RS[s] = varredura(s, fwd, up, rgt, GAMA + amp * 0.5 * osc, DELTA + amp * osc) @ Rcorpo
            # braco e membrana interna caem pouco (a queda comeca no cotovelo): caindo a partir do ombro a membrana
            # interna afundava no dorso
            RS[s + "b"] = varredura(s, fwd, up, rgt, (GAMA + amp * 0.5 * osc) * QG, (DELTA + amp * osc) * QB) @ Rcorpo
        POSE = {}
        for n in ORD:
            chave = n[-1] + ("b" if grupo(n) in ("braco", "dedo2") else "")
            d = (RS[chave] @ DOB[n]).normalized()
            p = A.data.bones[n].parent.name
            Mp = POSE[p] if p in POSE else A.pose.bones[p].matrix.copy()
            Mc = Mp @ REL[n]; y = rot(Mc) @ Vector((0, 1, 0))
            Md = Matrix.Translation(Mc.translation) @ (y.rotation_difference(d).to_matrix() @ rot(Mc)).to_4x4()
            POSE[n] = Md
            A.pose.bones[n].rotation_quaternion = (Mc.inverted() @ Md).to_quaternion()
            A.pose.bones[n].keyframe_insert("rotation_quaternion", frame=f, group=n)
    print("DOBRA", act.name, f0, f1, "params", GAMA, DELTA, ALFA_E, ALFA_W, FECHA)
A.animation_data.action = None
for pb in A.pose.bones: pb.matrix_basis.identity()
for m in M.modifiers: m.show_viewport = True
bpy.ops.wm.save_mainfile()
print("DOBRA_OK")
