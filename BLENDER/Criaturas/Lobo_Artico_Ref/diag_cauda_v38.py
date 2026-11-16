"""v38 diagnostico: caminho da cauda (Cauda1..Cauda4) em Sentar e LevantarSentado, medido no referencial do tronco.
Angulo da cauda no plano sagital do tronco: 0 = apontando para a frente ao longo das costas, +90 = para cima, 180 = para tras,
-90 = para baixo (por dentro do corpo / entre as traseiras). 'Por fora' = o caminho passa por cima (angulos positivos).
Uso: blender -b <blend> -P diag_cauda_v38.py -- <saida.json> [acoes]"""
import bpy, sys, json, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = a[0]; ACS = a[1].split(",") if len(a) > 1 else ["Sentar", "LevantarSentado"]
ARM = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]; P = ARM.pose.bones; sc = bpy.context.scene
def ang(ac, q):
    act = bpy.data.actions[ac]; ARM.animation_data.action = act
    if len(act.slots): ARM.animation_data.action_slot = act.slots[0]
    sc.frame_set(q); bpy.context.view_layer.update()
    fr = (P["Coluna3"].head - P["Quadril"].head).normalized()          # frente do tronco (quadril -> peito)
    up = V((1, 0, 0)).cross(fr).normalized()
    if up.z < 0: up = -up
    r = {}
    for n in ("Cauda1", "Cauda2", "Cauda3", "Cauda4"):
        d = (P[n].tail - P["Cauda1"].head).normalized()
        r[n] = round(math.degrees(math.atan2(d.dot(up), d.dot(fr))), 1)
    r["lat"] = round(max(abs((P[n].tail - P["Cauda1"].head).x) for n in ("Cauda4",)), 3)
    return r
R = {}
for ac in ACS:
    act = bpy.data.actions[ac]; n = int(act.frame_range[1]); R[ac] = {q: ang(ac, q) for q in range(0, n + 1, 2 if n > 60 else 1)}
R["Repouso_q0"] = ang("Repouso", 0)
json.dump(R, open(OUT, "w"), indent=0)
for ac in ACS:
    print(ac, " ".join("%d:%s/%s" % (q, v["Cauda1"], v["Cauda4"]) for q, v in R[ac].items()))
print("Repouso", R["Repouso_q0"]); print("DIAG_CAUDA_OK")
