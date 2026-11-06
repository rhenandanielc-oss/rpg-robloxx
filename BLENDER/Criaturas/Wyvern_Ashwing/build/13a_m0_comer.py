# M0 (somente leitura) do Comer: por quadro (30 Hz), z minimo da malha por regiao e o osso dominante do vertice mais baixo.
# Uso: blender -b <v.blend> -P 13a_m0_comer.py -- <08_base.py> <saida.json> [clipe=Comer]
import bpy, sys, json
argv = sys.argv[sys.argv.index("--") + 1:]
exec(open(argv[0], encoding="utf-8").read())
OUTJ = argv[1]; CL = argv[2] if len(argv) > 2 else "Comer"
a = bpy.data.actions[CL]
for ob, tipo in ((arm, "OBJECT"), (key, "KEY")):
    ob.animation_data.action = a; ob.animation_data.action_slot = [s for s in a.slots if s.target_id_type == tipo][0]
R_ = []
f = 0.0
while f <= a.frame_range[1] + 1e-6:
    sc.frame_set(int(f), subframe=f - int(f))
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    co = np.empty(len(ev.vertices) * 3); ev.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
    m = np.array(obj.matrix_world); co = co @ m[:3, :3].T + m[:3, 3]
    reg = {r: round(float(co[REG == r][:, 2].min()), 3) for r in sorted(set(REG))}
    i = int(co[:, 2].argmin())
    R_.append({"f": round(f, 1), "zmin": round(float(co[i, 2]), 3), "osso": DOM[i], "regioes": reg})
    f += 0.8
abaixo = [r for r in R_ if r["zmin"] < -0.03]
res = {"clipe": CL, "quadros": len(R_), "zmin": min(r["zmin"] for r in R_), "quadros_abaixo_-0.03": len(abaixo),
       "por_osso": {o: sum(1 for r in abaixo if r["osso"] == o) for o in sorted({r["osso"] for r in abaixo})},
       "regiao_min": {k: min(r["regioes"][k] for r in R_) for k in R_[0]["regioes"]}, "por_quadro": R_}
json.dump(res, open(OUTJ, "w"), indent=0)
print("M0", json.dumps({k: v for k, v in res.items() if k != "por_quadro"}))
for r in R_[::6]: print("Q", r["f"], r["zmin"], r["osso"], r["regioes"]["cabeca"], r["regioes"]["pernaL"], r["regioes"]["pernaR"])
