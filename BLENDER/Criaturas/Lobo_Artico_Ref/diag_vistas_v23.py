"""v23 (copia da diag_vistas_v22 + modo 'dobras' e vistas de corpo inteiro): vistas de REVISAO do flanco direito e do ventre,
camera PARADA (clipe no lugar), 960x720, fundo escuro. Mesmas cameras para v21 / v22 / v23.
Modos:
- real: EEVEE com textura e cartoes; sempelo: idem sem cartoes de pelo;
- wire: Workbench sem pelo, pele cinza com ARAME preto (copia avaliada da pele com modificador Wireframe depois do Armature);
- pesos: Workbench sem pelo, cor = mistura dos pesos: Coxa_D vermelho, Tibia_D amarelo, Metatarso_D laranja, Coluna1 azul,
  Coluna2 ciano, Coluna3 azul-claro, Quadril violeta, Coxa_E verde, Tibia_E verde-claro, Umero_D/E rosa, resto cinza.
- dobras: Workbench sem pelo, pele cinza; faces DOBRADAS no quadro (normal posada oposta a media das vizinhas, que no repouso
  concordavam) em VERMELHO e a regiao retopologizada (atributo retopo_v23) em azul-claro.
Vistas: barriga (de baixo), flanco_D, flanco_D_baixo, virilha_D (de tras/baixo para a virilha direita), tras_baixo, perfil_D;
corpo inteiro: c_perfil_D, c_perfil_E, c_34_D (tres-quartos dianteiro D), c_tras (traseira), c_baixo.
Uso: blender -b <anim.blend> -P diag_vistas_v22.py -- <dir> <acao|repouso> <quadros i-f:p> <vistas> <modo> [LOD] [pre=]"""
import bpy, sys, os, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True); ACAO = a[1]
r, _, p = a[2].partition(":"); i0, i1 = r.split("-"); QS = list(range(int(i0), int(i1) + 1, int(p or 1))); VS = a[3].split(","); MODO = a[4]
L = a[5] if len(a) > 5 and not a[5].startswith("pre=") else "LOW"; PRE = next((o[4:] for o in a[5:] if o.startswith("pre=")), "%s_%s_%s" % (MODO, L, ACAO))
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]
if ACAO == "repouso":
    ARM.animation_data.action = None
    for pb in ARM.pose.bones: pb.matrix_basis.identity()
else:
    ac = bpy.data.actions[ACAO]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"], "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem", "LOW_Marca", "LOW_Cristais"],
        "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}[L]
if MODO in ("sempelo", "wire", "pesos", "dobras"): CONJ = [n for n in CONJ if "Pelagem" not in n]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ
ARM.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
COR = {"Coxa_D": (0.95, 0.1, 0.1), "Tibia_D": (1.0, 0.9, 0.1), "Metatarso_D": (1.0, 0.55, 0.1), "Coluna1": (0.15, 0.3, 1.0), "Coluna2": (0.1, 0.85, 0.95),
       "Coluna3": (0.55, 0.75, 1.0), "Quadril": (0.6, 0.25, 0.85), "Coxa_E": (0.1, 0.7, 0.2), "Tibia_E": (0.55, 0.95, 0.5), "Umero_D": (1.0, 0.5, 0.75), "Umero_E": (1.0, 0.5, 0.75)}
