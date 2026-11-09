"""Remove os "carocos escuros" no comeco das patas dianteiras (logo abaixo do peito/juba). Diagnostico (diag_ombro.py):
a GEOMETRIA nao tem saliencia (render argila liso) e os pesos estao normais; o carocos e uma mancha quase preta ASSADA
NA TEXTURA (sombra da axila do modelo Meshy original), lida como volume. Correcao so do TOM (baixa frequencia), por face:
cor local suavizada (r 0,18) contra a cor "de pele" da vizinhanca (r 0,55, so faces acima do percentil 55 de luminancia);
a diferenca, so para clarear e limitada, e somada aos texels (os tracos do pelo ficam). UV espelhada: os dois lados
compartilham os texels, entao basta a metade +X. Geometria, UV, pesos e rig intactos.
Uso: blender -b rig7/Lobo_Ancestral_Rig.blend -P corrigir_axila.py -- <saida_dir> [raio_ref percentil delta_max]"""
import bpy, sys, os, json
import numpy as np
from mathutils.kdtree import KDTree
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
R_REF, PCT, DMAX = (float(A[1]), float(A[2]), float(A[3])) if len(A) > 3 else (0.55, 55, 0.38)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
yo = BD["BracoE"].head_local.y
LUM = np.array([0.299, 0.587, 0.114])
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
nt = me.materials[0].node_tree
tc = next(n for n in nt.nodes if n.type == "TEX_IMAGE" and n.image and n.image.name.startswith("T_Lobo_Cor")); IM = tc.image; R = IM.size[0]
px = np.empty(R * R * 4, np.float32); IM.pixels.foreach_get(px); px = px.reshape(R, R, 4); novo = px.copy()
me.calc_loop_triangles(); uvd = me.uv_layers.active.data
co = np.array([v.co[:] for v in me.vertices])
T = list(me.loop_triangles); tv = np.array([t.vertices[:] for t in T]); tuv = np.array([[uvd[l].uv[:] for l in t.loops] for t in T]) * R
cen = co[tv].mean(axis=1)
# caixa da regiao (metade +X) e caixa ampliada para a referencia de cor
def caixa(c, m):
    return (c[:, 0] > 0.15 - m) & (c[:, 0] < 1.75 + m) & (c[:, 2] > 2.5 - m) & (c[:, 2] < 4.6 + m) & (c[:, 1] > yo - 1.4 - m) & (c[:, 1] < yo + 0.8 + m)
reg = np.nonzero(caixa(cen, 0.0) & (cen[:, 0] > 0))[0]; viz = np.nonzero(caixa(cen, R_REF + 0.1) & (cen[:, 0] > 0))[0]
def texels(ti):
    a, b, c = tuv[ti]; x0, y0 = np.floor(tuv[ti].min(0)).astype(int); x1, y1 = np.ceil(tuv[ti].max(0)).astype(int)
    den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
    if abs(den) < 1e-9: return []
    out = []
    for py in range(max(0, y0 - 1), min(R, y1 + 2)):
        for px_ in range(max(0, x0 - 1), min(R, x1 + 2)):
            X, Y = px_ + 0.5, py + 0.5
            l1 = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / den
            l2 = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / den; l3 = 1 - l1 - l2
            if min(l1, l2, l3) >= -0.06: out.append((py, px_, l1, l2, l3))
    return out
TX = {ti: texels(ti) for ti in viz}
cor_f = {ti: (np.mean([px[p[0], p[1], :3] for p in TX[ti]], axis=0) if TX[ti] else None) for ti in viz}
vv = [ti for ti in viz if cor_f[ti] is not None]
kd = KDTree(len(vv))
for k, ti in enumerate(vv): kd.insert(cen[ti], k)
kd.balance()
C = np.array([cor_f[ti] for ti in vv]); L = C @ LUM
# v2: GANHO de luminancia (mantem o matiz: o marrom da pata continua marrom) ate a luminancia da vizinhanca; so o que
# o ganho (limitado a GMAX) nao alcanca no nucleo quase preto recebe cor somada, com o MATIZ da pele vizinha (faixa media
# de luminancia, sem o branco do peito). v1 (cor media das faces claras somada) acinzentava a marca marrom.
GMAX = 4.0
ajuste = {}
for ti in reg:
    if cor_f.get(ti) is None: continue
    perto = [k for _, k, _ in kd.find_range(cen[ti], 0.18)]; low = C[perto].mean(axis=0); ll = max(float(low @ LUM), 1e-3)
    viz_ = np.array([k for _, k, _ in kd.find_range(cen[ti], R_REF)]); lv = L[viz_]
    lt = float(np.percentile(lv, PCT))
    faixa = viz_[(lv >= np.percentile(lv, 35)) & (lv <= np.percentile(lv, 75))]
    matiz = C[faixa].mean(axis=0); matiz = matiz / max(float(matiz @ LUM), 1e-3)
    escuro = suave((lt * 0.85 - ll) / max(lt * 0.45, 1e-3))          # so onde esta bem mais escuro que a vizinhanca
    if lt <= ll or escuro <= 0: ajuste[ti] = (0.0, np.zeros(3)); continue
    g = min(lt / ll, GMAX); resto = max(0.0, min(lt - ll * g, DMAX))
    ajuste[ti] = ((g - 1.0) * escuro, matiz * resto * escuro)
gv = {}; av = {}; nv = {}
for ti, (g, ad) in ajuste.items():
    for v in tv[ti]: gv[v] = gv.get(v, 0) + g; av[v] = av.get(v, 0) + ad; nv[v] = nv.get(v, 0) + 1
def borda(p):
    m = min(p[0] - 0.15, 1.75 - p[0], p[2] - 2.5, 4.6 - p[2], p[1] - (yo - 1.4), yo + 0.8 - p[1]); return suave(m / 0.3)
mudados = 0; dl = []
for ti in ajuste:
    gs = [gv[v] / nv[v] * borda(co[v]) for v in tv[ti]]; ads = [av[v] / nv[v] * borda(co[v]) for v in tv[ti]]
    for py, px_, l1, l2, l3 in TX[ti]:
        g = gs[0] * l1 + gs[1] * l2 + gs[2] * l3; ad = ads[0] * l1 + ads[1] * l2 + ads[2] * l3
        if g > 1e-3 or np.abs(ad).max() > 1e-4:
            antes = px[py, px_, :3]; depois = np.clip(antes * (1 + g) + ad, 0, 1); novo[py, px_, :3] = depois
            mudados += 1; dl.append(float((depois - antes) @ LUM))
dl = np.array(dl)
rel = {"faces_regiao": int(len(reg)), "faces_corrigidas": int(sum(1 for g, ad in ajuste.values() if g > 0.01)), "texels": mudados,
       "delta_lum_max": round(float(dl.max()), 3), "delta_lum_medio": round(float(dl.mean()), 3), "GMAX": GMAX, "R_REF": R_REF, "PCT": PCT, "DMAX": DMAX}
print("AXILA", rel)
NI = bpy.data.images.new("T_Lobo_Cor_v8", R, R); NI.pixels.foreach_set(novo.ravel())
NI.filepath_raw = os.path.join(OUT, "T_Lobo_Cor.png"); NI.file_format = "PNG"; NI.save(); NI.pack(); tc.image = NI
json.dump(rel, open(os.path.join(OUT, "corrigir_axila.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("CORRIGIR_AXILA_OK")
