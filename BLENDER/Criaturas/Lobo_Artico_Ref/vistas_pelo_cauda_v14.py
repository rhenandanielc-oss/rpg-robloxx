"""Renders de REVISAO do pelo da cauda x perna traseira E (v14), mais legiveis que os da v12: camera FECHADA na fresta
cauda/coxa E, fundo escuro (o pelo branco destaca), 960x720. O clipe roda NO LUGAR (sem deslocamento: a camera fica parada
e so a pata/cauda se movem).
Modo 'cores': pelo e corpo pintados pelo osso dominante de cada vertice - CAUDA = laranja, PERNA E = azul, resto = cinza
claro (Workbench, luz de estudio). Pelo laranja indo junto com a perna = defeito.
Vistas: fresta_E (lado E, um pouco atras), fresta_tras (de tras, por baixo da cauda), fresta_baixo (de baixo/lado).
Uso: blender -b <anim.blend> -P vistas_pelo_cauda_v14.py -- <dir> <quadros i-f:p> <vistas> [cores] [pre=]"""
import bpy, sys, os, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
r, _, p = a[1].partition(":"); i0, i1 = r.split("-"); QS = list(range(int(i0), int(i1) + 1, int(p or 1))); VS = a[2].split(",")
OPC = a[3:]; CORES = "cores" in OPC; PRE = next((o[4:] for o in OPC if o.startswith("pre=")), "cores" if CORES else "real")
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; ac = bpy.data.actions["Andar"]; ARM.animation_data.action = ac
if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
CONJ = ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ
ARM.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
PERNA_E = {"Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E"}
if CORES:
    for n in ("LOW_Corpo", "LOW_Pelagem"):
        o = bpy.data.objects[n]; me = o.data; gn = {g.index: g.name for g in o.vertex_groups}
        at = me.color_attributes.new("Osso", "FLOAT_COLOR", "POINT")
        for v in me.vertices:
            c = sum(g.weight for g in v.groups if gn[g.group].startswith("Cauda")); pe = sum(g.weight for g in v.groups if gn[g.group] in PERNA_E)
            base = (0.85, 0.85, 0.85) if "Pelagem" in n else (0.55, 0.55, 0.57)
            col = tuple(base[k] * (1 - c - pe) + (1.0, 0.45, 0.05)[k] * c + (0.1, 0.35, 1.0)[k] * pe for k in range(3))
            at.data[v.index].color = (*col, 1)
        me.color_attributes.active_color = at
    sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "VERTEX"
    sh.show_shadows = True; sh.show_cavity = True; sh.background_type = "VIEWPORT"; sh.background_color = (0.12, 0.13, 0.15)
    sc.render.film_transparent = False
else:
    w_ = bpy.data.worlds.new("E"); sc.world = w_
    if w_.node_tree is None: w_.use_nodes = True
    w_.node_tree.nodes["Background"].inputs[0].default_value = (0.10, 0.11, 0.13, 1)
    for nome, en, rot in (("K", 3.2, (50, 0, 35)), ("C", 1.6, (120, 0, 205)), ("F", 1.4, (65, 0, -120)), ("B", 1.2, (100, 0, 160))):
        l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = [math.radians(x) for x in rot]
    sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32; sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 960, 720
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
CA = V((0.6, 3.0, 2.3))
VIS = {"fresta_E": (CA + V((5.5, 2.6, 0.6)), CA, 30), "fresta_tras": (CA + V((2.2, 6.0, -0.6)), CA + V((0, 0, -0.2)), 28),
       "fresta_baixo": (CA + V((4.6, 1.2, -1.7)), CA + V((0, 0, 0.3)), 28)}
for q in QS:
    sc.frame_set(q)
    for v in VS:
        pos, alvo, lens = VIS[v]; cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.lens = lens
        sc.render.filepath = os.path.join(OUT, "%s_%s_q%04d.png" % (PRE, v, q)); bpy.ops.render.render(write_still=True)
print("VISTAS_PELO_OK", len(QS), VS, flush=True)
