"""Maior velocidade de osso (cabeca do osso no espaco do modelo, studs/s) por clipe no Blender, quadro a quadro (30 Hz),
nos mesmos 10 ossos medidos no Studio (lote 3, 04/11): base para separar acao rapida intencional de estalo.
Uso: blender -b CR_Urso_v2_Anim.blend -P studio/vel_ossos_blender.py"""
import bpy, json
arm = bpy.data.objects["Urso_Rig"]; sc = bpy.context.scene
for pb in arm.pose.bones:
    for c in pb.constraints: c.mute = True
OSS = ["Raiz", "Cabeca", "Mandibula", "MaoE", "MaoD", "PeE", "PeD", "DedosE", "DedosD", "OrelhaE"]
res = {}
for c in ["Observar", "Sentar", "LevantarSentado", "Deitar", "LevantarDeitado", "Comer", "Ameaca", "GolpePata", "Mordida", "ReacaoImpacto", "Repouso", "Rugir"]:
    act = bpy.data.actions["Urso_" + c]; arm.animation_data.action = act
    f0, f1 = [int(x) for x in act.frame_range]; prev = None; mx = (0, "", 0)
    for f in range(f0, f1 + 1):
        sc.frame_set(f); p = {o: arm.pose.bones[o].head.copy() for o in OSS}
        if prev:
            for o in OSS:
                v = (p[o] - prev[o]).length * 30
                if v > mx[0]: mx = (round(v, 1), o, f - 1)
        prev = p
    res[c] = mx
print("VELOSSOS " + json.dumps(res))
