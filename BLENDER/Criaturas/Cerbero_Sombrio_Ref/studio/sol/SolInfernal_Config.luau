-- SolInfernal_Config (ModuleScript em ReplicatedStorage.SolInfernal) - PROTOTIPO do Sol Infernal do Cerbero Sombrio (26/11).
-- Numeros APROVADOS pelo usuario em 19/11 (DOCS/criaturas/cerbero-sombrio.md); queimadura 0,1x/s aprovada 26/11 [PROPOSTA ate o balanceamento].
-- Tudo [A TESTAR] no Roblox. Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/sol/
return {
	DanoBase = 17,               -- mordida basica do Cerbero (referencia dos multiplicadores)
	MultAlvo = 1.8,              -- alvo atingido
	MultExplosao = 1.0,          -- demais dentro do raio (nao acumula no alvo principal)
	RaioExplosao = 12,
	QueimaPorSegundo = 0.1,      -- x DanoBase, 3 ticks
	QueimaDuracao = 3,

	Carga = 3.37,                -- disparo no marcador "disparo" do clipe BolaInfernalR2 (carga visivel 3,35 s)
	CargaInicio = 0.5,           -- marcador "carga_inicio": a bola comeca a se formar
	CargaMax = 3.0,              -- marcador "carga_max": bola no tamanho cheio
	DuracaoClipe = 4.3,

	Velocidade = 30,             -- studs/s (aprovado no Blender r3b)
	CurvaGrausPorSeg = 130,
	Alcance = 50,
	RaioAcerto = 8,              -- visual 10
	RaioVisual = 10,
	RaioColisao = 2,             -- spherecast contra paredes e terreno (nao atravessa obstaculos)
	OrigemLocal = Vector3.new(0, 31.5, -15.5),  -- r3 26/11: ACIMA e um pouco a frente das 3 cabecas (como no Blender r3b: boca + R*0,55 a frente + R*1,55 acima)

	Recarga = 14,
	Energia = 35,                -- prototipo: sem barra de energia; so registrado no log
	AlcanceMira = 70,            -- alvo travado aceito ate esta distancia do Cerbero
	AlcanceComando = 60,         -- tecla de teste: jogador precisa estar ate esta distancia
	RecargaInterrompida = 0.5,   -- carga interrompida: a bola se desfaz e a recarga cai pela metade
}
