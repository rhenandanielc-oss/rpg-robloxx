"""Renderiza os clipes do Urso v2 (acoes FK do CR_Urso_v2_Anim.blend): tira de N quadros por clipe (perfil) e, com 'video',
todos os quadros de cada clipe em baixa resolucao para GIF normal e lento (montado fora do Blender por gif_clipes.py).
Luz neutra. Uso: blender -b CR_Urso_v2_Anim.blend -P render_clipes.py -- <saida_dir> [clipe1,clipe2] [video] [N=6] [cam=lado|34]"""
import bpy, sys, os, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
QUAIS = next((a.split(",") for a in A[1:] if not a.startswith(("video", "N=", "cam="))), None)
VIDEO = "video" in A; NQ = int(next((a[2:] for a in A if a.startswith("N=")), 6)); CAM = next((a[4:] for a in A if a.startswith("cam=")), "lado")
sc = bpy.context.scene; arm = bpy.data.objects["Urso_Rig"]
for o in [o for o in sc.objects if o.type == "EMPTY"]: o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
for o in [o for o in sc.objects if o.type in ("LIGHT", "CAMERA")]: bpy.data.objects.remove(o)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.42, 0.42, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
for nome, en, rot in (("K", 3.0, (0.84, 0, -0.61)), ("R", 2.0, (2.1, 0, 2.8)), ("F", 1.0, (1.13, 0, 1.92))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
if "Chao" not in bpy.data.objects:
    bpy.ops.mesh.primitive_plane_add(size=120); ch = bpy.context.object; ch.name = "Chao"; mc = bpy.data.materials.new("Chao"); mc.use_nodes = True
    nt = mc.node_tree; b = nt.nodes["Principled BSDF"]; ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 40
    ck.inputs[1].default_value = (0.33, 0.33, 0.33, 1); ck.inputs[2].default_value = (0.27, 0.27, 0.27, 1); nt.links.new(ck.outputs[0], b.inputs["Base Color"])
    ch.data.materials.append(mc)                                   # xadrez: permite ver escorregao do pe
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 12; sc.view_settings.view_transform = "AgX"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
pos, alvo = {"lado": ((-30, -1, 5.5), (0, -0.5, 4.8)), "frente": ((-9, -26, 6.5), (0, -1.5, 4.2))}.get(CAM, ((-21, -21, 9), (0, -0.5, 4.6)))
cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cd.lens = 42
if not arm.animation_data: arm.animation_data_create()
acoes = [a for a in bpy.data.actions if a.name.startswith("Urso_")]
for act in acoes:
    nome = act.name[5:]
    if QUAIS and nome not in QUAIS: continue
    arm.animation_data.action = act; f0, f1 = [int(x) for x in act.frame_range]
    if VIDEO:
        sc.render.resolution_x, sc.render.resolution_y = 480, 320; d = os.path.join(OUT, "video", nome); os.makedirs(d, exist_ok=True)
        for f in range(f0, f1 + 1):
            sc.frame_set(f); sc.render.filepath = os.path.join(d, "%04d.png" % f); bpy.ops.render.render(write_still=True)
    sc.render.resolution_x, sc.render.resolution_y = 560, 380
    for i in range(NQ):
        f = round(f0 + (f1 - f0) * i / max(1, NQ - 1)); sc.frame_set(f)
        sc.render.filepath = os.path.join(OUT, "tira", "%s_%02d.png" % (nome, i)); bpy.ops.render.render(write_still=True)
    print("CLIPE_RENDER", nome, f0, f1)
print("RENDER_CLIPES_OK")
