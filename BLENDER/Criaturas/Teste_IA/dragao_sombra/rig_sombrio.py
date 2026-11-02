"""Rig do DRAGAO SOMBRIO (copia do rig_glacial.py): mesmo esqueleto de 100 ossos; diferencas do Sombrio: cabeca
escalada K_CAB=1,14 em torno do pivo (mesma funcao do criar_sombrio.py) e cauda encurtada (x0,82 atras do quadril).
--- texto de origem ---
Rig do Dragao Glacial r4 com o MESMO esqueleto do Silverwing/CR_Dragao (100 ossos, mesmos nomes e hierarquia):
o gerador de clipes (meshy/anim_silverwing.py), o apelido de ossos do Studio e as animacoes continuam valendo.
Derivado de dragao_novo/rig_dragao.py. O que muda no Glacial:
- cabeca sem escala 1,3x: os pontos da cabeca vem do espaco canonico + OFF (alto do pescoco em S);
- spine_2..4 seguem o pescoco novo (peito -> base -> meio -> nuca); cauda redistribuida ate y=2,30;
- mandibula: dobradica em mandibula_eixo do master; pesos do maxilar vem do grupo SB_Mandibula (labios cortados no
  master), nao do calor; pecas rigidas pelo grupo TAG_* (cabeca / mandibula), o resto no osso mais proximo;
- membrana presa mais alto no flanco (r4) e borda interna nova.
K=0,744 e DY=-0,339 iguais ao CR (altura das patas = Silverwing -> passadas e velocidades iguais).
Uso: blender -b Silverwing_M2M.blend -P rig_sombrio.py -- <SB_Dragao_LOW.blend> <saida.blend>"""
import bpy, sys, os, math
from mathutils import Vector as V, Matrix
from mathutils.geometry import intersect_point_line
LOW_BLEND, SAIDA = sys.argv[sys.argv.index("--") + 1:][:2]
sys.path.insert(0, r"C:\Users\Rhenan\.claude\skills\blender-character-rigging\scripts")
import bind_mesh
sc = bpy.context.scene
A = bpy.data.objects["Silverwing_Rig"]; VELHA = bpy.data.objects["Silverwing"]
if A.animation_data:
    A.animation_data.action = None
    for t in list(A.animation_data.nla_tracks): A.animation_data.nla_tracks.remove(t)
for pb in A.pose.bones: pb.matrix_basis = Matrix.Identity(4)

K, DY = 0.744, -0.339
OFF = V((0, -0.03, 0.36))                                   # criar_glacial_r4.py: cabeca canonica -> alto do pescoco
K_CAB, PIV = 1.14, V((0, -0.64, 0.725))                     # criar_sombrio.py: cabeca maior em torno do pivo
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def f(p, cabeca=False):
    p = V(p)
    if cabeca:
        w = suave((-0.61 - p.y) / 0.09); p = PIV + (p - PIV) * (1 + (K_CAB - 1) * w) + OFF
    elif p.y > 0.30 and abs(p.x) < 0.01: p = V((p.x, 0.30 + (p.y - 0.30) * 0.82, p.z))   # cauda x0,82 (eixo)
    return V((p.x * K, p.y * K + DY, p.z * K))
def lerp(a, b, t): return a + (b - a) * t
raiz, cot, pul = V((0.085, -0.31, 0.60)), V((0.50, -0.18, 0.78)), V((1.00, -0.38, 0.90))
D = [[V((1.50, -0.53, 0.95)), V((1.92, -0.45, 0.95)), V((2.20, -0.28, 0.93))],
     [V((1.47, -0.20, 0.89)), V((1.84, 0.01, 0.85)), V((2.09, 0.20, 0.81))],
     [V((1.34, 0.05, 0.83)), V((1.57, 0.36, 0.77)), V((1.71, 0.67, 0.71))],
     [V((1.11, 0.12, 0.79)), V((1.15, 0.47, 0.71)), V((1.13, 0.82, 0.64))]]
