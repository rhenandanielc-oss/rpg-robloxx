"""Montaria M4 (10/11/2026): cavaleiro de TESTE sentado (preso ao osso Coluna2 no ponto do assento) nos clipes APROVADOS do Lobo
Ancestral (rig18/Lobo_Ancestral_Anim.blend, v26). Adaptado do m2_montado.py + m2_render_montado.py do Urso (aprovado 09/11).
Mede, por clipe: folga minima do manequim contra o lobo e contra a sela, e o balanco do assento (subida/descida em z, inclinacao
para frente/tras e para os lados, aceleracao vertical maxima). Opcional: video dos clipes principais (no lugar, como os clipes;
o jogo move o modelo). So leitura (nada salvo).
Uso: blender -b montaria/LA_M2_montaria.blend -P montaria/m4_montado.py -- <rig18/Lobo_Ancestral_Anim.blend> <saida.json> [pasta_video] [res=450]"""
import bpy, sys, os, json, math
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
RAIZ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.abspath(os.path.join(RAIZ, "..", "..", "Crocodilo_Primordial_Ref", "scripts")))
import manequim_r15 as mq
import m1_sela_lobo as sl
A = sys.argv[sys.argv.index("--") + 1:]; sc = bpy.context.scene; FPS = 30; sc.render.fps = FPS
arm = bpy.data.objects["Lobo_Ancestral_Rig"]; sela = bpy.data.objects[sl.NOME]; lo = [bpy.data.objects["Lobo_Ancestral_LOW"]]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
CLIPES = ("Repouso", "Observar", "Andar", "Trote", "Corrida", "Partida", "Freada", "VirarE", "VirarD", "Salto",
          "Uivo", "Rosnar", "Mordida", "Garra", "Impacto")
with bpy.data.libraries.load(os.path.abspath(A[0])) as (src, dst):
    dst.actions = [n for n in src.actions if n in ["Lobo_" + c for c in CLIPES] and n not in bpy.data.actions]
ra = bpy.data.objects["TESTE_Manequim_R15aprox_Rig"]; ra.animation_data.action = bpy.data.actions["DEMO_Cav_Sentado"]
arm.animation_data.action = None
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
sc.frame_set(1); bpy.context.view_layer.update()
def bvh_obj(o):
    dg = bpy.context.evaluated_depsgraph_get(); vs, fs = [], []
    for o_ in (o if isinstance(o, (list, tuple)) else [o]):
        ev = o_.evaluated_get(dg); m = ev.to_mesh(); W = o_.matrix_world; k = len(vs)
        vs += [W @ v.co for v in m.vertices]; fs += [tuple(i + k for i in p.vertices) for p in m.polygons]; ev.to_mesh_clear()
    return BVHTree.FromPolygons(vs, fs)
BL = arm.data.bones["Coluna2"].matrix_local
def osso(): return arm.matrix_world @ arm.pose.bones["Coluna2"].matrix @ BL.inverted()
REL = osso().inverted() @ ra.matrix_world
ra.animation_data.action = None                         # a pose sentada fica; o rig inteiro segue o osso
def tocar(nome):
    act = bpy.data.actions["Lobo_" + nome]; arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    return int(act.frame_range[0]), int(act.frame_range[1])
def quadro(f):
    sc.frame_set(f); bpy.context.view_layer.update(); ra.matrix_world = osso() @ REL; bpy.context.view_layer.update()
