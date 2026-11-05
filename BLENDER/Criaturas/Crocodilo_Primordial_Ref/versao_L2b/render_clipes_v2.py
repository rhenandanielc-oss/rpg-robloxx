"""Revisao dos clipes (Lote 1): chao quadriculado de 1 stud; locomocao com o modelo deslocado na velocidade do clipe (pe
apoiado fica parado no chao se nao escorregar); Nado com linha d'agua de TESTE (nao e fisica). Renderiza TODOS os quadros
de 1 ciclo por camera (GIF repete 3 ciclos depois). Nao salva o .blend.
Uso: blender -b CR_Crocodilo_Anim.blend -P render_clipes_v2.py -- <saida_dir> <clipes> <cameras> [passo_quadros]"""
import bpy, sys, os, json, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
CLIPES = A[1].split(","); CAMS_Q = A[2].split(","); PASSO = int(A[3]) if len(A) > 3 else 1
sc = bpy.context.scene; arm = bpy.data.objects["CR_Croc_Rig"]; lo = bpy.data.objects["CR_Croc_LOW"]; cam = sc.camera; cd = cam.data
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
for o in sc.objects:
    if o.type in ("EMPTY", "ARMATURE"): o.hide_render = True
# chao quadriculado (1 stud)
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0)); chao = bpy.context.object; chao.name = "Chao_Teste"
m = bpy.data.materials.new("M_Chao"); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 200; ck.inputs["Color1"].default_value = (0.55, 0.55, 0.56, 1)
ck.inputs["Color2"].default_value = (0.36, 0.36, 0.38, 1); nt.links.new(ck.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.9
chao.data.materials.append(m)
agua = None
manif = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "clipes", "manifesto_clipes.json")))
CAMS = {"lado": (V((30, -3, 8.0)), V((0, -2, 3.0)), 36, None), "34": (V((24, -22, 8)), V((0, -3, 2.4)), 32, None),
        "topo": (V((0, -1, 44)), V((0, -0.99, 0)), 0, 40), "cabeca": (V((8.0, -21.0, 5.5)), V((0, -12.5, 3.4)), 38, None),
        "patas": (V((15.0, -13.0, 2.0)), V((1.5, -4.0, 1.0)), 30, None), "frente": (V((0, -34, 4.0)), V((0, -10, 3.0)), 34, None)}
sc.render.resolution_x, sc.render.resolution_y = 640, 360; sc.eevee.taa_render_samples = 16
if not arm.animation_data: arm.animation_data_create()
for nome in CLIPES:
    act = bpy.data.actions["Croc_" + nome]; arm.animation_data.action = act
    if act.slots: arm.animation_data.action_slot = act.slots[0]
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); vel = manif[nome]["velocidade_studs_s"]
    sinc = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "clipes", "Crocodilo_%s.json" % nome))).get("sincronizacao", {})
    giro = math.radians(sinc.get("giro_graus_s", sinc.get("giro_graus_s_proposto", 0.0))); pivo_y = sinc.get("pivo_y", -4.0)
    desl_q = sinc.get("deslocamento_studs")
    AGUA = ("Nado", "NadoParado", "CurvaAquaticaEsquerda", "CurvaAquaticaDireita", "Mergulho", "Emersao")
    if nome in AGUA and agua is None:
        bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 4.3)); agua = bpy.context.object; agua.name = "Agua_Teste"
        ma = bpy.data.materials.new("M_Agua"); ma.use_nodes = True; ba = ma.node_tree.nodes["Principled BSDF"]
        ba.inputs["Base Color"].default_value = (0.12, 0.22, 0.24, 1); ba.inputs["Alpha"].default_value = 0.45; ba.inputs["Roughness"].default_value = 0.1
        ma.surface_render_method = "BLENDED" if hasattr(ma, "surface_render_method") else ma.blend_method
        agua.data.materials.append(ma)
    if agua: agua.hide_render = (nome not in AGUA)
    for cn in CAMS_Q:
        p, a, lente, orto = CAMS[cn]
        for qi, f in enumerate(range(f0, f1 + 1, PASSO)):
            sc.frame_set(f); t = (f - f0) / 30.0
            # o jogo anda para -Y na velocidade do clipe (ou pelo perfil por quadro) e gira em torno do pivo
            dq = desl_q[min(len(desl_q) - 1, f - f0)] if desl_q else vel * t
            desl = V((0, -dq, 0)); ang = giro * t
            from mathutils import Matrix as _Mx
            arm.matrix_world = _Mx.Translation(desl + V((0, pivo_y, 0))) @ _Mx.Rotation(ang, 4, "Z") @ _Mx.Translation(V((0, -pivo_y, 0)))
            lo.location = (0, 0, 0)
            cam.location = p + desl; cam.rotation_euler = (a - p).to_track_quat("-Z", "Y").to_euler()
            if cn == "topo": cam.rotation_euler = (0, 0, math.pi / 2)          # corpo na horizontal da imagem
            if orto: cd.type = "ORTHO"; cd.ortho_scale = orto
            else: cd.type = "PERSP"; cd.lens = lente
            sc.render.filepath = os.path.join(OUT, "%s_%s_%03d.png" % (nome, cn, qi)); bpy.ops.render.render(write_still=True)
        arm.matrix_world = __import__("mathutils").Matrix.Identity(4)
    print("RENDER_V2", nome, CAMS_Q, "quadros", len(range(f0, f1 + 1, PASSO)), "vel", vel)
print("RENDER_V2_OK")
