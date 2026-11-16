"""Vistas ORTOGRAFICAS de conferencia de simetria/alinhamento (repouso, sem rig) com linha central x=0 em vermelho
e grade de 0,5 stud no fundo. Corpo inteiro: frente, tras, topo, baixo, lado E, lado D. Cabeca: frente, topo, baixo, tras.
Tambem mede a assimetria: cada vertice espelhado (x->-x) contra a malha original (KDTree) -> simetria.json.
Uso: blender -b <arquivo.blend> -P vistas_simetria_v5.py -- <dir_saida>"""
import bpy, sys, os, json, math, bmesh
from mathutils import Vector as V
from mathutils.kdtree import KDTree
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); AQUI = os.path.dirname(SRC)
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); R = json.load(open(os.path.join(AQUI, "meshy", "rosto.json")))
sc = bpy.context.scene
malhas = [o for o in sc.objects if o.type == "MESH" and o.visible_get()]
# --- medida de assimetria por malha (coordenadas de mundo) ---
med = {}
for o in malhas:
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    if len(vs) < 10: continue
    kd = KDTree(len(vs))
    for i, p in enumerate(vs): kd.insert(p, i)
    kd.balance()
    ds = sorted(kd.find(V((-p.x, p.y, p.z)))[2] for p in vs)
    xs = [p.x for p in vs]
    med[o.name] = {"vertices": len(vs), "media": round(sum(ds) / len(ds), 4), "p95": round(ds[int(len(ds) * 0.95)], 4),
                   "max": round(ds[-1], 4), "x_min": round(min(xs), 3), "x_max": round(max(xs), 3),
                   "centro_bbox_x": round((min(xs) + max(xs)) / 2, 4)}
oE = V(PIV["olhos"]["E"]["centro_globo"]); oD = V(PIV["olhos"]["D"]["centro_globo"])
med["olhos"] = {"E": [round(c, 4) for c in oE], "D": [round(c, 4) for c in oD], "meio_x": round((oE.x + oD.x) / 2, 4),
                "dif_altura_z": round(oE.z - oD.z, 4), "dif_frente_y": round(oE.y - oD.y, 4)}
med["nariz_x"] = round(R["nariz"][0], 4)
json.dump(med, open(os.path.join(OUT, "simetria.json"), "w"), indent=1)
# --- cena ---
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
w_ = bpy.data.worlds.new("E"); sc.world = w_
if w_.node_tree is None: w_.use_nodes = True
w_.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.43, 0.45, 1)
for nome, en, rot in (("K", 3.0, (50, 0, 35)), ("C", 2.0, (120, 0, 205)), ("F", 1.2, (65, 0, -120)), ("B", 0.8, (150, 0, 0))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo)
    lo.rotation_euler = [math.radians(x) for x in rot]
def emissivo(nome, cor):
    m = bpy.data.materials.new(nome)
    if m.node_tree is None: m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear(); e = nt.nodes.new("ShaderNodeEmission"); e.inputs[0].default_value = cor + (1,)
    s = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs[0], s.inputs[0]); return m
def barra(nome, p0, p1, esp, mat):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(nome, me); sc.collection.objects.link(o); o.location = (V(p0) + V(p1)) / 2
    d = V(p1) - V(p0); o.scale = (max(abs(d.x), esp), max(abs(d.y), esp), max(abs(d.z), esp)); me.materials.append(mat); return o
vermelho = emissivo("Linha", (1.0, 0.05, 0.05)); amarelo = emissivo("Olhos", (1.0, 0.85, 0.0))
# linha central x=0: um plano fino vertical (y-z) que aparece na frente/tras/topo/baixo como risco
barra("Centro_XZ", (0, -9, -0.5), (0, -9, 9), 0.012, vermelho)          # na frente (y bem negativo, antes do focinho)
barra("Centro_XZ_tras", (0, 9, -0.5), (0, 9, 9), 0.012, vermelho)
barra("Centro_XY_topo", (0, -9, 9.5), (0, 9, 9.5), 0.012, vermelho)
barra("Centro_XY_baixo", (0, -9, -0.6), (0, 9, -0.6), 0.012, vermelho)
barra("Olhos_nivel", (-1.2, -9, oE.z), (1.2, -9, oE.z), 0.008, amarelo)  # linha horizontal na altura do olho E
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32; sc.view_settings.view_transform = "AgX"
cd = bpy.data.cameras.new("C"); cd.type = "ORTHO"; cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
cd.clip_end = 100
mn = V((min(min((o.matrix_world @ V(c)).x for c in o.bound_box) for o in malhas), min(min((o.matrix_world @ V(c)).y for c in o.bound_box) for o in malhas),
        min(min((o.matrix_world @ V(c)).z for c in o.bound_box) for o in malhas)))
mx = V((max(max((o.matrix_world @ V(c)).x for c in o.bound_box) for o in malhas), max(max((o.matrix_world @ V(c)).y for c in o.bound_box) for o in malhas),
        max(max((o.matrix_world @ V(c)).z for c in o.bound_box) for o in malhas)))
cz = (mn.z + mx.z) / 2; cy = (mn.y + mx.y) / 2; n0 = V(R["nariz"]); hc = V((0, n0.y + 0.9, (oE.z + n0.z) / 2))
# (nome, posicao, alvo, escala_ortho, resolucao, up)
C = [("corpo_frente", V((0, -20, cz)), V((0, 0, cz)), 1.15 * max(mx.z - mn.z, 2 * mx.x), (900, 900)),
     ("corpo_tras", V((0, 20, cz)), V((0, 0, cz)), 1.15 * max(mx.z - mn.z, 2 * mx.x), (900, 900)),
     ("corpo_topo", V((0, cy, 30)), V((0, cy, 0)), 1.1 * (mx.y - mn.y), (700, 1000)),
     ("corpo_baixo", V((0, cy, -30)), V((0, cy, 0)), 1.1 * (mx.y - mn.y), (700, 1000)),
     ("corpo_lado_E", V((20, cy, cz)), V((0, cy, cz)), 1.1 * (mx.y - mn.y), (1200, 800)),
     ("corpo_lado_D", V((-20, cy, cz)), V((0, cy, cz)), 1.1 * (mx.y - mn.y), (1200, 800)),
     ("cabeca_frente", V((0, -20, hc.z)), V((0, 0, hc.z)), 3.0, (900, 900)),
     ("cabeca_topo", V((0, hc.y, 30)), V((0, hc.y, 0)), 3.4, (800, 1000)),
     ("cabeca_baixo", V((0, hc.y, -30)), V((0, hc.y, 0)), 3.4, (800, 1000))]
for nome, pos, alvo, esc, (rx, ry) in C:
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.ortho_scale = esc
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    sc.render.filepath = os.path.join(OUT, "o_%s.png" % nome); bpy.ops.render.render(write_still=True)
print("SIMETRIA_OK", json.dumps(med))
