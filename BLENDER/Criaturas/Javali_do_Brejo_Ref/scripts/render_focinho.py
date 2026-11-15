"""Close lateral do focinho no quadro em que a cabeca fica mais baixa (chao quadriculado de 1 cm na altura 0).
Uso: JAVALI_PFX=JavaliBrejo blender -b <arquivo.blend> -P scripts/render_focinho.py -- <saida_dir> <rotulo> <Clipe1,Clipe2>"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); ROT = A[1]; L = A[2].split(",")
PFX = os.environ.get("JAVALI_PFX", "JavaliBrejo"); sc = bpy.context.scene; os.makedirs(OUT, exist_ok=True)
arm = bpy.data.objects[PFX + "_Rig"]; cab = bpy.data.objects[PFX + "_Cabeca"]; arm.animation_data_create()
for o in list(sc.objects):
    if o.type in ("CAMERA", "LIGHT"): bpy.data.objects.remove(o)
def zmin():
    dg = bpy.context.evaluated_depsgraph_get(); ev = cab.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); ev.to_mesh_clear(); c = c.reshape(-1, 3)
    i = int(c[:, 2].argmin()); return float(c[i, 2]), V(c[i])
sc.render.engine = "BLENDER_EEVEE"; sc.view_settings.view_transform = "Standard"
w = bpy.data.worlds.new("C"); w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.50, 0.46, 0.44, 1); sc.world = w
l = bpy.data.lights.new("S", "SUN"); l.energy = 3.0; lo = bpy.data.objects.new("S", l); sc.collection.objects.link(lo); lo.rotation_euler = (math.radians(55), 0, math.radians(-30))
bpy.ops.mesh.primitive_plane_add(size=1.2, location=(0, -0.6, 0)); ch = bpy.context.active_object
mp = bpy.data.materials.new("X"); nt = mp.node_tree; ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 60     # casas de 1 cm
ck.inputs["Color1"].default_value = (0.40, 0.38, 0.35, 1); ck.inputs["Color2"].default_value = (0.55, 0.53, 0.49, 1)
nt.links.new(ck.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"]); mp.blend_method = "BLEND" if hasattr(mp, "blend_method") else None
nt.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.55; ch.data.materials.append(mp)
cd = bpy.data.cameras.new("Q"); cam = bpy.data.objects.new("Q", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.type = "ORTHO"; cd.ortho_scale = 0.42
sc.render.resolution_x, sc.render.resolution_y = 560, 420; R = {}
for nome in L:
    act = bpy.data.actions[PFX + "_" + nome]; arm.animation_data.action = act
    if arm.animation_data.action_slot is None and len(act.slots): arm.animation_data.action_slot = act.slots[0]
    f0, f1 = int(act.frame_range[0]), int(act.frame_range[1]); melhor = (9.0, f0, None)
    for f in range(f0, f1 + 1):
        sc.frame_set(f); bpy.context.view_layer.update(); z, p = zmin()
        if z < melhor[0]: melhor = (z, f, p)
    z, f, p = melhor; sc.frame_set(f); bpy.context.view_layer.update()
    cam.location = V((1.5, p.y - 0.02, 0.62)); cam.rotation_euler = (V((0, p.y - 0.02, 0.07)) - cam.location).to_track_quat("-Z", "Y").to_euler()   # um pouco de cima: o chao aparece
    sc.render.filepath = os.path.join(OUT, f"{ROT}_{nome}.png"); bpy.ops.render.render(write_still=True)
    R[nome] = {"quadro": f - f0, "cabeca_z_min_cm": round(100 * z, 2)}
json.dump(R, open(os.path.join(OUT, f"{ROT}.json"), "w")); print("FOCINHO", ROT, R)
