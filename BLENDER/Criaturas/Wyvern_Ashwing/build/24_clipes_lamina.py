# Lote 8 de clipes da Wyvern: LAMINA DE VENTO (2a ativa do kit aprovado em 13/11/2026), sobre Wyvern_E7_clipes_L7.blend
# (preservado; boca fechada). So ACRESCENTA 2 actions. Regra oficial: "recolhe as asas a frente do peito e abre ambas de
# uma vez; cada asa emite um corte diagonal que cruza o outro logo a frente (X largo)". Angulos/tempos = PROPOSTA visual.
#   LaminaVento     1,6 s  (chao) agacha e cruza as asas dobradas a frente do peito (pose do AsasEscudo, aprovada), abre as
#                          duas DE UMA VEZ (0,12 s) ate a envergadura do voo, tronco projeta para a frente e o pescoco
#                          estica; segura aberta e volta ao idle. EMISSAO (instante do X) = T_EMISSAO.
#   LaminaVento_Ar  1,3 s  (voo) mesmo gesto a partir do ciclo de voo (fly_loop): asas cruzadas a frente do peito, abertura
#                          de uma vez, planeio curto e volta ao ciclo de voo na mesma fase.
# Reaproveita do lote 6 (build/20_clipes_lote6.py, linhas de funcoes comuns): agachar/plantar, ASA_ABERTA, IK do focinho,
# fechar_boca e a pose de asas do AsasEscudo (so os ossos das asas, no pico).
# Uso: blender -b Wyvern_E7_clipes_L7.blend -P 24_clipes_lamina.py -- <08_base.py> <saida.blend> <manifesto.json> [lab:<pasta> <json>]
import bpy, sys, math, json, os
argv = sys.argv[sys.argv.index("--") + 1:]
exec(open(argv[0], encoding="utf-8").read())
OUT, MANI = argv[1], argv[2]
# funcoes comuns do lote 6 (ate o fim do AsasEscudo): mesmas regras de pernas/IK/boca dos clipes aprovados
_src = open(os.path.join(os.path.dirname(argv[0]), "20_clipes_lote6.py"), encoding="utf-8").read().split("\n")
_ini = next(i for i, l in enumerate(_src) if l.startswith("I0, FI0 = "))
_fim = next(i for i, l in enumerate(_src) if l.startswith("# ---------------------------------------------------------------- SecarAsas"))
exec("\n".join(_src[_ini:_fim]))
T_EMISSAO = 0.49                                                     # s: asas no meio da abertura = sai o X (cliente/servidor)

