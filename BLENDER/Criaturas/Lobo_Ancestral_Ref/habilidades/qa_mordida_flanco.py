"""QA da Hab_MordidaFlanco (20/11): um 2o lobo DEITADO (acao Lobo_Deitado) de lado na frente do atacante, com o flanco
(meio do tronco) no ponto onde o focinho fecha (marcador Contato). Mede quadro a quadro: focinho -> superficie do corpo
do alvo (vertice mais proximo), altura do focinho x faixa vertical do flanco, deslize das 4 patas (almofadas) e renderiza
frente / lado / tres quartos (Workbench) em quadros-chave. Uso:
blender -b rig18/Lobo_Ancestral_Anim_Finalizacao.blend -P habilidades/qa_mordida_flanco.py -- <saida_dir>"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; FPS = 30
arm = bpy.data.objects["Lobo_Ancestral_Rig"]; LO = bpy.data.objects["Lobo_Ancestral_LOW"]
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
act = bpy.data.actions["Lobo_Hab_MordidaFlanco"]; arm.animation_data.action = act
NQ = int(act.frame_range[1])
# alvo: copia do rig + malha, acao Deitado, girado 90 graus (flanco voltado para o atacante)
arm2 = arm.copy(); arm2.data = arm.data.copy(); sc.collection.objects.link(arm2)
LO2 = LO.copy(); LO2.data = LO.data.copy(); sc.collection.objects.link(LO2)
for m in LO2.modifiers:
    if m.type == "ARMATURE": m.object = arm2
LO2.parent = arm2 if LO.parent == arm else LO2.parent
arm2.animation_data_create(); arm2.animation_data.action = bpy.data.actions["Lobo_Deitado"]
for pb in arm2.pose.bones:
    for c in pb.constraints: c.mute = True
def boca(): return arm.matrix_world @ arm.pose.bones["Mandibula"].tail
def pata(k): return arm.matrix_world @ arm.pose.bones[k].tail
F_CONT = int(round(0.50 * FPS)) + 1
sc.frame_set(F_CONT); M = boca()
# r2: a BARRIGA (lado das patas) fica voltada para o atacante (+Y); r1 deixava o dorso
arm2.rotation_euler = (0, 0, math.radians(90)); sc.frame_set(F_CONT)
_pt = sum(((arm2.matrix_world @ arm2.pose.bones[k].tail) for k in ("MaoE", "MaoD", "MetatarsoE", "MetatarsoD")), V((0, 0, 0))) / 4
_pe = arm2.matrix_world @ ((arm2.pose.bones["Peito"].head + arm2.pose.bones["Pelve"].head) / 2)
if _pt.y < _pe.y: arm2.rotation_euler = (0, 0, math.radians(-90)); sc.frame_set(F_CONT)
print("ALVO giro", round(math.degrees(arm2.rotation_euler.z)))
dg = bpy.context.evaluated_depsgraph_get()
def verts2():
    ev = LO2.evaluated_get(bpy.context.evaluated_depsgraph_get()); mw = ev.matrix_world
    return [mw @ v.co for v in ev.data.vertices]
peito = arm2.matrix_world @ arm2.pose.bones["Peito"].head; pelve = arm2.matrix_world @ arm2.pose.bones["Pelve"].head
meio = (peito + pelve) / 2
vs = verts2()
faixa = [v for v in vs if abs(v.x - meio.x) < 0.6]
ylado = max(v.y for v in faixa)                               # superficie do flanco voltada para +Y (o atacante)
zs = [v.z for v in faixa if v.y > ylado - 0.5]; zmin, zmax = min(zs), max(zs)
arm2.location = (M.x - meio.x, M.y - ylado - 0.05, 0)        # flanco do meio do tronco encosta no focinho no Contato
print("FLANCO z %.2f-%.2f (focinho no contato z %.2f)" % (zmin, zmax, M.z))
reg = []
pe0 = {}
for f in range(1, NQ + 1):
    sc.frame_set(f); vs = verts2(); b = boca()
    d = min((v - b).length for v in vs)
    if f == F_CONT: pe0 = {k: pata(k) for k in ("MaoE", "MaoD", "MetatarsoE", "MetatarsoD")}
    reg.append({"t": round((f - 1) / FPS, 3), "boca_corpo": round(d, 3), "boca": [round(c, 3) for c in b],
                "patas": {k: [round(c, 3) for c in pata(k)] for k in ("MaoE", "MaoD", "MetatarsoE", "MetatarsoD")}})
seg = [r for r in reg if 0.50 <= r["t"] <= 1.85]
b0 = V(seg[0]["boca"])
desl = max((V(r["boca"]) - b0).length for r in seg)
pes = {k: max((V(r["patas"][k]) - pe0[k]).length for r in seg) for k in pe0}
res = {"flanco_z": [round(zmin, 2), round(zmax, 2)], "boca_contato_z": round(M.z, 2),
       "boca_corpo_segurando": {"min": min(r["boca_corpo"] for r in seg), "max": max(r["boca_corpo"] for r in seg)},
       "boca_deriva_max": round(desl, 3), "patas_deriva_max": {k: round(v, 3) for k, v in pes.items()},
       "antes_contato_boca_corpo": [r["boca_corpo"] for r in reg if r["t"] in (0.0, 0.2, 0.3, 0.4)]}
print("QA", json.dumps(res))
json.dump({"resumo": res, "quadros": reg}, open(os.path.join(OUT, "qa_mordida_flanco.json"), "w"), indent=1)
# renders: frente (camera a -Y olhando +Y), lado (+X), tres quartos
sc.render.engine = "BLENDER_WORKBENCH"; sc.render.resolution_x, sc.render.resolution_y = 560, 400
sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"
cam = bpy.data.objects.new("CamQA", bpy.data.cameras.new("CamQA")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 40
alvo_v = V((M.x, M.y - 1.0, 2.4))
VIS = {"cima": V((0.3, 0.6, 15.0)), "rasante": V((-9.0, -7.0, 2.2)), "tres_quartos": V((11.0, 9.0, 6.5)), "lado_atacante": V((-12.0, 3.0, 3.0))}
for nome, pos in VIS.items():
    cam.location = alvo_v + pos
    cam.rotation_euler = (alvo_v - cam.location).to_track_quat("-Z", "Y").to_euler()
    for t in (0.0, 0.30, 0.50, 0.75, 1.0, 1.25, 1.55, 1.85, 2.6):
        sc.frame_set(int(round(t * FPS)) + 1)
        sc.render.filepath = os.path.join(OUT, "%s_%04d.png" % (nome, int(t * 1000))); bpy.ops.render.render(write_still=True)
print("QA_OK")
