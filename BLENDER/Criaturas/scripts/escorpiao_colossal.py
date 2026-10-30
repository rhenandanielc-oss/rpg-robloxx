# Escorpiao Colossal (Deserto de Cristal). OFICIAL: 8 pernas, 2 pincas, cauda segmentada com ferrao, 16-24 de comprimento com cauda
# estendida (usado 20); altura corporal PENDENTE (provisoria). 1 BU = 1 stud; frente -Y, cima +Z, esquerda +X.
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix, Quaternion
OUT = sys.argv[sys.argv.index("--") + 1]; DEST = sys.argv[sys.argv.index("--") + 2]
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
def skin_obj(name, pts, edges, radii, sub=2):
    me = bpy.data.meshes.new(name); me.from_pydata(pts, edges, [])
    ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    sk = ob.modifiers.new("Skin", "SKIN"); sk.use_smooth_shade = True
    ss = ob.modifiers.new("Sub", "SUBSURF"); ss.levels = sub
    for i, r in enumerate(radii):
        v = me.skin_vertices[0].data[i]; v.radius = (r[0], r[1]) if isinstance(r, tuple) else (r, r)
    me.skin_vertices[0].data[0].use_root = True
    return ob
def tubo(name, path, radii, achatar=None, lados=10):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); rings = []; n = len(path)
    for k in range(n):
        p = Vector(path[k]); d = (Vector(path[min(k + 1, n - 1)]) - Vector(path[max(k - 1, 0)])).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0)); u = d.cross(up).normalized(); v = d.cross(u).normalized()
        rings.append([bm.verts.new(p + u * math.cos(a / lados * 2 * math.pi) * radii[k] + v * math.sin(a / lados * 2 * math.pi) * radii[k] * (achatar or 1)) for a in range(lados)])
    for k in range(n - 1):
        for a in range(lados):
            b = (a + 1) % lados; bm.faces.new((rings[k][a], rings[k][b], rings[k + 1][b], rings[k + 1][a]))
    bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1]); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); scn.collection.objects.link(ob)
    for f in me.polygons: f.use_smooth = True
    return ob
# corpo: prossoma -> mesossoma (7) ; cauda: 5 segmentos + telson (cauda estendida para tras e levemente erguida)
corpo_pts = [(0, -6.2, 2.4), (0, -4.6, 2.6), (0, -3.0, 2.7), (0, -1.6, 2.75), (0, -0.2, 2.75), (0, 1.2, 2.7), (0, 2.5, 2.6), (0, 3.7, 2.5)]
corpo_r = [(1.6, 0.8), (2.4, 1.05), (2.6, 1.15), (2.75, 1.25), (2.8, 1.3), (2.6, 1.25), (2.2, 1.1), (1.5, 0.95)]
cauda_pts = [(0, 3.7, 2.5), (0, 5.0, 2.9), (0, 6.2, 3.3), (0, 7.4, 3.7), (0, 8.6, 4.1), (0, 9.8, 4.5), (0, 10.8, 4.7)]
cauda_r = [1.5, 0.95, 0.9, 0.85, 0.8, 0.78, 0.95]
pts = corpo_pts + cauda_pts[1:]; rad = corpo_r + cauda_r[1:]
edges = [(i, i + 1) for i in range(len(pts) - 1)]
corpo = skin_obj("Corpo", pts, edges, rad)
det = []
# aneis entre segmentos (placas) e cristas do dorso
for (x, y, z), r in zip(pts[1:-1], rad[1:-1]):
    rr = r if isinstance(r, tuple) else (r, r)
    det.append(tubo("Anel", [(0, y - 0.12, z), (0, y + 0.12, z)], [rr[0] * 1.02, rr[0] * 1.02], achatar=rr[1] / rr[0], lados=14))