def ease_out(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
# pose das asas cruzadas a frente do peito = AsasEscudo no pico, sem tremor (so os ossos das asas)
def _asas_cruzadas(z, y, up):
    P, _ = I(0.0)
    for s in "LR":
        k = sx_(s)
        girar(P, "shoulder_" + s, Z, R(z) * k)
        girar(P, "shoulder_" + s, Y, R(y) * k)
        girar(P, "upperarm_" + s, FRENTE, R(up) * k)
    return {b: P[b] for b in ASAS}
ASAS_X = _asas_cruzadas(PAR["esc_z"], PAR["esc_y"], PAR["esc_up"])
# no VOO o pescoco vai esticado a frente: as asas do escudo (erguidas para cobrir a cabeca) embrulhavam a cabeca (lab1/2);
# no ar as asas cruzam MAIS BAIXAS, a frente do peito e por baixo do pescoco
def asas_x_ar(): return _asas_cruzadas(LPAR["ar_z"], LPAR["ar_y"], LPAR["ar_up"])
LPAR = dict(agacha=0.8, avanco=1.2, incl_rec=4.0, incl_emit=-7.0, cab_rec=(0, 2.4, 1.4), cab_emit=(0, -1.8, 0.7), cab_rec_ar=(0, 1.0, 0.8), cab_emit_ar=(0, -0.6, 0.3),
            ar_z=-60, ar_y=25, ar_up=10,
            t_rec=(0.05, 0.36), t_abre=(0.41, 0.57), t_fecha=(0.95, 1.55), cauda=6.0)

def envs(t, dur):
    a0, a1 = LPAR["t_rec"]; b0, b1 = LPAR["t_abre"]; c0, c1 = LPAR["t_fecha"]
    k = dur / 1.6
    e_rec = suave((t - a0 * k) / ((a1 - a0) * k))                    # asas indo para o peito
    # abertura DE UMA VEZ em 0,16 s: suave (ease_out cubico dava 63% do caminho na 1a amostra: dedo da asa saltava 82-153 graus)
    e_ab = suave((t - b0 * k) / ((b1 - b0) * k))
    e_vol = suave((t - c0 * k) / ((c1 - c0) * k))                    # volta ao clipe de base
    e_emit = env(t, b0 * k, b1 * k, c0 * k, c1 * k)                  # tronco/pescoco projetados
    e_agacha = env(t, 0.0, a1 * k, b1 * k, (b1 + 0.35) * k)
    return e_rec, e_ab, e_vol, e_emit, e_agacha

def gesto(P, t, dur, chao):
    e_rec, e_ab, e_vol, e_emit, e_ag = envs(t, dur)
    inclinar(P, LPAR["incl_rec"] * e_ag * (1 - e_ab) + LPAR["incl_emit"] * e_emit)
    if e_emit > 1e-4: mover(P, "root", FRENTE * LPAR["avanco"] * e_emit)
    if chao:                                                           # corpo desce/avanca; os pes ficam plantados no lugar
        mover(P, "root", V((0, 0, -LPAR["agacha"] * e_ag)))
        if e_ag > 1e-4 or e_emit > 1e-4:
            for s in "LR": LOG["erro_perna"] = round(max(LOG.get("erro_perna", 0.0), plantar(P, s, LEG0[s], FK0["foot_" + s].to_3x3())), 3)
    # asas: base -> cruzadas -> abertas (de uma vez) -> base
    # caminho UNICO: base -> cruzadas (e_rec) -> abertas (e_ab) -> base (e_vol); misturas em cadeia desviavam o caminho
    base = {b: P[b] for b in ASAS}
    W = misturar(P, {**P, **(ASAS_X if chao else asas_x_ar())}, e_rec, ASAS)
    W = misturar(W, ASA_ABERTA, e_ab, ASAS)
    W = misturar(W, {**W, **base}, e_vol, ASAS)
    P.update({b: W[b] for b in ASAS})
    # cabeca: recolhe no preparo, estica para a frente na emissao
    f0 = foco(fk(P, [FOC]))
    sfx = "" if chao else "_ar"
    off = V(LPAR["cab_rec" + sfx]) * e_rec * (1 - e_ab) + V(LPAR["cab_emit" + sfx]) * e_emit
    if off.length > 1e-3:
        Pik = ik_focinho("lam_chao" if chao else "lam_ar", P, [(foco, f0 + off, 1.0)])
        P = misturar(P, Pik, 1.0, ["spine_03"] + PESCOCO + ["head"])
    else:
        ESTADO.pop("lam_chao" if chao else "lam_ar", None)
    for b in CAUDA[:5]: girar(P, b, X, R(LPAR["cauda"]) * e_emit * 0.2)    # cauda sobe um pouco: contrapeso do avanco
    fechar_boca(P, 1.0)
    return P

T_CHAO, T_AR = 1.6, 1.3
def c_lamina(t):
    P, fold = I(t)
    return gesto(P, t, T_CHAO, True), fold
def c_lamina_ar(t):
    P, fold = amostra("fly_loop", t % T_FLY)
    return gesto(P, t, T_AR, False), fold
CLIPES = {"LaminaVento": (c_lamina, T_CHAO), "LaminaVento_Ar": (c_lamina_ar, T_AR)}

# ---------------------------------------------------------------- medidas para o jogo (emissao) e QA
def pontas_asas(P):
    M = fk(P); return {s: ponta(M, "strut_b_02_" + s) for s in "LR"}, cabeca(M, "pelvis"), foco(M)
def qa(nome, fn, dur):
    n = int(round(dur * HZ)) + 1; ts = [dur * k / (n - 1) for k in range(n)]
    ant = None; salto = (0.0, ""); zmin = 9e9
    for t in ts:
        P, fold = fn(t)
        if ant:
            for b in OSSOS:
                d = math.degrees(ant[b][1].rotation_difference(P[b][1]).angle)
                if d > salto[0]: salto = (round(d, 1), "%s t=%.2f" % (b, t))
        if nome == "LaminaVento" and int(round(t * HZ)) % 3 == 0:
            zr = zmin_reg(P, fold); zmin = min(zmin, zr.get("asaL", 9e9), zr.get("asaR", 9e9))
        ant = P
    P, _ = fn(T_EMISSAO * dur / 1.6)
    pa, pel, fo = pontas_asas(P)
    return {"maior_salto_por_amostra_graus": salto,
            "emissao_s": round(T_EMISSAO * dur / 1.6, 3),
            "emissao_pontas_asas_rel_pelvis": {s: [round(v, 2) for v in (pa[s] - pel)] for s in "LR"},
            "emissao_focinho_rel_pelvis": [round(v, 2) for v in (fo - pel)],
            "z_min_asas_chao": (round(zmin, 3) if zmin < 9e8 else None)}

if len(argv) > 3 and argv[3].startswith("lab:"):
    pasta = argv[3][4:]; os.makedirs(pasta, exist_ok=True)
    pedidos = json.loads(argv[4])
    scn = bpy.context.scene; scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 640; scn.render.resolution_y = 430
    scn.world = bpy.data.worlds.new("W"); scn.world.color = (0.55, 0.6, 0.68)
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30))); bpy.context.object.data.energy = 4
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-60), 0, math.radians(200))); bpy.context.object.data.energy = 1.5
    bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0))
    cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); bpy.context.scene.collection.objects.link(cam); scn.camera = cam
    cd.type = "ORTHO"; cd.clip_end = 1000; cd.ortho_scale = 40
    for ob in (arm, key):
        if ob.animation_data: ob.animation_data.action = None
    for i, (nome, t, par) in enumerate(pedidos):
        LPAR.update(par); ESTADO.clear(); LOG.clear()
        P, fold = CLIPES[nome][0](t); aplicar(P, fold)
        for v, d in (("lado", V((1, 0, 0.05))), ("tres4", V((0.8, -0.7, 0.45))), ("frente", V((0, -1, 0.15)))):
            d = d.normalized(); c = V((0, -3, 7))
            cam.location = c + d * 300; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
            scn.render.filepath = os.path.join(pasta, "%02d_%s.png" % (i, v)); bpy.ops.render.render(write_still=True)
        print("LAB", i, nome, t, json.dumps(LOG))
    sys.exit(0)

mani = {"_fonte": "Wyvern_E7_clipes_L7.blend (idle_loop, fly_loop; pose de asas do AsasEscudo)", "_hz": HZ, "_parametros": LPAR}
for nome, (fn, dur) in CLIPES.items():
    ESTADO.clear(); LOG.clear()
    mani[nome] = gravar_clipe(nome, fn, dur, False)
    ESTADO.clear(); mani[nome]["qa"] = qa(nome, fn, dur); mani[nome]["log_ik"] = dict(LOG)
    print("CLIPE", nome, json.dumps(mani[nome]), flush=True)
zerar()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(mani, open(MANI, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OK")
