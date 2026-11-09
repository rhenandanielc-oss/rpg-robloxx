"""Quadros de clipes com as MESMAS cameras dos videos (lateral, frontal, 3/4), opcionalmente usando as acoes de outro
.blend (mesmo esqueleto) - para comparar malhas antes de regenerar clipes. So leitura.
Uso: blender -b <rig.blend> -P comparar_quadros.py -- <saida_dir> <prefixo> <blend_das_acoes|-> Clipe:quadro,..."""
import bpy, sys, os
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); PRE = A[1]; FONTE = A[2]; LISTA = A[3].split(","); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
if FONTE != "-":
    with bpy.data.libraries.load(os.path.abspath(FONTE)) as (src, dst):
        dst.actions = [a for a in src.actions if a.startswith("Lobo_") and a not in bpy.data.actions]
for o in sc.objects:
    if (o.type == "MESH" and o is not LO and not o.name.startswith("Plane")) or o.type == "EMPTY": o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
if not arm.animation_data: arm.animation_data_create()
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 12; sc.render.resolution_x, sc.render.resolution_y = 640, 400
cam = sc.camera; camd = cam.data; camd.type = "PERSP"
VISTAS = [("lateral", V((24, -1.5, 4.0)), V((0, -1.5, 3.4)), 40), ("frontal", V((0, -24, 4.0)), V((0, -1, 3.4)), 40),
          ("tres_quartos", V((15, -16, 7.5)), V((0, -1, 3.2)), 40)]
for item in LISTA:
    nome, q = item.split(":"); act = bpy.data.actions["Lobo_" + nome]; arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    sc.frame_set(int(act.frame_range[0]) + int(q))
    for vn, pos, alvo, lente in VISTAS:
        cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
        sc.render.filepath = os.path.join(OUT, "%s_%s_%s_%s.png" % (PRE, nome, q, vn)); bpy.ops.render.render(write_still=True)
print("QUADROS_OK", PRE)
