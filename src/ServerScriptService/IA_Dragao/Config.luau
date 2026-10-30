-- IA_Dragao/Config — valores de CALIBRACAO para o ambiente de teste (nao sao numeros oficiais aprovados).
-- Distancias em studs, tempos em segundos, taxas por segundo, angulos em graus.
return {
	-- percepcao em torno do NINHO
	vigilancia = 230,          -- nivel 1: presenca registrada se houver linha de visao (ou perto o bastante)
	critica = 75,              -- nivel 2: ameaca confirmada
	furtivoFator = 0.6,        -- jogador furtivo (atributo Furtivo ou andando devagar) reduz o raio de vigilancia
	velocidadeFurtiva = 9,     -- WalkSpeed <= isto conta como furtivo
	lembrarAmeaca = 8,         -- segundos que a ameaca continua valendo depois de sair da vigilancia
	observarDist = 140,        -- jogador perto do DRAGAO (fora do ninho): so observa
	-- defesa
	distGuarda = 26,           -- distancia do ovo onde o dragao se posiciona (entre ovo e invasor)
	distAtaque = 45,           -- invasor nesta distancia do dragao -> solicita ataque ao sistema de combate
	intervaloAtaque = 3,
	perseguicaoMax = 330,      -- distancia maxima do NINHO durante uma perseguicao
	territorio = 520,          -- raio do territorio em torno do ninho
	-- locomocao (clipes sao no lugar; velocidades casadas com os clipes)
	andarVel = 3.2, andarRitmo = 1.5,       -- clipe Andar calibrado a 3,2 studs/s -> 4,8 studs/s
	correrVel = 13, correrRitmo = 1.3,      -- clipe Correr calibrado a 13 studs/s -> ~17 studs/s
	vooVel = 34, vooRapidoVel = 55,
	giroAndar = 26, giroCorrer = 38, giroVoo = 42, giroParado = 40,
	alturaCruzeiro = 48, folgaVoo = 34, vSubida = 24,
	inclinacaoMax = 0.6,       -- rampa maxima a pe (dy/dx)
	tetoMinVoo = 140,          -- precisa de ceu livre acima para decolar/voar
	distPreferirVoo = 260,     -- acima disto, ir voando se o caminho a pe for longo
	-- rotina e necessidades (0..1)
	fomeTaxa = 1 / 300, sedeTaxa = 1 / 220, sonoTaxa = 1 / 500,
	limiarNecessidade = 0.7,
	tempoMinEstado = 4,
	-- coleta do ovo
	coletaSegundos = 4, coletaDist = 16,
	-- frequencia de decisao
	tickCalmo = 1.0, tickAtivo = 0.25, distJogadorAtivo = 600,
	-- LOD comportamental: sem jogador a menos de distJogadorLonge, decide a cada tickDormente e so rotinas paradas
	-- (eventos do ninho/ataque acordam a IA na hora: 'urgente')
	tickDormente = 2.5, distJogadorLonge = 1500,
	-- espaco pessoal (vale fora do ninho): perto e visivel -> alerta; muito perto por toleranciaProximo s -> defesa propria
	espacoPessoal = 75, espacoCritico = 34, toleranciaProximo = 4,
	-- investigacao da ultima posicao de uma presenca que sumiu (janela para comecar, tempo farejando/olhando)
	investigarJanela = 40, investigarTempo = 7,
	-- a IA pede ataque ate distAtaqueMax (alem de distAtaque exige linha de visao); o Combate escolhe golpe/habilidade
	distAtaqueMax = 150,
	-- convivencia: distancia minima entre destinos/posicoes de dragoes diferentes (patrulha, poleiros)
	distEntreDragoes = 90,
	-- DERROTAVEL (usuario 30/10): vida, recuperacao apos derrota, regeneracao fora de combate (sem dano ha regenApos s)
	vidaGuardiao = 600, tempoRecuperacao = 120, regenVida = 2, regenApos = 20,
	-- combate aereo: alvo a mais de alturaAlvoNoAr acima do chao = voando; distancia mantida na perseguicao
	alturaAlvoNoAr = 22, distCombateAr = 38,
}
