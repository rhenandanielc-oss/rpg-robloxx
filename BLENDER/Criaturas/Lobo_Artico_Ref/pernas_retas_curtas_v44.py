"""v44b: a MESMA correcao v31 (pernas dianteiras retas, dobra no plano sagital) aplicada SO as viradas curtas da v44, para a
emenda com o Repouso atual (que ja passou pela v31) ficar exata. Uso: blender -b anim_v44/CR_LoboArtico_Anim.blend -P pernas_retas_curtas_v44.py -- anim_v44b
--- texto original da v31: ---
v31: pernas DIANTEIRAS retas vistas de frente (pedido do usuario: "a perna se curva toda e vira, deixe mais reto ao se movimentar").
Diagnostico (diag_perna_frontal_v31.py, anim_v30): o IK do braco escolhe o lado da dobra pelo vetor de dobra da pose de repouso, que ja
e inclinado (plano 4-7 graus no Repouso) e gira junto com o pai: o cotovelo entrava para baixo do peito (ate 0,18 stud no Andar, 0,24 no
Trote, 1,06 na Corrida; plano da dobra ate 80 graus) e a perna fazia arco na vista de frente.
Correcao = pos-processo em TODOS os quadros de TODAS as acoes (inclusive Repouso, para as emendas continuarem exatas), so Umero/Antebraco
das dianteiras: o mesmo IK de 2 ossos da marcha_v21 com o vetor de dobra PROJETADO no plano sagital (sem componente X) -> o cotovelo fica
no plano vertical frente-tras que passa pelo ombro e pelo punho. O PUNHO fica no mesmo lugar e o Metacarpo/Dedos mantem a orientacao no
mundo: pe e apoio identicos (deslize inalterado). Funcao so da pose de cada quadro: pontas iguais continuam iguais.
Uso: blender -b anim_v30/CR_LoboArtico_Anim.blend -P pernas_retas_v31.py -- <dir_saida>"""
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V
import marcha_v21 as M
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
ARM = M.ARM; P = M.P; sc = bpy.context.scene
CADEIA = {"DE": ("Umero_E", "Antebraco_E", "Metacarpo_E", "Dedos_E"), "DD": ("Umero_D", "Antebraco_D", "Metacarpo_D", "Dedos_D")}
def ik_reto(k, T):
    sup, inf = CADEIA[k][:2]; bs, bi = M.B[sup], M.B[inf]; a_, b_ = bs.length, bi.length
    S = P[sup].head.copy(); Mpai = P[sup].parent.matrix @ M.B[sup].parent.matrix_local.inverted()
    K0, S0 = bs.tail_local, bs.head_local; d0 = (bi.tail_local - S0).normalized(); dob = Mpai.to_3x3() @ ((K0 - S0) - d0 * (K0 - S0).dot(d0))
    dob = V((0.0, dob.y, dob.z))                                       # v31: dobra no plano sagital (sem componente lateral)
    dv = T - S; d = min(dv.length, (a_ + b_) * 0.9995); dn = dv.normalized()
    al = (a_ * a_ - b_ * b_ + d * d) / (2 * d); h = math.sqrt(max(a_ * a_ - al * al, 0.0))
    perp = V((1.0, 0.0, 0.0)).cross(dn).normalized()                   # dobra perpendicular ao eixo lateral e a reta ombro-punho (sempre definida)
    ref = dob if abs(dob.normalized().dot(perp)) > 0.2 else (K_ORIG[0] - S)  # sentido: o do vetor de dobra; se ambiguo, o do cotovelo original
    if perp.dot(ref) < 0: perp = -perp
    K = S + dn * al + perp * h
    for nome, h0, t0 in ((sup, S, K), (inf, K, S + dn * d)):
        yv = (t0 - h0).normalized(); xr = Mpai.to_3x3() @ M.REST[nome].col[0].to_3d(); xv = (xr - yv * xr.dot(yv)).normalized()
        Mx = Matrix((xv, yv, xv.cross(yv))).transposed().to_4x4(); Mx.translation = h0; P[nome].matrix = Mx; bpy.context.view_layer.update()
    return (S + dn * d - T).length
OSSOS = [n for c in CADEIA.values() for n in c]; REL = {"acoes": {}}; K_ORIG = [None]
for pb in P: pb.rotation_mode = "QUATERNION"
for acn in [a for a in bpy.data.actions if a.name in ("VirarCurtoEsquerda", "VirarCurtoDireita")]:
    ARM.animation_data.action = acn
    if len(acn.slots): ARM.animation_data.action_slot = acn.slots[0]
    f0, f1 = (int(x) for x in acn.frame_range); NOVOS = []; err = 0.0; mpe = 0.0
    for q in range(f0, f1 + 1):
        ARM.animation_data.action = acn; sc.frame_set(q); bpy.context.view_layer.update()
        orig = {n: P[n].rotation_quaternion.copy() for n in OSSOS}; base = {n: P[n].matrix.copy() for n in OSSOS}; ARM.animation_data.action = None
        for n in OSSOS: P[n].matrix = base[n]
        bpy.context.view_layer.update(); r = {}
        for k, (sup, inf, met, ded) in CADEIA.items():
            W = base[inf].to_translation() + base[inf].col[1].xyz * M.B[inf].length                      # punho = cauda do antebraco
            K_ORIG[0] = base[inf].to_translation()
            err = max(err, ik_reto(k, W))
            om = base[met].copy(); om.translation = P[inf].tail; P[met].matrix = om; bpy.context.view_layer.update()
            od = base[ded].copy(); od.translation = P[met].tail; P[ded].matrix = od; bpy.context.view_layer.update()
            mpe = max(mpe, (P[ded].tail - (base[ded].to_translation() + base[ded].col[1].xyz * M.B[ded].length)).length)
            for n in (sup, inf, met, ded):
                qn = P[n].rotation_quaternion.copy()
                if qn.dot(orig[n]) < 0: qn = -qn
                r[n] = qn
        NOVOS.append(r)
    cb = acn.layers[0].strips[0].channelbag(acn.slots[0])
    for n in OSSOS:
        for i in range(4):
            fc = cb.fcurves.find('pose.bones["%s"].rotation_quaternion' % n, index=i)
            kp = {int(round(p.co.x)): p for p in fc.keyframe_points}
            for qi, q in enumerate(range(f0, f1 + 1)):
                if q in kp: p = kp[q]; p.co.y = NOVOS[qi][n][i]; p.handle_left_type = "AUTO_CLAMPED"; p.handle_right_type = "AUTO_CLAMPED"
            fc.update()
    ARM.animation_data.action = None
    for pb in P: pb.matrix_basis.identity()
    REL["acoes"][acn.name] = {"erro_ik_max": round(err, 7), "desvio_ponta_dedos_max": round(mpe, 7), "quadros": f1 - f0 + 1}
    print("V31", acn.name, REL["acoes"][acn.name], flush=True)
ARM.animation_data.action = bpy.data.actions["Andar"]
json.dump(REL, open(os.path.join(OUT, "pernas_retas_curtas_v44.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("PERNAS_RETAS_CURTAS_V44_OK", flush=True)
