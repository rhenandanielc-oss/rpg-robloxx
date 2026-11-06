# Wyvern (base Ashwing Drake Lite, Literock Studios - licenca: uso no jogo, sem redistribuir)
# E1 - proporcao oficial (RPG_02): 9-13 studs ate os ombros (dorso/cernelha), envergadura 30-42.
# O original tem asas ~6,7x a altura do ombro (fora da faixa oficial 2,3-4,7): encurta asas por escala
# uniforme no punho do braco (upperarm) e encurta a cauda SEM afinar (so desloca cada segmento).
# Depois escala tudo para studs (1 BU = 1 stud). Pesos, shape keys e clipes sao preservados.
# Uso: blender -b --factory-startup -P 01_proporcao.py -- <glb origem> <saida.blend> [ombro] [envergadura] [cauda]
import bpy, sys, json
from mathutils import Vector, Matrix
argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = argv[0], argv[1]
ALVO_OMBRO = float(argv[2]) if len(argv) > 2 else 10.0
ALVO_ENV = float(argv[3]) if len(argv) > 3 else 40.0
CAUDA = float(argv[4]) if len(argv) > 4 else 0.8

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
scn = bpy.context.scene
for o in list(bpy.data.objects):
    if o.name == "Icosphere": bpy.data.objects.remove(o)
arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
mesh = [o for o in bpy.data.objects if o.type == "MESH"][0]
arm.name = "Wyvern_Rig"; mesh.name = "Wyvern"

def fcurves(a):
    out = []
    for layer in a.layers:
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    return out

def usar(a):
    arm.animation_data.action = a
    try: arm.animation_data.action_slot = a.slots[0]
    except Exception: pass

# ---- cernelha no idle (so vertices dominados pela coluna toracica)
usar(bpy.data.actions["idle_loop"]); scn.frame_set(0)
dg = bpy.context.evaluated_depsgraph_get(); ev = mesh.evaluated_get(dg)
idx = {g.index for g in mesh.vertex_groups if g.name in ("spine_02", "spine_03")}
cern = 0.0
for v in mesh.data.vertices:
    gs = sorted(v.groups, key=lambda g: -g.weight)
    if gs and gs[0].group in idx: cern = max(cern, (mesh.matrix_world @ ev.data.vertices[v.index].co).z)
F = ALVO_OMBRO / cern
arm.animation_data.action = None
for pb in arm.pose.bones: pb.matrix_basis.identity()
scn.frame_set(0)

bones = arm.data.bones
def cadeia(raiz):
    r = [raiz]
    for c in bones[raiz].children_recursive: r.append(c.name)
    return r

# ---- asas: escala uniforme s em torno da cabeca do upperarm (mesmo efeito de escalar o osso na pose)
piv = {s: bones["upperarm_" + s].head_local.copy() for s in "LR"}
pont = max(abs((b.tail_local).x) for b in bones if b.name.endswith("_L"))
s_asa = (ALVO_ENV / (2 * F) - abs(piv["L"].x)) / (pont - abs(piv["L"].x))
asa = {s: cadeia("upperarm_" + s) for s in "LR"}

# ---- cauda: cada segmento k encolhe para CAUDA x comprimento; o deslocamento acumulado e por osso
cauda = ["tail_%02d" % i for i in range(1, 11)]
desl = {}
acc = Vector((0, 0, 0))
for i, n in enumerate(cauda):
    if i > 0:
        seg = bones[n].head_local - bones[cauda[i - 1]].head_local
        acc = acc + seg * (CAUDA - 1)
    desl[n] = acc.copy()
ult = bones[cauda[-1]]
desl_ponta = acc + (ult.tail_local - ult.head_local) * (CAUDA - 1)

def matriz_osso(n):
    for s in "LR":
        if n in asa[s]:
            p = piv[s]
            return Matrix.Translation(p) @ Matrix.Scale(s_asa, 4) @ Matrix.Translation(-p)
    if n in desl: return Matrix.Translation(desl[n])
    return None

gnome = {g.index: g.name for g in mesh.vertex_groups}
M = {g.index: matriz_osso(g.name) for g in mesh.vertex_groups}

