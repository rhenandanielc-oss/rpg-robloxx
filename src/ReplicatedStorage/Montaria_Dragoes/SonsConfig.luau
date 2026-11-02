-- SonsConfig (ModuleScript) — audio dos dragoes. SO audio licenciado: biblioteca Pro Sound Effects publicada na Roblox
-- ("Courtesy of Pro Sound Effects", conta ProSoundEffects) e sons do proprio motor (rbxasset://). Nada copiado de jogos.
-- Volumes/tons provisorios (NAO_APROVADO). corte = segundos ate parar (trecho util de um arquivo longo).
local function id(n) return "rbxassetid://" .. n end
return {
	NAO_APROVADO = true,
	distMax = 260,
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
