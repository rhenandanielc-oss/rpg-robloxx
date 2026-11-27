"""Mede os 6 pontos das pupilas (mesma busca do aura/fx_vigilia.py r3) em repouso e grava em JSON, ja no eixo do jogo
(x, z, y do Blender -> modelo: (-x, z, y) a partir da Raiz, como as chamas da aura). Uso: blender -b -t 1 CR_Cerbero_Fogo_A3.blend -P medir_olhos.py -- <saida.json>"""
import bpy, sys, json
from mathutils import Vector as V
A = sys.argv[sys.argv.index("--") + 1:]
rig = bpy.data.objects["Cerbero_Rig"]; BD = rig.data.bones
for pb in rig.pose.bones:
    for c in pb.constraints: c.mute = True
if rig.animation_data: rig.animation_data.action = None
for pb in rig.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()
CAB = bpy.data.objects["Cerbero_Cabecas"]
Mi = CAB.matrix_world.inverted(); res = []
for k in "CED":
    h_, t_ = BD["Cabeca" + k].head_local, BD["Cabeca" + k].tail_local
    fr_ = V((t_.x - h_.x, t_.y - h_.y, 0)).normalized(); lat = fr_.cross(V((0, 0, 1)))
    for lado in (-1, 1):
        for sobe, abre, recua in ((0.55, 0.62, 0.15), (0.45, 0.72, 0.3), (0.65, 0.55, 0.0)):
            alvo = t_ + V((0, 0, sobe)) + lat * lado * abre - fr_ * recua
            o_ = Mi @ (alvo + fr_ * 4.0); d_ = (Mi.to_3x3() @ (-fr_)).normalized()
            ok, loc, nrm, idx = CAB.ray_cast(o_, d_, distance=8.0)
            if ok:
                p = CAB.matrix_world @ loc + fr_ * 0.15
                res.append({"osso": "Cabeca" + k, "lado": lado, "blender": [round(p.x, 3), round(p.y, 3), round(p.z, 3)]}); break
raiz = rig.matrix_world @ BD["Raiz"].head_local
json.dump({"raiz_blender": list(raiz), "olhos": res}, open(A[0], "w"), indent=1)
print("OLHOS_OK", len(res), res)
