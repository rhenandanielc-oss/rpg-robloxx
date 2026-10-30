"""Medidas para encaixar o esqueleto no Drake (pose neutra): linha do corpo/pescoco/cabeca por fatias em Y,
trajeto das 4 patas por fatias em Z, bordo de ataque das asas por fatias em X, linha da cauda. Uso: blender -b -P medir_drake.py -- malha.glb"""
import bpy, sys
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[sys.argv.index("--") + 1])
o = [x for x in bpy.data.objects if x.type == "MESH"][0]
V = [o.matrix_world @ v.co for v in o.data.vertices]
def r3(v): return "(%.3f,%.3f,%.3f)" % tuple(v)
print("== CORPO (|x|<0.12): y -> z min/max, centro")
for k in range(-13, 14):
    y = k * 0.05; ps = [p for p in V if abs(p.y - y) < 0.02 and abs(p.x) < 0.12 and p.z > 0.12]
    if ps:
        zs = [p.z for p in ps]; xs = [p.x for p in ps]
        print("Y%+.2f n%4d z[%.3f,%.3f] zc %.3f xc %.3f" % (y, len(ps), min(zs), max(zs), (min(zs) + max(zs)) / 2, sum(xs) / len(xs)))
print("== PESCOCO/CABECA (y<-0.3, z>0.4): z -> y,x centro")
for k in range(8, 16):
    z = k * 0.05; ps = [p for p in V if abs(p.z - z) < 0.02 and p.y < -0.25 and abs(p.x) < 0.12]
    if ps: print("Z%.2f n%4d yc %.3f y[%.3f,%.3f] xc %.3f" % (z, len(ps), sum(p.y for p in ps) / len(ps), min(p.y for p in ps), max(p.y for p in ps), sum(p.x for p in ps) / len(ps)))
print("== PATAS (z fatias, por quadrante)")
for nome, cx, cy in (("PD_E", 0.11, -0.47), ("PD_D", -0.11, -0.47), ("PT_E", 0.11, -0.03), ("PT_D", -0.11, -0.03)):
    for z in (0.01, 0.04, 0.08, 0.12, 0.16, 0.2, 0.25, 0.3, 0.35):
        ps = [p for p in V if abs(p.z - z) < 0.012 and (p.x - cx) * (1 if cx > 0 else -1) > -0.07 and abs(p.y - cy) < 0.2 and abs(p.x) < 0.3]
        if ps:
            print(nome, "Z%.2f n%3d c%s y[%.3f,%.3f] x[%.3f,%.3f]" % (z, len(ps), r3(sum(ps, Vector()) / len(ps)), min(p.y for p in ps), max(p.y for p in ps), min(p.x for p in ps), max(p.x for p in ps)))
print("== ASAS bordo de ataque (por |x|): ponto de z max e y min")
for s in (1, -1):
    for k in range(2, 20):
        x = k * 0.05; ps = [p for p in V if abs(p.x - s * x) < 0.012 and p.z > 0.25]
        if ps:
            t = max(ps, key=lambda p: p.z); f = min(ps, key=lambda p: p.y); b = max(ps, key=lambda p: p.y)
            print("ASA%s X%.2f topo%s frente%s tras%s" % ("E" if s > 0 else "D", s * x, r3(t), r3(f), r3(b)))
print("== CAUDA (y>0.1): y -> centro")
for k in range(2, 13):
    y = k * 0.05; ps = [p for p in V if abs(p.y - y) < 0.015 and p.z < 0.45 and abs(p.x) < 0.7 and not (abs(p.x) > 0.06 and p.z < 0.2 and y < 0.15)]
    if ps: print("CY%.2f n%4d c%s z[%.3f,%.3f]" % (y, len(ps), r3(sum(ps, Vector()) / len(ps)), min(p.z for p in ps), max(p.z for p in ps)))
print("MEDIR_OK")
