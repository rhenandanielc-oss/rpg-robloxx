"""Gera Movimento_LoboArtico (ModuleScript em Lua) com o deslocamento aprovado no Blender, por quadro (30 fps), no espaco
do modelo do Roblox (pivo = origem do armature; frente -Z; esquerda -X): {dx, dz, giro_rad} por quadro.
Mapa Blender->Roblox: (x, y, z) -> (-x, z, y); rumo psi em torno de +Z (Blender) = giro em torno de +Y (Roblox), mesmo sinal.
Fontes: anim_v41/transicoes_v25.json (Arrancada/Frenagem), marchas_v29.json (trocas de marcha), viradas_v27.json, clipes_v21.json.
Lacos: velocidade constante (studs/s) -- Andar 3,0; Trote 4,0/0,6; Corrida = transicoes v_corrida."""
import json, math
A = '../anim_v41/'
t = json.load(open(A + 'transicoes_v25.json')); m = json.load(open(A + 'marchas_v29.json')); v = json.load(open(A + 'viradas_v27.json'))
curvas = {}
for nome, d in list(t['acoes'].items()) + list(m['acoes'].items()):
    assert d['direcao'] == [0, -1, 0], (nome, d['direcao'])
    curvas[nome] = [(0.0, x, 0.0) for x in d['X_por_quadro']]            # Blender Y -> Roblox Z
for nome, d in v['acoes'].items():
    curvas[nome] = [(-T[0], T[1], math.radians(p)) for T, p in zip(d['T_por_quadro'], d['psi_graus_por_quadro'])]
vel = {"Andar": 3.0, "Trote": 4.0 / 0.6, "Corrida": t['v_corrida']}
L = ["-- GERADO por studio/gerar_movimento_v41.py (Lobo Artico anim_v41). Nao editar a mao.",
     "-- Curvas[clipe][q+1] = {dx, dz, giro} no espaco do modelo (pivo = origem do rig, frente -Z), 30 fps.",
     "local M = {Fps = 30, Velocidade = {%s}, Curvas = {}}" % ", ".join("%s = %.4f" % kv for kv in vel.items())]
for nome, c in curvas.items():
    L.append("M.Curvas.%s = {%s}" % (nome, ",".join("{%.4f,%.4f,%.5f}" % q for q in c)))
L.append("return M")
open('Movimento_LoboArtico.lua', 'w', newline='\n').write("\n".join(L))
for nome, c in curvas.items(): print(nome, len(c), 'fim', c[-1])
print('vel', vel)
