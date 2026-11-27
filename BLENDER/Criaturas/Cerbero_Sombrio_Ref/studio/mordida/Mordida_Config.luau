-- Mordida_Config (ModuleScript em ReplicatedStorage.MordidaCerbero) - PROTOTIPO da mordida basica do Cerbero + poder ativo (27/11).
-- Oficial: mordida basica 17, corpo a corpo [v4]; Furia +15% de velocidade de ataque e cabecas independentes.
-- Decisoes 26/11: a cabeca (C, E ou D) mais perto do alvo morde (clipes em camada MordidaC/E/D, anda mordendo); intervalo 0,8 s
-- [PROPOSTA]; na Furia as 3 mordem sozinhas, cada uma o alvo mais perto dela; so mordidas (garras guardadas); um poder por vez
-- e a mordida bloqueada so na carga do Sol, no impacto/salto da Investida e no rugido (atributo MordidaBloqueada).
-- Valores [A TESTAR]. Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/mordida/
return {
	Dano = 17,
	Intervalo = 0.8,             -- entre mordidas (fora da Furia)
	VelAtaqueFuria = 1.15,       -- +15% na Furia: intervalo / 1,15 e clipe 1,15x mais rapido
	TempoContato = 0.30,         -- marcador "contato" dos clipes MordidaC/E/D (0,8 s)
	-- ponto de contato de cada boca: mandibula (pose de repouso, que e o que o servidor enxerga) + alcance a frente
	Alcance = 3.5,               -- studs a frente da mandibula
	RaioContato = 3.5,
	BuscaAlvo = 14,              -- clique sem alvo valido: procura o inimigo mais perto das bocas ate esta distancia
	BuscaFuria = 7,              -- Furia: cada cabeca so morde o que estiver a ate 7 studs da boca dela
	AlcanceComando = 60,
	Cabecas = {"C", "E", "D"},
}
