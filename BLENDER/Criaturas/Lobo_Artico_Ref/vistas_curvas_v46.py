"""v46b: render das curvas andando (Workbench, leve: resolucao baixa, 1 quadro sim 1 nao = 15 q/s, pausa entre quadros).
Linha do tempo = linha_curvas_v46.linha_seq (sequencia de clipes com a curva externa de cada clipe) ou, com --antes, o que o
Controle r10e faz hoje: o MESMO perfil de giro por quadro aplicado ao pivo (giro em volta do proprio pivo) com o Andar RETO tocando.
Chao em GRADE (1 stud; linhas finas a cada 0,5), SETA de rumo no chao sobre o pivo, TRAJETORIA do pivo (pontos laranja) e
RASTROS das 4 patas (pontos dos vertices da sola apoiados; DE azul, DD vermelho, TE verde, TD amarelo; ficam no chao ate o fim).
Cameras: topo (FIXA, ortografica, enquadra o caminho inteiro), c34 (FIXA, perspectiva, enquadra o caminho inteiro);
perfil_E / perfil_D / frente / tras / close_E / close_D SEGUEM so a POSICAO do pivo (nao giram: o giro do corpo aparece).
Uso: blender -b anim_v46b/CR_LoboArtico_Anim.blend -P vistas_curvas_v46.py -- <dir> <LOD> <cenario> <vistas,...> [--antes] [res=LxA] [passo=2]"""
import bpy, sys, os, json, math, bmesh, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector as V, Matrix
import linha_curvas_v46 as LC
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); L, CN = a[1], a[2]; VS = a[3].split(","); ANTES = "--antes" in a
RES = next((tuple(int(c) for c in o[4:].split("x")) for o in a if o.startswith("res=")), (560, 360)); PASSO = next((int(o[6:]) for o in a if o.startswith("passo=")), 2)
os.makedirs(OUT, exist_ok=True); sc = bpy.context.scene; SRC = os.path.dirname(bpy.data.filepath)
VJ = json.load(open(os.path.join(SRC, "curvas_v46b.json")))["acoes"]
if os.path.exists(os.path.join(SRC, "partida_v48.json")): VJ.update(json.load(open(os.path.join(SRC, "partida_v48.json")))["acoes"]); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
if os.path.exists(os.path.join(SRC, "partida_v50.json")): VJ.update(json.load(open(os.path.join(SRC, "partida_v50.json")))["acoes"])   # v50
if os.path.exists(os.path.join(SRC, "partida_v51.json")): VJ.update(json.load(open(os.path.join(SRC, "partida_v51.json")))["acoes"])   # v51
ARM = bpy.data.objects["LoboArtico_Rig"]; P = ARM.pose.bones
for pb in P: pb.rotation_mode = "QUATERNION"
for _m in ("trote", "corrida"):
    _pm = os.path.join(SRC, "curvas_%s_v49.json" % _m)
    if os.path.exists(_pm): VJ.update(json.load(open(_pm))["acoes"])
