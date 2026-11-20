"""Empacota os clipes JSON aprovados do Lobo Ancestral (60 ossos, rig v28/v31) em StringValues compactos para o Studio,
sem HTTP e sem publicar animacoes: grava studio/dados/<Clipe>.txt + studio/lobo_dados.project.json; depois
`rojo build studio/lobo_dados.project.json -o studio/LoboAncestral.rbxm` e o usuario faz Insert from File.
Formato (mesmo codificador do urso, codigo proprio do lobo):
  linha 1: nome|fps|loop(0/1)|quadros|osso1,osso2,...
  linha 2: #M|Marcador=t,Marcador=t,...   linha 3: #V|velocidade_studs_s|rotacao_raiz_graus|fonte
  demais : Osso|canal(1..7)|S<valor> (constante) ou Osso|canal|E<deltas> (x1e4, delta, zigzag, base64 5 bits)
  canais constantes iguais ao padrao (q identidade, t zero) sao omitidos. Canais = qx qy qz qw tx ty tz (matrix_basis).
Uso: python studio/empacotar_lobo.py   (a lista de clipes e fontes esta em FONTES abaixo; grava studio/inventario.json)"""
import json, os, hashlib
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
PADRAO = [0, 0, 0, 1, 0, 0, 0]
def enc(vals):
    out = []; prev = 0
    for v in vals:
        q = round(v * 10000); d = q - prev; prev = q; z = (-d * 2 - 1) if d < 0 else d * 2
        while True:
            c = z & 31; z >>= 5
            if z: out.append(A[c | 32])
            else: out.append(A[c]); break
    return "".join(out)
BASE = ["Repouso", "Observar", "Andar", "Trote", "Corrida", "Partida", "Freada", "VirarE", "VirarD", "Sentar", "Sentado",
        "LevantarSentado", "Deitar", "Deitado", "Descanso", "Adormecer", "Despertar", "LevantarDeitado", "Salto", "Uivo",
        "Rosnar", "Mordida", "Garra", "Impacto"]
L5 = ["Repouso", "Observar", "Sentado", "Uivo", "Adormecer", "Despertar"]           # lote 5 substitui SO estes nomes
FONTES = {}
for n in BASE: FONTES[n] = ("clipes30", "base v30/v31")
for n in L5: FONTES[n] = ("comportamento/clipes_l5", "vida L5 (revisao)")
for pasta, lote, nomes in [("comportamento/clipes_l1", "vida L1", ["Beber", "Comer", "Farejar", "Sacudir", "Espreguicar", "Bocejar"]),
                           ("comportamento/clipes_l2", "vida L2", ["LamberPata", "Cavar", "DormirEnrolado"]),
                           ("comportamento/clipes_l3", "vida L3", ["Alerta", "Espreita", "FarejarAndando", "OlharTras", "Bote"]),
                           ("comportamento/clipes_l4", "vida L4", ["UivoSentado", "UivoEmPe", "LatidoAviso", "Ganido", "RosnadoAmeaca", "Saudacao"]),
                           ("habilidades/clipes_kit28", "kit v28", ["Hab_SaltoPredatorio", "Hab_UivoAncestral"]),
                           ("habilidades/clipes_kit30", "kit v30 (Investida sobre a Corrida v30)", ["Hab_Investida"]),
                           ("montaria/clipes_m2_v31", "montaria M2 r3 no rig de 60 ossos", ["Montar_E", "Montar_D", "Desmontar_E", "Desmontar_D"])]:
    for n in nomes: FONTES[n] = (pasta, lote)
