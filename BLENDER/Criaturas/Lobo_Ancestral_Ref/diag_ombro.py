"""Diagnostico/close da transicao peito-escapula-pata dianteira (camera e luz FIXAS para comparar versoes). So leitura.
Modos: final (material do jogo), albedo (so a cor da textura, sem luz), argila (cinza, SEM normal map: mostra so a
geometria/normais da malha), pesos (cor = osso dominante). Vistas: frente, tres_quartos, lado (close na regiao).
Opcional: Clipe:quadro (acoes do proprio .blend) para ver a pose.
Uso: blender -b <rig.blend> -P diag_ombro.py -- <saida_dir> <prefixo> <modos,separados> [Clipe:quadro]"""
import bpy, sys, os
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); PRE = A[1]; MODOS = A[2].split(","); os.makedirs(OUT, exist_ok=True)
POSE = A[3] if len(A) > 3 else None
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for o in sc.objects:
    if (o.type == "MESH" and o is not LO and not o.name.startswith("Plane")) or o.type == "EMPTY": o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
    pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
if POSE:
    nome, q = POSE.split(":"); act = bpy.data.actions["Lobo_" + nome]
    arm.animation_data_create(); arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    sc.frame_set(int(q))
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 24; sc.render.resolution_x, sc.render.resolution_y = 900, 900
sc.view_settings.view_transform = "Standard"
cam = sc.camera; cam.data.type = "PERSP"; cam.data.lens = 110
yo = arm.data.bones["BracoE"].head_local.y
ALVO = V((0, yo, 3.35))
VISTAS = {"frente": V((0, yo - 16, 3.6)), "tres_quartos": V((11, yo - 11.5, 5.0)), "lado": V((16, yo, 4.0))}
if os.environ.get("DIAG_ZOOM"):                                      # close de uma axila (lado E)
    ALVO = V((1.0, yo - 0.5, 3.75)); VISTAS = {"zoom_frente": V((2.0, yo - 9, 3.4)), "zoom_34": V((6.5, yo - 7.0, 4.4))}
mat0 = LO.data.materials[0]
def mat_albedo():
    m = bpy.data.materials.new("diag_albedo"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    src = next(n for n in mat0.node_tree.nodes if n.type == "TEX_IMAGE" and n.image and n.image.name.startswith("T_Lobo_Cor"))
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = src.image; e = nt.nodes.new("ShaderNodeEmission"); o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(t.outputs["Color"], e.inputs["Color"]); nt.links.new(e.outputs["Emission"], o.inputs["Surface"]); return m
def mat_argila():
    m = bpy.data.materials.new("diag_argila"); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.55, 0.55, 0.55, 1); b.inputs["Roughness"].default_value = 0.8; return m
def mat_pesos():
    gi = {g.index: g.name for g in LO.vertex_groups}; me = LO.data
    cores = {}; import random; random.seed(3)
    for g in LO.vertex_groups: cores[g.name] = (random.random(), random.random(), random.random(), 1)
    for nm, c in (("Peito", (0.9, 0.9, 0.9, 1)), ("JubaPeito", (0.2, 0.9, 0.2, 1)), ("EscapulaE", (0.9, 0.2, 0.2, 1)), ("EscapulaD", (0.9, 0.2, 0.2, 1)),
                  ("BracoE", (0.2, 0.3, 1, 1)), ("BracoD", (0.2, 0.3, 1, 1)), ("AntebracoE", (1, 0.8, 0.1, 1)), ("AntebracoD", (1, 0.8, 0.1, 1)),
                  ("Pescoco1", (0.7, 0.3, 0.9, 1)), ("Coluna2", (0.3, 0.9, 0.9, 1))): cores[nm] = c
    at = me.color_attributes.get("diag_peso") or me.color_attributes.new("diag_peso", "FLOAT_COLOR", "POINT")
    for v in me.vertices:
        acc = [0, 0, 0]; s = 0
        for g in v.groups:
            c = cores[gi[g.group]]; acc = [acc[k] + c[k] * g.weight for k in range(3)]; s += g.weight
        at.data[v.index].color = (acc[0] / max(s, 1e-6), acc[1] / max(s, 1e-6), acc[2] / max(s, 1e-6), 1)
    m = bpy.data.materials.new("diag_pesos"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    a = nt.nodes.new("ShaderNodeVertexColor"); a.layer_name = "diag_peso"; e = nt.nodes.new("ShaderNodeEmission"); o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(a.outputs["Color"], e.inputs["Color"]); nt.links.new(e.outputs["Emission"], o.inputs["Surface"]); return m
MAT = {"final": lambda: mat0, "albedo": mat_albedo, "argila": mat_argila, "pesos": mat_pesos}
for modo in MODOS:
    LO.data.materials[0] = MAT[modo]()
    for vn, pos in VISTAS.items():
        cam.location = pos; cam.rotation_euler = (ALVO - pos).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "%s_%s_%s.png" % (PRE, modo, vn)); bpy.ops.render.render(write_still=True)
LO.data.materials[0] = mat0
