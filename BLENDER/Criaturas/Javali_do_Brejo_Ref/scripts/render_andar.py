"""(Copia de Javali_Silvestre_Ref/rig/render_javali.py; so muda o prefixo de nomes via JAVALI_PFX.) Render de REVISAO dos clipes do javali com CAMERAS FIXAS (adaptado de Cervo_do_Bosque_Ref/rig/render_fixo_cervo.py).
As acoes sao NO LUGAR; aqui um CONTROLADOR DE DEMONSTRACAO (externo, so para o render) move o objeto da armature no mundo
integrando a velocidade gravada na acao (velocidade_PROPOSTA ou v_perfil) e o giro (giro_graus_s_PROPOSTA). Camera nao segue.
Piso quadriculado de 0,1 u + postes fixos a cada 0,25 u (vermelho a cada 0,5 u); disco vermelho sob o casco em apoio.
Aceita CADEIA de clipes (transicoes): "ParadoParaAndar+Andar:0.9" = clipe inteiro e depois 0,9 s do Andar.
Mede: avanco da Raiz, avanco por ciclo, deriva no MUNDO do casco em apoio, menor z da pele, salto de pose entre clipes.
Uso: blender -b rig/clipes_LA/Javali_Clipes_LA.blend -P rig/render_javali.py -- <dir_saida> <cadeia> <rotulo> [passo=1] [ciclo_s]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); CADEIA = A[1]; ROT = A[2]
PASSO = int(A[3]) if len(A) > 3 else 1; T_CICLO = float(A[4]) if len(A) > 4 else 0.0
PFX = os.environ.get("JAVALI_PFX", "JavaliBrejo")   # Javali (base) ou JavaliBrejo (variante)
sc = bpy.context.scene; FPS = 30; arm = bpy.data.objects[PFX + "_Rig"]
MALHAS = [bpy.data.objects[PFX + "_Corpo"], bpy.data.objects[PFX + "_Cabeca"]]
arm.animation_data_create(); PIVO = arm.data.bones["Raiz"].head_local.copy()
# ---- linha do tempo: (acao, quadro local) por quadro global
SEG = []; LINHA = []
for item in CADEIA.split("+"):
    nome, _, seg = item.partition(":"); nome, _, off = nome.partition("@"); off = int(off or 0)   # Andar@1 = comeca no q1 (o q0
    act = bpy.data.actions[PFX + "_" + nome]; nq = int(act.frame_range[1] - act.frame_range[0]) + 1   # ja foi o ultimo da transicao)
    loop = bool(act.get("loop", False)); n = int(round(float(seg) * FPS)) if seg else nq - off
    SEG.append((nome, len(LINHA), n))
    for q in range(off, off + n): LINHA.append((act, q % nq if loop else min(q, nq - 1), nome))
TOTAL = len(LINHA)
def vel(act, q):
    vp = act.get("v_perfil")
    return float(vp[min(q, len(vp) - 1)]) if vp else float(act.get("velocidade_PROPOSTA", 0.0))
POS = [V((0, 0, 0))]; HEAD = [0.0]
for i in range(TOTAL):                                   # trapezio da velocidade; giro integrado (frente = -Y)
    a0, q0, _ = LINHA[i]; a1, q1, _ = LINHA[min(i + 1, TOTAL - 1)]
    v_ = 0.5 * (vel(a0, q0) + vel(a1, q1)) if i + 1 < TOTAL else vel(a0, q0)
    g_ = math.radians(float(a0.get("giro_graus_s_PROPOSTA", 0.0))) / FPS; hm = HEAD[-1] + 0.5 * g_
    POS.append(POS[-1] + V((math.sin(hm), -math.cos(hm), 0)) * v_ / FPS); HEAD.append(HEAD[-1] + g_)
def mw(i): return Matrix.Translation(POS[i] + PIVO) @ Matrix.Rotation(HEAD[i], 4, "Z") @ Matrix.Translation(-PIVO)
for o in sc.objects:
    if o.type == "MESH" and o not in MALHAS: o.hide_render = True
for o in MALHAS:
    if o.parent != arm: o.parent = arm
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False
try: sc.eevee.taa_render_samples = 16
except Exception: pass
w = bpy.data.worlds.new("C"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.60, 0.57, 1); sc.world = w
sol = bpy.data.lights.new("S", "SUN"); sol.energy = 2.4; so = bpy.data.objects.new("S", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(40), 0, math.radians(-55))
def mat(nome, cor):
    m = bpy.data.materials.new(nome); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*cor, 1); b.inputs["Roughness"].default_value = 1; return m
P = np.array([p[:] for p in POS]); cx, cy = float((P[:, 0].min() + P[:, 0].max()) / 2), float((P[:, 1].min() + P[:, 1].max()) / 2) + PIVO.y
span = float(max(np.ptp(P[:, 1]), np.ptp(P[:, 0]))) + 1.6
if os.environ.get("JAVALI_CAM_FIX"):                # antes x depois: mesma camera (centro y e vao fixos) nas duas versoes
    cy, span = [float(x) for x in os.environ["JAVALI_CAM_FIX"].split(",")]; cx = 0.0
bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, cy, 0)); ch = bpy.context.active_object; ch.scale = (span + 3, span + 3, 1)
mp = bpy.data.materials.new("Xadrez"); mp.use_nodes = True; nt = mp.node_tree; ck = nt.nodes.new("ShaderNodeTexChecker")
tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Generated"], ck.inputs["Vector"]); ck.inputs["Scale"].default_value = (span + 3) / 0.2          # casa de 0,1 u (o checker tem 2 casas por unidade de escala)
ck.inputs["Color1"].default_value = (0.42, 0.40, 0.37, 1); ck.inputs["Color2"].default_value = (0.56, 0.54, 0.50, 1)
nt.links.new(ck.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"]); nt.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1; ch.data.materials.append(mp)
M_R, M_B = mat("PosteV", (0.80, 0.08, 0.05)), mat("PosteB", (0.92, 0.92, 0.90))
y = cy + span / 2; i = 0
while y > cy - span / 2:                                  # postes fixos ao lado do caminho (lado de fora da camera lateral)
    big = i % 2 == 0
    bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.20 if big else 0.12, location=(float(P[:, 0].max()) + 0.32, y, 0.10 if big else 0.06))
    bpy.context.active_object.data.materials.append(M_R if big else M_B); y -= 0.25; i += 1
mk = mat("Apoio", (0.9, 0.08, 0.05)); MARC = {}
for k in ("QuartelaE", "QuartelaD", "QuartelaTrasE", "QuartelaTrasD"):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.028, depth=0.002); o_ = bpy.context.active_object; o_.data.materials.append(mk); MARC[k] = o_
cd = bpy.data.cameras.new("Q"); cam = bpy.data.objects.new("Q", cd); sc.collection.objects.link(cam); sc.camera = cam
d = max(2.4, span * 1.2)
VISTAS = {"lado_fixo": ((cx - d, cy, 0.42), (cx, cy, 0.30), 35, (1100, 420)),
          "34_fixo": ((cx - 0.62 * d, cy - 0.78 * d, 0.30 + 0.42 * d), (cx, cy, 0.28), 35, (960, 600))}
ED = [np.array([tuple(e.vertices) for e in o.data.edges]) for o in MALHAS]
def malha(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); mm = ev.to_mesh()
    c = np.empty(len(mm.vertices) * 3); mm.vertices.foreach_get("co", c); c = c.reshape(-1, 3); ev.to_mesh_clear()
    m_ = np.array(o.matrix_world); return c @ m_[:3, :3].T + m_[:3, 3]
arm.animation_data.action = None; arm.matrix_world = Matrix.Identity(4)
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update(); L0 = []
for o, ed in zip(MALHAS, ED): c0 = malha(o); L0.append(np.linalg.norm(c0[ed[:, 0]] - c0[ed[:, 1]], axis=1))
med = {"cadeia": CADEIA, "rotulo": ROT, "quadros": TOTAL, "fps": FPS, "segmentos": SEG,
       "controlador": "DEMONSTRACAO externo: arm.matrix_world integra v/giro gravados na acao; a acao e no lugar (Raiz sem avanco)",
       "raiz_mundo": [], "apoios": {}, "pele_z_min": 9.0, "estica_max": 0.0, "salto_entre_clipes_graus": []}
ap_ini, mundo_ini, deriva = {}, {}, {k: [] for k in MARC}
prev_pose = None
for qi in range(TOTAL):
    act, q, nome = LINHA[qi]; arm.animation_data.action = act; sc.frame_set(int(act.frame_range[0]) + q)
    arm.matrix_world = mw(qi); bpy.context.view_layer.update()
    pose = {pb.name: pb.matrix_basis.to_quaternion() for pb in arm.pose.bones}
    if prev_pose and qi in [s[1] for s in SEG]:
        med["salto_entre_clipes_graus"].append((qi, round(max(math.degrees(pose[n].rotation_difference(prev_pose[n]).angle) for n in pose), 3)))
    prev_pose = pose
    med["raiz_mundo"].append([round(c, 4) for c in (arm.matrix_world @ arm.pose.bones["Raiz"].head)[:2]])
    APO = json.loads(act.get("apoio_json", "{}"))
    for k in MARC:
        apo = bool(APO[k][min(q, len(APO[k]) - 1)]) if k in APO else True; pw = arm.matrix_world @ arm.pose.bones[k].head
        MARC[k].location = (pw.x, pw.y, 0.001); MARC[k].hide_render = not apo
        if apo and k not in ap_ini: ap_ini[k] = qi; mundo_ini[k] = pw.copy()
        elif apo: deriva[k].append(round((pw - mundo_ini[k]).to_2d().length, 4))
        elif k in ap_ini:
            med["apoios"].setdefault(k, []).append({"q_ini": ap_ini[k], "q_fim": qi - 1, "deriva_max": max(deriva[k]) if deriva[k] else 0.0})
            del ap_ini[k]; deriva[k] = []
    est = []
    for o, ed, l0 in zip(MALHAS, ED, L0):
        C = malha(o); est.append(np.linalg.norm(C[ed[:, 0]] - C[ed[:, 1]], axis=1) / np.maximum(l0, 1e-6)); med["pele_z_min"] = min(med["pele_z_min"], round(float(C[:, 2].min()), 4))
    ra = np.concatenate(est); ra[np.concatenate(L0) < 0.003] = 1.0             # micro-arestas (< 3 mm) da decimacao = ruido
    med["estica_max"] = max(med["estica_max"], round(float(ra.max()), 3)); med["estica_p99_max"] = max(med.get("estica_p99_max", 0.0), round(float(np.percentile(ra, 99)), 3))
    med["arestas_>2x_max_por_quadro"] = max(med.get("arestas_>2x_max_por_quadro", 0), int((ra > 2).sum()))
    if qi % PASSO: continue
    for vista, (loc, alvo, lente, res) in VISTAS.items():
        cam.location = loc; cam.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
        sc.render.resolution_x, sc.render.resolution_y = res; pasta = os.path.join(OUT, ROT, vista); os.makedirs(pasta, exist_ok=True)
        sc.render.filepath = os.path.join(pasta, "q%03d.png" % qi); bpy.ops.render.render(write_still=True)
for k in list(ap_ini):
    med["apoios"].setdefault(k, []).append({"q_ini": ap_ini[k], "q_fim": TOTAL - 1, "deriva_max": max(deriva[k]) if deriva[k] else 0.0})
r0, r1 = med["raiz_mundo"][0], med["raiz_mundo"][-1]; dist = math.hypot(r1[0] - r0[0], r1[1] - r0[1])
med["avanco_total_u"] = round(dist, 4); med["duracao_s"] = round(TOTAL / FPS, 4); med["velocidade_media"] = round(dist / max(TOTAL - 1, 1) * FPS, 4)
if T_CICLO: med["avanco_por_ciclo_u"] = round(dist / ((TOTAL - 1) / FPS / T_CICLO), 4)
med["deriva_max_casco_apoiado"] = max((a["deriva_max"] for l in med["apoios"].values() for a in l), default=0.0)
json.dump(med, open(os.path.join(OUT, ROT, "medidas.json"), "w"), indent=1)
print("MEDIDAS", ROT, {k: v for k, v in med.items() if k not in ("raiz_mundo", "apoios")})
