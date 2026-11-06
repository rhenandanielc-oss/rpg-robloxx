# Folha de revisao: renderiza um .blend da Wyvern em poses/vistas fixas, com humano de 5,5 studs para escala.
# Uso: blender -b <arquivo.blend> -P 90_revisao.py -- <pasta saida> <prefixo> [clipe:frame:vista,...]
import bpy, sys, os, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
OUT, PRE = argv[0], argv[1]
PLANO = argv[2].split(",") if len(argv) > 2 else ["idle_loop:0:lado", "idle_loop:0:tres4", "fly_loop:6:frente", "fly_loop:6:cima", "walk_loop:8:tres4", "roar:24:tres4"]
os.makedirs(OUT, exist_ok=True)
scn = bpy.context.scene
arm = bpy.data.objects["Wyvern_Rig"]; mesh = bpy.data.objects["Wyvern"]
if len(argv) > 3:   # padrao de cor a usar (imagem Wyvern_Cor_<nome> dentro do .blend)
    _b = [n for n in mesh.data.materials[0].node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
    _b.inputs["Base Color"].links[0].from_node.image = bpy.data.images["Wyvern_Cor_" + argv[3]]
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 900; scn.render.resolution_y = 600
scn.world = bpy.data.worlds.new("W"); scn.world.color = (0.55, 0.6, 0.68)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30))); bpy.context.object.data.energy = 4
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-60), 0, math.radians(200))); bpy.context.object.data.energy = 1.5
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
m = bpy.data.materials.new("chao"); m.diffuse_color = (0.42, 0.45, 0.38, 1); bpy.context.object.data.materials.append(m)
# humano de referencia (5,5 studs) ao lado
bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=4.0, location=(12, -18, 2.0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75, location=(12, -18, 4.75))
mh = bpy.data.materials.new("humano"); mh.diffuse_color = (0.85, 0.3, 0.2, 1)
for o in bpy.context.selected_objects: pass
for o in bpy.data.objects:
    if o.name.startswith(("Cylinder", "Sphere")): o.data.materials.append(mh)
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); scn.collection.objects.link(cam); scn.camera = cam; cd.type = "ORTHO"
VISTAS = {"lado": Vector((1, 0, 0.05)), "tres4": Vector((0.8, -0.7, 0.45)), "frente": Vector((0, -1, 0.15)), "cima": Vector((0.05, 0.2, 1))}
for item in PLANO:
    clipe, fr, vista = item.split(":")
    a = bpy.data.actions[clipe]; arm.animation_data.action = a; _k = bpy.data.objects["Wyvern"].data.shape_keys; _sk = [s for s in a.slots if s.target_id_type == "KEY"]
    if _sk and _k.animation_data: _k.animation_data.action = a; _k.animation_data.action_slot = _sk[0]   # shape keys do clipe (slot KEY)
    try: arm.animation_data.action_slot = a.slots[0]
    except Exception: pass
    scn.frame_set(int(fr))
    dg = bpy.context.evaluated_depsgraph_get(); ev = mesh.evaluated_get(dg)
    ws = [mesh.matrix_world @ v.co for v in ev.data.vertices]
    mn = Vector([min(w[i] for w in ws) for i in range(3)]); mx = Vector([max(w[i] for w in ws) for i in range(3)])
    # enquadramento FIXO por vista (mesma escala entre versoes, para comparar tamanhos)
    c = Vector((0, 8, 10))
    if vista.startswith("cauda"):   # close da ponta da cauda (ferrao)
        ponta = max(ws, key=lambda w: w.y); c = ponta - Vector((0, 2.5, 0))
        d = VISTAS["lado" if vista == "cauda" else "tres4"].normalized(); cd.ortho_scale = 9
    elif vista == "perto":   # 3/4 aproximado do corpo e da cabeca
        c = Vector((0, 2, 8)); d = VISTAS["tres4"].normalized(); cd.ortho_scale = 34
    else:
        d = VISTAS[vista].normalized()
        cd.ortho_scale = {"lado": 62, "tres4": 62, "frente": 66, "cima": 66}[vista]
    cam.location = c + d * 300; cam.rotation_euler = (-d).to_track_quat("-Z", "Y" if vista != "cima" else "Y").to_euler()
    cd.clip_end = 1000
    scn.render.filepath = os.path.join(OUT, f"{PRE}_{clipe}_{fr}_{vista}.png")
    bpy.ops.render.render(write_still=True)