_g = next((m for m in ("Trote", "Corrida") if CN.startswith(m.lower())), None)
G = dict(json.load(open(os.path.join(SRC, "clipes_v21.json")))["marchas"][_g], nome=_g) if _g else None
RETO = _g or "Andar"; NQR = int(round(G["T"] * 30)) if G else LC.NQ
LT = LC.linha_seq(CN, VJ, G=G)
if ANTES:                                                      # Controle r10e: Andar reto + pivo girando em volta de si mesmo
    psi = 0.0; pos = V((0, 0, 0)); qm = 0
    for e in LT:
        e["M"] = Matrix.Translation(pos) @ Matrix.Rotation(psi, 4, "Z"); e["psi"] = math.degrees(psi); e["pos"] = pos.copy()
        if e["clipe"] != "Repouso":
            e["mix"] = [("Repouso", m_[1], m_[2]) if m_[0] == "Repouso" else (RETO, qm % NQR, m_[2]) for m_ in e["mix"]]; qm += 1
        dt = 1.0 / LC.FPS; om = math.radians(e["omega"]); pm = psi + om * dt / 2
        pos = pos + V((math.sin(pm), -math.cos(pm), 0)) * e["v"] * dt; psi += om * dt
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Marca", "LOW_Cristais"], "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}[L]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ
ARM.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
xs = [e["pos"].x for e in LT]; ys = [e["pos"].y for e in LT]; cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
ext = max(max(xs) - min(xs), max(ys) - min(ys)) + 12; H = int(ext / 2) + 2
gm = bpy.data.meshes.new("grade"); bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=H); bm.to_mesh(gm); bm.free(); chao = bpy.data.objects.new("Chao", gm); chao.location = (cx, cy, -0.004); sc.collection.objects.link(chao)
gm = bpy.data.meshes.new("linhas"); bm = bmesh.new()
for i in range(-2 * H, 2 * H + 1):
    w = 0.01 if i % 2 else 0.025; c = i * 0.5
    for vs in (((cx + c - w, cy - H, 0), (cx + c + w, cy - H, 0), (cx + c + w, cy + H, 0), (cx + c - w, cy + H, 0)),
               ((cx - H, cy + c - w, 0.0005), (cx + H, cy + c - w, 0.0005), (cx + H, cy + c + w, 0.0005), (cx - H, cy + c + w, 0.0005))):
        bm.faces.new([bm.verts.new(p) for p in vs])
bm.to_mesh(gm); bm.free(); go = bpy.data.objects.new("Grade", gm); sc.collection.objects.link(go)
sm = bpy.data.meshes.new("seta"); bm = bmesh.new()
for vs in (((-0.1, 0, 0.02), (0.1, 0, 0.02), (0.1, -2.6, 0.02), (-0.1, -2.6, 0.02)), ((-0.35, -2.6, 0.02), (0.35, -2.6, 0.02), (0, -3.3, 0.02))):
    bm.faces.new([bm.verts.new(V(p)) for p in vs])
