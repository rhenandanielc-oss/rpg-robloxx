"""Renders dos clipes do lote 1 COM O RIG REAL, chao em GRADE (quadrados de 0,5 stud, linhas a cada 1 stud) e luz que mostra
deformacao. Opcao 'desloc': APRESENTACAO com deslocamento - o objeto do armature anda a -Y na velocidade do clipe
(clipes_v12.json; so no render, nada disso vai para o export): a pata apoiada tem de ficar parada sobre a grade; as
cameras acompanham o corpo. Sem 'desloc' o clipe roda no lugar (contrato do jogo).
Vistas: perfil_E, perfil_D, frente, tras, 34_E, 34_tras, patas_E, patas_D, cauda_E (close cauda/pata E), garganta, geral.
Uso: blender -b <anim.blend> -P vistas_clipes_v12.py -- <dir> <LOD> <acao> <quadros a,b | i-f:p> <vistas> [desloc] [sempelo] [res=LxA] [pre=]"""
import bpy, sys, os, json, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); L, ACAO = a[1], a[2]; os.makedirs(OUT, exist_ok=True)
def quadros(s):
    if "-" in s: r, _, p = s.partition(":"); i, f = r.split("-"); return list(range(int(i), int(f) + 1, int(p or 1)))
    return [int(q) for q in s.split(",")]
QS = quadros(a[3]); VS = a[4].split(","); OPC = a[5:]; DESL = "desloc" in OPC; SEMPELO = "sempelo" in OPC
RES = next((tuple(int(c) for c in o[4:].split("x")) for o in OPC if o.startswith("res=")), (640, 480))
PRE = next((o[4:] for o in OPC if o.startswith("pre=")), "%s_%s%s" % (L, ACAO, "_desloc" if DESL else ""))
sc = bpy.context.scene; SRC = os.path.dirname(bpy.data.filepath); CJ = json.load(open(os.path.join(SRC, "clipes_v12.json")))
ARM = bpy.data.objects["LoboArtico_Rig"]; _ac = bpy.data.actions[ACAO]; ARM.animation_data.action = _ac
if getattr(ARM.animation_data, "action_slot", None) is None and len(_ac.slots): ARM.animation_data.action_slot = _ac.slots[0]   # Blender 5: slot
VEL = CJ["andar"]["v_studs_s"] if ACAO == "Andar" else 0.0
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Pelagem", "LOW_Marca", "LOW_Cristais"], "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOD1_Pelagem", "LOW_Marca", "LOW_Cristais"],
        "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}[L]
if SEMPELO: CONJ = [n for n in CONJ if "Pelagem" not in n]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ; o.hide_viewport = False
ARM.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
w_ = bpy.data.worlds.new("E"); sc.world = w_
if w_.node_tree is None: w_.use_nodes = True
w_.node_tree.nodes["Background"].inputs[0].default_value = (0.40, 0.42, 0.45, 1)
for nome, en, rot in (("K", 3.0, (50, 0, 35)), ("C", 1.8, (120, 0, 205)), ("F", 1.2, (65, 0, -120)), ("B", 0.7, (150, 0, 0))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = [math.radians(x) for x in rot]
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, -20, 0)); chao = bpy.context.object; chao.name = "Chao_grade"
m = bpy.data.materials.new("Grade")
if m.node_tree is None: m.use_nodes = True
nt = m.node_tree; bs = nt.nodes["Principled BSDF"]; tc = nt.nodes.new("ShaderNodeTexCoord"); ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 80.0 * 2
ck.inputs["Color1"].default_value = (0.62, 0.64, 0.66, 1); ck.inputs["Color2"].default_value = (0.52, 0.54, 0.57, 1)
br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 80.0; br.inputs["Mortar Size"].default_value = 0.012; br.offset = 0.0; br.squash = 1.0
br.inputs["Color1"].default_value = (1, 1, 1, 1); br.inputs["Color2"].default_value = (1, 1, 1, 1); br.inputs["Mortar"].default_value = (0.15, 0.16, 0.18, 1)
br.inputs["Brick Width"].default_value = 1.0; br.inputs["Row Height"].default_value = 1.0
mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1.0
nt.links.new(tc.outputs["UV"], ck.inputs["Vector"]); nt.links.new(tc.outputs["UV"], br.inputs["Vector"])
nt.links.new(ck.outputs["Color"], mx.inputs[6]); nt.links.new(br.outputs["Color"], mx.inputs[7]); nt.links.new(mx.outputs[2], bs.inputs["Base Color"])
bs.inputs["Roughness"].default_value = 0.9; chao.data.materials.append(m)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 24; sc.view_settings.view_transform = "AgX"; sc.render.resolution_x, sc.render.resolution_y = RES
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
C0 = V((0, -0.6, 3.2)); PT = V((0, -0.6, 0.9)); CA = V((0.7, 3.0, 2.0)); GA = V((0.0, -4.35, 4.3))
VIS = {"perfil_E": (C0 + V((22, 0, 0.4)), C0, ("o", 15.5)), "perfil_D": (C0 + V((-22, 0, 0.4)), C0, ("o", 15.5)), "frente": (C0 + V((0, -22, 0.6)), C0, ("o", 10.0)),
       "tras": (C0 + V((0, 22, 0.6)), C0, ("o", 10.0)), "34_E": (C0 + V((12, -12, 4)), C0, 34), "34_tras": (C0 + V((-11, 12, 5)), C0, 34),
       "patas_E": (PT + V((9, -1.5, 0.4)), PT, 34), "patas_D": (PT + V((-9, -1.5, 0.4)), PT, 34), "cauda_E": (CA + V((4.8, 4.8, 1.0)), CA, 36),
       "garganta": (GA + V((3.9, -3.9, 0.9)), GA, 40), "geral": (C0 + V((15, -19, 5)), C0, 26)}
ARM0 = ARM.location.copy()
for q in QS:
    sc.frame_set(q); dy = -VEL * q / sc.render.fps if DESL else 0.0; ARM.location = ARM0 + V((0, dy, 0)); bpy.context.view_layer.update()
    for v in VS:
        pos, alvo, l_ = VIS[v]; pos = pos + V((0, dy, 0)); alvo = alvo + V((0, dy, 0))
        cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
        if isinstance(l_, tuple): cd.type = "ORTHO"; cd.ortho_scale = l_[1]
        else: cd.type = "PERSP"; cd.lens = l_
        sc.render.filepath = os.path.join(OUT, "%s_%s_q%04d.png" % (PRE, v, q)); bpy.ops.render.render(write_still=True)
print("VISTAS_CLIPES_OK", L, ACAO, len(QS), VS, flush=True)
