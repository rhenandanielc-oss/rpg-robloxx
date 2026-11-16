"""Render de UMA acao no lugar (lote de vida): camera fixa, chao em grade, Workbench, quadros a..b de passo p.
Uso: blender -b <blend> -P vistas_acao_v35.py -- <dir> <LOD> <acao> <a-b[:p]> <vistas> [res=LxA] [prefixo=...]"""
import bpy, sys, os, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); L = a[1]; AC = a[2]; R_ = a[3]; VS = a[4].split(","); OPC = a[5:]; os.makedirs(OUT, exist_ok=True)
RES = next((tuple(int(c) for c in o[4:].split("x")) for o in OPC if o.startswith("res=")), (480, 360)); PRE = next((o[8:] for o in OPC if o.startswith("prefixo=")), "")
r0, r1 = (int(x) for x in R_.split(":")[0].split("-")); PASSO = int(R_.split(":")[1]) if ":" in R_ else 1
sc = bpy.context.scene; ARM = bpy.data.objects["LoboArtico_Rig"]
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Marca", "LOW_Cristais"], "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}[L]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ
ARM.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
bpy.ops.mesh.primitive_grid_add(x_subdivisions=48, y_subdivisions=48, size=24, location=(0, -1, 0)); gr = bpy.context.object; gr.modifiers.new("w", "WIREFRAME").thickness = 0.015
bpy.ops.mesh.primitive_plane_add(size=24, location=(0, -1, -0.004)); chao = bpy.context.object
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "OBJECT"; sh.show_shadows = True
sh.background_type = "VIEWPORT"; sh.background_color = (0.4, 0.42, 0.45)
for o in sc.objects:
    if o.type == "MESH": o.color = (0.55, 0.57, 0.6, 1) if o == chao else ((0.22, 0.23, 0.26, 1) if o == gr else (0.85, 0.86, 0.88, 1))
sc.render.resolution_x, sc.render.resolution_y = RES
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
C0 = V((0, -1.0, 2.4))
VIS = {"perfil_E": (C0 + V((24, 0, 0.4)), ("o", 14.0)), "perfil_D": (C0 + V((-24, 0, 0.4)), ("o", 14.0)), "frente": (C0 + V((0, -24, 0.6)), ("o", 10.0)),
       "tras": (C0 + V((0, 24, 0.6)), ("o", 10.0)), "34_E": (C0 + V((12, -12, 6)), 32), "baixo_E": (C0 + V((12, -4, -1.6)), 30)}
acn = bpy.data.actions[AC]; ARM.animation_data.action = acn
if len(acn.slots): ARM.animation_data.action_slot = acn.slots[0]
for q in range(r0, r1 + 1, PASSO):
    sc.frame_set(q)
    for v in VS:
        pos, l_ = VIS[v]; cam.location = pos; cam.rotation_euler = (C0 - pos).to_track_quat("-Z", "Y").to_euler()
        if isinstance(l_, tuple): cd.type = "ORTHO"; cd.ortho_scale = l_[1]
        else: cd.type = "PERSP"; cd.lens = l_
        sc.render.filepath = os.path.join(OUT, "%s%s_%s_%s_q%04d.png" % (PRE, L, AC, v, q)); bpy.ops.render.render(write_still=True)
print("VISTAS_ACAO_OK", L, AC, r0, r1, VS, flush=True)
