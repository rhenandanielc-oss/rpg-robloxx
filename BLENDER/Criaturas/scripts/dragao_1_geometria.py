# Dragao das Montanhas - etapa 2: geometria completa (corpo robusto + asas), escala 1 BU = 1 stud.
# Frente = -Y, cima = +Z, direita da criatura = -X (em Blender olhando para -Y, a direita fica em -X).
# Oficial: quadrupede, duas asas independentes, 18-24 ate os ombros (usado 21). Comprimento/envergadura PROVISORIOS.
import bpy, bmesh, math, sys, os, json
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1]
FORMA = sys.argv[sys.argv.index("--") + 2] if len(sys.argv) > sys.argv.index("--") + 2 else "Montanhas"
# formas regionais (RPG_02: mesma estrutura-base; chifres, asas, escamas e proporcoes regionais distintos)
CFG = {"Montanhas": dict(corpo=1.0, pescoco=1.0, chifre="curvo", placaH=1.0, placaBase=0.42, achatar=0.35, asa=1.0, recorte=0.22),
       "Glacial": dict(corpo=0.88, pescoco=1.16, chifre="reto", placaH=1.55, placaBase=0.30, achatar=0.6, asa=1.08, recorte=0.15),
       "Sombrio": dict(corpo=0.94, pescoco=1.06, chifre="multiplo", placaH=1.8, placaBase=0.30, achatar=0.25, asa=1.05, recorte=0.34)}[FORMA]
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

def skin_obj(name, pts, edges, radii, sub=2):
    me = bpy.data.meshes.new(name)
    me.from_pydata(pts, edges, [])
    ob = bpy.data.objects.new(name, me)
    scn.collection.objects.link(ob)
    sk = ob.modifiers.new("Skin", "SKIN"); sk.use_smooth_shade = True
    ss = ob.modifiers.new("Sub", "SUBSURF"); ss.levels = sub; ss.render_levels = sub
    for i, r in enumerate(radii):
        v = me.skin_vertices[0].data[i]
        v.radius = (r[0], r[1]) if isinstance(r, tuple) else (r, r)
    me.skin_vertices[0].data[0].use_root = True
    return ob

# ---------- espinha (indices fixos usados pelo rig)
spine = [
    (0, 64, 3.2), (0, 57, 5.0), (0, 50, 7.2), (0, 43, 9.4), (0, 36, 11.4), (0, 29, 13.0), (0, 21.5, 14.2),  # 0-6 cauda
    (0, 13, 15.0),   # 7 pelve
    (0, 6, 14.4),    # 8 lombo
    (0, -1, 14.2),   # 9 meio
    (0, -7, 14.6),   # 10 peito (cernelha: topo = 14.6 + 6.4 = 21)
    (0, -12.5, 17.6),  # 11 base do pescoco
    (0, -16.0, 21.8), (0, -19.4, 25.6), (0, -22.6, 28.2),  # 12-14 pescoco
    (0, -25.8, 29.4),  # 15 nuca
    (0, -29.0, 29.2),  # 16 cranio
    (0, -32.6, 28.4),  # 17 focinho medio
    (0, -36.2, 27.7),  # 18 ponta do focinho
]
srad = [0.4, 1.1, 1.9, 2.8, 3.7, 4.6, 5.4,
        (6.6, 6.2), (7.2, 6.4), (7.8, 6.6), (7.6, 6.4), (5.4, 5.0),
        (4.5, 4.4), (3.9, 3.9), (3.5, 3.4), (3.3, 3.0), (3.4, 2.7), (2.5, 1.85), (1.75, 1.25)]
