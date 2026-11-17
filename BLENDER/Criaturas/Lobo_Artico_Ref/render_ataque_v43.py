"""Revisao do ataque basico v43: cada ataque PARCIAL sobreposto a Repouso, Andar e Corrida (como o Roblox faz em
prioridade Action: ossos com chave do ataque substituem os da locomocao; o resto segue a locomocao).
Uso: blender -b anim_v43/CR_LoboArtico_Anim.blend -P render_ataque_v43.py -- <dir> [vistas=perfil_E,34_E]
Depois: python prancha_ataque_v43.py"""
import bpy, sys, os, json, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True)
VISTAS = next((o[7:] for o in a[1:] if o.startswith("vistas=")), "perfil_E,34_E").split(",")
sc = bpy.context.scene; rig = bpy.data.objects["LoboArtico_Rig"]; rig.data.pose_position = "POSE"
REL = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "ataque_v43.json")))
for o in sc.objects:
    if o.type == "MESH" and o.name.startswith(("LOD1", "LOD2")): o.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE_NEXT"
sc.render.resolution_x, sc.render.resolution_y = 640, 440
w = sc.world or bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.32, 0.36, 0.42, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -0.002)); ch = bpy.context.object
mc = bpy.data.materials.new("Chao"); mc.use_nodes = True; mc.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.52, 0.55, 1); ch.data.materials.append(mc)
for nome, loc, en, sz in (("Chave", (9, -6, 12), 2200, 8), ("Recorte", (-8, 8, 9), 900, 6)):
    ld = bpy.data.lights.new(nome, "AREA"); ld.energy = en; ld.size = sz; lo = bpy.data.objects.new(nome, ld); sc.collection.objects.link(lo)
    lo.location = loc; lo.rotation_euler = (V((0, 0, 3)) - V(loc)).to_track_quat("-Z", "Y").to_euler()
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 55
C0 = V((0, -0.6, 3.6)); VIS = {"perfil_E": C0 + V((21, 0, 1.2)), "34_E": C0 + V((13, -14, 5.0)), "frente": C0 + V((0, -21, 3.0)), "cabeca": V((0, -4.4, 4.4)) + V((6.5, -5.5, 0.8))}
try: sc.view_settings.view_transform = "AgX"
except Exception: pass
def acao(nome, q):
    ac = bpy.data.actions[nome]; rig.animation_data.action = ac
    if len(ac.slots): rig.animation_data.action_slot = ac.slots[0]
    sc.frame_set(q); bpy.context.view_layer.update(); rig.animation_data.action = None
SO = next((o[3:].split(",") for o in a[1:] if o.startswith("so=")), None)
BASES = next((o[6:].split(",") for o in a[1:] if o.startswith("bases=")), ["Repouso", "Andar", "Corrida"])
for at, info in REL["acoes"].items():
    if SO and at not in SO: continue
    for base in BASES:
        nb = int(bpy.data.actions[base].frame_range[1])
        for q in ((0, 2, 3, 4, 5, 6, 8, 11) if SO else (0, 3, 5, 6, 7, 9, 12, 15)):
            for pb in rig.pose.bones: pb.matrix_basis.identity()
            acao(at, q); rot = {o: rig.pose.bones[o].rotation_quaternion.copy() for o in info["ossos"]}
            for pb in rig.pose.bones: pb.matrix_basis.identity()
            acao(base, (6 + q) % max(nb, 1))
            for o, r in rot.items(): rig.pose.bones[o].rotation_quaternion = r
            bpy.context.view_layer.update()
            for v in VISTAS:
                pos = VIS[v]; alvo = (rig.matrix_world @ rig.pose.bones["Cabeca"].head) if v == "cabeca" else C0
                if v == "cabeca": pos = alvo + V((6.5, -5.5, 0.8))
                cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
                sc.render.filepath = os.path.join(OUT, "%s_%s_%s_q%02d.png" % (at, base, v, q)); bpy.ops.render.render(write_still=True)
print("RENDER_ATAQUE_V43_OK", flush=True)
