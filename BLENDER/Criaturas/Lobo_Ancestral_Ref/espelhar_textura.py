"""Cor e relevo (normal) da regiao refeita por espelhar_frente.py: cada texel da metade +X recebe a amostra do ponto
espelhado da metade -X. Como a forma ja coincide com o espelho (residuo ~0,006), o ponto mais proximo e exato e os
tracos do pelo ficam continuos. Normal: tangente -> objeto (quadro da face de origem) -> espelho em X -> tangente
(quadro da face de destino). Mistura pela mascara (transicao na linha central/flanco). UV, topologia, pesos intactos.
Uso: blender -b rig6_geo/Lobo_Ancestral_Rig.blend -P espelhar_textura.py -- <saida_dir>"""
import bpy, sys, os, json
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; me = LO.data
w = np.load(os.path.join(os.path.dirname(bpy.data.filepath), "mascara_espelho.npy"))
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
me.calc_loop_triangles(); uvd = me.uv_layers.active.data
T = list(me.loop_triangles)
tv = np.array([t.vertices[:] for t in T]); tuv = np.array([[uvd[l].uv[:] for l in t.loops] for t in T])
nv = np.empty(n * 3); me.vertices.foreach_get("normal", nv); nv = nv.reshape(-1, 3)
def quadro(ti):                                           # T, B por face (derivadas da UV) e normal por vertice
    p = co[tv[ti]]; u = tuv[ti]; e1, e2 = p[1] - p[0], p[2] - p[0]; d1, d2 = u[1] - u[0], u[2] - u[0]
    r = d1[0] * d2[1] - d2[0] * d1[1]
    if abs(r) < 1e-12: return None
    Tg = (e1 * d2[1] - e2 * d1[1]) / r; Bg = (e2 * d1[0] - e1 * d2[0]) / r
    return Tg, Bg
