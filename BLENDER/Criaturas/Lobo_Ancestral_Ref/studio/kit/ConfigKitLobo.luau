-- ConfigKitLobo (ModuleScript em ReplicatedStorage.LoboAncestral) - parametros do kit Natureza do Lobo Ancestral.
-- TODOS OS NUMEROS SAO [PROPOSTA] para prototipo no place isolado (ficha §6ae); nao sao regra oficial. Ajustar aqui.
-- Elemento unico: Natureza. Mordida e garra basicas NAO ocupam slots. 2 passivas + 3 ativas (decisao do usuario 10/11).
return {
	PROPOSTA = true,
	Energia = {max = 100, regenPorS = 5},
	Vida = 400,
	Basico = {               -- fora dos slots
		Mordida = {dano = 10, alcance = 7, cone = 70, recarga = 1.0, clipe = "Mordida", marcador = "Contato"},
		Garra   = {dano = 8,  alcance = 6, cone = 80, recarga = 0.9, clipe = "Garra",   marcador = "Contato"},
	},
	Esquiva = {chanceBase = 0.05},
	Movimento = {andar = 3.02, trote = 0, corrida = 21.43, distSeguir = 9, distParar = 6}, -- velocidades = as dos clipes (sem patinar)
	Acumulo = {tetoVelocidade = 0.25, tetoEsquiva = 0.30, tetoDano = 0.25},  -- bonus aditivos somados numa tabela unica, com teto
	-- vantagem ambiental oficial da Floresta (10-15%) NAO entra nesta tabela e nao e reaplicada pelo kit
	CacadorNoturno = {
		noiteInicio = 18.5, noiteFim = 5.5, histerese = 0.1, intervalo = 1.0,      -- Lighting.ClockTime lido so no servidor
		velocidade = 0.12, esquiva = 0.10, danoFisico = 0.12,                     -- so mordida/garra e golpes fisicos do kit
	},
	InstintoCaca = {
		raio = 60, intervalo = 1.0, rastroSeg = 8, atrasoMin = 1.0,              -- pegadas de inimigos vistos (com linha de visao), sempre atrasadas
		ninhoRaio = 150, ninhoIntervalo = 30, ninhoErroGraus = 30,                -- pista de ninho: so direcao aproximada, sem posicao
	},
	SaltoPredatorio = {
		alcanceMin = 8, alcanceMax = 40, voo = 0.44, raioAcerto = 6, multDano = 1.4, recarga = 8, energia = 20,
		clipe = "Hab_SaltoPredatorio", decolagem = 0.42, golpe = 0.86, alturaArco = 0.18,      -- altura = 18% da distancia
	},
	UivoAncestral = {
		duracao = 6, velocidade = 0.15, esquiva = 0.20, recarga = 18, energia = 15,
		clipe = "Hab_UivoAncestral", buffInicio = 0.6,
	},
	Investida = {
		largura = 5, multDano = 1.2, recarga = 6, energia = 15, alcanceMordida = 1.5,   -- 15/11: 4 mordia alvo a 10 studs (focinho ~6,5 do pivo)
		clipe = "Hab_Investida", contato = 0.86,
		-- avanco = curva de velocidade do proprio clipe (clipes_kit30/Investida_velocidade.json): parado ate 0,22 s, rampa ate 0,36,
		-- galope 21,43 studs/s ate 0,78, desacelera ate 0,96 -> ~12,4 studs. A proposta antiga de 30 studs exigiria um clipe
		-- mais longo (com 30 studs neste clipe as patas patinariam 2,4x).
	},
}
