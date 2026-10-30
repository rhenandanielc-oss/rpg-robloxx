-- EfeitosAsas (ModuleScript, lado do cliente) — VFX elementais das asas sincronizados com marcadores de animacao.
-- Emissores pre-criados em ossos da asa (Bone herda de Attachment) e reaproveitados; Emit() so em marcadores.
-- LOD por distancia da camera + nivel grafico; teto de particulas por segundo por dragao. Puramente cosmetico.
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Config = require(script.Parent:WaitForChild("ConfigAsas"))
local M = {}
local ativos = {}

local function osso(modelo, nome)
	for _, d in ipairs(modelo:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end
end
local function criarPonto(pai, nome, posLocal)
	local b = pai:FindFirstChild(nome)
	if not b then b = Instance.new("Bone"); b.Name = nome; b.Position = posLocal; b.Parent = pai end   -- sem peso: so acompanha o pai
	return b
end
local function criarEmissor(ponto, c)
	local e = Instance.new("ParticleEmitter")
	local k = Config.escala or 1
	local tam = {}; for _, p in ipairs(c.tamanho.Keypoints) do table.insert(tam, NumberSequenceKeypoint.new(p.Time, p.Value * k)) end
	e.Name = "VFX_" .. c.nome; e.Texture = c.textura; e.Color = c.cor; e.Size = NumberSequence.new(tam); e.Transparency = c.transp
	e.Lifetime = c.vida; e.Speed = NumberRange.new(c.vel.Min * k * 0.6, c.vel.Max * k * 0.6); e.SpreadAngle = c.espalha; e.Drag = c.arrasto; e.Acceleration = c.acel * k
	e.LightEmission = c.luz; e.Rate = 0; e.Enabled = true; e.LockedToPart = false
	e.Rotation = NumberRange.new(0, 360); e.RotSpeed = c.giro or NumberRange.new(-40, 40)
	e.EmissionDirection = Enum.NormalId.Bottom                      -- para baixo/tras do bordo: segue o fluxo da batida
	e.Parent = ponto
	return e
end

-- pontos de emissao por asa: punho (origem dos dedos), meio e ponta de cada dedo
local function montar(modelo, forma)
	local cfg = Config.formas[forma]; if not cfg then return end
	local reg = {modelo = modelo, cfg = cfg, camadas = {}, poeira = {}, orcamento = 0, brilho = {}}
	for _, l in ipairs({"E", "D"}) do
		for k = 1, 3 do
			local dedo = osso(modelo, ("Dedo%d%s"):format(k, l))
			if dedo then
				local L = dedo:GetAttribute("Comprimento") or 40
				for _, f in ipairs({0.55, 0.95}) do
					local p = criarPonto(dedo, ("VFX_%s_%d"):format(f > 0.9 and "Ponta" or "Meio", math.floor(f * 100)), Vector3.new(0, L * f, 0))
					for _, c in ipairs(cfg.camadas) do
						table.insert(reg.camadas, {e = criarEmissor(p, c), n = c.por_evento / 6})   -- 6 pontos por asa
					end
				end
			end
		end
	end
	for _, pe in ipairs({"PernaDE_3", "PernaDD_3", "PernaTE_3", "PernaTD_3"}) do
		local b = osso(modelo, pe)
		if b then
			local e = criarEmissor(b, {nome = "Poeira", textura = "rbxasset://textures/particles/smoke_main.dds", cor = cfg.poeira.cor,
				tamanho = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.5), NumberSequenceKeypoint.new(1, 4)}),
				transp = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.55), NumberSequenceKeypoint.new(1, 1)}),
				vida = NumberRange.new(0.8, 1.5), vel = NumberRange.new(3, 8), espalha = Vector2.new(80, 10), arrasto = 3, acel = Vector3.new(0, 1, 0), luz = 0})
			e.EmissionDirection = Enum.NormalId.Top
			table.insert(reg.poeira, {e = e, osso = b})
		end
	end
	for _, d in ipairs(modelo:GetDescendants()) do
		if d:IsA("BasePart") and d.Name:find("Brilho") then
			table.insert(reg.brilho, d)
			if cfg.brilho.cor then d.Color = cfg.brilho.cor end
		end
	end
	ativos[modelo] = reg
	return reg
end

