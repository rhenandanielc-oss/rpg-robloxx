"""v24: vistas de REVISAO dos apoios (Workbench, rapido), com o RIG REAL, VARIOS CICLOS seguidos e DESLOCAMENTO EQUIVALENTE
(o objeto do armature anda a -Y a v = D/T da marcha, so no render; o clipe exportado continua no lugar), chao em GRADE de
1 stud (linhas finas a 0,5) e a TRAJETORIA dos pontos medidos de cada apoio: em cada fase de apoio (cronograma da marcha) os
vertices da pata que tocam o chao no meio do apoio (metodo do auditar_clipes_v21) viram um marcador no centro deles a cada
quadro enquanto estao a < 0,06 do chao; os marcadores da fase ficam no chao (rastro): apoio sem deslize = marcadores
empilhados num ponto; deslize = rastro alongado. Cores: DE azul, DD vermelho, TE verde, TD amarelo.
Vistas: perfil_E, perfil_D, frente, tras, 34_E, patas_E, patas_D (closes das patas de cada lado, camera acompanha o corpo).
Uso: blender -b <anim.blend> -P vistas_apoios_v24.py -- <dir> <LOD> <acao> <ciclos> <vistas> [res=LxA] [pre=]"""
import bpy, sys, os, json, math
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); L, ACAO, NC = a[1], a[2], int(a[3]); VS = a[4].split(","); os.makedirs(OUT, exist_ok=True)
OPC = a[5:]; RES = next((tuple(int(c) for c in o[4:].split("x")) for o in OPC if o.startswith("res=")), (480, 360)); PRE = next((o[4:] for o in OPC if o.startswith("pre=")), "%s_%s" % (L, ACAO))
sc = bpy.context.scene; SRC = os.path.dirname(bpy.data.filepath); CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
G = CJ["marchas"][ACAO]; FPS = CJ["fps"]; VEL = G["v_studs_s"]; ARM = bpy.data.objects["LoboArtico_Rig"]; ac = bpy.data.actions[ACAO]; n = int(ac.frame_range[1])
ARM.animation_data.action = ac
if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
CONJ = {"LOW": ["LOW_Cabeca", "LOW_Corpo", "LOW_Marca", "LOW_Cristais"], "LOD1": ["LOD1_Cabeca", "LOD1_Corpo", "LOW_Marca", "LOW_Cristais"], "LOD2": ["LOD2_Cabeca", "LOD2_Corpo", "LOW_Cristais"]}[L]
for o in sc.objects:
    if o.type == "MESH": o.hide_render = o.name not in CONJ
ARM.hide_render = True
for o in list(sc.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o)
def mat(nome, cor):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome); m.diffuse_color = (*cor, 1); return m
for nm in CONJ:
    o = bpy.data.objects[nm]
    for i, s in enumerate(o.material_slots): s.link = "OBJECT"; s.material = mat("Rev_pele", (0.82, 0.83, 0.86))
# chao: plano claro + grade de linhas (geometria) a cada 0,5 (grossa a cada 1)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -VEL * n * NC / FPS / 2 - 2, -0.002)); chao = bpy.context.object; chao.scale = (14, VEL * n * NC / FPS + 16, 1); chao.data.materials.append(mat("Rev_chao", (0.55, 0.57, 0.6)))
import bmesh
gm = bpy.data.meshes.new("grade"); bm = bmesh.new(); y0, y1 = 8.0, -VEL * n * NC / FPS - 10
for i in range(-14, 15):
    for xx, w in ((i * 0.5, 0.012 if i % 2 else 0.025),):
        vs = [bm.verts.new(p) for p in ((xx - w, y0, 0), (xx + w, y0, 0), (xx + w, y1, 0), (xx - w, y1, 0))]; bm.faces.new(vs)
for j in range(int(y1 / 0.5) - 1, int(y0 / 0.5) + 1):
    yy = j * 0.5; w = 0.012 if j % 2 else 0.025; vs = [bm.verts.new(p) for p in ((-7, yy - w, 0.0005), (7, yy - w, 0.0005), (7, yy + w, 0.0005), (-7, yy + w, 0.0005))]; bm.faces.new(vs)
