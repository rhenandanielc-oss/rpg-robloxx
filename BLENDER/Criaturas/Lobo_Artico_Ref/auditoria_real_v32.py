"""Auditoria contra lobo real (so leitura, sobre a anim_v31): medidas de POSE e de MARCHA das 12 acoes e da pose neutra do rig.
Unidades: stud; comprimentos tambem em CC = comprimento do corpo (focinho a base da cauda, no repouso) e AO = altura da cernelha no repouso.
Por acao (estatisticas por quadro): cernelha z (Coluna3 cabeca), garupa z (Quadril cabeca), inclinacao do dorso (graus, + = frente mais
alta), cabeca/focinho em relacao a cernelha (z), angulo do pescoco, cauda (Cauda1 e corda base-ponta, graus abaixo da horizontal),
oscilacao vertical e de arfagem; por pata: x do MCP no apoio (bitola: distancia lateral E-D no apoio), alcance a frente/atras do
ombro/quadril no apoio, fator de carga (apoio/ciclo), fase do toque; quadros sem nenhuma pata no chao (suspensao) e pares no chao.
Uso: blender -b anim_v31/CR_LoboArtico_Anim.blend -P auditoria_real_v32.py -- <saida_json>"""
import bpy, sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marcha_v21 as M
import marchas_v29 as MV
from mathutils import Vector as V
OUTJ = sys.argv[sys.argv.index("--") + 1:][0]; SRC = os.path.dirname(bpy.data.filepath)
ARM = M.ARM; P = M.P; sc = bpy.context.scene
CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); G = MV.marchas(CJ)
TJ = {}
for fn in ("marchas_v29.json", "transicoes_v25.json", "viradas_v27.json"):
    for k, v in json.load(open(os.path.join(SRC, fn)))["acoes"].items(): TJ[k] = v
def apoio(ac, k, q):
    if ac == "Repouso": return True
    return bool(TJ[ac]["apoio_por_quadro"][k][q]) if ac in TJ else bool(MV.apoio(G, {"acoes": {}}, ac, k, q))
OMBRO = {"DE": "Umero_E", "DD": "Umero_D", "TE": "Coxa_E", "TD": "Coxa_D"}; MCP = {k: c[2] for k, c in M.PATAS.items()}
def ang_h(v): return math.degrees(math.atan2(-v.z, math.hypot(v.x, v.y)))       # graus abaixo da horizontal
def medir():
    c3 = P["Coluna3"].head; qd = P["Quadril"].head; cb = P["Cabeca"].head; fo = P["Cabeca"].tail; pz = P["Pescoco1"].head
    d = {"cernelha_z": c3.z, "garupa_z": qd.z, "dorso_graus": math.degrees(math.atan2(c3.z - qd.z, qd.y - c3.y)), "cabeca_rel_cernelha": cb.z - c3.z,
         "focinho_rel_cernelha": fo.z - c3.z, "pescoco_graus": -ang_h(cb - pz), "cauda1_graus": ang_h(P["Cauda1"].tail - P["Cauda1"].head),
         "cauda_corda_graus": ang_h(P["Cauda4"].tail - P["Cauda1"].head), "cauda_ponta_z": P["Cauda4"].tail.z}
    for k in M.PATAS:
        m = P[MCP[k]].tail; o = P[OMBRO[k]].head; d["mcp_x_" + k] = m.x; d["mcp_y_rel_" + k] = m.y - o.y; d["mcp_z_" + k] = m.z
    return d
# pose neutra do rig (repouso do esqueleto, sem acao)
ARM.animation_data.action = None
for pb in P: pb.matrix_basis.identity()
bpy.context.view_layer.update(); NEUTRA = medir()
CC = abs(P["Cabeca"].tail.y - P["Cauda1"].head.y); AO = P["Coluna3"].head.z
OUT = {"referencia": {"CC_comprimento_corpo": CC, "AO_altura_cernelha": AO}, "pose_neutra": NEUTRA, "acoes": {}}
for ac in ["Repouso", "Andar", "Trote", "Corrida", "Arrancada", "Frenagem", "VirarEsquerda", "VirarDireita", "AndarParaTrote", "TroteParaAndar", "TroteParaCorrida", "CorridaParaTrote"]:
    acn = bpy.data.actions[ac]; ARM.animation_data.action = acn
    if len(acn.slots): ARM.animation_data.action_slot = acn.slots[0]
    f0, f1 = (int(x) for x in acn.frame_range); fr = []; ap = []
    for q in range(f0, f1 + 1):
        sc.frame_set(q); bpy.context.view_layer.update(); fr.append(medir()); ap.append({k: apoio(ac, k, q - f0) for k in M.PATAS})
    est = {m: {"min": round(min(f[m] for f in fr), 3), "max": round(max(f[m] for f in fr), 3), "media": round(sum(f[m] for f in fr) / len(fr), 3)} for m in fr[0]}
    bit = {}
    for par, (e, dd) in (("dianteira", ("DE", "DD")), ("traseira", ("TE", "TD"))):
        xe = [f["mcp_x_" + e] for f, a in zip(fr, ap) if a[e]]; xd = [f["mcp_x_" + dd] for f, a in zip(fr, ap) if a[dd]]
        bit[par] = round((sum(xe) / len(xe) - sum(xd) / len(xd)), 3) if xe and xd else None
    n = len(fr); susp = sum(1 for a in ap if not any(a.values())); nchao = [sum(a.values()) for a in ap]
    fc = {k: round(sum(a[k] for a in ap) / n, 3) for k in M.PATAS}
    alc = {k: [round(min(f["mcp_y_rel_" + k] for f, a in zip(fr, ap) if a[k]), 3), round(max(f["mcp_y_rel_" + k] for f, a in zip(fr, ap) if a[k]), 3)] if any(a[k] for a in ap) else None for k in M.PATAS}
    OUT["acoes"][ac] = {"quadros": n, "estatisticas": est, "bitola_no_apoio": bit, "fator_carga_aprox": fc, "quadros_suspensao": susp,
                        "patas_no_chao_min_max": [min(nchao), max(nchao)], "alcance_mcp_no_apoio_rel_ombro": alc,
                        "bob_vertical_cernelha": round(est["cernelha_z"]["max"] - est["cernelha_z"]["min"], 3)}
    print("AUD", ac, json.dumps({"dorso": est["dorso_graus"], "cabeca": est["cabeca_rel_cernelha"], "cauda": est["cauda_corda_graus"], "bitola": bit, "susp": susp}), flush=True)
OUT["marchas_parametros"] = {g: {"T_s": G[g]["T"], "cadencia_hz": round(1 / G[g]["T"], 3), "v_stud_s": G[g]["v_studs_s"], "passada_stud": round(G[g]["v_studs_s"] * G[g]["T"], 3),
                                 "passada_CC": round(G[g]["v_studs_s"] * G[g]["T"] / CC, 3), "passada_AO": round(G[g]["v_studs_s"] * G[g]["T"] / AO, 3), "v_CC_por_s": round(G[g]["v_studs_s"] / CC, 3),
                                 "fator_carga": G[g]["apoio"], "fases": G[g]["fases"]} for g in ("Andar", "Trote", "Corrida")}
json.dump(OUT, open(OUTJ, "w"), indent=1); print("AUDITORIA_REAL_OK", json.dumps(OUT["referencia"]), json.dumps(OUT["marchas_parametros"]), flush=True)
