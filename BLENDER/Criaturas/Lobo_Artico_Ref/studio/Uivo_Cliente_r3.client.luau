-- Uivo_Cliente (Script com RunContext = Client, Workspace.Teste_LoboArtico) - efeitos do UIVO BOREAL (r3, 16/11/2026).
-- So cosmetico: le os atributos do Uivo_Servidor e nunca decide nada.
-- r3 segue REFERENCIAS_PODERES_E_EFEITOS.md v5.2 §5.1/§5.3 (decisoes do usuario de 16/11):
--   * TUDO NO CORPO; fora do corpo SO neve levada pelo vento circulando (faixas finas em espiral, na frente e atras).
--   * Rosto limpo; olhos azul-gelo brilhando por conta propria.
--   * Duracao = duracao do buff (UivoAtivoFim), com fade-out no ultimo 1,5 s; pico no uivo.
--   * Som: uivo agudo + vento cortante + tilintar de gelo (sons Pro Sound Effects ja usados no kit Gelo do place).
--   * Alvos com lentidao (Lentidao_Boreal_Fim): geada no corpo do alvo enquanto durar.
-- Feito agora: cristais do dorso acendem em azul-gelo (Highlight so no LOW_Cristais, sem contorno), olhos, neve em orbita,
-- sons e geada nos alvos. PENDENTE (precisa de textura/malha nova): linhas azul-gelo continuas pelo corpo ("capa de
-- efeito" com UV do pelo), espinhos de gelo que CRESCEM do pelo e a pelicula de geada no dorso.
-- r2 (neutro, 16/11) tinha nevoa saindo da boca e luz no ombro: removidas (ferem "nada sai do corpo"). Copia: Uivo_Cliente_r2_neutro.
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW")
local function osso(n) return lobo:FindFirstChild(n, true) end
local cab = osso("Cabeca")
while not cab do task.wait(0.25); cab = osso("Cabeca") end     -- streaming: espera os ossos
local raiz = lobo:WaitForChild("RootPart")
local cristais = lobo:WaitForChild("LOW_Cristais", 10) or lobo:FindFirstChild("LOW_Cristais", true)

local GELO = Color3.fromRGB(165, 222, 255)
local NEVE = Color3.fromRGB(240, 248, 255)
local function id(n) return "rbxassetid://" .. n end
local SONS = {uivo = id(9120790529), vento = id(9125742111), tinido = id(9114590297), cristais = id(9114858178)}

-- pontos no corpo (Bone sem peso, so no cliente)
local function ponto(pai, nome, pos)
	local b = pai:FindFirstChild(nome) or Instance.new("Bone")
	b.Name = nome; b.CFrame = CFrame.new(pos); b.Parent = pai
	return b
end
local pNariz = ponto(cab, "FX_Nariz", Vector3.new(0, 1.565, 0))
-- limpa o que a r2 deixou (nevoa da boca e luz do ombro) caso exista
for _, n in ipairs({"FX_Boca", "FX_Marca"}) do local b = lobo:FindFirstChild(n, true); if b then b:Destroy() end end

-- sons --------------------------------------------------------------------------------------------------------------
local function som(nome, sid, vol, tom, pai)
	local s = pai:FindFirstChild(nome) or Instance.new("Sound")
	s.Name = nome; s.SoundId = sid; s.Volume = vol; s.PlaybackSpeed = tom
	s.RollOffMode = Enum.RollOffMode.InverseTapered; s.RollOffMinDistance = 12; s.RollOffMaxDistance = 220
	s.Parent = pai
	return s
end
local sUivo = som("Som_Uivo", SONS.uivo, 0.8, 1.12, pNariz)            -- agudo
local sVento = som("Som_Vento", SONS.vento, 0, 1.25, raiz); sVento.Looped = true   -- vento cortante (mais agudo)
local sTinido = som("Som_Tinido", SONS.tinido, 0.35, 1.3, raiz)
local sCristais = som("Som_Cristais", SONS.cristais, 0.3, 1.1, raiz)

-- cristais do dorso: brilho azul-gelo (so a malha dos cristais; sem contorno = sem halo) -----------------------------
local hl = Instance.new("Highlight")
hl.Name = "Brilho_Cristais"; hl.Adornee = cristais; hl.FillColor = GELO; hl.FillTransparency = 1
hl.OutlineTransparency = 1; hl.DepthMode = Enum.HighlightDepthMode.Occluded; hl.Enabled = false
hl.Parent = cristais

-- olhos azul-gelo (pequenos pontos Neon presos aos ossos das palpebras) ---------------------------------------------
local olhos = {}
for _, lado in ipairs({{"Palpebra_Sup_E", -0.07}, {"Palpebra_Sup_D", 0.07}}) do
	local b = osso(lado[1])
	if b then
		local p = Instance.new("Part")
		p.Name = "Olho_Boreal"; p.Shape = Enum.PartType.Ball; p.Size = Vector3.new(0.14, 0.14, 0.14)
		p.Material = Enum.Material.Neon; p.Color = GELO; p.Transparency = 1
		p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
		p.Parent = lobo
		table.insert(olhos, {p = p, b = b, dx = lado[2]})
	end
end

-- neve levada pelo vento em orbita (8 faixas finas, alturas diferentes, na frente e atras do corpo) ------------------
local orbita = Instance.new("Part")
orbita.Name = "Orbita_Boreal"; orbita.Transparency = 1; orbita.Size = Vector3.new(0.2, 0.2, 0.2)
orbita.Anchored = true; orbita.CanCollide = false; orbita.CanQuery = false; orbita.CanTouch = false; orbita.Parent = lobo
local faixas = {}
local N = 8
for i = 1, N do
	local a0 = Instance.new("Attachment"); a0.Parent = orbita
	local a1 = Instance.new("Attachment"); a1.Parent = orbita
	local tr = Instance.new("Trail")
	tr.Attachment0 = a0; tr.Attachment1 = a1; tr.Color = ColorSequence.new(NEVE, GELO)
	tr.Lifetime = 0.45; tr.LightEmission = 0.2; tr.LightInfluence = 0.8; tr.FaceCamera = true
	tr.Transparency = NumberSequence.new(1); tr.Enabled = false; tr.Parent = orbita
	local pe = Instance.new("ParticleEmitter")
	pe.Texture = "rbxasset://textures/particles/sparkles_main.dds"; pe.Color = ColorSequence.new(NEVE)
	pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.09), NumberSequenceKeypoint.new(1, 0.02)})
	pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.3), NumberSequenceKeypoint.new(1, 1)})
	pe.Lifetime = NumberRange.new(0.25, 0.45); pe.Speed = NumberRange.new(0.2, 0.6); pe.Rate = 0
	pe.LightEmission = 0.3; pe.LockedToPart = false; pe.Parent = a0
	faixas[i] = {a0 = a0, a1 = a1, tr = tr, pe = pe,
		fase = (i - 1) / N * math.pi * 2, altura = 1.3 + (i % 4) * 1.15, vel = 2.2 + (i % 3) * 0.35, sobe = (i % 2 == 0) and 1 or -1}
