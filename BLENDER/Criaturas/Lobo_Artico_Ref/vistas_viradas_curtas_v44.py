"""(v44 = copia da v27 para as viradas CURTAS: VirarCurtoEsquerda/Direita e viradas_curtas_v44.json.)
(v27 = copia da v26 lendo viradas_v27.json / export_clipes_v27.json; resto igual.)
v26: render das SEQUENCIAS de ida e volta das viradas (mesma linha do tempo e mesma composicao mundial da auditar_viradas_v26:
mundo = BASE @ T(t) @ Rz(psi(t)) aplicados ao objeto do armature, so no render; os clipes continuam no lugar). Workbench, chao em
GRADE (0,5 / 1 stud), SETA DE RUMO no chao (gira com o rumo externo), rastro dos pontos medidos de cada apoio (DE azul, DD vermelho,
TE verde, TD amarelo). Cameras FIXAS no mundo (nao giram com o lobo): topo (vista superior ortografica sobre o pivo: mostra o giro
real e a sequencia de passos), perfil_E (+X), perfil_D (-X), frente (-Y), tras (+Y), 34 (tres-quartos), patas_E / patas_D (closes
baixos fixos dos dois lados).
Uso: blender -b <anim.blend> -P vistas_viradas_v26.py -- <dir> <LOD> <sequencia ida_volta_E|ida_volta_D> <vistas> [res=LxA]"""
import bpy, sys, os, json, math, bmesh
from mathutils import Vector as V, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); L, SQ = a[1], a[2]; VS = a[3].split(","); os.makedirs(OUT, exist_ok=True)
RES = next((tuple(int(c) for c in o[4:].split("x")) for o in a[4:] if o.startswith("res=")), (480, 360))
sc = bpy.context.scene; SRC = os.path.dirname(bpy.data.filepath); VJ = json.load(open(os.path.join(SRC, "viradas_curtas_v44.json"))); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
N = {k: v["quadros"] for k, v in VJ["acoes"].items()}
def Mt(acao, q):
    if acao == "Repouso": return Matrix.Identity(4)
    A = VJ["acoes"][acao]; T = A["T_por_quadro"][q]; return Matrix.Translation(V((T[0], T[1], 0))) @ Matrix.Rotation(math.radians(A["psi_graus_por_quadro"][q]), 4, "Z")
ordem = {"ida_volta_E": ["VirarCurtoEsquerda", "VirarCurtoDireita"], "ida_volta_D": ["VirarCurtoDireita", "VirarCurtoEsquerda"]}[SQ]
LT = [("Repouso", q, Matrix.Identity(4)) for q in range(230, 240)]; base = Matrix.Identity(4)
for ac_ in ordem:
    for q in range(N[ac_]): LT.append((ac_, q, base @ Mt(ac_, q)))
    base = base @ Mt(ac_, N[ac_])
LT += [("Repouso", q, base) for q in range(0, 21)]
if os.environ.get("ANTES_SHIFTLOCK"):                         # v44: comportamento ATUAL do Controle r7 (giro do pivo com o Repouso tocando)
    LT = [("Repouso", (230 + i) % 240, m) for i, (_, q, m) in enumerate(LT)]
def apoio(acao, k, q): return True if acao == "Repouso" else VJ["acoes"][acao]["apoio_por_quadro"][k][q]
ARM = bpy.data.objects["LoboArtico_Rig"]
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Marca", "LOW_Cristais"], "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}[L]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ
ARM.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
PV = V(VJ["pivo"])
bpy.ops.mesh.primitive_plane_add(size=24, location=(PV.x, PV.y, -0.002)); chao = bpy.context.object
gm = bpy.data.meshes.new("grade"); bm = bmesh.new()
for i in range(-24, 25):
    w = 0.012 if i % 2 else 0.025; c = i * 0.5
    for vs in (((c - w, -12 + PV.y, 0), (c + w, -12 + PV.y, 0), (c + w, 12 + PV.y, 0), (c - w, 12 + PV.y, 0)), ((-12, PV.y + c - w, 0.0005), (12, PV.y + c - w, 0.0005), (12, PV.y + c + w, 0.0005), (-12, PV.y + c + w, 0.0005))):
        bm.faces.new([bm.verts.new(p) for p in vs])
bm.to_mesh(gm); bm.free(); go = bpy.data.objects.new("Grade", gm); sc.collection.objects.link(go)
sm = bpy.data.meshes.new("seta"); bm = bmesh.new()                     # seta de rumo: aponta para a FRENTE do lobo (-Y local), no chao, sobre o pivo
for vs in (((-0.12, 0, 0.02), (0.12, 0, 0.02), (0.12, -3.4, 0.02), (-0.12, -3.4, 0.02)), ((-0.45, -3.4, 0.02), (0.45, -3.4, 0.02), (0, -4.3, 0.02))):
    bm.faces.new([bm.verts.new(V(p) + V((PV.x, PV.y, 0))) for p in vs])
