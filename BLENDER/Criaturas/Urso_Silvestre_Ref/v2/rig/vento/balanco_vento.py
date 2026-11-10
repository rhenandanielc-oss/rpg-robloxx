"""Balanco procedural dos ossos Pelo* (demonstracao no Blender; o Roblox usara a MESMA formula num script do cliente).
Para cada Pelo*: giro em torno do eixo  cross(direcao_do_osso, vento)  (a mecha deita a favor do vento), angulo
   ang(t) = A * I * (0.55 + 0.30 * sin(2*pi*f*t + fase) + 0.15 * sin(2*pi*2.3*f*t + 1.7*fase))
I = intensidade (0 = sem vento, 0.4 = fraco, 1 = forte); A = 9 graus; f = 0.9 Hz; fase = posicao do osso ao longo do
vento (as mechas da frente movem antes). PARAMETROS DE TESTE, nao regra do jogo.
Uso: blender -b CR_Urso_v2_Anim.blend -P balanco_vento.py -- <saida_dir> <Clipe> <quadros> <intensidades csv> [medir]"""
import bpy, sys, os, math, json
from mathutils import Vector as V, Quaternion as Q
A_ = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A_[0]); os.makedirs(OUT, exist_ok=True)
CLIPE, NQ, INTS = A_[1], int(A_[2]), [float(x) for x in A_[3].split(",")]; MEDIR = "medir" in A_
AMP, FREQ, VENTO = math.radians(9.0), 0.9, V((1.0, 0.25, 0.0)).normalized()     # vento vindo da esquerda do urso
sc = bpy.context.scene; arm = bpy.data.objects["Urso_Rig"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
PELO = [pb for pb in arm.pose.bones if pb.name.startswith("Pelo")]
arm.animation_data.action = bpy.data.actions["Urso_" + CLIPE]
# as acoes assadas tem chave (identidade) tambem nos Pelo*: desliga essas curvas so aqui, senao o render as reaplica
def curvas(act):
    try: return list(act.fcurves)
    except AttributeError:
        out = []
        for ly in act.layers:
            for st in ly.strips:
                for cb in st.channelbags: out += list(cb.fcurves)
        return out
mudas = 0
for fc in curvas(arm.animation_data.action):
    if '"Pelo' in fc.data_path: fc.mute = True; mudas += 1
print("CURVAS_PELO_DESLIGADAS", mudas)
def aplicar(t, I):
    for pb in PELO:
        b = pb.bone; d = (b.tail_local - b.head_local).normalized(); eixo_w = d.cross(VENTO)
        if eixo_w.length < 1e-4: pb.rotation_quaternion = Q(); continue
        fase = b.head_local.dot(VENTO) * 0.35
        ang = AMP * I * (0.55 + 0.30 * math.sin(2 * math.pi * FREQ * t + fase) + 0.15 * math.sin(2 * math.pi * 2.3 * FREQ * t + 1.7 * fase))
        eixo_l = (b.matrix_local.to_3x3().inverted() @ eixo_w).normalized()        # eixo no espaco do osso (repouso)
        pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion = Q(eixo_l, ang)
if MEDIR:      # deslocamento maximo dos vertices com vento forte x sem vento, e se rosto/patas/boca ficam parados
    import numpy as np
    MAL = [bpy.data.objects[n] for n in ("Urso_Cabeca", "Urso_Corpo_Frente", "Urso_Corpo_Tras", "Urso_Boca")]
    def pts():
        dg = bpy.context.evaluated_depsgraph_get(); r = []
        for o in MAL:
            ev = o.evaluated_get(dg); me = ev.to_mesh(); co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", co); r.append(co.reshape(-1, 3).copy()); ev.to_mesh_clear()
        return r
    EXCL = {"Cabeca", "Mandibula", "OrelhaE", "OrelhaD", "AntebracoE", "MaoE", "DedosE", "AntebracoD", "MaoD", "DedosD", "CanelaE", "PeE", "DedosPeE", "CanelaD", "PeD", "DedosPeD"}
    res = {}
    for q in range(0, NQ, 4):
        sc.frame_set(q + 1); aplicar(0, 0); p0 = pts()
        for I in INTS:
            aplicar(q / 30, I); p1 = pts()
            for o, a, b in zip(MAL, p0, p1):
                d = np.linalg.norm(a - b, axis=1); gn = {g.index: g.name for g in o.vertex_groups}
                dom = np.array([gn[max(v.groups, key=lambda g: g.weight).group] in EXCL if v.groups else False for v in o.data.vertices])
                k = "I%.1f" % I; r = res.setdefault(k, {"max": 0, "rosto_patas_max": 0, "boca_max": 0, "mov_vertices": 0})
                r["max"] = max(r["max"], float(d.max())); r["rosto_patas_max"] = max(r["rosto_patas_max"], float(d[dom].max()) if dom.any() else 0)
                if o.name == "Urso_Boca": r["boca_max"] = max(r["boca_max"], float(d.max()))
                r["mov_vertices"] = max(r["mov_vertices"], int((d > 0.005).sum()) + (0 if o.name == MAL[0].name else 0))
    print("MEDIDA", json.dumps({k: {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in res.items()}))
    sys.exit(0)
# render: uma coluna por intensidade
for o in [o for o in sc.objects if o.type in ("LIGHT", "CAMERA")]: bpy.data.objects.remove(o)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.42, 1)
for nome, en, rot in (("K", 3.0, (0.84, 0, -0.61)), ("R", 2.0, (2.1, 0, 2.8))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=120)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 8; sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 520, 400
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
pos, alvo = V((-17, -9, 8.5)), V((0, 0.2, 5.2)); cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
for q in range(NQ):
    sc.frame_set(q + 1)
    for I in INTS:
        aplicar(q / 30, I); sc.render.filepath = os.path.join(OUT, "I%.1f_%03d.png" % (I, q)); bpy.ops.render.render(write_still=True)
print("VENTO_OK")
