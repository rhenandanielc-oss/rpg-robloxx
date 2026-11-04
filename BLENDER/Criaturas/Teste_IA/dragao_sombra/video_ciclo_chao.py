"""Video do ciclo de chao do Sombrio (Parado -> Andar -> Correr -> frenagem -> Andar -> Parado) na malha de jogo, com o
corpo andando no mundo como na montaria (Correr a vel/18,94, Andar a vel/7,9, freio 15 studs/s2, Parada por 0,9 s),
transicoes de 0,15 s e camera lateral que acompanha. Rastro dos pes no chao (marcas) para ver patinacao.
Uso: blender -b rig_sem_clipes.blend -P video_ciclo_chao.py -- <rig_com_clipes.blend> <saida_dir> <rotulo> [lado|34]"""
import bpy, sys, os, math
from mathutils import Vector as V, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; FONTE, OUT, ROT = a[0], os.path.abspath(a[1]), a[2]; VISTA = a[3] if len(a) > 3 else "lado"
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
NOMES = ["Parado", "Andar", "Correr", "Parada"]
for n in NOMES:
    if "Silverwing_" + n in bpy.data.actions: bpy.data.actions.remove(bpy.data.actions["Silverwing_" + n])
with bpy.data.libraries.load(FONTE) as (src, dst): dst.actions = ["Silverwing_" + n for n in NOMES]
if not A.animation_data: A.animation_data_create()
FPS = sc.render.fps; ESC = 17.5 * 1.0                     # unidades do rig -> studs (modelo em escala 17,5)
ACT = {n: bpy.data.actions["Silverwing_" + n] for n in NOMES}
def pose(n, t, loop=True):
    act = ACT[n]; f0, f1 = act.frame_range; d = (f1 - f0) / FPS
    tt = (t % d) if loop else min(t, d)
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f = f0 + tt * FPS; sc.frame_set(int(f), subframe=f - int(f))
    return {b.name: b.matrix_basis.copy() for b in A.pose.bones}
# roteiro (segundos): estado, velocidade e tempo de clipe como na montaria
DT = 1 / FPS; t = 0.0; vel = 0.0; x = 0.0; fases = []
clip_t = {n: 0.0 for n in NOMES}; atual, ant, fade = "Parado", None, 1.0
while t < 9.0:
    if t < 1.5: alvo = 0
    elif t < 3.5: alvo = 10                                   # VelAndar
    elif t < 6.0: alvo = 22                                   # VelCorrer
    else: alvo = 0
    acel = 9 if alvo > vel else 15
    vel += max(-acel * DT, min(acel * DT, alvo - vel))
    if t >= 6.0 and t < 6.9: est, r = "Parada", 1.0
    elif vel > 12: est, r = "Correr", vel / 18.94
    elif vel > 2: est, r = "Andar", vel / 7.9
    else: est, r = "Parado", 1.0
    if est != atual: ant, atual, fade = atual, est, 0.0; clip_t[est] = 0.0
    clip_t[atual] += DT * r
    if ant: clip_t[ant] += DT
    fade = min(1.0, fade + DT / 0.15)
    x += vel * DT
    fases.append((t, atual, clip_t[atual], ant, clip_t.get(ant, 0) if ant else 0, fade, x, vel))
    t += DT
# chao, luz, camera
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0)); chao = bpy.context.object
mt = bpy.data.materials.new("chao"); mt.use_nodes = True; bs = mt.node_tree.nodes["Principled BSDF"]
ck = mt.node_tree.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 160
ck.inputs[1].default_value = (0.42, 0.42, 0.44, 1); ck.inputs[2].default_value = (0.32, 0.32, 0.34, 1)
mt.node_tree.links.new(ck.outputs[0], bs.inputs["Base Color"]); chao.data.materials.append(mt)
for nm, en, rot in (("S1", 4.0, (0.9, 0.1, 0.6)), ("S2", 2.0, (2.2, 0, 3.6))):
    l = bpy.data.lights.new(nm, "SUN"); l.energy = en; lo = bpy.data.objects.new(nm, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
w = sc.world or bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.62, 0.72, 1)
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 35
sc.render.engine = "BLENDER_EEVEE"; sc.render.resolution_x, sc.render.resolution_y = 960, 540; sc.eevee.taa_render_samples = 16
# marcas dos pes: pequenas esferas deixadas onde o dedo toca o chao
PT = ["front_toes_tip_l", "front_toes_tip_r", "back_toes_tip_l", "back_toes_tip_r"]
mm = bpy.data.materials.new("marca"); mm.use_nodes = True; mm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.75, 0.1, 1)
A0 = A.matrix_world.copy(); M_ = M
frames_dir = os.path.join(OUT, ROT + "_quadros"); os.makedirs(frames_dir, exist_ok=True)
import bmesh
for i, (t, n, ct, na, cta, fd, x, vel) in enumerate(fases):
    pa = pose(n, ct, n != "Parada")
    if na and fd < 1.0:
        pb = pose(na, cta, na != "Parada")
        for b in A.pose.bones:
            qa, qb = pa[b.name].to_quaternion(), pb[b.name].to_quaternion(); ta, tb = pa[b.name].translation, pb[b.name].translation
            b.matrix_basis = Matrix.Translation(tb.lerp(ta, fd)) @ qb.slerp(qa, fd).to_matrix().to_4x4()
    else:
        for b in A.pose.bones: b.matrix_basis = pa[b.name]
    A.animation_data.action = None
    A.matrix_world = Matrix.Translation(V((0, -x / ESC, 0))) @ A0
    bpy.context.view_layer.update()
    for p in PT:
        w_ = A.matrix_world @ A.pose.bones[p].tail
        if w_.z < 0.012 and i % 2 == 0:
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.006, location=(w_.x, w_.y, 0.002), segments=8, ring_count=4); bpy.context.object.data.materials.append(mm)
    c = A.matrix_world @ A.pose.bones["spine_1"].head
    if VISTA == "lado": cam.location = c + V((-2.6, 0.0, 0.25))
    else: cam.location = c + V((-1.9, -1.7, 0.55))
    cam.rotation_euler = (c + V((0, 0, -0.05)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.image_settings.file_format = "PNG"; sc.render.filepath = os.path.join(frames_dir, "q%04d.png" % i); bpy.ops.render.render(write_still=True)
print("VIDEO_QUADROS", len(fases))
