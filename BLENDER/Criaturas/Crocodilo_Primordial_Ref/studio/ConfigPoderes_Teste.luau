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
		rigido_max = 6,                     -- 19/11: alvo com mais de 6 studs = PONTO DE MORDIDA (osso mais perto dos dentes), corpo fica em pe e e arrastado
		giro_corpo = 2.5,                   -- rad/s: o corpo arrastado vira para ficar atras da mordida (sem girar inteiro com a mandibula)
		profundidade_agua = 0.85,           -- agua: desce da altura de nado para a de espreita (render R2: agua 5,15 x 4,3)
	},
	AgarraoPvP = {                          -- 19/11 numeros APROVADOS pelo usuario [A TESTAR]; boneco com PvP=true simula criatura de jogador
		duracao = 2.5,                      -- s presa, do contato ao fim (agarrao + giro somados); PvE continua `Agarrao.sustentacao`
		colossal_lentidao = 0.5, colossal_dur = 1.5,   -- Porte=colossal: morde um membro, 50% lentidao, sem saltar/decolar
		soltar_pct = 0.08, boca_aberta = 0.6,          -- aliados: dano no croc >= 8% da vida (ou golpe pesado) solta; boca aberta 0,6 s
		golpe_vitima = 0.3, golpe_vitima_max = 1.0,    -- cada golpe da vitima na cabeca tira 0,3 s (max 1,0)
		imune = 8, reduz_janela = 4, reduz = 0.5,      -- solta: 8 s imune a agarrao; controle nos 4 s seguintes dura 50%
		forca_idade = {Filhote = 0.3, Jovem = 0.55, ["Pre-adulto"] = 0.8, Adulto = 1.0, Anciao = 1.1},   -- atributo Idade do croc
		pulo_atraso = 0.10, pulo_dur = 0.30, pulo_altura = 3,   -- vitima montada: o cavaleiro pula antes da mordida (usuario 19/11) [PROPOSTA de tempo]
		aviso_raio = 60, ir_max = 6,        -- 19/11 usuario: opcao "Soltar aliado" para aliados a ate 60 studs; a acao dura no maximo 6 s [PROPOSTA]
		soco_alcance = 8, soco_parar = 4.5, soco_intervalo = 0.55, soco_dano = 40,   -- golpe do jogador no crocodilo (dano de TESTE; o real vem do combate do jogador)
		pulo_lado = 5, pulo_recuo = 1.5,    -- 19/11 usuario "pular mais perto": cai AO LADO da cabeca do crocodilo (5 de lado, 1,5 atras do focinho), ja no alcance para bater
	},
	Giro = {voltas = 2, dano_por_volta = 8, ativo = false},   -- 19/11 usuario: Rolar da Morte REMOVIDO do kit (codigo guardado; ativo=false recusa)
	Vibracao = {                            -- 19/11 usuario: passiva Sentido de Vibracao [PROPOSTA de numeros]
		raio_agua = 40, raio_margem = 20, margem = 10,   -- na agua 40; em terra so a ate 10 studs da agua, raio 20
		vel_min = 1.5, vel_max = 60,        -- so quem se move (studs/s); parado nao vibra; acima de 60 = teletransporte, ignora
		intervalo = 0.25,                   -- s entre leituras do servidor
	},
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
