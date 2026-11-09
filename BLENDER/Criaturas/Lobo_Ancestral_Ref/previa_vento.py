"""Previa no Blender do pelo ao vento EM CADA FORCA DE CLIMA, com a mesma formula do jogo (vento_pelo_comum.py), por
cima de um clipe SEM vento. Renderiza o close 3/4 da juba por quadro e mede o balanco (pico a pico) por forca.
Uso: blender -b rig9/Lobo_Ancestral_Anim.blend -P previa_vento.py -- <saida_dir> <Clipe> <passo> <nome:vento,...>"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Quaternion
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vento_pelo_comum as VP
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); CL = A[1]; PASSO = int(A[2]); os.makedirs(OUT, exist_ok=True)
FORCAS = [(x.split(":")[0], float(x.split(":")[1])) for x in A[3].split(",")]
DIR_VENTO = V((-0.85, 0.50, 0.0)).normalized()                          # sopra da frente-esquerda (Blender)
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; PB = arm.pose.bones
for o in sc.objects:
    if (o.type == "MESH" and o is not LO and not o.name.startswith("Plane")) or o.type == "EMPTY": o.hide_render = True
for pb in PB:
    for c in pb.constraints: c.mute = True
act = bpy.data.actions["Lobo_" + CL]; arm.animation_data_create(); arm.animation_data.action = act
try: arm.animation_data.action_slot = act.slots[0]
except Exception: pass
vel = float(act.get("velocidade", 0.0))                                 # clipe no lugar: o ar do movimento vem da velocidade
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 8; sc.render.resolution_x, sc.render.resolution_y = 520, 520
cam = sc.camera; cam.data.type = "PERSP"; cam.data.lens = 60
alvo = V((0, -3.6, 5.6)); cam.location = V((9.5, -11.5, 8.0)); cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
ORDEM = [nm for nm in VP.AMP if nm in PB]                               # pais antes das filhas (ordem do dicionario)
gi = {g.index: g.name for g in LO.vertex_groups}
pelo = np.array([any(gi[g.group].startswith("Pelo") and g.weight > 0.3 for g in v.groups) for v in LO.data.vertices])
f0, f1 = [int(x) for x in act.frame_range]
rel = {}
for rot, w in FORCAS:
    W = DIR_VENTO * w; seq = []
    for f in range(f0, f1 + 1, PASSO):
        sc.frame_set(f); bpy.context.view_layer.update(); t = (f - f0) / 30.0
        ar = W + V((0.0, abs(vel) * VP.AR_MOVIMENTO, 0.0))              # o lobo anda para -Y: o ar vem de -Y para +Y
        s = VP.forca(ar.length)
        for nm in ORDEM:
            amp, fase = VP.AMP[nm]; pb = PB[nm]
            d = (pb.tail - pb.head).normalized()                        # direcao atual da mecha (pose)
            emp = ar - d * ar.dot(d)
            if emp.length < 1e-4: continue
            sens = min(1.0, emp.length / max(ar.length, 1e-4))
            eixo_m = d.cross(emp.normalized())
            ang = math.radians(amp * s * sens * VP.ganho(t, fase, ar.length))
            eixo_l = (pb.matrix.to_3x3().inverted() @ eixo_m).normalized()   # eixo no espaco do osso
            pb.rotation_quaternion = pb.rotation_quaternion @ Quaternion(eixo_l, ang)
            bpy.context.view_layer.update()
        ev = LO.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = ev.to_mesh()
        co = np.array([v.co[:] for v in m.vertices])[pelo]; ev.to_mesh_clear()
        M = np.array((arm.matrix_world @ PB["Peito"].matrix).inverted()); seq.append((np.c_[co, np.ones(len(co))] @ M.T)[:, :3])
        sc.render.filepath = os.path.join(OUT, "%s_%s_%04d.png" % (CL, rot, f)); bpy.ops.render.render(write_still=True)
    seq = np.array(seq); amp_ = np.linalg.norm(seq.max(axis=0) - seq.min(axis=0), axis=1)
    rel[rot] = {"vento_studs_s": w, "forca": round(VP.forca(w), 3), "balanco_mediana": round(float(np.median(amp_)), 3),
                "balanco_p90": round(float(np.percentile(amp_, 90)), 3), "balanco_max": round(float(amp_.max()), 3)}
    print("PREVIA", rot, json.dumps(rel[rot]))
json.dump(rel, open(os.path.join(OUT, "previa_%s.json" % CL), "w"), indent=1)
