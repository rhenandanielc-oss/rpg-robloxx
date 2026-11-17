-- IA_FaunaFloresta/Sons (17/11/2026, r3: cervo e coruja com sorteio + fades; javali r2 aprovado) - sons dos animais do PILOTO (cervo, javali, coruja), tocados pelo SERVIDOR em Sounds
-- posicionais dentro do modelo (o cliente ouve em 3D pela distancia). So audio LICENCIADO da biblioteca Pro Sound Effects
-- do Creator Store. Volumes/tons/trechos [A TESTAR] pelo usuario (ninguem do lado da IA ouve o audio).
-- Gatilhos: mudanca de estado (Controlador:mudar -> Sons.estado), evento pontual (Sons.evento) e "vida" em repouso.
-- r2 (pedido do usuario 17/11: javali "mais natural e continuo, que acabe devagar, nao de repente"):
--   * todo som entra com fadeIn e sai com fadeOut (Tween no volume); nada termina cortado
--   * VOZ: um canal por animal; uma voz nova esmaece a anterior (nao corta) em vez de empilhar
--   * javali usa takes longos e graves (4-5 s, "Pitched Down Growls"), sorteados entre varios
--   * CAMADA continua: enquanto o javali esta tenso (Alerta/Encarar/Ameaca/Vigiar) um rosnado grave em laco entra devagar
--     por baixo e some devagar quando ele relaxa ou investe
-- Realismo: coruja nao vocaliza em alerta (fica quieta) e o voo e quase silencioso.
local TweenService = game:GetService("TweenService")
local S = {}

local function id(n) return "rbxassetid://" .. n end

-- som = {id | ids (sorteia), vol, tom (PlaybackSpeed), inicio (s), dur (s, opcional: comeca a esmaecer antes do fim do take),
--        fadeIn (s), fadeOut (s), varia (+-tom aleatorio), voz (true = canal de voz do animal), laco (true = Looped)}
S.biblioteca = {
	Cervo = {
		-- "Deer Lip Smack, Snort, Heavy Exhale, Mouth Purse" (Pro Sound Effects): sao bufos curtos por natureza (~1 s);
		-- r3: sorteio entre takes + leve entrada e cauda esmaecida, para o bufo nao terminar seco
		alerta = { ids = { id(9114037159), id(9114037338) }, vol = 0.7, tom = 1.0, varia = 0.05, fadeIn = 0.04, fadeOut = 0.55, voz = true },  -- bufo de atencao
		fuga = { id = id(9114037335), vol = 1.0, tom = 0.95, varia = 0.03, fadeIn = 0.02, fadeOut = 0.5, voz = true },     -- Lip Smack 4: bufo de alarme
		vida = { ids = { id(9114037338), id(9114037159) }, vol = 0.32, tom = 0.97, varia = 0.06, fadeIn = 0.08, fadeOut = 0.6, voz = true },   -- resfolego calmo
	},
	Javali = {
		-- Pig Grunts 13/14/15 "Pitched Down Growls, Lethargic" (4,9/4,3/4,7 s): grunhido grave arrastado em repouso
		vida = { ids = { id(9117348597), id(9117350926), id(9117348727) }, vol = 0.45, tom = 0.85, varia = 0.05,
			fadeIn = 0.3, fadeOut = 1.4, voz = true },
		-- Pig Grunts 12 "Pitched Down Growls" (3,8 s): percebeu algo, grunhido mais firme
		alerta = { id = id(9117350831), vol = 0.7, tom = 0.88, varia = 0.04, fadeIn = 0.15, fadeOut = 1.2, voz = true },
		-- Pig Grunts 8 "Pitched Down, Deep, Menacing" (4,1 s): rosnado de ameaca
		ameaca = { id = id(9117358017), vol = 1.0, tom = 0.85, varia = 0.03, fadeIn = 0.2, fadeOut = 1.3, voz = true },
		-- investida: o mesmo rosnado grave, mais rapido e forte (no lugar do guincho de porco domestico da r1)
		investida = { id = id(9117358017), vol = 1.0, tom = 1.0, varia = 0.03, fadeIn = 0.08, dur = 2.4, fadeOut = 0.9, voz = true },
		chifrada = { id = id(9113470802), vol = 0.9, tom = 0.95, fadeOut = 0.6 },                       -- Body Fall Heavy Rustle 2: baque
		-- Pig Grunts 2 "Pitched Down, Deep, Menacing" (1,0 s): grunhido no golpe
		chifradaVoz = { id = id(9117357588), vol = 0.95, tom = 0.82, varia = 0.04, fadeOut = 0.5, voz = true },
		-- Pig Grunts 10 "Pitched Down Growls" (3,3 s): resmungo baixo andando de volta
		retorno = { id = id(9117350556), vol = 0.4, tom = 0.88, varia = 0.06, fadeIn = 0.3, fadeOut = 1.4, voz = true },
		-- camada continua de tensao: Pig Grunts 2 "Pitched Down Growls, Lethargic" (3,9 s) em laco, bem baixa
		tensao = { id = id(9117345997), vol = 0.32, tom = 0.78, fadeIn = 1.0, fadeOut = 1.6, laco = true },
	},
	Coruja = {
		-- r3: sorteio entre os 6 takes "Owl Hooting, Reverberant, Dry" (Several 1..6, 7,4-8,8 s); toca ~4,5 s e esmaece 1,6 s
		vida = { ids = { id(9117181035), id(9117181273), id(9117181271), id(9117181321), id(9117181543), id(9117181539) },
			vol = 0.6, tom = 1.0, dur = 4.5, fadeIn = 0.1, fadeOut = 1.6, varia = 0.03, voz = true },
		decolagem = { id = id(9113444620), vol = 0.22, tom = 0.7, varia = 0.04, fadeIn = 0.1, fadeOut = 0.9 },   -- Bird Wing Flaps Pigeon Two 1, grave e baixo
		pouso = { id = id(9113444792), vol = 0.18, tom = 0.72, dur = 1.4, fadeIn = 0.05, fadeOut = 0.8 },        -- Bird Wing Flaps Small Two 1
	},
}

