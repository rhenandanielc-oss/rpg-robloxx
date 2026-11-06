# Closes do ferrao com camera/luz/escala FIXAS (iguais entre versoes) + corpo inteiro + ciclos.
# Uso: blender -b <v.blend> -P 04b_closes.py -- <pasta> <prefixo> <modo> [padrao] [wire]
#   modo "estatico": idle_loop f0 -> lado, cima, tres4 (close) e corpo inteiro (tres4)
#   modo "ciclo:<clipe>[:passo]": todos os frames do clipe, close 3/4 que segue a cabeca do osso tail_09
import bpy, sys, os, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
OUT, PRE, MODO = argv[0], argv[1], argv[2]
PADRAO = argv[3] if len(argv) > 3 and argv[3] != "-" else None
WIRE = len(argv) > 4 and argv[4] == "wire"
os.makedirs(OUT, exist_ok=True)
scn = bpy.context.scene
arm = bpy.data.objects["Wyvern_Rig"]; mesh = bpy.data.objects["Wyvern"]
if PADRAO:
    _b = [n for n in mesh.data.materials[0].node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
    _b.inputs["Base Color"].links[0].from_node.image = bpy.data.images["Wyvern_Cor_" + PADRAO]
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 800; scn.render.resolution_y = 600
scn.world = bpy.data.worlds.new("W"); scn.world.color = (0.55, 0.6, 0.68)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30))); bpy.context.object.data.energy = 4
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-60), 0, math.radians(200))); bpy.context.object.data.energy = 1.5
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
m = bpy.data.materials.new("chao"); m.diffuse_color = (0.42, 0.45, 0.38, 1); bpy.context.object.data.materials.append(m)
if WIRE:   # arame por cima: copia da malha com modificador Wireframe (mesma armature)
    w = mesh.copy(); w.data = mesh.data.copy(); scn.collection.objects.link(w)
    w.data.materials.clear(); mw = bpy.data.materials.new("arame"); mw.diffuse_color = (1, 0.85, 0.1, 1)
    mw.use_nodes = True; mw.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1, 0.8, 0.05, 1)
    w.data.materials.append(mw)
    md = w.modifiers.new("arame", "WIREFRAME"); md.thickness = 0.012; md.use_replace = True
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); scn.collection.objects.link(cam); scn.camera = cam
cd.type = "ORTHO"; cd.clip_end = 1000
VISTAS = {"lado": Vector((1, 0, 0.05)), "cima": Vector((0.02, 0.05, 1)), "tres4": Vector((0.8, -0.7, 0.45)), "tras": Vector((0.35, 1, 0.3))}
# rotulo (versao / pose / vista) preso a camera
tc = bpy.data.curves.new("rot", "FONT"); rot = bpy.data.objects.new("rot", tc); scn.collection.objects.link(rot)
mt = bpy.data.materials.new("rot"); mt.use_nodes = True; bt = mt.node_tree.nodes["Principled BSDF"]
bt.inputs["Base Color"].default_value = (1, 1, 0.6, 1); bt.inputs["Emission Color"].default_value = (1, 1, 0.6, 1)
bt.inputs["Emission Strength"].default_value = 3; tc.materials.append(mt); rot.parent = cam
def mirar(c, d, esc, texto=""):
    d = d.normalized(); cd.ortho_scale = esc
    cam.location = c + d * 300; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    tc.body = texto; tc.size = esc * 0.045; rot.location = (-esc / 2 * 0.96, esc * 0.75 / 2 * 0.86, -10)
def usar(clipe):
    a = bpy.data.actions[clipe]; arm.animation_data.action = a; _k = bpy.data.objects["Wyvern"].data.shape_keys; _sk = [s for s in a.slots if s.target_id_type == "KEY"]
    if _sk and _k.animation_data: _k.animation_data.action = a; _k.animation_data.action_slot = _sk[0]   # shape keys do clipe (slot KEY)
    try: arm.animation_data.action_slot = a.slots[0]
    except Exception: pass
    return a
def render(nome):
    scn.render.filepath = os.path.join(OUT, nome); bpy.ops.render.render(write_still=True)
if MODO == "estatico":
    usar("idle_loop"); scn.frame_set(0)
    # centro fixo do close: cabeca do osso tail_10 no idle f0 (rig identico entre versoes -> mesma camera)
    pb = arm.pose.bones["tail_10"]; C_PERTO = arm.matrix_world @ pb.head.lerp(pb.tail, 0.45)
    for v in ("lado", "cima", "tres4"):
        mirar(C_PERTO, VISTAS[v], 9.5, f"{PRE} | idle f0 | close {v}"); render(f"{PRE}_close_{v}.png")
    mirar(Vector((0, 8, 10)), VISTAS["tres4"], 62, f"{PRE} | idle f0 | corpo tres4"); render(f"{PRE}_corpo_tres4.png")
    mirar(Vector((0, 8, 10)), VISTAS["lado"], 62, f"{PRE} | idle f0 | corpo lado"); render(f"{PRE}_corpo_lado.png")
else:
    partes = MODO.split(":"); clipe = partes[1]; passo = int(partes[2]) if len(partes) > 2 else 1
    a = usar(clipe); f0, f1 = int(a.frame_range[0]), int(a.frame_range[1])
    vista = partes[3] if len(partes) > 3 else "tres4"
    for f in range(f0, f1 + 1, passo):
        scn.frame_set(f)
        pb = arm.pose.bones["tail_10"]; c = arm.matrix_world @ pb.head.lerp(pb.tail, 0.3)
        mirar(c, VISTAS[vista], 8.0, f"{PRE} | {clipe} f{f} | {vista}"); render(f"{PRE}_{clipe}_{vista}_{f:03d}.png")