# ferrao: lamina curva para baixo/frente
fer = [(0, 10.8, 4.7), (0, 11.9, 4.6), (0, 12.6, 3.9), (0, 12.7, 3.0), (0, 12.3, 2.4)]
det.append(tubo("Ferrao", fer, [0.75, 0.55, 0.35, 0.18, 0.02]))
# pernas: 4 pares (coxa -> femur para cima/fora -> tibia para baixo -> tarso)
LEG = {}
for s, lado in ((1, "E"), (-1, "D")):
    for k, y in enumerate((-3.4, -1.9, -0.4, 1.1)):
        abre = (k - 1.5) * 0.5
        ch = [(s * 2.2, y, 2.1), (s * 4.6, y + abre * 0.6, 3.6), (s * 6.8, y + abre * 1.4, 1.5), (s * 7.6, y + abre * 1.8, 0.1)]
        det.append(tubo("Perna", ch, [0.5, 0.42, 0.3, 0.08])); LEG["%d_%s" % (k + 1, lado)] = ch
    # pedipalpo + pinca: ombro -> cotovelo -> mao (bulbo) -> dedos
    pp = [(s * 1.4, -5.8, 2.2), (s * 3.4, -7.2, 2.8), (s * 3.6, -9.2, 2.5)]
    det.append(tubo("Palpo", pp, [0.55, 0.5, 0.55]))
    mao = [(s * 3.6, -9.2, 2.5), (s * 3.7, -10.2, 2.4), (s * 3.5, -11.2, 2.35)]
    det.append(tubo("Pinca", mao, [0.9, 1.2, 0.9], achatar=0.7))
    dedoF = [(s * 3.2, -11.2, 2.4), (s * 2.9, -12.6, 2.5), (s * 2.7, -13.6, 2.3)]
    dedoM = [(s * 3.9, -11.2, 2.3), (s * 4.0, -12.6, 2.1), (s * 3.5, -13.5, 2.15)]
    det.append(tubo("DedoFixo", dedoF, [0.45, 0.3, 0.05])); det.append(tubo("DedoMovel", dedoM, [0.45, 0.3, 0.05]))
    LEG["Palpo_" + lado] = (pp, mao, dedoF, dedoM)
for o in det:
    if not o.name.startswith("Anel"):
        m = o.modifiers.new("Sub", "SUBSURF"); m.levels = 1
for o in [corpo] + det:
    bpy.ops.object.select_all(action="DESELECT"); bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.convert(target="MESH")
bpy.ops.object.select_all(action="DESELECT")
for o in [corpo] + det: o.select_set(True)
bpy.context.view_layer.objects.active = corpo; bpy.ops.object.join()
mesh = bpy.context.view_layer.objects.active; mesh.name = "Escorpiao_Colossal"
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.remove_doubles(threshold=0.001); bpy.ops.object.mode_set(mode="OBJECT")
print("TRIS_FINAL", sum(len(p.vertices) - 2 for p in mesh.data.polygons))
# ---------- armature
arm_d = bpy.data.armatures.new("Esqueleto"); arm = bpy.data.objects.new("Escorpiao_Rig", arm_d); scn.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT"); EB = arm_d.edit_bones
def osso(nome, h, t, pai=None, deform=True):
    b = EB.new(nome); b.head = Vector(h); b.tail = Vector(t); b.roll = 0
    if pai: b.parent = EB[pai]
    b.use_deform = deform
P = [Vector(p) for p in corpo_pts]; T = [Vector(p) for p in cauda_pts]
osso("Raiz", (0, 0, 0), (0, 0, 2), None, False)
osso("Prossoma", P[3], P[0], "Raiz"); osso("Abdomen", P[3], P[7], "Raiz")
prev = "Abdomen"
for k in range(6):
    n = "Cauda%d" % (k + 1); osso(n, T[k], T[k + 1], prev); prev = n
osso("Ferrao", Vector(fer[0]), Vector(fer[-1]), prev)
for nome, ch in LEG.items():
    if nome.startswith("Palpo"):
        lado = nome[-1]; pp, mao, dF, dM = ch
        osso("Palpo1_" + lado, pp[0], pp[1], "Prossoma"); osso("Palpo2_" + lado, pp[1], pp[2], "Palpo1_" + lado)
        osso("Pinca_" + lado, Vector(mao[0]), Vector(dF[-1]), "Palpo2_" + lado); osso("DedoMovel_" + lado, Vector(dM[0]), Vector(dM[-1]), "Pinca_" + lado)
    else:
        c = [Vector(p) for p in ch]; pai = "Prossoma" if int(nome[0]) <= 2 else "Abdomen"
        osso("Femur" + nome, c[0], c[1], pai); osso("Tibia" + nome, c[1], c[2], "Femur" + nome); osso("Tarso" + nome, c[2], c[3], "Tibia" + nome)
