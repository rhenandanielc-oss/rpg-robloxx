-- ConfigPoderes_Teste (ModuleScript em ServerStorage.Crocodilo_Piloto) - VALORES PROVISORIOS SO DO PLACE DE TESTE.
-- [PROPOSTA] Nenhum destes NUMEROS e regra do jogo (dano, recarga, alcances: provisorios). OFICIAL desde 20/11: elemento
-- Agua, ativas Agarrao/Giro de Emboscada/Submersao/Cauda de Mare, passivas Escamas Grossas/Sentido de Vibracao e a
-- regra do agarrao PvP (19/11). Agarrao e efeitos so valem para bonecos BonecoTeste.
return {
	SoBonecos = true,                       -- trava: alvo precisa ter o atributo BonecoTeste (nunca jogadores)
	Elemento = "Agua",                      -- 20/11 KIT OFICIAL (usuario): elemento unico Agua; dano das 4 ativas e de Agua (visual natural, sem brilho)
	Agarrao = {
		alcance = 6.5,                      -- studs da PONTA DOS DENTES ate o centro do boneco no contato
		ponta = 4.5,                        -- ponta dos dentes = 4,5 a frente do osso Mandibula (+Y do osso)
		sustentacao = 3.5,                  -- s segurando antes de soltar (usuario 16/11: 3,5 s por enquanto)
		dano_contato = 10, dano_por_segundo = 4,
		cone_frontal = 20, estalo_frontal = 0.38, virar_vel = 45, cone_virar = 30, peso_alto = 3, bote_frontal = 0.9,   -- 20/11 movimento natural [PROVISORIO]: bote frontal ate 20 graus; vira com as patas a 45 graus/s se a presa passar de 30; alvo em pe: +3 de custo por stud acima da faixa baixa
		altura_lado = 1.9,                  -- 20/11 encaixe: regiao a ate 1,9 do chao = MORDIDA DE LADO (cabeca baixa e girada); acima = boca normal
		subir_agua = 5.0,                   -- 20/11: na agua o corpo pode SUBIR ate 5 para a boca alcancar a presa na superficie (bote vindo do fundo)
		corrigir_agarrao = 1.5, corrigir_final = 3.0,   -- quanto o corpo do croc pode se ajustar para centralizar a boca na regiao (studs)
		revalidar = 0.5,                    -- s entre revalidacoes da pegada (espessura x vao) enquanto segura
		cravar = 0.4,                       -- 20/11 r2 usuario: dentes cravam ~0,4 studs no corpo (arcadas fecham alem da espessura)
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
	Arremesso = {                           -- 20/11 r2 usuario: ao soltar, sacudida de cabeca DE LADO e a presa voa ~8 studs, cai e levanta
		distancia = 8, altura = 2.5, voo = 0.7,          -- studs do ponto de soltura ate a queda; altura do arco; s no ar
		giro = 20, giro_dur = 0.22, volta_dur = 0.5,     -- SEM o clipe: graus de sacudida do corpo inteiro (acelera e solta no fim); volta ao rumo
		giro_clipe = 6, solta_clipe = 0.44,              -- r3 COM o clipe ArremessarPresaE/D (usuario: arma e chicoteia; corpo gira ~6 graus); evento solta 0,44 s
		lateral = 0.85, frente = 0.5,                    -- direcao do lancamento: mais para o lado que para a frente
		queda = 1.5,                                     -- PvE: fica caida 1,5 s e levanta (sem dano na queda)
		pvp_fator = 0.5, pvp_queda = false,              -- PvP: metade da distancia e NAO derruba (contrato: nao somar agarrao e queda)
		agua = false,                                    -- na agua so solta (sem arremesso) [PROPOSTA]
	},
	Montaria = {                            -- 20/11 1a entrega (usuario): botao Montar [E], controle pela camera, nada na superficie [PROPOSTA de numeros]
		raio = 12,                          -- studs do botao (ProximityPrompt) na sela
		subida = 4.0, descida = 3.6,        -- s = duracao dos clipes Montar/Desmontar (E/D)
		altura_hrp = 2.3, altura_chao_hrp = 3.0, lado_x = 6.0, lado_z = -4.0,   -- HRP sobre o assento; ponto de descida ao lado da sela
		timeout = 0.6,                      -- s sem pacote do cliente = solta o comando
		junta_inicio = 0.35,                -- r2: s para juntar a posicao do jogador ao comeco do caminho do Blender
		vel_andar = 2.8, vel_andar_clipe = 1.85,       -- Andar tocado 1,5x (clipe 1,85 studs/s: lento demais para montaria)
		vel_corrida = 8.75, vel_corrida_clipe = 8.75,  -- velocidade do proprio clipe (patas casadas)
		vel_nado = 8, nado_rapido = 1.3,    -- nado na superficie (Shift: 1,3x)
		acel = 5, acel_nado = 4, frear = 9, -- studs/s2
		giro_parado = 60, giro_andar = 70, giro_corrida = 45, giro_nado = 55,   -- graus/s (vira com peso)
		nado_extra = 0.4,                   -- nada 0,4 acima da altura de espreita (sela fora d'agua)
		degrau_max = 2.5, subida_s = 8,     -- maior degrau que sobe de uma vez; velocidade vertical maxima no relevo
	},
	-- 20/11 REGRAS DO LOBO ADOTADAS NO CROCODILO (usuario: "faca da mesma maneira"); contrato geral em
	-- BLENDER/Criaturas/Lobo_Ancestral_Ref/studio/kit/CONTRATO-CONTROLE-PORTE.md. Regras oficiais v6.2 §0b-0d; resto [A TESTAR].
	Hitbox = {                              -- golpes medidos da PONTA DOS DENTES / da cauda ate a SUPERFICIE do corpo (nao ao centro)
		ignorarOssos = {"Cauda", "Tail", "Pelo", "Juba", "Orelha", "Palpebra", "Olho", "Ear", "Fur", "Hair", "Raiz", "Root"},
		raioGenerico = 0.22,                -- corpo com ossos = capsulas osso->pai, raio = menor lado da caixa x 0,22 (como no Lobo)
		contatoMordida = 1.5, contatoCauda = 1.0, -- tolerancia (studs) entre o ponto de ataque e a superficie
	},
	Controle = {
		porte = {comprimento = 28, forca = 60},            -- Crocodilo Adulto: comprimento 28 / 2,5 = 11,2 = GRANDE; Forca 60 (contrato §5)
		tamanhoIdade = {Filhote = 0.40, Jovem = 0.65, ["Pre-adulto"] = 0.85, Adulto = 1.0, Anciao = 1.10},
		forcaIdade = {Filhote = 0.30, Jovem = 0.55, ["Pre-adulto"] = 0.80, Adulto = 1.0, Anciao = 1.10},
		classes = {{"pequeno", 3}, {"medio", 8}, {"grande", 16}, {"colossal", math.huge}},
		golpes = {CaudaDeMare = {impacto = 1.2}, GiroEmboscada = {impacto = 1.6, derrubaSempre = true}},   -- agarrao NAO derruba (contrato: nao somar agarrao e queda)
		porteRelativo = {[-3] = 0.05, [-2] = 0.2, [-1] = 0.55, [0] = 1.0, [1] = 1.3, [2] = 1.6, [3] = 1.8},
		forcaMinMax = {0.35, 1.5},
		lento = {chance = 0.30, fracao = 0.25, dur = 1.5}, manca = {chance = 0.14, fracao = 0.45, dur = 2.0, impactoMin = 1.0},
		queda = {chance = 0.16, impactoMin = 1.6, intervaloMin = 4.0},   -- 4 s DE PE (contados do fim do levantar) entre quedas
		duracaoPorte = {pequeno = 1.15, medio = 1.0, grande = 0.8, colossal = 0.5},
		pvp = {fatorDur = 0.5, janela = 12, maxSeguidos = 2, imuneSeg = 8},
	},
	Finalizacao = {                         -- 20/11 usuario: finalizacao PROPRIA DO CROCODILO = MORDIDA ESMAGADORA
		anuncio = 0.9, abordarAte = 14, vel = 7, giro = 3.0, encostar = 0.4, abordarMax = 3.0,   -- sibilo, aproxima ate os dentes ENCOSTAREM no corpo
		aperto = 1.8, danoCrava = 5,        -- 20/11 r2: segura o corpo e o clipe MordidaEsmagadora (1,8 s) crava 2x; corpo firme, sem girar
		vidaAlvoMax = 0.35, vidaPropriaMin = 0.30, ameacaRaio = 25,   -- IA: so finaliza alvo enfraquecido; poupa se fraco ou com outro inimigo perto
		ossosAlvo = {"Cabeca", "Pescoco", "Head", "Neck"},
	},
	Giro = {voltas = 2, dano_por_volta = 8, ativo = false},   -- 19/11 usuario: Rolar da Morte REMOVIDO do kit (codigo guardado; ativo=false recusa)
	Vibracao = {                            -- 19/11 usuario: passiva Sentido de Vibracao [PROPOSTA de numeros]
		raio_agua = 40, raio_margem = 20, margem = 10,   -- na agua 40; em terra so a ate 10 studs da agua, raio 20
		vel_min = 1.5, vel_max = 60,        -- so quem se move (studs/s); parado nao vibra; acima de 60 = teletransporte, ignora
		intervalo = 0.25,                   -- s entre leituras do servidor
	},
	GiroEmboscada = {                       -- P4 16/11 (ref. secao 4: Giro 2,0x a mordida 20, raio 12, derruba 1,5 s, +50% distraido; raso 1,2x)
		janela = 1.5, mult = 2.0, mult_raso = 1.2, bonus_distraido = 1.5, dano_base = 20,
		-- 20/11 EMBOSCADA SEM GIRO (usuario): bote saltando curto e baixo; mordida no pouso a `raio` da ponta do focinho
		raio = 4.5, derruba = 3.0, distancia = 12, voo = 0.55, altura = 3, centro_frente = 15.5,   -- [PROPOSTA]; antes 12/22/0,9/5/6 (giro em area)
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
		largura = 3.0, empurrao_agua = 9, empurrao_terra = 5, onda_agua = 20, onda_terra = 20,   -- r2 usuario 20/11: 'a onda deve chegar mais longe' (antes 14/8); r3 terra 10 -> 15 -> 20 ('na terra, alcance mais longe'; igual a agua)
		 proposto_graus = 360,
		-- 20/11 ONDA REAL (usuario): a onda alcanca, fere (Agua) e empurra; em terra e onda de lama menor [PROPOSTA de numeros]
		onda_dur_agua = 1.2, onda_dur_terra = 1.1, onda_dano_agua = 12, onda_dano_terra = 8, onda_empurrao_agua = 7, onda_empurrao_terra = 4},
	Escamas = {reducao = 0.15, vida = 950, recuo_terra = 0.8, recuo_agua = 2.0},   -- P4: passiva -15% dano fisico (ref. 4); recuo de TESTE
	AlturaAgua = 4.3,                       -- placa de agua so visual (teste)
}
