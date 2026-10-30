"""Medidas numericas do Silverwing_20k: aglomerados de vertices perto do chao (pes) e fatias horizontais
(componentes conexos por grade 2D) para achar centro de pescoco, tronco, patas e cauda."""
import bpy, sys
from collections import defaultdict
args = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=args[0])
o = [x for x in bpy.data.objects if x.type == "MESH"][0]
V = [o.matrix_world @ v.co for v in o.data.vertices]
def grupos(pts, cel=0.02):
    g = defaultdict(list)
    for p in pts: g[(round(p.x / cel), round(p.y / cel))].append(p)
    vis, out = set(), []
    for k in g:
        if k in vis: continue
        pilha, comp = [k], []
        vis.add(k)
        while pilha:
            c = pilha.pop(); comp += g[c]
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (c[0] + dx, c[1] + dy)
                    if n in g and n not in vis: vis.add(n); pilha.append(n)
        out.append(comp)
    return sorted(out, key=lambda c: -len(c))
for z0 in (0.02, 0.08, 0.15, 0.25, 0.35, 0.45, 0.55, 0.62, 0.70, 0.78):
    fat = [p for p in V if abs(p.z - z0) < 0.012]
    res = []
    for c in grupos(fat)[:8]:
        if len(c) < 6: continue
        n = len(c); cx = sum(p.x for p in c) / n; cy = sum(p.y for p in c) / n
        res.append("(n%d x%.3f y%.3f | x[%.2f,%.2f] y[%.2f,%.2f])" % (n, cx, cy, min(p.x for p in c), max(p.x for p in c),
                                                                    min(p.y for p in c), max(p.y for p in c)))
    print("Z%.2f" % z0, " ".join(res))
print("FATIAS_OK")
