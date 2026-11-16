"""Lote 2 (L2a): CLOSES de revisao de qualquer acao, camera PARADA (clipe no lugar), fundo escuro, 960x720, nas tres regioes de
risco: fresta cauda x coxa E, garganta e flanco direito. Modo 'cores' (Workbench): cada vertice do corpo e do pelo pintado
pela MISTURA dos pesos por grupo de ossos - cauda laranja, perna traseira E azul, perna traseira D verde, dianteira E ciano,
dianteira D turquesa, pescoco magenta, cabeca/mandibula amarelo, coluna/quadril cinza; transicoes de peso aparecem como
degrade. Modo normal: EEVEE com a textura.
Vistas: fresta_E, fresta_baixo, garganta_E, garganta_baixo, flanco_D, flanco_D_baixo, barriga (de baixo, entre as patas).
Uso: blender -b <anim.blend> -P vistas_closes_v21.py -- <dir> <acao> <quadros i-f:p> <vistas> [cores] [pre=]"""
import bpy, sys, os, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True); ACAO = a[1]
r, _, p = a[2].partition(":"); i0, i1 = r.split("-"); QS = list(range(int(i0), int(i1) + 1, int(p or 1))); VS = a[3].split(",")
OPC = a[4:]; CORES = "cores" in OPC; PRE = next((o[4:] for o in OPC if o.startswith("pre=")), ("cores_" if CORES else "real_") + ACAO)
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; ac = bpy.data.actions[ACAO]; ARM.animation_data.action = ac
if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
CONJ = ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ
ARM.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
def cor_osso(n):
    if n.startswith("Cauda"): return (1.0, 0.45, 0.05)
    if n in ("Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E"): return (0.1, 0.35, 1.0)
    if n in ("Coxa_D", "Tibia_D", "Metatarso_D", "DedosPe_D"): return (0.1, 0.75, 0.2)
    if n.endswith("_E") and n.split("_")[0] in ("Escapula", "Umero", "Antebraco", "Metacarpo", "Dedos"): return (0.1, 0.85, 0.95)
    if n.endswith("_D") and n.split("_")[0] in ("Escapula", "Umero", "Antebraco", "Metacarpo", "Dedos"): return (0.05, 0.55, 0.5)
    if n.startswith("Pescoco"): return (0.85, 0.2, 0.75)
    if n in ("Cabeca", "Mandibula") or n.startswith(("Palpebra", "Orelha")): return (0.95, 0.85, 0.15)
    return (0.6, 0.6, 0.62)
if CORES:
    for n in CONJ:
        o = bpy.data.objects[n]
        if o.type != "MESH" or not o.vertex_groups: continue
        me = o.data; gn = {g.index: g.name for g in o.vertex_groups}; at = me.color_attributes.new("Osso", "FLOAT_COLOR", "POINT")
        for v in me.vertices:
            ws = [(gn[g.group], g.weight) for g in v.groups if g.weight > 0]; t = sum(w for _, w in ws) or 1.0
            c = [sum(cor_osso(k)[i] * w for k, w in ws) / t for i in range(3)] if ws else [0.6, 0.6, 0.62]
            at.data[v.index].color = (*c, 1)
        me.color_attributes.active_color = at
    sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "VERTEX"
    sh.show_shadows = True; sh.show_cavity = True; sh.background_type = "VIEWPORT"; sh.background_color = (0.12, 0.13, 0.15)
else:
    w_ = bpy.data.worlds.new("E"); sc.world = w_
    if w_.node_tree is None: w_.use_nodes = True
    w_.node_tree.nodes["Background"].inputs[0].default_value = (0.10, 0.11, 0.13, 1)
    for nome, en, rot in (("K", 3.2, (50, 0, 35)), ("C", 1.6, (120, 0, 205)), ("F", 1.4, (65, 0, -120)), ("B", 1.2, (100, 0, 160))):
        l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = [math.radians(x) for x in rot]
    sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32; sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 960, 720
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
CA = V((0.6, 3.0, 2.3)); GA = V((0.0, -4.2, 4.2)); FL = V((-0.7, 0.6, 3.0))
VIS = {"fresta_E": (CA + V((5.5, 2.6, 0.6)), CA, 30), "fresta_baixo": (CA + V((4.6, 1.2, -1.7)), CA + V((0, 0, 0.3)), 28),
       "garganta_E": (GA + V((5.2, -2.6, -0.4)), GA, 32), "garganta_baixo": (GA + V((2.4, -3.6, -2.6)), GA, 30),
       "flanco_D": (FL + V((-6.5, -0.6, 0.4)), FL, 30), "flanco_D_baixo": (FL + V((-4.6, -1.6, -2.2)), FL + V((0, 0, 0.2)), 28),
       "barriga": (V((-2.2, -0.6, -0.4)) + V((0, 0, 0)), V((0, -0.6, 2.6)), 24)}
for q in QS:
    sc.frame_set(q)
    for v in VS:
        pos, alvo, lens = VIS[v]; cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.lens = lens
        sc.render.filepath = os.path.join(OUT, "%s_%s_q%04d.png" % (PRE, v, q)); bpy.ops.render.render(write_still=True)
print("VISTAS_CLOSES_OK", ACAO, len(QS), VS, flush=True)