# proporcoes regionais: tronco mais/menos massivo, pescoco mais longo
def esc(r, f): return (r[0] * f, r[1] * f) if isinstance(r, tuple) else r * f
srad = [esc(r, CFG["corpo"]) if 7 <= i <= 11 else r for i, r in enumerate(srad)]
b0 = Vector(spine[10])
spine = [tuple(b0 + Vector((0, (Vector(p) - b0).y * CFG["pescoco"], (Vector(p) - b0).z * (1 + (CFG["pescoco"] - 1) * 0.7)))) if i >= 11 else p for i, p in enumerate(spine)]
pts = list(spine); edges = [(i, i + 1) for i in range(len(spine) - 1)]; rad = list(srad)
I_PELVE, I_PEITO = 7, 10
LEG = {}
def perna(nome, base_idx, chain, radii):
    prev = base_idx; idx = []
    for p, r in zip(chain, radii):
        pts.append(p); rad.append(r); edges.append((prev, len(pts) - 1)); prev = len(pts) - 1; idx.append(prev)
    LEG[nome] = chain
for s, lado in ((-1, "D"), (1, "E")):
    # ombro -> meio do braco -> cotovelo -> pulso -> pata -> dedos (musculo em cima, afinando para baixo)
    perna("Dianteira_" + lado, I_PEITO, [(s * 5.8, -7.6, 12.4), (s * 6.3, -6.9, 9.6), (s * 6.6, -5.6, 7.0), (s * 6.3, -8.2, 2.4), (s * 6.3, -10.4, 1.0), (s * 6.3, -13.0, 0.62)],
          [(4.3, 4.8), (3.3, 3.5), (2.4, 2.5), (1.55, 1.55), (1.9, 0.95), (1.75, 0.6)])
    # quadril -> coxa -> joelho (frente) -> jarrete (tras) -> pata -> dedos
    perna("Traseira_" + lado, I_PELVE, [(s * 6.0, 13.2, 12.6), (s * 6.5, 11.2, 9.9), (s * 6.8, 9.3, 7.4), (s * 6.5, 14.6, 3.3), (s * 6.5, 12.1, 1.0), (s * 6.5, 9.4, 0.62)],
          [(4.9, 5.4), (3.8, 4.0), (2.6, 2.8), (1.6, 1.6), (2.0, 0.95), (1.85, 0.6)])
corpo = skin_obj("Corpo", pts, edges, rad)

