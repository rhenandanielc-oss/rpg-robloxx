"""Montaria M4 (09/11/2026, Studio autorizado): exporta o cavaleiro de TESTE (manequim R15 aproximado) das acoes
DEMO_Cav_Montar_E / DEMO_Cav_Desmontar_E / DEMO_Cav_Sentado para o Studio, no MESMO formato JSON dos clipes do urso (para o
empacotar_clipes.py e o decodificador do AdaptadorUrso): "ossos" = partes do R15; canais qx qy qz qw = rotacao da PARTE no
mundo do Studio; tx ty tz = centro da parte no Studio (so no LowerTorso; nas demais 0), relativo a RootPart do urso (Studio = (-x, z, y) do Blender; a origem
do Blender e a RootPart). O Studio converte isso em Pose/Transform das juntas do R15 real. 15 qps.
Uso: blender -b CR_Urso_v2_M2_montaria.blend -P m4_exportar_cavaleiro.py -- <pasta_saida>"""
import bpy, sys, os, json
from mathutils import Matrix, Vector as V
A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "Crocodilo_Primordial_Ref", "scripts")))
import manequim_r15 as mq
sc = bpy.context.scene; ra = bpy.data.objects["TESTE_Manequim_R15aprox_Rig"]
for pb in ra.pose.bones:
    for c in pb.constraints: c.mute = True
C = Matrix(((-1, 0, 0), (0, 0, 1), (0, 1, 0)))                 # Blender -> Studio
PASSO = 2
LISTA = (("DEMO_Cav_Montar_E", "Cav_Montar_E"), ("DEMO_Cav_Desmontar_E", "Cav_Desmontar_E"), ("DEMO_Cav_Sentado", "Cav_Sentado"),
         ("DEMO_Cav_Montar_D", "Cav_Montar_D"), ("DEMO_Cav_Desmontar_D", "Cav_Desmontar_D"))      # lado D: 09/11 (Studio lado D)
for acao, nome in LISTA:
    act = bpy.data.actions[acao]; ra.animation_data.action = act; f1 = int(act.frame_range[1]); qs = list(range(1, f1 + 1, PASSO))
    if qs[-1] != f1: qs.append(f1)
    ossos = {p: [] for p in mq.PARTES}
    for f in qs:
        sc.frame_set(f); bpy.context.view_layer.update()
        for p, (_, _, _, tam, cen) in mq.PARTES.items():
            Md = ra.matrix_world @ ra.pose.bones[p].matrix @ ra.data.bones[p].matrix_local.inverted()
            c_ = C @ (Md @ V(cen)); R_ = (C @ Md.to_3x3() @ C.transposed()).to_quaternion()
            if p != "LowerTorso": c_ = V((0, 0, 0))                    # so o quadril precisa de posicao (as outras juntas giram)
            ossos[p] += [round(R_.x, 5), round(R_.y, 5), round(R_.z, 5), round(R_.w, 5), round(c_.x, 5), round(c_.y, 5), round(c_.z, 5)]
    d = {"nome": nome, "fps": 15, "loop": False, "quadros": len(qs), "duracao": (len(qs) - 1) / 15, "velocidade": 0, "ossos": ossos}
    json.dump(d, open(os.path.join(OUT, nome + ".json"), "w"), separators=(",", ":")); print("CAV", nome, len(qs))
json.dump({}, open(os.path.join(OUT, "manifesto_clipes.json"), "w"))
print("CAV_OK")
