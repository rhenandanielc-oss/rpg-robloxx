"""Auditoria contra lobo real: pranchas de QUADROS MARCADOS do jogo (anim_v31) por acao, para comparar com filmagens reais.
Por acao: 8 quadros espacados em um ciclo (marchas) ou na acao inteira (transicoes/viradas/repouso), linhas = vistas (perfil e
frente/tras), rotulo = acao, quadro, fase e patas no chao. Saida review/v32_lobo_real/revisao/acao_<nome>.png e 00_pose_neutra.png.
Uso: python prancha_real_v32.py (nesta pasta)"""
import os, json
from PIL import Image, ImageDraw
R = "review/v32_lobo_real"; O = os.path.join(R, "revisao"); os.makedirs(O, exist_ok=True)
QM = "review/v31_frontal/quadros"; QS = os.path.join(R, "quadros", "seq25"); QV = os.path.join(R, "quadros", "vir")
LM = json.load(open(os.path.join(QM, "linha_LOW.json")))["linha_do_tempo"]; LS = json.load(open(os.path.join(QS, "linha_LOW.json")))["linha_do_tempo"]
LV = json.load(open(os.path.join(QV, "linha_LOW_ida_volta_E.json")))["linha_do_tempo"]
TJ = {}
for fn in ("marchas_v29.json", "transicoes_v25.json", "viradas_v27.json"):
    for k, v in json.load(open(os.path.join("anim_v31", fn)))["acoes"].items(): TJ[k] = v
NQ = {"Andar": 36, "Trote": 18, "Corrida": 14}; FASES = {"Andar": {"TE": 0.0, "DE": 0.25, "TD": 0.5, "DD": 0.75}, "Trote": {"DE": 0.0, "TD": 0.0, "DD": 0.5, "TE": 0.5},
                                                       "Corrida": {"TE": 0.0, "TD": 0.08, "DD": 0.3, "DE": 0.4}}
CARGA = {"Andar": 0.62, "Trote": 0.4, "Corrida": 0.28}
def no_chao(ac, q):
    if ac == "Repouso": return ["DE", "DD", "TE", "TD"]
    if ac in TJ: return [k for k in ("DE", "DD", "TE", "TD") if TJ[ac]["apoio_por_quadro"][k][q]]
    T = NQ[ac]; return [k for k in ("DE", "DD", "TE", "TD") if ((q / T) - FASES[ac][k]) % 1.0 < CARGA[ac]]
def idx(L, ac):
    return [(i, int(e.split()[1][1:])) for i, e in enumerate(L) if e.split()[0] == ac]
def cel(p, txt, w=300, h=225):
    im = Image.new("RGB", (w, h), (24, 24, 28))
    if os.path.exists(p):
        s = Image.open(p).convert("RGB"); s.thumbnail((w, h)); im.paste(s, ((w - s.width) // 2, (h - s.height) // 2))
    else: ImageDraw.Draw(im).text((6, h // 2), "falta " + os.path.basename(p), fill=(255, 80, 80))
    d = ImageDraw.Draw(im); d.rectangle((0, 0, w, 15), fill=(0, 0, 0)); d.text((3, 2), txt, fill=(255, 235, 120)); return im
def prancha(nome, itens, vistas, arq, titulo):
    w, h = 300, 225; img = Image.new("RGB", (len(itens) * (w + 3) + 3, len(vistas) * (h + 3) + 30), (40, 40, 40)); d = ImageDraw.Draw(img); d.text((6, 8), titulo, fill=(255, 235, 120))
    for c, (i, ac, q) in enumerate(itens):
        for r, v in enumerate(vistas):
            img.paste(cel(arq(v, i), "%s q%d %s | chao: %s" % (ac, q, v, " ".join(no_chao(ac, q)) or "nenhuma (suspensao)")), (3 + c * (w + 3), 30 + r * (h + 3)))
    img.save(os.path.join(O, "acao_%s.png" % nome)); print("PRANCHA", nome, len(itens))
def amostra(lista, n=8):
    if len(lista) <= n: return lista
    return [lista[round(j * (len(lista) - 1) / (n - 1))] for j in range(n)]
fm = lambda v, i: os.path.join(QM, "LOW_%s_t%04d.png" % (v, i)); fs = lambda v, i: os.path.join(QS, "LOW_%s_t%04d.png" % (v, i)); fv = lambda v, i: os.path.join(QV, "LOW_ida_volta_E_%s_t%04d.png" % (v, i))
for ac in ("Andar", "Trote", "Corrida"):
    I = idx(LM, ac); ciclo = [x for x in I if x[0] >= I[0][0]][:NQ[ac]]
    prancha(ac, [(i, ac, q) for i, q in amostra(ciclo)], ("perfil_D", "frente", "tras"), fm, "%s (v31): 8 fases de UM ciclo; perfil D, frente, tras. Comparar com o trecho real da mesma fase" % ac)
for ac in ("AndarParaTrote", "TroteParaCorrida", "CorridaParaTrote", "TroteParaAndar"):
    prancha(ac, [(i, ac, q) for i, q in amostra(idx(LM, ac))], ("perfil_D", "frente", "tras"), fm, "%s (v31): 8 quadros espacados na acao inteira" % ac)
for ac in ("Arrancada", "Frenagem"):
    prancha(ac, [(i, ac, q) for i, q in amostra(idx(LS, ac))], ("perfil_D", "frente", "tras"), fs, "%s (v31): 8 quadros espacados na acao inteira" % ac)
prancha("Repouso", [(i, "Repouso", q) for i, q in amostra(idx(LS, "Repouso"), 4)], ("perfil_D", "frente", "tras"), fs, "Repouso (v31): pose em pe")
for ac in ("VirarEsquerda", "VirarDireita"):
    prancha(ac, [(i, ac, q) for i, q in amostra(idx(LV, ac))], ("topo", "frente", "perfil_E"), fv, "%s (v31, sequencia ida_volta_E): 8 quadros; topo, frente, perfil E (camera fixa)" % ac)
# pose neutra x referencia
w, h = 560, 420; ref = "../../../REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png"
i0 = idx(LS, "Repouso")[0][0]
img = Image.new("RGB", (4 * (w + 4), h + 34), (40, 40, 40)); d = ImageDraw.Draw(img); d.text((6, 8), "Pose em pe: referencia de APARENCIA (nao comprova biomecanica) x Repouso v31 (perfil, frente, tras)", fill=(255, 235, 120))
for c, (p, t) in enumerate(((ref, "referencia"), (fs("perfil_D", i0), "v31 Repouso perfil D"), (fs("frente", i0), "v31 Repouso frente"), (fs("tras", i0), "v31 Repouso tras"))):
    img.paste(cel(p, t, w, h), (4 + c * (w + 4), 30))
img.save(os.path.join(O, "00_pose_neutra.png")); print("PRANCHA_REAL_V32_OK")
