"""v24: correcao do DESLIZE dos apoios em Andar, Trote e Corrida (anim_v23 so lido; saida <dir>). Diagnostico
(diag_apoios_v24.py, mesmo metodo do auditar_clipes_v21): o pivo do rolamento C (70% do osso dos dedos) fica PARADO no apoio
(erro ~1e-5: trajetoria e IK certos); o deslize vem do ROLAMENTO em torno de pontos que ficam ACIMA da sola:
- o metacarpo/metatarso gira em torno de C, que esta na linha do osso dos dedos (~0,1-0,2 acima do chao);
- os dedos sao reapontados para a PONTA do osso (tambem acima da sola) -> a almofada plantada dos dedos (peso ~1 em Dedos)
  anda para tras ate 0,034 no fim do apoio, ainda no chao.
Correcao (so o rolamento; cronograma, cadencia, passada, alturas, dobras, corpo, cabeca e cauda IGUAIS):
- pivo do metacarpo/metatarso a F_PIVO = 0,8 do osso dos dedos (v23: 0,7) e DESCIDO da linha do osso em direcao a sola
  L_PIVO = 0,25 nas traseiras e L_PIVO_D = 0,20 nas dianteiras (v23: 0, na linha do osso); a mesma regra nos 3 LODs;
- os dedos apontam para a ALMOFADA plantada dos dedos (centro dos vertices da sola do LOW com osso dominante Dedos, na altura
  da sola) em vez da ponta do osso.
Escolha medida (auditoria oficial, LOW/LOD1/LOD2): pivo na articulacao MCP (dedos parados) -> almofada do metacarpo desliza
0,06; pivo no chao sob a MCP ou sob C -> dedos afundam 0,07-0,19; grade F x L (0,4-1,0 x 0-0,8, dedos para a ponta ou
para a almofada): 0,8 x 0,25 com dedos para a almofada = menor deslize sem aumentar o afundamento (ver ficha 8.26).
Sem rolamento (rolo = 0) a pose e identica a da v23 (o pivo so importa quando gira): a mudanca fica no fim do apoio e na
saida do balanco, continua.
Procedimento por quadro: pose da v23 (todos os ossos) -> refaz SO as 4 patas pelo mesmo IK analitico de 2 ossos gravado em FK
(marcha_v21.py), com os mesmos parametros de cada marcha (clipes_v21.json; Andar = clipes_v12.py: centro 0, rolo_ini 0,72).
VERIFICAR=1: reconstroi com o pivo ANTIGO e mede a diferenca para a v23 (prova de que a reconstrucao e fiel).
Uso: blender -b anim_v23/CR_LoboArtico_Anim.blend -P clipes_v24.py -- <dir_saida>"""
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector as V, Matrix
import marcha_v21 as M
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
VERIF = bool(os.environ.get("VERIFICAR"))
CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
if not VERIF:
    for f in os.listdir(SRC):
        if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
    for im in bpy.data.images:
        fp = bpy.path.abspath(im.filepath)
        if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
A = CJ["marchas"]["Andar"]
G = {"Andar": {"T": A["T"], "D": A["D"], "apoio": A["apoio"], "fases": A["fases"], "centro": {k: 0.0 for k in M.PATAS},
               "altura": {"D": A["altura_dianteira"], "T": A["altura_traseira"]}, "rolamento_graus": A["rolamento_graus"], "rolo_ini": 0.72,
               "dobra_graus": {"D": A["dobra_balanco_dianteira_graus"], "T": A["dobra_balanco_traseira_graus"]}},
     "Trote": CJ["marchas"]["Trote"], "Corrida": CJ["marchas"]["Corrida"]}
ARM = M.ARM; P = M.P; sc = bpy.context.scene
# sola de cada pata (LOW, repouso)
ARM.animation_data.action = None
for pb in P: pb.matrix_basis.identity()
bpy.context.view_layer.update()
C_ = bpy.data.objects["LOW_Corpo"]; me = C_.data; gn = {g.index: g.name for g in C_.vertex_groups}
SOLA = {}
for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"]):
    ids = [v.index for v in me.vertices if v.co.z < 0.5 and math.hypot(v.co.x - xy[0], v.co.y - xy[1]) < 0.8]; zs = min(me.vertices[i].co.z for i in ids)
    dedo = M.PATAS[k][3]
    pad = [me.vertices[i].co for i in ids if me.vertices[i].co.z < zs + 0.03 and max(((gn[g.group], g.weight) for g in me.vertices[i].groups), key=lambda t: t[1])[0] == dedo]
    pc = sum(pad, V()) / len(pad); SOLA[k] = {"z_sola": zs, "almofada": V((pc.x, pc.y, zs)), "n_vertices_almofada": len(pad)}
