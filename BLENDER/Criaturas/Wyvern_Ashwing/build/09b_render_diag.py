# Renders diagnosticos do descanso: mesma camera/escala/luz para comparar versoes.
# Vistas: lado, frente, tres4 (corpo inteiro), perna_L / perna_R (close lateral da perna), baixo (camera por baixo, chao
# ...; sufixo _cinza = mesma vista em cinza neutro (override de material)
# oculto, arame sobre a malha). Em todas, as intersecoes REAIS que envolvem perna (profundidade >= 0,02) aparecem como
# esferas vermelhas (raio proporcional a profundidade); rotulo com versao, clipe, quadro e vista.
# Uso: blender -b <v.blend> -P 09b_render_diag.py -- <pasta> <rotulo_versao> <clipe:quadro[,clipe:quadro...]> [vistas] [marcar=1]
#  ou sequencia (video): <alvos> = seq=Deitar,Deitado*2,Levantar[@passo[@total]]  -> <versao>_<vista>_NNN.png, sem marcas,
#     loops repetidos sem duplicar o quadro final; "total" repete o ultimo quadro ate N (comparar versoes de duracao diferente)
import bpy, sys, os, math, itertools
from collections import Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.geometry import intersect_ray_tri
argv = sys.argv[sys.argv.index("--") + 1:]
OUT, VER = argv[0], argv[1]
SEQ = argv[2].startswith("seq=")
if SEQ:
    partes = argv[2][4:].split("@"); PASSO_S = float(partes[1]) if len(partes) > 1 else 1.6; TOTAL = int(partes[2]) if len(partes) > 2 else 0
    ALVOS = []
    for spec in partes[0].split(","):
        nome, rep_ = (spec.split("*") + ["1"])[:2]; a_ = bpy.data.actions[nome]; f1 = a_.frame_range[1]; loop = bool(a_.get("loop"))
        fs = [k * PASSO_S for k in range(int(f1 / PASSO_S + 1e-6) + 1)]
        for r in range(int(rep_)): ALVOS += [(nome, f) for f in (fs[:-1] if loop and fs[-1] >= f1 - 1e-6 else fs)]
    while len(ALVOS) < TOTAL: ALVOS.append(ALVOS[-1])
else:
    ALVOS = [(a.split(":")[0], float(a.split(":")[1])) for a in argv[2].split(",")]
