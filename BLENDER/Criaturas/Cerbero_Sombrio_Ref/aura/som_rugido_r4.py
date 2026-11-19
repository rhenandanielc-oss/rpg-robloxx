"""REPROVADO pelo usuario em 18/11 ("esse som no rugido nao"): nao usar. Os .wav e os videos _SOM foram apagados.
SOM PROVISORIO (sintetizado, NAO oficial) do Rugido Infernal r4 do Cerbero - so para sincronizar a previa no Blender.
Tres rugidos graves com timbre por cabeca (C medio, E mais agudo, D mais grave) + sopro de fogo ao acender o violeta + estalos
das mordidas do FuriaLoop. Tempos vindos do manifesto (rig/clipes_L3r4). Uso: python som_rugido_r4.py <saida_dir>"""
import numpy as np, wave, json, os, sys
SR = 44100; RNG = np.random.default_rng(7)
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(sys.argv[1]); os.makedirs(OUT, exist_ok=True)
MANI = json.load(open(os.path.join(AQUI, "..", "rig", "clipes_L3r4", "manifesto_clipes.json"), encoding="utf-8"))
EV = MANI["FuriaRugidoR4"]["eventos_s"]; PREV = MANI["Prev_FuriaR4"]["eventos_s"]; LOOP = MANI["FuriaLoop"]["eventos_s"]
def polo(x, fc):                                   # passa-baixa de 1 polo
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x): s = (1 - a) * v + a * s; y[i] = s
    return y
def suave(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def rugido(f0, dur_ab, dur_sus, dur_fe, brilho):
    n = int(SR * (dur_ab + dur_sus + dur_fe + 0.15)); t = np.arange(n) / SR
    env = suave(t / dur_ab) * (1 - suave((t - dur_ab - dur_sus) / dur_fe))
    jit = polo(RNG.normal(0, 1, n), 6.0); jit /= np.abs(jit).max() + 1e-9
    f = f0 * (1 + 0.10 * suave(t / dur_ab) - 0.06 * suave((t - dur_ab - dur_sus) / dur_fe) + 0.035 * jit)
    fase = 2 * np.pi * np.cumsum(f) / SR; x = np.zeros(n)
    for h in range(1, 40):
        fh = f0 * h
        if fh > 6000: break
        amp = h ** -0.85 * (1.0 + 1.6 * np.exp(-((fh - 420) / 160) ** 2) + 1.1 * np.exp(-((fh - 950 * brilho) / 260) ** 2) + 0.5 * np.exp(-((fh - 2300) / 500) ** 2))
        x += amp * np.sin(h * fase + RNG.uniform(0, 6.28))
    am = 1 + 0.55 * np.sin(2 * np.pi * 27 * t + 3 * polo(RNG.normal(0, 1, n), 4.0))      # rosnado (aspereza)
    sopro = polo(RNG.normal(0, 1, n), 2600) - polo(RNG.normal(0, 1, n), 300)
    y = (x / np.abs(x).max()) * am * 0.8 + 0.35 * sopro / (np.abs(sopro).max() + 1e-9)
    return np.tanh(1.9 * y * env) * 0.9
def fogo(dur):
    n = int(SR * dur); t = np.arange(n) / SR; env = suave(t / 0.08) * (1 - suave((t - 0.15) / (dur - 0.15)))
    r = RNG.normal(0, 1, n); y = polo(r, 900) - polo(r, 120); return 0.5 * y / np.abs(y).max() * env
def estalo():
    n = int(SR * 0.12); t = np.arange(n) / SR; r = RNG.normal(0, 1, n)
    return (polo(r, 3000) * np.exp(-t / 0.018) + 0.6 * np.sin(2 * np.pi * 140 * t) * np.exp(-t / 0.03)) * 0.6
def gravar(nome, y):
    y = np.clip(y / max(1e-9, np.abs(y).max()) * 0.85, -1, 1); s = (y * 32767).astype(np.int16)
    with wave.open(os.path.join(OUT, nome), "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(s.tobytes())
TIMBRE = {"C": (68.0, 1.0), "E": (82.0, 1.15), "D": (58.0, 0.9)}
dur_total = PREV["saida"] + 0.8 + 0.5; pista = np.zeros(int(SR * dur_total)); relato = {}
def somar(y, t0):
    i = int(SR * t0); pista[i:i + len(y)] += y[: len(pista) - i]
for k, (f0, br) in TIMBRE.items():
    ab = EV["boca_max_" + k] - EV["rugido_" + k]; sus = EV["fecha_" + k] - EV["boca_max_" + k]; fe = EV["fechada_" + k] - EV["fecha_" + k] + 0.1
    y = rugido(f0, ab, sus, fe, br); gravar("rugido_%s.wav" % k, y); somar(y, EV["rugido_" + k]); somar(fogo(0.7), EV["rugido_" + k])
    relato["rugido_" + k] = {"inicio_s": EV["rugido_" + k], "boca_max_s": EV["boca_max_" + k], "fim_s": round(EV["fechada_" + k] + 0.1, 3), "f0_hz": f0}
mords = []
for vez in range(2):
    for k in "CED":
        tm = PREV["loop"] + vez * 2.0 + LOOP["contato_" + k]; somar(estalo(), tm); mords.append(round(tm, 2))
gravar("furia_r4_trilha.wav", pista)
relato.update({"mordidas_loop_s": mords, "duracao_s": round(dur_total, 2), "nota": "som PROVISORIO sintetizado (placeholder), nao oficial"})
json.dump(relato, open(os.path.join(OUT, "som_r4.json"), "w"), indent=1, ensure_ascii=False); print("SOM_OK", relato)