mat = me.materials[0]; nt = mat.node_tree
tc = next(nd for nd in nt.nodes if nd.type == "TEX_IMAGE" and nd.image and nd.image.name.startswith("T_Lobo_Cor"))
tn = next(nd for nd in nt.nodes if nd.type == "TEX_IMAGE" and nd.image and nd.image.name.startswith("T_Lobo_Normal"))
R = tc.image.size[0]
def arr(im): a = np.empty(R * R * 4, np.float32); im.pixels.foreach_get(a); return a.reshape(R, R, 4)
cor, nor = arr(tc.image), arr(tn.image); cor_n, nor_n = cor.copy(), nor.copy()
def bil(img, u, v_):
    x = u * R - 0.5; y = v_ * R - 0.5; x0 = int(np.floor(x)); y0 = int(np.floor(y)); fx, fy = x - x0, y - y0
    x0 = min(R - 1, max(0, x0)); y0 = min(R - 1, max(0, y0)); x1 = min(R - 1, x0 + 1); y1 = min(R - 1, y0 + 1)
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x1] * fx * (1 - fy) + img[y1, x0] * (1 - fx) * fy + img[y1, x1] * fx * fy)
cen = co[tv].mean(axis=1)
fonte = np.nonzero(cen[:, 0] < -0.02)[0]
bvh = BVHTree.FromPolygons([V(p) for p in co], [list(tv[i]) for i in fonte])
TOL = 1.5 / R
alvo = [ti for ti in range(len(T)) if cen[ti, 0] > 0 and w[tv[ti]].max() > 0.02]
print("faces de destino:", len(alvo))
feitos = longe = 0; dist_ac = []
for ti in alvo:
    q = quadro(ti)
    if q is None: continue
    Tg, Bg = q; uv = tuv[ti] * R; pts = co[tv[ti]]; ww = w[tv[ti]]; nn = nv[tv[ti]]
    x0, y0 = np.floor(uv.min(axis=0) - 1.5).astype(int); x1, y1 = np.ceil(uv.max(axis=0) + 1.5).astype(int)
    a_, b_, c_ = uv; den = (b_[1] - c_[1]) * (a_[0] - c_[0]) + (c_[0] - b_[0]) * (a_[1] - c_[1])
    if abs(den) < 1e-9: continue
    for py in range(max(0, y0), min(R, y1 + 1)):
        for px in range(max(0, x0), min(R, x1 + 1)):
            X, Y = px + 0.5, py + 0.5
            l1 = ((b_[1] - c_[1]) * (X - c_[0]) + (c_[0] - b_[0]) * (Y - c_[1])) / den
            l2 = ((c_[1] - a_[1]) * (X - c_[0]) + (a_[0] - c_[0]) * (Y - c_[1])) / den; l3 = 1 - l1 - l2
            L = np.array([l1, l2, l3])
            if L.min() < -0.08: continue                                     # ate ~1,5 px fora da face (margem)
            L = np.clip(L, 0, None); L /= L.sum()
            wt = float(L @ ww)
            if wt < 0.01: continue
            P = L @ pts; N = L @ nn; N /= np.linalg.norm(N)
            loc, fn, fi, dist = bvh.find_nearest(V((-P[0], P[1], P[2])), 0.4)
            if loc is None: longe += 1; continue
            fs = fonte[fi]; ps = co[tv[fs]]; us = tuv[fs]
            # baricentrica do ponto de origem na face fs
            v0, v1, v2 = ps[1] - ps[0], ps[2] - ps[0], np.array(loc) - ps[0]
            d00, d01, d11, d20, d21 = v0 @ v0, v0 @ v1, v1 @ v1, v2 @ v0, v2 @ v1; dd = d00 * d11 - d01 * d01
            if abs(dd) < 1e-14: continue
            bb = (d11 * d20 - d01 * d21) / dd; cc = (d00 * d21 - d01 * d20) / dd; Ls = np.clip(np.array([1 - bb - cc, bb, cc]), 0, None); Ls /= Ls.sum()
            uvs = Ls @ us; c_src = bil(cor, *uvs); n_src = bil(nor, *uvs)
            # normal: tangente(origem) -> objeto -> espelho -> tangente(destino)
            qs = quadro(fs)
            if qs is not None:
                Ts, Bs = qs; Ns = Ls @ nv[tv[fs]]; Ns /= np.linalg.norm(Ns)
                Ts = Ts - Ns * (Ts @ Ns); Ts /= max(np.linalg.norm(Ts), 1e-9); Bs = Bs - Ns * (Bs @ Ns) - Ts * (Bs @ Ts); Bs /= max(np.linalg.norm(Bs), 1e-9)
                t = n_src[:3] * 2 - 1; no = t[0] * Ts + t[1] * Bs + t[2] * Ns; no[0] = -no[0]
                Td = Tg - N * (Tg @ N); Td /= max(np.linalg.norm(Td), 1e-9); Bd = Bg - N * (Bg @ N) - Td * (Bg @ Td); Bd /= max(np.linalg.norm(Bd), 1e-9)
                td = np.array([no @ Td, no @ Bd, no @ N]); td /= max(np.linalg.norm(td), 1e-9); n_new = td * 0.5 + 0.5
                nor_n[py, px, :3] = nor[py, px, :3] * (1 - wt) + n_new * wt
            cor_n[py, px, :3] = cor[py, px, :3] * (1 - wt) + c_src[:3] * wt
            feitos += 1; dist_ac.append(dist)
print("texels espelhados:", feitos, "| sem origem:", longe, "| dist med %.4f" % float(np.median(dist_ac)))
cor_n[:, :, 3] = 1; nor_n[:, :, 3] = 1
NC, NN = bpy.data.images.new("T_Lobo_Cor_v6", R, R), bpy.data.images.new("T_Lobo_Normal_v6", R, R); NN.colorspace_settings.name = "Non-Color"
NC.pixels.foreach_set(cor_n.ravel()); NN.pixels.foreach_set(nor_n.ravel())
for im, nome in ((NC, "T_Lobo_Cor.png"), (NN, "T_Lobo_Normal.png")):
    im.filepath_raw = os.path.join(OUT, nome); im.file_format = "PNG"; im.save()
tc.image, tn.image = NC, NN; NC.pack(); NN.pack()
json.dump({"texels_espelhados": feitos, "sem_origem": longe, "dist_mediana": float(np.median(dist_ac))}, open(os.path.join(OUT, "espelhar_textura.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("ESPELHAR_TEXTURA_OK")
