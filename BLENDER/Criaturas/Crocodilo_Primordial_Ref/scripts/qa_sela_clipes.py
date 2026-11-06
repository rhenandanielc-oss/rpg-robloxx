"""Lote 5: folga da sela (deformada pelo rig) x pele do crocodilo em todos os clipes. Por clipe e por peca (material):
menor distancia com sinal (negativa = a sela entra na pele) e quantos vertices entram mais de 0,05.
Uso: blender -b CR_Crocodilo_Sela.blend -P qa_sela_clipes.py -- <saida.json> [passo] [clipes]"""
import bpy, sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manequim_r15 as mq
A = sys.argv[sys.argv.index("--") + 1:]; PASSO = int(A[1]) if len(A) > 1 else 2
sc = bpy.context.scene; croc = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]; sela = bpy.data.objects["CR_Croc_Sela"]
for pb in croc.pose.bones:
    for c in pb.constraints: c.mute = True
PECA = {i: m.name.replace("M_Sela_", "") for i, m in enumerate(sela.data.materials)}
vpeca = {}
for p in sela.data.polygons:
    for v in p.vertices: vpeca.setdefault(v, PECA[p.material_index])
acoes = sorted((a for a in bpy.data.actions if a.name.startswith("Croc_")), key=lambda a: a.name)
if len(A) > 2: acoes = [bpy.data.actions["Croc_" + n] for n in A[2].split(",")]
res = {}
for act in acoes:
    croc.animation_data.action = act; croc.animation_data.action_slot = act.slots[0]
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); pior = {}; n_ruim = 0
    for f in range(f0, f1 + 1, PASSO):
        sc.frame_set(f); bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get(); bvh = mq.bvh_croc(lo)
        ev = sela.evaluated_get(dg); me = ev.to_mesh(); W = sela.matrix_world
        for v in me.vertices:
            w = W @ v.co; loc, _, _, d = bvh.find_nearest(w, 0.6)
            if loc is None: continue
            if d < 0.25 and mq.dentro(bvh, w):
                pc = vpeca[v.index]
                if -d < pior.get(pc, (9, 0))[0]: pior[pc] = (round(-d, 3), f - f0)
                if d > 0.05: n_ruim += 1
        ev.to_mesh_clear()
    nome = act.name[5:]; res[nome] = {"pior_por_peca": pior, "vertices_quadro_abaixo_-0,05": n_ruim}
    print("QA_SELA %-24s %s | >0,05: %d" % (nome, " ".join("%s %.3f(q%d)" % (k, v[0], v[1]) for k, v in sorted(pior.items())) or "sem contato", n_ruim), flush=True)
json.dump(res, open(A[0], "w"), indent=1)
print("QA_SELA_OK")
