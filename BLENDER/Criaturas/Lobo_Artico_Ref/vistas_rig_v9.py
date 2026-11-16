"""Renders COM O RIG REAL (armature deformando as malhas; nenhum vertice girado por script) do Lobo Artico v9.
Para cada quadro da acao ativa e cada vista grava <dir>/<prefixo>_<vista>_q<NNNN>.png e um JSON com a projecao 2D
(pixels) da cabeca/cauda de cada osso posado, para prancha_rig_v9.py desenhar a hierarquia por cima.
Opcoes: 'raiox' (Workbench translucido, para ver os ossos dentro da malha), 'arame' (wireframe sobre a cabeca),
'acao=<nome>' (outra acao), 'res=LxA'.
Uso: blender -b <rig.blend> -P vistas_rig_v9.py -- <dir> <LOW|LOD1|LOD2> <quadros: 0 | 0,40,80 | 0-544:4> <vistas,separadas> [opcoes]"""
import bpy, sys, os, json, math
from mathutils import Vector as V
from bpy_extras.object_utils import world_to_camera_view
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIVEL = a[1]; os.makedirs(OUT, exist_ok=True)
def quadros(s):
    if "-" in s:
        r, _, p = s.partition(":"); i, f = r.split("-"); return list(range(int(i), int(f) + 1, int(p or 1)))
    return [int(q) for q in s.split(",")]
QS = quadros(a[2]); VISTAS = a[3].split(","); OPC = a[4:]
RAIOX, ARAME = "raiox" in OPC, "arame" in OPC
RES = next((tuple(int(c) for c in o[4:].split("x")) for o in OPC if o.startswith("res=")), (800, 600))
sc = bpy.context.scene; SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"],
        "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}
if RAIOX: CONJ = {k: [n for n in v if "Cabeca" in n or "Corpo" in n] for k, v in CONJ.items()}
ARM = bpy.data.objects.get("LoboArtico_Rig")                             # None: .blend sem rig (v8), so para comparar o repouso
ac = next((o[5:] for o in OPC if o.startswith("acao=")), None)
if ac and ARM:
    ARM.animation_data_create(); ARM.animation_data.action = bpy.data.actions[ac]
    if ARM.animation_data.action_slot is None and len(bpy.data.actions[ac].slots): ARM.animation_data.action_slot = bpy.data.actions[ac].slots[0]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ[NIVEL]; o.hide_viewport = False
if ARM: ARM.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
w_ = bpy.data.worlds.new("E"); sc.world = w_
if w_.node_tree is None: w_.use_nodes = True
w_.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.43, 0.45, 1)
for nome, en, rot in (("K", 3.0, (50, 0, 35)), ("C", 2.0, (120, 0, 205)), ("F", 1.2, (65, 0, -120)), ("B", 0.8, (150, 0, 0))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo)
    lo.rotation_euler = [math.radians(x) for x in rot]
if RAIOX:
    sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.show_xray = True; sh.xray_alpha = 0.30; sh.color_type = "SINGLE"; sh.single_color = (0.85, 0.85, 0.85)
else:
    sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 24; sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = RES
