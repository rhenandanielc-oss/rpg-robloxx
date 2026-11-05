"""E4b r2 (com auxiliares de volume Cotovelo_Aux/Punho_Aux a meia rotacao). E4b: poses extremas por articulacao, medicoes e closes (textura e arame). Mesmo rig de teste para E4 e E4b.
Medicoes por pose, na zona da articulacao (esfera em volta da junta) e no corpo inteiro:
- razao de comprimento das arestas (posada / repouso): p1, p99, min, max e contagens fora de [0,6 ; 1,5];
- espessura: distancia de cada vertice da zona ate a cadeia de ossos (pai+filho), posada / repouso: p5 e min (afinamento).
Flexao com sinal automatico (o sinal que fecha o angulo entre os dois ossos).
Uso: blender -b <arquivo_com_rig.blend> -P e4b_04_poses.py -- <juntas.json> <saida_dir> [renders=1]"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix, Euler
A = sys.argv[sys.argv.index("--") + 1:]; J = json.load(open(A[0])); OUT = os.path.abspath(A[1]); REND = (A[2] != "0") if len(A) > 2 else True
os.makedirs(OUT, exist_ok=True); sc = bpy.context.scene
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
for pb in arm.pose.bones: pb.rotation_mode = "XYZ"
me = ob.data; co0 = np.array([v.co for v in me.vertices]); E = np.array([e.vertices[:] for e in me.edges])
L0 = np.linalg.norm(co0[E[:, 0]] - co0[E[:, 1]], axis=1)
TRI = np.array([(p.vertices[0], p.vertices[k], p.vertices[k + 1]) for p in me.polygons for k in range(1, len(p.vertices) - 1)])
def volume(P): a_, b_, c_ = P[TRI[:, 0]], P[TRI[:, 1]], P[TRI[:, 2]]; return float(np.einsum("ij,ij->i", a_, np.cross(b_, c_)).sum() / 6)
V0 = volume(co0)
qa_ = me.attributes.get("qa_juba"); JU = np.zeros(len(co0), np.float32)
if qa_: qa_.data.foreach_get("value", JU)
GI = {g.name: g.index for g in ob.vertex_groups}
def peso_cadeia(nomes):
    """soma do peso dos ossos da cadeia (e dos auxiliares do mesmo lado) por vertice"""
    lado = nomes[-1].split("_")[-1]; alvo = {GI[k] for k in GI if k in nomes or (k.startswith(("Cotovelo_Aux", "Punho_Aux")) and k.endswith(lado))}
    w = np.zeros(len(co0))
    for v in me.vertices:
        for g in v.groups:
            if g.group in alvo: w[v.index] += g.weight
    return w
E_PELE = (JU[E[:, 0]] < 0.01) & (JU[E[:, 1]] < 0.01)       # arestas de pele (fora da juba e das mechas)
def zerar():
    for pb in arm.pose.bones: pb.rotation_euler = (0, 0, 0); pb.location = (0, 0, 0)
def mundo(nome):
    pb = arm.pose.bones[nome]; return np.array(arm.matrix_world @ pb.head), np.array(arm.matrix_world @ pb.tail)
def angulo(pai, filho):
    a0, a1 = mundo(pai); b0, b1 = mundo(filho); u = (a1 - a0) / np.linalg.norm(a1 - a0); v = (b1 - b0) / np.linalg.norm(b1 - b0)
    return math.degrees(math.acos(np.clip(u @ v, -1, 1)))
def flex(filho, graus):
    """dobra a junta entre o pai e o filho: escolhe o sinal (eixo X local) que AUMENTA o desvio entre as direcoes"""
    pb = arm.pose.bones[filho]; pai = pb.parent.name; base = pb.rotation_euler.copy(); melhor = None
    for sgn in (1, -1):
        pb.rotation_euler = (base.x + math.radians(sgn * graus), base.y, base.z); bpy.context.view_layer.update()
        a = angulo(pai, filho)
        if melhor is None or a > melhor[0]: melhor = (a, sgn)
    pb.rotation_euler = (base.x + math.radians(melhor[1] * graus), base.y, base.z); bpy.context.view_layer.update()
def girar(nome, rx=0, ry=0, rz=0):
    pb = arm.pose.bones[nome]; pb.rotation_euler = (pb.rotation_euler.x + math.radians(rx), pb.rotation_euler.y + math.radians(ry), pb.rotation_euler.z + math.radians(rz))
    bpy.context.view_layer.update()
def avanca(nome, graus, direcao):
    """gira o osso no eixo X local no sentido que leva a ponta para a direcao dada (ex.: (0,-1,0) = para a frente)"""
    pb = arm.pose.bones[nome]; base = pb.rotation_euler.copy(); melhor = None
    for sgn in (1, -1):
        pb.rotation_euler = (base.x + math.radians(sgn * graus), base.y, base.z); bpy.context.view_layer.update()
        t = mundo(nome)[1] @ np.array(direcao)
        if melhor is None or t > melhor[0]: melhor = (t, sgn)
    pb.rotation_euler = (base.x + math.radians(melhor[1] * graus), base.y, base.z); bpy.context.view_layer.update()
D, T = J["DD"], J["TD"]
POSES = [  # nome, funcao, centro da zona, raio, cadeia de ossos para a espessura, camera (alvo, azimute, elevacao, distancia)
 ("ombro_avanco", lambda: (avanca("Escapula_DD", 12, (0, -1, 0)), avanca("Umero_DD", 38, (0, -1, 0))), D["ombro"], 2.6, ["Escapula_DD", "Umero_DD"], (D["ombro"], -75, 5, 11)),
 ("cotovelo_dobra", lambda: flex("Antebraco_DD", 95), D["cotovelo"], 1.3, ["Umero_DD", "Antebraco_DD"], (D["cotovelo"], -80, 5, 9)),
 ("punho_dobra", lambda: flex("Mao_DD", 85), D["punho"], 0.9, ["Antebraco_DD", "Mao_DD"], (D["punho"], -80, 5, 7)),
 ("passo_dianteiro", lambda: (avanca("Umero_DD", 28, (0, -1, 0)), flex("Antebraco_DD", 70), flex("Mao_DD", 55)), D["cotovelo"], 2.4, ["Umero_DD", "Antebraco_DD", "Mao_DD"], (D["cotovelo"], -80, 5, 14)),
 ("quadril_recuo", lambda: avanca("Coxa_TD", 32, (0, 1, 0)), T["quadril"], 2.4, ["Quadril", "Coxa_TD"], (T["quadril"], -80, 5, 12)),
 ("joelho_dobra", lambda: flex("Canela_TD", 70), T["joelho"], 1.3, ["Coxa_TD", "Canela_TD"], (T["joelho"], -80, 5, 9)),
 ("jarrete_dobra", lambda: flex("Metatarso_TD", 75), T["jarrete"], 1.0, ["Canela_TD", "Metatarso_TD"], (T["jarrete"], -80, 5, 8)),
 ("passo_traseiro", lambda: (avanca("Coxa_TD", 22, (0, -1, 0)), flex("Canela_TD", 55), flex("Metatarso_TD", 50)), T["joelho"], 2.6, ["Coxa_TD", "Canela_TD", "Metatarso_TD"], (T["joelho"], -80, 5, 15)),
 ("pescoco_baixo_virado", lambda: (girar("Pescoco1", rx=-18, rz=18), girar("Pescoco2", rx=-15, rz=15), girar("Cabeca", rx=-10, rz=10)), J["pescoco"][1], 3.6, ["Peito", "Pescoco1", "Pescoco2"], (J["pescoco"][1], -45, 10, 20)),
 ("coluna_curva", lambda: [girar(b, rz=10) for b in ("Coluna1", "Coluna2", "Peito")], J["coluna"][2], 3.4, ["Quadril", "Coluna1", "Coluna2", "Peito"], ((0, -1, 9), -30, 50, 40)),
 ("cauda_curva", lambda: [girar("Cauda%d" % i, rx=14, rz=12) for i in range(1, 7)], J["cauda"][1], 1.3, ["Quadril", "Cauda1", "Cauda2"], (J["cauda"][2], -70, 10, 16)),
 ("boca_32", lambda: girar("Mandibula", rx=0) or flex_boca(32), J["mandibula"]["pivo"], 1.8, ["Cabeca", "Mandibula"], ((-0.2, -14.2, 12.4), -40, 6, 7)),
]
def flex_boca(g):
    pb = arm.pose.bones["Mandibula"]; z0 = mundo("Mandibula")[1][2]
    pb.rotation_euler = (math.radians(g), 0, 0); bpy.context.view_layer.update()
    if mundo("Mandibula")[1][2] > z0: pb.rotation_euler = (math.radians(-g), 0, 0); bpy.context.view_layer.update()
def posado():
    dg = bpy.context.evaluated_depsgraph_get(); m = ob.evaluated_get(dg).to_mesh(); p = np.array([v.co for v in m.vertices]); ob.evaluated_get(dg).to_mesh_clear(); return p
def dist_cadeia(P, segs):
    d = np.full(len(P), 1e9)
    for a, b in segs:
        ab = b - a; t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-9), 0, 1); d = np.minimum(d, np.linalg.norm(P - (a + t[:, None] * ab), axis=1))
    return d
# cena para renders
w = bpy.data.worlds.new("N"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.62, 0.62, 0.62, 1)
sol = bpy.data.lights.new("Sol", "SUN"); sol.energy = 2.2; sol.angle = math.radians(40)
so = bpy.data.objects.new("Sol", sol); sc.collection.objects.link(so); so.rotation_euler = (math.radians(35), 0, math.radians(20))
sc.render.engine = "BLENDER_EEVEE"; sc.render.film_transparent = True; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 50
arame = ob.copy(); arame.name = "_arame"; sc.collection.objects.link(arame)
wm = arame.modifiers.new("Arame", "WIREFRAME"); wm.thickness = 0.012; wm.use_replace = True; wm.use_even_offset = False
ma = bpy.data.materials.new("_arame"); ma.use_nodes = True; nt = ma.node_tree; em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (0.05, 0.05, 0.08, 1)
nt.links.new(em.outputs[0], nt.nodes["Material Output"].inputs[0])
arame.data = ob.data; arame.material_slots[0].link = "OBJECT"; arame.material_slots[0].material = ma
for i in range(1, len(arame.material_slots)): arame.material_slots[i].link = "OBJECT"; arame.material_slots[i].material = ma
arame.hide_render = True
def vista(nome, alvo, az, el, dist, res=560, com_arame=False):
    alvo = Vector(alvo)
    cam.location = alvo + Vector((-math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el)))) * dist
    cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
    arame.hide_render = not com_arame
    sc.render.resolution_x = sc.render.resolution_y = res; sc.render.filepath = os.path.join(OUT, nome + ".png"); bpy.ops.render.render(write_still=True)
rel = {}
zerar(); bpy.context.view_layer.update(); REP = posado()
for nome, fn, centro, raio, cadeia, camv in POSES:
    if os.environ.get('R2_POSES') and nome not in os.environ['R2_POSES'].split(','): continue
    zerar(); bpy.context.view_layer.update()
    segs0 = [mundo(b) for b in cadeia]
    if REND:
        vista(nome + "_0_tex", *camv); vista(nome + "_0_arame", *camv, com_arame=True)
    fn()
    for t_, c_ in (("Cotovelo_Aux_DD", "Antebraco_DD"), ("Cotovelo_Aux_DE", "Antebraco_DE"), ("Punho_Aux_DD", "Mao_DD"), ("Punho_Aux_DE", "Mao_DE")):
        if t_ in arm.pose.bones: e_ = arm.pose.bones[c_].rotation_euler; arm.pose.bones[t_].rotation_euler = (e_.x * 0.5, e_.y * 0.5, e_.z * 0.5)   # auxiliar de volume: metade do filho
    for t_, c_ in (("Tufo1", "Cauda5"), ("Tufo2", "Cauda6")):   # secundarios do tufo acompanham a cauda (no rig final: restricao)
        if t_ in arm.pose.bones: arm.pose.bones[t_].rotation_euler = arm.pose.bones[c_].rotation_euler.copy()
    bpy.context.view_layer.update(); segs1 = [mundo(b) for b in cadeia]; P = posado()
    L1 = np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1); r = L1 / np.maximum(L0, 1e-6)
    c = np.array(centro, float); zona_v = np.linalg.norm(co0 - c, axis=1) < raio; zona_e = zona_v[E[:, 0]] & zona_v[E[:, 1]]
    d0 = dist_cadeia(co0[zona_v], segs0); d1 = dist_cadeia(P[zona_v], segs1); ok = d0 > 0.15; esp = d1[ok] / d0[ok]
    if zona_e.sum() < 3 or ok.sum() < 3: print("POSE", nome, "zona vazia"); continue
    rz = r[zona_e]
    top = np.argsort(-np.abs(np.log(np.maximum(r, 1e-6))))[:5]
    ext = [[round(float(r[k_]), 2)] + [round(float(c_), 1) for c_ in (co0[E[k_, 0]] + co0[E[k_, 1]]) / 2] for k_ in top]
    rel[nome] = {"zona": {"arestas": int(zona_e.sum()), "razao_p1": round(float(np.percentile(rz, 1)), 3), "razao_p99": round(float(np.percentile(rz, 99)), 3),
                          "razao_min": round(float(rz.min()), 3), "razao_max": round(float(rz.max()), 3), "fora_0.6_1.5": int(((rz < 0.6) | (rz > 1.5)).sum()),
                          "espessura_p5": round(float(np.percentile(esp, 5)), 3), "espessura_min": round(float(esp.min()), 3), "espessura_p95": round(float(np.percentile(esp, 95)), 3)},
                 "corpo": {"razao_min": round(float(r.min()), 3), "razao_max": round(float(r.max()), 3), "fora_0.6_1.5": int(((r < 0.6) | (r > 1.5)).sum()),
                           "alongamento_abs_max": round(float((L1 - L0).max()), 3), "arestas_esticadas_>1.5x_e_>0.05": int(((r > 1.5) & (L1 - L0 > 0.05)).sum())}}
    rel[nome]["piores_arestas_corpo"] = ext
    rel[nome]["pele_fora_da_juba"] = {"razao_max": round(float(r[E_PELE].max()), 3), "alongamento_abs_max": round(float((L1 - L0)[E_PELE].max()), 3),
                                      "arestas_esticadas_>1.5x_e_>0.05": int(((r > 1.5) & (L1 - L0 > 0.05) & E_PELE).sum())} if qa_ else None
    if cadeia[-1].endswith(("_DD", "_TD")):   # "pele da pata": vertices da zona que pertencem a pata (peso da cadeia >= 0,5), sem as mechas em volta
        # esfera maior (2,2): no cotovelo a esfera de 1,3 so pega as mechas da juba que cobrem a junta
        z2 = (np.linalg.norm(co0 - c, axis=1) < max(raio, 2.2)) & (peso_cadeia(cadeia) >= 0.5)
        e0 = dist_cadeia(co0[z2], segs0); e1 = dist_cadeia(P[z2], segs1); k2 = e0 > 0.15; es = e1[k2] / e0[k2]
        rel[nome]["zona"].update({"pata_vertices": int(k2.sum()), "pata_espessura_p5": round(float(np.percentile(es, 5)), 3) if k2.sum() > 3 else None,
                                  "pata_espessura_min": round(float(es.min()), 3) if k2.sum() > 3 else None})
    pele_v = (JU[zona_v] < 0.01)[ok]
    if qa_ and pele_v.sum() > 3: rel[nome]["pele_fora_da_juba"].update({"espessura_p5": round(float(np.percentile(esp[pele_v], 5)), 3), "espessura_min": round(float(esp[pele_v].min()), 3), "vertices_zona": int(pele_v.sum())})
    rel[nome]["volume_perdido_studs3"] = round(V0 - volume(P), 3)   # perda de volume do corpo inteiro na pose (afinamento por mistura de ossos)
    print("POSE", nome, json.dumps(rel[nome]), flush=True)
    if REND:
        vista(nome + "_1_tex", *camv); vista(nome + "_1_arame", *camv, com_arame=True)
zerar(); bpy.context.view_layer.update()
json.dump(rel, open(os.path.join(OUT, "poses.json"), "w"), indent=1); print("POSES_OK")
