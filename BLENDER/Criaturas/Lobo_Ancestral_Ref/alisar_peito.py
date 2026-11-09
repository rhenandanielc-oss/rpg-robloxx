"""Peitoral acima das patas mais liso e natural (pedido 05/11: "esta parecendo pelos agrupados"). Diagnostico (diag_ombro.py):
a regiao e feita de lascas pontudas e separadas (render argila) com sombras escuras assadas entre elas na textura.
Tres camadas, so na regiao (mascara macia: frente do peito, z Z0..Z1, entre e acima das patas; cabeca e patas fora):
 1. FORMA: suavizacao de Taubin (preserva volume) -> as lascas viram pelagem continua.
 2. SOMBRAS: texels mais escuros que a media local sobem em direcao a ela (LEVANTA); tracos claros ficam.
 3. RELEVO: normal map puxado para o plano (ACHATA) -> o sombreamento nao recria as lascas.
UV, topologia, pesos e rig intactos; simetrico (UV espelhada: os dois lados compartilham os texels).
Uso: blender -b rig12/Lobo_Ancestral_Rig.blend -P alisar_peito.py -- <saida_dir> [iteracoes levanta achata suaviza_cor]"""
import bpy, sys, os, json
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
IT, LEVANTA, ACHATA = (int(A[1]), float(A[2]), float(A[3])) if len(A) > 3 else (30, 0.65, 0.55)
SUAVIZA_COR = float(A[4]) if len(A) > 4 else 0.0                     # 4. DESENHO: mistura com a cor desfocada (some o contorno pintado das lascas)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
yo = BD["BracoE"].head_local.y
Z0, Z1 = 2.9, 5.9                                                      # v1 (ate 5,4) deixava lascas no meio do peito
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
print("vertices na regiao (w>0,1):", int((w > 0.1).sum()))
# 1. forma (Taubin)
for _ in range(IT):
    L = media(co) - co; co = co + 0.55 * w[:, None] * L
    L = media(co) - co; co = co - 0.58 * w[:, None] * L
co[np.abs(co0[:, 0]) < 1e-6, 0] = 0.0
d = np.linalg.norm(co - co0, axis=1)
me.vertices.foreach_set("co", co.ravel()); me.update()
# 2 e 3: textura de cor e normal so nas faces da regiao (peso interpolado por texel)
nt = me.materials[0].node_tree
tc = next(x for x in nt.nodes if x.type == "TEX_IMAGE" and x.image and x.image.name.startswith("T_Lobo_Cor"))
tn = next(x for x in nt.nodes if x.type == "TEX_IMAGE" and x.image and x.image.name.startswith("T_Lobo_Normal"))
R = tc.image.size[0]
def arr(im): a = np.empty(R * R * 4, np.float32); im.pixels.foreach_get(a); return a.reshape(R, R, 4)
cor, nor = arr(tc.image), arr(tn.image); cor_n, nor_n = cor.copy(), nor.copy()
def borrar(img, r):
    out = img.copy()
    for eixo in (0, 1):
        acc = np.zeros_like(out)
        for k in range(-r, r + 1): acc += np.roll(out, k, axis=eixo)
        out = acc / (2 * r + 1)
    return out
media_cor = borrar(cor[:, :, :3], 6); fina = borrar(cor[:, :, :3], 3)
me.calc_loop_triangles(); uvd = me.uv_layers.active.data
tv = np.array([t.vertices[:] for t in me.loop_triangles]); tuv = np.array([[uvd[l].uv[:] for l in t.loops] for t in me.loop_triangles]) * R
LUM = np.array([0.299, 0.587, 0.114]); feitos = 0
for ti in np.nonzero(w[tv].max(axis=1) > 0.02)[0]:
    if co0[tv[ti], 0].mean() < -1e-4: continue                        # UV espelhada: basta a metade +X (e a linha central)
    a_, b_, c_ = tuv[ti]; ww = w[tv[ti]]
    den = (b_[1] - c_[1]) * (a_[0] - c_[0]) + (c_[0] - b_[0]) * (a_[1] - c_[1])
    if abs(den) < 1e-9: continue
    x0, y0 = np.floor(tuv[ti].min(0)).astype(int); x1, y1 = np.ceil(tuv[ti].max(0)).astype(int)
    for py in range(max(0, y0 - 1), min(R, y1 + 2)):
        for px in range(max(0, x0 - 1), min(R, x1 + 2)):
            X, Y = px + 0.5, py + 0.5
            l1 = ((b_[1] - c_[1]) * (X - c_[0]) + (c_[0] - b_[0]) * (Y - c_[1])) / den
            l2 = ((c_[1] - a_[1]) * (X - c_[0]) + (a_[0] - c_[0]) * (Y - c_[1])) / den; l3 = 1 - l1 - l2
            if min(l1, l2, l3) < -0.06: continue
            k = float(np.clip(ww[0] * l1 + ww[1] * l2 + ww[2] * l3, 0, 1))
            if k < 0.01: continue
            c0 = cor[py, px, :3]; m_ = media_cor[py, px]
            escuro = max(0.0, float((m_ - c0) @ LUM))                    # so o que e mais escuro que a media local
            c1 = c0 + (m_ - c0) * LEVANTA * k if escuro > 0 else c0
            c1 = c1 + (fina[py, px] - c1) * SUAVIZA_COR * k
            cor_n[py, px, :3] = np.clip(c1, 0, 1)
            nv = nor[py, px, :3] * 2 - 1; nv = nv + (np.array([0, 0, 1.0]) - nv) * ACHATA * k; nv /= max(np.linalg.norm(nv), 1e-6)
            nor_n[py, px, :3] = nv * 0.5 + 0.5; feitos += 1
cor_n[:, :, 3] = 1; nor_n[:, :, 3] = 1
NC, NN = bpy.data.images.new("T_Lobo_Cor_v13", R, R), bpy.data.images.new("T_Lobo_Normal_v13", R, R); NN.colorspace_settings.name = "Non-Color"
NC.pixels.foreach_set(cor_n.ravel()); NN.pixels.foreach_set(nor_n.ravel())
for im, nome in ((NC, "T_Lobo_Cor.png"), (NN, "T_Lobo_Normal.png")):
    im.filepath_raw = os.path.join(OUT, nome); im.file_format = "PNG"; im.save(); im.pack()
tc.image, tn.image = NC, NN
rel = {"iteracoes": IT, "levanta": LEVANTA, "achata": ACHATA, "suaviza_cor": SUAVIZA_COR, "vertices_regiao": int((w > 0.1).sum()),
       "desloc_max": round(float(d.max()), 3), "desloc_med_regiao": round(float(np.median(d[w > 0.5])), 3), "texels": feitos}
print("ALISAR", rel)
json.dump(rel, open(os.path.join(OUT, "alisar_peito.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("ALISAR_PEITO_OK")
