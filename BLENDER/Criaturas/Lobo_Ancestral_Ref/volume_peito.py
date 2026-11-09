"""Peitoral acima das patas com MAIS PONTAS de pelo, mechas mais separadas e mais volume (pedido 05/11, depois de ver o
alisamento de alisar_peito.py: "quero mais pontas de pelos aparecendo, mais separados e volumosos"). Base: rig12 (peito
original, nao o alisado). Na regiao (frente do peito, z Z0..Z1; cabeca e patas fora):
 - superficie de referencia = malha suavizada (Taubin, preserva volume) -> o "pelo" e o quanto cada vertice sai dela;
 - as mechas que SAEM da superficie sao exageradas por (1 + REALCA) -> pontas mais longas e separadas entre si;
 - a regiao inteira cresce INFLA para fora (volume) e as pontas caem um pouco (CAI, como pelo pesado).
UV, textura, topologia, pesos e rig intactos; simetrico.
Uso: blender -b rig12/Lobo_Ancestral_Rig.blend -P volume_peito.py -- <saida_dir> [realca infla cai]"""
import bpy, sys, os, json
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
REALCA, INFLA, CAI = (float(A[1]), float(A[2]), float(A[3])) if len(A) > 3 else (0.9, 0.07, 0.25)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
yo = BD["BracoE"].head_local.y
Z0, Z1 = 2.9, 5.9
n = len(me.vertices); co = np.array([v.co[:] for v in me.vertices]); co0 = co.copy()
gi = {g.index: g.name for g in LO.vertex_groups}
cab = np.array([any(gi[g.group] in ("Cabeca", "Mandibula", "OrelhaE", "OrelhaD") and g.weight > 0.3 for g in v.groups) for v in me.vertices])
perna = np.array([sum(g.weight for g in v.groups if gi[g.group].startswith(("Antebraco", "Mao", "Dedos"))) for v in me.vertices])
viz = [[] for _ in range(n)]
for e in me.edges: a, b = e.vertices; viz[a].append(b); viz[b].append(a)
VZ = [np.array(v, int) for v in viz]
def media(f): return np.array([f[VZ[i]].mean(axis=0) if len(VZ[i]) else f[i] for i in range(n)])
w = (suave((co[:, 2] - Z0) / 0.35) * suave((Z1 - co[:, 2]) / 0.5) * suave(((yo + 0.9) - co[:, 1]) / 0.6)
     * suave((1.75 - np.abs(co[:, 0])) / 0.35) * (1 - np.clip(perna * 1.5, 0, 1)) * (~cab))
for _ in range(2): w = 0.5 * w + 0.5 * media(w)
borda = np.array([len(v) < 3 for v in VZ]); w[borda] = 0
# superficie de referencia (Taubin) e sua normal
cs = co0.copy()
for _ in range(40):
    cs = cs + 0.55 * (media(cs) - cs); cs = cs - 0.58 * (media(cs) - cs)
me.calc_loop_triangles(); tri = np.array([t.vertices[:] for t in me.loop_triangles])
ns = np.zeros_like(cs); fn = np.cross(cs[tri[:, 1]] - cs[tri[:, 0]], cs[tri[:, 2]] - cs[tri[:, 0]])
for k in range(3): np.add.at(ns, tri[:, k], fn)
ns /= np.maximum(np.linalg.norm(ns, axis=1, keepdims=True), 1e-9)
off = co0 - cs; fora = (off * ns).sum(axis=1)
ponta = suave(fora / 0.12)                                             # 0 na superficie, 1 nas pontas das mechas
desloc = (off * REALCA * ponta[:, None]                                # mecha mais longa e separada
          + ns * INFLA                                                 # volume
          + np.array([0, 0, -1.0]) * CAI * REALCA * np.maximum(fora, 0)[:, None] * ponta[:, None])   # ponta cai um pouco
co = co0 + desloc * w[:, None]
co[np.abs(co0[:, 0]) < 1e-6, 0] = 0.0
me.vertices.foreach_set("co", co.ravel()); me.update()
d = np.linalg.norm(co - co0, axis=1)
rel = {"realca": REALCA, "infla": INFLA, "cai": CAI, "vertices_regiao": int((w > 0.1).sum()), "pontas": int(((ponta > 0.5) & (w > 0.3)).sum()),
       "desloc_max": round(float(d.max()), 3), "desloc_med_regiao": round(float(np.median(d[w > 0.5])), 3)}
print("VOLUME", rel)
json.dump(rel, open(os.path.join(OUT, "volume_peito.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("VOLUME_PEITO_OK")
