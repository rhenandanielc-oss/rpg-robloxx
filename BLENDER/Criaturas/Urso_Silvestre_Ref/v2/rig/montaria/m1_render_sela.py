"""Montaria M1: renders de revisao da sela reforcada no Urso Silvestre v2 (adaptado do s1_02_render_sela.py do Leao Solar) (pose de repouso), com e sem o manequim de TESTE (proporcoes aproximadas
do R15, modulo manequim_r15.py do Crocodilo, so importado) sentado. Vistas: perfil D/E, 3/4 frente, 3/4 tras, topo, frente e
closes do assento/adorno e da cilha. So leitura do .blend (nada e salvo).
Uso: blender -b <com_sela.blend> -P s1_02_render_sela.py -- <saida_dir> [acao=nenhuma] [quadro=1] [res=720]"""
import bpy, sys, os, math
from mathutils import Vector as V, Matrix as M
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
ACAO = A[1] if len(A) > 1 and A[1] != "nenhuma" else None; QD = int(A[2]) if len(A) > 2 else 1; RES = int(A[3]) if len(A) > 3 else 720
RAIZ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.abspath(os.path.join(RAIZ, "..", "..", "..", "..", "Crocodilo_Primordial_Ref", "scripts")))
import manequim_r15 as mq
import m1_sela_urso as sl
mq.SENTADO = sl.SENTADO_URSO
R = math.radians; sc = bpy.context.scene
arm = bpy.data.objects["Urso_Rig"]; sela = bpy.data.objects[sl.NOME]
if ACAO: arm.animation_data.action = bpy.data.actions[ACAO]
else:
    arm.animation_data.action = None
    for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
sc.frame_set(QD); bpy.context.view_layer.update()
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
# manequim sentado (quadril preso ao osso Coluna1 no ponto do assento)
ra, mob, alvos = mq.criar()
for pb in ra.pose.bones:
    for c in pb.constraints: c.mute = False
q = V(sela["quadril"]); bl = arm.data.bones["Coluna2"].matrix_local
Mq = arm.matrix_world @ arm.pose.bones["Coluna2"].matrix @ bl.inverted() @ M.Translation(q)
import json as _j
for k_, v_ in _j.loads(sela["sentado"]).items(): mq.SENTADO[tuple(k_.split("|"))] = tuple(v_)
mq.sentado(ra, alvos, Mq); bpy.context.view_layer.update()
VISTAS = {"perfil_D": (-90, 6, 30, (0.0, 0.3, 7.0), 45), "perfil_E": (90, 6, 30, (0.0, 0.3, 7.0), 45), "34_frente": (-40, 18, 30, (0.0, -0.5, 7.2), 45),
          "34_tras": (-140, 22, 28, (0.0, 0.8, 7.6), 45), "topo": (0.0001, 89, 20, (0.0, 0.5, 8.5), 45), "frente": (0, 10, 34, (0.0, -1.5, 7.0), 45),
          "close_assento": (-35, 25, 8, (0.0, 0.3, 8.9), 50), "close_cilha_D": (-80, 0, 11, (-2.2, -0.45, 5.6), 50)}
def render(nome, com_cav):
    mob.hide_render = not com_cav
    Mr = arm.matrix_world @ arm.pose.bones["Raiz"].matrix; giro = Mr.to_euler().z; org = Mr.translation.copy(); org.z = 0.0   # segue a raiz (posicao e rumo)
    for v, (az, el, dist, alvo, lens) in VISTAS.items():
        cd.lens = lens; al = org + (M.Rotation(giro, 4, "Z") @ V(alvo)); az = az - math.degrees(giro)
        cam.location = al + V((-math.sin(R(az)) * math.cos(R(el)), -math.cos(R(az)) * math.cos(R(el)), math.sin(R(el)))) * dist
        cam.rotation_euler = (al - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (nome, v)); bpy.ops.render.render(write_still=True)
render("sela", False); render("sela_cav", True)
print("RENDER_S1_OK")
