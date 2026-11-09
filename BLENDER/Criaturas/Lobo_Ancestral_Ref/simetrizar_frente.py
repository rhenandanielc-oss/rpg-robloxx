"""Acabamento da leitura frontal do Lobo Ancestral (rig4, em repouso):
1. COR/NORMAL da frente dos ombros e do peito: a metade -X recebe o espelho da metade +X, texel a texel e SEM raios
   (texel -> ponto 3D pela UV -> espelho em X -> ponto mais proximo da superficie -> UV -> amostra), so na mascara macia.
   v1 (bake de copia espelhada) descartada: 69% dos texels sem acerto e borda magenta da cor-sentinela.
2. CABECA: giro de yaw em torno do eixo vertical do atlas ate a trufa ficar no meio das orelhas (x = 0); so posicoes de
   vertice da cabeca (transicao no pescoco). Pesos, UV, topologia e esqueleto intactos.
Uso: blender -b rig4/Lobo_Ancestral_Rig.blend -P simetrizar_frente.py -- <saida_dir> [sem_cabeca]"""
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector as V, Matrix
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
nr = np.empty(n * 3); me.vertices.foreach_get("normal", nr); nr = nr.reshape(-1, 3)
gi = {g.index: g.name for g in LO.vertex_groups}
dono = [gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else "" for v in me.vertices]
viz = [[] for _ in range(n)]
for e in me.edges: a, b = e.vertices; viz[a].append(b); viz[b].append(a)
def macia(m, it):
    m = m.astype(float)
    for _ in range(it): m = np.array([0.5 * m[i] + 0.5 * (m[viz[i]].mean() if viz[i] else m[i]) for i in range(n)])
    return m
rel = {}
# ------------------------------------------------------------------ 2. cabeca (antes do bake, para a mascara seguir a malha final)
if "sem_cabeca" not in A:
    cab = np.array([1.0 if d in ("Cabeca", "Mandibula", "OrelhaE", "OrelhaD") else (0.5 if d == "Pescoco2" else 0.0) for d in dono])
    w = np.clip(macia(cab, 3) * 1.2, 0, 1)
    nariz = co[np.argmin(co[:, 1])]; atl = BD["Cabeca"].head_local
    ang = math.atan2(nariz[0] - atl.x, -(nariz[1] - atl.y))                   # desvio do nariz (0 = para -Y)
    th = -ang * w; dx, dy = co[:, 0] - atl.x, co[:, 1] - atl.y
    co[:, 0] = atl.x + dx * np.cos(th) - dy * np.sin(th); co[:, 1] = atl.y + dx * np.sin(th) + dy * np.cos(th)
    me.vertices.foreach_set("co", co.ravel()); me.update()
    rel["cabeca_yaw_graus"] = round(math.degrees(-ang), 2); print("CABECA yaw corrigido %.2f graus, nariz x %.3f -> %.3f" % (math.degrees(-ang), nariz[0], co[np.argmin(co[:, 1]), 0]))
# ------------------------------------------------------------------ 1. cor da frente dos ombros/peito
y_omb = BD["BracoE"].head_local.y
frente = (co[:, 1] < y_omb + 0.7) & (co[:, 2] > 2.3) & (co[:, 2] < 5.6) & (np.abs(co[:, 0]) < 2.1)
nao = np.array([d in ("Cabeca", "Mandibula", "OrelhaE", "OrelhaD", "MaoE", "MaoD", "DedosE", "DedosD") for d in dono])
reg = frente & ~nao & (nr[:, 1] < 0.35)
m = np.clip(macia(reg, 4) * 1.5, 0, 1)
w = m * suave(-co[:, 0] / 0.35)                               # so a metade -X recebe o espelho; transicao na linha central
print("COR verts na mascara (w>0,05):", int((w > 0.05).sum()))
mat = me.materials[0]; nt = mat.node_tree
tex_cor = next(nd for nd in nt.nodes if nd.type == "TEX_IMAGE" and nd.image and nd.image.name.startswith("T_Lobo_Cor"))
tex_nor = next(nd for nd in nt.nodes if nd.type == "TEX_IMAGE" and nd.image and nd.image.name.startswith("T_Lobo_Normal"))
IMC, IMN = tex_cor.image, tex_nor.image; R = IMC.size[0]
def arr(im): a = np.empty(R * R * 4, np.float32); im.pixels.foreach_get(a); return a.reshape(R, R, 4)
cor, nor = arr(IMC), arr(IMN); cor_n, nor_n = cor.copy(), nor.copy()
# v2 (sem raios): texel -> ponto 3D (baricentrica na UV) -> espelho em X -> ponto mais proximo da superficie -> UV -> amostra
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
me.calc_loop_triangles(); uvd = me.uv_layers.active.data
tris = list(me.loop_triangles)
P3 = [[me.vertices[i].co.copy() for i in t.vertices] for t in tris]
UV = [[V((uvd[l].uv[0], uvd[l].uv[1], 0.0)) for l in t.loops] for t in tris]
bvh = BVHTree.FromPolygons([v.co for v in me.vertices], [list(t.vertices) for t in tris])
def amostra(img, u, v_):
    x_ = min(R - 1, max(0, int(u * R))); y_ = min(R - 1, max(0, int(v_ * R))); return img[y_, x_]
