-- MovimentoVivo_Perfis (ModuleScript, ReplicatedStorage.MovimentoVivo.Perfis) — camada dinamica de movimento por
-- rig. Cada criatura com o atributo PerfilMovimento = "<nome>" usa o perfil abaixo. So VISUAL (cliente): somada por
-- cima das animacoes a cada quadro, reagindo ao movimento REAL do modelo (giro, subida/descida, aceleracao) e ao olhar
-- do cavaleiro. Angulos em graus; ganhos em graus por (rad/s) de giro, por grau de trajetoria ou por (stud/s2).
-- Referencia de fluidez: jogos de montaria (Dragon Adventures) — so principios, nada copiado.
return {
	Silverwing = {
		pescoco = {"Pescoco2", "spine_3", "Pescoco4"}, cabeca = "Cabeca",
		divPescoco = {0.3, 0.35, 0.35},                   -- como o giro do pescoco se distribui pelos ossos
		coluna = {"Coluna2", "spine_0"}, divColuna = {0.6, 0.4},
		cauda = {"tail_1", "tail_2", "Cauda3", "tail_4", "tail_5", "tail_6", "tail_tip"},
		ombros = {E = "shoulder_l", D = "shoulder_r"},
		patasD = {"front_leg_l", "front_leg_r"}, patasT = {"back_leg_l", "back_leg_r"},
		-- curvas: o pescoco/cabeca "puxam" para dentro da curva, a coluna dobra, a cauda abre para FORA com atraso
		curvaPescoco = 70, curvaCabeca = 20, curvaColuna = 24, curvaCauda = 15,   -- por segmento da cauda
		maxPescoco = 55, maxColuna = 22, maxCaudaSeg = 17,
		-- subida/descida (grau da trajetoria): pescoco acompanha mais que o corpo, cauda compensa
		trajPescoco = 0.55, trajCauda = -0.25, maxTraj = 32,
		-- aceleracao (stud/s2): patas ficam para tras acelerando e vem para frente freando; torax reage
		acelPatas = 1.6, acelTorax = 0.5, maxAcel = 28,
		-- asa interna da curva baixa/fecha um pouco, externa sobe (so no ar)
		curvaAsa = 24, maxAsa = 22, sinalAsa = 1,
		-- olhar: montado segue a camera do cavaleiro; solto e parado olha jogadores proximos
		olharYaw = 0.55, olharPitch = 0.4, maxOlharYaw = 45, maxOlharPitch = 22, olharDist = 70,
		-- molas (rigidez; a cauda vai ficando mais 'mole' para a ponta = atraso natural)
		molaPescoco = 30, molaCabeca = 45, molaColuna = 22, molaCauda = {18, 14, 11, 9, 7.5, 6.5, 6}, molaPatas = 16, molaAsa = 20,
		distMax = 320,                                    -- acima disto (camera) nao calcula
		-- PATCH_PES_IK: IK de 2 ossos por perna {coxa, canela, pe, ponta dos dedos}; so levanta pe que entraria no chao
		pesIK = {
			{"front_leg_l", "front_ankle_l", "front_foot_l", "front_toes_tip_l"}, {"front_leg_r", "front_ankle_r", "front_foot_r", "front_toes_tip_r"},
			{"back_leg_l", "back_ankle_l", "back_foot_l", "back_toes_tip_l"}, {"back_leg_r", "back_ankle_r", "back_foot_r", "back_toes_tip_r"},
		},
		pesFolga = 0.15, pesMax = 5, pesSonda = 12, pesDist = 160,   -- studs
		pesDobraMax = 150,                                -- graus: joelho nunca dobra mais que isso pelo IK
	},
	-- Wyvern (12/11): rig proprio (base Ashwing, 61 ossos; bipede, asa-braco). Mesmos principios do Silverwing com
	-- pescoco de 5 ossos e cauda de 10 (ganho por segmento menor). Coluna SEM o Coluna2 (osso da sela: o cavaleiro segue
	-- esse osso). Sem patas dianteiras (as maos sao da asa). IK so nas 2 pernas: coxa -> canela, metatarso (foot) mantem a
	-- orientacao do clipe, sonda na base dos dedos (toes_tip_*). Valores = ponto de partida visual (nao aprovados).
	Wyvern = {
		pescoco = {"neck_01", "Pescoco2", "neck_03", "Pescoco4", "neck_05"}, cabeca = "Cabeca",
		divPescoco = {0.14, 0.18, 0.2, 0.22, 0.26},
		coluna = {"spine_01", "spine_03"}, divColuna = {0.45, 0.55},
		cauda = {"tail_01", "tail_02", "Cauda3", "tail_04", "tail_05", "tail_06", "tail_07", "tail_08", "tail_09", "tail_tip"},
		ombros = {E = "shoulder_l", D = "shoulder_r"},
		patasD = {}, patasT = {"thigh_L", "thigh_R"},
		curvaPescoco = 70, curvaCabeca = 20, curvaColuna = 20, curvaCauda = 10,
		maxPescoco = 55, maxColuna = 18, maxCaudaSeg = 12,
		trajPescoco = 0.55, trajCauda = -0.2, maxTraj = 32,
		acelPatas = 1.2, acelTorax = 0.5, maxAcel = 22,
		curvaAsa = 26, maxAsa = 24, sinalAsa = 1,
		olharYaw = 0.55, olharPitch = 0.4, maxOlharYaw = 45, maxOlharPitch = 22, olharDist = 60,
		molaPescoco = 32, molaCabeca = 48, molaColuna = 24, molaCauda = {20, 17, 14, 12, 10.5, 9, 8, 7.2, 6.6, 6}, molaPatas = 16, molaAsa = 22,
		distMax = 300,
		pesIK = {{"thigh_L", "calf_L", "foot_L", "toes_tip_l"}, {"thigh_R", "calf_R", "foot_R", "toes_tip_r"}},
		pesFolga = 0.15, pesMax = 4, pesSonda = 10, pesDist = 160, pesDobraMax = 150,
	},
}
