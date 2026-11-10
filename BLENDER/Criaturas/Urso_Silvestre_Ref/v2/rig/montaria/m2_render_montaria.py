"""Montaria M2: render da subida/descida na sela do Urso Silvestre v2 (urso Urso_<clipe>_X + manequim de TESTE DEMO_Cav_<clipe>_X),
lados E (x+) e D (x-). Adaptado do s2_03_render_montaria.py do Leao Solar. So leitura (nada salvo).
Uso: blender -b CR_Urso_v2_M2_montaria.blend -P m2_render_montaria.py -- <saida> [E,D] [res=540]
(env S2_CLIPES=Montar,Desmontar; S2_QUADROS=1,40 = so esses quadros, sem video; S2_VISTAS=lado,34)"""
import bpy, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); LADOS = (A[1] if len(A) > 1 else "E,D").split(","); RES = int(A[2]) if len(A) > 2 else 540
R = math.radians; sc = bpy.context.scene; sc.render.fps = 30
arm = bpy.data.objects["Urso_Rig"]; ra = bpy.data.objects["TESTE_Manequim_R15aprox_Rig"]
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0)); ch = bpy.context.active_object
mc = bpy.data.materials.new("_chao"); mc.use_nodes = True; nt = mc.node_tree; bs = nt.nodes["Principled BSDF"]
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 100; ck.inputs["Color1"].default_value = (0.47, 0.43, 0.36, 1); ck.inputs["Color2"].default_value = (0.38, 0.35, 0.29, 1)
tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["UV"], ck.inputs["Vector"]); nt.links.new(ck.outputs["Color"], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.95
ch.data.materials.append(mc)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.64, 0.66, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.6; sol.angle = R(8)
so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (R(50), 0, R(35))
sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = False; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 45
sc.render.resolution_x, sc.render.resolution_y = int(RES * 16 / 9) // 2 * 2, RES; sc.render.image_settings.file_format = "PNG"
def video(pasta, prefixo, nq, saida, fps):
    s2 = bpy.data.scenes.new("_v"); s2.sequence_editor_create(); s2.render.fps = fps; s2.frame_start = 1; s2.frame_end = nq
    st = s2.sequence_editor.strips.new_image("img", os.path.join(pasta, "%s_%04d.png" % (prefixo, 1)), channel=1, frame_start=1)
    for f in range(2, nq + 1): st.elements.append("%s_%04d.png" % (prefixo, f))
    s2.render.resolution_x, s2.render.resolution_y = sc.render.resolution_x, sc.render.resolution_y
    im = s2.render.image_settings
    try: im.media_type = "VIDEO"
    except Exception: pass
    im.file_format = "FFMPEG"; s2.render.ffmpeg.format = "MPEG4"; s2.render.ffmpeg.codec = "H264"; s2.render.ffmpeg.constant_rate_factor = "HIGH"
    s2.render.filepath = saida; bpy.ops.render.render(animation=True, scene=s2.name); bpy.data.scenes.remove(s2)
CLIPES_S2 = os.environ.get("S2_CLIPES", "Montar").split(",")
for clip_, lado in [(c_, l_) for c_ in CLIPES_S2 for l_ in LADOS]:
    s = 1 if lado == "E" else -1; az_lado = 90 if s < 0 else -90          # camera do lado da subida (x- = az +90)
    la = bpy.data.actions["Urso_%s_%s" % (clip_, lado)]; ma = bpy.data.actions["DEMO_Cav_%s_%s" % (clip_, lado)]
    arm.animation_data.action = la; ra.animation_data.action = ma; nq = int(la.frame_range[1])
    vistas = {"lado": (az_lado, 6, 32, (s * 2.0, 0.0, 4.6), 45), "34": (az_lado * 0.5, 14, 32, (s * 1.5, -0.5, 5.0), 45),
              "frente": (0, 8, 38, (0.0, -0.5, 5.0), 45), "tras_34": (az_lado * 1.55, 16, 28, (s * 1.0, 0.8, 5.8), 45),
              "close": (az_lado * 0.8, 18, 17, (s * 1.8, 0.3, 6.2), 45)}
    if os.environ.get("S2_VISTAS"): vistas = {k: v for k, v in vistas.items() if k in os.environ["S2_VISTAS"].split(",")}
    sel = [int(x) for x in os.environ["S2_QUADROS"].split(",")] if os.environ.get("S2_QUADROS") else range(1, nq + 1)
    pasta = os.path.join(OUT, "%s_%s" % (clip_, lado)); os.makedirs(pasta, exist_ok=True)
    for vista, (az, el, dist, alvo, lens) in vistas.items():
        cd.lens = lens; al = V(alvo)
        cam.location = al + V((-math.sin(R(az)) * math.cos(R(el)), -math.cos(R(az)) * math.cos(R(el)), math.sin(R(el)))) * dist
        cam.rotation_euler = (al - cam.location).to_track_quat("-Z", "Y").to_euler()
        for f in sel:
            sc.frame_set(f); sc.render.filepath = os.path.join(pasta, "%s_%04d.png" % (vista, f)); bpy.ops.render.render(write_still=True)
        if not os.environ.get("S2_QUADROS"):
            video(pasta, vista, nq, os.path.join(OUT, "%s_%s_%s.mp4" % (clip_, lado, vista)), 30)
            video(pasta, vista, nq, os.path.join(OUT, "%s_%s_%s_lento.mp4" % (clip_, lado, vista)), 10)
    print("RENDER_S2_OK", clip_, lado, flush=True)