bpy.ops.object.mode_set(mode="OBJECT")
print("OSSOS", len(arm_d.bones))
segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm_d.bones if b.use_deform}
def dist_seg(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared)); return (p - (a + ab * t)).length
vgs = {n: mesh.vertex_groups.new(name=n) for n in segs}
for v in mesh.data.vertices:
    ws = sorted(((1.0 / (dist_seg(v.co, *segs[n]) ** 6 + 0.002), n) for n in segs), reverse=True)[:3]  # quitina rigida: pesos concentrados
    tot = sum(w for w, _ in ws)
    for w, n in ws:
        if w / tot > 0.03: vgs[n].add([v.index], w / tot, "REPLACE")
m = mesh.modifiers.new("Armature", "ARMATURE"); m.object = arm; mesh.parent = arm
PB = arm.pose.bones
for pb in PB: pb.rotation_mode = "QUATERNION"
def R(ax, ay, az): return Matrix.Rotation(math.radians(az), 3, "Z") @ Matrix.Rotation(math.radians(ay), 3, "Y") @ Matrix.Rotation(math.radians(ax), 3, "X")
def aplicar(pose):
    for pb in PB: pb.rotation_quaternion = Quaternion(); pb.location = Vector()
    for nome, val in pose.items():
        pb = PB[nome]; M3 = pb.bone.matrix_local.to_3x3(); rot, loc = val if isinstance(val, tuple) else (val, None)
        pb.rotation_quaternion = (M3.inverted() @ rot @ M3).to_quaternion()
        if loc is not None: pb.location = M3.inverted() @ Vector(loc)
def S(x): return math.sin(2 * math.pi * x)
def C(x): return math.cos(2 * math.pi * x)
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
# cauda arqueada sobre o dorso (postura tipica) e pincas a frente
def cauda_arco(f=1.0, extra=0.0):
    return {**{"Cauda%d" % (k + 1): R((22 if k < 5 else 12) * f + extra * (k == 5), 0, 0) for k in range(6)}, "Ferrao": R(20 * f + extra, 0, 0)}
def palpos(abre=0.0, ergue=0.0):
    p = {}
    for lado, s in (("E", 1), ("D", -1)):
        p["Palpo1_" + lado] = R(-ergue, 0, s * 6); p["Palpo2_" + lado] = R(-ergue * 0.5, 0, 0); p["DedoMovel_" + lado] = R(0, 0, s * abre)
    return p
# marcha alternada: grupo A (1E,2D,3E,4D) e grupo B (1D,2E,3D,4E); femur gira no plano horizontal e levanta na recuperacao
GA = {"1_E", "2_D", "3_E", "4_D"}
def marcha(t, amp=18, lift=16):
    p = {}
    for k in range(1, 5):
        for lado, s in (("E", 1), ("D", -1)):
            nm = "%d_%s" % (k, lado); f = 0.0 if nm in GA else 0.5; x = t - f
            p["Femur" + nm] = R(0, -s * lift * max(0, S(x + 0.25)), s * amp * S(x))
            p["Tibia" + nm] = R(0, s * 6 * max(0, S(x + 0.25)), 0)
    p["Prossoma"] = R(0, 1.2 * S(2 * t), 0); p["Abdomen"] = R(0, -1.0 * S(2 * t), 0)
    return p
FPS = 30; scn.render.fps = FPS; ACOES = {}
def acao(nome, dur, loop, f):
    act = bpy.data.actions.new(nome); arm.animation_data_create(); arm.animation_data.action = act
    nfr = max(2, int(dur * FPS))
    for fr in range(nfr + 1):
        aplicar(f(fr / nfr))
        for pb in PB: pb.keyframe_insert("rotation_quaternion", frame=fr + 1); pb.keyframe_insert("location", frame=fr + 1)
    act.use_fake_user = True; ACOES[nome] = act
    tr = arm.animation_data.nla_tracks.new(); tr.name = nome; tr.strips.new(nome, 1, act); arm.animation_data.action = None