def deformar(co, v):
    tot = sum(g.weight for g in v.groups) or 1.0
    out = Vector((0, 0, 0)); resto = 1.0
    for g in v.groups:
        m = M.get(g.group); w = g.weight / tot
        if m is not None: out += w * (m @ co); resto -= w
    return out + resto * co

me = mesh.data
if me.shape_keys:
    base = me.shape_keys.reference_key
    novos = {}
    for kb in me.shape_keys.key_blocks:
        novos[kb.name] = [deformar(kb.data[i].co, me.vertices[i]) for i in range(len(me.vertices))]
    for kb in me.shape_keys.key_blocks:
        for i, c in enumerate(novos[kb.name]): kb.data[i].co = c
    for i, c in enumerate(novos[base.name]): me.vertices[i].co = c
else:
    for v in me.vertices: v.co = deformar(v.co.copy(), v)

# ---- ossos em edicao
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.data.edit_bones
for b in eb:
    m = matriz_osso(b.name)
    if m is None: continue
    roll = b.roll
    if b.name in desl:
        h = b.head + desl[b.name]
        t = (b.tail + (desl_ponta if b.name == cauda[-1] else desl[cauda[cauda.index(b.name) + 1]])) if True else None
        b.head = h; b.tail = t
    else:
        b.head = m @ b.head; b.tail = m @ b.tail
    b.roll = roll
bpy.ops.object.mode_set(mode="OBJECT")

# ---- clipes: deslocamentos locais dos ossos encurtados acompanham a nova escala
for a in bpy.data.actions:
    for fc in fcurves(a):
        if not fc.data_path.endswith("location") or '"' not in fc.data_path: continue
        n = fc.data_path.split('"')[1]
        k = None
        for s in "LR":
            if n in asa[s] and n != "upperarm_" + s: k = s_asa
        if n in desl and n != "tail_01": k = CAUDA
        if k:
            for p in fc.keyframe_points:
                p.co.y *= k; p.handle_left.y *= k; p.handle_right.y *= k

# ---- escala global para studs: objetos + deslocamentos animados
for o in (arm, mesh):
    if o.parent is None: o.scale = (F, F, F)   # o filho herda do pai; escalar os dois dava F^2
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True); mesh.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
for a in bpy.data.actions:
    for fc in fcurves(a):
        if fc.data_path.endswith("location"):
            for p in fc.keyframe_points:
                p.co.y *= F; p.handle_left.y *= F; p.handle_right.y *= F

# ---- medidas finais
res = {"F_m_para_stud": round(F, 3), "cernelha_original_m": round(cern, 3), "escala_asa": round(s_asa, 3), "cauda": CAUDA}
for nome in ("idle_loop", "fly_loop", "walk_loop"):
    usar(bpy.data.actions[nome]); best = [0, 0, 0]; cz = 0
    for f in range(int(bpy.data.actions[nome].frame_range[1]) + 1):
        scn.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); ev = mesh.evaluated_get(dg)
        ws = [mesh.matrix_world @ v.co for v in ev.data.vertices]
        for i in range(3): best[i] = max(best[i], max(w[i] for w in ws) - min(w[i] for w in ws))
        if f == 0:
            for v in mesh.data.vertices:
                gs = sorted(v.groups, key=lambda g: -g.weight)
                if gs and gs[0].group in idx: cz = max(cz, ws[v.index].z)
    res[nome] = {"largura_max": round(best[0], 1), "comprimento_max": round(best[1], 1), "altura_max": round(best[2], 1), "cernelha_f0": round(cz, 2)}
arm.animation_data.action = None
for pb in arm.pose.bones: pb.matrix_basis.identity()
scn.frame_set(0); dg = bpy.context.evaluated_depsgraph_get(); ev = mesh.evaluated_get(dg)
ws = [mesh.matrix_world @ v.co for v in ev.data.vertices]
res["repouso_envergadura"] = round(max(w.x for w in ws) - min(w.x for w in ws), 1)
res["repouso_comprimento"] = round(max(w.y for w in ws) - min(w.y for w in ws), 1)
usar(bpy.data.actions["idle_loop"])
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("RESJSON" + json.dumps(res) + "RESFIM")