if ARAME:
    for nm in CONJ[NIVEL]:
        if "Cabeca" not in nm: continue
        cab = bpy.data.objects[nm]; wf = cab.copy(); wf.data = cab.data; wf.name = "Arame"; sc.collection.objects.link(wf); wf.hide_render = False
        m = wf.modifiers.new("W", "WIREFRAME"); m.thickness = 0.0025; m.use_replace = True; m.use_even_offset = False
        mw = bpy.data.materials.new("Arame")
        if mw.node_tree is None: mw.use_nodes = True
        mw.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
        m.material_offset = len(cab.data.materials); cab.data.materials.append(mw)
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
n0 = V(PIV["endireitar_v6"]["nariz_depois"]); kE = V(PIV["canto_v8"]["E"]["canto_K"]); kD = V(PIV["canto_v8"]["D"]["canto_K"])
oE = V(PIV["olhos"]["E"]["centro_globo"]); oD = V(PIV["olhos"]["D"]["centro_globo"]); om = (oE + oD) / 2; CPt = V(PIV["costura"]["ponto"])
C0 = V((0, -0.6, 3.4))
# vistas: (posicao, alvo, lente | ('orto', escala)); 'segue' = acompanha o osso Cabeca posado (closes do rosto)
VS = {"frente": (C0 + V((0, -24, 1.2)), C0, ("orto", 9.5)), "tras": (C0 + V((0, 24, 1.2)), C0, ("orto", 9.5)),
      "lado_E": (C0 + V((24, 0, 0.6)), C0, ("orto", 14.5)), "lado_D": (C0 + V((-24, 0, 0.6)), C0, ("orto", 14.5)),
      "topo": (C0 + V((0, 0, 24)), C0, ("orto", 14.5)),
      "34_E": (C0 + V((12, -12, 5)), C0, 52), "34_D": (C0 + V((-12, -12, 5)), C0, 52), "34_tras": (C0 + V((-11, 12, 6)), C0, 52),
      "canto_E": (kE + V((1.3, -0.35, 0.05)), kE + V((0, 0.05, -0.12)), 50, "segue"), "canto_D": (kD + V((-1.3, -0.35, 0.05)), kD + V((0, 0.05, -0.12)), 50, "segue"),
      "boca_34": (n0 + V((2.5, -2.5, 0.45)), n0 + V((0, 0.55, -0.15)), 60, "segue"), "boca_baixo": (n0 + V((0.6, -1.6, -2.8)), n0 + V((0, 0.55, -0.15)), 60, "segue"),
      "olhos": (om + V((0, -2.2, 0.15)), om, 70, "segue"), "olho_E": (oE + V((2.2, -0.35, 0.05)), oE, 75, "segue"), "olho_D": (oD + V((-2.2, -0.35, 0.05)), oD, 75, "segue"),
      "costura_E": (CPt + V((3.2, -0.4, 0.9)), CPt + V((0, 0.2, 0.7)), 45), "costura_D": (CPt + V((-3.2, -0.4, 0.9)), CPt + V((0, 0.2, 0.7)), 45),
      "costura_baixo": (CPt + V((1.2, -0.6, -3.2)), CPt + V((0, 0.2, 0.3)), 45),
      "patas": (V((0, -0.6, 0.6)) + V((7, -7, 1.2)), V((0, -0.6, 0.6)), 35)}
def mira(vista):
    d = VS[vista]; pos, alvo = V(d[0]), V(d[1])
    if len(d) > 3 and d[3] == "segue" and ARM:                                  # close do rosto: camera presa ao osso Cabeca
        pb = ARM.pose.bones["Cabeca"]; M = ARM.matrix_world @ pb.matrix @ pb.bone.matrix_local.inverted()
        pos, alvo = M @ pos, M @ alvo
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
    if isinstance(d[2], tuple): cd.type = "ORTHO"; cd.ortho_scale = d[2][1]
    else: cd.type = "PERSP"; cd.lens = d[2]
PRE = next((o[4:] for o in OPC if o.startswith("pre=")), NIVEL)
proj = {}
for q in QS:
    sc.frame_set(q); bpy.context.view_layer.update()
    for vista in VISTAS:
        mira(vista); bpy.context.view_layer.update()
        nome = "%s_%s_q%04d" % (PRE, vista, q); sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
        ossos = {}
        for pb in (ARM.pose.bones if ARM else []):
            h = world_to_camera_view(sc, cam, ARM.matrix_world @ pb.head); t = world_to_camera_view(sc, cam, ARM.matrix_world @ pb.tail)
            ossos[pb.name] = [[h.x * RES[0], (1 - h.y) * RES[1], h.z], [t.x * RES[0], (1 - t.y) * RES[1], t.z], pb.parent.name if pb.parent else None]
        proj[nome] = ossos
json.dump(proj, open(os.path.join(OUT, "ossos_%s_%s.json" % (PRE, "_".join(VISTAS)[:60])), "w"))
print("VISTAS_RIG_OK", NIVEL, len(QS), VISTAS, flush=True)