flanco = V((0.090, 0.30, 0.52))                             # r4
borda_meio = lerp(D[3][2], flanco, 0.5) + (cot - lerp(D[3][2], flanco, 0.5)).normalized() * 0.40
J = {}
def b(n, h, t, cabeca=False): J[n] = (f(h, cabeca), f(t, cabeca))
b("hips", (0, 0.20, 0.472), (0, 0.15, 0.477))
b("spine_0", (0, 0.15, 0.477), (0, -0.08, 0.498)); b("spine_1", (0, -0.08, 0.498), (0, -0.31, 0.512))
# pescoco em S (eixo do master r4): peito -> base -> meio -> nuca
b("spine_2", (0, -0.31, 0.512), (0, -0.512, 0.680)); b("spine_3", (0, -0.512, 0.680), (0, -0.580, 0.900))
b("spine_4", (0, -0.580, 0.900), (0, -0.67, 1.085))
b("head", (0, -0.64, 0.725), (0, -0.70, 0.745), True)
b("mouth_upper", (0, -0.70, 0.745), (0, -0.86, 0.745), True); b("mouth_upper_tip", (0, -0.86, 0.745), (0, -0.965, 0.714), True)
b("mouth_lower", (0, -0.735, 0.712), (0, -0.84, 0.700), True); b("mouth_lower_tip", (0, -0.84, 0.700), (0, -0.935, 0.690), True)
b("horn_base_l", (0, -0.64, 0.725), (0.030, -0.745, 0.830), True); b("horn_l", (0.030, -0.745, 0.830), (0.055, -0.66, 0.94), True)
b("horn_tip_L", (0.055, -0.66, 0.94), (0.075, -0.50, 0.99), True)
b("collar_anchor_l", (0, -0.31, 0.512), (0.04, -0.31, 0.495)); b("front_leg_collar_l", (0.04, -0.31, 0.495), (0.105, -0.31, 0.470))
b("front_leg_l", (0.105, -0.31, 0.470), (0.150, -0.20, 0.265)); b("front_ankle_l", (0.150, -0.20, 0.265), (0.150, -0.275, 0.075))
b("front_foot_l", (0.150, -0.275, 0.075), (0.152, -0.30, 0.036)); b("front_toes_l", (0.152, -0.30, 0.036), (0.152, -0.36, 0.022))
b("front_toes_tip_l", (0.152, -0.36, 0.022), (0.152, -0.42, 0.016))
b("stomach", (0, -0.08, 0.498), (0, -0.08, 0.38)); b("stomach_tip", (0, -0.08, 0.38), (0, -0.08, 0.35))
b("shoulder_l", (0.02, -0.26, 0.56), raiz); b("wing_1_l", raiz, cot); b("wing_2_l", cot, pul)
m3 = lerp(pul, D[0][0], 0.5)
b("wing_3_l", pul, m3); b("wing_4_l", m3, D[0][0]); b("wing_5_l", D[0][0], D[0][1]); b("wing_tip_l", D[0][1], D[0][2])
for k, d in ((5, D[1]), (4, D[2]), (3, D[3])):
    b("wing_feather_%d_0_l" % k, pul, d[0]); b("wing_feather_%d_1_l" % k, d[0], d[1]); b("wing_feather_%d_tip_l" % k, d[1], d[2])
b("wing_feather_2_0_l", cot, lerp(cot, borda_meio, 0.4)); b("wing_feather_2_1_l", lerp(cot, borda_meio, 0.4), lerp(cot, borda_meio, 0.75))
b("wing_feather_2_tip_l", lerp(cot, borda_meio, 0.75), borda_meio)
b("wing_feather_1_0_l", raiz, lerp(raiz, flanco, 0.35)); b("wing_feather_1_1_l", lerp(raiz, flanco, 0.35), lerp(raiz, flanco, 0.7))
b("wing_feather_1_tip_l", lerp(raiz, flanco, 0.7), flanco)
cauda = [(0, 0.20, 0.472), (0, 0.46, 0.430), (0, 0.72, 0.394), (0, 1.00, 0.352), (0, 1.30, 0.312), (0, 1.62, 0.280), (0, 1.95, 0.260), (0, 2.28, 0.256)]
for i, n in enumerate(["tail_1", "tail_2", "tail_3", "tail_4", "tail_5", "tail_6", "tail_tip"]): b(n, cauda[i], cauda[i + 1])
b("hips_anchor_l", (0, 0.20, 0.472), (0.04, 0.21, 0.462)); b("back_leg_hip_l", (0.04, 0.21, 0.462), (0.115, 0.22, 0.445))
b("back_leg_l", (0.115, 0.22, 0.445), (0.165, 0.07, 0.250)); b("back_ankle_l", (0.165, 0.07, 0.250), (0.162, 0.245, 0.060))
b("back_foot_l", (0.162, 0.245, 0.060), (0.162, 0.200, 0.030)); b("back_toes_l", (0.162, 0.200, 0.030), (0.162, 0.14, 0.020))
b("back_toes_tip_l", (0.162, 0.14, 0.020), (0.162, 0.08, 0.014))
for n in list(J):
    if n.endswith("_l") or n.endswith("_L"):
        nr = n[:-2] + ("_r" if n.endswith("_l") else "_R"); h, t = J[n]
        J[nr] = (V((-h.x, h.y, h.z)), V((-t.x, t.y, t.z)))
