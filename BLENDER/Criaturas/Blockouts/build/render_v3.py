"""Folhas de revisao do Lobo Ancestral V3 (EEVEE, sol + preenchimento, chao neutro).
Uso: blender -b <blend> -P render_v3.py -- <pasta_saida> [Acao:t ...]
Gera frente, lateral, tres_quartos, close_cabeca e uma imagem por pose pedida."""
import bpy, sys, os, math
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]
out = a[0]; poses = a[1:]
os.makedirs(out, exist_ok=True)
sc = bpy.context.scene
for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try: sc.render.engine = eng; break
    except TypeError: pass
sc.render.resolution_x, sc.render.resolution_y = 1000, 750
sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Standard"
for o in list(bpy.data.objects):
    if o.name.startswith("REF_") or o.type == "LIGHT" or o.type == "CAMERA": bpy.data.objects.remove(o, do_unlink=True)
w = bpy.data.worlds.new("W"); sc.world = w
bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND"); bg.inputs[0].default_value = (0.5, 0.56, 0.64, 1); bg.inputs[1].default_value = 0.5
def luz(nome, e, rot, cor=(1, 1, 1)):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = e; l.color = cor
    o = bpy.data.objects.new(nome, l); sc.collection.objects.link(o); o.rotation_euler = [math.radians(x) for x in rot]
luz("Sol", 2.2, (48, 0, 35), (1, 0.97, 0.92)); luz("Fill", 0.6, (65, 0, 215), (0.8, 0.87, 1))      # luz neutra (sem estourar)
bpy.ops.mesh.primitive_plane_add(size=400); chao = bpy.context.active_object
m = bpy.data.materials.new("Chao"); b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"); b.inputs["Base Color"].default_value = (0.2, 0.21, 0.17, 1)
chao.data.materials.append(m)
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
if arm and arm.animation_data:
    for tr in arm.animation_data.nla_tracks: tr.mute = True
    arm.animation_data.action = None
if arm:                                                      # a pose salva pode ser a ultima acao avaliada: volta ao repouso
    for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    bpy.context.view_layer.update()
for o in bpy.data.objects:                                  # pre-visualizacao: corpo ainda sem textura assada recebe a cor base
    if o.type == "MESH" and o.name.endswith("_Corpo_Blockout"):
        bs = next(n for n in o.active_material.node_tree.nodes if n.type == "BSDF_PRINCIPLED"); bs.inputs["Base Color"].default_value = (0.13, 0.13, 0.125, 1)
def malhas(): return [o for o in bpy.data.objects if o.type == "MESH" and o != chao]
def caixa():
    dg = bpy.context.evaluated_depsgraph_get(); pts = []
    for o in malhas():
        eo = o.evaluated_get(dg); me = eo.to_mesh(); pts += [eo.matrix_world @ v.co for v in list(me.vertices)[::25]]; eo.to_mesh_clear()
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    return (mn + mx) / 2, (mx - mn).length
def mira(alvo, d, lente, nome):
    cam_d.lens = lente; cam.location = alvo + d
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out, nome + ".png"); bpy.ops.render.render(write_still=True)
c, r = caixa()
if os.environ.get("CAM_FIXO"):                               # mesma camera/escala para comparar versoes
    c, r = Vector((0, -1.2, 4.2)), 11.5
for nome, d in (("frente", (0, -1, 0.12)), ("lateral", (1, 0, 0.08)), ("tres_quartos", (0.8, -0.85, 0.35))):
    mira(c, Vector(d).normalized() * r * 1.15, 40, nome)
olho = next((o for o in bpy.data.objects if o.type == "MESH" and "_Olho" in o.name), None)        # close centrado nos olhos
h = (sum((olho.matrix_world @ v.co for v in olho.data.vertices), Vector()) / len(olho.data.vertices) + Vector((0, -0.05, -0.07))) if olho else Vector((0, -4.25, 8.35))
ke = 1.0 if os.environ.get("CAM_FIXO") else max(1.0, caixa()[1] / 12.0)   # close proporcional ao tamanho da criatura
mira(h, Vector((1.6, -2.3, 0.5)) * ke, 50, "close_cabeca")
mira(h, Vector((0.0, -3.0, 0.15)) * ke, 50, "close_cabeca_frente")
if os.environ.get("CAM_FIXO"): mira(Vector((0.75, -1.6, 5.0)), Vector((2.0, -0.7, 0.6)), 50, "close_pelagem")      # ombro/cernelha (lobos)
else: mira(c + Vector((r * 0.08, -r * 0.1, r * 0.06)), Vector((1.0, -0.35, 0.3)).normalized() * r * 0.22, 50, "close_pelagem")   # flanco/ombro (generico)
for ps in poses:
    nome, t = ps.split(":")
    act = bpy.data.actions.get(nome)
    if not (arm and act): continue
    arm.animation_data.action = act
    f0, f1 = act.frame_range; sc.frame_set(int(f0 + float(t) * (f1 - f0)))
    c, r = caixa()
    mira(c, Vector((1, -0.25, 0.12)).normalized() * r * 1.2, 40, "pose_%s_%s_lateral" % (nome, t.replace(".", "")))
    mira(c, Vector((0.8, -0.85, 0.35)).normalized() * r * 1.2, 40, "pose_%s_%s" % (nome, t.replace(".", "")))
    arm.animation_data.action = None
    for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
    sc.frame_set(1)
print("RENDER_OK")