bm.to_mesh(sm); bm.free(); seta = bpy.data.objects.new("Seta", sm); sc.collection.objects.link(seta)
C = bpy.data.objects[L + "_Corpo"]; me = C.data
patas = {k: [v.index for v in me.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8] for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"])}
CORK = {"DE": (0.15, 0.4, 1.0), "DD": (1.0, 0.15, 0.1), "TE": (0.1, 0.85, 0.2), "TD": (1.0, 0.85, 0.05)}
def usar(ac_):
    acn = bpy.data.actions[ac_]; ARM.animation_data.action = acn
    if len(acn.slots): ARM.animation_data.action_slot = acn.slots[0]
cache = {}
def posado(ac_, q):
    if (ac_, q) not in cache:
        usar(ac_); sc.frame_set(q); dg = bpy.context.evaluated_depsgraph_get(); e = C.evaluated_get(dg); m = e.to_mesh(); cache[(ac_, q)] = [v.co.copy() for v in m.vertices]; e.to_mesh_clear()
    return cache[(ac_, q)]
esf = bpy.data.meshes.new("m"); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.06); bm.to_mesh(esf); bm.free(); obs = []
for k, ids in patas.items():
    segs, cur = [], []
    for i, e in enumerate(LT):
        if apoio(e[0], k, e[1]): cur.append(i)
        elif cur: segs.append(cur); cur = []
    if cur: segs.append(cur)
    for sg in segs:
        im = sg[len(sg) // 2]; Pm = posado(*LT[im][:2]); zm = min(Pm[i].z for i in ids); pts = [i for i in ids if Pm[i].z < zm + 0.03]
        for j in sg:
            Pq = posado(*LT[j][:2]); vis = [Pq[i] for i in pts if Pq[i].z < zm + 0.06]
            if not vis: continue
            c = LT[j][2] @ (sum(vis, V()) / len(vis)); o = bpy.data.objects.new("pt", esf); o.location = (c.x, c.y, 0.02); o.color = (*CORK[k], 1); sc.collection.objects.link(o); obs.append((j, sg[-1], o))
def mat(nome, cor):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome); m.diffuse_color = (*cor, 1); return m
for nm in CONJ:
    for s_ in bpy.data.objects[nm].material_slots: s_.link = "OBJECT"; s_.material = mat("Rev_pele", (0.82, 0.83, 0.86))
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "OBJECT"; sh.show_shadows = True
sh.background_type = "VIEWPORT"; sh.background_color = (0.4, 0.42, 0.45)
for o in sc.objects:
    if o.type == "MESH" and not o.name.startswith("pt"):
        o.color = (0.82, 0.83, 0.86, 1) if o.name in CONJ else ((0.55, 0.57, 0.6, 1) if o == chao else ((0.95, 0.5, 0.1, 1) if o == seta else (0.2, 0.21, 0.24, 1)))
sc.render.resolution_x, sc.render.resolution_y = RES
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
C0 = PV + V((0, 0, 3.0)); PT = PV + V((0, 0, 0.8))
VIS = {"topo": (PV + V((0, 0, 30)), PV, ("o", 17.0)), "perfil_E": (C0 + V((24, 0, 0.6)), C0, ("o", 13.5)), "perfil_D": (C0 + V((-24, 0, 0.6)), C0, ("o", 13.5)),
       "frente": (C0 + V((0, -24, 0.6)), C0, ("o", 13.5)), "tras": (C0 + V((0, 24, 0.6)), C0, ("o", 13.5)), "34": (C0 + V((11, -11, 7)), C0, 34),
       "patas_E": (PT + V((10, 0.5, 0.6)), PT, 28), "patas_D": (PT + V((-10, 0.5, 0.6)), PT, 28)}
for i, (ac_, q, Mw) in enumerate(LT):
    usar(ac_); sc.frame_set(q); ARM.matrix_world = Mw; seta.matrix_world = Mw
    for q0, qf, o in obs: o.hide_render = not (q0 <= i <= qf + 10)
    bpy.context.view_layer.update()
    for v in VS:
        pos, alvo, l_ = VIS[v]; cam.location = pos
        cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y" if v != "topo" else "Y").to_euler() if v != "topo" else (0, 0, 0)
        if isinstance(l_, tuple): cd.type = "ORTHO"; cd.ortho_scale = l_[1]
        else: cd.type = "PERSP"; cd.lens = l_
        sc.render.filepath = os.path.join(OUT, "%s%s_%s_%s_t%04d.png" % ("ANTES_" if os.environ.get("ANTES_SHIFTLOCK") else "", L, SQ, v, i)); bpy.ops.render.render(write_still=True)
f_ = base.to_3x3() @ V((0, -1, 0))
json.dump({"linha_do_tempo": ["%s q%d" % e[:2] for e in LT], "psi_mundo_graus": [round(math.degrees(math.atan2((e[2].to_3x3() @ V((0, -1, 0))).x, -(e[2].to_3x3() @ V((0, -1, 0))).y)), 3) for e in LT]},
          open(os.path.join(OUT, "linha_%s_%s.json" % (L, SQ)), "w"))
print("VISTAS_VIRADAS_OK", L, SQ, len(LT), VS, flush=True)
