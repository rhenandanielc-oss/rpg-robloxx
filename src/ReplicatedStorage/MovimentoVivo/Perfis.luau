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
	},
}