end

-- geada nos alvos com lentidao -----------------------------------------------------------------------------------------
local geadas = {}
local function atualizarGeada()
	local centro = lobo:GetPivot().Position
	for m, h in pairs(geadas) do
		local fim = m.Parent and m:GetAttribute("Lentidao_Boreal_Fim")
		if not fim or fim <= workspace:GetServerTimeNow() then h:Destroy(); geadas[m] = nil end
	end
	for _, d in ipairs(workspace:GetChildren()) do
		local function olhar(m)
			if m:IsA("Model") and m ~= lobo and m:GetAttribute("Lentidao_Boreal_Fim") and not geadas[m] then
				local piv = m:GetPivot().Position
				if (piv - centro).Magnitude < 60 then
					local h = Instance.new("Highlight"); h.Name = "Geada_Boreal"; h.Adornee = m
					h.FillColor = GELO; h.FillTransparency = 0.72; h.OutlineTransparency = 1
					h.DepthMode = Enum.HighlightDepthMode.Occluded; h.Parent = m
					geadas[m] = h
				end
			end
		end
		olhar(d)
		if d:IsA("Folder") or (d:IsA("Model") and not d:FindFirstChildOfClass("Humanoid")) then
			for _, c in ipairs(d:GetChildren()) do olhar(c) end
		end
	end
end
task.spawn(function() while lobo.Parent do atualizarGeada(); task.wait(0.25) end end)

