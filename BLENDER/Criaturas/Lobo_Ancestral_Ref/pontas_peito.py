"""MECHAS NOVAS no peitoral acima das patas (pedido 05/11: "mais pontas de pelo aparecendo, mais separados e volumosos").
A malha e leve: so alongar as pontas existentes (volume_peito.py) muda pouco. Aqui nascem N mechas afiladas (piramide de
3 lados + base = 4 tris cada) espalhadas na superficie da regiao com espacamento minimo, apontando para BAIXO e para FORA
(como pelo pesado do peito), tamanhos variados. Cada mecha: UV = a do ponto onde nasce (cor do pelo local; a ponta um
pouco mais clara pela UV vizinha mais alta), pesos = os do vertice mais proximo (acompanha clipes e o vento do pelo),
normais personalizadas: as antigas ficam, as novas = normal da face. Simetrico (lado -X espelha o +X).
Uso: blender -b rig13/Lobo_Ancestral_Rig.blend -P pontas_peito.py -- <saida_dir> [n_metade espacamento]"""
import bpy, bmesh, sys, os, json, math, random
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
N_METADE, ESP = (int(A[1]), float(A[2])) if len(A) > 2 else (110, 0.19)
random.seed(7)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
yo = BD["BracoE"].head_local.y
gi = {g.index: g.name for g in LO.vertex_groups}
antes_tris = sum(len(p.vertices) - 2 for p in me.polygons)
co = np.array([v.co[:] for v in me.vertices])
cab = np.array([any(gi[g.group] in ("Cabeca", "Mandibula", "OrelhaE", "OrelhaD") and g.weight > 0.2 for g in v.groups) for v in me.vertices])
perna = np.array([sum(g.weight for g in v.groups if gi[g.group].startswith(("Antebraco", "Mao", "Dedos"))) for v in me.vertices])
me.calc_loop_triangles(); uvd = me.uv_layers.active.data
T = list(me.loop_triangles)
tv = np.array([t.vertices[:] for t in T]); tuv = np.array([[uvd[l].uv[:] for l in t.loops] for t in T])
cen = co[tv].mean(axis=1); fn = np.array([t.normal[:] for t in T]); area = np.array([t.area for t in T])
# faces candidatas (lado +X; o -X e espelho): frente do peito, olhando para fora/frente, fora da cabeca e das patas
ok = ((cen[:, 0] > 0.04) & (cen[:, 0] < 1.65) & (cen[:, 2] > 3.15) & (cen[:, 2] < 5.6) & (cen[:, 1] < yo + 0.7)
      & (fn[:, 1] < 0.25) & (~cab[tv].any(axis=1)) & (perna[tv].max(axis=1) < 0.4))
cand = np.nonzero(ok)[0]; pesos = area[cand] / area[cand].sum()
print("faces candidatas", len(cand))
pontos = []
tent = 0
while len(pontos) < N_METADE and tent < 20000:
    tent += 1
    fi = int(np.random.default_rng(tent).choice(cand, p=pesos))
    r1, r2 = random.random(), random.random()
    if r1 + r2 > 1: r1, r2 = 1 - r1, 1 - r2
    L_ = np.array([1 - r1 - r2, r1, r2]); p = L_ @ co[tv[fi]]
    if any(np.linalg.norm(p - q[0]) < ESP for q in pontos): continue
    pontos.append((p, fi, L_))
print("mechas por lado", len(pontos))
PESOS = [{g.group: g.weight for g in v.groups} for v in me.vertices]   # (pesos lidos antes: o bmesh reindexa ao criar vertices)
cn = np.empty(len(me.loops) * 3); me.corner_normals.foreach_get("vector", cn); cn = cn.reshape(-1, 3)
bm = bmesh.new(); bm.from_mesh(me)
ln = bm.loops.layers.float_vector.new("nrm_tmp"); uvl = bm.loops.layers.uv.active; dl = bm.verts.layers.deform.active
for f in bm.faces:
    for l in f.loops: l[ln] = cn[l.index]
