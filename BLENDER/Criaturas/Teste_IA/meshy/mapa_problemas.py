"""Mapa de problemas num quadro: faces com aresta esticada (>1.8x, vermelho), comprimida (<0.4x, azul) e faces de asa
que cruzam a outra asa (amarelo). Workbench com cor por atributo, 5 vistas. Tambem imprime centroides dos cruzamentos
e os ossos dominantes nas faces vermelhas.
Uso: blender -b Silverwing_M2M.blend -P mapa_problemas.py -- saida_dir acao:quadro ..."""
import bpy, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import Counter
args = sys.argv[sys.argv.index("--") + 1:]; out = args[0]; pedidos = [a.split(":") for a in args[1:]]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
gi = {g.index: g.name for g in M.vertex_groups}
def dom(v): return gi[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "-"
DOM = [dom(v) for v in M.data.vertices]
LADO = [d[-1] if d.startswith(("wing_", "shoulder_")) else "" for d in DOM]
R0 = [v.co.copy() for v in M.data.vertices]
polys = [tuple(p.vertices) for p in M.data.polygons]
at = M.data.color_attributes.get("diag") or M.data.color_attributes.new("diag", "BYTE_COLOR", "CORNER")
M.data.color_attributes.active_color = at
for o in bpy.data.objects:
    if o.name.startswith("chao"): o.hide_render = True
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "VERTEX"
sc.render.resolution_x, sc.render.resolution_y = 520, 420
cam = bpy.data.objects["cam_rev"]; sc.camera = cam
for acao, q in pedidos:
    act = bpy.data.actions["Silverwing_" + acao]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    sc.frame_set(int(q))
    dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh()
    P = [v.co.copy() for v in me.vertices]; M.evaluated_get(dg).to_mesh_clear()
    cor = []; ver = Counter()
    for fi, pv in enumerate(polys):
        c = (0.75, 0.75, 0.75, 1)
        for i in range(len(pv)):
            a, b = pv[i], pv[(i + 1) % len(pv)]; l0 = (R0[a] - R0[b]).length
            if l0 < 1e-6: continue
            r = (P[a] - P[b]).length / l0
            if r > 1.8: c = (1, 0.05, 0.05, 1); ver[DOM[a]] += 1
            elif r < 0.4 and c[0] < 1: c = (0.1, 0.3, 1, 1)
        cor.append(c)
    il = [i for i, p in enumerate(polys) if LADO[p[0]] == "l"]; ir = [i for i, p in enumerate(polys) if LADO[p[0]] == "r"]
    tl = BVHTree.FromPolygons(P, [polys[i] for i in il]); tr = BVHTree.FromPolygons(P, [polys[i] for i in ir])
    cent = []
    for a, b in tl.overlap(tr):
        cor[il[a]] = cor[ir[b]] = (1, 0.9, 0.1, 1)
        cent.append(sum((P[v] for v in polys[il[a]]), Vector()) / len(polys[il[a]]))
    if cent:
        cm = sum(cent, Vector()) / len(cent); print("CRUZ", acao, q, len(cent), "centro", tuple(round(c, 3) for c in cm),
              "ossos", Counter(DOM[polys[il[a]][0]] for a, b in tl.overlap(tr)).most_common(4),
              Counter(DOM[polys[ir[b]][0]] for a, b in tl.overlap(tr)).most_common(4))
    print("ESTICADAS", acao, q, "total", sum(ver.values()), ver.most_common(10))
    k = 0
    for p in M.data.polygons:
        for li in p.loop_indices: at.data[li].color = cor[p.index]
    M.data.update()
    mn = Vector([min(p[i] for p in P) for i in range(3)]); mx = Vector([max(p[i] for p in P) for i in range(3)])
    c = (mn + mx) / 2; r = (mx - mn).length
    for vista, d in (("frente", (0, -1, 0.1)), ("topo", (0, -0.01, 1)), ("lado", (1, 0, 0.1)), ("tras", (0.2, 1, 0.5)), ("baixo", (0.1, -0.2, -1))):
        cam.location = c + Vector(d).normalized() * r * 1.1
        cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(out, "mapa_%s_%s_%s.png" % (acao, q, vista)); bpy.ops.render.render(write_still=True)
print("MAPA_OK")