falta = [bn.name for bn in A.data.bones if bn.name not in J and bn.name not in ("root", "DRV_root")]
assert not falta, "ossos sem posicao: %s" % falta

Z_ANTIGO = {bn.name: (bn.matrix_local.to_3x3() @ V((0, 0, 1))) for bn in A.data.bones}
bpy.ops.object.select_all(action="DESELECT"); A.select_set(True); bpy.context.view_layer.objects.active = A
bpy.ops.object.mode_set(mode="EDIT")
for eb in A.data.edit_bones: eb.use_connect = False
for n, (h, t) in J.items():
    eb = A.data.edit_bones[n]; eb.head, eb.tail = h, t; eb.align_roll(Z_ANTIGO[n])
bpy.ops.object.mode_set(mode="OBJECT")

# ------------------------------------------------------------------ malha LOW (com mapas assados embutidos)
with bpy.data.libraries.load(LOW_BLEND) as (src, dst): dst.objects = ["SB_Dragao_LOW"]
low = dst.objects[0]; sc.collection.objects.link(low)
low.matrix_world = Matrix.Translation(V((0, DY, 0))) @ Matrix.Scale(K, 4)
bpy.ops.object.select_all(action="DESELECT"); low.select_set(True); bpy.context.view_layer.objects.active = low
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
mat = low.data.materials[0]
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")
pecas = [o for o in bpy.context.selected_objects if o.type == "MESH"]
pecas.sort(key=lambda o: -len(o.data.vertices)); corpo = pecas[0]
def extensao_x(o): xs = [v.co.x for v in o.data.vertices]; return max(xs) - min(xs)
def pesos(o, nome):
    g = o.vertex_groups.get(nome)
    if not g: return {}
    return {v.index: x.weight for v in o.data.vertices for x in v.groups if x.group == g.index and x.weight > 1e-4}
membranas = [o for o in pecas[1:] if extensao_x(o) > 0.25 and not pesos(o, "TAG_cabeca")]
rigidas = [o for o in pecas[1:] if o not in membranas]
print("RIG pecas: corpo %d verts, membranas %d, rigidas %d" % (len(corpo.data.vertices), len(membranas), len(rigidas)))
INFO = {o.name: (pesos(o, "SB_Mandibula"), bool(pesos(o, "TAG_cabeca")), bool(pesos(o, "TAG_mandibula"))) for o in pecas}
for o in pecas:                                             # grupos de marcacao saem antes do calor/limite de 4
    for nome in ("SB_Mandibula", "TAG_cabeca", "TAG_mandibula"):
        g = o.vertex_groups.get(nome)
        if g: o.vertex_groups.remove(g)
DEF = [bn for bn in A.data.bones if bn.use_deform]
def seg(bn): return A.matrix_world @ bn.head_local, A.matrix_world @ bn.tail_local
def dist_seg(p, bn):
    h, t = seg(bn); q, fr = intersect_point_line(p, h, t); fr = max(0.0, min(1.0, fr)); return (p - lerp(h, t, fr)).length

for bn in A.data.bones:
    if bn.name.startswith(("wing_feather_1", "wing_feather_2")) or bn.name.startswith(("horn_", "stomach_tip", "mouth_upper_tip", "mouth_lower_tip")):
        bn.use_deform = False
print("RIG corpo:", bind_mesh.run(armature=A.name, meshes=[corpo.name], method="auto", limit=4, clean=0.01))
for bn in A.data.bones:
    if bn.name not in ("root", "DRV_root"): bn.use_deform = True