bm.to_mesh(sm); bm.free(); seta = bpy.data.objects.new("Seta", sm); sc.collection.objects.link(seta)
C = bpy.data.objects[L + "_Corpo"]; me = C.data; Mw0 = C.matrix_world.copy()
patas = {k: [v.index for v in me.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8] for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"])}
CORK = {"DE": (0.15, 0.4, 1.0), "DD": (1.0, 0.15, 0.1), "TE": (0.1, 0.85, 0.2), "TD": (1.0, 0.85, 0.05)}
CACHE = {}
def basis(acao, q):
    if (acao, q) not in CACHE:
        ac = bpy.data.actions[acao]; ARM.animation_data.action = ac
        if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
        sc.frame_set(int(ac.frame_range[0]) + q); CACHE[(acao, q)] = {pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P}
        ARM.animation_data.action = None
    return CACHE[(acao, q)]
def posar(e):
    ARM.animation_data.action = None; LC.aplicar(P, None, None, e["mix"], basis); bpy.context.view_layer.update()
esf = bpy.data.meshes.new("m"); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=5, radius=0.09); bm.to_mesh(esf); bm.free()
traj = bpy.data.meshes.new("t"); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=4, radius=0.08); bm.to_mesh(traj); bm.free(); obs = []
for k, ids in patas.items():                                   # rastro: so os quadros apoiados, 1 a cada 2
    segs, cur = [], []
    for i, e in enumerate(LT):
        if e["apoio"][k]: cur.append(i)
        elif cur: segs.append(cur); cur = []
    if cur: segs.append(cur)
    for sg in segs:
        posar(LT[sg[len(sg) // 2]]); dg = bpy.context.evaluated_depsgraph_get(); ev = C.evaluated_get(dg); m = ev.to_mesh()
        zm = min((Mw0 @ m.vertices[i].co).z for i in ids); pts = [i for i in ids if (Mw0 @ m.vertices[i].co).z < zm + 0.03]; ev.to_mesh_clear()
        for j in sg[::2]:
            posar(LT[j]); dg = bpy.context.evaluated_depsgraph_get(); ev = C.evaluated_get(dg); m = ev.to_mesh()
            vis = [Mw0 @ m.vertices[i].co for i in pts]; vis = [p for p in vis if p.z < zm + 0.06]; ev.to_mesh_clear()
            if not vis: continue
            c = LT[j]["M"] @ (sum(vis, V()) / len(vis)); o = bpy.data.objects.new("pt", esf); o.location = (c.x, c.y, 0.02); o.color = (*CORK[k], 1)
            sc.collection.objects.link(o); obs.append((j, o))
for i, e in enumerate(LT[::3]):
    o = bpy.data.objects.new("tr", traj); o.location = (e["pos"].x, e["pos"].y, 0.015); o.color = (1.0, 0.55, 0.1, 1); sc.collection.objects.link(o); obs.append((i * 3, o))
def mat(nome, cor):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome); m.diffuse_color = (*cor, 1); return m
for nm in CONJ:
    for s_ in bpy.data.objects[nm].material_slots: s_.link = "OBJECT"; s_.material = mat("Rev_pele", (0.82, 0.83, 0.86))
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "OBJECT"; sh.show_shadows = True
sh.background_type = "VIEWPORT"; sh.background_color = (0.4, 0.42, 0.45)
for o in sc.objects:
    if o.type == "MESH" and o.name not in ("pt",) and not o.name.startswith(("pt", "tr")):
        o.color = (0.82, 0.83, 0.86, 1) if o.name in CONJ else ((0.55, 0.57, 0.6, 1) if o == chao else ((0.95, 0.5, 0.1, 1) if o == seta else (0.25, 0.26, 0.29, 1)))
sc.render.resolution_x, sc.render.resolution_y = RES; sc.render.resolution_percentage = 100
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
CTR = V((cx, cy, 0)); R_ = ext / 2
FIXA = {"topo": (CTR + V((0, 0, 60)), CTR, ("o", ext * 1.0)), "c34": (CTR + V((R_ * 1.1, -R_ * 1.1, R_ * 0.9)), CTR + V((0, 0, 0.5)), 30)}
SEGUE = {"perfil_E": (V((22, -1.5, 3.0)), ("o", 17.0)), "perfil_D": (V((-22, -1.5, 3.0)), ("o", 17.0)), "frente": (V((0, -24, 3.0)), ("o", 15.0)),
         "tras": (V((0, 22, 3.0)), ("o", 15.0)), "close_E": (V((11, -2.5, 1.4)), 28), "close_D": (V((-11, -2.5, 1.4)), 28)}
pre = ("ANTES_" if ANTES else "V46B_") + "%s_%s_" % (L, CN)
for i in range(0, len(LT), PASSO):
    e = LT[i]; posar(e); ARM.matrix_world = e["M"]; seta.matrix_world = e["M"]
    for j, o in obs: o.hide_render = j > i
    bpy.context.view_layer.update()
    for v in VS:
        if v in FIXA: pos, alvo, l_ = FIXA[v]
        else:
            off, l_ = SEGUE[v]; base = e["pos"] + V((0, -1.0, 0)); pos = base + off; alvo = base + V((0, 0, 2.4 if not v.startswith("close") else 1.2)); pos.z = off.z
        cam.location = pos; sh.show_shadows = v != "topo"
        cam.rotation_euler = (0, 0, 0) if v == "topo" else (alvo - pos).to_track_quat("-Z", "Y").to_euler()
        if isinstance(l_, tuple): cd.type = "ORTHO"; cd.ortho_scale = l_[1]
        else: cd.type = "PERSP"; cd.lens = l_
        sc.render.filepath = os.path.join(OUT, v, pre + "%s_t%04d.png" % (v, i // PASSO)); bpy.ops.render.render(write_still=True)
        time.sleep(0.12)                                        # pedido do usuario: leve, mesmo que demore
json.dump([{"q": i, "clipe": LT[i]["clipe"], "qc": LT[i]["q"], "omega": LT[i]["omega"], "psi": round(LT[i]["psi"], 2), "pos": [round(x, 3) for x in LT[i]["pos"]][:2]}
           for i in range(0, len(LT), PASSO)], open(os.path.join(OUT, pre + "linha.json"), "w"))
print("VISTAS_V46_OK", L, CN, "ANTES" if ANTES else "v46b", len(LT), VS, flush=True)
