"""Teste GEOMETRICO sem rig da v5 (nao e animacao validada): aplica SO os pesos gravados nos grupos (Palpebra_*, Mandibula),
como um rig faria, numa copia em memoria. Fases: repouso | meio (palpebras 50%, mandibula 15 graus) | maximo (100%, 32 graus).
Vistas da boca: frente, perfil, 3/4, por baixo; dos olhos: frente, perfil, 3/4. Opcional 'arame': sobrepoe o wireframe.
Uso: blender -b <arquivo.blend> -P teste_rosto_v5.py -- <dir_saida> [arame]"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True); ARAME = "arame" in a
SRC = os.path.dirname(bpy.data.filepath); AQUI = os.path.dirname(SRC)
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); R = json.load(open(os.path.join(AQUI, "meshy", "rosto.json")))
cab = bpy.data.objects["LOW_Cabeca"]; me = cab.data; pv = V(PIV["mandibula"]["pivo_sugerido"])
REP = [v.co.copy() for v in me.vertices]; gi = {g.name: g.index for g in cab.vertex_groups}
pesos = [{e.group: e.weight for e in v.groups} for v in me.vertices]
def pose(fo, gb):
    for v, p0 in zip(me.vertices, REP): v.co = p0.copy()
    for lado, ol in PIV["olhos"].items():
        S, ax = V(ol["centro_globo"]), V(ol["eixo"])
        for nome, ang in (("Palpebra_Sup_" + lado, ol["fechar_sup_graus"]), ("Palpebra_Inf_" + lado, ol["fechar_inf_graus"])):
            g = gi.get(nome)
            for v in me.vertices:
                w = pesos[v.index].get(g, 0.0)
                if w > 0: v.co = S + Matrix.Rotation(math.radians(ang * w * fo), 3, ax) @ (v.co - S)
    g = gi.get("Mandibula")
    for v in me.vertices:
        w = pesos[v.index].get(g, 0.0)
        if w > 0: v.co = pv + Matrix.Rotation(math.radians(gb) * w, 3, V((1, 0, 0))) @ (v.co - pv)
    me.update()
sc = bpy.context.scene
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
w_ = bpy.data.worlds.new("E"); sc.world = w_
if w_.node_tree is None: w_.use_nodes = True
w_.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.43, 0.45, 1)
for nome, en, rot in (("K", 3.0, (50, 0, 35)), ("C", 2.0, (120, 0, 205)), ("F", 1.2, (65, 0, -120)), ("B", 0.8, (150, 0, 0))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo)
    lo.rotation_euler = [math.radians(x) for x in rot]
if ARAME:                                                                # arame sobre a malha (mesma geometria posada)
    wf = cab.copy(); wf.data = cab.data; wf.name = "Arame"; sc.collection.objects.link(wf)
    m = wf.modifiers.new("W", "WIREFRAME"); m.thickness = 0.0025; m.use_replace = True; m.use_even_offset = False
    mw = bpy.data.materials.new("Arame")
    if mw.node_tree is None: mw.use_nodes = True
    mw.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
    wf.data.materials.clear() if False else None
    m.material_offset = len(cab.data.materials); cab.data.materials.append(mw)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32; sc.render.resolution_x, sc.render.resolution_y = 800, 600
sc.view_settings.view_transform = "AgX"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
n0 = V(R["nariz"]); oE = V(PIV["olhos"]["E"]["centro_globo"]); oD = V(PIV["olhos"]["D"]["centro_globo"]); om = (oE + oD) / 2
VB = [("frente", n0 + V((0, -3.6, 0.15)), n0 + V((0, 0.55, -0.15)), 60), ("perfil", n0 + V((3.6, 0.55, -0.05)), n0 + V((0, 0.55, -0.15)), 60),
      ("34", n0 + V((2.5, -2.5, 0.45)), n0 + V((0, 0.55, -0.15)), 60), ("baixo", n0 + V((0.6, -1.6, -2.8)), n0 + V((0, 0.55, -0.15)), 60)]
VO = [("frente", om + V((0, -2.2, 0.15)), om, 70), ("perfil", oE + V((2.2, -0.35, 0.05)), oE, 75), ("34", om + V((1.6, -1.7, 0.4)), om, 70)]
for fase, fo, gb in (("repouso", 0.0, 0), ("meio", 0.5, 15), ("maximo", 1.0, 32)):
    pose(fo, gb)
    for grupo, vistas in (("boca", VB), ("olhos", VO)):
        for nome, pos, alvo, lente in vistas:
            cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
            sc.render.filepath = os.path.join(OUT, "t_%s_%s_%s.png" % (grupo, fase, nome)); bpy.ops.render.render(write_still=True)
pose(0, 0)
print("TESTE_V5_OK")
