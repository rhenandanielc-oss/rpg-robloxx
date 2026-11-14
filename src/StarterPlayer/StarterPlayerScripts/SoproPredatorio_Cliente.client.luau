-- SoproPredatorio_Cliente (LocalScript, StarterPlayerScripts) — VISUAL, SOM e CABECA do Sopro Predatorio da Wyvern (so
-- cosmetico; o servidor decide cone, alcance, dano e duracao). Eventos do RemoteEvent Combate_Dragoes.FX do Sopro do
-- Nucleo, filtrados por hab = "Sopro", el = "Ar" e modelo com FormaRegional = "Wyvern":
--   preparo : inspiracao (som "Sniff Breathe In" grave) e ar sendo puxado para a boca (fios curtos convergindo).
--   emissao : JATO continuo e concentrado: nucleo branco translucido ESTREITO na boca que abre de leve ate o alcance do
--             servidor (o jato visual acaba onde a hitbox acaba), fitas de velocidade finas e um sopro aspero em laco
--             (lábios + pressao, tom mais alto que o do Gelo); a cabeca/pescoco seguem a MIRA viva (alvoPos).
--   mira    : nova mira (cursor do cavaleiro) -> o jato e a cabeca acompanham.
--   fim     : corta o jato aos poucos e solta uma expiracao curta.
-- Cabeca: por cima do clipe (PreSimulation, como a cauda da Ferroada) o giro ate a mira e distribuido por neck_03,
-- Pescoco4, neck_05 e Cabeca, limitado a +-40 graus de lado e +-25 de altura, entrando/saindo suave.
-- Custo: 1 ancora com 3 emissores e 2 sons por Wyvern soprando (reaproveitados entre sopros); preparo 1 emissor curto.
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Debris = game:GetService("Debris")
local FX = RS:WaitForChild("Combate_Dragoes"):WaitForChild("FX")
local function id(n) return "rbxassetid://" .. n end
local SOM = {inspira = {id(9119305128), id(9119305469)}, sopro = id(9126167059), pressao = id(9114437277),
	expira = {id(9113972744), id(9113971975)}}
local FUMACA = "rbxasset://textures/particles/smoke_main.dds"
local BRILHO = "rbxasset://textures/particles/sparkles_main.dds"
local BRANCO, GELO = Color3.fromRGB(255, 255, 255), Color3.fromRGB(205, 232, 250)
local PESCOCO = {{"neck_03", 0.15}, {"Pescoco4", 0.2}, {"neck_05", 0.25}, {"Cabeca", 0.4}}
local LIM_YAW, LIM_PITCH = math.rad(40), math.rad(25)
local W = {}                                         -- [modelo] = estado

