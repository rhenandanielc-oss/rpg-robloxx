"""Renders dos clipes do cervo (adaptado do Bufalo, 61_render_clipes.py): o modelo ANDA no mundo a v (PROPOSTA) sobre um
chao xadrez de 0,1 u (escorregao visivel), camera acompanha; marca vermelha sob o casco apoiado. Mede, quadro a quadro,
o estiramento da pele (aresta posada / repouso) e o ponto mais baixo dos cascos.
Uso: blender -b rig/clipes_L1/Cervo_Clipes_L1.blend -P rig/render_clipes_cervo.py -- <dir_saida> <clipe> [passo=1] [repete=1] [limite_quadros]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); CLIPE = A[1]; PASSO = int(A[2]) if len(A) > 2 else 1
REPETE = int(A[3]) if len(A) > 3 else 1
LIMITE = int(A[4]) if len(A) > 4 else 10 ** 9          # no maximo N quadros (poupa o PC)
sc = bpy.context.scene; arm = bpy.data.objects["Cervo_Rig"]; MALHAS = [bpy.data.objects["Cervo_Corpo"], bpy.data.objects["Cervo_Cabeca"]]
act = bpy.data.actions["Cervo_" + CLIPE]; arm.animation_data_create(); arm.animation_data.action = act
vel = float(act.get("velocidade_PROPOSTA", 0.0)); nq = int(act.frame_range[1] - act.frame_range[0]) + 1; FPS = 30
GIRO = math.radians(float(act.get("giro_graus_s_PROPOSTA", 0.0))); PIVO = arm.data.bones["Raiz"].head_local.copy()
VP = list(act["v_perfil"]) if "v_perfil" in act else None              # lote 2: velocidade variavel (arrancada/frenagem/transicoes)
def mundo(qi):
    pos = V((0, 0, 0)); h = 0.0
    for i in range(qi):
        v_ = 0.5 * (VP[i % nq] + VP[(i + 1) % nq]) if VP else vel
        h_m = h + 0.5 * GIRO / FPS; pos += V((math.sin(h_m), -math.cos(h_m), 0)) * v_ / FPS; h += GIRO / FPS
    return pos, h
for o in sc.objects:
    if o.type == "MESH" and o not in MALHAS: o.hide_render = True
for o in MALHAS:
    if o.parent != arm: o.parent = arm
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
try: sc.eevee.taa_render_samples = 16
except Exception: pass
w = bpy.data.worlds.new("C"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.58, 0.55, 1); sc.world = w
sol = bpy.data.lights.new("S", "SUN"); sol.energy = 2.4; so = bpy.data.objects.new("S", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(40), 0, math.radians(-55))
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0)); ch = bpy.context.active_object; ch.name = "ChaoXadrez"
m = bpy.data.materials.new("Xadrez"); m.use_nodes = True; nt = m.node_tree; ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 200   # 0,1 u por casa
ck.inputs["Color1"].default_value = (0.42, 0.40, 0.37, 1); ck.inputs["Color2"].default_value = (0.55, 0.53, 0.49, 1)
nt.links.new(ck.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"]); nt.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1; ch.data.materials.append(m)
cd = bpy.data.cameras.new("Q"); cam = bpy.data.objects.new("Q", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 40
VISTAS = {"lado": (0, 6, 5.0), "34": (40, 12, 4.8)}
APOIO = json.loads(act.get("apoio_json", "{}")); MARC = {}
if APOIO:
    mk = bpy.data.materials.new("Apoio"); mk.use_nodes = True; mk.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.08, 0.05, 1)
    for k in APOIO:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.004); o_ = bpy.context.active_object; o_.data.materials.append(mk); MARC[k] = o_
ED = [np.array([tuple(e.vertices) for e in o.data.edges]) for o in MALHAS]
def malha(o):
    dg = bpy.context.evaluated_depsgraph_get(); ev = o.evaluated_get(dg); mm = ev.to_mesh()
    c = np.empty(len(mm.vertices) * 3); mm.vertices.foreach_get("co", c); c = c.reshape(-1, 3); ev.to_mesh_clear()
    mw = np.array(o.matrix_world); return c @ mw[:3, :3].T + mw[:3, 3]
arm.animation_data.action = None; arm.location = (0, 0, 0)
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
L0 = []
for o, ed in zip(MALHAS, ED): c0 = malha(o); L0.append(np.linalg.norm(c0[ed[:, 0]] - c0[ed[:, 1]], axis=1))
arm.animation_data.action = act
met = []
for qi in range(0, min(nq * REPETE, LIMITE), PASSO):
    sc.frame_set(int(act.frame_range[0]) + qi % nq); pos, h = mundo(qi)
    arm.matrix_world = Matrix.Translation(pos + PIVO) @ Matrix.Rotation(h, 4, "Z") @ Matrix.Translation(-PIVO); bpy.context.view_layer.update()
    for k, o_ in MARC.items():
        h_ = arm.matrix_world @ arm.pose.bones[k].tail; o_.location = (h_.x, h_.y, 0.002); o_.hide_render = not APOIO[k][min(qi % nq, len(APOIO[k]) - 1)]
    est = []; zc = 9.0
    for o, ed, l0 in zip(MALHAS, ED, L0):
        C = malha(o); est.append(np.linalg.norm(C[ed[:, 0]] - C[ed[:, 1]], axis=1) / np.maximum(l0, 1e-6)); zc = min(zc, float(C[:, 2].min()))
    ra = np.concatenate(est)
    met.append({"q": qi, "estica_max": round(float(ra.max()), 3), "estica_p99": round(float(np.percentile(ra, 99)), 3), "arestas_>2x": int((ra > 2).sum()), "pele_z_min": round(zc, 4)})
    for vista, (az, el, dist) in VISTAS.items():
        alvo = pos + V((0, 0, 0.85)) + V((math.sin(h), -math.cos(h), 0)) * 0.0; a_ = math.radians(az) + h
        d = V((-math.cos(a_) * math.cos(math.radians(el)), -math.sin(a_) * math.cos(math.radians(el)), math.sin(math.radians(el))))
        cam.location = alvo + d * dist; cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
        pasta = os.path.join(OUT, CLIPE, vista); os.makedirs(pasta, exist_ok=True)
        sc.render.resolution_x, sc.render.resolution_y = 480, 380; sc.render.filepath = os.path.join(pasta, "q%03d.png" % qi); bpy.ops.render.render(write_still=True)
res = {"clipe": CLIPE, "velocidade_PROPOSTA": vel, "quadros": nq, "estica_max": max(x["estica_max"] for x in met), "estica_p99_max": max(x["estica_p99"] for x in met),
       "arestas_>2x_max": max(x["arestas_>2x"] for x in met), "pele_z_min": min(x["pele_z_min"] for x in met), "por_quadro": met}
json.dump(res, open(os.path.join(OUT, CLIPE, "metricas.json"), "w"), indent=1)
print("RENDER_CLIPE", CLIPE, {k: v for k, v in res.items() if k != "por_quadro"})