bm.to_mesh(gm); bm.free(); go = bpy.data.objects.new("Grade", gm); sc.collection.objects.link(go); gm.materials.append(mat("Rev_linha", (0.2, 0.21, 0.24)))
# pontos medidos por fase (mesmo metodo da auditoria), ao longo dos ciclos
C = bpy.data.objects[L + "_Corpo"]; me = C.data
patas = {k: [v.index for v in me.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8] for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"])}
COR = {"DE": (0.15, 0.4, 1.0), "DD": (1.0, 0.15, 0.1), "TE": (0.1, 0.85, 0.2), "TD": (1.0, 0.85, 0.05)}
def posado():
    dg = bpy.context.evaluated_depsgraph_get(); e = C.evaluated_get(dg); m = e.to_mesh(); P = [v.co.copy() for v in m.vertices]; e.to_mesh_clear(); return P
PP = {}
for q in range(n + 1): sc.frame_set(q); PP[q] = posado()
def apoio(k, Q): u = ((Q / FPS / G["T"]) - G["fases"][k]) % 1.0; return u < G["apoio"]
NQ = n * NC; marc = {}                                             # Q (quadro global) -> lista (k, posicao) visiveis ate Q
fases = {k: [] for k in patas}
for k in patas:
    cur = []
    for Q in range(-n, NQ + 1):
        if apoio(k, Q): cur.append(Q)
        elif cur: fases[k].append(cur); cur = []
    if cur: fases[k].append(cur)
esf = bpy.data.meshes.new("m"); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.055); bm.to_mesh(esf); bm.free()
PONTOS = []                                                        # (Q_inicio_visivel, Q_fim_fase, k, pos)
for k, fs in fases.items():
    for sg in fs:
        qm = sg[len(sg) // 2]; P = PP[qm % n]; zm = min(P[i].z for i in patas[k]); pts = [i for i in patas[k] if P[i].z < zm + 0.03]
        for Q in sg:
            Pq = PP[Q % n]; vis = [Pq[i] for i in pts if Pq[i].z < zm + 0.06]
            if not vis: continue
            c = sum(vis, V()) / len(vis); PONTOS.append((Q, sg[-1], k, V((c.x, c.y - VEL * Q / FPS, 0.01))))
obs = []
for Q, Qf, k, p in PONTOS:
    o = bpy.data.objects.new("pt", esf); o.location = p; sc.collection.objects.link(o); o.data = esf; o.color = (*COR[k], 1); obs.append((Q, Qf, o))
for k, cor in COR.items(): mat("Rev_" + k, cor)
sc.render.engine = "BLENDER_WORKBENCH"; sh = sc.display.shading; sh.light = "STUDIO"; sh.color_type = "OBJECT"; sh.show_shadows = True; sh.show_cavity = False
sh.background_type = "VIEWPORT"; sh.background_color = (0.4, 0.42, 0.45)
for o in sc.objects:
    if o.type == "MESH" and o.name not in [x[2].name for x in obs]:
        o.color = (0.82, 0.83, 0.86, 1) if o.name in CONJ else ((0.55, 0.57, 0.6, 1) if o.name == chao.name else (0.2, 0.21, 0.24, 1))
sc.render.resolution_x, sc.render.resolution_y = RES; sc.render.film_transparent = False
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
C0 = V((0, -0.6, 3.2)); PT = V((0, -0.6, 0.9))
VIS = {"perfil_E": (C0 + V((22, 0, 0.4)), C0, ("o", 15.5)), "perfil_D": (C0 + V((-22, 0, 0.4)), C0, ("o", 15.5)), "frente": (C0 + V((0, -22, 0.6)), C0, ("o", 10.0)),
       "tras": (C0 + V((0, 22, 0.6)), C0, ("o", 10.0)), "34_E": (C0 + V((12, -12, 4)), C0, 34),
       "patas_E": (PT + V((9, -1.5, 0.4)), PT, 34), "patas_D": (PT + V((-9, -1.5, 0.4)), PT, 34)}
ARM0 = ARM.location.copy()
for Q in range(NQ + 1):
    sc.frame_set(Q % n if Q % n or Q == 0 else n); dy = -VEL * Q / FPS; ARM.location = ARM0 + V((0, dy, 0))
    for q0, qf, o in obs: o.hide_render = not (q0 <= Q and Q <= qf + int(0.35 * n))     # rastro da fase fica ate 35% do ciclo depois
    bpy.context.view_layer.update()
    for v in VS:
        pos, alvo, l_ = VIS[v]; pos = pos + V((0, dy, 0)); alvo = alvo + V((0, dy, 0))
        cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler()
        if isinstance(l_, tuple): cd.type = "ORTHO"; cd.ortho_scale = l_[1]
        else: cd.type = "PERSP"; cd.lens = l_
        sc.render.filepath = os.path.join(OUT, "%s_%s_q%04d.png" % (PRE, v, Q)); bpy.ops.render.render(write_still=True)
print("VISTAS_APOIOS_OK", L, ACAO, NQ + 1, VS, flush=True)