-- estado -> som (tocado ao ENTRAR no estado)
S.porEstado = {
	Cervo = { Alerta = "alerta", Fuga = "fuga" },
	Javali = { Alerta = "alerta", Ameaca = "ameaca", Investida = "investida", Retorno = "retorno" },
	Coruja = { Decolagem = "decolagem", Pouso = "pouso" },
}
-- camada continua por estado (entra/sai com fade): {som, estados}
S.camada = {
	Javali = { som = "tensao", estados = { Alerta = true, Encarar = true, Ameaca = true, Vigiar = true } },
}
-- "vida" em repouso: intervalo aleatorio [min, max] s; so nesses estados
S.vida = {
	Cervo = { estados = { Repouso = true }, min = 14, max = 28 },
	Javali = { estados = { Repouso = true }, min = 7, max = 15 },
	Coruja = { estados = { Pousada = true }, min = 12, max = 26 },
}
S.alcance = { min = 10, max = 140 }   -- RollOff (studs): ate 'min' volume cheio; some em 'max'

local function fonte(m)
	return m:FindFirstChild("Javali_Cabeca", true) or m:FindFirstChild("Cervo_Cabeca", true) or m:FindFirstChild("Coruja_Cabeca", true)
		or m:FindFirstChild("RootPart") or m.PrimaryPart
end

local rng = Random.new()
local vozes = setmetatable({}, { __mode = "k" })     -- modelo -> Sound da voz atual
local camadas = setmetatable({}, { __mode = "k" })   -- modelo -> Sound da camada continua

-- esmaece e destroi (nunca corta seco)
local function apagar(s, t)
	if not s or not s.Parent or s:GetAttribute("Apagando") then return end
	s:SetAttribute("Apagando", true)
	local tw = TweenService:Create(s, TweenInfo.new(math.max(0.05, t or 0.4), Enum.EasingStyle.Sine, Enum.EasingDirection.Out), { Volume = 0 })
	tw.Completed:Connect(function() s:Destroy() end)
	tw:Play()
end
S.apagar = apagar

