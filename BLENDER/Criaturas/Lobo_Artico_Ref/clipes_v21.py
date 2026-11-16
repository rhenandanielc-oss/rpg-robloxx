"""Lote 2, etapa L2a: 'Trote' e 'Corrida' (galope natural de lobo), acrescentados como acoes na malha APROVADA do lote 1
(anim_v20/ so e lido; saida em anim_v21/ com Repouso e Andar intactos). Mesmo contrato: NO LUGAR (Raiz fixa, frente -Y; o jogo
move o modelo), IK analitico -> FK em todos os quadros (marcha_v21.py, mesmas funcoes do lote 1).
Parametros TECNICOS (ajustaveis; nao sao regras de jogo). A velocidade de cada marcha e a DEMONSTRADA pela passada e pela
cadencia: v = D / T, com a varredura de cada pata no apoio S = D * apoio limitada pelo ALCANCE medido do rig (alcance_v21.py).
- Trote: pares diagonais (DE+TD, DD+TE), apoio 0,40 (pequena suspensao entre os pares), 2 balancos de corpo por ciclo.
  Rolamento do fim do apoio 15 (Trote) e 20 graus (Corrida): com 30-35 o contato das almofadas deslizava 0,032-0,036 (medido).
- Corrida: galope ROTATORIO de lobo (TE -> TD -> DD -> DE, a sequencia das dianteiras comeca do lado da ultima traseira),
  apoio por pata 0,28, suspensao RECOLHIDA depois das dianteiras; coluna estende no impulso das traseiras / alcance das
  dianteiras e flexiona na suspensao; corpo mais baixo, cabeca baixa e estabilizada, cauda em contrapeso, orelhas para tras.
Uso: blender -b anim_v20/CR_LoboArtico_Anim.blend -P clipes_v21.py -- anim_v21"""
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector as V
import marcha_v21 as M
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
X, Y, Z = M.X, M.Y, M.Z; onda = M.onda
TROTE = {"T": 0.6, "D": 4.0, "apoio": 0.40, "fases": {"DE": 0.0, "TD": 0.0, "DD": 0.5, "TE": 0.5},
         "centro": {"DE": -0.35, "DD": -0.35, "TE": 0.0, "TD": 0.0}, "altura": {"D": 0.55, "T": 0.45},
         "rolamento_graus": 15.0, "rolo_ini": 0.7, "dobra_graus": {"D": 105.0, "T": 75.0}, "quadril_z": -0.12}
CORRIDA = {"T": 0.45, "D": 9.5, "apoio": 0.28, "fases": {"TE": 0.0, "TD": 0.08, "DD": 0.30, "DE": 0.40},
           "centro": {"DE": -0.45, "DD": -0.45, "TE": -0.25, "TD": -0.25}, "altura": {"D": 0.8, "T": 0.75},
           "rolamento_graus": 20.0, "rolo_ini": 0.6, "dobra_graus": {"D": 125.0, "T": 85.0}, "quadril_z": -0.32,
           "suspensao_centro": 0.84, "coluna_graus": 5.0, "compensa_coluna": 0.8, "arfagem_graus": 3.5, "subida": 0.16}
for nm_, G in (("TROTE", TROTE), ("CORRIDA", CORRIDA)):                    # AJUSTE_<MARCHA>='{json}': testes de parametro
    if os.environ.get("AJUSTE_" + nm_): G.update(json.loads(os.environ["AJUSTE_" + nm_]))
for G in (TROTE, CORRIDA): G["v_studs_s"] = round(G["D"] / G["T"], 3); G["varredura_apoio"] = round(G["D"] * G["apoio"], 3); G["cadencia_hz"] = round(1 / G["T"], 3)
def escapulas(add, G, t, A):
    for lado in ("E", "D"):
        u = ((t / G["T"]) - G["fases"]["D" + lado]) % 1.0; add("Escapula_" + lado, X, -A * math.cos(2 * math.pi * (u - G["apoio"] / 2)))
def corpo_trote(t):
    G = TROTE; T = G["T"]; R = {}
    def add(n, e, g): R.setdefault(n, []).append((e, g))
    q = V((0.02 * onda(t, T, 0.0), 0.0, G["quadril_z"] - 0.05 * math.cos(4 * math.pi * (t / T - G["apoio"] / 2))))
    add("Quadril", Y, 2.0 * onda(t, T, 0.25)); add("Quadril", Z, 1.5 * onda(t, T, 0.0))
    for n, g in (("Coluna1", -0.8), ("Coluna2", -1.0), ("Coluna3", -1.2)): add(n, Z, g * onda(t, T, 0.05))
    add("Coluna3", X, 1.0 * math.cos(4 * math.pi * t / T)); add("Pescoco1", X, 4.0 - 1.0 * math.cos(4 * math.pi * t / T + 0.4))
    add("Cabeca", X, -3.0 - 1.4 * math.cos(4 * math.pi * t / T + 0.8))      # cabeca um pouco baixa e estabilizada
    add("Pescoco1", Z, 1.0 * onda(t, T, 0.3)); add("Cabeca", Z, 0.8 * onda(t, T, 0.35))
    for i, n in enumerate(("Cauda1", "Cauda2", "Cauda3", "Cauda4")):
        add(n, X, -4.0 if i == 0 else 0.0); add(n, Z, (2.0 + 1.5 * i) * onda(t, T, 0.15 + 0.08 * i)); add(n, X, 1.5 * math.cos(4 * math.pi * t / T + 0.6 * i))
    for n in ("Orelha_E", "Orelha_D"): add(n, X, -6.0 + 2.0 * math.cos(4 * math.pi * t / T + 1.0))
    escapulas(add, G, t, 8.0)
    return R, q
