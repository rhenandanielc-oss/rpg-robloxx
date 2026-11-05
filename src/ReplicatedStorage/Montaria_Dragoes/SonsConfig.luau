-- SonsConfig (ModuleScript) — audio dos dragoes. SO audio licenciado: biblioteca Pro Sound Effects publicada na Roblox
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
