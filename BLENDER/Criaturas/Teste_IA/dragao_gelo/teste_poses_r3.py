"""Teste de deformacao do GL_Dragao r3 SEM rig definitivo (o rig_glacial ainda nao existe): deforma uma copia em memoria
do master com pesos calculados aqui e verifica (1) boca aberta (grupo GL_Mandibula + dentes/assoalho inferiores na
dobradica salva em mandibula_eixo), (2) pescoco flexionado para baixo, para tras e de lado (cadeia de 5 juntas no eixo
do pescoco, pesos suaves por posicao ao longo do eixo; pecas rigidas seguem pela origem) e (3) patas apoiadas (altura
das garras e dedos em relacao ao chao). Conta penetracoes: vertices de chifres/espinhos dentro do corpo (longe da base)
e pares de espinhos dorsais que se tocam. Nao salva nada no master.
Uso: blender -b GL_Dragao_master.blend -P teste_poses_r3.py -- <saida_dir>"""
import bpy, sys, os, math
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
CORPO = bpy.data.objects["GL_Dragao_Corpo"]; me = CORPO.data
BASE_CO = [v.co.copy() for v in me.vertices]
LIG = bpy.data.objects.get("GL_Dragao_Boca_Ligacao")              # r3-r7; no r8 a boca e uma bolsa do proprio corpo
LIG_CO = [v.co.copy() for v in LIG.data.vertices] if LIG else []
PECAS = [o for o in bpy.data.collections["GL_Dragao"].objects if o != CORPO and o.type == "MESH" and not o.name.startswith("GL_Dragao_Membrana")]
BASE_M = {o.name: o.matrix_world.copy() for o in PECAS}
# referencia de cada peca rigida = centro da caixa (a cavidade da boca tem origem longe dela)
REF = {o.name: o.matrix_world @ (sum((V(c) for c in o.bound_box), V()) / 8) for o in PECAS}
# juntas do pescoco no espaco do mundo (eixo do criar_glacial_r3: base do pescoco -> nuca)
J = [V((0, -0.512, 0.680)), V((0, -0.572, 0.795)), V((0, -0.582, 0.900)), V((0, -0.578, 1.000)), V((0, -0.625, 1.080)), V((0, -0.75, 1.117))]
def param(p):
    """posicao continua ao longo da cadeia (0 = base, 5 = nuca; >5 cabeca) ou None fora do pescoco/cabeca"""
    if not (p.z > 0.62 and p.y < -0.38 and abs(p.x) < 0.30): return None
    best = (1e9, 0.0)
    for k in range(len(J) - 1):
        a, b = J[k], J[k + 1]; ab = V((0, b.y - a.y, b.z - a.z)); ap = V((0, p.y - a.y, p.z - a.z))
        t = max(0.0, min(1.0, ap.dot(ab) / ab.length_squared)); d = (ap - ab * t).length
        if d < best[0]: best = (d, k + t)
    s = best[1]
    if s >= len(J) - 1.001 and p.y < J[-1].y: s = len(J) - 1 + 1.0       # cabeca: alem da nuca
    return s
def peso(s, k): return suave((s - k) / 0.7 + 0.5)
def mat_pescoco(s, ang, eixo):
    M = Matrix.Identity(4)
    for k in range(len(J) - 1, -1, -1):                     # FK: junta da ponta primeiro, base por ultimo
        w = peso(s, k)
        if w <= 1e-4: continue
        R = Matrix.Translation(J[k]) @ Matrix.Rotation(ang * w, 4, eixo) @ Matrix.Translation(-J[k])
        M = R @ M
    return M
def resetar():
    for v, c in zip(me.vertices, BASE_CO): v.co = c
    for o in PECAS: o.matrix_world = BASE_M[o.name]
    if LIG:
        for v, c in zip(LIG.data.vertices, LIG_CO): v.co = c
        LIG.data.update()
def pose_pescoco(ang, eixo):
    for v, c in zip(me.vertices, BASE_CO):
        s = param(c)
        if s is not None: v.co = mat_pescoco(s, ang, eixo) @ c
    for o in PECAS:
        s = param(REF[o.name])
        if s is not None: o.matrix_world = mat_pescoco(s, ang, eixo) @ BASE_M[o.name]
    me.update()
