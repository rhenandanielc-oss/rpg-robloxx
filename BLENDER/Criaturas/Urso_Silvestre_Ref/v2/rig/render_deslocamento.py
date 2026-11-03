"""SIMULACAO NO BLENDER do deslocamento do Urso v2: o modelo anda de fato (-Y) e gira no pivo (Raiz) como o jogo faria,
com camera FIXA, chao em xadrez fino e marcas no chao onde cada pata pousa (a marca fica parada; se a pata escorregar, sai
de cima dela). Grava tambem a posicao de cada pata no mundo (CSV) para o grafico. Velocidades e giro sao PARAMETROS
TECNICOS desta revisao (lidos do manifesto), NAO regras do jogo; o comportamento no Roblox continua pendente.
Uso: blender -b CR_Urso_v2_Anim.blend -P render_deslocamento.py -- <saida_dir> [demo1,demo2]"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix as M
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
QUAIS = A[1].split(",") if len(A) > 1 else None
sc = bpy.context.scene; arm = bpy.data.objects["Urso_Rig"]; FPS = 30
man = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "clipes", "manifesto_clipes.json"), encoding="utf-8"))
V_AND = man["Andar"]["velocidade_studs_s_PROPOSTA"]; V_GAL = man["Corrida"]["velocidade_studs_s_PROPOSTA"]
W_E = man["VirarE"].get("giro_graus_s_PROPOSTA", 60.0); W_D = man["VirarD"].get("giro_graus_s_PROPOSTA", -60.0)
def nq(c): return man[c]["quadros"]                                       # loop: quadros = duracao*fps, sem quadro repetido
# demo: lista de (clipe, repeticoes, v por indice de quadro, giro graus/s)
DEMOS = {
    "Andar": [("Andar", 3, lambda i: V_AND, 0.0)],
    "Corrida": [("Corrida", 5, lambda i: V_GAL, 0.0)],
    "VirarE": [("VirarE", 2, lambda i: 0.0, W_E)],
    "VirarD": [("VirarD", 2, lambda i: 0.0, W_D)],
    "Arrancada_Corrida_Frenagem": [("Arrancada", 1, lambda i: man["Arrancada"]["v_perfil_PARAMETRO"][i], 0.0),
                                   ("Corrida", 2, lambda i: V_GAL, 0.0),
                                   ("Frenagem", 1, lambda i: man["Frenagem"]["v_perfil_PARAMETRO"][i], 0.0)],
}
for o in [o for o in sc.objects if o.type == "EMPTY"]: o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
for o in [o for o in sc.objects if o.type in ("LIGHT", "CAMERA")]: bpy.data.objects.remove(o)
for o in [o for o in sc.objects if o.type == "MESH" and o.parent is None and o.name.startswith("Urso_")]:
    mw = o.matrix_world.copy(); o.parent = arm; o.matrix_parent_inverse = arm.matrix_world.inverted(); o.matrix_world = mw
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.42, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
for nome, en, rot in (("K", 3.0, (0.84, 0, -0.61)), ("R", 2.0, (2.1, 0, 2.8)), ("F", 1.0, (1.13, 0, 1.92))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=200); ch = bpy.context.object; mc = bpy.data.materials.new("Chao"); mc.use_nodes = True
nt = mc.node_tree; b = nt.nodes["Principled BSDF"]; ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 200  # casa de 1 stud
ck.inputs[1].default_value = (0.34, 0.34, 0.34, 1); ck.inputs[2].default_value = (0.26, 0.26, 0.26, 1); nt.links.new(ck.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.95
ch.data.materials.append(mc)
CORES = {"MaoE": (0.9, 0.2, 0.2, 1), "MaoD": (0.95, 0.75, 0.1, 1), "PeE": (0.2, 0.45, 0.95, 1), "PeD": (0.2, 0.85, 0.35, 1)}
MAT = {}
for k, c in CORES.items():
    m = bpy.data.materials.new("M_" + k); m.use_nodes = True; m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = c
    m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = c; m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.6
    MAT[k] = m
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 8; sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 640, 360
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
PIVO = arm.data.bones["Raiz"].head_local.copy()
if not arm.animation_data: arm.animation_data_create()
PATAS = {"MaoE": "MaoE", "MaoD": "MaoD", "PeE": "PeE", "PeD": "PeD"}
for demo, segs in DEMOS.items():
    if QUAIS and demo not in QUAIS: continue
    # roteiro quadro a quadro: (acao, indice), deslocamento acumulado s e angulo
    rot = []; s = 0.0; ang = 0.0
    for si, (clip, rep, vf, wg) in enumerate(segs):
        n = nq(clip) - (1 if not man[clip]["loop"] and si < len(segs) - 1 else 0)   # ultimo quadro = 1o do clipe seguinte
        for r in range(rep):
            for i in range(n):
                try: vf(i)
                except (KeyError, IndexError): print("SEM_PERFIL", demo, clip); break
                rot.append((clip, i, s, ang)); s += vf(i) / FPS; ang += math.radians(wg) / FPS
    # camera fixa enquadrando o trajeto
    ext = rot[-1][2]; giro = any(abs(x[3]) > 1e-6 for x in rot)
    if giro: pos, alvo, lente = V((-17, -17, 15)), V((0, 0, 2.5)), 34
    else:
        meio = -ext / 2; dist = max(24.0, ext * 0.95 + 14)
        pos, alvo, lente = V((-dist, meio - 1.5, 10.0)), V((0, meio - 1.5, 2.2)), 38
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
    for o in [o for o in sc.objects if o.name.startswith("Marca_")]: bpy.data.objects.remove(o)
    # 1a passada: posicoes das patas no mundo e deteccao de pouso (para as marcas)
    def mov(sv, a):
        return M.Translation(PIVO) @ M.Rotation(a, 4, "Z") @ M.Translation(-PIVO) @ M.Translation((0, -sv, 0))
    traj = []
    for qi, (clip, i, sv, a) in enumerate(rot):
        arm.animation_data.action = bpy.data.actions["Urso_" + clip]; arm.matrix_world = mov(sv, a); sc.frame_set(i + 1)
        traj.append({k: arm.matrix_world @ arm.pose.bones[b].head for k, b in PATAS.items()})
    zmin = {k: min(t[k].z for t in traj) for k in PATAS}
    contato = [{k: t[k].z < zmin[k] + 0.04 for k in PATAS} for t in traj]
    linhas = ["quadro,t,clipe,pata,x,y,z,apoio"]
    for qi, t in enumerate(traj):
        for k in PATAS:
            linhas.append("%d,%.4f,%s,%s,%.4f,%.4f,%.4f,%d" % (qi, qi / FPS, rot[qi][0], k, t[k].x, t[k].y, t[k].z, contato[qi][k]))
            if contato[qi][k] and (qi == 0 or not contato[qi - 1][k]):          # inicio de apoio: marca parada no chao
                bpy.ops.mesh.primitive_cylinder_add(radius=0.36, depth=0.02, location=(t[k].x, t[k].y, 0.012), vertices=16)
                mk = bpy.context.object; mk.name = "Marca_%s_%d" % (k, qi); mk.data.materials.append(MAT[k])
    open(os.path.join(OUT, demo + "_patas.csv"), "w", encoding="utf-8").write("\n".join(linhas))
    d = os.path.join(OUT, "video", demo); os.makedirs(d, exist_ok=True)
    for qi, (clip, i, sv, a) in enumerate(rot):
        arm.animation_data.action = bpy.data.actions["Urso_" + clip]; arm.matrix_world = mov(sv, a)
        sc.frame_set(i + 1)
        for mk in [o for o in sc.objects if o.name.startswith("Marca_")]:
            mk.hide_render = int(mk.name.rsplit("_", 1)[1]) > qi
        sc.render.filepath = os.path.join(d, "%04d.png" % qi); bpy.ops.render.render(write_still=True)
    arm.matrix_world = M.Identity(4)
    print("DESLOC", demo, len(rot), "quadros", "trajeto %.2f studs" % ext)
print("DESLOCAMENTO_OK")
