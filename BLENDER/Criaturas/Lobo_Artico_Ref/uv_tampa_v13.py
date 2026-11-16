"""v13, passo 4 (CORRECAO DAS MANCHAS): a causa e a COR BASE das tampas da v10. Teste de isolamento (cor base uniforme ->
manchas somem; normal map desligado -> continuam): as tampas usam UV emprestada, um triangulo por face de referencia vizinha,
e essas referencias eram as faces da faixa escondida com o bake escuro (fresta cauda/pata). Repintar essas faces
(passo 1) nao resolve porque os texels sao compartilhados.
Correcao: as tampas (atributo 'lado_tampa' -1 cauda / +1 pata, nos 3 LODs) ganham UV PROPRIA num retangulo VAZIO do atlas do
corpo (procura o maior quadrado livre, ocupado por nenhum LOD), por projecao planar no plano medio de cada tampa (base do
LOW, a mesma para LOD1/LOD2). Os texels desse retangulo sao pintados por transferencia: texel -> ponto no plano -> ponto
mais proximo de uma face LIMPA do mesmo lado (luminancia >= CLARA x mediana, fora das tampas) -> UV -> amostra (cor,
rugosidade, emissao); normal = plana (0,5; 0,5; 1), porque o espaco tangente das faces de origem nao vale na tampa.
Geometria, pesos, rig e clipes iguais. Uso: blender -b anim_v13/CR_LoboArtico_Anim.blend -P uv_tampa_v13.py"""
import bpy, bmesh, os, json, statistics
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc
CLARA, MARGEM = 0.9, 3
SRC = os.path.dirname(bpy.data.filepath); REL = {"parametros": {"CLARA": CLARA, "MARGEM_px": MARGEM}}
ARM = bpy.data.objects["LoboArtico_Rig"]; AC = ARM.animation_data.action; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()
mat = bpy.data.objects["LOW_Corpo"].data.materials[0]
IM = {k: n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image for k in ("_cor", "_normal", "_rugosidade", "_emissao") if k in n.image.name}
ARR = {}
for k, im in IM.items():
    a = np.empty(im.size[0] * im.size[1] * 4, np.float32); im.pixels.foreach_get(a); ARR[k] = a.reshape(im.size[1], im.size[0], 4)
H, W = ARR["_cor"].shape[:2]; REL["textura"] = [W, H]; ORIG = {k: v.copy() for k, v in ARR.items()}
# 1. ocupacao UV de todos os LODs (linha de varredura por triangulo) e maior quadrado vazio
oc = np.zeros((H, W), bool)
def raster(tri, cb):
    xs = [u.x * W for u in tri]; ys = [u.y * H for u in tri]
    x0, x1 = max(0, int(min(xs)) - 1), min(W - 1, int(max(xs)) + 1); y0, y1 = max(0, int(min(ys)) - 1), min(H - 1, int(max(ys)) + 1)
    (ax, ay), (bx, by), (cx, cy) = zip(xs, ys); den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(den) < 1e-12: return
    X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
    l1 = ((by - cy) * (X - cx) + (cx - bx) * (Y - cy)) / den; l2 = ((cy - ay) * (X - cx) + (ax - cx) * (Y - cy)) / den; l3 = 1 - l1 - l2
    e = 1.5 / max(1.0, abs(den) ** 0.5)
    cb(y0, x0, (l1 > -e) & (l2 > -e) & (l3 > -e))
for L in ("LOW", "LOD1", "LOD2"):
    me = bpy.data.objects[L + "_Corpo"].data; uv = me.uv_layers.active.data
    for p in me.polygons:
        li = list(p.loop_indices)
        for k in range(1, len(li) - 1):
            def marca(y0, x0, m): oc[y0:y0 + m.shape[0], x0:x0 + m.shape[1]] |= m
            raster([uv[li[0]].uv, uv[li[k]].uv, uv[li[k + 1]].uv], marca)
livre = ~oc; dp = np.zeros((H + 1, W + 1), np.int32); best = (0, 0, 0)
for y in range(H):
    pr, ro, lv = dp[y], dp[y + 1], livre[y]
    for x in range(W):
        if lv[x]:
            v = min(pr[x], pr[x + 1], ro[x]) + 1; ro[x + 1] = v
            if v > best[0]: best = (v, x, y)
