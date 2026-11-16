"""Teste GEOMETRICO sem rig por LOD (nao e animacao validada), no .blend com grupos: igual a teste_rosto_v5.py, mas mostra
o conjunto de malhas do LOD escolhido (o mesmo de cada GLB) e gira os pesos da cabeca desse LOD.
Fases: repouso | meio (palpebras 50%, mandibula 15 graus) | maximo (100%, 32 graus). Boca: frente, perfil, 3/4, baixo;
olhos: frente, perfil, 3/4. Cameras centradas no nariz endireitado (rig_pivos: endireitar_v6.nariz_depois).
Opcoes: 'lados' (acrescenta perfil_D e 34_D, lado direito, a boca e olhos); 'arame' (wireframe sobre a cabeca); 'protecao' (so LOW: cabeca colorida pelo grupo Protecao_LOD, vermelho = protegido).
Uso: blender -b <arquivo.blend> -P teste_lod_v7.py -- <dir_saida> <LOW|LOD1|LOD2> [lados] [arame] [protecao]"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIVEL = a[1]; os.makedirs(OUT, exist_ok=True)
ARAME, PROT, LADOS = "arame" in a, "protecao" in a, "lados" in a
SRC = os.path.dirname(bpy.data.filepath); AQUI = os.path.dirname(SRC)
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"],
        "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}
sc = bpy.context.scene
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ[NIVEL]; o.hide_set(o.hide_render)
cab = bpy.data.objects[NIVEL + "_Cabeca"]; me = cab.data; pv = V(PIV["mandibula"]["pivo_sugerido"])
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
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
w_ = bpy.data.worlds.new("E"); sc.world = w_
if w_.node_tree is None: w_.use_nodes = True
w_.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.43, 0.45, 1)
for nome, en, rot in (("K", 3.0, (50, 0, 35)), ("C", 2.0, (120, 0, 205)), ("F", 1.2, (65, 0, -120)), ("B", 0.8, (150, 0, 0))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo)
    lo.rotation_euler = [math.radians(x) for x in rot]
if PROT:                                                                 # mapa de protecao: cor por vertice do grupo
    gp = cab.vertex_groups["Protecao_LOD"].index; at = me.color_attributes.new("Prot", "FLOAT_COLOR", "POINT")
    for v in me.vertices:
        w = next((e.weight for e in v.groups if e.group == gp), 1.0); at.data[v.index].color = (1.0, w, w, 1.0)
    mp = bpy.data.materials.new("Prot")
    if mp.node_tree is None: mp.use_nodes = True
    nt = mp.node_tree; ca = nt.nodes.new("ShaderNodeVertexColor"); ca.layer_name = "Prot"
    nt.links.new(ca.outputs[0], nt.nodes["Principled BSDF"].inputs["Base Color"])
    me.materials.clear(); me.materials.append(mp)
if ARAME or PROT:                                                        # arame sobre a malha (mesma geometria posada)
    wf = cab.copy(); wf.data = cab.data; wf.name = "Arame"; sc.collection.objects.link(wf); wf.hide_render = False
    m = wf.modifiers.new("W", "WIREFRAME"); m.thickness = 0.0025; m.use_replace = True; m.use_even_offset = False
    mw = bpy.data.materials.new("Arame")
    if mw.node_tree is None: mw.use_nodes = True
    mw.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
    m.material_offset = len(cab.data.materials); cab.data.materials.append(mw)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32; sc.render.resolution_x, sc.render.resolution_y = 800, 600
sc.view_settings.view_transform = "AgX"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
n0 = V(PIV.get("endireitar_v6", {}).get("nariz_depois") or json.load(open(os.path.join(AQUI, "meshy", "rosto.json")))["nariz"])
oE = V(PIV["olhos"]["E"]["centro_globo"]); oD = V(PIV["olhos"]["D"]["centro_globo"]); om = (oE + oD) / 2
VB = [("frente", n0 + V((0, -3.6, 0.15)), n0 + V((0, 0.55, -0.15)), 60), ("perfil", n0 + V((3.6, 0.55, -0.05)), n0 + V((0, 0.55, -0.15)), 60),
      ("34", n0 + V((2.5, -2.5, 0.45)), n0 + V((0, 0.55, -0.15)), 60), ("baixo", n0 + V((0.6, -1.6, -2.8)), n0 + V((0, 0.55, -0.15)), 60)]
VO = [("frente", om + V((0, -2.2, 0.15)), om, 70), ("perfil", oE + V((2.2, -0.35, 0.05)), oE, 75), ("34", om + V((1.6, -1.7, 0.4)), om, 70)]
if LADOS:
    VB += [("perfil_D", n0 + V((-3.6, 0.55, -0.05)), n0 + V((0, 0.55, -0.15)), 60), ("34_D", n0 + V((-2.5, -2.5, 0.45)), n0 + V((0, 0.55, -0.15)), 60)]
    VO += [("perfil_D", oD + V((-2.2, -0.35, 0.05)), oD, 75), ("34_D", om + V((-1.6, -1.7, 0.4)), om, 70)]
FASES = (("repouso", 0.0, 0),) if PROT else (("repouso", 0.0, 0), ("meio", 0.5, 15), ("maximo", 1.0, 32))
for fase, fo, gb in FASES:
    pose(fo, gb)
    for grupo, vistas in (("boca", VB), ("olhos", VO)):
        for nome, pos, alvo, lente in vistas:
            cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
            sc.render.filepath = os.path.join(OUT, "t_%s_%s_%s.png" % (grupo, fase, nome)); bpy.ops.render.render(write_still=True)
pose(0, 0)
print("TESTE_LOD_OK", NIVEL)
