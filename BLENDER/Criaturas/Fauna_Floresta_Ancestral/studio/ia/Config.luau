-- IA_FaunaFloresta/Config (16/11/2026) - perfis por especie do PILOTO de IA (Cervo, Javali, Coruja).
-- Todos os numeros sao [A TESTAR]; os fluxos sao [PROPOSTA] (a regra oficial so diz: comportamento proprio por especie
-- dentro de fuga/defesa/ataque/perseguicao curta/retorno ao habitat). Velocidades = velocidade do clipe aprovado (m/s do
-- Blender, manifesto) x escala do modelo, para as patas casarem com o deslocamento.
local C = {}

-- placa de estado sobre cada animal + log em atributos (removivel). 17/11: o piloto do mapa real desliga com o atributo
-- Debug=false na pasta da IA; a cena de teste continua com DEBUG ligado (sem atributo)
C.DEBUG = script.Parent:GetAttribute("Debug") ~= false
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
	-- 17/11: subida/descida 4,5/3,0 nao venciam a altura dos galhos da Lagoa_5 (37 studs) sem rota longa
	voo = { subida = 7.0, descida = 7.0, giro = math.rad(120), raioCorpo = 1.4, folgaChao = 4, chegada = 1.0,
		reavaliar = 1.5, tentativas = 3, poleiroLivre = 5,
		raioGiro = 2.5,               -- sem velocidade nao gira no ar (no poleiro gira so com o clipe VirarNoLugar, que da os passos)
		curvaClipe = math.rad(15) },  -- planando: curva acima disto usa PlanarCurvaE/D (asas inclinadas)
	clipes = { repouso = "Repouso", alertaE = "OlharE", alertaD = "OlharD", decolar = "FugaDecolando",
		bater = "BaterAsas", planar = "Planar", bater2planar = "BaterParaPlanar", pousar = "Pousar",
		curvaE = "PlanarCurvaE", curvaD = "PlanarCurvaD" },
}

-- ==================================================================== VIVENCIA (17/11) [PROPOSTA] / numeros [A TESTAR]
-- Habitats aprovados pelo usuario (17/11): rotinas autonomas de descanso, alimentacao, agua e retorno; a ameaca tem prioridade.
-- Pontos reais ficam na cena (CenaLagoa). Aqui: tempos, tentativas e a POSICAO DA BOCA/BICO de cada clipe de contato, medida
-- no Studio (17/11) no pivo do modelo na escala de referencia (escRef = 3): x, altura acima do plano dos cascos, -frente.
C.escRef = 3
C.vivencia = {
	tempoTeste = 1,                 -- divisor das esperas (atributo TempoTeste na pasta da IA sobrepoe; so para teste)
	tentativasPonto = 2,            -- pontos alternativos tentados quando um esta ocupado/bloqueado
	esperaReserva = { 4, 8 },       -- espera (s) por um ponto reservado antes de tentar outro
	tempoMaxIda = 90,               -- desiste de chegar ao ponto depois disto (s) (o cervo anda a ~2 studs/s; desvio dos troncos)
	precisao = 0.45,                -- erro maximo do pivo no ponto da acao (studs, na escala de referencia)
	alinhamento = math.rad(14),     -- erro maximo de direcao no ponto
}
C.especies.Cervo.boca = { Pastar = Vector3.new(0, 1.58, -2.46), Beber = Vector3.new(0, 0.64, -2.07) }
C.especies.Cervo.cascos = 1.3       -- meia distancia entre cascos dianteiros e traseiros (alinha o corpo ao terreno)
C.especies.Cervo.profMax = 1.0      -- nao entra em agua mais funda que isto (studs, escRef)
C.especies.Cervo.vivencia = {
	repouso = { 18, 30 },
	pastar = { 6, 10 },             -- segundos no laco de Pastar (ramoneio no arbusto)
	beber = { 5, 8 },
	extrasRepouso = { "CocarCabeca", "Sacudir" },
	clipes = { pastarEntrar = "PastarEntrar", pastar = "Pastar", pastarSair = "PastarSair",
		beberEntrar = "BeberEntrar", beber = "Beber", beberSair = "BeberSair" },
}
C.especies.Javali.boca = { Fucar = Vector3.new(0, 0.07, -1.11), Farejar = Vector3.new(0, 0.16, -1.34), Beber = Vector3.new(0, 0.31, -1.62) }
C.especies.Javali.cascos = 1.3
C.especies.Javali.profMax = 0.9
C.especies.Javali.vivencia = {
	repouso = { 14, 24 },
	fucar = 2,                      -- repeticoes do Fucar (come bolotas, raizes e larvas)
	beber = 1,                      -- repeticoes do Beber (clipe de 5,2 s)
	clipes = { farejar = "Farejar", fucar = "Fucar", beber = "Beber" },
}
C.especies.Coruja.boca = { Beber = Vector3.new(0, 0.45, -0.55) }
C.especies.Coruja.profMax = 0.7
C.especies.Coruja.vivencia = {
	observar = { 10, 18 },          -- no galho de vigia antes de cacar
	repouso = { 16, 26 },           -- cochilo no poleiro abrigado
	aguaCadaCiclos = 3,             -- visita ocasional a agua (atributo ForcarAgua=true antecipa; TempoTeste acelera)
	presaRespawn = 20,              -- o roedor de TESTE reaparece depois disto (s)
	clipes = { olharE = "OlharE", olharD = "OlharD", inclinar = "InclinarCabeca", espreitar = "Espreitar", piar = "Piar",
		mergulho = "MergulhoCaca", comer = "Comer", decolarCalmo = "Decolar", beber = "Beber",
		adormecer = "Adormecer", dormindo = "Dormindo", despertar = "Despertar", ajeitar = "AjeitarPenas" },
}

return C
