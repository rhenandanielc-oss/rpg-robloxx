"""v10, passo 2: textura da regiao separada (roda sobre rig_v10/ gerado por separar_cauda_v10.py; altera so a regiao).
A area de contato cauda x pata ficava ESCONDIDA na v9 e o bake antigo deixou nela textura com defeito (manchas escuras);
com a cauda separada ela aparece ao mover. Por LOD e por lado (cauda / pata, atributos 'classe_cauda' e 'lado_tampa'):
- faces de CONTATO = do lado, a menos de 0,15 da superficie do OUTRO lado no repouso (escondidas na v9); pele LIMPA = a
  mais de 0,30 (uma 1a versao usava a distancia a borda das tampas, 0,45: nao cobria o contato largo e as listras ficavam);
- UV das TAMPAS: cada triangulo usa UMA face limpa de referencia (a mais proxima do centro) por transformacao afim: reusa
  pelo limpo sem texels proprios (UV por vertice de faces diferentes atravessava ilhas do atlas e aparecia como listras);
- so LOD0: texels das faces de CONTATO sao repintados por transferencia: pixel -> ponto 3D na
  face -> ponto mais proximo da pele limpa do mesmo lado -> UV -> amostra do mapa original. Mapas: cor, normal, rugosidade
  (LOD1/LOD2 usam as mesmas texturas). Copias em rig_v10/ (as da v9 ficam intactas).
Uso: blender -b rig_v10/CR_LoboArtico_Rig.blend -P textura_cauda_v10.py"""
import bpy, bmesh, os, json
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.interpolate import poly_3d_calc
from mathutils.geometry import barycentric_transform
D_CONTATO, D_LIMPA = 0.15, 0.30                                  # escondida no repouso / fonte limpa
SRC = os.path.dirname(bpy.data.filepath); REL = {}
mat = bpy.data.objects["LOW_Corpo"].data.materials[0]
IMGS = {n.image.name: n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image and any(k in n.image.name for k in ("_cor", "_normal", "_rugosidade"))}
ARR = {}
for nm, im in IMGS.items():
    a = np.empty(im.size[0] * im.size[1] * 4, np.float32); im.pixels.foreach_get(a); ARR[nm] = a.reshape(im.size[1], im.size[0], 4)
ORIG = {k: v.copy() for k, v in ARR.items()}
for L in ("LOW", "LOD1", "LOD2"):
    o = bpy.data.objects[L + "_Corpo"]; bm = bmesh.new(); bm.from_mesh(o.data)
    cls = bm.faces.layers.int.get("classe_cauda"); lad = bm.faces.layers.int.get("lado_tampa"); uv = bm.loops.layers.uv.active
    bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    tampa = [f for f in bm.faces if f[lad] != 0]; ts = set(tampa)
    borda = {v for f in tampa for v in f.verts if any(g not in ts for g in v.link_faces)}
    kd = KDTree(len(borda))
    for i, v in enumerate(borda): kd.insert(v.co, i)
    kd.balance()
    r = REL[L] = {}
    for sinal, nome in ((-1, "cauda"), (1, "pata")):
        lado_f = [f for f in bm.faces if f not in ts and f[cls] == sinal]
        outro = [f for f in bm.faces if f[cls] == -sinal or f[lad] == -sinal]
        bo = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in outro])
        dout = {f: bo.find_nearest(f.calc_center_median())[3] for f in lado_f}       # distancia a superficie do OUTRO lado
        limpa = [f for f in lado_f if dout[f] > D_LIMPA]; contato = [f for f in lado_f if dout[f] <= D_CONTATO]
        bvh = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in limpa])
        def uv_limpo(p):
            loc, nr, fi, d = bvh.find_nearest(p); rf = limpa[fi]; bc = poly_3d_calc([v.co for v in rf.verts], loc)
            return sum((l[uv].uv * b for l, b in zip(rf.loops, bc)), V((0, 0)))
        for f in tampa:                                                 # UM triangulo de referencia por face da tampa (afim):
            if f[lad] != sinal: continue                                # UV por vertice vinda de faces/ilhas diferentes
            loc, nr, fi, d = bvh.find_nearest(f.calc_center_median()); rl = list(limpa[fi].loops)[:3]   # cobria o atlas (listras)
            A3 = [l.vert.co for l in rl]; U3 = [V((l[uv].uv.x, l[uv].uv.y, 0)) for l in rl]
            for l in f.loops:
                q = barycentric_transform(l.vert.co, A3[0], A3[1], A3[2], U3[0], U3[1], U3[2]); l[uv].uv = (q.x, q.y)
        px = 0
        if L == "LOW":
            for nm, A in ARR.items():
                H, W = A.shape[:2]; O = ORIG[nm]
                for f in contato:
                    ls = list(f.loops)
                    for k in range(1, len(ls) - 1):                     # leque de triangulos da face
                        tri = (ls[0], ls[k], ls[k + 1]); U = [V((l[uv].uv.x * W, l[uv].uv.y * H, 0)) for l in tri]; P3 = [l.vert.co for l in tri]
                        x0, x1 = int(max(0, min(u.x for u in U) - 1)), int(min(W - 1, max(u.x for u in U) + 1))
                        y0, y1 = int(max(0, min(u.y for u in U) - 1)), int(min(H - 1, max(u.y for u in U) + 1))
                        if (x1 - x0) * (y1 - y0) > 40000: continue
                        for yy in range(y0, y1 + 1):
                            for xx in range(x0, x1 + 1):
                                q = V((xx + 0.5, yy + 0.5, 0)); d1 = U[1] - U[0]; d2 = U[2] - U[0]; dq = q - U[0]
                                den = d1.x * d2.y - d1.y * d2.x
                                if abs(den) < 1e-9: continue
                                b1 = (dq.x * d2.y - dq.y * d2.x) / den; b2 = (d1.x * dq.y - d1.y * dq.x) / den
                                if b1 < -0.02 or b2 < -0.02 or b1 + b2 > 1.02: continue
                                p = P3[0] + (P3[1] - P3[0]) * b1 + (P3[2] - P3[0]) * b2; us = uv_limpo(p)
                                sx, sy = min(W - 1, max(0, int(us.x * W))), min(H - 1, max(0, int(us.y * H)))
                                A[yy, xx] = O[sy, sx]; px += 1
        r[nome] = {"faces_limpas": len(limpa), "faces_contato_repintadas": len(contato) if L == "LOW" else 0, "texels_escritos": px,
                   "faces_tampa": sum(1 for f in tampa if f[lad] == sinal)}
    bm.to_mesh(o.data); bm.free(); o.data.update(); print("TEX_V10", L, r, flush=True)
for nm, im in IMGS.items():
    im.pixels.foreach_set(ARR[nm].ravel()); fp = os.path.join(SRC, os.path.basename(bpy.path.abspath(im.filepath)))
    im.filepath_raw = fp; im.file_format = "PNG"; im.save(); REL.setdefault("imagens", []).append(os.path.basename(fp))
RJ = json.load(open(os.path.join(SRC, "rig_v10.json"))); RJ["v10_textura"] = REL; json.dump(RJ, open(os.path.join(SRC, "rig_v10.json"), "w"), indent=1)
bpy.ops.wm.save_mainfile(); print("TEX_V10_OK", flush=True)