bm.verts.ensure_lookup_table()
from mathutils.kdtree import KDTree
kd = KDTree(len(co))
for i, p in enumerate(co): kd.insert(p, i)
kd.balance()
def mecha(p, n, uv, uv_ponta, viz, forma, sx):
    """MECHA CURVA em 2 segmentos (base -> meio -> ponta), lamina com frente e verso (6 tris). Sombreamento com a NORMAL DA
    PELE (a mecha se mistura ao peito; v2 com normal da face parecia triangulo colado). forma = (ruido x, ruido y,
    comprimento, meia-largura), sorteada uma vez e espelhada no lado -X (sx = -1)."""
    rx, ry, L, rb = forma
    n = V(n).normalized(); baixo = V((0, 0, -1))
    d1 = (n * 0.45 + baixo * 0.85 + V((rx * sx, ry, 0))).normalized()   # saida da pele
    d2 = (d1 + baixo * 0.9).normalized()                                 # a ponta cai (pelo pesado)
    t1 = V((0, 0, 1)).cross(d1).normalized() if abs(d1.z) < 0.99 else V((1, 0, 0))
    b0 = V(p) - n * 0.03; meio = V(p) + d1 * (0.5 * L); ponta = meio + d2 * (0.5 * L)
    pts = [b0 + t1 * rb, b0 - t1 * rb, meio + t1 * (rb * 0.6), meio - t1 * (rb * 0.6), ponta]
    vs = [bm.verts.new(q) for q in pts]
    vt = [bm.verts.new(q - n * 0.006) for q in pts]                       # verso: vertices proprios (mesma face nao pode repetir)
    for v in vs + vt:
        dv = v[dl]
        for k, x in viz.items(): dv[k] = x
    frente = [(0, 1, 3), (0, 3, 2), (2, 3, 4)]
    faces = []
    for tri_ in frente:
        f = bm.faces.new([vs[i] for i in tri_]); f.normal_update()
        if f.normal.dot(n) < 0: f.normal_flip()
        faces.append((f, 1))
        g = bm.faces.new([vt[i] for i in tri_][::-1]); g.normal_update()
        if g.normal.dot(n) > 0: g.normal_flip()
        faces.append((g, -1))
    for f, lado_ in faces:
        f.smooth = True
        for l in f.loops:
            l[uvl].uv = uv
            l[ln] = n * lado_ if l.vert not in (vs[4], vt[4]) else (n * 0.6 + d2 * 0.4).normalized() * lado_
    return len(faces)
novas = 0
for p, fi, L_ in pontos:
    uv = V(tuple(L_ @ tuv[fi])); uvp = V(tuple(tuv[fi][np.argmax(tuv[fi][:, 1])]))      # ponta: canto de UV mais alto da face
    viz = PESOS[kd.find(p)[1]]
    nrm = fn[fi]
    forma = (random.uniform(-0.15, 0.15), random.uniform(-0.1, 0.1), random.uniform(0.24, 0.48), random.uniform(0.045, 0.075))
    novas += mecha(p, nrm, uv, uvp, viz, forma, 1)
    pm = p * np.array([-1, 1, 1]); vizm = PESOS[kd.find(pm)[1]]
    novas += mecha(pm, (-nrm[0], nrm[1], nrm[2]), uv, uvp, vizm, forma, -1)   # espelho exato no lado -X
bm.to_mesh(me); bm.free(); me.update()
a = np.empty(len(me.loops) * 3); me.attributes["nrm_tmp"].data.foreach_get("vector", a); a = a.reshape(-1, 3)
a /= np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-9)
me.attributes.remove(me.attributes["nrm_tmp"]); me.normals_split_custom_set(a.tolist()); me.update()
depois_tris = sum(len(p.vertices) - 2 for p in me.polygons)
rel = {"mechas": 2 * len(pontos), "tris_antes": antes_tris, "tris_depois": depois_tris, "espacamento": ESP}
print("PONTAS", rel)
json.dump(rel, open(os.path.join(OUT, "pontas_peito.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("PONTAS_PEITO_OK")
