# Emendas entre clipes (somente leitura): diferenca de pose (graus por osso, deslocamento maximo de vertice) entre
# quadros escolhidos. Pares: clipe:inicio|fim -> clipe:inicio|fim.
# Uso: blender -b <v.blend> -P 14b_emendas.py -- <saida.json> "A:fim>B:ini,C:ini>D:ini,..."
import bpy, sys, json, math
argv = sys.argv[sys.argv.index("--") + 1:]
scn = bpy.context.scene; arm = bpy.data.objects["Wyvern_Rig"]; obj = bpy.data.objects["Wyvern"]; key = obj.data.shape_keys
def pose(nome, qual):
    a = bpy.data.actions[nome]
    for ob, tipo in ((arm, "OBJECT"), (key, "KEY")):
        ob.animation_data.action = a; ob.animation_data.action_slot = [s for s in a.slots if s.target_id_type == tipo][0]
    f = 0.0 if qual == "ini" else a.frame_range[1]; scn.frame_set(int(f), subframe=f - int(f))
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    return {pb.name: pb.matrix_basis.to_quaternion() for pb in arm.pose.bones}, [obj.matrix_world @ v.co for v in ev.vertices]
R = {}
for par in argv[1].split(","):
    a, b = par.split(">"); (qa, Pa), (qb, Pb) = pose(*a.split(":")), pose(*b.split(":"))
    ang = max((math.degrees(qa[n].rotation_difference(qb[n]).angle), n) for n in qa)
    R[par] = {"graus_max": [round(ang[0], 2), ang[1]], "desloc_max_vertice": round(max((Pa[i] - Pb[i]).length for i in range(len(Pa))), 4)}
json.dump(R, open(argv[0], "w"), indent=1); print("EMENDAS", json.dumps(R))
