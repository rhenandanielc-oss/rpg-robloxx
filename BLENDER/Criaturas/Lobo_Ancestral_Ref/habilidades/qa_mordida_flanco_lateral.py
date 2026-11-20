"""QA da Hab_MordidaFlanco contra o alvo CAIDO DE LADO (20/11, queda lateral). Um 2o lobo toca CaidoLado<E|D> com a
BARRIGA (lado das patas) voltada para o atacante; o meio do tronco (entre Peito e Pelve) encosta no focinho no
marcador Contato. Mede: focinho -> superficie do TRONCO (so pele de Peito/Coluna/Pelve), onde a boca cai ao longo do
tronco (0 = peito, 1 = pelve), distancia do focinho as pernas do alvo, malha do atacante dentro do tronco, deslize das
patas e renders (cima / rasante / tres quartos / lado proximo). Uso:
blender -b rig18/Lobo_Ancestral_Anim_Queda.blend -P habilidades/qa_mordida_flanco_lateral.py -- <saida> <E|D>"""
import bpy, sys, os, json, math
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); LADO = A[1]; CLIPE = A[2] if len(A) > 2 else "Hab_MordidaFlancoLado"; os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; FPS = 30
arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
act = bpy.data.actions["Lobo_" + CLIPE]; arm.animation_data.action = act; NQ = int(act.frame_range[1])
arm2 = arm.copy(); arm2.data = arm.data.copy(); sc.collection.objects.link(arm2)
LO2 = LO.copy(); LO2.data = LO.data.copy(); sc.collection.objects.link(LO2)
for m in LO2.modifiers:
    if m.type == "ARMATURE": m.object = arm2
if LO.parent == arm: LO2.parent = arm2
arm2.animation_data_create(); arm2.animation_data.action = bpy.data.actions["Lobo_CaidoLado" + LADO]
for pb in arm2.pose.bones:
    for c in pb.constraints: c.mute = True
gi = {g.index: g.name for g in LO.vertex_groups}
def dono(v): return gi[max(v.groups, key=lambda g: g.weight).group] if v.groups else "-"
def pele(v): return sum(g.weight for g in v.groups if gi[g.group].startswith(("Pelo", "Cauda"))) < 0.05
TRONCO = [v.index for v in LO.data.vertices if v.groups and pele(v) and dono(v) in ("Peito", "Coluna1", "Coluna2", "Pelve")]
PERNAS = [v.index for v in LO.data.vertices if v.groups and dono(v).startswith(("Braco", "Antebraco", "Mao", "Dedos", "Coxa", "Canela", "Metatarso", "Pe"))]
CAB1 = [v.index for v in LO.data.vertices if v.groups and dono(v) in ("Cabeca", "Mandibula")]
def boca(): return arm.matrix_world @ arm.pose.bones["Mandibula"].tail
def pata(k): return arm.matrix_world @ arm.pose.bones[k].tail
def mw_verts(obj, idx):
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()); mw = ev.matrix_world; d = ev.data.vertices
    return [mw @ d[i].co for i in idx]
F_CONT = int(round(0.50 * FPS)) + 1
sc.frame_set(F_CONT); M = boca()
def bones2(n): return arm2.matrix_world @ arm2.pose.bones[n].head
for giro in (90, -90):                                           # barriga (lado das patas) voltada para +Y (o atacante)
    arm2.rotation_euler = (0, 0, math.radians(giro)); arm2.location = (0, 0, 0); sc.frame_set(F_CONT)
    pt = sum((arm2.matrix_world @ arm2.pose.bones[k].tail for k in ("MaoE", "MaoD", "MetatarsoE", "MetatarsoD")), V()) / 4
    if pt.y > ((bones2("Peito") + bones2("Pelve")) / 2).y: break
