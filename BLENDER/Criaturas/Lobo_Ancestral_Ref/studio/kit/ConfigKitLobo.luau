-- ConfigKitLobo (ModuleScript em ReplicatedStorage.LoboAncestral) - parametros do kit do Lobo Ancestral.
-- TODOS OS NUMEROS SAO [PROPOSTA] para prototipo no place isolado; nao sao regra oficial. Ajustar aqui.
-- 16/11/2026: alinhado a REFERENCIAS_PODERES_E_EFEITOS.md v6.2 §2 (Documents\RPG_Roblox): elementos Natureza e Ar (decisao
-- do usuario), Uivo +20% vel/+25% esquiva 8 s, Salto 8-50 sem alvo + planeio + encadeavel, Instinto raio 80 + marca da presa.
-- Mordida e garra basicas NAO ocupam slots. 2 passivas + 3 ativas (decisao do usuario 10/11).
return {
	PROPOSTA = true,
	Versao = "v6.2",
	Elementos = {"Natureza", "Ar"},
	Energia = {max = 100, regenPorS = 5},
	Vida = 400,
	Basico = {               -- fora dos slots (alcance >= ombro ~6, regra §0d)
		Mordida = {dano = 10, alcance = 7, cone = 70, recarga = 1.0, clipe = "Mordida", marcador = "Contato"},
		Garra   = {dano = 8,  alcance = 5.3, cone = 80, recarga = 0.9, clipe = "Garra",   marcador = "Contato"},
	},
	Esquiva = {chanceBase = 0.05},
	-- 20/11 HITBOX DE CONTATO [A TESTAR]: corpo do alvo = capsulas nos OSSOS (acompanham a animacao; cauda e pelos fora) e o golpe
	-- conta da BOCA (Mandibula) / PATA (Mao) do lobo. Antes: caixa fixa da malha (3,7 x 8,5 x 13,4, com cauda) medida da anca.
	Hitbox = {
		capsulasLobo = {{"Pelve", "Peito", 1.3}, {"Peito", "Pescoco1", 1.1}, {"Pescoco1", "Cabeca", 0.8}, {"Cabeca", "Mandibula", 0.6},
			{"EscapulaD", "MaoD", 0.45}, {"EscapulaE", "MaoE", 0.45}, {"CoxaD", "PeD", 0.5}, {"CoxaE", "PeE", 0.5}},
		ignorarOssos = {"Cauda", "Tail", "Pelo", "Juba", "Orelha", "Palpebra", "Ear", "Fur", "Hair", "Raiz", "Root"},
		raioGenerico = 0.22,          -- outras criaturas com ossos: raio = menor lado da caixa x 0,22 (cada especie pode publicar o seu)
		boca = 0.9,                   -- ponta do focinho = Mandibula + 0,9 na direcao pescoco->mandibula
		contatoMordida = 1.0, contatoGarra = 1.0, contatoSalto = 1.5, corpoInvestida = 0.6,
		preverMordida = 1.6, preverGarra = 1.5, tContato = 0.45,   -- IA: so ataca se a boca/pata vai tocar (bote ~0,6 + velocidade x tempo ate o contato)
	},
	-- 19/11 GOLPES POR PORTE, QUEDA E FINALIZACAO (contrato geral das domesticaveis; prototipo no Lobo) [PROPOSTA]/[A TESTAR]
	-- Regras oficiais usadas (REFERENCIAS_PODERES_E_EFEITOS v6.2 §0b-0d): porte = ombro (ou comprimento / 2,5) x tamanho da idade;
	-- pequeno < 3, medio 3-8, grande 8-16, colossal >= 16; teto de lentidao 60%; >= 4 s entre atordoamentos (queda conta como
	-- atordoamento); colossal sofre metade da duracao; Forca (indice §0c) resiste a derrubada. O resto e proposta deste prototipo.
	Controle = {
		porte = {ombro = 6.2, idade = "Adulto", forca = 20},              -- Lobo Ancestral Adulto (§0c): ombro 6,2 / medio / Forca 20
		tamanhoIdade = {Filhote = 0.40, Jovem = 0.65, ["Pre-adulto"] = 0.85, Adulto = 1.0, Anciao = 1.10},
		forcaIdade = {Filhote = 0.30, Jovem = 0.55, ["Pre-adulto"] = 0.80, Adulto = 1.0, Anciao = 1.10},
		classes = {{"pequeno", 3}, {"medio", 8}, {"grande", 16}, {"colossal", math.huge}},
		golpes = {Mordida = {impacto = 1.0}, Garra = {impacto = 0.8}, SaltoPredatorio = {impacto = 1.6}, Investida = {impacto = 2.0}},
		-- chance final = base x impacto x fatorPorte(atacante - alvo, em classes) x fatorForca (forca do atacante / forca do alvo)
		porteRelativo = {[-3] = 0.05, [-2] = 0.2, [-1] = 0.55, [0] = 1.0, [1] = 1.3, [2] = 1.6, [3] = 1.8},
		forcaMinMax = {0.35, 1.5},
		lento = {chance = 0.30, fracao = 0.25, dur = 1.5},                 -- golpe comum: passo mais curto por um instante
		manca = {chance = 0.14, fracao = 0.45, dur = 2.0, impactoMin = 1.0}, -- pata falha: claudica
		queda = {chance = 0.16, dur = 3.0, extraEnfraquecido = 2.5,   -- r2 20/11: alvo ja enfraquecido (Vida <= finalizar.vidaAlvoMax) demora mais a levantar [A TESTAR]
			 impactoMin = 1.6, intervaloMin = 4.0, levantarVel = 1.5, -- derruba (Vida > 0)
			 -- r3 20/11: queda LATERAL propria (o caido fica de lado, barriga exposta). Lado de baixo: cai para LONGE do atacante
			 -- (barriga voltada para quem bateu); parede/corpo/sem chao/desnivel do lado das pernas ou das costas: tenta o outro;
			 -- nenhum livre: o de mais espaco (limitacao registrada no log). Medidas x escala do modelo [A TESTAR]
			 lateral = {clipeQueda = "QuedaLado", clipeCaido = "CaidoLado", clipeLevantar = "LevantarLado",
				pernas = 4.0, costas = 1.8, alturaSonda = 1.2, desnivelMax = 1.6,
				barrigaE = 1}},    -- caido sobre o lado E: a barriga aponta para +RightVector do modelo (medido no Studio 20/11)
		tetoLentidao = 0.60,
		duracaoPorte = {pequeno = 1.15, medio = 1.0, grande = 0.8, colossal = 0.5},
		pvp = {fatorDur = 0.5, janela = 12, maxSeguidos = 2, imuneSeg = 8},   -- criatura de jogador: controle curto e com resistencia a repeticao
		-- 20/11 finalizacao PROPRIA DO LOBO (outras especies terao a sua): morde o pescoco do caido, PUXA ate a boca e ESTRANGULA
		-- (segura sacudindo) antes do desfecho; interrompivel o tempo todo; se o lobo for ferido durante o estrangulamento, solta
		-- r2 (20/11, correcao do usuario): o lobo vai ao MEIO do corpo do caido, no FLANCO/barriga, morde e sacode a PROPRIA
		-- cabeca (clipe proprio Hab_MordidaFlanco); nao puxa, nao estrangula, nao mexe no corpo do alvo. Outras especies: a sua.
		estilo = {nome = "Lobo: mordida no flanco + sacudidas da cabeca", clipe = "Hab_MordidaFlanco",
			raioTronco = 1.3,        -- capsula Pelve-Peito do lobo deitado (superficie do flanco)
			frenteBoca = 5.06,       -- medido no Studio 20/11: pivo -> focinho no Contato (altura 0,74; deriva <= 0,1 nas sacudidas)
			contato = 0.9,           -- boca -> superficie do TRONCO no Contato (senao cancela: sem encaixe)
			contatoSegurar = 1.3,    -- durante as sacudidas (senao cancela: perdeu contato)
			ajusteMax = 1.5, giroMax = 135,  -- encaixe durante o rosnado (studs / graus); r9: chega de lado e orbitava; gira no lugar rosnando (patas deslizam: falta clipe de giro curto)
			preparo = 4.0,           -- r7: ponto de preparacao 4 studs para fora do flanco (entra perpendicular ao corpo)
			arcoFolga = 3.0,         -- contorna o corpo por esta distancia alem da cabeca/cauda quando esta do outro lado
			cancelaDano = 1,
			-- r3 20/11: alvo deitado DE LADO (CaidoLado). A barriga lateral fica 0,43 x (Peito-Pelve) a frente da coluna, na
			-- altura do tronco; clipe proprio com a boca no meio da barriga (Blender: boca 0,14-0,34 do tronco, 0,49-0,54 entre
			-- peito e pelve). Medidas como fracao do comprimento Peito-Pelve, entao valem para qualquer escala.
			clipeLado = "Hab_MordidaFlancoLado",
			ladoDesloc = 0.156,      -- centro real do tronco deitado de lado: deslocado da coluna para a barriga
			ladoRaio = 0.272,        -- meia largura do tronco deitado (centro -> superficie da barriga)
			frenteBocaLado = 5.46},  -- pivo -> focinho no Contato do clipe lateral (Blender 5,73 x 0,953 do clipe aprovado) [A TESTAR]
		finalizar = {anuncio = 0.9, alcance = 7.5, cone = 120, vidaMin = 0.30, ameacaRaio = 25, folgaTempo = 0.8, clipeAnuncio = "Rosnar",
			abordarAte = 14, vigiarDist = 8, energiaMin = 10,
			vidaAlvoMax = 0.35},  -- IA: so finaliza alvo enfraquecido (acima disso aproveita a queda com golpes normais) e que chega antes de levantar
	},
	-- 19/11: esquiva VISIVEL (ativa da IA e passiva sorteada): pequeno "teleporte" lateral validado no servidor [A TESTAR]
	EsquivaVisual = {dist = 5, dur = 0.12, intervalo = 0.7, desnivel = 2.5, largura = 3.2, comprimento = 10,
		diagonal = 0.8, distCurta = 3.5},   -- 19/11: diagonais afastando do atacante e lateral curta antes de desistir [A TESTAR]
	Movimento = {andar = 3.02, trote = 0, corrida = 21.43, distSeguir = 9, distParar = 6}, -- velocidades = as dos clipes (sem patinar)
	-- bonus aditivos somados numa tabela unica, com teto. Esquiva total = base 5% + bonus (teto 30%) = 35% no maximo (decisao do
	-- usuario: teto de esquiva 35%; noite 10% + Uivo 25% = 35% de bonus -> 30%). Velocidade: noite 12% + Uivo 20% = 32% cabe.
	Acumulo = {tetoVelocidade = 0.35, tetoEsquiva = 0.30, tetoDano = 0.25},
	-- vantagem ambiental oficial da Floresta (10-15%) NAO entra nesta tabela e nao e reaplicada pelo kit
	CacadorNoturno = {
		noiteInicio = 18.5, noiteFim = 5.5, histerese = 0.1, intervalo = 1.0,      -- Lighting.ClockTime lido so no servidor
		velocidade = 0.12, esquiva = 0.10, danoFisico = 0.12,                     -- so mordida/garra e golpes fisicos do kit
	},
	InstintoCaca = {
		raio = 80, intervalo = 1.0, rastroSeg = 8, atrasoMin = 1.0,              -- pegadas de inimigos vistos (com linha de visao), sempre atrasadas
		ninhoRaio = 150, ninhoIntervalo = 30, ninhoErroGraus = 30,                -- pista de ninho: so direcao aproximada, sem posicao
		marcaSeg = 8, marcaDano = 0.10,                                           -- presa marcada (alvo do Salto ou quem o lobo acerta): +10% so nela
		-- "revela inimigos escondidos em vegetacao": [PENDENTE] - nao ha sistema de esconderijo no place de teste
	},
	SaltoPredatorio = {
		alcanceMin = 8, alcanceMax = 50, voo = 0.44, planeio = 0.6, raioAcerto = 6, multDano = 1.2,
		folgaPouso = 5.8, raioAcertoSuperficie = 8.5,                -- r5 18/11: pouso/acerto medidos a SUPERFICIE do alvo [A TESTAR]
		recarga = 8, energia = 20, energiaSemAlvo = 12,
		cadeiaJanela = 2.0, cadeiaFatorEnergia = 0.5,            -- 2o salto em ate 2 s apos pousar: sem recarga, metade da energia
		clipe = "Hab_SaltoPredatorio", decolagem = 0.42, golpe = 0.86, alturaArco = 0.18,      -- altura = 18% da distancia
		apiceClipe = 0.64,                                       -- o clipe congela aqui durante o planeio (meio do voo)
		desnivelMax = 8,                                         -- 17/11: pouso no chao real; desnivel maximo (studs) [A TESTAR]
		anteciparMax = 10,                                       -- 17/11: alvo em movimento: correcao maxima do ponto de pouso [A TESTAR]
	},
	UivoAncestral = {
		duracao = 8, velocidade = 0.20, esquiva = 0.25, recarga = 20, energia = 20,
		clipe = "Hab_UivoAncestral", buffInicio = 0.6, fadeVisual = 1.5,
	},
	-- 17/11: IA de DEFESA do guardiao de TESTE (sem dono). Nao e IA do jogo principal. Todos [PROPOSTA]/[A TESTAR].
	IA_Guardiao = {
		intervalo = 0.2, raioAmeaca = 22, raioAlerta = 45, aproximacao = 3,   -- ameaca: perto, ou chegando >= 3 studs/s ate 45
		calmaSeg = 5, coleira = 25, voltaPostoDist = 3, giroGrausS = 180,      -- sem ameaca 5 s -> calmo e volta ao posto
		uivoAte = 30, investidaAte = 17, saltoDesde = 18,                       -- escolha: Uivo -> Mordida (<=8) -> Investida (<=17) -> Salto (18-50)
	},
	-- 19/11: IA ESTRATEGICA do lobo sem dono (modulo LoboIA, prototipo no place isolado; nao integrada). Gatilhos de ameaca e
	-- coleira continuam os do IA_Guardiao acima. Todos [PROPOSTA]/[A TESTAR].
	IA_Lobo = {
		tickCombate = 0.2, tickCalmo = 0.5, tickLonge = 1.5, raioJogadorPerto = 200,   -- decisao mais rara sem jogador por perto
		velocidades = {Espreita = 0.86, FarejarAndando = 1.61, Andar = 3.02, Trote = 7.67, Corrida = 21.43},   -- = clipes (sem patinar)
		giro = {Andar = 30, FarejarAndando = 30, Espreita = 25, Trote = 110, Corrida = 75},   -- graus/s andando para a frente
		virarParado = 60,                       -- calmo/alerta: acima disso, parado, usa VirarE/D
		sonda = 10, degrauMax = 2.5, separacao = 7,  -- obstaculo a frente (do pivo), degrau maximo por passo, distancia entre lobos
		distMin = 6.3,                          -- superficie do alvo a partir do pivo (focinho ~6,5): nao avanca alem (nao atravessa)
		pressaoAte = 14, perseguirDesde = 16, corridaDesde = 18, corridaFreia = 8, previsaoMax = 0.8,
		lembrarSeg = 8, investigarJanela = 20, farejarSeg = 4,
		planoMin = 1.2, intervaloGolpes = 0.35, reTentar = 2.0, repeticao = 14, variacao = 8, reservaEnergia = 15,
		investida = {min = 9, max = 17, cone = 12}, salto = {cone = 25},
		uivo = {vida = 0.6, distMin = 14, distSegura = 14, sobra = 15, fugaDist = 16, avancoMax = 2},   -- 19/11: so com espaco e rival sem avancar
		flanco = {encarado = 35, aposGolpes = 2, intervalo = 6, angulo = 70, duracao = 3.5},
		esquiva = {frente = 0.6, dist = 12, duracao = 1.5, intervalo = 4, salto = 14, angulo = 45},
		recuo = {vida = 0.35, energia = 18, dist = 16, recuperarAte = 55, defenderDentro = 8, maxSeg = 4, minSeg = 2.5},
		desistirVida = 0.12, recuperacaoApos = 6, avisoIntervalo = 8, idleIntervalo = 12,
		reposDist = 7.5, reposAngulo = 55, reposRaio = 10, reposSeg = 2.5,   -- colado e fora do cone: arco de reposicionamento
		capsula = {tras = 0.3, frente = 5.6, raio = 1.0}, folgaCorpo = 0.0, folgaTol = 0.03, folgaPiso = 0.15, virarContatoIntervalo = 3.0,   -- 19/11 silhueta anca->focinho (ponta ~6,6 do pivo) [A TESTAR]
		estiloVar = 0.15,                       -- variacao do estilo sorteado por lobo (arco/saida) [A TESTAR]
		corpoMin = 4.5,                         -- (fora de uso desde 19/11: substituido pela capsula/folgaCorpo acima)
		sondaAlvo = 5,                          -- sonda contra o corpo do proprio alvo (< distMin)
		-- 19/11 pressao em ciclos (duelo v48 "parado"): entrar em arco curto mordendo andando, abrir espaco e reentrar
		pressao = {arco = 35, andarAte = 9, golpesPorEntrada = 2, esperaContato = 0.55, coladoMax = 0.7,   -- r7: arcos maiores (giro/variacao)
			abrirAng = 90, abrirRaio = 11, abrirSeg = 1.8, reentrarMin = 8, retaAte = 11, antecipa = 0.6, retaLado = 0},   -- retaLado 30 testado (r5) e descartado: precisao caiu
		ritmoGolpes = 3,                      -- golpes basicos seguidos antes de rodear e voltar
	},
	Investida = {
		largura = 5, multDano = 1.2, recarga = 6, energia = 15, alcanceMordida = 1.5,   -- 15/11: 4 mordia alvo a 10 studs (focinho ~6,5 do pivo)
		clipe = "Hab_Investida", contato = 0.86,
		-- avanco = curva de velocidade do proprio clipe (clipes_kit30/Investida_velocidade.json): parado ate 0,22 s, rampa ate 0,36,
		-- galope 21,43 studs/s ate 0,78, desacelera ate 0,96 -> ~12,4 studs. A proposta antiga de 30 studs exigiria um clipe
		-- mais longo (com 30 studs neste clipe as patas patinariam 2,4x).
	},
}
