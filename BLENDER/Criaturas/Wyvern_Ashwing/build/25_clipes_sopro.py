# Lote 9 de clipes da Wyvern: SOPRO PREDATORIO (3a ativa do kit aprovado em 13/11/2026), sobre Wyvern_E7_clipes_L8.blend
# (preservado). So ACRESCENTA 3 actions. Regra oficial: "inspira, estende o pescoco e sopra pela boca um jato continuo e
# concentrado de Ar a curta distancia ... a cabeca pode acompanhar a presa". Angulos/tempos = PROPOSTA visual.
#   Sopro_Inicio  1,05 s  inspira (peito sobe, pescoco recua e a cabeca sobe, boca fechada) e estende o pescoco para a
#                         frente e um pouco para baixo, abrindo a boca; o JATO comeca no fim (o Nucleo emite em 1,05 s).
#   Sopro_Loop    1,2 s   (laco) pescoco estendido, boca aberta, tremor curto de esforco e peito esvaziando devagar.
#   Sopro_Fim     0,8 s   fecha a boca e o pescoco volta ao repouso.
# Emendas: o fim do Inicio, o comeco/fim do Loop e o comeco do Fim usam a MESMA pose de sopro (pose_sopro(0)).
# Boca pela regra do L7: mandibula = +18 graus (fechada) - abertura. As versoes "_Sup" (so pescoco/cabeca/mandibula, para
# soprar andando/voando) sao copias no Studio com peso 0 nos outros ossos (padrao do Sombrio).
# Reaproveita do lote 6 (build/20_clipes_lote6.py): I(t), agachar/plantar, IK do focinho, fechar_boca.
# Uso: blender -b Wyvern_E7_clipes_L8.blend -P 25_clipes_sopro.py -- <08_base.py> <saida.blend> <manifesto.json> [lab:<pasta> <json>]
import bpy, sys, math, json, os
argv = sys.argv[sys.argv.index("--") + 1:]
exec(open(argv[0], encoding="utf-8").read())
OUT, MANI = argv[1], argv[2]
_src = open(os.path.join(os.path.dirname(argv[0]), "20_clipes_lote6.py"), encoding="utf-8").read().split("\n")
_ini = next(i for i, l in enumerate(_src) if l.startswith("I0, FI0 = "))
_fim = next(i for i, l in enumerate(_src) if l.startswith("# ---------------------------------------------------------------- SecarAsas"))
exec("\n".join(_src[_ini:_fim]))

SPAR = dict(boca=20.0,                     # graus de abertura a partir da boca fechada (bite 24, roar 26)
            inspira=(0, 2.4, 2.2),          # recuo/subida do focinho na inspiracao (studs; FRENTE = -Y)
            sopra=(0, -2.6, -1.0),          # pescoco estendido para a frente e um pouco para baixo
            peito=7.0,                      # graus: tronco ergue na inspiracao (peito "enche")
            agacha=0.35, tremor=0.18, cauda=4.0,
            t_insp=(0.05, 0.50), t_ext=(0.52, 0.95), t_boca=(0.62, 0.98))
T_INI, T_LOOP, T_FIM = 1.05, 1.2, 0.8

def jaw_aberta(P, graus):
    l, _, e = P["jaw"]; P["jaw"] = (l, Q(V((1, 0, 0)), R(18.0 - graus)), e)

NUCA = ["spine_03"] + PESCOCO + ["head"]
_POSES = {}
def poses_pescoco():
    """resolve o IK do focinho SO 2 vezes (inspiracao e sopro, sobre a base do instante T_INI) e guarda as rotacoes
    locais do pescoco; cada quadro so interpola entre elas (r2: IK por quadro perto do limite de alcance trocava de
    solucao e a cabeca saltava 12-14 graus por amostra)"""
    if _POSES: return _POSES
    for nome, k_insp, k_ext, alvo in (("insp", 1, 0, "inspira"), ("ext", 1, 1, "sopra")):
        P, _ = I(T_INI)
        agachar(P, SPAR["agacha"] * k_ext); inclinar(P, SPAR["peito"] * k_insp - 1.5 * k_ext)
        f0 = foco(fk(P, [FOC])); ESTADO.pop("sopro", None)
        Pik = ik_focinho("sopro", P, [(foco, f0 + V(SPAR[alvo]), 1.0)])
        _POSES[nome] = {b: Pik[b] for b in NUCA}
    return _POSES

def pose_sopro(P, t, k_ext, k_insp, k_boca, tremor_t=None):
    """aplica sobre P (base idle no instante t): inspiracao (k_insp), extensao (k_ext), boca (k_boca)"""
    agachar(P, SPAR["agacha"] * k_ext)
    inclinar(P, SPAR["peito"] * k_insp - 1.5 * k_ext)                      # ergue o peito ao inspirar; leve a frente ao soprar
    N_ = poses_pescoco()
    P = misturar(P, {**P, **N_["insp"]}, k_insp, NUCA)
    P = misturar(P, {**P, **N_["ext"]}, k_ext, NUCA)
    if tremor_t is not None:                                               # esforco: tremor curto da cabeca (rotacao direta)
        w = 2 * math.pi / T_LOOP
        girar(P, "head", X, R(1.6) * math.sin(tremor_t * w * 8) * SPAR["tremor"] / 0.18)
        girar(P, "head", Z, R(1.0) * math.sin(tremor_t * w * 13) * (1 - math.cos(tremor_t * w)) * 0.5 * SPAR["tremor"] / 0.18)
    for b in CAUDA[:5]: girar(P, b, X, R(SPAR["cauda"]) * k_ext * 0.2)     # contrapeso do pescoco estendido
    jaw_aberta(P, SPAR["boca"] * k_boca + (math.sin(tremor_t * 2 * math.pi / T_LOOP * 6) * 1.2 * k_boca if tremor_t is not None else 0))
    return P

