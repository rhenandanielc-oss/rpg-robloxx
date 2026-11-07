-- ConfigMontaria (ModuleScript, ReplicatedStorage.Montaria_Dragoes) — PROTOTIPO, lido por servidor e cliente.
-- Velocidades, curvas, planeio e controles sao CALIBRACAO DE TESTE (NAO_APROVADO): ajustar apos testes de jogo.
-- Regras oficiais aplicadas: so o dono monta; ovo/bebe/jovem nao montam; pre-adulto so montaria terrestre (especie
-- grande); voo montado exige a missao de desbloqueio (atributo VooDesbloqueado), nao basta ser adulto; guardiao
-- selvagem de ninho nunca e montavel; sem desmontar em pleno voo.
return {
	NAO_APROVADO = true,
	estagios = {                                     -- estagio -> {chao, voo} (voo ainda exige a missao)
		Ovo = {false, false}, Bebe = {false, false}, Jovem = {false, false},
		PreAdulto = {true, false}, Adulto = {true, true}, Anciao = {true, true},
	},
	formasGrandes = {Montanhas = true},              -- pre-adulto so monta em especie grande
	distMontar = 38,                                 -- studs do jogador ate o dorso
	-- (06/11, usuario: "O cavaleiro ainda nao sobe, ele fica no mesmo lugar, e entra no corpo do dragao") com 0,75 o cavaleiro
	-- ficava 25% para tras do dorso (ao levantar do Abaixado, 0,4 stud dentro do corpo); com a sela ele segue o dorso inteiro
	assento = {osso = "Coluna2", acima = 10.6, frente = 0.6, seguirOsso = 1.0},   -- sela entre as asas (sem cristas/pescoco)
	-- chao (studs/s, graus/s)
	andarVel = 4.8, correrVel = 17, recuarVel = 2.4,
	acelChao = 9, freioChao = 15, giroAndar = 30, giroCorrer = 40, giroParado = 24,
	ritmoAndarBase = 3.2, ritmoCorrerBase = 13,      -- velocidade calibrada dos clipes Andar/Correr
	frenagemMin = 11,                                -- acima disto, soltar o acelerador toca Correr_Frenagem
	-- ar
	vooVel = 34, vooRapidoVel = 55, vooMin = 14, acelVoo = 10, freioVoo = 8,   -- vooMin = sustentacao: S nunca para nem voa para tras
	-- curvas (29/10, referencia de fluidez de jogos de montaria): mais resposta e inclinacao do corpo inteiro na curva
	-- (antes: giroVoo 42, giroVooRapido 28, inclinacaoMax 32, suavRoll 2.5, acelGiro 140)
	giroVoo = 52, giroVooRapido = 36,                -- graus/s: dragao colossal nao faz curva de 180 instantanea
	inclinacaoMax = 60, suavRoll = 4,                -- graus / resposta
	vSubida = 24, vDescida = 30, pitchCamera = 0.55,  -- quanto a camera inclina a trajetoria
	planeioQueda = 7, planeioPerda = 1.6, planeioMin = 18,   -- planeio: perde altura e velocidade (sem sustentacao infinita)
	-- voo guiado pela camera (arcade assistido; NAO_APROVADO): graus, graus/s, studs/s
	-- (29/10) corpo inteiro aponta para a trajetoria como na referencia: antes subida 40, descida 60, gamaTaxa 70,
	-- narizSegue 0.85 e pitch do corpo limitado a 40 graus
	voo = {zonaMorta = 5, ganhoPitch = 1.0, gamaMaxSubida = 60, gamaMaxDescida = 70, gamaTaxa = 95, planeioGama = 4,
		pitchMax = 65, pitchResp = 5.5,
		gravidade = 16, arrastoExcesso = 0.6, mergulhoVel = 80, mergulhoInicio = 22,
		ganhoYaw = 2.4, acelGiro = 200, giroLento = 58, velGiroLento = 22, velPairar = 22, narizSegue = 1.0},
	-- voo livre (atributo VooLivre no modelo; teste do Dragao Glacial): sem W freia ate parar no ar; S sem funcao no ar;
	-- pouso automatico abaixo de alturaPouso (studs acima do apoio) descendo devagar. Por modelo: AlturaPouso, FolgaChao.
	vooLivre = {velPlena = 20, velPairar = 16, desacel = 9, vSubidaParado = 16, vDescidaParado = 16, gamaEQ = 35, velMaxPouso = 26, alturaPouso = 12},
	-- Mordida Aerea (TESTE, NAO_APROVADO): tempos em s casados com o clipe de 1,0 s; dano/empurrao provisorios
	mordidaAerea = {recarga = 4, duracao = 1.0, disparo = 0.28, fimDisparo = 0.62, inicioMordida = 0.40, fimMordida = 0.66,
		velocidade = 78, gamaMaxSubida = 25, gamaMaxDescida = 45, raioHitbox = 5.5, avancoHitbox = 2.5, dano = 40,
		empurrao = 55, freioImpacto = 0.6},
	folgaChao = 8, tetoDecolagem = 60,               -- espaco livre exigido acima para decolar
	alturaMinPouso = 3, vPouso = 18, pousoInclinacaoMin = 0.72, pousoAlcance = 160,
	-- rede
	entradaHz = 15, entradaTimeout = 0.6,            -- sem entrada recente -> solta o acelerador
	-- controles (teclado/mouse, gamepad, toque). Movimento vem do PlayerModule (WASD / analogico / joystick).
	controles = {
		decolar = {Enum.KeyCode.Space, Enum.KeyCode.ButtonA},          -- no chao: decola; no ar: sobe
		descer = {Enum.KeyCode.LeftControl, Enum.KeyCode.ButtonL2},
		correr = {Enum.KeyCode.LeftShift, Enum.KeyCode.ButtonL3},
		planar = {Enum.KeyCode.G, Enum.KeyCode.ButtonY},
		mordida = {Enum.UserInputType.MouseButton1, Enum.KeyCode.ButtonL1}, garra = {Enum.KeyCode.R, Enum.KeyCode.DPadLeft},   -- Mordida Aerea: M1 (clique esquerdo) / L1 (so voo livre)
		pousar = {Enum.KeyCode.F, Enum.KeyCode.ButtonB},
		subirAr = {Enum.KeyCode.E}, descerAr = {Enum.KeyCode.Q},          -- (29/10) E sobe / Q desce (prioridade sobre a camera)
		desmontar = {Enum.KeyCode.X, Enum.KeyCode.DPadDown},
		rugido = {Enum.KeyCode.T, Enum.KeyCode.DPadRight},               -- PATCH_RUGIDOS_FOGO: rugir (chao parado/andando ou voando)
		elemento = {Enum.KeyCode.Z, Enum.KeyCode.DPadUp},                  -- so liga em forma com MAIS de um elemento (nenhuma hoje)
		travar = {Enum.KeyCode.C, Enum.UserInputType.MouseButton3, Enum.KeyCode.ButtonR3},   -- PATCH_TRAVA_ALVO: alvo dinamico (liga/solta)
		habilidades = {                                                   -- ordem oficial das 4 ativas (oficial 30/10): {id, tecla, gamepad, rotulo}
			{"Sopro", Enum.KeyCode.One, Enum.KeyCode.ButtonR2, "Sopro"},
			{"Arremetida", Enum.KeyCode.Two, Enum.KeyCode.ButtonR1, "Arremetida"},
			{"Tempestade", Enum.KeyCode.Three, Enum.KeyCode.ButtonX, "Tempestade"},
			{"Coracao", Enum.KeyCode.Four, Enum.KeyCode.DPadRight, "Coração Inf."},
		},
		passivas = {SangueDeMagma = "Sangue de Magma", Burning = "Burning", SangueGlacial = "Sangue Glacial", Frostbite = "Frostbite",
			MarcaSombria = "Marca Sombria", RastroBreu = "Rastro do Breu"},   -- PATCH_CORRENTES_NOITE: rotulos do Sombrio   -- exibicao no HUD (lista vem do atributo Passivas)
		-- PATCH_KIT_GELO: rotulo de cada slot por forma, e slots que seguem mandando a mira enquanto a habilidade roda (s)
		rotulosForma = {Glacial = {Sopro = "Sopro Glacial", Arremetida = "Rajadas", Tempestade = "Zero Absol.", Coracao = "Nevasca"},
			Sombrio = {Sopro = "Sopro Umbral", Arremetida = "Correntes", Tempestade = "Passo Sombrio", Coracao = "Eclipse"}},   -- PATCH_ECLIPSE_DRACONICO / PATCH_PASSO_SOMBRIO
		dicaForma = {Glacial = " | segure 1: Sopro Glacial | 2 Rajadas de Gelo (mire) | 3 Zero Absoluto | 4 Nevasca Ancestral",
			Sombrio = " | segure 1: Sopro Umbral | 2 Correntes da Noite (mire no chao) | 3 Passo Sombrio | 4 Eclipse Dracônico"},
		miraVivaForma = {Glacial = {Arremetida = 2.6}, Sombrio = {Arremetida = 1.6}},   -- Correntes: mira ate a batida
		corEnergiaForma = {Glacial = Color3.fromRGB(150, 215, 255), Sombrio = Color3.fromRGB(165, 90, 255)},
	},
	-- alturaAlvo: ACIMA do dorso (o pivo fica no chao; o dorso esta a ~34). Antes era 14 = dentro do tronco, e a camera
	-- de oclusao do Roblox colava no corpo. No ar soma alturaVoo (os clipes de voo erguem o corpo 14 acima do pivo).
	camera = {distancia = 70, distMin = 45, distMax = 150, alturaAlvo = 42, alturaVoo = 14, suav = 6, fovBase = 70, fovVel = 10,
		pitchNeutro = 0.28},                                       -- rad: camera olhando 16 graus para baixo = voo nivelado
}
