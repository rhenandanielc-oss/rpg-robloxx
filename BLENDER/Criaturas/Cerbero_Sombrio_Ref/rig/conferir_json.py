"""Confere os clipes exportados (JSON da ponte para o Studio) por REIMPORTACAO: aplica cada JSON no rig limpo (sem IK) e
compara com a acao FK do .blend de animacao. Por clipe: ossos e quadros, diferenca maxima de posicao das patas e das pontas
dos focinhos, pata mais baixa e continuidade do loop (ultimo quadro -> primeiro).
Uso: blender -b -t 4 CR_Cerbero_Rig.blend -P conferir_json.py -- <pasta_clipes>"""
import bpy, sys, os, json, glob
from mathutils import Vector as V, Quaternion
PASTA = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
arm = bpy.data.objects["Cerbero_Rig"]; PB = arm.pose.bones
with bpy.data.libraries.load(os.path.join(PASTA, "CR_Cerbero_Anim.blend")) as (src, dst):
    dst.actions = [a for a in src.actions if a.startswith("Cerbero_")]
for pb in PB:
    for c in pb.constraints: c.mute = True
PONTOS = ["MaoE", "MaoD", "PeE", "PeD", "CabecaC", "CabecaE", "CabecaD", "MandibulaC", "MandibulaE", "MandibulaD"]
def pontos(): bpy.context.view_layer.update(); return {n: PB[n].tail.copy() for n in PONTOS}
if not arm.animation_data: arm.animation_data_create()
linhas = []
for arq in sorted(glob.glob(os.path.join(PASTA, "Cerbero_*.json"))):
    d = json.load(open(arq)); nome = d["nome"]; nq = d["quadros"]; ossos = d["ossos"]
    faltam = [pb.name for pb in PB if pb.name not in ossos and pb.name not in d.get("pais_peso0", []) and not d.get("camada")]; dif = 0.0; zmin = 99.0; pts0 = None; ultimo = None
    act = bpy.data.actions[nome]
    for q in range(nq):
        arm.animation_data.action = act; bpy.context.scene.frame_set(q + 1); ref = pontos()
        arm.animation_data.action = None                  # L3: camada = pose da acao + ossos da mascara vindos do JSON
        for pb in PB:
            if pb.name not in ossos: continue
            s = ossos[pb.name][q * 7:(q + 1) * 7]; pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = Quaternion((s[3], s[0], s[1], s[2])); pb.location = V(s[4:7])
        js = pontos(); dif = max(dif, max((js[n] - ref[n]).length for n in PONTOS))
        zmin = min(zmin, min(js[n].z for n in ("MaoE", "MaoD", "PeE", "PeD")))
        if q == 0: pts0 = js
        ultimo = js
    salto = None
    if d["loop"]:                                         # loop: o quadro seguinte ao ultimo e o primeiro (passo de 1 quadro tipico)
        tip = max((ultimo[n] - pts0[n]).length for n in PONTOS); salto = round(tip, 3)
    linhas.append("%s;quadros=%d;ossos=%d;faltam=%s;dif_json_x_acao=%.5f;ponta_pata_min_z=%.3f;salto_loop_ultimo_primeiro=%s;eventos=%s" % (
        nome, nq, len(ossos), faltam, dif, zmin, salto, d.get("eventos")))
    print("JSON", linhas[-1], flush=True)
open(os.path.join(PASTA, "conferencia_json.txt"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
print("CONFERENCIA_OK")
