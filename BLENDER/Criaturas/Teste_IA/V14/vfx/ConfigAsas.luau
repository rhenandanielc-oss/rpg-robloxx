-- ConfigAsas (ModuleScript) — efeitos cosmeticos das asas por forma regional. Sem dano, energia ou estatisticas.
-- Cada camada: emissor pre-criado nos pontos da asa; 'por_evento' = particulas emitidas por marcador de animacao.
-- Valores sao artisticos (ajustaveis aqui sem mexer na logica).
local T = {
	faisca = "rbxasset://textures/particles/sparkles_main.dds",
	fumaca = "rbxasset://textures/particles/smoke_main.dds",
	fogo = "rbxasset://textures/particles/fire_main.dds",
}
local function seq(...) return ColorSequence.new(...) end
local function ns(a, b, c) return NumberSequence.new({NumberSequenceKeypoint.new(0, a), NumberSequenceKeypoint.new(0.5, b), NumberSequenceKeypoint.new(1, c)}) end

return {
	-- multiplicador por estado (nome do clipe contem a chave); clipes sem marcadores nao emitem nada
	estados = {Planeio = 0.15, Voo_Rapido = 1.2, Decolagem = 1.6, Pouso = 1.4, Voo = 1.0},
	-- eventos (marcadores) -> fator de intensidade
	eventos = {WingDownstrokeStart = 0.35, WingDownstrokePeak = 1.0, WingUpstroke = 0.15, WingGlide = 0.2, WingFold = 0.1,
		TakeoffImpulse = 1.8, LandingImpact = 1.5},
	lod = {perto = 120, longe = 300, teto_por_segundo = 90},
	escala = 4.5,   -- tamanho/velocidade das particulas proporcionais ao dragao (envergadura ~100 studs)
	formas = {
		Montanhas = {
			camadas = {
				{nome = "Faiscas", textura = T.faisca, cor = seq(Color3.fromRGB(255, 214, 120), Color3.fromRGB(255, 120, 30)),
					tamanho = ns(0.35, 0.25, 0), transp = ns(0, 0.2, 1), vida = NumberRange.new(0.4, 0.9), vel = NumberRange.new(6, 14),
					espalha = Vector2.new(35, 35), arrasto = 2.5, acel = Vector3.new(0, -6, 0), luz = 1, por_evento = 6},
				{nome = "Brasas", textura = T.faisca, cor = seq(Color3.fromRGB(255, 90, 20), Color3.fromRGB(120, 25, 5)),
					tamanho = ns(0.6, 0.45, 0.1), transp = ns(0.1, 0.4, 1), vida = NumberRange.new(1.0, 1.8), vel = NumberRange.new(2, 6),
					espalha = Vector2.new(60, 60), arrasto = 1.2, acel = Vector3.new(0, 1.5, 0), luz = 0.6, por_evento = 3},
			},
			poeira = {cor = seq(Color3.fromRGB(110, 95, 85), Color3.fromRGB(70, 60, 55)), por_evento = 10,
				materiais = {"Rock", "Basalt", "Ground", "Slate", "Sand", "Mud", "Grass", "LeafyGrass", "Pavement", "CrackedLava"}},
			brilho = {pulso_transp = 0.62, base_transp = 0.8, cor = nil},   -- pelicula de brilho existente (V14_Brilho_*)
		},
		Glacial = {
			camadas = {
				{nome = "Cristais", textura = T.faisca, cor = seq(Color3.fromRGB(230, 248, 255), Color3.fromRGB(150, 205, 255)),
					tamanho = ns(0.3, 0.22, 0), transp = ns(0.1, 0.3, 1), vida = NumberRange.new(0.6, 1.2), vel = NumberRange.new(4, 10),
					espalha = Vector2.new(40, 40), arrasto = 2.0, acel = Vector3.new(0, -3, 0), luz = 0.35, por_evento = 5},
				{nome = "Neve", textura = T.fumaca, cor = seq(Color3.fromRGB(240, 250, 255), Color3.fromRGB(200, 225, 245)),
					tamanho = ns(0.25, 0.4, 0.5), transp = ns(0.4, 0.6, 1), vida = NumberRange.new(0.8, 1.6), vel = NumberRange.new(2, 5),
					espalha = Vector2.new(70, 70), arrasto = 1.0, acel = Vector3.new(0, -1.5, 0), luz = 0, por_evento = 4},
				{nome = "Nevoa", textura = T.fumaca, cor = seq(Color3.fromRGB(205, 230, 255), Color3.fromRGB(180, 210, 240)),
					tamanho = ns(1.2, 2.2, 3.0), transp = ns(0.75, 0.85, 1), vida = NumberRange.new(0.5, 0.9), vel = NumberRange.new(1, 3),
					espalha = Vector2.new(25, 25), arrasto = 3.0, acel = Vector3.zero, luz = 0, por_evento = 1},
			},
			poeira = {cor = seq(Color3.fromRGB(240, 248, 255), Color3.fromRGB(210, 225, 240)), por_evento = 12,
				materiais = {"Snow", "Glacier", "Ice"}},
			brilho = {pulso_transp = 0.7, base_transp = 0.85, cor = Color3.fromRGB(150, 210, 255)},
		},
		Sombrio = {
			camadas = {
				{nome = "Fragmentos", textura = T.faisca, cor = seq(Color3.fromRGB(220, 90, 255), Color3.fromRGB(110, 20, 160)),
					tamanho = ns(0.35, 0.3, 0), transp = ns(0.05, 0.3, 1), vida = NumberRange.new(0.5, 1.0), vel = NumberRange.new(4, 11),
					espalha = Vector2.new(45, 45), arrasto = 2.0, acel = Vector3.new(0, -1, 0), luz = 0.5, por_evento = 5, giro = NumberRange.new(-180, 180)},
				{nome = "Sombra", textura = T.fumaca, cor = seq(Color3.fromRGB(35, 10, 45), Color3.fromRGB(10, 0, 15)),
					tamanho = ns(0.8, 1.6, 2.2), transp = ns(0.55, 0.75, 1), vida = NumberRange.new(0.6, 1.1), vel = NumberRange.new(1, 4),
					espalha = Vector2.new(50, 50), arrasto = 2.5, acel = Vector3.zero, luz = 0, por_evento = 2},
			},
			poeira = {cor = seq(Color3.fromRGB(60, 25, 70), Color3.fromRGB(20, 5, 25)), por_evento = 8, materiais = nil},  -- qualquer solo
			brilho = {pulso_transp = 0.6, base_transp = 0.82, cor = Color3.fromRGB(200, 60, 255), oscila = true},
		},
	},
}