acao("Repouso", 4.0, True, lambda t: {**cauda_arco(1.0 + 0.05 * S(t)), **palpos(6 + 6 * max(0, S(t * 2)), 3), "Prossoma": R(0.6 * S(t), 0, 0)})
acao("Andar", 1.0, True, lambda t: {**marcha(t), **cauda_arco(1.0, 2 * S(t)), **palpos(4, 4)})
acao("Corrida", 0.55, True, lambda t: {**marcha(t, 24, 20), **cauda_arco(0.85), **palpos(2, 6)})
for nome, s in (("VirarEsquerda", 1), ("VirarDireita", -1)):
    acao(nome, 1.0, True, lambda t, s=s: {**marcha(t, 12, 12), **cauda_arco(1.0), **palpos(4, 4), "Prossoma": R(0, 0, 8 * s), "Abdomen": R(0, 0, -6 * s)})
acao("Observar", 3.5, True, lambda t: {**cauda_arco(1.1), **palpos(10, 14 + 4 * S(t)), "Prossoma": R(-6, 0, 10 * S(t))})
def ferroada(t):
    u = ease(t / 0.3) * (1 - ease((t - 0.45) / 0.55))
    return {**cauda_arco(1.0 + 0.6 * u, 25 * u), **palpos(6, 6), "Abdomen": R(-4 * u, 0, 0)}
acao("FerraoPerfurante", 1.2, False, ferroada)
def pincas(t):
    u = ease(t / 0.35); fecha = ease((t - 0.45) / 0.15) * (1 - ease((t - 0.8) / 0.2))
    p = {**cauda_arco(1.0), **palpos(28 * u * (1 - fecha), 10 * u)}
    for lado, s in (("E", 1), ("D", -1)): p["Palpo1_" + lado] = R(-10 * u, 0, s * (6 - 14 * fecha))
    return p
acao("PincasEsmagadoras", 1.6, False, pincas)
def escavar(t):
    u = ease(t / 0.4); p = marcha(t * 3, 8, 6)
    p["Prossoma"] = (R(4 * u + 2 * S(t * 6), 0, 0), (0, 0, -1.6 * u)); p["Abdomen"] = (R(-2 * u, 0, 3 * S(t * 6)), (0, 0, -1.5 * u))
    for k in range(1, 5):
        for lado, s in (("E", 1), ("D", -1)): p["Femur%d_%s" % (k, lado)] = R(0, s * 14 * u, s * 6 * S(t * 3 - k * 0.2))
    p.update(cauda_arco(0.6)); p.update(palpos(0, -6 * u))
    return p
acao("EscavacaoDeAreia", 2.5, False, escavar)
print("ACOES", len(ACOES))
# ---------- quitina: placas lisas com variacao e frisos (assado), 3 padroes oficiais
PAD = [("Negro_Obsidiana", (0.01, 0.01, 0.012), (0.10, 0.09, 0.10)), ("Bronze_Desertico", (0.10, 0.06, 0.03), (0.48, 0.32, 0.16)), ("Areia_Rochosa", (0.22, 0.18, 0.12), (0.62, 0.54, 0.40))]
bpy.context.view_layer.objects.active = mesh
for o in scn.objects: o.select_set(False)
mesh.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003); bpy.ops.object.mode_set(mode="OBJECT")
mat = bpy.data.materials.new("Quitina"); mat.use_nodes = True; Nn = mat.node_tree.nodes; Lk = mat.node_tree.links
b = Nn["Principled BSDF"]; tc = Nn.new("ShaderNodeTexCoord")
nz = Nn.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.4; nz.inputs["Detail"].default_value = 6; Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
vo = Nn.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 1.4; vo.feature = "DISTANCE_TO_EDGE"; Lk.new(tc.outputs["Object"], vo.inputs["Vector"])
eg = Nn.new("ShaderNodeMapRange"); eg.inputs["From Max"].default_value = 0.06; Lk.new(vo.outputs["Distance"], eg.inputs["Value"])
mu = Nn.new("ShaderNodeMath"); mu.operation = "MULTIPLY"; Lk.new(eg.outputs["Result"], mu.inputs[0]); Lk.new(nz.outputs["Fac"], mu.inputs[1])
rp = Nn.new("ShaderNodeValToRGB"); Lk.new(mu.outputs[0], rp.inputs["Fac"]); Lk.new(rp.outputs["Color"], b.inputs["Base Color"])
b.inputs["Roughness"].default_value = 0.35
bp = Nn.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.08; Lk.new(eg.outputs["Result"], bp.inputs["Height"]); Lk.new(bp.outputs["Normal"], b.inputs["Normal"])
mesh.data.materials.clear(); mesh.data.materials.append(mat)
scn.render.engine = "CYCLES"; scn.cycles.samples = 4
def assar(tipo, nome, cs):
    img = bpy.data.images.new(nome, 2048, 2048, alpha=False); img.colorspace_settings.name = cs
    tn = Nn.new("ShaderNodeTexImage"); tn.image = img
    for n in Nn: n.select = False
    tn.select = True; Nn.active = tn
    if tipo == "DIFFUSE": bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4)
    else: bpy.ops.object.bake(type="NORMAL", margin=4)
    img.filepath_raw = os.path.join(DEST, nome + ".png"); img.file_format = "PNG"; img.save(); return tn
