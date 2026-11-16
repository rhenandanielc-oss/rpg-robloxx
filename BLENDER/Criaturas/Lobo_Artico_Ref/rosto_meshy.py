"""Mede o rosto do Lobo Artico (Meshy, pose neutra) a partir da geometria + textura de cor do Meshy:
focinho, olhos (iris ciano), linha da boca (traco escuro) e canto da boca. Grava rosto.json para o refino e o rig.
Uso: blender -b meshy/CR_LoboArtico_meshy_neutro.blend -P rosto_meshy.py -- <saida_dir>"""
import bpy, sys, os, json
import numpy as np
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
ob = bpy.data.objects["CR_LoboArtico_Meshy"]; me = ob.data
b = next(n for n in me.materials[0].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
def origem(sock):
    for lk in sock.links:
        n_ = lk.from_node
        if n_.type == "TEX_IMAGE": return n_.image
        for s in n_.inputs:
            r = origem(s) if s.is_linked else None
            if r: return r
img = origem(b.inputs["Base Color"]); W, H = img.size
px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(H, W, 4)
nl = len(me.loops); uv = np.empty(nl * 2, np.float32); me.uv_layers.active.data.foreach_get("uv", uv); uv = uv.reshape(-1, 2)
vi = np.empty(nl, np.int32); me.loops.foreach_get("vertex_index", vi)
co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
nr = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get("normal", nr); nr = nr.reshape(-1, 3)
rgb = px[np.clip((uv[:, 1] % 1) * H, 0, H - 1).astype(int), np.clip((uv[:, 0] % 1) * W, 0, W - 1).astype(int), :3]
P = co[vi]; N = nr[vi]
mx, mn = rgb.max(1), rgb.min(1); sat = (mx - mn) / np.maximum(mx, 1e-3); lum = rgb @ np.array([0.3, 0.59, 0.11], np.float32)
nariz = co[np.argmin(co[:, 1])]; ny, nz = float(nariz[1]), float(nariz[2])
print("ROSTO nariz", np.round(nariz, 3))
# olhos: amostras ciano na frente da cabeca, acima do focinho
cab = (P[:, 1] < ny + 1.6) & (P[:, 2] > nz + 0.05)
ciano = (sat > 0.30) & (rgb[:, 2] > rgb[:, 0] + 0.15) & (rgb[:, 1] > rgb[:, 0] + 0.05) & cab
olhos = {}
for lado, sel in (("E", P[:, 0] > 0.05), ("D", P[:, 0] < -0.05)):
    q = P[ciano & sel]; qn = N[ciano & sel]
    if len(q) < 10: print("ROSTO sem olho", lado, len(q)); continue
    c = np.median(q, 0); d = np.linalg.norm(q - c, axis=1); q = q[d < np.percentile(d, 90)]; qn = qn[d < np.percentile(d, 90)]
    c = q.mean(0); n = qn.mean(0); n /= np.linalg.norm(n)
    larg = float(np.percentile(np.linalg.norm(q - c, axis=1), 95) * 2)
    olhos[lado] = {"centro": c.round(4).tolist(), "normal": n.round(4).tolist(), "largura_iris": round(larg, 4), "amostras": int(len(q))}
print("ROSTO olhos", olhos)
# linha da boca: traco escuro abaixo do nariz (sem o proprio nariz)
reg = (P[:, 1] > ny + 0.20) & (P[:, 1] < ny + 1.40) & (P[:, 2] < nz - 0.05) & (P[:, 2] > nz - 0.80) & (np.abs(P[:, 0]) > 0.04)
esc = reg & (lum < 0.22)
q = P[esc]
if len(q) > 30:
    A = np.c_[np.ones(len(q)), q[:, 1]]; coef, *_ = np.linalg.lstsq(A, q[:, 2], rcond=None)
    canto = float(np.percentile(q[:, 1], 97))
else:
    coef = np.array([nz - 0.28 - (ny + 0.15) * -0.2, -0.2]); canto = ny + 1.1
print("ROSTO boca amostras", len(q), "z = %.3f + %.3f*y" % tuple(coef), "canto_y", round(canto, 3))
json.dump({"nariz": nariz.round(4).tolist(), "olhos": olhos, "boca": {"a": float(coef[0]), "b": float(coef[1]), "canto_y": canto,
           "amostras": int(len(q))}}, open(os.path.join(OUT, "rosto.json"), "w"), indent=1)
print("ROSTO_OK")
