"""Simulacao LOCAL (NAO e o Roblox) da orientacao PARADA do Controle: r7 x r8 (20/11/2026).
r7: |a| > 60 -> Virar 90 graus (3,1 s, curva do clipe); 4 < |a| <= 60 -> gira o PIVO a 60 graus/s com o Repouso tocando
    (patas plantadas: "shift lock").
r8: zona morta 20 graus (30 durante 1 s depois de um giro); 20-60 -> VirarCurto 45 graus (1,53 s, anim_v44b); > 60 -> Virar 90.
    Os clipes seguem a curva de rumo do proprio clipe (aqui: suavizada) e NAO reiniciam no meio.
Mede: graus girados SEM passos (pivo sobre patas plantadas), quantos giros com passos, erro medio/maximo de orientacao e
quantas inversoes de sentido (tremor). Uso: python simular_giro_r8.py -> tabela + simular_giro_r8.json"""
import math, json
DT = 1 / 60
CLIP = {"Virar": (90.0, 3.1), "Curto": (45.0, 1.53)}
def norm(a): return (a + 180) % 360 - 180
def perfil(x): return x * x * (3 - 2 * x)                     # rumo do clipe (aprox. da curva trapezoidal suave)

def rodar(versao, alvo_fn, T=20.0):
    rumo, t, clipe, sem_passos, giros, inv, ult_sinal, fim_giro = 0.0, 0.0, None, 0.0, 0, 0, 0, -9
    filt, fora_desde = alvo_fn(0.0), None                          # r8b: direcao do alvo suavizada + persistencia
    erros = []
    while t < T:
        a = norm(alvo_fn(t) - rumo)
        if versao in ("r8b", "r8c"):
            filt += norm(alvo_fn(t) - filt) * (1 - math.exp(-DT / 0.4)); a = norm(filt - rumo)
        if clipe:
            nome, sinal, t0, r0 = clipe; ang, dur = CLIP[nome]; x = (t - t0) / dur
            if x >= 1: rumo = r0 + sinal * ang; clipe = None; fim_giro = t
            else: rumo = r0 + sinal * ang * perfil(x)
        else:
            g = abs(a); s = 1 if a > 0 else -1
            if versao == "r7":
                if g > 60: clipe = ("Virar", s, t, rumo); giros += 1
                elif g > 4:
                    passo = min(g, 60 * DT); rumo += s * passo; sem_passos += passo
                    if ult_sinal and s != ult_sinal: inv += 1
                    ult_sinal = s
            else:
                zm = 30 if t - fim_giro < 1.0 else 20
                if versao == "r8c": zm = 40 if t - fim_giro < 1.0 else 35      # r8c: a cabeca cobre ate 35 graus
                pronto = True
                if versao in ("r8b", "r8c"):
                    if g > zm: fora_desde = fora_desde if fora_desde is not None else t
                    else: fora_desde = None
                    pronto = fora_desde is not None and t - fora_desde >= 0.3
                if pronto and g > 60: clipe = ("Virar", s, t, rumo); giros += 1; fora_desde = None
                elif pronto and g > zm: clipe = ("Curto", s, t, rumo); giros += 1; fora_desde = None
                if clipe:
                    if ult_sinal and s != ult_sinal: inv += 1
                    ult_sinal = s
        erros.append(abs(norm(alvo_fn(t) - rumo)))
        t += DT
    return {"versao": versao, "graus_sem_passos": round(sem_passos, 1), "giros_com_passos": giros, "inversoes": inv,
            "erro_medio": round(sum(erros) / len(erros), 1), "erro_max_ult5s": round(max(erros[-int(5 / DT):]), 1)}

CEN = {
    "alvo parado a frente (5 graus)": lambda t: 5.0,
    "alvo parado ao lado (90 graus)": lambda t: 90.0,
    "alvo parado atras (180 graus)": lambda t: 179.0,
    "alvo a 35 graus": lambda t: 35.0,
    "oscilacao pequena (+-12 graus em torno de 0, 0,5 Hz)": lambda t: 12 * math.sin(2 * math.pi * 0.5 * t),
    "oscilacao em torno de 30 graus (+-12)": lambda t: 30 + 12 * math.sin(2 * math.pi * 0.5 * t),
    "alvo circulando (r 10, 6 studs/s = 34 graus/s)": lambda t: math.degrees(6 / 10 * t),
    "alvo circulando devagar (r 15, 3 studs/s = 11 graus/s)": lambda t: math.degrees(3 / 15 * t),
}
res = []
print("%-56s %-4s %8s %6s %5s %7s %8s" % ("cenario", "ver", "semPass", "giros", "inv", "erroMed", "erroMax5s"))
for nome, f in CEN.items():
    for v in ("r7", "r8", "r8b", "r8c"):
        r = rodar(v, f); r["cenario"] = nome; res.append(r)
        print("%-56s %-4s %8s %6s %5s %7s %8s" % (nome, v, r["graus_sem_passos"], r["giros_com_passos"], r["inversoes"], r["erro_medio"], r["erro_max_ult5s"]))
json.dump(res, open("simular_giro_r8.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
