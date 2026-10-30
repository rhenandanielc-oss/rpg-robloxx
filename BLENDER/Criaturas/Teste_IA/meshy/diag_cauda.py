"""Diagnostico da cauda (somente leitura): raio da malha por segmento, desvio lateral/vertical da raiz em relacao a
linha da coluna, angulos entre segmentos por clipe, menor altura da malha da cauda (corte no chao), estiramento de
arestas na juncao quadril-cauda, e render de perto (lado/topo/tras) por clipe.
Uso: blender -b arq.blend -P diag_cauda.py -- saida_dir"""
import bpy, sys, os, math
from mathutils import Vector
out = sys.argv[sys.argv.index("--") + 1:][0]; os.makedirs(out, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
CAUDA = ["tail_1", "tail_2", "tail_3", "tail_4", "tail_5", "tail_6", "tail_tip"]
gi = {g.index: g.name for g in M.vertex_groups}
def dom(v): return gi[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "-"
D = [dom(v) for v in M.data.vertices]
# raio por segmento (repouso)
for n in CAUDA + ["hips"]:
    b = A.data.bones[n]; h, t = b.head_local, b.tail_local; ax = (t - h).normalized()
    ds = [((v.co - h) - ax * (v.co - h).dot(ax)).length for i, v in enumerate(M.data.vertices) if D[i] == n]
    zs = [v.co.z for i, v in enumerate(M.data.vertices) if D[i] == n]
    cx = sum(v.co.x for i, v in enumerate(M.data.vertices) if D[i] == n) / max(1, len(ds))
    print("RAIO", n, "verts", len(ds), "medio", round(sum(ds) / max(1, len(ds)), 3), "max", round(max(ds or [0]), 3),
          "zmin", round(min(zs or [0]), 3), "x_malha", round(cx, 3), "x_osso", round(h.x, 3), "head", tuple(round(c, 3) for c in h))
sp = A.data.bones["spine_0"]; hp = A.data.bones["hips"]
print("LINHA coluna spine_0", tuple(round(c, 3) for c in sp.head_local), "->", tuple(round(c, 3) for c in sp.tail_local),
      "hips", tuple(round(c, 3) for c in hp.head_local), "->", tuple(round(c, 3) for c in hp.tail_local))
juncao = set(i for i, d in enumerate(D) if d in ("hips", "tail_1", "tail_2", "hips_anchor_l", "hips_anchor_r", "spine_0"))
E = [tuple(e.vertices) for e in M.data.edges if e.vertices[0] in juncao or e.vertices[1] in juncao]
R0 = [v.co.copy() for v in M.data.vertices]
cam = bpy.data.objects["cam_rev"]; sc.camera = cam; sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 520, 360
cauda_v = [i for i, d in enumerate(D) if d.startswith("tail")]
for nome in ["Parado", "Andar", "Correr", "Voo", "Curva_E", "Subida", "Descida", "Pairar"]:
    act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); f = f0 + (f1 - f0) // 3; sc.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh(); P = [v.co.copy() for v in me.vertices]; M.evaluated_get(dg).to_mesh_clear()
    angs = []
    for i in range(len(CAUDA) - 1):
        a = (A.pose.bones[CAUDA[i]].tail - A.pose.bones[CAUDA[i]].head).normalized(); b = (A.pose.bones[CAUDA[i + 1]].tail - A.pose.bones[CAUDA[i + 1]].head).normalized()
        angs.append(round(math.degrees(a.angle(b)), 1))
    hb = A.pose.bones["hips"]; t1 = A.pose.bones["tail_1"]; s0 = A.pose.bones["spine_0"]
    col = (hb.head - s0.tail).normalized() if False else (A.pose.bones["hips"].head - A.pose.bones["spine_1"].head).normalized()
    base = math.degrees(col.angle((t1.tail - t1.head).normalized()))
    est = sum(1 for a, b in E if (R0[a] - R0[b]).length > 1e-6 and (P[a] - P[b]).length / (R0[a] - R0[b]).length > 1.6)
    zmin = min(P[i].z for i in cauda_v)
    lat = [round(A.pose.bones[n].head.x + 0.02, 3) for n in CAUDA]
    print("CLIPE", nome, f, "angs", angs, "base_vs_coluna", round(base, 1), "estic_juncao", est, "zmin_malha", round(zmin, 3), "lateral", lat)
    c = A.pose.bones["tail_2"].head.copy()
    for vista, d in (("lado", (1, 0, 0.05)), ("topo", (0.01, 0.2, 1)), ("tras", (0.15, 1, 0.3))):
        cam.location = c + Vector(d).normalized() * 1.1; cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, "cauda_%s_%s.png" % (nome, vista)); bpy.ops.render.render(write_still=True)
print("DIAG_CAUDA_OK")
