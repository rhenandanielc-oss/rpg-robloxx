-- ConfigCombate (ModuleScript, ServerScriptService.Combate_Dragao) — PROTOTIPO.
-- OFICIAL (Documentos 01/02 ATUALIZADOS, revisao 30/10/2026 — prevalece sobre as regras antigas):
--   Cada criatura tem UM elemento natural. Sem desbloqueio de 2o/3o elemento, sem troca em combate, sem fusoes.
--   Dragao das Montanhas = FOGO exclusivo (identidade vulcanica).
--   Ativas (4): Sopro Draconico, Arremetida Draconica, Tempestade de Asas, Coracao Infernal (substitui a Ruptura).
--   Passivas (2): Sangue de Magma, Burning. Garra/mordida/mordida aerea sao basicos (fora dos 4 slots).
--   Ruptura Vulcanica e Dominio Draconico NAO pertencem ao Montanhas; o codigo deles fica disponivel (recuperavel).
-- PENDENTE: TODOS os numeros abaixo (dano, recarga, energia, alcance, duracoes, percentuais) sao PROVISORIOS
-- (NAO_APROVADO) e ficam aqui para balanceamento; nenhum foi oficializado.
local NAO_APROVADO = true
return {
	NAO_APROVADO = NAO_APROVADO,
	elementosGlobais = {"Fogo", "Terra", "Ar", "Raio", "Gelo", "Agua", "Luz", "Sombra"},  -- referencia; cada forma restringe abaixo
	-- elemento UNICO por forma (oficial 30/10). Glacial = Gelo e Sombrio = Sombra: kits ainda nao definidos (nao ativar)
	elementosForma = {Montanhas = {"Fogo"}, Glacial = {"Gelo"}},
	habilidadesForma = {Montanhas = {"Sopro", "Arremetida", "Tempestade", "Coracao"}, Glacial = {"Sopro", "Arremetida", "Tempestade", "Coracao"}},
	passivasForma = {Montanhas = {"SangueDeMagma", "Burning"}, Glacial = {"SangueGlacial", "Frostbite"}},
	-- PATCH_KIT_GELO (oficial 02/11): o slot (tecla/HUD/IA) continua com o mesmo id; a forma decide a habilidade real
	kitForma = {Glacial = {Sopro = "SoproGlacial", Arremetida = "Rajadas", Tempestade = "ZeroAbsoluto", Coracao = "Nevasca"}},
	maxElementos = 1,                                            -- sem elementos secundarios (o Nucleo nao le desbloqueios)
	energiaMax = 100, energiaRegen = 6,                         -- por segundo
	basicos = {
		Mordida = {clipe = "Ataque_Mordida", recarga = 1.6, dano = 18, alcance = 34, raio = 14, intensidade = "leve"},
		Garra = {clipe = "Ataque_Garra_E", clipeD = "Ataque_Garra_D", recarga = 1.8, dano = 14, alcance = 30, raio = 18, intensidade = "moderado"},
		Cauda = {clipe = "Ataque_Cauda", recarga = 3, dano = 20, raio = 62, intensidade = "pesado"},
		Rugido = {clipe = "Rugido_Combate", recarga = 8, dano = 0, emissao = 0.95,  -- sem dano: nao ha regra aprovada
			-- PATCH_RUGIDOS_FOGO (02/11): por forma, o clipe certo para a situacao {clipe, segundo da emissao}: parado =
			-- corpo inteiro; andando = so pescoco/cabeca (_Sup) sobre a locomocao; voando = parcial aereo (asas seguem o voo)
			porForma = {Montanhas = {chao = {"Rugido_Combate", 0.48}, mov = {"Rugido_Combate_Sup", 0.48}, ar = {"Rugido_Aereo_Sup", 0.84}}}},
	},
	habilidades = {
		Sopro = {recarga = 9, energia = 25, emissao = 1.8, tick = 0.3, elemental = true,
			emissaoMax = 6, energiaSeg = 8,                       -- segurado: ate 6 s, 8 de energia/s alem dos 1,8 s (EXPERIMENTAL)
			porElemento = {
				-- alcance AUMENTADO para teste (antes 75/95/60); angulo do cone casado com a largura visual do jato
				Fogo = {forma = "cone", alcance = 110, angulo = 12, dano = 6},
				-- versoes de outros elementos: NAO usadas pelo Montanhas (so Fogo); mantidas para futuras criaturas
				Terra = {forma = "projetil", alcance = 120, quantidade = 4, velocidade = 150, raioImpacto = 13, dano = 12},
				Raio = {forma = "descarga", alcance = 100, largura = 5, pulsos = 3, dano = 10},
				Ar = {forma = "cone", alcance = 95, angulo = 18, dano = 5},
			}},
		-- Arremetida Draconica (ATUALIZACAO OFICIAL 02/11): 5 s de velocidade extraordinaria no PROPRIO controlador de
		-- locomocao (montaria: chao e voo; IA: perseguicao integrada), partindo da velocidade atual e terminando por
		-- desaceleracao; o jogador continua dirigindo. Contato da cabeca com um inimigo valido = UMA mordida devastadora
		-- por ativacao (dano > mordida comum, Burning), que encerra a fase ofensiva. Numeros provisorios (NAO_APROVADO).
		Arremetida = {recarga = 12, energia = 30, intensidade = "pesado", duracao = 5,
			velChao = 52, acelChao = 24,                           -- correr normal 17-22 -> ~2,4x
			velAr = 90, acelAr = 30,                               -- voo rapido 55 / voo livre 20
			giroIA = 75,                                           -- graus/s de correcao de rumo da IA na perseguicao
			danoMordida = 46, raioMordida = 9, avancoMordida = 7, alturaMordida = 22,   -- alcance: horizontal + faixa vertical (cabeca alta)
			   -- mordida comum = 18; hitbox a frente da cabeca
			antecipa = 0.32,                                       -- s: abre a mandibula antes do contato previsto
			freioImpacto = 0.5, empurraoMordida = 40, recuperacao = 0.7,
			distancia = 170},                                      -- so para a decisao da IA (alcance de perseguicao)
		-- Tempestade: no solo o corpo se eleva e as asas batem repetidas vezes; no ar as batidas comecam direto. Cada batida
		-- REAL do clipe (tempos abaixo) solta uma onda: dano (1a cheia, demais fracao) e empurrao, 1 acerto por alvo por batida.
		Tempestade = {recarga = 16, energia = 40, raio = 78, dano = 16, intensidade = "moderado",
			elevacao = 11,                                         -- quanto o corpo sobe de verdade na versao terrestre
			-- PATCH_TEMPESTADE_V2 (02/11): SEQUENCIA de batidas. Solo: Tempestade_Asas ate a 3a batida (2,62 s), o corpo
			-- fica no alto e o clipe aereo (Tempestade_Asas_Ar) da mais 2 batidas; depois o trecho final do clipe terrestre
			-- (a partir de 2,6 s) faz a descida e o pouso. Ar: o clipe aereo 2 vezes = 4 batidas. Tempos = pontos baixos
			-- das asas nos clipes (a onda sai no instante da batida real).
			batidasChao = {1.75, 2.17, 2.54, 3.62, 4.48}, trocaAr = 2.62, retomaQueda = 4.95, quedaClipe = 2.6, pousoApos = 0.35,
			batidasAr = {1.0, 1.86, 3.4, 4.26}, voltasAr = 2, clipeAr = 2.4,
			fatorSecundario = 0.35,                                -- dano das batidas seguintes = dano x fator
			fatorEmpurraoSec = 0.55,                               -- empurrao das seguintes (nada de lancar sem controle)
			empurrao = {horizontal = 42, vertical = 16}},           -- studs/s (reacao curta; provisorio)
		Ruptura = {recarga = 15, energia = 35, dano = 24, intensidade = "pesado",
			requerSolo = true, distSoloMax = 7,                    -- patas ate 7 studs do chao
			ondaRaio = 22,                                         -- onda de choque no impacto (centro do corpo)
			aneis = {24, 36, 48}, pilaresPorAnel = {6, 8, 10}, intervaloAnel = 0.16,   -- erupcao em VOLTA do dragao (360 graus)
			folgaCorpo = 7, folgaAsa = 5,                          -- exclusao: distancia minima do pilar aos ossos/membranas
			raioPilar = 8, protecaoOvo = 16,
			lancamento = {vertical = 48, horizontal = 28}},        -- reacao curta (studs/s); intensidade a balancear
		Dominio = {recarga = 30, energia = 35, duracao = 12, multiplicadorDano = 1.0},
		-- ===== KIT DO GELO (Dragao Glacial, oficial 02/11; numeros PROVISORIOS) =====
		-- Sopro Glacial: jato continuo de frio (mesma mecanica do sopro segurado), dano por tick + Frostbite por tick
		SoproGlacial = {recarga = 10, energia = 25, emissao = 1.8, tick = 0.3, elemental = true, emissaoMax = 5, energiaSeg = 8,
			emAtaque = "Sopro", clipes = "Sopro_Glacial", frost = 6,
			porElemento = {Gelo = {forma = "cone", alcance = 105, angulo = 11, dano = 6}}},
		-- Rajadas de Gelo: 4 lancas rapidas pela boca, cada uma com mira propria (cursor do cavaleiro ou alvo da IA com
		-- antecipacao); hitbox FINA (mais dificil de acertar), mais dano e muito Frostbite por acerto
		Rajadas = {recarga = 11, energia = 30, elemental = true, intensidade = "moderado", clipe = "Rajadas_Gelo", duracao = 2.4,
			disparos = {0.72, 1.08, 1.44, 1.80}, velocidade = 240, alcance = 230, raio = 3.2, dano = 22, frost = 24, coneMin = 0.25},
		-- Zero Absoluto: tensao e descarga; onda circular que se expande pelo chao (1 acerto por alvo) e deixa uma zona
		-- congelada que segue acumulando Frostbite em quem fica dentro
		ZeroAbsoluto = {recarga = 15, energia = 35, elemental = true, intensidade = "pesado", clipe = "Zero_Absoluto", duracao = 2.8,
			emissao = 1.06, raio = 64, velOnda = 95, alturaFaixa = 18, alturaMaxAr = 45, dano = 24, frost = 50,
			zona = 4.0, zonaRaio = 52, zonaTick = 0.5, zonaFrost = 6},
		-- Nevasca Ancestral (ultimate): sobe (solo) ou ganha altitude (ar), ruge, corpo inteiro brilha, tempestade de
		-- fragmentos em ondas ao redor; no solo desce e pousa no fim
		Nevasca = {recarga = 28, energia = 55, elemental = true, intensidade = "pesado", clipe = "Nevasca_Ancestral", duracao = 5.6,
			elevacaoSolo = 26, subidaAr = 14, subida = {0.5, 1.6}, descida = {4.7, 5.4}, rugido = 1.75,
			ondas = {2.2, 2.9, 3.6, 4.3}, raio = 95, dano = 30, fatorOnda = 0.55, frost = 30},   -- NAO pertence ao Montanhas (outras formas)
		-- Coracao Infernal (oficial 30/10): concentra energia no peito/garganta, EXPELE pela boca uma lamina de fogo que
		-- se projeta do focinho e depois GIRA ao redor do corpo (plano horizontal na altura da boca), com rastro.
		-- Hitbox = setor varrido pela lamina a cada quadro (entre o angulo anterior e o atual), 1 acerto por alvo por uso.
		-- Solo e ar. Duracao, voltas, sentido, raio e dano: PENDENTES (provisorios abaixo).
		Coracao = {recarga = 18, energia = 40, dano = 24, intensidade = "pesado",
			carga = 1.1,                                           -- concentracao (peito/garganta brilham)
			expele = 0.4,                                          -- lamina sai da boca e se estende ate o raio externo
			giro = 1.7, voltas = 1.25, sentido = 1,                -- 1 = anti-horario visto de cima; -1 = horario
			raioExterno = 62,                                      -- alcance da ponta (studs) — configuravel
			larguraLamina = 6,                                     -- meia-largura da hitbox perpendicular a lamina
			alturaFaixa = 16,                                      -- tolerancia vertical em volta do plano da lamina
			dissipa = 0.6},
	},
	-- PASSIVAS (oficial 30/10; numeros PENDENTES/provisorios)
	passivas = {
		-- Sangue de Magma: resistencia natural a dano de Fogo; dano significativo recebido ativa reforco ofensivo temporario
		SangueDeMagma = {resistenciaFogo = 0.3,                 -- fracao do dano de Fogo ignorada
			limiar = 0.08, janela = 3,                         -- dano >= 8% da vida maxima dentro de 3 s ativa
			duracao = 8, multiplicadorOfensivo = 1.2, intervalo = 20},
		-- Burning: todo ataque ofensivo VALIDO que acertou aplica queimadura (dano periodico). 1 queimadura por alvo e por
		-- origem: novos acertos so RENOVAM a duracao (sem empilhar), com teto de renovacoes por aplicacao.
		Burning = {duracao = 4, intervalo = 1, danoTick = 3, renovaMax = 3,
			duracaoMaxTotal = 12,                              -- teto absoluto de uma queimadura continua (s)
			imuneAtributo = "ImuneQueimadura"},                -- alvo com este atributo = true nao queima
		-- Sangue Glacial (Glacial): frio constante — resistencia a Gelo, imune ao proprio Frostbite; em combate os olhos
		-- e o interior da boca brilham (atributo SangueGlacialFim, so visual)
		SangueGlacial = {resistenciaGelo = 0.3, combateJanela = 6},
		-- Frostbite (Glacial): acumulo 0..100 por alvo; lentidao e vulnerabilidade crescem com o acumulo; em 100 o alvo
		-- CONGELA por instantes e volta a 45 (com janela em que acumula mais devagar, sem travar em cadeia); sem novos
		-- acertos o acumulo cai. basico = acumulo dos ataques basicos (mordida/garra/cauda/mordida aerea)
		Frostbite = {max = 100, basico = 10, decaiApos = 2.0, decaiPorSeg = 12, lentidaoMax = 0.55, vulnerabMax = 0.25,
			congelaDur = 1.4, aposCongelar = 45, imuneCongelarPor = 4, imuneAtributo = "ImuneFrostbite"},
	},
	pvpAtivoAtributo = "PvPAtivo",                              -- Workspace:SetAttribute("PvPAtivo", true) libera dano entre jogadores
	zonaSeguraTag = "ZonaSegura",                               -- CollectionService: partes que protegem quem esta dentro
	estruturaProtegidaTag = "EstruturaProtegida",               -- efeitos nunca nascem dentro destas partes
	pedidoIntervaloMin = 0.25,                                  -- anti-spam do RemoteEvent
	sons = {},                                                  -- sem audio licenciado disponivel: pontos de sincronia apenas
}
