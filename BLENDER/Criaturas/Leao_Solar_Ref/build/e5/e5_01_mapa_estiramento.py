"""E5 inspecao: mapa de estiramento por face (area posada/repouso) nas poses da pata dianteira, pintado sobre a malha.
Uso: blender -b E4b_r2.blend -P e5_01_mapa_estiramento.py -- <juntas.json> <saida_dir> [poses]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]; J = json.load(open(A[0])); OUT = os.path.abspath(A[1]); os.makedirs(OUT, exist_ok=True)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "e4b_r2", "r2_poses_lib.py"), encoding="utf-8").read())
sc = bpy.context.scene; me = OB.data
TRI = np.array([(p.vertices[0], p.vertices[k], p.vertices[k + 1], p.index) for p in me.polygons for k in range(1, len(p.vertices) - 1)])
def areas(P): return 0.5 * np.linalg.norm(np.cross(P[TRI[:, 1]] - P[TRI[:, 0]], P[TRI[:, 2]] - P[TRI[:, 0]]), axis=1)
A0 = areas(CO0)
ca = me.color_attributes.new("_estir", "BYTE_COLOR", "CORNER")
mat = bpy.data.materials.new("_estir"); mat.use_nodes = True; nt = mat.node_tree; at = nt.nodes.new("ShaderNodeVertexColor"); at.layer_name = "_estir"
em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(at.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs[0])
for s in OB.material_slots: s.link = "OBJECT"; s.material = mat
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
def vista(nome, alvo, az, el, dist):
    alvo = Vector(alvo)
    cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = sc.render.resolution_y = 560; sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
cor_loop = np.zeros((len(me.loops), 4)); cor_loop[:, 3] = 1
for nome in (A[2].split(",") if len(A) > 2 else ["ombro_avanco", "passo_dianteiro"]):
    zerar(); POSE[nome](); P = posado(); r = areas(P) / np.maximum(A0, 1e-9)
    rf = np.ones(len(me.polygons)); np.maximum.at(rf, TRI[:, 3], r)
    t = np.clip((rf - 1) / 2.0, 0, 1)   # 1 = branco/cinza; 3x = vermelho
    for p in me.polygons:
        c = (0.75 + 0.25 * t[p.index], 0.75 * (1 - t[p.index]), 0.75 * (1 - t[p.index]), 1)
        for li in p.loop_indices: cor_loop[li] = c
    ca.data.foreach_set("color", cor_loop.ravel().astype(np.float32))
    big = np.argsort(-rf)[:8]
    print("POSE", nome, "faces area>2x:", int((rf > 2).sum()), "piores:", [(round(float(rf[f]), 2), np.round(np.array(me.polygons[f].center), 2).tolist()) for f in big])
    alvo = J["DD"]["cotovelo"]
    for v, az, el in (("lado", -90, 5), ("frente", -15, 5), ("tras", -160, 5), ("dentro", 70, 5)): vista(f"{nome}_{v}", alvo, az, el, 12)
