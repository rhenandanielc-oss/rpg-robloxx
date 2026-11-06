"""Lote 5: renders de revisao da sela definitiva (pose de descanso ou quadro de um clipe), com ou sem o cavaleiro de teste
sentado, e folga estatica (vertices da sela x pele: negativa = entra na pele; partes do manequim x sela).
Uso: blender -b CR_Crocodilo_Sela.blend -P render_sela.py -- <saida_dir> <tag> [cavaleiro] [clipe:quadro]"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix as M
from mathutils.bvhtree import BVHTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manequim_r15 as mq
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True); TAG = A[1]
CAV = "cavaleiro" in A[2:]; CQ = next((x for x in A[2:] if ":" in x), None)
sc = bpy.context.scene; croc = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]; sela = bpy.data.objects["CR_Croc_Sela"]
cam = sc.camera; cd = cam.data
for pb in croc.pose.bones:
    for c in pb.constraints: c.mute = True
for o in sc.objects:
    if o.type in ("EMPTY", "ARMATURE"): o.hide_render = True
if CQ:
    nm, q = CQ.split(":"); act = bpy.data.actions["Croc_" + nm]; croc.animation_data.action = act; croc.animation_data.action_slot = act.slots[0]; sc.frame_set(int(q) + 1)
else:
    croc.animation_data.action = None
    for pb in croc.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
bpy.context.view_layer.update()
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0)); chao = bpy.context.object
m = bpy.data.materials.new("M_Chao"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 200; ck.inputs["Color1"].default_value = (0.55, 0.55, 0.56, 1)
ck.inputs["Color2"].default_value = (0.36, 0.36, 0.38, 1); nt.links.new(ck.outputs["Color"], b.inputs["Base Color"]); chao.data.materials.append(m)
# folga da sela x pele (sela deformada pelo rig)
dg = bpy.context.evaluated_depsgraph_get(); bvh = mq.bvh_croc(lo)
ev = sela.evaluated_get(dg); me = ev.to_mesh(); W = sela.matrix_world; vs = [W @ v.co for v in me.vertices]; ev.to_mesh_clear()
pior = 9.0; n_dentro = 0
for p in vs:
    loc, _, _, d = bvh.find_nearest(p, 3.0)
    if loc is None: continue
    s = -d if mq.dentro(bvh, p) else d
    if s < 0: n_dentro += 1
    pior = min(pior, s)
res = {"tag": TAG, "clipe": CQ, "sela_x_pele_min": round(pior, 3), "vertices_dentro": n_dentro, "vertices": len(vs)}
if CAV:
    ra, ob, alvos = mq.criar(); Zq = sela["z_quadril"]
    mq.sentado(ra, alvos, mq.assento_mundo(croc, Zq)); bpy.context.view_layer.update()
    amo = mq.amostras_partes(0.2)
    res["cavaleiro_x_pele"] = mq.folgas(ra, amo, bvh)
    bs = BVHTree.FromObject(sela, bpy.context.evaluated_depsgraph_get()); res["cavaleiro_x_sela"] = mq.folgas(ra, amo, bs, Minv=sela.matrix_world.inverted(), raio=3.0)
print("RENDER_SELA", json.dumps(res))
json.dump(res, open(os.path.join(OUT, "folga_%s.json" % TAG), "w"), indent=1)
Y0 = -4.7
CAMS = {"lado": (V((22, Y0, 8)), V((0, Y0, 4.6)), 45), "34": (V((12, -15, 11)), V((0, Y0, 5.0)), 40),
        "frente": (V((0, -24, 10)), V((0, Y0, 5.0)), 45), "tras": (V((-7, 14, 11)), V((0, Y0, 5.2)), 42),
        "34d": (V((-12, -14, 10)), V((0, Y0, 5.0)), 40), "baixo": (V((9, -5, 1.2)), V((0, Y0, 2.0)), 30),
        "close": (V((6.5, -9.5, 8.5)), V((0, Y0, 5.6)), 40), "topo": (V((0, Y0, 30)), V((0, Y0 + 0.01, 0)), 0)}
sc.render.resolution_x, sc.render.resolution_y = 1100, 700; sc.eevee.taa_render_samples = 48
for cn, (p, a, lente) in CAMS.items():
    cam.location = p; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y").to_euler()
    if cn == "topo": cam.rotation_euler = (0, 0, math.pi / 2); cd.type = "ORTHO"; cd.ortho_scale = 9
    else: cd.type = "PERSP"; cd.lens = lente
    sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (TAG, cn)); bpy.ops.render.render(write_still=True)
print("RENDER_SELA_OK")
