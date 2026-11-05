"""E5: separa juba de pelo dourado pela cor (vermelho/verde) em vez da saturacao. Imprime distribuicoes e o valor nos
vertices citados no relatorio r2. Uso: blender -b E4b_r2.blend -P e5_05_cor_juba.py"""
import bpy, numpy as np
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; me = ob.data; n = len(me.vertices); co = np.array([v.co for v in me.vertices])
img = [nd.image for m in me.materials for nd in m.node_tree.nodes if nd.type == "TEX_IMAGE" and nd.image and nd.image.colorspace_settings.name == "sRGB"][0]
R = img.size[0]; px = np.array(img.pixels[:], np.float32).reshape(R, R, -1)[..., :3]
# cor media por vertice amostrando os cantos (loops) com 5 pontos em volta (menos ruido que 1 texel)
uvd = me.uv_layers.active.data; acc = np.zeros((n, 3)); cnt = np.zeros(n)
for l in me.loops:
    u, v = uvd[l.index].uv
    for du, dv in ((0, 0), (2, 0), (-2, 0), (0, 2), (0, -2)):
        acc[l.vertex_index] += px[int(np.clip(v * R + dv, 0, R - 1)), int(np.clip(u * R + du, 0, R - 1))]; cnt[l.vertex_index] += 1
cor = acc / np.maximum(cnt, 1)[:, None]; rg = cor[:, 0] / np.maximum(cor[:, 1], 1e-3); mx, mn = cor.max(1), cor.min(1); sat = (mx - mn) / np.maximum(mx, 1e-4)
pata = (co[:, 2] < 3.5) & (co[:, 2] > 1.0) & (np.abs(np.abs(co[:, 0]) - 1.7) < 1.2) & (co[:, 1] < -5) & (co[:, 1] > -10)
corpo = (co[:, 2] > 6) & (co[:, 2] < 9) & (co[:, 1] > -2) & (co[:, 1] < 4)
juba = (co[:, 1] < -10) & (co[:, 2] > 8) & (co[:, 1] > -13)
for nome, m in (("pata", pata), ("corpo", corpo), ("juba", juba)):
    print("DIST", nome, int(m.sum()), "r/g p5,p50,p95", np.round(np.percentile(rg[m], [5, 50, 95]), 2), "sat p5,p50,p95", np.round(np.percentile(sat[m], [5, 50, 95]), 2))
for p in ((3.09, -6.73, 5.42), (2.83, -6.6, 5.08), (1.79, -6.39, 5.24), (0.9, -7.0, 5.3), (1.58, -9.1, 6.15)):
    i = int(np.argmin(np.linalg.norm(co - np.array(p), axis=1))); print("PONTO", p, "r/g %.2f sat %.2f" % (rg[i], sat[i]), np.round(cor[i], 3))
np.save(bpy.path.abspath("//e5_cor_vert.npy"), np.c_[co, cor]); print("SALVO")
