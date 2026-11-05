"""E5: zona 'juba pintada na pele da pata dianteira' (cor de juba dentro do cilindro da pata, abaixo da juncao com o peito).
Grava e5/zona_pata.json (indices por posicao) e renders da zona. Uso: blender -b E4b_r2.blend -P e5_04_zona_pintada.py -- <juntas.json> <saida_dir>"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]; J = json.load(open(A[0])); OUT = os.path.abspath(A[1]); os.makedirs(OUT, exist_ok=True); sc = bpy.context.scene
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; me = ob.data
for o in bpy.data.objects:
    if o.type == "ARMATURE": o.data.pose_position = "REST"
n = len(me.vertices); co = np.array([v.co for v in me.vertices])
img = [nd.image for m in me.materials for nd in m.node_tree.nodes if nd.type == "TEX_IMAGE" and nd.image and nd.image.colorspace_settings.name == "sRGB"][0]
R = img.size[0]; px = np.array(img.pixels[:], np.float32).reshape(R, R, -1)[..., :3]
uvd = me.uv_layers.active.data; uvv = np.zeros((n, 2)); cnt = np.zeros(n)
for l in me.loops: uvv[l.vertex_index] += uvd[l.index].uv; cnt[l.vertex_index] += 1
uvv /= np.maximum(cnt, 1)[:, None]
cor = px[np.clip((uvv[:, 1] * R).astype(int), 0, R - 1), np.clip((uvv[:, 0] * R).astype(int), 0, R - 1)]
mx, mn = cor.max(1), cor.min(1); sat = (mx - mn) / np.maximum(mx, 1e-4)
def seg(P, a, b):
    ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1); return np.linalg.norm(P - (a + t[:, None] * ab), axis=1), t
res = {}
for perna in ("DD", "DE"):
    d = J[perna]; c_, p_, a_ = (np.array(d[k], float) for k in ("cotovelo", "punho", "pata"))
    D, t = seg(co, c_ - (p_ - c_) * 0.25, p_)            # antebraco (um pouco acima do cotovelo)
    sx = 1 if perna == "DD" else -1
    na_pata = (D < 1.45) & (co[:, 0] * sx > 0.35) & (co[:, 2] < 5.6)
    pint = na_pata & (sat > 0.62)
    print(perna, "vertices na pata", int(na_pata.sum()), "pintados de juba", int(pint.sum()), "z", np.round(co[pint, 2].min(), 2), np.round(co[pint, 2].max(), 2),
          "cor media pata limpa", np.round(cor[na_pata & (sat < 0.5) & (co[:, 2] < 3.5)].mean(0), 3), "juba", np.round(cor[pint].mean(0), 3))
    res[perna] = {"na_pata": np.nonzero(na_pata)[0].tolist(), "pintados": np.nonzero(pint)[0].tolist()}
json.dump({"pos": co.round(5).tolist(), **res}, open(os.path.join(OUT, "zona_pata.json"), "w"))
# render: zona pintada em magenta
ca = me.color_attributes.new("_z", "BYTE_COLOR", "POINT"); cc = np.ones((n, 4)) * [0.8, 0.8, 0.8, 1]
for perna in res: cc[res[perna]["na_pata"]] = [0.3, 0.6, 1, 1]; cc[res[perna]["pintados"]] = [1, 0.1, 0.7, 1]
ca.data.foreach_set("color", cc.ravel().astype(np.float32))
mat = bpy.data.materials.new("_z"); mat.use_nodes = True; nt = mat.node_tree; at = nt.nodes.new("ShaderNodeVertexColor"); at.layer_name = "_z"
bs = nt.nodes["Principled BSDF"]; nt.links.new(at.outputs[0], bs.inputs["Base Color"])
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.4; so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
def vista(nome, alvo, az, el, dist):
    alvo = Vector(alvo)
    cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = sc.render.resolution_y = 520; sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
orig = [s.material for s in ob.material_slots]
for tag, mats in (("tex", orig), ("zona", [mat] * len(orig))):
    for s, m in zip(ob.material_slots, mats): s.link = "OBJECT"; s.material = m
    for nome, az, el in (("frente", 0, 5), ("lado", -90, 5), ("34", -40, 10)): vista(f"{tag}_{nome}", (0.8, -8, 4.8), az, el, 15)
