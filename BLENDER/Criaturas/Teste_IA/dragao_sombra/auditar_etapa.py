"""Auditoria de um grupo de clipes do Sombrio na malha de jogo (studs = unidades do rig x 17,5):
- malha abaixo do chao: z minimo e QUAL parte entra (osso dominante dos vertices mais baixos);
- ponta da cauda: z minimo do osso tail_tip;
- pes: deslize horizontal maximo dos dedos apoiados (clipes parados no lugar devem ficar ~0);
- laco: diferenca de pose entre o 1o e o ultimo quadro (clipes em laco);
- mandibula: abertura maxima (graus).
Uso: blender -b rig_com_clipes.blend -P auditar_etapa.py -- <saida.json> Clipe1,Clipe2,... [passo]"""
import bpy, sys, json, math
from collections import Counter
a = sys.argv[sys.argv.index("--") + 1:]; SAIDA = a[0]; NOMES = a[1].split(","); PASSO = int(a[2]) if len(a) > 2 else 2
ESC = 17.5
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
gi = {g.index: g.name for g in M.vertex_groups}
DONO = [gi[max(v.groups, key=lambda g: g.weight).group] if v.groups else "" for v in M.data.vertices]
def regiao(n):
    if n.startswith("tail"): return "cauda"
    if n.startswith(("wing", "shoulder")): return "asa"
    if n.startswith(("front_", "back_", "collar", "hips_anchor")): return "pata"
    if n.startswith(("head", "mouth", "horn")): return "cabeca"
    if n.startswith(("spine_2", "spine_3", "spine_4")): return "pescoco"
    return "tronco"
PT = ["front_toes_tip_l", "front_toes_tip_r", "back_toes_tip_l", "back_toes_tip_r"]
res = {}
for nome in NOMES:
    act = bpy.data.actions.get("Silverwing_" + nome)
    if not act: res[nome] = "FALTA"; continue
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range)
    zmin, quem, cauda, desl, mand = 9, Counter(), 9, 0.0, 0.0
    pes_ant = None; poses = []
    for f in list(range(f0, f1 + 1, PASSO)) + [f1]:
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh(); mw = M.matrix_world
        zs = sorted(((mw @ v.co).z, i) for i, v in enumerate(me.vertices))
        if zs[0][0] < zmin: zmin = zs[0][0]
        for z, i in zs[:40]:
            if z < -0.004: quem[regiao(DONO[i])] += 1
        M.evaluated_get(dg).to_mesh_clear()
        cauda = min(cauda, (A.matrix_world @ A.pose.bones["tail_tip"].tail).z)
        pes = {p: A.matrix_world @ A.pose.bones[p].tail for p in PT}
        if pes_ant:
            for p in PT:
                if pes[p].z < 0.02 and pes_ant[p].z < 0.02:
                    d_ = pes[p] - pes_ant[p]; desl = max(desl, math.hypot(d_.x, d_.y))
        pes_ant = pes
        q = A.pose.bones["mouth_lower"].matrix_basis.to_quaternion(); mand = max(mand, math.degrees(2 * math.acos(min(1, abs(q.w)))))
        poses.append({b.name: b.matrix_basis.to_quaternion() for b in A.pose.bones})
    laco = None
    if act.get("loop", True) is not False and len(poses) > 1:
        laco = round(max(math.degrees(poses[0][n].rotation_difference(poses[-1][n]).angle) for n in poses[0]), 2)
    res[nome] = {"malha_zmin_studs": round(zmin * ESC, 2), "quem_entra": dict(quem.most_common(3)), "cauda_ponta_zmin_studs": round(cauda * ESC, 2),
                 "pe_desliza_max_studs": round(desl * ESC, 2), "mandibula_max_graus": round(mand, 1), "laco_dif_graus": laco,
                 "duracao_s": round((f1 - f0) / sc.render.fps, 2)}
    print("AUD", nome, json.dumps(res[nome]))
json.dump(res, open(SAIDA, "w"), indent=1)