def c_inicio(t):
    P, fold = I(t)
    a0, a1 = SPAR["t_insp"]; b0, b1 = SPAR["t_ext"]; c0, c1 = SPAR["t_boca"]
    k_insp = suave((t - a0) / (a1 - a0)); k_ext = suave((t - b0) / (b1 - b0)); k_boca = suave((t - c0) / (c1 - c0))
    return pose_sopro(P, t, k_ext, k_insp, k_boca, None), fold

def c_loop(t):
    P, fold = I(T_INI)                                                       # base parada no mesmo instante do fim do Inicio
    u = t / T_LOOP
    P = pose_sopro(P, t, 1.0, 1.0, 1.0, t % T_LOOP)
    for b in ("spine_02", "spine_03"): girar(P, b, X, R(-1.0) * math.sin(2 * math.pi * u))   # peito esvazia/enche (laco)
    return P, fold

def c_fim(t):
    k = 1 - suave(t / T_FIM)
    P, fold = I(T_INI + t)
    P = pose_sopro(P, t, k, k, 1 - suave(t / (T_FIM * 0.55)), None)
    if k <= 1e-4: fechar_boca(P, 1.0)
    return P, fold

CLIPES = {"Sopro_Inicio": (c_inicio, T_INI, False), "Sopro_Loop": (c_loop, T_LOOP, True), "Sopro_Fim": (c_fim, T_FIM, False)}

def qa(nome, fn, dur):
    n = int(round(dur * HZ)) + 1; ts = [dur * k / (n - 1) for k in range(n)]
    ant = None; salto = (0.0, ""); zmin = 9e9
    for t in ts:
        P, fold = fn(t)
        if ant:
            for b in OSSOS:
                d = math.degrees(ant[b][1].rotation_difference(P[b][1]).angle)
                if d > salto[0]: salto = (round(d, 1), "%s t=%.2f" % (b, t))
        if int(round(t * HZ)) % 4 == 0:
            zr = zmin_reg(P, fold); zmin = min(zmin, zr.get("cabeca", 9e9))
        ant = P
    return {"maior_salto_por_amostra_graus": salto, "z_min_cabeca": round(zmin, 3)}

def emenda(a, b):
    """maior diferenca (graus) entre a pose final de a e a inicial de b"""
    Pa, _ = CLIPES[a][0](CLIPES[a][1]); Pb, _ = CLIPES[b][0](0.0)
    d = max((math.degrees(Pa[o][1].rotation_difference(Pb[o][1]).angle), o) for o in OSSOS)
    return [round(d[0], 2), d[1]]

if len(argv) > 3 and argv[3].startswith("lab:"):
    pasta = argv[3][4:]; os.makedirs(pasta, exist_ok=True)
    pedidos = json.loads(argv[4])
    scn = bpy.context.scene; scn.render.engine = "BLENDER_EEVEE"; scn.render.resolution_x = 640; scn.render.resolution_y = 430
    scn.world = bpy.data.worlds.new("W"); scn.world.color = (0.55, 0.6, 0.68)
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), 0, math.radians(30))); bpy.context.object.data.energy = 4
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(-60), 0, math.radians(200))); bpy.context.object.data.energy = 1.5
    bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0))
    cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); bpy.context.scene.collection.objects.link(cam); scn.camera = cam
    cd.type = "ORTHO"; cd.clip_end = 1000; cd.ortho_scale = 30
    for ob in (arm, key):
        if ob.animation_data: ob.animation_data.action = None
    for i, (nome, t, par) in enumerate(pedidos):
        SPAR.update({k: tuple(v) if isinstance(v, list) else v for k, v in par.items()}); ESTADO.clear(); LOG.clear(); _POSES.clear()
        P, fold = CLIPES[nome][0](t); aplicar(P, fold)
        for v, d in (("lado", V((1, 0, 0.05))), ("tres4", V((0.8, -0.7, 0.35))), ("frente", V((0, -1, 0.1)))):
            d = d.normalized(); c = V((0, -6, 9))
            cam.location = c + d * 300; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
            scn.render.filepath = os.path.join(pasta, "%02d_%s.png" % (i, v)); bpy.ops.render.render(write_still=True)
        print("LAB", i, nome, t, json.dumps(LOG))
    sys.exit(0)

mani = {"_fonte": "Wyvern_E7_clipes_L8.blend (idle_loop)", "_hz": HZ, "_parametros": SPAR}
for nome, (fn, dur, loop) in CLIPES.items():
    ESTADO.clear(); LOG.clear()
    mani[nome] = gravar_clipe(nome, fn, dur, loop)
    ESTADO.clear(); mani[nome]["qa"] = qa(nome, fn, dur); mani[nome]["log_ik"] = dict(LOG)
    print("CLIPE", nome, json.dumps(mani[nome]), flush=True)
ESTADO.clear()
mani["_emendas_graus"] = {"Inicio->Loop": emenda("Sopro_Inicio", "Sopro_Loop"), "Loop->Loop": emenda("Sopro_Loop", "Sopro_Loop"),
                          "Loop->Fim": emenda("Sopro_Loop", "Sopro_Fim")}
print("EMENDAS", json.dumps(mani["_emendas_graus"]))
zerar()
bpy.ops.wm.save_as_mainfile(filepath=OUT)
json.dump(mani, open(MANI, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("OK")
