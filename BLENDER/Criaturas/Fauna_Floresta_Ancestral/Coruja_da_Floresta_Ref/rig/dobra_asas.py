"""Resolve a pose de ASA FECHADA da coruja por ALVOS (a malha veio de asas abertas e a asa nao e plana: a parte interna cai
~60 graus, a externa e quase horizontal -> giros fixos deixavam penas para fora). Para cada osso da asa (pai -> filho):
  1) aponta o osso para um alvo anatomico de asa fechada (cotovelo atras, pulso a frente junto ao peito, mao para tras,
     ponta das primarias sobre a cauda);
  2) busca a ROLAGEM em torno do proprio eixo que minimiza: pena saindo para o lado (|x| > limite), pena entrando no tronco
     e pena abaixo do chao.
Grava as rotacoes LOCAIS (quaternions, lado E; o D e espelho) em rig/dobra_asas.json para as poses e os clipes.
Uso: blender -b rig/CR_Coruja_Rig.blend -P rig/dobra_asas.py -- <saida_json>"""
import bpy, sys, os, math, json
import numpy as np
from mathutils import Vector as V, Matrix, Quaternion
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
arm = bpy.data.objects["Coruja_Rig"]; PB = arm.pose.bones; B = arm.data.bones; O = bpy.data.objects["Coruja_Corpo"]
for b in PB: b.rotation_mode = "QUATERNION"; b.rotation_quaternion = (1, 0, 0, 0)
bpy.context.view_layer.update()
LADOS = (("E", 1), ("D", -1))
# alvos (onde a CAUDA de cada osso deve ficar, aproximado) - asa fechada de coruja ao lado do corpo, ponta sobre a cauda
ALVO_E = {"BracoAsa": V((0.165, 0.085, 0.330)), "AntebracoAsa": V((0.175, -0.060, 0.390)),
          "MaoAsa": V((0.165, 0.040, 0.360)), "Primarias": V((0.110, 0.250, 0.170))}
LIM_X = float(os.environ.get("LIM_X", "0.175")); Z_TOPO = float(os.environ.get("Z_TOPO", "0.45"))   # ombro ~0,43
rest = np.array([v.co[:] for v in O.data.vertices]); GN = {g.index: g.name for g in O.vertex_groups}
dom = np.array([max(((GN[g.group], g.weight) for g in v.groups), key=lambda e: e[1])[0] if v.groups else "" for v in O.data.vertices])
def coords():
    dg = bpy.context.evaluated_depsgraph_get(); ev = O.evaluated_get(dg); m = ev.to_mesh()
    c = np.empty(len(m.vertices) * 3); m.vertices.foreach_get("co", c); ev.to_mesh_clear(); return c.reshape(-1, 3)
LOG = {}; RES = {}
for l, sx in LADOS:
    CAD = [n + l for n in ("BracoAsa", "AntebracoAsa", "MaoAsa", "Primarias")]
    ALVO = {n + l: V((sx * v.x, v.y, v.z)) for n, v in ALVO_E.items()}
    asa = np.isin(dom, ["OmbroAsa" + l] + CAD) & (rest[:, 0] * sx > 0.10)
    def custo(mask):
        c = coords()[mask]; ax = c[:, 0] * sx
        fora = np.clip(ax - LIM_X, 0, None); dentro = np.clip(0.11 - ax, 0, None) * ((c[:, 2] > 0.14) & (c[:, 2] < 0.50) & (c[:, 1] < 0.12))
        chao = np.clip(0.01 - c[:, 2], 0, None); acima = np.clip(c[:, 2] - Z_TOPO, 0, None)   # (r2: painel subia acima do ombro)
        return float((fora ** 2).sum() * 4 + (dentro ** 2).sum() * 6 + (chao ** 2).sum() * 10 + (acima ** 2).sum() * 6)
    for nm in CAD:
        pb = PB[nm]; bpy.context.view_layer.update()
        H = pb.head.copy(); d_atual = (pb.tail - pb.head).normalized(); d_alvo = (ALVO[nm] - H).normalized()
        alinha = d_atual.rotation_difference(d_alvo); R0 = pb.matrix.to_3x3()
        mask = asa & np.isin(dom, CAD[CAD.index(nm):])
        def tenta(g):
            R = Quaternion(d_alvo, math.radians(g)).to_matrix() @ alinha.to_matrix() @ R0
            pb.matrix = Matrix.Translation(H) @ R.to_4x4(); bpy.context.view_layer.update(); return custo(mask)
        melhor = min((tenta(g), g) for g in range(-180, 180, 10))
        for passo in (5, 2):
            for g in (melhor[1] - passo, melhor[1] + passo):
                c_ = tenta(g)
                if c_ < melhor[0]: melhor = (c_, g)
        tenta(melhor[1])
        LOG[nm] = {"rolagem": melhor[1], "custo": round(melhor[0], 6), "quat_local": [round(x, 6) for x in pb.rotation_quaternion]}
        print("DOBRA", nm, LOG[nm], flush=True)
    c = coords()[asa]; ax = c[:, 0] * sx
    RES[l] = {"lateral_max": round(float(ax.max()), 3), "lateral_min": round(float(ax.min()), 3), "z_min": round(float(c[:, 2].min()), 3), "y_max": round(float(c[:, 1].max()), 3)}
print("DOBRA_RES", RES)
json.dump({"ossos": {k: v["quat_local"] for k, v in LOG.items()}, "rolagens": {k: v["rolagem"] for k, v in LOG.items()}, "medidas_asas": RES,
           "alvos_E": {k: list(v) for k, v in ALVO_E.items()}, "lim_x": LIM_X}, open(OUT, "w"), indent=1)
