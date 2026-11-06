"""Lote 5 (sela definitiva): inspecao somente leitura do dorso na pose de descanso - cortes transversais da pele
(largura/altura por y), cristas perto do assento, ossos dominantes por regiao e alcance das patas dianteiras/traseiras.
Uso: blender -b CR_Crocodilo_Anim.blend -P inspecao_sela.py"""
import bpy, json
import numpy as np
from mathutils import Vector as V
croc = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]
croc.animation_data.action = None
for pb in croc.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
me = lo.data; W = lo.matrix_world
co = np.array([W @ v.co for v in me.vertices])
gn = {g.index: g.name for g in lo.vertex_groups}
dom = []
for v in me.vertices:
    if v.groups: g = max(v.groups, key=lambda g: g.weight); dom.append((gn[g.group], g.weight))
    else: dom.append(("-", 0))
print("BBOX", co.min(0).round(2), co.max(0).round(2), "verts", len(co), "tris", sum(len(p.vertices) - 2 for p in me.polygons))
for y in np.arange(-10.0, 1.01, 0.5):
    s = co[np.abs(co[:, 1] - y) < 0.25]
    if not len(s): continue
    topo = s[np.abs(s[:, 0]) < 0.6][:, 2].max() if (np.abs(s[:, 0]) < 0.6).any() else None
    alto = s[s[:, 2] > 2.5]
    larg = (alto[:, 0].min(), alto[:, 0].max()) if len(alto) else (0, 0)
    ossos = {}
    for i in np.where(np.abs(co[:, 1] - y) < 0.25)[0]:
        if co[i, 2] > 3.0: ossos[dom[i][0]] = ossos.get(dom[i][0], 0) + 1
    print("CORTE y %5.1f topo %.2f z_min %.2f x %.2f..%.2f (z>2,5) | z max %.2f | ossos dorso %s" % (y, topo or -1, s[:, 2].min(), larg[0], larg[1], s[:, 2].max(),
          dict(sorted(ossos.items(), key=lambda kv: -kv[1])[:3])))
# perfil lateral na altura do assento: x da pele por z (lado +X e -X)
for y in (-5.8, -4.6, -3.4):
    s = co[np.abs(co[:, 1] - y) < 0.2]
    linha = []
    for z in np.arange(1.0, 6.01, 0.5):
        f = s[np.abs(s[:, 2] - z) < 0.25]
        linha.append("z%.1f:%s" % (z, ("%.2f/%.2f" % (f[:, 0].min(), f[:, 0].max())) if len(f) else "-"))
    print("PERFIL y", y, " ".join(linha))
for b in croc.data.bones:
    if b.name.startswith(("Braco", "Antebraco", "Coxa", "Perna", "Coluna", "Mao", "Pe", "Ombro", "Quadril", "Raiz", "Pescoco")):
        print("OSSO %-10s cab %s cauda %s pai %s" % (b.name, tuple(round(c, 2) for c in b.head_local), tuple(round(c, 2) for c in b.tail_local), b.parent.name if b.parent else None))
