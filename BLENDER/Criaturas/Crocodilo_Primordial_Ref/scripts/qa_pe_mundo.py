"""QA dos pes no MUNDO para clipes de giro/deslocamento (acao assada, restricoes desligadas):
 (b) OSSO: velocidade da cabeca do osso Mao/Pe (punho/tornozelo) durante o apoio;
 (c) MALHA: velocidade do centroide da SOLA (vertices com peso > 0,5 no osso Mao/Pe e z de repouso < 0,35) durante o apoio.
O corpo recebe a transformacao que o jogo aplica: giro (sincronizacao.giro_graus_s em torno de pivo_y) ou deslocamento.
Apoio = fase do laco < fracao de apoio (viradas: 0,65; pares diagonais MaoE/PeD fase 0, MaoD/PeE fase 0,5).
Uso: blender -b CR_Crocodilo_Anim.blend -P qa_pe_mundo.py -- <clipe> [apoio]"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V, Matrix as M
A = sys.argv[sys.argv.index("--") + 1:]; CL = A[0]; APOIO = float(A[1]) if len(A) > 1 else 0.65
sc = bpy.context.scene; arm = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
d = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "clipes", "Crocodilo_%s.json" % CL)))
s = d.get("sincronizacao", {}); w = math.radians(s.get("giro_graus_s", 0.0)); py = s.get("pivo_y", 0.0); vel = d.get("velocidade", 0.0)
act = bpy.data.actions["Croc_" + CL]; arm.animation_data.action = act; arm.animation_data.action_slot = act.slots[0]
f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); nq = f1 - f0 + 1; T = d["duracao"]
FASE = {"MaoE": 0.0, "PeD": 0.0, "MaoD": 0.5, "PeE": 0.5}
sola = {}
for k in FASE:
    g = lo.vertex_groups[k].index
    sola[k] = [v.index for v in lo.data.vertices if v.co.z < 0.35 and any(gg.group == g and gg.weight > 0.5 for gg in v.groups)]
dg = bpy.context.evaluated_depsgraph_get()
hist = {k: [] for k in FASE}
for qi in range(nq):
    sc.frame_set(f0 + qi); t = qi / 30.0
    G = M.Translation(V((0, py, 0))) @ M.Rotation(w * t, 4, "Z") @ M.Translation(V((0, -py, 0))) @ M.Translation(V((0, -vel * t, 0)))
    ev = lo.evaluated_get(dg); me = ev.to_mesh(); co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    for k in FASE:
        ossow = G @ (arm.matrix_world @ arm.pose.bones[k].head)
        c = co[sola[k]].mean(axis=0); solaw = G @ V(c)
        fase = ((t / T) + FASE[k]) % 1.0
        hist[k].append((fase, ossow.copy(), solaw.copy()))
    ev.to_mesh_clear()
pior_b = (0, None); pior_c = (0, None)
for k, h in hist.items():
    for i in range(1, nq):
        fa, ob_, sb = h[i]; fp, ob0, sb0 = h[i - 1]
        if fa < APOIO and fp < APOIO and fp < fa:
            vb = (ob_ - ob0).length * 30; vc = (sb - sb0).length * 30
            if vb > pior_b[0]: pior_b = (vb, (k, i, round(fa, 3)))
            if vc > pior_c[0]: pior_c = (vc, (k, i, round(fa, 3)))
print("QA_MUNDO", CL, "| (b) osso max %.3f studs/s em %s | (c) sola max %.3f studs/s em %s | verts sola %s" % (
    pior_b[0], pior_b[1], pior_c[0], pior_c[1], {k: len(v) for k, v in sola.items()}))