# v3: so o TOM (baixa frequencia). Cor media suavizada por vertice no proprio lado e no ponto espelhado; a diferenca e
# somada a textura original (os tracos do pelo ficam). v2 (copia texel a texel) quebrava os tracos e manchava o peito.
uv_v = np.zeros((n, 2)); cnt = np.zeros(n)
for l in me.loops: uv_v[l.vertex_index] += uvd[l.index].uv; cnt[l.vertex_index] += 1
uv_v /= np.maximum(cnt, 1)[:, None]
def amostra_media(u, v_, raio=3):
    x_ = int(u * R); y_ = int(v_ * R)
    return cor[max(0, y_ - raio):y_ + raio + 1, max(0, x_ - raio):x_ + raio + 1, :3].reshape(-1, 3).mean(axis=0)
c_prop = np.array([amostra_media(*uv_v[i]) for i in range(n)])
c_esp = c_prop.copy(); longe = 0
alvo = np.nonzero(w > 0.01)[0]
for i in alvo:
    p = me.vertices[i].co; loc, nn, fi, dist = bvh.find_nearest(V((-p.x, p.y, p.z)))
    if loc is None or dist > 0.45: longe += 1; continue
    q = barycentric_transform(loc, *P3[fi], *UV[fi]); c_esp[i] = amostra_media(q.x, q.y)
def suaviza(c, it):
    for _ in range(it): c = np.array([0.5 * c[i] + 0.5 * (c[viz[i]].mean(axis=0) if viz[i] else c[i]) for i in range(n)])
    return c
delta = np.clip(0.7 * (suaviza(c_esp, 4) - suaviza(c_prop, 4)), -0.10, 0.10) * w[:, None]   # atenuado e limitado (v3a estourava o creme)
trocados = 0
for ti_, t in enumerate(tris):
    wv = [w[i] for i in t.vertices]
    if max(wv) < 0.02: continue
    dv = [delta[i] for i in t.vertices]
    uv = np.array([[q.x, q.y] for q in UV[ti_]]) * R
    x0, y0 = np.floor(uv.min(axis=0)).astype(int); x1, y1 = np.ceil(uv.max(axis=0)).astype(int)
    a_, b_, c_ = uv; den = (b_[1] - c_[1]) * (a_[0] - c_[0]) + (c_[0] - b_[0]) * (a_[1] - c_[1])
    if abs(den) < 1e-9: continue
    for py in range(max(0, y0), min(R, y1 + 1)):
        for px_ in range(max(0, x0), min(R, x1 + 1)):
            X, Y = px_ + 0.5, py + 0.5
            l1 = ((b_[1] - c_[1]) * (X - c_[0]) + (c_[0] - b_[0]) * (Y - c_[1])) / den
            l2 = ((c_[1] - a_[1]) * (X - c_[0]) + (a_[0] - c_[0]) * (Y - c_[1])) / den; l3 = 1 - l1 - l2
            if min(l1, l2, l3) < -0.02: continue
            d_ = dv[0] * l1 + dv[1] * l2 + dv[2] * l3
            cor_n[py, px_, :3] = np.clip(cor[py, px_, :3] + d_, 0, 1); trocados += 1
print("TEXTURA (tom) texels ajustados:", trocados, "| vertices sem correspondente:", longe, "| delta medio", np.round(delta[alvo].mean(axis=0), 3))
cor_n[:, :, 3] = 1; nor_n[:, :, 3] = 1
print("TEXTURA texels trocados:", trocados, "| sem correspondente proximo (mantidos):", longe)
mk = np.zeros((R, R, 1))
NC, NN = bpy.data.images.new("T_Lobo_Cor_v5", R, R), bpy.data.images.new("T_Lobo_Normal_v5", R, R); NN.colorspace_settings.name = "Non-Color"
NC.pixels.foreach_set(cor_n.ravel()); NN.pixels.foreach_set(nor_n.ravel())
for im, nome in ((NC, "T_Lobo_Cor.png"), (NN, "T_Lobo_Normal.png")):
    im.filepath_raw = os.path.join(OUT, nome); im.file_format = "PNG"; im.save()
tex_cor.image, tex_nor.image = NC, NN; NC.pack(); NN.pack()

rel.update({"texels_ajustados": trocados, "vertices_sem_correspondente": longe})
json.dump(rel, open(os.path.join(OUT, "simetrizar_frente.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("SIMETRIZAR_FRENTE_OK")
