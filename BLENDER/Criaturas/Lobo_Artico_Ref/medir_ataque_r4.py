"""QA numerico do ataque basico v43 r4 x r3 (17/11/2026), golpe sobreposto a locomocao como no Roblox.
Mede: focinho (avanco/altura no contato), abertura da mandibula por quadro, pata (altura maxima, alcance, ponta abaixo do
chao, distancia ate a outra pata = cruzamento, torcao do carpo em torno do proprio eixo), ombro (sobe?), translacao do
Pescoco1 e se as pernas SEM chave seguem a locomocao. Saida: review/v43r4/revisao/qa_r4.json + resumo no console.
Uso: blender -b anim_v43r4/CR_LoboArtico_Anim.blend -P medir_ataque_r4.py"""
import bpy, json, math, os
from mathutils import Vector as V
rig = bpy.data.objects["LoboArtico_Rig"]; sc = bpy.context.scene; P = rig.pose.bones; W = rig.matrix_world
def aplicar(n, q):
    ac = bpy.data.actions[n]; rig.animation_data.action = ac
    if len(ac.slots): rig.animation_data.action_slot = ac.slots[0]
    sc.frame_set(q); bpy.context.view_layer.update(); rig.animation_data.action = None
def canais(ac):
    r = {}
    for ly in ac.layers:
        for st in ly.strips:
            for cb in st.channelbags:
                for fc in cb.fcurves: r.setdefault(fc.data_path.split('"')[1], set()).add(fc.data_path.split(".")[-1])
    return r
def pose(g, qg, b, qb):
    ch = canais(bpy.data.actions[g])
    for pb in P: pb.matrix_basis.identity()
    aplicar(g, qg); val = {o: (P[o].rotation_quaternion.copy(), P[o].location.copy()) for o in ch}
    for pb in P: pb.matrix_basis.identity()
    aplicar(b, qb)
    for o, (r, l) in val.items():
        P[o].rotation_quaternion = r
        if "location" in ch[o]: P[o].location = l
    bpy.context.view_layer.update()
def pt(n, cauda=True): return W @ (P[n].tail if cauda else P[n].head)
def boca():
    c = (W.to_3x3() @ P["Cabeca"].matrix.to_3x3()).col[1].normalized(); m = (W.to_3x3() @ P["Mandibula"].matrix.to_3x3()).col[1].normalized()
    return math.degrees(c.angle(m))
def torcao(n):       # rotacao do osso em torno do proprio eixo Y relativo ao repouso (graus)
    q = P[n].matrix_basis.to_quaternion(); sw = q.to_swing_twist("Y")[1]; return abs(math.degrees(sw))
R = {}
for b in ("Repouso", "Andar", "Trote", "Corrida"):
    nb = int(bpy.data.actions[b].frame_range[1])
    for fase in ((0,) if b == "Repouso" else (0, nb // 2)):
        for g in ("Mordida1", "Mordida2", "GarraE", "GarraD"):
            for ver in (("R3_" + g, g, g + "_Corrida") if b == "Corrida" else ("R3_" + g, g)):
                linha = []
                for q in range(16):
                    for pb in P: pb.matrix_basis.identity()
                    aplicar(b, (fase + q) % max(nb, 1)); base_f = pt("Cabeca"); base_pe = pt("Dedos_E"); base_pd = pt("Dedos_D"); base_om = pt("Umero_E", False)
                    pose(ver, q, b, (fase + q) % max(nb, 1))
                    f = pt("Cabeca"); pe = pt("Dedos_E"); pd = pt("Dedos_D"); om = pt("Umero_E", False); omd = pt("Umero_D", False)
                    lado = "E" if g.endswith("E") else ("D" if g.endswith("D") else None)
                    pg = pe if lado == "E" else pd; po = pd if lado == "E" else pe; bg = base_pe if lado == "E" else base_pd
                    linha.append({"q": q, "focinho_frente": round(-(f.y - base_f.y), 3), "focinho_alt": round(f.z - base_f.z, 3), "focinho_lado": round(f.x - base_f.x, 3),
                                  "boca_graus": round(boca(), 1), "pata_z": round(pg.z, 3) if lado else None, "pata_frente_vs_loc": round(-(pg.y - bg.y), 3) if lado else None,
                                  "dist_outra_pata_x": round(abs(pg.x - po.x), 3) if lado else None, "pata_outra_z": round(po.z, 3) if lado else None,
                                  "ombro_dz": round((om if lado != "D" else omd).z - base_om.z, 3) if lado else None,
                                  "torcao_carpo": round(torcao("Metacarpo_" + lado), 1) if lado else None, "torcao_dedos": round(torcao("Dedos_" + lado), 1) if lado else None,
                                  "pescoco1_loc": round(P["Pescoco1"].location.length, 3)})
                R["%s|%s%d" % (ver, b, fase)] = linha
json.dump(R, open("review/v43r4/revisao/qa_r4.json", "w"), indent=0)
def res(k, g):
    L = R[k]; c = 6 if g.startswith("Mordida") else 7
    if g.startswith("Mordida"):
        return "contato: frente %.2f alt %.2f lado %.2f | boca q4 %.0f q5 %.0f q6 %.0f q8 %.0f | pescoco1 trans max %.2f" % (
            L[c]["focinho_frente"], L[c]["focinho_alt"], L[c]["focinho_lado"], L[4]["boca_graus"], L[5]["boca_graus"], L[6]["boca_graus"], L[8]["boca_graus"], max(x["pescoco1_loc"] for x in L))
    zs = [x["pata_z"] for x in L]
    return "pata z max %.2f min %.2f | contato frente(vs loc) %.2f z %.2f | outra pata x min %.2f | ombro dz max %.2f | torcao carpo max %.0f dedos %.0f" % (
        max(zs), min(zs), L[c]["pata_frente_vs_loc"], L[c]["pata_z"], min(x["dist_outra_pata_x"] for x in L), max(x["ombro_dz"] for x in L),
        max(x["torcao_carpo"] for x in L), max(x["torcao_dedos"] for x in L))
for k in R:
    g = k.split("|")[0].replace("R3_", "").replace("_Corrida", ""); print("QA", k, res(k, g), flush=True)
print("QA_R4_OK", flush=True)
