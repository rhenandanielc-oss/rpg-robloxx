"""Ataque basico (v43, 17/11/2026) - pedido: "mordida e garra atacando ANDANDO, senao nao existe PvP de verdade".
Regra oficial: ataque basico = sequencia de mordidas e garras com animacoes variadas, fora dos slots.
Solucao: clipes PARCIAIS - so os ossos do golpe tem chave (pescoco, cabeca, boca, orelhas; na garra tambem UMA pata
dianteira). No Roblox tocam em prioridade Action por cima de Repouso/Andar/Trote/Corrida: os ossos sem chave seguem a
locomocao (o lobo continua andando/correndo e virando enquanto morde/arranha).
Acoes novas (30 q/s, uma vez, 15 q = 0,5 s; marcador Contato):
- Mordida1: recua a cabeca (q0-4), bote para a frente e para baixo com a boca aberta, fecha no Contato (q6 = 0,2 s), volta.
- Mordida2: variacao lateral - bote torcendo o pescoco/cabeca para o lado e "rasgando" (gira a cabeca) no fechamento.
- GarraE / GarraD: ergue a pata dianteira para a frente (q0-4), golpe para baixo e para tras com dedos abertos (Contato q7),
  volta; pescoco baixa e a cabeca acompanha o lado do golpe.
Sequencia sugerida no jogo: Mordida1 -> GarraE -> Mordida2 -> GarraD (reinicia se parar de atacar ~1 s).
Uso: blender -b anim_v42/CR_LoboArtico_Anim.blend -P gen_ataque_v43.py -- <dir_saida>
     (render de revisao: render_ataque_v43.py sobre o .blend gerado)"""
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V
import marcha_v21 as M
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
ARM = M.ARM; P = M.P; sc = bpy.context.scene
for pb in P: pb.rotation_mode = "QUATERNION"
def suave(x): x = max(0.0, min(1.0, x)); return x * x * x * (10 - 15 * x + 6 * x * x)
def janela(q, a, b): return suave((q - a) / max(1e-9, b - a))
def girar(osso, eixo, graus, piv=None):
    if not graus: return
    pb = P[osso]; h = (pb.head if piv is None else piv).copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(graus), 4, eixo) @ Matrix.Translation(-h) @ pb.matrix; bpy.context.view_layer.update()
def da_acao(nome, q):
    ac = bpy.data.actions[nome]; ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
    sc.frame_set(q); bpy.context.view_layer.update(); ARM.animation_data.action = None
def repouso_q0(): da_acao("Repouso", 0)

PALP = ["Palpebra_Sup_E", "Palpebra_Inf_E", "Palpebra_Sup_D", "Palpebra_Inf_D"]
CABECA = ["Pescoco1", "Pescoco2", "Cabeca", "Mandibula", "Orelha_E", "Orelha_D"] + PALP    # r3: olhos animados nos golpes
from mathutils import Quaternion
PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
def olhos(f_sup, f_inf):
    """r3 (usuario 17/11 "quero animacao nos olhos"): palpebras pelo mesmo metodo da piscada do Repouso (rotacao LOCAL em X
    com os angulos de fechamento medidos em rig_pivos.json). 0 = aberto, 1 = fechado."""
    for lado, ol in PIV["olhos"].items():
        P["Palpebra_Sup_" + lado].rotation_quaternion = Quaternion((1, 0, 0), math.radians(ol["fechar_sup_graus"] * f_sup))
        P["Palpebra_Inf_" + lado].rotation_quaternion = Quaternion((1, 0, 0), math.radians(ol["fechar_inf_graus"] * f_inf))
    bpy.context.view_layer.update()
PATA = {"E": list(M.PATAS["DE"]), "D": list(M.PATAS["DD"])}
N = 15; CONTATO_M = 6; CONTATO_G = 7

def env(q, pico, fim=N):
    """0 -> 1 no pico (golpe) -> 0 no fim; windup antes do pico"""
    return janela(q, 0, pico) * (1 - janela(q, pico + 2, fim))
def mordida(q, lado=0):
    repouso_q0()
    rec = janela(q, 0, 3) * (1 - janela(q, 3, CONTATO_M))          # recua (windup)
    bote = janela(q, 3, CONTATO_M) * (1 - janela(q, CONTATO_M + 2, N))   # bote e volta
    # r2 (usuario 17/11 "por que ele nao abre a boca ao morder"): r1 abria so +22 graus por 3 quadros (q3-q5), ja com a
    # cabeca baixa -> invisivel. Agora abre ja no recuo (rosto a mostra), bem aberta (+42), segura e FECHA DE ESTALO no
    # contato (q5 -> q6); depois solta um pouco (+12) e fecha.
    abre = janela(q, 0, 2.5) * (1 - janela(q, CONTATO_M - 0.8, CONTATO_M))
    abre2 = 0.28 * janela(q, CONTATO_M + 3, CONTATO_M + 5) * (1 - janela(q, 12, N))
    girar("Pescoco1", "X", -8 * rec + 18 * bote); girar("Pescoco2", "X", -6 * rec + 12 * bote)
    girar("Cabeca", "X", -6 * rec + 10 * bote)
    if lado:
        girar("Pescoco1", "Z", 16 * lado * (rec * 0.4 + bote)); girar("Pescoco2", "Z", 10 * lado * bote)
        girar("Cabeca", "Y", -22 * lado * janela(q, CONTATO_M, CONTATO_M + 3) * (1 - janela(q, 10, N)))   # rasga girando
    girar("Mandibula", "X", 40 * abre + 40 * abre2)        # r2: "+" ABRE (convencao do gen_bloco4_v41: boca > 0 fecha com "-"); r1 fechava para dentro do cranio
    for o in ("Orelha_E", "Orelha_D"): girar(o, "X", -30 * max(rec, bote, abre))
    # olhos: estreitam no preparo (mira), FECHAM por reflexo no estalo da mordida (q5-q7) e reabrem
    mira = janela(q, 0, 3) * (1 - janela(q, 11, N)); reflexo = janela(q, CONTATO_M - 1, CONTATO_M) * (1 - janela(q, CONTATO_M + 1, CONTATO_M + 3))
    olhos(max(0.42 * mira, 0.92 * reflexo), max(0.35 * mira, 0.85 * reflexo))
    return 0.0
