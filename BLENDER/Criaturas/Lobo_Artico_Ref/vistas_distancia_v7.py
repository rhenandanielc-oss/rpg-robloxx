"""PROPOSTA de distancias de troca de LOD (sem medicao no Roblox): renders 1280x720 com campo de visao vertical de 70 graus
(o padrao da camera do Roblox), camera em 3/4 pela frente-esquerda, olhando o meio do lobo. Para cada distancia, o LOD
proposto ao lado do LOD0 e do LOD anterior, para julgar se a troca aparece. Distancias propostas: LOD0 ate 35 studs,
LOD1 de 35 a 80, LOD2 acima de 80. Repouso e boca aberta+olhos fechados (pesos girados como em teste_lod_v7.py).
Uso: blender -b <arquivo.blend> -P vistas_distancia_v7.py -- <dir_saida>"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"],
        "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}
sc = bpy.context.scene; pv = V(PIV["mandibula"]["pivo_sugerido"])
def pose(cab, rep, fo, gb):
    me = cab.data; gi = {g.name: g.index for g in cab.vertex_groups}
    for v, p0 in zip(me.vertices, rep): v.co = p0.copy()
    for lado, ol in PIV["olhos"].items():
        S, ax = V(ol["centro_globo"]), V(ol["eixo"])
        for nome, ang in (("Palpebra_Sup_" + lado, ol["fechar_sup_graus"]), ("Palpebra_Inf_" + lado, ol["fechar_inf_graus"])):
            g = gi.get(nome)
            for v in me.vertices:
                w = next((e.weight for e in v.groups if e.group == g), 0.0)
                if w > 0: v.co = S + Matrix.Rotation(math.radians(ang * w * fo), 3, ax) @ (v.co - S)
    g = gi.get("Mandibula")
    for v in me.vertices:
        w = next((e.weight for e in v.groups if e.group == g), 0.0)
        if w > 0: v.co = pv + Matrix.Rotation(math.radians(gb) * w, 3, V((1, 0, 0))) @ (v.co - pv)
    me.update()
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
w_ = bpy.data.worlds.new("E"); sc.world = w_
if w_.node_tree is None: w_.use_nodes = True
w_.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.62, 0.70, 1)
for nome, en, rot in (("K", 3.0, (50, 0, 35)), ("C", 1.5, (120, 0, 205))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo)
    lo.rotation_euler = [math.radians(x) for x in rot]
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0)); chao = bpy.context.active_object
mc = bpy.data.materials.new("Neve")
if mc.node_tree is None: mc.use_nodes = True
mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.82, 0.85, 0.9, 1); chao.data.materials.append(mc)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32; sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.view_settings.view_transform = "AgX"
cd = bpy.data.cameras.new("C"); cd.sensor_fit = "VERTICAL"; cd.angle_y = math.radians(70); cd.clip_end = 1000
cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
alvo = V((0, -1.0, 3.6)); dirc = V((0.75, -1.0, 0.18)).normalized()
REP = {n: [v.co.copy() for v in bpy.data.objects[n + "_Cabeca"].data.vertices] for n in CONJ}
for d, niveis in ((20, ("LOW",)), (35, ("LOW", "LOD1")), (80, ("LOD1", "LOD2")), (120, ("LOW", "LOD2"))):
    cam.location = alvo + dirc * d; cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    for n in niveis:
        for o in sc.objects:
            if o.type == "MESH" and o is not chao: o.hide_render = o.name not in CONJ[n]
        for fase, fo, gb in (("repouso", 0.0, 0), ("aberta", 1.0, 32)):
            pose(bpy.data.objects[n + "_Cabeca"], REP[n], fo, gb)
            sc.render.filepath = os.path.join(OUT, "d%03d_%s_%s.png" % (d, n, fase)); bpy.ops.render.render(write_still=True)
            pose(bpy.data.objects[n + "_Cabeca"], REP[n], 0.0, 0)
print("DISTANCIA_OK")