VISTAS_ = argv[3].split(",") if len(argv) > 3 else ["lado", "frente", "tres4", "perna_L", "baixo"]
MARCAR = (argv[4] != "0") if len(argv) > 4 else True
os.makedirs(OUT, exist_ok=True)
scn = bpy.context.scene
arm = bpy.data.objects["Wyvern_Rig"]; mesh = bpy.data.objects["Wyvern"]; key = mesh.data.shape_keys
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 960; scn.render.resolution_y = 640
scn.world = bpy.data.worlds.new("W"); scn.world.color = (0.55, 0.6, 0.68)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30))); bpy.context.object.data.energy = 4
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-60), 0, math.radians(200))); bpy.context.object.data.energy = 1.5
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(180), 0, 0)); luz_baixo = bpy.context.object; luz_baixo.data.energy = 2.5
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0)); chao = bpy.context.object
m = bpy.data.materials.new("chao"); m.diffuse_color = (0.42, 0.45, 0.38, 1); chao.data.materials.append(m)
grade = []
for i in range(-15, 16):
    for eixo in (0, 1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(i * 4 if eixo == 0 else 0, i * 4 if eixo == 1 else 0, 0.01))
        o = bpy.context.object; o.scale = (0.04, 120, 0.01) if eixo == 0 else (120, 0.04, 0.01)
        mg = bpy.data.materials.get("grade") or bpy.data.materials.new("grade"); mg.diffuse_color = (0.3, 0.32, 0.28, 1)
        o.data.materials.append(mg); grade.append(o)
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=4.0, location=(12, -18, 2.0)); h1 = bpy.context.object
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75, location=(12, -18, 4.75)); h2 = bpy.context.object
mh = bpy.data.materials.new("humano"); mh.diffuse_color = (0.85, 0.3, 0.2, 1)
for o in (h1, h2): o.data.materials.append(mh)
# arame: copia ligada da malha com modificador Wireframe (so na vista de baixo)
fio = mesh.copy(); scn.collection.objects.link(fio)
wm = fio.modifiers.new("fio", "WIREFRAME"); wm.thickness = 0.025; wm.use_replace = True
mf = bpy.data.materials.new("fio"); mf.diffuse_color = (0.05, 0.05, 0.05, 1); mf.use_nodes = True
mf.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
fio.data = mesh.data; fio.active_material_index = 0
wm.material_offset = len(mesh.data.materials); mesh.data.materials.append(mf)
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); scn.collection.objects.link(cam); scn.camera = cam
cd.type = "ORTHO"; cd.clip_end = 1000
tc = bpy.data.curves.new("rot", "FONT"); rot = bpy.data.objects.new("rot", tc); scn.collection.objects.link(rot)
mt = bpy.data.materials.new("rot"); mt.use_nodes = True; bt = mt.node_tree.nodes["Principled BSDF"]
bt.inputs["Base Color"].default_value = (1, 1, 0.6, 1); bt.inputs["Emission Color"].default_value = (1, 1, 0.6, 1)
bt.inputs["Emission Strength"].default_value = 3; tc.materials.append(mt); rot.parent = cam
mm = bpy.data.materials.new("marca"); mm.use_nodes = True; bm = mm.node_tree.nodes["Principled BSDF"]
bm.inputs["Base Color"].default_value = (1, 0.05, 0.05, 1); bm.inputs["Emission Color"].default_value = (1, 0.05, 0.05, 1); bm.inputs["Emission Strength"].default_value = 4
# vista: (direcao da camera, centro, escala) - centro fixo para comparar versoes
VISTAS = {"lado": (Vector((1, 0, 0.05)), Vector((0, 7, 8)), 42), "frente": (Vector((0, -1, 0.15)), Vector((0, 0, 7)), 30),
          "tres4": (Vector((0.8, -0.7, 0.45)), Vector((0, 5, 7)), 40),
          "perna_L": (Vector((1, 0.15, 0.1)), Vector((2, 1.0, 2.4)), 11), "perna_R": (Vector((-1, 0.15, 0.1)), Vector((-2, 1.0, 2.4)), 11),
          "baixo": (Vector((0.15, 0.1, -1)), Vector((0, 1.5, 2)), 22),
          "pe_L": (Vector((1, -0.3, 0.12)), Vector((2.1, -1.0, 0.8)), 6), "pe_R": (Vector((-1, -0.3, 0.12)), Vector((-2.1, -1.0, 0.8)), 6),
          "joelho_L": (Vector((1, 0.1, 0.1)), Vector((2.0, 0.0, 3.4)), 9)}
# intersecoes reais com perna
me = mesh.data; me.calc_loop_triangles(); TRI = [tuple(t.vertices) for t in me.loop_triangles]
rest = [v.co.copy() for v in me.vertices]; kd = KDTree(len(rest))
for i, p in enumerate(rest): kd.insert(p, i)
kd.balance(); S = {}
for i in range(len(rest)):
    if i in S: continue
    for _, j, _ in kd.find_range(rest[i], 1e-3): S.setdefault(j, i)
