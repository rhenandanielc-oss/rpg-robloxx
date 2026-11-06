# Revisao de clipes: quadros com camera FIXA (corpo inteiro, humano de 5,5 studs), rotulo clipe/quadro/vista,
# acao aplicada no rig E nas shape keys (slot KEY). Gera PNGs por quadro, uma folha por clipe e um MP4 por clipe/vista.
# Uso: blender -b <v.blend> -P 07b_revisao_clipes.py -- <pasta> <clipe1,clipe2,...> [vistas=lado,tres4] [passo=0.8]
#      [quadros=f1,f2,... ou -] [centro=x,y,z] [escala_ortho]   (opcionais: quadros fixos e enquadramento proprio)
import bpy, sys, os, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]; CLIPES = argv[1].split(","); VISTAS_ = argv[2].split(",") if len(argv) > 2 else ["lado", "tres4"]
PASSO = float(argv[3]) if len(argv) > 3 else 0.8
FR = [float(x) for x in argv[4].split(",")] if len(argv) > 4 and argv[4] != "-" else None
CEN = Vector([float(x) for x in argv[5].split(",")]) if len(argv) > 5 else None
ESC = float(argv[6]) if len(argv) > 6 else None
os.makedirs(OUT, exist_ok=True)
scn = bpy.context.scene
arm = bpy.data.objects["Wyvern_Rig"]; mesh = bpy.data.objects["Wyvern"]; key = mesh.data.shape_keys
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 960; scn.render.resolution_y = 640
scn.world = bpy.data.worlds.new("W"); scn.world.color = (0.55, 0.6, 0.68)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30))); bpy.context.object.data.energy = 4
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-60), 0, math.radians(200))); bpy.context.object.data.energy = 1.5
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0))
m = bpy.data.materials.new("chao"); m.diffuse_color = (0.42, 0.45, 0.38, 1); bpy.context.object.data.materials.append(m)
# grade no chao (marca deslocamento/escorregao): linhas a cada 4 studs
for i in range(-15, 16):
    for eixo in (0, 1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(i * 4 if eixo == 0 else 0, i * 4 if eixo == 1 else 0, 0.01))
        o = bpy.context.object; o.scale = (0.04, 120, 0.01) if eixo == 0 else (120, 0.04, 0.01)
        mg = bpy.data.materials.get("grade") or bpy.data.materials.new("grade"); mg.diffuse_color = (0.3, 0.32, 0.28, 1)
        o.data.materials.append(mg)
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=4.0, location=(12, -18, 2.0)); h1 = bpy.context.object
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75, location=(12, -18, 4.75)); h2 = bpy.context.object
mh = bpy.data.materials.new("humano"); mh.diffuse_color = (0.85, 0.3, 0.2, 1)
for o in (h1, h2): o.data.materials.append(mh)
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); scn.collection.objects.link(cam); scn.camera = cam
cd.type = "ORTHO"; cd.clip_end = 1000
tc = bpy.data.curves.new("rot", "FONT"); rot = bpy.data.objects.new("rot", tc); scn.collection.objects.link(rot)
mt = bpy.data.materials.new("rot"); mt.use_nodes = True; bt = mt.node_tree.nodes["Principled BSDF"]
bt.inputs["Base Color"].default_value = (1, 1, 0.6, 1); bt.inputs["Emission Color"].default_value = (1, 1, 0.6, 1)
bt.inputs["Emission Strength"].default_value = 3; tc.materials.append(mt); rot.parent = cam
VISTAS = {"lado": Vector((1, 0, 0.05)), "tres4": Vector((0.8, -0.7, 0.45)), "frente": Vector((0, -1, 0.15)), "cima": Vector((0.05, 0.2, 1))}
def usar(nome):
    a = bpy.data.actions[nome]
    for ob, tipo in ((arm, "OBJECT"), (key, "KEY")):
        if ob.animation_data is None: ob.animation_data_create()
        ob.animation_data.action = a
        sl = [s for s in a.slots if s.target_id_type == tipo]
        if sl: ob.animation_data.action_slot = sl[0]
    return a
for nome in CLIPES:
    a = usar(nome); f1 = a.frame_range[1]
    alto = nome in ("Pouso", "takeoff")
    k = 0; lst = FR or [i * PASSO for i in range(int(f1 / PASSO + 1e-6) + 1)]
    for f in lst:
        scn.frame_set(int(f), subframe=f - int(f))
        for v in VISTAS_:
            d = VISTAS[v].normalized(); esc = 62 if v != "frente" else 66
            c = Vector((0, 8, 17 if alto else 9))
            if alto: esc = 84
            if CEN is not None: c = CEN; esc = ESC
            cd.ortho_scale = esc; cam.location = c + d * 300; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
            tc.body = f"E7 | {nome} f{f:.1f} | {v}"; tc.size = esc * 0.03; rot.location = (-esc / 2 * 0.96, esc * 0.667 / 2 * 0.9, -10)
            scn.render.filepath = os.path.join(OUT, f"{nome}_{v}_{k:03d}.png"); bpy.ops.render.render(write_still=True)
        k += 1
    print("CLIPE", nome, "quadros", k, flush=True)
print("OK")
