"""Capturas fixas do giro de cabeca da coruja (antes x depois): frente, perfil, 3/4 de tras e CLOSE da juncao, nos quadros
inicio / meio do giro / extremo / retorno, com luz neutra e a mesma camera para qualquer versao.
Uso: blender -b <clipes.blend> -P rig/captura_cabeca.py -- <saida_dir> <rotulo> [acoes=OlharE,OlharD] [quadros=0,5,20,58,71]"""
import bpy, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.join(os.path.abspath(A[0]), A[1]); os.makedirs(OUT, exist_ok=True)
ACOES = (A[2] if len(A) > 2 else "OlharE,OlharD").split(","); QS = [int(x) for x in (A[3] if len(A) > 3 else "0,5,20,58,71").split(",")]
sc = bpy.context.scene
for im in bpy.data.images:
    if im.filepath and "low_voxel" in im.filepath: im.filepath = im.filepath.replace("low_voxel", "low_v1"); im.reload()
arm = bpy.data.objects["Coruja_Rig"]; arm.animation_data_create()
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)
w = bpy.data.worlds.new("F"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (*lin("8a8580"), 1)
sd = bpy.data.lights.new("Sol", "SUN"); sd.energy = 2.0; sd.angle = math.radians(12)
so = bpy.data.objects.new("Sol", sd); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), 0, math.radians(-35))
def camera(nome, loc, alvo, lente):
    c = bpy.data.cameras.new(nome); o = bpy.data.objects.new(nome, c); sc.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (V(alvo) - V(loc)).to_track_quat("-Z", "Y").to_euler(); c.lens = lente; return o
CAMS = {"frente": camera("F", (0, -1.4, 0.50), (0, 0, 0.40), 42), "perfil": camera("P", (-1.4, -0.05, 0.48), (0, -0.05, 0.40), 42),
        "34tras": camera("T", (-0.85, 1.0, 0.85), (0, -0.05, 0.42), 42), "close": camera("C", (-0.42, 0.30, 0.62), (0, -0.12, 0.47), 50)}
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"; sc.render.resolution_x, sc.render.resolution_y = 480, 480
for nome in ACOES:
    act = bpy.data.actions["Coruja_" + nome]; arm.animation_data.action = act
    for q in QS:
        sc.frame_set(int(act.frame_range[0]) + q)
        for v, cam in CAMS.items():
            sc.camera = cam; sc.render.filepath = os.path.join(OUT, f"{nome}_q{q:03d}_{v}.png"); bpy.ops.render.render(write_still=True)
print("CAPTURA_OK", OUT)
