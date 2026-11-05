"""Vozes em camadas (05/11, aprovado de ouvido: "Aprovar e aplicar"). Perfil de voz do Sombrio; Fogo (Montanhas) e Gelo
(Glacial) com camadas por baixo da voz e tom proprio por tipo de rugido; asas/passos calmos para todos. SonsConfig ja foi
editado no src/ (dados); aqui: trocas ancoradas no SonsDragao_Cliente (src/) e o patch Studio
V14/ia/patch_vozes_camadas.luau (tudo-ou-nada; backup unico ServerStorage.Backup_Vozes_Camadas_2026-11-05 com os 2 scripts
anteriores; o SonsConfig do Studio so e trocado se for igual ao do HEAD do git)."""
import os, subprocess
RAIZ = r"C:/Users/Rhenan/Downloads/RPG_Roblox_GitHub_Pacote_Inicial"
MARCA = "PATCH_VOZES_CAMADAS"
CLI = "src/StarterPlayer/StarterPlayerScripts/SonsDragao_Cliente.client.luau"
CFG = "src/ReplicatedStorage/Montaria_Dragoes/SonsConfig.luau"
VOZ_SOMBRIO = '''-- PATCH_VOZES_CAMADAS (05/11): Sombrio — tons por tipo (aprovados de ouvido); fases = as do Montanhas (mesmo sistema
-- universal de clipes). Chaves que o perfil nao tem (farejar, beber...) ficam mudas. O Rugido_Combate NAO tem voz aqui: e o clipe da
-- habilidade Rugido, cujo som vem do evento FX (rugidoCombate + camadas), senao rugiria duas vezes.
local VOZ_SOMBRIO = {
	Rugido_Territorial = {{0.30, "rugidoTerritorial", 1, 1.1, 0.72}},
	Rugido_Ameaca = {{0.30, "rugidoAmeaca", 1, 1.05, 0.78}}, Ninho_Ameaca = {{0.34, "rugidoAmeaca", 1, 1.0, 0.78}},
	Intimidar = {{0.18, "intimidar", 0.9, 0.85, 0.75}},
	Reagir_Estimulo = {{0.12, "alerta", 0.8, 0.65, 0.8}}, Ninho_Alerta = {{0.2, "alerta", 0.8, 0.65, 0.78}},
	Idle_Alerta_Mantido = {{0.5, "grunhido", 0.35, 0.5, 0.75}}, Preparar_Combate = {{0.3, "esforco", 0.5, 0.65, 0.75}},
	Curiosidade = {{0.45, "respiro", 0.8, 0.5, 1.0}}, Deitar = {{0.7, "respiro", 0.7, 0.4, 0.95}},
	Comer = {{0.1, "mordida", 1, 0.7, 0.8}, {0.433, "mordida", 1, 0.7, 0.8}, {0.766, "mordida", 1, 0.7, 0.8}},
	Dano_Leve = {{0.05, "danoLeve", 1, 0.65, 0.8}}, Dano_Leve_Ar = {{0.05, "danoLeve", 1, 0.65, 0.8}},
	Dano_Forte = {{0.05, "dano", 1, 0.9, 0.72}}, Dano_Forte_Ar = {{0.05, "dano", 1, 0.9, 0.72}},
}
'''
CAMADAS = '''-- PATCH_VOZES_CAMADAS (05/11): camadas da voz (SonsConfig.formas[..].camadas[k] = {{som, vol rel, tom rel, atraso}}):
-- tocam junto com a voz principal, no mesmo tom relativo (inclui a variacao), e acabam junto com ela
local function camadas(pp, C, k, vol, tom, corte, dist)
	local l = C.camadas and C.camadas[k]; if not l then return end
	for _, c in ipairs(l) do
		local atraso = c[4] or 0
		local dur = corte and math.max(0.6, corte - atraso) or nil
		local function vai() if pp.Parent then tocar(pp, c[1], vol * c[2], tom * c[3], dur, dist, atraso == 0 and ENVELOPE[k]) end end
		if atraso > 0 then task.delay(atraso, vai) else vai() end
	end
end
'''
TROCAS = [
 # tom proprio por tipo no Fogo (antes: TOM_RUGIDO_FOGO em todos)
 ('\tRugido_Ameaca = {{0.30, "rugidoAmeaca", 1, 1.05, TOM_RUGIDO_FOGO}},\n',
  '\tRugido_Ameaca = {{0.30, "rugidoAmeaca", 1, 1.05, 0.95}},                -- PATCH_VOZES_CAMADAS: tom por tipo\n'),
 ('{0.36, "rugidoVitoria", 1, 1.0, TOM_RUGIDO_FOGO}', '{0.36, "rugidoVitoria", 1, 1.0, 0.88}'),
 ('\tNinho_Ameaca = {{0.34, "rugidoAmeaca", 1, 1.0, TOM_RUGIDO_FOGO}},\n', '\tNinho_Ameaca = {{0.34, "rugidoAmeaca", 1, 1.0, 0.95}},\n'),
 # Glacial: o Rugido_Territorial estava preso dentro de um comentario (caia no generico 0.85 x TomVoz)
 ('\tNinho_Ameaca = {{0.34, "rugidoAmeaca", 1, 1.0, 1.0}},   -- (03/11) uma tomada fixa e longa (o "intimidar" sorteava uma curta) Rugido_Territorial = {{0.3, "rugido", 1, 1.25, 1.0}},\n',
  '\tNinho_Ameaca = {{0.34, "rugidoAmeaca", 1, 1.0, 1.0}},   -- (03/11) uma tomada fixa e longa (o "intimidar" sorteava uma curta)\n'
  '\tRugido_Territorial = {{0.3, "rugido", 1, 1.25, 1.0}},   -- PATCH_VOZES_CAMADAS: antes ficava dentro do comentario acima\n'),
 ('local VOZ_FORMA = {Montanhas = VOZ_MONTANHAS, Glacial = {\n',
  VOZ_SOMBRIO + 'local VOZ_FORMA = {Montanhas = VOZ_MONTANHAS, Sombrio = VOZ_SOMBRIO, Glacial = {\n'),
 ('\trugidoTerritorial = 8, rugidoCorpo = 2, rugidoAmeaca = 4, rugidoAmeacaCorpo = 2, rugidoVitoria = 20, rosnado = 2.5, bafo = 3, inspira = 2}\n',
  '\trugidoTerritorial = 8, rugidoCorpo = 2, rugidoAmeaca = 4, rugidoAmeacaCorpo = 2, rugidoVitoria = 20, rosnado = 2.5, bafo = 3, inspira = 2,\n'
  '\trugidoCombate = 6}                                               -- PATCH_VOZES_CAMADAS\n'),
 ('\tinspira = 1.1, dano = 0.9, despertar = 1.4, intimidar = 1.8, rugido = 3.4}\n',
  '\tinspira = 1.1, dano = 0.9, despertar = 1.4, intimidar = 1.8, rugido = 3.4, rugidoCombate = 1.9}\n'),
 ('local function sorteia(t) return type(t) == "table" and t[math.random(#t)] or t end\n',
  'local function sorteia(t) return type(t) == "table" and t[math.random(#t)] or t end\n' + CAMADAS),
 ('\t\t\t\tlocal varia = RUGIDOS[k] and 1 or (0.95 + math.random() * 0.1)      -- rugido: sempre o mesmo tom\n'
  '\t\t\t\ttocar(pp, sorteia(C[k]), vol, ev[5] * varia * tomVoz(pp), CORTE_VOZ[k], dist, ENVELOPE[k])\n',
  '\t\t\t\t-- PATCH_VOZES_CAMADAS: rugido varia pouco (+-3%) em volta do tom do tipo; o resto +-5%\n'
  '\t\t\t\tlocal varia = RUGIDOS[k] and (0.97 + math.random() * 0.06) or (0.95 + math.random() * 0.1)\n'
  '\t\t\t\tlocal tom = ev[5] * varia * tomVoz(pp)\n'
  '\t\t\t\ttocar(pp, sorteia(C[k]), vol, tom, CORTE_VOZ[k], dist, ENVELOPE[k])\n'
  '\t\t\t\tcamadas(pp, C, k, vol, tom, CORTE_VOZ[k], dist)\n'),
 ('\t\t\t\t\t\t\t\ttocar(pp, C.passoPeso, C.passoPesoVolume * (nome == "Correr" and 1.4 or 1), 0.9 + math.random() * 0.2, C.passoPesoCorte, C.distPasso)\n',
  '\t\t\t\t\t\t\t\tif (C.passoPesoVolume or 0) > 0 then                 -- PATCH_VOZES_CAMADAS: 0 = sem baque\n'
  '\t\t\t\t\t\t\t\t\ttocar(pp, C.passoPeso, C.passoPesoVolume * (nome == "Correr" and 1.4 or 1), 0.9 + math.random() * 0.2, C.passoPesoCorte, C.distPasso)\n'
  '\t\t\t\t\t\t\t\tend\n'),
 ('\t\telseif h == "Rugido" and f == "emissao" then tocar(pp, C.rugidoCombate or C.rugido, 1.5, 0.95 * tomVoz(pp), 1.9, C.distVoz, true) end\n',
  '\t\telseif h == "Rugido" and f == "emissao" then\n'
  '\t\t\tlocal k = C.rugidoCombate and "rugidoCombate" or "rugido"; local tom = 0.95 * tomVoz(pp)\n'
  '\t\t\ttocar(pp, C[k], 1.5, tom, 1.9, C.distVoz, true); camadas(pp, C, k, 1.5, tom, 1.9, C.distVoz)   -- PATCH_VOZES_CAMADAS\n'
  '\t\tend\n'),
]
p = os.path.join(RAIZ, CLI); s = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in s else "\n"; s = s.replace("\r\n", "\n")
if MARCA not in s:
    for a, b in TROCAS:
        n = s.count(a); assert n == 1, (n, a[:70]); s = s.replace(a, b)
    open(p, "w", encoding="utf-8", newline="").write(s.replace("\n", nl)); print("src ok cliente")