def corpo_corrida(t):
    G = CORRIDA; T = G["T"]; u = (t / T) % 1.0; R = {}
    def add(n, e, g): R.setdefault(n, []).append((e, g))
    flex = math.cos(2 * math.pi * (u - G["suspensao_centro"]))              # +1 recolhido (suspensao), -1 estendido
    q = V((0.03 * onda(t, T, 0.1), 0.0, G["quadril_z"] + G["subida"] * math.cos(2 * math.pi * (u - G["suspensao_centro"]))))
    soma = G["coluna_graus"] * 2.7                                     # giro total da coluna (Coluna1+2+3)
    add("Quadril", X, G["arfagem_graus"] * 0.5 * (1 + math.cos(2 * math.pi * (u - 0.48))) - G["compensa_coluna"] * soma * min(flex, 0.0))   # o dorso
    # estende sem levantar os ombros (no lugar, a extensao pura erguia a frente e as dianteiras nao alcancavam o chao); so na extensao
    add("Quadril", Y, 1.5 * onda(t, T, 0.2))
    for n, f in (("Coluna1", 1.0), ("Coluna2", 1.0), ("Coluna3", 0.7)): add(n, X, G["coluna_graus"] * f * flex)
    pesc = -(G["arfagem_graus"] * 0.5 * (1 + math.cos(2 * math.pi * (u - 0.48))) + soma * flex - G["compensa_coluna"] * soma * min(flex, 0.0))   # cabeca estavel
    add("Pescoco1", X, 9.0 + 0.6 * pesc); add("Pescoco2", X, 0.25 * pesc); add("Cabeca", X, -7.0 + 0.15 * pesc)
    add("Pescoco1", Z, 0.8 * onda(t, T, 0.3))
    for i, n in enumerate(("Cauda1", "Cauda2", "Cauda3", "Cauda4")):          # cauda estendida para tras, contrapeso
        add(n, X, (-14.0 if i == 0 else -3.0) - (3.0 + 1.5 * i) * flex); add(n, Z, (1.5 + 1.0 * i) * onda(t, T, 0.2 + 0.1 * i))
    for n in ("Orelha_E", "Orelha_D"): add(n, X, -14.0 - 2.0 * flex)
    escapulas(add, G, t, 14.0)
    return R, q
def montar(G, fn_corpo, t):
    R, q = fn_corpo(t); M.aplicar_corpo(R, q); pes = {k: M.pata_marcha(G, k, t) for k in M.PATAS}; r = M.aplicar_patas(pes)
    if os.environ.get("DBG_V21") and r[0] > 0.01: print("DBG", round(t * M.FPS), {k: (round(e, 3), [round(x, 2) for x in pes[k][:2]]) for k, e in M.ERR_PATA.items() if e > 0.01}, flush=True)
    return r
REL = json.load(open(os.path.join(SRC, "clipes_v12.json"))); REL["marchas"] = {"Andar": dict(REL["andar"], centro={k: 0.0 for k in M.PATAS}), "Trote": TROTE, "Corrida": CORRIDA}
REL["lote2_L2a"] = {}
for nome, G, fn in (("Trote", TROTE, corpo_trote), ("Corrida", CORRIDA, corpo_corrida)):
    n = int(round(G["T"] * M.FPS)); G["T"] = n / M.FPS; G["v_studs_s"] = round(G["D"] / G["T"], 3)    # ciclo em quadros inteiros
    ac, err, ext = M.gravar(nome, n, lambda t, G=G, fn=fn: montar(G, fn, t))
    REL["lote2_L2a"][nome] = {"quadros": n, "duracao_s": round(G["T"], 4), "laco": True, "v_studs_s": G["v_studs_s"], "varredura_apoio": G["varredura_apoio"],
                              "erro_ik_max": round(err, 5), "extensao_max_perna": {k: round(x, 3) for k, x in ext.items()}}
    print("V21", nome, json.dumps(REL["lote2_L2a"][nome]), flush=True)
M.ARM.animation_data.action = bpy.data.actions["Corrida"]
json.dump(REL, open(os.path.join(OUT, "clipes_v21.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("CLIPES_V21_OK", flush=True)
