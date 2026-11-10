"""Renders do Blender com as MESMAS cameras das capturas do Studio do piloto (04/11), para comparar lado a lado.
Studio (relativo ao pivo do urso) -> Blender: (x, y, z)s -> (-xs, zs, ys). FOV vertical 70 graus (padrao do Studio).
Uso: blender -b CR_Urso_v2_Anim.blend -P studio/render_comparar.py -- <saida_dir> [lote2]
lote2 (04/11): Corrida q7, Arrancada q24, Frenagem q20 (lado) e VirarE q18 visto de cima com o giro de 36 graus no pivo."""
import bpy, sys, os, math
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; arm = bpy.data.objects["Urso_Rig"]
for o in [o for o in sc.objects if o.type == "EMPTY"]: o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
for o in [o for o in sc.objects if o.type in ("LIGHT", "CAMERA")]: bpy.data.objects.remove(o)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.45, 0.6, 0.8, 1)
for nome, en, rot in (("K", 3.0, (0.84, 0, -0.61)), ("R", 1.5, (2.1, 0, 2.8))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=120); mc = bpy.data.materials.new("C"); mc.use_nodes = True
mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1); bpy.context.object.data.materials.append(mc)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16; sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 868, 400
cd = bpy.data.cameras.new("C"); cd.sensor_fit = "VERTICAL"; cd.angle_y = math.radians(70)
cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
def b(s): return V((-s[0], s[2], s[1]))
CAPS = [("Repouso", 0, "34", (-15, 8, -16), (0, 4, -0.5)),
        ("Rugir", 28, "lado", (-19, 5, -1), (0, 4.2, -1)),
        ("Rugir", 28, "frente", (-3.6, 6.4, -11.5), (0, 6.9, -4.5)),
        ("Andar", 9, "lado", (-19, 5, -1), (0, 4.2, -1))]
if "lote2" in sys.argv:
    CAPS = [("Corrida", 7, "lado", (-19, 5, -1), (0, 4.2, -1)), ("Arrancada", 24, "lado", (-19, 5, -1), (0, 4.2, -1)),
            ("Frenagem", 20, "lado", (-19, 5, -1), (0, 4.2, -1)), ("VirarE", 18, "cima", (-14, 15, -14), (0, 3, 0.5))]
if "lote3" in sys.argv:   # 04/11: os 10 clipes restantes; mesmas cameras das capturas do Studio (ver CAMS)
    CAMS = {"lado": ((-19, 5, -1), (0, 4.2, -1)), "boca": ((-3.6, 6.4, -11.5), (0, 6.9, -4.5)),
            "34": ((-12, 7, -12), (0, 4.5, -1.5)), "barriga": ((-8, 0.7, 1.5), (0, 0.5, 1.5)),
            "boca_lado": ((-6.5, 6.6, -4.6), (0, 6.6, -4.6)), "boca_alto": ((-3.2, 12.6, -5.2), (0, 12.5, 1.0))}
    LISTA = [("Observar", 43, "lado"), ("Sentar", 42, "lado"), ("LevantarSentado", 25, "lado"), ("Deitar", 60, "lado"),
             ("Deitar", 60, "barriga"), ("LevantarDeitado", 30, "lado"), ("Comer", 10, "boca"), ("Ameaca", 31, "lado"),
             ("Ameaca", 31, "boca"), ("Ameaca", 31, "boca_alto"), ("Ameaca", 77, "lado"), ("GolpePata", 13, "34"), ("Mordida", 9, "boca"),
             ("Mordida", 9, "boca_lado"), ("ReacaoImpacto", 13, "lado")]
    CAPS = [(c, q, v, CAMS[v][0], CAMS[v][1]) for c, q, v in LISTA]
GIRO = {"VirarE": 36.0}                                 # mesmo giro aplicado no Studio (60 graus/s x 0,6 s), no pivo da Raiz
PIVO = arm.data.bones["Raiz"].head_local.copy()
if not arm.animation_data: arm.animation_data_create()
for clip, q, vista, pos, alvo in CAPS:
    arm.animation_data.action = bpy.data.actions["Urso_" + clip]; sc.frame_set(q + 1)
    from mathutils import Matrix as Mx
    g = math.radians(GIRO.get(clip, 0.0)) if "lote2" in sys.argv else 0.0
    arm.matrix_world = Mx.Translation(PIVO) @ Mx.Rotation(g, 4, "Z") @ Mx.Translation(-PIVO)
    p, a = b(pos), b(alvo); cam.location = p; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(OUT, "blender_%s_%02d_%s.png" % (clip, q, vista)); bpy.ops.render.render(write_still=True)
print("COMPARAR_OK")