def cores(pd): rp.color_ramp.elements[0].color = pd[1] + (1,); rp.color_ramp.elements[1].color = pd[2] + (1,)
cores(PAD[0]); tnor = assar("NORMAL", "Escorpiao_Colossal_Normal", "Non-Color")
for pd in PAD[1:]: cores(pd); assar("DIFFUSE", "Escorpiao_Colossal_Cor_" + pd[0], "sRGB")
cores(PAD[0]); tcor = assar("DIFFUSE", "Escorpiao_Colossal_Cor_" + PAD[0][0], "sRGB")
for n in list(Nn):
    if n not in (tcor, tnor): Nn.remove(n)
o_ = Nn.new("ShaderNodeOutputMaterial"); b_ = Nn.new("ShaderNodeBsdfPrincipled"); nm = Nn.new("ShaderNodeNormalMap")
Lk.new(tcor.outputs["Color"], b_.inputs["Base Color"]); Lk.new(tnor.outputs["Color"], nm.inputs["Color"]); Lk.new(nm.outputs["Normal"], b_.inputs["Normal"]); b_.inputs["Roughness"].default_value = 0.35; Lk.new(b_.outputs["BSDF"], o_.inputs["Surface"])
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 960; scn.render.resolution_y = 600
sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 3.4; so = bpy.data.objects.new("Sol", sun); scn.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(35))
scn.world = bpy.data.worlds.new("W"); scn.world.use_nodes = True; scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.66, 1)
bpy.ops.mesh.primitive_plane_add(size=200); ch = bpy.context.active_object
cm = bpy.data.materials.new("Areia"); cm.use_nodes = True; cm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.72, 0.62, 0.42, 1); ch.data.materials.append(cm)
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=4.2, location=(9, -9, 2.1)); h1 = bpy.context.active_object
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(9, -9, 4.7)); h2 = bpy.context.active_object
cam = bpy.data.cameras.new("Cam"); co = bpy.data.objects.new("Cam", cam); scn.collection.objects.link(co); scn.camera = co; cam.lens = 35
def foto(nome, an, t, loc, alvo):
    act = ACOES[an]; arm.animation_data.action = act; scn.frame_set(1 + int(t * (act.frame_range[1] - 1)))
    co.location = loc; co.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = os.path.join(OUT, "Escorpiao_%s.png" % nome); bpy.ops.render.render(write_still=True); arm.animation_data.action = None
foto("34", "Repouso", 0, (22, -24, 14), (0, 0, 3)); foto("lateral", "Andar", 0.25, (28, 0, 5), (0, 0, 3)); foto("cima", "Andar", 0.25, (0, 0.01, 30), (0, 0, 0))
foto("ferrao", "FerraoPerfurante", 0.3, (22, -24, 14), (0, 0, 3)); foto("pincas", "PincasEsmagadoras", 0.4, (10, -28, 10), (0, -6, 3))
for o in (ch, h1, h2, co, so): bpy.data.objects.remove(o, do_unlink=True)
for o in scn.objects: o.select_set(False)
arm.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.gltf(filepath=os.path.join(DEST, "Escorpiao_Colossal.glb"), export_format="GLB", use_selection=True, export_animations=True, export_animation_mode="ACTIONS", export_skins=True, export_yup=True)
bpy.ops.export_scene.fbx(filepath=os.path.join(DEST, "Escorpiao_Colossal.fbx"), use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=True,
                         bake_anim_use_nla_strips=False, path_mode="COPY", embed_textures=True, axis_forward="-Z", axis_up="Y")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(DEST, "Escorpiao_Colossal.blend"))
d = mesh.dimensions; print("DIM %.1f x %.1f x %.1f" % (d.x, d.y, d.z)); print("EXPORTADO")
