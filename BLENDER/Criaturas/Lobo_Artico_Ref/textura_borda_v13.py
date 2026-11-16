"""v13: repinta as MANCHAS ESCURAS da face interna da cauda/pata traseira E (borda do corte da v10 com o bake antigo
escondido), visiveis no Andar. So textura: geometria, UV, pesos, rig e clipes iguais aos de anim_v12/ (preservado).
1. Mede a cor de cada face do corpo na regiao (y > 2,0, z < 4,3, x > -0,3) amostrando os texels do triangulo UV;
   escura = luminancia < LIMIAR x mediana da regiao; marca as escuras + 1 anel de vizinhas (bordas suaves);
2. Repinta os texels das faces marcadas (e os a ate 1 px do triangulo: muitas sao menores que 1 texel) por transferencia: pixel -> ponto 3D na face -> ponto mais proximo de uma face NAO
   marcada do mesmo lado (atributo 'classe_cauda' da v10; fora da caixa do corte vale qualquer face limpa da regiao) ->
   UV -> amostra do mapa original. Mapas: cor, normal, rugosidade (os 3 LODs usam as mesmas texturas).
Uso: blender -b anim_v12/CR_LoboArtico_Anim.blend -P textura_borda_v13.py -- <saida_dir>"""
import bpy, bmesh, sys, os, json, shutil, statistics
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); LIMIAR = float(os.environ.get("LIMIAR", 0.72))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.exists(fp) and os.path.dirname(fp) != OUT:
        dst = os.path.join(OUT, os.path.basename(fp)); shutil.copy(fp, dst); im.filepath = dst; im.reload()
for f in os.listdir(SRC):
    if f.endswith(".json"): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
o = bpy.data.objects["LOW_Corpo"]; mat = o.data.materials[0]
IM = {n.image.name: n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image and any(k in n.image.name for k in ("_cor", "_normal", "_rugosidade"))}
ARR = {}
for nm, im in IM.items():
    a = np.empty(im.size[0] * im.size[1] * 4, np.float32); im.pixels.foreach_get(a); ARR[nm] = a.reshape(im.size[1], im.size[0], 4)
ORIG = {k: v.copy() for k, v in ARR.items()}; COR = next(k for k in ARR if "_cor" in k); H_, W_ = ARR[COR].shape[:2]
bm = bmesh.new(); bm.from_mesh(o.data); uv = bm.loops.layers.uv.active; cls = bm.faces.layers.int.get("classe_cauda"); lad = bm.faces.layers.int.get("lado_tampa")
bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
def regiao(c): return c.y > 2.0 and c.z < 4.3 and c.x > -0.3
def amostra_lum(f):
    ls = f.loops; us = [l[uv].uv for l in ls]; pts = [sum(us, V((0, 0))) / len(us)] + [us[0] * 0.6 + us[i] * 0.4 for i in range(1, len(us))]
    v = []
    for u in pts:
        x, y = min(W_ - 1, max(0, int(u.x * W_))), min(H_ - 1, max(0, int(u.y * H_))); c = ORIG[COR][y, x]; v.append(0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])
    return float(sum(v) / len(v))
RF = [f for f in bm.faces if regiao(f.calc_center_median()) and not f[lad]]
LUM = {f.index: amostra_lum(f) for f in RF}; med = statistics.median(LUM.values())
esc = {f.index for f in RF if LUM[f.index] < LIMIAR * med}
anel = {g.index for i in esc for e in bm.faces[i].edges for g in e.link_faces if regiao(g.calc_center_median()) and not g[lad]}
marc = esc | anel
REL = {"limiar": LIMIAR, "mediana_luminancia_regiao": round(med, 4), "faces_regiao": len(RF), "faces_escuras": len(esc), "faces_repintadas": len(marc), "por_lado": {}}
for sinal in (-1, 1, 0):
    alvo = [bm.faces[i] for i in marc if bm.faces[i][cls] == sinal]
    if not alvo: continue
    limpa = [f for f in RF if f.index not in marc and (f[cls] == sinal or f[cls] == 0 or sinal == 0)]
    bvh = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in limpa])
    def uv_limpo(p):
        loc, nr, fi, d = bvh.find_nearest(p); rf = limpa[fi]; bc = poly_3d_calc([v.co for v in rf.verts], loc)
        return sum((l[uv].uv * b for l, b in zip(rf.loops, bc)), V((0, 0)))
    px = 0
    for nm, A in ARR.items():
        H, W = A.shape[:2]; O = ORIG[nm]
        for f in alvo:
            ls = list(f.loops)
            for k in range(1, len(ls) - 1):
                tri = (ls[0], ls[k], ls[k + 1]); U = [V((l[uv].uv.x * W, l[uv].uv.y * H, 0)) for l in tri]; P3 = [l.vert.co for l in tri]
                x0, x1 = int(max(0, min(u.x for u in U) - 1)), int(min(W - 1, max(u.x for u in U) + 1)); y0, y1 = int(max(0, min(u.y for u in U) - 1)), int(min(H - 1, max(u.y for u in U) + 1))
                if (x1 - x0) * (y1 - y0) > 40000: continue
                d1, d2 = U[1] - U[0], U[2] - U[0]; den = d1.x * d2.y - d1.y * d2.x
                if abs(den) < 1e-9: continue
                for yy in range(y0, y1 + 1):
                    for xx in range(x0, x1 + 1):
                        q_ = V((xx + 0.5, yy + 0.5, 0)); dq = q_ - U[0]; b1 = (dq.x * d2.y - dq.y * d2.x) / den; b2 = (d1.x * dq.y - d1.y * dq.x) / den
                        c1, c2 = max(0.0, b1), max(0.0, b2)
                        if c1 + c2 > 1: c1, c2 = c1 / (c1 + c2), c2 / (c1 + c2)
                        if (U[0] + d1 * c1 + d2 * c2 - q_).length > 1.0: continue        # texels a ate 1 px (faces menores que 1 texel)
                        us = uv_limpo(P3[0] + (P3[1] - P3[0]) * c1 + (P3[2] - P3[0]) * c2)
                        A[yy, xx] = O[min(H - 1, max(0, int(us.y * H))), min(W - 1, max(0, int(us.x * W)))]; px += 1
    REL["por_lado"][{-1: "cauda", 1: "pata", 0: "fora_do_corte"}[sinal]] = {"faces": len(alvo), "texels_escritos": px}
bm.free()
# conferencia: luminancia das faces repintadas depois
for nm, im in IM.items():
    im.pixels.foreach_set(ARR[nm].ravel()); fp = os.path.join(OUT, os.path.basename(bpy.path.abspath(im.filepath))); im.filepath_raw = fp; im.file_format = "PNG"; im.save()
ORIG[COR] = ARR[COR]; bm = bmesh.new(); bm.from_mesh(o.data); uv = bm.loops.layers.uv.active; bm.faces.ensure_lookup_table()
depois = [amostra_lum(bm.faces[i]) for i in esc]; bm.free()
REL["luminancia_escuras_antes_depois"] = [round(sum(LUM[i] for i in esc) / max(1, len(esc)), 4), round(sum(depois) / max(1, len(depois)), 4)]
REL["escuras_restantes"] = sum(1 for x in depois if x < LIMIAR * med)
json.dump(REL, open(os.path.join(OUT, "textura_borda_v13.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("V13_OK", json.dumps(REL), flush=True)