CFG_NOVO = open(os.path.join(RAIZ, CFG), encoding="utf-8").read().replace("\r\n", "\n")
CFG_HEAD = subprocess.run(["git", "-C", RAIZ, "show", "HEAD:" + CFG], capture_output=True, encoding="utf-8").stdout.replace("\r\n", "\n")
assert MARCA in CFG_NOVO and MARCA not in CFG_HEAD and len(CFG_HEAD) > 1000
for x in [a + b for a, b in TROCAS] + [CFG_NOVO, CFG_HEAD]: assert "]=====]" not in x
L = ['-- patch_vozes_camadas.luau (Studio, Edit) — vozes em camadas + Sombrio + asas/passos calmos (05/11).',
     '-- Gerado por sombrio/gerar_patch_vozes_camadas.py; backup unico ServerStorage.Backup_Vozes_Camadas_2026-11-05.',
     'assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")',
     'local SS = game:GetService("ServerStorage")',
     'local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end',
     'local C = game.StarterPlayer.StarterPlayerScripts.SonsDragao_Cliente; local src = C.Source:gsub("\\r\\n", "\\n")',
     'local K = game.ReplicatedStorage.Montaria_Dragoes.SonsConfig; local cfg = K.Source:gsub("\\r\\n", "\\n")',
     'if src:find("%s", 1, true) or cfg:find("%s", 1, true) then return "ja aplicado" end' % (MARCA, MARCA),
     'assert(cfg == [=====[' + CFG_HEAD + ']=====], "SonsConfig do Studio difere do HEAD do git (nao troco)")']
for a, b in TROCAS:
    L.append('src = troca(src, [=====[' + a + ']=====], [=====[' + b + ']=====])')
L += ['assert(loadstring(src), "SonsDragao_Cliente nao compila")',
      'local novoCfg = [=====[' + CFG_NOVO + ']=====]',
      'assert(loadstring(novoCfg), "SonsConfig nao compila")',
      'if not SS:FindFirstChild("Backup_Vozes_Camadas_2026-11-05") then local f = Instance.new("Folder"); f.Name = "Backup_Vozes_Camadas_2026-11-05"; C:Clone().Parent = f; K:Clone().Parent = f; f.Parent = SS end',
      'C.Source = src; K.Source = novoCfg',
      'return "aplicado: SonsDragao_Cliente (" .. #src .. " bytes) + SonsConfig (" .. #novoCfg .. " bytes)"']
open(os.path.join(RAIZ, "BLENDER/Criaturas/Teste_IA/V14/ia/patch_vozes_camadas.luau"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("patch gerado")
