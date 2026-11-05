-- patch_vozes_camadas.luau (Studio, Edit) — vozes em camadas + Sombrio + asas/passos calmos (05/11).
-- Gerado por sombrio/gerar_patch_vozes_camadas.py; backup unico ServerStorage.Backup_Vozes_Camadas_2026-11-05.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local SS = game:GetService("ServerStorage")
local function troca(src, a, b) local i, j = string.find(src, a, 1, true); assert(i, "trecho nao encontrado: " .. a:sub(1, 60)); assert(not string.find(src, a, j + 1, true), "repetido: " .. a:sub(1, 60)); return src:sub(1, i - 1) .. b .. src:sub(j + 1) end
local C = game.StarterPlayer.StarterPlayerScripts.SonsDragao_Cliente; local src = C.Source:gsub("\r\n", "\n")
local K = game.ReplicatedStorage.Montaria_Dragoes.SonsConfig; local cfg = K.Source:gsub("\r\n", "\n")
if src:find("PATCH_VOZES_CAMADAS", 1, true) or cfg:find("PATCH_VOZES_CAMADAS", 1, true) then return "ja aplicado" end
assert(cfg == [=====[-- SonsConfig (ModuleScript) — audio dos dragoes. SO audio licenciado: biblioteca Pro Sound Effects publicada na Roblox
-- ("Courtesy of Pro Sound Effects", conta ProSoundEffects) e sons do proprio motor (rbxasset://). Nada copiado de jogos.
-- Volumes/tons provisorios (NAO_APROVADO). corte = segundos ate parar (trecho util de um arquivo longo).
local function id(n) return "rbxassetid://" .. n end
return {
	NAO_APROVADO = true,
	distMax = 260,
	-- PATCH_RUGIDO_SEM_ATRASO (02/11): segundo do arquivo em que o rugido fica AUDIVEL (RMS medido com AudioAnalyzer no
	-- Studio). Varias tomadas comecam quase em silencio (ate 1,1 s) e a boca abria antes do som: o mixer comeca o som
	-- nesse ponto (TimePosition) e encurta o corte na mesma medida (o fim do arquivo continua o mesmo).
	inicioAudivel = {
		["9126100408"] = 0.22, ["9126100484"] = 0.47, ["9126100903"] = 1.02, ["9126100708"] = 1.17, ["9126100618"] = 0.92,  -- Fogo
		["9113973520"] = 0.32, ["9113973748"] = 0.52, ["9113985445"] = 0.75,                                                -- Fogo (intimidar, padrao)
		["9116306862"] = 1.00, ["9116302511"] = 0.04, ["9116303194"] = 0.25, ["9116303929"] = 0.92, ["9116300504"] = 0.32,  -- Glacial
		["9116304872"] = 0.07,
	},
	asa = {id(9120771864), id(9120776877)},        -- Wing Flaps 27 / 1 (SFX): "Large Flying Creature"
	asaVolume = 0.9, asaTom = {0.75, 0.9},
	passo = {"rbxasset://sounds/action_footsteps_plastic.mp3"}, passoTom = {0.42, 0.55}, passoVolume = 0.9,
	passoPeso = id(9118633669), passoPesoCorte = 0.35, passoPesoVolume = 0.35,   -- Rock Impacts Deep Crunchy Hits 11
	mordida = {id(9125467298), id(9125466463)},   -- Creature Bite Pterodactyl Crunch (SFX)
	mordidaTom = {0.7, 0.85},
	avanco = id(9126229255),                         -- Whoosh By Fast Airy Swooshing (SFX)
	fogo = id(9114463219),                           -- Flame Licks 8 (SFX)
	ar = id(9125805579),                             -- Rising Whoosh Hissing Build Up (SFX)
	rocha = id(9118633669), rochaArrasto = id(9125881604),   -- Rock Impacts / Rock Scrape (SFX)
	rugido = id(9113985445),                         -- Creature Roar Deep Throaty Growls 2 (SFX)
	respiro = id(9113971531), respiroVolume = 0.35, respiroTom = {0.55, 0.7},   -- Creature Growls Lion 4: Deep Quiet Breathy (SFX)
	respiroIntervalo = {7, 15},                      -- segundos entre respiracoes audiveis (parado/andando), nunca regular
	esforco = id(9125467848), esforcoVolume = 0.55,  -- Creature Growls Lion Deep Guttural Rumbling (SFX): esforco curto
	garra = id(9119228132), garraVolume = 0.9,       -- Slow Whoosh Beefy Airy Pass By 5 (SFX): deslocamento do golpe
	impacto = id(9118633669), impactoCorte = 0.3,    -- Rock Impacts Deep Crunchy: so quando ACERTA
	maxSimultaneos = 6,                              -- por dragao (evita sobreposicao)
	-- PATCH_AUDIO_GELO (02/11): perfil PROPRIO por forma regional (atributo FormaRegional). O que nao estiver aqui cai
	-- no padrao acima (Montanhas). Alcance por categoria (dist*): voz longe, respiracao perto.
	formas = {
		-- PATCH_RUGIDOS_FOGO (02/11): voz do Dragao das Montanhas — agressiva, rouca e dominante (familia Creature Roar /
		-- Giant Crab Monster / Pit Bull snarl); NADA da familia Lion usada no Glacial. So as chaves de VOZ; o resto herda.
		Montanhas = {
			-- usuario 02/11: UM som por rugido, mesmo tom em todos, mas cada tipo com a SUA tomada; o arquivo anterior (Deep
			-- Throaty Growls, rebaixado) soava "engasgado" -> familia Thunder With Lion Roar (Growl, Low Rumble, Roar), limpa,
			-- grave e com ronco por baixo (sem as variantes com estalo eletrico)
			rugidoTerritorial = id(9126100903),          -- Thunder With Lion Roar Growl Low Rumble Roar 14 (4,2 s)
			rugidoAmeaca = id(9126100484),               -- idem 8 (3,1 s)
			rugidoVitoria = id(9126100708),              -- idem 13 (3,8 s)
			rosnado = {id(9113973520), id(9113973748), id(9113973436)},   -- Creature Growls Pit Bull 4 / 3 / 1: snarl agressivo
			bafo = id(9114431819),                       -- Fire Burst 6: ascending air release (calor na expiracao, baixo)
			esforco = {id(9125467833), id(9125467848)}, grunhido = {id(9125467833), id(9125467848)}, alerta = id(9125467848),
			intimidar = {id(9113973520), id(9113973748)},
			dano = id(9113985598), danoLeve = id(9125467848),            -- Creature Roar Mix Of Animals 2 / Guttural 3
			farejar = {id(9119305209), id(9119305223)},  -- Sniff Breathe In 5 / 6
			respiroSono = id(9113971531), despertar = id(9113985604),    -- Lion 4 breathy lento (do Montanhas) / Creature Roar Mix 1
			beber = id(9120571917), mastigar = {id(9125467298), id(9125466463)},
			inspira = {id(9119305002), id(9119304904)},
			distVoz = 360, distRespiro = 90,
		},
		Glacial = {
			-- voz: felino grande grave/cansado (Lion "tired/pitched down", growls com "tubular ticking") — nao e o Montanhas
			rugido = id(9116306862),                     -- Lion Roar Tired 3: pitched down, large (territorial)
			rugidoCombate = id(9116302511),              -- Lion Roar Short Blast Attack Angry Sharp 4 (direcionado)
			intimidar = {id(9116303194), id(9116303929)}, -- Lion Roar Snarl Growl Inhale Exhale 1 / 8
			rugidoAmeaca = id(9116303194),               -- (03/11) ameaca do ninho: Snarl Growl 1 (forte ~1,2 s + cauda)
			esforco = {id(9125470306), id(9125470318), id(9125470377), id(9125470501)},   -- Lion Deep Guttural Rumbling 7/8/9/11
			grunhido = {id(9125470318), id(9125470377)}, alerta = id(9125470306),
			respiro = {id(9113971975), id(9113972744), id(9113973128)}, respiroVolume = 0.32, respiroTom = {0.62, 0.74},  -- Creature Growls Lion 6/20/8
			respiroSono = id(9113972534),                -- Creature Growls Lion 16: breathy lento (6,5 s)
			despertar = id(9116304872),                  -- Lion Roar Tired 12: distant, muffled (curto)
			dano = id(9125628981), danoLeve = id(9116304872),   -- Lion Roar Painful Bellow 5 / Tired 12
			farejar = {id(9119305128), id(9119305002)},  -- Sniff Breathe In 4 / 2
			beber = id(9120571904),                      -- Water Lapping Single Person 1 (trecho curto, tom baixo)
			mastigar = id(9113445183),                   -- Bite Ice Cube 1: crunch
			ataqueVoz = {id(9125629454), id(9125629224)}, -- Lion Roar Short Attack Lunge Jumping Fighting 5 / 2
			mordida = {id(9113445183)}, mordidaTom = {0.55, 0.65},
			garra = id(9125647922), garraVolume = 0.7,   -- Magic Zoom Up: golpe cortando o ar (tom baixo)
			avanco = id(9125647922),
			impacto = id(9114861568), impactoCorte = 0.5, -- Ice Cube Drops: golpe seco
			-- corpo: membrana pesada nas asas, neve compacta + garras nos passos
			asa = {id(9114461411), id(9114461597), id(9114461307)}, asaVolume = 1.0, asaTom = {0.4, 0.5},   -- Flag Flapping 3 (cloth)
			passo = {id(9125965053), id(9126274134), id(9126274119)}, passoTom = {0.62, 0.78}, passoVolume = 0.55, -- Snow Stomping / Paddle Into Icy Snow
			passoPeso = id(9119316414), passoPesoCorte = 0.4, passoPesoVolume = 0.42,   -- Snow Impact Big Hits Semi-Deep
			pouso = id(9119316414),
			-- vento do voo pela VELOCIDADE (laço; some ao pousar). No planeio so ha vento, sem batidas.
			ventoVoo = id(9125742262), ventoVooVolume = 0.55, ventoVooTom = {0.7, 1.15}, ventoVooVel = {4, 70},   -- voo livre: plena 20, mergulho ate 80 (ConfigMontaria)
			distVoz = 340, distRespiro = 80, distPasso = 140, distAsa = 200,
		},
	},
}
]=====], "SonsConfig do Studio difere do HEAD do git (nao troco)")
src = troca(src, [=====[	Rugido_Ameaca = {{0.30, "rugidoAmeaca", 1, 1.05, TOM_RUGIDO_FOGO}},
]=====], [=====[	Rugido_Ameaca = {{0.30, "rugidoAmeaca", 1, 1.05, 0.95}},                -- PATCH_VOZES_CAMADAS: tom por tipo
]=====])
src = troca(src, [=====[{0.36, "rugidoVitoria", 1, 1.0, TOM_RUGIDO_FOGO}]=====], [=====[{0.36, "rugidoVitoria", 1, 1.0, 0.88}]=====])
src = troca(src, [=====[	Ninho_Ameaca = {{0.34, "rugidoAmeaca", 1, 1.0, TOM_RUGIDO_FOGO}},
]=====], [=====[	Ninho_Ameaca = {{0.34, "rugidoAmeaca", 1, 1.0, 0.95}},
]=====])
src = troca(src, [=====[	Ninho_Ameaca = {{0.34, "rugidoAmeaca", 1, 1.0, 1.0}},   -- (03/11) uma tomada fixa e longa (o "intimidar" sorteava uma curta) Rugido_Territorial = {{0.3, "rugido", 1, 1.25, 1.0}},
]=====], [=====[	Ninho_Ameaca = {{0.34, "rugidoAmeaca", 1, 1.0, 1.0}},   -- (03/11) uma tomada fixa e longa (o "intimidar" sorteava uma curta)
	Rugido_Territorial = {{0.3, "rugido", 1, 1.25, 1.0}},   -- PATCH_VOZES_CAMADAS: antes ficava dentro do comentario acima
]=====])
src = troca(src, [=====[local VOZ_FORMA = {Montanhas = VOZ_MONTANHAS, Glacial = {
]=====], [=====[-- PATCH_VOZES_CAMADAS (05/11): Sombrio — tons por tipo (aprovados de ouvido); fases = as do Montanhas (mesmo sistema
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
local VOZ_FORMA = {Montanhas = VOZ_MONTANHAS, Sombrio = VOZ_SOMBRIO, Glacial = {
]=====])
src = troca(src, [=====[	rugidoTerritorial = 8, rugidoCorpo = 2, rugidoAmeaca = 4, rugidoAmeacaCorpo = 2, rugidoVitoria = 20, rosnado = 2.5, bafo = 3, inspira = 2}
]=====], [=====[	rugidoTerritorial = 8, rugidoCorpo = 2, rugidoAmeaca = 4, rugidoAmeacaCorpo = 2, rugidoVitoria = 20, rosnado = 2.5, bafo = 3, inspira = 2,
	rugidoCombate = 6}                                               -- PATCH_VOZES_CAMADAS
]=====])
src = troca(src, [=====[	inspira = 1.1, dano = 0.9, despertar = 1.4, intimidar = 1.8, rugido = 3.4}
]=====], [=====[	inspira = 1.1, dano = 0.9, despertar = 1.4, intimidar = 1.8, rugido = 3.4, rugidoCombate = 1.9}
]=====])
src = troca(src, [=====[local function sorteia(t) return type(t) == "table" and t[math.random(#t)] or t end
]=====], [=====[local function sorteia(t) return type(t) == "table" and t[math.random(#t)] or t end
-- PATCH_VOZES_CAMADAS (05/11): camadas da voz (SonsConfig.formas[..].camadas[k] = {{som, vol rel, tom rel, atraso}}):
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
]=====])
src = troca(src, [=====[				local varia = RUGIDOS[k] and 1 or (0.95 + math.random() * 0.1)      -- rugido: sempre o mesmo tom
				tocar(pp, sorteia(C[k]), vol, ev[5] * varia * tomVoz(pp), CORTE_VOZ[k], dist, ENVELOPE[k])
]=====], [=====[				-- PATCH_VOZES_CAMADAS: rugido varia pouco (+-3%) em volta do tom do tipo; o resto +-5%
				local varia = RUGIDOS[k] and (0.97 + math.random() * 0.06) or (0.95 + math.random() * 0.1)
				local tom = ev[5] * varia * tomVoz(pp)
				tocar(pp, sorteia(C[k]), vol, tom, CORTE_VOZ[k], dist, ENVELOPE[k])
				camadas(pp, C, k, vol, tom, CORTE_VOZ[k], dist)
]=====])
src = troca(src, [=====[								tocar(pp, C.passoPeso, C.passoPesoVolume * (nome == "Correr" and 1.4 or 1), 0.9 + math.random() * 0.2, C.passoPesoCorte, C.distPasso)
]=====], [=====[								if (C.passoPesoVolume or 0) > 0 then                 -- PATCH_VOZES_CAMADAS: 0 = sem baque
									tocar(pp, C.passoPeso, C.passoPesoVolume * (nome == "Correr" and 1.4 or 1), 0.9 + math.random() * 0.2, C.passoPesoCorte, C.distPasso)
								end
]=====])
src = troca(src, [=====[		elseif h == "Rugido" and f == "emissao" then tocar(pp, C.rugidoCombate or C.rugido, 1.5, 0.95 * tomVoz(pp), 1.9, C.distVoz, true) end
]=====], [=====[		elseif h == "Rugido" and f == "emissao" then
			local k = C.rugidoCombate and "rugidoCombate" or "rugido"; local tom = 0.95 * tomVoz(pp)
			tocar(pp, C[k], 1.5, tom, 1.9, C.distVoz, true); camadas(pp, C, k, 1.5, tom, 1.9, C.distVoz)   -- PATCH_VOZES_CAMADAS
		end
]=====])
assert(loadstring(src), "SonsDragao_Cliente nao compila")
local novoCfg = [=====[-- SonsConfig (ModuleScript) — audio dos dragoes. SO audio licenciado: biblioteca Pro Sound Effects publicada na Roblox
-- ("Courtesy of Pro Sound Effects", conta ProSoundEffects) e sons do proprio motor (rbxasset://). Nada copiado de jogos.
-- Volumes/tons provisorios (NAO_APROVADO). corte = segundos ate parar (trecho util de um arquivo longo).
local function id(n) return "rbxassetid://" .. n end
return {
	NAO_APROVADO = true,
	distMax = 260,
	-- PATCH_RUGIDO_SEM_ATRASO (02/11): segundo do arquivo em que o rugido fica AUDIVEL (RMS medido com AudioAnalyzer no
	-- Studio). Varias tomadas comecam quase em silencio (ate 1,1 s) e a boca abria antes do som: o mixer comeca o som
	-- nesse ponto (TimePosition) e encurta o corte na mesma medida (o fim do arquivo continua o mesmo).
	inicioAudivel = {
		["9126100408"] = 0.22, ["9126100484"] = 0.47, ["9126100903"] = 1.02, ["9126100708"] = 1.17, ["9126100618"] = 0.92,  -- Fogo
		["9113973520"] = 0.32, ["9113973748"] = 0.52, ["9113985445"] = 0.75,                                                -- Fogo (intimidar, padrao)
		["9116306862"] = 1.00, ["9116302511"] = 0.04, ["9116303194"] = 0.25, ["9116303929"] = 0.92, ["9116300504"] = 0.32,  -- Glacial
		["9116304872"] = 0.07,
		-- PATCH_VOZES_CAMADAS (05/11): Sombrio, camadas de Fogo/Gelo e asa de membrana (RMS medido no Studio)
		["9120047949"] = 0.19, ["9120049293"] = 0.19, ["9120043128"] = 0.26, ["9120038597"] = 0.15, ["9125989548"] = 0.45,  -- Sombrio
		["9114535371"] = 0.34, ["9117733732"] = 0.06,
		["9117357645"] = 0.17, ["9117357818"] = 0.25, ["9117357829"] = 0.30,                                                -- camadas Fogo
		["9114858583"] = 0.10, ["9114858761"] = 0.15, ["9114858588"] = 0.36,                                                -- camadas Gelo
		["9125714705"] = 0.26,                                                                                              -- asa
	},
	-- PATCH_VOZES_CAMADAS (05/11, usuario: asas e passos "mais tranquilos"): asa = swish de membrana grave e suave; passo =
	-- pata acolchoada abafada; sem baque de pedra por baixo (passoPesoVolume 0). Valem para todas as formas (o Glacial
	-- troca so os passos, por neve). Antes: Wing Flaps 27/1 (0,9) e passo de plastico + Rock Impacts.
	asa = {id(9125714705)},                          -- Ninja Robe Swish Cloth Flaps 13 (SFX), comeca em 0,26 s
	asaVolume = 2.2, asaTom = {0.5, 0.58},
	passo = {id(9113532211), id(9113532682)}, passoTom = {0.42, 0.5}, passoVolume = 3.2,   -- Body Pat Muted 7 / 14 (SFX)
	passoPeso = id(9118633669), passoPesoCorte = 0.35, passoPesoVolume = 0,      -- Rock Impacts (desligado)
	mordida = {id(9125467298), id(9125466463)},   -- Creature Bite Pterodactyl Crunch (SFX)
	mordidaTom = {0.7, 0.85},
	avanco = id(9126229255),                         -- Whoosh By Fast Airy Swooshing (SFX)
	fogo = id(9114463219),                           -- Flame Licks 8 (SFX)
	ar = id(9125805579),                             -- Rising Whoosh Hissing Build Up (SFX)
	rocha = id(9118633669), rochaArrasto = id(9125881604),   -- Rock Impacts / Rock Scrape (SFX)
	rugido = id(9113985445),                         -- Creature Roar Deep Throaty Growls 2 (SFX)
	respiro = id(9113971531), respiroVolume = 0.35, respiroTom = {0.55, 0.7},   -- Creature Growls Lion 4: Deep Quiet Breathy (SFX)
	respiroIntervalo = {7, 15},                      -- segundos entre respiracoes audiveis (parado/andando), nunca regular
	esforco = id(9125467848), esforcoVolume = 0.55,  -- Creature Growls Lion Deep Guttural Rumbling (SFX): esforco curto
	garra = id(9119228132), garraVolume = 0.9,       -- Slow Whoosh Beefy Airy Pass By 5 (SFX): deslocamento do golpe
	impacto = id(9118633669), impactoCorte = 0.3,    -- Rock Impacts Deep Crunchy: so quando ACERTA
	maxSimultaneos = 6,                              -- por dragao (evita sobreposicao)
	-- PATCH_AUDIO_GELO (02/11): perfil PROPRIO por forma regional (atributo FormaRegional). O que nao estiver aqui cai
	-- no padrao acima (Montanhas). Alcance por categoria (dist*): voz longe, respiracao perto.
	formas = {
		-- PATCH_RUGIDOS_FOGO (02/11): voz do Dragao das Montanhas — agressiva, rouca e dominante (familia Creature Roar /
		-- Giant Crab Monster / Pit Bull snarl); NADA da familia Lion usada no Glacial. So as chaves de VOZ; o resto herda.
		Montanhas = {
			-- (05/11, usuario: "variacoes igual ao do Sombrio") rugidos em CAMADAS (ver camadas) e tom proprio por tipo no
			-- cliente; substitui a regra de 02/11 abaixo (um som so e mesmo tom).
			-- usuario 02/11: UM som por rugido, mesmo tom em todos, mas cada tipo com a SUA tomada; o arquivo anterior (Deep
			-- Throaty Growls, rebaixado) soava "engasgado" -> familia Thunder With Lion Roar (Growl, Low Rumble, Roar), limpa,
			-- grave e com ronco por baixo (sem as variantes com estalo eletrico)
			rugidoTerritorial = id(9126100903),          -- Thunder With Lion Roar Growl Low Rumble Roar 14 (4,2 s)
			rugidoAmeaca = id(9126100484),               -- idem 8 (3,1 s)
			rugidoVitoria = id(9126100708),              -- idem 13 (3,8 s)
			rugidoCombate = id(9126100484),              -- (05/11) idem 8, curto e mais agudo (tom no cliente)
			-- camadas = {[voz] = {{som, volume relativo, tom relativo, atraso s}}}: tocam junto com a voz principal (mesma
			-- garganta: varios animais misturados, como no Sombrio). Fogo: grunhido grave de javali rebaixado + chama no fim.
			camadas = {
				rugidoTerritorial = {{id(9117357645), 0.5, 0.76}, {id(9114463219), 0.3, 0.76, 2.2}},   -- Pig Grunts 3 / Flame Licks 8
				rugidoAmeaca = {{id(9117357818), 0.57, 0.76}},                                     -- Pig Grunts 4
				rugidoCombate = {{id(9117357829), 0.5, 0.77}},                                     -- Pig Grunts 5
				rugidoVitoria = {{id(9117357645), 0.45, 0.75}},                                    -- Pig Grunts 3
			},
			rosnado = {id(9113973520), id(9113973748), id(9113973436)},   -- Creature Growls Pit Bull 4 / 3 / 1: snarl agressivo
			bafo = id(9114431819),                       -- Fire Burst 6: ascending air release (calor na expiracao, baixo)
			esforco = {id(9125467833), id(9125467848)}, grunhido = {id(9125467833), id(9125467848)}, alerta = id(9125467848),
			intimidar = {id(9113973520), id(9113973748)},
			dano = id(9113985598), danoLeve = id(9125467848),            -- Creature Roar Mix Of Animals 2 / Guttural 3
			farejar = {id(9119305209), id(9119305223)},  -- Sniff Breathe In 5 / 6
			respiroSono = id(9113971531), despertar = id(9113985604),    -- Lion 4 breathy lento (do Montanhas) / Creature Roar Mix 1
			beber = id(9120571917), mastigar = {id(9125467298), id(9125466463)},
			inspira = {id(9119305002), id(9119304904)},
			distVoz = 360, distRespiro = 90,
		},
		Glacial = {
			-- voz: felino grande grave/cansado (Lion "tired/pitched down", growls com "tubular ticking") — nao e o Montanhas
			rugido = id(9116306862),                     -- Lion Roar Tired 3: pitched down, large (territorial)
			rugidoCombate = id(9116302511),              -- Lion Roar Short Blast Attack Angry Sharp 4 (direcionado)
			intimidar = {id(9116303194), id(9116303929)}, -- Lion Roar Snarl Growl Inhale Exhale 1 / 8
			rugidoAmeaca = id(9116303194),               -- (03/11) ameaca do ninho: Snarl Growl 1 (forte ~1,2 s + cauda)
			-- (05/11) camadas de gelo rachando por baixo da voz (gelo de verdade como textura)
			camadas = {
				rugido = {{id(9114858583), 0.37, 1.06}},          -- Ice Crackle Large Block Cracks 1
				rugidoAmeaca = {{id(9114858761), 0.5, 1.1}},      -- Ice Cracks 2
				rugidoCombate = {{id(9114858588), 0.45, 1.11}},   -- Ice Crackle Large Block Cracks 3
				intimidar = {{id(9114858583), 0.33, 1.3}},
			},
			esforco = {id(9125470306), id(9125470318), id(9125470377), id(9125470501)},   -- Lion Deep Guttural Rumbling 7/8/9/11
			grunhido = {id(9125470318), id(9125470377)}, alerta = id(9125470306),
			respiro = {id(9113971975), id(9113972744), id(9113973128)}, respiroVolume = 0.32, respiroTom = {0.62, 0.74},  -- Creature Growls Lion 6/20/8
			respiroSono = id(9113972534),                -- Creature Growls Lion 16: breathy lento (6,5 s)
			despertar = id(9116304872),                  -- Lion Roar Tired 12: distant, muffled (curto)
			dano = id(9125628981), danoLeve = id(9116304872),   -- Lion Roar Painful Bellow 5 / Tired 12
			farejar = {id(9119305128), id(9119305002)},  -- Sniff Breathe In 4 / 2
			beber = id(9120571904),                      -- Water Lapping Single Person 1 (trecho curto, tom baixo)
			mastigar = id(9113445183),                   -- Bite Ice Cube 1: crunch
			ataqueVoz = {id(9125629454), id(9125629224)}, -- Lion Roar Short Attack Lunge Jumping Fighting 5 / 2
			mordida = {id(9113445183)}, mordidaTom = {0.55, 0.65},
			garra = id(9125647922), garraVolume = 0.7,   -- Magic Zoom Up: golpe cortando o ar (tom baixo)
			avanco = id(9125647922),
			impacto = id(9114861568), impactoCorte = 0.5, -- Ice Cube Drops: golpe seco
			-- corpo: membrana pesada nas asas, neve compacta + garras nos passos
			-- (05/11) asas = membrana suave do padrao; passos = Dragon Footsteps na neve (foley suave), sem baque por baixo.
			-- Antes: Flag Flapping 3 (1,0) e Snow Stomping (0,55) + Snow Impact Big Hits (0,42).
			passo = {id(9114165338), id(9114166974), id(9114165461)}, passoTom = {0.8, 0.9}, passoVolume = 8,   -- Dragon Footsteps 2/31/5 (Snow)
			passoPeso = id(9119316414), passoPesoCorte = 0.4, passoPesoVolume = 0,   -- Snow Impact Big Hits (desligado)
			pouso = id(9119316414),
			-- vento do voo pela VELOCIDADE (laço; some ao pousar). No planeio so ha vento, sem batidas.
			ventoVoo = id(9125742262), ventoVooVolume = 0.55, ventoVooTom = {0.7, 1.15}, ventoVooVel = {4, 70},   -- voo livre: plena 20, mergulho ate 80 (ConfigMontaria)
			distVoz = 340, distRespiro = 80, distPasso = 140, distAsa = 200,
		},
		-- PATCH_VOZES_CAMADAS (05/11, aprovado de ouvido pelo usuario): voz do Dragao Sombrio — tigre grave + rosnado oco de
		-- espirito por baixo; corpo = padrao calmo (membrana / pata acolchoada). Tons por tipo no cliente (VOZ_FORMA.Sombrio).
		Sombrio = {
			rugidoTerritorial = id(9120047949),          -- Tiger Roars 6 (3,2 s)
			rugidoAmeaca = id(9120049293), rugidoCombate = id(9120049293),   -- Tiger Roars 6 (outra tomada)
			rugido = id(9120047949),
			intimidar = id(9120043128),                  -- Tiger Hiss
			esforco = id(9120038597), grunhido = id(9120038597), alerta = id(9120038597),   -- Tiger Growls 2
			respiro = id(9114535371), respiroVolume = 0.4, respiroTom = {0.66, 0.74},       -- Frightened Ox 2
			dano = id(9117733732), danoLeve = id(9117733732),                               -- Polar Bear 1
			camadas = {
				rugidoTerritorial = {{id(9125989548), 0.55, 1.04}},   -- Spirit Whoosh Airy Growl
				rugidoAmeaca = {{id(9120043128), 0.43, 0.9}},         -- Tiger Hiss
				rugidoCombate = {{id(9125989548), 0.4, 1.06}},
				rugido = {{id(9125989548), 0.55, 1.04}},
			},
			distVoz = 360, distRespiro = 90,
		},
	},
}
]=====]
assert(loadstring(novoCfg), "SonsConfig nao compila")
if not SS:FindFirstChild("Backup_Vozes_Camadas_2026-11-05") then local f = Instance.new("Folder"); f.Name = "Backup_Vozes_Camadas_2026-11-05"; C:Clone().Parent = f; K:Clone().Parent = f; f.Parent = SS end
C.Source = src; K.Source = novoCfg
return "aplicado: SonsDragao_Cliente (" .. #src .. " bytes) + SonsConfig (" .. #novoCfg .. " bytes)"