if MODO in ("wire", "pesos", "dobras"):
    for n in CONJ:
        o = bpy.data.objects[n]
        if o.type != "MESH": continue
        me = o.data; gn = {g.index: g.name for g in o.vertex_groups}; at = me.color_attributes.new("Diag", "FLOAT_COLOR", "POINT")
        for v in me.vertices:
            if MODO in ("wire", "dobras"): c = (0.72, 0.72, 0.74)
            else:
                ws = [(gn[g.group], g.weight) for g in v.groups if g.weight > 0]; t = sum(w for _, w in ws) or 1.0
                c = tuple(sum(COR.get(k, (0.55, 0.55, 0.57))[i] * w for k, w in ws) / t for i in range(3)) if ws else (0.55, 0.55, 0.57)
            at.data[v.index].color = (*c, 1)
        me.color_attributes.active_color = at
    if MODO == "wire":
        c = bpy.data.objects[L + "_Corpo"]; w = c.copy(); w.data = c.data.copy(); sc.collection.objects.link(w); w.name = "ARAME"
        mo = w.modifiers.new("Arame", "WIREFRAME"); mo.thickness = 0.006; mo.use_replace = True; mo.use_even_offset = False
        at = w.data.color_attributes.active_color
        for i in range(len(at.data)): at.data[i].color = (0.02, 0.02, 0.02, 1)
        w.hide_render = False
    if MODO == "dobras":
        import numpy as np
        C_ = bpy.data.objects[L + "_Corpo"]; me_ = C_.data; AT = me_.color_attributes.new("Dobra", "FLOAT_COLOR", "CORNER"); me_.color_attributes.active_color = AT
        F_ = [list(p.vertices) for p in me_.polygons]; LI = [list(p.loop_indices) for p in me_.polygons]
        VIZ = [[] for _ in F_]; ef = {}
        for k, p in enumerate(me_.polygons):
            for e in p.edge_keys: ef.setdefault(e, []).append(k)
        for fs in ef.values():
            for k in fs: VIZ[k] += [j for j in fs if j != k]
        RT = me_.attributes.get("retopo_v23")
        def normais(P):
            n = np.array([np.cross(P[f[1]] - P[f[0]], P[f[2]] - P[f[0]]) for f in F_]); return n / np.maximum(np.linalg.norm(n, axis=1), 1e-12)[:, None]
        N0_ = normais(np.array([v.co[:] for v in me_.vertices]))
        BASE0 = [float(np.dot(N0_[k], N0_[VIZ[k]].mean(0))) if VIZ[k] else 1.0 for k in range(len(F_))]
        def pinta_dobras():
            dg = bpy.context.evaluated_depsgraph_get(); e = C_.evaluated_get(dg); m = e.to_mesh(); P = np.array([v.co[:] for v in m.vertices]); e.to_mesh_clear()
            N = normais(P); nd = 0
            for k in range(len(F_)):
                d = float(np.dot(N[k], N[VIZ[k]].mean(0))) if VIZ[k] else 1.0
                dob = d < 0 and BASE0[k] > 0.3; nd += dob
                c = (0.95, 0.08, 0.08, 1) if dob else ((0.55, 0.75, 0.95, 1) if RT and RT.data[k].value else (0.72, 0.72, 0.74, 1))
                for li in LI[k]: AT.data[li].color = c
            me_.update(); return nd
    sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "VERTEX"
    sh.show_shadows = False; sh.show_cavity = False; sh.background_type = "VIEWPORT"; sh.background_color = (0.12, 0.13, 0.15)
else:
    w_ = bpy.data.worlds.new("E"); sc.world = w_
    if w_.node_tree is None: w_.use_nodes = True
    w_.node_tree.nodes["Background"].inputs[0].default_value = (0.10, 0.11, 0.13, 1)
    for nome, en, rot in (("K", 3.2, (50, 0, 35)), ("C", 1.6, (120, 0, 205)), ("F", 1.4, (65, 0, -120)), ("B", 1.6, (160, 0, 120))):
        l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = [math.radians(x) for x in rot]
    sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 32; sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 960, 720
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
FL = V((-0.7, 0.6, 3.0)); BA = V((0, -0.3, 2.6)); VI = V((-0.8, 0.9, 2.9))
VIS = {"barriga": (V((-2.2, -0.6, -0.4)), V((0, -0.6, 2.6)), 24), "flanco_D": (FL + V((-6.5, -0.6, 0.4)), FL, 30),
       "flanco_D_baixo": (FL + V((-4.6, -1.6, -2.2)), FL + V((0, 0, 0.2)), 28), "virilha_D": (VI + V((-1.6, 4.2, -2.4)), VI, 30),
       "tras_baixo": (V((-0.4, 7.5, 0.8)), V((-0.4, 0.8, 2.6)), 30), "perfil_D": (V((-18, -0.6, 3.4)), V((0, -0.6, 3.2)), 32),
       "c_perfil_D": (V((-13, 0.3, 4.2)), V((0, 0.3, 3.9)), 30), "c_perfil_E": (V((13, 0.3, 4.2)), V((0, 0.3, 3.9)), 30),
       "c_34_D": (V((-9.5, -8.5, 6.5)), V((0, 0.2, 3.7)), 30), "c_tras": (V((-0.8, 12.5, 5.0)), V((0, 0.5, 3.6)), 30),
       "c_baixo": (V((-5.5, 0.3, -4.0)), V((0, 0.3, 3.0)), 24)}
for q in QS:
    sc.frame_set(q)
    if MODO == "dobras": print("DOBRAS", ACAO, L, q, pinta_dobras(), flush=True)
    for v in VS:
        pos, alvo, lens = VIS[v]; cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.lens = lens
        sc.render.filepath = os.path.join(OUT, "%s_%s_q%04d.png" % (PRE, v, q)); bpy.ops.render.render(write_still=True)
print("DIAG_VISTAS_OK", ACAO, MODO, L, len(QS), VS, flush=True)
