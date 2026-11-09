"""Patas dianteiras do Lobo Ancestral retas e DENTRO do corpo (pedido do usuario 04/11: "as duas, dentro do corpo, nao
pra fora"). No rig6 a linha dos ossos fica em +-1,3 e a borda externa da pata no cotovelo chega a 1,8, enquanto o peito
mede +-1,6 -> as patas abriam para fora. Aqui o antebraco, o punho e os dedos vao para x = +-X_PATA (vertical) e a
articulacao do ombro para +-X_OMBRO; escapula fixa. Traseiras: metatarso/pe em +-X_TRAS e joelho em +-X_JOELHO, quadril fixo. Malha e ossos de repouso deslocados JUNTOS (mesmo campo lateral por
altura), entao pesos/UV/topologia ficam validos; simetria exata mantida (campo aplicado com o sinal do lado).
IK refeito (alvos, polos, angulo do polo). Uso: blender -b rig6/Lobo_Ancestral_Rig.blend -P patas_para_dentro.py -- <saida_dir>"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
X_PATA, X_OMBRO = 0.95, 1.22                     # dianteiras: antebraco/punho/dedos e articulacao do ombro
X_TRAS, X_JOELHO = 1.0, 0.95                     # traseiras: metatarso/pe (vertical) e joelho; quadril fixo
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
def h(b): return BD[b + "E"].head_local
def t(b): return BD[b + "E"].tail_local
CAD = {"dian": {"ossos": ("Escapula", "Braco", "Antebraco", "Mao", "Dedos"), "frente": 1.0,
                "pts": [(t("Dedos").z, X_PATA - t("Dedos").x), (h("Dedos").z, X_PATA - h("Dedos").x), (h("Mao").z, X_PATA - h("Mao").x),
                        (h("Antebraco").z, X_PATA - h("Antebraco").x), (h("Braco").z, X_OMBRO - h("Braco").x), (h("Escapula").z, 0.0)]},
       "tras": {"ossos": ("Coxa", "Canela", "Metatarso", "Pe"), "frente": -1.0,
                "pts": [(t("Pe").z, X_TRAS - t("Pe").x), (h("Pe").z, X_TRAS - h("Pe").x), (h("Metatarso").z, X_TRAS - h("Metatarso").x),
                        (h("Canela").z, X_JOELHO - h("Canela").x), (h("Coxa").z, 0.0)]}}
for k, c_ in CAD.items():
    c_["pts"].sort(); c_["zs"] = np.array([p[0] for p in c_["pts"]]); c_["dx"] = np.array([p[1] for p in c_["pts"]])
    print("campo", k, [(round(a, 2), round(b, 3)) for a, b in c_["pts"]])
def campo(k, z): return np.interp(z, CAD[k]["zs"], CAD[k]["dx"])
# ------------------------------------------------------------------ malha
n = len(me.vertices); co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3); co0 = co.copy()
gi = {g.index: g.name for g in LO.vertex_groups}
viz = [[] for _ in range(n)]
for e in me.edges: a, b = e.vertices; viz[a].append(b); viz[b].append(a)
VZ = [np.array(v, int) for v in viz]
lado = np.sign(co[:, 0]); lado[np.abs(co[:, 0]) < 1e-6] = 0
y_omb = BD["BracoE"].head_local.y; y_cox = BD["CoxaE"].head_local.y
dx = np.zeros(n)
for k, c_ in CAD.items():
    cad = {o + s for o in c_["ossos"] for s in "ED"}
    m = np.array([sum(g.weight for g in v.groups if gi[g.group] in cad) for v in me.vertices])
    for _ in range(3): m = 0.5 * m + 0.5 * np.array([m[VZ[i]].mean() if len(VZ[i]) else m[i] for i in range(n)])
    m = np.clip(m * 1.25, 0, 1)
    if k == "dian": m *= np.clip((y_omb + 1.7 - co[:, 1]) / 0.8, 0, 1)          # nao alcanca o flanco
    else: m *= np.clip((co[:, 1] - (y_cox - 1.9)) / 0.8, 0, 1)
    dx += campo(k, co[:, 2]) * m * lado * np.clip(np.abs(co[:, 0]) / 0.35, 0, 1)   # linha central fixa
co[:, 0] += dx
me.vertices.foreach_set("co", co.ravel()); me.update()
print("MALHA movidos", int((np.abs(dx) > 0.005).sum()), "max %.3f" % np.abs(dx).max())
# ------------------------------------------------------------------ ossos de repouso (mesmo campo)
bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); EB = arm.data.edit_bones
# posicoes ABSOLUTAS calculadas do repouso original (ossos conectados compartilham cabeca/cauda: somar em cada um
# deslocava duas vezes - v1 deixou o cotovelo/punho fora da malha)
novo = {}
for k, c_ in CAD.items():
    for s, sx in (("E", 1), ("D", -1)):
        for nm in c_["ossos"]:
            eb = EB[nm + s]; hd, tl = eb.head.copy(), eb.tail.copy()
            hd.x += sx * float(campo(k, hd.z)); tl.x += sx * float(campo(k, tl.z)); novo[nm + s] = (hd, tl, eb.roll)
for nm, (hd, tl, roll) in novo.items():
    eb = EB[nm]; eb.head = hd; eb.tail = tl; eb.roll = roll
bpy.ops.object.mode_set(mode="OBJECT")
# ------------------------------------------------------------------ IK: alvos, polos e angulo do polo
rel = {"X_PATA": X_PATA, "X_OMBRO": X_OMBRO, "X_TRAS": X_TRAS, "X_JOELHO": X_JOELHO, "polo": {}}
CH = [("Braco", "Antebraco", "Mao", 1.0), ("Coxa", "Canela", "Metatarso", -1.0)]
for b0n, b1n, b2n, fr in CH:
    for s in ("E", "D"):
        b1, b2 = BD[b1n + s], BD[b2n + s]
        alvo = bpy.data.objects["IK_" + b2n + s]; alvo.location = b2.head_local.copy(); alvo.rotation_mode = "QUATERNION"; alvo.rotation_quaternion = b2.matrix_local.to_quaternion()
        bpy.data.objects["Polo_" + b1n + s].location = b1.head_local + V((0.0, 2.5 * fr, 0.0))
bpy.context.view_layer.update()
for b0n, b1n, b2n, fr in CH:
    for s in ("E", "D"):
        c = arm.pose.bones[b1n + s].constraints["IK"]; b0 = BD[b0n + s]
        def erro(a_):
            c.pole_angle = a_; bpy.context.view_layer.update(); return (arm.pose.bones[b0.name].tail - b0.tail_local).length
        a_ = min((erro(math.radians(g)), math.radians(g)) for g in range(-180, 180, 3))[1]
        for passo in (1.0, 0.25, 0.05): a_ = min([a_ + math.radians(passo * q) for q in range(-4, 5)], key=erro)
        c.pole_angle = a_; rel["polo"][b2n + s] = [round(math.degrees(a_), 2), round(erro(a_), 5)]; print("POLO", b2n + s, rel["polo"][b2n + s])
dg = bpy.context.evaluated_depsgraph_get(); ev = LO.evaluated_get(dg); mm = ev.to_mesh()
ce = np.array([v.co[:] for v in mm.vertices]); ev.to_mesh_clear()
rel["desvio_repouso_ik"] = float(np.abs(ce - co).max()); print("DESVIO repouso com IK %.5f" % rel["desvio_repouso_ik"])
rel["ossos"] = {b + s: [round(c_, 3) for c_ in BD[b + s].head_local] for b in ("Braco", "Antebraco", "Mao", "Dedos", "Coxa", "Canela", "Metatarso", "Pe") for s in "ED"}
json.dump(rel, open(os.path.join(OUT, "patas_para_dentro.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("PATAS_PARA_DENTRO_OK")
