"""Analise frontal (ortografica) da leitura do peito/juba, so leitura: classifica a malha em CABECA, JUBA/PEITO e CORPO
(pelos pesos dominantes + posicao), renderiza mascaras de cada classe e a malha base, e grava as coordenadas projetadas
dos eixos anatomicos (cranio, esterno, coluna, pelve) para a sobreposicao (sobrepor_frontal.py). Tambem mede, por
faixa de altura, extremos e centro de cada classe e o volume (area) a esquerda/direita da linha central.
Uso: blender -b <blend com rig> -P analise_frontal.py -- <saida_dir> [acao] [quadro]"""
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
ACAO = A[1] if len(A) > 1 else None; Q = int(A[2]) if len(A) > 2 else 0
sc = bpy.context.scene; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]
for o in sc.objects:
    if (o.type == "MESH" and o is not LO) or o.type == "EMPTY": o.hide_render = True
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
    pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if ACAO:
    act = bpy.data.actions[ACAO]; arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    sc.frame_set(int(act.frame_range[0]) + Q)
bpy.context.view_layer.update()
gi = {g.index: g.name for g in LO.vertex_groups}
def dono(v): return gi[max(v.groups, key=lambda q: q.weight).group] if v.groups else ""
CAB = {"Cabeca", "Mandibula", "OrelhaE", "OrelhaD"}; JUB = {"JubaE", "JubaD", "JubaPeito", "Pescoco1", "Pescoco2", "Peito"}
y_omb = arm.data.bones["BracoE"].head_local.y
classe = []
for v in LO.data.vertices:
    d = dono(v)
    if d in CAB: classe.append(2)
    elif d in JUB and v.co.y < y_omb + 0.5 and v.co.z > 3.4: classe.append(1)
    else: classe.append(0)
dg = bpy.context.evaluated_depsgraph_get(); ev = LO.evaluated_get(dg).to_mesh()
pos = np.array([LO.matrix_world @ v.co for v in ev.vertices]); cls = np.array(classe)
# copias estaticas por classe (malha avaliada) para as mascaras
def copia(nome, k):
    bm = bmesh.new(); bm.from_mesh(ev)
    bm.verts.ensure_lookup_table()
    apagar = [f for f in bm.faces if not all(cls[v.index] == k for v in f.verts)]
    bmesh.ops.delete(bm, geom=apagar, context="FACES")
    m = bpy.data.meshes.new(nome); bm.to_mesh(m); bm.free()
    o = bpy.data.objects.new(nome, m); sc.collection.objects.link(o); o.matrix_world = LO.matrix_world
    mat = bpy.data.materials.new(nome)
    if mat.node_tree is None: mat.use_nodes = True
    nt = mat.node_tree; out = nt.nodes["Material Output"]; em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (1, 1, 1, 1)
    nt.links.new(em.outputs[0], out.inputs[0]); m.materials.append(mat); o.hide_render = True; return o
MASC = {k: copia("Masc_" + n, k) for k, n in ((0, "corpo"), (1, "juba"), (2, "cabeca"))}
LO.evaluated_get(dg).to_mesh_clear()
for o in sc.objects:
    if o.name.startswith("Plane"): o.hide_render = True
W = H = 1000; ESC = 9.5; ZC = 4.3
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 8; sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.film_transparent = True
cam = sc.camera; camd = cam.data; camd.type = "ORTHO"; camd.ortho_scale = ESC; cam.location = V((0, -30, ZC)); cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.filepath = os.path.join(OUT, "base.png"); bpy.ops.render.render(write_still=True)
LO.hide_render = True
for k, o in MASC.items():
    for o2 in MASC.values(): o2.hide_render = o2 is not o
    sc.render.filepath = os.path.join(OUT, "mascara_%d.png" % k); bpy.ops.render.render(write_still=True)
def px(x, z): return (float((x / ESC + 0.5) * W), float((1 - ((z - ZC) / ESC + 0.5)) * H))
PB = arm.pose.bones
def mw(p): return arm.matrix_world @ p
eixos = {}
nariz = pos[np.argmin(pos[:, 1])]; ore = [mw(PB["OrelhaE"].tail), mw(PB["OrelhaD"].tail)]
meio_or = (ore[0] + ore[1]) / 2
eixos["cranio"] = [px(meio_or.x, meio_or.z), px(nariz[0], nariz[2])]
eixos["orelhas"] = [px(ore[0].x, ore[0].z), px(ore[1].x, ore[1].z)]
# esterno: pontos mais a frente do peito (classe juba/corpo) por faixa de altura, media de x dos 30 mais frontais
est = []
for z0 in np.arange(3.2, 6.4, 0.4):
    s = (np.abs(pos[:, 2] - z0) < 0.2) & (cls != 2) & (pos[:, 1] < y_omb + 0.5)
    if s.sum() > 30:
        idx = np.argsort(pos[s][:, 1])[:30]; est.append((float(pos[s][idx][:, 0].mean()), float(z0)))
eixos["esterno"] = [px(x, z) for x, z in est]
eixos["coluna"] = [px(mw(PB[b].head).x, mw(PB[b].head).z) for b in ("Pelve", "Coluna1", "Coluna2", "Peito", "Pescoco1", "Pescoco2", "Cabeca")]
eixos["pelve"] = [px(mw(PB["CoxaE"].head).x, mw(PB["CoxaE"].head).z), px(mw(PB["CoxaD"].head).x, mw(PB["CoxaD"].head).z)]
eixos["ombros"] = [px(mw(PB["BracoE"].head).x, mw(PB["BracoE"].head).z), px(mw(PB["BracoD"].head).x, mw(PB["BracoD"].head).z)]
med = {"cranio_inclinacao_graus": round(float(math.degrees(math.atan2(nariz[0] - meio_or.x, meio_or.z - nariz[2]))), 2),
       "nariz_x": round(float(nariz[0]), 3), "orelhas_meio_x": round(float(meio_or.x), 3), "orelhas_dz": round(float(ore[0].z - ore[1].z), 3),
       "esterno_x": [round(x, 3) for x, z in est], "esterno_z": [round(z, 2) for x, z in est]}
for k, nome in ((1, "juba"), (0, "corpo")):
    faixas = []
    for z0 in np.arange(2.8, 7.4, 0.4):
        s = (np.abs(pos[:, 2] - z0) < 0.2) & (cls == k) & ((pos[:, 1] < y_omb + 0.5) if k == 1 else (pos[:, 1] < y_omb + 1.2))
        if s.sum() > 20:
            xs = pos[s][:, 0]; faixas.append({"z": round(float(z0), 2), "x_min": round(float(xs.min()), 3), "x_max": round(float(xs.max()), 3),
                                              "meio": round(float((xs.min() + xs.max()) / 2), 3), "media": round(float(xs.mean()), 3),
                                              "frac_dir_pos": round(float((xs > 0).mean()), 3)})
    med[nome] = faixas
json.dump({"eixos_px": eixos, "medidas": med, "escala": ESC, "zc": ZC, "W": W, "H": H}, open(os.path.join(OUT, "analise.json"), "w"), indent=1)
print("ANALISE_OK", json.dumps({k: med[k] for k in ("cranio_inclinacao_graus", "nariz_x", "orelhas_meio_x", "orelhas_dz")}))
for f in med["juba"]: print("  JUBA z=%.1f [%+.2f %+.2f] meio=%+.2f media=%+.2f frac(x>0)=%.2f" % (f["z"], f["x_min"], f["x_max"], f["meio"], f["media"], f["frac_dir_pos"]))
print("  ESTERNO", list(zip(med["esterno_z"], med["esterno_x"])))
