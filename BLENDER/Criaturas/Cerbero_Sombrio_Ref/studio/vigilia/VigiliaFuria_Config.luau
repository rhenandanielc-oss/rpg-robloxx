-- VigiliaFuria_Config (ModuleScript em ReplicatedStorage.VigiliaFuria) - PROTOTIPO da Vigilia (passiva) e da Furia do Cerbero (26/11).
-- Oficial (REFERENCIAS_PODERES_E_EFEITOS.md): Rugido Infernal - inimigos a 25 studs (inclusive no ar) -15% de velocidade e -15% de dano
-- por 4 s; Furia - 8 s com +20% de dano e +15% de velocidade de ataque; recarga 30 s, energia 40.
-- Vigilia - enxerga criaturas invisiveis a ate 15 studs (pupilas brilham 1 s; contorno so para o dono); -50% no atordoamento recebido.
-- Decisoes 26/11: Furia com tudo que da para testar (a velocidade de ataque e as cabecas independentes ficam para a mordida basica);
-- 3 faixas de vento no tronco + estouro de fogo em cada boca no rugido; boneco invisivel; pontos de brilho nos 6 olhos.
-- Valores [A TESTAR] no Roblox. Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/vigilia/
return {
	-- Furia / Rugido Infernal
	RaioRugido = 25,
	RugidoLentidao = 0.15,
	RugidoMultDano = 0.85,       -- dano causado pelos afetados (marcado; nao ha ataque de inimigo no place)
	RugidoDuracao = 4,
	FuriaDuracao = 8,
	FuriaMultDano = 1.2,         -- aplicado no Sol Infernal e na Investida (atributo MultDano no Cerbero)
	FuriaVelAtaque = 1.15,       -- PENDENTE: mordida basica ainda nao existe no Studio
	FuriaFade = 1.5,             -- ultimo 1,5 s volta ao normal
	Recarga = 30,
	Energia = 40,                -- prototipo: so no log
	AlcanceComando = 60,
	-- marcadores do clipe FuriaRugidoR4 (2,9 s): rugido de cada cabeca e entrada na Furia
	Rugidos = {{"C", 0.27}, {"E", 0.97}, {"D", 1.67}},
	EntraFuria = 2.9,

	-- Vigilia
	RaioVigilia = 15,            -- medido da cabeca mais proxima ate o centro da criatura invisivel
	PupilasDuracao = 1,
	ReducaoAtordoamento = 0.5,   -- PENDENTE: nao ha atordoamento no place (so atributo)
	-- pontos das pupilas (medidos no Blender em repouso, studio/vigilia/olhos.json), em relacao ao RootPart (frente = -Z)
	Olhos = {
		{"CabecaC", Vector3.new(-0.321, 17.616, -10.488)}, {"CabecaC", Vector3.new(0.901, 17.616, -10.716)},
		{"CabecaE", Vector3.new(5.272, 15.064, -10.71)}, {"CabecaE", Vector3.new(6.282, 15.064, -9.99)},
		{"CabecaD", Vector3.new(-5.616, 15.546, -8.118)}, {"CabecaD", Vector3.new(-5.026, 15.546, -9.209)},
	},
}