def pose_boca(ang):
    H = V(CORPO["mandibula_eixo"]); R = Matrix.Translation(H) @ Matrix.Rotation(ang, 4, "X") @ Matrix.Translation(-H)
    gi = CORPO.vertex_groups["GL_Mandibula"].index
    for v, c in zip(me.vertices, BASE_CO):
        w = next((g.weight for g in v.groups if g.group == gi), 0.0)
        if w > 0: v.co = c.lerp(R @ c, w)
    for o in PECAS:
        if o.name.startswith(("Dente_Inf", "GL_Dragao_Boca_Inf")): o.matrix_world = R @ BASE_M[o.name]
    if not LIG: me.update(); return
    gl = LIG.vertex_groups["GL_Mandibula"].index; Mw = LIG.matrix_world; Mi = Mw.inverted()
    for v, c in zip(LIG.data.vertices, LIG_CO):                 # pele interna estica entre palato e assoalho
        w = next((g.weight for g in v.groups if g.group == gl), 0.0)
        if w > 0: v.co = Mi @ (Mw @ c).lerp(R @ (Mw @ c), w)
    LIG.data.update()
    me.update()
def bvh(o):
    e = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh()
    vs = [o.matrix_world @ v.co for v in m.vertices]; fs = [tuple(p.vertices) for p in m.polygons]; e.to_mesh_clear()
    return BVHTree.FromPolygons(vs, fs), vs
def penetracoes():
    bpy.context.view_layer.update()
    tc, _ = bvh(CORPO); dentro = {}
    pontiagudas = [o for o in PECAS if o.name.startswith(("Chifre", "Espinho"))]
    for o in pontiagudas:
        _, vs = bvh(o); base = o.matrix_world.translation; n = 0
        for p in vs:
            if (p - base).length < 0.025: continue           # a base fica de proposito dentro da pele
            hit = tc.find_nearest(p)
            if hit[0] is not None and (p - hit[0]).dot(hit[1]) < -0.0015: n += 1
        if n: dentro[o.name] = n
    dors = sorted([o for o in PECAS if o.name.startswith("Espinho_Dorsal_") and "Cauda" not in o.name], key=lambda o: o.name)
    toques = 0
    arv = [bvh(o)[0] for o in dors]
    for a, b in zip(arv, arv[1:]): toques += bool(a.overlap(b))
    return dentro, toques
cam = sc.camera; camd = cam.data
def foto(nome, pos, alvo, lente):
    cam.location = pos; cam.rotation_euler = (alvo - pos).to_track_quat("-Z", "Y").to_euler(); camd.lens = lente
    sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
sc.render.resolution_x, sc.render.resolution_y = 960, 540
CAB = V((0, -0.86, 1.08))
TESTES = [("neutro", None), ("boca_aberta", ("boca", math.radians(30))), ("pescoco_baixo", ("pesc", math.radians(12), "X")),
          ("pescoco_tras", ("pesc", math.radians(-9), "X")), ("pescoco_lado", ("pesc", math.radians(13), "Z")), ("pescoco_lado_moderado", ("pesc", math.radians(9), "Z"))]
for nome, t in TESTES:
    resetar()
    if t and t[0] == "boca": pose_boca(t[1])
    elif t: pose_pescoco(t[1], t[2])
    dentro, toques = penetracoes()
    print("TESTE", nome, "pecas_dentro_do_corpo", len(dentro), sum(dentro.values()), dentro, "toques_entre_dorsais", toques)
    if nome == "boca_aberta":
        foto("boca_aberta_lado", V((-0.62, -1.02, 1.03)), V((0, -0.86, 1.05)), 55)
        foto("boca_aberta_34", V((-0.42, -1.35, 1.12)), V((0, -0.88, 1.05)), 50)
    else:
        foto(nome, V((-1.35, -1.55, 1.25)), V((0, -0.62, 0.92)), 38)
resetar()
# patas apoiadas: menor altura de garras e dedos (chao em z=0)
garras = [o for o in PECAS if o.name.split(".")[0] == "Garra"]
pont = sorted(min((o.matrix_world @ v.co).z for v in o.evaluated_get(dg).to_mesh().vertices) for o in garras)
zc = min(v.co.z for v in me.vertices)
print("TESTE patas garras", len(garras), "ponta_min %.4f ponta_max %.4f" % (pont[0], pont[-1]), "corpo_min %.4f" % zc)
foto("patas_apoiadas", V((-0.55, -1.05, 0.16)), V((-0.10, -0.30, 0.05)), 42)
foto("patas_traseiras", V((-0.70, 0.75, 0.16)), V((-0.12, 0.20, 0.05)), 42)
print("TESTE_OK")
