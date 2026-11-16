"""Sequencia CONTINUA de abrir/fechar a boca (teste geometrico sem rig, pesos girados como em teste_lod_v7.py): mandibula
0 -> 32 -> 0 graus em 13 quadros (curva suave), por LOD, camera de 3/4 do lado E e lateral do canto D.
Saida: <dir>/<LOD>/q_<vista>_<NN>.png. A montagem em GIF/tira e feita por prancha_v8.py.
Uso: blender -b <arquivo.blend> -P sequencia_v8.py -- <dir_saida>"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"],
        "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}
sc = bpy.context.scene; pv = V(PIV["mandibula"]["pivo_sugerido"])
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
w_ = bpy.data.worlds.new("E"); sc.world = w_
if w_.node_tree is None: w_.use_nodes = True
w_.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.43, 0.45, 1)
for nome, en, rot in (("K", 3.0, (50, 0, 35)), ("C", 2.0, (120, 0, 205)), ("F", 1.2, (65, 0, -120)), ("B", 0.8, (150, 0, 0))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo)
    lo.rotation_euler = [math.radians(x) for x in rot]
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 24; sc.render.resolution_x, sc.render.resolution_y = 640, 480
sc.view_settings.view_transform = "AgX"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
n0 = V(PIV.get("endireitar_v6", {}).get("nariz_depois") or (0, -6.66, 5.37))
kE = V(PIV.get("canto_v8", {}).get("E", {}).get("canto_K") or (0.34, -5.81, 5.30)); kD = V(PIV.get("canto_v8", {}).get("D", {}).get("canto_K") or (-0.31, -5.74, 5.29))
VISTAS = [("34_E", n0 + V((2.5, -2.5, 0.45)), n0 + V((0, 0.55, -0.15)), 60), ("canto_D", kD + V((-1.3, -0.35, 0.05)), kD + V((0, 0.05, -0.12)), 50)]
ANG = [32 * (1 - math.cos(math.pi * 2 * k / 12)) / 2 for k in range(13)]
for L, nomes in CONJ.items():
    for o in sc.objects:
        if o.type == "MESH": o.hide_render = o.name not in nomes
    cab = bpy.data.objects[L + "_Cabeca"]; me = cab.data; g = cab.vertex_groups["Mandibula"].index
    rep = [v.co.copy() for v in me.vertices]; W = [next((e.weight for e in v.groups if e.group == g), 0.0) for v in me.vertices]
    os.makedirs(os.path.join(OUT, L), exist_ok=True)
    for k, ang in enumerate(ANG):
        for v, p0, w in zip(me.vertices, rep, W):
            v.co = pv + Matrix.Rotation(math.radians(ang) * w, 3, V((1, 0, 0))) @ (p0 - pv) if w > 0 else p0
        me.update()
        for nome, pos, alvo, lente in VISTAS:
            cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
            sc.render.filepath = os.path.join(OUT, L, "q_%s_%02d.png" % (nome, k)); bpy.ops.render.render(write_still=True)
    for v, p0 in zip(me.vertices, rep): v.co = p0
    me.update()
print("SEQUENCIA_OK")