-- fases do uivo (som) ----------------------------------------------------------------------------------------------
local faseAtual = ""
local function fadeOut(s, t)
	if not s.IsPlaying then return end
	local tw = TweenService:Create(s, TweenInfo.new(t), {Volume = 0}); tw:Play()
	tw.Completed:Once(function(st) if st == Enum.PlaybackState.Completed then s:Stop() end end)
end
local tPico = -100
lobo:GetAttributeChangedSignal("UivoFase"):Connect(function()
	local f = lobo:GetAttribute("UivoFase") or ""
	if f == faseAtual then return end
	faseAtual = f
	if f == "Uivando" then
		local atraso = math.clamp(workspace:GetServerTimeNow() - (lobo:GetAttribute("UivoFaseT") or 0), 0, 1)
		sUivo.Volume = 0.8; sUivo.TimePosition = atraso; sUivo:Play()
		sTinido.TimePosition = 0; sTinido:Play()
		tPico = os.clock() - atraso
	elseif f == "Uivar" then
		sCristais.Volume = 0.3; sCristais.TimePosition = 0; sCristais:Play()      -- espinhos "acordando"
	elseif f == "PararUivar" then
		fadeOut(sUivo, 0.5)
	else
		fadeOut(sUivo, 0.25); fadeOut(sCristais, 0.25)
	end
end)

-- quadro a quadro: intensidade do efeito (fade-in 0,6 s, pico no uivo, fade-out no ultimo 1,5 s) ----------------------
local ligado = false
RunService.RenderStepped:Connect(function()
	local agora = workspace:GetServerTimeNow()
	local fim = lobo:GetAttribute("UivoAtivoFim") or 0
	local dur = lobo:GetAttribute("UivoDur") or 8
	local resta = fim - agora
	local ativo = resta > 0 and (lobo:GetAttribute("MultVelocidade") or 1) > 1
	if not ativo then
		if ligado then
			ligado = false; hl.Enabled = false
			for _, o in ipairs(olhos) do o.p.Transparency = 1 end
			for _, fx in ipairs(faixas) do fx.tr.Enabled = false; fx.pe.Rate = 0 end
			fadeOut(sVento, 0.3)
		end
		return
	end
	if not ligado then
		ligado = true; hl.Enabled = true
		for _, fx in ipairs(faixas) do fx.tr.Enabled = true end
		sVento.Volume = 0; sVento:Play()
	end
	local decorrido = dur - resta
	local env = math.clamp(decorrido / 0.6, 0, 1) * math.clamp(resta / 1.5, 0, 1)
	local pico = math.max(0, 1 - math.abs(os.clock() - tPico - 0.4) / 0.9)       -- sobe por um instante no uivo
	local pulso = 0.5 + 0.5 * math.sin(os.clock() * math.pi * 2 / 1.5)          -- 1,5 s
	-- cristais: discreto (0,62-0,52) com pico (0,30)
	hl.FillTransparency = 1 - env * (0.38 + 0.10 * pulso + 0.32 * pico)
	-- olhos
	for _, o in ipairs(olhos) do
		local cf = o.b.TransformedWorldCFrame
		o.p.CFrame = cf * CFrame.new(o.dx, 0, 0)
		o.p.Transparency = 1 - env * (0.55 + 0.35 * pico)
	end
	-- neve em orbita: elipse em volta do corpo (frente -Z), espiral suave
	local pv = lobo:GetPivot()
	orbita.CFrame = pv * CFrame.new(0, 0, -0.6)
	local t = os.clock()
	local tr = NumberSequence.new({NumberSequenceKeypoint.new(0, 1 - 0.55 * env), NumberSequenceKeypoint.new(1, 1)})
	for _, fx in ipairs(faixas) do
		local th = fx.fase + t * fx.vel
		local h = fx.altura + 0.55 * math.sin(t * 1.3 * fx.sobe + fx.fase)
		local p = Vector3.new(math.cos(th) * 3.4, h, math.sin(th) * 6.0)
		fx.a0.Position = p; fx.a1.Position = p + Vector3.new(0, 0.12, 0)
		fx.tr.Transparency = tr
		fx.pe.Rate = 10 * env
	end
	sVento.Volume = 0.32 * env
end)