# ---------- detalhes: chifres, placas dorsais, garras
def tubo(name, path, radii, achatar=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []
    n = len(path)
    for k in range(n):
        p = Vector(path[k])
        d = (Vector(path[min(k + 1, n - 1)]) - Vector(path[max(k - 1, 0)])).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
        u = d.cross(up).normalized(); v = d.cross(u).normalized()
        ring = []
        for a in range(10):
            ang = a / 10 * 2 * math.pi
            off = u * math.cos(ang) * radii[k] + v * math.sin(ang) * radii[k] * (achatar or 1)
            ring.append(bm.verts.new(p + off))
        rings.append(ring)
    for k in range(n - 1):
        for a in range(10):
            b = (a + 1) % 10
            bm.faces.new((rings[k][a], rings[k][b], rings[k + 1][b], rings[k + 1][a]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    for f in me.polygons: f.use_smooth = True
    return ob
def arco(a, b, alt, n=8):
    a, b = Vector(a), Vector(b); return [tuple(a.lerp(b, t) + Vector((0, 0, alt * math.sin(t * math.pi)))) for t in [i / (n - 1) for i in range(n)]]
det = []
for s in (-1, 1):
    nu = Vector(spine[15]); cr = Vector(spine[16])  # nuca e cranio (ja com o pescoco regional)
    def hp(dx, dy, dz, base=cr): return tuple(base + Vector((s * dx, dy, dz)))
    if CFG["chifre"] == "curvo":
        ph = arco(hp(1.6, 2.0, 2.0), hp(3.4, 11.5, 5.3), 2.6)
    elif CFG["chifre"] == "reto":
        ph = arco(hp(1.4, 2.0, 2.0), hp(2.6, 14.0, 4.2), 0.6)
    else:
        ph = arco(hp(1.7, 1.5, 2.0), hp(5.2, 10.0, 6.5), 2.0)
    det.append(tubo("Chifre", ph, [1.25 * (1 - i / 8) + 0.06 for i in range(len(ph))]))
    ph2 = arco(hp(2.6, 0.4, 1.2), hp(5.0, 6.0, 1.6), 1.0, 6)
    det.append(tubo("ChifreMenor", ph2, [0.6 * (1 - i / 6) + 0.05 for i in range(len(ph2))]))
    if CFG["chifre"] == "multiplo":
        for k, (dy, dz) in enumerate(((3.6, 2.6), (5.4, 2.4), (-1.0, -1.6))):
            pk = arco(hp(2.2, dy, dz), hp(4.2, dy + 4.0, dz + 2.2), 0.6, 5)
            det.append(tubo("Espinho", pk, [0.55 * (1 - i / 5) + 0.04 for i in range(len(pk))]))
    # cristas sobre os olhos
    det.append(tubo("Sobrancelha", [hp(2.2, -2.4, 0.8), hp(2.6, 0.0, 1.7), hp(2.4, 2.0, 1.8)], [0.45, 0.55, 0.3]))
# placas dorsais: laminas de rocha (achatadas lateralmente), do cranio a ponta da cauda
ids = list(range(16, -1, -1))
for i in ids:
    if i in (17, 18): continue
    x, y, z = spine[i]; r = srad[i][1] if isinstance(srad[i], tuple) else srad[i]
    h = (0.55 * r + 0.8) * CFG["placaH"]
    base = (0, y + 0.4, z + r * 0.86); topo = (0, y + 1.8, z + r * 0.86 + h)
    det.append(tubo("Placa", [base, tuple(Vector(base).lerp(Vector(topo), 0.5)), topo], [CFG["placaBase"] * r + 0.35, 0.28 * r * CFG["placaBase"] / 0.42 + 0.2, 0.05], achatar=CFG["achatar"]))
# garras: 3 por pata, curvas para baixo
for nome, ch in LEG.items():
    px, py, pz = ch[-1]
    for k, dx in enumerate((-0.9, 0, 0.9)):
        a = (px + dx, py - 0.7, 0.75); b = (px + dx * 1.15, py - 2.4, 0.12)
        det.append(tubo("Garra", [a, tuple(Vector(a).lerp(Vector(b), 0.5) + Vector((0, -0.2, 0.2))), b], [0.42, 0.26, 0.04]))
for ob in det:
    m = ob.modifiers.new("Sub", "SUBSURF"); m.levels = 1

# ---------- asas (pose aberta). Por lado: braco (umero, antebraco), punho, 4 dedos e membrana recortada
ASA = {}
def asa(s, lado):
    A = CFG["asa"]
    def wx(x): return s * (4.8 + (x - 4.8) * A)
    ombro = Vector((s * 4.8, -8.5, 19.6)); cotov = Vector((wx(14.0), -6.0, 25.0)); punho = Vector((wx(25.0), -9.5, 27.0))
    dedos = [Vector((wx(43.0), -5.0, 25.0)), Vector((wx(40.0), 5.0, 21.5)), Vector((wx(33.0), 13.0, 18.5)), Vector((wx(24.0), 17.0, 16.5))]
    flanco = Vector((s * 6.0, 9.0, 16.5))
    ASA[lado] = {"ombro": tuple(ombro), "cotovelo": tuple(cotov), "punho": tuple(punho), "dedos": [tuple(d) for d in dedos], "flanco": tuple(flanco)}
    # ossos visiveis (tubos)
    arm = [tubo("AsaBraco", [tuple(ombro), tuple(ombro.lerp(cotov, 0.5)), tuple(cotov)], [1.5, 1.25, 1.0]),
           tubo("AsaAntebraco", [tuple(cotov), tuple(cotov.lerp(punho, 0.5)), tuple(punho)], [1.0, 0.85, 0.75])]
    for d in dedos:
        arm.append(tubo("AsaDedo", [tuple(punho), tuple(punho.lerp(d, 0.5)), tuple(d)], [0.6, 0.35, 0.08]))
    # garra do punho
    arm.append(tubo("GarraPunho", [tuple(punho), tuple(punho + Vector((s * 0.4, -1.6, 1.2))), tuple(punho + Vector((s * 0.2, -2.4, 0.8)))], [0.45, 0.25, 0.04]))
    # membrana: contorno ombro -> cotovelo -> punho -> dedo1 -> recorte -> dedo2 -> ... -> dedo4 -> recorte -> flanco
    cont = [ombro, cotov, punho, dedos[0]]
    for a, b in zip(dedos[:-1], dedos[1:]):
        mid = a.lerp(b, 0.5); cont.append(mid.lerp(punho, CFG["recorte"])); cont.append(b)
    m4 = dedos[-1].lerp(flanco, 0.5); cont.append(m4.lerp(punho, 0.2)); cont.append(flanco)
    me = bpy.data.meshes.new("Membrana"); bm = bmesh.new()
    vs = [bm.verts.new(p) for p in cont]
    for i in range(len(vs)): bm.edges.new((vs[i], vs[(i + 1) % len(vs)]))
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bm.edges[:])
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=4, use_grid_fill=True)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free()
    mob = bpy.data.objects.new("Membrana", me); scn.collection.objects.link(mob)
    so = mob.modifiers.new("Esp", "SOLIDIFY"); so.thickness = 0.16
    for f in me.polygons: f.use_smooth = True
    for o in arm:
        mm = o.modifiers.new("Sub", "SUBSURF"); mm.levels = 1
    for o in arm + [mob]: o["lado"] = lado
    return arm + [mob]
asas = []
for s, lado in ((-1, "D"), (1, "E")):
    asas += asa(s, lado)

# ---------- aplicar e juntar (corpo+detalhes) e (asas por lado ficam no mesmo objeto final)
def aplicar_juntar(objs, nome):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active; o.name = nome
    return o
# grupos de regiao (usados pelos pesos do rig): corpo/detalhes, asa esquerda, asa direita
def marcar(o, g):
    vg = o.vertex_groups.new(name=g); vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
for o in [corpo] + det:
    bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.convert(target="MESH"); marcar(o, "REG_CORPO")
for o in asas:
    bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.convert(target="MESH"); marcar(o, "REG_ASA_" + o["lado"])
final = aplicar_juntar([corpo] + det + asas, "Dragao_das_Montanhas")
bpy.ops.object.select_all(action="DESELECT"); final.select_set(True); bpy.context.view_layer.objects.active = final
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.remove_doubles(threshold=0.001); bpy.ops.object.mode_set(mode="OBJECT")
tris = sum(len(p.vertices) - 2 for p in final.data.polygons)
print("TRIS", tris)
json.dump({"spine": spine, "legs": LEG, "asas": ASA}, open(os.path.join(OUT, "dragao_esqueleto_%s.json" % FORMA), "w"))

mat = bpy.data.materials.new("Previa"); mat.use_nodes = True
b = mat.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (0.2, 0.2, 0.21, 1); b.inputs["Roughness"].default_value = 0.85
final.data.materials.append(mat)
sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 3.5
so = bpy.data.objects.new("Sol", sun); scn.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(30))
scn.world = bpy.data.worlds.new("W"); scn.world.use_nodes = True; scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.62, 0.7, 1)
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 960; scn.render.resolution_y = 600
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 10, 0))
bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=5.2, location=(16, -18, 2.6))
def render(path, loc, target, lens=35):
    cam = bpy.data.cameras.new("Cam"); co = bpy.data.objects.new("Cam", cam); scn.collection.objects.link(co)
    co.location = loc; co.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); cam.lens = lens
    scn.camera = co; scn.render.filepath = path; bpy.ops.render.render(write_still=True)
render(os.path.join(OUT, "d2_lateral_%s.png" % FORMA), (110, 2, 24), (0, 8, 16))
render(os.path.join(OUT, "d2_tres_quartos_%s.png" % FORMA), (70, -95, 45), (0, 2, 16))
render(os.path.join(OUT, "d2_frente_%s.png" % FORMA), (0, -110, 30), (0, 0, 18))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "d2_geo_%s.blend" % FORMA))