local function criar(m, d, nome)
	local p = fonte(m); if not p then return nil end
	local s = Instance.new("Sound"); s.Name = "Som_" .. nome
	s.SoundId = d.ids and d.ids[rng:NextInteger(1, #d.ids)] or d.id
	s.PlaybackSpeed = (d.tom or 1) * (1 + rng:NextNumber(-1, 1) * (d.varia or 0))
	s.RollOffMode = Enum.RollOffMode.InverseTapered; s.RollOffMinDistance = S.alcance.min; s.RollOffMaxDistance = S.alcance.max
	s.TimePosition = d.inicio or 0; s.Looped = d.laco == true
	s.Volume = (d.fadeIn and d.fadeIn > 0) and 0 or (d.vol or 1)
	s.Parent = p
	s:Play()
	if d.fadeIn and d.fadeIn > 0 then
		TweenService:Create(s, TweenInfo.new(d.fadeIn, Enum.EasingStyle.Sine, Enum.EasingDirection.Out), { Volume = d.vol or 1 }):Play()
	end
	return s
end

-- toca uma vez; entra/sai com fade. Voz nova esmaece a voz anterior do mesmo animal.
function S.tocar(m, especie, nome)
	local d = S.biblioteca[especie] and S.biblioteca[especie][nome]
	if not d then return nil end
	if d.voz and vozes[m] then apagar(vozes[m], 0.5) end
	local s = criar(m, d, nome); if not s then return nil end
	if d.voz then vozes[m] = s end
	m:SetAttribute("UltimoSom", nome)
	local fo = d.fadeOut or 0.3
	task.spawn(function()
		if not s.IsLoaded then s.Loaded:Wait() end
		local tam = d.dur or math.max(0.1, s.TimeLength - (d.inicio or 0))
		local real = tam / s.PlaybackSpeed
		if not d.dur then fo = math.min(fo, real * 0.45) end    -- take curto (bufo): so a cauda esmaece, o corpo do som fica inteiro
		task.wait(math.max(0, real - fo))      -- comeca a esmaecer 'fo' s antes do fim
		if vozes[m] == s then vozes[m] = nil end
		apagar(s, fo)
	end)
	return s
end

-- camada continua (laco): liga/desliga conforme o estado
local function camada(k, estado)
	local C = S.camada[k.especie]; if not C then return end
	local quer = C.estados[estado] == true
	local atual = camadas[k.m]
	if quer and not (atual and atual.Parent and not atual:GetAttribute("Apagando")) then
		camadas[k.m] = criar(k.m, S.biblioteca[k.especie][C.som], C.som)
	elseif not quer and atual then
		camadas[k.m] = nil; apagar(atual, S.biblioteca[k.especie][C.som].fadeOut)
	end
end

-- chamado pelo Controlador ao mudar de estado
function S.estado(k, estado)
	camada(k, estado)
	local nome = S.porEstado[k.especie] and S.porEstado[k.especie][estado]
	if nome then S.tocar(k.m, k.especie, nome) end
end

-- evento pontual (ex.: "chifrada")
function S.evento(k, ev)
	if ev == "chifrada" then
		S.tocar(k.m, k.especie, "chifrada"); S.tocar(k.m, k.especie, "chifradaVoz")
	else S.tocar(k.m, k.especie, ev) end
end

-- laco de "vida": um fio por animal; toca o som de repouso de tempos em tempos enquanto o estado permitir
function S.iniciarVida(k)
	local V = S.vida[k.especie]; if not V then return end
	task.spawn(function()
		local prox = os.clock() + rng:NextNumber(3, V.min)
		while k:vivo() do
			task.wait(0.5)
			if V.estados[k.estado] then
				if os.clock() >= prox then S.tocar(k.m, k.especie, "vida"); prox = os.clock() + rng:NextNumber(V.min, V.max) end
			else prox = math.max(prox, os.clock() + 4) end      -- ao voltar ao repouso espera um pouco antes do 1o som
		end
		if camadas[k.m] then apagar(camadas[k.m], 1.0); camadas[k.m] = nil end
	end)
end

return S
