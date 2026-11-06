# Imagens MARCADAS dos casos do 05a: cinza neutro, VERSO das faces em vermelho (mostra face dobrada/abertura
# vista de fora), arame preto e marcadores: azul = face dobrada, magenta = borda aberta, laranja = intersecao.
# Uso: blender -b <v.blend> -P 05b_marcados.py -- <verif.json> <pasta> <prefixo> [clipe:frame]
#   sem clipe: pose de REPOUSO (posicoes do json de repouso); com clipe:frame: pose do clipe + intersecoes do frame
import bpy, sys, os, math, json
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
V = json.load(open(argv[0])); OUT, PRE = argv[1], argv[2]
QUADRO = argv[3] if len(argv) > 3 else None
os.makedirs(OUT, exist_ok=True)
scn = bpy.context.scene
arm = bpy.data.objects["Wyvern_Rig"]; mesh = bpy.data.objects["Wyvern"]
scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 900; scn.render.resolution_y = 700
scn.world = bpy.data.worlds.new("W"); scn.world.color = (0.75, 0.77, 0.8)
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30))); bpy.context.object.data.energy = 3.5
bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-60), 0, math.radians(200))); bpy.context.object.data.energy = 1.5
# material neutro com verso vermelho
mn = bpy.data.materials.new("neutro"); mn.use_nodes = True; nt = mn.node_tree
b = nt.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.6
geo = nt.nodes.new("ShaderNodeNewGeometry"); mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
mix.inputs["A"].default_value = (0.55, 0.55, 0.55, 1); mix.inputs["B"].default_value = (0.9, 0.05, 0.05, 1)
nt.links.new(geo.outputs["Backfacing"], mix.inputs["Factor"]); nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
mn.use_backface_culling = False
mesh.data.materials[0] = mn
# arame
w = mesh.copy(); w.data = mesh.data.copy(); scn.collection.objects.link(w)
w.data.materials.clear(); mw = bpy.data.materials.new("arame"); mw.use_nodes = True
mw.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1); w.data.materials.append(mw)
md = w.modifiers.new("arame", "WIREFRAME"); md.thickness = 0.004; md.use_replace = True
def marcador(p, cor, r):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=p, segments=12, ring_count=8)
    o = bpy.context.object; m = bpy.data.materials.new("m"); m.use_nodes = True
    bb = m.node_tree.nodes["Principled BSDF"]; bb.inputs["Base Color"].default_value = cor
    bb.inputs["Emission Color"].default_value = cor; bb.inputs["Emission Strength"].default_value = 2.0
    o.data.materials.append(m); o.show_in_front = True
AZUL, MAG, LAR = (0.1, 0.3, 1, 1), (1, 0.1, 0.9, 1), (1, 0.5, 0, 1)
if QUADRO:
    clipe, fr = QUADRO.split(":"); a = bpy.data.actions[clipe]; arm.animation_data.action = a; _k = bpy.data.objects["Wyvern"].data.shape_keys; _sk = [s for s in a.slots if s.target_id_type == "KEY"]
    if _sk and _k.animation_data: _k.animation_data.action = a; _k.animation_data.action_slot = _sk[0]   # shape keys do clipe (slot KEY)
    try: arm.animation_data.action_slot = a.slots[0]
    except Exception: pass
    scn.frame_set(int(fr))
    for c in V["ciclos"][clipe]["casos_reais"]:
        if c["quadro"] == int(fr): marcador(Vector(c["pos"]), LAR, 0.03)
    pb = arm.pose.bones["tail_09"]; centros = {"juncao": (arm.matrix_world @ pb.head.lerp(pb.tail, 0.1), 2.4)}
else:
    arm.data.pose_position = "REST"; scn.frame_set(0)
    for f in V["faces_dobradas"]: marcador(Vector(f["pos"]), AZUL, 0.018)
    for bd in V["bordas_abertas"]: marcador(Vector(bd["pos"]), MAG, 0.014)
    for c in V["repouso_intersecoes"]:
        if "pos" in c: marcador(Vector(c["pos"]), LAR, 0.03)
    # centros FIXOS (coordenadas de repouso do E4/E6; iguais para todas as versoes comparadas)
    centros = {"juncao": (Vector((0.04, 22.72, 5.95)), 1.6), "meio": (Vector((0.05, 25.9, 5.2)), 2.0),
               "ponta": (Vector((0.0, 27.22, 2.9)), 1.4), "regiao": (Vector((0.0, 25.0, 4.6)), 9.0)}
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); scn.collection.objects.link(cam); scn.camera = cam
cd.type = "ORTHO"; cd.clip_end = 1000
VISTAS = {"lado": Vector((1, 0, 0.05)), "cima": Vector((0.02, 0.05, 1)), "tres4": Vector((0.8, -0.7, 0.45)), "baixo": Vector((-0.3, 0.1, -1))}
# rotulo (versao / pose / vista) preso a camera
tc = bpy.data.curves.new("rot", "FONT"); rot = bpy.data.objects.new("rot", tc); scn.collection.objects.link(rot)
mt = bpy.data.materials.new("rot"); mt.use_nodes = True; bt = mt.node_tree.nodes["Principled BSDF"]
bt.inputs["Base Color"].default_value = (1, 1, 0.6, 1); bt.inputs["Emission Color"].default_value = (1, 1, 0.6, 1); bt.inputs["Emission Strength"].default_value = 3
tc.materials.append(mt); rot.parent = cam
POSE = QUADRO.replace(":", " f") if QUADRO else "repouso"
for nome, (c, esc) in centros.items():
    for v in ("lado", "cima", "tres4", "baixo"):
        d = VISTAS[v].normalized(); cd.ortho_scale = esc
        cam.location = c + d * 300; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        tc.body = f"{PRE.split('_')[0]} | {POSE} | {nome} {v}"; tc.size = esc * 0.045
        rot.location = (-esc / 2 * 0.96, esc * 0.7 / 0.9 / 2 * 0.88, -10)
        scn.render.filepath = os.path.join(OUT, f"{PRE}_{nome}_{v}.png"); bpy.ops.render.render(write_still=True)
print("OK", list(centros))
