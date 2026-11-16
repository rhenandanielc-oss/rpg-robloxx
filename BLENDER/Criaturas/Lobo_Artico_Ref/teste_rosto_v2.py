"""Teste GEOMETRICO sem rig da v2 (nao e animacao validada): aplica os pesos dos grupos numa copia em memoria.
Fases: repouso | meio (palpebras 50%, mandibula 15 graus) | maximo (palpebras 100%, mandibula 32 graus).
Vistas da boca: frente, perfil, 3/4, por baixo; dos olhos: frente, perfil, 3/4. Monta pranchas por fase.
Uso: blender -b low_v2/CR_LoboArtico_LOW.blend -P teste_rosto_v2.py -- <dir_saida>"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); AQUI = os.path.dirname(SRC)
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); R = json.load(open(os.path.join(AQUI, "meshy", "rosto.json")))
cab = bpy.data.objects["LOW_Cabeca"]; me = cab.data
BA, BB = PIV["mandibula"]["linha_boca"]; CANTO = PIV["mandibula"]["canto_y"]; pv = V(PIV["mandibula"]["pivo_sugerido"])
n_boca = V((0, -BB, 1)).normalized(); P0 = V((0, CANTO, BA + BB * CANTO))
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
REPOUSO = [v.co.copy() for v in me.vertices]
gi = {g.name: g.index for g in cab.vertex_groups}
pesos = [{e.group: e.weight for e in v.groups} for v in me.vertices]
# mandibula da pele: faces abaixo do plano dos labios (vertice so entra se todas as faces estao embaixo)
baixo = [False] * len(me.polygons)
for f in me.polygons:
    c = f.center; gs = set().union(*(pesos[i].keys() for i in f.vertices))
    if gi["Boca_Superior"] in gs or any(gi[k] in gs for k in gi if k.startswith("Palpebra")): continue
    if (c - P0).dot(n_boca) < 0 and c.y < CANTO + 0.35 and c.z > BA + BB * c.y - 0.30 and abs(c.x - 0.05) < 0.6: baixo[f.index] = True
vf = [[] for _ in me.vertices]
for f in me.polygons:
    for i in f.vertices: vf[i].append(f.index)
def pose(f_olho, graus_boca):
    for v, p0 in zip(me.vertices, REPOUSO): v.co = p0.copy()
    for lado, ol in PIV["olhos"].items():
        S, ax = V(ol["centro_globo"]), V(ol["eixo"])
        for nome, ang in (("Palpebra_Sup_" + lado, ol["fechar_sup_graus"]), ("Palpebra_Inf_" + lado, ol["fechar_inf_graus"])):
            g = gi[nome]
            for v in me.vertices:
                w = pesos[v.index].get(g, 0.0)
                if w > 0: v.co = S + Matrix.Rotation(math.radians(ang * w * f_olho), 3, ax) @ (v.co - S)
    gb = math.radians(graus_boca)
    for v in me.vertices:
        w = pesos[v.index].get(gi["Boca_Inferior"], 0.0)
        if w == 0 and vf[v.index] and all(baixo[k] for k in vf[v.index]): w = suave((CANTO + 0.35 - v.co.y) / 0.35)
        if w > 0: v.co = pv + Matrix.Rotation(gb * w, 3, V((1, 0, 0))) @ (v.co - pv)
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
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32; sc.render.resolution_x, sc.render.resolution_y = 800, 600
sc.view_settings.view_transform = "AgX"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
n0 = V(R["nariz"]); oE = V(PIV["olhos"]["E"]["centro_globo"]); oD = V(PIV["olhos"]["D"]["centro_globo"]); om = (oE + oD) / 2
VB = [("frente", n0 + V((0, -3.6, 0.15)), n0 + V((0, 0.55, -0.15)), 60), ("perfil", n0 + V((3.6, 0.55, -0.05)), n0 + V((0, 0.55, -0.15)), 60),
      ("34", n0 + V((2.5, -2.5, 0.45)), n0 + V((0, 0.55, -0.15)), 60), ("baixo", n0 + V((0.6, -1.6, -2.8)), n0 + V((0, 0.55, -0.15)), 60)]
VO = [("frente", om + V((0, -2.2, 0.15)), om, 70), ("perfil", oE + V((2.2, -0.35, 0.05)), oE, 75), ("34", om + V((1.6, -1.7, 0.4)), om, 70)]
FASES = (("repouso", 0.0, 0), ("meio", 0.5, 15), ("maximo", 1.0, 32))
for fase, fo, gb in FASES:
    pose(fo, gb)
    for grupo, vistas in (("boca", VB), ("olhos", VO)):
        for nome, pos, alvo, lente in vistas:
            cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
            sc.render.filepath = os.path.join(OUT, "t_%s_%s_%s.png" % (grupo, fase, nome)); bpy.ops.render.render(write_still=True)
pose(0, 0)
print("TESTE_V2_OK")