lado_q, xf, yf = best; X0, Y0 = xf - lado_q + 1 + MARGEM, yf - lado_q + 1 + MARGEM; Q = lado_q - 2 * MARGEM
REL["quadrado_livre_px"] = {"lado": int(lado_q), "x0": int(xf - lado_q + 1), "y0": int(yf - lado_q + 1), "util": int(Q)}
RET = {-1: (X0, Y0, Q, Q // 2 - 1), 1: (X0, Y0 + Q // 2 + 1, Q, Q - Q // 2 - 1)}     # (x0, y0, largura, altura) em px; cauda embaixo, pata em cima
# 2. base planar de cada tampa (LOW) e faces limpas de origem
o = bpy.data.objects["LOW_Corpo"]; bm = bmesh.new(); bm.from_mesh(o.data); uvl = bm.loops.layers.uv.active
lad = bm.faces.layers.int.get("lado_tampa"); cls = bm.faces.layers.int.get("classe_cauda"); bm.faces.ensure_lookup_table()
def lum(f):
    us = [l[uvl].uv for l in f.loops]; c = sum(us, V((0, 0))) / len(us); x, y = min(W - 1, int(c.x * W)), min(H - 1, int(c.y * H)); p = ORIG["_cor"][y, x]
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]
reg = [f for f in bm.faces if not f[lad] and f.calc_center_median().y > 2.0 and f.calc_center_median().z < 4.3 and f.calc_center_median().x > -0.3]
med = statistics.median(lum(f) for f in reg); REL["mediana_luminancia"] = round(float(med), 4)
BASE = {}
for s in (-1, 1):
    fs = [f for f in bm.faces if f[lad] == s]; pts = np.array([v.co[:] for f in fs for v in f.verts]); c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c); e1, e2 = V(vt[0]), V(vt[1]); c = V(c)
    q = np.array([[(V(p) - c).dot(e1), (V(p) - c).dot(e2)] for p in pts]); mn, mx = q.min(0), q.max(0)
    x0, y0, w, h = RET[s]; esc = min(w / (mx[0] - mn[0]), h / (mx[1] - mn[1]))
    BASE[s] = (c, e1, e2, mn, esc)
    limpa = [f for f in reg if (f[cls] == s or f[cls] == 0) and lum(f) >= CLARA * med]
    bvh = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in limpa])
    px = 0
    for yy in range(y0, y0 + h):
        for xx in range(x0, x0 + w):
            a_ = (xx + 0.5 - x0) / esc + mn[0]; b_ = (yy + 0.5 - y0) / esc + mn[1]; p3 = c + e1 * a_ + e2 * b_
            loc, nr, fi, d = bvh.find_nearest(p3); rf = limpa[fi]; bc = poly_3d_calc([v.co for v in rf.verts], loc)
            us = sum((l[uvl].uv * b for l, b in zip(rf.loops, bc)), V((0, 0))); sx, sy = min(W - 1, max(0, int(us.x * W))), min(H - 1, max(0, int(us.y * H)))
            for k in ARR:
                ARR[k][yy, xx] = (0.5, 0.5, 1.0, 1.0) if k == "_normal" else ORIG[k][sy, sx]
            px += 1
    REL["lado_%d" % s] = {"faces_tampa_LOW": len(fs), "faces_origem_limpas": len(limpa), "texels": px, "escala_px_por_stud": round(float(esc), 2)}
bm.free()
# borda de MARGEM px em volta (sangria) copiando o texel mais proximo do retangulo
for s, (x0, y0, w, h) in RET.items():
    for yy in range(y0 - MARGEM, y0 + h + MARGEM):
        for xx in range(x0 - MARGEM, x0 + w + MARGEM):
            if 0 <= yy < H and 0 <= xx < W and livre[yy, xx] and not (x0 <= xx < x0 + w and y0 <= yy < y0 + h):
                cy_, cx_ = min(max(yy, y0), y0 + h - 1), min(max(xx, x0), x0 + w - 1)
                for k in ARR: ARR[k][yy, xx] = ARR[k][cy_, cx_]
for k, im in IM.items():
    im.pixels.foreach_set(ARR[k].ravel()); im.filepath_raw = bpy.path.abspath(im.filepath); im.file_format = "PNG"; im.save()
# 3. UV propria das tampas nos 3 LODs (mesma base planar do LOW, presa ao retangulo)
for L in ("LOW", "LOD1", "LOD2"):
    o = bpy.data.objects[L + "_Corpo"]; bm = bmesh.new(); bm.from_mesh(o.data); uvl = bm.loops.layers.uv.active; lad = bm.faces.layers.int.get("lado_tampa"); n = 0
    for f in bm.faces:
        s = f[lad]
        if not s: continue
        c, e1, e2, mn, esc = BASE[s]; x0, y0, w, h = RET[s]
        for l in f.loops:
            d = l.vert.co - c; u = min(x0 + w - 0.5, max(x0 + 0.5, x0 + (d.dot(e1) - mn[0]) * esc)); v = min(y0 + h - 0.5, max(y0 + 0.5, y0 + (d.dot(e2) - mn[1]) * esc))
            l[uvl].uv = (u / W, v / H)
        n += 1
    bm.to_mesh(o.data); o.data.update(); bm.free(); REL[L] = {"faces_tampa_com_uv_propria": n}
json.dump(REL, open(os.path.join(SRC, "uv_tampa_v13.json"), "w"), indent=1, default=float)
ARM.animation_data.action = AC; bpy.ops.wm.save_mainfile(); print("UV_TAMPA_V13_OK", json.dumps(REL, default=float), flush=True)
