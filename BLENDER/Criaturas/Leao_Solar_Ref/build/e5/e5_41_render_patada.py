"""E5 revisao da Patada: renderiza acoes ja gravadas (antes/depois) nas mesmas vistas, para comparar. So leitura do .blend (nada e salvo).
Vistas: perfil, frente e 3/4 do lado do golpe; qa_livre (baixa, do lado de fora e a frente: a juba do peito nao cobre a pata);
close da pata/punho com e sem wireframe. Videos em tempo real (30 qps) e lento (10 qps).
Uso: blender -b <arquivo.blend> -P e5_41_render_patada.py -- <saida_dir> <prefixo> <Acao1,Acao2> [res=540]
(env E5_QUADROS=1,5,9 = so esses quadros, sem video; E5_VISTAS=perfil,close = so essas vistas)"""
import bpy, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); PREF = A[1]; ACOES = A[2].split(","); RES = int(A[3]) if len(A) > 3 else 540
R = math.radians; sc = bpy.context.scene; sc.render.fps = 30
arm = bpy.data.objects["Leao_Solar_Rig"]; ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; PB = arm.pose.bones
# cena (igual a e5_20: chao xadrez com sombra, sol, EEVEE)
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0)); ch = bpy.context.active_object; ch.name = "_chao"
mc = bpy.data.materials.new("_chao"); mc.use_nodes = True; nt = mc.node_tree; bs = nt.nodes["Principled BSDF"]
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 100; ck.inputs["Color1"].default_value = (0.47, 0.43, 0.36, 1); ck.inputs["Color2"].default_value = (0.38, 0.35, 0.29, 1)
tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["UV"], ck.inputs["Vector"]); nt.links.new(ck.outputs["Color"], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.95
ch.data.materials.append(mc)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.64, 0.66, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.6; sol.angle = R(8)
so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (R(50), 0, R(35))
sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = False; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 45
# wireframe: copia que partilha a malha, com o mesmo Armature + Wireframe, material preto proprio (slot do objeto)
wf = ob.copy(); wf.name = "_wire"; sc.collection.objects.link(wf)
for m in list(wf.modifiers):
    if m.type != "ARMATURE": wf.modifiers.remove(m)
mw = wf.modifiers.new("W", "WIREFRAME"); mw.thickness = 0.018; mw.use_replace = True; mw.use_even_offset = True
mp = bpy.data.materials.new("_wire_mat"); mp.use_nodes = True; mp.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
for sl in wf.material_slots: sl.link = "OBJECT"; sl.material = mp
wf.hide_render = True
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
for nome in ACOES:
    act = bpy.data.actions[nome]; arm.animation_data_create(); arm.animation_data.action = act
    nq = int(act.frame_range[1]); sc.frame_start, sc.frame_end = 1, nq
    lado = nome[-1] if nome[-2:] in ("_D", "_E") else os.environ.get("E5_LADO", "D")   # Bote etc.: lado da camera/close por env
    az = -90 if lado == "D" else 90; k = 1 if lado == "D" else -1; mao = "Mao_D" + lado
    vistas = {"perfil": (az, 5, 50, None, False), "frente": (0, 5, 50, None, False), "34": (-40 * k, 13, 52, None, False),
              "qa_livre": (-70 * k, 3, 32, None, False), "close": (-55 * k, 8, 12, mao, False), "close_wire": (-55 * k, 8, 12, mao, True)}
    if os.environ.get("E5_TRAS"):                                            # bote: close da traseira (jarrete) com e sem wireframe
        vistas.update({"close_tras": (-75 * k, 6, 15, "Metatarso_T" + lado, False), "close_tras_wire": (-75 * k, 6, 15, "Metatarso_T" + lado, True)})
    if os.environ.get("E5_VISTAS"): vistas = {v: vistas[v] for v in os.environ["E5_VISTAS"].split(",")}
    base = nome.replace("Leao_", ""); pasta = os.path.join(OUT, "%s_%s" % (PREF, base)); os.makedirs(pasta, exist_ok=True)
    sel = [int(x) for x in os.environ["E5_QUADROS"].split(",")] if os.environ.get("E5_QUADROS") else range(1, nq + 1)
    for vista, (az_, el, dist, segue, wire) in vistas.items():
        wf.hide_render = not wire
        for f in sel:
            sc.frame_set(f)
            rz = arm.matrix_world @ PB["Raiz"].head; rz.z = rz.z * float(os.environ.get("E5_SEGUE_Z", "0"))   # acompanha a raiz (bote: E5_SEGUE_Z=0.6 no voo)
            alvo = rz + V((0, 0.5, 7.5)) if segue is None else arm.matrix_world @ PB[segue].head
            if vista == "qa_livre": alvo = rz + V((1.5 * k, -9.5, 5.0))
            cam.location = alvo + V((-math.sin(R(az_)) * math.cos(R(el)), -math.cos(R(az_)) * math.cos(R(el)), math.sin(R(el)))) * dist
            cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = os.path.join(pasta, "%s_%04d.png" % (vista, f)); bpy.ops.render.render(write_still=True)
        if not os.environ.get("E5_QUADROS"):
            video(pasta, vista, nq, os.path.join(OUT, "%s_%s_%s.mp4" % (PREF, base, vista)), 30)
            video(pasta, vista, nq, os.path.join(OUT, "%s_%s_%s_lento.mp4" % (PREF, base, vista)), 10)
    print("RENDER_OK", nome, flush=True)
