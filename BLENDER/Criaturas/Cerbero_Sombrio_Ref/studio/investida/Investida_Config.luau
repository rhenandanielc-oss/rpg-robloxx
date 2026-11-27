-- Investida_Config (ModuleScript em ReplicatedStorage.InvestidaSombria) - PROTOTIPO da Investida Sombria do Cerbero (26/11).
-- Oficial (REFERENCIAS_PODERES_E_EFEITOS.md): impulso ~12 studs em 0,5 s, depois +40% de velocidade por 4 s com direcao livre;
-- rastro de sombra 3 s que reduz 15% a velocidade de quem pisa; recarga 12 s, energia 25.
-- Aprovado 20/11 (r5): alvo ate metade do porte = passa por cima (1,0x); alvo maior = para + impacto 0,6x + mordidas C/E/D 0,7x (2,7x).
-- Decisao 26/11: alvo MEDIO (entre metade e o tamanho do Cerbero) tambem para e morde (2,7x); porte = altura do corpo vs cernelha.
-- Valores [A TESTAR] no Roblox. Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/investida/
return {
	DanoBase = 17,
	MultPassagem = 1.0,         -- alvo pequeno: passa por cima
	MultImpacto = 0.6,          -- alvo medio/maior: impacto no contato
	MultMordida = 0.7,          -- cada uma das 3 mordidas (C, E, D)

	Cernelha = 13.72,           -- porte do Cerbero (topo do dorso, Coluna2)
	LimitePequeno = 0.5,        -- altura do alvo <= 50% da cernelha = pequeno

	ImpulsoDistancia = 12,      -- studs
	ImpulsoDuracao = 0.5,       -- entre os marcadores "impulso" (0,40) e "fim_impulso" (0,90) do clipe InvestidaR3
	ImpulsoInicio = 0.40,
	VelocidadeBase = 22,        -- corrida do Cerbero (previa do Blender 22,3) [A TESTAR]
	BoostMult = 1.4,            -- +40%
	BoostDuracao = 4,
	VelocidadeSobre = 22.3,     -- velocidade do clipe InvestidaSobre
	CurvaGrausPorSeg = 180,     -- direcao livre durante o boost (tecla de teste: segue o mouse)

	-- deteccao a frente (distancias a partir do pivo do Cerbero, no sentido da corrida)
	GatilhoSobre = 18,          -- alvo pequeno: o clipe comeca aqui (decolagem das dianteiras ~5 studs antes do alvo)
	GatilhoImpacto = 12.5,      -- alvo medio/maior: frente do focinho encosta
	LarguraBusca = 7,           -- meia largura do corredor de busca
	GatilhoParede = 13,         -- para antes de atravessar paredes

	TempoApiceSobre = 1.13,     -- dano da passagem no apice do salto
	TempoImpacto = 0.13,        -- "absorve"
	TemposMordida = {0.47, 0.53, 0.57},   -- mordida_C, mordida_E, mordida_D
	DuracaoSobre = 2.67,
	DuracaoImpacto = 1.9,

	RastroPasso = 2.5,          -- um trecho de rastro a cada 2,5 studs
	RastroDuracao = 3,
	RastroRaio = 3,
	RastroLentidao = 0.15,

	Recarga = 12,
	Energia = 25,               -- prototipo: so no log
	AlcanceComando = 60,
}
