"""Close-ups da boca aberta do Sombrio (pico do Rugido_Territorial) para revisao do interior.
Uso: blender -b <rig.blend> -P render_boca.py -- <saida_dir> <prefixo> [esconder_boca]"""
import bpy, os, sys
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT, PRE = os.path.abspath(a[0]), a[1]; os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]
b = bpy.data.objects.get("Silverwing_Boca")
if b and len(a) > 2: b.hide_render = True
act = bpy.data.actions["Silverwing_Rugido_Territorial"]
if not A.animation_data: A.animation_data_create()
A.animation_data.action = act
if hasattr(A.animation_data, "action_slot") and act.slots: A.animation_data.action_slot = act.slots[0]
f0, f1 = act.frame_range; sc.frame_set(int(f0 + (f1 - f0) * 0.45))
if os.environ.get("FECHADA"):                                         # boca fechada: repouso (sem clipe)
    A.animation_data.action = None
    for b_ in A.pose.bones: b_.matrix_basis.identity()
    bpy.context.view_layer.update()
pb = lambda n, t=False: A.matrix_world @ (A.pose.bones[n].tail if t else A.pose.bones[n].head)
up, lo, hd, ml = pb("mouth_upper_tip"), pb("mouth_lower_tip"), pb("head"), pb("mouth_lower")
boca = (up + lo + ml + pb("mouth_upper")) / 4                        # centro da cavidade aberta
frente = ((up + lo) / 2 - (ml + pb("mouth_upper")) / 2).normalized()
lado = frente.cross(V((0, 0, 1))).normalized(); d = (up - ml).length
VISTAS = {"frente": (frente * 2.2 + V((0, 0, -0.3)), 0.0), "frente_baixo": (frente * 1.8 + V((0, 0, -1.0)), 0.0),
          "34": (frente * 1.6 + lado * 1.3 + V((0, 0, -0.2)), 0.0), "lado": (lado * 2.4, 0.0),
          "dentro": (frente * 0.9 + V((0, 0, -0.25)), 0.0),
          "ceu": (frente * 0.9 + V((0, 0, -0.9)), 0.0), "lingua": (frente * 1.5 + V((0, 0, 0.9)), 0.0), "34_perto": (frente * 0.9 + lado * 0.8 + V((0, 0, -0.1)), 0.0)}
if os.environ.get("VISTAS"): VISTAS = {k: v for k, v in VISTAS.items() if k in os.environ["VISTAS"].split(",")}
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 640, 480
cam = bpy.data.objects.get("CamBoca") or bpy.data.objects.new("CamBoca", bpy.data.cameras.new("CamBoca"))
if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
sc.camera = cam; cam.data.lens = 40; cam.data.clip_start = 0.001
luzes = [o for o in sc.objects if o.type == "LIGHT"]
if not luzes:
    l = bpy.data.objects.new("SolBoca", bpy.data.lights.new("SolBoca", "SUN")); l.data.energy = 3.5; sc.collection.objects.link(l); l.rotation_euler = (0.8, 0.2, 0.6)
# luz de preenchimento vinda da frente (como o ambiente claro do Roblox)
f = bpy.data.objects.get("FillBoca") or bpy.data.objects.new("FillBoca", bpy.data.lights.new("FillBoca", "SUN"))
if f.name not in sc.collection.objects: sc.collection.objects.link(f)
f.data.energy = 1.2; f.rotation_euler = (-frente).to_track_quat("-Z", "Y").to_euler()
for nome, (off, _) in VISTAS.items():
    cam.location = boca + off * d; cam.rotation_euler = (boca - cam.location).to_track_quat("-Z", "Y").to_euler()
    if nome == "lingua":                                              # olha a mandibula de baixo por cima, de frente
        eixo = (lo - ml).normalized(); alvo_l = ml.lerp(lo, 0.55)
        cam.location = lo + eixo * d * 1.3 + V((0, 0, d * 1.5)) + lado * d * 0.2
        cam.rotation_euler = (alvo_l - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (PRE, nome)); bpy.ops.render.render(write_still=True)
print("RENDER_OK")