def mandibula(o, wmap):
    """maxilar inferior: o peso de SB_Mandibula vai para mouth_lower, o resto dos ossos e escalado por (1-w); o que
    nao e maxilar na cabeca fica no head (o calor espalha pescoco/boca pelo cranio)"""
    ml = o.vertex_groups.get("mouth_lower") or o.vertex_groups.new(name="mouth_lower")
    # o calor espalha mouth_lower pelo labio de CIMA/ceu da boca (osso proximo): fora do grupo SB_Mandibula ele sai e o
    # peso vai para o head (r8: senao o labio superior descia junto ao abrir = boca "rasgada")
    gh = o.vertex_groups.get("head") or o.vertex_groups.new(name="head"); tirados = 0
    for v in o.data.vertices:
        if v.index in wmap: continue
        for x in v.groups:
            if x.group == ml.index and x.weight > 0:
                gh.add([v.index], x.weight, "ADD"); x.weight = 0.0; tirados += 1
    print("RIG mouth_lower removido de", tirados, "vertices fora da mandibula")
    for vi, w in wmap.items():
        v = o.data.vertices[vi]
        for x in v.groups:
            if x.group != ml.index: x.weight *= (1 - w)
        ml.add([vi], w, "ADD")
mandibula(corpo, INFO[corpo.name][0])
OSSOS_ASA = {s: [bn for bn in DEF if bn.name.endswith("_" + s) and bn.name.startswith(("wing_", "shoulder_"))] for s in ("l", "r")}
for o in membranas:
    lado = "l" if sum(v.co.x for v in o.data.vertices) > 0 else "r"
    cand = OSSOS_ASA[lado] + [A.data.bones[n] for n in ("spine_0", "spine_1", "hips")]
    for bn in cand:
        if bn.name not in o.vertex_groups: o.vertex_groups.new(name=bn.name)
    for v in o.data.vertices:
        p = o.matrix_world @ v.co
        ds = sorted(((dist_seg(p, bn), bn.name) for bn in cand))[:4]
        ws = [(1.0 / max(d, 0.004) ** 3, n) for d, n in ds]; s = sum(w for w, _ in ws)
        for w, n in ws: o.vertex_groups[n].add([v.index], w / s, "REPLACE")
REGRAS = lambda c: [bn for bn in DEF if not bn.name.startswith(("wing_feather", "shoulder_", "wing_", "mouth_", "horn_"))] if abs(c.x) < 0.3 else DEF
cont = {}
for o in rigidas:
    wm, cab_, mand_ = INFO[o.name]
    if wm:                                                   # pele interna da boca: estica entre head e mouth_lower
        gh = o.vertex_groups.new(name="head"); gm = o.vertex_groups.new(name="mouth_lower")
        for v in o.data.vertices:
            w = wm.get(v.index, 0.0); gh.add([v.index], 1 - w, "REPLACE"); gm.add([v.index], w, "REPLACE")
        cont["boca_ligacao"] = cont.get("boca_ligacao", 0) + 1; continue
    c = sum((o.matrix_world @ v.co for v in o.data.vertices), V()) / len(o.data.vertices)
    alvo = A.data.bones["mouth_lower"] if mand_ else A.data.bones["head"] if cab_ else min(REGRAS(c), key=lambda bn: dist_seg(c, bn))
    cont[alvo.name] = cont.get(alvo.name, 0) + 1
    g = o.vertex_groups.new(name=alvo.name); g.add([v.index for v in o.data.vertices], 1.0, "REPLACE")
print("RIG rigidas por osso:", dict(sorted(cont.items())))
bpy.ops.object.select_all(action="DESELECT")
for o in [corpo] + membranas + rigidas:
    for m in list(o.modifiers):
        if m.type == "ARMATURE": o.modifiers.remove(m)
    o.parent = None; o.select_set(True)
bpy.context.view_layer.objects.active = corpo; bpy.ops.object.join()
nova = corpo; bpy.data.objects.remove(VELHA, do_unlink=True)
nova.name = "Silverwing"; nova.data.name = "Silverwing"
nova.parent = A; nova.matrix_parent_inverse = A.matrix_world.inverted()
am = nova.modifiers.new("Armature", "ARMATURE"); am.object = A
bpy.ops.object.select_all(action="DESELECT"); nova.select_set(True); bpy.context.view_layer.objects.active = nova
bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=4)
bpy.ops.object.vertex_group_normalize_all(group_select_mode="ALL", lock_active=False)
sem = bind_mesh.unweighted(nova, A)
print("RIG_TRIS", sum(len(p.vertices) - 2 for p in nova.data.polygons), "sem_peso", sem, "grupos", len(nova.vertex_groups))
nova.data.materials.clear(); nova.data.materials.append(mat)
bpy.ops.wm.save_as_mainfile(filepath=SAIDA)
print("RIG_OK")
