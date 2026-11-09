"""Vista LATERAL ortografica do lobo em repouso com a linha dos ossos das patas (dianteira e traseira, lado E) desenhada
por cima, para comparar o eixo da perna com a referencia. So leitura. Uso: blender -b <rig.blend> -P lado_perna.py -- <saida.png>  (depois: python desenhar_linhas.py <saida.png>)"""
import bpy, sys, os
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
sc = bpy.context.scene; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; BD = arm.data.bones
for o in sc.objects:
    if (o.type == "MESH" and o is not LO and not o.name.startswith("Plane")) or o.type == "EMPTY": o.hide_render = True
if arm.animation_data: arm.animation_data.action = None
for pb in arm.pose.bones:
    pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    for c in pb.constraints: c.mute = True
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16; R = 1000; sc.render.resolution_x, sc.render.resolution_y = R, R
cam = sc.camera; cam.data.type = "ORTHO"; ESC = 9.0; cam.data.ortho_scale = ESC; C = V((0, -2.0, 3.6))
cam.location = V((30, C.y, C.z)); cam.rotation_euler = (C - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True)
import json
def px(p): return [(0.5 + (p.y - C.y) / ESC) * R, (0.5 - (p.z - C.z) / ESC) * R]   # camera em +X olhando -X: direita da tela = +Y, frente (-Y) a esquerda
linhas = {}
for cad in (("EscapulaE", "BracoE", "AntebracoE", "MaoE", "DedosE"), ("CoxaE", "CanelaE", "MetatarsoE", "PeE")):
    linhas[cad[0]] = [px(BD[b].head_local) for b in cad] + [px(BD[cad[-1]].tail_local)]
json.dump(linhas, open(OUT + ".json", "w")); print("OK", OUT)
