-- IA_FaunaFloresta/Config (16/11/2026) - perfis por especie do PILOTO de IA (Cervo, Javali, Coruja).
-- Todos os numeros sao [A TESTAR]; os fluxos sao [PROPOSTA] (a regra oficial so diz: comportamento proprio por especie
-- dentro de fuga/defesa/ataque/perseguicao curta/retorno ao habitat). Velocidades = velocidade do clipe aprovado (m/s do
-- Blender, manifesto) x escala do modelo, para as patas casarem com o deslocamento.
local C = {}

C.DEBUG = true                 -- placa de estado sobre cada animal + log em atributos (removivel)
C.TAG_ALVO_TESTE = "AlvoFaunaTeste"   -- alvos falsos do roteiro de teste (so com DEBUG)

C.especies = {}

C.especies.Cervo = {
	tipo = "terrestre",
	-- clipe: velocidade do manifesto (m/s); multiplicada pela escala do modelo no Controlador
	vClipe = { Andar = 0.7102, Trote = 1.8519, Corrida = 4.8437, VirarE = 0.7102, VirarD = 0.7102 },
	-- transicoes sem v_perfil no JSON: curva propria [A TESTAR] (fracoes da velocidade de Corrida/Trote/Andar)
	perfilProprio = {
		Arrancada = { de = 0, para = "Corrida", inicio = 10 / 30 },       -- 10 quadros de susto parado (LEIA-ME do cervo)
		CorridaParaTrote = { de = "Corrida", para = "Trote" },
		TroteParaAndar = { de = "Trote", para = "Andar" },
		Frenagem = { de = "Corrida", para = 0 },
	},
	percepcao = { intervalo = 0.25, raioAlerta = 38, raioSairAlerta = 50, raioFuga = 26, alturaOlhos = 1.6 },
	alertaMin = 0.8,                -- "alerta por um instante" antes de decidir
	calma = 2.0,                    -- segundos fora do raioSairAlerta para voltar ao repouso
	-- raioGiro: menor raio de curva andando (studs) = velocidade/giro do clipe VirarE aprovado (2,13 studs/s a 25 graus/s);
	-- acima disso o raio cresce com a velocidade (tauGiro s). Sem velocidade NAO gira (17/11: nada de girar parado).
	corpo = { peito = 0.6, raio = 1.6, raioGiro = 4.9, tauGiro = 0.4 },   -- peito (m do Blender x escala), raio do corpo (studs)
	-- curva andando: VirarE/VirarD quando a curva pedida passa de 'entra'; volta ao Andar abaixo de 'sai'
	curva = { entra = math.rad(12), sai = math.rad(5), giroReto = math.rad(8), giroClipe = math.rad(25) },
	fuga = { distSegura = 60, tempoMax = 9, lookahead = 9, raioCorpo = 1.6, recalc = 0.4, giro = math.rad(200) },
	retorno = { giro = math.rad(110), raioChegada = 3, recalcCaminho = 1.0, manobraMax = 4 },
	clipes = { repouso = "Repouso", alerta = "Alerta", arrancada = "Arrancada", corrida = "Corrida",
		corridaTrote = "CorridaParaTrote", trote = "Trote", troteAndar = "TroteParaAndar", andar = "Andar",
		frenagem = "Frenagem", virarE = "VirarE", virarD = "VirarD" },
}

C.especies.Javali = {
	tipo = "terrestre",
	vClipe = { Andar = 0.4444, Trote = 1.3265, Corrida = 2.8, VirarE = 0.4444, VirarD = 0.4444 },
	percepcao = { intervalo = 0.25, raioAlerta = 30, raioSairAlerta = 40, raioFuga = 0, alturaOlhos = 0.9 },
	alertaMin = 0.6,
	calma = 2.0,
	corpo = { peito = 0.5, raio = 1.3, raioGiro = 3.05, tauGiro = 0.45 },   -- raioGiro do VirarE aprovado (1,33 studs/s a 25 graus/s)
	curva = { entra = math.rad(12), sai = math.rad(5), giroReto = math.rad(8), giroClipe = math.rad(25) },
	encarar = { vel = 1.6, tolerancia = math.rad(10), tempoMax = 3.0 },   -- vira para o alvo ANDANDO em arco (VirarE/D x 1,6)
	ameaca = { raioAmeaca = 24, raioInvestida = 18 },  -- ameaca se o alvo chegar a 24; so investe se continuar a <= 18 depois
	investida = { distMax = 22, alemDoAlvo = 5, tempoMax = 2.6, lookahead = 3.5, raioCorpo = 1.4, minLivre = 8,
		alinhamento = math.rad(15),   -- so investe de frente para o alvo (a investida nao gira)
		folgaGolpe = 1.5 },           -- a Chifrada comeca quando faltam isto (studs) entre a ponta do focinho e a superficie do alvo: o pico do golpe
	                              -- cai no contato e a freada ainda empurra ~0,4 (raio fixo falhava: 5,5 entrava 1 stud, 6,5 parava longe)
	recarga = 6,                         -- sem nova investida por este tempo (evita perseguicao sem fim)
	retorno = { giro = math.rad(110), raioChegada = 3, recalcCaminho = 1.0, manobraMax = 4 },
	clipes = { repouso = "Repouso", alerta = "Alerta", alertaRepouso = "AlertaParaRepouso", ameaca = "Ameaca",
		investida = "Investida", corrida = "Corrida", recuperacao = "RecuperacaoInvestida", andar = "Andar",
		andarParado = "AndarParaParado", paradoAndar = "ParadoParaAndar", virarE = "VirarE", virarD = "VirarD",
		chifrada = "Chifrada" },
}

C.especies.Coruja = {
	tipo = "voo",
	vClipe = { BaterAsas = 3.0, Planar = 3.6 },
	percepcao = { intervalo = 0.25, raioAlerta = 30, raioSairAlerta = 40, raioFuga = 18, alturaOlhos = 0.5 },
	alertaMin = 0.8,
	calma = 2.0,
	corpo = { peito = 0.4, raio = 1.4 },
	voo = { subida = 4.5, descida = 3.0, giro = math.rad(120), raioCorpo = 1.4, folgaChao = 4, chegada = 1.0,
		reavaliar = 1.5, tentativas = 3, poleiroLivre = 5,
		raioGiro = 2.5,               -- sem velocidade nao gira no ar (no poleiro gira so com o clipe VirarNoLugar, que da os passos)
		curvaClipe = math.rad(15) },  -- planando: curva acima disto usa PlanarCurvaE/D (asas inclinadas)
	clipes = { repouso = "Repouso", alertaE = "OlharE", alertaD = "OlharD", decolar = "FugaDecolando",
		bater = "BaterAsas", planar = "Planar", bater2planar = "BaterParaPlanar", pousar = "Pousar",
		curvaE = "PlanarCurvaE", curvaD = "PlanarCurvaD" },
}

return C