SOLD = [{S[i] for i in t} for t in TRI]
GR = {g.index: g.name for g in mesh.vertex_groups}
DOM = [GR[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else "?" for v in me.vertices]
EP = [Counter(DOM[i] for i in t).most_common(1)[0][0].startswith(("thigh", "calf", "foot", "toe")) for t in TRI]
def bari(p, tv, tol=0.02):
    a, b, c = tv; v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11, d20, d21 = v0.dot(v0), v0.dot(v1), v1.dot(v1), v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-14: return False
    v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den
    return v >= -tol and w >= -tol and v + w <= 1 + tol
def marcas():
    ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data; P = [mesh.matrix_world @ v.co for v in ev.vertices]
    bvh = BVHTree.FromPolygons(P, TRI, all_triangles=True); out = []
    for a, b in bvh.overlap(bvh):
        if a >= b or not (EP[a] or EP[b]) or SOLD[a] & SOLD[b]: continue
        A, B = TRI[a], TRI[b]; pts = []
        for X_, Y_ in ((A, B), (B, A)):
            tv = [P[i] for i in Y_]
            for u, v in ((X_[0], X_[1]), (X_[1], X_[2]), (X_[2], X_[0])):
                q = intersect_ray_tri(*tv, P[v] - P[u], P[u], True)
                if q is not None and (q - P[u]).dot(q - P[v]) <= 1e-12: pts.append(q)
        if len(pts) < 2: continue
        p1, p2 = max(itertools.combinations(pts, 2), key=lambda ab: (ab[0] - ab[1]).length)
        if (p1 - p2).length < 0.01: continue
        d = 0.0
        for A_, B_ in ((A, B), (B, A)):
            nb = (P[B_[1]] - P[B_[0]]).cross(P[B_[2]] - P[B_[0]])
            if nb.length < 1e-12: continue
            nb.normalize(); tv = [P[i] for i in B_]
            for i in A_:
                dd = (P[i] - tv[0]).dot(nb)
                if dd < 0 and bari(P[i] - nb * dd, tv): d = max(d, -dd)
        if d >= 0.02: out.append(((p1 + p2) / 2, d))
    return out
def usar(nome):
    a = bpy.data.actions[nome]
    for ob, tipo in ((arm, "OBJECT"), (key, "KEY")):
        if ob.animation_data is None: ob.animation_data_create()
        ob.animation_data.action = a
        sl = [s for s in a.slots if s.target_id_type == tipo]
        if sl: ob.animation_data.action_slot = sl[0]
MCINZA = bpy.data.materials.new("cinza"); MCINZA.diffuse_color = (0.6, 0.6, 0.6, 1)
esferas = []
if SEQ: MARCAR = False
for k_, (nome, f) in enumerate(ALVOS):
    usar(nome); scn.frame_set(int(f), subframe=f - int(f)); bpy.context.view_layer.update()
    for o in esferas: bpy.data.objects.remove(o)
    esferas = []
    mk = marcas() if MARCAR else []
    for p, d in mk:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04 + 0.25 * min(d, 1.0), location=p, segments=8, ring_count=6)
        o = bpy.context.object; o.data.materials.append(mm); esferas.append(o)
    for v in VISTAS_:
        cinza = v.endswith("_cinza")                                 # sombreamento neutro (material unico cinza)
        scn.view_layers[0].material_override = MCINZA if cinza else None
        d, c, esc = VISTAS[v[:-6] if cinza else v]; d = d.normalized()
        baixo = v.startswith("baixo")
        for o in [chao] + grade: o.hide_render = baixo
        fio.hide_render = not baixo; luz_baixo.hide_render = not baixo
        cd.ortho_scale = esc; cam.location = c + d * 300; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        tc.body = f"{VER} | {nome} f{f:.1f} | {v}" + ("" if SEQ else f" | {len(mk)} marcas"); tc.size = esc * 0.03; rot.location = (-esc / 2 * 0.96, esc * 0.667 / 2 * 0.9, -10)
        arq = f"{VER}_{v}_{k_:03d}.png" if SEQ else f"{VER}_{nome}_f{f:.1f}_{v}.png"
        scn.render.filepath = os.path.join(OUT, arq); bpy.ops.render.render(write_still=True)
    print("ALVO", nome, f, "marcas", len(mk), "prof_max", round(max([d for _, d in mk], default=0), 3), flush=True)
print("OK")
