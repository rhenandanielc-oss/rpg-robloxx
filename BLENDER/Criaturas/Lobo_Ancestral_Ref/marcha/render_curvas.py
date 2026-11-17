"""Curvas v32 (16/11/2026): QA no MUNDO + quadros de revisao. O objeto da armadura anda no mundo como o jogo faria: avanca
v (studs/s) para -Y local e gira GIRO graus/s em volta de O_GIRO (AndarCurva*); Virar* fica no lugar (o giro esta na raiz).
QA: deslize da almofada APOIADA no mundo (studs/s) e giro da pata apoiada no mundo (graus por apoio).
Saida: <dir>/<clipe>/f0001.png... (esquerda 3/4 acompanhando, direita vista de cima com as pisadas) + <dir>/qa_curvas.json
Uso: blender -b rig18/Lobo_Ancestral_Anim_Curvas_v32.blend -P marcha/render_curvas.py -- <dir> AndarCurvaE,AndarCurvaD,VirarE,VirarD"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V, Matrix
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True); NOMES = A[1].split(",")
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; PB = arm.pose.bones; BD = arm.data.bones
PES = ("MaoE", "MaoD", "MetatarsoE", "MetatarsoD"); DEDO = {"MaoE": "DedosE", "MaoD": "DedosD", "MetatarsoE": "PeE", "MetatarsoD": "PeD"}
FPS = 30; V_AND = 3.0240; T_AND = 1.2; AP = 0.62; FA = {"MetatarsoE": 0.0, "MaoE": 0.25, "MetatarsoD": 0.5, "MaoD": 0.75}
GIRO = {"AndarCurvaE": 30.0, "AndarCurvaD": -30.0}
Y_MEIO = (BD["MaoE"].tail_local.y + BD["MetatarsoE"].tail_local.y) / 2; O = V((0, Y_MEIO, 0))
for o in sc.objects:
    if o.type == "MESH" and o is not LO: o.hide_render = True
    if o.type == "EMPTY": o.hide_render = True
for pb in PB:
    for c in pb.constraints: c.mute = True
if not arm.animation_data: arm.animation_data_create()
def mundo(nome, t):
    g = GIRO.get(nome)
    if g is None: return Matrix.Identity(4)
    om = math.radians(g); th = om * t
    P = V(((V_AND / om) * (1 - math.cos(th)), -(V_AND / om) * math.sin(th), 0))
    return Matrix.Translation(P) @ Matrix.Translation(O) @ Matrix.Rotation(th, 4, "Z") @ Matrix.Translation(-O)
def acao(nome):
    act = bpy.data.actions["Lobo_" + nome]; arm.animation_data.action = act
    if hasattr(act, "slots") and len(act.slots): arm.animation_data.action_slot = act.slots[0]
    return act
# ---- passada 1: QA e pisadas
qa = {}; pisadas = {}; NQ = {}
for nome in NOMES:
    act = acao(nome); nq0 = int(act.frame_range[1] - act.frame_range[0]) + 1
    loop = bool(act.get("loop", False)); nq = nq0 * 3 if loop else nq0; NQ[nome] = nq
    hist = {k: [] for k in PES}
    for qi in range(nq):
        t = qi / FPS; sc.frame_set(int(qi % nq0) + 1 if loop else qi + 1)
        W = mundo(nome, t)
        for k in PES:
            p = W @ PB[k].tail; d = (W.to_3x3() @ (PB[DEDO[k]].tail - PB[DEDO[k]].head)); ang = math.degrees(math.atan2(d.x, -d.y))
            hist[k].append((t, p.copy(), ang))
    r = {"desliza_max_studs_s": 0.0, "giro_pata_apoiada_max_graus": 0.0}
    pis = []
    for k in PES:
        H = hist[k]
        for i in range(1, len(H)):
            t, p, a = H[i]; tp, pp, ap_ = H[i - 1]
            zmin = min(h[1].z for h in H)
            apoiada = p.z < zmin + 0.02 and pp.z < zmin + 0.02 and abs(p.z - pp.z) < 0.004   # almofada no chao nos 2 quadros
            if nome.startswith("AndarCurva"):
                uk = ((t / T_AND) - FA[k]) % 1.0; ukp = ((tp / T_AND) - FA[k]) % 1.0
                apoiada = uk < AP and ukp < AP and ukp < uk
                if apoiada and abs(uk - AP / 2) < 0.5 / (T_AND * FPS): pis.append((t, k, [round(c, 3) for c in p]))
            if apoiada:
                v_ = (V((p.x, p.y, 0)) - V((pp.x, pp.y, 0))).length * FPS
                r["desliza_max_studs_s"] = max(r["desliza_max_studs_s"], round(v_, 3))
                r["giro_pata_apoiada_max_graus"] = max(r["giro_pata_apoiada_max_graus"], round(abs(((a - ap_ + 180) % 360) - 180) * FPS, 2))
    if not nome.startswith("AndarCurva"):
        for k in PES: pis.append((0.0, k, [round(c, 3) for c in hist[k][-1][1]]))
    r["giro_pata_apoiada_max_graus"] = round(r["giro_pata_apoiada_max_graus"] / FPS, 3)   # graus por quadro
    qa[nome] = r; pisadas[nome] = sorted(pis, key=lambda z: z[0]); print("QA", nome, json.dumps(r), flush=True)
json.dump(qa, open(os.path.join(OUT, "qa_curvas.json"), "w"), indent=1)
if os.environ.get("QA_SO"): print("QA_SO_OK"); sys.exit(0)
# ---- cena de render
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 12
sc.render.resolution_x, sc.render.resolution_y = 640, 720
w = bpy.data.worlds.new("Wr"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.70, 0.78, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
sol = bpy.data.objects.new("SolR", bpy.data.lights.new("SolR", "SUN")); sc.collection.objects.link(sol); sol.data.energy = 3.5
sol.rotation_euler = (math.radians(40), 0, math.radians(-35))
bpy.ops.mesh.primitive_plane_add(size=120); chao = bpy.context.object
mat = bpy.data.materials.new("ChaoR"); mat.use_nodes = True; nt = mat.node_tree; bs = nt.nodes["Principled BSDF"]
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 120.0
ck.inputs["Color1"].default_value = (0.22, 0.24, 0.14, 1); ck.inputs["Color2"].default_value = (0.13, 0.15, 0.08, 1)
nt.links.new(ck.outputs["Color"], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.95; chao.data.materials.append(mat)
mpis = bpy.data.materials.new("Pisada"); mpis.use_nodes = True; mpis.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.85, 0.75, 0.2, 1)
cam = bpy.data.objects.new("CamR", bpy.data.cameras.new("CamR")); sc.collection.objects.link(cam); sc.camera = cam
def olhar(o, alvo): o.rotation_euler = (alvo - o.location).to_track_quat("-Z", "Y").to_euler()
def numpy_img(path): im = bpy.data.images.load(path); a = np.array(im.pixels[:]).reshape(im.size[1], im.size[0], 4); bpy.data.images.remove(im); return a
for nome in NOMES:
    acao(nome); act = bpy.data.actions["Lobo_" + nome]; nq0 = int(act.frame_range[1] - act.frame_range[0]) + 1
    loop = bool(act.get("loop", False)); nq = NQ[nome]
    marcas = []
    d = os.path.join(OUT, nome); os.makedirs(d, exist_ok=True)
    tpis = [(tt, k, V(p)) for tt, k, p in pisadas[nome]] if nome.startswith("AndarCurva") else []
    centro_cima = sum((p for _, _, p in tpis), V((0, 0, 0))) / max(1, len(tpis)) if tpis else V((0, Y_MEIO, 0))
    for qi in range(nq):
        t = qi / FPS; sc.frame_set(int(qi % nq0) + 1 if loop else qi + 1)
        Wm = mundo(nome, t); arm.matrix_world = Wm
        # pisadas ja feitas ate t (so curvas)
        while len(marcas) < len(tpis) and tpis[len(marcas)][0] <= t + 1e-6:
            _, k, p = tpis[len(marcas)]
            bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.02, location=(p.x, p.y, 0.01)); m = bpy.context.object
            m.data.materials.append(mpis); marcas.append(m)
        cen = Wm @ V((0, Y_MEIO, 3.0))
        cam.data.lens = 35; cam.location = cen + V((11.0, -9.0, 6.5)); olhar(cam, cen + V((0, 0, -0.8)))
        sc.render.filepath = os.path.join(d, "_a.png"); bpy.ops.render.render(write_still=True); a_ = numpy_img(sc.render.filepath)
        cam.data.lens = 30; cam.location = centro_cima + V((0, 0, 24.0)); cam.rotation_euler = (0, 0, 0)
        sc.render.filepath = os.path.join(d, "_b.png"); bpy.ops.render.render(write_still=True); b_ = numpy_img(sc.render.filepath)
        img = bpy.data.images.new("q", 1280, 720); img.pixels[:] = np.concatenate([a_, b_], axis=1).ravel()
        img.filepath_raw = os.path.join(d, "f%04d.png" % (qi + 1)); img.file_format = "PNG"; img.save(); bpy.data.images.remove(img)
    for m in marcas: bpy.data.objects.remove(m)
    arm.matrix_world = Matrix.Identity(4)
print("RENDER_OK", json.dumps(qa))
