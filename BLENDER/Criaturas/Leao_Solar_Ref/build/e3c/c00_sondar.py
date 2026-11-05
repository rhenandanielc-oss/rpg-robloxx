"""Sonda a geometria do focinho na E3_t2 (antes da boca): cortes sagital (x=0, 0.5, 1.0) e transversais (y=-15..-12.5),
para desenhar a anatomia da boca. Uso: blender -b E3_t2.blend -P c00_sondar.py -- <saida.npz>"""
import bpy, bmesh, sys
import numpy as np
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E")][0]
bm0 = bmesh.new(); bm0.from_mesh(ob.data)
roi = [f for f in bm0.faces if (lambda c: c.y < -11.0 and c.z > 9.5 and abs(c.x) < 3.2)(f.calc_center_median())]
out = {}
def corte(co, no, nome):
    bm = bm0.copy()
    fs = [f for f in bm.faces if (lambda c: c.y < -11.0 and c.z > 9.5 and abs(c.x) < 3.2)(f.calc_center_median())]
    g = list({v for f in fs for v in f.verts}) + list({e for f in fs for e in f.edges}) + fs
    r = bmesh.ops.bisect_plane(bm, geom=g, plane_co=co, plane_no=no, dist=1e-6)["geom_cut"]
    segs = [(tuple(e.verts[0].co), tuple(e.verts[1].co)) for e in r if isinstance(e, bmesh.types.BMEdge) and
            all(abs((v.co - V(co)).dot(V(no))) < 1e-4 for v in e.verts)]
    out[nome] = np.array(segs, np.float32).reshape(-1, 6); bm.free(); print(nome, len(segs))
for x in (0.0, 0.4, 0.8, 1.2):
    corte((x, 0, 0), (1, 0, 0), "sx_%0.1f" % x)
for y in (-15.2, -14.8, -14.4, -14.0, -13.6, -13.2, -12.8):
    corte((0, y, 0), (0, 1, 0), "sy_%0.1f" % y)
np.savez(A[0], **out); print("SONDA_OK")
