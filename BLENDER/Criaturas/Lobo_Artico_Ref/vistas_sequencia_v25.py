"""v25: render da SEQUENCIA CONTINUA Repouso (q230..239) -> Arrancada -> Corrida x3 -> Frenagem -> Repouso (q0..q30), sem cortes,
com o RIG REAL (Workbench), chao em GRADE (linhas 0,5 / 1 stud) e DESLOCAMENTO pela CURVA nao uniforme (transicoes_v25.json; Corrida
a v constante; so no render - os clipes continuam no lugar), mesma linha do tempo e mesmos apoios da auditar_sequencia_v25:
rastro dos pontos medidos de cada fase de apoio (DE azul, DD vermelho, TE verde, TD amarelo); apoio sem deslize = marcadores
empilhados. Faixa no topo de cada quadro: acao, quadro, velocidade e patas no chao (escrita depois, na prancha).
Vistas: perfil_E, perfil_D, frente, tras, 34_E, patas_E, patas_D (camera acompanha o corpo), fixa_D (camera PARADA no ponto de
partida, perfil D largo, mostra a curva de deslocamento sem acompanhar).
Uso: blender -b <anim.blend> -P vistas_sequencia_v25.py -- <dir> <LOD> <vistas> [res=LxA] [modo=solid|real]"""
import bpy, sys, os, json, math, bmesh
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); L = a[1]; VS = a[2].split(","); os.makedirs(OUT, exist_ok=True)
OPC = a[3:]; RES = next((tuple(int(c) for c in o[4:].split("x")) for o in OPC if o.startswith("res=")), (480, 360))
sc = bpy.context.scene; SRC = os.path.dirname(bpy.data.filepath); CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); TJ = json.load(open(os.path.join(SRC, "transicoes_v25.json")))
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); COR = CJ["marchas"]["Corrida"]; VC = COR["v_studs_s"]; FPS = 30
NA, NF = TJ["acoes"]["Arrancada"]["quadros"], TJ["acoes"]["Frenagem"]["quadros"]
LT = [("Repouso", q) for q in range(230, 240)] + [("Arrancada", q) for q in range(NA)] + [("Corrida", q) for _ in range(3) for q in range(14)] + \
     [("Frenagem", q) for q in range(NF)] + [("Repouso", q) for q in range(0, 31)]
def dx(ac_, q):
    if ac_ in ("Arrancada", "Frenagem"): Xs = TJ["acoes"][ac_]["X_por_quadro"]; return Xs[q] - Xs[q - 1] if q > 0 else (Xs[0] if ac_ == "Arrancada" else -VC / FPS)
    return -VC / FPS if ac_ == "Corrida" else 0.0
Xc = []; x = 0.0
for i, e in enumerate(LT):
    if i > 0: x += dx(*e)
    Xc.append(x)
def apoio(ac_, k, q):
    if ac_ == "Repouso": return True
    if ac_ in ("Arrancada", "Frenagem"): return TJ["acoes"][ac_]["apoio_por_quadro"][k][q]
    u = ((q / FPS / COR["T"]) - COR["fases"][k]) % 1.0; return u < COR["apoio"]
ARM = bpy.data.objects["LoboArtico_Rig"]
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"], "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}[L]
REAL = "modo=real" in OPC
if not REAL: CONJ = [n for n in CONJ if "Pelagem" not in n]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ
ARM.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
def mat(nome, cor):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome); m.diffuse_color = (*cor, 1); return m
x_fim = Xc[-1]
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, x_fim / 2, -0.002)); chao = bpy.context.object; chao.scale = (16, abs(x_fim) + 30, 1)
gm = bpy.data.meshes.new("grade"); bm = bmesh.new(); y0, y1 = 14.0, x_fim - 14
for i in range(-16, 17):
    w = 0.012 if i % 2 else 0.025; xx = i * 0.5; vs = [bm.verts.new(p) for p in ((xx - w, y0, 0), (xx + w, y0, 0), (xx + w, y1, 0), (xx - w, y1, 0))]; bm.faces.new(vs)
for j in range(int(y1 / 0.5) - 1, int(y0 / 0.5) + 1):
    yy = j * 0.5; w = 0.012 if j % 2 else 0.025; vs = [bm.verts.new(p) for p in ((-8, yy - w, 0.0005), (8, yy - w, 0.0005), (8, yy + w, 0.0005), (-8, yy + w, 0.0005))]; bm.faces.new(vs)
