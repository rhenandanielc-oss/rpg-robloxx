"""Closes da regiao cauda x pata traseira COM O RIG REAL (quadros da acao Teste_Piloto), por LOD.
Modos: 'pescoco' (v11: pesos do pescoco na cabeca+corpo, + arame) | 'tampa' (tampas da v10: vermelho = cauda, verde = pata; + arame) | 'classe' (corpo sem pelo, cor por s = d_pata - d_cauda: vermelho = cauda, verde = pata, amarelo = faixa |s|<0,15,
azul = resto; + arame) | 'pesos' (corpo sem pelo: vermelho = Cauda*, verde = pata traseira E/D, azul = outros; + arame) |
'textura' (materiais; 'sempelo' tira os cartoes). Vistas: tras_cauda, lado_E_cauda, lado_D_cauda, interno_E (corte em
x = -0,3 pelo plano de recorte da camera: mostra a face interna da cauda e do jarrete esquerdo), interno_D (corte em x = 0,3),
baixo_cauda, 34_tras_E. Uso: blender -b <rig.blend> -P vistas_cauda_v10.py -- <dir> <LOD> <modo> <quadros a,b,c> <vistas> [sempelo] [pre=]"""
import bpy, sys, os, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); L, MODO = a[1], a[2]; QS = [int(q) for q in a[3].split(",")]; VS = a[4].split(",")
SEMPELO = "sempelo" in a or MODO != "textura"; PRE = next((x[4:] for x in a if x.startswith("pre=")), "%s_%s" % (L, MODO + ("_sempelo" if SEMPELO and MODO == "textura" else "")))
os.makedirs(OUT, exist_ok=True); sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]; B = ARM.data.bones
CONJ = {"LOW": ["LOW_Corpo", "LOW_Pelagem", "LOW_Cabeca", "LOW_Marca", "LOW_Cristais"], "LOD1": ["LOD1_Corpo", "LOD1_Pelagem", "LOD1_Cabeca", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Corpo", "LOD2_Cabeca", "LOW_Cristais"]}[L]
if SEMPELO: CONJ = [n for n in CONJ if "Pelagem" not in n]
if MODO in ("classe", "pesos", "tampa", "pescoco"): CONJ = [n for n in CONJ if "Marca" not in n and "Cristais" not in n]
CORPO = bpy.data.objects[L + "_Corpo"]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ; o.hide_viewport = False
ARM.hide_render = True
def dseg(p, h, t):
    ab = t - h; u = max(0.0, min(1.0, (p - h).dot(ab) / ab.length_squared)); return (p - (h + ab * u)).length
CA = [(B[n].head_local, B[n].tail_local) for n in ("Cauda1", "Cauda2", "Cauda3", "Cauda4")]
PT = {l: [(B[n + "_" + l].head_local, B[n + "_" + l].tail_local) for n in ("Coxa", "Tibia", "Metatarso", "DedosPe")] for l in "ED"}
if MODO == "pescoco":                                                   # v11: pesos do pescoco em cabeca + corpo (+ arame)
    for nm in [n for n in CONJ if "Pelagem" not in n]:
        o = bpy.data.objects[nm]; me = o.data; gn = {g.index: g.name for g in o.vertex_groups}; at = me.color_attributes.new("Diag", "FLOAT_COLOR", "POINT")
        for v in me.vertices:
            w = {gn[e.group]: e.weight for e in v.groups}
            r_ = w.get("Pescoco2", 0) + 0.5 * w.get("Cabeca", 0) + w.get("Mandibula", 0) * 0.3; g_ = w.get("Coluna3", 0) + w.get("Pescoco1", 0) * 0.6 + w.get("Coluna2", 0)
            b_ = sum(x for k, x in w.items() if k.startswith(("Escapula", "Umero", "Antebraco")))
            at.data[v.index].color = (min(1, r_), min(1, g_), min(1, b_), 1)
        wf = o.copy(); wf.data = o.data; wf.name = "Arame_" + nm; sc.collection.objects.link(wf); wf.hide_render = False
        m = wf.modifiers.new("W", "WIREFRAME"); m.thickness = 0.004; m.use_replace = True
        mw = bpy.data.materials.new("Arame"); mw.diffuse_color = (0, 0, 0, 1); m.material_offset = len(o.data.materials); o.data.materials.append(mw)
    sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.color_type = "VERTEX"; sh.light = "STUDIO"
    MODO = "ja"
if MODO == "tampa":                                                     # tampas v10: vermelho = cauda, verde = pata
    me = CORPO.data; at = me.color_attributes.new("Diag", "FLOAT_COLOR", "CORNER"); la = me.attributes.get("lado_tampa")
    for p_ in me.polygons:
        s_ = la.data[p_.index].value if la else 0; c = (0.9, 0.15, 0.1) if s_ < 0 else ((0.15, 0.75, 0.2) if s_ > 0 else (0.75, 0.75, 0.78))
        for li in p_.loop_indices: at.data[li].color = (*c, 1)
    MODO = "pesos_"
if MODO in ("classe", "pesos", "pesos_"):
    me = CORPO.data; gn = {g.index: g.name for g in CORPO.vertex_groups}
    at = me.color_attributes.new("Diag", "FLOAT_COLOR", "POINT") if MODO != "pesos_" else None
    for v in (me.vertices if at else []):
        p = v.co
        if MODO == "classe":
            if 2.0 < p.y < 5.2 and p.z < 4.2:
                s = min(dseg(p, h, t) for h, t in PT["E" if p.x > 0 else "D"]) - min(dseg(p, h, t) for h, t in CA)
                c = (1, 0.85, 0.1) if abs(s) < 0.15 else ((0.9, 0.15, 0.1) if s > 0 else (0.15, 0.75, 0.2))
            else: c = (0.35, 0.45, 0.8)
        else:
            w = {gn[e.group]: e.weight for e in v.groups}
            cr = sum(x for k, x in w.items() if k.startswith("Cauda")); cl = sum(x for k, x in w.items() if k.startswith(("Coxa", "Tibia", "Metatarso", "DedosPe")))
            c = (cr, cl, max(0.0, 1 - cr - cl))
        at.data[v.index].color = (*c, 1)
    sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.color_type = "VERTEX"; sh.light = "STUDIO"
    for n in CONJ:
        if n != CORPO.name: bpy.data.objects[n].hide_render = True
    wf = CORPO.copy(); wf.data = CORPO.data; wf.name = "Arame"; sc.collection.objects.link(wf); wf.hide_render = False
    m = wf.modifiers.new("W", "WIREFRAME"); m.thickness = 0.004; m.use_replace = True
    mw = bpy.data.materials.new("Arame"); mw.diffuse_color = (0, 0, 0, 1); m.material_offset = len(CORPO.data.materials); CORPO.data.materials.append(mw)
    sh.color_type = "VERTEX"
elif MODO != "ja":
    for o in list(sc.objects):
        if o.type in ("LIGHT",): bpy.data.objects.remove(o)
    w_ = bpy.data.worlds.new("E"); sc.world = w_
    if w_.node_tree is None: w_.use_nodes = True
    w_.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.43, 0.45, 1)
    for nome, en, rot in (("K", 3.0, (50, 0, 35)), ("C", 2.0, (120, 0, 205)), ("F", 1.2, (65, 0, -120)), ("B", 0.8, (150, 0, 0))):
        l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = [math.radians(x) for x in rot]
    sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 24; sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 640, 520
for o in list(sc.objects):
    if o.type == "CAMERA": bpy.data.objects.remove(o)
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
A0 = V((0.7, 3.0, 2.1)); G0 = V((0.0, -4.35, 4.3))
VIS = {"tras_cauda": (A0 + V((0.3, 6.5, 0.4)), A0, 38, 0.1), "lado_E_cauda": (A0 + V((6.5, 0.2, 0.3)), A0, 38, 0.1), "lado_D_cauda": (V((-0.7, 3.0, 2.1)) + V((-6.5, 0.2, 0.3)), V((-0.7, 3.0, 2.1)), 38, 0.1),
       "interno_E": (V((-3.0, 3.0, 2.1)), V((1.0, 3.0, 2.1)), 32, 2.7), "interno_D": (V((3.0, 3.0, 2.1)), V((-1.0, 3.0, 2.1)), 32, 2.7),
       "baixo_cauda": (A0 + V((0.0, 0.6, -6.0)), A0, 38, 0.1), "34_tras_E": (A0 + V((4.8, 4.8, 1.2)), A0, 36, 0.1),
       # v11: garganta / babador / peito (G0) e vista geral na distancia de jogo proposta (~25 studs)
       "garganta_frente": (G0 + V((0, -5.2, -0.6)), G0, 42, 0.1), "garganta_E": (G0 + V((5.4, -0.3, 0.2)), G0, 42, 0.1), "garganta_D": (G0 + V((-5.4, -0.3, 0.2)), G0, 42, 0.1),
       "garganta_baixo": (G0 + V((0.5, -1.6, -4.6)), G0, 40, 0.1), "garganta_34": (G0 + V((3.9, -3.9, 0.9)), G0, 42, 0.1), "garganta_34_D": (G0 + V((-3.9, -3.9, 0.9)), G0, 42, 0.1),
       "geral_jogo": (V((0, -0.6, 3.4)) + V((15, -19, 6)), V((0, -0.6, 3.4)), 30, 0.1)}
for q in QS:
    sc.frame_set(q)
    for v in VS:
        pos, alvo, lente, clip = VIS[v]; cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente; cd.clip_start = clip
        sc.render.filepath = os.path.join(OUT, "%s_%s_q%04d.png" % (PRE, v, q)); bpy.ops.render.render(write_still=True)
print("VISTAS_CAUDA_OK", L, MODO, QS, VS, flush=True)
