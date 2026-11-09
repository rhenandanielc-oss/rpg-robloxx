"""Linha dos labios da HIGH: para cada fatia y do focinho, raio lateral (de +X e de -X) em varias alturas; o sulco e o
ponto mais fundo (menor |x|) entre o nariz e o queixo. So leitura. Uso: blender -b <blend> -P medir_boca.py -- <objeto>"""
import bpy, sys, json
from mathutils import Vector as V
nome = sys.argv[sys.argv.index("--") + 1]; ob = bpy.data.objects[nome]
dg = bpy.context.evaluated_depsgraph_get()
vs = [v.co for v in ob.data.vertices]; nar = min(vs, key=lambda v: v.y)
print("NARIZ", tuple(round(c, 3) for c in nar))
out = []
for k in range(0, 40):
    y = nar.y + 0.12 + k * 0.05
    for sx in (1, -1):
        pts = []
        for j in range(70):
            z = nar.z - 0.75 + j * 0.02
            ok, h, n, _ = ob.ray_cast(V((4 * sx, y, z)), V((-sx, 0, 0)), distance=6)
            if ok and abs(h.x) < 1.6: pts.append((abs(h.x), z))
        if len(pts) < 10: continue
        # sulco: minimo local de |x| com paredes dos dois lados (acima e abaixo mais largas)
        best = None
        for i in range(3, len(pts) - 3):
            xa = max(p[0] for p in pts[i - 3:i]); xb = max(p[0] for p in pts[i + 1:i + 4])
            prof = min(xa, xb) - pts[i][0]
            if best is None or prof > best[0]: best = (prof, pts[i][1], pts[i][0])
        out.append((round(y, 3), sx, round(best[1], 3), round(best[0], 3), round(best[2], 3)))
for r in out: print("SULCO y=%.2f lado=%+d z=%.3f prof=%.3f x=%.3f" % r)
