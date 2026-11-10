"""Compara a malha deformada do rig ORIGINAL com a da variante com Pelo* (Pelo* parados), em todos os clipes.
Salva as posicoes do original num .npy e, na segunda chamada, mede a diferenca. Pelo* sem chave = pose de descanso.
Uso: blender -b <Anim.blend> -P comparar_deformacao.py -- <arquivo.npz> salvar|comparar"""
import bpy, sys, numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; ARQ, MODO = A[0], A[1]
sc = bpy.context.scene; arm = bpy.data.objects["Urso_Rig"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
MAL = [bpy.data.objects[n] for n in ("Urso_Cabeca", "Urso_Corpo_Frente", "Urso_Corpo_Tras", "Urso_Boca")]
res = {}
for act in sorted(a.name for a in bpy.data.actions if a.name.startswith("Urso_")):
    arm.animation_data.action = bpy.data.actions[act]; n = int(bpy.data.actions[act].frame_range[1])
    for q in range(1, n + 1, 6):
        sc.frame_set(q); dg = bpy.context.evaluated_depsgraph_get(); pts = []
        for o in MAL:
            ev = o.evaluated_get(dg); me = ev.to_mesh(); co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", co)
            pts.append((np.array(o.matrix_world)[:3, :3] @ co.reshape(-1, 3).T).T + np.array(o.matrix_world)[:3, 3]); ev.to_mesh_clear()
        res["%s:%d" % (act, q)] = np.concatenate(pts)
if MODO == "salvar": np.savez_compressed(ARQ, **res); print("SALVO", len(res))
else:
    ref = np.load(ARQ); piores = []
    for k, v in res.items():
        r = ref[k][:len(v)]; d = np.linalg.norm(v[:len(r)] - r, axis=1); piores.append((float(d.max()), float(np.percentile(d, 99.9)), k, float(v[:, 2].min() - r[:, 2].min())))
    piores.sort(reverse=True)
    print("DEFORMACAO max %.4f p99.9 %.4f em %s" % (piores[0][0], piores[0][1], piores[0][2]))
    print("DIF_CHAO max %.4f" % max(abs(p[3]) for p in piores))
    for p in piores[:6]: print("  ", p[2], "max %.4f p99.9 %.4f chao %+.4f" % (p[0], p[1], p[3]))
