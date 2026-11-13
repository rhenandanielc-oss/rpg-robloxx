"""Render de DIAGNOSTICO/REVISAO com CAMERA FIXA (12/11/2026, pedido "corrida parece no lugar").
A acao do clipe e NO LUGAR (a Raiz nao avanca; o jogo move o modelo). Aqui o deslocamento e aplicado UMA vez, de fora,
no objeto da armature (arm.matrix_world), integrando a velocidade gravada na acao (velocidade_PROPOSTA ou v_perfil).
A camera NAO segue: o cervo atravessa postes fixos a cada 0,5 u (vermelho a cada 1 u) e um piso em faixas de 0,25 u.
Mede por quadro a posicao da Raiz no mundo e, em cada apoio (flags da acao), a posicao no MUNDO do casco
(cabeca da Quartela): deriva = quanto o casco se move durante o proprio apoio.
Uso: blender -b <clipes.blend> -P rig/render_fixo_cervo.py -- <dir_saida> <clipe> <ciclos> <rotulo> [ciclo_s]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); CLIPE = A[1]; CICLOS = float(A[2]); ROT = A[3] if len(A) > 3 else ""
sc = bpy.context.scene; arm = bpy.data.objects["Cervo_Rig"]; MALHAS = [bpy.data.objects["Cervo_Corpo"], bpy.data.objects["Cervo_Cabeca"]]
act = bpy.data.actions["Cervo_" + CLIPE]; arm.animation_data_create(); arm.animation_data.action = act
FPS = 30; nq = int(act.frame_range[1] - act.frame_range[0]) + 1
vel = float(act.get("velocidade_PROPOSTA", 0.0)); VP = list(act["v_perfil"]) if "v_perfil" in act else None
T_CICLO = float(A[4]) if len(A) > 4 else nq / FPS          # duracao de UM ciclo da marcha (s)
PIVO = arm.data.bones["Raiz"].head_local.copy()
TOTAL = int(round(CICLOS * T_CICLO * FPS))
def desloc(qi):                                     # deslocamento externo acumulado ate o quadro qi (direcao -Y = focinho)
    if VP: return -sum(0.5 * (VP[i % nq] + VP[(i + 1) % nq]) for i in range(qi)) / FPS
    return -vel * qi / FPS
for o in sc.objects:
    if o.type == "MESH" and o not in MALHAS: o.hide_render = True
for o in MALHAS:
    if o.parent != arm: o.parent = arm
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"; sc.render.film_transparent = False
try: sc.eevee.taa_render_samples = 16
except Exception: pass
w = bpy.data.worlds.new("C"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.60, 0.57, 1); sc.world = w
sol = bpy.data.lights.new("S", "SUN"); sol.energy = 2.4; so = bpy.data.objects.new("S", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(40), 0, math.radians(-55))
def mat(nome, cor):
    m = bpy.data.materials.new(nome); m.use_nodes = True; m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*cor, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1; return m
# piso em faixas transversais de 0,25 u (visiveis de longe) + postes fixos
comp = abs(desloc(TOTAL)) + 3.0
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -comp / 2 + 1.0, 0)); ch = bpy.context.active_object; ch.scale = (6, comp + 2, 1)
mp = bpy.data.materials.new("Faixas"); mp.use_nodes = True; nt = mp.node_tree; tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
mt = nt.nodes.new("ShaderNodeMath"); mt.operation = "MULTIPLY"; mt.inputs[1].default_value = 2.0       # 1 faixa = 0,5 u (claro/escuro 0,25 u)
fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"; gt = nt.nodes.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.5
mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs[6].default_value = (0.40, 0.38, 0.35, 1); mix.inputs[7].default_value = (0.62, 0.60, 0.56, 1)
nt.links.new(tc.outputs["Object"], sep.inputs[0]); nt.links.new(sep.outputs["Y"], mt.inputs[0])
# coordenada de objeto do plano escalado: Y do objeto vai de -0,5 a 0,5 -> converte para unidades do mundo
mt2 = nt.nodes.new("ShaderNodeMath"); mt2.operation = "MULTIPLY"; mt2.inputs[1].default_value = comp + 2
nt.links.new(sep.outputs["Y"], mt2.inputs[0]); nt.links.new(mt2.outputs[0], mt.inputs[0])
nt.links.new(mt.outputs[0], fr.inputs[0]); nt.links.new(fr.outputs[0], gt.inputs[0]); nt.links.new(gt.outputs[0], mix.inputs[0])
nt.links.new(mix.outputs[2], nt.nodes["Principled BSDF"].inputs["Base Color"]); ch.data.materials.append(mp)
M_R, M_B = mat("PosteV", (0.80, 0.08, 0.05)), mat("PosteB", (0.92, 0.92, 0.90))
y = 1.0; i = 0
while y > -comp:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.30 if i % 2 == 0 else 0.18, location=(0.45, y, 0.15 if i % 2 == 0 else 0.09))
    p_ = bpy.context.active_object; p_.data.materials.append(M_R if i % 2 == 0 else M_B); y -= 0.5; i += 1
# marca vermelha no chao sob o casco em apoio
APOIO = json.loads(act.get("apoio_json", "{}")); MARC = {}
mk = mat("Apoio", (0.9, 0.08, 0.05))
for k in APOIO:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.003); o_ = bpy.context.active_object; o_.data.materials.append(mk); MARC[k] = o_
cd = bpy.data.cameras.new("Q"); cam = bpy.data.objects.new("Q", cd); sc.collection.objects.link(cam); sc.camera = cam
y_meio = desloc(TOTAL) / 2 + PIVO.y
VISTAS = {"lado_fixo": ((-8.5, y_meio, 0.75), (0, y_meio, 0.6), 30, (1280, 420)),
          "34_fixo": ((-4.2, y_meio - 6.5, 1.9), (0, y_meio, 0.55), 30, (1100, 560))}
med = {"clipe": CLIPE, "rotulo": ROT, "quadros_render": TOTAL, "fps": FPS, "ciclo_s": T_CICLO, "vel_PROPOSTA": vel,
       "deslocamento_aplicado_em": "arm.matrix_world (externo, 1x); acao no lugar (Raiz sem avanco)", "raiz_y": [], "apoios": {}}
ap_ini = {}; mundo_ini = {}; deriva = {k: [] for k in APOIO}
for qi in range(TOTAL + 1):
    sc.frame_set(int(act.frame_range[0]) + qi % nq)
    arm.matrix_world = Matrix.Translation(V((0, desloc(qi), 0))); bpy.context.view_layer.update()
    med["raiz_y"].append(round((arm.matrix_world @ arm.pose.bones["Raiz"].head).y, 4))
    for k in APOIO:
        apo = bool(APOIO[k][qi % nq]); pw = arm.matrix_world @ arm.pose.bones[k].head
        MARC[k].location = (pw.x, pw.y, 0.0015); MARC[k].hide_render = not apo
        if apo and k not in ap_ini: ap_ini[k] = qi; mundo_ini[k] = pw.copy()
        elif apo: deriva[k].append(round((pw - mundo_ini[k]).to_2d().length, 4))
        elif k in ap_ini:
            med["apoios"].setdefault(k, []).append({"q_ini": ap_ini[k], "q_fim": qi - 1, "y_mundo": round(mundo_ini[k].y, 4),
                                                   "deriva_max": max(deriva[k]) if deriva[k] else 0.0})
            del ap_ini[k]; deriva[k] = []
    if qi == TOTAL: break
    for vista, (loc, alvo, lente, res) in VISTAS.items():
        cam.location = loc; cam.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente
        sc.render.resolution_x, sc.render.resolution_y = res; pasta = os.path.join(OUT, CLIPE, vista); os.makedirs(pasta, exist_ok=True)
        sc.render.filepath = os.path.join(pasta, "q%03d.png" % qi); bpy.ops.render.render(write_still=True)
ry = med["raiz_y"]; dur = TOTAL / FPS
med["deslocamento_total"] = round(ry[0] - ry[-1], 4); med["velocidade_efetiva"] = round((ry[0] - ry[-1]) / dur, 4)
med["deslocamento_por_ciclo"] = round((ry[0] - ry[-1]) / (TOTAL / (T_CICLO * FPS)), 4)
med["deriva_max_casco_apoiado"] = max((a["deriva_max"] for l in med["apoios"].values() for a in l), default=0.0)
json.dump(med, open(os.path.join(OUT, CLIPE, "medidas_fixo.json"), "w"), indent=1)
print("FIXO", CLIPE, ROT, {k: v for k, v in med.items() if k not in ("raiz_y", "apoios")})
