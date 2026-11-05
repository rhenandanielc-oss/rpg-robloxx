"""E4: teste de deformacao com rig PROVISORIO (nao e o rig final). Juntas achadas na propria malha (colunas das patas
seguidas de baixo para cima, linha media do dorso, cauda por fatias), pesos automaticos (calor), poses simples:
pescoco baixo e virado, passo dianteiro, passo traseiro, coluna curvada, cauda erguida e para o lado, juba (cabeca virada).
Mede arestas esticadas/encolhidas por pose e renderiza 3/4 e perfil texturizados + argila.
Uso: blender -b Leao_Solar_Ref_E4.blend -P e4_06_deformacao.py -- <saida_dir> <saida.blend>"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Euler
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; ob = bpy.data.objects["Leao_Solar_E4"]
for o in list(bpy.data.objects):
    if o.type == "ARMATURE": bpy.data.objects.remove(o, do_unlink=True)
for m in list(ob.modifiers): ob.modifiers.remove(m)
ob.vertex_groups.clear()
co = np.array([v.co for v in ob.data.vertices])
def coluna(px, py, zs, raio=0.9):
    """centroide da pata subindo: em cada altura, vertices perto (xy) do centroide anterior"""
    c = np.array([px, py]); out = []
    for z in zs:
        sel = (np.abs(co[:, 2] - z) < 0.25) & (np.linalg.norm(co[:, :2] - c, axis=1) < raio)
        if sel.sum() > 3: c = co[sel, :2].mean(0)
        out.append(Vector((c[0], c[1], z)))
    return out
def pata(sx, sy):
    sel = (np.sign(co[:, 0]) == sx) & (co[:, 2] < 0.5) & ((co[:, 1] < -3) if sy < 0 else (co[:, 1] > 3))
    if sy > 0: sel &= co[:, 1] < 11
    pts = co[sel]
    # o grupo mais denso (a pata, nao a cauda)
    c = pts[:, :2].mean(0)
    for _ in range(5): d = np.linalg.norm(pts[:, :2] - c, axis=1); c = pts[d < 1.0, :2].mean(0)
    return c
J = {}
for nome, sx, sy in (("DE", -1, -1), ("DD", 1, -1), ("TE", -1, 1), ("TD", 1, 1)):
    px, py = pata(sx, sy)
    zs = [0.35, 1.7, 5.0, 8.2] if sy < 0 else [0.35, 3.0, 5.8, 8.8]
    J[nome] = coluna(px, py, zs)
    print("PATA", nome, [tuple(round(c, 2) for c in p) for p in J[nome]])
def meio(y, zmin=None):
    sel = (np.abs(co[:, 1] - y) < 0.4) & (np.abs(co[:, 0]) < 0.8)
    if zmin is not None: sel &= co[:, 2] > zmin
    z = co[sel, 2]; return Vector((0, y, (z.min() + z.max()) / 2)) if len(z) else Vector((0, y, 10))
quadril = Vector((0, (J["TE"][3].y + J["TD"][3].y) / 2, 9.0)); cernelha = Vector((0, (J["DE"][3].y + J["DD"][3].y) / 2, 10.0))
espinha = [quadril.lerp(cernelha, t) for t in (0, 0.35, 0.7, 1.0)]
pesc = [cernelha, Vector((0, -10.8, 12.8)), Vector((0, -12.0, 13.6))]; cabeca_fim = Vector((0, -14.6, 14.2))
# cauda: seguida de tras para a frente a partir de y=12 (so cauda ali), fatia a fatia, perto do ponto anterior; para
# quando a fatia encosta no corpo (muitos vertices) -> base da cauda
sel = (np.abs(co[:, 1] - 12.0) < 0.25) & (co[:, 2] > 1.5); c = co[sel].mean(0); trilha = [Vector(c)]
for y in np.arange(11.6, 5.0, -0.35):
    sel = (np.abs(co[:, 1] - y) < 0.2) & (np.linalg.norm(co[:, [0, 2]] - c[[0, 2]], axis=1) < 0.6)
    if sel.sum() < 3 or sel.sum() > 60: break
    c = np.array([co[sel, 0].mean(), y, co[sel, 2].mean()]); trilha.append(Vector(c))
trilha = trilha[::-1]; c = co[(np.abs(co[:, 1] - 12.0) < 0.25) & (co[:, 2] > 1.5)].mean(0)
for y in np.arange(12.4, 18.4, 0.4):
    sel = (np.abs(co[:, 1] - y) < 0.2) & (np.linalg.norm(co[:, [0, 2]] - c[[0, 2]], axis=1) < 1.2)
    if sel.sum() < 3: continue
    c = np.array([co[sel, 0].mean(), y, co[sel, 2].mean()]); trilha.append(Vector(c))
L = [0.0]
for a_, b_ in zip(trilha, trilha[1:]): L.append(L[-1] + (b_ - a_).length)
cauda = [Vector((0, quadril.y + 1.6, 8.7))]                  # base da cauda no dorso (a fatia encosta no corpo antes)
for k in range(5):
    alvo = L[-1] * k / 4; i = max(j for j in range(len(L)) if L[j] <= alvo + 1e-6); cauda.append(trilha[i])
print("CAUDA", [tuple(round(c, 2) for c in p) for p in cauda])
ad = bpy.data.armatures.new("Rig_Teste_Deformacao"); arm = bpy.data.objects.new("Rig_Teste_Deformacao", ad); sc.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode="EDIT")
def osso(n, a, b, pai=None):
    e = ad.edit_bones.new(n); e.head = a; e.tail = b
    if pai: e.parent = ad.edit_bones[pai]; e.use_connect = (ad.edit_bones[pai].tail - a).length < 1e-4
    return n
osso("Raiz", quadril - Vector((0, 0, 1.5)), quadril)
p = "Raiz"
for i in range(3): p = osso("Coluna%d" % (i + 1), espinha[i], espinha[i + 1], p)
p = osso("Pescoco1", pesc[0], pesc[1], p); p = osso("Pescoco2", pesc[1], pesc[2], p); osso("Cabeca", pesc[2], cabeca_fim, p)
for nome in ("DE", "DD"):
    c = J[nome]; o0 = osso("Escapula_" + nome, cernelha + Vector((0.6 * math.copysign(1, c[3].x), 0, 0)), c[3], "Coluna3")
    o1 = osso("Umero_" + nome, c[3], c[2], o0); o2 = osso("Antebraco_" + nome, c[2], c[1], o1); osso("Pata_" + nome, c[1], c[0] + Vector((0, -0.6, 0)), o2)
for nome in ("TE", "TD"):
    c = J[nome]; o0 = osso("Coxa_" + nome, c[3], c[2], "Raiz"); o1 = osso("Canela_" + nome, c[2], c[1], o0)
    osso("Pata_" + nome, c[1], c[0] + Vector((0, -0.6, 0)), o1)
p = "Raiz"
for i in range(len(cauda) - 1): p = osso("Cauda%d" % (i + 1), cauda[i], cauda[i + 1], p)
bpy.ops.object.mode_set(mode="OBJECT")
for o in sc.objects: o.select_set(False)
ob.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
sem_l = [v.index for v in ob.data.vertices if not any(g.weight > 1e-3 for g in v.groups)]; sem = len(sem_l)
# o calor nao alcanca cascas soltas (dentes, lingua): no rig final elas vao para Cabeca/Mandibula; aqui, Cabeca
ob.vertex_groups["Cabeca"].add(sem_l, 1.0, "REPLACE")
print("PESOS automaticos: vertices sem peso", sem, "de", len(ob.data.vertices))
infl = [sum(1 for g in v.groups if g.weight > 0.01) for v in ob.data.vertices]
print("INFLUENCIAS >1%: max", max(infl), "media", round(sum(infl) / len(infl), 2), "verts com >4:", sum(1 for x in infl if x > 4))
# ---------------------------------------------------------------- poses
POSES = {
    "repouso": {},
    "pescoco_baixo_virado": {"Pescoco1": (20, 0, 15), "Pescoco2": (15, 0, 15), "Cabeca": (-10, 0, 10)},
    "passo_dianteiro": {"Umero_DD": (-35, 0, 0), "Antebraco_DD": (70, 0, 0), "Pata_DD": (-50, 0, 0), "Escapula_DD": (-12, 0, 0)},
    "passo_traseiro": {"Coxa_TD": (35, 0, 0), "Canela_TD": (-65, 0, 0), "Pata_TD": (50, 0, 0)},
    "coluna_curvada": {"Coluna1": (0, 0, 10), "Coluna2": (6, 0, 10), "Coluna3": (6, 0, 10), "Pescoco1": (0, 0, 10)},
    "cauda": {"Cauda1": (25, 0, 15), "Cauda2": (20, 0, 20), "Cauda3": (15, 0, 20), "Cauda4": (10, 0, 15), "Cauda5": (10, 0, 10)},
}
me = ob.data; E = np.array([e.vertices[:] for e in me.edges]); L0 = np.linalg.norm(co[E[:, 0]] - co[E[:, 1]], axis=1)
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.2; sol.angle = math.radians(40)
so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = True; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
def vista(nome, alvo, az, el, dist, res=520):
    alvo = Vector(alvo)
    cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = sc.render.resolution_y = res; sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
CAM = {"repouso": ((0, 0, 8), 46), "pescoco_baixo_virado": ((0, -10, 11), 26), "passo_dianteiro": ((1.5, -9, 4), 22),
       "passo_traseiro": ((2, 5.5, 4.5), 22), "coluna_curvada": ((0, -1, 8), 46), "cauda": ((0.5, 12, 5.5), 24)}
rel = {}
for nome, rot in POSES.items():
    for pb in arm.pose.bones: pb.rotation_mode = "XYZ"; pb.rotation_euler = (0, 0, 0)
    for b, r in rot.items(): arm.pose.bones[b].rotation_euler = Euler([math.radians(x) for x in r])
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); m = ob.evaluated_get(dg).to_mesh(); pc = np.array([v.co for v in m.vertices]); ob.evaluated_get(dg).to_mesh_clear()
    L1 = np.linalg.norm(pc[E[:, 0]] - pc[E[:, 1]], axis=1); r_ = L1 / np.maximum(L0, 1e-6)
    rel[nome] = {"arestas_esticadas_>1.5": int((r_ > 1.5).sum()), "encolhidas_<0.6": int((r_ < 0.6).sum()), "razao_max": round(float(r_.max()), 2), "razao_min": round(float(r_.min()), 2)}
    print("POSE", nome, rel[nome], flush=True)
    alvo, d = CAM[nome]
    vista(nome + "_34", alvo, -40, 10, d); vista(nome + "_perfil", alvo, -90, 0, d)
json.dump(rel, open(os.path.join(OUT, "deformacao.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A[1])); print("DEFORMACAO_OK")
