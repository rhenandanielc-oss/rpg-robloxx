"""QA da malha deformada contra o chao (z = 0) nas acoes FK: menor z por regiao (cabeca, corpo, cauda, patas) e quadro do
pior caso. regiao = osso de maior peso (pes = Mao*/Pe*, a sola apoia em z ~0). Uso:
blender -b CR_Crocodilo_Anim.blend -P qa_malha_chao.py -- Clipe1,Clipe2 [saida.json]"""
import bpy, sys, json
A = sys.argv[sys.argv.index("--") + 1:]
arm = bpy.data.objects["CR_Croc_Rig"]; me = bpy.data.objects["CR_Croc_LOW"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
gi = {g.index: g.name for g in me.vertex_groups}
dono = {}
for v in me.data.vertices:                                   # regiao pelo osso de maior peso
    if v.groups: dono[v.index] = gi[max(v.groups, key=lambda g: g.weight).group]
def regiao(i, co):
    n = dono.get(i, "")
    if n[:3] in ("Mao", "PeE", "PeD"): return "pes"
    if n.startswith(("Antebraco", "Canela", "Braco", "Coxa")): return "pernas"
    if n.startswith("Cauda"): return "cauda"
    if n in ("Cabeca", "Mandibula", "Pescoco2"): return "focinho" if co.y < -13.0 else "cabeca"
    return "corpo"
res = {}
for nome in A[0].split(","):
    act = bpy.data.actions["Croc_" + nome]; arm.animation_data.action = act
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); pior = {}
    for f in range(f0, f1 + 1):
        bpy.context.scene.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = me.evaluated_get(dg); m = ev.to_mesh()
        mw = me.matrix_world; rest = me.data.vertices
        for v in m.vertices:
            z = (mw @ v.co).z; rg = regiao(v.index, rest[v.index].co)
            if rg not in pior or z < pior[rg][0]: pior[rg] = (round(z, 3), f, round((mw @ v.co).x, 2), round((mw @ v.co).y, 2))
        ev.to_mesh_clear()
    res[nome] = pior; print("CHAO", nome, pior, flush=True)
if len(A) > 1: json.dump(res, open(A[1], "w"), indent=1)
