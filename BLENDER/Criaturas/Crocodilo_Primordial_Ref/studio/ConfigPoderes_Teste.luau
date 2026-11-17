-- ConfigPoderes_Teste (ModuleScript em ServerStorage.Crocodilo_Piloto) - VALORES PROVISORIOS SO DO PLACE DE TESTE.
-- [PROPOSTA] Nenhum destes numeros e regra do jogo: elemento, passiva, kit, dano, recarga e a regra do agarrao PvP do
-- Crocodilo Primordial continuam PENDENTES (decisao do criador). Agarrao e efeitos so valem para bonecos BonecoTeste.
return {
	SoBonecos = true,                       -- trava: alvo precisa ter o atributo BonecoTeste (nunca jogadores)
	Agarrao = {
		alcance = 6.5,                      -- studs da PONTA DOS DENTES ate o centro do boneco no contato
		ponta = 4.5,                        -- ponta dos dentes = 4,5 a frente do osso Mandibula (+Y do osso)
		sustentacao = 3.5,                  -- s segurando antes de soltar (usuario 16/11: 3,5 s por enquanto)
		dano_contato = 10, dano_por_segundo = 4,
		profundidade_agua = 0.85,           -- agua: desce da altura de nado para a de espreita (render R2: agua 5,15 x 4,3)
	},
	Giro = {voltas = 2, dano_por_volta = 8},
	GiroEmboscada = {                       -- P4 16/11 (ref. secao 4: Giro 2,0x a mordida 20, raio 12, derruba 1,5 s, +50% distraido; raso 1,2x)
		janela = 1.5, mult = 2.0, mult_raso = 1.2, bonus_distraido = 1.5, dano_base = 20,
		raio = 12, derruba = 1.5, distancia = 22, voo = 0.9, altura = 5, centro_frente = 6,
	},
	Submersao = {                           -- P4 16/11 (agua real; numeros de TESTE)
		folga_topo = 4.0, folga_fundo = 1.0, -- topo do corpo abaixo da superficie / sola acima do fundo (P4b: usuario achou raso 1,5)
		extra_montado = 3.5,                 -- P4b: com cavaleiro afunda mais (usuario 16/11); mergulho montado = decisao do criador
		deteccao = 12, cone = 40, subida_bote = 0.3, deriva = 3.0, parar_antes = 0.5, investida_max = 14, bote_abaixo = 2.0,   -- P4b: presa a frente da cabeca -> sobe rapido e bote; errou = nada adiante
		espreita = 0.8, descida = 0.5, subida = 0.6,   -- s (ref. 5.9: afunda em 0,5 s)
		velocidade = 10, vel_clipe = 1.3,    -- studs/s submerso (proposta: nado 8 x 1,25) e velocidade do clipe
		distancia = 50, olhar_frente = 18,   -- percurso maximo e onde mede a profundidade a frente (cabeca ~16)
		energia_s = 5, energia_teste = 100,  -- ref. secao 4: 5 de energia/s
		tempo_terra = 4.0,                   -- variante em terra (postura baixa)
		profundidade = 2.4,                  -- [P3] so a arena antiga (placa visual)
	},
	Corpo = {pivo = 2.87, olhos = 5.0, topo = 5.74, cabeca = 16, ponta_bote = 13.8},   -- alturas acima da sola (medidas: Studio e malha no Blender)
	Cauda = {raio = 11, empurrao = 9, dano = 20,   -- P4: dano 1,0x a mordida (ref. 4); acerto pela TRAJETORIA da cauda
		largura = 3.0, empurrao_agua = 9, empurrao_terra = 5, onda_agua = 14, onda_terra = 8, proposto_graus = 360},
	Escamas = {reducao = 0.15, vida = 950, recuo_terra = 0.8, recuo_agua = 2.0},   -- P4: passiva -15% dano fisico (ref. 4); recuo de TESTE
	AlturaAgua = 4.3,                       -- placa de agua so visual (teste)
}
