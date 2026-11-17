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
		Garra   = {dano = 8,  alcance = 6, cone = 80, recarga = 0.9, clipe = "Garra",   marcador = "Contato"},
	},
	Esquiva = {chanceBase = 0.05},
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
	Investida = {
		largura = 5, multDano = 1.2, recarga = 6, energia = 15, alcanceMordida = 1.5,   -- 15/11: 4 mordia alvo a 10 studs (focinho ~6,5 do pivo)
		clipe = "Hab_Investida", contato = 0.86,
		-- avanco = curva de velocidade do proprio clipe (clipes_kit30/Investida_velocidade.json): parado ate 0,22 s, rampa ate 0,36,
		-- galope 21,43 studs/s ate 0,78, desacelera ate 0,96 -> ~12,4 studs. A proposta antiga de 30 studs exigiria um clipe
		-- mais longo (com 30 studs neste clipe as patas patinariam 2,4x).
	},
}
