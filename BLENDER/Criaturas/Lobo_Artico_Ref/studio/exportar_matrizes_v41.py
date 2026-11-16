"""So leitura: matrizes completas dos ossos (espaco do armature) no repouso e em quadros de teste, para conferir o GIRO
de cada osso no Studio (as pontas sozinhas nao mostram o giro em torno do proprio eixo). Saida json_v41/matrizes_v41.json."""
import bpy, sys, os, json
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); sc = bpy.context.scene; A = bpy.data.objects["LoboArtico_Rig"]
def m3(m): return [[round(m[i][j], 5) for j in range(4)] for i in range(4)]
res = {"rest": {b.name: m3(b.matrix_local) for b in A.data.bones}, "poses": {}}
for nome, f in (("Farejar", 30), ("Sentado", 0), ("Corrida", 7), ("Deitar", 80), ("Sacudir", 30), ("Uivando", 60)):
    act = bpy.data.actions[nome]; A.animation_data.action = act
    if A.animation_data.action_slot is None and len(act.slots): A.animation_data.action_slot = act.slots[0]
    sc.frame_set(f); res["poses"]["%s|%d" % (nome, f)] = {b.name: m3(b.matrix) for b in A.pose.bones}
json.dump(res, open(OUT, "w")); print("MATRIZES_OK")