peito, pelve = bones2("Peito"), bones2("Pelve"); meio = (peito + pelve) / 2
tr = mw_verts(LO2, TRONCO)
faixa = [v for v in tr if abs(v.x - meio.x) < 0.6]
ylado = max(v.y for v in faixa)                                   # superficie da barriga/flanco voltada para o atacante
zs = [v.z for v in faixa if v.y > ylado - 0.5]
arm2.location = (M.x - meio.x, M.y - ylado - 0.05, 0); sc.frame_set(F_CONT)
peito, pelve = bones2("Peito"), bones2("Pelve")
print("ALVO giro %d; barriga z %.2f-%.2f; focinho no contato z %.2f" % (round(math.degrees(arm2.rotation_euler.z)), min(zs), max(zs), M.z))
reg = []; pe0 = {}
for f in range(1, NQ + 1):
    sc.frame_set(f); b = boca(); tr = mw_verts(LO2, TRONCO); pr = mw_verts(LO2, PERNAS)
    vt = min(tr, key=lambda v: (v - b).length); d = (vt - b).length
    eixo = pelve - peito; u = (vt - peito).dot(eixo) / eixo.length_squared       # 0 peito .. 1 pelve
    dp = min((v - b).length for v in pr)
    cab = mw_verts(LO, CAB1); dentro = sum(1 for v in cab[::4] if min((w - v).length for w in tr[::3]) < 0.08)
    if f == F_CONT: pe0 = {k: pata(k) for k in ("MaoE", "MaoD", "MetatarsoE", "MetatarsoD")}
    reg.append({"t": round((f - 1) / FPS, 3), "boca_tronco": round(d, 3), "ao_longo": round(u, 2), "boca_pernas": round(dp, 3),
                "cabeca_encostada": dentro, "boca": [round(c, 3) for c in b],
                "patas": {k: [round(c, 3) for c in pata(k)] for k in ("MaoE", "MaoD", "MetatarsoE", "MetatarsoD")}})
seg = [r for r in reg if 0.50 <= r["t"] <= 1.85]; b0 = V(seg[0]["boca"])
res = {"clipe": CLIPE, "lado": LADO, "barriga_z": [round(min(zs), 2), round(max(zs), 2)], "boca_contato_z": round(M.z, 2),
       "boca_tronco_segurando": [min(r["boca_tronco"] for r in seg), max(r["boca_tronco"] for r in seg)],
       "ao_longo_tronco": [min(r["ao_longo"] for r in seg), max(r["ao_longo"] for r in seg)],
       "boca_pernas_min": min(r["boca_pernas"] for r in seg),
       "boca_deriva_max": round(max((V(r["boca"]) - b0).length for r in seg), 3),
       "patas_deriva_max": {k: round(max((V(r["patas"][k]) - pe0[k]).length for r in seg), 3) for k in pe0},
       "antes_contato": [(r["t"], r["boca_tronco"]) for r in reg if r["t"] in (0.0, 0.2, 0.3, 0.4)]}
print("QA", json.dumps(res))
json.dump({"resumo": res, "quadros": reg}, open(os.path.join(OUT, "qa_lateral_%s_%s.json" % (CLIPE, LADO)), "w"), indent=1)
sc.render.engine = "BLENDER_WORKBENCH"; sc.render.resolution_x, sc.render.resolution_y = 560, 400
sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
cam = bpy.data.objects.new("CamQA", bpy.data.cameras.new("CamQA")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 40
alvo_v = V((M.x, M.y - 0.4, 1.2)); print("CENA boca", tuple(round(c, 2) for c in M), "alvo meio", tuple(round(c, 2) for c in meio + arm2.location))
VIS = {"cima": (V((0.3, 0.6, 15.0)), 60), "perto_lado": (V((12.0, 3.0, 5.5)), 45), "perto_outro": (V((-12.0, 3.0, 5.5)), 45),
       "rasante": (V((12.0, -3.5, 2.0)), 45)}       # perto: por cima das costas do atacante (o alvo fica deitado ao longo de X)                  # perto: boca, barriga, patas e chao, dos dois lados
for nome, (pos, lens) in VIS.items():
    cam.data.lens = lens; cam.location = alvo_v + pos; cam.rotation_euler = (alvo_v - cam.location).to_track_quat("-Z", "Y").to_euler()
    for t in (0.0, 0.30, 0.50, 1.0, 1.55, 2.6):
        sc.frame_set(int(round(t * FPS)) + 1)
        sc.render.filepath = os.path.join(OUT, "%s_%s_%s_%04d.png" % (CLIPE, LADO, nome, int(t * 1000))); bpy.ops.render.render(write_still=True)
print("QA_OK")