bm.to_mesh(gm); bm.free(); go = bpy.data.objects.new("Grade", gm); sc.collection.objects.link(go)
# marcadores dos apoios (metodo da auditoria)
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
esf = bpy.data.meshes.new("m"); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.055); bm.to_mesh(esf); bm.free()
obs = []
for k, ids in patas.items():
    segs, cur = [], []
    for i, e in enumerate(LT):
        if apoio(e[0], k, e[1]): cur.append(i)
        elif cur: segs.append(cur); cur = []
    if cur: segs.append(cur)
    for sg in segs:
        im = sg[len(sg) // 2]; Pm = posado(*LT[im]); zm = min(Pm[i].z for i in ids); pts = [i for i in ids if Pm[i].z < zm + 0.03]
        for j in sg:
            Pq = posado(*LT[j]); vis = [Pq[i] for i in pts if Pq[i].z < zm + 0.06]
            if not vis: continue
            c = sum(vis, V()) / len(vis); o = bpy.data.objects.new("pt", esf); o.location = (c.x, c.y + Xc[j], 0.01); o.color = (*CORK[k], 1); sc.collection.objects.link(o); obs.append((j, sg[-1], o))
if REAL:
    w_ = bpy.data.worlds.new("E"); sc.world = w_
    if w_.node_tree is None: w_.use_nodes = True
    w_.node_tree.nodes["Background"].inputs[0].default_value = (0.40, 0.42, 0.45, 1)
    for nome, en, rot in (("K", 3.0, (50, 0, 35)), ("C", 1.8, (120, 0, 205)), ("F", 1.2, (65, 0, -120))):
        l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = [math.radians(v_) for v_ in rot]
    chao.data.materials.append(mat("Rev_chao", (0.55, 0.57, 0.6))); gm.materials.append(mat("Rev_linha", (0.15, 0.16, 0.18)))
    for o in [o for _, _, o in obs]:
        o.data = o.data.copy() if False else o.data
    sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16; sc.view_settings.view_transform = "AgX"
    for k in CORK: mat("Rev_" + k, CORK[k])
    esf.materials.append(mat("Rev_pt", (1, 0.3, 0.1)))
else:
    for nm in CONJ:
        for s in bpy.data.objects[nm].material_slots: s.link = "OBJECT"; s.material = mat("Rev_pele", (0.82, 0.83, 0.86))
    sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "OBJECT"; sh.show_shadows = True
    sh.background_type = "VIEWPORT"; sh.background_color = (0.4, 0.42, 0.45)
    for o in sc.objects:
        if o.type == "MESH" and o.name != "pt" and not o.name.startswith("pt"):
            o.color = (0.82, 0.83, 0.86, 1) if o.name in CONJ else ((0.55, 0.57, 0.6, 1) if o == chao else (0.2, 0.21, 0.24, 1))
sc.render.resolution_x, sc.render.resolution_y = RES
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
C0 = V((0, -0.6, 3.2)); PT = V((0, -0.6, 0.9))
VIS = {"perfil_E": (C0 + V((22, 0, 0.4)), C0, ("o", 15.5), True), "perfil_D": (C0 + V((-22, 0, 0.4)), C0, ("o", 15.5), True), "frente": (C0 + V((0, -22, 0.6)), C0, ("o", 10.0), True),
       "tras": (C0 + V((0, 22, 0.6)), C0, ("o", 10.0), True), "34_E": (C0 + V((12, -12, 4)), C0, 34, True),
       "patas_E": (PT + V((9, -1.5, 0.4)), PT, 34, True), "patas_D": (PT + V((-9, -1.5, 0.4)), PT, 34, True),
       "fixa_D": (V((-60, x_fim / 2 - 2, 4.5)), V((0, x_fim / 2 - 2, 3.0)), ("o", abs(x_fim) + 18), False)}
ARM0 = ARM.location.copy()
for i, (ac_, q) in enumerate(LT):
    usar(ac_); sc.frame_set(q); ARM.location = ARM0 + V((0, Xc[i], 0))
    for q0, qf, o in obs: o.hide_render = not (q0 <= i <= qf + 8)
    bpy.context.view_layer.update()
    for v in VS:
        pos, alvo, l_, seg = VIS[v]
        if seg: pos = pos + V((0, Xc[i], 0)); alvo = alvo + V((0, Xc[i], 0))
        cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
        if isinstance(l_, tuple): cd.type = "ORTHO"; cd.ortho_scale = l_[1]
        else: cd.type = "PERSP"; cd.lens = l_
        sc.render.filepath = os.path.join(OUT, "%s_%s_t%04d.png" % (L, v, i)); bpy.ops.render.render(write_still=True)
json.dump({"linha_do_tempo": ["%s q%d" % e for e in LT], "X": Xc}, open(os.path.join(OUT, "linha_%s.json" % L), "w"))
print("VISTAS_SEQ_OK", L, len(LT), VS, flush=True)