PIVO = os.environ.get("PIVO", "grade")
def alvo_v24(k, dy, dz, rolo, dobra):
    """PIVO=mcp (escolhido): rolamento DIGITIGRADO - os dedos ficam PLANTADOS (osso dos dedos parado, na orientacao do toque)
    e o metacarpo/metatarso gira na articulacao MCP (o calcanhar sobe); PIVO=sola: giro em torno de C projetado na sola e
    dedos apontados para a almofada (testado: afundava a almofada ate 0,07); PIVO=mcp_chao: giro em torno do chao sob a MCP."""
    mcp = M.MCP0[k] + V((0, dy, dz)); tv = M.TIP0[k] - M.MCP0[k]; C = mcp + 0.7 * tv
    if PIVO == "mcp": return mcp, rolo + dobra, 0.45 * dobra
    if PIVO == "grade":                                                  # pivo a F_PIVO do osso dos dedos, descido L_PIVO da linha do osso ate a sola
        fp = float(os.environ.get("F_PIVO", 0.8)); lp = float(os.environ.get("L_PIVO", 0.25)); Cf = mcp + fp * tv
        if k[0] == "D": lp = float(os.environ.get("L_PIVO_D", 0.20))     # dianteiras: 0,20 (0,25 afundava o LOD2 DD 0,033)
        Cg = Cf - V((0, 0, lp * (Cf.z - (SOLA[k]["z_sola"] + dz))))
        m_ef = Cg + Matrix.Rotation(rolo, 3, M.X) @ (mcp - Cg)
        if os.environ.get("DEDOS", "almofada") == "almofada":                # dedos apontados para a ALMOFADA plantada
            pv0 = SOLA[k]["almofada"] - M.MCP0[k]; nd = (mcp + pv0) - m_ef
            return m_ef, rolo + dobra, math.atan2(nd.z, nd.y) - math.atan2(pv0.z, pv0.y) + 0.45 * dobra
        nd = (mcp + tv) - m_ef                                            # dedos para a ponta (como na v23)
        return m_ef, rolo + dobra, math.atan2(nd.z, nd.y) - math.atan2(tv.z, tv.y) + 0.45 * dobra
    Cg = V((C.x, C.y, SOLA[k]["z_sola"] + dz)) if PIVO == "sola" else V((mcp.x, mcp.y, SOLA[k]["z_sola"] + dz))
    m_ef = Cg + Matrix.Rotation(rolo, 3, M.X) @ (mcp - Cg)
    pv0 = SOLA[k]["almofada"] - M.MCP0[k]; alvo = mcp + pv0              # almofada dos dedos fica onde tocou
    nd = alvo - m_ef; phi_dedo_rolo = math.atan2(nd.z, nd.y) - math.atan2(pv0.z, pv0.y)
    return m_ef, rolo + dobra, phi_dedo_rolo + 0.45 * dobra
REL = {"pivo": PIVO, "F_PIVO": os.environ.get("F_PIVO", 0.8), "L_PIVO": os.environ.get("L_PIVO", 0.25), "L_PIVO_D": os.environ.get("L_PIVO_D", 0.20), "dedos": os.environ.get("DEDOS", "almofada"), "sola": {k: {"z_sola": round(s["z_sola"], 4), "almofada": [round(x, 4) for x in s["almofada"]], "n_vertices_almofada": s["n_vertices_almofada"]} for k, s in SOLA.items()}, "acoes": {}}
PERNAS = [n for c in M.PATAS.values() for n in c]
for nome in ("Andar", "Trote", "Corrida"):
    ac = bpy.data.actions[nome]; n = int(ac.frame_range[1]); ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    BASE, REF = [], []
    for q in range(n + 1):
        sc.frame_set(q); BASE.append({pb.name: (pb.rotation_quaternion.copy(), pb.location.copy(), pb.scale.copy()) for pb in P})
        REF.append({nm: (P[nm].matrix.copy()) for nm in PERNAS})
    ARM.animation_data.action = None; Gm = G[nome]; dif = [0.0]
    def fn(t, Gm=Gm):
        qi = int(round(t * M.FPS)); b = BASE[qi]
        for pb in P: pb.rotation_mode = "QUATERNION"; pb.rotation_quaternion, pb.location, pb.scale = b[pb.name]
        bpy.context.view_layer.update(); err = 0.0; ext = {}
        for k in M.PATAS:
            dy, dz, rolo, dobra = M.pata_marcha(Gm, k, t)
            m_ef, phi, phd = (M.alvo_pata if VERIF else alvo_v24)(k, dy, dz, rolo, dobra); e, x = M.ik(k, m_ef, phi, phd); err = max(err, e); ext[k] = x
        for c in M.PATAS.values():
            for nm in c: P[nm].location = (0, 0, 0)
        bpy.context.view_layer.update()
        for nm in PERNAS:
            Mx = P[nm].matrix; Mr = REF[qi][nm]; dif[0] = max(dif[0], (Mx.translation - Mr.translation).length, max((Mx.col[j].to_3d() - Mr.col[j].to_3d()).length for j in range(3)))
        return err, ext
    if VERIF:
        for qi in range(n + 1): fn(qi / M.FPS)
        print("VERIF", nome, "dif_max_ossos_das_pernas", round(dif[0], 6), flush=True); continue
    # grava: mesma rotina do lote 1/2 (todos os ossos em todos os quadros, sem acao atribuida)
    VAL = []; ERR = 0.0
    for qi in range(n + 1):
        e, _ = fn(qi / M.FPS); ERR = max(ERR, e); VAL.append({pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P})
    novo = bpy.data.actions.new(nome + "_v24"); ARM.animation_data.action = novo
    for qi, vals in enumerate(VAL):
        for pb in P:
            pb.rotation_quaternion, pb.location = vals[pb.name]
            pb.keyframe_insert("rotation_quaternion", frame=qi, group=pb.name)
            if pb.name == "Quadril": pb.keyframe_insert("location", frame=qi, group=pb.name)
    novo.use_fake_user = True; novo.frame_range = (0, n); ARM.animation_data.action = None
    bpy.data.actions.remove(ac); novo.name = nome
    REL["acoes"][nome] = {"quadros": n, "erro_ik_max": round(ERR, 6), "diferenca_max_pernas_vs_v23": round(dif[0], 5)}
    print("V24", nome, json.dumps(REL["acoes"][nome]), flush=True)
if not VERIF:
    for pb in P: pb.matrix_basis.identity()
    ARM.animation_data.action = bpy.data.actions["Corrida"]
    CJ["v24_apoios"] = REL; json.dump(CJ, open(os.path.join(OUT, "clipes_v21.json"), "w"), indent=1)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("CLIPES_V24_OK", flush=True)
