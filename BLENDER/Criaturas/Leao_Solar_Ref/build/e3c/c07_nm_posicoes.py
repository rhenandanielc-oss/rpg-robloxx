"""E3b: posicoes dos restos nao-manifold e das bordas abertas (agrupados por proximidade, 0,35 stud) e closes de cada grupo
com marcador, para conferir se aparecem. Le, nao salva o .blend. Uso: blender -b <e3b.blend> -P c07_nm_posicoes.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, json
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E")][0]
bm = bmesh.new(); bm.from_mesh(ob.data)
pts = [("aresta>2faces", (e.verts[0].co + e.verts[1].co) / 2) for e in bm.edges if len(e.link_faces) > 2]
pts += [("borda_aberta", (e.verts[0].co + e.verts[1].co) / 2) for e in bm.edges if e.is_boundary]
pts += [("vert_nao_manifold", v.co.copy()) for v in bm.verts if not v.is_manifold]
grupos = []
for tipo, p in pts:
    for g in grupos:
        if (g["c"] - p).length < 0.35: g["n"][tipo] = g["n"].get(tipo, 0) + 1; g["ps"].append(p); g["c"] = sum(g["ps"], Vector()) / len(g["ps"]); break
    else: grupos.append({"c": p.copy(), "ps": [p], "n": {tipo: 1}})
grupos.sort(key=lambda g: -len(g["ps"]))
res = [{"centro": [round(x, 2) for x in g["c"]], "contagem": g["n"]} for g in grupos]
json.dump(res, open(os.path.join(OUT, "nao_manifold_posicoes.json"), "w"), indent=1)
for r in res: print("GRUPO", r)
sc = bpy.context.scene; sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = True
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.2; so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
sc.render.resolution_x = sc.render.resolution_y = 420
for i, g in enumerate(grupos[:6]):
    c = g["c"]; lado = 1 if c.x >= 0 else -1
    for nome, d in (("fora", Vector((lado * 0.8, -0.45, 0.35)).normalized()),):
        cam.location = c + d * 3.5; cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "nm_%d_%s.png" % (i, nome)); bpy.ops.render.render(write_still=True)
print("NM_OK")
