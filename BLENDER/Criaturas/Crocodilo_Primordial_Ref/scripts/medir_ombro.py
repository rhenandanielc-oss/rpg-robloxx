"""Somente leitura: altura da pele no ombro/quadril sem cristas (percentil do topo em fatias) e posicao das patas.
Uso: blender -b <blend> -P medir_ombro.py -- <objeto>"""
import bpy, sys
nome = sys.argv[sys.argv.index("--") + 1]
ob = bpy.data.objects[nome]; P = [v.co for v in ob.data.vertices]
pes = [p for p in P if p.z < 0.25]
ys = sorted(p.y for p in pes)
print("PES faixa y", round(ys[0], 2), round(ys[-1], 2))
for y in [x * 1.0 for x in range(-14, 15)]:
    s = sorted(p.z for p in P if abs(p.y - y) < 0.3 and abs(p.x) < 2.2)
    b = [p.z for p in P if abs(p.y - y) < 0.3 and abs(p.x) < 1.0]
    if s: print("FATIA y %5.1f topo_p90 %.2f topo_max %.2f base %.2f larg %.2f" % (y, s[int(len(s) * 0.90)], s[-1], min(b) if b else -1,
          2 * max(abs(p.x) for p in P if abs(p.y - y) < 0.3)))
