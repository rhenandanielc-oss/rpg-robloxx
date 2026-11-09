"""Curva dos labios pela TEXTURA (traco escuro do Meshy), na HIGH recentrada: raio lateral (+X/-X) em cada fatia y do
focinho; para cada altura z le o texel (UV baricentrica da face atingida) e marca a faixa mais escura abaixo da trufa.
Na frente (x=0) o raio vem de -Y e procura, de baixo para cima, o primeiro traco escuro (o labio sob a trufa).
Saida: labio.json com pontos (y, z) por lado e a curva media. So leitura.
Uso: blender -b <blend com Lobo_Meshy> -P medir_labio.py -- <saida.json> <x_recentro>"""
import bpy, sys, json
import numpy as np
from mathutils import Vector as V
from mathutils.geometry import barycentric_transform
A = sys.argv[sys.argv.index("--") + 1:]; SAIDA = A[0]; DX = float(A[1])
ob = bpy.data.objects["Lobo_Meshy"]; me = ob.data
nt = me.materials[0].node_tree
img = next(n.image for n in nt.nodes if n.type == "TEX_IMAGE" and n.image and n.image.colorspace_settings.name == "sRGB")
W, H = img.size; px = np.empty(W * H * 4, np.float32); img.pixels.foreach_get(px); px = px.reshape(H, W, 4)
uvd = me.uv_layers.active.data; me.calc_loop_triangles(); tri_de = {}
for t in me.loop_triangles: tri_de.setdefault(t.polygon_index, []).append(t)
def lum_em(h, fi):
    for t in tri_de.get(fi, []):
        a, b, c = (me.vertices[i].co for i in t.vertices)
        ua, ub, uc = (V((uvd[l].uv[0], uvd[l].uv[1], 0)) for l in t.loops)
        p = barycentric_transform(h, a, b, c, ua, ub, uc)
        u, v = p.x % 1.0, p.y % 1.0
        r, g, b_ = px[min(H - 1, int(v * H)), min(W - 1, int(u * W)), :3]
        return 0.3 * r + 0.59 * g + 0.11 * b_
    return 1.0
vs = [v.co for v in me.vertices]; NAR = min(vs, key=lambda v: v.y).copy(); NAR.x += DX
print("NARIZ", tuple(round(c, 3) for c in NAR))
lados = {1: [], -1: []}
for k in range(30):
    yy = NAR.y + 0.10 + k * 0.05
    for sx in (1, -1):
        col = []
        for j in range(55):
            zz = NAR.z - 0.75 + j * 0.02
            ok, h, nn, fi = ob.ray_cast(V((4 * sx - DX, yy, zz)), V((-sx, 0, 0)), distance=6)
            if ok and abs(h.x + DX) < 1.3: col.append((zz, lum_em(h, fi), abs(h.x + DX)))
        if len(col) < 8: continue
        L = np.array([c[1] for c in col]); Z = np.array([c[0] for c in col])
        Ls = np.convolve(L, np.ones(3) / 3, mode="same")
        i = int(np.argmin(Ls[1:-1])) + 1
        lados[sx].append((round(yy, 3), round(float(Z[i]), 3), round(float(Ls[i]), 3), round(float(np.median(L)), 3)))
frente = []
for xx in (-0.15, 0.0, 0.15):
    col = []
    for j in range(60):
        zz = NAR.z - 0.9 + j * 0.02
        ok, h, nn, fi = ob.ray_cast(V((xx - DX, NAR.y - 3, zz)), V((0, 1, 0)), distance=6)
        if ok: col.append((zz, lum_em(h, fi), h.y))
    med = np.median([c[1] for c in col]) if col else 1
    esc = [c for c in col if c[1] < 0.45 * med]
    frente.append((xx, esc[0][0] if esc else None, round(float(med), 3), esc[0][2] if esc else None))
for sx in (1, -1):
    for r in lados[sx]: print("LADO %+d y=%.2f z=%.3f lum=%.3f mediana=%.3f" % ((sx,) + r))
print("FRENTE", frente)
json.dump({"nariz": list(NAR), "lados": {str(k): v for k, v in lados.items()}, "frente": frente}, open(SAIDA, "w"), indent=1)