local function fatorLOD(modelo)
	local cam = workspace.CurrentCamera; if not cam then return 0 end
	local dist = (modelo:GetPivot().Position - cam.CFrame.Position).Magnitude
	if dist > Config.lod.longe then return 0 end
	local f = dist < Config.lod.perto and 1 or 1 - (dist - Config.lod.perto) / (Config.lod.longe - Config.lod.perto) * 0.7
	local q = UserSettings():GetService("UserGameSettings").SavedQualityLevel.Value   -- 0 = automatico
	if q ~= 0 and q <= 3 then f *= 0.4 elseif q ~= 0 and q <= 6 then f *= 0.7 end
	return f
end

local function soloApropriado(reg, b)
	local lista = reg.cfg.poeira.materiais
	local params = RaycastParams.new(); params.FilterDescendantsInstances = {reg.modelo}; params.FilterType = Enum.RaycastFilterType.Exclude
	local r = workspace:Raycast(b.TransformedWorldCFrame.Position + Vector3.new(0, 2, 0), Vector3.new(0, -8, 0), params)
	if not r then return false end
	if not lista then return true end
	for _, m in ipairs(lista) do if r.Material.Name == m then return true end end
	return false
end

local function pulsoBrilho(reg, forca)
	local b = reg.cfg.brilho
	for _, p in ipairs(reg.brilho) do
		local alvo = b.base_transp - (b.base_transp - b.pulso_transp) * math.clamp(forca, 0, 1)
		p.Transparency = alvo
		TweenService:Create(p, TweenInfo.new(0.55, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Transparency = b.base_transp}):Play()
	end
end

local function disparar(reg, evento, valor)
	local fe = Config.eventos[evento]; if not fe then return end
	-- o marcador carrega o estado no Value ("Voo", "Planeio", "Voo|forte"...): o nome da animacao nao replica ao cliente
	valor = tostring(valor or "Voo")
	local estadoMult = Config.estados[valor:match("^[^|]+")] or 1
	local forte = valor:find("forte") and 1.8 or 1
	local f = fe * estadoMult * forte * fatorLOD(reg.modelo)
	if f <= 0 then return end
	if evento == "TakeoffImpulse" or evento == "LandingImpact" then
		for _, p in ipairs(reg.poeira) do
			if soloApropriado(reg, p.osso) then p.e:Emit(math.max(1, math.floor(reg.cfg.poeira.por_evento / 4 * f))) end
		end
	end
	for _, c in ipairs(reg.camadas) do
		local n = c.n * f
		n = math.floor(n) + ((math.random() < n % 1) and 1 or 0)          -- fracoes viram probabilidade: sem padrao repetido
		if n > 0 and reg.orcamento + n <= Config.lod.teto_por_segundo then reg.orcamento += n; c.e:Emit(n) end
	end
	if evento == "WingDownstrokePeak" or evento == "TakeoffImpulse" then pulsoBrilho(reg, 0.6 * forte * estadoMult) end
end


function M.registrar(modelo)
	local reg = ativos[modelo]
	if reg and reg.ligado then return end
	local forma = modelo:GetAttribute("FormaRegional"); if not forma then return end
	if not osso(modelo, "Dedo2E") then return end                       -- ossos ainda nao chegaram (streaming): tenta depois
	reg = reg or montar(modelo, forma); if not reg then return end
	local animator = modelo:FindFirstChildWhichIsA("Animator", true); if not animator then return end
	reg.ligado = true
	local function ligar(track)                                       -- clipes sem estes marcadores nao emitem nada
		for evento in pairs(Config.eventos) do
			track:GetMarkerReachedSignal(evento):Connect(function(valor) disparar(reg, evento, valor) end)
		end
	end
	for _, t in ipairs(animator:GetPlayingAnimationTracks()) do ligar(t) end
	animator.AnimationPlayed:Connect(ligar)
	modelo.AncestryChanged:Connect(function(_, pai) if not pai then ativos[modelo] = nil end end)
end

RunService.Heartbeat:Connect(function(dt)
	for _, reg in pairs(ativos) do reg.orcamento = math.max(0, reg.orcamento - Config.lod.teto_por_segundo * dt) end
	for _, reg in pairs(ativos) do
		local b = reg.cfg.brilho
		if b.oscila then for _, p in ipairs(reg.brilho) do p.Transparency = math.clamp(p.Transparency + (math.random() - 0.5) * 0.02, b.pulso_transp, 1) end end
	end
end)
return M