def garra(q, lado):
    repouso_q0(); s = "E" if lado > 0 else "D"; sg = 1 if lado > 0 else -1
    sobe = janela(q, 0, 4) * (1 - janela(q, 4, CONTATO_G))           # ergue a pata
    golpe = janela(q, 4, CONTATO_G) * (1 - janela(q, CONTATO_G + 2, N))   # desce/raspa e volta
    cab = janela(q, 0, 4) * (1 - janela(q, 10, N))
    u, a, m, d = PATA[s]
    # r3 (usuario 17/11 "as patadas estao estranhas, nao precisa colocar tao para cima"): ergue ~metade (umero -62 -> -32)
    girar(u, "X", -32 * sobe + 14 * golpe); girar(u, "Z", -6 * sg * sobe)        # para a frente, pouco para dentro
    girar(a, "X", -16 * sobe + 4 * golpe)
    girar(m, "X", 26 * sobe - 8 * golpe); girar(d, "X", -20 * golpe + 10 * sobe)   # dedos abertos no golpe
    girar("Pescoco1", "X", 8 * cab); girar("Pescoco2", "X", 6 * cab); girar("Pescoco1", "Z", 8 * sg * cab)
    girar("Cabeca", "X", 4 * cab)
    girar("Mandibula", "X", 14 * janela(q, 2, 5) * (1 - janela(q, 9, N)))   # r2: rosnado com a boca entreaberta (sinal corrigido)
    for o in ("Orelha_E", "Orelha_D"): girar(o, "X", -26 * cab)
    # olhos: estreitam mirando, piscam forte no golpe da pata
    mira = janela(q, 0, 3) * (1 - janela(q, 11, N)); reflexo = janela(q, CONTATO_G - 1, CONTATO_G) * (1 - janela(q, CONTATO_G + 1, CONTATO_G + 3))
    olhos(max(0.40 * mira, 0.75 * reflexo), max(0.32 * mira, 0.65 * reflexo))
    return 0.0
def piscar(q):
    """Piscar (8 q = 0,27 s): fecha em 3 q, segura 1, abre em 4 (igual a piscada do Repouso, 0,24 s)"""
    repouso_q0(); f = janela(q, 0, 3) * (1 - janela(q, 4, 8)); olhos(f, 0.9 * f); return 0.0
def gravar_parcial(nome, n, fn, ossos):
    for a_ in [a_ for a_ in bpy.data.actions if a_.name == nome]: bpy.data.actions.remove(a_)
    acn = bpy.data.actions.new(nome); VAL = []
    for q in range(n + 1):
        fn(q); VAL.append({o: P[o].rotation_quaternion.copy() for o in ossos})
    ARM.animation_data.action = acn; prev = {}
    for q, vals in enumerate(VAL):
        for o in ossos:
            rq = vals[o]
            if o in prev and rq.dot(prev[o]) < 0: rq = -rq
            prev[o] = rq; P[o].rotation_quaternion = rq; P[o].keyframe_insert("rotation_quaternion", frame=q, group=o)
    acn.use_fake_user = True; acn.frame_range = (0, n); ARM.animation_data.action = None
    for pb in P: pb.matrix_basis.identity()
REL = {"acoes": {}, "nota": "clipes PARCIAIS: so os ossos listados tem chave; tocar em prioridade Action sobre a locomocao"}
for nome, fn, ossos, cont in (
        ("Mordida1", lambda q: mordida(q, 0), CABECA, CONTATO_M),
        ("Mordida2", lambda q: mordida(q, 1), CABECA, CONTATO_M),
        ("GarraE", lambda q: garra(q, 1), CABECA + PATA["E"], CONTATO_G),
        ("GarraD", lambda q: garra(q, -1), CABECA + PATA["D"], CONTATO_G)):
    gravar_parcial(nome, N, fn, ossos)
    REL["acoes"][nome] = {"quadros": N, "parcial": True, "ossos": ossos, "marcadores_s": {"Contato": round(cont / 30, 3)}}
gravar_parcial("Piscar", 8, piscar, PALP)                          # r3: so as palpebras; tocado de tempos em tempos no jogo
REL["acoes"]["Piscar"] = {"quadros": 8, "parcial": True, "ossos": PALP, "marcadores_s": {}}
print("V43", {k: (v["quadros"], len(v["ossos"])) for k, v in REL["acoes"].items()}, flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "ataque_v43.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("GEN_ATAQUE_V43_OK", flush=True)