local function ns(...) local a = {...}; local k = {}; for i = 1, #a, 2 do table.insert(k, NumberSequenceKeypoint.new(a[i], a[i + 1])) end; return NumberSequence.new(k) end
local function osso(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end
local function pasta()
	local f = workspace:FindFirstChild("VFX_Temporarios")
	if not f then f = Instance.new("Folder"); f.Name = "VFX_Temporarios"; f.Parent = workspace end
	return f
end
local function som(pai, sid, vol, tom, laco)
	local s = Instance.new("Sound"); s.SoundId = sid; s.Volume = vol; s.PlaybackSpeed = tom; s.Looped = laco == true
	s.RollOffMaxDistance = 140; s.RollOffMinDistance = 12; s.Parent = pai; s:Play()
	if not laco then Debris:AddItem(s, 6) end
	return s
end
local function sorteia(l) return l[math.random(1, #l)] end

local function estado(m)
	local s = W[m]
	if s and s.anc and s.anc.Parent then return s end
	s = s or {}; W[m] = s
	s.cab = osso(m, "Cabeca"); s.boca = osso(m, "mouth_upper_tip")
	s.ossos = {}; for i, x in ipairs(PESCOCO) do s.ossos[i] = osso(m, x[1]) end
	local anc = Instance.new("Part"); anc.Name = "SoproPredatorio_Ancora"; anc.Anchored = true; anc.CanCollide = false
	anc.CanQuery = false; anc.CanTouch = false; anc.Transparency = 1; anc.Size = Vector3.new(0.2, 0.2, 0.2); anc.Parent = pasta()
	local a = Instance.new("Attachment"); a.Parent = anc
	-- nucleo: estreito na boca e abrindo de leve (tamanho cresce com a vida da particula; pouca dispersao angular)
	local nucleo = Instance.new("ParticleEmitter"); nucleo.Texture = FUMACA; nucleo.Color = ColorSequence.new(BRANCO, GELO)
	nucleo.LightEmission = 0.35; nucleo.LightInfluence = 0.4; nucleo.Transparency = ns(0, 0.55, 0.15, 0.62, 0.8, 0.82, 1, 1)
	nucleo.Size = ns(0, 0.6, 0.5, 2.4, 1, 4.2); nucleo.SpreadAngle = Vector2.new(3, 3); nucleo.Drag = 0.6
	nucleo.Rotation = NumberRange.new(0, 360); nucleo.RotSpeed = NumberRange.new(-180, 180)
	nucleo.EmissionDirection = Enum.NormalId.Front; nucleo.Rate = 0; nucleo.Parent = a
	-- fitas de velocidade finas (o ar sob pressao)
	local linhas = Instance.new("ParticleEmitter"); linhas.Texture = BRILHO; linhas.Color = ColorSequence.new(BRANCO)
	linhas.LightEmission = 0.8; linhas.LightInfluence = 0; linhas.Transparency = ns(0, 0.3, 1, 1)
	linhas.Size = ns(0, 0.35, 1, 0.12); linhas.Orientation = Enum.ParticleOrientation.VelocityParallel; linhas.Squash = ns(0, 3, 1, 3)
	linhas.SpreadAngle = Vector2.new(5, 5); linhas.EmissionDirection = Enum.NormalId.Front; linhas.Rate = 0; linhas.Parent = a
	-- brisa na boca (abertura do jato)
	local boca = Instance.new("ParticleEmitter"); boca.Texture = FUMACA; boca.Color = ColorSequence.new(BRANCO)
	boca.LightEmission = 0.3; boca.Transparency = ns(0, 0.6, 1, 1); boca.Size = ns(0, 0.8, 1, 2.2)
	boca.Lifetime = NumberRange.new(0.12, 0.2); boca.Speed = NumberRange.new(8, 14); boca.SpreadAngle = Vector2.new(25, 25)
	boca.EmissionDirection = Enum.NormalId.Front; boca.Rate = 0; boca.Parent = a
	s.anc, s.a, s.nucleo, s.linhas, s.bocaE = anc, a, nucleo, linhas, boca
	s.yaw, s.pitch, s.w = 0, 0, 0
	m.AncestryChanged:Connect(function(_, p) if not p and W[m] then if W[m].anc then W[m].anc:Destroy() end; W[m] = nil end end)
	return s
end
local function posBoca(s, m)
	local cf = s.cab and s.cab.TransformedWorldCFrame
	if s.boca then return s.boca.TransformedWorldCFrame.Position, cf and cf.UpVector or m:GetPivot().LookVector end
	if cf then return cf.Position + cf.UpVector * 5, cf.UpVector end
	return m:GetPivot().Position, m:GetPivot().LookVector
end
local function ligarJato(s, ligado, alcance)
	if ligado then
		-- o nucleo percorre o alcance do servidor: d = v/drag*(1-e^(-drag*vida)) -> v para vida 0,55 s
		local vida = 0.55; local v = (alcance or 35) * 0.6 / (1 - math.exp(-0.6 * vida))
		s.nucleo.Lifetime = NumberRange.new(vida * 0.9, vida); s.nucleo.Speed = NumberRange.new(v * 0.95, v * 1.05)
		s.linhas.Lifetime = NumberRange.new(0.25, 0.35); s.linhas.Speed = NumberRange.new((alcance or 35) / 0.3, (alcance or 35) / 0.26)
		s.nucleo.Rate, s.linhas.Rate, s.bocaE.Rate = 140, 45, 40
	else
		s.nucleo.Rate, s.linhas.Rate, s.bocaE.Rate = 0, 0, 0
	end
end

local function parar(m, s)
	s.ativo = false; ligarJato(s, false)
	for _, k in ipairs({"somSopro", "somPressao"}) do
		local x = s[k]; s[k] = nil
		if x then task.spawn(function() for i = 1, 8 do if not x.Parent then return end; x.Volume *= 0.7; task.wait(0.04) end; x:Destroy() end) end
	end
end

FX.OnClientEvent:Connect(function(e)
	if type(e) ~= "table" or e.hab ~= "Sopro" or e.el ~= "Ar" then return end
	local m = e.d
	if typeof(m) ~= "Instance" or not m:IsA("Model") or m:GetAttribute("FormaRegional") ~= "Wyvern" then return end
	local s = estado(m)
	if e.fase == "preparo" then
		if s.cab then som(s.cab, sorteia(SOM.inspira), 0.85, 0.62) end           -- inspiracao (peito menor que o do dragao)
		-- ar puxado para a boca: fios curtos convergindo por ~0,9 s
		local b = posBoca(s, m)
		local p = Instance.new("Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.Transparency = 1
		p.Shape = Enum.PartType.Ball; p.Size = Vector3.new(6, 6, 6); p.Position = b; p.Parent = pasta()
		local f = Instance.new("ParticleEmitter"); f.Texture = BRILHO; f.Color = ColorSequence.new(GELO, BRANCO)
		f.LightEmission = 0.7; f.Shape = Enum.ParticleEmitterShape.Sphere; f.ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface
		f.ShapeInOut = Enum.ParticleEmitterShapeInOut.Inward; f.Speed = NumberRange.new(9, 12); f.Lifetime = NumberRange.new(0.25, 0.3)
		f.Orientation = Enum.ParticleOrientation.VelocityParallel; f.Size = ns(0, 0.4, 1, 0.12); f.Squash = ns(0, 2, 1, 2)
		f.Transparency = ns(0, 1, 0.3, 0.35, 1, 0.9); f.Rate = 30; f.Parent = p
		s.prep = p; Debris:AddItem(p, 1.4)
		task.delay(0.95, function() if f.Parent then f.Enabled = false end end)
	elseif e.fase == "emissao" then
		if s.prep then s.prep:Destroy(); s.prep = nil end
		s.ativo = true; s.alvo = e.alvoPos; s.alcance = e.alcance or 35
		ligarJato(s, true, s.alcance)
		local pai = s.cab or m.PrimaryPart
		if pai then
			s.somSopro = som(pai, SOM.sopro, 0.9, 0.82, true)                    -- labios: sopro forte
			s.somPressao = som(pai, SOM.pressao, 0.55, 1.35, true)                -- pressao aspera (mais aguda que a do Gelo)
		end
	elseif e.fase == "mira" then
		s.alvo = e.alvoPos
	elseif e.fase == "fim" then
		parar(m, s)
		if s.cab then som(s.cab, sorteia(SOM.expira), 0.5, 1.15) end
	end
end)

-- jato: segue a boca (ja com o giro da cabeca) e aponta para a mira validada pelo servidor
RunService.RenderStepped:Connect(function()
	for m, s in pairs(W) do
		if s.anc and s.anc.Parent and (s.ativo or s.nucleo.Rate > 0) then
			local b, d = posBoca(s, m)
			if s.alvo then local v = s.alvo - b; if v.Magnitude > 3 then d = (d * 0.35 + v.Unit * 0.65).Unit end end
			s.anc.CFrame = CFrame.lookAt(b, b + d)
		end
	end
end)

-- cabeca/pescoco seguem a mira por cima do clipe (entra/sai suave)
RunService.PreSimulation:Connect(function(dt)
	for m, s in pairs(W) do
		local alvoW = s.ativo and 1 or 0
		s.w += (alvoW - s.w) * math.min(1, dt * 6)
		if s.w > 0.01 and s.cab and s.cab.Parent then
			local cf = s.cab.TransformedWorldCFrame
			local frente = cf.UpVector                                              -- nuca -> focinho (eixo do osso Cabeca)
			local yawD, pitchD = 0, 0
			if s.alvo then
				local v = s.alvo - cf.Position
				local fh, vh = Vector3.new(frente.X, 0, frente.Z), Vector3.new(v.X, 0, v.Z)
				if fh.Magnitude > 1e-3 and vh.Magnitude > 1e-3 then
					fh, vh = fh.Unit, vh.Unit
					yawD = math.atan2(fh:Cross(vh).Y, fh:Dot(vh))
					pitchD = math.asin(math.clamp(v.Unit.Y, -1, 1)) - math.asin(math.clamp(frente.Y, -1, 1))   -- elevacao do alvo - da cabeca
				end
			end
			yawD = math.clamp(yawD, -LIM_YAW, LIM_YAW); pitchD = math.clamp(pitchD, -LIM_PITCH, LIM_PITCH)
			s.yaw += (yawD - s.yaw) * math.min(1, dt * 8); s.pitch += (pitchD - s.pitch) * math.min(1, dt * 8)
			local lado = frente:Cross(Vector3.yAxis); lado = lado.Magnitude > 1e-3 and lado.Unit or Vector3.xAxis
			for i, x in ipairs(PESCOCO) do
				local b = s.ossos[i]
				if b and b.Parent then
					local wcf = b.TransformedWorldCFrame
					local eY = wcf:VectorToObjectSpace(Vector3.yAxis)
					local eL = wcf:VectorToObjectSpace(lado)
					b.Transform = b.Transform * CFrame.fromAxisAngle(eY, s.yaw * x[2] * s.w) * CFrame.fromAxisAngle(eL, s.pitch * x[2] * s.w)   -- + em torno de frente x Y = nariz para cima
				end
			end
		end
	end
end)