# 16/11 (aprovado pelo usuario): virar andando + VirarE/D r2 (patas giram junto) + pelo do rosnado/latido sem dividir
for n in ["AndarCurvaE", "AndarCurvaD", "VirarE", "VirarD"]: FONTES[n] = ("marcha/clipes_curvas32", "curvas v32")
for n in ["RosnadoAmeaca", "LatidoAviso"]: FONTES[n] = ("comportamento/clipes_l4_r2", "vida L4 r2 (pelo)")
# 20/11: finalizacao propria do Lobo (mordida no flanco + sacudidas da cabeca), habilidades/clipes_finalizacao.py r2
FONTES["Hab_MordidaFlanco"] = ("habilidades/clipes_fin", "finalizacao r2 (flanco)")
# 20/11 r3: queda LATERAL propria (QuedaLado/CaidoLado/LevantarLado E/D) + mordida no flanco do alvo deitado de lado
for n in ["QuedaLadoE", "CaidoLadoE", "LevantarLadoE", "QuedaLadoD", "CaidoLadoD", "LevantarLadoD", "Hab_MordidaFlancoLado"]:
    FONTES[n] = ("habilidades/clipes_queda", "queda lateral r4 patas abertas" if n != "Hab_MordidaFlancoLado" else "queda lateral r3")
if __name__ == "__main__":
    os.makedirs(os.path.join(AQUI, "dados"), exist_ok=True)
    inv = {}; arvore = {"$className": "Folder"}
    OSSOS = None
    for nome, (pasta, lote) in FONTES.items():
        f = os.path.join(RAIZ, pasta, "LoboAncestral_" + nome + ".json")
        d = json.load(open(f, encoding="utf-8")); n = d["quadros"]
        ossos = list(d["ossos"].keys())
        assert len(ossos) == 60, (nome, len(ossos))
        if OSSOS is None: OSSOS = set(ossos)
        assert set(ossos) == OSSOS, nome
        mk = ",".join("%s=%.4f" % (m["nome"], m["t"]) for m in d["marcadores"])
        L = ["%s|%d|%d|%d|%s" % (nome, d["fps"], 1 if d["loop"] else 0, n, ",".join(ossos)), "#M|" + mk,
             "#V|%.4f|%.2f|%s" % (d.get("velocidade", 0.0) or 0.0, d.get("rotacao_raiz_graus", 0.0) or 0.0, lote)]
        for b in ossos:
            arr = d["ossos"][b]; assert len(arr) == 7 * n, (nome, b)
            for k in range(7):
                ch = [arr[i * 7 + k] for i in range(n)]
                if max(ch) - min(ch) < 1e-5:
                    if abs(ch[0] - PADRAO[k]) < 1e-5: continue
                    L.append("%s|%d|S%.5f" % (b, k + 1, ch[0]))
                else: L.append("%s|%d|E%s" % (b, k + 1, enc(ch)))
        txt = "\n".join(L)
        open(os.path.join(AQUI, "dados", nome + ".txt"), "w", encoding="utf-8", newline=chr(10)).write(txt)
        arvore[nome] = {"$path": "dados/" + nome + ".txt"}
        inv[nome] = {"fonte": pasta + "/LoboAncestral_" + nome + ".json", "lote": lote, "quadros": n, "fps": d["fps"],
                     "duracao": d["duracao"], "loop": d["loop"], "marcadores": d["marcadores"], "velocidade": d.get("velocidade"),
                     "bytes": len(txt), "md5_json": hashlib.md5(open(f, "rb").read()).hexdigest()}
        print("%-22s %-40s %4dq %6d bytes" % (nome, lote, n, len(txt)))
    vel = os.path.join(RAIZ, "habilidades", "clipes_kit30", "Investida_velocidade.json")
    if os.path.exists(vel):
        open(os.path.join(AQUI, "dados", "Perfil_Hab_Investida.txt"), "w", encoding="utf-8", newline=chr(10)).write(
            json.dumps(json.load(open(vel, encoding="utf-8"))))
        arvore["Perfil_Hab_Investida"] = {"$path": "dados/Perfil_Hab_Investida.txt"}
    json.dump({"name": "LoboAncestral", "tree": {"$className": "Folder", "Dados": arvore, "AdaptadorLobo": {"$path": "AdaptadorLobo.luau"}}}, open(os.path.join(AQUI, "lobo_dados.project.json"), "w"), indent=1)
    json.dump(inv, open(os.path.join(AQUI, "inventario.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(len(inv), "clipes; total", sum(v["bytes"] for v in inv.values()), "bytes")