amo = mq.amostras_partes(0.2); res = {}
for nome in CLIPES:
    if "Lobo_" + nome not in bpy.data.actions: print("FALTA", nome); continue
    f0, f1 = tocar(nome); pl, ps = {}, {}; zs, pit, rol = [], [], []
    for f in range(f0, f1 + 1):
        quadro(f); M_ = osso() @ REL
        p = (ra.matrix_world @ ra.pose.bones["LowerTorso"].head); zs.append(p.z)
        fw = M_.to_3x3() @ V((0, -1, 0)); lt = M_.to_3x3() @ V((1, 0, 0))
        pit.append(math.degrees(math.asin(max(-1, min(1, fw.normalized().z))))); rol.append(math.degrees(math.asin(max(-1, min(1, lt.normalized().z)))))
        if (f - f0) % 2: continue
        fo = mq.folgas(ra, amo, bvh_obj(lo), passo=2); fs = mq.folgas(ra, amo, bvh_obj(sela), raio=3.0, passo=2)
        for k, v in fo.items():
            if v < pl.get(k, (9, 0))[0]: pl[k] = (v, f)
        for k, v in fs.items():
            if v < ps.get(k, (9, 0))[0]: ps[k] = (v, f)
    acc = max((abs(zs[i + 1] - 2 * zs[i] + zs[i - 1]) * FPS * FPS for i in range(1, len(zs) - 1)), default=0.0)
    corpo = {k: v for k, v in pl.items() if "Leg" not in k and "Foot" not in k}
    res[nome] = {"quadros": f1 - f0 + 1,
                 "lobo_min_geral": [round(min(pl.values())[0], 3), min(pl, key=lambda k: pl[k][0])],
                 "lobo_min_tronco_bracos_cabeca": [round(min(corpo.values())[0], 3), min(corpo, key=lambda k: corpo[k][0])],
                 "sela_min": [round(min(ps.values())[0], 3), min(ps, key=lambda k: ps[k][0])],
                 "quadril_z_amplitude": round(max(zs) - min(zs), 3), "inclinacao_frente_graus": [round(min(pit), 1), round(max(pit), 1)],
                 "inclinacao_lado_graus": [round(min(rol), 1), round(max(rol), 1)], "acel_vertical_max": round(acc, 1),
                 "pernas_min": {k: round(v[0], 3) for k, v in pl.items() if ("Leg" in k or "Foot" in k)}}
    print("MONTADO", nome, json.dumps(res[nome]), flush=True)
json.dump(res, open(A[1], "w"), indent=1); print("MONTADO_OK")
if len(A) > 2:                                          # video
    OUT = os.path.abspath(A[2]); RES = int(A[3]) if len(A) > 3 else 450; R = math.radians; os.makedirs(OUT, exist_ok=True)
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0)); ch = bpy.context.active_object
    mc = bpy.data.materials.new("_chao"); mc.use_nodes = True; nt = mc.node_tree; bs = nt.nodes["Principled BSDF"]
    ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 100; ck.inputs["Color1"].default_value = (0.47, 0.43, 0.36, 1); ck.inputs["Color2"].default_value = (0.38, 0.35, 0.29, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["UV"], ck.inputs["Vector"]); nt.links.new(ck.outputs["Color"], bs.inputs["Base Color"])
    ch.data.materials.append(mc)
    w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.64, 0.66, 1)
    sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.6; sol.angle = R(8)
    so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (R(50), 0, R(35))
    sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
    cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 45
    sc.render.resolution_x, sc.render.resolution_y = int(RES * 16 / 9) // 2 * 2, RES; sc.render.image_settings.file_format = "PNG"
    az, el, dist, al = -60, 12, 30, V((0, -0.8, 5.0))
    cam.location = al + V((-math.sin(R(az)) * math.cos(R(el)), -math.cos(R(az)) * math.cos(R(el)), math.sin(R(el)))) * dist
    cam.rotation_euler = (al - cam.location).to_track_quat("-Z", "Y").to_euler()
    pasta = os.path.join(OUT, "montado"); os.makedirs(pasta, exist_ok=True); n = 0; marcas = []
    for nome, voltas in (("Repouso", 1), ("Andar", 2), ("Trote", 3), ("Corrida", 6), ("VirarE", 1), ("Salto", 1), ("Mordida", 1)):
        f0, f1 = tocar(nome); marcas.append((nome, n + 1))
        for _ in range(voltas):
            for f in range(f0, f1 + 1):
                quadro(f); n += 1; sc.render.filepath = os.path.join(pasta, "m_%04d.png" % n); bpy.ops.render.render(write_still=True)
    s2 = bpy.data.scenes.new("_v"); s2.sequence_editor_create(); s2.render.fps = 30; s2.frame_start = 1; s2.frame_end = n
    st = s2.sequence_editor.strips.new_image("img", os.path.join(pasta, "m_0001.png"), channel=1, frame_start=1)
    for f in range(2, n + 1): st.elements.append("m_%04d.png" % f)
    s2.render.resolution_x, s2.render.resolution_y = sc.render.resolution_x, sc.render.resolution_y
    im = s2.render.image_settings
    try: im.media_type = "VIDEO"
    except Exception: pass
    im.file_format = "FFMPEG"; s2.render.ffmpeg.format = "MPEG4"; s2.render.ffmpeg.codec = "H264"; s2.render.ffmpeg.constant_rate_factor = "HIGH"
    s2.render.filepath = os.path.join(OUT, "Montado_lobo.mp4"); bpy.ops.render.render(animation=True, scene=s2.name)
    json.dump(marcas, open(os.path.join(OUT, "marcas.json"), "w")); print("RENDER_MONTADO_OK", n, marcas)
