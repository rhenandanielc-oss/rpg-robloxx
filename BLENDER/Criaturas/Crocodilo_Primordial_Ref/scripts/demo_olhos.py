"""Demo dos olhos (O1, 17/11) no CR_Crocodilo_Rig_Olhos.blend, so para revisao (o jogo faz isto por script):
1) olhar fixa um alvo a esquerda: o OLHO vira primeiro (0,12 s), a cabeca/pescoco acompanham depois e o olho volta ao
   centro conforme a cabeca chega (olho guia a cabeca); 2) piscadas em intervalos irregulares; 3) entrar na agua:
   fecha rapido, segura, reabre. Quadros em <saida>/q_####.png (Workbench, rapido).
Uso: blender -b CR_Crocodilo_Rig_Olhos.blend -P demo_olhos.py -- <saida> [vista]"""
import bpy, sys, os, math
from mathutils import Vector as V, Quaternion
a = sys.argv[sys.argv.index("--") + 1:]; OUT = a[0]; VISTA = a[1] if len(a) > 1 else "34"
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "TEXTURE"
sc.render.resolution_x = 640; sc.render.resolution_y = 400
m = bpy.data.materials["M_Croc_LOW"]
for n in m.node_tree.nodes:
    if n.type == "TEX_IMAGE" and n.image and n.image.name.startswith("CR_Croc_cor"): m.node_tree.nodes.active = n
A = bpy.data.objects["CR_Croc_Rig"]; PB = A.pose.bones; BD = A.data.bones
for pb in PB: pb.rotation_mode = "QUATERNION"
cam = bpy.data.objects["Cam"]; cam.data.type = "PERSP"; cam.data.lens = 50
FPS = 20; DUR = 5.0
def kf(t, pts):
    if t <= pts[0][0]: return pts[0][1]
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0); u = u * u * (3 - 2 * u); return v0 + (v1 - v0) * u
    return pts[-1][1]
def gira(nome, eixo_mundo, graus):
    r = BD[nome].matrix_local.to_3x3()
    q = Quaternion(eixo_mundo, math.radians(graus)).to_matrix()
    PB[nome].rotation_quaternion = (r.inverted() @ q @ r).to_quaternion()
PISCAS = [0.35, 1.9, 2.25, 3.0]          # irregular: uma dupla perto de 2 s
def palp(t):
    f = 0.0
    for t0 in PISCAS:
        f = max(f, kf(t - t0, [(-1, 0), (0, 0), (0.08, 1), (0.11, 1), (0.30, 0)]))
    f = max(f, kf(t, [(3.55, 0), (3.62, 1), (4.0, 1), (4.35, 0)]))      # agua
    return f
for i in range(int(DUR * FPS)):
    t = i / FPS
    for pb in PB: pb.rotation_quaternion = (1, 0, 0, 0)
    # cabeca vira 28 graus a esquerda (do crocodilo) entre 0,9 e 1,7 s; olho chega antes (0,7-0,82) e devolve aos poucos
    cab = kf(t, [(0.9, 0), (1.7, 28.0)])
    olho_alvo = kf(t, [(0.7, 0), (0.82, 20.0)])
    olho = max(0.0, olho_alvo - cab * 0.72)                               # olho = alvo - parte que a cabeca ja girou
    olho += 1.2 * math.sin(t * 11.0) * kf(t, [(1.8, 0), (2.0, 1)])        # micro-sacadas fixando o alvo
    gira("Pescoco", V((0, 0, 1)), cab * 0.4); gira("Pescoco2", V((0, 0, 1)), cab * 0.6)
    for s in "ED":
        gira("Olho" + s, BD["Olho" + s].matrix_local.col[2].xyz, olho)
        f = palp(t)
        gira("PalpebraSup" + s, BD["PalpebraSup" + s].matrix_local.col[0].xyz, -22.0 * f)
        gira("PalpebraInf" + s, BD["PalpebraInf" + s].matrix_local.col[0].xyz, 17.0 * f)
    bpy.context.view_layer.update()
    olhoE = A.matrix_world @ PB["OlhoE"].head
    mc = (A.matrix_world @ PB["Cabeca"].matrix @ BD["Cabeca"].matrix_local.inverted()).to_3x3()   # camera presa a cabeca
    if VISTA == "34": pos = olhoE + mc @ V((1.6, -1.9, 0.9))
    else: pos = olhoE + mc @ V((2.4, 0.1, 0.35))
    alvo = olhoE + mc @ V((0, -0.15, -0.05))
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); sc.camera = cam
    sc.render.filepath = os.path.join(OUT, "q_%04d.png" % i); bpy.ops.render.render(write_still=True)
print("DEMO_OK", int(DUR * FPS), "quadros")
