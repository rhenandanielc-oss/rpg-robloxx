"""Importa o GLB do Meshy do urso, orienta (frente = -Y, pes em Z = 0, centrado em X) e escala para o porte oficial
(topo da corcova = 9,0 studs; RPG_02: 8-10 ate os ombros). Salva CR_Urso_meshy_bruto.blend e imprime medidas.
Uso: blender -b --factory-startup -P importar_meshy.py -- <glb> <saida_dir> [girar_graus_z]"""
import bpy, sys, os, math
from mathutils import Vector as V, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; glb, OUT = a[0], os.path.abspath(a[1]); GIRO = float(a[2]) if len(a) > 2 else 0.0
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=glb)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
for o in bpy.context.scene.objects: o.select_set(o in ms)
bpy.context.view_layer.objects.active = ms[0]
if len(ms) > 1: bpy.ops.object.join()
ob = bpy.context.object; ob.name = "CR_Urso_Meshy"
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM"); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for o in [o for o in bpy.context.scene.objects if o.type == "EMPTY"]: bpy.data.objects.remove(o)
me = ob.data
if GIRO: me.transform(Matrix.Rotation(math.radians(GIRO), 4, "Z"))
pts = [v.co for v in me.vertices]
mn = V((min(p[i] for p in pts) for i in range(3))); mx = V((max(p[i] for p in pts) for i in range(3)))
print("MESHY_BRUTO tris", sum(len(p.vertices) - 2 for p in me.polygons), "caixa", tuple(round(c, 3) for c in mn), tuple(round(c, 3) for c in mx))
# frente: o lado do eixo mais longo (X ou Y) onde fica a cabeca = metade com o ponto mais alto do primeiro terco (corcova/cabeca)
L = mx - mn; eixo = 0 if L.x > L.y else 1
def alt_ponta(sinal):
    lim = (mn[eixo] + L[eixo] * 0.25) if sinal < 0 else (mx[eixo] - L[eixo] * 0.25)
    sel = [p.z for p in pts if (p[eixo] < lim if sinal < 0 else p[eixo] > lim)]
    return sum(sel) / len(sel)
# a cabeca fica mais baixa e estreita que a garupa? usa a largura media: a frente tem a cabeca (estreita) na ponta extrema
def larg_ponta(sinal):
    lim = (mn[eixo] + L[eixo] * 0.08) if sinal < 0 else (mx[eixo] - L[eixo] * 0.08)
    sel = [p[1 - eixo] for p in pts if (p[eixo] < lim if sinal < 0 else p[eixo] > lim)]
    return max(sel) - min(sel)
frente = -1 if larg_ponta(-1) < larg_ponta(1) else 1
print("MESHY eixo", "XY"[eixo], "frente", frente, "larguras", round(larg_ponta(-1), 3), round(larg_ponta(1), 3))
ang = {(1, -1): 0.0, (1, 1): math.pi, (0, -1): -math.pi / 2, (0, 1): math.pi / 2}[(eixo, frente)]
me.transform(Matrix.Rotation(ang, 4, "Z"))
pts = [v.co for v in me.vertices]
mn = V((min(p[i] for p in pts) for i in range(3))); mx = V((max(p[i] for p in pts) for i in range(3)))
c = V(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z)); me.transform(Matrix.Translation(-c))
pts = [v.co for v in me.vertices]; L = mx - mn
# corcova: ponto mais alto entre 15% e 45% do comprimento a partir da frente
y0 = min(p.y for p in pts); comp = max(p.y for p in pts) - y0
omb = max(p.z for p in pts if y0 + comp * 0.15 < p.y < y0 + comp * 0.45)
k = 9.0 / omb; me.transform(Matrix.Scale(k, 4))
pts = [v.co for v in me.vertices]
mn = V((min(p[i] for p in pts) for i in range(3))); mx = V((max(p[i] for p in pts) for i in range(3)))
print("MESHY_FINAL escala %.4f caixa %s %s comprimento %.2f largura %.2f altura %.2f" % (k, tuple(round(x, 2) for x in mn), tuple(round(x, 2) for x in mx), mx.y - mn.y, mx.x - mn.x, mx.z))
for m in me.materials: print("MAT", m.name)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Urso_meshy_bruto.blend"))
print("MESHY_OK")
