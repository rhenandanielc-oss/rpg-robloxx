"""Testes da boca da E3: poses da mandibula (graus) e closes 3/4, perfil e vista interna, com a mesma luz neutra.
Mede tambem penetracao: vertices da mandibula (peso>0,5) que entram na pele da cabeca/juba (BVH, lado da normal).
Uso: blender -b <e3.blend> -P e3_06_render_boca.py -- <saida_dir> <graus,graus,...>"""
import bpy, sys, os, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
GRAUS = [float(x) for x in A[1].split(",")]
sc = bpy.context.scene; sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = True
sc.view_settings.view_transform = "Standard"
w = bpy.data.worlds.new("Neutro"); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.2; sol.angle = math.radians(40)
so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
cam_d = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
arm = bpy.data.objects["Leao_Rig_Teste_Boca"]; pb = arm.pose.bones["Mandibula"]; pb.rotation_mode = "XYZ"
corpo = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E")][0]
def queixo_z(a):
    pb.rotation_euler = (math.radians(a), 0, 0); bpy.context.view_layer.update()
    return (arm.matrix_world @ pb.tail).z
SINAL = 1 if queixo_z(10) < queixo_z(0) else -1
def persp(nome, alvo, az, el, dist, lens, w_=900, h_=900):
    cam_d.type = "PERSP"; cam_d.lens = lens; alvo = Vector(alvo)
    cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)),
                                  math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = w_, h_
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
def penetracao():
    dg = bpy.context.evaluated_depsgraph_get(); ev = corpo.evaluated_get(dg); m = ev.to_mesh()
    gi = corpo.vertex_groups["Mandibula"].index; wv = []
    for v in corpo.data.vertices:
        x = 0.0
        for g in v.groups:
            if g.group == gi: x = g.weight
        wv.append(x)
    cab = [p for p in m.polygons if p.material_index == 0 and max(wv[i] for i in p.vertices) < 0.05]
    bvh = BVHTree.FromPolygons([v.co.copy() for v in m.vertices], [list(p.vertices) for p in cab])
    n = 0
    for i, v in enumerate(m.vertices):
        if wv[i] < 0.5 or corpo.data.vertices[i].co.y > -11.5: continue
        hit = bvh.find_nearest(v.co, 0.25)
        if hit[0] is not None and (v.co - hit[0]).dot(hit[1]) < -0.01: n += 1
    ev.to_mesh_clear(); return n
def interior_fora():
    """boca fechada: vertices do interior/dentes/lingua que ficam FORA da pele (visiveis por fora)"""
    dg = bpy.context.evaluated_depsgraph_get(); ev = corpo.evaluated_get(dg); m = ev.to_mesh()
    pele = [p for p in m.polygons if p.material_index == 0]
    bvh = BVHTree.FromPolygons([v.co.copy() for v in m.vertices], [list(p.vertices) for p in pele])
    boca = {i for p in m.polygons if p.material_index == 1 for i in p.vertices}
    pele_v = {i for p in pele for i in p.vertices}
    pts = [m.vertices[i].co.copy() for i in boca - pele_v]
    for nome in ("Leao_Lingua", "Leao_Dentes_Sup", "Leao_Dentes_Inf"):
        o = bpy.data.objects[nome].evaluated_get(dg); mm = o.to_mesh(); pts += [v.co.copy() for v in mm.vertices]; o.to_mesh_clear()
    n = 0
    for p in pts:
        hit = bvh.find_nearest(p, 0.6)
        if hit[0] is not None and (p - hit[0]).dot(hit[1]) > 0.005: n += 1
    ev.to_mesh_clear(); return n, len(pts)
pb.rotation_euler = (0, 0, 0); bpy.context.view_layer.update()
print("FECHADA interior_fora_da_pele", interior_fora())
ALVO = (0, -14.2, 12.6)
rel = []
for g in GRAUS:
    pb.rotation_euler = (math.radians(SINAL * g), 0, 0); bpy.context.view_layer.update()
    t = "%02d" % int(g)
    persp("boca_%s_34" % t, ALVO, -38, 6, 12, 50)
    persp("boca_%s_perfil" % t, ALVO, -90, 0, 12, 50)
    if g > 0: persp("boca_%s_interna" % t, (0, -14.0, 12.35), -8, -4, 6.5, 50)
    n = penetracao(); rel.append((g, n)); print("POSE", g, "queixo_z", round((arm.matrix_world @ pb.tail).z, 3), "penetracao_verts", n)
print("BOCA_RENDER_OK", rel)
