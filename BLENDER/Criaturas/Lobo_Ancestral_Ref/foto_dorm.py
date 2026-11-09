"""Render do Descanso (dormindo) com camera como a da foto de referencia (frente-direita, baixa) + vista de cima, e
medida de INTERSECAO cabeca x perna direita (vertices da cabeca dentro da capsula de Antebraco/Mao direitos, raio 0,40).
So leitura. Uso: blender -b <Anim.blend> -P foto_dorm.py -- <saida.png> [Clipe:quadro]"""
import bpy, sys, os
import numpy as np
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); IT = A[1] if len(A) > 1 else "Descanso:0"
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; PB = arm.pose.bones
for o in sc.objects:
    if (o.type == "MESH" and o is not LO and not o.name.startswith("Plane")) or o.type == "EMPTY": o.hide_render = True
for pb in PB:
    for c in pb.constraints: c.mute = True
nome, q = IT.split(":"); act = bpy.data.actions["Lobo_" + nome]; arm.animation_data_create(); arm.animation_data.action = act
try: arm.animation_data.action_slot = act.slots[0]
except Exception: pass
sc.frame_set(int(act.frame_range[0]) + int(q)); bpy.context.view_layer.update()
gi = {g.index: g.name for g in LO.vertex_groups}
D = np.array([gi[max(v.groups, key=lambda q_: q_.weight).group] if v.groups else "" for v in LO.data.vertices])
ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = ev.to_mesh(); co = np.array([v.co[:] for v in m.vertices]); ev.to_mesh_clear()
cab = co[np.isin(D, ["Cabeca", "Mandibula"])]
def capsula(a, b, r):
    a, b = np.array(a), np.array(b); ab = b - a; t = np.clip(((cab - a) @ ab) / (ab @ ab), 0, 1)
    return int((np.linalg.norm(cab - (a + t[:, None] * ab), axis=1) < r).sum())
for s_ in "ED":
    n = capsula(PB["Antebraco" + s_].head, PB["Antebraco" + s_].tail, 0.40) + capsula(PB["Mao" + s_].head, PB["Mao" + s_].tail, 0.40)
    print("INTERSECAO cabeca x perna dianteira %s: %d vertices" % (s_, n))
print("QUEIXO z %.3f" % cab[:, 2].min())
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16; sc.render.resolution_x, sc.render.resolution_y = 800, 600
cam = sc.camera; cam.data.type = "PERSP"; cam.data.lens = 40
alvo = V((-0.3, -2.0, 1.0)); outs = []
CAMF = V(tuple(float(x) for x in os.environ.get("LOBO_CAM", "-14,-7,4").split(",")))
for vn, pos in (("foto", CAMF), ("cima", V((0.01, -2.2, 22)))):
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
    f = OUT.replace(".png", "_%s.png" % vn); sc.render.filepath = f; bpy.ops.render.render(write_still=True); outs.append(f)
    bpy.context.view_layer.update()
    from bpy_extras.object_utils import world_to_camera_view
    marc = {}
    for b in ("MaoE", "MaoD", "MetatarsoE", "MetatarsoD", "Cabeca", "AntebracoE", "AntebracoD", "Pelve"):
        pt = PB[b].tail if b != "Cabeca" else PB[b].head
        c_ = world_to_camera_view(sc, cam, arm.matrix_world @ pt); marc[b] = (c_.x, 1 - c_.y)
    import json; json.dump(marc, open(f.replace(".png", ".json"), "w"))
print("FOTO_DORM_OK", outs)
