"""Pata dianteira reta DE LADO, como na referencia (coluna vertical do cotovelo a pata). Medido no rig9 (lado_perna.py):
a malha do antebraco ja e vertical (linha central y ~ -4,1 de z 1,0 a 2,8), mas a pata fica 0,25 A FRENTE da coluna
(a perna parece dobrada embaixo) e os OSSOS nao seguem a perna: cotovelo na borda de tras (y -3,34), punho na borda da
frente (y -4,44) -> o antebraco cruza a perna na diagonal e, ao animar, torce a parte de baixo para tras.
Correcao: (1) malha abaixo do punho (z < Z1) recua ate DMAX com transicao suave (a pata fica sob a coluna, dedos para a
frente como antes); (2) ossos de repouso no CENTRO da perna: cotovelo na parte de tras da coluna, punho no centro
da coluna, articulacao do ombro a frente, base dos dedos recuada junto com a pata; ombro fixo; (3) IK refeito. Pesos/UV/textura intactos; simetrico.
Uso: blender -b rig9/Lobo_Ancestral_Rig.blend -P perna_reta_lateral.py -- <saida_dir>"""
import bpy, sys, os, json, math
import numpy as np
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
LO = bpy.data.objects["Lobo_Ancestral_LOW"]; arm = bpy.data.objects["Lobo_Ancestral_Rig"]; me = LO.data; BD = arm.data.bones
for pb in arm.pose.bones: pb.rotation_quaternion = (1, 0, 0, 0); pb.location = (0, 0, 0)
if arm.animation_data: arm.animation_data.action = None
def suave(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
Z0, Z1, DMAX = 0.45, 1.15, 0.25
# v1 (ombro fixo, cotovelo no centro): a cadeia ficou esticada (folga 0,03) e o IK nao alcancava as passadas (erro ate
# 0,36, escorregao 1,2). v2: articulacao do ombro A FRENTE (Y_OMBRO, dentro do peito, como no lobo real) e cotovelo na
# parte de tras da coluna (centro + RECUO_COT): folga ~0,33 e o antebraco segue quase vertical pela perna.
Y_OMBRO, RECUO_COT = -4.50, 0.18
def dy(z): return DMAX * suave((Z1 - np.asarray(z, float)) / (Z1 - Z0))
n = len(me.vertices); co = np.array([v.co[:] for v in me.vertices]); co0 = co.copy()
gi = {g.index: g.name for g in LO.vertex_groups}
cad = {"AntebracoE", "MaoE", "DedosE", "AntebracoD", "MaoD", "DedosD", "PeloCotoveloE", "PeloCotoveloD"}
w = np.array([sum(g.weight for g in v.groups if gi[g.group] in cad) for v in me.vertices])
viz = [[] for _ in range(n)]
for e in me.edges: a, b = e.vertices; viz[a].append(b); viz[b].append(a)
VZ = [np.array(v, int) for v in viz]
for _ in range(3): w = 0.5 * w + 0.5 * np.array([w[VZ[i]].mean() if len(VZ[i]) else w[i] for i in range(n)])
m = np.clip(w * 1.3, 0, 1) * (co[:, 1] < -2.6)                       # so as patas dianteiras
desl = dy(co[:, 2]) * m
co[:, 1] += desl
me.vertices.foreach_set("co", co.ravel()); me.update()
# centro da perna (E) depois do recuo, por altura
selE = (m > 0.5) & (co[:, 0] > 0)
def centro(z0, r=0.18):
    s = selE & (np.abs(co[:, 2] - z0) < r); y = co[s, 1]; return float((np.percentile(y, 15) + np.percentile(y, 85)) / 2)
y_cot = centro(BD["AntebracoE"].head_local.z, 0.25); y_pun = centro(BD["MaoE"].head_local.z, 0.2)
rel = {"Z0": Z0, "Z1": Z1, "DMAX": DMAX, "vertices_recuados": int((desl > 0.005).sum()), "y_cotovelo": round(y_cot, 3), "y_punho": round(y_pun, 3)}
print("CENTROS cotovelo %.3f punho %.3f" % (y_cot, y_pun))
bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.mode_set(mode="EDIT"); EB = arm.data.edit_bones
novo = {}
for s in ("E", "D"):
    cot = EB["Antebraco" + s].head.copy(); pun = EB["Mao" + s].head.copy(); bd = EB["Dedos" + s].head.copy(); td = EB["Dedos" + s].tail.copy()
    cot.y = y_cot + RECUO_COT; pun.y = y_pun; bd.y += float(dy(bd.z)); td.y += float(dy(td.z))
    novo[s] = (cot, pun, bd, td)
for s, (cot, pun, bd, td) in novo.items():                          # absolutos (ossos conectados compartilham pontos)
    omb = EB["Braco" + s].head.copy(); omb.y = Y_OMBRO
    for nm, h, t in (("Escapula" + s, EB["Escapula" + s].head.copy(), omb), ("Braco" + s, omb, cot), ("Antebraco" + s, cot, pun), ("Mao" + s, pun, bd), ("Dedos" + s, bd, td)):
        eb = EB[nm]; roll = eb.roll; eb.head = h; eb.tail = t; eb.roll = roll
    pc = EB.get("PeloCotovelo" + s)
    if pc: d_ = cot - pc.head; pc.head = pc.head + V((0, d_.y * 0.0, 0));
bpy.ops.object.mode_set(mode="OBJECT")
# IK das dianteiras: alvo no punho, polo atras do cotovelo, angulo do polo por busca
for s in ("E", "D"):
    b1, b2 = BD["Antebraco" + s], BD["Mao" + s]
    alvo = bpy.data.objects["IK_Mao" + s]; alvo.location = b2.head_local.copy(); alvo.rotation_mode = "QUATERNION"; alvo.rotation_quaternion = b2.matrix_local.to_quaternion()
    bpy.data.objects["Polo_Antebraco" + s].location = b1.head_local + V((0.0, 2.5, 0.0))
bpy.context.view_layer.update()
rel["polo"] = {}
for s in ("E", "D"):
    c = arm.pose.bones["Antebraco" + s].constraints["IK"]; b0 = BD["Braco" + s]
    def erro(a_):
        c.pole_angle = a_; bpy.context.view_layer.update(); return (arm.pose.bones[b0.name].tail - b0.tail_local).length
    a_ = min((erro(math.radians(g)), math.radians(g)) for g in range(-180, 180, 3))[1]
    for passo in (1.0, 0.25, 0.05): a_ = min([a_ + math.radians(passo * q) for q in range(-4, 5)], key=erro)
    c.pole_angle = a_; rel["polo"]["Mao" + s] = [round(math.degrees(a_), 2), round(erro(a_), 5)]; print("POLO", s, rel["polo"]["Mao" + s])
dg = bpy.context.evaluated_depsgraph_get(); ev = LO.evaluated_get(dg); mm = ev.to_mesh()
ce = np.array([v.co[:] for v in mm.vertices]); ev.to_mesh_clear()
rel["desvio_repouso_ik"] = float(np.abs(ce - co).max()); print("DESVIO repouso com IK %.5f" % rel["desvio_repouso_ik"])
rel["ossos"] = {b: [round(c_, 3) for c_ in BD[b].head_local] for b in ("BracoE", "AntebracoE", "MaoE", "DedosE")}
print("OSSOS", rel["ossos"])
json.dump(rel, open(os.path.join(OUT, "perna_reta_lateral.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "Lobo_Ancestral_Rig.blend")); print("PERNA_RETA_OK")
