"""v49: = gerar_movimento_v48 + CURVAS DE TROTE E CORRIDA (anim_v49/curvas_trote_v49.json, curvas_corrida_v49.json)."""
"""v48: = gerar_movimento_v47 + PARTIDA/PARADA (anim_v48/partida_v48.json, curva externa por quadro com deslocamento lateral)."""
"""v47: = gerar_movimento_v46b + as VIRADAS DE COMBATE (anim_v47b/viradas_combate_v47.json: VirarCombate90/180 E/D, pivo 25% a frente das
traseiras); saida Movimento_LoboArtico_v49.lua. Anteriores intactos."""
"""v46b: = gerar_movimento_v44 + as CURVAS ANDANDO da anim_v46c (curvas_v46b.json: lacos AndarCurva*/AndarCurvaFechada* e transicoes
AndarParaCurva*/CurvaParaAndar*/CurvaParaFechada*/FechadaParaCurva*); saida Movimento_LoboArtico_v49.lua. Para as curvas a
translacao inclui o deslocamento LATERAL (giro em volta do centro do corpo, nao do pivo). Os anteriores ficam intactos."""
"""v44: = gerar_movimento_v41 + as viradas CURTAS da anim_v44b (viradas_curtas_v44.json); saida Movimento_LoboArtico_v49.lua
(o Movimento_LoboArtico.lua da v41 fica intacto). Texto original:
Gera Movimento_LoboArtico (ModuleScript em Lua) com o deslocamento aprovado no Blender, por quadro (30 fps), no espaco
do modelo do Roblox (pivo = origem do armature; frente -Z; esquerda -X): {dx, dz, giro_rad} por quadro.
Mapa Blender->Roblox: (x, y, z) -> (-x, z, y); rumo psi em torno de +Z (Blender) = giro em torno de +Y (Roblox), mesmo sinal.
Fontes: anim_v41/transicoes_v25.json (Arrancada/Frenagem), marchas_v29.json (trocas de marcha), viradas_v27.json, clipes_v21.json.
Lacos: velocidade constante (studs/s) -- Andar 3,0; Trote 4,0/0,6; Corrida = transicoes v_corrida."""
import json, math
A = '../anim_v41/'
t = json.load(open(A + 'transicoes_v25.json')); m = json.load(open(A + 'marchas_v29.json')); v = json.load(open(A + 'viradas_v27.json'))
vc = json.load(open('../anim_v44b/viradas_curtas_v44.json'))
cb = json.load(open('../anim_v46c/curvas_v46b.json'))
vk = json.load(open('../anim_v47b/viradas_combate_v47.json'))
pp = json.load(open('../anim_v48/partida_v48.json'))
tc = json.load(open('../anim_v49/curvas_trote_v49.json')); cc = json.load(open('../anim_v49/curvas_corrida_v49.json'))
curvas = {}
for nome, d in list(t['acoes'].items()) + list(m['acoes'].items()):
    assert d['direcao'] == [0, -1, 0], (nome, d['direcao'])
    curvas[nome] = [(0.0, x, 0.0) for x in d['X_por_quadro']]            # Blender Y -> Roblox Z
for nome, d in list(v['acoes'].items()) + list(vc['acoes'].items()) + list(vk['acoes'].items()):
    curvas[nome] = [(-T[0], T[1], math.radians(p)) for T, p in zip(d['T_por_quadro'], d['psi_graus_por_quadro'])]
for nome, d in list(cb['acoes'].items()) + list(pp['acoes'].items()) + list(tc['acoes'].items()) + list(cc['acoes'].items()):
    curvas[nome] = [(-e[0], e[1], math.radians(e[2])) for e in d['externa_por_quadro_xy_psi']]
vel = {"Andar": 3.0, "Trote": 4.0 / 0.6, "Corrida": t['v_corrida']}
L = ["-- GERADO por studio/gerar_movimento_v49.py (Lobo Artico anim_v41 + viradas curtas v44b + curvas andando v46b + viradas de combate v47 + partida/parada v48 + curvas de trote/corrida v49). Nao editar a mao.",
     "-- Curvas[clipe][q+1] = {dx, dz, giro} no espaco do modelo (pivo = origem do rig, frente -Z), 30 fps.",
     "local M = {Fps = 30, Velocidade = {%s}, Curvas = {}}" % ", ".join("%s = %.4f" % kv for kv in vel.items())]
for nome, c in curvas.items():
    L.append("M.Curvas.%s = {%s}" % (nome, ",".join("{%.4f,%.4f,%.5f}" % q for q in c)))
L.append("return M")
open('Movimento_LoboArtico_v49.lua', 'w', newline='\n').write("\n".join(L))
for nome, c in curvas.items(): print(nome, len(c), 'fim', c[-1])
print('vel', vel)
